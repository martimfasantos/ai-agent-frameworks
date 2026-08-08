# Claude Agent SDK

- Repo: https://github.com/anthropics/claude-agent-sdk-python
- Documentation: https://platform.claude.com/docs/en/agent-sdk/overview
- Version: **0.2.130**

## About Claude Agent SDK

The Claude Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript. It is maintained by Anthropic and designed for building production AI agents that autonomously read files, run commands, search the web, edit code, and more.

Key features:
- **One-shot queries** - Send a prompt, get a result with `query()`
- **Built-in tools** - Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
- **Custom tools** - `@tool` decorator + in-process MCP servers
- **Structured outputs** - JSON Schema / Pydantic model validation
- **System prompts** - Custom string, preset, or preset with append
- **Permissions** - Modes, allow/deny lists, `can_use_tool` callback
- **Hooks** - PreToolUse, PostToolUse, Stop, SessionStart lifecycle hooks
- **Sessions** - Resume, fork, continue conversations across calls
- **SessionStore** - Pluggable transcript storage (in-memory, S3, Redis, Postgres)
- **Subagents** - AgentDefinition for task delegation
- **MCP servers** - Connect external tool servers via stdio/HTTP
- **Streaming** - Real-time StreamEvent and partial message delivery
- **Deferred tool use** - Human-in-the-loop approval via hook deferral
- **Hook event streaming** - Observe hook lifecycle via HookEventMessage
- **Strict MCP config** - Lock down MCP sources for deterministic tool sets
- **Cost tracking** - Budget caps, turn limits, effort levels, per-model usage
- **Interruption** - Cancel a running turn and read why it ended via `terminal_reason`

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`

### Install dependencies

```bash
uv sync
```

### Configure environment

Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

### Run examples

```bash
uv run python 00_hello_world.py
uv run python 01_built_in_tools.py
uv run python 02_custom_tools.py
uv run python 03_structured_outputs.py
uv run python 04_system_prompts.py
uv run python 05_permissions.py
uv run python 06_hooks.py
uv run python 07_sessions.py
uv run python 08_multi_turn.py
uv run python 09_subagents.py
uv run python 10_mcp_servers.py
uv run python 11_streaming.py
uv run python 12_cost_tracking.py
uv run python 13_file_checkpointing.py
uv run python 14_session_store.py
uv run python 15_deferred_tool_use.py
uv run python 16_hook_events.py
uv run python 17_strict_mcp.py
uv run python 18_thinking_config.py
uv run python 19_task_budget.py
uv run python 20_sandbox_settings.py
uv run python 21_interrupt_and_terminal_reason.py
```

## Examples

| # | File | Topics |
|---|------|--------|
| 00 | `00_hello_world.py` | One-shot query, ResultMessage |
| 01 | `01_built_in_tools.py` | Built-in tools (Read, Glob), allowed_tools, tool inspection |
| 02 | `02_custom_tools.py` | @tool decorator, create_sdk_mcp_server, in-process MCP |
| 03 | `03_structured_outputs.py` | JSON Schema output, Pydantic model schema |
| 04 | `04_system_prompts.py` | Custom string, preset, preset with append |
| 05 | `05_permissions.py` | Permission modes, allow/deny lists, can_use_tool callback, CanUseToolShadowedWarning |
| 06 | `06_hooks.py` | PreToolUse/PostToolUse hooks, matchers, deny decisions |
| 07 | `07_sessions.py` | Session resume, fork, session ID capture |
| 08 | `08_multi_turn.py` | ClaudeSDKClient, multi-turn conversations |
| 09 | `09_subagents.py` | AgentDefinition, agent delegation, model selection |
| 10 | `10_mcp_servers.py` | External MCP server (stdio), filesystem tools |
| 11 | `11_streaming.py` | Real-time StreamEvent, partial messages |
| 12 | `12_cost_tracking.py` | Cost tracking, max_turns, max_budget_usd, effort, model_usage |
| 13 | `13_file_checkpointing.py` | File checkpointing, rewind_files |
| 14 | `14_session_store.py` | InMemorySessionStore, eager flush, store inspection |
| 15 | `15_deferred_tool_use.py` | HITL deferred tool use, hook "defer" decision |
| 16 | `16_hook_events.py` | Hook event streaming, HookEventMessage |
| 17 | `17_strict_mcp.py` | strict_mcp_config for deterministic tool sets |
| 18 | `18_thinking_config.py` | Extended thinking: enabled, adaptive, and disabled modes |
| 19 | `19_task_budget.py` | Dollar cap (max_budget_usd) and TaskBudget token budget for agent spend |
| 20 | `20_sandbox_settings.py` | SandboxSettings for sandboxed bash with network domain controls |
| 21 | `21_interrupt_and_terminal_reason.py` | interrupt() to cancel a turn, ResultMessage.terminal_reason, draining after an interrupt |

## Key dependencies

- `claude-agent-sdk>=0.2.106` - Claude Agent SDK (Python), locked at 0.2.130
- `pydantic-settings` - Settings management from .env
