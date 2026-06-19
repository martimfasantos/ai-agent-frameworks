# LangChain

- Repo: https://github.com/langchain-ai/langchain
- Documentation: https://docs.langchain.com/oss/python/langchain/

## LangChain Examples

These examples use the **LangChain v1.0+ API** centered on `create_agent()`, which is the primary agent factory function. All examples focus on LangChain core (LangGraph is used only as the underlying runtime, not directly).

### How to setup

#### Virtual environment (uv)

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

Install dependencies with:

```bash
uv sync
```

This creates a `.venv` and installs all packages from `pyproject.toml`.

#### .env

See `.env.example` and create a `.env` file in this directory. You need an OpenAI API key:

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

#### Run the examples

Run any example with:

```bash
uv run python <file_name>.py
```

For example:

```bash
uv run python 00_hello_world.py
```

### Examples

| # | File | Feature |
|---|------|---------|
| 00 | `00_hello_world.py` | Simplest agent with `create_agent()` |
| 01 | `01_chat_models.py` | `init_chat_model()`, `ChatOpenAI()`, multi-turn |
| 02 | `02_tools.py` | `@tool` decorator, agent with tools |
| 03 | `03_streaming.py` | `stream()` with updates and messages modes |
| 04 | `04_structured_output.py` | `response_format` with Pydantic models |
| 05 | `05_short_term_memory.py` | `InMemorySaver` checkpointer, thread-based memory |
| 06 | `06_runtime_context.py` | `context_schema`, `ToolRuntime[Context]` DI |
| 07 | `07_context_engineering.py` | Dynamic prompts, tool filtering, message injection |
| 08 | `08_middleware.py` | `@before_model`, `@after_model`, `@dynamic_prompt` |
| 09 | `09_guardrails.py` | `@before_agent`, `@after_agent` content filtering |
| 10 | `10_human_in_the_loop.py` | `HumanInTheLoopMiddleware`, interrupt/resume |
| 11 | `11_long_term_memory.py` | `InMemoryStore`, store read/write from tools |
| 12 | `12_retrieval_rag.py` | Agentic RAG with retrieval tools |
| 13 | `13_mcp.py` | MCP integration with `MultiServerMCPClient` and FastMCP |
| 14 | `14_multi_agent_subagents.py` | Subagents as tools, supervisor pattern |
| 15 | `15_multi_agent_handoffs.py` | State-driven handoffs with `wrap_model_call` |
| 16 | `16_multi_agent_router.py` | Router pattern with `StateGraph`, `Send` fan-out |
| 17 | `17_multi_agent_skills.py` | Skills pattern with progressive skill disclosure |
| 18 | `18_observability.py` | LangSmith tracing, metadata, selective tracing |
| 19 | `19_dynamic_tool_registration.py` | Dynamic tool injection via middleware |
| 20 | `20_stream_events_v3.py` | v3 event streaming with tool-started/finished and text-delta events |
