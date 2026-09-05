import os
import asyncio
from typing import AsyncGenerator

from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from settings import settings
from utils import print_new_section

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- Building multi-agent systems with SequentialAgent pipelines
- Sharing session state between agents using output_key
- Custom BaseAgent for deterministic, non-LLM steps
- Composing specialist LlmAgents in a research-to-report pipeline

Multi-agent systems in ADK allow agents to collaborate by sharing a
common session state. A SequentialAgent runs each sub-agent in order.
Agents can write their outputs to session state (via output_key) and
read from it in their instructions (via {key} interpolation), creating
a reliable data-passing pipeline without needing tool calls.

For more details, visit:
https://google.github.io/adk-docs/agents/multi-agents/
-------------------------------------------------------
"""

APP_NAME = "multi_agent_demo"
USER_ID = "user"
SESSION_ID = "session-001"


# --- 1. Custom BaseAgent for deterministic research (no LLM needed) ---
class ResearchAgent(BaseAgent):
    """Simulates a research step — writes findings to session state."""

    name: str = "ResearchAgent"
    description: str = "Gathers research findings on a topic."

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        topic = ctx.session.state.get("research_topic", "AI")
        findings = (
            f"Research findings on {topic}:\n"
            "- Advanced language models (GPT-4, Gemini, Claude)\n"
            "- Multimodal AI combining text, images, and audio\n"
            "- Agentic AI systems that take autonomous actions\n"
            "- Widespread adoption across healthcare, finance, and education"
        )
        ctx.session.state["research_data"] = findings
        print(f"  [ResearchAgent] Stored findings for topic: {topic}")
        yield Event(author=self.name)


# --- 2. Analysis agent — reads research_data, writes analysis_summary ---
analysis_agent = LlmAgent(
    name="AnalysisAgent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You are a data analyst. "
        "Analyze this research:\n\n{research_data}\n\n"
        "Provide exactly 3 concise bullet-point insights. "
        "Output only the bullet points."
    ),
    description="Analyzes research findings and extracts key insights.",
    output_key="analysis_summary",
)

# --- 3. Report agent — reads both keys, writes final_report ---
report_agent = LlmAgent(
    name="ReportGenerator",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You are a professional report writer. "
        "Write a concise 3-sentence executive summary based on:\n\n"
        "Research:\n{research_data}\n\n"
        "Analysis:\n{analysis_summary}\n\n"
        "Output only the summary."
    ),
    description="Generates a final executive summary from research and analysis.",
    output_key="final_report",
)

# --- 4. Compose into a SequentialAgent pipeline ---
# SequentialAgent emits a DeprecationWarning as of ADK 2.6.x in favor of
# `Workflow`; see 21_workflow_graphs.py for the graph-based successor.
research_pipeline = SequentialAgent(
    name="ResearchPipeline",
    sub_agents=[ResearchAgent(), analysis_agent, report_agent],
    description="Runs research → analysis → report in sequence.",
)


async def run_pipeline() -> None:
    initial_state = {
        "research_topic": "AI technologies",
        "research_data": "",
        "analysis_summary": "",
        "final_report": "",
    }

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )
    runner = Runner(
        agent=research_pipeline,
        app_name=APP_NAME,
        session_service=session_service,
    )

    content = Content(role="user", parts=[Part(text="Run the research pipeline.")])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            text = event.content.parts[0].text
            if text and text.strip():
                print(f"\n[{event.author.upper()}]\n{text}")

    # Read structured results from shared session state
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    if session:
        print("\n--- Session State Results ---")
        if session.state.get("analysis_summary"):
            print(
                f"\nAnalysis (stored by AnalysisAgent):\n{session.state['analysis_summary']}"
            )
        if session.state.get("final_report"):
            print(
                f"\nFinal Report (stored by ReportGenerator):\n{session.state['final_report']}"
            )


print_new_section("Multi-Agent Research Pipeline")
print("Pipeline: ResearchAgent → AnalysisAgent → ReportGenerator\n")
asyncio.run(run_pipeline())
