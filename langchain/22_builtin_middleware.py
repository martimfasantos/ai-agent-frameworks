import os
from collections.abc import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import (
    ClearToolUsesEdit,
    ContextEditingMiddleware,
    ModelCallLimitMiddleware,
    ModelRequest,
    ModelResponse,
    SummarizationMiddleware,
    ToolCallLimitMiddleware,
    TriggerClause,
    wrap_model_call,
)
from langchain.tools import tool
from langchain_core.messages.utils import count_tokens_approximately
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore LangChain with the following features:
- SummarizationMiddleware(trigger=, keep=) with TriggerClause AND-semantics
- ContextEditingMiddleware(edits=[ClearToolUsesEdit(...)]) to prune stale tool output
- ModelCallLimitMiddleware(thread_limit=, run_limit=, exit_behavior=)
- ToolCallLimitMiddleware to cap how often a single tool may be called

LangChain ships a catalog of prebuilt middleware, so the common context and
budget problems do not need custom hooks. These three cover the ones you hit
first in production: a conversation that outgrows the context window, tool
outputs that stay in history long after they are useful, and a loop that keeps
calling the model or a tool forever.

For more details, visit:
https://docs.langchain.com/oss/python/langchain/middleware/built-in
-------------------------------------------------------
"""

model = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=0)

# --------------------------------------------------------------
# Example 1: SummarizationMiddleware with a TriggerClause
# --------------------------------------------------------------
print("=== Example 1: SummarizationMiddleware (TriggerClause AND-semantics) ===")

# --- 1. A single TriggerClause is AND: BOTH thresholds must be crossed ---
# (a list of clauses would be OR: any one clause is enough)
summarizing_agent = create_agent(
    model=model,
    system_prompt="You are a trip planner. Reply in one short sentence.",
    middleware=[
        SummarizationMiddleware(
            model=model,
            trigger=TriggerClause(messages=8, tokens=180),
            keep=("messages", 2),
        )
    ],
    checkpointer=InMemorySaver(),
)

turns = [
    "I am planning a trip to Lisbon in May.",
    "I want to see the Belem tower and ride tram 28.",
    "My budget is 1200 euros for five nights.",
    "I am travelling with my brother, who is vegetarian.",
    "What do you remember about my trip?",
]

config = {"configurable": {"thread_id": "summarization-demo"}}
previous_count = 0
for turn in turns:
    result = summarizing_agent.invoke(
        {"messages": [{"role": "user", "content": turn}]}, config=config
    )
    messages = result["messages"]
    summarized = len(messages) < previous_count
    print(
        f"  turn: {turn[:44]:<44} -> {len(messages):>2} messages,"
        f" ~{count_tokens_approximately(messages):>3} tokens"
        + (" <- both thresholds crossed, history summarized" if summarized else "")
    )
    previous_count = len(messages)

print("\n  history is now a summary plus the 2 most recent messages:")
print(f"    {str(messages[0].content)[:200]}...")
print(f"  last answer: {messages[-1].content}\n")

# --------------------------------------------------------------
# Example 2: ContextEditingMiddleware + ClearToolUsesEdit
# --------------------------------------------------------------
print("=== Example 2: ContextEditingMiddleware (ClearToolUsesEdit) ===")


# --- 2. A tool whose output is verbose and quickly goes stale ---
@tool
def get_city_report(city: str) -> str:
    """Get a verbose tourism report for a city."""
    return (
        f"Tourism report for {city}. Peak season runs from June to September, with "
        f"hotel occupancy above ninety percent and average nightly rates roughly "
        f"forty percent higher than in the shoulder months. Public transport covers "
        f"the historic centre well, and most museums close one weekday. Visitors "
        f"typically stay three to four nights and rate walkability highly. "
        f"Weather in {city} is mild, and rainfall is concentrated in winter."
    )


PLACEHOLDER = "[cleared to save context]"


# --- 3. A probe placed INSIDE the editing middleware, to see what the model receives ---
# (context edits are applied to the model request only — agent state keeps the originals)
@wrap_model_call
def show_model_context(
    request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    tool_messages = [m for m in request.messages if m.type == "tool"]
    cleared = sum(1 for m in tool_messages if m.content == PLACEHOLDER)
    print(
        f"  [model call] {len(tool_messages)} tool results in request,"
        f" {cleared} cleared, ~{count_tokens_approximately(request.messages)} tokens"
    )
    return handler(request)


# --- 4. Clear all but the most recent tool result once context passes the trigger ---
editing_agent = create_agent(
    model=model,
    tools=[get_city_report],
    system_prompt=(
        "Call get_city_report exactly once for each city the user names. Older tool "
        "results may have been cleared from your context — never repeat a tool call, "
        "answer in one sentence with whatever is still visible."
    ),
    middleware=[
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=250,  # start clearing above ~250 tokens of context
                    keep=1,  # keep only the most recent tool result
                    placeholder=PLACEHOLDER,
                )
            ]
        ),
        show_model_context,
    ],
)

result = editing_agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "Compare Lisbon, London and Tokyo for a May trip."}
        ]
    }
)

print("  agent state still holds every original tool result:")
for message in result["messages"]:
    if message.type == "tool":
        print(f"    {message.name:<16} -> {str(message.content)[:56]}...")
print(f"  final answer: {result['messages'][-1].content}\n")

# --------------------------------------------------------------
# Example 3: ModelCallLimitMiddleware + ToolCallLimitMiddleware
# --------------------------------------------------------------
print("=== Example 3: ModelCallLimitMiddleware + ToolCallLimitMiddleware ===")


# --- 5. A tool that always claims there is more to fetch ---
@tool
def fetch_page(page: int) -> str:
    """Fetch one page of search results."""
    return f"Page {page}: 3 results found. More pages are available."


# --- 6. Cap both the model loop and the individual tool ---
limited_agent = create_agent(
    model=model,
    tools=[fetch_page],
    system_prompt="Page through every page of results until there are no more pages.",
    middleware=[
        ModelCallLimitMiddleware(thread_limit=8, run_limit=3, exit_behavior="end"),
        ToolCallLimitMiddleware(tool_name="fetch_page", run_limit=2, exit_behavior="continue"),
    ],
)

result = limited_agent.invoke(
    {"messages": [{"role": "user", "content": "List every result page you can find."}]}
)

# The final AI message is synthesized by the middleware, so it has no response metadata.
model_calls = sum(1 for m in result["messages"] if m.type == "ai" and m.response_metadata)
tool_results = [m for m in result["messages"] if m.type == "tool"]
blocked = [m for m in tool_results if "limit exceeded" in str(m.content)]
print(f"  model calls made      : {model_calls} (run_limit=3, then exit_behavior='end')")
print(f"  fetch_page executions : {len(tool_results) - len(blocked)} (run_limit=2)")
print(f"  blocked tool calls    : {len(blocked)} -> {blocked[0].content}")
print(f"  final answer          : {str(result['messages'][-1].content)[:120]}")
