import os
from collections import Counter

from crewai import Agent, Crew, LLM, Task
from crewai.flow import Flow, start
from crewai.tools import tool

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-------------------------------------------------------
In this example, we explore CrewAI with the following features:
- LLM.stream_events() for token frames straight off a model call
- Flow.stream_events() for a whole run's frames
- The StreamSession context manager and stream.result
- Channel projections: stream.llm, stream.tools, stream.interleave([...])

Frame streaming is the newer streaming surface: every runtime event is
normalised into a StreamFrame carrying a channel (llm, flow, tools, messages,
lifecycle, custom), a namespace and the source payload, so a consumer filters
by channel instead of subscribing to individual event classes. The older
surface - an event listener on LLMStreamChunkEvent - is still shown in
09_streaming.py; reach for frame streaming for new runtime integrations.

For more details, visit:
https://docs.crewai.com/en/learn/consuming-streams
-------------------------------------------------------
"""

# --- 1. Stream token frames from a single LLM call ---
print("=== 1. LLM.stream_events() -> stream.llm ===")

llm = LLM(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    temperature=0,
)

llm_stream = llm.stream_events("In one sentence, what is a stream frame?")
with llm_stream:
    for frame in llm_stream.llm:
        # frame.content is the token text for chunk frames, "" for the rest
        print(frame.content, end="", flush=True)

print(f"\nresult: {llm_stream.result}")


# --- 2. A flow step that runs a crew with a tool ---
@tool("lookup_release_date")
def lookup_release_date(version: str) -> str:
    """Looks up the release date of a CrewAI version."""
    dates = {"1.15.2": "2026-01-14", "1.15.11": "2026-02-03"}
    return dates.get(version, f"No release date on record for {version}")


reporter = Agent(
    role="Release Reporter",
    goal="Report release dates using the lookup tool",
    backstory="You always use the lookup tool and answer in one short sentence.",
    tools=[lookup_release_date],
    llm=settings.OPENAI_MODEL_NAME,
)


class ReleaseFlow(Flow):
    @start()
    def report(self) -> str:
        task = Task(
            description="When was CrewAI 1.15.2 released?",
            expected_output="One sentence with the release date.",
            agent=reporter,
        )
        return Crew(agents=[reporter], tasks=[task]).kickoff().raw


# --- 3. Stream the flow, interleaving two channels in emission order ---
print("\n=== 2. Flow.stream_events() -> stream.interleave(['flow', 'tools']) ===")

flow_stream = ReleaseFlow().stream_events()
with flow_stream:
    for frame in flow_stream.interleave(["flow", "tools"]):
        print(f"[{frame.channel}] seq={frame.seq} {frame.type} ns={'/'.join(frame.namespace)}")

# --- 4. Frames stay buffered once consumed, so channels can be counted after ---
channels = Counter(frame.channel for frame in flow_stream.frames)
print(f"\nframes by channel: {dict(channels)}")
print(f"result: {flow_stream.result}")
