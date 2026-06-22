# Agno Example Outputs

Captured outputs from running all 17 examples against agno v2.6.18 with `gpt-4o-mini`.

> These outputs may vary between runs due to LLM non-determinism. The structure and tool invocations should remain consistent.

---

## 00_basic_agent.py

```
╭──────────────────────────────────────────────────────────────────────────────╮
│ The phrase "Hello, World!" is commonly used as a simple example in           │
│ programming tutorials to illustrate the basic syntax of a programming        │
│ language, originating from the 1972 Bell Labs' book "The C Programming       │
│ Language" by Brian Kernighan and Dennis Ritchie.                             │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 01_agent_with_tools.py

```
╭────────────────────────────────────────────────────────────────╮
│ In Lisbon right now:                                           │
│                                                                │
│ - **Weather**: Sunny, 25°C, with a light breeze from the west. │
│ - **Local Time**: 14:30 (UTC+1).                               │
╰────────────────────────────────────────────────────────────────╯
```

---

## 02_async_agent.py

```
=== Query 1 ===
╭──────────────────────────────────────────────────────────────────────────────╮
│ ### What's New with Python                                                   │
│                                                                              │
│ Python 3.13 has been released, introducing several performance improvements  │
│ and new features.                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯

=== Query 2 ===
╭──────────────────────────────────────────────────────────────────────────────╮
│ ## Agno Framework Updates                                                    │
│                                                                              │
│ ### Agno v2.5                                                                │
│ - Introduction of step-based workflows                                       │
│ - Added support for teams                                                    │
│ - Improved tool support                                                      │
╰──────────────────────────────────────────────────────────────────────────────╯

=== Query 3 ===
╭──────────────────────────────────────────────────────────────────────────────╮
│ ## Latest Developments in AI                                                 │
│                                                                              │
│ - AI Adoption Growth: 40% increase year-over-year in enterprise software.    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 03_streaming.py

```
=== Streaming response ===

### The Colorful Awakening

In a small workshop filled with the whirring of machinery, there resided a
curious little robot named Artie. Unlike other robots that were designed for
tasks like assembly lines or data analysis, Artie dreamt of creating beauty...

[Token-by-token streaming output — full short story rendered in real time]

=== Stream complete ===
```

---

## 04_structured_output.py

```
╭──────────────────────────────────────────────────────────────────────────────╮
│ {                                                                            │
│   "title": "Pastéis de Nata (Portuguese Custard Tarts)",                     │
│   "description": "A classic Portuguese dessert featuring a flaky pastry...", │
│   "ingredients": [                                                           │
│     {"name": "puff pastry", "quantity": "500 grams (store-bought)"},         │
│     {"name": "granulated sugar", "quantity": "150 grams"},                   │
│     {"name": "egg yolks", "quantity": "6"},                                  │
│     ...                                                                      │
│   ],                                                                         │
│   "steps": [                                                                 │
│     "Preheat the oven to 250°C (482°F).",                                    │
│     ...                                                                      │
│   ],                                                                         │
│   "prep_time_minutes": 30                                                    │
│ }                                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯

Recipe: Pastéis de Nata (Portuguese Custard Tarts)
Prep time: 30 minutes
Number of ingredients: 10
Number of steps: 9
```

---

## 05_team.py

```
INFO Agent 'Researcher' inheriting model from Team: gpt-4o-mini
INFO Agent 'Writer' inheriting model from Team: gpt-4o-mini
INFO Agent 'Critic' inheriting model from Team: gpt-4o-mini
╭──────────────────────────────────────────────────────────────────────────────╮
│ # The Evolution of Python: A Historical Overview                             │
│                                                                              │
│ Python, one of the most popular programming languages in the world today,    │
│ has a fascinating history filled with innovation and community-driven        │
│ growth...                                                                    │
│                                                                              │
│ ## The Birth of Python                                                       │
│ - Guido van Rossum created Python in December 1989                           │
│ - Python 0.9.0 released in February 1991                                     │
│                                                                              │
│ ## The Rise of Popularity                                                    │
│ - Python 1.0 (1994): lambda, map, filter, reduce                             │
│ - Python 2.0 (2000): list comprehensions, garbage collection                 │
│                                                                              │
│ ## The Transition to Python 3                                                │
│ - Python 3.0 (2008): breaking changes for modernization                      │
│                                                                              │
│ ## The Explosion of Adoption                                                 │
│ - Data science/ML libraries (NumPy, Pandas, TensorFlow)                      │
│ - Python Software Foundation (PSF) established in 2001                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 06_workflow.py

```
╭──────────────────────────────────────────────────────────────────────────────╮
│ ### Investment Summary Report: Large-Cap Tech Stocks                         │
│                                                                              │
│ #### Current Stock Prices                                                    │
│ - **Apple Inc. (AAPL):** $195.50                                             │
│ - **Alphabet Inc. (GOOGL):** $142.30                                         │
│ - **Microsoft Corp. (MSFT):** $420.10                                        │
│                                                                              │
│ #### Key Investment Risks                                                    │
│ - Market Volatility                                                          │
│ - Regulatory Scrutiny                                                        │
│ - Technological Changes                                                      │
│ - Consumer Spending Dependence                                               │
│ - Global Supply Chain Risks                                                  │
│                                                                              │
│ #### Recommendations                                                         │
│ - Stay informed about market trends and regulations                          │
│ - Diversify investments across sectors                                       │
│ - Implement risk management strategies                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 07_human_in_the_loop.py

```
=== Initial run (will pause for confirmation) ===

╭───────────────────────────────────────────────────╮
│ I have tools to execute, but I need confirmation. │
╰───────────────────────────────────────────────────╯

Pending confirmations: 1
  Tool: send_email
  Args: {'to': 'alice@example.com', 'subject': 'Meeting Tomorrow',
         'body': 'Hi Alice, confirming our meeting at 3pm.'}

=== Continuing run after approval ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ The email has been sent to **alice@example.com** with the subject            │
│ **'Meeting Tomorrow'**. The body of the email stated:                        │
│                                                                              │
│ *"Hi Alice, confirming our meeting at 3pm."*                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 08_knowledge_rag.py

```
INFO Adding content from Pastéis de Nata
INFO Adding content from Bacalhau à Brás
INFO Adding content from Francesinha
INFO Adding content from Caldo Verde
INFO Found 4 documents
╭──────────────────────────────────────────────────────────────────────────────╮
│ The **Francesinha** is a traditional Portuguese sandwich originating from    │
│ **Porto**. It consists of cured ham, linguiça, fresh sausage, and steak,    │
│ covered with melted cheese and a rich spiced tomato-beer sauce. Typically    │
│ served with French fries.                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

============================================================

INFO Found 4 documents
╭──────────────────────────────────────────────────────────────────────────────╮
│ **Pastéis de Nata** are Portuguese custard tarts from the Jerónimos          │
│ Monastery in Belém, Lisbon. Made with puff pastry, egg yolks, sugar, milk,  │
│ and vanilla. Baked at high temperature until caramelized.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 09_memory.py

```
=== Interaction 1: Sharing information ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ Nice to meet you, Alice! As a software engineer who loves hiking and         │
│ Portuguese food, you have a great mix of interests.                          │
╰──────────────────────────────────────────────────────────────────────────────╯

=== Interaction 2: Testing recall ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ How about a hiking trip to explore some beautiful trails? You could pack a   │
│ delicious picnic featuring some Portuguese food to enjoy along the way.      │
╰──────────────────────────────────────────────────────────────────────────────╯

=== Interaction 3: Specific recall ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ I remember that your name is Alice, you're a software engineer, and you      │
│ have a love for hiking and Portuguese food.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 10_storage.py

```
=== Turn 1 ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ Great choice! Variables are fundamental in programming...                    │
│                                                                              │
│ ### What is a Variable?                                                      │
│ A variable is like a container used to store data values.                    │
│                                                                              │
│ ### Declaring Variables in Python                                            │
│ name = "Alice"    # A string variable                                        │
│ age = 25          # An integer variable                                      │
╰──────────────────────────────────────────────────────────────────────────────╯

=== Turn 2 ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ Loops are essential in programming...                                        │
│                                                                              │
│ ### 1. For Loop                                                              │
│ for fruit in fruits:                                                         │
│     print(fruit)                                                             │
│                                                                              │
│ ### 2. While Loop                                                            │
│ while count <= 5:                                                            │
│     print(count)                                                             │
╰──────────────────────────────────────────────────────────────────────────────╯

=== Turn 3 ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ Let's create an exercise that involves both variables and loops...           │
│                                                                              │
│ ### Exercise: Student Grades                                                 │
│ - Create a list of student names                                             │
│ - Create a list of their grades                                              │
│ - Use a for loop to print each student and grade                             │
│ - Calculate the average using a while loop                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 11_guardrails.py

```
=== Test 1: Valid request ===

╭────────────────────────────────────────╮
│ The capital of Portugal is **Lisbon**. │
╰────────────────────────────────────────╯

=== Test 2: Blocked request (disallowed keyword) ===

ERROR    Validation failed: Request blocked: contains disallowed keyword 'hack'.
╭──────────────────────────────────────────────────────╮
│ Request blocked: contains disallowed keyword 'hack'. │
╰──────────────────────────────────────────────────────╯

=== Test 3: Blocked request (too long) ===

ERROR    Validation failed: Request blocked: input too long (1200 chars, max 500).
╭────────────────────────────────────────────────────────╮
│ Request blocked: input too long (1200 chars, max 500). │
╰────────────────────────────────────────────────────────╯
```

---

## 12_reasoning_tools.py

```
=== Problem 1: Logic puzzle ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ The farmer has **8 sheep left alive**. The phrase "all but 8 die" indicates  │
│ that 8 sheep remain.                                                         │
╰──────────────────────────────────────────────────────────────────────────────╯

=== Problem 2: Planning ===

╭──────────────────────────────────────────────────────────────────────────────╮
│ ### Schedule                                                                 │
│ - 11:00 AM - 12:00 PM: Gym session                                          │
│ - 12:00 PM - 12:30 PM: Free time                                            │
│ - 12:30 PM - 1:15 PM: Lunch                                                 │
│ - 1:15 PM - 1:30 PM: Get ready                                              │
│ - 1:30 PM - 2:00 PM: Commute to meeting                                     │
│ Meeting Time: 2:00 PM                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

## 13_session_state.py

```
=== Step 1: Add items ===

╭────────────────────────────────────╮
│ I've added the items to your cart: │
│                                    │
│ - **Notebook** for **$12.99**      │
│ - **Pen** for **$3.50**            │
│                                    │
│ ### Running Total: **$16.49**      │
╰────────────────────────────────────╯

=== Step 2: View cart ===

╭─────────────────────────────╮
│ Here's what's in your cart: │
│                             │
│ - **Notebook**: $12.99      │
│ - **Pen**: $3.50            │
│                             │
│ ### **Total: $16.49**       │
╰─────────────────────────────╯

=== Step 3: Add more and check total ===

╭──────────────────────────────────────────────────────────╮
│ I've added a **coffee mug** for **$8.00** to your cart.  │
│                                                          │
│ ### Your current total is **$24.49**.                    │
╰──────────────────────────────────────────────────────────╯

=== Raw session state ===
Cart: {'cart': [{'item': 'Notebook', 'price': 12.99}, {'item': 'Pen', 'price': 3.5},
{'item': 'coffee mug', 'price': 8.0}], 'total': 24.49}
```

---

## 14_mcp_tools.py

```
Secure MCP Filesystem Server running on stdio
╭─────────────────────────────────────────────────────────────────╮
│ Here are the first 10 entries in the `/private/tmp` directory:  │
│                                                                 │
│ 1. [FILE] 0b26-efca-172f-fc4d                                   │
│ 2. [FILE] 0d8e-6046-f80a-b4a9                                   │
│ 3. [FILE] 1958-f6e4-9301-e34a                                   │
│ ...                                                              │
│ 10. [FILE] 65a4-5845-bc7b-a1d2                                  │
│                                                                 │
│ Let me know if you need more information or further assistance! │
╰─────────────────────────────────────────────────────────────────╯
```

---

## 15_hooks.py

```
=== Run 1 ===

  [PRE-HOOK] Received input: What is the speed of light?...
  [POST-HOOK] Generated output: The speed of light in a vacuum is approximately...
  [POST-HOOK] Disclaimer appended.
╭──────────────────────────────────────────────────────────────────────────────╮
│ The speed of light in a vacuum is approximately **299,792 kilometers per     │
│ second** (or about **186,282 miles per second**).                            │
│                                                                              │
│ ---                                                                          │
│ *Disclaimer: This is AI-generated content for demonstration purposes.*       │
╰──────────────────────────────────────────────────────────────────────────────╯

=== Run 2 ===

  [PRE-HOOK] Received input: Who invented the telephone?...
  [POST-HOOK] Generated output: The telephone was invented by Alexander Graham Bell...
  [POST-HOOK] Disclaimer appended.
╭────────────────────────────────────────────────────────────────────────╮
│ The telephone was invented by Alexander Graham Bell in 1876.           │
│                                                                        │
│ ---                                                                    │
│ *Disclaimer: This is AI-generated content for demonstration purposes.* │
╰────────────────────────────────────────────────────────────────────────╯

=== Hook call log ===
  1. [INPUT] What is the speed of light?
  2. [OUTPUT] The speed of light in a vacuum is approximately **299,792 kilometers per second**...
  3. [INPUT] Who invented the telephone?
  4. [OUTPUT] The telephone was invented by Alexander Graham Bell in 1876.
```

---

## 16_approval_decorator.py

```
=== Example 1: Safe operation (list files) ===

╭─────────────────────────────────────╮
│ ### Files in the current directory: │
│ - `report.pdf`                      │
│ - `notes.txt`                       │
│ - `budget.xlsx`                     │
│ - `photo.jpg`                       │
╰─────────────────────────────────────╯

=== Example 2: Destructive operation (delete file — needs approval) ===

╭───────────────────────────────────────────────────╮
│ I have tools to execute, but I need confirmation. │
╰───────────────────────────────────────────────────╯

Pending approvals: 1
  Tool: delete_file
  Args: {'filename': 'notes.txt'}

=== Continuing after approval ===

╭──────────────────────────────────────────╮
│ The file **notes.txt** has been deleted. │
╰──────────────────────────────────────────╯
```

> The @approval decorator gates the delete_file tool behind human approval while list_files executes freely.
