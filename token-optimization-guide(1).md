# The Token Optimization Playbook

**A field guide to context, prompt, and related engineering for the per-token era.**

> **Status:** v1.0 · 2026-09-20
> **Scope:** Provider-agnostic. Examples bias toward GitHub Copilot, OpenAI, Anthropic, and Google models because those are the production surfaces most teams ship on today, but every pattern generalises to any BPE / Unigram / SentencePiece tokenizer.
> **Inspired by** the public quick guide at *ashy-dune-0b4215a0f.7.azurestaticapps.net* and the *sukurcf* detailed playbook, both authored by Microsoft Asia Developer GBB. This document is a deeper, broader, provider-agnostic rewrite that adds the open-source ecosystem, evaluation tooling, and prompt-engineering patterns the originals stop short of.

---

## Table of Contents

1. [Why tokens are a line item](#1-why-tokens-are-a-line-item)
2. [The anatomy of a prompt packet](#2-the-anatomy-of-a-prompt-packet)
3. [The three token types and how they are billed](#3-the-three-token-types-and-how-they-are-billed)
4. [The six cost drivers](#4-the-six-cost-drivers)
5. [The six pillars of token discipline](#5-the-six-pillars-of-token-discipline)
6. [Context engineering patterns](#6-context-engineering-patterns)
7. [Prompt engineering patterns](#7-prompt-engineering-patterns)
8. [Model routing and reasoning depth](#8-model-routing-and-reasoning-depth)
9. [Agent, tool, and session governance](#9-agent-tool-and-session-governance)
10. [Fifteen scenarios — the context-rot catalog](#10-fifteen-scenarios--the-context-rot-catalog)
11. [Eleven levers, deep dive](#11-eleven-levers-deep-dive)
12. [Evaluation, observability, and logs](#12-evaluation-observability-and-logs)
13. [Open-source ecosystem — 50+ repos, categorized](#13-open-source-ecosystem--50-repos-categorized)
14. [The calculator — pricing reference](#14-the-calculator--pricing-reference)
15. [Checklists and copy-paste templates](#15-checklists-and-copy-paste-templates)
16. [Companion scripts](#16-companion-scripts)
17. [Glossary and references](#17-glossary-and-references)

---

## 1. Why tokens are a line item

For the first two years of the LLM-application boom, tokens were abstract — a technical curiosity measured by the tokenizer, not by finance. Per-seat pricing for Copilot, flat-rate ChatGPT, and the early "free trial" era for Anthropic hid the underlying reality: every inference call costs somebody money, and the unit of cost is a token, not a request.

That changed in 2025. OpenAI moved the API to strict token-metered billing for reasoning models. Anthropic followed with usage-based tiering. GitHub Copilot moved from per-seat credits to **Usage-Based Billing (UBB)** effective June 2026, and every other major IDE-integrated assistant has either followed or announced equivalent plans. The implication is direct: every redundant token is now a line item on someone's invoice, and the people paying the invoice have started asking why their cost-per-developer doubled in a quarter.

The shift from per-seat to per-token is not just an accounting change — it changes the engineering incentives. Under per-seat, the cheapest thing a developer could do was throw the entire codebase at the model. Under per-token, that same move is the single most expensive thing they can do, and the second most expensive is to repeat it on the next turn. The teams who treat tokens as a budget line — measuring them, routing them, caching them, capping them — keep their cost-per-developer flat or falling. The teams who don't see cost-per-developer double in six months, then get surprised when the CFO freezes the Copilot entitlement.

This playbook is the engineering response to that shift. It is a working set of patterns, anti-patterns, reference prices, and open-source tools that a team can adopt in a quarter to take their per-developer token spend from "uncontrolled" (typically 30%+ overage) to "predictable" (10–15% overage, with monitoring). The headline numbers below are the realistic target — they are not aspirational; they are what teams who have done the work actually report.

| Metric | Uncontrolled team | Disciplined team |
|---|---|---|
| Token overage vs. plan | 30%+ | 10–15% |
| Useful work per license | 1.0× | 1.6–1.8× |
| Total token reduction | baseline | 37–44% (no measured productivity loss) |
| Cost per developer / quarter | rising | flat or falling |

---

## 2. The anatomy of a prompt packet

When you send "Refactor this" to a Copilot Chat, you are sending the smallest piece of the prompt. The model does not see just your three words; it sees an assembled **prompt packet** with up to seven layers, each of which is billed on every turn. Understanding this layering is the precondition for any optimisation work, because most of the leverage lives in the layers developers forget exist.

| Layer | What it contains | Who controls it | Cost behaviour |
|---|---|---|---|
| **1. System prompt** | Provider's base instructions, safety policy, tooling preamble. | Provider | Billed every turn. Fixed for a session, but not cacheable by you. |
| **2. Custom instructions** | Your repo's `copilot-instructions.md`, `AGENTS.md`, per-language `.instructions.md` files. | You | Billed every turn *unless* the prefix is byte-identical across turns — then it hits the cache discount. |
| **3. Tools & MCP schemas** | JSON schema for every enabled tool (Slack, Jira, DB, internal CLIs). | You + admin | Billed every turn, **multiplied by the number of steps in the agent loop**. The most overlooked tax. |
| **4. Conversation history** | Prior turns, tool results, retrieved files from earlier in the session. | You (via session lifecycle) | Grows every turn. By turn 30, it is typically 2–5× the size of the current prompt. |
| **5. Retrieved context** | Files you `@mention`, `#-mention`, RAG chunks, web search results. | You | Billed on the turn it's retrieved, then re-billed every subsequent turn while it stays in the window. |
| **6. Your message** | The actual instruction you typed. | You | The smallest piece. Shrinking this saves almost nothing on its own. |
| **7. Reasoning trace** | For reasoning models, the invisible chain-of-thought before the visible reply. | Model (gated by `reasoning_effort`) | Billed at the **output rate** — 4–8× the input rate — and frequently dwarfs the visible output. |

The single most important mental shift this table drives home is that **the user's message is the smallest piece**. Teams that try to save tokens by writing shorter questions save almost nothing, because the question is maybe 200 tokens out of a 20,000-token prompt packet. The leverage is in the other six layers: scope the retrieved context, prune the tool catalog, hold the instruction prefix stable so it caches, reset the session before history compounds, and right-size the reasoning effort. The rest of this playbook is, in effect, a tour of those six layers.

---

## 3. The three token types and how they are billed

Token cost is not one number. It is three numbers, and confusing them is the most common budgeting mistake. The three types behave differently, are billed at different rates, and respond to different optimisations.

### 3.1 Input tokens

Input tokens are everything in the prompt packet above that the model has to *read*: the system prompt, custom instructions, tool schemas, history, retrieved context, your message. They are billed at the **standard input rate** on every turn. If you send the same 5,000-token file reference on five consecutive turns, you pay for 25,000 input tokens. The lever is *scope and reuse*: send only what's needed, and reuse the rest via caching.

### 3.2 Cached tokens

Cached tokens are a subset of input tokens whose **byte-identical prefix** the provider can reuse across calls. When the prefix matches, the cached portion is billed at roughly **10% of the input rate** — a 90% discount. The catch is that the prefix must be byte-identical; any change (a single character in the system prompt, a re-ordered tool list, a one-line edit to `copilot-instructions.md`) invalidates the cache from the point of change onward. The lever is **stability**: keep the front of the prompt packet frozen across a session, and put volatile content (your message, fresh retrieved context) at the *end* of the packet.

### 3.3 Output tokens

Output tokens are what the model *writes*: the visible reply plus, for reasoning models, the invisible chain-of-thought. They are billed at the **output rate**, which is 4–8× the input rate on most providers. Output is the most expensive lane, and the most overlooked because it's invisible. A request that pulls 20,000 input tokens and emits 5,000 output tokens often costs more than the inverse, because the output rate overwhelms the input volume. The lever is **constrain and right-size**: explicit output caps ("code only, no explanation"), right-sized reasoning effort, and decomposition of high-effort tasks into lower-effort phases.

| Type | Relative rate | Billed on | Primary lever |
|---|---|---|---|
| Input | 1× | Every turn | Scope · compress · cache |
| Cached | ~0.1× | Every turn (if prefix matches) | Keep the prefix byte-identical |
| Output | 4–8× | Every generated token | Constrain · right-size reasoning · decompose |

A useful budgeting exercise: take any production prompt and estimate the *output cost* separately from the *input cost*. Most teams find the output cost is 50–80% of the total, even though it's the part they think about least. That insight reframes the optimisation target — you do not have an input problem, you have an output problem dressed up as an input problem.

---

## 4. The six cost drivers

Six factors account for almost all token cost. They are not equal — some swing the bill 2×, others swing it 40×. Ranking them by impact tells you where to spend your optimisation hour.

### 4.1 Context size (30–50% of spend)

The single largest line item. Every file you `@mention`, every chunk RAG retrieves, every prior turn in the session is billed on every subsequent turn while it stays in the window. A team that habitually uses `#codebase` (whole-repo context) is paying 5–10× what the same team pays with `#file` or `#selection`. The fix is the escalation ladder: `#selection → #file:Lx-Ly → #file → #codebase`, used in that order, with `#codebase` reserved for genuinely repo-wide questions.

### 4.2 Model selection (5–8× spread)

Choosing the wrong tier is the second-largest cost driver. Within a single provider, the "powerful" tier is typically 5–8× the cost of the "lightweight" tier. Across providers, an Opus-tier model is ~1.7× a Sonnet-tier model, and a Sonnet-tier model is ~6× a Haiku-tier model. Most teams default to the most capable model and never downgrade — even for tasks (lookups, simple edits, boilerplate generation) where the lightweight tier is equally accurate. The fix is **model routing**: plan with the big model, execute with the small model.

### 4.3 Reasoning effort (3–5× output, up to 60× at "Max")

Reasoning models expose a `reasoning_effort` knob: Low, Medium, High, Max. Each level multiplies the output-token count, and because output is billed at 4–8× input, the cost compounds. A "Max" effort request can produce 60× the output tokens of a "Low" effort request for the same visible reply. Most tasks do not need High effort; many do not need Medium. The fix is to default to Low or Medium, and reserve High/Max for tasks with explicit verification gates.

### 4.4 Agent-mode loops (10–40× multiplier)

Agent mode is where cost explodes. An agent that takes 30 steps to complete a task re-sends the entire prompt packet on every step — system prompt, custom instructions, tool schemas, history, retrieved context — and emits reasoning on every step. The multiplier vs. a single-shot Ask is roughly the number of steps. A 30-step agent run can cost 30× a single-shot request for the same outcome. The fix is **mode matching**: use Ask for questions, Plan for phased work, and reserve Agent for genuinely iterative tasks that need feedback loops.

### 4.5 MCP tool overhead (compounds past ~20 tools)

Every enabled tool's JSON schema rides along on every step of every agent turn. A 200-token tool schema × 30 steps × 50 tools is 300,000 tokens of pure schema overhead, before any actual work. Past ~20 enabled tools the cost becomes material; past ~50 it becomes the dominant cost. The fix is **per-workspace tool scoping**: enable Slack only in the workspace where Slack is used; enable the DB tool only in the data workspace; disable everything else by default.

### 4.6 Session length (2–5× by turn 30)

The longer a session runs, the more expensive each turn becomes, because the history accumulates and re-bills. By turn 30, the average per-turn cost is 2–5× the per-turn cost at turn 1, even if the work being done is identical. A team that runs one 40-turn session across four unrelated tasks pays 5–10× what the same team pays with four 10-turn sessions, one per task. The fix is **session hygiene**: one task = one session, `/clear` between unrelated tasks, and `/compact` at ~70% of the context window.

---

## 5. The six pillars of token discipline

The six pillars are the positive counterpart to the six cost drivers — the practices that, adopted together, deliver the 37–44% token reduction and 1.6–1.8× entitlement multiplier in the table at the top of this document.

| # | Pillar | Principle | Contribution |
|---|---|---|---|
| 01 | **Context discipline** | Send only what matters | 10–14% |
| 02 | **Intelligent model routing** | Match capability to task | 10–14% |
| 03 | **Instruction engineering** | Pay once for what you'd otherwise pay every turn | 7–10% |
| 04 | **Reasoning depth control** | Don't pay for thinking the task doesn't need | 5–8% |
| 05 | **Agent & tool governance** | Enable, don't accumulate | 3–5% |
| 06 | **Session lifecycle** | Reset, don't compound | 5–8% |

The contributions are roughly additive — adopt all six and you land near the 37–44% total reduction; adopt the first three and you typically capture 25–30%. The pillars are not new technology; they are discipline. The hard part is the institutional habit, not the technical pattern.

The rest of the playbook unpacks each pillar into concrete patterns. Sections 6–9 cover the engineering (context, prompt, routing, governance), sections 10–11 cover the scenario library and the eleven deep-dive levers, and sections 12–15 cover the tooling, the open-source ecosystem, the pricing calculator, and the copy-paste templates.

---

## 6. Context engineering patterns

Context engineering is the discipline of deciding **what the model sees**, separate from **what you ask it**. It is where the largest token savings live, because the context layers (retrieved files, RAG chunks, history) are the largest part of the prompt packet and the most amenable to systematic control. A prompt engineer writes the instruction once; a context engineer builds the system that decides what gets attached to that instruction on every turn.

### 6.1 The escalation ladder

The single most effective context-engineering pattern is the **escalation ladder**: a strict order of precedence for what to attach, used from the smallest rung upward, and only escalating to the next rung when the current one is insufficient.

| Rung | Pattern | Typical tokens | When to use |
|---|---|---|---|
| 1 | `#selection` — only the lines you have highlighted | 50–500 | The change is local to a known region |
| 2 | `#file:Lx-Ly` — a line range in a file | 200–2,000 | The change is in a known region of a known file |
| 3 | `#file` — the whole file | 500–10,000 | The change requires whole-file context (imports, types) |
| 4 | `#folder` — a directory | 2,000–50,000 | The change spans multiple files in a known directory |
| 5 | `#codebase` — whole-repo semantic search | 10,000–200,000 | The change requires repo-wide discovery; **last resort** |

The discipline is to start at rung 1 and only escalate when you can articulate why the current rung is insufficient. Most tasks live at rungs 1–3. `#codebase` should be a deliberate decision, not a default. Teams that adopt the ladder as a written convention (and enforce it in their `copilot-instructions.md`) typically cut their context-token spend 30–50% within a quarter.

### 6.2 Three-layer instruction files

Custom instructions should be split into three layers, not one giant `copilot-instructions.md`. Each layer has a different volatility, and the layering matters because it lets the cacheable prefix stay stable while volatile rules live elsewhere.

- **Layer 1 — Global:** cross-cutting rules that apply to every file in every repo. Examples: "Use uv, not pip", "Don't refactor auth — pending audit". Lives in `~/.github/copilot-instructions.md` or the org-level instructions. ~20 rules, ~500 tokens. Stable across months.
- **Layer 2 — Repo:** rules that apply to one repo. Lives in `<repo>/.github/copilot-instructions.md`. ~50 rules, ~1,500 tokens. Stable across weeks.
- **Layer 3 — Path-scoped:** rules that apply only to a glob. Lives in `<repo>/.github/<name>.instructions.md` with `applyTo` frontmatter, e.g. `applyTo: "src/api/**/*.ts"`. Loaded only when a file matching the glob is in the active context. ~10 rules per file, ~300 tokens. Stable per feature.

```markdown
---
applyTo: "src/api/**/*.ts"
---
# API conventions
- All endpoints return `Result<T, ApiError>`, never throw.
- Validate with zod at the controller boundary; never inline.
- Versioning: URL path (`/v1`, `/v2`), not header.
```

Path-scoped instructions are the most under-used pattern in the ecosystem. They let you keep rich, domain-specific rules (API conventions, DB migration order, test patterns) loaded only when relevant, instead of having a single 3,000-token instructions file ride along on every turn.

### 6.3 The cache-stable prefix

Cached tokens cost ~10% of input tokens, but only when the prefix is byte-identical across calls. The implication is structural: **the front of your prompt packet should not change within a session.** Concretely:

- The system prompt is fixed by the provider — leave it alone.
- Custom instructions should not be edited mid-session.
- Tool schemas should not be enabled or disabled mid-session.
- The retrieved context you attach at turn N should not be re-attached in a different order at turn N+1.
- Your message (the volatile part) goes at the **end** of the packet, not the front.

When teams complain that "prompt caching doesn't seem to help", the cause is almost always one of: (a) they edited the custom instructions mid-session, invalidating the cache; (b) their RAG retriever re-ranks chunks between calls, so the retrieved context is never byte-identical; or (c) they prepend the user message before the retrieved context, so the cache prefix changes every turn. The fix in all three cases is structural: stabilise the front, volatilise the back.

### 6.4 RAG chunking strategies

When retrieval is needed, the chunking strategy controls both retrieval quality and token cost. There is no single right answer, but there is a clear hierarchy of strategies by cost-effectiveness.

| Strategy | Tokens per chunk | Strengths | Weaknesses |
|---|---|---|---|
| Fixed-size token window | 200–500 | Simple, predictable, cacheable | Cuts across semantic boundaries |
| Recursive character split | 200–1,000 | Respects paragraph/code boundaries | Tuning-sensitive; defaults often wrong |
| Sentence-aware split | 1–3 sentences | Good for prose | Poor for code |
| Semantic chunking (embedding-based) | Variable | Respects topic boundaries | Higher compute cost; non-deterministic |
| Late chunking (embed whole doc, chunk late) | Variable | Preserves cross-chunk context | Newer; fewer libraries |
| Hierarchical / parent-doc | Variable | Small chunk for retrieval, big chunk for context | More complex pipeline |

For most teams the right default is **recursive character split with a token-aware length function** (LangChain's `RecursiveCharacterTextSplitter` with `length_function=tiktoken`, or `chonkie`'s `TokenChunker`). Move to semantic chunking only when retrieval quality is the bottleneck, not token cost. Use the open-source tools in section 13.3 to experiment.

### 6.5 Sliding window and summarisation

For long-running sessions, two patterns help manage the growing history:

- **Sliding window** with explicit summarisation: keep the last N turns verbatim, replace older turns with a single "Prior context" summary. The summary is one call (paid once) and saves the cost of re-billing the original turns on every subsequent call. Implement manually or use LangChain's `ConversationSummaryBufferMemory`.
- **Compaction at 70%**: when the conversation reaches 70% of the context window, run a compaction pass — the model summarises the history into a stable block, which then becomes part of the cache-stable prefix. Copilot exposes this as `/compact`; most agent frameworks have an equivalent.

Both patterns trade a one-time output cost for an ongoing input-cost saving. They pay off when the session is expected to run more than ~20 turns; for short sessions they are net-negative.

### 6.6 Context discipline anti-patterns

A short list of patterns to refuse in code review:

- **`#codebase` as the default.** Almost always a habit, not a necessity.
- **Re-attaching the same file every turn.** Once it's in the window, leave it; if it's not needed, drop it explicitly.
- **Whole-repo RAG retrieval.** Cap retrieved chunks at 5–10 per query; more is almost always noise that costs tokens.
- **Long system prompts that change often.** If your system prompt is 2,000 tokens and you edit it weekly, you are paying full input rate on every call and never hitting the cache.
- **Mixing instructions and retrieved context.** Keep instructions in the cache-stable prefix; keep retrieved context in the volatile tail.

---

## 7. Prompt engineering patterns

Prompt engineering is the discipline of **what you ask and how you phrase it**. It is the layer most teams focus on, partly because it is the most visible and partly because the tooling (prompt management, A/B testing, evaluation) has matured fastest. The savings per pattern are smaller than context engineering (5–20% per pattern, not 30–50%), but the patterns compound and they are cheap to adopt.

### 7.1 Prompt compression

The highest-ROI prompt pattern is also the simplest: **remove the words that don't carry information.** Politeness ("Hey, could you please help me…"), hedging ("I think it might have some issues with…"), and preamble ("Let me explain the context first…") all bill tokens without changing the output. A representative example:

- Before (40 tokens): *"Hey, could you please help me refactor this function? I think it might have some issues with how it handles authentication, and I'd love to make it more efficient if possible."*
- After (10 tokens): `Refactor function. Fix auth handling. Make efficient.`

Same outcome, 75% fewer tokens. The pattern is mechanical: drop the politeness, drop the hedging, drop the preamble, keep only the verbs and the nouns. This is uncomfortable for the first week and automatic after the second.

### 7.2 Structured phrasing beats prose

Prose is token-expensive because it relies on word order and connectors that the model has to parse. Structured phrasing — bullet lists, key:value pairs, code blocks, mini-YAML — is denser and parses more reliably. The same task described both ways:

Before (55 tokens, prose):
> *"I need you to write a new API endpoint for creating users. It should be a POST request to /api/users. It needs to validate that the name and email are present and that the email is in a valid format. If validation fails, return a 400 with the errors. If it succeeds, return a 201 with the created user."*

After (35 tokens, structured):
```
POST /api/users
Validate:
  - name: string, required
  - email: string, required, valid format
400 on validation fail (include errors)
201 on success (return created user)
```

Same task, ~36% fewer tokens, *and* the model is less likely to drift on the contract. Structured phrasing is the prompt equivalent of typed function signatures: it constrains both cost and output.

### 7.3 Output caps in the instruction tail

Output tokens are billed at 4–8× the input rate, so a one-line instruction that constrains output is the highest-leverage sentence in any prompt. Put it at the **end** of your message, where the model treats it as the final instruction before generation.

- *"Add the endpoint. Code only, no explanation."* — caps output at the code block.
- *"Reply with the function signature and a one-line docstring. No implementation."* — caps output at the signature.
- *"List the affected files. One file per line, no commentary."* — caps output at a flat list.

A 1,800-token "explain then implement" response becomes a 500-token "code only" response — a 40–80% output-cost cut from a single sentence. The pattern is so reliable that teams that adopt it as a written convention typically cut their per-task output spend in half within a month.

### 7.4 Write rules, not steps

A common anti-pattern is to write the model's process as numbered steps ("First, read the file. Then, identify the imports. Then, list the dependencies…"). Step-by-step instructions inflate the prompt, constrain the model unnecessarily, and produce worse output than rule-based instructions. Rules are shorter, more cacheable, and let the model pick the order.

- Before (60 tokens, steps): *"First, read the file. Then, identify all the imports. Then, list the dependencies that are unused. Then, suggest which ones to remove. Then, write the change."*
- After (15 tokens, rules): *"Identify unused imports. Suggest removals. Write the change."*

The rule form is 4× shorter and produces equivalent-or-better output because the model is free to choose its own order of operations.

### 7.5 Few-shot examples, compressed

When few-shot examples are needed, compress them. A representative example is a 200-token input/output pair; a compressed example (showing only the relevant input slice and the relevant output slice) is 30 tokens. For a 3-shot prompt, that's 510 tokens saved per call, which on a 10-call workflow is 5,100 tokens. The compression pattern:

- Drop everything in the example input that is not relevant to the task.
- Drop everything in the example output that the model would obviously produce.
- Keep only the *boundary conditions* — the part of the input that triggers the part of the output.

### 7.6 Choose the language deliberately

Tokenizers are not language-neutral. English text is almost always the cheapest to tokenize, because the major BPE vocabularies (GPT, Claude, Gemini) were built with English-heavy corpora. Non-English text often costs 1.5–2.5× more tokens per word, with the worst case being agglutinative languages (Turkish, Finnish) and logographic languages (Chinese, Japanese, Korean) on certain tokenizers.

| Language | Approx. tokens / 1000 words | vs. English baseline |
|---|---|---|
| English | ~1,300 | 1.0× |
| Spanish / French / German | ~1,500 | 1.15× |
| Chinese | ~1,800 | 1.4× |
| Japanese | ~2,000 | 1.5× |
| Korean | ~2,200 | 1.7× |
| Russian | ~2,100 | 1.6× |
| Turkish | ~2,700 | 2.1× |

For prompts that will be reused many times, writing the system prompt in English (even if the user-facing output is in another language) is a free 30–50% saving. The Komatsuzaki tokenizer heatmap is the canonical reference; see section 17 for the link.

### 7.7 The role/persona pattern, minimised

The "You are a senior engineer…" persona preamble is a fixture of prompt libraries and is almost always wasted tokens. The model does not need a persona to do engineering work; it needs a task. If a persona is genuinely needed (for tone matching in a writing task, for example), keep it to one line, not a paragraph.

- Before (90 tokens): *"You are a senior software engineer with 15 years of experience in TypeScript, React, and Node.js. You care about clean code, testability, and performance. You always follow SOLID principles. Your task is to…"*
- After (15 tokens): *"Refactor the following function for readability and testability. Code only."*

The persona is implicit in the task. The model performs the same with or without it.

### 7.8 Instruction hierarchy — system, developer, user

Most providers expose a hierarchy of instruction roles: **system** (provider-controlled), **developer** (app-controlled), **user** (end-user-controlled). Tokens placed in the system or developer role are cacheable across users; tokens placed in the user role are not. The implication: any instruction that is constant across your user base should live in the developer role, not the user role, so it caches.

A common mistake is to inject "house style" instructions into every user message. Moving them to the developer role (one-time cost, then cached forever) typically saves 30–50% on instruction tokens for high-volume apps.

---

## 8. Model routing and reasoning depth

Model selection is a 5–8× cost lever, and reasoning depth is a 3–5× output-cost lever. Together they are the second-largest category of savings after context discipline. Both are about **matching capability to task** — using the smallest model and the lowest reasoning effort that produces acceptable output.

### 8.1 The three-tier model hierarchy

Almost every provider now exposes a three-tier hierarchy. The names differ; the price-per-token ratios are remarkably consistent.

| Tier | Examples | Relative price | Best fit |
|---|---|---|---|
| **Lightweight** | GPT-5.4 nano, Claude Haiku, Gemini 3 Flash | 1× | Lookups, simple edits, boilerplate, classification, short replies |
| **Versatile** | GPT-5.4, Claude Sonnet, Gemini 3.1 Pro | 6–10× | Daily-driver coding, multi-step reasoning, agentic loops |
| **Powerful** | GPT-5.5, Claude Opus, Gemini 3.1 Pro Long | 15–25× | Architecture, complex refactors, novel design, hard debugging |

The mistake most teams make is defaulting to the versatile tier (or worse, the powerful tier) for every task. The realistic distribution in a coding workflow is roughly 60% lightweight, 30% versatile, 10% powerful. A team that inverts this — 10% lightweight, 30% versatile, 60% powerful — pays 3–4× what the disciplined team pays for the same work.

### 8.2 Phased routing: plan high, execute low

The most effective routing pattern is **phased**: use the powerful model for planning, then the lightweight or versatile model for execution. A 30-turn workflow that uses Opus for all 30 turns costs ~50 cost units. The same workflow that uses Opus for 2 plan turns, Sonnet for 18 build turns, and Haiku for 10 lookup turns costs ~22.8 units — a 54% saving with no measurable quality loss.

```
Plan   (2 turns, Opus)      → 2 × 1.67 = 3.34
Build  (18 turns, Sonnet)   → 18 × 1.00 = 18.0
Lookup (10 turns, Haiku)    → 10 × 0.15 = 1.5
                                Total   = 22.84
```

Auto Mode (Copilot's automatic tier selector) implements a version of this and is documented to give a ~10% token-multiplier discount on top. If you don't have Auto Mode, the pattern is easy to script: route based on a simple classifier (turn 1 = plan; tool-calling = build; "list", "find", "where" = lookup).

### 8.3 Reasoning effort, right-sized

Reasoning models expose `reasoning_effort`: Low, Medium, High, Max. Each step multiplies the *output* token count, and because output is billed at 4–8× the input rate, the cost compounds aggressively.

| Effort | Output multiplier | When to use |
|---|---|---|
| Low | 1× | Mechanical edits, lookups, boilerplate, simple refactors |
| Medium | 3× | Multi-step refactors, bug diagnosis, design with constraints |
| High | 14× | Architecture, complex debugging, novel design |
| Max | 60× | Reserve for one-off reasoning problems; never the default |

The decomposition pattern is the key to using reasoning effort well: a single High-effort request can usually be broken into 3–5 Medium-effort requests with explicit verification gates between them. The decomposed version produces better output (each step is verifiable) *and* costs less (3 × 3× = 9× output, vs. 1 × 14× = 14× output).

- Before (one shot, ~$5–7): `/effort high "Refactor the entire auth module to support OAuth2 + SAML + WebAuthn"`
- After (decomposed, ~$1.5–2.5):
  1. `/effort medium "Plan the refactor: list the files, the dependencies, the order."`
  2. `/effort low "Implement step 1: add the OAuth2 strategy."` (verify)
  3. `/effort low "Implement step 2: add the SAML strategy."` (verify)
  4. `/effort low "Implement step 3: add the WebAuthn strategy."` (verify)
  5. `/effort medium "Review the three steps for consistency and security."`

### 8.4 Model routing in production

For production apps (not IDE assistants), the routing decision is made by code, not by the developer. The open-source ecosystem offers several ready-made routers:

- **RouteLLM** (lm-sys) — trains a binary classifier on (prompt, weak model OK, strong model needed) labels and routes at inference time.
- **LiteLLM** (BerriAI) — a unified gateway to 100+ models with `token_count()` and per-request budget tracking; can implement routing rules in YAML.
- **Portkey gateway** — production gateway with retries, caching, and guardrails across 1,600+ models.
- **Helicone** — observability-first gateway with A/B testing, caching, and cost dashboards built in.

A typical production routing policy combines a cheap classifier (a 1B-parameter model or a regex) with a budget guard: route to the cheap tier unless the classifier confidence is below threshold, then route to the strong tier; cap the strong-tier calls per user per day to prevent runaway cost.

### 8.5 Workflow modes: Ask, Plan, Agent

Copilot and most agent frameworks expose three workflow modes that correspond to different cost regimes:

- **Ask** — single-turn, no tools, no iteration. Cost ≈ 1× the prompt packet.
- **Plan** — multi-turn, no execution. The model produces a plan; you approve; you execute (manually or with a follow-up Ask). Cost ≈ 2–5× Ask, but bounded.
- **Agent** — multi-turn with tool execution and feedback. Cost ≈ 10–40× Ask, unbounded unless capped.

The rule of thumb: **if you cannot state the acceptance criteria in one sentence, use Ask or Plan first, not Agent.** Agent mode is for genuinely iterative tasks that need feedback loops; everything else is more cheaply handled with Ask or Plan. Most teams over-use Agent mode and pay 10× what they need to.

---

## 9. Agent, tool, and session governance

The last pillar is governance — the institutional patterns that keep the other five pillars from regressing. Without governance, every optimisation decays in a quarter; with it, the gains compound.

### 9.1 Tool and MCP scope discipline

Every enabled tool's schema rides along on every step of every agent turn. A 200-token schema × 30 steps × 50 tools is 300,000 tokens of pure schema overhead. The fix is **per-workspace scoping**:

- Enable Slack only in the workspace where Slack is used.
- Enable Jira only in the project-management workspace.
- Enable the DB tool only in the data workspace; scope to one environment per workspace.
- Disable everything else by default; enable on demand for the task.

A real audit documented in the reference playbook: 188 tools globally enabled (Slack used 8% of the time, Jira 2%, DB spread across 5 environments) → 52 tools per-workspace after scoping → ~13,000 tokens saved per agent task, before any other optimisation.

### 9.2 Subagents as compression boundaries

A subagent is a separate agent call with its own context window. The pattern: instead of having the parent agent read 20 files (20,000 tokens re-billed every turn), spawn a subagent that reads them in isolation and returns a 1,000-token summary. The parent reasons over the 1,000-token summary, not the 20,000 tokens of source.

The cost saving is roughly the ratio of source to summary — a 10× reduction in the parent's context-token cost. The pattern is especially powerful for discovery tasks ("find every place we use `validateToken`"), parallel review tasks ("review for correctness, quality, security, architecture — in parallel"), and research tasks ("read these 50 docs and tell me what's relevant").

### 9.3 AGENTS.md: landmines, not encyclopedias

`AGENTS.md` (or `copilot-instructions.md`) is the file the model reads on every turn. Its purpose is not to document the repo — it is to plant landmines: rules the model cannot infer and would otherwise violate. A common failure mode is to use it as an encyclopedia: "This is a Python project. Tests live in `tests/`. We use PostgreSQL and JWT for auth." All of this is derivable from the code; writing it down costs tokens every turn without changing the model's behavior.

An ETH-Zurich study across 47 projects found that LLM-generated instruction files (the "encyclopedia" style) reduced correctness by 2% *and* increased token cost by 20–23%. The encyclopedia pattern is actively harmful.

The landmine pattern, by contrast, is short and high-signal:

```markdown
# Landmines
- Use uv, not pip. (The CI will reject pip installs.)
- Migrations must run in order; `alembic upgrade head` is forbidden in PRs.
- Do not refactor auth — pending audit Q3. Touching `auth/` blocks the PR.
- Tests run in parallel; do not use module-level state.
```

Four rules, ~60 tokens, each one preventing a class of failure. The encyclopedia pattern would be 1,500 tokens and prevent nothing.

### 9.4 Session lifecycle

The session-lifecycle pattern is mechanical: **one task = one session.** When the task is done, `/clear`. When the context window reaches ~70%, `/compact`. When switching tasks, `/clear` first, then start the new task. The pattern prevents the history-compounding tax (2–5× by turn 30) and keeps each session's per-turn cost flat.

| Signal | Action |
|---|---|
| Task complete | `/clear` |
| Switching to an unrelated task | `/clear` |
| Context window at 70% | `/compact` (or manual summarisation) |
| Context window at 90% | `/clear` and start over (compaction is too late) |
| Long-running task spanning multiple sessions | Use a subagent to preserve the relevant context |

### 9.5 The three-layer budget

Governance at the org level is the three-layer budget:

- **Per-user limit (ULB):** cap each developer's daily/weekly token spend. Copilot exposes this; LiteLLM exposes it for custom apps. Default: 150% of expected average — high enough not to block productive work, low enough to catch runaway scripts.
- **Cost-center budgets:** per-team or per-project budgets with alerts at 80% and hard caps at 100%. Lets teams own their spend.
- **Enterprise cap with 80% alert:** a hard ceiling on total org spend, with an alert at 80% to the finance partner. Prevents the "Copilot bill doubles in a quarter" surprise.

A team that adopts the three-layer budget moves from "30%+ uncontrolled overage" to "10–15% predictable overage" within a month, without any other optimisation. The budget is the lever that makes every other lever observable.

---

## 10. Fifteen scenarios — the context-rot catalog

The fifteen scenarios below are the catalog of recurring failure modes the reference playbooks document. Each one has a *before* (the wasteful pattern), an *after* (the tight pattern), a measurable impact, and a recommendation. They are grouped by category; read them as a checklist when designing a new agent workflow or auditing an existing one.

### 10.1 Context scenarios

#### Scenario 1 — Context bloat from whole-file reads
**Problem:** Developer uses `#codebase` or attaches whole files when only a few lines are relevant.
**Before (22,000 tokens):** `Refactor the authentication flow #codebase`
**After (9,000 tokens):** `Refactor the authentication flow #login.ts #session.ts #validateToken`
**Impact:** 30–50% context-token reduction.
**Recommendation:** Adopt the escalation ladder as a written convention; enforce in code review.

#### Scenario 2 — Whole-repo RAG retrieval without chunk caps
**Problem:** RAG pipeline retrieves 50 chunks per query "for completeness".
**Before:** 50 chunks × 500 tokens = 25,000 retrieved tokens per turn.
**After:** Top-5 chunks × 500 tokens = 2,500 retrieved tokens per turn.
**Impact:** 90% retrieval-token reduction; usually improves retrieval quality (less noise).
**Recommendation:** Cap retrieved chunks at 5–10 per query. Tune with `ragas` faithfulness/relevance scores.

### 10.2 Prompt scenarios

#### Scenario 3 — Prompt compaction
**Problem:** Prompts are polite, hedging, and preamble-heavy.
**Before (40 tokens):** *"Hey, could you please help me refactor this function? I think it might have some issues with how it handles authentication, and I'd love to make it more efficient if possible."*
**After (10 tokens):** `Refactor function. Fix auth handling. Make efficient.`
**Impact:** ~75% fewer prompt tokens for the same task.
**Recommendation:** Adopt "no politeness, no hedging, no preamble" as a team rule.

#### Scenario 4 — Structured phrasing beats prose
**Problem:** API contracts described in prose paragraphs.
**Before (55 tokens, prose):** A paragraph describing POST /api/users, validation rules, response codes.
**After (35 tokens, structured):** A 5-line YAML-like block with the same contract.
**Impact:** ~36% fewer tokens, same task; reduced model drift on the contract.
**Recommendation:** Use structured phrasing for any contract, schema, or list of constraints.

### 10.3 Output scenarios

#### Scenario 5 — Output control, the highest-ROI instruction
**Problem:** Model produces "explain then implement" output when only the implementation is needed.
**Before (1,800 tokens output):** `Explain how to add the endpoint, then implement it with full commentary.`
**After (500 tokens output):** `Add the endpoint. Code only, no explanation.`
**Impact:** 40–80% output-cost cut from a single sentence.
**Recommendation:** Add output caps to every prompt template by default. Output is billed 4–8× input.

#### Scenario 6 — Reasoning-depth control
**Problem:** Default reasoning effort is "High" for tasks that need "Low".
**Before (12,000 output tokens):** `/effort high "Refactor the entire auth module to support OAuth2 + SAML + WebAuthn"`
**After (2,500 output tokens):** Decomposed into 5 steps with effort Medium / Low / Low / Low / Medium.
**Impact:** 50–80% output-token reduction.
**Recommendation:** Default to Low or Medium; reserve High for tasks with explicit verification gates.

### 10.4 Model routing scenarios

#### Scenario 7 — Intelligent model routing
**Problem:** Single model used for all tasks regardless of complexity.
**Before (50 cost units, all Opus):** 30 turns × 1.67 = 50.
**After (23 cost units, mixed):** 2 Opus + 18 Sonnet + 10 Haiku = 22.84.
**Impact:** 25–55% saving vs. single-model strategy.
**Recommendation:** Use Auto Mode where available, or implement phased routing in code.

#### Scenario 8 — Workflow modes (Ask, Plan, Agent)
**Problem:** Agent mode used for a single-shot question.
**Before (50,000 tokens, agent loop):** A 30-step agent run for a question that needs one answer.
**After (2,000 tokens, Ask mode):** A single-turn Ask with the same question.
**Impact:** 5–25× swing between modes.
**Recommendation:** Match the mode to the task. If you can't state acceptance criteria in one sentence, use Plan first.

### 10.5 Caching scenarios

#### Scenario 9 — Instruction engineering and the cache discount
**Problem:** Custom instructions edited mid-session, invalidating cache.
**Before (100 rel. units):** Mid-session instruction edits × full input rate on every turn.
**After (12 rel. units):** Stable instructions × cached rate (10% of input).
**Impact:** 70–80% input-cost cut on cache hits.
**Recommendation:** Hold the instruction prefix byte-identical for the session. Use path-scoped instructions for volatile rules.

#### Scenario 10 — Path-scoped instructions
**Problem:** 1,500-line `copilot-instructions.md` loaded on every turn for every file.
**Before:** 3,000 tokens billed every turn regardless of file.
**After:** Path-scoped `*.instructions.md` with `applyTo` frontmatter; loaded only when relevant files are in context.
**Impact:** 60–90% instruction-token reduction on tasks touching specific paths.
**Recommendation:** Use path-scoped instructions for domain-specific rules (API, DB, tests).

### 10.6 Session scenarios

#### Scenario 11 — Session lifecycle & compaction
**Problem:** One 40-turn session spanning four unrelated tasks.
**Before (50,000 tokens):** History compounds across tasks; turn 30 costs 5× turn 1.
**After (12,000 tokens):** Four 10-turn sessions with `/clear` between tasks.
**Impact:** 30–50% reduction on long workflows.
**Recommendation:** One task = one session. `/clear` between unrelated tasks. `/compact` at 70% window.

### 10.7 Tools & agents scenarios

#### Scenario 12 — MCP schema tax
**Problem:** Every enabled tool's schema rides along on every agent step.
**Before (188 tools):** 188 × 200 tokens × 30 steps = ~1.1M schema tokens per agent run.
**After (52 tools, per-workspace):** 52 × 200 × 30 = ~312K tokens.
**Impact:** −72% tool catalog in a real audit; ~13K tokens saved per task.
**Recommendation:** Per-workspace tool scoping. Disable by default; enable on demand.

#### Scenario 13 — Subagents as compression boundaries
**Problem:** Parent agent reads 20 files in its own context; re-bills every turn.
**Before (84,000 tokens):** 20 files × 4,200 tokens × 1 turn = 84K (re-billed each subsequent turn).
**After (8,500 tokens):** Subagent reads in isolation; parent receives 1K summary.
**Impact:** ~10× input-token reduction for the parent's context.
**Recommendation:** Delegate discovery and parallel review to subagents.

### 10.8 Governance scenarios

#### Scenario 14 — AGENTS.md landmines vs. noise
**Problem:** LLM-generated AGENTS.md filled with derivable facts.
**Before (100 rel. units):** 1,500-token encyclopedia; correctness −2%, token cost +20–23% (ETH-Zurich study).
**After (78 rel. units):** 60-token landmine file; correctness unchanged, cost down.
**Impact:** 20–23% token cost removed; correctness preserved.
**Recommendation:** Write landmines (rules that cannot be inferred), not encyclopedias.

#### Scenario 15 — Governance: the three-layer budget
**Problem:** No per-user or per-team budgets; runaway scripts go unnoticed.
**Before (30% overage):** Uncontrolled; CFO surprises each quarter.
**After (12% overage):** ULB 150% of average; cost-center budgets; enterprise cap with 80% alert.
**Impact:** 30%+ overage → predictable 10–15% overage.
**Recommendation:** Adopt the three-layer budget as a Day-0 setup, not an afterthought.

---

## 11. Eleven levers, deep dive

The eleven levers below are the deep-dive counterparts to the scenarios above. Each one is a practice a team can adopt in a sprint; together, they are the playbook. Each entry has a summary, two measurable stats, and an extended discussion with the patterns, anti-patterns, and trade-offs you'll need when implementing it.

### Lever 1 — Prompt compression

**Summary:** Remove the words that don't carry information. The simplest and highest-ROI lever; the only one that costs zero effort to adopt.

**Stats:** 75% prompt-token reduction on conversational prompts; 30–50% on already-terse prompts.

**Extended:**

Three levels of compression:
1. **Surface compression** — drop politeness, hedging, preamble. Mechanical; immediate 30–50% saving.
2. **Structural compression** — convert prose to bullets / code blocks / mini-YAML. 15–25% additional saving.
3. **Semantic compression** — drop redundant instructions, fold overlapping constraints. 10–20% further saving; requires careful review.

The anti-pattern is over-compression: instructions so terse that the model has to infer intent. The rule is to compress up to the point where ambiguity would creep in, then stop. A useful test: read the prompt aloud; if a competent colleague would understand the task with no further context, the compression is sufficient.

### Lever 2 — Choose the right language

**Summary:** English is almost always the cheapest tokenizer. Write system prompts in English even if user-facing output is in another language.

**Stats:** Up to 2× cost in worst-case tokenizers (e.g., agglutinative languages on Anthropic); 30–50% saving on reusable system prompts.

**Extended:**

The tokenizer efficiency varies by provider. The Komatsuzaki heatmap (6 models × 9 languages) shows English cheapest in most cases; Gemini and Qwen most efficient for non-English; Anthropic and Kimi most expensive. For a global team, the right answer is usually: system prompt in English, user-facing interaction in the user's language. The model translates internally at no extra cost beyond the input-token difference.

### Lever 3 — Manage your context

**Summary:** Split instructions into three layers; cache the stable prefix; cap retrieved chunks.

**Stats:** 30–50% context-token reduction; 70–80% input-cost cut on cache hits.

**Extended:**

Three layers of rules:
- Global (~20 rules, ~500 tokens, stable across months)
- Repo (~50 rules, ~1,500 tokens, stable across weeks)
- Path-scoped (~10 rules per file, ~300 tokens, loaded only when relevant)

The cache-stable prefix is the key. The front of the prompt packet — system prompt, custom instructions, tool schemas — should not change within a session. Volatile content (your message, fresh retrieved context) goes at the *end*.

VS Code context mentions have an escalation ladder: `#selection → #file:Lx-Ly → #file → #codebase`. Treat `#codebase` as a deliberate decision, not a default.

### Lever 4 — Output control

**Summary:** One short rule, paid once — short replies forever.

**Stats:** 40–80% output-cost cut; output is billed 4–8× input, so the impact on total cost is significant.

**Extended:**

Output caps are the highest-leverage sentence in any prompt. Put them at the **end** of the message:

| Cap pattern | Tokens saved | Trade-off |
|---|---|---|
| "Code only, no explanation." | ~70% | No educational value |
| "Reply with the function signature and a one-line docstring." | ~85% | No implementation |
| "List the affected files. One file per line." | ~95% | No code at all |
| "Maximum 3 bullet points." | ~60% | Reduced nuance |

The trade-off is real: caps reduce educational output and explanation. For tasks where the developer wants to learn from the response, omit the cap; for tasks where they want the artifact, the cap is a 40–80% saving.

### Lever 5 — Choose the right mode

**Summary:** Ask, Plan, Agent — match the mode, then divide and conquer.

**Stats:** 5–25× swing between modes; agent mode is 10–40× the cost of Ask.

**Extended:**

Mode budget at a glance:
- Ask: 1× the prompt packet; for single-shot answers.
- Plan: 2–5× Ask; for multi-step work where you want to review before execution.
- Agent: 10–40× Ask; for genuinely iterative tasks with feedback loops.

The most expensive mistake is jumping to Agent for a task that should be Ask. The rule: if you cannot state the acceptance criteria in one sentence, use Ask or Plan first.

### Lever 6 — Custom agents, skills, sub-agents

**Summary:** Pick the right container for the work.

**Stats:** ~10× input-token reduction for subagent delegation; 30–50% for skill-based lazy loading.

**Extended:**

Three containers, three cost profiles:
- **Custom agents** — pre-configured instructions, tools, and modes for a recurring task. Pay the setup once; reuse forever.
- **Skills** — lazy-loaded context. A skill is a markdown file with `applyTo`-style frontmatter; it's loaded only when invoked. Useful for domain-specific patterns (API conventions, test patterns, migration rules).
- **Sub-agents** — a second context window. The subagent does work in isolation and returns a summary. Useful for discovery, parallel review, and research.

Sub-agents are the compression boundary: parent agent reasons over a 1K summary, not the 20K of source. The 10× saving comes from the ratio of source to summary.

### Lever 7 — Choose the right model

**Summary:** Mix models. Plan with the big one, build with the small one.

**Stats:** 25–55% saving vs. single-model strategy; 5–8× price spread between tiers.

**Extended:**

Rough model-selection guide:
- Lightweight (Haiku, nano, Flash): lookups, simple edits, classification, boilerplate, short replies. 60% of a coding workflow.
- Versatile (Sonnet, GPT-5.4, Pro): daily-driver coding, multi-step reasoning, agentic loops. 30%.
- Powerful (Opus, GPT-5.5, Pro Long): architecture, complex refactors, novel design, hard debugging. 10%.

The two-stage workflow: plan with the powerful model (1–2 turns), build with the versatile or lightweight model (10–20 turns), look up with the lightweight model (5–10 turns). Across a 30-turn session, this is 50 cost units vs. 22.8 cost units — 54% saving with no measurable quality loss.

### Lever 8 — Manage your AGENTS file

**Summary:** Landmines, not encyclopedias.

**Stats:** 20–23% token cost removed by deleting derivable content; correctness preserved.

**Extended:**

Keep the landmines — delete the noise. The landmine pattern is short, high-signal, and prevents failure classes the model would otherwise hit. The encyclopedia pattern is long, low-signal, and costs tokens every turn without changing behavior.

A simple test: would a competent engineer reading the repo's code infer this rule in 30 seconds? If yes, it's noise. If no, it's a landmine.

### Lever 9 — Clean up your tools

**Summary:** Every tool's schema rides along on every step.

**Stats:** −72% tool catalog in a real audit; ~13K tokens saved per task.

**Extended:**

Four simple ways to control the agent loop:
1. **Per-workspace scoping** — enable tools only where they're used.
2. **Schema cost grows with steps** — every step multiplies the schema tax. Cap steps for tool-heavy tasks.
3. **Audit the catalog** — most teams have 2–5× more tools enabled than they use. Audit quarterly.
4. **Disable by default; enable on demand** — make enabling a deliberate decision, not a default.

A real audit (green box): 188 tools globally → 52 tools per-workspace → ~13K tokens saved per agent task, before any other optimisation.

### Lever 10 — Usage limits & overages

**Summary:** Cap the bill before the bill caps you.

**Stats:** 30%+ uncontrolled overage → 10–15% predictable overage.

**Extended:**

The three-layer budget: per-user (150% of expected average), cost-center (80% alert, 100% hard cap), enterprise (80% alert, hard ceiling). Adopted as Day-0 setup, this is the lever that makes every other lever observable.

### Lever 11 — Power-user guidance

**Summary:** Advanced optimization patterns for teams running the fundamentals.

**Stats:** Compounding 5–10% additional savings on top of the baseline 37–44%.

**Extended:**

For teams who have adopted the first ten levers and want to go further:

- **Parallel review subagents** — fan out correctness / quality / security / architecture reviews to four subagents, each with a focused context. 4× the review coverage, 0.3× the parent's context cost.
- **Cache-aware prompt assembly** — order your prompt packet so the cache-stable prefix is byte-identical across calls, and the volatile content (user message, fresh retrieved context) is at the end.
- **Compaction over reset** — when the context window hits 70%, compact rather than clear; the compacted summary becomes part of the cache-stable prefix and caches going forward.
- **Speculative decoding** (production serving only) — for self-hosted inference, EAGLE-3 / Lookahead Decoding can deliver 2–4× throughput without changing the model. See section 13.7 for the open-source implementations.
- **Quantized serving** — for self-hosted inference, AWQ INT4 + Marlin kernels give 3–4× memory and throughput wins with minimal accuracy loss. See section 13.5.

---

## 12. Evaluation, observability, and logs

Optimisation without measurement is guesswork. The observability layer is what turns the eleven levers from "good advice" into a system you can run, regress-test, and improve. This section covers the metrics to track, the tooling to track them, and the patterns for using logs to drive optimisation decisions.

### 12.1 The four metrics that matter

| Metric | What it measures | Why it matters |
|---|---|---|
| **Tokens per task** | Input + output + cached tokens for a unit of work | The denominator of cost; what you actually want to drive down |
| **Cost per task** | Tokens × per-token price, summed across the task | The invoice number; the metric finance cares about |
| **Latency per task** | Wall-clock time from request to response | UX metric; often correlated with token count |
| **Quality per task** | Correctness / faithfulness / user satisfaction | The denominator of value; do not let it drop while cost drops |

The first three are mechanical to capture: every API response includes a `usage` object with `prompt_tokens`, `completion_tokens`, `cached_tokens`, and most gateways (LiteLLM, Helicone, Langfuse) parse and aggregate them automatically. The fourth is harder and is where most teams under-invest. The patterns below cover both.

### 12.2 Log schema — what to capture per call

Every LLM call should be logged with at minimum the following fields. The schema is OpenTelemetry-compatible and matches what Langfuse, Helicone, and OpenLIT emit natively.

```json
{
  "trace_id": "uuid",
  "span_id": "uuid",
  "parent_span_id": "uuid | null",
  "timestamp": "ISO-8601",
  "user_id": "string",
  "session_id": "string",
  "model": "claude-sonnet-4.5",
  "provider": "anthropic",
  "tier": "versatile",
  "mode": "ask | plan | agent",
  "reasoning_effort": "low | medium | high | max",
  "tools_enabled": ["slack", "jira", "db"],
  "prompt": {
    "system_tokens": 350,
    "instructions_tokens": 1200,
    "tools_schema_tokens": 1800,
    "history_tokens": 4500,
    "retrieved_tokens": 2400,
    "user_message_tokens": 180
  },
  "response": {
    "output_tokens": 850,
    "reasoning_tokens": 2100,
    "cached_tokens": 4900,
    "finish_reason": "stop | tool_call | length"
  },
  "cost_usd": 0.0142,
  "latency_ms": 1340
}
```

The schema looks heavy but the value compounds: with this captured per call, you can answer "which team is over-spending?", "which prompt template has the worst tokens-per-task?", "what fraction of input tokens hit cache?", and "is reasoning effort driving cost without driving quality?" — all from logs you already have.

### 12.3 Dashboards — what to display

The minimum dashboard for a team running token optimisation has four panels:

1. **Daily cost by tier** — stacked bar of lightweight / versatile / powerful spend per day. Watch for the powerful tier growing; that's where runaway cost lives.
2. **Cache hit rate** — line chart of `cached_tokens / (cached_tokens + input_tokens)`. Target: 60%+ on stable workloads. Below 40% means the cache-stable prefix is breaking.
3. **Tokens per task** — histogram by task type. Outliers are tasks where the model is over-attached or over-reasoning.
4. **Quality regression** — plot of your quality metric (pass rate on evals, user thumbs-up, LLM-judge score) over time. Must not trend down as cost trends down.

The first three are mechanical with Langfuse, Helicone, or OpenLIT. The fourth requires an eval harness (section 12.5).

### 12.4 Cost attribution — who spent what

Cost attribution is the unglamorous prerequisite for org-level governance. Without it, the three-layer budget (section 9.5) cannot work. The pattern:

- **Per-user attribution** — every call carries a `user_id`; aggregate by user. Maps to the per-user limit (ULB).
- **Per-team / cost-center attribution** — every call carries a `team_id` derived from the user's team or the project they're working on. Maps to cost-center budgets.
- **Per-task-type attribution** — every call carries a `task_type` (e.g., `code-review`, `refactor`, `lookup`). Tells you which workflows are expensive and worth optimising first.

Most gateways support this via custom headers or metadata. LiteLLM exposes `metadata={"user_id": ..., "team_id": ..., "task_type": ...}` per call; Helicone and Langfuse have equivalent mechanisms. The data flows into the same observability dashboards, broken down by the dimensions you care about.

### 12.5 Eval harnesses — quality regression testing

Cost optimisation without quality tracking is dangerous: you can cut tokens by degrading output and not notice for a month. The eval harness is the safety net. Three open-source options cover most team needs:

- **promptfoo** — declarative YAML config; test prompts across models with deterministic and LLM-graded assertions. Best for prompt A/B and regression testing.
- **ragas** — RAG-specific metrics (faithfulness, answer relevancy, context precision). Best for chunking / retrieval quality.
- **DSPy** — programming-not-prompting framework with auto-optimizers (BootstrapFewShot, MIPRO) that can reduce prompt token count while preserving accuracy.

The pattern: capture a golden set of ~50–200 production prompts (with their expected outputs), run them through the eval harness on every prompt change, and alert if quality drops more than 2%. Most teams set this up in a week and it pays for itself the first time it catches a regression.

### 12.6 LLM-as-judge for quality

For tasks where ground truth is expensive to produce, use an LLM as a judge: a stronger model scores the output of a weaker model on a rubric. The pattern:

```
You are a code reviewer. Score the following diff on a 1-5 scale for:
- Correctness (does it do what the task asked?)
- Readability (would you accept it in PR review?)
- Safety (any obvious vulnerabilities?)

Diff: <diff>
Task: <task>

Output JSON: {"correctness": N, "readability": N, "safety": N, "notes": "..."}
```

LLM-as-judge scores correlate with human scores at r=0.7–0.85 on most coding and writing tasks. They are cheap (one cheap-model call per judged output), fast (parallelisable), and consistent (same rubric every time). The main failure mode is the judge agreeing with the generator's mistakes; mitigate by using a different model family for the judge than for the generator.

### 12.7 A/B testing prompts

Once you have an eval harness, A/B testing prompts is mechanical: pick the metric (tokens per task, cost per task, quality), select a sample (production traffic or golden set), run both prompts, compare. Langfuse, Helicone, and PromptLayer all support prompt A/B out of the box; for custom setups, the pattern is a 50/50 routing rule with metric aggregation per arm.

The mistake most teams make is A/B testing too many things at once. Test one variable at a time: the prompt template, the model, the reasoning effort, the chunking strategy. Multivariate testing is possible but rarely worth the complexity for prompt optimisation.

### 12.8 Observability tooling summary

| Tool | Category | Strengths | Self-hostable |
|---|---|---|---|
| **Langfuse** | Observability + prompt mgmt | Per-trace token usage, cost dashboards, prompt versioning, A/B | Yes (MIT) |
| **Helicone** | Observability gateway | Caching, rate limiting, cost dashboards, A/B | Yes (Apache-2.0) |
| **OpenLIT** | OTel-native observability | Token usage spans joined with app traces | Yes (Apache-2.0) |
| **Lunary** | Analytics + evals | Self-hostable analytics, prompt management | Yes (SDKs OSS) |
| **TruLens** | Eval + tracking | LLM app / agent eval; quality + cost in one place | Yes (MIT) |
| **LangSmith** | LangChain's observability | Best integration with LangChain pipelines | No (SaaS) |
| **promptfoo** | Eval / red-teaming | Declarative config; deterministic + LLM-graded assertions | Yes (MIT) |
| **ragas** | RAG evaluation | Faithfulness, answer relevancy, context precision | Yes (Apache-2.0) |

For most teams the right starting stack is **Langfuse (or Helicone) for observability** + **promptfoo for prompt regression** + **ragas for RAG quality**. All three are open-source, self-hostable, and cover 90% of the eval/observability surface.

---

## 13. Open-source ecosystem — 50+ repos, categorized

The open-source ecosystem for token optimisation has matured rapidly. The catalogue below is grouped by category; within each category the canonical tool is listed first, alternatives second. Star counts are point-in-time (2026-09-20) and will drift up.

### 13.1 Tokenizers (BPE / Unigram / model-specific)

| Name | Stars | License | What it does |
|---|---:|---|---|
| [openai/tiktoken](https://github.com/openai/tiktoken) | 19,288 | MIT | Reference BPE tokenizer for OpenAI models (`cl100k_base`, `o200k_base`). Foundation of most token-counting libraries. |
| [google/sentencepiece](https://github.com/google/sentencepiece) | 12,091 | Apache-2.0 | Unsupervised BPE/Unigram tokenizer used by Llama, T5, Gemma. |
| [huggingface/tokenizers](https://github.com/huggingface/tokenizers) | 11,050 | Apache-2.0 | Fast Rust tokenizers (BPE/WordPiece/Unigram) with HFHub integration. |
| [huggingface/transformers](https://github.com/huggingface/transformers) | 166,437 | Apache-2.0 | Umbrella library; ships `AutoTokenizer` for every open model. |
| [dqbd/tiktoken](https://github.com/dqbd/tiktoken) | 1,074 | MIT | JS/WASM port of tiktoken for browsers and Node. |
| [niieani/gpt-tokenizer](https://github.com/niieani/gpt-tokenizer) | 846 | MIT | Pure-JS BPE encoder/decoder for GPT-2/3.5/4/o200k. No WASM. |
| [xenova/transformers.js](https://github.com/xenova/transformers.js) | 16,304 | Apache-2.0 | Runs HF tokenizers + models in-browser via ONNX. |
| [anthropics/anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python) | 3,908 | MIT | Official Anthropic SDK; `client.count_tokens` for Claude budgeting. |
| [js-tiktoken (npm)](https://www.npmjs.com/package/js-tiktoken) | n/a | MIT | Pure-JS tiktoken build for Node/edge runtimes. |
| [@anthropic-ai/tokenizer (npm)](https://www.npmjs.com/package/@anthropic-ai/tokenizer) | n/a | MIT | Official Anthropic tokenizer for Claude. |

**Picks:** Python → `tiktoken` + HF `tokenizers`. JS browser/edge → `niieani/gpt-tokenizer` (no WASM) or `dqbd/tiktoken` (WASM, faster). In-browser ML → `transformers.js`.

### 13.2 Token counting & context budgeting

| Name | Stars | License | What it does |
|---|---:|---|---|
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 59,212 | MIT | Unified gateway to 100+ LLMs with `token_count()`, per-request cost tracking, budgets. |
| [AgentOps-AI/tokencost](https://github.com/AgentOps-AI/tokencost) | 2,008 | MIT | Tiny library mapping every model's per-1K-token prices; 2-line cost calculation. |
| [hegelai/prompttools](https://github.com/hegelai/prompttools) | 3,055 | Apache-2.0 | Test prompts AND token usage/cost across providers in one matrix experiment. |
| [tokenmeter (npm)](https://www.npmjs.com/package/tokenmeter) | n/a | MIT | Drop-in metering for token/cost analytics in Node apps. |

**Picks:** `tokencost` for prices, `litellm` for the gateway, `prompttools` for cross-provider experiments.

### 13.3 Context-window management / RAG / chunking

| Name | Stars | License | What it does |
|---|---:|---|---|
| [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | 146,714 | MIT | `RecursiveCharacterTextSplitter`, `TokenTextSplitter`, `length_function=tiktoken`. Default chunking/counting stack. |
| [run-llama/llama_index](https://github.com/run-llama/llama_index) | 52,244 | MIT | Token-aware chunkers (sentence, semantic, hierarchical); context-window abstractions. |
| [deepset-ai/haystack](https://github.com/deepset-ai/haystack) | 26,561 | Apache-2.0 | Production RAG orchestration with `PreProcessor` chunking and pipeline components. |
| [feyninc/chonkie](https://github.com/feyninc/chonkie) | 4,760 | MIT | Lightweight chunker (semantic / sentence / token / late-chunking); fast drop-in for LangChain. |
| [aurelio-labs/semantic-chunkers](https://github.com/aurelio-labs/semantic-chunkers) | 259 | MIT | Clean semantic chunking implementations (UPRP, semantic). |
| [isaacus-dev/semchunk](https://github.com/isaacus-dev/semchunk) | 668 | — | Minimal dependency-free semantic chunker that respects a token budget. |
| [benbrandt/text-splitter](https://github.com/benbrandt/text-splitter) | 631 | MIT | Rust-powered semantic chunking with custom length functions. |
| [neuml/txtai](https://github.com/neuml/txtai) | 12,964 | Apache-2.0 | All-in-one semantic search + RAG + embeddings framework. |
| [chroma-core/chroma](https://github.com/chroma-core/chroma) | 29,336 | Apache-2.0 | Open-source vector database for RAG. |
| [FlowiseAI/Flowise](https://github.com/FlowiseAI/Flowise) | 55,466 | Apache-2.0 | Visual no-code builder for LLM/RAG pipelines. |

**Picks:** Default → `langchain` RecursiveCharacterTextSplitter with `length_function=tiktoken`. Production → benchmark `chonkie` and `semantic-chunkers`. Measure with `ragas` (13.6).

### 13.4 Prompt-engineering frameworks / optimizers

| Name | Stars | License | What it does |
|---|---:|---|---|
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 25,302 | MIT | Test prompts, agents, RAG with deterministic + LLM-graded assertions across models. |
| [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | 38,154 | MIT | Programming-not-prompting; `BootstrapFewShot`, `MIPRO` auto-optimize prompts to fewer / more effective tokens. |
| [microsoft/promptflow](https://github.com/microsoft/promptflow) | 11,245 | MIT | Microsoft's LLM app authoring/eval framework with prompt orchestration. |
| [hegelai/prompttools](https://github.com/hegelai/prompttools) | 3,055 | Apache-2.0 | Cross-provider prompt + token usage / cost experiments. |
| [microsoft/EvoPrompt](https://github.com/microsoft/EvoPrompt) | 52 | MIT | Evolution-based automatic prompt optimization (genetic + DE variants). |
| [vaughanlove/PromptBreeder](https://github.com/vaughanlove/PromptBreeder) | 185 | MIT | DeepMind's PromptBreeder in LangChain: evolutionary self-improvement of prompts. |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 34,845 | MIT | Prompt management (versioning, A/B) + observability. |
| [APE (paper)](https://arxiv.org/abs/2211.01910) | n/a | — | Automatic Prompt Engineer; foundational APO work. |
| [OPRO (paper)](https://arxiv.org/abs/2309.03409) | n/a | — | Optimization by PROmpting; LLMs as prompt optimizers. |

**Picks:** `promptfoo` for regression testing; `dspy` for auto-optimization; `langfuse` for prompt management.

### 13.5 Prompt caching / KV-cache / inference optimization

| Name | Stars | License | What it does |
|---|---:|---|---|
| [vllm-project/vllm](https://github.com/vllm-project/vllm) | 92,221 | Apache-2.0 | High-throughput serving; invented PagedAttention for KV-cache management + continuous batching. |
| [InternLM/lmdeploy](https://github.com/InternLM/lmdeploy) | 8,082 | Apache-2.0 | Compress + serve LLMs with W4A16, KV-cache quantization, TurboMind engine. |
| [huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference) | 10,885 | Apache-2.0 | HF's production TGI server with continuous batching + paged attention. |
| [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | 14,677 | Apache-2.0 | NVIDIA's heavily optimized inference engine (FP8/INT4) with KV-cache reuse. |
| [microsoft/DeepSpeed](https://github.com/microsoft/DeepSpeed) | 43,145 | Apache-2.0 | DeepSpeed-Inference + FastGen: KV-cache management, fused kernels, dynamic batching. |
| [lm-sys/FastChat](https://github.com/lm-sys/FastChat) | 39,540 | Apache-2.0 | Open training/serving/eval platform (Vicuna); vLLM originated here. |
| [mit-han-lab/streaming-llm](https://github.com/mit-han-lab/streaming-llm) | 7,266 | MIT | Attention sinks make KV-cache reusable across infinite context. |
| [mit-han-lab/llm-awq](https://github.com/mit-han-lab/llm-awq) | 3,636 | MIT | AWQ INT4 activation-aware weight quantization; 3–4× memory/throughput. |
| [mit-han-lab/smoothquant](https://github.com/mit-han-lab/smoothquant) | 1,686 | MIT | PTQ that smooths activation outliers; enables INT8 LLM inference. |
| [mit-han-lab/qserve](https://github.com/mit-han-lab/qserve) | 861 | Apache-2.0 | W4A8KV4 co-design (MLSys'25); efficient serving of quantized LLMs. |
| [IST-DASLab/marlin](https://github.com/IST-DASLab/marlin) | 1,149 | Apache-2.0 | Near-ideal FP16×INT4 GEMM kernel; powers fast INT4 in vLLM/TGI. |

**Picks:** `vllm` for most workloads. `TensorRT-LLM` for NVIDIA FP8. `llm-awq` + `marlin` for INT4 latency wins. `streaming-llm` for infinite-context streaming.

### 13.6 LLM evaluation & observability

| Name | Stars | License | What it does |
|---|---:|---|---|
| [explodinggradients/ragas](https://github.com/explodinggradients/ragas) | 15,788 | Apache-2.0 | De-facto RAG evaluation: faithfulness, answer relevancy, context precision. |
| [truera/trulens](https://github.com/truera/trulens) | 3,565 | MIT | Eval + tracking for LLM apps/agents; token usage, latency, quality in one place. |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 34,845 | MIT | Per-trace token usage + cost dashboards + prompt versioning + A/B. |
| [helicone/helicone](https://github.com/helicone/helicone) | 6,166 | Apache-2.0 | Observability gateway: caching, rate limiting, cost dashboards, A/B. |
| [openlit/openlit](https://github.com/openlit/openlit) | 2,772 | Apache-2.0 | OpenTelemetry-native observability for LLMs + AI agents. |
| [lunary-ai/lunary-py](https://github.com/lunary-ai/lunary-py) | 21 | — | Self-hostable analytics/eval client; token usage, cost, prompt analytics. |
| [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) | 25,302 | MIT | Deterministic + LLM-graded prompt regression testing. |

**Picks:** `langfuse` or `helicone` for observability + `promptfoo` for prompt regression + `ragas` for RAG quality.

### 13.7 Speculative decoding / multi-token prediction

| Name | Stars | License | What it does |
|---|---:|---|---|
| [SafeAILab/EAGLE](https://github.com/SafeAILab/EAGLE) | 2,537 | Apache-2.0 | EAGLE-1/2/3 speculative decoding; 2–4× speedup by predicting draft tokens from the feature layer. |
| [hao-ai-lab/LookaheadDecoding](https://github.com/hao-ai-lab/LookaheadDecoding) | 1,343 | Apache-2.0 | Lookahead Decoding (ICML'24); parallel multi-token prediction via Jacobi iterations. |
| [hemingkx/Spec-Bench](https://github.com/hemingkx/Spec-Bench) | 413 | Apache-2.0 | Unified benchmark + eval harness for speculative decoding. |
| [Medusa](https://github.com/Foolish-Shallow/Medusa) | — | MIT* | Adds Medusa heads to predict several future tokens per forward pass. |

**Picks:** `EAGLE-3` for production speculative decoding. `Spec-Bench` to benchmark before/after.

### 13.8 Cost optimization / routing / batching

| Name | Stars | License | What it does |
|---|---:|---|---|
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 59,212 | MIT | Unified gateway with budget tracking + routing. |
| [Portkey-AI/gateway](https://github.com/Portkey-AI/gateway) | 13,040 | MIT | Production AI gateway routing to 1600+ models; retries, caching, guardrails. |
| [lm-sys/RouteLLM](https://github.com/lm-sys/RouteLLM) | 5,510 | Apache-2.0 | Routers that send easy queries to weak models, hard queries to strong. |
| [TabbyML/tabby](https://github.com/TabbyML/tabby) | 33,881 | Apache-2.0 | Self-hosted coding assistant; avoids per-token API fees entirely. |
| [helicone/helicone](https://github.com/helicone/helicone) | 6,166 | Apache-2.0 | Caching gateway; cuts redundant token calls. |
| [OpenRouter](https://openrouter.ai) | n/a | SaaS | Paid unified API gateway to 200+ models. |

**Picks:** `litellm` for the gateway, `RouteLLM` for cost-aware routing, `tabby` for fully self-hosted (no per-token fees).

### 13.9 Tokenizer visualization & education

| Name | Stars | License | What it does |
|---|---:|---|---|
| [dqbd/tiktokenizer](https://github.com/dqbd/tiktokenizer) | 1,695 | MIT | The `tiktokenizer.vercel.app` playground; visualize how text splits into tokens. |
| [OpenAI Tokenizer (web)](https://platform.openai.com/tokenizer) | n/a | SaaS | Official OpenAI web playground for GPT-3.5/4 tokenization. |
| [HuggingFace Tokenizers Playground](https://huggingface.co/spaces/Xenova/the-tokenizer-playground) | n/a | SaaS | Compare BPE/WordPiece/Unigram tokenizers in the browser. |

**Picks:** All three are free; use them for onboarding new team members to the concept of a token.

### 13.10 Long-context benchmarks & research

| Name | Stars | License | What it does |
|---|---:|---|---|
| [gkamradt/needle-in-a-haystack](https://github.com/gkamradt/needle-in-a-haystack) | 2,386 | MIT | Original needle-in-haystack retrieval test across context lengths. |
| [booydar/babilong](https://github.com/booydar/babilong) | 257 | Apache-2.0 | BABILong: needle-in-haystack on bAbI tasks; up to 10M tokens. |
| [THUDM/LongBench](https://github.com/THUDM/LongBench) | 1,238 | MIT | LongBench v1+v2 (ACL'24/'25); 50+ tasks / 6 languages at long context. |
| [OpenBMB/InfiniteBench](https://github.com/OpenBMB/InfiniteBench) | 393 | MIT | ∞Bench: long-context eval beyond 100K tokens. |
| [hsiehjackson/RULER](https://github.com/hsiehjackson/RULER) | 1,619 | Apache-2.0 | RULER: 13 task categories to expose real vs claimed context sizes. |
| [OpenLMLab/LEval](https://github.com/OpenLMLab/LEval) | 407 | GPL-3.0 | L-Eval (ACL'24 Outstanding); 54 sub-datasets for long-context LLMs. |

**Picks:** Before shipping a long-context model, run it through `RULER`, `needle-in-a-haystack`, and `LongBench`. Claimed vs real context sizes often differ by 2–4×.

---

## 14. The calculator — pricing reference

The pricing table below is a snapshot of GitHub Copilot Usage-Based Billing rates effective June 2026 (the source the reference playbooks cite). For non-Copilot use, the relative ratios between tiers hold across providers; absolute prices differ. **1 credit = $0.01 USD.** Auto Mode applies a 10% discount on top.

| Tier | Model | Input $/1M | Cached $/1M | Output $/1M |
|---|---|---:|---:|---:|
| **Lightweight** | GPT-5.4 nano | 0.20 | 0.02 | 1.25 |
| | GPT-5 mini | 0.25 | 0.025 | 2.00 |
| | GPT-5.4 mini | 0.75 | 0.075 | 4.50 |
| | Gemini 3 Flash | 0.50 | 0.05 | 3.00 |
| | Gemini 3.5 Flash | 1.50 | 0.15 | 9.00 |
| | MAI-Code-1-Flash | 0.75 | 0.075 | 4.50 |
| | Raptor mini | 0.25 | 0.025 | 2.00 |
| **Versatile** | GPT-5.4 | 2.50 | 0.25 | 15.00 |
| | GPT-5.4 Long | 5.00 | 0.50 | 22.50 |
| | Claude Haiku 4.5 | 1.00 | 0.10 | 5.00 |
| | Claude Sonnet 4 / 4.5 / 4.6 | 3.00 | 0.30 | 15.00 |
| | Gemini 2.5 Pro | 1.25 | 0.125 | 10.00 |
| | Gemini 3.1 Pro | 2.00 | 0.20 | 12.00 |
| **Powerful** | GPT-5.3-Codex | 1.75 | 0.175 | 14.00 |
| | GPT-5.5 | 5.00 | 0.50 | 30.00 |
| | GPT-5.5 Long | 10.00 | 1.00 | 45.00 |
| | Claude Opus 4.5–4.8 | 5.00 | 0.50 | 25.00 |
| | Claude Fable 5 (1M ctx) | 10.00 | 1.00 | 50.00 |
| | Gemini 3.1 Pro Long | 4.00 | 0.40 | 18.00 |

### 14.1 Reasoning effort multipliers (applied to output)

| Effort | Multiplier |
|---|---:|
| Low | ×1 |
| Medium | ×3 |
| High | ×14 |
| Max | ×60 |

### 14.2 A worked example

A 30-turn agent task on Claude Sonnet 4.5 with Medium reasoning effort, average 10K input tokens per turn, 1K output tokens per turn (before reasoning multiplier), 50% cache hit rate on input:

- Input: 30 turns × 10K × 50% × $3 + 30 turns × 10K × 50% × $0.30 = $4.50 + $0.45 = **$4.95**
- Output: 30 turns × 1K × 3 (Medium) × $15 = **$1.35**
- Total: **$6.30**

Same task with Auto Mode (10% discount), High reasoning effort, no caching:
- Input: 30 × 10K × $3 = $9.00 (× 0.9 Auto) = **$8.10**
- Output: 30 × 1K × 14 × $15 = $6,300 × 0.9 = **$5.67**
- Total: **$13.77** — 2.2× the cost of the optimised version.

### 14.3 Plan math

Copilot plan math (effective June 2026):
- **Copilot Business:** $19/seat/month, 1,900 credits included ($19 of usage).
- **Copilot Enterprise:** $39/seat/month, 3,900 credits included ($39 of usage).
- Overages billed at the rates in the table above.

A disciplined team running 30 turns/day on Sonnet with the optimisation stack above spends ~$6.30 × 22 working days = **$139/month/developer** — well within the Enterprise included credits. An uncontrolled team on Opus with High effort and no caching spends ~$13.77 × 22 × 2 (Opus premium) = **$606/month/developer** — well into overage. The 4× gap is the lever this playbook exists to close.

---

## 15. Checklists and copy-paste templates

### 15.1 Day-0 setup checklist

- [ ] Enable per-user limits (ULB) at 150% of expected average.
- [ ] Enable cost-center budgets with 80% alerts.
- [ ] Set enterprise cap with 80% alert to finance partner.
- [ ] Default model to Auto Mode (where available) or Versatile tier with explicit downgrade rules.
- [ ] Default reasoning effort to Low or Medium.
- [ ] Audit enabled MCP tools; scope per-workspace.
- [ ] Write `AGENTS.md` / `copilot-instructions.md` as landmines only (~20 rules, ~60 tokens).
- [ ] Set up Langfuse / Helicone / OpenLIT observability.
- [ ] Capture a golden set of 50–200 prompts for regression testing.
- [ ] Set up promptfoo or ragas eval harness.

### 15.2 Per-task checklist (developer)

- [ ] State acceptance criteria in one sentence. If you can't, use Plan mode, not Agent.
- [ ] Use the escalation ladder: `#selection → #file:Lx-Ly → #file → #folder → #codebase`.
- [ ] Cap retrieved RAG chunks at 5–10.
- [ ] Add output cap at end of prompt ("Code only", "List one per line", etc.).
- [ ] Use reasoning effort Low/Medium by default; reserve High/Max for explicit gates.
- [ ] End-of-task: `/clear` (or `/compact` if continuation expected).

### 15.3 Per-week checklist (team lead)

- [ ] Review the cost-by-tier dashboard. Watch for powerful-tier growth.
- [ ] Review cache-hit-rate. Target 60%+. Below 40% → investigate prefix stability.
- [ ] Review tokens-per-task histogram. Investigate outliers.
- [ ] Review quality metric. Must not trend down as cost trends down.
- [ ] Audit MCP tool catalog; disable anything unused in the last week.

### 15.4 Per-quarter checklist (org)

- [ ] Re-baseline the golden eval set; rotate stale prompts.
- [ ] Compare per-developer spend across teams; investigate 2×+ outliers.
- [ ] Re-evaluate model tier defaults; new model generations shift the cost-per-quality frontier.
- [ ] Audit `AGENTS.md` / `copilot-instructions.md` files; delete anything derivable.
- [ ] Run RULER / needle-in-a-haystack on any long-context claims you depend on.

### 15.5 Template — global `copilot-instructions.md`

```markdown
# Global landmines
- Use uv, not pip. (CI rejects pip installs.)
- Migrations must run in order; `alembic upgrade head` is forbidden in PRs.
- Do not refactor auth — pending audit Q3. Touching `auth/` blocks the PR.
- Tests run in parallel; do not use module-level state.
- Prefer structured output (zod / pydantic) over free-form parsing.
- Default reasoning effort: Low. Reserve High for architecture.
- Output caps: prefer "code only" over "explain + code".
```

### 15.6 Template — path-scoped instructions

```markdown
---
applyTo: "src/api/**/*.ts"
---
# API conventions
- All endpoints return `Result<T, ApiError>`, never throw.
- Validate with zod at the controller boundary; never inline.
- Versioning: URL path (`/v1`, `/v2`), not header.
- Error shape: `{ "error": { "code": "STRING", "message": "STRING", "details"?: OBJECT } }`.
```

### 15.7 Template — task kickoff (chat-paste)

```
Task: <one-sentence statement of acceptance criteria>

Context:
- Files: #file1 #file2 (escalation ladder: prefer #selection or #file:Lx-Ly)
- Related: #file3 (for types/imports only)

Constraints:
- Code only, no explanation.
- Don't modify tests unless asked.
- Reasoning effort: medium (downgrade to low if mechanical)

Output: <expected artifact>
```

### 15.8 Template — on-demand recipe (`review-pr.prompt.md`)

```markdown
---
mode: agent
---
# PR review

You are reviewing a PR. For each file in the diff:

1. Identify correctness issues (will it break? what case?).
2. Identify readability issues (would you accept in review?).
3. Identify security issues (any obvious vulns?).
4. Identify architecture issues (does it fit the surrounding pattern?).

Output format:
- One section per file.
- For each issue: severity (high/medium/low), description, suggested fix.
- No file → "No issues."
```

### 15.9 Template — subagent delegation

```
Parent prompt:
"Research the authentication flow. Use a subagent to read the 20 auth files
in isolation. Return a 1,000-token summary: (a) the flow, (b) the dependencies,
(c) the landmines. I will plan the refactor from your summary."

Subagent prompt (in isolated context):
"Read these 20 files. Summarize in 1,000 tokens:
- The authentication flow (step-by-step, no code).
- External dependencies (packages, services).
- Landmines (rules the team has in AGENTS.md or code comments).

Files: #file1 #file2 ... #file20"
```

### 15.10 Template — production routing policy (LiteLLM YAML)

```yaml
model_list:
  - model_name: cheap
    litellm_params:
      model: anthropic/claude-haiku-4.5
  - model_name: strong
    litellm_params:
      model: anthropic/claude-sonnet-4.5

router_settings:
  routing_strategy: simple-shuffle
  fallbacks:
    - strong: [cheap]

litellm_settings:
  max_budget: 100  # USD per day per user
  budget_duration: 1d
  cache: true
  cache_params:
    type: redis
    ttl: 600  # 10 min

callbacks:
  - langfuse  # observability
```

---

## 16. Companion scripts

A reference Python script ships alongside this playbook at **`/home/z/my-project/scripts/token_budget.py`**. It implements the mechanical parts of the playbook: token counting, cost estimation, AGENTS.md auditing, escalation-ladder recommendation, prompt-packet breakdown, and language-tax estimation.

### 16.1 Setup

```bash
pip install tiktoken   # required for accurate OpenAI/GPT tokenization
# Optional: pip install transformers   # for non-OpenAI tokenizers (Llama, Gemma, etc.)
```

### 16.2 Commands

```bash
# Count tokens in text, a file, or a directory of source files
python token_budget.py count --text "Refactor function. Fix auth handling. Make efficient."
python token_budget.py count --file path/to/prompt.md
python token_budget.py count --dir src/auth

# Estimate cost for a request (model + reasoning effort + cache hit rate)
python token_budget.py cost \
    --model claude-sonnet-4.5 \
    --input 10000 --output 1000 \
    --effort medium --cache-hit 0.5 --auto-mode

# Audit an AGENTS.md file for the landmine-vs-encyclopedia pattern
python token_budget.py audit --file AGENTS.md

# Recommend an escalation-ladder attachment for a change
python token_budget.py ladder --loc 50 --complexity low

# Pretty-print a prompt packet breakdown by layer
python token_budget.py breakdown --system 350 --instructions 1200 --tools 1800 \
    --history 4500 --retrieved 2400 --user 180

# Estimate token overhead by language (the language tax)
python token_budget.py language-tax --words 1000
```

### 16.3 Sample output

```json
{
  "model": "claude-sonnet-4.5",
  "tier": "versatile",
  "input_tokens": 10000,
  "cached_tokens": 5000,
  "output_tokens_visible": 1000,
  "output_tokens_with_reasoning": 3000,
  "reasoning_effort": "medium",
  "reasoning_multiplier": 3,
  "input_cost_usd": 0.015,
  "cached_cost_usd": 0.0015,
  "output_cost_usd": 0.045,
  "total_cost_usd": 0.0615
}
```

### 16.4 Extending the script

The pricing table is a Python dict at the top of the file; add your provider's rates by editing it. For non-OpenAI tokenizers, swap the `get_encoder()` function to use HuggingFace `transformers.AutoTokenizer.from_pretrained("...")`. The script is intentionally short (≈300 lines) and dependency-light so it can be dropped into any repo without ceremony.

### 16.5 Suggested next scripts to build

- **`prompt_compress.py`** — paste a verbose prompt; receive a compressed version (drop politeness, hedging, preamble; convert prose to bullets). Use an LLM-as-judge pass to verify the compressed prompt produces equivalent output.
- **`tool_audit.py`** — read MCP config from `.vscode/mcp.json`; estimate per-agent-run schema cost; recommend per-workspace scoping.
- **`eval_runner.py`** — wrap promptfoo or ragas; run on a golden set; alert if quality drops more than 2%.
- **`cache_stability.py`** — diff two prompt packets; report whether the cache-stable prefix is preserved.

---

## 17. Glossary and references

### 17.1 Glossary

| Term | Definition |
|---|---|
| **BPE** | Byte-Pair Encoding. The tokenizer family used by GPT, Claude, and Gemini. Builds vocabulary by merging frequent byte pairs. |
| **Unigram** | The alternative tokenizer family used by SentencePiece / Llama. Builds vocabulary by selecting tokens that maximize a likelihood score. |
| **Prompt packet** | The full assembled input the model sees: system prompt + custom instructions + tool schemas + history + retrieved context + user message. |
| **Cache-stable prefix** | The byte-identical front portion of the prompt packet that can be cached across calls at ~10% of the input rate. |
| **Reasoning effort** | The knob (Low/Medium/High/Max) that controls how many tokens the model spends on chain-of-thought before the visible reply. |
| **MCP** | Model Context Protocol. The standard for tool schemas the model can call; each enabled tool's schema rides along on every agent step. |
| **Subagent** | A separate agent call with its own context window, used to compress source material into a summary before the parent agent reasons over it. |
| **Landmine** | In an AGENTS.md file, a rule the model cannot infer from the code and would otherwise violate. The opposite of "encyclopedia" content. |
| **ULB** | Per-User Limit Budget. The per-developer daily/weekly token spend cap. Default: 150% of expected average. |
| **Escalation ladder** | The order `#selection → #file:Lx-Ly → #file → #folder → #codebase` for context attachment, used from smallest upward. |
| **Tier** | Provider's model hierarchy: Lightweight / Versatile / Powerful. Roughly 1× / 6–10× / 15–25× the input price. |
| **UBB** | Usage-Based Billing. The per-token billing model that replaced per-seat credits (Copilot effective June 2026). |

### 17.2 References

**Reference playbooks (the source of inspiration for this document):**
- Quick guide: `https://ashy-dune-0b4215a0f.7.azurestaticapps.net/`
- Detailed playbook: `https://sukurcf.github.io/sessions/token-optimization-best-practises/detailed/index.html#/home`
- Both authored by Microsoft Asia Developer GBB, based on public GitHub Copilot documentation.

**Official documentation:**
- GitHub Copilot — Models and pricing: `https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing`
- GitHub Copilot — Prepare for usage-based billing: `https://docs.github.com/en/copilot/billing/about-billing-for-github-copilot-in-your-organization`
- GitHub Copilot — Changing the AI model: `https://docs.github.com/en/copilot/using-github-copilot/using-ai-coding-tools-to-write-and-debug-code-faster/changing-the-ai-model-for-copilot-chat`
- VS Code Copilot customization: `https://code.visualstudio.com/docs/copilot/copilot-customization`
- VS Code Copilot chat modes: `https://code.visualstudio.com/docs/copilot/chat/chat-modes`
- VS Code MCP servers: `https://code.visualstudio.com/docs/copilot/customization/mcp-servers`
- OpenAI Tokenizer playground: `https://platform.openai.com/tokenizer`
- Anthropic Prompt Caching docs: `https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching`
- Google Gemini long-context docs: `https://ai.google.dev/gemini-api/docs/long-context`

**Tokenization research:**
- Komatsuzaki tokenizer heatmap (6 models × 9 languages): `https://github.com/komatsuzaki/awesome-tokenizer-efficiency`
- Sennrich et al., "Neural Machine Translation of Rare Words with Subword Units" (BPE): `https://arxiv.org/abs/1508.07909`
- Kudo, "Subword Regularization" (Unigram / SentencePiece): `https://arxiv.org/abs/1804.10959`

**Automatic prompt optimization:**
- APE — Automatic Prompt Engineer: `https://arxiv.org/abs/2211.01910`
- OPRO — Optimization by PROmpting: `https://arxiv.org/abs/2309.03409`
- DSPy: `https://arxiv.org/abs/2310.03714`
- EvoPrompt: `https://arxiv.org/abs/2309.08532`

**Inference optimization:**
- vLLM PagedAttention paper: `https://arxiv.org/abs/2309.06180`
- EAGLE speculative decoding: `https://arxiv.org/abs/2401.15077`
- AWQ activation-aware weight quantization: `https://arxiv.org/abs/2306.00978`
- Streaming-LLM attention sinks: `https://arxiv.org/abs/2309.17453`

**Long-context benchmarks:**
- Needle in a haystack (original): `https://github.com/gkamradt/needle-in-a-haystack`
- RULER: `https://arxiv.org/abs/2404.06654`
- LongBench v2: `https://arxiv.org/abs/2412.15204`
- ∞Bench: `https://arxiv.org/abs/2402.13718`

**Related research cited in the reference playbooks:**
- ETH-Zurich study on LLM-generated AGENTS.md (47 projects): correctness −2%, token cost +20–23%. Referenced in the sukurcf playbook.
- GitHub blog — Improving token efficiency in agentic workflows: `https://github.blog/news-insights/product-news/improving-token-efficiency-in-github-agentic-workflows/`
- GitHub Skills — Getting started with Copilot (free course, ~1 hour): `https://github.com/skills/getting-started-with-github-copilot`

### 17.3 A final note

The numbers in this playbook are snapshots. Token prices, model tiers, reasoning-effort multipliers, and cache discount rates change every quarter; the patterns do not. If you adopt the six pillars and the eleven levers, the exact ratios can drift by 20% in either direction and the playbook will still produce a 30–45% token-cost reduction in your first quarter. The levers that compound most reliably are context discipline, model routing, and the cache-stable prefix; the levers that are easiest to lose are session hygiene and tool-scope discipline, because they require institutional habit rather than individual practice.

The discipline that holds it all together is the three-layer budget. Without it, every other lever decays in a quarter. With it, the gains compound — and the next quarter's optimisation work builds on the previous quarter's, instead of re-deriving it.
