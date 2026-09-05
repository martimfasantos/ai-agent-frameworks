import os
import asyncio

from google.adk.agents import LlmAgent, ParallelAgent, LoopAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.tool_context import ToolContext

from settings import settings
from utils import call_agent_async, print_new_section

os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore Google ADK with the following features:
- SequentialAgent: running sub-agents in a fixed order with state passing
- LoopAgent: iterative refinement with an exit condition tool
- ParallelAgent: running sub-agents concurrently for independent tasks

Workflow agents in ADK orchestrate other agents without using an LLM for
routing decisions. SequentialAgent runs agents one after another, passing
shared state. LoopAgent repeats a pipeline until a condition is met.
ParallelAgent runs agents simultaneously to reduce latency on independent work.

For more details, visit:
https://google.github.io/adk-docs/agents/workflow-agents/
-------------------------------------------------------
"""

# Note: since ADK 2.6.x all three classes below emit a DeprecationWarning naming
# `Workflow` as their successor. They still work, and they remain the most direct
# way to show the three orchestration shapes. See 21_workflow_graphs.py for the
# same patterns expressed as a Workflow graph.


# ----------------------------------------------------------------
#                    1. Sequential Agent
# ----------------------------------------------------------------
# Runs sub-agents in order: Writer -> Reviewer -> Refactorer
# Each agent stores output in state via output_key for the next agent to read.
# https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/

code_writer_agent = LlmAgent(
    name="code_writer_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You are a Python code generator. "
        "Write a Python function that fulfills the user's request. "
        "Output only the code block enclosed in triple backticks."
    ),
    description="Writes initial Python code from a specification.",
    output_key="generated_code",
)

code_reviewer_agent = LlmAgent(
    name="code_reviewer_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You are an expert Python code reviewer. "
        "Review this code:\n```python\n{generated_code}\n```\n"
        "Provide 2-3 bullet points of feedback. "
        "If no issues, reply exactly: 'No major issues found.'"
    ),
    description="Reviews code and provides concise feedback.",
    output_key="review_comments",
)

code_refactorer_agent = LlmAgent(
    name="code_refactorer_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You are a Python code refactorer. "
        "Apply these review comments to improve the code:\n"
        "Code:\n```python\n{generated_code}\n```\n"
        "Comments: {review_comments}\n"
        "If comments say 'No major issues found.', return the original code unchanged. "
        "Output only the final code block."
    ),
    description="Refactors code based on review comments.",
    output_key="refactored_code",
)

code_pipeline_agent = SequentialAgent(
    name="code_pipeline_agent",
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
    description="Writes, reviews, and refactors code sequentially.",
)

# --- Run Sequential Agent ---
print_new_section("1. Sequential Agent")
query = "Write a Python function that computes the nth Fibonacci number."
print(f"Query: {query}")
asyncio.run(call_agent_async(code_pipeline_agent, query))
print("\n" + "-" * 50 + "\n")


# ----------------------------------------------------------------
#                    2. Loop Agent
# ----------------------------------------------------------------
# Runs sub-agents in a loop until the exit_loop tool is called.
# Pattern: Critic -> Refiner (calls exit_loop when satisfied).
# https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/


def exit_loop(tool_context: ToolContext) -> dict:
    """Call this only when the critique says no further changes are needed."""
    print(f"  [exit_loop] Triggered by {tool_context.agent_name} — stopping loop.")
    tool_context.actions.escalate = True
    return {}


initial_writer_agent = LlmAgent(
    name="initial_writer_agent",
    model=settings.GOOGLE_MODEL_NAME,
    include_contents="none",
    instruction=(
        "You are a creative writing assistant. "
        "Write a 2-4 sentence story draft on this topic: {initial_topic}. "
        "Output only the story text."
    ),
    description="Writes the initial story draft.",
    output_key="current_document",
)

critic_agent_in_loop = LlmAgent(
    name="critic_agent_in_loop",
    model=settings.GOOGLE_MODEL_NAME,
    include_contents="none",
    instruction=(
        "You are a constructive critic reviewing a short story:\n"
        "```\n{current_document}\n```\n"
        "The story must include the main character's name and age. "
        "If you see 1-2 clear improvements needed, state them briefly. "
        "If it is adequate, reply exactly: 'No major issues found.'"
    ),
    description="Critiques the story draft.",
    output_key="criticism",
)

refiner_agent_in_loop = LlmAgent(
    name="refiner_agent_in_loop",
    model=settings.GOOGLE_MODEL_NAME,
    include_contents="none",
    instruction=(
        "You are a creative writing refiner. "
        "Current story:\n```\n{current_document}\n```\n"
        "Critique: {criticism}\n"
        "If the critique is exactly 'No major issues found.', call exit_loop. "
        "Otherwise, apply the suggestions and output only the improved story."
    ),
    description="Refines the story or exits the loop.",
    tools=[exit_loop],
    output_key="current_document",
)

refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[critic_agent_in_loop, refiner_agent_in_loop],
    max_iterations=3,
)

loop_pipeline_agent = SequentialAgent(
    name="iterative_writing_pipeline",
    sub_agents=[initial_writer_agent, refinement_loop],
    description="Writes and iteratively refines a story.",
)

# --- Run Loop Agent ---
print_new_section("2. Loop Agent")
query = "Write a short story about a robot learning to love."
print(f"Query: {query}")
asyncio.run(
    call_agent_async(
        loop_pipeline_agent, query, tool_calls=True, state={"initial_topic": query}
    )
)
print("\n" + "-" * 50 + "\n")


# ----------------------------------------------------------------
#                    3. Parallel Agent
# ----------------------------------------------------------------
# Runs two researcher agents concurrently, then merges results.
# https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/

researcher_agent_1 = LlmAgent(
    name="renewable_energy_researcher",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You are an energy research assistant. "
        "Search for the latest renewable energy advancements. "
        "Summarize in 1-2 sentences. Output only the summary."
    ),
    description="Researches renewable energy sources.",
    tools=[google_search],
    output_key="renewable_energy_result",
)

researcher_agent_2 = LlmAgent(
    name="ev_technology_researcher",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "You are a transportation research assistant. "
        "Search for the latest electric vehicle technology developments. "
        "Summarize in 1-2 sentences. Output only the summary."
    ),
    description="Researches electric vehicle technology.",
    tools=[google_search],
    output_key="ev_technology_result",
)

parallel_research_agent = ParallelAgent(
    name="parallel_research_agent",
    sub_agents=[researcher_agent_1, researcher_agent_2],
    description="Runs multiple research agents concurrently.",
)

merger_agent = LlmAgent(
    name="synthesis_agent",
    model=settings.GOOGLE_MODEL_NAME,
    instruction=(
        "Synthesize these two research summaries into a brief combined report (4-6 sentences). "
        "Renewable Energy: {renewable_energy_result}\n"
        "Electric Vehicles: {ev_technology_result}\n"
        "Base your response only on the provided summaries."
    ),
    description="Merges parallel research results into one report.",
)

sequential_pipeline_agent = SequentialAgent(
    name="research_and_synthesis_pipeline",
    sub_agents=[parallel_research_agent, merger_agent],
    description="Runs parallel research then synthesizes the results.",
)

# --- Run Parallel Agent ---
print_new_section("3. Parallel Agent")
query = "Research the latest sustainable technology advancements."
print(f"Query: {query}")
asyncio.run(call_agent_async(sequential_pipeline_agent, query, tool_calls=True))
