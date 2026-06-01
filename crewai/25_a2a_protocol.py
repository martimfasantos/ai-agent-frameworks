import os

from crewai import Agent, Task, Crew
from crewai.a2a import A2AClientConfig

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- Agent-to-Agent (A2A) protocol for inter-agent communication
- A2AClientConfig for connecting to remote A2A-compatible agents
- Using remote agents as tools within a crew

A2A (Agent-to-Agent) is Google's open protocol that lets agents from
different frameworks communicate. CrewAI supports A2A natively:
- As a CLIENT: call remote A2A agents from within a crew
- As a SERVER: expose a crew as an A2A endpoint (see docs)

This example shows the client side — connecting to a remote A2A agent
and using it as a tool in your crew workflow.

For more details, visit:
https://docs.crewai.com/en/concepts/a2a
-------------------------------------------------------
"""


# --- 1. Configure an A2A remote agent connection ---
# This would connect to any A2A-compatible agent server (CrewAI, ADK, etc.)
# For demo purposes we show the config structure; replace with a real endpoint.
remote_math_agent = A2AClientConfig(
    endpoint="http://localhost:8000/.well-known/agent.json",
    timeout=30,
    max_turns=5,
    fail_fast=True,
)

# --- 2. Define a local agent that delegates to remote A2A agent ---
coordinator = Agent(
    role="Task Coordinator",
    goal="Coordinate tasks between local and remote agents",
    backstory=(
        "You coordinate complex workflows by delegating specialized tasks "
        "to the most appropriate agent, whether local or remote."
    ),
    llm=settings.OPENAI_MODEL_NAME,
    verbose=False,
)

local_writer = Agent(
    role="Technical Writer",
    goal="Write clear technical documentation",
    backstory="You specialize in making complex topics understandable.",
    llm=settings.OPENAI_MODEL_NAME,
    verbose=False,
)

# --- 3. Define tasks ---
# In a real setup, a task can target a remote A2A agent via the protocol
writing_task = Task(
    description="Write a brief explanation of the A2A protocol in 3 bullet points.",
    expected_output="3 concise bullet points explaining A2A.",
    agent=local_writer,
)


def main():
    print("=== A2A (Agent-to-Agent) Protocol Demo ===\n")
    print("A2A enables cross-framework agent communication:")
    print("  - CrewAI agents can call Google ADK, LangGraph, etc.")
    print("  - Any A2A server can be consumed as a remote tool")
    print("  - Protocol handles auth, streaming, and turn management\n")

    # Show the A2A client config
    print("A2A Client Config:")
    print(f"  endpoint: {remote_math_agent.endpoint}")
    print(f"  timeout:  {remote_math_agent.timeout}s")
    print(f"  max_turns: {remote_math_agent.max_turns}")
    print(f"  fail_fast: {remote_math_agent.fail_fast}\n")

    # Run the local crew (the A2A remote call requires a running server)
    crew = Crew(
        agents=[coordinator, local_writer],
        tasks=[writing_task],
        verbose=False,
    )

    result = crew.kickoff()
    print(f"Local result:\n{result.raw}\n")

    print("=== To expose this crew as an A2A server ===")
    print("from crewai.a2a import A2AServerConfig")
    print("server = A2AServerConfig(name='my-crew', skills=[...])")
    print("# Then run: crewai a2a serve")


if __name__ == "__main__":
    main()
