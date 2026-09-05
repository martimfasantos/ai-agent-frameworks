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

## 19. Plugins (`19_plugins.py`)

```
$ uv run python 19_plugins.py

-----------------------------------------------------------------
               1. App(plugins=[...]): plugin hooks vs. agent callbacks
-----------------------------------------------------------------

Query: How many units of SKU-100 do we have?

  [plugin:audit_plugin] user message: 'How many units of SKU-100 do we have?'
  [plugin:audit_plugin] invocation started (root agent: InventoryAgent)
  [plugin:audit_plugin] agent starting: InventoryAgent
  [agent-callback] before_agent on InventoryAgent
  [plugin:audit_plugin] tool call: get_stock_level({'sku': 'SKU-100'})
  [plugin:audit_plugin] tool result: get_stock_level -> {'sku': 'SKU-100', 'units': 42}

  Final answer: We have 42 units of SKU-100.
  [plugin:audit_plugin] invocation finished

  Note: [agent-callback] fired once, only for InventoryAgent.
        [plugin:audit_plugin] saw the whole invocation — run, agent, tool.

-----------------------------------------------------------------
               2. Runner(plugins=[...]): on_agent_error / on_run_error
-----------------------------------------------------------------

Query: Charge the card for order ORD-7 (the tool will raise)

  [plugin:audit_plugin] user message: 'Charge the card for order ORD-7.'
  [plugin:audit_plugin] invocation started (root agent: PaymentAgent)
  [plugin:audit_plugin] agent starting: PaymentAgent
  [plugin:audit_plugin] tool call: charge_card({'order_id': 'ORD-7'})
  [plugin:audit_plugin] AGENT ERROR in PaymentAgent: RuntimeError: payment gateway timed out for ORD-7 (notification only — ADK re-raises)
  [plugin:audit_plugin] RUN ERROR: RuntimeError: payment gateway timed out for ORD-7 (notification only — ADK re-raises)

  Exception reached the caller: RuntimeError: payment gateway timed out for ORD-7

  Note: both error hooks fired for PaymentAgent, which declares no
        callbacks at all — and the RuntimeError still reached the caller,
        because both hooks are notification-only.

-----------------------------------------------------------------
               3. ReflectAndRetryModelPlugin (built-in, ADK 2.6.0)
-----------------------------------------------------------------

  name:                             reflect_retry_model_plugin
  max_retries:                      2
  throw_exception_if_retry_exceeded: True
  tracking_scope:                   invocation
  on_model_errors:                  ['MALFORMED_FUNCTION_CALL']

  On a tracked model error it injects reflection guidance and re-runs the
  turn; after max_retries consecutive failures it raises RuntimeError.
  Section 1's model behaved, so it stayed silent.

-----------------------------------------------------------------
               Summary
-----------------------------------------------------------------

  Plugins registered on the App: ['audit_plugin', 'reflect_retry_model_plugin']
  Hook events recorded by the one shared AuditPlugin instance: 12
  Agents covered without any per-agent wiring: InventoryAgent, PaymentAgent
```

> Plugins are the runner-level counterpart of the per-agent callbacks in
> `06_callbacks.py`. One `AuditPlugin` instance covered two different agents
> across two invocations — `PaymentAgent` declares no callbacks of its own yet
> still produced a full hook trace. `on_agent_error_callback` and
> `on_run_error_callback` (new in ADK 2.5.0) both fired, and the `RuntimeError`
> still reached the caller: they are notification-only hooks and cannot suppress
> the exception.

**Verdict:** PASS - both error hooks fire and the exception is still re-raised; the plugin covers agents that have no callbacks of their own.

---

## 20. Agent as MCP Server (`20_agent_as_mcp_server.py`)

```
$ uv run python 20_agent_as_mcp_server.py

-----------------------------------------------------------------
  What an MCP host discovers on this server
-----------------------------------------------------------------
  Tools exposed: 1  (the agent's 2 tools stay private)
    name:        support_agent
    description: Answers customer questions about order status and returns.
    inputSchema: {"properties": {"request": {"title": "Request", "type": "string"}}, "required": ["request"], "title": "call_agentArguments", "type": "object"}

-----------------------------------------------------------------
  Call 1: 'Where is order ORD-42?'
-----------------------------------------------------------------
    [progress] I'm checking the status of your order.
  Agent: Your order ORD-42 has been shipped with DHL and is expected to arrive in 2 days.

-----------------------------------------------------------------
  Call 2: 'How long do I have to return it?' (same connection)
-----------------------------------------------------------------
    [progress] I'm checking the return window for your order.
  Agent: You have 14 days left to return order ORD-42.

-----------------------------------------------------------------
  Summary
-----------------------------------------------------------------
  MCP tools exposed:            1 (support_agent)
  Agent tools visible to host:  0 (encapsulated behind the agent)
  Progress notifications sent:  2
  Call 2 resolved 'it' from call 1 — same ADK session per connection.
```

> The exact inverse of `11_mcp_tools.py`: there ADK consumed an MCP server, here
> the ADK agent *is* one. `to_mcp_server` (new in ADK 2.5.0) registers the whole
> agent as a single MCP tool — the host sees `support_agent`, never
> `get_order_status` or `get_return_window`. Call 2 resolving "it" proves ADK
> keeps one session per MCP connection. The `[progress]` lines are the agent's
> intermediate text forwarded as MCP progress notifications; the count depends on
> whether the model narrates before calling a tool.

**Verdict:** PASS - one MCP tool exposed, progress notifications delivered, conversation state preserved across two calls on one connection.

---

## 21. Workflow Graphs (`21_workflow_graphs.py`)

```
$ uv run python 21_workflow_graphs.py

-----------------------------------------------------------------
               1. Running the Workflow graph directly
-----------------------------------------------------------------

  Ticket: 'I was charged twice on   invoice 88'
    node normalize     -> 'i was charged twice on invoice 88'
    node classify      -> 'i was charged twice on invoice 88'
    node issue_refund  -> 'Refund issued and the case was closed.'

  Ticket: 'My SERVER keeps crashing'
    node normalize     -> 'my server keeps crashing'
    node classify      -> 'my server keeps crashing'
    node escalate      -> 'Escalated to engineering with a 24h SLA.'

  The two tickets took different branches out of `classify`, decided by
  Event(route=[...]) — and not one model call was made.

-----------------------------------------------------------------
               2. The same Workflow used as an LlmAgent tool
-----------------------------------------------------------------

  Query: Ticket: I was charged twice on invoice 88, please help.

    tool call:   triage_workflow({'text': 'I was charged twice on invoice 88, please help.'})
    node normalize     ran inside the tool
    node classify      ran inside the tool
    node issue_refund  ran inside the tool
    tool result: {'result': 'Refund issued and the case was closed.'}

  Agent: The ticket was triaged, a refund was issued, and the case was closed.

  Tool declaration derived from the Workflow:
    name:        triage_workflow
    description: Triages a customer support ticket and resolves or escalates it.
    input:       ['text']
```

> `Workflow` is the successor ADK 2.6.x names when deprecating the
> `SequentialAgent` / `ParallelAgent` / `LoopAgent` trio used in
> `05_workflow_agents.py`. Section 1 runs the graph with zero model calls — the
> two tickets leave `classify` on different branches purely from
> `Event(route=[...])`. Section 2 shows node-as-tool (new in ADK 2.4.0): the same
> graph object handed to `LlmAgent(tools=[...])` is auto-wrapped as a `NodeTool`,
> with the declaration derived from the Workflow's `description` and
> `input_schema`. Without an `input_schema`, `NodeTool.__init__` raises.

**Verdict:** PASS - conditional routing branches correctly with no LLM, and the same Workflow runs as an agent tool.

---

## Summary

| # | File | Status | Notes |
|---|------|--------|-------|
| 16 | `16_transfer_control.py` | PASS | Agent transfer restrictions enforced |
| 17 | `17_code_executor.py` | PASS | Code execution with correct result |
| 18 | `18_planners.py` | PASS | Plan-then-act vs baseline comparison |
| 19 | `19_plugins.py` | PASS | Error hooks fire, exception still re-raised |
| 20 | `20_agent_as_mcp_server.py` | PASS | Agent published as a single MCP tool |
| 21 | `21_workflow_graphs.py` | PASS | Graph routing + Workflow used as a tool |

> Note: Examples 00-15 were verified in the initial Google ADK setup (v1.33.0).
> Examples 16-18 were added at v2.1.0 and 19-21 at v2.6.2; only these are
> documented here.

**6/6 documented examples pass.**
