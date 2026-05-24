# AI Frameworks & LangChain: A Complete Guide from Basics to Mastery

> A comprehensive guide for beginners to understand AI frameworks, Agentic AI, and master the LangChain framework with examples, diagrams, and interview preparation.

---

## Table of Contents

1. [Part 1: Introduction to AI Frameworks](#part-1-introduction-to-ai-frameworks)
2. [Part 2: Different AI Frameworks Available](#part-2-different-ai-frameworks-available)
3. [Part 3: Agentic AI Explained](#part-3-agentic-ai-explained)
4. [Part 4: LangChain Framework from Scratch](#part-4-langchain-framework-from-scratch)
   - [4.1 What is LangChain?](#41-what-is-langchain)
   - [4.2 Core Architecture](#42-core-architecture)
   - [4.3 Installation & Setup](#43-installation--setup)
   - [4.4 Models](#44-models)
   - [4.5 Prompts & Templates](#45-prompts--templates)
   - [4.6 Output Parsers](#46-output-parsers)
   - [4.7 Chains](#47-chains)
   - [4.8 Memory](#48-memory)
   - [4.9 Tools](#49-tools)
   - [4.10 Agents](#410-agents)
   - [4.11 Retrieval Augmented Generation (RAG)](#411-retrieval-augmented-generation-rag)
   - [4.12 Callbacks](#412-callbacks)
   - [4.13 LangChain Expression Language (LCEL)](#413-langchain-expression-language-lcel)
5. [Part 5: Interview Tips & Common Questions](#part-5-interview-tips--common-questions)

---

# Part 1: Introduction to AI Frameworks

## 1.1 What is an AI Framework?

An **AI framework** is a software library or platform that provides pre-built tools, abstractions, and infrastructure to simplify the development of AI-powered applications. Just as web frameworks like Django or Express.js simplify web development by handling routing, templating, and database connections, AI frameworks simplify the process of building applications that leverage large language models (LLMs) and other AI capabilities.

Without an AI framework, developers would need to write boilerplate code for every interaction with an LLM — managing API calls, formatting prompts, parsing responses, maintaining conversation history, connecting external data sources, and orchestrating multi-step reasoning. AI frameworks handle all of these concerns and more, allowing developers to focus on the business logic and user experience of their applications.

### Why Do We Need AI Frameworks?

Building production-ready AI applications involves numerous challenges that go far beyond simply calling an API. Consider a conversational chatbot: it must remember previous messages, maintain a consistent personality, handle errors gracefully, stream responses in real time, validate outputs, and potentially call external tools to fetch live data. Each of these requirements adds complexity. AI frameworks abstract away this complexity by providing well-tested, composable building blocks.

Key reasons to use AI frameworks include:

- **Abstraction**: They hide the complexity of API integrations, prompt engineering, and response parsing behind clean, reusable interfaces. You can switch from OpenAI to Anthropic to a local model without rewriting your application logic.
- **Composability**: They allow you to chain together multiple AI operations (e.g., retrieve documents, then summarize them, then format the output) in a declarative and maintainable way.
- **Standardization**: They enforce consistent patterns for prompt templates, memory management, and tool usage, making your codebase easier to understand and maintain.
- **Ecosystem**: They provide integrations with hundreds of data sources, tools, and services, so you do not have to build these integrations from scratch.
- **Production Readiness**: They offer features like observability, caching, rate limiting, and error handling that are essential for deploying AI applications at scale.

### AI Framework Architecture Overview

```mermaid
graph TB
    subgraph "Your AI Application"
        A[User Interface]
    end

    subgraph "AI Framework Layer"
        B[Prompt Management]
        C[Model Interface]
        D[Memory & State]
        E[Tool Integration]
        F[Output Parsing]
        G[Orchestration / Chains]
    end

    subgraph "External Services"
        H[OpenAI / GPT]
        I[Anthropic / Claude]
        J[Google / Gemini]
        K[Databases / APIs]
        L[Search Engines]
    end

    A --> G
    G --> B
    G --> C
    G --> D
    G --> E
    G --> F
    C --> H
    C --> I
    C --> J
    E --> K
    E --> L
```

## 1.2 Key Concepts in AI Development

Before diving deeper into specific frameworks, it is essential to understand the foundational concepts that all AI frameworks build upon:

### Large Language Models (LLMs)

Large Language Models are neural networks trained on vast amounts of text data. They can generate human-like text, answer questions, translate languages, write code, and perform many other language tasks. Examples include GPT-4, Claude, Gemini, Llama, and Mistral. LLMs are the core engine that AI frameworks wrap around and enhance.

### Prompts and Prompt Engineering

A **prompt** is the input text you send to an LLM. **Prompt engineering** is the art and science of crafting prompts that produce desired outputs. Effective prompt engineering involves being specific, providing context, giving examples (few-shot prompting), and structuring instructions clearly. AI frameworks provide prompt template systems that make it easy to create, manage, and version prompts.

### Context Window

Every LLM has a **context window** — the maximum number of tokens (roughly, words or word pieces) it can process in a single request. This includes both the input prompt and the generated output. Context windows range from a few thousand tokens in older models to over a million in newer ones. AI frameworks help you manage context windows by trimming, summarizing, or selecting the most relevant information to include.

### Tokens

LLMs process text in units called **tokens**, which are roughly equivalent to 3/4 of an English word. Tokenization affects both the cost of API calls (which are priced per token) and the context window limits. Understanding tokens is critical for optimizing AI application performance and cost.

### Embeddings

**Embeddings** are numerical vector representations of text. They capture the semantic meaning of text in a way that allows mathematical comparison — texts with similar meanings will have similar embedding vectors. Embeddings are the foundation of semantic search, document retrieval, and many RAG (Retrieval Augmented Generation) architectures.

---

# Part 2: Different AI Frameworks Available

The AI framework ecosystem has grown rapidly. Each framework has its own philosophy, strengths, and ideal use cases. Understanding the landscape helps you choose the right tool for your project.

## 2.1 Framework Comparison Overview

```mermaid
graph LR
    subgraph "General Purpose"
        A[LangChain]
        B[LlamaIndex]
    end

    subgraph "Agentic"
        C[CrewAI]
        D[AutoGen]
        E[LangGraph]
    end

    subgraph "Production"
        F[Haystack]
        G[FastChat]
    end

    subgraph "Lightweight"
        H[LiteLLM]
        I[Promptflow]
    end
```

## 2.2 Detailed Framework Comparison

### LangChain

| Aspect | Details |
|--------|---------|
| **Type** | General-purpose AI application framework |
| **Language** | Python, JavaScript/TypeScript |
| **Best For** | Building LLM-powered apps, chains, agents, RAG pipelines |
| **Strengths** | Largest ecosystem, extensive integrations (700+), active community, versatile |
| **Weaknesses** | Can be complex for simple use cases, abstraction layers sometimes obscure control, frequent API changes |
| **Learning Curve** | Moderate to steep |

LangChain is the most popular and comprehensive AI framework. It provides a full toolkit for building any type of LLM application, from simple Q&A bots to complex multi-agent systems. Its modular architecture lets you use only the components you need. The framework excels at composability — you can chain together prompts, models, parsers, memory, and tools into sophisticated workflows.

### LlamaIndex

| Aspect | Details |
|--------|---------|
| **Type** | Data-focused AI framework |
| **Language** | Python, TypeScript |
| **Best For** | RAG applications, document indexing, knowledge management |
| **Strengths** | Superior data ingestion, advanced indexing strategies, excellent for search/retrieval |
| **Weaknesses** | Less flexible for non-RAG use cases, smaller agent ecosystem |
| **Learning Curve** | Moderate |

LlamaIndex (formerly GPT Index) specializes in connecting LLMs to your data. While LangChain is a general-purpose framework, LlamaIndex focuses deeply on data ingestion, indexing, and retrieval. It offers sophisticated indexing strategies (vector, keyword, knowledge graph) and query engines that optimize how documents are retrieved and synthesized.

### CrewAI

| Aspect | Details |
|--------|---------|
| **Type** | Multi-agent orchestration framework |
| **Language** | Python |
| **Best For** | Building teams of AI agents that collaborate on tasks |
| **Strengths** | Role-based agent design, intuitive collaboration patterns, human-like team dynamics |
| **Weaknesses** | Newer framework, smaller community, limited integrations |
| **Learning Curve** | Low to moderate |

CrewAI models AI application development around the metaphor of a team or "crew." Each agent has a defined role, goal, and backstory. Agents can delegate tasks to each other, share information, and work together to accomplish complex objectives. This role-based approach makes it intuitive for building collaborative AI systems.

### AutoGen (by Microsoft)

| Aspect | Details |
|--------|---------|
| **Type** | Multi-agent conversation framework |
| **Language** | Python |
| **Best For** | Multi-agent conversations, code generation, collaborative problem-solving |
| **Strengths** | Strong research backing, flexible conversation patterns, excellent for coding tasks |
| **Weaknesses** | Complex setup, less production-ready, steep learning curve |
| **Learning Curve** | Steep |

AutoGen enables the creation of multi-agent systems where agents communicate through conversations. It supports human-in-the-loop patterns, where a human can participate in or supervise agent conversations. The framework is particularly well-suited for tasks that benefit from multiple perspectives, such as code review, brainstorming, and complex analysis.

### LangGraph

| Aspect | Details |
|--------|---------|
| **Type** | Stateful agent orchestration framework |
| **Language** | Python, JavaScript |
| **Best For** | Complex, stateful agent workflows with cycles and conditional branching |
| **Strengths** | Graph-based state machines, fine-grained control, built-in persistence, human-in-the-loop |
| **Weaknesses** | More complex than basic LangChain, requires understanding of graph concepts |
| **Learning Curve** | Moderate to steep |

LangGraph extends LangChain with a graph-based approach to building agent workflows. While LangChain chains are linear (step A, then step B, then step C), LangGraph allows you to define workflows as directed graphs with cycles, conditional edges, and persistent state. This makes it ideal for agents that need to loop, retry, branch based on conditions, or maintain complex state over time.

### Haystack (by deepset)

| Aspect | Details |
|--------|---------|
| **Type** | Production-ready NLP/Search framework |
| **Language** | Python |
| **Best For** | Production search systems, QA pipelines, enterprise NLP |
| **Strengths** | Production-grade, clean pipeline architecture, strong search capabilities |
| **Weaknesses** | Less flexible for non-search use cases, smaller community than LangChain |
| **Learning Curve** | Moderate |

Haystack focuses on building production-ready search and question-answering systems. Its pipeline architecture is clean and well-documented, making it a strong choice for enterprise deployments where reliability and maintainability are paramount.

### LiteLLM

| Aspect | Details |
|--------|---------|
| **Type** | LLM API gateway/abstraction |
| **Language** | Python |
| **Best For** | Unified API across multiple LLM providers, cost optimization |
| **Strengths** | Simple, lightweight, provider-agnostic, built-in load balancing and fallbacks |
| **Weaknesses** | Not a full framework, limited to model invocation abstraction |
| **Learning Curve** | Low |

LiteLLM provides a single, unified interface to call over 100 LLM providers using the OpenAI API format. It handles the differences between providers (parameter names, response formats, authentication) transparently, and adds features like load balancing, fallbacks, and cost tracking.

## 2.3 Framework Selection Decision Tree

```mermaid
graph TD
    Start[What are you building?] --> Q1{Need RAG with<br>your own data?}
    Q1 -->|Yes, primarily| Llama[LlamaIndex]
    Q1 -->|No| Q2{Multiple agents<br>collaborating?}

    Q2 -->|Yes, role-based| Crew[CrewAI]
    Q2 -->|Yes, conversation-based| Auto[AutoGen]
    Q2 -->|No| Q3{Complex stateful<br>workflows?}

    Q3 -->|Yes| LG[LangGraph]
    Q3 -->|No| Q4{Production search/QA?}

    Q4 -->|Yes| Hay[Haystack]
    Q4 -->|No| Q5{Just need a unified<br>LLM API?}

    Q5 -->|Yes| Lite[LiteLLM]
    Q5 -->|No, general purpose| LC[LangChain]

    style LC fill:#4CAF50,color:#fff
    style Llama fill:#2196F3,color:#fff
    style Crew fill:#FF9800,color:#fff
    style Auto fill:#9C27B0,color:#fff
    style LG fill:#F44336,color:#fff
    style Hay fill:#607D8B,color:#fff
    style Lite fill:#795548,color:#fff
```

## 2.4 Side-by-Side Comparison Table

| Feature | LangChain | LlamaIndex | CrewAI | AutoGen | LangGraph | Haystack |
|---------|-----------|------------|--------|---------|-----------|----------|
| **Primary Focus** | General AI apps | Data/RAG | Multi-agent | Multi-agent | Stateful agents | Search/QA |
| **RAG Support** | Excellent | Best-in-class | Basic | Basic | Good | Excellent |
| **Agent Support** | Good | Basic | Best-in-class | Excellent | Best-in-class | Basic |
| **Integrations** | 700+ | 160+ | 50+ | 30+ | LangChain+ | 50+ |
| **Production Ready** | Yes | Yes | Growing | Research | Yes | Yes |
| **Python** | Yes | Yes | Yes | Yes | Yes | Yes |
| **JavaScript** | Yes | Yes | No | No | Yes | No |
| **Open Source** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Community Size** | Largest | Large | Growing | Large | Growing | Medium |

---

# Part 3: Agentic AI Explained

## 3.1 What is Agentic AI?

**Agentic AI** refers to AI systems that can autonomously plan, reason, decide, and take actions to achieve goals — rather than simply responding to single prompts in a stateless manner. An AI agent goes beyond the traditional "input a prompt, get a response" paradigm. It can break down complex tasks into sub-tasks, choose which tools to use, decide when to ask for help, verify its own work, and adapt its approach based on intermediate results.

The word "agentic" comes from "agent" — an entity that acts on behalf of a user with some degree of autonomy. In the AI context, an agent combines the reasoning capabilities of an LLM with the ability to interact with the external world through tools, APIs, and databases.

### Traditional LLM vs. Agentic AI

```mermaid
graph LR
    subgraph "Traditional LLM"
        A1[User Prompt] --> B1[LLM]
        B1 --> C1[Response]
    end

    subgraph "Agentic AI"
        A2[User Goal] --> B2[Agent]
        B2 --> C2[Plan]
        C2 --> D2[Select Tool]
        D2 --> E2[Execute Action]
        E2 --> F2{Goal Achieved?}
        F2 -->|No| C2
        F2 -->|Yes| G2[Final Result]
    end

    style B2 fill:#FF5722,color:#fff
    style F2 fill:#FFC107,color:#000
```

## 3.2 Key Characteristics of Agentic AI

### Autonomy

Agentic AI systems can operate independently once given a goal. Instead of requiring step-by-step human instructions for every action, the agent determines the best course of action on its own. For example, if you ask an agent to "research the latest AI regulations and write a summary report," it can plan the research steps, perform web searches, read documents, extract key information, and compose the report without human intervention at each step.

### Reasoning and Planning

Agents use the LLM's reasoning capabilities to break down complex goals into executable steps. This involves understanding the goal, identifying what information or actions are needed, creating a plan, and executing that plan in a logical order. Modern agents often use techniques like ReAct (Reason + Act), Chain-of-Thought prompting, and Tree-of-Thought reasoning to improve their planning quality.

### Tool Use

A defining feature of agentic AI is the ability to use tools. Tools are functions or APIs that the agent can call to interact with the outside world. Examples include web search engines, calculators, database query tools, file system operations, API clients, and code interpreters. The agent decides which tool to use, what parameters to pass, and how to interpret the results — all based on the current context and goal.

### Memory and State

Agentic systems maintain state across interactions. They remember what they have done, what information they have gathered, and what remains to be accomplished. This memory can be short-term (within a single task execution) or long-term (persisting across sessions). Memory enables agents to build on previous work, avoid repeating actions, and provide contextually relevant responses.

### Self-Correction and Reflection

Advanced agents can evaluate their own outputs and correct mistakes. If an action does not produce the expected result, the agent can analyze why, adjust its approach, and try again. This reflective capability makes agents more robust and reliable, especially for complex tasks where the optimal approach is not known in advance.

## 3.3 The ReAct Pattern: Reason + Act

The **ReAct** (Reasoning + Acting) pattern is one of the most popular architectures for building AI agents. It alternates between reasoning steps (thinking about what to do) and acting steps (using tools to do it), creating an observable and controllable execution loop.

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent
    participant T as Tools

    U->>A: "What's the weather in Paris and should I carry an umbrella?"

    Note over A: THOUGHT: I need to check current weather in Paris
    A->>T: Call weather_api("Paris")
    T-->>A: {temp: 12°C, rain: 80%, humidity: 85%}

    Note over A: OBSERVATION: Rain probability is 80%
    Note over A: THOUGHT: I should also check hourly forecast
    A->>T: Call forecast_api("Paris", hours=6)
    T-->>A: {rain_expected: true, peak_rain: "2pm-5pm"}

    Note over A: OBSERVATION: Rain expected between 2-5pm
    Note over A: THOUGHT: I have enough information to answer

    A->>U: Yes, carry an umbrella. 80% chance of rain today,<br/>heaviest between 2-5pm. Temperature is 12°C.
```

## 3.4 Types of AI Agents

```mermaid
graph TB
    subgraph "Agent Types"
        A[Simple Agent<br/>Single tool, single step]
        B[ReAct Agent<br/>Reason-Act loop with tools]
        C[Plan-and-Execute Agent<br/>Plan all steps, then execute]
        D[Multi-Agent System<br/>Multiple agents collaborate]
        E[Hierarchical Agent<br/>Manager delegates to workers]
    end

    A --> B --> C
    B --> D
    C --> E

    style D fill:#9C27B0,color:#fff
    style E fill:#FF5722,color:#fff
```

### Simple Agent

A simple agent takes a user input, makes a single LLM call, and returns the result. This is essentially the traditional LLM interaction pattern with a thin agent wrapper. It is useful for straightforward tasks that do not require tools or multi-step reasoning.

### ReAct Agent

The ReAct agent follows the Reason-Act-Observe loop described above. At each step, it reasons about what to do next, selects and executes a tool, observes the result, and then reasons again. This continues until the agent determines it has enough information to provide a final answer. ReAct agents are versatile and work well for tasks that require gathering information from multiple sources.

### Plan-and-Execute Agent

Instead of reasoning one step at a time, the Plan-and-Execute agent first creates a complete plan of all the steps it needs to take, and then executes them in order. This approach is beneficial for complex, multi-step tasks where having a full plan upfront leads to better outcomes than ad-hoc step-by-step reasoning.

### Multi-Agent System

Multi-agent systems involve multiple AI agents working together, each with potentially different roles, capabilities, and perspectives. They can collaborate by sharing information, dividing tasks, reviewing each other's work, and combining their outputs. Frameworks like CrewAI and AutoGen specialize in this pattern.

### Hierarchical Agent

In a hierarchical system, a "manager" or "supervisor" agent delegates tasks to specialized "worker" agents. The manager is responsible for understanding the overall goal, breaking it into sub-tasks, assigning them to appropriate workers, and synthesizing the results. This mirrors how human organizations operate.

## 3.5 Agentic AI Workflow

```mermaid
graph TD
    A[User Goal] --> B[Agent Receives Task]
    B --> C[Reason: Analyze Goal]
    C --> D[Plan: Break into Sub-tasks]
    D --> E[Select: Choose Appropriate Tool]
    E --> F[Act: Execute Tool/Action]
    F --> G[Observe: Process Result]
    G --> H{Goal Complete?}
    H -->|No| I{Need Different Approach?}
    I -->|Yes| J[Reflect: Adjust Strategy]
    J --> C
    I -->|No| C
    H -->|Yes| K[Synthesize Final Answer]
    K --> L[Return Result to User]

    style A fill:#4CAF50,color:#fff
    style H fill:#FFC107,color:#000
    style I fill:#FF9800,color:#fff
    style L fill:#2196F3,color:#fff
```

## 3.6 Real-World Applications of Agentic AI

- **Customer Support Agents**: Handle complex support tickets by searching knowledge bases, checking order status, processing refunds, and escalating to human agents when needed.
- **Research Assistants**: Perform literature reviews, search academic databases, summarize findings, and draft research reports.
- **Software Development Agents**: Write code, run tests, debug errors, review pull requests, and deploy applications.
- **Data Analysis Agents**: Connect to databases, write SQL queries, generate visualizations, and produce analytical reports.
- **Personal Assistants**: Manage calendars, send emails, book appointments, and organize information across multiple services.

---

# Part 4: LangChain Framework from Scratch

## 4.1 What is LangChain?

**LangChain** is an open-source framework that simplifies the development of applications powered by large language models. Created by Harrison Chase and launched in late 2022, it has rapidly become the most popular framework in the AI application ecosystem, with over 80,000 GitHub stars and a thriving community.

LangChain provides a standardized, composable set of abstractions for every component of an LLM application: prompts, models, output parsers, memory, tools, agents, and retrieval systems. These components can be used independently or composed together into powerful workflows.

### LangChain's Core Philosophy

1. **Be Data-Aware**: Connect LLMs to your own data sources (documents, databases, APIs)
2. **Be Agentic**: Enable LLMs to interact with their environment through tools and actions
3. **Be Composable**: Build complex applications from simple, reusable components

### LangChain Ecosystem

```mermaid
graph TB
    subgraph "LangChain Ecosystem"
        A[LangChain<br/>Core Framework]
        B[LangGraph<br/>Agent Orchestration]
        C[LangSmith<br/>Observability & Debugging]
        D[LangServe<br/>Deployment API]
    end

    A --> B
    A --> C
    A --> D

    subgraph "What Each Provides"
        E[Models, Prompts,<br/>Chains, Memory,<br/>Tools, Retrieval]
        F[Cyclic Graphs,<br/>State Machines,<br/>Human-in-the-Loop]
        G[Tracing, Evaluation,<br/>Testing, Monitoring]
        H[REST API,<br/>Playground,<br/>Production Deploy]
    end

    A -.-> E
    B -.-> F
    C -.-> G
    D -.-> H

    style A fill:#1E88E5,color:#fff
    style B fill:#43A047,color:#fff
    style C fill:#FB8C00,color:#fff
    style D fill:#E53935,color:#fff
```

## 4.2 Core Architecture

LangChain's architecture is built around six foundational pillars. Each pillar addresses a specific challenge in LLM application development:

```mermaid
graph TB
    subgraph "LangChain's Six Pillars"
        A[Models<br/>LLM & Chat Model<br/>Interfaces]
        B[Prompts<br/>Templates &<br/>Management]
        C[Chains<br/>Composable<br/>Workflows]
        D[Memory<br/>State &<br/>Conversation History]
        E[Tools<br/>External<br/>Capabilities]
        F[Agents<br/>Autonomous<br/>Decision Making]
    end

    A --> C
    B --> C
    D --> C
    C --> F
    E --> F

    style A fill:#42A5F5,color:#fff
    style B fill:#66BB6A,color:#fff
    style C fill:#FFA726,color:#fff
    style D fill:#AB47BC,color:#fff
    style E fill:#EF5350,color:#fff
    style F fill:#78909C,color:#fff
```

## 4.3 Installation and Setup

### Installing LangChain

```bash
# Install the core LangChain package
pip install langchain

# Install with community integrations
pip install langchain-community

# Install specific provider packages
pip install langchain-openai        # For OpenAI models
pip install langchain-anthropic      # For Anthropic/Claude models
pip install langchain-google-genai   # For Google Gemini models

# Install LangChain with all common dependencies
pip install langchain[all]
```

### Setting Up API Keys

```python
import os

# Set your API keys as environment variables
os.environ["OPENAI_API_KEY"] = "sk-your-openai-api-key-here"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-anthropic-key-here"

# Or use a .env file with python-dotenv
# pip install python-dotenv
from dotenv import load_dotenv
load_dotenv()  # Loads keys from .env file automatically
```

### Your First LangChain Program

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Step 1: Initialize the model
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Step 2: Create messages
messages = [
    SystemMessage(content="You are a helpful AI tutor."),
    HumanMessage(content="Explain what an AI framework is in simple terms.")
]

# Step 3: Get a response
response = llm.invoke(messages)
print(response.content)
```

## 4.4 Models

Models are the foundation of every LangChain application. LangChain provides a unified interface to interact with different types of language models, regardless of the provider.

### Types of Models

```mermaid
graph TB
    subgraph "LangChain Model Types"
        A[BaseLanguageModel]
        B[LLM<br/>Text In → Text Out]
        C[ChatModel<br/>Messages In → Message Out]
        D[Embeddings<br/>Text In → Vector Out]
    end

    A --> B
    A --> C
    A --> D

    subgraph "Providers"
        E[OpenAI]
        F[Anthropic]
        G[Google]
        H[HuggingFace]
        I[Ollama - Local]
    end

    B --> E
    B --> F
    C --> E
    C --> G
    D --> E
    D --> H
    C --> I

    style B fill:#42A5F5,color:#fff
    style C fill:#66BB6A,color:#fff
    style D fill:#FFA726,color:#fff
```

### LLMs (Text-in, Text-out)

The simplest model interface. You provide a text string, and it returns a text string. This is the legacy interface and is suitable for simple completion tasks.

```python
from langchain_openai import OpenAI

# Initialize a text completion model
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.7)

# Simple text completion
result = llm.invoke("What are the three laws of robotics?")
print(result)

# Batch processing
results = llm.batch([
    "What is Python?",
    "What is JavaScript?",
    "What is Rust?"
])
for r in results:
    print(r)
    print("---")
```

### Chat Models (Messages-in, Message-out)

The modern interface that works with structured message objects. This is the recommended way to interact with LLMs because it supports conversation history, system prompts, and different message roles.

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Initialize a chat model
chat = ChatOpenAI(model="gpt-4", temperature=0.7)

# Create a conversation with different message types
messages = [
    SystemMessage(content="You are a sarcastic but helpful coding assistant."),
    HumanMessage(content="How do I center a div?"),
    AIMessage(content="Oh, the age-old question. Use flexbox, obviously."),
    HumanMessage(content="But I'm using CSS Grid for the layout...")
]

response = chat.invoke(messages)
print(response.content)
# Output will acknowledge the Grid context and suggest Grid-based centering
```

### Key Model Parameters

| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| `temperature` | Controls randomness. 0 = deterministic, 1 = very creative | 0.0 - 1.0 |
| `max_tokens` | Maximum number of tokens in the response | 100 - 4096 |
| `top_p` | Nucleus sampling — controls diversity of token selection | 0.1 - 1.0 |
| `frequency_penalty` | Penalizes tokens that appear frequently | -2.0 - 2.0 |
| `presence_penalty` | Penalizes tokens that have appeared at all | -2.0 - 2.0 |
| `model` | The specific model to use | "gpt-4", "claude-3-opus", etc. |

### Streaming Responses

For a better user experience, you can stream responses token by token:

```python
from langchain_openai import ChatOpenAI

chat = ChatOpenAI(model="gpt-4", streaming=True)

# Stream tokens as they are generated
for chunk in chat.stream("Tell me a story about a brave AI agent."):
    print(chunk.content, end="", flush=True)
print()  # Newline after streaming completes
```

### Embeddings

Embeddings convert text into numerical vectors for semantic search, clustering, and similarity comparison:

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Embed a single text
vector = embeddings.embed_query("What is machine learning?")
print(f"Vector dimension: {len(vector)}")  # e.g., 1536
print(f"First 5 values: {vector[:5]}")

# Embed multiple documents
doc_vectors = embeddings.embed_documents([
    "Machine learning is a subset of AI.",
    "Deep learning uses neural networks.",
    "Natural language processing handles text data."
])
print(f"Number of document vectors: {len(doc_vectors)}")
```

---

## 4.5 Prompts and Templates

Prompt templates are one of LangChain's most powerful features. They allow you to create reusable, parameterized prompts that can be shared, versioned, and composed.

### Why Use Prompt Templates?

- **Reusability**: Write a prompt once, use it with different inputs
- **Consistency**: Ensure all users of your application get the same prompt structure
- **Maintainability**: Change the prompt in one place rather than hunting through code
- **Validation**: Automatically validate that all required variables are provided

### PromptTemplate (for LLMs)

```python
from langchain_core.prompts import PromptTemplate

# Create a simple prompt template
template = PromptTemplate.from_template(
    "Write a {length} explanation of {topic} for a {audience} audience."
)

# Format the template with variables
formatted = template.format(
    length="brief",
    topic="neural networks",
    audience="beginner"
)
print(formatted)
# Output: Write a brief explanation of neural networks for a beginner audience.

# Use with an LLM
from langchain_openai import OpenAI
llm = OpenAI(temperature=0.7)
result = llm.invoke(template.format(length="detailed", topic="transformers", audience="technical"))
print(result)
```

### ChatPromptTemplate (for Chat Models)

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Create a chat prompt template with multiple message types
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} assistant specializing in {domain}."),
    ("human", "{question}"),
])

# Format and use it
formatted = prompt.format(
    role="senior",
    domain="Python programming",
    question="How do decorators work?"
)
print(formatted)

# With a chat model
from langchain_openai import ChatOpenAI
chat = ChatOpenAI(model="gpt-4", temperature=0.7)
chain = prompt | chat  # LCEL pipe syntax (covered later)
result = chain.invoke({
    "role": "expert",
    "domain": "machine learning",
    "question": "Explain backpropagation step by step."
})
print(result.content)
```

### MessagesPlaceholder (Dynamic Conversation History)

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Create a template that accepts dynamic conversation history
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful math tutor."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

# Use with conversation history
from langchain_core.messages import HumanMessage, AIMessage

chat_history = [
    HumanMessage(content="What is 2 + 2?"),
    AIMessage(content="2 + 2 equals 4."),
]

formatted = prompt.format(
    chat_history=chat_history,
    question="What about 2 + 3?"
)
```

### Few-Shot Prompt Templates

Few-shot prompting provides examples to guide the model's behavior:

```python
from langchain_core.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate

# Define examples
examples = [
    {"input": "happy", "output": "sad"},
    {"input": "tall", "output": "short"},
    {"input": "fast", "output": "slow"},
]

# Create the few-shot prompt
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

# Combine with the main prompt
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "You provide antonyms for words."),
    few_shot_prompt,
    ("human", "{input}"),
])

# Use it
from langchain_openai import ChatOpenAI
chat = ChatOpenAI(model="gpt-4", temperature=0.0)
chain = final_prompt | chat
result = chain.invoke({"input": "bright"})
print(result.content)  # Likely: "dark" or "dim"
```

### Prompt Template Flow

```mermaid
graph LR
    A[Raw Template<br/>with {variables}] --> B[PromptTemplate]
    C[Variable Values] --> B
    B --> D[Formatted Prompt<br/>Ready for LLM]
    D --> E[LLM / Chat Model]
    E --> F[Response]

    style B fill:#66BB6A,color:#fff
    style D fill:#42A5F5,color:#fff
```

---

## 4.6 Output Parsers

Output parsers transform the raw string output from an LLM into structured, usable data. They bridge the gap between free-form LLM text and the structured formats your application needs.

### Why Output Parsers Matter

LLMs return plain text, but your application often needs structured data — a JSON object, a list of items, a specific schema, or a Pydantic model. Output parsers handle the conversion, including format instructions, parsing, and error recovery.

### Output Parser Architecture

```mermaid
graph LR
    A[LLM Raw Output<br/>String] --> B[Output Parser]
    B --> C{Parse Successful?}
    C -->|Yes| D[Structured Data<br/>JSON/Pydantic/List]
    C -->|No| E[Retry with<br/>Error Feedback]
    E --> A

    style B fill:#AB47BC,color:#fff
    style D fill:#66BB6A,color:#fff
    style E fill:#EF5350,color:#fff
```

### StrOutputParser (Simplest)

Just returns the string content of the message:

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

chat = ChatOpenAI(model="gpt-4", temperature=0.7)
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")

# Chain with string output parser
chain = prompt | chat | StrOutputParser()

result = chain.invoke({"topic": "programmers"})
print(result)  # Plain string, no message wrapper
```

### CommaSeparatedListOutputParser

Parses comma-separated lists:

```python
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

parser = CommaSeparatedListOutputParser()

prompt = ChatPromptTemplate.from_template(
    "List five {category} programming languages.\n{format_instructions}"
)

chain = prompt | ChatOpenAI(temperature=0.0) | parser

result = chain.invoke({
    "category": "object-oriented",
    "format_instructions": parser.get_format_instructions()
})
print(result)
# Output: ['Java', 'Python', 'C++', 'C#', 'Ruby']
print(type(result))  # <class 'list'>
```

### PydanticOutputParser (Most Powerful)

Parses LLM output into Pydantic models with full validation:

```python
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List

# Step 1: Define your data model
class BookReview(BaseModel):
    title: str = Field(description="The title of the book")
    author: str = Field(description="The author of the book")
    rating: float = Field(description="Rating out of 10")
    summary: str = Field(description="A brief summary of the book")
    key_themes: List[str] = Field(description="List of key themes in the book")

# Step 2: Create the parser
parser = PydanticOutputParser(pydantic_object=BookReview)

# Step 3: Create the prompt with format instructions
prompt = ChatPromptTemplate.from_template(
    """Provide a detailed review of the book: {book_name}

    {format_instructions}
    """
)

# Step 4: Build and run the chain
chain = prompt | ChatOpenAI(model="gpt-4", temperature=0.0) | parser

result = chain.invoke({
    "book_name": "The Pragmatic Programmer",
    "format_instructions": parser.get_format_instructions()
})

print(f"Title: {result.title}")
print(f"Author: {result.author}")
print(f"Rating: {result.rating}/10")
print(f"Summary: {result.summary}")
print(f"Key Themes: {', '.join(result.key_themes)}")
# Output is a fully validated BookReview Pydantic object
```

### JsonOutputParser

Similar to PydanticOutputParser but returns plain dictionaries:

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_template(
    """Extract the following information from this text:
    - name: person's name
    - age: person's age
    - occupation: person's job

    Text: {text}

    {format_instructions}
    """
)

chain = prompt | ChatOpenAI(temperature=0.0) | parser

result = chain.invoke({
    "text": "John Smith is a 35-year-old software engineer working at Google.",
    "format_instructions": parser.get_format_instructions()
})

print(result)
# Output: {'name': 'John Smith', 'age': 35, 'occupation': 'software engineer'}
```

---

## 4.7 Chains

Chains are the core orchestration mechanism in LangChain. They allow you to compose multiple components — prompts, models, parsers, and other chains — into a single, cohesive workflow.

### What is a Chain?

A chain is a sequence of operations where the output of one step becomes the input of the next. Think of it as a pipeline or assembly line: raw materials (user input) enter one end, pass through various processing steps, and emerge as a finished product (structured output) at the other end.

### Chain Execution Flow

```mermaid
graph LR
    A[User Input] --> B[Prompt Template]
    B --> C[LLM / Chat Model]
    C --> D[Output Parser]
    D --> E[Structured Result]

    style A fill:#4CAF50,color:#fff
    style B fill:#66BB6A,color:#fff
    style C fill:#42A5F5,color:#fff
    style D fill:#AB47BC,color:#fff
    style E fill:#FF9800,color:#fff
```

### LangChain Expression Language (LCEL) — The Pipe Operator

LCEL is LangChain's declarative way to compose chains using the pipe (`|`) operator. It is the recommended approach for building chains in modern LangChain.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Define components
prompt = ChatPromptTemplate.from_template("Explain {concept} in {style} terms.")
model = ChatOpenAI(model="gpt-4", temperature=0.7)
parser = StrOutputParser()

# Compose them with the pipe operator
chain = prompt | model | parser

# Run the chain
result = chain.invoke({"concept": "recursion", "style": "ELI5"})
print(result)
```

The pipe operator creates a `RunnableSequence` that chains the components together. Each component must implement the `Runnable` interface, which defines `invoke()`, `batch()`, `stream()`, and `ainvoke()` methods.

### LCEL Execution Methods

| Method | Description | Sync/Async | Use Case |
|--------|-------------|------------|----------|
| `invoke()` | Process a single input | Sync | Single request |
| `batch()` | Process multiple inputs | Sync | Bulk processing |
| `stream()` | Stream output tokens | Sync | Real-time display |
| `ainvoke()` | Process a single input | Async | Non-blocking |
| `abatch()` | Process multiple inputs | Async | Non-blocking bulk |
| `astream()` | Stream output tokens | Async | Non-blocking stream |

```python
# Single invocation
result = chain.invoke({"concept": "APIs", "style": "simple"})

# Batch processing
results = chain.batch([
    {"concept": "APIs", "style": "simple"},
    {"concept": "databases", "style": "technical"},
    {"concept": "cloud computing", "style": "business"},
])

# Streaming
for chunk in chain.stream({"concept": "machine learning", "style": "poetic"}):
    print(chunk, end="", flush=True)
```

### Sequential Chains

When you need the output of one chain to feed into another:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4", temperature=0.7)

# Chain 1: Generate a company name
name_prompt = ChatPromptTemplate.from_template(
    "Suggest a creative name for a {business_type} company."
)
name_chain = name_prompt | model | StrOutputParser()

# Chain 2: Create a tagline for the name
tagline_prompt = ChatPromptTemplate.from_template(
    "Create a catchy tagline for a company called {company_name}."
)
tagline_chain = tagline_prompt | model | StrOutputParser()

# Run sequentially
company_name = name_chain.invoke({"business_type": "AI-powered pet care"})
print(f"Company Name: {company_name}")

tagline = tagline_chain.invoke({"company_name": company_name})
print(f"Tagline: {tagline}")
```

### Sequential Chain Data Flow

```mermaid
graph TD
    A["Input: {business_type: 'AI pet care'}"] --> B[Name Chain]
    B --> C["company_name: 'PawsAI'"]
    C --> D[Tagline Chain]
    D --> E["tagline: 'Smart Care for Happy Tails'"]

    style B fill:#42A5F5,color:#fff
    style D fill:#66BB6A,color:#fff
```

### RunnableParallel (Fan-out)

Run multiple chains concurrently and combine results:

```python
from langchain_core.runnables import RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4", temperature=0.7)

# Define parallel chains
joke_chain = (
    ChatPromptTemplate.from_template("Tell a joke about {topic}")
    | model | StrOutputParser()
)

fact_chain = (
    ChatPromptTemplate.from_template("Tell a fact about {topic}")
    | model | StrOutputParser()
)

quote_chain = (
    ChatPromptTemplate.from_template("Give a quote about {topic}")
    | model | StrOutputParser()
)

# Combine in parallel
parallel_chain = RunnableParallel(
    joke=joke_chain,
    fact=fact_chain,
    quote=quote_chain,
)

# Run — all three chains execute concurrently
result = parallel_chain.invoke({"topic": "artificial intelligence"})
print(f"Joke: {result['joke']}")
print(f"Fact: {result['fact']}")
print(f"Quote: {result['quote']}")
```

### RunnableParallel Flow

```mermaid
graph TD
    A[Input: topic] --> B[Joke Chain]
    A --> C[Fact Chain]
    A --> D[Quote Chain]
    B --> E["{joke: '...'}"]
    C --> F["{fact: '...'}"]
    D --> G["{quote: '...'}"]
    E --> H[Combined Result]
    F --> H
    G --> H

    style B fill:#42A5F5,color:#fff
    style C fill:#66BB6A,color:#fff
    style D fill:#AB47BC,color:#fff
    style H fill:#FF9800,color:#fff
```

### RunnablePassthrough and RunnableLambda

```python
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# RunnablePassthrough: Passes input through unchanged
# RunnableLambda: Applies a custom Python function

def word_count(text: str) -> int:
    return len(text.split())

chain = (
    ChatPromptTemplate.from_template("Write a haiku about {topic}")
    | ChatOpenAI(temperature=0.7)
    | StrOutputParser()
    | RunnableLambda(word_count)  # Count words in the haiku
)

word_count_result = chain.invoke({"topic": "autumn"})
print(f"Word count: {word_count_result}")
```

---

## 4.8 Memory

Memory enables LangChain applications to maintain state across interactions. Without memory, each interaction with an LLM is stateless — the model has no recollection of previous exchanges. Memory solves this by storing and retrieving conversation history.

### Memory Architecture

```mermaid
graph TD
    A[User Input] --> B[Memory: Retrieve History]
    B --> C[Prompt + History + New Input]
    C --> D[LLM]
    D --> E[Response]
    E --> F[Memory: Store Exchange]

    style B fill:#AB47BC,color:#fff
    style F fill:#AB47BC,color:#fff
```

### ConversationBufferMemory

Stores the entire conversation history. Simple but can exceed the model's context window for long conversations.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory

# Store chat histories per session
store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Create the prompt with history placeholder
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

# Build the chain
chain = prompt | ChatOpenAI(model="gpt-4", temperature=0.7)

# Wrap with message history
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

# First message
response1 = chain_with_history.invoke(
    {"question": "My name is Alice and I love Python programming."},
    config={"configurable": {"session_id": "user-123"}},
)
print(response1.content)

# Second message — remembers the name!
response2 = chain_with_history.invoke(
    {"question": "What's my name and what programming language do I love?"},
    config={"configurable": {"session_id": "user-123"}},
)
print(response2.content)
# Output will mention Alice and Python
```

### ConversationBufferWindowMemory (Manual Approach)

Keeps only the last K exchanges to manage context window limits:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory

# Custom windowed history
class WindowedChatHistory:
    def __init__(self, k=5):
        self.history = InMemoryChatMessageHistory()
        self.k = k  # Keep last k exchanges

    def add_message(self, message):
        self.history.add_message(message)
        # Trim to keep only last k exchanges (2 messages per exchange)
        messages = self.history.messages
        if len(messages) > self.k * 2:
            self.history = InMemoryChatMessageHistory(
                messages=messages[-(self.k * 2):]
            )

    @property
    def messages(self):
        return self.history.messages
```

### ConversationSummaryMemory

Instead of storing all messages, it maintains a running summary of the conversation:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Approach: Periodically summarize the conversation
# LangChain provides this via higher-level abstractions

summary_prompt = ChatPromptTemplate.from_template(
    """Progressively summarize the lines of conversation provided,
    adding onto the previous summary and returning a new summary.

    Current summary:
    {summary}

    New lines of conversation:
    {new_lines}

    New summary:"""
)

llm = ChatOpenAI(model="gpt-4", temperature=0.0)
summary_chain = summary_prompt | llm | StrOutputParser()
```

### Memory Types Comparison

```mermaid
graph TB
    subgraph "Memory Types"
        A[Buffer Memory<br/>Stores everything]
        B[Window Memory<br/>Keeps last K exchanges]
        C[Summary Memory<br/>Summarizes history]
        D[Vector Memory<br/>Semantic retrieval]
        E[KG Memory<br/>Knowledge graph]
    end

    A -->|Long conversations<br/>exceed context| B
    B -->|Loses old context| C
    C -->|May lose details| D
    D -->|Most flexible but<br/>most complex| E

    style A fill:#42A5F5,color:#fff
    style B fill:#66BB6A,color:#fff
    style C fill:#FFA726,color:#fff
    style D fill:#AB47BC,color:#fff
    style E fill:#EF5350,color:#fff
```

| Memory Type | Pros | Cons | Best For |
|-------------|------|------|----------|
| Buffer | Simple, complete history | Exceeds context window | Short conversations |
| Window | Bounded size | Loses early context | Medium conversations |
| Summary | Compressed, preserves key info | May lose details | Long conversations |
| Vector | Semantic retrieval, scalable | More complex setup | Large knowledge bases |
| Knowledge Graph | Structured relationships | Complex implementation | Relationship-heavy data |

---

## 4.9 Tools

Tools are functions that an AI agent can call to interact with the external world. They extend the agent's capabilities beyond text generation, enabling it to fetch real-time data, perform calculations, query databases, make API calls, and more.

### Tool Architecture

```mermaid
graph TD
    A[Agent] --> B{Which tool<br/>should I use?}
    B -->|Weather query| C[Weather Tool]
    B -->|Math problem| D[Calculator Tool]
    B -->|Search needed| E[Search Tool]
    B -->|Database query| F[Database Tool]

    C --> G[Result: Sunny, 25°C]
    D --> H[Result: 42]
    E --> I[Result: Search snippets]
    F --> J[Result: Query rows]

    G --> K[Agent synthesizes<br/>final answer]
    H --> K
    I --> K
    J --> K

    style A fill:#78909C,color:#fff
    style B fill:#FFC107,color:#000
    style K fill:#4CAF50,color:#fff
```

### Creating Custom Tools with the @tool Decorator

```python
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@tool
def get_word_length(word: str) -> int:
    """Returns the length of a word."""
    return len(word)

# Tools have name, description, and args_schema
print(f"Tool name: {multiply.name}")
print(f"Tool description: {multiply.description}")
print(f"Tool args: {multiply.args_schema.model_json_schema()}")

# Invoke a tool directly
result = multiply.invoke({"a": 7, "b": 6})
print(f"7 * 6 = {result}")  # 42
```

### Creating Tools with StructuredTool

For more control over the tool definition:

```python
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="Search query string")
    max_results: int = Field(default=5, description="Maximum number of results")

def search_function(query: str, max_results: int = 5) -> str:
    """Simulated search function."""
    # In real use, this would call a search API
    return f"Found {max_results} results for '{query}'"

search_tool = StructuredTool.from_function(
    func=search_function,
    name="web_search",
    description="Search the web for information",
    args_schema=SearchInput,
)

result = search_tool.invoke({"query": "LangChain tutorial", "max_results": 3})
print(result)  # Found 3 results for 'LangChain tutorial'
```

### Built-in Tools

LangChain provides many pre-built tools through `langchain-community`:

```python
# Example: Wikipedia tool
# pip install wikipedia
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
result = wikipedia.invoke("Artificial intelligence")
print(result[:200])  # First 200 chars of the Wikipedia article

# Example: Python REPL tool (for code execution)
from langchain_community.tools import PythonREPLTool
python_repl = PythonREPLTool()
result = python_repl.invoke("print(2 ** 10)")
print(result)  # 1024

# Example: Requests tool (for HTTP calls)
from langchain_community.tools import RequestsGetTool
from langchain_community.utilities import TextRequestsWrapper
```

### Tool Best Practices

1. **Write clear descriptions**: The LLM uses the tool's `description` to decide when and how to use it. Be specific about what the tool does, what inputs it expects, and what it returns.
2. **Use type hints**: Always add type hints to your tool functions. LangChain uses them to generate the argument schema.
3. **Keep tools focused**: Each tool should do one thing well. Avoid "Swiss army knife" tools that try to handle multiple unrelated tasks.
4. **Handle errors gracefully**: Tools should return meaningful error messages rather than raising exceptions, so the agent can understand what went wrong and try a different approach.
5. **Document edge cases**: Mention limitations and edge cases in the tool description to help the LLM use the tool correctly.

---

## 4.10 Agents

Agents are the most powerful abstraction in LangChain. An agent uses an LLM as a reasoning engine to decide which actions (tool calls) to take, in what order, based on the user's input and the results of previous actions.

### How Agents Work

```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent (LLM)
    participant T as Tools

    U->>A: "What is 15% of 847?"

    Note over A: LLM reasons: "I need to calculate 15% of 847.<br/>I should use the calculator tool."

    A->>T: multiply(0.15, 847)
    T-->>A: 127.05

    Note over A: LLM reasons: "I have the answer: 127.05"

    A->>U: 15% of 847 is 127.05
```

### Agent Decision Loop

```mermaid
graph TD
    A[User Input] --> B[Agent]
    B --> C[LLM Decides: Think / Act / Finish]
    C --> D{Decision?}
    D -->|Act| E[Call Tool]
    E --> F[Get Observation]
    F --> B
    D -->|Think| G[Internal Reasoning]
    G --> B
    D -->|Finish| H[Return Final Answer]

    style B fill:#78909C,color:#fff
    style D fill:#FFC107,color:#000
    style H fill:#4CAF50,color:#fff
```

### Creating an Agent with create_tool_calling_agent

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Step 1: Define tools
@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def power(base: int, exponent: int) -> int:
    """Raise a number to a power."""
    return base ** exponent

tools = [add, multiply, power]

# Step 2: Create the prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful math assistant. Use tools to calculate answers."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # Required for agent reasoning
])

# Step 3: Create the agent
llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_tool_calling_agent(llm, tools, prompt)

# Step 4: Create the agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # Shows reasoning steps
    max_iterations=10,  # Safety limit
)

# Step 5: Run the agent
result = agent_executor.invoke({
    "input": "What is (5 + 3) squared?"
})
print(result["output"])
```

### Agent Execution Trace

When `verbose=True`, you can see the agent's reasoning:

```
> Entering new AgentExecutor chain...

Invoking: `add` with `{'a': 5, 'b': 3}`
8

Invoking: `power` with `{'base': 8, 'exponent': 2}`
64

> Finished chain.
The result of (5 + 3) squared is 64.
```

### Agent with Search Tool (Real-World Example)

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Simulated search tool
@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    # In production, use Tavily, SerpAPI, or similar
    fake_results = {
        "langchain latest version": "LangChain v0.3.0 was released with LCEL improvements.",
        "python latest version": "Python 3.13 was released in October 2024.",
    }
    for key, value in fake_results.items():
        if key in query.lower():
            return value
    return f"Search results for: {query}"

@tool
def get_current_weather(city: str) -> str:
    """Get the current weather for a city."""
    # In production, call a real weather API
    return f"Weather in {city}: 22°C, partly cloudy"

tools = [search_web, get_current_weather]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools when you need current information."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({
    "input": "What's the weather in Tokyo and what's the latest Python version?"
})
print(result["output"])
```

### Agent Types in LangChain

```mermaid
graph TB
    subgraph "Agent Types"
        A[Tool-Calling Agent<br/>Uses model's native<br/>tool-calling API]
        B[ReAct Agent<br/>Reason + Act<br/>in text]
        C[OpenAI Functions Agent<br/>Uses OpenAI's<br/>function calling]
        D[Structured Chat Agent<br/>For multi-tool<br/>conversations]
        E[Self-Ask Agent<br/>Decomposes into<br/>sub-questions]
    end

    A -->|Recommended| F[Best for most<br/>modern use cases]
    B -->|Legacy| G[Works with any<br/>LLM provider]
    C -->|OpenAI Only| H[Optimized for<br/>OpenAI models]

    style A fill:#4CAF50,color:#fff
    style F fill:#4CAF50,color:#fff
```

### AgentExecutor Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `agent` | The agent to run | Required |
| `tools` | List of tools available to the agent | Required |
| `verbose` | Print reasoning steps | False |
| `max_iterations` | Maximum reasoning steps | 15 |
| `max_execution_time` | Timeout in seconds | None |
| `early_stopping_method` | What to do on limit: "force" or "generate" | "force" |
| `handle_parsing_errors` | How to handle output parsing errors | False |
| `return_intermediate_steps` | Return all tool calls made | False |

---

## 4.11 Retrieval Augmented Generation (RAG)

RAG is one of the most important patterns in LLM application development. It addresses a fundamental limitation of LLMs: they only know what was in their training data. RAG enables LLMs to access and reason about your private, up-to-date, or domain-specific data.

### Why RAG?

```mermaid
graph LR
    subgraph "Without RAG"
        A1[User Question] --> B1[LLM]
        B1 --> C1[Answer from<br/>training data only]
    end

    subgraph "With RAG"
        A2[User Question] --> B2[Retriever]
        B2 --> C2[Relevant Documents]
        C2 --> D2[Question + Documents]
        D2 --> E2[LLM]
        E2 --> F2[Answer grounded<br/>in your data]
    end

    style C1 fill:#EF5350,color:#fff
    style F2 fill:#4CAF50,color:#fff
```

### RAG Pipeline Architecture

```mermaid
graph TD
    subgraph "Indexing Phase (Offline)"
        A[Documents] --> B[Split into Chunks]
        B --> C[Generate Embeddings]
        C --> D[Store in Vector Store]
    end

    subgraph "Query Phase (Online)"
        E[User Question] --> F[Embed Question]
        F --> G[Similarity Search<br/>in Vector Store]
        G --> H[Retrieve Top-K Chunks]
        H --> I[Construct Prompt:<br/>Question + Retrieved Chunks]
        I --> J[LLM Generates Answer]
    end

    D -.->|Search| G

    style D fill:#42A5F5,color:#fff
    style J fill:#4CAF50,color:#fff
```

### Step 1: Document Loading

```python
from langchain_community.document_loaders import TextLoader, PyPDFLoader, WebBaseLoader

# Load from a text file
text_loader = TextLoader("./my_document.txt")
text_docs = text_loader.load()

# Load from a PDF
pdf_loader = PyPDFLoader("./research_paper.pdf")
pdf_docs = pdf_loader.load()

# Load from a web page
# pip install beautifulsoup4
web_loader = WebBaseLoader("https://en.wikipedia.org/wiki/LangChain")
web_docs = web_loader.load()

print(f"Loaded {len(pdf_docs)} pages from PDF")
print(f"First page preview: {pdf_docs[0].page_content[:200]}")
```

### Step 2: Text Splitting

Large documents need to be split into smaller chunks for effective retrieval:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Create a text splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,       # Max characters per chunk
    chunk_overlap=200,     # Overlap between chunks for context
    separators=["\n\n", "\n", ". ", " ", ""],  # Split priorities
)

# Split documents
chunks = splitter.split_documents(pdf_docs)
print(f"Split into {len(chunks)} chunks")
print(f"First chunk: {chunks[0].page_content[:200]}")
```

### Why Recursive Splitting?

```mermaid
graph TD
    A[Full Document] --> B[Try splitting by \n\n]
    B --> C{Chunks still<br/>too large?}
    C -->|Yes| D[Try splitting by \n]
    C -->|No| E[Done]
    D --> F{Chunks still<br/>too large?}
    F -->|Yes| G[Try splitting by . ]
    F -->|No| E
    G --> H{Still too large?}
    H -->|Yes| I[Try splitting by space]
    H -->|No| E
    I --> J[Character-level split]

    style E fill:#4CAF50,color:#fff
```

### Step 3: Create Embeddings and Vector Store

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Create embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create a vector store from document chunks
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"  # Optional: persist to disk
)

# Or load an existing vector store
# vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
```

### Step 4: Retrieval

```python
# Create a retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",  # or "mmr" for diversity
    search_kwargs={"k": 4}     # Return top 4 most similar chunks
)

# Retrieve relevant documents
docs = retriever.invoke("What are the main topics in the document?")
for i, doc in enumerate(docs):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content[:200])
    print(f"Source: {doc.metadata.get('source', 'unknown')}")
```

### Step 5: Build the RAG Chain

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# Define the RAG prompt
rag_prompt = ChatPromptTemplate.from_template(
    """Answer the question based on the following context. 
    If you cannot find the answer in the context, say "I don't have enough information."

    Context:
    {context}

    Question: {question}

    Answer:"""
)

# Helper function to format documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Build the RAG chain
llm = ChatOpenAI(model="gpt-4", temperature=0)

rag_chain = (
    RunnableParallel(
        context=retriever | format_docs,  # Retrieve and format docs
        question=RunnablePassthrough(),    # Pass question through
    )
    | rag_prompt
    | llm
    | StrOutputParser()
)

# Ask a question
answer = rag_chain.invoke("What are the key findings of the research?")
print(answer)
```

### RAG Chain Data Flow

```mermaid
graph LR
    A[Question] --> B[RunnableParallel]
    B --> C[Retriever → format_docs]
    B --> D[RunnablePassthrough]
    C --> E[context + question]
    D --> E
    E --> F[RAG Prompt]
    F --> G[LLM]
    G --> H[StrOutputParser]
    H --> I[Answer]

    style B fill:#42A5F5,color:#fff
    style I fill:#4CAF50,color:#fff
```

### Advanced RAG Techniques

| Technique | Description | When to Use |
|-----------|-------------|-------------|
| **Parent Document Retriever** | Retrieve small chunks but return the parent document for context | When small chunks lose important context |
| **Multi-Query Retriever** | Generate multiple query variations for better recall | When user queries are ambiguous |
| **Contextual Compression** | Compress retrieved documents to only relevant parts | When chunks are large and contain irrelevant info |
| **Ensemble Retriever** | Combine multiple retrieval strategies (e.g., vector + keyword) | When no single strategy covers all cases |
| **Re-ranking** | Score and re-order retrieved documents by relevance | When precision matters more than recall |
| **Self-Query** | Extract metadata filters from the question | When documents have structured metadata |

---

## 4.12 Callbacks

Callbacks are LangChain's observability mechanism. They allow you to hook into every step of execution — logging, tracing, monitoring, and debugging your chains and agents.

### Callback Architecture

```mermaid
graph TD
    A[Chain Execution] --> B[Callback Manager]
    B --> C[on_chain_start]
    B --> D[on_llm_start]
    B --> E[on_tool_start]
    B --> F[on_chain_end]
    B --> G[on_llm_end]
    B --> H[on_tool_end]
    B --> I[on_llm_error]
    B --> J[on_chain_error]

    C --> K[Your Custom Handler]
    D --> K
    E --> K
    F --> K
    G --> K
    H --> K
    I --> K
    J --> K

    style K fill:#FF9800,color:#fff
```

### Custom Callback Handler

```python
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class MyCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for logging and monitoring."""

    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"[LLM START] Model: {serialized.get('name', 'unknown')}")
        print(f"[LLM START] Number of prompts: {len(prompts)}")

    def on_llm_end(self, response, **kwargs):
        tokens = response.llm_output.get('token_usage', {}) if response.llm_output else {}
        print(f"[LLM END] Tokens used: {tokens}")

    def on_llm_error(self, error, **kwargs):
        print(f"[LLM ERROR] {error}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        print(f"[CHAIN START] {serialized.get('name', 'unnamed')}")
        print(f"[CHAIN START] Inputs: {inputs}")

    def on_chain_end(self, outputs, **kwargs):
        print(f"[CHAIN END] Outputs: {outputs}")

    def on_tool_start(self, serialized, input_str, **kwargs):
        print(f"[TOOL START] {serialized.get('name', 'unnamed')}")
        print(f"[TOOL START] Input: {input_str}")

    def on_tool_end(self, output, **kwargs):
        print(f"[TOOL END] Output: {output}")


# Use the callback handler
handler = MyCallbackHandler()

prompt = ChatPromptTemplate.from_template("Explain {topic} in one sentence.")
model = ChatOpenAI(model="gpt-4", temperature=0)
chain = prompt | model | StrOutputParser()

result = chain.invoke(
    {"topic": "quantum computing"},
    config={"callbacks": [handler]}
)
```

### Using LangSmith for Observability

LangSmith is LangChain's official observability platform:

```python
import os

# Set LangSmith environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
os.environ["LANGCHAIN_PROJECT"] = "my-langchain-project"

# Now all chain executions are automatically traced in LangSmith
# No code changes needed — just set the environment variables
```

---

## 4.13 LangChain Expression Language (LCEL)

LCEL is the declarative composition language that powers modern LangChain. It provides a consistent interface for composing, invoking, and managing chains.

### LCEL Design Principles

1. **Every component is a Runnable**: Prompts, models, parsers, tools, retrievers — they all implement the `Runnable` interface
2. **Compose with pipes**: The `|` operator creates `RunnableSequence` chains
3. **Consistent interface**: Every runnable has `invoke()`, `batch()`, `stream()`, and async variants
4. **Automatic schema propagation**: Input and output schemas flow through the chain automatically

### Runnable Interface Methods

```mermaid
graph TB
    subgraph "Runnable Interface"
        A[invoke<br/>Single input, sync]
        B[batch<br/>Multiple inputs, sync]
        C[stream<br/>Token-by-token, sync]
        D[ainvoke<br/>Single input, async]
        E[abatch<br/>Multiple inputs, async]
        F[astream<br/>Token-by-token, async]
        G[ainvoke<br/>Single input, async]
    end

    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#9C27B0,color:#fff
```

### LCEL Composition Primitives

| Primitive | Purpose | Example |
|-----------|---------|---------|
| `RunnableSequence` (`\|`) | Chain steps sequentially | `prompt \| model \| parser` |
| `RunnableParallel` | Run steps concurrently | `RunnableParallel(a=chain1, b=chain2)` |
| `RunnablePassthrough` | Pass input through unchanged | Pass user input alongside retrieved docs |
| `RunnableLambda` | Wrap a Python function | Custom data transformation |
| `RunnableBranch` | Conditional branching | Route based on input type |
| `RunnableWithMessageHistory` | Add memory to a chain | Maintain conversation state |

### RunnableBranch Example

```python
from langchain_core.runnables import RunnableBranch

# Conditional logic in chains
branch = RunnableBranch(
    (lambda x: "math" in x["topic"].lower(), math_chain),
    (lambda x: "code" in x["topic"].lower(), code_chain),
    (lambda x: "history" in x["topic"].lower(), history_chain),
    default_chain,  # Fallback
)

result = branch.invoke({"topic": "math", "question": "What is 2+2?"})
```

### Complete LCEL Example: Building a Full RAG + Chat Application

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.vectorstores import Chroma

# --- Setup ---
llm = ChatOpenAI(model="gpt-4", temperature=0.7)
embeddings = OpenAIEmbeddings()

# Assume we have a vectorstore already created
vectorstore = Chroma(persist_directory="./my_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

# --- Build the chain ---
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Answer questions based on the 
    provided context. If the context doesn't contain the answer, say so.

    Context:
    {context}"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

# RAG chain without history
rag_chain = RunnableParallel(
    context=retriever | format_docs,
    question=RunnablePassthrough(),
) | prompt | llm | StrOutputParser()

# Add conversation history
store = {}
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Final chain with memory
chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

# --- Use it ---
response1 = chain_with_history.invoke(
    {"question": "What does the document say about AI safety?"},
    config={"configurable": {"session_id": "user-1"}},
)
print(response1)

response2 = chain_with_history.invoke(
    {"question": "Can you elaborate on that?"},
    config={"configurable": {"session_id": "user-1"}},
)
print(response2)
```

---

# Part 5: Interview Tips and Common Questions

## 5.1 Conceptual Questions

### Q1: What is the difference between an LLM and a Chat Model in LangChain?

**Answer**: An LLM takes a plain text string as input and returns a text string as output. It is the legacy completion-style interface. A Chat Model takes a list of structured `Message` objects (SystemMessage, HumanMessage, AIMessage) as input and returns an `AIMessage` as output. Chat Models are the modern, recommended interface because they support conversation history, system prompts, and different message roles. Most modern LLMs (GPT-4, Claude, Gemini) are accessed through the Chat Model interface.

### Q2: What is the ReAct pattern and why is it important?

**Answer**: ReAct (Reason + Act) is an agent architecture that interleaves reasoning steps with action steps. At each iteration, the agent first reasons about the current situation (Thought), then takes an action using a tool (Action), and observes the result (Observation). This Thought-Action-Observation loop continues until the agent can produce a final answer. ReAct is important because it makes the agent's decision-making process transparent and debuggable, it allows the agent to adapt its strategy based on intermediate results, and it produces better outcomes than pure reasoning or pure acting alone.

### Q3: What is the difference between a Chain and an Agent?

**Answer**: A Chain follows a predetermined, fixed sequence of operations. The flow is defined at design time — input goes through step A, then step B, then step C. An Agent, on the other hand, uses an LLM to dynamically decide which actions to take and in what order. The flow is determined at runtime based on the user's input and intermediate results. Chains are simpler, more predictable, and easier to debug. Agents are more flexible and powerful but less predictable and harder to debug.

### Q4: Explain RAG and why it is needed.

**Answer**: RAG (Retrieval Augmented Generation) is a pattern that enhances LLM responses by retrieving relevant documents from a knowledge base and including them in the prompt context. It is needed because LLMs have three fundamental limitations: (1) their knowledge is frozen at training time, so they cannot access current information; (2) they have no access to private or proprietary data; and (3) they can hallucinate — confidently generating incorrect information. RAG addresses all three by grounding the LLM's responses in retrieved, factual documents. The retrieval step ensures relevance, and the inclusion of source documents enables attribution and verification.

### Q5: What is LCEL and what benefits does it provide?

**Answer**: LCEL (LangChain Expression Language) is LangChain's declarative composition syntax using the pipe (`|`) operator. It provides several benefits: (1) a consistent interface — every component implements `invoke()`, `batch()`, `stream()`, and async variants; (2) first-class streaming support that works automatically through composed chains; (3) automatic tracing and observability through LangSmith; (4) parallel execution through `RunnableParallel`; and (5) type safety with automatic schema propagation. LCEL replaced the older `LLMChain` class as the recommended way to compose LangChain components.

## 5.2 Architecture and Design Questions

### Q6: How would you design a customer support chatbot using LangChain?

**Answer**: A production customer support chatbot would use the following architecture:

1. **Document Loading**: Ingest the company's knowledge base (FAQs, product docs, policy documents) using appropriate loaders.
2. **Vector Store**: Create embeddings and store them in a vector database (Pinecone, Weaviade, or Chroma) for semantic retrieval.
3. **RAG Chain**: Build a retrieval chain that finds relevant knowledge base articles for each user question and includes them as context.
4. **Memory**: Use conversation memory so the bot can handle multi-turn conversations and reference previous exchanges.
5. **Tools**: Add tools for common actions — order lookup, refund processing, ticket creation — so the bot can actually resolve issues, not just provide information.
6. **Agent**: Use a tool-calling agent so the bot can decide when to search the knowledge base, when to use an action tool, and when to escalate to a human.
7. **Guardrails**: Add input validation, output filtering, and safety checks to ensure the bot stays within its designated scope.
8. **Monitoring**: Integrate LangSmith for tracing, and add metrics for response quality, resolution rate, and customer satisfaction.

### Q7: How do you handle the context window limit in a RAG application?

**Answer**: Several strategies can be used individually or in combination:

1. **Chunk size tuning**: Adjust the text splitter's `chunk_size` to produce chunks that, when combined with the prompt and question, fit within the context window.
2. **Top-K tuning**: Reduce the number of retrieved documents (`k`) to limit the total context size.
3. **Contextual compression**: Use a compressor to extract only the relevant portions of each retrieved document, removing irrelevant content.
4. **Re-ranking**: Retrieve more documents initially (e.g., k=20), then use a re-ranker to select only the most relevant ones (e.g., top 5).
5. **Map-reduce**: Process each document independently to extract relevant information, then synthesize the extracts into a final answer.
6. **Summarization**: Summarize long documents before including them in the context.
7. **Parent-child retrieval**: Retrieve using small chunks for precision, but include the parent document (or a summary of it) for broader context.

### Q8: What are the different types of memory in LangChain and when would you use each?

**Answer**:

- **ConversationBufferMemory**: Stores the complete conversation history. Best for short conversations where full context is important.
- **ConversationBufferWindowMemory**: Stores only the last K exchanges. Best for medium-length conversations where recent context is most important.
- **ConversationSummaryMemory**: Maintains a running summary of the conversation. Best for long conversations where a compressed view is sufficient.
- **ConversationSummaryBufferMemory**: Combines summary for old messages with full buffer for recent messages. Best balance between completeness and token efficiency.
- **VectorStoreRetrieverMemory**: Stores all messages in a vector store and retrieves the most semantically relevant ones. Best for conversations where specific details from the past need to be recalled regardless of recency.
- **ConversationKGMemory**: Extracts entities and relationships into a knowledge graph. Best for conversations involving complex relationships between entities.

## 5.3 Practical and Coding Questions

### Q9: How do you create a custom tool in LangChain?

**Answer**: There are two main approaches:

1. **@tool decorator** (recommended for most cases): Add the `@tool` decorator to a function with type hints and a docstring. LangChain automatically extracts the name, description, and argument schema.

2. **StructuredTool class** (for more control): Create a `StructuredTool` with explicit name, description, function, and argument schema using a Pydantic model.

Key best practices: write clear descriptions (the LLM uses them for tool selection), add type hints (LangChain uses them for the argument schema), keep tools focused on one task, handle errors gracefully by returning error messages instead of raising exceptions, and document edge cases in the description.

### Q10: Write a chain that translates text and then summarizes it.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatOpenAI(model="gpt-4", temperature=0.3)

# Step 1: Translate
translate_prompt = ChatPromptTemplate.from_template(
    "Translate the following text to {target_language}:\n\n{text}"
)
translate_chain = translate_prompt | model | StrOutputParser()

# Step 2: Summarize
summarize_prompt = ChatPromptTemplate.from_template(
    "Summarize the following text in {summary_length} words or less:\n\n{text}"
)
summarize_chain = summarize_prompt | model | StrOutputParser()

# Combine
text = "Artificial intelligence is transforming industries worldwide..."
translated = translate_chain.invoke({
    "target_language": "French",
    "text": text
})
summary = summarize_chain.invoke({
    "summary_length": 50,
    "text": translated
})
print(summary)
```

## 5.4 System Design Questions

### Q11: Design a multi-agent research system.

```mermaid
graph TD
    A[User: Research Request] --> B[Supervisor Agent]
    B --> C[Search Agent]
    B --> D[Analysis Agent]
    B --> E[Writing Agent]

    C --> C1[Web Search Tool]
    C --> C2[Academic DB Tool]
    C --> C3[News API Tool]

    D --> D1[Summarization Chain]
    D --> D2[Fact-Checking Chain]
    D --> D3[Comparison Chain]

    E --> E1[Outline Generator]
    E --> E2[Section Writer]
    E --> E3[Citation Formatter]

    C -->|Search results| B
    D -->|Analysis results| B
    E -->|Draft sections| B
    B --> F[Final Research Report]

    style B fill:#FF5722,color:#fff
    style F fill:#4CAF50,color:#fff
```

**Answer**: A multi-agent research system would use LangGraph for orchestration with the following design:

1. **Supervisor Agent**: Receives the research request, decomposes it into sub-tasks, assigns them to specialist agents, and synthesizes the results.
2. **Search Agent**: Equipped with web search, academic database, and news API tools. Responsible for finding relevant sources and raw information.
3. **Analysis Agent**: Has chains for summarization, fact-checking, and comparison. Processes the raw information into structured analysis.
4. **Writing Agent**: Has chains for outlining, section writing, and citation formatting. Produces the final research document.
5. **State Management**: LangGraph maintains a shared state that all agents read from and write to, including the research request, gathered sources, analysis notes, and draft sections.
6. **Human-in-the-Loop**: The supervisor pauses for human review at key checkpoints — after the search phase, after the analysis phase, and before finalizing the report.

## 5.5 Debugging and Optimization Questions

### Q12: How do you debug a LangChain agent that is not using the correct tool?

**Answer**:

1. **Enable verbose mode**: Set `verbose=True` in the `AgentExecutor` to see the agent's full reasoning chain, including which tools it considers and why it chooses one over another.
2. **Check tool descriptions**: The LLM selects tools based on their descriptions. If the description is vague or ambiguous, the agent may choose the wrong tool. Make descriptions specific, detailed, and distinct from each other.
3. **Review the prompt**: The system prompt should clearly instruct the agent on when to use each tool. Add explicit guidance like "Use the calculator tool for any arithmetic operations."
4. **Use LangSmith tracing**: LangSmith shows the exact prompts, tool calls, and responses at each step, making it easy to identify where the agent went wrong.
5. **Test tools independently**: Verify that each tool works correctly when called directly with known inputs.
6. **Check argument passing**: Sometimes the agent calls the right tool but passes incorrect arguments. This can be a prompt issue or a schema issue.
7. **Add few-shot examples**: Include examples of correct tool usage in the prompt to guide the agent.

### Q13: How do you optimize a RAG pipeline for better retrieval quality?

**Answer**:

1. **Improve chunking**: Experiment with chunk size and overlap. Smaller chunks improve precision but may lose context; larger chunks provide more context but may include irrelevant information.
2. **Use better embeddings**: Upgrade to the latest embedding model (e.g., `text-embedding-3-large` instead of `text-embedding-ada-002`).
3. **Add metadata filtering**: Store metadata (date, category, source) with each chunk and use it to filter retrievals before similarity search.
4. **Implement re-ranking**: After initial retrieval, use a cross-encoder or LLM to re-rank results by actual relevance to the query.
5. **Query transformation**: Use techniques like HyDE (Hypothetical Document Embeddings) — ask the LLM to generate a hypothetical answer, then use that for retrieval.
6. **Multi-query retrieval**: Generate multiple variations of the user's query and retrieve for each, then merge results.
7. **Evaluate with metrics**: Use frameworks like RAGAS to measure retrieval precision, context relevance, faithfulness, and answer relevancy.

## 5.6 Quick Reference: LangChain Cheat Sheet

```
┌─────────────────────────────────────────────────────────┐
│                  LANGCHAIN CHEAT SHEET                   │
├─────────────────────────────────────────────────────────┤
│ MODELS                                                   │
│   ChatOpenAI(model="gpt-4")        # Chat model         │
│   OpenAI(model="gpt-3.5-turbo")    # Completion model   │
│   OpenAIEmbeddings()               # Embeddings          │
├─────────────────────────────────────────────────────────┤
│ PROMPTS                                                  │
│   PromptTemplate.from_template("...{var}...")            │
│   ChatPromptTemplate.from_messages([                     │
│       ("system", "..."),                                 │
│       MessagesPlaceholder("history"),                    │
│       ("human", "{question}"),                           │
│   ])                                                     │
├─────────────────────────────────────────────────────────┤
│ PARSERS                                                  │
│   StrOutputParser()                # Plain string        │
│   JsonOutputParser()               # JSON dict           │
│   PydanticOutputParser()           # Pydantic model      │
│   CommaSeparatedListOutputParser() # List of strings     │
├─────────────────────────────────────────────────────────┤
│ CHAINS (LCEL)                                            │
│   chain = prompt | model | parser                        │
│   result = chain.invoke({...})                           │
│   results = chain.batch([{...}, {...}])                  │
│   for chunk in chain.stream({...}): ...                  │
├─────────────────────────────────────────────────────────┤
│ TOOLS                                                    │
│   @tool                                                  │
│   def my_tool(param: type) -> return_type:              │
│       """Description for the LLM."""                     │
│       ...                                                │
├─────────────────────────────────────────────────────────┤
│ AGENTS                                                   │
│   agent = create_tool_calling_agent(llm, tools, prompt)  │
│   executor = AgentExecutor(agent, tools, verbose=True)   │
│   result = executor.invoke({"input": "..."})             │
├─────────────────────────────────────────────────────────┤
│ RAG                                                      │
│   vectorstore = Chroma.from_documents(docs, embeddings)  │
│   retriever = vectorstore.as_retriever(k=4)              │
│   rag_chain = (                                          │
│       {"context": retriever | format, "q": passthrough}  │
│       | prompt | llm | parser                            │
│   )                                                      │
├─────────────────────────────────────────────────────────┤
│ MEMORY                                                   │
│   RunnableWithMessageHistory(                            │
│       chain, get_session_history,                        │
│       input_messages_key="question",                     │
│       history_messages_key="history",                    │
│   )                                                      │
└─────────────────────────────────────────────────────────┘
```

## 5.7 Common Pitfalls to Avoid

| Pitfall | Description | Solution |
|---------|-------------|----------|
| **Ignoring token limits** | Sending too many tokens to the model | Monitor token usage, use chunking and summarization |
| **Vague tool descriptions** | Agent cannot select the right tool | Write specific, detailed tool descriptions |
| **No error handling** | Chain fails silently or crashes | Add `handle_parsing_errors` to AgentExecutor, use try/except |
| **Over-abstraction** | Too many layers make debugging hard | Start simple, add complexity only when needed |
| **Ignoring streaming** | Users wait for full response before seeing anything | Use `stream()` for better UX |
| **No evaluation** | You do not know if RAG is working well | Use RAGAS or LangSmith evaluation |
| **Storing secrets in code** | API keys hardcoded in source files | Use environment variables or `.env` files |
| **Not using LangSmith** | No visibility into chain execution | Enable LangSmith tracing from the start |

---

## 5.8 Recommended Learning Path

```mermaid
graph TD
    A[Week 1: Basics] --> B[Week 2: Chains & Parsers]
    B --> C[Week 3: RAG]
    C --> D[Week 4: Agents & Tools]
    D --> E[Week 5: Memory & State]
    E --> F[Week 6: Production]

    A --- A1[Models & Prompts]
    A --- A2[Simple Chains]
    A --- A3[LCEL Basics]

    B --- B1[Sequential Chains]
    B --- B2[Output Parsers]
    B --- B3[RunnableParallel]

    C --- C1[Document Loaders]
    C --- C2[Text Splitters]
    C --- C3[Vector Stores]
    C --- C4[Retrievers]

    D --- D1[Custom Tools]
    D --- D2[Tool-Calling Agents]
    D --- D3[ReAct Agents]

    E --- E1[Conversation Memory]
    E --- E2[RunnableWithMessageHistory]
    E --- E3[LangGraph State]

    F --- F1[LangSmith Tracing]
    F --- F2[Error Handling]
    F --- F3[Evaluation]
    F --- F4[Deployment with LangServe]

    style A fill:#4CAF50,color:#fff
    style B fill:#66BB6A,color:#fff
    style C fill:#2196F3,color:#fff
    style D fill:#FF9800,color:#fff
    style E fill:#AB47BC,color:#fff
    style F fill:#F44336,color:#fff
```

---

*This guide covers the fundamentals of AI frameworks, Agentic AI, and LangChain. Practice with real projects, experiment with different configurations, and build progressively more complex applications to deepen your understanding. The field evolves rapidly, so keep exploring the official LangChain documentation and community resources for the latest updates.*
