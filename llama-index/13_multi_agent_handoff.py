import asyncio

from llama_index.core.agent.workflow import (
    AgentInput,
    AgentWorkflow,
    FunctionAgent,
    ToolCall,
    ToolCallResult,
)
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

from settings import settings


"""
-------------------------------------------------------
In this example, we explore LlamaIndex with the following features:
- AgentWorkflow for orchestrating several agents in one run
- can_handoff_to to declare which agents an agent may delegate to
- root_agent to pick who starts, and initial_state for shared scratch space
- Tools that read and write the shared state via ctx.store
- Streaming AgentInput / ToolCall / AgentOutput to watch the handoff happen

An AgentWorkflow lets specialised agents pass control between each other. Each
FunctionAgent declares the agents it may hand off to; the framework injects a
`handoff` tool accordingly, so delegation is a normal tool call the LLM decides
to make. The `initial_state` dict is shared by every agent in the run, which is
how work-in-progress travels between them without being re-summarised into the
prompt.

For more details, visit:
https://developers.llamaindex.ai/python/framework/understanding/agent/multi_agent/
-------------------------------------------------------
"""

llm = OpenAI(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
)


# --- 1. Tools that read and write the workflow's shared state ---
# AgentWorkflow stores initial_state under the "state" key of the context store,
# so every agent in the run reads and writes the same dict through it.
async def record_notes(ctx: Context, notes: str) -> str:
    """Save research notes to the shared state."""
    state = await ctx.store.get("state")
    state["notes"].append(notes)
    await ctx.store.set("state", state)
    return "Notes recorded."


async def read_notes(ctx: Context) -> str:
    """Read every research note saved so far."""
    state = await ctx.store.get("state")
    return "\n".join(state["notes"]) if state["notes"] else "No notes yet."


async def write_report(ctx: Context, report: str) -> str:
    """Save the finished report to the shared state."""
    state = await ctx.store.get("state")
    state["report"] = report
    await ctx.store.set("state", state)
    return "Report saved."


# --- 2. A researcher that may hand off to the writer ---
research_agent = FunctionAgent(
    name="ResearchAgent",
    description="Collects facts about a topic and records them as notes.",
    system_prompt=(
        "You research topics from your own knowledge. Record two short factual "
        "notes with record_notes, then hand off to WriteAgent. Do not write the "
        "report yourself."
    ),
    llm=llm,
    tools=[record_notes],
    can_handoff_to=["WriteAgent"],
)

# --- 3. A writer that turns the notes into the final answer ---
write_agent = FunctionAgent(
    name="WriteAgent",
    description="Turns recorded notes into a short report.",
    system_prompt=(
        "Call read_notes, write a 2-sentence report from them, save it with "
        "write_report, then reply with the report text."
    ),
    llm=llm,
    tools=[read_notes, write_report],
    can_handoff_to=[],  # terminal: an empty list means no handoff tool is injected
)

# --- 4. Wire them into an AgentWorkflow with shared initial state ---
workflow = AgentWorkflow(
    agents=[research_agent, write_agent],
    root_agent="ResearchAgent",
    initial_state={"notes": [], "report": ""},
)


# --- 5. Run it and stream the handoff ---
async def main():
    ctx = Context(workflow)
    handler = workflow.run(
        user_msg="Write a short report on why the Lisbon tram 28 is famous.",
        ctx=ctx,
    )

    current = None
    async for event in handler.stream_events():
        if isinstance(event, AgentInput) and event.current_agent_name != current:
            current = event.current_agent_name
            print(f"\n>>> {current} is now in control")
        # ToolCallResult subclasses ToolCall, so exclude it to log each call once
        elif isinstance(event, ToolCall) and not isinstance(event, ToolCallResult):
            print(f"    tool: {event.tool_name}({list(event.tool_kwargs)})")

    await handler

    # --- 6. Inspect the shared state both agents wrote to ---
    state = await ctx.store.get("state")
    print("\n--- Shared state ---")
    for i, note in enumerate(state["notes"], start=1):
        print(f"note {i}: {note}")
    print(f"\nreport: {state['report']}")


if __name__ == "__main__":
    asyncio.run(main())
