---
**Knowledge Transfer Session: AI Use-Cases — Coding: Easy Prompts for Coding**
---

> **📌 This page serves as the pre-read material and post-session reference for the KT session on using AI/LLMs for everyday coding tasks. Bookmark this page and revisit it anytime.**

---

## Table of Contents

1. [Context and Objective](#1-context-and-objective)
2. [Audience and Prerequisites](#2-audience-and-prerequisites)
3. [LLM Fundamentals](#3-llm-fundamentals)
4. [Tokens — How LLMs Measure Usage](#4-tokens--how-llms-measure-usage)
5. [Prompt Engineering Basics](#5-prompt-engineering-basics)
6. [Tools, Templates, and Prompts for Coding](#6-tools-templates-and-prompts-for-coding)
7. [Easy Coding Prompts — Examples by Use-Case](#7-easy-coding-prompts--examples-by-use-case)
8. [Demo Steps — Live Walkthrough](#8-demo-steps--live-walkthrough)
9. [Best Practices](#9-best-practices)
10. [Common Pitfalls and How to Avoid Them](#10-common-pitfalls-and-how-to-avoid-them)
11. [Prompt Cheat Sheet — Quick Reference](#11-prompt-cheat-sheet--quick-reference)
12. [Resources](#12-resources)
13. [Glossary](#13-glossary)
14. [FAQ](#14-faq)

---

## 1. Context and Objective

### Why This Session?

AI-powered coding assistants have moved from "nice to have" to an essential part of the modern developer's toolkit. Whether you are writing a new feature, debugging a stubborn issue, or trying to understand someone else's code, LLMs can dramatically speed up your work. However, most developers either under-use these tools (sticking to simple questions) or over-rely on them (copy-pasting without understanding). The sweet spot lies in learning **how to ask the right questions** — and that is exactly what this session covers.

### Objective

By the end of this KT session, you will be able to:

- **Understand** how LLMs work at a high level — what they are, what types exist, and how they process your requests.
- **Grasp** the concept of tokens and why it matters for cost and output quality.
- **Write effective prompts** using proven patterns and techniques tailored for coding tasks.
- **Apply ready-to-use prompt templates** for your day-to-day coding needs — from writing functions to debugging to code review.
- **Recognize best practices and pitfalls** so you can use AI responsibly and efficiently in your workflow.
- **Validate and iterate** on AI-generated code instead of blindly trusting it.

### What This Session Is NOT

This session is **not** about replacing developers with AI. It is about **augmenting** your skills. AI is a powerful assistant, but you remain the decision-maker, the architect, and the person accountable for the code that ships to production.

---

## 2. Audience and Prerequisites

### Who Is This For?

- **Developers** (any level — junior, mid, senior) who want to use AI tools more effectively in their daily coding workflow.
- **Tech Leads and Engineering Managers** who want to understand how their teams can leverage AI for productivity gains.
- **QA Engineers** who want to use AI for test generation and test-case writing.
- **Anyone** on the tech team curious about how to talk to LLMs for coding help.

### Prerequisites

- Basic programming knowledge (any language — Java, Python, JavaScript, etc.).
- No prior experience with AI/ML is needed.
- A ChatGPT, Claude, Gemini, or Copilot account (free tier is fine for following along).

---

## 3. LLM Fundamentals

### 3.1 What Is a Large Language Model (LLM)?

Think of an LLM as a **super-powered autocomplete**. You give it some text (called a "prompt"), and it predicts what text should come next based on the enormous amount of text it was trained on. That training includes books, articles, code repositories, documentation, and much more. The "Large" in LLM refers to the massive number of parameters (think of these as the model's "knowledge connections") — typically ranging from billions to trillions.

**In simple terms:** An LLM is a software program that has read a huge portion of the internet and learned the patterns in human language (including programming languages). When you type something, it generates a response by predicting the most likely and relevant continuation.

### 3.2 Types of AI Models

Not all AI models are the same. Here is a breakdown you should know:

#### Foundation Models

Foundation models are the **base models** trained on massive, broad datasets. They are general-purpose and not specialized for any single task. Think of them as a college graduate who knows a little bit about everything.

| Model | Developer | Key Features |
|-------|-----------|-------------|
| **GPT-4o / GPT-4** | OpenAI | Strong reasoning, multimodal (text + image), widely used |
| **Claude 3.5 / 4 Sonnet** | Anthropic | Excellent at long context, coding, and following instructions |
| **Gemini 1.5 Pro / Flash** | Google | Massive context window (up to 1M+ tokens), multimodal |
| **Llama 3 / 3.1** | Meta (Facebook) | Open-source, can be self-hosted, strong community support |
| **Mistral / Mixtral** | Mistral AI | Open-weight models, efficient and fast |
| **DeepSeek-V3 / Coder** | DeepSeek | Open-source, strong coding capabilities |

#### Frontier Models

Frontier models are the **most advanced models at any given time** — the cutting edge of what is possible. As of mid-2025, models like GPT-4o, Claude 4 Opus/Sonnet, and Gemini 2.0 Ultra sit in this category. These models excel at complex reasoning, nuanced understanding, and generating high-quality code. They are typically accessed through APIs or subscription services and are more expensive to use.

**Key characteristics of frontier models:**
- They handle complex, multi-step reasoning well.
- They understand context deeply and rarely lose track of long conversations.
- They are better at following precise instructions.
- They come at a higher cost (both money and compute resources).

#### Small Language Models (SLMs)

SLMs are **lighter, faster, and cheaper** versions of language models. They have fewer parameters (typically 1B to 8B) but are surprisingly capable for specific, focused tasks. Think of them as a specialist rather than a generalist.

| Model | Parameters | Use Case |
|-------|-----------|----------|
| **Phi-3 / Phi-4** (Microsoft) | 3.8B - 14B | On-device coding assistance, lightweight tasks |
| **Gemma 2** (Google) | 2B - 9B | Quick responses, running locally on laptops |
| **Llama 3.2** (1B/3B) (Meta) | 1B - 3B | Mobile and edge deployment, fast completions |
| **Codestral** (Mistral) | 22B | Code-specific, runs efficiently on developer machines |

**When to use SLMs:**
- When you need **fast responses** and latency matters.
- When you want to run models **locally** for privacy or offline use.
- When the task is **simple and well-defined** (e.g., code formatting, simple function generation).
- When **cost is a constraint** and you are processing large volumes.

#### The Model Selection Mindset

You do not always need the biggest, most expensive model. Here is a simple rule of thumb:

> **Start simple, scale up when needed.** Use an SLM or mid-tier model for quick, straightforward tasks. Only reach for the frontier models when the task demands deep reasoning, long context understanding, or complex code generation.

| Task Complexity | Recommended Model Type | Examples |
|----------------|----------------------|----------|
| Simple (formatting, comments, small functions) | SLM / Mid-tier | Phi-3, GPT-3.5, Gemma |
| Medium (feature code, debugging, refactoring) | Mid-tier / Frontier | GPT-4o-mini, Claude Haiku, Llama 3 |
| Complex (architecture, multi-file changes, deep analysis) | Frontier | GPT-4o, Claude Sonnet/Opus, Gemini Pro |
| Very Complex (system design, novel algorithms, research) | Top-tier Frontier | Claude Opus, GPT-4o, Gemini Ultra |

### 3.3 How LLMs Actually Process Your Request (High Level)

When you type a prompt like *"Write a Python function to sort a list,"* here is what happens under the hood:

1. **Your text is tokenized** — broken into small pieces called tokens (more on this in the next section).
2. **Tokens are converted to numbers** — each token gets a numerical representation (embedding) that captures its meaning.
3. **The model processes these numbers** through its neural network layers, using the patterns it learned during training.
4. **It predicts the next token** — one token at a time, it generates the most likely next piece of text.
5. **It repeats** until it produces a "stop" signal or hits a length limit.

**Important takeaway:** LLMs do not "think" like humans. They do not have understanding or consciousness. They are incredibly sophisticated pattern matchers. This means they can produce confident-sounding but incorrect answers (called "hallucinations"). Always verify the output.

---

## 4. Tokens — How LLMs Measure Usage

### 4.1 What Is a Token?

A token is the **smallest unit of text** that an LLM processes. It is roughly equivalent to a word or part of a word, but the exact mapping depends on the tokenizer used by each model.

**Simple examples:**

| Text | Approximate Token Count | Notes |
|------|------------------------|-------|
| `Hello` | 1 token | Short common word = 1 token |
| `Hello world` | 2 tokens | Two common words = 2 tokens |
| `Unbelievable` | 2-3 tokens | Longer/uncommon word gets split |
| `print("Hello, World!")` | 5-7 tokens | Code often uses more tokens than plain text |
| `function calculateTotal(price, quantity) { return price * quantity; }` | ~15 tokens | Code includes symbols that each count as tokens |

**Rules of thumb:**
- **1 token ≈ 4 characters** in English text.
- **1 token ≈ 0.75 words** (or roughly 100 tokens = 75 words).
- **Code is token-heavy** — a line of code typically uses more tokens than a line of plain English because of all the symbols, brackets, and special characters.
- **Common words** (the, is, and, code, function) usually map to 1 token each.
- **Uncommon words** or technical jargon may get split into multiple tokens.

### 4.2 Why Tokens Matter

Tokens are the **currency of LLM usage**. Everything — cost, limits, and performance — is measured in tokens:

- **Input tokens** (also called "prompt tokens"): The tokens in your message/question that you send to the model.
- **Output tokens** (also called "completion tokens"): The tokens the model generates in its response.
- **Total tokens** = Input + Output. This is what most APIs bill you on.

### 4.3 Understanding Context Windows

Every model has a **context window** — the maximum total number of tokens it can process in a single conversation turn (including both your input and its output). Think of it as the model's short-term memory.

| Model | Context Window | What This Means Practically |
|-------|---------------|----------------------------|
| GPT-4o | 128K tokens | ~300 pages of text or a medium-sized codebase |
| Claude 4 Sonnet | 200K tokens | ~500 pages — can handle large files |
| Gemini 1.5 Pro | 1M - 2M tokens | Entire books, large codebases, hours of video |
| Llama 3.1 8B | 128K tokens | Similar to GPT-4o for context |
| Phi-3 | 128K tokens | Surprisingly large context for a small model |

**What happens when you exceed the context window?** The model starts "forgetting" earlier parts of the conversation. It will not crash, but the quality of its responses will degrade because it can no longer see the full context.

### 4.4 Cost Implications

Different models charge different rates per token. Here is a simplified comparison (prices change frequently, so always check current rates):

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Cost for a 50-token exchange |
|-------|----------------------|------------------------|------------------------------|
| GPT-4o | ~$2.50 | ~$10 | ~$0.0006 |
| GPT-4o-mini | ~$0.15 | ~$0.60 | ~$0.00004 |
| Claude 4 Sonnet | ~$3 | ~$15 | ~$0.0009 |
| Claude 3.5 Haiku | ~$0.80 | ~$4 | ~$0.0002 |
| Gemini 1.5 Flash | ~$0.075 | ~$0.30 | ~$0.00002 |

**In practice:** For individual developers using ChatGPT/Claude web interfaces, the token cost is baked into your subscription. But if you are building internal tools or automations using APIs, understanding token costs is crucial for budgeting.

### 4.5 How to Validate and Monitor Token Usage

If you are using LLMs through APIs (for internal tools or automation), here is how to keep track of token usage:

**Using API response headers:**
Most LLM APIs return token usage in their response. For example, the OpenAI API returns:
```
"usage": {
  "prompt_tokens": 42,
  "completion_tokens": 150,
  "total_tokens": 192
}
```

**Manual estimation:**
- Use tools like **OpenAI's Tokenizer** (tokenizer.openai.com) to count tokens before sending a request.
- Use the rule of thumb: **4 characters = 1 token** for rough estimation.
- For code, estimate **1 token per 3-4 characters** since code has more symbols.

**Practical tips:**
- Keep your prompts **concise but complete** — every unnecessary token costs money and eats into your context window.
- When working with large codebases, **only include the relevant portions** rather than pasting entire files.
- If your application uses APIs, **log token usage** and set up alerts for unexpected spikes.
- Use **cheaper models** (like GPT-4o-mini or Claude Haiku) for simple tasks and reserve frontier models for complex ones.

---

## 5. Prompt Engineering Basics

### 5.1 What Is Prompt Engineering?

Prompt engineering is the **art and science of crafting instructions** (prompts) that get the best possible output from an LLM. Think of it as learning how to communicate effectively with a very knowledgeable but very literal-minded assistant who has no context about your specific situation unless you provide it.

**A simple analogy:** Imagine you are briefing a new team member who is incredibly smart but has never worked on your project. You would not just say "fix the bug" — you would explain what the code does, what the expected behavior is, what you are seeing instead, and what you have already tried. Prompt engineering is the same principle applied to AI.

### 5.2 Anatomy of a Good Prompt

Every effective prompt has four key components:

```
┌─────────────────────────────────────────────────┐
│  1. ROLE      - Who should the AI act as?       │
│  2. CONTEXT   - What is the background?          │
│  3. TASK      - What exactly should it do?       │
│  4. FORMAT    - How should the output look?      │
│  5. CONSTRAINTS - What rules or limits apply?    │
└─────────────────────────────────────────────────┘
```

**Example — Bad Prompt vs. Good Prompt:**

| Aspect | Bad Prompt | Good Prompt |
|--------|-----------|-------------|
| Input | `Write a function to sort a list` | `You are an experienced Python developer. Write a Python function that takes a list of dictionaries (each with "name" and "age" keys) and returns the list sorted by age in descending order. Include type hints, docstrings, and a simple example usage. Return only the code block.` |
| What is missing | Everything except the task | Role, context, constraints, format |
| Expected output quality | Generic, untested | Specific, well-structured, production-ready |

### 5.3 Types of Prompts

Understanding the different prompting techniques helps you choose the right approach for each task:

#### Zero-Shot Prompting

You give the model a task with **no examples**. The model relies entirely on its training to understand what you want.

```
Prompt: "Convert the following JSON to a Java class: { 'name': 'John', 'age': 30, 'city': 'New York' }"
```

**Best for:** Simple, well-defined tasks where the expected output format is obvious.

**When it works well:** The task is common (like JSON to class conversion, writing a regex, basic formatting).

#### Few-Shot Prompting

You give the model a **few examples** of the input → output pattern before asking it to do the actual task.

```
Prompt:
"Convert SQL queries to Python Pandas code.

Example 1:
SQL: SELECT name, age FROM users WHERE age > 25
Pandas: df[['name', 'age']][df['age'] > 25]

Example 2:
SQL: SELECT city, COUNT(*) FROM users GROUP BY city
Pandas: df.groupby('city').size().reset_index(name='count')

Now convert this:
SQL: SELECT department, AVG(salary) FROM employees GROUP BY department HAVING AVG(salary) > 50000"
```

**Best for:** Tasks where showing the pattern makes the expected output much clearer.

#### Chain-of-Thought (CoT) Prompting

You ask the model to **think step by step**. This dramatically improves reasoning quality for complex tasks.

```
Prompt: "Debug this Python function. Think step by step about what could be wrong:

def calculate_discount(price, discount_percent):
    return price - discount_percent

Expected: calculate_discount(100, 20) should return 80
Actual: It returns 80 (seems right?)
Wait, actually it returns 80 which is correct numerically but the logic is wrong — it is subtracting the percentage directly instead of calculating the percentage of the price. Walk through the fix step by step."
```

**Best for:** Debugging, logic errors, mathematical calculations, and any task that benefits from explicit reasoning.

#### Role-Based Prompting

You assign a **specific role or persona** to the model to frame its responses appropriately.

```
Prompt: "You are a senior Java developer with 15 years of experience working on
enterprise applications at a bank. Review this code for potential issues:
[CODE HERE]
Focus on: thread safety, performance, error handling, and adherence to Java best practices."
```

**Best for:** Code reviews, architecture discussions, and when you want responses that reflect a specific level of expertise or perspective.

#### System Prompt vs. User Prompt

| System Prompt | User Prompt |
|--------------|-------------|
| Sets the behavior and personality of the AI | The actual question or task you want answered |
| Usually set once at the beginning of a conversation | Changes with each message you send |
| Example: "You are a helpful coding assistant that gives concise answers with code examples" | Example: "How do I reverse a string in JavaScript?" |
| In ChatGPT: This is configured via "Custom Instructions" or the API | This is what you type in the chat box |

### 5.4 Prompt Patterns for Coding

These are the most commonly useful patterns for coding tasks:

| Pattern | How It Works | Example Use |
|---------|-------------|-------------|
| **Direct Instruction** | State exactly what you want | "Write a React component that displays a user profile card with name, email, and avatar" |
| **Explain Then Fix** | Ask it to explain first, then fix | "Explain what this code does, then suggest improvements for readability" |
| **Compare Approaches** | Ask for multiple solutions | "Show me 3 different ways to flatten a nested array in JavaScript, with pros and cons of each" |
| **Iterative Refinement** | Start simple, then add requirements | "First write a basic REST API endpoint. Now add input validation. Now add error handling. Now add logging." |
| **Test-First** | Ask for tests before code | "Write unit tests for a function that validates email addresses, then write the function to pass those tests" |
| **Code Review** | Ask for review with specific criteria | "Review this pull request for security vulnerabilities, performance issues, and code style" |
| **Translate Code** | Convert between languages/frameworks | "Convert this Java Spring Boot controller to a Python FastAPI endpoint" |
| **Documentation** | Generate docs from code | "Generate a README with setup instructions, API documentation, and usage examples for this module" |

---

## 6. Tools, Templates, and Prompts for Coding

### 6.1 Popular AI Coding Tools

| Tool | Type | Best For | Free Tier? |
|------|------|----------|-----------|
| **ChatGPT** (OpenAI) | Chat interface | General coding questions, explanations, one-off tasks | Yes (GPT-4o-mini, limited GPT-4o) |
| **Claude** (Anthropic) | Chat interface | Long code reviews, large context, careful analysis | Yes (limited) |
| **GitHub Copilot** | IDE plugin | Inline code completions, real-time suggestions | Yes for students, paid for pros |
| **Cursor** | AI-native IDE | Full codebase-aware editing, AI-first development | Free basic plan |
| **Codeium / Windsurf** | IDE plugin + IDE | Free copilot alternative, code completions | Yes (generous) |
| **Gemini** (Google) | Chat interface | Multi-modal tasks, Google ecosystem integration | Yes |
| **Replit AI** | Cloud IDE + AI | Quick prototyping, learning, small projects | Yes (limited) |
| **Amazon CodeWhisperer** | IDE plugin | AWS-specific coding, enterprise environments | Yes (individual tier) |

### 6.2 Prompt Template Structure

Here is a **reusable template** you can adapt for any coding task:

```
[ROLE]
You are a [senior/junior] [language/framework] developer with [X] years of experience.

[CONTEXT]
I am working on [project/module description]. 
The tech stack is [languages, frameworks, versions].
The codebase follows [conventions/patterns].

[TASK]
Please [specific action]: [detailed description of what you want].

[CONSTRAINTS]
- Use [specific library/version/pattern]
- Follow [naming conventions/style guide]
- Do NOT [things to avoid]
- The code must [performance/security requirements]

[FORMAT]
- Return the code in a [markdown code block with language identifier]
- Include brief comments explaining the logic
- [Add any other format requirements]
```

### 6.3 Quick-Fill Templates for Common Tasks

#### Template: Write a New Function

```
Write a [language] function that [one-line description].
Parameters: [list parameters with types]
Return type: [expected return type]
Edge cases to handle: [list edge cases]
Include: [type hints / JSDoc / docstring / error handling]
```

#### Template: Debug an Issue

```
I am getting this error in [language/framework]:

[Error message]

Here is the relevant code:
[Code snippet]

What I expected: [expected behavior]
What actually happens: [actual behavior]
Environment: [OS, version, any relevant details]

Please identify the issue and provide the fix.
```

#### Template: Code Review

```
Review this [language] code for:
1. [Bug/logic errors]
2. [Performance issues]
3. [Security vulnerabilities]
4. [Code style and readability]
5. [Best practices violations]

Rate each category from 1-5 and explain your ratings.
Then provide the improved code.

Code:
[Your code here]
```

#### Template: Explain Code

```
Explain this [language] code to me as if I am a [beginner/intermediate/senior] developer.
Break it down step by step.
Highlight any non-obvious or tricky parts.

Code:
[Code here]
```

#### Template: Write Unit Tests

```
Write unit tests for this [language] function using [testing framework].
Cover the following scenarios:
1. [Happy path]
2. [Edge case 1]
3. [Edge case 2]
4. [Error case]

Function to test:
[Code here]
```

#### Template: Refactor Code

```
Refactor this [language] code to improve [readability/performance/maintainability].
Keep the same functionality.
Preserve the same public API/interface.
Explain what you changed and why.

Original code:
[Code here]
```

#### Template: Add Logging and Error Handling

```
Add comprehensive logging and error handling to this [language] code.
Use [logging framework] and follow [project conventions].
Add logs for: [entry/exit, key decisions, errors, warnings]
Handle these specific errors: [list expected errors]

Code:
[Code here]
```

---

## 7. Easy Coding Prompts — Examples by Use-Case

This is the **core section** of this guide. Below are real-world, copy-paste-ready prompts organized by common coding tasks. Each example includes the prompt, what makes it effective, and the kind of output you can expect.

---

### 7.1 Writing Functions and Utilities

#### Prompt: Generate a Utility Function
```
Write a TypeScript function called "formatCurrency" that takes a number and a currency code (like "USD", "EUR", "INR") and returns a formatted currency string using the Intl.NumberFormat API. Include proper error handling for invalid inputs, add JSDoc comments, and write 5 example usages covering different currencies and edge cases.
```

**Why this works:** It specifies the language (TypeScript), the function name, the exact API to use (Intl.NumberFormat), the expected error handling, documentation style (JSDoc), and verification examples. The model knows exactly what to deliver.

#### Prompt: Create a Data Validation Utility
```
Create a Python utility module for validating user registration data. It should validate: email (proper format), password (min 8 chars, at least one uppercase, one lowercase, one number, one special char), phone number (Indian format), and age (must be 18+). Return a dictionary with field names as keys and error messages as values. Return empty dict if all valid. Use regex patterns and include docstrings.
```

**Why this works:** It lists every validation rule clearly, specifies the Indian phone format, defines the exact return structure, and asks for documentation.

---

### 7.2 Explaining and Understanding Code

#### Prompt: Explain a Complex Code Snippet
```
Explain this JavaScript function line by line. I am a junior developer. Highlight any clever tricks, potential bugs, or performance concerns. Also suggest what you would name this function for clarity.

function debounce(fn, ms) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), ms);
  };
}
```

**Why this works:** It sets the audience level (junior developer), asks for line-by-line breakdown, and specifically requests analysis of tricks, bugs, and naming.

#### Prompt: Understand a Database Query
```
Explain what this SQL query does in plain English. Break down each clause (SELECT, FROM, WHERE, JOIN, GROUP BY) and explain the purpose. Also mention any potential performance issues.

SELECT 
    d.department_name,
    COUNT(e.employee_id) as employee_count,
    AVG(e.salary) as avg_salary,
    MAX(e.salary) as max_salary
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
WHERE e.hire_date >= '2023-01-01'
GROUP BY d.department_name
HAVING COUNT(e.employee_id) > 0
ORDER BY avg_salary DESC;
```

**Why this works:** It asks for plain English explanation, clause-by-clause breakdown, and flags potential performance issues proactively.

---

### 7.3 Debugging and Fixing Bugs

#### Prompt: Fix a Runtime Error
```
I am getting this error in my Python Flask application:

TypeError: Object of type 'datetime' is not JSON serializable

It happens when I return this from my API endpoint:
{
    "user_id": 123,
    "username": "john_doe",
    "created_at": datetime.datetime(2024, 1, 15, 10, 30, 0),
    "last_login": datetime.datetime(2024, 3, 20, 14, 45, 0)
}

Show me 3 different ways to fix this, explain the pros and cons of each, and recommend the best approach for a production Flask application.
```

**Why this works:** It includes the exact error message, the problematic data, asks for multiple solutions, and wants a recommendation — giving you options and a clear path forward.

#### Prompt: Fix a Logic Bug
```
This Python function is supposed to find the second largest number in a list, but it gives wrong results for [5, 5, 4, 3]. Walk through what happens step by step, identify the bug, and provide the corrected code with explanation.

def second_largest(numbers):
    largest = max(numbers)
    numbers.remove(largest)
    return max(numbers)
```

**Why this works:** It specifies the exact failing input, asks for step-by-step walkthrough, and requests both the fix and the explanation.

---

### 7.4 Code Review and Improvement

#### Prompt: Review a Function for Best Practices
```
You are a senior Python developer. Review this function. Rate it on a scale of 1-10 for each category:
- Correctness
- Readability
- Error handling
- Performance
- Pythonic style

For each rating below 8, explain what is wrong and how to fix it. Then provide the improved version.

def get_user_data(id):
    result = db.execute("SELECT * FROM users WHERE id=" + str(id))
    user = result.fetchone()
    return {"name": user[1], "email": user[2], "role": user[3]}
```

**Why this works:** It assigns a role (senior Python developer), uses a structured rating system, asks for explanations for issues, and requests the improved code — all in one prompt.

---

### 7.5 Refactoring Code

#### Prompt: Refactor Nested If-Else
```
Refactor this Python code to use a cleaner pattern. Remove the deep nesting, improve readability, and maintain the same behavior. Show the before and after, and explain why the refactored version is better.

def process_order(order):
    if order is not None:
        if order.items is not None:
            if len(order.items) > 0:
                if order.customer is not None:
                    if order.customer.is_verified:
                        total = sum(item.price for item in order.items)
                        return process_payment(order.customer, total)
                    else:
                        return "Customer not verified"
                else:
                    return "No customer"
            else:
                return "No items"
        else:
            return "No items"
    else:
        return "No order"
```

**Why this works:** It identifies the specific problem (deep nesting), states the goals (cleaner pattern, better readability), and asks for before/after comparison with explanation.

#### Prompt: Refactor to Use Design Pattern
```
Refactor this Java code to use the Strategy pattern. The current code has a long if-else chain for calculating shipping costs based on different carrier types. Show the refactored code with proper class structure and explain how the Strategy pattern makes it easier to add new carriers in the future.

[Include your existing code here]
```

**Why this works:** It names the specific pattern, explains the current problem (long if-else chain), states the benefit it wants to see (easier to add new carriers), and asks for explanation.

---

### 7.6 Writing Tests

#### Prompt: Generate Comprehensive Tests
```
Write comprehensive JUnit 5 tests for this Java service class. Cover:
- Happy path scenarios
- Null and empty input handling
- Boundary conditions (zero, negative, max values)
- Exception scenarios

Use @ParameterizedTest where appropriate. Include meaningful assertion messages. 

[Include your service class code here]
```

**Why this works:** It specifies the testing framework (JUnit 5), lists the categories of tests to cover, mentions parameterized tests, and asks for meaningful assertion messages.

#### Prompt: Test-Driven Development
```
I need to build a password strength checker in JavaScript. Write the tests first (using Jest) that cover these rules:
- At least 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Returns a score from 0-5 and specific feedback for each missing rule

Write all the tests, then write the implementation that passes all of them.
```

**Why this works:** It follows TDD methodology — tests first, then implementation. It clearly defines the scoring rules and expected output format.

---

### 7.7 API and Backend Development

#### Prompt: Create a REST API Endpoint
```
Create a Spring Boot REST controller for managing a "Task" entity with the following endpoints:
- POST /api/tasks - Create a new task
- GET /api/tasks - List all tasks with pagination and filtering by status
- GET /api/tasks/{id} - Get a task by ID
- PUT /api/tasks/{id} - Update a task
- DELETE /api/tasks/{id} - Delete a task

Use proper HTTP status codes, request validation, and a service layer pattern.
Include the DTO classes, the Service interface and implementation, and the Controller.
Use Java 17 records for DTOs if appropriate.
```

**Why this works:** It lists every endpoint, specifies the technology stack (Spring Boot, Java 17), mentions important patterns (service layer, records), and asks for the full stack (DTO, Service, Controller).

#### Prompt: Write a Database Migration
```
Write a Flyway migration script (V3__add_user_preferences.sql) that:
- Creates a "user_preferences" table with columns: user_id (FK to users), theme (varchar, default 'light'), language (varchar, default 'en'), notifications_enabled (boolean, default true), and created_at/updated_at timestamps
- Adds appropriate indexes
- Includes a backfill script to insert default preferences for existing users
- Is compatible with both PostgreSQL and MySQL
```

**Why this works:** It specifies the migration tool, version naming, all columns with types and defaults, asks for indexes, includes a backfill strategy, and mentions cross-database compatibility.

---

### 7.8 Frontend Development

#### Prompt: Build a React Component
```
Build a React (TypeScript) component called "SearchableUserList" that:
- Accepts an array of user objects (id, name, email, department, avatar_url) as a prop
- Has a search input that filters users by name or email as you type (debounced by 300ms)
- Shows a loading skeleton while "isLoading" prop is true
- Displays results in a clean card layout with avatar, name, email, and department
- Shows "No results found" when search yields nothing
- Is fully typed with proper interfaces
- Uses modern React patterns (hooks, functional components)
```

**Why this works:** It specifies the component name, every prop, the exact behavior (debounce timing, loading state, empty state), the visual layout, and coding standards (TypeScript, hooks).

#### Prompt: Fix a CSS Issue
```
My flexbox layout is not working as expected. The sidebar should be 250px fixed width, and the main content should take the remaining space. But when the main content has a lot of text, the sidebar gets pushed down. Here is my CSS:

[Include your CSS here]

And here is the HTML structure:
[Include your HTML here]

Explain why this is happening and provide the corrected CSS.
```

**Why this works:** It describes the expected behavior, the actual problem, and provides the current code for diagnosis.

---

### 7.9 DevOps and Scripting

#### Prompt: Write a CI/CD Pipeline
```
Write a GitHub Actions workflow file (.github/workflows/ci.yml) for a Node.js project that:
- Triggers on push to main and pull requests
- Runs on Ubuntu Latest
- Sets up Node.js 20
- Installs dependencies
- Runs linting (ESLint)
- Runs tests (Jest with coverage)
- Builds the project
- Uploads coverage report as an artifact
Fails fast if any step fails. Add helpful comments explaining each section.
```

**Why this works:** It specifies the CI tool, trigger conditions, environment, every step in order, and asks for comments.

#### Prompt: Write a Shell Script
```
Write a Bash script called "deploy.sh" that:
- Takes the environment name (dev/staging/prod) as a parameter
- Validates the parameter (exits with error message if invalid)
- Pulls the latest code from the correct branch
- Installs dependencies
- Runs database migrations
- Restarts the service
- Runs a health check with 3 retries
- Sends a Slack notification with deployment status (success or failure)
- Logs everything to a file with timestamps
Include proper error handling and make it idempotent (safe to run multiple times).
```

**Why this works:** It describes every step, asks for validation, error handling, logging, notifications, and idempotency — all critical for production scripts.

---

### 7.10 Documentation

#### Prompt: Generate API Documentation
```
Generate Swagger/OpenAPI 3.0 documentation for the following REST API endpoints. Include request/response schemas, example values, error responses, and authentication requirements.

[Describe your endpoints or paste your controller code]
```

#### Prompt: Write a README
```
Write a comprehensive README.md for this project. Include:
- Project description and purpose
- Tech stack and versions
- Prerequisites
- Setup and installation steps
- Environment variables needed (with descriptions, not actual values)
- How to run in development and production
- How to run tests
- Project structure overview
- API documentation link or summary
- Contributing guidelines
- License

Here is the project info: [Brief description of your project]
```

---

## 8. Demo Steps — Live Walkthrough

This section outlines the **step-by-step demos** that will be performed during the KT session. You can follow along in real-time or try these on your own afterward.

### Demo 1: The Power of a Good Prompt (5 minutes)

**Goal:** Show the difference between a vague prompt and a well-structured prompt.

| Step | Action |
|------|--------|
| 1 | Open ChatGPT or Claude |
| 2 | Send a vague prompt: *"Write a login page"* |
| 3 | Observe: generic, unhelpful output |
| 4 | Now send a structured prompt using the template from Section 6.2 |
| 5 | Observe: specific, usable, well-organized output |

**Key takeaway:** The same AI gives dramatically different results based on how you ask. Structure matters more than the model you use.

### Demo 2: Zero-Shot vs. Few-Shot vs. Chain-of-Thought (7 minutes)

**Goal:** Demonstrate how different prompting techniques affect output quality.

| Step | Action |
|------|--------|
| 1 | **Zero-shot:** Ask *"Convert this curl command to a Python requests call: [curl command]"* |
| 2 | Observe: likely correct, but might miss edge cases |
| 3 | **Few-shot:** Provide 2 examples of curl → Python conversions, then ask for a third |
| 4 | Observe: more consistent style, better handling of headers/auth |
| 5 | **Chain-of-Thought:** Ask *"Convert this curl command to Python. Think step by step about how each curl flag maps to a requests parameter."* |
| 6 | Observe: detailed reasoning, explicit mapping, educational |

**Key takeaway:** For simple tasks, zero-shot is fine. For consistency, use few-shot. For understanding and complex tasks, chain-of-thought wins.

### Demo 3: Iterative Coding with AI (8 minutes)

**Goal:** Show how to build code incrementally through conversation.

| Step | Prompt to Send |
|------|---------------|
| 1 | *"Write a simple Todo class in Python with add, remove, and list methods"* |
| 2 | *"Now add a method to mark a todo as complete"* |
| 3 | *"Add due dates and a method to list overdue todos"* |
| 4 | *"Now add input validation — title cannot be empty, due date must be a future date"* |
| 5 | *"Add file persistence — save todos to a JSON file and load them on initialization"* |
| 6 | *"Write unit tests for all methods using pytest"* |

**Key takeaway:** Building code iteratively with AI gives you more control and better results than asking for everything at once. Each step builds on the previous one, and you can course-correct along the way.

### Demo 4: Debugging a Real Bug (5 minutes)

**Goal:** Show AI-assisted debugging workflow.

| Step | Action |
|------|--------|
| 1 | Present a piece of buggy code (e.g., a function with an off-by-one error) |
| 2 | Ask the AI: *"What is wrong with this code? Think step by step."* |
| 3 | Observe the AI walking through the logic and identifying the bug |
| 4 | Ask: *"Show me the fix and explain why it works"* |
| 5 | Ask: *"How would I write a test that catches this bug?"* |

**Key takeaway:** AI is excellent at spotting logic errors and explaining them. Always ask it to "think step by step" for debugging.

### Demo 5: Code Review Simulation (5 minutes)

**Goal:** Demonstrate using AI as a code reviewer.

| Step | Action |
|------|--------|
| 1 | Present a piece of code with intentional issues (missing error handling, SQL injection risk, hardcoded values) |
| 2 | Ask the AI to review with specific criteria (security, performance, readability, error handling) |
| 3 | Observe the AI catching issues and suggesting improvements |
| 4 | Ask: *"Rate the severity of each issue (Critical / High / Medium / Low)"* |
| 5 | Discuss: which issues would you actually fix vs. which are nitpicks? |

**Key takeaway:** AI code reviews are great for catching common issues, but human judgment is still needed to prioritize and decide what to fix.

### Demo 6: Cross-Language Code Translation (3 minutes)

**Goal:** Show how AI can help when working across languages.

| Step | Action |
|------|--------|
| 1 | Provide a Java method and ask: *"Convert this Java method to Python, preserving the same logic and adding Pythonic idioms"* |
| 2 | Ask: *"What are the key differences between the Java and Python versions?"* |
| 3 | Discuss: when is this useful? (migrations, polyglot codebases, learning new languages) |

---

## 9. Best Practices

### 9.1 General Prompting Best Practices

| # | Practice | Explanation | Example |
|---|----------|-------------|---------|
| 1 | **Be specific** | The more detail you provide, the better the output | Instead of "fix this," say "fix the null pointer exception on line 15 caused by..." |
| 2 | **Provide context** | Include relevant code, error messages, environment details | Always paste the relevant code snippet rather than describing it |
| 3 | **Use constraints** | Tell the AI what NOT to do | "Do not use any external libraries" or "Keep the response under 50 lines" |
| 4 | **Specify the format** | Define how you want the output structured | "Return as a markdown table" or "Provide the code in a single code block" |
| 5 | **Iterate, do not start over** | Build on previous responses in the same conversation | "Now modify that function to also handle..." is better than starting fresh |
| 6 | **Ask for explanations** | Understanding the code is as important as getting it | "Explain why you chose this approach" or "What are the trade-offs?" |
| 7 | **Use examples** | Showing is faster than telling | Paste a sample input/output rather than describing the format |
| 8 | **Set the role** | Framing the AI's expertise level changes the output quality | "You are a senior developer" vs. just asking the question |
| 9 | **Break complex tasks down** | One prompt per logical task is better than a mega-prompt | Separate "write the function" from "write the tests" from "write the docs" |
| 10 | **Verify the output** | Never blindly trust AI-generated code | Always read, understand, and test the code before using it |

### 9.2 Coding-Specific Best Practices

| # | Practice | Why It Matters |
|---|----------|---------------|
| 1 | **Always include the language and version** | Python 2 vs. Python 3, ES5 vs. ES2024, Java 8 vs. Java 21 — the output differs significantly |
| 2 | **Specify the framework and version** | "Spring Boot 3.2" vs. just "Spring" — the annotations and patterns change between versions |
| 3 | **Mention your project conventions** | If your team uses specific naming conventions (camelCase, snake_case), naming patterns, or architectural patterns (repository pattern, MVC), tell the AI |
| 4 | **Provide the exact error message** | Copy-paste the full stack trace rather than summarizing it. The AI needs the exact details to diagnose accurately |
| 5 | **Include imports and dependencies** | When asking for code, specify which libraries are available. "Using React Query v5" is more helpful than just "React" |
| 6 | **Ask for tests alongside code** | Getting tests with your code gives you immediate verification. Ask: "Include unit tests for this function" |
| 7 | **Request explanations for non-obvious choices** | If the AI uses a design pattern, library function, or approach you are not familiar with, ask it to explain |
| 8 | **Keep the scope small** | Asking "build my entire application" gives poor results. Asking "build the user authentication module" gives much better results |
| 9 | **Paste only relevant code** | Do not paste your entire codebase. Include only the function, class, or module you need help with, plus any interfaces/types it depends on |
| 10 | **Use AI for learning, not just answers** | Ask "why does this work?" and "what are alternative approaches?" to actually improve your skills |

### 9.3 Security Best Practices

| # | Rule | Explanation |
|---|------|-------------|
| 1 | **NEVER share sensitive data** | Do not paste API keys, passwords, tokens, PII, or production credentials into any AI tool |
| 2 | **Never paste entire production codebases** | Use only the relevant snippets. Consider whether the code you are sharing could reveal proprietary logic |
| 3 | **Check your organization's AI policy** | Some companies have approved tools and prohibited tools. Know the policy before using AI with code |
| 4 | **Sanitize before sharing** | Remove real URLs, IP addresses, usernames, database names, and any identifying information from code before pasting it to an AI |
| 5 | **Review AI code for security issues** | AI can introduce vulnerabilities (SQL injection, XSS, insecure defaults). Always review generated code with security in mind |
| 6 | **Be cautious with internal tooling** | If using AI APIs in internal tools, ensure proper access controls, rate limiting, and data handling policies are in place |

### 9.4 Workflow Integration Tips

**For individual developers:**

| Workflow Step | How AI Helps |
|--------------|-------------|
| **Before coding** | Use AI to plan the approach: "Design the database schema for a blog system" |
| **While coding** | Use AI for specific functions: "Write a function to paginate results" |
| **After coding** | Use AI for review: "Review this function for edge cases" |
| **Before committing** | Use AI for commit messages: "Write a conventional commit message for these changes" |
| **During debugging** | Use AI to diagnose: "Why might this function return null?" |
| **During documentation** | Use AI to generate docs: "Write Javadoc for this class" |

**For teams:**

- **Create a shared prompt library** — store the best prompts your team has found in a shared document (like this Confluence page!).
- **Standardize conventions in system prompts** — if using AI tools with system prompts, encode your team's coding standards there.
- **Pair prompt + review** — one developer writes the prompt, another reviews the AI output. This catches errors and spreads AI skills across the team.
- **Track what works** — note which prompts give the best results for your specific codebase and tech stack.

---

## 10. Common Pitfalls and How to Avoid Them

| # | Pitfall | What Happens | How to Avoid It |
|---|---------|-------------|-----------------|
| 1 | **Vague prompts** | Generic, unhelpful responses | Always include language, context, and specific requirements |
| 2 | **Blindly trusting output** | Bugs and vulnerabilities in production code | Always read, understand, and test AI-generated code |
| 3 | **Over-reliance** | You stop learning and become dependent on AI | Use AI to learn, not just to get answers. Always understand the code |
| 4 | **Not iterating** | First response is often not the best | Refine your prompt, provide more context, ask for improvements |
| 5 | **Pasting too much** | AI gets confused, wastes tokens, may lose focus on the actual question | Only include the relevant code snippet (typically under 200 lines) |
| 6 | **Pasting too little** | AI has to guess, often misses the real issue | Include enough surrounding code for context — imports, type definitions, error messages |
| 7 | **Not specifying constraints** | AI uses libraries/patterns you do not want | Say "do not use external libraries" or "use only Java 8 features" |
| 8 | **Ignoring the AI's questions** | If the AI asks for clarification, provide it | A clarification round always produces better results than a guess |
| 9 | **Not version-checking** | AI might suggest deprecated APIs or old patterns | Always specify the version: "React 18", "Spring Boot 3", "Node.js 20" |
| 10 | **Sharing secrets** | API keys and passwords end up in AI training data | Sanitize code before sharing. Never paste .env files or credentials |
| 11 | **Mega-prompts** | Asking for too much in one prompt leads to incomplete, shallow results | Break large tasks into smaller, focused prompts |
| 12 | **Not learning from the output** | Copy-pasting without understanding means you will ask the same thing again | Read the code, ask "why," understand the pattern so you can do it yourself next time |

---

## 11. Prompt Cheat Sheet — Quick Reference

### The 5-Element Formula

```
ROLE + CONTEXT + TASK + CONSTRAINTS + FORMAT = Great Prompt
```

### Quick Prompt Starters

| I want to... | I should say... |
|-------------|-----------------|
| Write a function | "Write a [language] function that [does X]. Parameters: [list]. Return type: [type]. Include [error handling / docs / tests]." |
| Fix a bug | "I am getting [error message] in [language/framework]. Here is the code: [code]. What I expected: [X]. What happens: [Y]." |
| Understand code | "Explain this [language] code step by step as if I am a [beginner/intermediate] developer. Highlight non-obvious parts." |
| Review code | "Review this [language] code for [security / performance / readability / best practices]. Rate each area 1-5. Provide improved code." |
| Refactor | "Refactor this [language] code to improve [readability / performance]. Keep the same functionality. Show before and after." |
| Write tests | "Write [framework] tests for this [language] [function/class]. Cover: [happy path, edge cases, errors]." |
| Translate code | "Convert this [language A] code to [language B]. Preserve the same logic. Adapt to [language B] idioms and conventions." |
| Generate documentation | "Write [README / API docs / Javadoc] for this code. Include [setup, usage, examples, API reference]." |
| Debug step by step | "Debug this code. Think step by step about what could be wrong. Identify the root cause and provide the fix." |
| Compare approaches | "Show me different ways to [do X] in [language]. Compare [approach A] vs [approach B] with pros and cons." |

### Power Words That Improve Results

Adding these phrases to your prompts significantly improves output quality:

- **"Think step by step"** — forces explicit reasoning (especially for debugging and complex logic)
- **"Explain your reasoning"** — makes the AI show its work, helping you verify correctness
- **"Consider edge cases"** — prompts the AI to think about boundary conditions
- **"Follow best practices for [language/framework]"** — ensures modern, idiomatic code
- **"Write production-ready code"** — signals that you need error handling, validation, and proper structure (not just a quick example)
- **"Show me 3 approaches"** — gives you options to compare instead of a single answer
- **"What are the trade-offs?"** — surfaces hidden costs and considerations
- **"Optimize for [performance / readability / maintainability]"** — focuses the AI on what matters most to you

---

## 12. Resources

### Official Documentation

| Resource | URL |
|----------|-----|
| OpenAI API Documentation | https://platform.openai.com/docs |
| Anthropic (Claude) Documentation | https://docs.anthropic.com |
| Google Gemini API Documentation | https://ai.google.dev/docs |
| OpenAI Prompt Engineering Guide | https://platform.openai.com/docs/guides/prompt-engineering |
| Anthropic Prompt Engineering Guide | https://docs.anthropic.com/claude/docs/prompt-engineering |

### Free Tools and Playgrounds

| Tool | What It Does | URL |
|------|-------------|-----|
| ChatGPT | General-purpose AI chat | https://chat.openai.com |
| Claude | Long-context AI chat | https://claude.ai |
| Gemini | Google's AI chat | https://gemini.google.com |
| OpenAI Playground | Test prompts with different models | https://platform.openai.com/playground |
| Anthropic Console | Test Claude prompts | https://console.anthropic.com |
| Tokenizer (OpenAI) | Count tokens in your text | https://tokenizer.openai.com |

### Learning Resources

| Resource | Description | URL |
|----------|-------------|-----|
| Prompt Engineering Guide (DAIR.AI) | Comprehensive prompt engineering techniques | https://www.promptingguide.ai |
| Learn Prompting | Free prompt engineering course | https://learnprompting.org |
| DeepLearning.AI - ChatGPT Prompt Engineering | Free short course by Andrew Ng | https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/ |
| GitHub Copilot Docs | How to get the most from Copilot | https://docs.github.com/en/copilot |

### Prompt Libraries and Collections

| Resource | Description |
|----------|-------------|
| Awesome ChatGPT Prompts | Community-curated prompt collection for various roles and tasks |
| PromptBase | Marketplace for quality prompts |
| LangChain Hub | Shared prompts for LangChain users |
| This Confluence Page | Your team's own curated prompt library (maintain and grow it!) |

### Recommended Reading

| Topic | Resource |
|-------|----------|
| How LLMs work (visual explainer) | "Attention Is All You Need" paper summary (available on various blogs) |
| Prompt engineering fundamentals | "A Survey of Techniques for Maximizing LLM Performance" (arXiv) |
| AI coding best practices | Your organization's AI usage policy and security guidelines |
| Staying updated | Follow OpenAI, Anthropic, and Google AI blogs for new model releases and features |

---

## 13. Glossary

| Term | Simple Definition |
|------|------------------|
| **LLM** | Large Language Model — an AI that processes and generates human-like text (and code) |
| **Token** | The smallest piece of text an LLM processes (roughly 3/4 of a word in English) |
| **Context Window** | The maximum amount of text (in tokens) an LLM can consider at one time |
| **Prompt** | The instruction or question you give to an LLM |
| **Zero-Shot** | Asking an LLM to do something with no examples provided |
| **Few-Shot** | Providing a few examples before asking the LLM to perform the task |
| **Chain-of-Thought** | Asking the LLM to reason step by step for better results |
| **Hallucination** | When an LLM generates confident but incorrect or made-up information |
| **Fine-Tuning** | Additional training of a model on specific data to specialize it |
| **Foundation Model** | A base, general-purpose AI model before any specialization |
| **Frontier Model** | The most advanced AI models available at a given time |
| **SLM** | Small Language Model — a lighter, cheaper, faster model for simpler tasks |
| **API** | Application Programming Interface — how programs communicate with LLMs |
| **RAG** | Retrieval-Augmented Generation — combining LLMs with external data sources |
| **Temperature** | A setting that controls how creative or predictable the LLM's responses are |
| **System Prompt** | A hidden instruction that sets the AI's behavior for an entire conversation |
| **IDE** | Integrated Development Environment — your coding software (VS Code, IntelliJ, etc.) |

---

## 14. FAQ

### Q: Which AI tool should I use for coding?

**A:** For most developers, **ChatGPT (GPT-4o)** or **Claude (Sonnet)** are the best starting points for chat-based coding help. For inline code completions in your IDE, **GitHub Copilot** or **Codeium** (free) are excellent choices. If you want an AI-native coding environment, try **Cursor**. The key insight: the tool matters less than how you use it. A good prompt in any tool beats a bad prompt in the best tool.

### Q: Should I be worried about AI replacing developers?

**A:** AI is a tool that makes developers more productive, not a replacement. Developers who learn to use AI effectively will be more productive than those who do not. The skills that matter most — system design, understanding requirements, making trade-off decisions, and debugging complex issues — still require human judgment. Think of it this way: calculators did not replace mathematicians, and AI will not replace developers. It will, however, change what "productive" looks like.

### Q: Is it safe to paste my company's code into ChatGPT/Claude?

**A:** Check your organization's AI usage policy first. Some companies have enterprise agreements with AI providers that ensure data is not used for training. If you are using the free tier, assume anything you paste could potentially influence future model versions. Best practice: **sanitize code** before sharing (remove secrets, internal URLs, business-specific logic that is proprietary). Share only the minimal code needed to get help.

### Q: The AI gave me code that does not work. What should I do?

**A:** This is normal and expected. AI models are not perfect. Here is what to do:
1. **Share the error message** — paste the exact error into the conversation.
2. **Provide more context** — the AI might have made wrong assumptions about your setup.
3. **Ask it to think step by step** — this often catches logic errors.
4. **Iterate** — tell the AI what is wrong: "This approach does not work because [reason]. Try a different approach."
5. **Verify yourself** — always test and understand the code before considering the task done.

### Q: How do I get better at prompting?

**A:** Like any skill, prompting improves with practice. Start with the templates in this guide. Pay attention to which prompts give good results and which do not. When a response is not useful, ask yourself: "What information was I missing from my prompt?" Over time, you will develop an intuition for what makes a good prompt. Also, read the official prompt engineering guides from OpenAI and Anthropic — they are free and constantly updated.

### Q: Should I use the free or paid version of ChatGPT/Claude?

**A:** For basic coding tasks (writing simple functions, explaining concepts, basic debugging), the free tiers are often sufficient. For complex tasks (large code reviews, multi-file changes, deep analysis), the paid versions (GPT-4o, Claude Sonnet/Opus) provide significantly better results. If your organization provides access to paid tiers, use them. If not, the free tiers are still incredibly useful when paired with good prompting techniques.

---

> **💬 Questions? Feedback? Suggestions for new prompts?** Edit this page or reach out to the KT session facilitator. This is a living document — let us keep it updated with the best prompts and practices our team discovers.
