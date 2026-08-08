import asyncio
import contextlib
import sys
from pathlib import Path

from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.utils.workflow import (
    draw_agent_workflow,
    draw_agent_workflow_mermaid,
    draw_all_possible_flows,
    draw_all_possible_flows_mermaid,
    draw_most_recent_execution,
    draw_most_recent_execution_mermaid,
)
from workflows import Workflow, Context, step
from workflows.events import Event, StartEvent, StopEvent

sys.path.append(str(Path(__file__).parent.parent))
from settings import settings


"""
-------------------------------------------------------
In this example, we explore LlamaIndex Workflows with the following features:
- Drawing all possible flows with draw_all_possible_flows()
- Drawing the most recent execution with draw_most_recent_execution()
- Mermaid renderers that emit diagram source instead of HTML
- Drawing agents and multi-agent handoffs with draw_agent_workflow()
- Using the WorkflowServer debugger UI for visualization

Workflows can be visualized straight from the type annotations on their steps.
The llama-index-utils-workflow package renders either an interactive pyvis HTML
page or Mermaid source (handy for committing a diagram into Markdown docs), for
both a static view of every possible path and a trace of the run that just
happened. Agents get their own renderers, since an AgentWorkflow's interesting
structure is its handoff graph rather than its steps.

For more details, visit:
https://developers.llamaindex.ai/python/llamaagents/workflows/drawing/
-------------------------------------------------------
"""

# Generated diagrams live in the framework-level res/ directory
RES_DIR = Path(__file__).parent.parent / "res"
RES_DIR.mkdir(parents=True, exist_ok=True)


def graph_only(mermaid: str) -> str:
    """Strip the trailing classDef styling block so the graph is readable"""
    return "\n".join(
        line for line in mermaid.splitlines() if not line.strip().startswith("classDef")
    ).rstrip()


# --- 1. Define events for a multi-path workflow ---
class ProcessEvent(Event):
    data: str


class ValidationEvent(Event):
    is_valid: bool
    message: str


# --- 2. Define a workflow with multiple paths ---
class DrawableWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> ProcessEvent:
        """Initial processing step"""
        return ProcessEvent(data="Sample data to process")

    @step
    async def process_data(self, ev: ProcessEvent) -> ValidationEvent:
        """Process and validate data"""
        is_valid = len(ev.data) > 0
        return ValidationEvent(
            is_valid=is_valid,
            message="Data is valid" if is_valid else "Data is invalid",
        )

    @step
    async def handle_result(self, ev: ValidationEvent) -> StopEvent:
        """Handle validation result"""
        return StopEvent(result=ev.message)


async def main():
    workflow = DrawableWorkflow(timeout=30, verbose=False)
    handler = workflow.run()
    await handler

    llm = OpenAI(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
    )
    researcher = FunctionAgent(
        name="ResearchAgent",
        description="Gathers information.",
        llm=llm,
        can_handoff_to=["WriteAgent"],
    )
    writer = FunctionAgent(
        name="WriteAgent",
        description="Writes the final answer.",
        llm=llm,
    )
    agent_workflow = AgentWorkflow(
        agents=[researcher, writer], root_agent="ResearchAgent"
    )

    # pyvis drops its JS/CSS bundle into the working directory alongside the HTML
    # it writes, so render from inside res/ to keep everything self-contained.
    with contextlib.chdir(RES_DIR):
        # --- 3. Static view: every possible path ---
        # Since llama-index-utils-workflow 0.10.1 this accepts either an instance
        # or the workflow class itself, so no run is required to draw it.
        draw_all_possible_flows(DrawableWorkflow, filename="all_paths.html")
        print("Wrote res/all_paths.html")

        # --- 4. Execution view: only the path that actually ran ---
        draw_most_recent_execution(handler, filename="most_recent.html")
        print("Wrote res/most_recent.html")

        # --- 5. Mermaid renderers return the diagram source as a string ---
        mermaid = draw_all_possible_flows_mermaid(
            DrawableWorkflow, filename="all_paths.mermaid"
        )
        draw_most_recent_execution_mermaid(handler, filename="most_recent.mermaid")
        print("Wrote res/all_paths.mermaid and res/most_recent.mermaid")

        # --- 6. Agent renderers: draw the handoff graph of an AgentWorkflow ---
        draw_agent_workflow(agent_workflow, filename="agent_handoffs.html")
        handoffs = draw_agent_workflow_mermaid(
            agent_workflow, filename="agent_handoffs.mermaid"
        )
        print("Wrote res/agent_handoffs.html and res/agent_handoffs.mermaid")

    print(f"\nMermaid source for all possible flows:\n{graph_only(mermaid)}")
    print(f"\nMermaid source for the agent handoff graph:\n{graph_only(handoffs)}")

    # --- 7. Alternative: Use the WorkflowServer debugger UI ---
    # from llama_agents.server import WorkflowServer
    # server = WorkflowServer()
    # server.add_workflow("drawable", DrawableWorkflow())
    # await server.serve("0.0.0.0", 8080)
    # Then open http://localhost:8080 to see the debugger UI


if __name__ == "__main__":
    asyncio.run(main())
