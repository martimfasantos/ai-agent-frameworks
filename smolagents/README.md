# smolagents

- Repo: https://github.com/huggingface/smolagents
- Documentation: https://huggingface.co/docs/smolagents/index
- Version: **1.26.0**

## About smolagents

smolagents is a lightweight framework by Hugging Face for building AI agents that write and execute Python code to solve tasks. Its unique approach — **CodeAgent** — has the agent generate Python code snippets as actions (the "CodeAct" pattern), which are executed in a sandboxed interpreter. This is more expressive than JSON tool-calling and allows agents to chain logic, use variables, and compose tools naturally.

Key features:
- **CodeAgent** - Agents write Python code as actions (CodeAct pattern)
- **ToolCallingAgent** - Traditional JSON tool-calling for comparison
- **`@tool` decorator** - Simple function-based tool creation
- **Built-in tools** - Wikipedia, web search, Python interpreter, and more
- **Multi-agent** - Manager agents delegate to sub-agents via `managed_agents`
- **Multiple model providers** - OpenAI, LiteLLM, HF Inference, Anthropic, Azure, local models
- **Streaming** - Step-by-step event streaming via generator
- **Planning** - Automatic plan generation with `planning_interval`
- **Memory** - Inspect `agent.memory.steps` for full execution history
- **MCP tools** - Model Context Protocol integration via `ToolCollection.from_mcp()`
- **Callbacks** - Step callbacks and final answer validation checks

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

Required: `OPENAI_API_KEY` for the default OpenAI provider. Optionally set `OPENAI_MODEL_NAME` (defaults to `gpt-4o-mini`).

### Run examples

```bash
uv run python 00_hello_world.py
uv run python 01_custom_tools.py
uv run python 02_builtin_tools.py
uv run python 03_tool_calling_agent.py
uv run python 04_streaming.py
uv run python 05_multi_agent.py
uv run python 06_different_models.py
uv run python 07_memory_management.py
uv run python 08_code_agent_multi_step.py
uv run python 09_planning.py
uv run python 10_text_to_sql.py
uv run python 11_mcp_tools.py
uv run python 12_callbacks_observability.py
uv run python 13_advanced_patterns.py
```

## Examples

| # | File | Topics |
|---|------|--------|
| 0 | `00_hello_world.py` | Basic CodeAgent creation and single query |
| 1 | `01_custom_tools.py` | `@tool` decorator with weather and currency tools |
| 2 | `02_builtin_tools.py` | `WikipediaSearchTool` for real knowledge lookup |
| 3 | `03_tool_calling_agent.py` | `ToolCallingAgent` with JSON tool calls (vs CodeAgent) |
| 4 | `04_streaming.py` | `stream=True` step-by-step event streaming |
| 5 | `05_multi_agent.py` | Manager + sub-agents via `managed_agents` |
| 6 | `06_different_models.py` | `OpenAIModel` and `LiteLLMModel` provider swap |
| 7 | `07_memory_management.py` | `agent.memory.steps`, step callbacks, cross-run persistence |
| 8 | `08_code_agent_multi_step.py` | CodeAct: multi-step code execution with persistent variables |
| 9 | `09_planning.py` | `planning_interval` for automatic plan generation |
| 10 | `10_text_to_sql.py` | Natural language to SQL against in-memory SQLite |
| 11 | `11_mcp_tools.py` | MCP stdio server integration via `ToolCollection.from_mcp()` |
| 12 | `12_callbacks_observability.py` | Post-run execution trace with step/tool/error counts |
| 13 | `13_advanced_patterns.py` | Custom instructions, `final_answer_checks`, step inspection |
| 14 | `14_gradio_ui.py` | GradioUI for interactive web chat interface |

## Key dependencies

- `smolagents[toolkit]>=1.26.0` - smolagents with built-in tool support
- `smolagents[mcp]>=1.26.0` - MCP integration (installs `mcpadapt`)
- `litellm` - Multi-provider LLM support (for example 06)
- `wikipedia-api` - Wikipedia tool backend (for example 02)
- `pydantic-settings` - Settings management from .env
