import operator
from typing import Annotated

from dotenv import load_dotenv

from langgraph.errors import InvalidUpdateError
from langgraph.graph import StateGraph, START, END
from langgraph.types import Overwrite
from typing_extensions import TypedDict

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore LangGraph with the following features:
- Bypassing a channel's reducer with Overwrite(value=...)
- The JSON-safe {"__overwrite__": ...} form of the same instruction
- InvalidUpdateError when two parallel nodes Overwrite the same channel
- Deferring a fan-in node with add_node(..., defer=True)

A reducer such as operator.add is a one-way street: every node that writes
to the channel appends. Overwrite is the escape hatch — it replaces the
channel value instead of merging into it, which is how a compaction or
summarisation node discards history. defer=True solves the complementary
problem on the control-flow side: a fan-in node whose branches have
different lengths would otherwise run once per super-step in which any
branch arrives, instead of once at the end with everything collected.

For more details, visit:
https://docs.langchain.com/oss/python/langgraph/use-graph-api#bypass-reducers-with-overwrite
-----------------------------------------------------------------------
"""


# --- 1. State whose channel accumulates via a reducer ---
class NotesState(TypedDict):
    notes: Annotated[list[str], operator.add]


def gather(state: NotesState) -> dict:
    """Normal update: goes through operator.add, so it appends."""
    return {"notes": ["gathered-a", "gathered-b"]}


def compact(state: NotesState) -> dict:
    """Overwrite update: bypasses operator.add and replaces the channel."""
    summary = f"summary of {len(state['notes'])} notes"
    return {"notes": Overwrite([summary])}


builder = StateGraph(NotesState)
builder.add_node("gather", gather)
builder.add_node("compact", compact)
builder.add_edge(START, "gather")
builder.add_edge("gather", "compact")
builder.add_edge("compact", END)
graph = builder.compile()

# --- 2. Watch the channel across super-steps ---
print("=== Reducer append, then Overwrite ===\n")

for snapshot in graph.stream({"notes": ["seed"]}, stream_mode="values"):
    print(f"  notes = {snapshot['notes']}")
print("\n  Without Overwrite the last line would have been")
print("  ['seed', 'gathered-a', 'gathered-b', 'summary of 3 notes']\n")


# --- 3. The JSON-safe form: {"__overwrite__": value} ---
def compact_json_form(state: NotesState) -> dict:
    """Same semantics as Overwrite, survives a JSON round-trip through a server."""
    return {"notes": {"__overwrite__": ["summary via JSON form"]}}


json_builder = StateGraph(NotesState)
json_builder.add_node("compact_json_form", compact_json_form)
json_builder.add_edge(START, "compact_json_form")
json_builder.add_edge("compact_json_form", END)

print("=== JSON form of Overwrite ===\n")
result = json_builder.compile().invoke({"notes": ["seed", "kept-nothing"]})
print(f"  notes = {result['notes']}\n")


# --- 4. The trap: two parallel Overwrites on one channel ---
def compact_left(state: NotesState) -> dict:
    return {"notes": Overwrite(["from-left"])}


def compact_right(state: NotesState) -> dict:
    return {"notes": Overwrite(["from-right"])}


parallel_builder = StateGraph(NotesState)
parallel_builder.add_node("compact_left", compact_left)
parallel_builder.add_node("compact_right", compact_right)
parallel_builder.add_edge(START, "compact_left")
parallel_builder.add_edge(START, "compact_right")
parallel_builder.add_edge("compact_left", END)
parallel_builder.add_edge("compact_right", END)

print("=== Two parallel Overwrites on the same channel ===\n")
try:
    parallel_builder.compile().invoke({"notes": ["seed"]})
except InvalidUpdateError as exc:
    print(f"  InvalidUpdateError: {str(exc).splitlines()[0]}")
print("  There is no reducer left to merge them, so LangGraph refuses to pick.\n")


# --- 5. Uneven branches: with and without defer ---
class PipelineState(TypedDict):
    log: Annotated[list[str], operator.add]


def make_step(name: str):
    def step(state: PipelineState) -> dict:
        return {"log": [name]}

    return step


def build_pipeline(defer: bool):
    """Long branch: extract -> enrich -> score. Short branch: lookup. Both fan into report."""
    calls: list[int] = []

    def report(state: PipelineState) -> dict:
        calls.append(len(state["log"]))
        return {"log": [f"report(saw {len(state['log'])})"]}

    b = StateGraph(PipelineState)
    for name in ("extract", "enrich", "score", "lookup"):
        b.add_node(name, make_step(name))
    b.add_node("report", report, defer=defer)

    b.add_edge(START, "extract")
    b.add_edge("extract", "enrich")
    b.add_edge("enrich", "score")
    b.add_edge("score", "report")
    b.add_edge(START, "lookup")
    b.add_edge("lookup", "report")
    b.add_edge("report", END)
    return b.compile(), calls


print("=== Fan-in across uneven branches ===\n")

for defer in (False, True):
    pipeline, calls = build_pipeline(defer)
    final = pipeline.invoke({"log": []})
    print(f"  defer={defer}")
    print(f"    report ran {len(calls)}x, log entries visible per call: {calls}")
    print(f"    final log = {final['log']}")
    print()

print("  Without defer, 'lookup' finishes in super-step 1 and fires 'report'")
print("  before the long branch is done. defer=True holds it until the run")
print("  is about to end, so it runs once with every branch collected.")
