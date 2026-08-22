from typing import Union

from dotenv import load_dotenv

from agno.agent import Agent
from agno.exceptions import InputCheckError
from agno.guardrails import BaseGuardrail
from agno.models.openai import OpenAIChat
from agno.run.agent import RunInput
from agno.run.team import TeamRunInput
from agno.utils.pprint import pprint_run_response

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Agno with the following features:
- Input guardrails using pre_hooks with BaseGuardrail
- Custom guardrail class that validates user input
- InputCheckError to block disallowed requests
- Multiple guardrails chained together

Guardrails protect agents from processing harmful or
out-of-scope requests. They run as pre-hooks before the
agent processes input. If a guardrail raises InputCheckError,
the agent stops and returns the error message instead of
calling the LLM.

For more details, visit:
https://docs.agno.com/agents/guardrails
-------------------------------------------------------
"""


# --- 1. Define custom guardrails ---
class ContentPolicyGuardrail(BaseGuardrail):
    """Blocks requests containing disallowed topics."""

    blocked_keywords = ["hack", "exploit", "steal", "illegal"]

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        content = str(run_input.input_content).lower()
        for keyword in self.blocked_keywords:
            if keyword in content:
                raise InputCheckError(
                    f"Request blocked: contains disallowed keyword '{keyword}'."
                )

    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        self.check(run_input)


class LengthGuardrail(BaseGuardrail):
    """Blocks excessively long input to prevent prompt injection attempts."""

    max_length = 500

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        content = str(run_input.input_content)
        if len(content) > self.max_length:
            raise InputCheckError(
                f"Request blocked: input too long ({len(content)} chars, max {self.max_length})."
            )

    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        self.check(run_input)


# --- 2. Create the agent with guardrails ---
agent = Agent(
    model=OpenAIChat(id=settings.OPENAI_MODEL_NAME),
    pre_hooks=[ContentPolicyGuardrail(), LengthGuardrail()],
    instructions="You are a helpful assistant that answers general knowledge questions.",
    markdown=True,
)

# --- 3. Test with a valid request ---
print("=== Test 1: Valid request ===\n")
try:
    run_output = agent.run("What is the capital of Portugal?")
    pprint_run_response(run_output)
except InputCheckError as e:
    print(f"Blocked: {e}")

# --- 4. Test with a blocked request ---
print("\n=== Test 2: Blocked request (disallowed keyword) ===\n")
try:
    run_output = agent.run("How can I hack into a computer?")
    pprint_run_response(run_output)
except InputCheckError as e:
    print(f"Blocked: {e}")

# --- 5. Test with an overly long request ---
print("\n=== Test 3: Blocked request (too long) ===\n")
try:
    long_input = "Tell me about Portugal. " * 50  # ~600 chars
    run_output = agent.run(long_input)
    pprint_run_response(run_output)
except InputCheckError as e:
    print(f"Blocked: {e}")
