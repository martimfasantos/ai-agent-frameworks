import os

from crewai import Agent, Task, Crew
from crewai.events import (
    BaseEventListener,
    CrewKickoffStartedEvent,
    CrewKickoffCompletedEvent,
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    ToolUsageStartedEvent,
    ToolUsageFinishedEvent,
    FlowFailedEvent,
)
from crewai.flow import Flow, start

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- Custom event listeners using BaseEventListener
- Listening to crew, agent, task, and tool events
- FlowFailedEvent, emitted when a flow raises
- Real-time monitoring and logging of crew execution

Event listeners provide a powerful way to monitor and react to
events during crew execution. You can track when crews start/stop,
agents begin/finish, tasks complete, and tools are used.

For more details, visit:
https://docs.crewai.com/en/concepts/event-listener
-------------------------------------------------------
"""


# --- 1. Create a custom event listener ---
class ExecutionMonitor(BaseEventListener):
    """Monitors crew execution and logs key events."""

    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(CrewKickoffStartedEvent)
        def on_crew_start(source, event):
            print("[MONITOR] Crew execution started")

        @crewai_event_bus.on(CrewKickoffCompletedEvent)
        def on_crew_complete(source, event):
            print("[MONITOR] Crew execution completed")

        @crewai_event_bus.on(AgentExecutionStartedEvent)
        def on_agent_start(source, event):
            print(f"[MONITOR] Agent started: {event.agent.role}")

        @crewai_event_bus.on(AgentExecutionCompletedEvent)
        def on_agent_complete(source, event):
            print(f"[MONITOR] Agent completed: {event.agent.role}")

        @crewai_event_bus.on(TaskStartedEvent)
        def on_task_start(source, event):
            print(f"[MONITOR] Task started: {event.task.description[:50]}...")

        @crewai_event_bus.on(TaskCompletedEvent)
        def on_task_complete(source, event):
            print(f"[MONITOR] Task completed: {event.task.description[:50]}...")

        @crewai_event_bus.on(ToolUsageStartedEvent)
        def on_tool_start(source, event):
            print(f"[MONITOR] Tool usage started: {event.tool_name}")

        @crewai_event_bus.on(ToolUsageFinishedEvent)
        def on_tool_finish(source, event):
            print(f"[MONITOR] Tool usage finished: {event.tool_name}")

        @crewai_event_bus.on(FlowFailedEvent)
        def on_flow_failed(source, event):
            print(f"[MONITOR] Flow failed: {event.flow_name} - {event.error}")


# --- 2. Instantiate the listener (registration happens automatically) ---
monitor = ExecutionMonitor()

# --- 3. Create agents and tasks ---
agent = Agent(
    role="Researcher",
    goal="Research and summarize information",
    backstory="You are a skilled researcher.",
    llm=settings.OPENAI_MODEL_NAME,
    verbose=True,
)

task = Task(
    description="Provide a brief summary of the Python programming language.",
    expected_output="A short paragraph summarizing Python.",
    agent=agent,
)

# --- 4. Create and run the crew ---
crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True,
)

result = crew.kickoff()
# The monitor will print event logs as the crew executes


# --- 5. A flow that raises, so FlowFailedEvent has something to report ---
class FailingFlow(Flow):
    @start()
    def break_early(self) -> None:
        raise RuntimeError("simulated flow failure")


try:
    FailingFlow().kickoff()
except RuntimeError as error:
    print(f"Flow raised: {error}")
