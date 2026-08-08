import asyncio
from typing import Any, Dict, List

from pydantic import BaseModel

from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.core.agent.workflow.workflow_events import (
    AgentOutput,
    AgentStreamStructuredOutput,
)
from llama_index.core.base.llms.types import ChatMessage
from llama_index.llms.openai import OpenAI

from settings import settings


"""
-------------------------------------------------------
In this example, we explore LlamaIndex with the following features:
- Pydantic models for structured data validation
- Structured LLMs for enforcing output schemas
- Agent-level structured output with output_cls
- Custom structured output with structured_output_fn
- Streaming structured output via AgentStreamStructuredOutput

Structured outputs ensure that agent responses conform to a specific schema,
enabling type-safe integration with downstream systems. `output_cls` lets the
framework do the extraction, while `structured_output_fn` hands you the chat
history so you can parse it yourself (the two are mutually exclusive —
`output_cls` wins). Either way the result is emitted on the event stream as an
AgentStreamStructuredOutput, so a UI can render it before the run finishes.

For more details, visit:
https://developers.llamaindex.ai/python/framework/understanding/agent/structured_output/
-------------------------------------------------------
"""

# --- 1. Define the structured output models ---
class Song(BaseModel):
    """Data model for a song."""
    title: str
    length_seconds: int


# --- 2. Create the LLM and Structured LLM ---
# 2.1 Create the base LLM
llm = OpenAI(
    model=settings.OPENAI_MODEL_NAME,
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
)
# 2.2 Create the structured LLM with Song output schema
sllm = llm.as_structured_llm(output_cls=Song)

# --- 3. Create the agent with structured output schema ---
agent = ReActAgent(
    name="music_agent",
    description="A simple music agent.",
    system_prompt=(
        "Name one specific real song by the requested artist and its length in "
        "seconds. Answer with the song title, not the word 'song'."
    ),
    llm=llm,  # use the normal LLM
    output_cls=Song,  # enforce structured output at the agent level
)


# --- 4. Custom structured output with structured_output_fn ---
# Instead of letting the agent extract the schema, we get the whole chat history
# and decide ourselves how to turn it into structured data. The callback may be
# sync or async and returns a dict (or a BaseModel).
async def extract_song(messages: List[ChatMessage]) -> Dict[str, Any]:
    """Parse the conversation into a Song, defaulting the length if unstated."""
    transcript = "\n".join(str(m.content) for m in messages if m.content)
    parsed = await sllm.acomplete(
        f"Extract the song discussed in this conversation.\n\n{transcript}"
    )
    song: Song = parsed.raw
    return song.model_dump()


custom_agent = FunctionAgent(
    name="custom_music_agent",
    description="A music agent that post-processes its own transcript.",
    system_prompt="Name one song by the requested artist, in one sentence.",
    llm=llm,
    structured_output_fn=extract_song,
)


# --- 5. Run the agents and the structured LLM ---
async def main():
    # 5.1 Agent with output_cls
    print("=== Agent with output_cls ===")
    response: AgentOutput = await agent.run("Suggest a song by Don Toliver.")
    print("Structured response:", response.structured_response)
    print("As a Song object:", response.get_pydantic_model(Song))

    # 5.2 Agent with structured_output_fn, consuming the structured stream event
    print("\n=== Agent with structured_output_fn (streamed) ===")
    handler = custom_agent.run("Suggest a song by Tame Impala.")
    async for event in handler.stream_events():
        if isinstance(event, AgentStreamStructuredOutput):
            print("Streamed structured output:", event.output)
    response = await handler
    print("Final text:", str(response).strip())
    print("As a Song object:", response.get_pydantic_model(Song))

    # 5.3 Structured LLM used directly, without an agent
    print("\n=== Structured LLM directly ===")
    output = sllm.complete("Suggest a song by Don Toliver.")
    output_obj: Song = output.raw
    print("Is output of type Song?", isinstance(output_obj, Song))
    print(output_obj)


if __name__ == "__main__":
    asyncio.run(main())
