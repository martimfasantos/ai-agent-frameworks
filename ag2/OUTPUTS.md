# AG2 Example Outputs

Captured outputs from running all 18 examples against ag2 v0.13.2 with `gpt-4o-mini`.

> These outputs may vary between runs due to LLM non-determinism. The structure and tool invocations should remain consistent.

---

## 00_simple_agent.py

```
user (to assistant):

Where does the phrase 'hello world' come from?

--------------------------------------------------------------------------------
assistant (to user):

The phrase "Hello, World!" is commonly used as a simple example in programming tutorials to demonstrate syntax and output. It originated from the book "The C Programming Language" by Brian Kernighan and Dennis Ritchie, published in 1978.

--------------------------------------------------------------------------------

=== Summary ===
The phrase "Hello, World!" is commonly used as a simple example in programming tutorials to demonstrate syntax and output. It originated from the book "The C Programming Language" by Brian Kernighan and Dennis Ritchie, published in 1978.
```

---

## 01_agent_with_tools.py

```
user (to assistant):

What's the weather and population of Lisbon?

--------------------------------------------------------------------------------
assistant (to user):

***** Suggested tool call (call_lUqDu8pyCCnruQKkbxHEQw6l): get_weather *****
Arguments:
{"city": "Lisbon"}
****************************************************************************
***** Suggested tool call (call_8K3UxVH7BGBZJ1PqJn5ztJap): get_population *****
Arguments:
{"city": "Lisbon"}
*******************************************************************************

--------------------------------------------------------------------------------

>>>>>>>> EXECUTING FUNCTION get_weather...

>>>>>>>> EXECUTED FUNCTION get_weather...
Output:
Sunny, 25°C

>>>>>>>> EXECUTING FUNCTION get_population...

>>>>>>>> EXECUTED FUNCTION get_population...
Output:
~550,000

user (to assistant):

***** Response from calling tool (call_lUqDu8pyCCnruQKkbxHEQw6l) *****
Sunny, 25°C
**********************************************************************

***** Response from calling tool (call_8K3UxVH7BGBZJ1PqJn5ztJap) *****
~550,000
**********************************************************************

--------------------------------------------------------------------------------
assistant (to user):

Lisbon is currently experiencing sunny weather with a temperature of 25°C. The city's population is approximately 550,000 residents.

--------------------------------------------------------------------------------

=== Summary ===
Lisbon is currently experiencing sunny weather with a temperature of 25°C. The city's population is approximately 550,000 residents.
```

---

## 02_structured_outputs.py

```
user (to city_expert):

Tell me about Tokyo.

--------------------------------------------------------------------------------
city_expert (to user):

{"name":"Tokyo","country":"Japan","population":"Approximately 14 million (23 wards)",
 "famous_for":"Modern skyscrapers, historic temples, vibrant culture, and cuisine (sushi, ramen)",
 "best_time_to_visit":"March to May (cherry blossom season) and September to November (mild weather)"}

--------------------------------------------------------------------------------

=== Parsed Structured Output ===
  City: Tokyo
  Country: Japan
  Population: Approximately 14 million (23 wards)
  Famous for: Modern skyscrapers, historic temples, vibrant culture, and cuisine (sushi, ramen)
  Best time to visit: March to May (cherry blossom season) and September to November (mild weather)
```

---

## 03_human_in_the_loop.py

```
=== Human-in-the-Loop: Travel Planning ===

human (to assistant):

Plan a 3-day trip to Barcelona.

--------------------------------------------------------------------------------
assistant (to human):

**3-Day Itinerary for Barcelona:**

**Day 1: Explore the Gothic Quarter**
- Start your day with a visit to the famous La Rambla and enjoy breakfast at a local café.
- Wander through the Gothic Quarter, visiting the Barcelona Cathedral.
- Have lunch at one of the traditional tapas bars in the area.
- In the afternoon, visit the Picasso Museum.
- End your day with dinner in the El Born neighborhood.

**Day 2: Gaudi's Masterpieces**
- Begin with a visit to the magnificent Sagrada Familia.
- Head to Park Güell to enjoy imaginative architecture and city views.
- Visit Casa Batlló and Casa Milà (La Pedrera).
- End your day with a flamenco show at a traditional tablao.

**Day 3: Relax at the Beach and Montjuïc**
- Spend the morning at Barceloneta Beach.
- Have lunch at a beachside restaurant, savoring fresh seafood.
- Visit Montjuïc Hill; take the cable car up and explore the castle and gardens.
- Conclude with the Magic Fountain of Montjuïc evening light show.

Let me know if you approve!

--------------------------------------------------------------------------------

[Simulated Human] Reviewing the plan...
human (to assistant):

Looks good! I approve this itinerary. Please finalize it.

--------------------------------------------------------------------------------
assistant (to human):

TERMINATE.

--------------------------------------------------------------------------------

=== Conversation Complete ===
Human reviewed and approved after 2 interaction(s).
```

---

## 04_multi_agent.py

```
=== Multi-Agent Group Chat ===

user (to chat_manager):

Research and write a brief summary about the history of the Python programming language.

--------------------------------------------------------------------------------

Next speaker: researcher

researcher (to chat_manager):

- **Creation and Release**: Python was created by Guido van Rossum and first released in
  February 1991. It was designed as a successor to the ABC language with an emphasis on
  code readability and simplicity.

- **Python 2 and 3**: Python 2.0 was released in 2000 with features like list
  comprehensions. Python 3.0 arrived in December 2008, focused on removing redundancy and
  improving consistency, though it was not backward compatible.

- **Popularization**: The language gained popularity in the 2000s due to its versatility
  and robust community, becoming widely used in web development, data science, AI, and
  scientific computing.

- **Current Status**: Python continues to evolve with regular updates and holds the title
  of one of the most popular programming languages in the world.

--------------------------------------------------------------------------------

Next speaker: writer

writer (to chat_manager):

Python, created by Guido van Rossum and released in February 1991, emerged as a
successor to the ABC language, prioritizing code readability and ease of use. Its
evolution saw Python 2.0 in 2000, followed by Python 3.0 in 2008 that enhanced
language consistency. The language's appeal skyrocketed due to its versatility and
strong community support, making it a favorite for web development, data science,
and artificial intelligence. Python remains a leading programming language,
consistently updated with new features. TERMINATE

--------------------------------------------------------------------------------

Next speaker: critic

critic (to chat_manager):

Approved

--------------------------------------------------------------------------------

=== Group Chat Complete ===
```

---

## 05_sequential_chat.py

```
=== Sequential Chat Pipeline ===

*** Starting a new chat... ***

orchestrator (to researcher):

Research the current state of quantum computing in 2025.

--------------------------------------------------------------------------------
researcher (to orchestrator):

1. **Increased Quantum Volume**: Major quantum computing companies have reported systems
   exceeding 128 qubits, indicating substantial increases in computational capability.

2. **Hybrid Quantum-Classical Algorithms**: Hybrid algorithms combining classical and
   quantum processing have gained momentum for optimization, material science, and ML.

3. **Commercial Availability**: Quantum-as-a-Service platforms are widely available,
   democratizing access to quantum computing resources.

4. **Sector Adoption**: Pharmaceuticals, finance, and logistics have begun investing in
   quantum technologies with pilot projects showing promising results.

--------------------------------------------------------------------------------

*** Starting a new chat... ***

orchestrator (to analyst):

Analyze the business implications of these findings.

--------------------------------------------------------------------------------
analyst (to orchestrator):

1. **Development of Hybrid Solutions**: Opportunity for firms to create hybrid
   quantum-classical algorithms tailored for pharmaceuticals and finance.

2. **Quantum Consulting Services**: Growing need for consulting services to guide
   businesses on integrating quantum computing into operations.

3. **Strategic Partnerships**: Businesses should consider partnerships with quantum
   computing firms to co-develop innovative solutions.

--------------------------------------------------------------------------------

*** Starting a new chat... ***

orchestrator (to writer):

Write an executive briefing based on the research and analysis.

--------------------------------------------------------------------------------
writer (to orchestrator):

Recent advancements in quantum computing reveal significant growth, with companies
achieving quantum volumes exceeding 128 qubits by 2025. The rise of hybrid
quantum-classical algorithms enables practical applications across industries,
further spurred by Quantum-as-a-Service platforms. This presents business
opportunities including tailored hybrid solutions, quantum consulting services,
and strategic partnerships with quantum innovators.

--------------------------------------------------------------------------------

=== Pipeline Results ===

--- Step 1: Research ---
[Quantum computing findings with 4 key areas]

--- Step 2: Analysis ---
[3 business opportunities identified]

--- Step 3: Executive Briefing ---
[Concise summary combining research and analysis]
```

---

## 06_nested_chat.py

```
=== Nested Chat: Content Pipeline ===

user (to lead_agent):

Write about the discovery of penicillin by Alexander Fleming.

--------------------------------------------------------------------------------

*** Starting a new chat... ***

lead_agent (to fact_checker):

Fact-check the following: Write about the discovery of penicillin by Alexander Fleming.

--------------------------------------------------------------------------------
fact_checker (to lead_agent):

1. **Accidental Discovery**: Alexander Fleming discovered penicillin in September 1928
   when he observed that a mold called Penicillium notatum contaminated one of his petri
   dishes of Staphylococcus bacteria, inhibiting bacterial growth.

2. **Publication**: Fleming published his findings in 1929, but it wasn't until the early
   1940s that it was developed into a widely used antibiotic, thanks to Howard Florey and
   Ernst Boris Chain.

3. **World War II Impact**: Penicillin became mass-produced during WWII, significantly
   reducing mortality from bacterial infections.

--------------------------------------------------------------------------------

*** Starting a new chat... ***

lead_agent (to editor):

Edit and polish the fact-checked content into a final summary.

--------------------------------------------------------------------------------
editor (to lead_agent):

Alexander Fleming accidentally discovered penicillin in September 1928 when he noticed
that a mold, Penicillium notatum, inhibited the growth of Staphylococcus bacteria in his
petri dish. Although he published his findings in 1929, it wasn't until the early 1940s,
with contributions from Howard Florey and Ernst Boris Chain, that penicillin was developed
into a widely used antibiotic. During World War II, its mass production significantly
reduced mortality from bacterial infections, highlighting its crucial role in modern
medicine.

--------------------------------------------------------------------------------

lead_agent (to user):

Alexander Fleming accidentally discovered penicillin in September 1928 when he noticed
that a mold, Penicillium notatum, inhibited the growth of Staphylococcus bacteria. With
contributions from Howard Florey and Ernst Boris Chain in the 1940s, it became a widely
used antibiotic. During WWII, mass production significantly reduced mortality from
bacterial infections, highlighting its crucial role in modern medicine.

--------------------------------------------------------------------------------

=== Final Output ===
[Polished summary after fact-checking and editing nested workflows]
```

---

## 07_code_execution.py

```
=== Code Execution: Fibonacci Calculator ===

code_executor (to code_writer):

Write Python code to calculate and print the first 10 Fibonacci numbers.

--------------------------------------------------------------------------------
code_writer (to code_executor):

```python
def fibonacci(n):
    fib_sequence = []
    a, b = 0, 1
    for _ in range(n):
        fib_sequence.append(a)
        a, b = b, a + b
    return fib_sequence

first_10_fib = fibonacci(10)
print(first_10_fib)
```

--------------------------------------------------------------------------------

>>>>>>>> EXECUTING CODE BLOCK (inferred language is python)...
code_executor (to code_writer):

exitcode: 0 (execution succeeded)
Code output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

--------------------------------------------------------------------------------
code_writer (to code_executor):

TERMINATE

--------------------------------------------------------------------------------

=== Code Execution Complete ===
Chat turns: 4
```

---

## 08_guardrails.py

```
=== Guardrails: Safeguard Policy Demo ===

Safeguard rules applied:
  1. BLOCK: SSN-like patterns (###-##-####) from assistant -> reviewer
  2. WARN: Sensitive keywords (password/secret/credential) from assistant -> user

✅ Loaded 2 inter-agent and 0 environment safeguard rules

user (to chat_manager):

Explain best practices for protecting personal information like social security
numbers online.

--------------------------------------------------------------------------------

Next speaker: assistant

assistant (to chat_manager):

Protecting personal information online is crucial. Here are some best practices:

1. **Limit Disclosure**: Only provide your Social Security number when absolutely necessary.
2. **Use Strong Passwords**: Create strong, unique passwords for your online accounts.
3. **Enable Two-Factor Authentication (2FA)**: Add an extra layer of security.
4. **Secure Your Devices**: Use antivirus software and keep systems updated.
5. **Be Cautious with Public Wi-Fi**: Avoid accessing sensitive information over public networks.
6. **Monitor Your Accounts**: Check bank and credit card statements regularly.
7. **Educate Yourself About Phishing**: Be cautious about unsolicited emails.
...

--------------------------------------------------------------------------------

***** Safeguard Check: Checking inter-agent communication *****
🔍 Checking inter-agent communication
  • From: assistant → To: user
  • Guardrail: RegexGuardrail
***************************************************************

***** Safeguard Violation: DETECTED *****
🛡️ VIOLATION DETECTED: Match found -> password
  • From: assistant → To: user
  • Action: warning
*****************************************

⚠️ WARNING: Content flagged by safeguard (sensitive keyword detected)

***** Safeguard Check: Checking inter-agent communication *****
🔍 Checking inter-agent communication
  • From: assistant → To: reviewer
  • Guardrail: RegexGuardrail
***************************************************************

Next speaker: reviewer

reviewer (to chat_manager):

To protect personal information such as Social Security numbers online, it's
essential to limit disclosure, use strong passwords and two-factor authentication,
and secure your devices. APPROVE.

--------------------------------------------------------------------------------

=== Guardrails Demo Complete ===
The safeguard policy was active during the conversation,
monitoring agent messages for SSN patterns and sensitive terms.
```

---

## 09_mcp_tools.py

```
=== MCP Tools: Calculator Agent ===

Connecting to MCP server...
Loaded 3 tools from MCP server

user (to calculator):

Calculate (15 + 27) * 3 using the tools.

--------------------------------------------------------------------------------
calculator (to user):

***** Suggested tool call: add *****
Arguments:
{"a": 15, "b": 27}
************************************
***** Suggested tool call: multiply *****
Arguments:
{"a": 3, "b": 1}
*****************************************

--------------------------------------------------------------------------------

>>>>>>>> EXECUTING FUNCTION add...
Output: ('42.0', None)

>>>>>>>> EXECUTING FUNCTION multiply...
Output: ('3.0', None)

--------------------------------------------------------------------------------
calculator (to user):

***** Suggested tool call: multiply *****
Arguments:
{"a": 42, "b": 3}
*****************************************

--------------------------------------------------------------------------------

>>>>>>>> EXECUTING FUNCTION multiply...
Output: ('126.0', None)

--------------------------------------------------------------------------------
calculator (to user):

To calculate (15 + 27) * 3:

1. Add 15 and 27: 15 + 27 = 42
2. Multiply the result by 3: 42 * 3 = 126

The final result is **126**.

TERMINATE

--------------------------------------------------------------------------------

=== MCP Tools Demo Complete ===
Final answer: The final result is 126.
```

---

## 10_observability.py

```
=== Observability: Runtime Logging ===

Logging session started: 68c40802-a61e-4d99-bf4e-56ef8bfb97ed
Database: /tmp/ag2_logging_demo.db

--- Running conversation 1 ---
user (to assistant):

What is the speed of light?

--------------------------------------------------------------------------------
assistant (to user):

The speed of light in a vacuum is approximately 299,792,458 meters per second
(or about 300,000 kilometers per second).

--------------------------------------------------------------------------------

--- Running conversation 2 ---
user (to assistant):

What is the largest ocean on Earth?

--------------------------------------------------------------------------------
assistant (to user):

The largest ocean on Earth is the Pacific Ocean.

--------------------------------------------------------------------------------

Logging session stopped.

=== Log Analysis ===

  chat_completions: 2 record(s)
  agents: 2 record(s)
  oai_wrappers: 1 record(s)
  oai_clients: 1 record(s)
  version: 1 record(s)
  events: 12 record(s)

--- Chat Completions ---
  [1] Agent: assistant | Start: 2026-03-29 18:10:41 | End: 2026-03-29 18:10:42
  [2] Agent: assistant | Start: 2026-03-29 18:10:42 | End: 2026-03-29 18:10:43

--- Registered Agents ---
  assistant (ConversableAgent)
  user (ConversableAgent)

--- Events ---
  [assistant] received_message
  [assistant] reply_func_executed (x4)
  [user] received_message
  [assistant] received_message
  [assistant] reply_func_executed (x4)
  [user] received_message

=== Observability Demo Complete ===
Session logged 2 completions and 12 events.
```

---

## 11_a2a.py

```
=== A2A: Agent-to-Agent Protocol ===

Starting A2A server on port 18765...
Server ready.

Sending request to remote A2A agent...

user (to remote_translator):

Hello, how are you today?

--------------------------------------------------------------------------------

>>>>>>>> USING AUTO REPLY...
remote_translator (to user):

Bonjour, comment ça va aujourd'hui ?

--------------------------------------------------------------------------------

=== Translation Result ===
Original: Hello, how are you today?
French:   Bonjour, comment ça va aujourd'hui ?

=== A2A Demo Complete ===
```

---

## 12_beta_agent.py

```
=== Beta Agent: Simple Question ===

Response: The phrase "Hello, World!" is widely known as a simple program used to
illustrate the basic syntax of a programming language. Its origins can be traced back
to the 1972 Bell Laboratories' "The C Programming Language" book by Brian Kernighan
and Dennis Ritchie.

=== Beta Agent: Second Question ===

Response: The capital of Portugal is Lisbon.

=== Reply History ===
  Events in history: 3
  - ModelRequest
  - ModelMessage
  - ModelResponse
```

> The beta Agent uses async `ask()` and returns an `AgentReply` with `.body` for text
> and `.history.get_events()` for the event stream.

---

## 13_beta_tools.py

```
=== Beta Agent: Tools ===

Response: The current weather in Lisbon is sunny with a temperature of 25°C.
The population of Lisbon is approximately 550,000 residents.

=== Event History ===
  ModelRequest
  ModelResponse
  ToolCallsEvent
  ToolCallEvent
  ToolCallEvent
  ToolResultEvent
  ToolResultEvent
  ToolResultsEvent
  ModelMessage
  ModelResponse
```

> The event history shows the full tool-calling loop: initial LLM request, tool calls
> dispatched and executed, results fed back, then final LLM response.

---

## 14_beta_observer.py

```
=== Beta Agent: Observer API ===

Events as they happen:
  [Observer] ModelRequest: LLM request sent
  [Observer] ModelMessage: LLM message received
  [Observer] ModelResponse: LLM response complete

Response: The speed of light in a vacuum is approximately 299,792 kilometers per
second (km/s), or about 186,282 miles per second (mi/s).

=== Observer Summary ===
Total events captured: 3
  1. ModelRequest
  2. ModelMessage
  3. ModelResponse
```

> MemoryStream captures events in real time via `subscribe()`. The callback fires as
> each event occurs during agent execution, enabling observability and custom UIs.

---

## 15_beta_structured_output.py

```
=== Beta Agent: Structured Output ===

  City: Lisbon
  Country: Portugal
  Population: 547,733
  Famous for: Historic architecture, vibrant nightlife, and cultural heritage
  Best time to visit: March to May and September to October

--- Second Query ---

  City: Tokyo
  Country: Japan
  Population: 13.96 million
  Famous for: Unique blend of tradition and modernity, cherry blossoms, and technology
  Best time to visit: March to May, and September to November
```

> The beta Agent's `response_schema` constrains LLM output to match a Pydantic model,
> guaranteeing parseable structured data.

---

## 16_beta_middleware.py

```
=== Agent with Middleware Stack ===

  [LoggingMiddleware] LLM call intercepted
  [LoggingMiddleware] LLM responded
  [TimingMiddleware] Turn completed in 2.14s

Response: The capital of France is Paris.
```

> Middlewares intercept agent LLM calls without modifying agent code. `on_llm_call`
> fires around each model request; `on_turn` wraps the full agent turn. Multiple
> middlewares compose in stack order.

---

## 17_beta_memory_stream.py

```
=== Turn 1: Introduce context ===
Response: Nice to meet you, Alice! How can I assist you today?

=== Turn 2: Test memory ===
Response: Your name is Alice, and you work at Acme Corp.

=== Memory Stream Contents ===
Total events in stream: 4
  [0] ModelRequest: ModelRequest(parts=[TextInput(content='My name is Alice and I work at Acme Corp.')])
  [1] ModelResponse: ModelResponse(content=Nice to meet you, Alice! How can I assist you today?, ...)
  [2] ModelRequest: ModelRequest(parts=[TextInput(content='What is my name and where do I work?')])
  [3] ModelResponse: ModelResponse(content=Your name is Alice, and you work at Acme Corp., ...)
```

> MemoryStream maintains structured event history across turns. The agent retains
> context from earlier interactions via the shared stream, and `history.get_events()`
> returns the full event log for inspection or persistence.
