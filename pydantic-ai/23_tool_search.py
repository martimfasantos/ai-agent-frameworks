from dotenv import load_dotenv

from pydantic_ai import Agent, Tool

from settings import settings

load_dotenv()

"""
-------------------------------------------------------
In this example, we explore Pydantic AI with the following features:
- Tool Search for large toolsets with deferred loading
- Tool.defer_loading to hide tools until discovered via search
- Native provider tool search (Anthropic/OpenAI) with fallback

When an agent has many tools, sending all of them to the model
on every request wastes context and can confuse the model. Tool
Search lets you mark tools as deferred — they become available
only after the model discovers them via a search function. On
providers that support native tool search (Anthropic, OpenAI),
the discovery is handled server-side for optimal performance.

For more details, visit:
https://ai.pydantic.dev/tools-toolsets/toolsets/
-------------------------------------------------------
"""


# --- 1. Define a large set of specialized tools ---
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    data = {"lisbon": "Sunny, 26°C", "london": "Cloudy, 15°C", "tokyo": "Rainy, 20°C"}
    return data.get(city.lower(), f"No weather data for {city}")


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert between currencies."""
    rates = {"USD_EUR": 0.92, "EUR_USD": 1.09, "USD_GBP": 0.79, "GBP_USD": 1.27}
    key = f"{from_currency.upper()}_{to_currency.upper()}"
    rate = rates.get(key, 1.0)
    return f"{amount} {from_currency} = {amount * rate:.2f} {to_currency}"


def translate_text(text: str, target_language: str) -> str:
    """Translate text to a target language (simulated)."""
    translations = {
        "hello_spanish": "Hola",
        "hello_french": "Bonjour",
        "goodbye_spanish": "Adiós",
    }
    key = f"{text.lower()}_{target_language.lower()}"
    return translations.get(key, f"[Translated '{text}' to {target_language}]")


def calculate_tip(bill_amount: float, tip_percentage: float = 18.0) -> str:
    """Calculate tip amount for a restaurant bill."""
    tip = bill_amount * (tip_percentage / 100)
    return f"Bill: ${bill_amount:.2f}, Tip ({tip_percentage}%): ${tip:.2f}, Total: ${bill_amount + tip:.2f}"


def get_time_zone(city: str) -> str:
    """Get the timezone for a city."""
    zones = {"lisbon": "WET (UTC+0)", "new york": "EST (UTC-5)", "tokyo": "JST (UTC+9)"}
    return zones.get(city.lower(), f"Unknown timezone for {city}")


# --- 2. Create agent with deferred tools ---
# Only get_weather is immediately visible to the model.
# The other tools require discovery via tool search.
agent = Agent(
    model=settings.OPENAI_MODEL_NAME,
    instructions="You are a helpful assistant. Be concise, reply in 1-2 sentences. Use your tools when relevant.",
    tools=[
        Tool(get_weather, defer_loading=False),  # Always visible
        Tool(convert_currency, defer_loading=True),  # Deferred - needs search
        Tool(translate_text, defer_loading=True),  # Deferred - needs search
        Tool(calculate_tip, defer_loading=True),  # Deferred - needs search
        Tool(get_time_zone, defer_loading=True),  # Deferred - needs search
    ],
)

# --- 3. Run queries that use visible and deferred tools ---
print("=== Tool Search: Deferred Loading ===")
print()

# Query using always-visible tool
result = agent.run_sync("What's the weather in Lisbon?")
print(f"Q: What's the weather in Lisbon?")
print(f"A: {result.output}")
print()

# Query that requires discovering a deferred tool
result = agent.run_sync("Convert 100 USD to EUR")
print(f"Q: Convert 100 USD to EUR")
print(f"A: {result.output}")
print()

# Another deferred tool query
result = agent.run_sync("Calculate the tip on a $85 bill at 20%")
print(f"Q: Calculate the tip on a $85 bill at 20%")
print(f"A: {result.output}")
print()

# --- 4. Show tool configuration ---
print("=== Tool Configuration ===")
print("  get_weather:      defer_loading=False (always visible)")
print("  convert_currency: defer_loading=True  (discovered via search)")
print("  translate_text:   defer_loading=True  (discovered via search)")
print("  calculate_tip:    defer_loading=True  (discovered via search)")
print("  get_time_zone:    defer_loading=True  (discovered via search)")
