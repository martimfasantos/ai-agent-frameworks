# CrewAI

- Repo: https://github.com/crewAIInc/crewAI
- Documentation: https://docs.crewai.com/
- Version: **1.14.4**

## About CrewAI

CrewAI is an open-source framework for building multi-agent AI systems. It provides a structured way to define agents with roles, goals, and backstories, assemble them into crews, and orchestrate their collaboration on complex tasks.

Key features:
- **Agents & Crews** - Role-based agents that collaborate in sequential or hierarchical crews
- **Custom & built-in tools** - `@tool` decorator, `BaseTool` class, and `crewai_tools` package
- **Structured outputs** - Pydantic model responses via `output_pydantic` and `response_format`
- **Task features** - Async execution, context chaining, callbacks, guardrails, conditional tasks
- **Memory system** - Short-term, long-term, and entity memory with RAG
- **Knowledge sources** - String, file, and web-based knowledge per agent or crew
- **Flows** - Event-driven workflow orchestration with `@start`, `@listen`, `@router`
- **Planning** - Automatic step-by-step plan generation before execution
- **Streaming** - Real-time LLM output streaming with event listeners
- **MCP integration** - Model Context Protocol server connections
- **Execution hooks** - `@before_llm_call`, `@after_llm_call`, `@before_tool_call`, `@after_tool_call`
- **Multimodal agents** - Image and file processing with `multimodal=True`
- **Human feedback** - `@human_feedback` decorator for human-in-the-loop flows
- **Checkpointing & forking** - Save execution state, resume after failures, fork for "what if" exploration

## Setup

### Prerequisites

- Python 3.12+
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
uv run python 00_hello_world.py
uv run python 01_agent_kickoff.py
uv run python 02_tools.py
uv run python 03_built_in_tools.py
uv run python 04_structured_outputs.py
uv run python 05_tasks.py
uv run python 06_conditional_tasks.py
uv run python 07_guardrails.py
uv run python 08_callbacks.py
uv run python 09_streaming.py
uv run python 10_memory.py
uv run python 11_reasoning.py
uv run python 12_knowledge.py
uv run python 13_multimodal_agents.py
uv run python 14_multi_agent_collaboration.py
uv run python 15_mcp_integration.py
uv run python 16_planning.py
uv run python 17_event_listeners.py
uv run python 18_execution_hooks.py
uv run python 19_flows.py
uv run python 20_flows_with_agents.py
uv run python 21_human_feedback_in_flows.py
uv run python 22_crew_simplification.py
uv run python 23_checkpointing.py
```

## Examples

| # | File | Topics |
|---|------|--------|
| 0 | `00_hello_world.py` | Basic agent, task, crew |
| 1 | `01_agent_kickoff.py` | Agent kickoff without crew, response_format |
| 2 | `02_tools.py` | Custom tools (@tool, BaseTool, built-in) |
| 3 | `03_built_in_tools.py` | Built-in crewai_tools (web, file, code) |
| 4 | `04_structured_outputs.py` | Pydantic structured outputs (LLM + task) |
| 5 | `05_tasks.py` | Tasks (async, context, output_pydantic, markdown) |
| 6 | `06_conditional_tasks.py` | ConditionalTask with condition function |
| 7 | `07_guardrails.py` | Task guardrails (single + chained) |
| 8 | `08_callbacks.py` | Task callbacks for post-processing |
| 9 | `09_streaming.py` | LLM streaming with event listener |
| 10 | `10_memory.py` | Memory system (short-term, long-term, entity) |
| 11 | `11_reasoning.py` | Agent reasoning with max_reasoning_attempts |
| 12 | `12_knowledge.py` | Knowledge sources (string, docling, crew-wide) |
| 13 | `13_multimodal_agents.py` | Multimodal agents (image analysis) |
| 14 | `14_multi_agent_collaboration.py` | Delegation, sequential and hierarchical process |
| 15 | `15_mcp_integration.py` | MCP server integration (DSL syntax) |
| 16 | `16_planning.py` | Crew planning mode |
| 17 | `17_event_listeners.py` | Custom event listeners (BaseEventListener) |
| 18 | `18_execution_hooks.py` | LLM and tool call hooks |
| 19 | `19_flows.py` | Flows (@start, @listen, @router, and_, or_) |
| 20 | `20_flows_with_agents.py` | Flows with integrated agents and async |
| 21 | `21_human_feedback_in_flows.py` | @human_feedback decorator in flows |
| 22 | `22_crew_simplification.py` | @CrewBase decorators, YAML config |
| 23 | `23_checkpointing.py` | Checkpointing, resume, fork, CheckpointConfig |

## Key dependencies

- `crewai[tools]>=1.14.4` - CrewAI framework with built-in tools
- `pydantic>=2.11.7` - Data validation and structured outputs
- `pydantic-settings>=2.10.1` - Settings management from .env
