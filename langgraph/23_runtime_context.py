from dataclasses import dataclass

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore LangGraph with the following features:
- Declaring run-scoped dependencies with StateGraph(..., context_schema=...)
- Injecting Runtime[ContextSchema] as a second node argument
- Reading runtime.context, runtime.store and runtime.stream_writer in a node
- Passing per-run values with graph.invoke(..., context=...)
- runtime.previous for the functional API's per-thread carry-over value

Runtime context is the LangGraph 1.0 replacement for smuggling
configuration (user id, tenant, locale, db handles) through graph state.
Context is declared once as a schema, supplied per run, and reaches every
node via a typed Runtime object — it never becomes part of the state, so
it is never checkpointed and never merged by a reducer.

For more details, visit:
https://docs.langchain.com/oss/python/langgraph/use-graph-api#add-runtime-configuration
-----------------------------------------------------------------------
"""

llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME)


# --- 1. Declare the run-scoped context schema ---
@dataclass
class RequestContext:
    """Per-run dependencies. Not state: never checkpointed, never reduced."""

    user_id: str
    locale: str
    tone: str


class ReplyState(TypedDict, total=False):
    question: str
    profile: str
    reply: str


# --- 2. Seed a store with data the nodes will look up by context ---
store = InMemoryStore()
store.put(("profiles",), "u-100", {"name": "Alice", "plan": "enterprise"})
store.put(("profiles",), "u-200", {"name": "Bruno", "plan": "free"})


# --- 3. Nodes take (state, runtime) — runtime carries context/store/stream_writer ---
def load_profile(state: ReplyState, runtime: Runtime[RequestContext]) -> dict:
    """Resolve the caller's profile from the store using runtime.context."""
    user_id = runtime.context.user_id

    # runtime.stream_writer emits to stream_mode="custom" without touching state
    runtime.stream_writer({"step": "load_profile", "user_id": user_id})

    record = runtime.store.get(("profiles",), user_id)
    profile = f"{record.value['name']} ({record.value['plan']} plan)"
    return {"profile": profile}


def answer(state: ReplyState, runtime: Runtime[RequestContext]) -> dict:
    """Shape the LLM call from runtime.context — no context value is in state."""
    ctx = runtime.context
    runtime.stream_writer({"step": "answer", "tone": ctx.tone})

    system = (
        f"You are a support agent. The customer you are helping is {state['profile']}. "
        f"Reply in {ctx.locale} using a {ctx.tone} tone, in exactly one sentence."
    )
    response = llm.invoke(
        [SystemMessage(content=system), HumanMessage(content=state["question"])]
    )
    return {"reply": response.content}


# --- 4. Build the graph, binding the context schema and the store ---
builder = StateGraph(ReplyState, context_schema=RequestContext)
builder.add_node("load_profile", load_profile)
builder.add_node("answer", answer)
builder.add_edge(START, "load_profile")
builder.add_edge("load_profile", "answer")
builder.add_edge("answer", END)

graph = builder.compile(store=store)

# --- 5. Same input state, different context per run ---
print("=== Same input, two different runtime contexts ===\n")

question = {"question": "Can I export my data?"}

for ctx in (
    RequestContext(user_id="u-100", locale="English", tone="formal"),
    # A plain dict is accepted too — it is coerced into the context schema
    {"user_id": "u-200", "locale": "Portuguese", "tone": "playful"},
):
    result = graph.invoke(question, context=ctx)
    print(f"  context ....... {ctx}")
    print(f"  profile ....... {result['profile']}")
    print(f"  reply ......... {result['reply']}")
    print(f"  state keys .... {sorted(result)}  <- no user_id/locale/tone in state")
    print()

# --- 6. runtime.stream_writer feeds stream_mode="custom" ---
print("=== Custom stream written from runtime.stream_writer ===\n")

for chunk in graph.stream(
    question,
    stream_mode="custom",
    context=RequestContext(user_id="u-100", locale="English", tone="terse"),
):
    print(f"  {chunk}")
print()

# --- 7. runtime.previous: functional-API-only carry-over across runs ---
print("=== runtime.previous (functional API, needs a checkpointer) ===\n")


@entrypoint(checkpointer=InMemorySaver())
def running_total(amount: int, runtime: Runtime) -> entrypoint.final:
    """Return the running total while saving it for the next run on this thread."""
    previous = runtime.previous or 0
    total = previous + amount
    return entrypoint.final(value={"previous": previous, "total": total}, save=total)


config = {"configurable": {"thread_id": "totals-1"}}
for amount in (10, 5, 2):
    step = running_total.invoke(amount, config=config)
    print(f"  +{amount:<3} previous={step['previous']:<3} total={step['total']}")
