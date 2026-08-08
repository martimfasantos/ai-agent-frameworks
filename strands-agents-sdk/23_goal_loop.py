from strands import Agent
from strands.models.openai import OpenAIModel
from strands.types.content import Message
from strands.vended_plugins.goal import GoalLoop, ValidationOutcome

from settings import settings

"""
-------------------------------------------------------
In this example, we explore Strands Agents SDK with the following features:
- GoalLoop, the iterative-refinement plugin (new in v1.44.0)
- A natural-language goal judged by an auto-built LLM judge
- A programmatic validator returning a ValidationOutcome
- Inspecting GoalResult: passed, stop_reason, and per-attempt feedback

GoalLoop wraps an invocation in a validate-and-retry loop: the response is
checked against the goal and, if it fails, the agent is re-prompted with the
feedback until it passes or max_attempts runs out. The judge reuses the host
agent's model, so no extra provider is needed.

For more details, visit:
https://strandsagents.com/docs/user-guide/concepts/plugins/goal-loop/
-------------------------------------------------------
"""

openai_model = OpenAIModel(
    client_args={
        "api_key": settings.OPENAI_API_KEY.get_secret_value()
        if settings.OPENAI_API_KEY
        else ""
    },
    model_id=settings.OPENAI_MODEL_NAME,
)


def text_of(message: Message) -> str:
    """Concatenate the text blocks of a message."""
    return "".join(block.get("text", "") for block in message.get("content", []))


def report(loop: GoalLoop, agent: Agent) -> None:
    """Print the GoalResult of the most recent run."""
    result = loop.last_result(agent)
    print(f"  passed: {result.passed}  stop_reason: {result.stop_reason}")
    for attempt in result.attempts:
        print(f"  attempt {attempt.attempt}: passed={attempt.passed} feedback={attempt.feedback}")


print("=== Goal Loop: Validate and Retry ===\n")

# --- 1. A natural-language goal, judged by the model ---
print("--- Natural-language goal (LLM judge) ---")
judged_loop = GoalLoop(
    goal="The answer must be a single sentence of at most 15 words.",
    max_attempts=3,
)
judged_agent = Agent(
    model=openai_model,
    system_prompt="You are a travel writer.",
    plugins=[judged_loop],
    callback_handler=None,
)

result = judged_agent("Give me reasons to visit Lisbon.")
print(f"Response:\n{text_of(result.message)}")
report(judged_loop, judged_agent)
print()


# --- 2. A programmatic validator instead of a judge ---
def ends_with_marker(response: Message, agent: Agent, **kwargs) -> ValidationOutcome:
    """Require the response to end with the literal marker [verified]."""
    body = text_of(response).strip()
    if body.endswith("[verified]"):
        return ValidationOutcome(passed=True)
    return ValidationOutcome(
        passed=False,
        feedback="The response must end with the exact literal marker [verified].",
    )


print("--- Programmatic validator ---")
validated_loop = GoalLoop(goal=ends_with_marker, max_attempts=3)
validated_agent = Agent(
    model=openai_model,
    system_prompt="You are a concise assistant. Answer in one sentence.",
    plugins=[validated_loop],
    callback_handler=None,
)

# The prompt never mentions the marker, so the first attempt fails and the loop retries.
result = validated_agent("What is the capital of Portugal?")
print(f"Response: {text_of(result.message)}")
report(validated_loop, validated_agent)
print()

# --- 3. Summary ---
print("--- Summary ---")
print("goal=<str>      -> an internal judge agent scores the response (host agent's model)")
print("goal=<callable> -> your own validator; may return bool, dict, or ValidationOutcome")
print("stop_reason: 'satisfied' | 'max_attempts' | 'timeout'")
print("Other knobs: timeout, preserve_context=False to discard failed attempts,")
print("resume_prompt_template to reword the retry prompt.")
