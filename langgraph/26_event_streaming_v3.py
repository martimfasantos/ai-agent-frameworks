from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.stream import UpdatesTransformer
from langgraph.types import interrupt
from typing_extensions import TypedDict

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore LangGraph with the following features:
- graph.stream_events(..., version="v3") returning a GraphRunStream
- Typed native projections: .messages, .values, .subgraphs, .output
- Per-message projections: message.text deltas and message.output
- .interrupted / .interrupts to detect a paused run
- Opting extra projections in with transformers=[UpdatesTransformer]

The v3 event protocol replaces stream_mode tuples with a run handle whose
typed projections you iterate: run.messages yields one stream per LLM call,
run.values yields state snapshots, run.output drives the run to completion.
Iterating a projection is what pumps the graph — there is no background
thread — so each projection is single-consumer and a run is driven once.
The v3 protocol is still marked experimental, so running this emits a
LangChainBetaWarning on stderr.

For more details, visit:
https://docs.langchain.com/oss/python/langgraph/event-streaming
-----------------------------------------------------------------------
"""

llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME)

SYSTEM = SystemMessage(content="You are terse. Answer in one short sentence.")


# --- 1. A minimal chat graph to stream from ---
def chat(state: MessagesState) -> dict:
    return {"messages": [llm.invoke([SYSTEM] + state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("chat", chat)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)
graph = builder.compile()


def ask(text: str) -> dict:
    return {"messages": [HumanMessage(content=text)]}


# --- 2. run.messages: one stream handle per LLM call, with token deltas ---
print("=== run.messages -> message.text deltas ===\n")

run = graph.stream_events(ask("Name the largest planet."), version="v3")
for message in run.messages:
    print(f"  node={message.node}")
    print("  deltas: ", end="", flush=True)
    for delta in message.text:
        print(f"{delta!r} ", end="", flush=True)
    print()
    print(f"  assembled: {str(message.text)}")
    print(f"  tokens:    {message.output.usage_metadata['total_tokens']}")
print()

# --- 3. run.values: state snapshots, then run.output for the final state ---
print("=== run.values -> snapshots, run.output -> final state ===\n")

run = graph.stream_events(ask("Name the smallest planet."), version="v3")
for step, snapshot in enumerate(run.values):
    print(f"  snapshot {step}: {len(snapshot['messages'])} message(s)")
print(f"  run.output keys: {list(run.output)}")
print(f"  final answer:    {run.output['messages'][-1].text}\n")

# --- 4. transformers=[...]: opt in to a non-native projection ---
print("=== transformers=[UpdatesTransformer] -> run.extensions['updates'] ===\n")

run = graph.stream_events(
    ask("Name the hottest planet."),
    version="v3",
    transformers=[UpdatesTransformer],
)
print(f"  projections available: {list(run.extensions)}")
for update in run.extensions["updates"]:
    for node, payload in update.items():
        print(f"  update from '{node}': {payload['messages'][-1].text}")
print()

# --- 5. run.subgraphs: nested runs get their own handle ---
print("=== run.subgraphs -> nested run handles ===\n")

inner_builder = StateGraph(MessagesState)
inner_builder.add_node("inner_chat", chat)
inner_builder.add_edge(START, "inner_chat")
inner_builder.add_edge("inner_chat", END)

outer_builder = StateGraph(MessagesState)
outer_builder.add_node("delegate", inner_builder.compile())
outer_builder.add_edge(START, "delegate")
outer_builder.add_edge("delegate", END)
outer = outer_builder.compile()

run = outer.stream_events(ask("Name the reddest planet."), version="v3")
for subgraph in run.subgraphs:
    print(f"  subgraph '{subgraph.graph_name}' at path {subgraph.path}")
    for message in subgraph.messages:
        print(f"    {str(message.text)}")
print()


# --- 6. run.interrupted / run.interrupts: a paused run ---
class ApprovalState(TypedDict, total=False):
    decision: str


def request_approval(state: ApprovalState) -> dict:
    return {"decision": interrupt({"question": "Deploy to production?"})}


approval_builder = StateGraph(ApprovalState)
approval_builder.add_node("request_approval", request_approval)
approval_builder.add_edge(START, "request_approval")
approval_builder.add_edge("request_approval", END)
approval_graph = approval_builder.compile(checkpointer=InMemorySaver())

print("=== run.interrupted / run.interrupts ===\n")

run = approval_graph.stream_events(
    {}, {"configurable": {"thread_id": "approval-1"}}, version="v3"
)
print(f"  interrupted: {run.interrupted}")
for pause in run.interrupts:
    print(f"  waiting on:  {pause.value}")
