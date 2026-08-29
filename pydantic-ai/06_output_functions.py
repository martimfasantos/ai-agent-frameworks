from dotenv import load_dotenv
from pydantic import BaseModel

from pydantic_ai import Agent, TextOutput

from settings import settings

load_dotenv()

"""
-----------------------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Output functions via output_type with callables
- TextOutput wrapper for post-processing plain text
- Multiple output functions for branching logic
- Combining output functions with structured models

Output functions let you define custom post-processing logic that runs
when the agent produces its final output. Unlike validators that reject
and retry, output functions transform the agent's raw output into your
desired format. TextOutput wraps a function that receives the agent's
text response and returns a processed result.

For more details, visit:
https://pydantic.dev/docs/ai/core-concepts/output/#output-functions
-----------------------------------------------------------------------
"""


# --------------------------------------------------------------
# Example 1: TextOutput for post-processing
# --------------------------------------------------------------
print("=== Example 1: TextOutput Post-Processing ===")


# --- 1. Define an output function that processes text ---
def word_count(text: str) -> dict:
    """Count words in the agent's response and return stats."""
    words = text.split()
    return {
        "text": text,
        "word_count": len(words),
        "char_count": len(text),
    }


# --- 2. Create agent with TextOutput ---
stats_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=TextOutput(word_count),
    instructions="Write a brief description of Python programming.",
)

# --- 3. Run and see processed output ---
result1 = stats_agent.run_sync("Describe Python in 2-3 sentences.")
print(f"Output: {result1.output}")
print(f"Type: {type(result1.output)}")
print()


# --------------------------------------------------------------
# Example 2: TextOutput for format conversion
# --------------------------------------------------------------
print("=== Example 2: TextOutput for Format Conversion ===")


# --- 1. Define a converter function ---
def to_uppercase_lines(text: str) -> list[str]:
    """Convert text to uppercase and split into lines."""
    return [line.strip().upper() for line in text.strip().split("\n") if line.strip()]


# --- 2. Create agent ---
format_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=TextOutput(to_uppercase_lines),
    instructions="List exactly 3 benefits of exercise, one per line. No numbering.",
)

result2 = format_agent.run_sync("What are the benefits of exercise?")
print(f"Output lines: {result2.output}")
print(f"Type: {type(result2.output)}")
print()


# --------------------------------------------------------------
# Example 3: Multiple output types with functions and models
# --------------------------------------------------------------
print("=== Example 3: Mixed Output Types ===")


class StructuredAnswer(BaseModel):
    """A structured answer with confidence."""

    answer: str
    confidence: float


def extract_keywords(text: str) -> list[str]:
    """Extract keywords from text (simple split-based approach)."""
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "and",
        "or",
    }
    words = text.lower().split()
    return list(
        set(
            w.strip(".,!?")
            for w in words
            if w.strip(".,!?") not in stop_words and len(w) > 2
        )
    )


# Agent can return either a structured model OR run the text through a function
mixed_agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    output_type=[StructuredAnswer, TextOutput(extract_keywords)],  # type: ignore
    instructions=(
        "If the user asks a factual question, respond with a structured answer "
        "including your confidence (0.0 to 1.0). "
        "For other requests, just respond with plain text."
    ),
)

# Factual question — likely returns StructuredAnswer
result3 = mixed_agent.run_sync("What is the capital of France?")
print(f"Factual output: {result3.output}")
print(f"Type: {type(result3.output).__name__}")
