# Google ADK - Example Outputs

> All examples require a valid `GOOGLE_API_KEY` in `.env`. The Gemini free tier
> has a 20 requests/day limit per model — run examples individually to avoid
> 429 RESOURCE_EXHAUSTED errors.

---

## 16. Transfer Control (`16_transfer_control.py`)

```
$ uv run python 16_transfer_control.py

=== User asks a billing question ===
[billing_agent]: I can definitely help you look into your last invoice. To understand what
might be wrong, could you please tell me more about it?

For example:
*   What specifically seems incorrect? (e.g., the total amount, a specific item charged,
    a discount missing, a duplicate charge, an incorrect date?)
*   Do you have the invoice number or the date it was issued?

Once I have a bit more detail, I can guide you on the next steps to resolve this!

=== Transfer control summary ===
billing_agent:   disallow_transfer_to_parent=True,  disallow_transfer_to_peers=True
                 -> Terminal agent, must handle request fully
technical_agent: disallow_transfer_to_parent=False, disallow_transfer_to_peers=True
                 -> Can escalate back to triage, but not to billing
```

> Transfer control restrictions (new in ADK v2) prevent agents from escalating
> or laterally transferring when they should handle the request themselves.
> `disallow_transfer_to_parent=True` makes an agent terminal (must resolve locally),
> while `disallow_transfer_to_peers=True` prevents cross-agent handoffs.

**Verdict:** PASS - billing_agent handles request without escalation; transfer restrictions enforced.

---

## 17. Code Executor (`17_code_executor.py`)

```
$ uv run python 17_code_executor.py

=== Math with code execution ===
[math_agent]: To find the sum of the first 100 prime numbers, I will write a Python script that:
1. Defines a function to check if a number is prime.
2. Iterates through numbers, checking for primality, until 100 prime numbers are found.
3. Sums these prime numbers.

--- Generated Code ---
import math

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def sum_first_n_primes(n_primes):
    primes = []
    num = 2
    while len(primes) < n_primes:
        if is_prime(num):
            primes.append(num)
        num += 1
    return sum(primes)

num_to_find = 100
result = sum_first_n_primes(num_to_find)
print(f"The sum of the first {num_to_find} prime numbers is: {result}")

--- End Code ---

--- Execution Result ---
Code execution result:
The sum of the first 100 prime numbers is: 24133

--- End Result ---

[math_agent]: The sum of the first 100 prime numbers is 24133.
```

> UnsafeLocalCodeExecutor (new in ADK v2) lets agents generate and execute Python
> code locally. Requires `artifact_service=InMemoryArtifactService()` in the Runner.
> The agent writes code, executes it, and returns the result — enabling complex
> computations that can't be done in a single LLM call.

**Verdict:** PASS - Agent generates Python code, executes it locally, returns correct result (24133).

---

## 18. Planners (`18_planners.py`)

```
$ uv run python 18_planners.py

==================================================
=== With PlanReActPlanner ===
==================================================
Query: I want to travel from London to Tokyo. Check the weather in Tokyo, find me a
flight, and suggest a mid-range hotel.

[travel_planner]: /*PLANNING*/
1. Get the current weather for Tokyo using the `get_weather` tool.
2. Get available flights from London to Tokyo using the `get_flights` tool.
3. Get hotel recommendations for Tokyo with a "mid-range" budget using the `get_hotels` tool.
4. Combine all the information and provide a final answer.

[travel_planner]: /*REASONING*/
The weather in Tokyo is rainy, 18C, with 85% humidity. Now, let's find the flights
from London to Tokyo.

/*ACTION*/
[travel_planner]: /*REASONING*/
A flight from London to Tokyo is available for $450, departing at 9:00 AM and arriving
at 2:00 PM. Now, let's find hotel recommendations for Tokyo with a "mid-range" budget.

/*ACTION*/
[travel_planner]: /*FINAL_ANSWER*/
[travel_planner]: The weather in Tokyo is rainy, 18C, with 85% humidity.
A flight from London to Tokyo is available for $450, departing at 9:00 AM and arriving
at 2:00 PM. For a mid-range hotel in Tokyo, I recommend the Grand Hotel, which costs
$150/night and has a 4.5-star rating.

==================================================
=== Without Planner (baseline) ===
==================================================
Query: I want to travel from London to Tokyo. Check the weather in Tokyo, find me a
flight, and suggest a mid-range hotel.

[travel_basic]: The weather in Tokyo is rainy, 18C with 85% humidity. There is a flight
from London to Tokyo for $450, departing at 9:00 AM and arriving at 2:00 PM. For a
mid-range hotel in Tokyo, I recommend the Grand Hotel, which costs $150 per night and
has a 4.5-star rating.

=== Planner Comparison ===
PlanReActPlanner: Generates an explicit plan, then executes step by step
BuiltInPlanner:   Uses Gemini's native planning (more efficient)
No planner:       Agent decides on the fly (may miss steps)
```

> PlanReActPlanner (new in ADK v2) makes the agent generate an explicit plan before
> executing. The agent shows PLANNING, REASONING, ACTION, and FINAL_ANSWER stages.
> Compared to no-planner mode, it provides better traceability and is less likely
> to skip steps in complex multi-tool queries.

**Verdict:** PASS - PlanReActPlanner produces explicit plan with step-by-step execution; baseline agent handles the same query without planning structure.

---

## Summary

| # | File | Status | Notes |
|---|------|--------|-------|
| 16 | `16_transfer_control.py` | PASS | Agent transfer restrictions enforced |
| 17 | `17_code_executor.py` | PASS | Code execution with correct result |
| 18 | `18_planners.py` | PASS | Plan-then-act vs baseline comparison |

> Note: Examples 00-15 were verified in the initial Google ADK setup (v1.33.0).
> Only the new v2.1.0 examples are documented here.

**3/3 new examples pass.**
