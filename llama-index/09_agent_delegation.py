import re
import asyncio
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import ReActAgent, FunctionAgent
from llama_index.core.workflow import Context
from llama_index.core.agent.workflow.workflow_events import ToolCall
from settings import settings


"""
-------------------------------------------------------
In this example, we explore LlamaIndex with the following features:
- Wrapping an agent as a tool
- Agent delegation pattern
- Specialized agents

This shows how one agent can use another agent as a tool, enabling delegation
of specialized tasks.

For more details, visit:
https://docs.llamaindex.ai/en/stable/module_guides/agent/agents/
-------------------------------------------------------
"""

# --- 1. Configure the LLM ---
llm = OpenAI(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value()
)

# --- 2. Create the sub-agents that will perform specific tasks ---
research_agent = FunctionAgent(
    llm=llm,
    tools=[],
    verbose=False,  # step logging became functional in workflows 2.15.0
    system_prompt="You are a research assistant. Provide detailed notes on any topic."
)

write_agent = FunctionAgent(
    llm=llm,
    tools=[],
    verbose=False,  # step logging became functional in workflows 2.15.0
    system_prompt="You are a writing assistant. Write clear and concise summaries based on research notes."
)

# --- 3. Create the tools for the orchestrator to call the sub agents ---
async def call_research_agent(ctx: Context, prompt: str) -> str:
    """Useful for recording research notes based on a specific prompt."""
    result = await research_agent.run(
        user_msg=f"Write some notes about the following: {prompt}"
    )

    async with ctx.store.edit_state() as ctx_state:
        ctx_state["state"]["research_notes"].append(str(result))

    return str(result)

async def call_write_agent(ctx: Context) -> str:
    """Useful for writing a report based on the research notes or revising the report based on feedback."""
    async with ctx.store.edit_state() as ctx_state:
        notes = ctx_state["state"].get("research_notes", None)
        if not notes:
            return "No research notes to write from."

        user_msg = f"Write a markdown report from the following notes. Be sure to output the report in the following format: <report>...</report>:\n\n"

        # Add the research notes to the user message
        notes = "\n\n".join(notes)
        user_msg += f"<research_notes>{notes}</research_notes>\n\n"

        # Run the write agent
        result = await write_agent.run(user_msg=user_msg)
        report = re.search(
            r"<report>(.*)</report>", str(result), re.DOTALL
        ).group(1)
        ctx_state["state"]["report_content"] = str(report)

    return str(report)


# --- 4. Create the orchestrator agent that delegates to the research agent ---
orchestrator_agent = ReActAgent(
    llm=llm,
    system_prompt="You are an orchestrator assistant. Delegate research tasks to the sub-agents.",
    tools=[call_research_agent, call_write_agent],
    initial_state={
        "research_notes": [],
        "report_content": None,
        "review": None,
    },
)

# --- 5. Run the orchestrator agent with a research question ---
async def main():
    handler = orchestrator_agent.run(
        "Write me a report on the history of the web …"
    )
    async for ev in handler.stream_events():
        if isinstance(ev, ToolCall):
            print(f"Tool selected: {ev.tool_name}")
    output = await handler
    
    # NOTE: the output takes a while to generate since it involves multiple agent calls and LLM interactions
    print("-" * 50)
    print("Final Output: ", output)


if __name__ == "__main__":
    asyncio.run(main())
