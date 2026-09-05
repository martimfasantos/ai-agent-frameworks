import asyncio
import os
from typing import Any

from openai.types.responses import (
    ResponseOutputMessage,
    ResponseOutputRefusal,
    ResponseOutputText,
)
from pydantic import BaseModel

from agents import (
    Agent,
    ModelResponse,
    RunErrorHandlerInput,
    RunErrorHandlerResult,
    Runner,
    Usage,
    function_tool,
)
from agents.models.interface import Model

from settings import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY.get_secret_value()

"""
-----------------------------------------------------------------------------
In this example, we explore OpenAI's Agents SDK with the following features:
- Runner.run(error_handlers={...}) for graceful recovery instead of exceptions
- All three handler kinds: max_turns, model_refusal, invalid_final_output
- RunErrorHandlerInput / RunErrorHandlerResult

By default a run that hits its turn limit, gets refused, or produces output
that fails its `output_type` raises. Error handlers let you convert each of
those into a usable final output, so a run degrades gracefully instead of
blowing up in the caller's face.

The refusal and invalid-output scenarios use a small scripted stub model so
they fire deterministically without depending on how the real model behaves.

For more details, visit:
https://openai.github.io/openai-agents-python/running_agents/
-----------------------------------------------------------------------------
"""


# --- 1. A scripted stub model, so the failure modes are deterministic ---
class ScriptedModel(Model):
    """Replays a canned model response — no API call, always the same output."""

    def __init__(self, output: list[Any]) -> None:
        self.output = output

    async def get_response(self, *args: Any, **kwargs: Any) -> ModelResponse:
        return ModelResponse(output=self.output, usage=Usage(requests=1), response_id=None)

    def stream_response(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("This stub is only used with Runner.run().")


def scripted_message(content: list[Any]) -> list[Any]:
    return [
        ResponseOutputMessage(
            id="msg_scripted",
            role="assistant",
            status="completed",
            type="message",
            content=content,
        )
    ]


# --- 2. Error handlers — each returns a usable final output ---
def on_max_turns(payload: RunErrorHandlerInput) -> RunErrorHandlerResult:
    print(f"  [handler] max_turns  <- {type(payload.error).__name__}: {payload.error}")
    print(f"  [handler] {len(payload.run_data.new_items)} item(s) produced before the limit")
    return RunErrorHandlerResult(
        final_output="I ran out of turns before finishing — ask again to continue."
    )


def on_model_refusal(payload: RunErrorHandlerInput) -> RunErrorHandlerResult:
    print(f"  [handler] model_refusal  <- {type(payload.error).__name__}: {payload.error}")
    return RunErrorHandlerResult(
        final_output="I can't help with that request, but I can answer product questions."
    )


class WeatherReport(BaseModel):
    city: str
    conditions: str


def on_invalid_final_output(payload: RunErrorHandlerInput) -> RunErrorHandlerResult:
    print(f"  [handler] invalid_final_output  <- {type(payload.error).__name__}")
    # The fallback must still satisfy the agent's output_type.
    return RunErrorHandlerResult(
        final_output=WeatherReport(city="unknown", conditions="unavailable")
    )


# --- 3. Scenario 1: turn limit reached on a real run ---
@function_tool
def lookup_order(order_id: str) -> str:
    """Look up the status of an order."""
    print(f"  [tool] lookup_order({order_id})")
    return f"Order {order_id}: shipped, arriving Friday."


async def scenario_max_turns() -> None:
    print("--- Scenario 1: max_turns (real model, max_turns=1) ---")
    agent = Agent(
        name="Support Agent",
        instructions="Look up the order with the tool, then summarise it in one sentence.",
        model=settings.OPENAI_MODEL_NAME,
        tools=[lookup_order],
    )

    # Turn 1 is consumed by the tool call, so summarising would need a second turn.
    result = await Runner.run(
        agent,
        "What's the status of order ORD-77?",
        max_turns=1,
        error_handlers={"max_turns": on_max_turns},
    )
    print(f"  Final output: {result.final_output}\n")


# --- 4. Scenario 2: the model refuses ---
async def scenario_model_refusal() -> None:
    print("--- Scenario 2: model_refusal (scripted refusal) ---")
    agent = Agent(
        name="Refusing Agent",
        instructions="You answer product questions.",
        model=ScriptedModel(
            scripted_message([ResponseOutputRefusal(refusal="I won't do that.", type="refusal")])
        ),
    )

    result = await Runner.run(
        agent,
        "Do something I am not allowed to ask for.",
        error_handlers={"model_refusal": on_model_refusal},
    )
    print(f"  Final output: {result.final_output}\n")


# --- 5. Scenario 3: output that does not match output_type ---
async def scenario_invalid_final_output() -> None:
    print("--- Scenario 3: invalid_final_output (scripted prose vs output_type) ---")
    agent = Agent(
        name="Weather Agent",
        instructions="Report the weather.",
        model=ScriptedModel(
            # Prose where a WeatherReport JSON object was required.
            scripted_message(
                [
                    ResponseOutputText(
                        text="It is sunny and warm.", type="output_text", annotations=[]
                    )
                ]
            )
        ),
        output_type=WeatherReport,
    )

    result = await Runner.run(
        agent,
        "What's the weather in Lisbon?",
        error_handlers={"invalid_final_output": on_invalid_final_output},
    )
    print(f"  Final output: {result.final_output}\n")


async def main() -> None:
    print("=== Error Handlers Example ===\n")
    await scenario_max_turns()
    await scenario_model_refusal()
    await scenario_invalid_final_output()
    print("=== Error Handlers Demo Complete ===")
    print("Every run returned a usable final output — none of them raised.")


if __name__ == "__main__":
    asyncio.run(main())
