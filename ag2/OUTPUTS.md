# AG2 Example Outputs

Captured outputs from running all 22 examples against ag2 v1.0.1 with `gpt-4o-mini`.

> These outputs may vary between runs due to LLM non-determinism. The structure, tool invocations, and event sequences should remain consistent.

> AG2 1.0 is a framework substitution, not a version bump: `autogen.beta` became the top-level `ag2` package and the classic `ConversableAgent` API moved to the separate `autogen` distribution ([AG2 Classic](https://github.com/ag2ai/ag2-classic)). Every example in this folder was rewritten or re-imported against the new `ag2` API, so these outputs share nothing with the v0.13.4 baseline.

---

## 00_simple_agent.py

```
=== Turn 1: new conversation ===
Response: The phrase "Hello, World!" is commonly used as a simple example in programming languages to illustrate basic syntax. It was popularized by the 1978 book "The C Programming Language" by Brian Kernighan and Dennis Ritchie, where it was used in the first example of a C program.

=== Turn 2: continuation via reply.ask() ===
Response: From C Programming Language example.

=== Conversation history: 6 event(s) ===
  - ModelRequest
  - UsageEvent
  - ModelResponse
  - ModelRequest
  - UsageEvent
  - ModelResponse
```

> `reply.ask()` continues the same conversation — turn 2 compresses turn 1's answer without being told what it was. The 6 history events are the two turns.

---

## 01_agent_with_tools.py

```
=== Agent with tools ===

Response: Lisbon is currently experiencing sunny weather with a temperature of 25°C. The city's population is approximately 550,000.

=== Tool activity ===
  -> called get_weather({"city": "Lisbon"})
  -> called get_population({"city": "Lisbon"})
  <- get_weather returned 'Sunny, 25°C'
  <- get_population returned '~550,000'
```

> The tool activity section proves both tools actually executed and shows the exact arguments the model chose and the values it got back.

---

## 02_structured_outputs.py

```
=== Structured output: CityInfo ===

  raw body:           {"name":"Tokyo","country":"Japan","population":"14 million (city proper), 37 million (metropolitan area)","famous_for":"Skyscrapers, technology, pop culture, cuisine, and historical sites","best_time_to_visit":"March to May (spring) and September to November (autumn)"}
  parsed type:        CityInfo
  City:               Tokyo
  Country:            Japan
  Population:         14 million (city proper), 37 million (metropolitan area)
  Famous for:         Skyscrapers, technology, pop culture, cuisine, and historical sites
  Best time to visit: March to May (spring) and September to November (autumn)

=== Per-turn schema override: Distance ===

  parsed type: Distance
  Tokyo -> Lisbon: 10860 km
```

> `reply.body` is the raw JSON the model emitted; `await reply.content()` is the parsed Pydantic object. The second turn overrides the schema for that turn only.

---

## 03_human_in_the_loop.py

```
=== Booking 1: the human approves ===
  [human] asked: Approve booking to Barcelona for EUR 180? (yes/no)
  [human] answered: 'yes'
Agent: Your flight to Barcelona has been successfully booked and charged EUR 180.

=== Booking 2: the human rejects ===
  [human] asked: Approve booking to Reykjavik for EUR 940? (yes/no)
  [human] answered: 'no'
Agent: The booking to Reykjavik was cancelled by the human reviewer.

=== 2 human input request(s) handled ===
```

> The tool suspends on `context.input()` and the `hitl_hook` answers it. The approval genuinely gates the outcome: 'yes' confirms, 'no' cancels.

---

## 04_multi_agent.py

```
=== Multi-agent collaboration via subagents ===

Delegations the coordinator's model chose:
  -> task_researcher
  -> task_writer
  -> task_critic

=== Final output ===
Python's journey began in the late 1980s when Guido van Rossum created the language at Centrum Wiskunde & Informatica in the Netherlands, aiming to offer an intuitive programming experience. The first official release, Python 0.9.0, debuted in February 1991 and laid the foundation with essential features like functions, exception handling, and key data types such as lists and dictionaries. Fast forward to October 2000, Python 2.0 introduced innovative concepts like list comprehensions and automatic garbage collection. Then, in December 2008, Python 3.0 emerged as a significant overhaul, emphasizing a more streamlined and consistent language, while deliberately stepping away from backward compatibility to refine its design.
```

> The delegation list is the proof: the coordinator's model chose researcher → writer → critic on its own. Nothing hard-codes that order.

---

## 05_sequential_chat.py

```
=== Sequential pipeline: research -> analysis -> briefing ===

      intake: Topic: the current state of quantum computing.
  researcher: RESEARCH — quantum computing is advancing rapidly with major investments from governments and corporations; practical applications are emerging across sectors like cryptography and materials science; challenges remain in error rates and qubit coherence times.
     analyst: ANALYSIS — Increased investment in quantum computing can lead to breakthroughs in technology and industry applications; addressing challenges in error rates and qubit coherence will be crucial for the technology's widespread adoption and effectiveness.
      writer: BRIEFING — The current state of quantum computing shows rapid advancements fueled by significant investments, resulting in potential applications in fields such as cryptography and materials science; however, overcoming challenges related to error rates and qubit coherence is essential for broader adoption and practicality.

=== Pipeline closed: reason='sequence_complete' ===
```

> Ordering is enforced by `TransitionGraph.sequence()`, not by the models. Each stage visibly builds on the previous one, and the hub closes the channel with `sequence_complete`.

---

## 06_nested_chat.py

```
=== Nested workflow behind a single tool ===

Tools the publisher saw:
  -> task_lead_agent

Tools the encapsulated pipeline used internally:
  -> task_fact_checker
  -> task_editor

=== Final output ===
In 1928, Alexander Fleming discovered penicillin when he observed that the mold Penicillium notatum had antibacterial properties, inhibiting bacterial growth in a contaminated petri dish. This groundbreaking discovery, though made in 1928, only led to the mass production of penicillin in the early 1940s, during World War II, ultimately transforming medical treatment by introducing effective antibiotics.
```

> The publisher only ever sees one tool (`task_lead_agent`). The second list is read from the inner shared stream and reveals the encapsulated two-step workflow the caller never saw.

---

## 07_code_execution.py

```
=== Task 1: compute the first 10 Fibonacci numbers ===

Agent: The first 10 Fibonacci numbers are [0, 1, 1, 2, 3, 5, 8, 13, 21, 34] and they have been written to fib.txt in the working directory.

=== Task 2: read the file back from the same sandbox ===

Agent: The contents of fib.txt are:\n0\n1\n1\n2\n3\n5\n8\n13\n21\n34.

=== Executed snippets ===
  -> run_code: {"code": "fib = [0, 1]\nfor i in range(2, 10):\n    fib.append(fib[i-1] + fib[i-2])\nprint(fib)", "language": "python"}
  -> run_code: {"code": "fib = [0, 1]\nfor i in range(2, 10):\n    fib.append(fib[i-1] + fib[i-2])\nwith open('fib.txt', 'w') as f:\n  
  <- [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
  <- 
  -> run_code: {"code":"with open('fib.txt', 'r') as f:\n    contents = f.read()\nprint(contents)","language":"python"}
  <- 0
1
1
2
3
5
8
13
21
34

Sandbox files: ['fib.txt']
```

> Task 2 reads back a file written in task 1, proving the sandbox filesystem persists across calls. Each snippet runs as a fresh process, so the model re-declares `fib` in the second call rather than relying on globals from the first.

---

## 08_guardrails.py

```
=== Request 1: safe record ===
Agent: The record has been successfully pushed to the CRM.

=== Request 2: record containing an SSN ===
Agent: HALTED: FATAL: blocked PII in call to send_to_crm

=== Guardrail activity ===
ObserverAlerts: 1
  - [FATAL] pii-guardian: blocked PII in call to send_to_crm
HaltEvents:     1
  - source=pii-guardian reason='FATAL: blocked PII in call to send_to_crm'
```

> Request 1 succeeds; request 2 emits a FATAL `ObserverAlert`, `AlertPolicy` turns it into a `HaltEvent`, and the reply is the synthetic `HALTED: ...` string. Note this halts the turn rather than vetoing the call — the tool still runs, but its result never reaches the model.

---

## 09_mcp_tools.py

```
=== Calculation ===

Agent: The result of (15 + 27) * 3 is 126.

=== MCP tool activity ===
  -> add({"a": 15, "b": 27})
  -> multiply({"a": 3, "b": 1})
  <- 3.0
  <- 42.0
  -> multiply({"a":42,"b":3})
  <- 126.0
```

> The `add` and `multiply` tools are discovered from `mcp_server.py` over stdio and executed locally. The FastMCP server's own protocol logging goes to stderr and is not shown here.

---

## 10_observability.py

```
=== Session: two turns on one observed stream ===

Turn 1: The speed of light in a vacuum is approximately 299,792 kilometers per second (km/s), or about 186,282 miles per second (mi/s).
  [trace] tool call: get_distance({"city_a":"Lisbon","city_b":"Reykjavik"})
Turn 2: The distance from Lisbon to Reykjavik is approximately 2,780 kilometers.

Wrote 14 events to res/ag2_event_log.jsonl

=== Event counts ===
  UsageEvent: 3
  ModelResponse: 3
  ModelRequest: 2
  ModelMessage: 2
  ToolCallsEvent: 1
  ToolCallEvent: 1
  ToolResultEvent: 1
  ToolResultsEvent: 1

=== Token usage ===
  prompt tokens:     380
  completion tokens: 74
```

> The stream-based replacement for the removed SQLite `runtime_logging`. The event log is written to `res/ag2_event_log.jsonl` and then queried for event counts and token totals.

---

## 11_a2a.py

```
=== A2A: agent-to-agent over JSON-RPC ===

Server listening on http://127.0.0.1:18765
Agent card: name='translator' version=1.0.0
Bindings:   ['JSONRPC']
Skills:     ['translator']

Turn 1
  sent:     Hello, how are you today?
  received: Bonjour, comment ça va aujourd'hui ?

Turn 2 (same conversation, server-side glossary tool consulted)
  sent:     The agent used a tool.
  received: L'agent a utilisé un outil.

=== A2A demo complete ===
```

> The card is fetched over HTTP from `/.well-known/agent-card.json`. Turn 2 renders 'tool' as 'outil', which is the server-side glossary tool's house translation — proof the remote tool executed on the server.

---

## 12_beta_agent.py

```
=== Beta Agent: Simple Question ===

Response: The phrase "Hello, World!" is commonly used as a simple programming example to demonstrate the basic syntax of a programming language, and it first appeared in the 1978 book "The C Programming Language" by Brian Kernighan and Dennis Ritchie. It has since become a standard introductory exercise in many programming tutorials.

=== Beta Agent: Second Question ===

Response: The capital of Portugal is Lisbon.

=== Reply History ===
  Events in history: 3
  - ModelRequest
  - UsageEvent
  - ModelResponse
```

---

## 13_beta_tools.py

```
=== Beta Agent: Tools ===

Response: The current weather in Lisbon is sunny with a temperature of 25°C. The population of Lisbon is approximately 550,000.

=== Event History ===
  ModelRequest
  UsageEvent
  ModelResponse
  ToolCallsEvent
  ToolCallEvent
  ToolCallEvent
  ToolResultEvent
  ToolResultEvent
  ToolResultsEvent
  UsageEvent
  ModelResponse
```

> The event history shows the full loop: request → response with tool calls → two tool executions → results → final response.

---

## 14_beta_observer.py

```
=== Beta Agent: Observer API ===

Events as they happen:
  [Observer] ModelRequest: LLM request sent
  [Observer] ModelMessage: LLM message received
  [Observer] UsageEvent
  [Observer] ModelResponse: LLM response complete

Response: The speed of light in a vacuum is approximately 299,792 kilometers per second (or about 186,282 miles per second).

=== Observer Summary ===
Total events captured: 4
  1. ModelRequest
  2. ModelMessage
  3. UsageEvent
  4. ModelResponse
```

> The `[Observer]` lines are printed live from the subscriber as each event lands, before the response is returned.

---

## 15_beta_structured_output.py

```
=== Beta Agent: Structured Output ===

  City: Lisbon
  Country: Portugal
  Population: 552,700 (2021)
  Famous for: Historic architecture, Fado music, vibrant nightlife, and delicious cuisine.
  Best time to visit: March to May and September to October.

--- Second Query ---

  City: Tokyo
  Country: Japan
  Population: 13.96 million
  Famous for: Unique blend of traditional culture and modern technology, cuisine, shopping, and anime culture.
  Best time to visit: March to May (spring) and September to November (autumn)
```

---

## 16_beta_middleware.py

```
=== Agent with Middleware Stack ===

  [CallTracerMiddleware] LLM call intercepted
  [CallTracerMiddleware] LLM responded
  [TimingMiddleware] Turn completed in 0.67s

Response: The capital of France is Paris.
```

> Both middlewares fire on one turn: `on_llm_call` brackets the model call and `on_turn` brackets the whole turn, so the timing line prints last.

---

## 17_beta_memory_stream.py

```
=== Turn 1: Introduce context ===
Response: Nice to meet you, Alice! How can I assist you today?

=== Turn 2: Test memory ===
Response: Your name is Alice, and you work at Acme Corp.

=== Memory Stream Contents ===
Total events in stream: 6
  [0] ModelRequest: ModelRequest(parts=[TextInput(content='My name is Alice and I work at Acme Corp....
  [1] UsageEvent: UsageEvent(label=None, kind='model_call', model='gpt-4o-mini-2024-07-18', provid...
  [2] ModelResponse: ModelResponse(content=Nice to meet you, Alice! How can I assist you today?, usag...
  [3] ModelRequest: ModelRequest(parts=[TextInput(content='What is my name and where do I work?')])...
  [4] UsageEvent: UsageEvent(label=None, kind='model_call', model='gpt-4o-mini-2024-07-18', provid...
  [5] ModelResponse: ModelResponse(content=Your name is Alice, and you work at Acme Corp., usage=Usag...
```

> Turn 2 recalls the name and employer from turn 1 purely because both turns share one `MemoryStream`.

---

## 18_observable_run.py

```
=== Live token stream ===

Paris, the capital of France, is renowned for its art, fashion, and cultural landmarks, including the iconic Eiffel Tower and the Louvre Museum. The city's charm lies in its historic architecture, vibrant cafés, and romantic atmosphere, making it a beloved destination for travelers worldwide.

Final body length: 293 chars

=== Mid-turn steering with run.enqueue() ===

  [event] tool returned, injecting a follow-up instruction

Steered result: Lisbon is the capital of Portugal, founded before Rome, located on the Tagus estuary.
```

> The first block prints tokens as they arrive rather than after the turn. The second injects a follow-up mid-turn via `run.enqueue()` — the same turn then returns the compressed one-liner.

---

## 19_resume.py

```
=== Step 1: an original conversation ===
Agent: On Day 1, visit Kinkaku-ji (Golden Pavilion), Ryoan-ji rock garden, and the Arashiyama Bamboo Grove, while on Day 2, explore Fushimi Inari Taisha, Gion district, and the Kyoto Imperial Palace, finishing with a traditional kaiseki dinner.

Stored trajectory: 3 events
  ['ModelRequest', 'UsageEvent', 'ModelResponse']

=== Step 2: resume from the stored trajectory ===
Agent: Take the Shinkansen (bullet train) from Tokyo to Kyoto, which takes about 2 hours and 30 minutes, or use the JR Special Rapid Service from Osaka, which takes about 30 minutes.

=== Step 3: resume from an out-of-band tool result ===
  replayed call:  lookup_order(id=A-1001)
  out-of-band result: 'Shipped, arriving Tuesday.'
  Agent: Your order A-1001 has been shipped and is scheduled to arrive on Tuesday.
```

> Step 2 uses a brand-new `Agent` with no live stream, yet answers in context — everything it knows came from the replayed events. Step 3 drives the loop from a `ToolResultsEvent` produced out of band, without re-executing the tool.

---

## 20_metrics.py

```
=== Generating traffic ===

assistant: 250 EUR is equal to 272.50 USD.
assistant: I cannot convert EUR to Klingon darseks as there is no exchange rate available for that currency.
reviewer:  Approved.

=== Prometheus exposition (filtered) ===

  ag2_llm_calls_total{agent="assistant",error_type="",finish_reason="tool_calls",model="gpt-4o-mini",outcome="success",provider="openai"} 2.0
  ag2_llm_calls_total{agent="assistant",error_type="",finish_reason="stop",model="gpt-4o-mini",outcome="success",provider="openai"} 2.0
  ag2_llm_calls_total{agent="reviewer",error_type="",finish_reason="stop",model="gpt-4o-mini",outcome="success",provider="openai"} 1.0
  ag2_llm_tokens_total{agent="assistant",model="gpt-4o-mini",provider="openai",token_type="input"} 1159.0
  ag2_llm_tokens_total{agent="assistant",model="gpt-4o-mini",provider="openai",token_type="output"} 73.0
  ag2_llm_tokens_total{agent="assistant",model="gpt-4o-mini",provider="openai",token_type="total"} 1232.0
  ag2_llm_tokens_total{agent="reviewer",model="gpt-4o-mini",provider="openai",token_type="input"} 41.0
  ag2_llm_tokens_total{agent="reviewer",model="gpt-4o-mini",provider="openai",token_type="output"} 2.0
  ag2_llm_tokens_total{agent="reviewer",model="gpt-4o-mini",provider="openai",token_type="total"} 43.0
  ag2_tool_calls_total{agent="assistant",error_type="",outcome="success",tool="convert_currency"} 1.0
  ag2_tool_calls_total{agent="assistant",error_type="ValueError",outcome="error",tool="convert_currency"} 1.0
  ag2_agent_turns_total{agent="assistant",error_type="",outcome="success"} 2.0
  ag2_agent_turns_total{agent="reviewer",error_type="",outcome="success"} 1.0
```

> Real Prometheus exposition text. Note the two `ag2_tool_calls_total` series: one `outcome="success"` and one `outcome="error"` with `error_type="ValueError"` from the unsupported-currency call.

---

## 21_cli_agents_acp.py

```
=== ACP adapters ===

  Claude Code  command=claude-agent-acp     on PATH=False
  Codex        command=codex-acp            on PATH=False
  OpenCode     command=opencode acp         on PATH=True

=== Agent construction ===
  agent name:        coder
  config type:       ClaudeCodeConfig
  workspace (cwd):   res/acp_workspace
  permission_policy: auto
  expose_tools:      True

=== Driving OpenCode ===

  OpenCode session failed: RequestError: Internal error: OpenCode service failure
  This usually means the CLI agent is installed but not authenticated.
```

> This run had `opencode` on PATH but no authenticated provider, so the ACP session failed. The example verifies adapter presets and agent construction, reports the real error, and exits 0 — no transcript is fabricated. With an authenticated CLI agent the `=== Driving ... ===` section streams its thoughts, tool calls, and final message.

---
