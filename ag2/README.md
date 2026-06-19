# AG2

- Repo: https://github.com/ag2ai/ag2
- Documentation: https://docs.ag2.ai/latest/
- Version: **0.13.2**

## About AG2

AG2 (formerly AutoGen) is an open-source framework for building multi-agent AI systems. It provides a flexible, high-level API for creating conversable agents that can collaborate through various orchestration patterns.

Key features:
- **ConversableAgent** - Core agent class with LLM integration and tool support
- **Structured outputs** - Pydantic model responses via `response_format`
- **Human-in-the-loop** - Configurable human input modes for agent oversight
- **Group chat** - Multi-agent orchestration with AutoPattern, RoundRobin, etc.
- **Sequential chat** - Chained conversations with automatic carryover
- **Nested chat** - Encapsulate workflows inside a single agent
- **Code execution** - Local and Docker-based code executors
- **Guardrails (Maris)** - Policy-based content filtering and safeguards
- **MCP tools** - Model Context Protocol integration
- **A2A protocol** - Agent-to-Agent communication over HTTP (v1.0 compatible)
- **Observability** - Runtime logging to SQLite with event capture
- **Beta Agent** - New async-first Agent with OpenAIConfig, MemoryStream observer, and structured responses (path to v1.0)

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Install dependencies

```bash
uv sync
```

### Configure environment

Copy `.env.example` to `.env` and add your credentials:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### Run examples

```bash
uv run python 00_simple_agent.py
uv run python 01_agent_with_tools.py
uv run python 02_structured_outputs.py
uv run python 03_human_in_the_loop.py
uv run python 04_multi_agent.py
uv run python 05_sequential_chat.py
uv run python 06_nested_chat.py
uv run python 07_code_execution.py
uv run python 08_guardrails.py
uv run python 09_mcp_tools.py
uv run python 10_observability.py
uv run python 11_a2a.py
uv run python 12_beta_agent.py
uv run python 13_beta_tools.py
uv run python 14_beta_observer.py
uv run python 15_beta_structured_output.py
```

## Examples

| # | File | Topics |
|---|------|--------|
| 0 | `00_simple_agent.py` | Basic ConversableAgent, `run()` / `process()`, LLMConfig |
| 1 | `01_agent_with_tools.py` | `functions=` parameter, tool registration, multi-tool agents |
| 2 | `02_structured_outputs.py` | Pydantic `response_format`, schema-conforming JSON responses |
| 3 | `03_human_in_the_loop.py` | Simulated human approval, `register_reply()`, conversation flow |
| 4 | `04_multi_agent.py` | `AutoPattern`, `initiate_group_chat()`, multi-agent collaboration |
| 5 | `05_sequential_chat.py` | `initiate_chats()` pipeline, carryover summaries, specialist agents |
| 6 | `06_nested_chat.py` | `register_nested_chats()`, encapsulated workflows, inner delegation |
| 7 | `07_code_execution.py` | `LocalCommandLineCodeExecutor`, code writer/executor agent pattern |
| 8 | `08_guardrails.py` | Safeguard policies (Maris), regex filtering, inter-agent safeguards |
| 9 | `09_mcp_tools.py` | `create_toolkit()`, `stdio_client`, FastMCP server integration |
| 10 | `10_observability.py` | `runtime_logging` to SQLite, event capture, post-hoc analysis |
| 11 | `11_a2a.py` | `A2aAgentServer`, `A2aRemoteAgent`, distributed agents over HTTP |
| 12 | `12_beta_agent.py` | Beta `Agent`, `OpenAIConfig`, async `ask()`, `AgentReply` |
| 13 | `13_beta_tools.py` | Beta Agent tools, event history with tool call/result events |
| 14 | `14_beta_observer.py` | `MemoryStream` event subscription, real-time event observation |
| 15 | `15_beta_structured_output.py` | Beta Agent `response_schema`, Pydantic structured outputs |
| 16 | `16_beta_middleware.py` | Beta Middleware for intercepting LLM calls and agent turns |
| 17 | `17_beta_memory_stream.py` | MemoryStream for persistent conversation history across turns |

## Key dependencies

- `ag2[openai,mcp,a2a]>=0.13.2` - AG2 framework with OpenAI, MCP, and A2A extras
- `mcp>=1.9.2` - Model Context Protocol SDK (for MCP server)
- `pydantic-settings` - Settings management from .env
- `uvicorn` - ASGI server for A2A examples
