from dotenv import load_dotenv
from pydantic import BaseModel

from pydantic_ai import Agent, RunContext, ModelRetry

from utils import show_metrics
from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Output validators with @agent.output_validator decorator
- Automatic retry logic with ModelRetry exceptions
- Rule validation against a simulated database
- Partial output validation during streaming

This example demonstrates how to implement output validation with Pydantic AI,
both for full outputs and partial outputs.
Output validators ensure that AI-generated content meets pre-defined rules
and constraints. The agent automatically retries when validation fails,
prompting the model to generate a valid output based on the validation feedback.

For more details, visit:
https://ai.pydantic.dev/output/#output-validator
-----------------------------------------------------------------------
"""

# ----------------------------------------------
# Example 1: Full Output Validation
# ----------------------------------------------


# --- 1. Define output model ---
class UserProfile(BaseModel):
    username: str
    email: str
    age: int


# --- 2. Simulated database with existing users ---
class FakeDatabase:
    existing_usernames = {"admin", "user", "test"}
    existing_emails = {"admin@test.com", "user@test.com"}


# --- 3. Create agent with output type ---
profile_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=UserProfile,
    instructions="Extract user profile information from the text.",
)


# --- 4. Add output validator to check against database ---
@profile_agent.output_validator
def validate_user_profile(ctx: RunContext, output: UserProfile) -> UserProfile:
    """Validate that username and email are not already taken."""

    # Check if username exists
    if output.username.lower() in FakeDatabase.existing_usernames:
        raise ModelRetry(
            f'Username "{output.username}" is already taken. '
            "Please suggest a different username."
        )

    # Add more validation rules as needed...

    return output


# --- 5. Run the examples ---
def run_full_output_validation_examples():

    # 5.1. Test with valid data (should succeed)
    print("=== Test 1: Valid User ===")
    result1 = profile_agent.run_sync(
        "Create a profile for newuser with email new@example.com, age 25"
    )
    print(f"Output: {result1.output}")
    print(f"Username: {result1.output.username}")
    print(f"Email: {result1.output.email}")
    print("\n" + "-" * 50)

    """
    Expected output:
        username='newuser' email='new@example.com' age=25
    """

    # 5.2. Test with existing username (should retry and find alternative)
    print("\n=== Test 2: Existing Username (will retry) ===")
    result2 = profile_agent.run_sync(
        "Register user 'admin' with email fresh@example.com, age 30"
    )
    print(f"Output: {result2.output}")
    print(f"New username suggested: {result2.output.username}")
    print("\n" + "-" * 50)

    """
    Expected behavior:
        - Agent tries 'admin' but validator rejects it
        - ModelRetry asks agent to suggest different username
        - Agent suggests alternative like 'admin123' or 'admin_user'
    """

    # 5.3. Show usage metrics to see retries
    show_metrics(result2.usage)

    # NOTE: When validation fails, the agent makes multiple requests.
    # You'll see requests > 1 when ModelRetry is triggered.


# ----------------------------------------------
# Example 2: Partial Output Validation
# ----------------------------------------------

# --- 1. Create agent ---
partial_agent = Agent(model=settings.OPENAI_MODEL_NAME)


# --- 2. Add partial output validator ---
@partial_agent.output_validator
def validate_output(ctx: RunContext, output: str) -> str:
    if ctx.partial_output:  # If partial output, accept as is
        return output
    else:  # Full output - apply rule
        if len(output) < 50:
            raise ModelRetry("Output is too short.")
        return output


# --- 3. Run the example ---
async def run_partial_output_validation_example():
    async with partial_agent.run_stream("Write a long story about a cat") as result:
        async for message in result.stream_text():
            print(message)
            # > Once upon a
            # > Once upon a time, there was
            # > Once upon a time, there was a curious cat
            # > Once upon a time, there was a curious cat named Whiskers who ...


if __name__ == "__main__":
    run_full_output_validation_examples()
    import asyncio

    asyncio.run(run_partial_output_validation_example())
