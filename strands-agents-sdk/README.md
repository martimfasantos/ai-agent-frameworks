# Strands Agents SDK

- Repo: https://github.com/strands-agents/sdk-python
- Documentation: https://strandsagents.com/latest/
- Version: **1.39.0**

## About Strands Agents SDK

Strands Agents is an open-source SDK from AWS/Amazon for building AI agents using a model-driven approach. The SDK defaults to **Amazon Bedrock** (Claude Sonnet) as the model provider but supports many alternatives including OpenAI, Anthropic, Ollama, LiteLLM, and more.

Key features:
- **Model-driven** - The model decides when and how to use tools
- **`@tool` decorator** - Simple function-based tool creation
- **Class-based tools** - OOP tools with shared state
- **Structured output** - Pydantic model responses
- **Multi-agent patterns** - Agents-as-tools (with `as_tool()`), swarm, graph, workflow orchestration
- **Hooks** - Lifecycle event hooks for monitoring and control
- **Conversation management** - Sliding window, summarizing, and null managers
- **A2A protocol** - Agent-to-Agent communication standard
- **MCP tools** - Model Context Protocol integration
- **Skills/plugins** - Composable agent skill bundles
- **Streaming** - Async iterators and callback handlers
- **Observability** - Built-in metrics, token usage, and tool call statistics
- **Session persistence** - FileSessionManager and S3SessionManager for state persistence

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

The default provider is **Amazon Bedrock** (requires AWS credentials). You can also configure OpenAI or Anthropic as alternative providers.

### Run examples

```bash
uv run python 00_hello_world.py
uv run python 01_custom_tools.py
uv run python 02_structured_output.py
uv run python 03_system_prompt_and_conversation.py
uv run python 04_model_providers.py
uv run python 05_agents_as_tools.py
uv run python 06_streaming_and_callbacks.py
uv run python 07_metrics_and_observability.py
uv run python 08_class_based_tools.py
uv run python 09_hooks.py
uv run python 10_conversation_management.py
uv run python 11_multi_agent_swarm.py
uv run python 12_multi_agent_graph.py
uv run python 13_multi_agent_workflow.py
uv run python 14_a2a_agent.py
uv run python 15_mcp_tools.py
uv run python 16_skills_plugin.py
uv run python 17_session_persistence.py
uv run python 18_context_compression.py
```

## Examples

| # | File | Topics |
|---|------|--------|
| 0 | `00_hello_world.py` | Basic agent creation and invocation |
| 1 | `01_custom_tools.py` | `@tool` decorator with word_count, reverse_string, letter_counter |
| 2 | `02_structured_output.py` | Pydantic models for type-safe responses (PersonInfo, MovieReview) |
| 3 | `03_system_prompt_and_conversation.py` | System prompts and multi-turn conversation |
| 4 | `04_model_providers.py` | Bedrock, OpenAI, Anthropic, Ollama provider configuration |
| 5 | `05_agents_as_tools.py` | Multi-agent orchestration with `as_tool()` and direct agent passing |
| 6 | `06_streaming_and_callbacks.py` | Custom callback handlers and async streaming |
| 7 | `07_metrics_and_observability.py` | AgentResult metrics, token usage, tool call stats |
| 8 | `08_class_based_tools.py` | Class-based tools with shared state (TaskManager) |
| 9 | `09_hooks.py` | Lifecycle hooks: before/after invocation, before/after tool call |
| 10 | `10_conversation_management.py` | SlidingWindow, Summarizing, and Null conversation managers |
| 11 | `11_multi_agent_swarm.py` | Swarm multi-agent orchestration with handoffs |
| 12 | `12_multi_agent_graph.py` | Graph-based DAG agent orchestration |
| 13 | `13_multi_agent_workflow.py` | Workflow tool for sequential multi-step pipelines |
| 14 | `14_a2a_agent.py` | Agent-to-Agent (A2A) protocol communication |
| 15 | `15_mcp_tools.py` | Model Context Protocol (MCP) tool integration |
| 16 | `16_skills_plugin.py` | AgentSkills plugin with programmatic Skill creation |
| 17 | `17_session_persistence.py` | FileSessionManager for state and conversation persistence |
| 18 | `18_context_compression.py` | Proactive context compression with SummarizingConversationManager |

## Key dependencies

- `strands-agents>=1.39.0` - Strands Agents SDK
- `strands-agents-tools>=0.5.2` - Community tools (calculator, current_time, shell, etc.)
- `pydantic-settings` - Settings management from .env
