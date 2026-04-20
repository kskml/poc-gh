# AI Use-Cases: Easy Prompts for Coding

> **Knowledge Transfer Session** | Prepared for internal team enablement
> Last Updated: April 2026

---

## Table of Contents

- [1. Context and Objective](#1-context-and-objective)
- [2. LLM Basics — What You Need to Know](#2-llm-basics--what-you-need-to-know)
  - [2.1 What is an LLM?](#21-what-is-an-llm)
  - [2.2 Types of AI Models](#22-types-of-ai-models)
  - [2.3 Popular Models Available Today](#23-popular-models-available-today)
- [3. LLM and Token Concepts](#3-llm-and-token-concepts)
  - [3.1 What Are Tokens?](#31-what-are-tokens)
  - [3.2 How Tokenization Works](#32-how-tokenization-works)
  - [3.3 Why Tokens Matter — Cost and Limits](#33-why-tokens-matter--cost-and-limits)
  - [3.4 How to Validate Your Token Usage](#34-how-to-validate-your-token-usage)
- [4. Prompt Engineering Basics](#4-prompt-engineering-basics)
  - [4.1 What is Prompt Engineering?](#41-what-is-prompt-engineering)
  - [4.2 Anatomy of a Good Prompt](#42-anatomy-of-a-good-prompt)
  - [4.3 Common Prompt Techniques](#43-common-prompt-techniques)
- [5. Easy Prompts for Coding — The Main Event](#5-easy-prompts-for-coding--the-main-event)
  - [5.1 Code Generation](#51-code-generation)
  - [5.2 Code Explanation](#52-code-explanation)
  - [5.3 Code Review](#53-code-review)
  - [5.4 Bug Detection and Fixing](#54-bug-detection-and-fixing)
  - [5.5 Code Refactoring](#55-code-refactoring)
  - [5.6 Unit Test Generation](#56-unit-test-generation)
  - [5.7 Writing Code Comments and Documentation](#57-writing-code-comments-and-documentation)
  - [5.8 Code Translation and Conversion](#58-code-translation-and-conversion)
  - [5.9 Writing SQL and Database Queries](#59-writing-sql-and-database-queries)
  - [5.10 Regular Expressions](#510-regular-expressions)
  - [5.11 Working with APIs](#511-working-with-apis)
  - [5.12 Debugging Help](#512-debugging-help)
- [6. Prompt Templates for Daily Use](#6-prompt-templates-for-daily-use)
- [7. Demo Steps](#7-demo-steps)
- [8. Best Practices](#8-best-practices)
- [9. Do's and Don'ts — Quick Reference](#9-dos-and-donts--quick-reference)
- [10. Resources](#10-resources)

---

## 1. Context and Objective

### Why This Session?

Every developer today has access to AI-powered coding assistants — whether it is ChatGPT, GitHub Copilot, Claude, Gemini, or tools built into your IDE. But most developers use these tools at only a fraction of their potential. They ask vague questions, get vague answers, and conclude that "AI is not that useful for real coding." The truth is that AI coding tools are incredibly powerful when you know how to talk to them.

This Knowledge Transfer session is designed to bridge that gap. We will start from the very basics — what these AI models actually are, how they work under the hood (in simple terms), and what tokens are — and then quickly move into the practical skill that matters most: **writing effective prompts for everyday coding tasks.**

The goal is not to make you a prompt engineering expert or an AI researcher. The goal is to make you **a more productive developer** who can use AI to write better code, faster, and with fewer bugs.

### Who Is This For?

- Software developers and engineers of all experience levels
- Tech leads who want to guide their teams on AI-assisted coding
- QA engineers who want to generate better test cases
- Anyone on the team who writes code or works with code reviews

### What Will You Learn?

By the end of this session, you will be able to:

1. **Understand** the different types of AI models available and which one to use for what
2. **Explain** what tokens are, why they matter, and how to keep your costs under control
3. **Write clear, effective prompts** for common coding tasks like generating code, debugging, refactoring, writing tests, and more
4. **Apply** proven prompt patterns and templates in your daily workflow
5. **Avoid** common mistakes that lead to poor AI outputs

### Prerequisites

- Basic programming knowledge (any language)
- No prior AI or machine learning experience required

---

## 2. LLM Basics — What You Need to Know

### 2.1 What is an LLM?

**LLM** stands for **Large Language Model**. In simple terms, it is a software program that has been trained on a massive amount of text (books, articles, code, websites, conversations) so that it can understand and generate human-like text. Think of it as a very advanced version of your phone's autocomplete — but instead of predicting the next word, it can hold entire conversations, write essays, and yes, write code.

When you type a prompt like "Write a Python function to sort a list," the model does not "think" the way a human does. Instead, it calculates the most likely next words based on patterns it learned during training. Because it was trained on millions of code examples, those "likely next words" often happen to be correct, well-structured code.

**Key things to remember:**

- LLMs are **not search engines.** They do not look up information in real time (unless specifically connected to a search tool). They generate responses based on patterns learned during training.
- LLMs are **not compilers.** The code they generate may look correct but can contain bugs, logic errors, or use outdated libraries. Always review and test AI-generated code.
- LLMs have a **knowledge cutoff.** They only know information up to a certain date. Anything that happened after that date is unknown to them unless you provide it in the prompt or use a tool with search capability.
- LLMs can **hallucinate.** This means they can confidently provide incorrect information — including making up function names, library methods, or API endpoints that do not actually exist. Always verify.

### 2.2 Types of AI Models

Not all AI models are the same. Understanding the different categories helps you choose the right tool for the right job.

#### Foundation Models

A **Foundation Model** is a large AI model trained on a broad, general-purpose dataset. It is like a raw, un-specialized brain. It knows a lot about many topics but has not been fine-tuned for any specific task. Examples include GPT-3, the base Llama models, and BERT.

Think of a foundation model like a university graduate who has studied many subjects — they have a lot of general knowledge, but they are not yet a specialist in anything. To make them useful for a specific task (like coding, medical diagnosis, or legal analysis), they usually need additional training or fine-tuning.

Foundation models are typically used by companies and researchers as a starting point. Most developers interact with models that have already been fine-tuned or enhanced on top of these foundations.

#### Frontier Models

**Frontier Models** are the most advanced, capable AI models available at any given time. These are the cutting-edge models that push the boundaries of what AI can do. As of early 2026, frontier models include **GPT-4o, Claude 4, Gemini 2.5, and Grok 3**.

Frontier models are characterized by:

- **Strong reasoning ability:** They can solve complex problems, follow multi-step instructions, and handle nuanced tasks
- **Large context windows:** They can process very long prompts and documents (some handle over 1 million tokens)
- **Multimodal capabilities:** Many can process not just text but also images, audio, and even video
- **Better coding performance:** They score higher on coding benchmarks and can handle more complex programming tasks

When you need the best possible output — for complex refactoring, architecture decisions, or tricky bug fixes — a frontier model is usually your best bet. However, they are also the most expensive and slowest to respond.

#### Small Language Models (SLMs)

**Small Language Models** are compact AI models that are much smaller than frontier models — typically with 1 to 8 billion parameters compared to 100+ billion for large models. Examples include **Llama 3 (8B), Mistral (7B), Phi-3, Gemma 2,** and **DeepSeek-Coder**.

Despite their smaller size, SLMs have become surprisingly capable, especially for specific tasks. Their advantages include:

- **Speed:** They respond much faster because they are smaller
- **Cost:** They are cheaper to run, both in the cloud and on local hardware
- **Privacy:** They can be run locally on your own machine, meaning your code never leaves your device — important for companies with strict data policies
- **Specialization:** Many SLMs are fine-tuned for specific tasks like coding (e.g., DeepSeek-Coder, CodeLlama)

**When to use what?**

| Task | Recommended Model Type |
|------|----------------------|
| Quick question, simple code snippet | SLM or any model |
| Complex architecture design | Frontier model |
| Learning a new concept | Any model |
| Code running on sensitive/proprietary codebase | Local SLM |
| Writing tests for existing code | Frontier model or coding-specialized SLM |
| Everyday coding assistance | Frontier model (best results) |
| Running offline / air-gapped environment | Local SLM |

### 2.3 Popular Models Available Today

Here is a quick overview of the models you are most likely to encounter in your daily work:

| Model | Creator | Strengths | Good For |
|-------|---------|-----------|----------|
| **GPT-4o / o3** | OpenAI | Strong all-rounder, great reasoning, multimodal | General coding, complex problems |
| **Claude 4** | Anthropic | Excellent at long context, careful reasoning, safe outputs | Long code reviews, large file analysis |
| **Gemini 2.5** | Google | Massive context window, strong search integration | Projects needing web/search data |
| **GitHub Copilot** | GitHub/OpenAI | IDE-integrated, real-time suggestions | Inline coding while you work |
| **Llama 3** | Meta | Open-source, can run locally | Privacy-sensitive work, local deployment |
| **DeepSeek-Coder** | DeepSeek | Specialized for code, open-source | Code-specific tasks, local coding assistant |
| **Mistral / Codestral** | Mistral AI | Fast, efficient, coding-focused | Quick code generation, European data compliance |
| **CodeLlama** | Meta | Fine-tuned for code generation | Code completion, local coding tasks |

---

## 3. LLM and Token Concepts

### 3.1 What Are Tokens?

When you send a message to an AI model, it does not read your text the way a human does — letter by letter or word by word. Instead, it breaks your text into small chunks called **tokens**. A token is the basic unit that the model processes.

Here is how tokens roughly work in practice:

- A common English word like "apple" is usually **1 token**
- A shorter or common word like "the" or "is" might be **1 token**
- A longer or uncommon word like "unbelievable" might be **2-3 tokens**
- Numbers and code symbols each count as tokens: `function` might be 1-2 tokens
- Punctuation marks usually attach to adjacent words as part of the same token
- **In code, things get interesting:** a variable name like `userAuthenticationToken` might be 3-5 tokens because the model breaks it into subwords it recognizes

**A rough rule of thumb:**
- **English text:** 1 token ≈ 4 characters ≈ 0.75 words
- **Code:** Code is denser, so 1 token ≈ 2-3 characters on average. A 100-line Python function might use 300-500 tokens depending on how dense the code is.

### 3.2 How Tokenization Works

Tokenization is the process of breaking text into tokens. Different models use different tokenizers, so the exact token count for the same text can vary between models. Here is a simplified example:

```
Input: "Write a Python function to sort a list"

Possible tokenization:
["Write", " a", " Python", " function", " to", " sort", " a", " list"]
= 8 tokens
```

```
Input: "def calculate_user_score(user_id, transactions):"
Possible tokenization:
["def", " calculate", "_", "user", "_", "score", "(", "user", "_", "id", ",", " transactions", "):"]
= 13 tokens
```

Notice how the model breaks `calculate_user_score` into `calculate`, `_`, `user`, `_`, `score` — it splits on word boundaries it recognizes. This is why code with long variable names uses more tokens than code with short names.

**Why does this matter?** Because every token counts toward your usage limit and your cost. Sending a 10,000-token prompt costs more than a 500-token prompt, and models have a maximum number of tokens they can process in a single conversation (the "context window").

### 3.3 Why Tokens Matter — Cost and Limits

There are three practical reasons every developer should understand tokens:

#### 1. Context Window Limits

Every model has a **context window** — the maximum total number of tokens it can handle in a single interaction (your prompt + its response combined). If your conversation exceeds this limit, the model will either truncate earlier messages or return an error.

| Model | Context Window (approx.) | What This Means |
|-------|-------------------------|-----------------|
| GPT-4o | 128,000 tokens | ~300 pages of text |
| Claude 4 | 200,000 tokens | ~500 pages of text |
| Gemini 2.5 | 1,000,000 tokens | ~2,000 pages of text |
| Llama 3 (8B) | 8,000 - 128,000 tokens | Varies by version |

**Practical impact:** If you paste an entire large codebase into a model with an 8K context window, it will lose track of the earlier code. If you are working with a frontier model with 128K+ tokens, you can comfortably include multiple files and still have room for the response.

#### 2. Cost Per Token

Most AI APIs charge based on token usage. You pay for:
- **Input tokens:** The text you send (your prompt)
- **Output tokens:** The text the model generates (its response)

Pricing varies widely. As a rough guide:

| Model Tier | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) |
|-----------|--------------------------|----------------------------|
| Frontier (GPT-4o) | $2.50 - $5.00 | $10.00 - $15.00 |
| Mid-tier (GPT-4o-mini) | $0.15 - $0.60 | $0.60 - $2.40 |
| Open-source (self-hosted) | Free (but hardware costs) | Free (but hardware costs) |

**Practical impact:** A single coding session with 50 prompt-response exchanges, averaging 500 tokens each way, uses roughly 50,000 tokens — costing just a few cents on a frontier model. But if your team of 100 developers does this every day, costs add up quickly.

#### 3. Response Quality and Token Limits

Models have a **maximum output token limit** — the longest response they can generate in a single turn. For example, GPT-4o has a 16,384 token output limit. If you ask the model to "refactor this entire 500-line file," it may cut off mid-response.

### 3.4 How to Validate Your Token Usage

You do not need to guess how many tokens your prompts are using. Here are practical ways to check:

#### Using Online Token Counters

The simplest approach: use a free online tokenizer like [tokenizer.openai.com](https://tokenizer.openai.com) or [tiktoken-counter.richardotoole.com](https://tiktoken-counter.richardotoole.com). Paste your prompt, and it tells you the exact token count.

#### Using the API Response

When you use an AI model through its API, the response object includes token usage metadata:

```json
{
  "usage": {
    "prompt_tokens": 127,
    "completion_tokens": 384,
    "total_tokens": 511
  }
}
```

Your application can log these values to track usage over time, set up alerts when costs exceed a threshold, or optimize prompts that are using too many tokens.

#### Using Python (tiktoken library)

If you want to count tokens programmatically:

```python
import tiktoken

# Choose the tokenizer for your model
encoding = tiktoken.encoding_for_model("gpt-4o")

text = "Write a Python function to sort a list"
token_count = len(encoding.encode(text))
print(f"Token count: {token_count}")
# Output: Token count: 8
```

#### Practical Tips to Save Tokens

- **Be concise:** Remove unnecessary context from your prompts. Instead of pasting an entire 200-line file, paste only the relevant function.
- **Use shorter variable names in code you are sharing with the AI** (for the prompt, not your actual codebase).
- **Clear chat history** when starting a new task. Old messages in the conversation still count toward the token limit.
- **Use system prompts efficiently:** Set up your instructions once rather than repeating them in every message.
- **Choose the right model:** Do not use a frontier model for tasks a smaller model can handle just as well (simple code generation, formatting, explanations).

---

## 4. Prompt Engineering Basics

### 4.1 What is Prompt Engineering?

**Prompt engineering** is the skill of crafting instructions (called "prompts") that get the best possible output from an AI model. It is not about tricking the AI or using secret commands. It is about **communicating clearly** — the same skill that makes you a good communicator with humans also makes you good at prompting AI.

Think of it this way: if you ask a junior developer "fix this code" and hand them a 500-line file with no context, they will struggle. But if you say "this function is supposed to return the sum of all even numbers in a list, but it is returning odd numbers too — can you check the condition on line 12?" they will fix it quickly. Prompt engineering is the same principle applied to AI.

### 4.2 Anatomy of a Good Prompt

A well-crafted prompt typically contains some or all of these elements:

```
[ROLE] + [CONTEXT] + [TASK] + [CONSTRAINTS] + [FORMAT] + [EXAMPLES]
```

Let us break each one down:

**Role:** Tell the AI who it should be. This sets the tone and expertise level.
> "You are a senior Java developer with 10 years of experience."

**Context:** Provide background information the AI needs.
> "We are migrating a legacy monolithic application to microservices. The current user authentication module uses session-based auth and we need to convert it to JWT-based auth."

**Task:** Clearly state what you want done.
> "Write a Spring Boot REST controller that handles user login and returns a JWT token."

**Constraints:** Set boundaries and requirements.
> "Use Spring Security 6. Do not use deprecated APIs. Include proper error handling for invalid credentials. Follow REST best practices."

**Format:** Specify how you want the output.
> "Return only the code with inline comments. Do not include explanations."

**Examples:** Show what you expect (few-shot prompting).
> "Here is an example of the existing code style we follow: [paste example]. Match this style."

### 4.3 Common Prompt Techniques

Here are the most useful prompting techniques for coding, explained simply:

#### Zero-Shot Prompting

You give the AI a task without any examples. This works well for straightforward, common tasks.

> "Write a JavaScript function that checks if a string is a palindrome."

The model knows what a palindrome is and what JavaScript looks like, so it can do this without examples.

#### Few-Shot Prompting

You give the AI a few examples of what you want before asking it to do the actual task. This is powerful when you need a specific style, format, or pattern.

> "Here is an example of how we write validation functions in our codebase:
> ```
> function validateEmail(email) {
>   const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
>   return regex.test(email);
> }
> ```
> Now write a similar validation function for phone numbers that accepts formats like +1-234-567-8900, 234.567.8900, and (234) 567-8900."

#### Chain-of-Thought Prompting

Ask the model to think step-by-step before giving the answer. This dramatically improves accuracy for complex problems.

> "A user reports that our API returns a 500 error when they pass a date string like '2024-13-45'. Think step-by-step about what could go wrong and write a robust date validation function."

#### Role-Based Prompting

Assign a specific role to the AI to set the expertise level and perspective.

> "You are a senior security engineer. Review this code for common security vulnerabilities and suggest fixes."

#### Iterative Prompting

Do not expect the perfect answer in one shot. Have a conversation. Start broad, then refine.

> **Message 1:** "Write a REST API for managing users."
> **Message 2:** "Good, now add pagination to the list endpoint."
> **Message 3:** "Now add input validation using Joi."
> **Message 4:** "The error responses should follow this format: { code, message, details }."

This back-and-forth approach almost always produces better results than one giant, complex prompt.

---

## 5. Easy Prompts for Coding — The Main Event

This is the core of our session. Below are practical, ready-to-use prompts organized by common coding tasks. Each section explains the approach and gives you prompts you can copy, customize, and use immediately.

### 5.1 Code Generation

This is the most common use case. You describe what you need, and the AI writes the code. The key is to be specific about language, framework, and requirements.

#### Prompt 1 — Simple Function

```
Write a Python function that takes a list of integers and returns the two numbers that add up to a target sum. If no pair exists, return None. Include type hints and docstring.
```

**What makes this prompt effective:**
- Specifies the language (Python)
- Defines clear inputs (list of integers) and output (tuple of two numbers or None)
- Specifies edge case behavior (return None)
- Requests additional quality elements (type hints, docstring)

#### Prompt 2 — Full Feature / Component

```
Create a React component for a login form with the following requirements:
- Email and password fields
- "Remember me" checkbox
- Submit button that calls an onLogin prop
- Show validation errors: email must be valid format, password must be at least 8 characters
- Use TypeScript
- Follow a modern, clean UI style
- Do NOT use any external UI library — use plain CSS or inline styles
```

**What makes this prompt effective:**
- Lists all UI elements needed
- Specifies validation rules
- Sets technology constraints (TypeScript, no external libraries)
- Sets a style preference (modern, clean)

#### Prompt 3 — API Endpoint

```
Write a Node.js Express route handler for a POST /api/orders endpoint that:
- Accepts a JSON body with: userId (string), items (array of { productId, quantity }), shippingAddress (object)
- Validates that userId is not empty, items array is not empty, and each quantity is a positive integer
- Returns 201 with the created order object on success
- Returns 400 with a descriptive error message on validation failure
- Returns 500 with a generic error message on server error
- Use async/await and include proper error handling
```

#### Prompt 4 — Database Model

```
Create a Prisma schema for a blog application with the following:
- User model: id, email (unique), name, createdAt, updatedAt
- Post model: id, title, content, published (boolean), author (relation to User), createdAt, updatedAt
- Comment model: id, text, post (relation to Post), author (relation to User), createdAt
- Include proper indexes and cascade delete rules
```

### 5.2 Code Explanation

Sometimes you inherit code you did not write (or wrote a long time ago). AI can explain it to you in plain language.

#### Prompt 1 — Explain a Function

```
Explain what this function does, step by step, in plain English:

def merge_intervals(intervals):
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            last[1] = max(last[1], current[1])
        else:
            merged.append(current)
    return merged
```

#### Prompt 2 — Explain Like I'm a Beginner

```
Explain this React hook as if I am a junior developer who just learned hooks last week. What problem does it solve? When would I use it? Walk through each line:

function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}
```

#### Prompt 3 — Explain Architecture

```
I just joined this project and found this file structure. Can you explain the overall architecture pattern being used and what each directory is responsible for?

src/
  controllers/
  services/
  repositories/
  models/
  middleware/
  routes/
  utils/
  config/
```

### 5.3 Code Review

AI can act as a second pair of eyes for code reviews. It will not replace human reviewers but can catch issues early.

#### Prompt 1 — General Review

```
Review this code for:
1. Bugs or logic errors
2. Security vulnerabilities
3. Performance issues
4. Code style and readability
5. Best practices violations

Provide specific line references and suggest fixes:

[paste your code here]
```

#### Prompt 2 — Security-Focused Review

```
You are a security expert. Review this authentication middleware code for security vulnerabilities. Check for:
- SQL injection
- XSS
- CSRF
- Insecure token handling
- Improper input validation
- Information leakage in error messages

For each issue found, explain the risk and provide a fixed version of the code:

[paste your code here]
```

#### Prompt 3 — Performance Review

```
Analyze this function for performance issues. The function currently takes 5+ seconds to process a list of 10,000 items. Identify bottlenecks and suggest an optimized version:

[paste your code here]
```

### 5.4 Bug Detection and Fixing

AI is excellent at spotting bugs, especially the common ones that are easy to miss when you have been staring at code for hours.

#### Prompt 1 — Fix This Bug

```
This function is supposed to return the average of numbers in a list, but it returns the wrong result when the list is empty or contains negative numbers. Find the bug and fix it:

def calculate_average(numbers):
    total = sum(numbers)
    return total / len(numbers)
```

**What makes this prompt effective:** It describes the symptoms (wrong result with empty list or negative numbers), not just says "fix this."

#### Prompt 2 — Fix the Error Message

```
I am getting this error when running my Node.js application:

TypeError: Cannot read properties of undefined (reading 'map')
    at getFormattedUsers (users.js:15:32)

Here is my code:

const getFormattedUsers = (users) => {
  return users.map(user => ({
    id: user.id,
    fullName: `${user.firstName} ${user.lastName}`,
    email: user.email.toLowerCase()
  }));
};

What is causing this error and how do I fix it? Include a defensive coding approach.
```

#### Prompt 3 — Logic Bug

```
This function is supposed to check if a year is a leap year, but it gives incorrect results for years like 1900, 2000, and 2100. What is wrong?

function isLeapYear(year) {
  return year % 4 === 0;
}
```

### 5.5 Code Refactoring

Refactoring is one of the most powerful coding use cases for AI. Describe what you want to improve, and the AI will rewrite the code.

#### Prompt 1 — Simplify Complex Code

```
Refactor this function to make it simpler and more readable. It currently has nested if-else statements that are hard to follow. Use early returns and keep the same behavior:

[paste your complex function here]
```

#### Prompt 2 — Modernize Code

```
This code was written for Python 2. Update it to modern Python 3 (3.10+) best practices. Use walrus operator, type hints, f-strings, and dataclasses where appropriate:

[paste your legacy code here]
```

#### Prompt 3 — Design Pattern Application

```
Refactor this class to use the Strategy pattern. Currently, the class has a large switch statement to handle different payment methods. I want each payment method to be its own class:

[paste your code here]
```

#### Prompt 4 — Reduce Duplication

```
I have three functions that share a lot of duplicated logic for API error handling. Refactor them to extract the common logic into a shared utility function or decorator:

function1: [paste code]
function2: [paste code]
function3: [paste code]
```

### 5.6 Unit Test Generation

Writing tests is one of the best use cases for AI. You paste your code, and the AI generates comprehensive test cases — including edge cases you might not have thought of.

#### Prompt 1 — Generate Tests for a Function

```
Write comprehensive unit tests for this function using Jest. Include tests for:
- Normal cases
- Edge cases (empty input, null, undefined)
- Boundary cases
- Error cases

function calculateDiscount(price, discountPercent) {
  if (price < 0 || discountPercent < 0 || discountPercent > 100) {
    throw new Error('Invalid input values');
  }
  return price - (price * discountPercent / 100);
}
```

#### Prompt 2 — Generate Tests for a React Component

```
Write React Testing Library tests for this component. Test:
- Renders correctly with required props
- Shows validation errors on invalid input
- Calls onSubmit with correct data when form is submitted
- Calls onSubmit with formatted phone number

[paste your component code here]
```

#### Prompt 3 — Generate Tests for an API Endpoint

```
Write integration tests using supertest for this Express route. Test:
- Success case (200)
- Missing required fields (400)
- Invalid data types (400)
- Server error (500)

[paste your route code here]
```

### 5.7 Writing Code Comments and Documentation

Good documentation is essential but tedious to write. AI can help generate comments, docstrings, README sections, and API documentation.

#### Prompt 1 — Add Comments to Existing Code

```
Add clear, useful inline comments to this function. Do not over-comment obvious lines. Focus on explaining the "why" behind complex logic:

[paste your uncommented code here]
```

#### Prompt 2 — Generate Docstrings

```
Add Google-style docstrings to all public functions and classes in this Python module. Include parameter types, return types, and examples:

[paste your code here]
```

#### Prompt 3 — Write a README Section

```
Write a "Getting Started" section for the README of this project. Assume the reader is a developer setting up the project for the first time. Include:
- Prerequisites
- Installation steps
- Environment variables needed
- How to run the project
- How to run tests

[paste your package.json or requirements.txt or relevant config]
```

### 5.8 Code Translation and Conversion

Need to convert code from one language to another? This is something AI does remarkably well.

#### Prompt 1 — Language Translation

```
Convert this Python code to TypeScript. Keep the same logic and variable names. Add proper TypeScript types:

def paginate(items, page=1, per_page=10):
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "total": len(items),
        "page": page,
        "per_page": per_page,
        "total_pages": math.ceil(len(items) / per_page)
    }
```

#### Prompt 2 — Framework Migration

```
Convert this class component to a functional component using React hooks. Maintain all the same functionality:

[paste your class component here]
```

#### Prompt 3 — Convert Callbacks to Async/Await

```
Refactor this Node.js code from callback-based to async/await. Handle errors properly with try-catch:

[paste your callback-based code here]
```

### 5.9 Writing SQL and Database Queries

SQL queries can be complex, especially with joins, aggregations, and window functions. AI is great at writing and optimizing SQL.

#### Prompt 1 — Write a Query

```
Write a SQL query for a PostgreSQL database that finds the top 10 customers who spent the most in the last 30 days. The tables are:
- customers: id, name, email, created_at
- orders: id, customer_id, total_amount, status, created_at
- order_items: id, order_id, product_id, quantity, unit_price

Only include completed orders (status = 'completed'). Return customer name, email, total spent, and number of orders.
```

#### Prompt 2 — Optimize a Slow Query

```
This SQL query is running very slow (8+ seconds) on a table with 5 million rows. How can I optimize it?

SELECT u.name, u.email, COUNT(o.id) as order_count, SUM(o.total_amount) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed'
  AND o.created_at > '2024-01-01'
GROUP BY u.id, u.name, u.email
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC;
```

#### Prompt 3 — Explain a Complex Query

```
Explain this SQL query in plain English. What does each CTE do? What is the final result?

[paste your complex SQL query here]
```

### 5.10 Regular Expressions

Regular expressions are notoriously hard to write and read. AI can generate them, explain them, and fix them.

#### Prompt 1 — Generate a Regex

```
Write a regular expression that matches:
- Indian mobile numbers in formats: +91 9876543210, +91-9876543210, 9876543210, 09876543210
- Should NOT match numbers with more or fewer than 10 digits (excluding country code)
Provide the regex and a brief explanation of each part.
```

#### Prompt 2 — Explain a Regex

```
Explain this regular expression piece by piece. What does each part match?

^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$
```

#### Prompt 3 — Fix a Regex

```
This regex is supposed to match email addresses but it incorrectly matches strings like "user@.com" and "user@domain.". Fix it:

^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$
```

### 5.11 Working with APIs

AI can help you work with APIs — from writing integration code to debugging API issues.

#### Prompt 1 — API Integration Code

```
Write a function that calls the GitHub REST API to get the list of repositories for a given user. Use the fetch API. Include:
- Proper error handling for network errors and API rate limiting
- Pagination support (GitHub returns max 30 repos per page)
- TypeScript types for the response

GitHub API docs: GET /users/{username}/repos
```

#### Prompt 2 — Parse API Response

```
I am getting this JSON response from an API and I need to extract and transform the data into a flat list. The nested structure is:

{
  "departments": [
    {
      "name": "Engineering",
      "employees": [
        { "name": "Alice", "role": "Developer", "salary": 90000 },
        { "name": "Bob", "role": "Senior Developer", "salary": 120000 }
      ]
    }
  ]
}

Write a JavaScript function that converts this into:
[
  { department: "Engineering", employee: "Alice", role: "Developer", salary: 90000 },
  { department: "Engineering", employee: "Bob", role: "Senior Developer", salary: 120000 }
]
```

### 5.12 Debugging Help

When you are stuck on a bug and cannot figure out why something is not working, AI can be a great debugging partner.

#### Prompt 1 — Why Is This Not Working?

```
My React component is not re-rendering when the prop changes. Here is the component and the parent component. What could be wrong?

Parent:
[paste parent component]

Child:
[paste child component]
```

#### Prompt 2 — Intermittent Bug

```
I have an intermittent bug in my application. About 1 in 10 times, the user's session gets cleared after a page refresh. I am using localStorage to store the session token. Here is my auth code:

[paste your auth code]

What could cause this to happen intermittently?
```

#### Prompt 3 — Environment-Specific Bug

```
This code works perfectly in my local development environment but fails in production with a CORS error. What could be different between the environments?

Local: http://localhost:3000 (frontend), http://localhost:8080 (backend)
Production: https://app.mycompany.com (frontend), https://api.mycompany.com (backend)

[paste your CORS configuration or fetch call]
```

---

## 6. Prompt Templates for Daily Use

Here are copy-paste-ready templates you can customize for your daily work. Replace the `[bracketed]` parts with your specific details.

### Template 1 — Generate Code

```
Write a [language] [function/class/component] that [describe what it does].
Requirements:
- [requirement 1]
- [requirement 2]
- [requirement 3]
Use [framework/library/version]. Include [error handling/logging/tests/comments].
```

### Template 2 — Review Code

```
Review this [language] code for [bugs/security/performance/readability]. 
For each issue found:
1. Describe the problem
2. Explain why it is a problem
3. Provide the fixed code

Code:
[paste code]
```

### Template 3 — Fix a Bug

```
I am getting this error: [paste error message]
Here is my code: [paste code]
What is causing this error? Explain the root cause and provide a fix.
Also, suggest how to prevent this type of error in the future.
```

### Template 4 — Write Tests

```
Write [test framework] tests for this [language] [function/component/module].
Test framework: [Jest/PyTest/JUnit/etc.]
Coverage goals:
- Happy path scenarios
- Edge cases: [list specific edge cases]
- Error scenarios: [list specific error cases]
- Boundary values

Code to test:
[paste code]
```

### Template 5 — Refactor Code

```
Refactor this [language] code to improve [readability/performance/maintainability].
Keep the same behavior. Focus on:
- [specific improvement 1]
- [specific improvement 2]

Current code:
[paste code]
```

### Template 6 — Explain Code

```
Explain this [language] code [in plain English / to a beginner / at a high level].
I want to understand:
- What it does
- How it works
- Why certain decisions were made (if you can infer)

Code:
[paste code]
```

### Template 7 — Generate Documentation

```
Generate [JSDoc / docstring / Swagger / README] documentation for this code.
Format: [Google style / JSDoc / OpenAPI 3.0]
Include: [parameters, return values, examples, error conditions]

Code:
[paste code]
```

### Template 8 — Convert Code

```
Convert this [source language/framework] code to [target language/framework].
Keep the same logic and behavior. Use [target-specific best practices].

Source code:
[paste code]
```

---

## 7. Demo Steps

The following is a suggested step-by-step demo plan for the live KT session. Each step includes what to show, what prompt to use, and what talking points to cover.

### Demo 1 — Token Counting (3 minutes)

**What to show:** Use [tokenizer.openai.com](https://tokenizer.openai.com) to demonstrate tokenization.

**Steps:**
1. Open the tokenizer in the browser
2. Type "Hello, how are you?" — show it is ~6 tokens
3. Type a 50-line Python function — show the token count
4. Type the same function with shorter variable names — show the token count is lower
5. Explain: "This is why concise prompts save money and stay within limits"

**Talking points:**
- Tokens are the currency of AI models
- Code uses tokens faster than plain English
- Shorter prompts within the same context window leave more room for the response

### Demo 2 — Bad Prompt vs Good Prompt (5 minutes)

**What to show:** Same task, two different prompts, dramatically different results.

**Bad prompt:**
```
fix my code
```
(Paste a complex function with a subtle bug — no context, no language specified)

**Good prompt:**
```
This Python function is supposed to find the median of a sorted list, but it returns
the wrong result for even-length lists. The expected median for [1, 2, 3, 4] is 2.5
but it returns 2. Find the bug and fix it. Keep the O(1) time complexity.

def find_median(sorted_list):
    mid = len(sorted_list) // 2
    return sorted_list[mid]
```

**Talking points:**
- Context matters: language, expected behavior, actual behavior
- Constraints guide the AI toward better solutions
- Specificity eliminates ambiguity

### Demo 3 — Code Generation (5 minutes)

**What to show:** Generate a complete, production-ready function from a well-structured prompt.

**Prompt to use:**
```
Write a TypeScript utility function called 'retry' that wraps an async function and
retries it on failure. Requirements:
- Accept the async function, max retries (default 3), and delay between retries in ms (default 1000)
- Use exponential backoff: delay doubles after each retry
- Throw the last error if all retries fail
- Include JSDoc documentation with @example
```

**Talking points:**
- The prompt specifies language, function name, behavior, defaults, and documentation requirements
- Walk through the generated code and highlight how it matches the requirements
- Show how you could iterate: "Now add jitter to prevent thundering herd"

### Demo 4 — Code Review with AI (5 minutes)

**What to show:** Paste a piece of real (but sanitized) code and get a review.

**Prompt to use:**
```
Review this code for bugs, security issues, and best practices violations:

app.post('/api/upload', (req, res) => {
  const filename = req.body.filename;
  const data = req.body.data;
  fs.writeFileSync(`/uploads/${filename}`, data);
  res.json({ message: 'File uploaded successfully' });
});
```

**Talking points:**
- AI immediately spots the path traversal vulnerability (no sanitization of filename)
- AI catches the missing error handling
- AI identifies that writeFileSync blocks the event loop
- This is a quick way to get a first-pass review before formal code review

### Demo 5 — Unit Test Generation (5 minutes)

**What to show:** Generate comprehensive tests from existing code.

**Prompt to use:** Use the `calculateDiscount` function example from section 5.6.

**Talking points:**
- AI generates more test cases than most developers would write manually
- Includes edge cases you might forget (negative numbers, boundary values)
- Tests are a starting point — review and adapt them, do not blindly trust

### Demo 6 — Iterative Refinement (3 minutes)

**What to show:** Start with a basic prompt, then refine the output through conversation.

**Round 1:** "Write a function to validate an email address."
**Round 2:** "Now make it support international email addresses with Unicode characters."
**Round 3:** "Now add a function to validate a list of emails and return which ones are invalid."

**Talking points:**
- Iterative prompting produces better results than trying to cram everything into one prompt
- Each round builds on the previous context
- This mirrors how you would work with a human developer

---

## 8. Best Practices

### 8.1 Crafting Effective Prompts

**Be specific about language and framework.** Instead of "write a function to sort data," say "write a Python function using pandas to sort a DataFrame by the 'date' column in descending order." The more specific you are, the less the AI has to guess.

**Provide context, not just instructions.** Instead of "fix this error," share the error message, the relevant code, what you expected to happen, and what actually happened. Think of it like reporting a bug to a colleague — the more context they have, the faster they can help.

**Break complex tasks into smaller steps.** Do not ask the AI to "build a complete e-commerce application" in one prompt. Instead, ask it to help with one piece at a time: the data model, then the API endpoints, then the frontend components. Iterative prompting consistently produces better results.

**Use examples when the format matters.** If you need the output in a specific format — a particular JSON structure, a specific test framework style, a particular naming convention — show an example of what you want. Few-shot prompting is extremely effective for this.

**Specify what you do NOT want.** Sometimes it is as important to tell the AI what to avoid as what to include. "Do not use any external libraries," "Do not include comments," "Do not change the function signature" — these constraints prevent unwanted deviations.

### 8.2 Reviewing and Validating AI Output

**Never trust AI-generated code blindly.** Always review the code before using it. Check for:
- Logic correctness — does it actually do what you asked?
- Security issues — any vulnerabilities like SQL injection, XSS, hardcoded secrets?
- Dependencies — does it use libraries or functions that exist in your project?
- Code style — does it match your team's conventions?

**Test AI-generated code thoroughly.** Run the code. Run tests. Try edge cases. AI code can look perfectly correct and still have subtle bugs, especially around edge cases and error handling.

**Verify API references.** AI models sometimes invent function names, parameters, or library methods that do not exist. If the AI references a specific library function, take 30 seconds to verify it in the official documentation.

**Use AI as a starting point, not an ending point.** Think of AI-generated code as a first draft. It gets you 80% of the way there. The remaining 20% — adapting it to your codebase, handling your specific edge cases, matching your conventions — is your job as a developer.

### 8.3 Cost and Productivity Optimization

**Choose the right model for the task.** Do not use GPT-4o to generate a simple regex or format a JSON string. Use a lighter, faster, cheaper model for simple tasks. Save the powerful (expensive) models for complex tasks that require deep reasoning.

**Reuse prompts and templates.** If you find a prompt pattern that works well, save it. Create a shared prompt library for your team. Consistency in prompting leads to consistency in output quality.

**Keep conversations focused.** Long conversations accumulate tokens and can confuse the model. Start a new conversation when you switch to a new task. This keeps the context window clean and reduces costs.

**Set up usage monitoring.** If your team is using AI APIs directly, set up monitoring and budget alerts. Track which prompts are being used most frequently, which models are being called, and how many tokens are being consumed.

### 8.4 Security and Privacy Considerations

**Never share sensitive data with public AI tools.** This includes:
- Production API keys, secrets, or credentials
- Customer personal data (PII)
- Proprietary source code or trade secrets
- Internal system architecture details
- Database schemas with real data

**Use enterprise or self-hosted solutions for sensitive work.** If your company has an enterprise AI tool with data privacy guarantees, use that instead of public ChatGPT. Alternatively, run local models like Llama or CodeLlama for code that cannot leave your machine.

**Sanitize code before sharing.** Before pasting code into a public AI tool, remove or replace:
- API keys and tokens
- Connection strings
- Internal URLs and IP addresses
- Employee or customer names
- Company-specific business logic details

---

## 9. Do's and Don'ts — Quick Reference

| Do | Don't |
|----|-------|
| Be specific about language, framework, and version | Say "write code" without any context |
| Provide relevant code and error messages | Expect the AI to guess your problem |
| Break complex tasks into smaller steps | Ask for an entire application in one prompt |
| Review and test all AI-generated code | Copy-paste AI output directly to production |
| Iterate and refine your prompts | Accept the first output as final |
| Verify library and API references | Assume AI-generated function names are real |
| Use examples to show desired format | Describe the format in abstract terms |
| Set constraints ("do not use external libraries") | Leave requirements open-ended |
| Choose the right model for the task | Use the most expensive model for simple tasks |
| Sanitize code before sharing with AI | Paste production secrets and credentials |
| Use AI for learning and understanding | Use AI as a replacement for understanding |

---

## 10. Resources

### Official Documentation and Tools

- [OpenAI API Documentation](https://platform.openai.com/docs) — Official docs for GPT models and API
- [Anthropic Claude Documentation](https://docs.anthropic.com) — Official docs for Claude models
- [Google Gemini Documentation](https://ai.google.dev/docs) — Official docs for Gemini models
- [OpenAI Tokenizer](https://tokenizer.openai.com) — Visual tool to count tokens
- [tiktoken (Python library)](https://github.com/openai/tiktoken) — Programmatic token counting

### Prompt Engineering Resources

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) — Official best practices from OpenAI
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering) — Official best practices from Anthropic
- [Learn Prompting](https://learnprompting.org) — Free, comprehensive prompt engineering course
- [PromptingGuide.ai](https://www.promptingguide.ai) — Academic-style guide to prompting techniques

### AI Coding Tools

- [GitHub Copilot](https://github.com/features/copilot) — AI-powered IDE assistant
- [Cursor](https://cursor.sh) — AI-first code editor
- [Codeium](https://codeium.com) — Free AI coding assistant
- [Continue](https://continue.dev) — Open-source AI code assistant for VS Code and JetBrains
- [Aider](https://aider.chat) — AI pair programming in your terminal

### Local / Privacy-Focused Models

- [Ollama](https://ollama.ai) — Run LLMs locally on your machine
- [LM Studio](https://lmstudio.ai) — Download and run local LLMs with a GUI
- [GPT4All](https://gpt4all.io) — Open-source local LLMs for consumer hardware

### Recommended Reading

- "Prompt Engineering for Developers" by DeepLearning.AI (Free short course)
- "Building Applications with Large Language Models" (DeepLearning.AI course series)
- "A Programmer's Introduction to AI" — Understanding AI concepts for software developers

---

> **Note:** This is a living document. As AI models and best practices evolve, please update this page with new findings, prompt patterns, and tools that work well for our team. If you discover a useful prompt pattern, add it to the Prompt Templates section above.
