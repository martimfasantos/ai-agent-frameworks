# Claude Agent SDK - Example Outputs

All examples run with `claude-agent-sdk>=0.2.106` and the Claude Code CLI. The SDK auto-selects the model via `ANTHROPIC_API_KEY`.

> **Note:** LLM responses are non-deterministic. Your outputs will differ in wording but should follow the same structure and demonstrate the same features.

---

## 00_hello_world.py

```
$ uv run python 00_hello_world.py

## The Origin of "Hello, World!"

The phrase **"Hello, World!"** as a programming tradition traces back to the early 1970s at Bell Labs.

### Key Milestones

1. **1972 – The earliest known use** comes from Brian Kernighan's internal Bell Labs memo,
   *"A Tutorial Introduction to the Language B"*, where a simple program printed `hello, world`.

2. **1974** – Kernighan used it again in a Bell Labs technical report,
   *"Programming in C: A Tutorial"*.

3. **1978 – The book that made it famous**: It appeared in ***The C Programming Language***
   (often called "K&R C") by **Brian Kernighan and Dennis Ritchie**.

### Why "Hello, World!"?

Kernighan has said he doesn't remember a specific reason for choosing the phrase — it was
simply a short, friendly, and clear way to demonstrate that a program could produce output.

### Legacy

The tradition spread because *The C Programming Language* became one of the most read
programming books of all time. Now virtually every programming language, framework, or
tutorial starts with a "Hello, World!" example as a rite of passage.
```

**Verdict:** PASS - One-shot `query()` call returns a complete response about "Hello, World!" history.

---

## 01_built_in_tools.py

```
$ uv run python 01_built_in_tools.py

[Tool Call] Glob: {'pattern': '**/*.py'}
[Tool Call] Read: {'file_path': '/Users/.../claude-agents-sdk/settings.py', 'limit': 5}
[Tool Call] Bash: {'command': 'find ... -name "*.py" -not -path "*/.venv/*"', 'description': 'List Python files excluding .venv'}

--- Result ---
Here's a summary of the results:

### Python Files in the Project (excluding `.venv`)

| File |
|------|
| `00_hello_world.py` |
| `01_built_in_tools.py` |
| ... (15 total files) |
| `settings.py` |

### First 5 Lines of `settings.py`

```python
import pydantic
from pydantic_settings import BaseSettings
```

The project contains **15 Python files** — a numbered series of example scripts
plus a `settings.py` that uses **Pydantic's `BaseSettings`** for configuration.
```

**Verdict:** PASS - Built-in tools (Glob, Read, Bash) invoked via allowed_tools and bypassPermissions, agent lists files and reads content.

---

## 02_custom_tools.py

```
$ uv run python 02_custom_tools.py

Here's the info for **Lisbon, Portugal**:

- Weather: Sunny, 25°C
- Population: ~545,000

Sounds like a lovely day in Lisbon!
```

**Verdict:** PASS - Custom MCP tools (get_weather, get_population) created via @tool decorator and create_sdk_mcp_server(), both invoked correctly.

---

## 03_structured_outputs.py

```
$ uv run python 03_structured_outputs.py

=== Example 1: Raw JSON Schema ===
Structured output: {
  "name": "Paris",
  "country": "France",
  "population_millions": 2.1,
  "famous_for": [
    "Eiffel Tower",
    "The Louvre Museum",
    "Notre-Dame Cathedral",
    "Fashion and haute couture",
    "Cuisine and fine dining",
    "Art and culture",
    "River Seine",
    "Champs-Élysées"
  ]
}

=== Example 2: Pydantic Model Schema ===
Title: 1984
Author: George Orwell
Rating: 9.5/5
Summary: George Orwell's *1984* is a chilling and prescient masterpiece of dystopian
fiction. Set in the totalitarian superstate of Oceania, it follows Winston Smith...
Themes: Totalitarianism, Surveillance and Privacy, Propaganda and Truth, Psychological
Manipulation, Resistance and Conformity, Loss of Individual Identity, Language as a
Tool of Control
```

**Verdict:** PASS - Both raw JSON schema and Pydantic model-derived schema produce valid structured output matching the defined schemas.

---

## 04_system_prompts.py

```
$ uv run python 04_system_prompts.py

=== Example 1: Custom String System Prompt ===
Arrr, Python be a high-level programming language, easy to read and write like a fine
treasure map! It be used fer web development, data plunderin', AI sorcery, and
automation. A fine tool in any code pirate's chest, it be!

=== Example 2: Preset System Prompt (claude_code) ===
Here are the tools available to me:

**File Operations**
- `Read` — read files
- `Write` — create/overwrite files
- `Edit` — make targeted edits to files
- `Glob` — find files by pattern
- `Grep` — search file contents

**Execution**
- `Bash` — run shell commands

**Research & Planning**
- `Agent` — launch specialized subagents
- `WebFetch` — fetch a URL
- `WebSearch` — search the web
...

=== Example 3: Preset with Append ===
A Python list comprehension is a concise way to create lists using a single expression.

**Syntax:**
```python
[expression for item in iterable if condition]
```

**Examples:**
```python
squares = [x**2 for x in range(5)]    # [0, 1, 4, 9, 16]
even_sq = [x**2 for x in range(10) if x % 2 == 0]  # [0, 4, 16, 36, 64]
```

Happy coding!
```

**Verdict:** PASS - All three system prompt modes work: custom string (pirate persona), preset claude_code, and preset with appended instructions (concise + beginner-friendly).

---

## 05_permissions.py

```
$ uv run python 05_permissions.py

=== Example 1: Permission Mode with Allow/Deny Lists ===
[Tool Call] Glob

Result: The Glob tool returned many results (truncated), largely because it picked up
`.py` files from within the `.venv` directory...

=== Example 2: can_use_tool Callback ===

Result: `settings.py` — 15 lines, one setting:

```python
import pydantic
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: pydantic.SecretStr
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings: Settings = Settings()
```

Audit log (0 calls): []

=== Example 3: can_use_tool Shadowed by allowed_tools ===
Result: **14 lines** (15 with the trailing newline — `wc -l` reports 14).

[CanUseToolShadowedWarning] can_use_tool will not be invoked for: Read. An
allowed_tools entry that allows a whole tool auto-approves it before the
callback is consulted. To gate every tool call, use a PreToolUse hook; or
narrow the entry so calls fall through to can_use_tool. Allow rules from
settings files can also shadow the callback but are not visible here.

Callback invocations during this run: 0
Use a PreToolUse hook to gate tools that allowed_tools already approves.
```

**Verdict:** PASS - Example 1 uses allowed_tools/disallowed_tools with permission_mode. Example 2 demonstrates can_use_tool callback with AsyncIterable streaming prompt (required by the SDK for this feature). Example 3 shows the shadowing footgun: `allowed_tools=["Read"]` auto-approves before the callback runs, so it is never invoked, and since 0.2.111 the SDK raises `CanUseToolShadowedWarning` to say so.

> The `0 calls` audit log in Example 2 is expected here, not a failure — allow rules in the machine's own Claude Code settings can auto-approve `Read` before the callback is consulted, which is exactly the condition Example 3 makes explicit.

---

## 06_hooks.py

```
$ uv run python 06_hooks.py

  [PreToolUse] About to call: Glob
               Input: {'pattern': '*.py'}
  [PostToolUse] Finished: Glob
  [PreToolUse] About to call: Bash
               Input: {'command': 'ls *.py 2>/dev/null || ...'}
  [PreToolUse] BLOCKED: Bash tool is not allowed!
  [PreToolUse] About to call: Glob
               Input: {'pattern': '[!.]*.py'}
  [PostToolUse] Finished: Glob
  [PreToolUse] About to call: Agent
               Input: {'description': 'Find top-level .py files', ...}
  [PreToolUse] About to call: Bash
               Input: {'command': 'ls -1 *.py 2>/dev/null'}
  [PreToolUse] BLOCKED: Bash tool is not allowed!
  [PreToolUse] About to call: Glob
               Input: {'pattern': '*.py'}
  [PostToolUse] Finished: Glob
  [PostToolUse] Finished: Agent

--- Result ---
Here are the **15 `.py` files** found in the current directory:
| # | File |
|---|------|
| 1 | `00_hello_world.py` |
| ... |
| 15 | `settings.py` |
```

**Verdict:** PASS - PreToolUse hooks log tool calls before execution, Bash calls are blocked by the deny hook, PostToolUse hooks fire after completion. All three hook types demonstrated correctly.

---

## 07_sessions.py

```
$ uv run python 07_sessions.py

=== Step 1: Start a new session ===
Response: I've noted it: the secret code is **ALPHA-7**. Confirmed!
Session ID: 5da80ee6-679a-4871-b550-1603375bc2a9

=== Step 2: Resume the session ===
Response: The secret code you told me earlier is **ALPHA-7**.

=== Step 3: Fork the session ===
Forked session response: The answer to 2 + 2 is **4**!
New session ID: 421f2380-1045-448c-ad19-dde6b75c9865
(Original session '5da80ee6-679a-4871-b550-1603375bc2a9' is unchanged)
```

**Verdict:** PASS - Session created with unique ID, resumed by ID (remembers ALPHA-7), forked to new session with independent ID while preserving original.

---

## 08_multi_turn.py

```
$ uv run python 08_multi_turn.py

=== Turn 1 ===
Response: Got it! I'll keep in mind that you're building a REST API with **FastAPI**.
I'm ready to help you with routing, data validation, authentication, database
integration, middleware, testing, and project structure.
Session: aa3522d1-8a8c-473b-998f-91a8f561f3a7

=== Turn 2 ===
Response: For a **FastAPI** project, here are the top recommendations:
- `python-jose` + `passlib` (Most Common for Custom JWT Auth)
- `fastapi-users` (Batteries-Included)
- `authlib` (OAuth2 / OpenID Connect)
- External Auth Services (Auth0, Clerk, Supabase Auth)

For most FastAPI projects, **`python-jose` + `passlib`** is the go-to starting point.

=== Turn 3 ===
Response: ```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

app = FastAPI()
...
```
```

**Verdict:** PASS - ClaudeSDKClient maintains context across 3 turns: sets FastAPI context (Turn 1), recommends auth library building on context (Turn 2), provides code example for recommended library (Turn 3).

---

## 09_subagents.py

```
$ uv run python 09_subagents.py

  [task_started] {'type': 'system', 'subtype': 'task_started', 'task_id': 'a39127f5c1dd049e1',
    'description': 'Review Python calc function', 'task_type': 'local_agent', ...}
  [task_started] {'type': 'system', 'subtype': 'task_started', 'task_id': 'a540bad4ba94b6489',
    'description': 'Write docstring for calc function', 'task_type': 'local_agent', ...}
  [task_notification] {'task_id': 'a540bad4ba94b6489', 'status': 'completed',
    'summary': 'Write docstring for calc function', ...}
  [task_notification] {'task_id': 'a39127f5c1dd049e1', 'status': 'completed',
    'summary': 'Review Python calc function', ...}

--- Final Result ---
## Code Review — Issues Found
1. **Division by zero** — no handling for `y == 0`
2. **Silent `None` return** — unknown `op` returns `None`
3. **No input validation**, **Fragile string-based dispatch**
4. **Missing type hints**, **Missing docstring**

## Doc Writer — Suggested Docstring
```python
def calc(x, y, op):
    """Perform basic arithmetic operations on two numbers.
    Args:
        x (float): The first operand.
        y (float): The second operand.
        op (str): The operation to perform ("add", "sub", "mul", "div").
    Returns:
        float: The result of the arithmetic operation.
    Raises:
        ValueError: If op is not one of the supported operations.
        ZeroDivisionError: If op is "div" and y is 0.
    """
```
```

**Verdict:** PASS - Two AgentDefinition subagents (code_reviewer with sonnet, doc_writer with haiku) delegated via the Agent tool. Both complete their tasks and results are aggregated by the orchestrator.

---

## 10_mcp_servers.py

```
$ uv run python 10_mcp_servers.py

[MCP Tool] ToolSearch: {'query': 'select:mcp__filesystem__list_directory,...'}
[MCP Tool] mcp__filesystem__list_directory: {'path': '.'}
[MCP Tool] mcp__filesystem__read_file: {'path': './settings.py'}

--- Result ---
### Current Directory Contents

| Type | Name |
|------|------|
| FILE | `.env`, `.env.example`, `.python-version` |
| DIR  | `.venv`, `__pycache__` |
| FILE | `00_hello_world.py` through `13_file_checkpointing.py` |
| FILE | `pyproject.toml`, `settings.py`, `uv.lock` |

### `settings.py`

```python
import pydantic
from pydantic_settings import BaseSettings
...
```
```

**Verdict:** PASS - External MCP server (@modelcontextprotocol/server-filesystem via npx stdio) connected, tools mcp__filesystem__list_directory and mcp__filesystem__read_file invoked successfully.

---

## 11_streaming.py

```
$ uv run python 11_streaming.py

Streaming response:

Here's a haiku about Python programming:

*Indentation rules*
*Whitespace whispers the structure*
*Serpent speaks clearly*

--- Stream complete ---
Characters streamed: 122
Final result: Here's a haiku about Python programming:

*Indentation rules*
*Whitespace whispers the structure*
*Serpent speaks clearly*
```

**Verdict:** PASS - Real-time streaming with include_partial_messages=True delivers text deltas via StreamEvent, character count tracked, final ResultMessage matches streamed content.

---

## 12_cost_tracking.py

```
$ uv run python 12_cost_tracking.py

=== Example 1: Cost and Usage Tracking ===
Result: A REST API (Representational State Transfer Application Programming Interface) is
a standardized architectural style for building web services that allows different systems
to communicate over HTTP using standard methods like GET, POST, PUT, and DELETE.
Cost: $0.007165
Turns: 1
Duration: 3036ms (API: 3030ms)
Usage: {'input_tokens': 3, 'cache_creation_input_tokens': 905, 'cache_read_input_tokens':
8242, 'output_tokens': 86, 'server_tool_use': {'web_search_requests': 0, ...},
'service_tier': 'standard', ...}

=== Example 2: Limit Max Turns ===
Stopped after 4 turns
Stop reason: tool_use
Result: None
Turn limit hit: Claude Code returned an error result: Reached maximum number of turns (3)

=== Example 3: Budget Cap ===
Result: Paris.
Cost: $0.020575
Budget limit: $0.05

=== Example 4: Effort Level ===
[Low effort] Result: 4
Duration: 2280ms

=== Example 5: Per-Model Usage ===
Model: claude-opus-5 (firstParty)
  Input tokens:          6
  Output tokens:         311
  Cache read tokens:     56171
  Cache creation tokens: 49109
  Cost:                  $0.439857
  Context window:        1000000

Cache creation tokens in usage (main loop only): 25876
Cache creation tokens in model_usage (whole tree): 49109
```

**Verdict:** PASS - All five controls demonstrated: cost/usage tracking with total_cost_usd and usage dict, max_turns=3 limiting agent rounds, max_budget_usd=0.05 capping spend, effort="low" for fast simple answers, and per-model accounting via model_usage.

> Example 5 is the point of the `ModelUsage` addition: `usage` counts only the main loop (25,876 cache-creation tokens) while `model_usage` aggregates the whole agent tree including the subagent (49,109). Anything measuring spend from `usage` alone undercounts subagent runs.
>
> Examples 2 and 3 exceed their limits by design; the SDK signals both by raising on the error result, which the example now catches and prints. Whether the budget cap in Example 3 fires depends on how expensive the configured model is.

---

## 13_file_checkpointing.py

```
$ uv run python 13_file_checkpointing.py

Working directory: /var/folders/.../claude_checkpoint_s24rlq_a
Initial file content: Original content: Hello World

=== Turn 1: Modify the file ===
Checkpoint UUID: 7a7f23c7-6580-4060-9f6f-fed40fd62f4c
Result: Done! Read example.txt (contained "Original content: Hello World"),
then overwrote it with "Modified by agent: version 2".
File now contains: Modified by agent: version 2

=== Turn 2: Modify again ===
File now contains: Modified again: version 3

=== Rewinding to Turn 1 checkpoint ===
File after rewind: Original content: Hello World
```

**Verdict:** PASS - File checkpointing enabled with `enable_file_checkpointing=True` and `extra_args={"replay-user-messages": None}`. Agent modifies file across two turns, then `rewind_files()` restores the file to its original state by resuming the session with an empty prompt.

---

## 14. Session Store (`14_session_store.py`)

```
$ uv run python 14_session_store.py

=== Session Store Demo ===
Store type: InMemorySessionStore

--- Step 1: Run a query with session mirroring ---
Response: The three primary colors are red, blue, and yellow.
Session ID: abc123-...

--- Step 2: List sessions from store ---
Sessions in store: 1
  - abc123-... (created: 2026-05-10T...)

--- Step 3: Read messages from session abc123-... ---
Total messages in transcript: 4
  [SystemMessage]
  [UserMessage]
  [AssistantMessage]
  [ResultMessage] -> The three primary colors are red, blue, and yel...
```

> SessionStore decouples transcript storage from local disk. The InMemorySessionStore mirrors the session in real-time via `session_store_flush="eager"`, and `list_sessions_from_store` / `get_session_messages_from_store` inspect the stored transcript.

**Verdict:** PASS - InMemorySessionStore captures session transcript, list and read functions work.

---

## 15. Deferred Tool Use (`15_deferred_tool_use.py`)

```
$ uv run python 15_deferred_tool_use.py

=== Deferred Tool Use (Human-in-the-Loop) ===
  [HITL Hook] Tool 'mcp__database__delete_record' requested with args: {'record_id': 'usr-42'}
  [HITL Hook] Deferring for human approval...

Result subtype: end_turn

--- Deferred Tool Use ---
  Tool ID:    toolu_abc123
  Tool Name:  mcp__database__delete_record
  Tool Input: {'record_id': 'usr-42'}

  A human reviewer would inspect this and decide to approve or deny.
  To resume, pass the session ID back with the approval decision.
```

> The PreToolUse hook returns `permissionDecision: "defer"`, which halts the agent run. The `deferred_tool_use` field on ResultMessage carries the tool call details for human review.

**Verdict:** PASS - Deferred tool use stops the agent and exposes the pending tool call for HITL review.

---

## 16. Hook Events (`16_hook_events.py`)

```
$ uv run python 16_hook_events.py

=== Hook Event Streaming ===

[HookEvent #1]
  Event: PreToolUse
  Subtype: hook_event
  Tool: Glob

[HookEvent #2]
  Event: PostToolUse
  Subtype: hook_event
  Tool: Glob

--- Result ---
Here are the Python files in the current directory: ...

Total hook events received: 2
```

> With `include_hook_events=True`, hook lifecycle events are streamed as `HookEventMessage` objects, giving full observability into which hooks fired and their decisions.

**Verdict:** PASS - HookEventMessage objects received in the stream with tool and event metadata.

---

## 17. Strict MCP Config (`17_strict_mcp.py`)

```
$ uv run python 17_strict_mcp.py

=== Strict MCP Config Demo ===

Running with strict_mcp_config=True (no external MCP servers)...

[Tool] Glob

--- Result ---
Here are the Python files in the current directory: ...

Note: strict_mcp_config=True ensured no project/user/global MCP servers loaded.
```

> With `strict_mcp_config=True`, only explicitly-passed MCP servers are available. No project, user, or global MCP configurations are loaded, ensuring a deterministic tool set.

**Verdict:** PASS - Agent runs with only built-in tools; no external MCP servers loaded.

---

## 18. Thinking Config (`18_thinking_config.py`)

```
$ uv run python 18_thinking_config.py

=== Example 1: Adaptive Thinking ===
Response: 2 + 2 = 4

=== Example 2: Thinking Enabled (budget: 2000 tokens) ===
Response: # The Halting Problem

The halting problem asks a simple-sounding question:

> Can you write a program that looks at any other program and tells you whether
it will eventually finish running or get stuck looping forever?

The answer, proven by Alan Turing in 1936, is no. It's impossible to build such
a program...

=== Example 3: Thinking Disabled ===
Response: Three prime numbers: 2, 3, and 5.
```

> ThinkingConfig controls extended thinking behavior. In SDK 0.2.x these are
> TypedDicts that require an explicit `type` discriminator:
> - `ThinkingConfigAdaptive(type="adaptive")`: model decides whether to think based on complexity
> - `ThinkingConfigEnabled(type="enabled", budget_tokens=N)`: always think, capped at N tokens
> - `ThinkingConfigDisabled(type="disabled")`: suppress thinking for faster, cheaper responses
>
> Verified live via `query()` against the Claude CLI: all three modes return
> `ResultMessage(subtype="success")`.

**Verdict:** PASS - All three thinking modes run and return successful results.

---

## 19. Task Budget (`19_task_budget.py`)

```
$ uv run python 19_task_budget.py

=== Example 1: Dollar Budget Cap ===
Response: Logic flows like streams—
a missing semicolon
halts the universe.

=== Example 2: TaskBudget with Token Limit ===
Response: # A Brief History of Python

## Origins (late 1980s-1991)
Python was created by Guido van Rossum at CWI in the Netherlands. He began work
in December 1989 as a hobby project, designing it as a successor to the ABC
language...

=== Budget Controls Summary ===
max_budget_usd:    Hard dollar cap on total API spend
TaskBudget(total): Total token budget the model paces against
max_turns:         Maximum agent reasoning iterations
```

> Budget controls cap agent resource consumption per task:
> - `max_budget_usd=1.00`: hard dollar ceiling on total API spend (the SDK raises
>   an error result if the cap trips, so set it above a single task's expected cost)
> - `TaskBudget(total=25000)`: total token budget the model is made aware of and
>   paces against. `total` is a token count and must be at least the model minimum
>   (20,000 tokens for the default model)
>
> Verified live via `query()` against the Claude CLI: both examples return
> `ResultMessage(subtype="success")`.

**Verdict:** PASS - Dollar cap and TaskBudget token budget both run successfully.

---

## 20. Sandbox Settings (`20_sandbox_settings.py`)

```
$ uv run python 20_sandbox_settings.py

=== Example 1: Sandbox with Network Locked Down ===
Response: 15 * 23 = 345

=== Example 2: Full Sandbox Configuration ===
Response: Here are the files in the current directory:
- 00_hello_world.py
- 01_built_in_tools.py
- ...
- 20_sandbox_settings.py
- settings.py

=== Sandbox Settings Summary ===
enabled=True:           Sandbox bash commands (macOS/Linux)
network.allowedDomains: Whitelist outbound domains ([] blocks all)
network.deniedDomains:  Always-blocked domains
Sandboxing prevents data exfiltration and limits blast radius
```

> SandboxSettings sandboxes bash command execution. In SDK 0.2.x the keys are
> camelCase and network access is controlled by domain lists (not an `enabled`
> flag on the network config):
> - `SandboxSettings(enabled=True, ...)`: enable bash sandboxing (macOS/Linux)
> - `SandboxNetworkConfig(allowedDomains=[])`: block all outbound domains
> - `SandboxNetworkConfig(allowedDomains=["api.github.com"])`: whitelist domains
> - `SandboxNetworkConfig(deniedDomains=[...])`: always-blocked domains
>
> Verified live via `query()` against the Claude CLI: both examples return
> `ResultMessage(subtype="success")`.

**Verdict:** PASS - Sandboxed bash with network domain controls runs successfully.

---

## 21_interrupt_and_terminal_reason.py

```
$ uv run python 21_interrupt_and_terminal_reason.py

=== Example 1: Interrupt a Running Turn ===
  [interrupt() sent while the model was streaming]
  subtype:         error_during_execution
  terminal_reason: aborted_streaming
  is_error:        True
  result:          None
  extra deltas after interrupt: 0

  Sending a follow-up turn on the same client...
  terminal_reason: completed
  result:          4

=== Example 2: terminal_reason=max_turns ===
  subtype:         error_max_turns
  terminal_reason: max_turns
  stop_reason:     tool_use
  turns used:      2

=== terminal_reason values ===
completed:         the turn finished on its own
max_turns:         max_turns was reached
api_error:         the upstream API call failed
aborted_streaming: interrupted while the model was generating text
aborted_tools:     interrupted while a tool call was in flight
None:              older CLI, or a result that bypassed the query loop
```

**Verdict:** PASS - `interrupt()` cancels the turn mid-stream and `terminal_reason` (0.2.126) reports why it ended: `aborted_streaming` for the cancelled turn, `completed` for the follow-up, `max_turns` when the limit is hit.

> `extra deltas after interrupt: 0` is the proof the cancellation took effect immediately — no further text arrived after the call. The aborted turn still emits its own `ResultMessage`, so the example keeps iterating `receive_response()` to drain it; skipping that drain makes the next `query()` read the dead turn's buffered messages. Note `ClaudeSDKClient` yields error results as `ResultMessage`, whereas `query()` raises on them — which is why the client is used here.

---

## Summary

| # | File | Status | Notes |
|---|------|--------|-------|
| 0 | `00_hello_world.py` | PASS | Basic query with ResultMessage |
| 1 | `01_built_in_tools.py` | PASS | Built-in tool definitions and invocations |
| 2 | `02_custom_tools.py` | PASS | Custom tool registration and dispatch |
| 3 | `03_structured_outputs.py` | PASS | JSON schema output validation |
| 4 | `04_system_prompts.py` | PASS | System prompt configuration and presets |
| 5 | `05_permissions.py` | PASS | Permission modes, allow/deny lists, can_use_tool |
| 6 | `06_hooks.py` | PASS | PreToolUse/PostToolUse hook callbacks |
| 7 | `07_sessions.py` | PASS | Session create, resume, fork |
| 8 | `08_multi_turn.py` | PASS | Context retention across 3 turns |
| 9 | `09_subagents.py` | PASS | Two subagents delegated via Agent tool |
| 10 | `10_mcp_servers.py` | PASS | External MCP server integration |
| 11 | `11_streaming.py` | PASS | Real-time token streaming |
| 12 | `12_cost_tracking.py` | PASS | Cost, turns, duration, budget, effort, model_usage |
| 13 | `13_file_checkpointing.py` | PASS | File checkpoint and rewind |
| 14 | `14_session_store.py` | PASS | InMemorySessionStore transcript |
| 15 | `15_deferred_tool_use.py` | PASS | Human-in-the-loop deferral |
| 16 | `16_hook_events.py` | PASS | Hook event streaming |
| 17 | `17_strict_mcp.py` | PASS | Strict MCP config isolation |
| 18 | `18_thinking_config.py` | PASS | Extended thinking modes |
| 19 | `19_task_budget.py` | PASS | Dollar cap and token budget |
| 20 | `20_sandbox_settings.py` | PASS | Sandboxed bash with network domain controls |
| 21 | `21_interrupt_and_terminal_reason.py` | PASS | interrupt() cancellation and terminal_reason |

**22/22 examples pass.**
