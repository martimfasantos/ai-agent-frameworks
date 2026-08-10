# LangGraph Examples — Outputs

Captured output from running all examples with `langgraph==1.2.6`, `langchain-openai==1.2.2`, and `gpt-4o-mini`.

---

## 00_hello_world.py

> **Feature:** Basic graph with `StateGraph`, `MessagesState`, `START`/`END` nodes, and `invoke`. The output shows a single-node chatbot responding to a user message — the simplest possible LangGraph application.

```
=== LangGraph Hello World ===

User: Where does 'hello world' come from?
AI: The phrase "Hello, World!" is famously known as a simple program used to illustrate the basics of programming in various languages. Its origins can be traced back to the early 1970s and the first edition of the C programming language. The phrase was used in the book "The C Programming Language," written by Brian Kernighan and Dennis Ritchie, which was published in 1978.

In the book, a simple program that prints "Hello, World!" to the screen serves as an introductory example for demonstrating the syntax of the C language. Since then, "Hello, World!" has become a standard first program for beginners learning to code in many programming languages, symbolizing the start of their programming journey.
```

---

## 01_state_and_reducers.py

> **Feature:** Custom state with `TypedDict`, reducer functions via `Annotated[list, operator.add]`, and conditional edges. The output shows a multi-node pipeline where each node appends to a shared list (reducer in action), a conditional edge routes to a "deep dive" node when quality > 5, and the final summary aggregates all accumulated notes.

```
=== State & Reducers Example ===

Topic: Artificial Intelligence
Quality Score: 7
Research Notes (3 total):
  - Note 1: Artificial Intelligence has a rich history dating back decades.
  - Note 2: Artificial Intelligence is widely used in modern applications.
  - Deep dive: Artificial Intelligence has influenced many related fields.

Final Summary: Detailed summary from 3 notes: Note 1: Artificial Intelligence has a rich history dating back decades. | Note 2: Artificial Intelligence is widely used in modern applications. | Deep dive: Artificial Intelligence has influenced many related fields.
```

---

## 02_pydantic_state.py

> **Feature:** Pydantic `BaseModel` as graph state schema with runtime validation. The output demonstrates two things: (1) a valid order flowing through the graph with discount calculation, and (2) a validation error caught when invalid data (empty name, negative price) is provided — proving the schema enforces constraints at graph boundaries.

```
=== Pydantic State Validation ===

Customer: John Doe
Items: ['Widget A', 'Gadget B', 'Gizmo C']
Original Total: $99.97
Discount: 15.0%
Final Price: $84.97
Status: confirmed

=== Validation Error Demo ===

Caught validation error: ValidationError: 2 validation errors for OrderState
customer_name
  Value error, Customer name cannot be empty [type=value_error, input_value='', input_type=str]
total_price
  Input should be greater than or equal to 0 [type=greater_than_equal, input_value=-10, input_type=int]
```

---

## 03_input_output_schemas.py

> **Feature:** Input/output schema filtering with `StateGraph(State, input_schema=..., output_schema=...)`. The output shows that only the fields defined in the output schema (`answer`, `confidence`) are returned to the caller — the internal `raw_research` field is hidden, demonstrating how schemas control what enters and exits a graph.

```
=== Input/Output Schemas ===

Answer: Based on 3 sources: The answer to 'What is quantum computing?' involves multiple perspectives from our research.
Confidence: 100%

Keys in result: ['answer', 'confidence']
Note: 'raw_research' is internal — not exposed to the caller
```

---

## 04_graph_visualization.py

> **Feature:** Graph visualization with `draw_mermaid()` and `draw_ascii()`. The output shows both formats: a Mermaid flowchart (saved to `res/agent_graph.mmd` for rendering) and an ASCII art representation — useful for debugging graph topology and documenting workflows.

```
=== Mermaid Diagram ===

---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	classifier(classifier)
	technical(technical)
	general(general)
	review(review)
	__end__([<p>__end__</p>]):::last
	__start__ --> classifier;
	classifier -.-> general;
	classifier -.-> technical;
	general --> review;
	technical --> review;
	review --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc


Mermaid diagram saved to res/agent_graph.mmd

=== ASCII Graph ===

          +-----------+
          | __start__ |
          +-----------+
                *
                *
                *
          +------------+
          | classifier |
          +------------+
          ...        ...
         .              .
       ..                ..
+---------+          +-----------+
| general |          | technical |
+---------+          +-----------+
          ***        ***
             *      *
              **  **
            +--------+
            | review |
            +--------+
                *
                *
                *
           +---------+
           | __end__ |
           +---------+
```

---

## 05_tool_calling.py

> **Feature:** Function calling with `@tool`, `bind_tools`, `ToolNode`, and `tools_condition`. The output shows the agent calling two tools in parallel (`get_weather` and `get_population`), receiving structured tool results, and synthesizing them into a final natural-language answer — the standard ReAct agent loop.

```
=== Tool Calling Agent ===

System: You are a helpful city information assistant. Be concise.
Human: What's the weather and population of Tokyo?
AI: [Calling tools: ['get_weather', 'get_population']]
Tool: Sunny, 28°C, 45% humidity
Tool: 13.9 million
AI: The weather in Tokyo is sunny with a temperature of 28°C and 45% humidity. The population of Tokyo is approximately 13.9 million.
```

---

## 06_command_from_tools.py

> **Feature:** `Command` objects returned from `@tool` functions to update state and route to a different node. The output shows a tool returning `Command(update={"department": "billing"}, goto="billing")`, which simultaneously updates the active department in state and transfers control to the billing agent node — enabling tool-driven routing.

```
=== Command from Tools ===

Final department: billing

H: I have a question about my bill for account ACC-001. Why was I charged $142.50?
AI: [Calling: ['transfer_to_billing']]
Tool: Transferred to billing: Customer has a billing question regarding a charge of $142.50 on their account.
AI: I've transferred your question to the billing department for further assistance regarding the charge of $142.50 on your account.
AI: I've transferred you to the billing department for your question about the $142.50 charge on your account.
```

---

## 07_prompt_chaining_and_routing.py

> **Feature:** Two workflow patterns — (1) **prompt chaining** where an outline node feeds a draft node feeds a polish node in sequence, and (2) **LLM-based routing** with `with_structured_output` to classify queries and route to specialized handlers. The output shows a 3-step writing pipeline producing progressively refined text, then three queries each routed to the correct department (technical, billing, general).

```
=== Example 1: Prompt Chaining ===

Topic: The future of renewable energy

Outline:
1. Advancements in technology increasing efficiency and reducing costs.
2. Global policy support and investment driving widespread adoption.
3. Integration with energy storage and smart grids for enhanced reliability.

Draft:
Recent advancements in technology have significantly increased efficiency and lowered costs across various sectors. Global policy support and investment have further fueled the widespread adoption of these innovations, making them more accessible. Additionally, the integration of these technologies with energy storage systems and smart grids has enhanced reliability, paving the way for a more resilient and sustainable energy landscape.

Polished:
Recent technological advancements have dramatically boosted efficiency and reduced costs across multiple sectors. Coupled with global policy support and investment, these innovations are becoming increasingly accessible. By integrating with energy storage systems and smart grids, they not only enhance reliability but also pave the way for a more resilient and sustainable energy landscape.


=== Example 2: LLM-based Routing ===

Query: My server keeps returning 503 errors after the latest deployment
  Routed to: technical (The query relates to server errors and deployment issues, which fall under technical support.)
  Response: A 503 error typically indicates that your server is temporarily unavailable; check your server logs for any resource issues or service downtime.

Query: I was double-charged on my last invoice
  Routed to: billing (The query concerns a financial issue related to billing and charges on an invoice.)
  Response: I apologize for the inconvenience. Please provide the invoice number or details, and I will look into the double charge for you.

Query: What are your business hours?
  Routed to: general (The question is about general information regarding business hours, not related to technical issues or billing.)
  Response: Our business hours are Monday to Friday, 9 AM to 5 PM.
```

---

## 08_streaming.py

> **Feature:** Streaming modes with `graph.astream()`. The output demonstrates two modes: (1) `updates` mode showing node-by-node results as they complete (tool call, tool result, final answer), and (2) `messages` mode delivering token-by-token output for real-time UI rendering.

```
=== Stream Mode: updates ===

[Node: chatbot]
  Tool call: calculate({'expression': '42 * 17 + 3'})

[Node: tools]
  Content: 717

[Node: chatbot]
  Content: The result of 42 × 17 + 3 is 717.

=== Stream Mode: messages (token-by-token) ===

AI: Pi (π) is a mathematical constant representing the ratio of a circle's circumference to its diameter, approximately equal to 3.14159. It is an irrational number, meaning it cannot be expressed as a simple fraction and has an infinite, non-repeating decimal expansion.
```

---

## 09_custom_streaming.py

> **Feature:** Custom stream events with `get_stream_writer()` and `stream_mode="custom"`. The output shows user-defined progress events emitted during node execution — status updates, per-item progress with percentages, and analysis results — enabling rich real-time feedback beyond the built-in streaming modes.

```
=== Custom Streaming with get_stream_writer() ===

[STATUS] Starting data ingestion...
[PROGRESS] ingestion: 1/3 (33%) - hello world
[PROGRESS] ingestion: 2/3 (67%) - langgraph streaming
[PROGRESS] ingestion: 3/3 (100%) - custom events are powerful
[STATUS] Ingestion complete: 3 items processed

[NODE COMPLETE] ingestion
[STATUS] Starting analysis...
[ANALYSIS] HELLO WORLD -> length=11, words=2
[ANALYSIS] LANGGRAPH STREAMING -> length=19, words=2
[ANALYSIS] CUSTOM EVENTS ARE POWERFUL -> length=26, words=4
[STATUS] Analysis complete: 3 results

[NODE COMPLETE] analysis

Done!
```

---

## 10_persistence.py

> **Feature:** Short-term memory with `InMemorySaver` and `thread_id` config. The output shows: (1) Thread 1 remembers the user's name and profession across turns, (2) Thread 2 has no access to Thread 1's context (isolation), and (3) persisted state can be inspected — showing message counts and checkpoint IDs per thread.

```
=== Thread 1: Multi-turn Conversation ===

User: My name is Alice and I'm a software engineer.
AI: Nice to meet you, Alice! As a software engineer, what areas do you specialize in?

User: What's my name and profession?
AI: Your name is Alice, and you are a software engineer.

=== Thread 2: Independent Conversation ===

User: Do you know my name?
AI: No, I don't know your name unless you tell me. If you'd like to share it, feel free!

=== Inspecting Persisted State ===

Thread 1 - Number of messages: 4
Thread 1 - Checkpoint ID: 1f1271bc-e86c-64b0-8004-a103aea5e363
Thread 2 - Number of messages: 2
Thread 2 - Checkpoint ID: 1f1271bc-efc3-6312-8001-dbba5416c3d9
```

---

## 11_message_management.py

> **Feature:** Three message management techniques — `trim_messages` (token-budget trimming), `RemoveMessage` (selective deletion), and the summarize-then-prune pattern. The output shows: (1) trimming a 10-message history to fit a token budget (system message always kept), and (2) replacing old messages with a summary while preserving recent context — critical for long conversations that exceed context windows.

```
=== Example 1: Trim Messages ===

Original message count: 10
Trimmed message count: 9
  [Human] What is Python?
  [AI] Python is a high-level programming language known for its simplicity and readabi...
  [Human] What about JavaScript?
  [AI] JavaScript is a versatile language primarily used for web development, both fron...
  [Human] Compare their type systems.
  [AI] Python uses dynamic typing with optional type hints. JavaScript also uses dynami...
  [Human] Which is better for AI/ML?
  [AI] Python dominates AI/ML due to libraries like TensorFlow, PyTorch, and scikit-lea...
  [Human] Summarize what we discussed so far.

=== Example 2: Remove Specific Messages ===

User: Hi! I'm learning about machine learning.
AI: That's great to hear! Machine learning is a fascinating field with many applications...

User: What's the difference between supervised and unsupervised learning?
AI: Supervised and unsupervised learning are two fundamental approaches in machine learning...

User: Can you give an example of supervised learning?
AI: Certainly! One classic example of supervised learning is spam detection for email systems...

User: What about reinforcement learning?
AI: Reinforcement learning (RL) is another important paradigm in machine learning...

Messages remaining: 2
Summary: The user is learning about machine learning and asks about the difference between supervised and unsupervised learning. The AI explains that supervised learning involves training on labeled data to predict outcomes, while unsupervised learning works with unlabeled data to identify patterns.
```

---

## 12_long_term_memory.py

> **Feature:** Cross-thread long-term memory with `InMemoryStore`, `get_store()`, `store.put()`, and `store.search()`. The output shows: (1) Thread 1 stores user preferences in the memory store, (2) Thread 2 (a completely separate conversation) retrieves those preferences from the store — demonstrating memory that persists across threads, unlike the per-thread checkpointer in example 10.

```
=== Thread 1: Teaching Preferences ===

User: I like programming in Python and I prefer dark mode editors.
AI: Got it! You enjoy programming in Python and prefer dark mode editors. How can I assist you today?

User: I enjoy hiking on weekends.
AI: Noted! You enjoy hiking on weekends. If you need any hiking tips or recommendations, feel free to ask!

=== Thread 2: Preferences Remembered ===

User: What do you know about my preferences?
AI: You like programming in Python and prefer dark mode editors. You also enjoy hiking on weekends.

=== Store Contents ===

Stored memories: 2
  [pref_0] {'text': 'I like programming in Python and I prefer dark mode editors.', 'type': 'preference'}
  [pref_1] {'text': 'I enjoy hiking on weekends.', 'type': 'preference'}
```

---

## 13_time_travel.py

> **Feature:** Replay and fork from historical checkpoints using `get_state_history()` and `update_state()`. The output shows: (1) a 3-turn conversation building up 9 checkpoints, (2) listing the checkpoint history, (3) replaying from an earlier checkpoint and injecting a different user message ("I changed my mind, I want Vue.js"), and (4) the forked timeline diverging from the original — the forked timeline has fewer messages since it branched earlier.

```
=== Building Conversation History ===

User: Hi! I'm building a web app with React.
AI: That's great to hear! Building a web app with React can be a rewarding experience...

User: Should I use Redux or Zustand for state management?
AI: Choosing between Redux and Zustand for state management in your React application depends on...

User: I decided to go with Zustand. What middleware should I use?
AI: Zustand is quite flexible and allows you to use middleware to extend its functionality...

=== Checkpoint History ===

Total checkpoints: 9

  Checkpoint 0: 6 messages (id: 1f1271bf-1ec8-6886-8007-b63fe3c4e69e)
  Checkpoint 1: 5 messages (id: 1f1271be-a4e9-6948-8006-b0c7fd062a4f)
  Checkpoint 2: 4 messages (id: 1f1271be-a4e8-6d18-8005-5fa425593490)
  ...
  Checkpoint 8: 0 messages (id: 1f1271be-4389-613a-bfff-486b4807621c)

=== Replay from Checkpoint (after first exchange) ===

Replaying from checkpoint with 2 messages
User: Actually, I changed my mind. I want to use Vue.js instead.
AI: No problem at all! Vue.js is a fantastic choice for building web applications...

=== Forked Timeline ===

Messages in forked timeline: 2
Messages in original timeline: 4
```

---

## 14_human_in_the_loop.py

> **Feature:** Human-in-the-loop interrupts with `interrupt()` and `Command(resume=...)`. The output shows: (1) the graph pauses at a tool node and enters "interrupted" status, (2) the pending approval details are surfaced (action, amount, accounts), and (3) after the human approves, the graph resumes and completes the transfer — enabling gated execution for sensitive operations.

```
=== Human-in-the-Loop: Approval Flow ===

Graph status: interrupted
Next nodes to run: ('tools',)

Pending approval: {'action': 'transfer_funds', 'from': 'ACC-001', 'to': 'ACC-002', 'amount': 500.0, 'message': 'Approve transfer of $500.00 from ACC-001 to ACC-002?'}

--- Human approves the transfer ---

H: Transfer $500 from ACC-001 to ACC-002
AI: [Calling: ['transfer_funds']]
Tool: Transfer of $500.00 from ACC-001 to ACC-002 completed successfully.
AI: The transfer of $500 from ACC-001 to ACC-002 has been completed successfully.
```

---

## 15_retry_policies.py

> **Feature:** Automatic retries with exponential backoff via `RetryPolicy` and `add_node(..., retry_policy=...)`. The output shows: (1) a flaky API failing twice then succeeding on the 3rd attempt (with ~2s backoff between retries visible in timestamps), and (2) a permanently broken API exhausting all 3 retries and raising the final `ConnectionError` — demonstrating both recovery and graceful failure.

```
=== Retry Policy Demo ===

Calling flaky API (will fail first 2 attempts)...

  [!] Attempt 1 at 00:54:04 - FAILED (simulated transient error)
  [!] Attempt 2 at 00:54:06 - FAILED (simulated transient error)
  [+] Attempt 3 at 00:54:08 - SUCCESS

Final result: Processed: API returned data for 'fetch_user_data' after 3 attempts


=== Retry Exhaustion Demo ===

Calling permanently broken API (max 3 attempts)...

  [!] Attempt 1 - FAILED
  [!] Attempt 2 - FAILED
  [!] Attempt 3 - FAILED

Retries exhausted! Caught: ConnectionError: Permanent failure
```

---

## 16_map_reduce.py

> **Feature:** Fan-out parallelism with the `Send` API. The output shows: (1) 4 topics dispatched to parallel worker nodes via `Send`, (2) each worker independently analyzing its topic, and (3) a synthesizer node aggregating all results into a unified report — demonstrating dynamic parallel execution where the number of workers is determined at runtime.

```
=== Map-Reduce with Send API ===

Analyzing 4 topics in parallel...

--- Individual Analyses ---

**Quantum Computing**: As of October 2023, quantum computing is experiencing significant advancements, with major tech companies making strides in error correction, qubit scalability, and algorithm development. The future outlook indicates a rapidly growing ecosystem where quantum computing may transform industries such as cryptography and pharmaceuticals within the next decade.

**Renewable Energy**: Renewable energy sources such as solar and wind continue to experience rapid growth, spurred by technological advancements and increased investment. Projections indicate that renewables could dominate the global energy landscape by 2040, driven by decarbonization goals.

**Space Exploration**: Space exploration is experiencing unprecedented growth, marked by increased investments from both government agencies and private companies. The future appears promising, with potential plans for manned missions to Mars and sustained human presence on the Moon.

**Artificial General Intelligence**: The field of AGI remains in a speculative yet rapidly evolving stage, with advancements in machine learning pushing the boundaries of narrow AI capabilities. Many experts predict that achieving true AGI could occur within the next few decades, albeit with significant safety challenges.

--- Synthesized Report ---

As of October 2023, critical advancements are being made across several high-tech fields, including quantum computing, renewable energy, space exploration, and artificial general intelligence. Quantum computing is nearing practical applications, with potential to revolutionize industries by surpassing classical computing within the next decade. Renewable energy sources are set to dominate the energy landscape by 2040 due to technological improvements and supportive policies. Similarly, space exploration is witnessing a boom in investment, paving the way for ambitious missions to the Moon and Mars.
```

---

## 17_subgraphs.py

> **Feature:** Subgraph composition — using a compiled graph as a node within a parent graph. The output demonstrates two patterns: (1) **shared state** where parent and subgraph use the same `MessagesState` schema (a research → verify → summarize pipeline), and (2) **different state** where the subgraph has its own internal schema (text analysis returning word count, sentiment, and summary) — showing how to encapsulate complex logic behind a single node.

```
=== Example 1: Subgraph with Shared State ===

[Human] Tell me about the James Webb Space Telescope

[AI] 1. The James Webb Space Telescope (JWST) was launched on December 25, 2021, as a collaborative project between NASA, ESA, and the Canadian Space Agency.
2. JWST features a 6.5-meter primary mirror...
3. It is designed to observe the universe primarily in infrared wavelengths...

[AI] Verification Note: All provided facts about the James Webb Space Telescope (JWST) are accurate as of my knowledge cutoff in October 2023.

[AI] The James Webb Space Telescope (JWST), launched on December 25, 2021, is a collaboration between NASA, the European Space Agency, and the Canadian Space Agency. With its 6.5-meter primary mirror, JWST is designed to observe the universe primarily in infrared wavelengths.


=== Example 2: Subgraph with Different State ===

Input: LangGraph is an excellent framework for building stateful AI agents. It provides...
Analysis: Words: 27, Sentiment: positive, Summary: LangGraph is a highly effective framework for creating stateful AI agents, offering robust tools for graph-based workflows, persistence, and streaming.
```

---

## 18_multi_agent_handoffs.py

> **Feature:** Multi-agent handoffs using `Command(goto=...)` to transfer control between specialist agents within a single graph. The output shows: (1) a sales inquiry routed from triage to the sales agent, which calls `lookup_pricing` and answers with plan details, and (2) a support inquiry routed to the support agent, which calls `check_system_status` and reports the dashboard issue — demonstrating dynamic agent selection and tool specialization.

```
=== Multi-Agent Handoffs ===

--- Scenario 1: Sales inquiry ---

H: What's the pricing for the pro plan?
AI: I'll transfer you to our sales team.
AI: [Calling: ['lookup_pricing']]
Tool: $29.99/month - 100 users, 50GB storage
AI: The pricing for the Pro plan is $29.99/month, which includes support for 100 users and 50GB of storage.

Final active agent: sales

--- Scenario 2: Support inquiry ---

H: The dashboard is loading very slowly. What's going on?
AI: I'll transfer you to our support team.
AI: [Calling: ['check_system_status']]
Tool: Dashboard: Degraded performance (investigating)
AI: The dashboard is currently experiencing degraded performance, and the team is investigating the issue.

Final active agent: support
```

---

## 19_orchestrator_worker.py

> **Feature:** Orchestrator-worker pattern using `Send` for dynamic delegation and `with_structured_output` for structured planning. The output shows: (1) the orchestrator LLM decomposing "launch a SaaS product" into 3 subtasks, (2) worker nodes executing each subtask in parallel, and (3) a synthesizer combining all worker outputs into a cohesive final report — demonstrating LLM-driven task planning with parallel execution.

```
=== Orchestrator-Worker Pattern ===

Orchestrator created 3 subtasks:
  1. Develop Technical Architecture Overview
  2. Formulate Marketing Strategy
  3. Establish Pricing Model

  Worker completed: Develop Technical Architecture Overview
  Worker completed: Establish Pricing Model
  Worker completed: Formulate Marketing Strategy

--- Final Output ---

**Comprehensive Guide for Launching a New SaaS Product**

**1. Technical Architecture Overview**
To effectively support our SaaS product, we will utilize Amazon Web Services (AWS) for its robust cloud infrastructure. The architecture will adopt a microservices approach with RESTful APIs facilitating communication between individual services.

**2. Marketing Strategy**
An effective marketing strategy will begin with a thorough analysis of our target audience using demographic and psychographic insights. Key components include SEO, social media engagement, content marketing, and targeted online advertisements.

**3. Pricing Model**
We will explore tiered subscription plans, a freemium model, and a pay-per-use model. Competitor analysis and customer surveys will refine our pricing approach to align with market expectations.
```

---

## 20_evaluator_optimizer.py

> **Feature:** Generate-evaluate loop with conditional looping and structured evaluation. The output shows: (1) the generator producing marketing copy, (2) the evaluator scoring it 9/10 and determining it meets the quality threshold, and (3) the loop terminating after just 1 iteration — if the score were below threshold, it would loop back to the generator with feedback, demonstrating self-improving output via iterative refinement.

```
=== Evaluator-Optimizer Loop ===

[Iteration 1] Generator output:
  Transform your living space into a personalized oasis with our innovative smart home device. Powered by advanced AI, it learns your daily routines to...
[Iteration 1] Evaluator: score=9/10, meets_threshold=True

--- Final Result ---
Iterations: 1
Final Score: 9/10
Output:
Transform your living space into a personalized oasis with our innovative smart home device. Powered by advanced AI, it learns your daily routines to seamlessly adjust lighting, temperature, and music, ensuring optimal comfort at every moment. Whether you're winding down after a long day or getting ready to entertain, this device creates the perfect ambiance without you lifting a finger. Embrace effortless living and experience a home that truly understands your needs.
```

---

## 21_functional_api.py

> **Feature:** The functional API with `@entrypoint`, `@task`, `entrypoint.final`, and futures for parallel execution. The output shows three patterns: (1) parallel tasks analyzing 3 topics concurrently using futures, (2) `entrypoint.final` returning a value to the caller while saving different data to the checkpoint, and (3) a sequential pipeline (draft → review) producing a published article with metadata — all without constructing a `StateGraph`, using decorators instead.

```
=== Example 1: Basic Functional API ===

  Quantum Computing: Quantum computing represents a monumental shift in computational capability, with the potential to solve complex problems intractable for classical computers, thus revolutionizing fields such as cryptography, material science, and pharmaceuticals.
  Gene Editing: Gene editing is critically important as it holds the potential to revolutionize medicine, agriculture, and biotechnology by enabling precise modifications to DNA.
  Nuclear Fusion: Nuclear fusion holds immense importance for its potential to provide a nearly limitless and clean source of energy, which could significantly reduce reliance on fossil fuels.


=== Example 2: entrypoint.final ===

Returned to caller: The report on Artificial Intelligence Ethics examines the moral implications of AI technologies, focusing on issues such as bias, transparency, accountability, and the need for regulatory frameworks.
Saved in checkpoint: The report on Artificial Intelligence Ethics examines the moral implications of AI technologies...


=== Example 3: Sequential Pipeline ===

  Draft: The future of space travel promises to revolutionize our understanding of the un...
  Reviewed: Get ready for an exhilarating leap into the cosmos! With groundbreaking technolo...

  Final output:
    Topic: The Future of Space Travel
    Content: Get ready for an exhilarating leap into the cosmos! With groundbreaking technological advancements paving the way for human colonies on Mars and deeper exploration of celestial bodies, the future of space travel is set to redefine our understanding of the universe.
    Words: 50
    Status: published
```

## 22_error_handling_and_caching.py

```
=== Successful Query ===
  Answer: The capital of France is Paris.

=== Failed Query (triggers error handler) ===
  [Error Handler] Recovered from failure for: 'Please fail this lookup'
  Answer: [Fallback] Could not process 'Please fail this lookup' — service unavailable.

=== Cached Query (same input, uses cache) ===
  Answer: The capital of France is Paris.

=== Node Configuration ===
  cache_policy.ttl: 60s
  error_handler: on_lookup_error (graceful degradation)
```

> Demonstrates node-level error handlers and cache policies (new in v1.2.0) — graceful degradation when nodes fail, and TTL-based caching for expensive computations.

## 23_runtime_context.py

```
=== Same input, two different runtime contexts ===

  context ....... RequestContext(user_id='u-100', locale='English', tone='formal')
  profile ....... Alice (enterprise plan)
  reply ......... Yes, as an enterprise plan user, you have the ability to export your data at any time.
  state keys .... ['profile', 'question', 'reply']  <- no user_id/locale/tone in state

  context ....... {'user_id': 'u-200', 'locale': 'Portuguese', 'tone': 'playful'}
  profile ....... Bruno (free plan)
  reply ......... Oi Bruno! No plano gratuito, você pode sonhar em exportar seus dados, mas por enquanto, vamos aproveitar juntos tudo o que temos por aqui! 🌟
  state keys .... ['profile', 'question', 'reply']  <- no user_id/locale/tone in state

=== Custom stream written from runtime.stream_writer ===

  {'step': 'load_profile', 'user_id': 'u-100'}
  {'step': 'answer', 'tone': 'terse'}

=== runtime.previous (functional API, needs a checkpointer) ===

  +10  previous=0   total=10
  +5   previous=10  total=15
  +2   previous=15  total=17
```

> The two runs share the identical input state `{"question": ...}` and differ only in the `context=` argument, yet the profile lookup and the reply language/tone both change — proof the context reached the nodes. The `state keys` line is the load-bearing part: `user_id`, `locale` and `tone` never appear in state, so they are never checkpointed and never passed through a reducer. `runtime.previous` is functional-API-only, hence the separate `@entrypoint` section.

## 24_overwrite_and_deferred_nodes.py

```
=== Reducer append, then Overwrite ===

  notes = ['seed']
  notes = ['seed', 'gathered-a', 'gathered-b']
  notes = ['summary of 3 notes']

  Without Overwrite the last line would have been
  ['seed', 'gathered-a', 'gathered-b', 'summary of 3 notes']

=== JSON form of Overwrite ===

  notes = ['summary via JSON form']

=== Two parallel Overwrites on the same channel ===

  InvalidUpdateError: Can receive only one Overwrite value per super-step.
  There is no reducer left to merge them, so LangGraph refuses to pick.

=== Fan-in across uneven branches ===

  defer=False
    report ran 2x, log entries visible per call: [2, 5]
    final log = ['extract', 'lookup', 'enrich', 'report(saw 2)', 'score', 'report(saw 5)']

  defer=True
    report ran 1x, log entries visible per call: [4]
    final log = ['extract', 'lookup', 'enrich', 'score', 'report(saw 4)']

  Without defer, 'lookup' finishes in super-step 1 and fires 'report'
  before the long branch is done. defer=True holds it until the run
  is about to end, so it runs once with every branch collected.
```

> No LLM calls — fully deterministic. The `notes` progression shows `operator.add` appending, then `Overwrite` replacing the channel wholesale. `defer=False` runs the fan-in node twice (seeing 2 then 5 entries) because the short branch finishes first; `defer=True` runs it exactly once with all 4 entries.

## 25_timeouts_and_durability.py

```
=== Constraint: timeout= requires an async node ===

  ValueError at compile(): Node timeouts are only supported for async nodes because sync Python execution cannot be safely cancelled in-process. Node 'sync_node' is sync.

=== Async node exceeding timeout=0.3 ===

  NodeTimeoutError: Node 'slow_fetch' exceeded its run timeout of 0.300s (elapsed: 0.301s).

=== TimeoutPolicy + RetryPolicy(retry_on=NodeTimeoutError) ===

  run_timeout=0.3s  idle_timeout=0.2s
  attempt 1 timed out, then: fetched on attempt 2

=== Durability modes over a 3-node run ===

  durability=sync   -> 5 checkpoint(s) persisted
  durability=async  -> 5 checkpoint(s) persisted
  durability=exit   -> 1 checkpoint(s) persisted

  "sync"/"async" write every super-step, so the run is resumable from
  the last completed node. "exit" writes once at the end — cheapest,
  but an interrupted run has nothing to resume from.
```

> No LLM calls — timings come from `asyncio.sleep`. Note where the async-only constraint bites: `add_node(..., timeout=)` accepts a sync node silently and `compile()` is what raises. The checkpoint counts are the proof for durability: 5 for `"sync"`/`"async"` versus 1 for `"exit"`.

## 26_event_streaming_v3.py

```
=== run.messages -> message.text deltas ===

  node=chat
  deltas: 'J' 'upiter' ' is' ' the' ' largest' ' planet' '.'
  assembled: Jupiter is the largest planet.
  tokens:    33

=== run.values -> snapshots, run.output -> final state ===

  snapshot 0: 1 message(s)
  snapshot 1: 2 message(s)
  run.output keys: ['messages']
  final answer:    Mercury is the smallest planet.

=== transformers=[UpdatesTransformer] -> run.extensions['updates'] ===

  projections available: ['values', 'messages', 'lifecycle', 'subgraphs', 'updates']
  update from 'chat': Venus is the hottest planet.

=== run.subgraphs -> nested run handles ===

  subgraph 'delegate' at path ('delegate:b19a8a75-996e-2a8b-298a-b6a365c7ef08',)
    Mars is the reddest planet.

=== run.interrupted / run.interrupts ===

  interrupted: True
  waiting on:  {'question': 'Deploy to production?'}
```

> Every section uses a fresh `stream_events(..., version="v3")` call: projections are single-consumer and iterating one is what pumps the graph, so a run cannot be replayed across projections. `values`/`messages`/`lifecycle`/`subgraphs` are always present; `updates` only appears because `transformers=[UpdatesTransformer]` opted it in. Running this also prints a `LangChainBetaWarning` on stderr — v3 is still marked experimental.
