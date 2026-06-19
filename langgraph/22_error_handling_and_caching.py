import os
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.types import CachePolicy

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore LangGraph with the following features:
- Node-level error handlers (new in v1.2.0)
- Cache policies for expensive node computations
- Graceful degradation when nodes fail

Error handlers let nodes recover from failures without crashing
the entire graph. Cache policies avoid re-running expensive
computations when inputs haven't changed.

For more details, visit:
https://langchain-ai.github.io/langgraph/reference/graphs/
-------------------------------------------------------
"""


# --- 1. Define state ---
class State(TypedDict):
    query: str
    answer: str


# --- 2. Define nodes ---
llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0)


def lookup(state: State) -> dict:
    """Simulate a node that might fail (e.g., external API call)."""
    query = state["query"]
    if "fail" in query.lower():
        raise ValueError(f"Lookup failed for: {query}")
    response = llm.invoke(f"Answer concisely in one sentence: {query}")
    return {"answer": response.content}


# --- 3. Error handler: graceful degradation ---
def on_lookup_error(state: State) -> dict:
    """Recover from lookup failure with a fallback answer."""
    query = state.get("query", "unknown")
    print(f"  [Error Handler] Recovered from failure for: '{query}'")
    return {"answer": f"[Fallback] Could not process '{query}' — service unavailable."}


# --- 4. Build graph with error_handler and cache_policy ---
cache_policy = CachePolicy(ttl=60)  # Cache results for 60 seconds

graph = StateGraph(State)
graph.add_node(
    "lookup",
    lookup,
    error_handler=on_lookup_error,
    cache_policy=cache_policy,
)
graph.set_entry_point("lookup")
graph.add_edge("lookup", END)

app = graph.compile()


# --- 5. Run: successful case ---
print("=== Successful Query ===")
result = app.invoke({"query": "What is the capital of France?", "answer": ""})
print(f"  Answer: {result['answer']}")
print()

# --- 6. Run: failure case (triggers error handler) ---
print("=== Failed Query (triggers error handler) ===")
result = app.invoke({"query": "Please fail this lookup", "answer": ""})
print(f"  Answer: {result['answer']}")
print()

# --- 7. Run: cache hit (same successful query again) ---
print("=== Cached Query (same input, uses cache) ===")
result = app.invoke({"query": "What is the capital of France?", "answer": ""})
print(f"  Answer: {result['answer']}")
print()

# --- 8. Show configuration ---
print("=== Node Configuration ===")
print(f"  cache_policy.ttl: {cache_policy.ttl}s")
print(f"  error_handler: on_lookup_error (graceful degradation)")
