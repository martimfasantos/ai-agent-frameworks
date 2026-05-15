# Agno

- Repo: https://github.com/agno-agi/agno
- Documentation: https://docs.agno.com
- Version: **2.6.5**

## Agno Examples

### How to setup

#### Virtual environment

Create a virtual environment with uv:

```bash
uv venv
```

Then activate it:
```bash
# On Linux/macOS
source .venv/bin/activate
# On Windows
.venv\Scripts\activate
```

Install the dependencies:
```bash
uv sync
```

#### .env

See `.env.example` and create a `.env` file.
You need an OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Examples

| # | File | Feature | Description |
|---|------|---------|-------------|
| 00 | `00_basic_agent.py` | Agents | Basic agent with instructions and formatted output |
| 01 | `01_agent_with_tools.py` | Tools | Custom tools with `@tool` decorator |
| 02 | `02_async_agent.py` | Async | Async agent runs with `arun()` and `asyncio.gather` |
| 03 | `03_streaming.py` | Streaming | Token-by-token streaming with `RunOutputEvent` |
| 04 | `04_structured_output.py` | Structured Output | Type-safe responses with `output_schema` and Pydantic |
| 05 | `05_team.py` | Teams | Multi-agent team with `TeamMode.coordinate` |
| 06 | `06_workflow.py` | Workflows | Step-based workflows with `Step` and `Parallel` |
| 07 | `07_human_in_the_loop.py` | HITL | Tool confirmation with `requires_confirmation` |
| 08 | `08_knowledge_rag.py` | Knowledge/RAG | Vector search with `Knowledge` + `LanceDb` |
| 09 | `09_memory.py` | Memory | Agentic memory with `MemoryManager` |
| 10 | `10_storage.py` | Storage | Session persistence with `SqliteDb` |
| 11 | `11_guardrails.py` | Guardrails | Input validation with `BaseGuardrail` pre-hooks |
| 12 | `12_reasoning_tools.py` | Reasoning | Step-by-step thinking with `ReasoningTools` |
| 13 | `13_session_state.py` | Session State | Stateful tools with `session_state` |
| 14 | `14_mcp_tools.py` | MCP Tools | External tool servers via Model Context Protocol |
| 15 | `15_hooks.py` | Hooks | Pre-hooks and post-hooks for logging and transforms |
| 16 | `16_approval_decorator.py` | Approval | `@approval` decorator for tool-level HITL gating |

### Running examples

Run any example directly:

```bash
python 00_basic_agent.py
```

> **Note:** Example `14_mcp_tools.py` requires Node.js (npx) installed for the MCP filesystem server.
