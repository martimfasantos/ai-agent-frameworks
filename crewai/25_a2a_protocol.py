import os

from crewai import Agent, Task, Crew

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- Agent-to-Agent (A2A) protocol concepts
- A2AClientConfig structure for connecting to remote agents
- A2AServerConfig structure for exposing crews as A2A endpoints

A2A (Agent-to-Agent) is Google's open protocol that lets agents from
different frameworks communicate. CrewAI supports A2A natively:
- As a CLIENT: call remote A2A agents from within a crew
- As a SERVER: expose a crew as an A2A endpoint

This example demonstrates A2A config structures and runs a local
crew that would coordinate with remote agents in production.

Requirements: pip install crewai[a2a] (installs a2a-sdk)

For more details, visit:
https://docs.crewai.com/en/concepts/a2a
-------------------------------------------------------
"""


def main():
    # --- 1. Show A2A Client Config structure ---
    # In production, this connects to any A2A-compatible agent server
    print("=== A2A (Agent-to-Agent) Protocol Demo ===\n")
    print("--- A2AClientConfig (connect TO remote agents) ---")
    print("  from crewai.a2a import A2AClientConfig")
    print("  remote_agent = A2AClientConfig(")
    print('      endpoint="http://remote-server/.well-known/agent.json",')
    print("      timeout=30,")
    print("      max_turns=5,")
    print("      fail_fast=True,")
    print("  )")
    print()

    # --- 2. Show A2A Server Config structure ---
    print("--- A2AServerConfig (expose crew AS an A2A endpoint) ---")
    print("  from crewai.a2a import A2AServerConfig")
    print("  server = A2AServerConfig(")
    print('      name="my-crew-server",')
    print('      description="A CrewAI agent exposed via A2A",')
    print('      version="1.0.0",')
    print("      skills=[...],")
    print("  )")
    print("  # Then run: crewai a2a serve")
    print()

    # --- 3. Run a local crew (simulating the coordinator pattern) ---
    print("--- Local Crew (coordinator pattern) ---\n")

    coordinator = Agent(
        role="Task Coordinator",
        goal="Coordinate tasks and summarize results",
        backstory="You coordinate workflows between specialized agents.",
        llm=settings.OPENAI_MODEL_NAME,
        verbose=False,
    )

    local_researcher = Agent(
        role="Local Researcher",
        goal="Research topics and provide factual summaries",
        backstory="You provide quick factual answers on any topic.",
        llm=settings.OPENAI_MODEL_NAME,
        verbose=False,
    )

    research_task = Task(
        description="Explain what the A2A protocol is and why it matters for multi-agent systems, in 3 bullet points.",
        expected_output="3 concise bullet points about A2A protocol.",
        agent=local_researcher,
    )

    crew = Crew(
        agents=[coordinator, local_researcher],
        tasks=[research_task],
        verbose=False,
    )

    result = crew.kickoff()
    print(f"Result:\n{result.raw}\n")

    print("=== A2A Integration Summary ===")
    print("- CrewAI crews can CALL remote A2A agents (any framework)")
    print("- CrewAI crews can BE CALLED by other A2A clients")
    print("- Protocol handles discovery, auth, streaming, and turns")
    print("- Enables cross-framework orchestration (CrewAI + ADK + LangGraph)")


if __name__ == "__main__":
    main()
