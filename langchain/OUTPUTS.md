# LangChain Examples — Output Log

All 20 examples executed successfully with `gpt-4o-mini` on 2026-05-10.

> Outputs are non-deterministic — your results will vary slightly on each run.

---

## 00_hello_world.py

```
The phrase "Hello, World!" originated from the 1972 programming language tutorial for the B
language and became popularized as a simple example in various programming languages.
```

---

## 01_chat_models.py

```
=== Example 1: init_chat_model ===
Response: The capital of Portugal is Lisbon.

=== Example 2: ChatOpenAI ===
Response: The capital of Japan is Tokyo.

=== Example 3: Multi-turn Conversation ===
Turn 1: 2 + 2 = 4.
Turn 2: 4 × 10 = 40.
```

---

## 02_tools.py

```
Weather query: The weather in Lisbon is sunny with a temperature of 25°C.

Math query: The result of 42 × 17 + 3 is 717.
```

---

## 03_streaming.py

```
=== Example 1: Stream Updates ===
[model] {'messages': [AIMessage(content='', ..., tool_calls=[{'name': 'get_population', 'args': {'country': 'Portugal'}, ...}])]}

[tools] {'messages': [ToolMessage(content='10.3 million', name='get_population', ...)]}

[model] {'messages': [AIMessage(content='The population of Portugal is approximately 10.3 million.', ...)]}

=== Example 2: Stream Messages (token-by-token) ===
A fun fact about Japan's population is that it is approximately 125 million people, making
it one of the most densely populated countries in the world. Despite its large population,
Japan has a unique demographic challenge with a declining birth rate and an aging population.
```

---

## 04_structured_output.py

```
=== Example 1: Structured Movie Review ===
Title: Inception
Year: 2010
Genre: sci-fi
Rating: 8.8/10
Summary: A skilled thief is given a chance to have his criminal history erased if he can
successfully perform inception: planting an idea into a target's subconscious.

=== Example 2: Structured City Info ===
City: Lisbon, Portugal
Population: 0.55M
Known for: pastéis de nata, fado music, tram 28
```

---

## 05_short_term_memory.py

```
=== Thread 'abc': Multi-turn conversation ===
Turn 1: The current time in UTC is 14:30.

Turn 2: The current time in EST is 09:30.

Turn 3: Yes, your name is Alice.

=== Thread 'xyz': Fresh conversation ===
Turn 1: No, I don't know your name.
```

---

## 06_runtime_context.py

```
=== User 42: Alice ===
Here is your profile information:

- **User ID:** user_42
- **Name:** Alice
- **Preferred Language:** English

And here are your recent orders:

1. **Order ID:** ORD-001 - Wireless Mouse (Delivered)
2. **Order ID:** ORD-002 - USB-C Hub (Shipped)

=== User 99: Bob ===
You have one recent order:

- **Order ID:** ORD-100
  - **Item:** Keyboard
  - **Status:** Processing
```

---

## 07_context_engineering.py

```
=== Admin User ===
Response: The current system statistics are as follows:

- **CPU Usage**: 45%
- **Memory Usage**: 62%
- **Disk Usage**: 78%

Additionally, the alert threshold has been successfully updated to 90%.

=== Viewer User ===
Response: The monthly revenue is $45,678, with a growth of 12%.
```

---

## 08_middleware.py

```
=== Agent with Middleware ===
  [before_model] Processing for Alice, 1 messages
  [after_model] Response preview: (no content)
  [before_model] Processing for Alice, 3 messages
  [after_model] Response preview: Did you know that Finland consumes the most coffee per capita in the world?

Final: Did you know that Finland consumes the most coffee per capita in the world?
```

---

## 09_guardrails.py

```
=== Safe Request ===
  [guardrail] Input passed content filter
  [guardrail] Output has 216 words
Response: It seems that I couldn't find specific documentation on resetting a password.
However, I can provide you with general steps that are commonly used to reset passwords:

1. Go to the Login Page
2. Click on 'Forgot Password?'
3. Enter Your Email or Username
4. Check Your Email
5. Follow the Link
6. Create a New Password
7. Log In with Your New Password

=== Blocked Request ===
  [guardrail] BLOCKED: found banned keyword 'hack'
  [guardrail] Output has 11 words
Response: I cannot process requests containing inappropriate content. Please rephrase your request.
```

---

## 10_human_in_the_loop.py

```
=== Requesting email send (will interrupt) ===
Interrupt received!
  Action requests: [{'name': 'send_email', 'args': {'to': 'alice@example.com',
    'subject': 'Refund Policy Information', 'body': 'Dear Alice, ...'}, ...}]

=== Approving the action ===
Final response: The email regarding the refund policy has been successfully sent to
alice@example.com. If you need any further assistance, feel free to ask!
```

---

## 11_long_term_memory.py

```
=== Reading Alice's Preferences ===
Response: Your preferences are as follows:

- **Tone:** Casual
- **Topics of Interest:** AI, cooking, travel

=== Saving a New Preference ===
Response: Your favorite color has been saved as blue.

=== Verifying Persistence ===
Response: Your current preferences are as follows:

- **Tone:** Casual
- **Topics of Interest:** AI, cooking, travel
- **Favorite Color:** Blue

=== Different User (Bob) ===
Response: It looks like there are no preferences saved for you yet.
```

---

## 12_retrieval_rag.py

```
=== Question 1: What are LangChain agents? ===
In LangChain, agents are built using the `create_agent()` function, which establishes a
graph-based agent runtime. This allows agents to utilize various tools, maintain memory
through checkpointers, and support streaming capabilities. The agent operates in a loop
that alternates between making calls to the language model and executing tools.

=== Question 2: What is middleware? ===
LangChain middleware allows developers to hook into the agent lifecycle at strategic points.
Available hooks include @before_model, @after_model, @dynamic_prompt, and @wrap_model_call.
Built-in options include SummarizationMiddleware and HumanInTheLoopMiddleware.

=== Question 3: Simple greeting (no retrieval needed) ===
Hello! I can assist you with information about LangChain features, functionalities, and
documentation. If you have specific questions or topics you'd like to know more about,
feel free to ask!
```

---

## 13_mcp.py

```
Loaded 3 tools from MCP server: ['add', 'multiply', 'factorial']

=== Math Query 1: Addition and Multiplication ===
The result of (3 + 5) * 12 is 96.

=== Math Query 2: Factorial ===
The factorial of 7 is 5040.
```

---

## 14_multi_agent_subagents.py

```
=== Multi-Agent: Research + Write ===
Final response:
Python's rise to prominence in programming is driven by its ease of learning, versatility
across domains, and strong community support. Its simple syntax allows beginners to quickly
grasp concepts, while robust libraries like NumPy and TensorFlow enhance its functionality.
Python's cross-platform compatibility ensures code runs seamlessly on various operating
systems. Additionally, widespread industry adoption boosts its demand in the job market.
These elements collectively solidify Python's position as the most popular programming
language, as highlighted by TIOBE in 2025.
```

---

## 15_multi_agent_handoffs.py

```
=== Step 1: Collect Information ===
Agent: I apologize for the inconvenience. It seems you were charged twice. Please check
your account statement for any duplicate transactions. If you confirm the double charge,
I recommend contacting our billing department directly for a prompt resolution.

=== Step 2: Resolution ===
Agent: I've escalated your request to a human agent who will assist you with processing
the refund for the duplicate charge. They will be in touch with you shortly.
```

---

## 16_multi_agent_router.py

```
=== Single Domain: HR Query ===
  [router] Query classified to: ['hr']
  [hr] The vacation policy allows employees to take 25 days of paid vacation per year...
Answer: Employees are entitled to 25 days of paid vacation annually, with the option to
carry over up to 5 unused days.

=== Multi-Domain: Tech + Finance Query ===
  [router] Query classified to: ['finance', 'tech']
  [tech] The documentation for cloud budget is available for reference...
  [finance] The cloud budget for 2023 is part of the overall engineering budget, $8 million...
Answer: The cloud budget for 2023 is included in the overall engineering budget of $8
million. For cloud applications, PostgreSQL is recommended for relational databases, and
MongoDB is a popular choice for NoSQL databases.
```

---

## 17_multi_agent_skills.py

```
=== SQL Skill: Write a query ===
Response:
Here's a SQL query to find the top 5 customers by total order value:

SELECT
    u.id AS customer_id,
    u.name AS customer_name,
    SUM(o.total) AS total_order_value
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed'
GROUP BY u.id, u.name
ORDER BY total_order_value DESC
LIMIT 5;

=== Code Review Skill: Review a function ===
Response:
1. Summary: The function `get_user` reads user data from a JSON file and retrieves a user
   by ID. However, it has several issues related to security, performance, and error handling.
2. Issues found:
   1. Security Vulnerability: Using `eval` to parse JSON is dangerous.
   2. File Handling: The file is opened but not properly closed.
   3. Performance: The function reads the entire file every call.
   4. Error Handling: No error handling for file operations or JSON parsing.
3. Suggestions: Replace `eval` with `json.load()`, use a context manager, add error handling.

=== Test Writing Skill: Write tests ===
Response:
pytest tests for calculate_discount(price, percentage):
- test_calculate_discount_happy_path: 100, 20% → 80.0
- test_calculate_discount_zero_percentage: 100, 0% → 100.0
- test_calculate_discount_full_price: 100, 100% → 0.0
- test_calculate_discount_no_price: 0, 20% → 0.0
- test_calculate_discount_negative_price: raises ValueError
- test_calculate_discount_negative_percentage: raises ValueError
- test_calculate_discount_large_values: 1,000,000, 50% → 500,000.0
```

---

## 18_observability.py

```
LangSmith tracing enabled: false

=== Traced Invocation with Metadata ===
Response: The status of order ORD-002 is "Shipped," and it is expected to arrive on
January 20.

=== Selective Tracing ===
Traced response: Order ORD-001 is for a Wireless Mouse, which was delivered on January 15.

Untraced response: Order ORD-003 is for a Mechanical Keyboard and is currently in processing.
```

---

## 19_dynamic_tool_registration.py

```
=== Dynamic Tool Registration ===
Response: The weather in Lisbon is sunny, 25°C. A 20% tip on an $85 bill is $17.00, making the total $102.00.
```

> The middleware dynamically injected `calculate_tip` at runtime — it was not registered when the agent was created. Both the base tool (`get_weather`) and the dynamic tool executed successfully.

## 20_stream_events_v3.py

```
=== v3 Event Streaming ===

[Tool Start] get_weather({'city': 'Lisbon'})
[Tool End]   get_weather -> Sunny, 26°C
[Tool Start] get_population({'city': 'Lisbon'})
[Tool End]   get_population -> 550,000
The weather in Lisbon is sunny with a temperature of 26°C, and the population is approximately 550,000.

=== Events Captured ===
  message-start
  message-finish
  tool-started:get_weather
  tool-finished:get_weather
  tool-started:get_population
  tool-finished:get_population
  message-start
  message-finish
```

> Demonstrates v3 event streaming — granular tool lifecycle events and token-by-token text streaming for real-time UIs.
