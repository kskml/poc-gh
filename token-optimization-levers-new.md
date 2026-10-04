---
title: "Token Optimization Levers for AI Coding Assistants"
subtitle: "A practical handbook for everyday developers"
author: "Z.ai"
date: "2026-10-05"
version: "2.0"
template: "technical-handbook"
color_scheme: "editorial-blue"
language: "en"
---

<div align="center">

# Token Optimization Levers for AI Coding Assistants
## *A practical handbook for everyday developers*

&nbsp;

**Author** &nbsp;&nbsp; Z.ai  
**Version** &nbsp;&nbsp; 2.0 (Extended Edition)  
**Published** &nbsp;&nbsp; 2026-10-05  
**Reading time** &nbsp;&nbsp; ~25 minutes  
**Levers covered** &nbsp;&nbsp; 18

&nbsp;

---

</div>

## Table of Contents

**Front matter**

- [1. Why this guide exists](#1-why-this-guide-exists)
- [2. The complete lever list](#2-the-complete-lever-list)
- [3. How to read each lever](#3-how-to-read-each-lever)

**Chapter 4 — Prompt-level levers (A)**

- [4.1 Prompt engineering / concise instructions](#41-prompt-engineering--concise-instructions)
- [4.2 Output constraints & structured formats](#42-output-constraints--structured-formats)

**Chapter 5 — Context & session levers (B)**

- [5.1 Context engineering / selective context](#51-context-engineering--selective-context)
- [5.2 Session management & context compaction](#52-session-management--context-compaction)
- [5.3 History summarization & fresh sessions](#53-history-summarization--fresh-sessions)
- [5.4 Repo memory / instruction files](#54-repo-memory--instruction-files)

**Chapter 6 — Tool & retrieval levers (C)**

- [6.1 Just-in-time / selective retrieval](#61-just-in-time--selective-retrieval)
- [6.2 Tool output management & truncation](#62-tool-output-management--truncation)
- [6.3 Exclusion of noise](#63-exclusion-of-noise)

**Chapter 7 — Architecture & model levers (D)**

- [7.1 Sub-agents / task decomposition](#71-sub-agents--task-decomposition)
- [7.2 Model selection / cascading](#72-model-selection--cascading)

**Chapter 8 — Caching & platform lever (E)**

- [8.1 Prompt caching](#81-prompt-caching)

**Chapter 9 — Skills, tools & output control levers (F)**

- [9.1 Skills & persistent agent workflows](#91-skills--persistent-agent-workflows)
- [9.2 Tool set restriction per turn](#92-tool-set-restriction-per-turn)
- [9.3 Repo graph & structural code tools](#93-repo-graph--structural-code-tools)
- [9.4 Caveman mode & ultra-terse output styles](#94-caveman-mode--ultra-terse-output-styles)
- [9.5 Tool call batching & parallelism](#95-tool-call-batching--parallelism)
- [9.6 Token budgeting & live counting](#96-token-budgeting--live-counting)

**Back matter**

- [10. Closing — the high-ROI habits](#10-closing--the-high-roi-habits)
- [Appendix A — Tools quick-reference](#appendix-a--tools-quick-reference)

---


---

## 1. Why this guide exists

Every token an AI coding assistant reads or writes costs you money, adds latency, eats into the context window, and—most importantly—degrades quality. When the context gets bloated, models start ignoring instructions, forget earlier decisions, and hallucinate APIs. The community calls this **context rot**: the larger and noisier the context, the worse the model's effective intelligence becomes.

The good news: most token waste comes from a handful of predictable patterns—pasting whole files, never starting fresh sessions, letting tool outputs pile up, and using the biggest model for trivial edits. Fixing those patterns is **context engineering**, and it tends to beat clever prompt tricks by an order of magnitude.

This guide lists every high-impact lever available to a developer *inside the tools themselves* (Cursor, Claude Code, Copilot Chat, Aider, Windsurf, OpenCode). No backend changes, no fine-tuning, no API wrangling—just habits, settings, and project files you can adopt today.

---

## 2. The complete lever list

Grouped by where in the request lifecycle the savings happen.

**A. Prompt-level (what you type this turn)**
1. Prompt engineering / concise instructions
2. Output constraints & structured formats

**B. Context & session (what the model carries across turns)**
3. Context engineering / selective context
4. Session management & context compaction
5. History summarization & fresh sessions
6. Repo memory / instruction files (`.cursorrules`, `CLAUDE.md`, `AGENTS.md`)

**C. Tool & retrieval (how the agent explores the repo)**
7. Just-in-time / selective retrieval
8. Tool output management & truncation
9. Exclusion of noise (build artifacts, lockfiles, deps)

**D. Architecture & model (how you structure the work)**
10. Sub-agents / task decomposition
11. Model selection / cascading

**E. Caching & platform**
12. Prompt caching

**F. Skills, tools & output control**
13. Skills & persistent agent workflows
14. Tool set restriction per turn
15. Repo graph & structural code tools (graphify, ast-grep, ctags, LSP)
16. Caveman mode & ultra-terse output styles
17. Tool call batching & parallelism
18. Token budgeting & live counting

---

## 3. How to read each lever

Every lever below follows the same shape:

- **One-line definition + why it matters**
- **What it reduces** (input tokens, output tokens, cost, latency, or context rot)
- **Do / Don't table** — concrete actions vs. common mistakes
- **Worked examples** tailored to coding agents
- **Expected impact** — a rough range so you can prioritize

Impact ranges assume a typical mid-size repo (10k–500k LoC) and multi-turn agentic sessions. Your mileage will vary, but the relative ordering is stable across Cursor, Claude Code, Copilot, Aider, and Windsurf.

---

## 4. Prompt-level levers (A)

### 4.1. Prompt engineering / concise instructions

**Definition.** Writing tight, purposeful prompts that say exactly what you want and nothing more.

**Why it matters for coding agents.** A model can't ignore fluff in your prompt—it processes every word, and verbose prompts dilute signal. Worse, "explain everything" style prompts encourage the model to write essays back, multiplying output tokens.

**What it reduces.** Input tokens (small wins per turn) and output tokens (often the bigger win when you constrain scope).

| ✅ Do | ❌ Don't |
|----|-------|
| Lead with the verb: *find*, *refactor*, *fix*, *add test for* | Write "Can you please take a look at this and let me know what you think?" |
| Specify the target: file, function, line, symbol | Paste the whole file and hope the agent figures out the scope |
| State the desired output: *diff only*, *JSON*, *bullet list* | Ask for "a comprehensive analysis" then complain it's long |
| Give one concrete example when the format is non-obvious | Give three examples that subtly contradict each other |
| Use numbered steps for multi-step tasks | Bury seven requirements in a single paragraph |
| Drop greetings, "thanks", and meta-commentary | Treat the chat like an email to a colleague |

> **📌 Examples**
>
>
> - ❌ *"Can you please look at this auth code and tell me what might be wrong?"*
> - ✅ *"Find the null-deref bug in `auth.ts:42` where `user` can be undefined. Reply with the fix as a diff, no explanation."*
>
> - ❌ *"Here's our whole checkout service. Make it better."*
> - ✅ *"Refactor `processPayment` in `checkout/service.ts` to extract validation into a pure function. Keep the public signature. Return only the new function."*
>
> - ❌ *"Write tests for this."* (model writes 30 tests, half irrelevant)
> - ✅ *"Add 3 unit tests for `parseInvoice` covering: empty input, negative total, malformed JSON. Use the existing `vitest` patterns in `__tests__/invoice.test.ts`."*
>
> **Expected impact.** 10–30% on prompt tokens, 30–60% on response tokens when you constrain format. Compounds across long sessions.
>

---

### 4.2. Output constraints & structured formats

**Definition.** Explicitly telling the model what shape its answer must take.

**Why it matters for coding agents.** Unconstrained answers drift into essays. A one-line fix can become a 400-word explanation if you don't pin the format. Structured formats (diff, JSON, single function) also make the answer directly consumable by the next tool in the pipeline.

**What it reduces.** Output tokens (often the dominant cost in agentic flows) and downstream input tokens when the response is fed back.

| ✅ Do | ❌ Don't |
|----|-------|
| Specify *diff only*, *patch only*, *function only* | Accept prose-wrapped code with explanations |
| Pin a schema: `Return JSON {fix: string, severity: "low"\|"med"\|"high"}` | Say "give me the data as JSON" and hope the keys are right |
| Use word/line caps: *≤ 20 lines*, *one paragraph* | Leave length open when you have a budget |
| Tell the model what *not* to include: *no commentary, no imports* | Let it prefix every code block with `Here is the code:` |
| Provide a template it can fill in | Make it invent the structure from scratch every time |

> **📌 Examples**
>
>
> - ✅ *"Reply with only a unified diff. No prose. No ` ```diff ` fences. No 'Here is the fix:'."*
> - ✅ *"Return a JSON array of ` {file, line, issue}` objects. Max 10 entries."*
> - ✅ *"Output the new function only. Keep the original signature. Do not include the surrounding class."*
> - ✅ *"Generate the migration SQL. No explanation, no 'this migration adds…' preamble."*
>
> **Expected impact.** 40–80% on output tokens. Especially important in loops where the output is parsed by another tool.
>

---

## 5. Context & session levers (B)

### 5.1. Context engineering / selective context

**Definition.** Choosing exactly what the model sees—files, symbols, ranges—instead of dumping everything in.

**Why it matters for coding agents.** This is the single highest-leverage lever. A typical refactoring task needs 3–5 functions, not 30 files. Every unrelated line you feed the model is a line it might fixate on, hallucinate against, or be confused by. Context rot is real: at >50% of the context window, model accuracy on real tasks drops measurably.

**What it reduces.** Input tokens (often dramatically) and improves quality (which reduces retry loops, saving more tokens downstream).

| ✅ Do | ❌ Don't |
|----|-------|
| Use the agent's symbol-level references (`@function`, `@class`) | Paste the whole 800-line file "for context" |
| Pass only the function signature + the body that matters | Include sibling functions, imports, and module-level constants "just in case" |
| Extract a minimal repro snippet for bug reports | Attach the entire failing test suite plus setup |
| Mention related files by path, let the agent decide whether to read | Inline-open five files into the chat preemptively |
| Trim pasted code to the relevant lines, with a comment `// …` | Paste with full original whitespace and 200-line headers |
| Use "lookup" or "go to definition" agent commands | Manually grepping and pasting results back |

> **📌 Examples**
>
>
> - ❌ Paste `package.json`, `tsconfig.json`, three test files, and the implementation file when asking why a test fails.
> - ✅ *"Test `auth.login rejects expired token` fails. Here is the test (12 lines) and the function under test (30 lines). Why does `jwt.verify` throw instead of returning null?"*
>
> - ❌ Open the entire `routes/` directory in Cursor's context before asking about one route.
> - ✅ Use `@routes/checkout.ts` and let the agent pull `@models/order.ts` only if it asks.
>
> - ❌ *"Here are all 47 files in our component library, please review."*
> - ✅ *"Review `Button.tsx` and `IconButton.tsx` for prop API inconsistencies. Ignore the rest."*
>
> **Expected impact.** 40–80% on file-heavy tasks. Often the difference between a $0.05 task and a $1.50 task.
>

---

### 5.2. Session management & context compaction

**Definition.** Keeping each chat session scoped to one task, and compacting accumulated context before it gets dangerously long.

**Why it matters for coding agents.** Every turn in a session re-sends the entire accumulated history. Turn 1 costs 2k tokens, turn 10 might cost 40k, turn 30 could cost 150k—just to re-read the same growing transcript. Past ~60% of the context window, models also start dropping early instructions, contradicting themselves, and forgetting your constraints.

**What it reduces.** Input tokens (multiplicative across turns) and quality (which prevents retry loops).

| ✅ Do | ❌ Don't |
|----|-------|
| Start a new chat per task: *bug X*, *feature Y*, *refactor Z* | Run one mega-session for the whole workday |
| Run `/compact` (Claude Code) or summarize-then-restart (Cursor) when the thread passes ~20 turns | Keep going until the model forgets your original goal |
| Keep one task per session; spin off sub-tasks to new sessions | Pile bug-fixes, feature work, and questions into one thread |
| Before compacting, ask the model to write a "decisions log" you can paste into the new session | Trust the auto-compaction to preserve your style preferences—it often drops them |
| Close dead-end branches explicitly: *"Abandoning approach X, do not propose it again"* | Leave abandoned ideas floating in history where the model may resurrect them |

> **📌 Examples**
>
>
> - ✅ In Claude Code: type `/compact` after every successful milestone (test passes, PR opened). The model summarizes and you continue with a clean slate.
> - ✅ In Cursor: when a chat hits ~30 messages, ask *"Summarize what we decided and the current file state in ≤10 bullets."* Copy the summary, start a new chat, paste it as the first message.
> - ✅ In Copilot Chat: don't reuse the "Suggest" panel across unrelated tasks. New chat = new mental model.
>
> **Expected impact.** 50%+ on long sessions; quality improvement is often the bigger win.
>

---

### 5.3. History summarization & fresh sessions

**Definition.** Deliberately producing a tight summary of past work, then starting a fresh session with only that summary as context.

**Why it matters for coding agents.** Closely related to session management, but more aggressive: instead of letting the agent compact in place, *you* control what survives. This is the only reliable way to keep multi-day refactors coherent without context rot.

**What it reduces.** Input tokens across the next N turns (often 5–10x reduction) and prevents quality collapse on long projects.

| ✅ Do | ❌ Don't |
|----|-------|
| End each work block with: *"Summarize decisions, open questions, file changes, and pending todos in ≤15 bullets."* | Just close the tab and hope you remember tomorrow |
| Paste the summary + relevant diffs into the next session as a cold start | Re-explain the whole project to the agent each morning |
| Keep a running `DECISIONS.md` in the repo the agent can read on demand | Re-derive the architecture every session |
| Discard tangents and abandoned approaches from the summary | Include every dead-end "in case it's useful later" |
| Pin the next concrete step at the top of the new session | Leave the next step implicit and let the agent propose five wrong ones |

> **📌 Examples**
>
>
> - ✅ *"Write a handover note: (1) what we changed, (2) what's pending, (3) tests passing/failing, (4) one open question. ≤200 words."* → save to `NOTES.md` → new chat starts with `Read NOTES.md, then implement step (2).`
> - ✅ In Claude Code: use `/export` (or copy the transcript) before `/clear`, then write a 10-line summary yourself.
> - ✅ For multi-day refactors: commit a `CONTEXT.md` at the end of each day, have the next session read it first thing.
>
> **Expected impact.** 60–90% on accumulated context vs. naive continuation. Especially powerful on 3+ day projects.
>

---

### 5.4. Repo memory / instruction files

**Definition.** Persistent project files (`CLAUDE.md`, `.cursorrules`, `AGENTS.md`, `.github/copilot-instructions.md`, `WINDSURF_RULES`) that the agent reads automatically at session start.

**Why it matters for coding agents.** These files let you state your project's conventions once—test framework, package manager, naming, lint config, preferred libraries—and have them apply to every session forever, without re-explaining each time. They also constrain output style, which prevents the model from suggesting `npm install` when you use `pnpm`.

**What it reduces.** Input tokens (you stop re-typing context every session) and output tokens (the model picks the right tool the first time, avoiding redo loops).

| ✅ Do | ❌ Don't |
|----|-------|
| Keep it under ~300 lines; favor bullet lists | Write a 5000-word essay on your architecture |
| Put the most-important rules at the top (some models weight early lines more) | Bury "use pnpm" on line 400 |
| Include: build/test commands, file layout, naming, banned patterns, env setup | Include: history, opinions, philosophical preferences |
| Update it when conventions change (commit it like code) | Let it drift out of date until the agent's advice is wrong |
| Reference other files instead of duplicating: *"See `docs/style.md` for naming"* | Maintain three competing copies in `.cursorrules`, `CLAUDE.md`, `AGENTS.md` |
| Use tool-specific files where they exist (Cursor reads `.cursor/rules/*.mdc`) | Assume one file works across all tools identically |

> **📌 Examples**
>
>
> A minimal `CLAUDE.md` that pays for itself in one session:
>
> ```markdown
> # Project: acme-checkout
> - Language: TypeScript 5.4, strict mode
> - Package manager: pnpm (NEVER use npm or yarn)
> - Test runner: vitest, colocated as `*.test.ts`
> - Lint: biome (no eslint/prettier)
> - Build: `pnpm build` → `dist/`
> - Conventions:
>   - Functions: `camelCase`; Types: `PascalCase`; Constants: `SCREAMING_SNAKE`
>   - No default exports; use named exports
>   - Errors: throw `AppError` subclasses, never `Error`
> - Banned:
>   - `any`, `ts-expect-error`, `console.log` (use `logger`)
>   - `lodash` (use native ES)
>   - `moment` (use `date-fns`)
> ```
>
> - ✅ Cursor: use `.cursor/rules/*.mdc` for per-folder rules (e.g. different rules in `frontend/` vs `backend/`).
> - ✅ Aider: use `CONVENTIONS.md` and pass `--read CONVENTIONS.md` or just name it `.aider.conf.yml`'s read list.
> - ✅ Copilot: maintain `.github/copilot-instructions.md`; it's read by Copilot Chat and workspace suggestions.
>
> **Expected impact.** Saves 5–15% per session in re-explanation, but the bigger win is fewer wrong-tool suggestions and redo loops.
>

---

## 6. Tool & retrieval levers (C)

### 6.1. Just-in-time / selective retrieval

**Definition.** Letting the agent search the repo and pull only the symbols or line ranges it actually needs, instead of preloading files.

**Why it matters for coding agents.** Modern agents (Claude Code, Cursor, Aider, Windsurf) have built-in codebase search: symbol lookup, glob, grep, "go to definition." Used well, they read 50 lines instead of 800. Used poorly (or not at all), you'll catch yourself pasting whole files back into the chat.

**What it reduces.** Input tokens (often dramatic on navigation-heavy tasks) and quality (less noise = better focus).

| ✅ Do | ❌ Don't |
|----|-------|
| Tell the agent to search: *"Find all call sites of `audit()` and report back the file:line list"* | Manually `grep` in your terminal and paste the results |
| Use `@codebase` / "search repo" features for natural-language lookups | Open 10 files in the editor hoping the agent will read them |
| Ask for symbol-level reads: *"Read only the body of `UserRepository.findActive`"* | Let the agent pull an entire 2k-line repository file |
| Request a *report* first, then a *fix* in a follow-up turn | Demand "fix it" in one shot, which forces the agent to read everything defensively |
| Provide a starting hint: *"start at `src/auth/login.ts:88`"* | Make the agent guess where to start across 500 files |

> **📌 Examples**
>
>
> - ❌ Paste `routes/checkout.ts` (450 lines), `services/payment.ts` (300 lines), `models/order.ts` (180 lines) into Cursor before asking why a webhook fails.
> - ✅ *"Find the webhook handler in `routes/`. Read only the function that verifies the signature. Tell me which `crypto.timingSafeEqual` call is wrong."*
>
> - ✅ Claude Code: *"Use grep to find all usages of `process.env.DATABASE_URL`, then list file:line."* — the agent reads ~5 lines per match instead of 5 whole files.
>
> - ✅ Copilot Chat: use `#workspace` for repo-wide queries instead of opening files into context.
>
> **Expected impact.** 30–70% on navigation-heavy tasks; eliminates the "I pasted the wrong file" failure mode entirely.
>

---

### 6.2. Tool output management & truncation

**Definition.** Trimming the outputs of tools the agent runs (tests, builds, shell commands, logs) before they pile up in context.

**Why it matters for coding agents.** When an agent runs `npm test` and the output is 4000 lines, every subsequent turn re-sends those 4000 lines. After three test runs, you've burned 12k tokens on test output alone. Worse, the model starts answering questions *about the log* instead of about your code.

**What it reduces.** Input tokens (often the dominant cost in debug-by-test-loops) and quality (less noise).

| ✅ Do | ❌ Don't |
|----|-------|
| Pipe noisy commands through `head`/`tail`/`grep` before they hit the agent | Paste full build logs into the chat |
| Ask the agent to run a *summarized* version: `npm test 2>&1 \| tail -50` | Run `npm test` and let all 4000 lines flow into context |
| Configure the agent's tool wrappers to truncate by default (Cursor, Claude Code have settings for this) | Accept default tool output sizes forever |
| For repeated runs, ask the agent to grep for the specific failure: `npm test \| rg "FAIL\|Error"` | Re-run the whole suite and re-read the whole output each iteration |
| Split test runs: `vitest run path/to/specific.test.ts` | Always `vitest run` the entire suite when one test is failing |

> **📌 Examples**
>
>
> - ❌ *"Run the test suite"* → 4000 lines of output flood the context.
> - ✅ *"Run `vitest run auth/login.test.ts` and show me only failing assertions and their line numbers."*
>
> - ❌ Paste the entire `docker logs` (50k lines) of a failing container.
> - ✅ *"Get the last 100 lines of `docker logs app` and grep for `Error\|Exception`."*
>
> - ✅ In Claude Code: configure `Bash` tool output truncation to 2000 chars in settings, so runaway logs cap automatically.
>
> **Expected impact.** 60–90% on log-heavy debugging loops; turns a $2 debug session into a $0.20 one.
>

---

### 6.3. Exclusion of noise (build artifacts, lockfiles, deps)

**Definition.** Telling the agent (and its retrieval tools) to never look at `node_modules/`, `dist/`, `build/`, lockfiles, `.git/`, minified bundles, etc.

**Why it matters for coding agents.** If the agent's codebase search treats `package-lock.json` as searchable, every "find where X is used" query returns 50 hits inside the lockfile. Each hit tempts the model to read it, blowing context. Same for `*.min.js`, `dist/`, generated code. A single misconfigured ignore file can 10x your token bill on exploration tasks.

**What it reduces.** Input tokens (prevents accidental blowups) and quality (search results stay relevant).

| ✅ Do | ❌ Don't |
|----|-------|
| Maintain `.cursorignore` / `.aiderignore` / `.codeiumignore` mirroring `.gitignore` plus extras | Assume `.gitignore` is enough—most agents read files git tracks *and* untracked ones |
| Add `*.min.js`, `*.map`, `package-lock.json`, `pnpm-lock.yaml`, `dist/`, `build/`, `.next/`, `coverage/` to the ignore list | Let the agent index a 100MB lockfile "in case it's useful" |
| Configure indexing to skip vendored code: `vendor/`, `third_party/`, `bower_components/` | Watch the agent propose edits to files in `node_modules/` |
| Run a quick audit: ask the agent *"list files you can search"* and prune anything noisy | Set up the index once and never revisit |
| For monorepos: scope the agent to the affected package (`packages/web/`) per task | Index the whole monorepo and let cross-package noise leak in |

> **📌 Examples**
>
>
> A starter `.cursorignore` / `.aiderignore`:
>
> ```
> # Build / generated
> dist/
> build/
> .next/
> out/
> coverage/
> *.min.js
> *.min.css
> *.map
>
> # Deps
> node_modules/
> bower_components/
> vendor/
>
> # Lockfiles (huge, low-signal)
> package-lock.json
> pnpm-lock.yaml
> yarn.lock
> composer.lock
> Gemfile.lock
>
> # VCS / IDE
> .git/
> .idea/
> .vscode/
> *.swp
>
> # Data / logs
> *.log
> *.csv
> *.sqlite
> *.db
> ```
>
> - ✅ Aider: use `--read` for files you want the agent to *always* see (e.g. `CONVENTIONS.md`) and `.aiderignore` for everything you want it to *never* see.
> - ✅ Claude Code: maintain an `AGENTS.md` note like *"Never read files under `dist/` or any `*.lock` file."* — Claude Code will respect this in tool selection.
>
> **Expected impact.** Prevents 5–50x accidental context blowups; biggest safety net you can install.
>

---

## 7. Architecture & model levers (D)

### 7.1. Sub-agents / task decomposition

**Definition.** Splitting a large task into smaller sub-agent invocations, each with a focused goal and small context, then synthesizing the results.

**Why it matters for coding agents.** A 10-file refactor in a single context means the model reads all 10 files *every turn*. Decomposed: sub-agent A explores and returns a 200-word plan; sub-agent B implements file 1; sub-agent C implements file 2; main agent stitches. Each sub-agent's context stays small, so quality stays high and tokens stay low.

**What it reduces.** Total tokens (often—because you avoid re-reading huge contexts every turn) and prevents context rot (each sub-agent has a tight scope).

| ✅ Do | ❌ Don't |
|----|-------|
| Use the agent's sub-agent / Task tool for exploration: "scan the repo, return a 200-word plan" | Force one mega-agent to read 30 files and hold them all in context |
| Have sub-agents return summaries, not full file contents | Have sub-agents dump 5 files back into the parent context |
| Scope each sub-agent to one deliverable (one file, one decision, one test) | Ask a sub-agent to "refactor the auth module" (too big) |
| Run independent sub-agents in parallel when the agent supports it | Serialize 5 explorations that could've been concurrent |
| Discard sub-agent transcripts once synthesized (don't carry them forward) | Keep sub-agent outputs in the main context "for reference" |

> **📌 Examples**
>
>
> - ✅ In Claude Code: use the `Task` tool with sub-agent type "Explore" to find all call sites of `legacyAuth()`. The sub-agent reads 20 files internally but returns a 15-line report. You then ask the main agent to refactor based on that report.
>
> - ✅ Cursor: spawn Composer sub-tasks for parallel mechanical edits (rename a symbol across 30 files) rather than asking the main chat to do it sequentially.
>
> - ✅ Manual decomposition: instead of *"Migrate this service from REST to GraphQL,"* do:
>   1. Sub-task: "List all REST endpoints and their handlers."
>   2. Sub-task: "For endpoint X, propose the GraphQL schema."
>   3. Sub-task: "Implement resolver for `User.queries`."
>
> **Expected impact.** 50–80% context reduction on multi-file tasks; quality improvement is often the bigger win.
>

---

### 7.2. Model selection / cascading

**Definition.** Picking the right model for the job: small/fast/cheap for trivial edits, large/smart/expensive for design and refactors.

**Why it matters for coding agents.** Using GPT-4-class / Claude Opus-class / Sonnet-4-class models for every single edit is like hiring a senior architect to fix a typo. The cost gap between tiers is 5–15x; the quality gap on simple tasks is near zero. Modern coding agents let you switch models per turn or per task type—use it.

**What it reduces.** Cost (5–15x on easy tasks) and latency (smaller models are 2–5x faster).

| ✅ Do | ❌ Don't |
|----|-------|
| Use mini/flash/haiku for: rename, format, add a missing import, write a one-line test | Use the flagship model for autocomplete of boilerplate |
| Use mid-tier (Sonnet, GPT-4.1, etc.) for: feature work, bug fixes, test scaffolding | Always default to the biggest model "to be safe" |
| Use flagship (Opus, GPT-4.1-pro, etc.) for: architecture, multi-file refactors, tricky bugs | Burn Opus tokens on "convert all double quotes to single" |
| Set up cascades: small model drafts → large model reviews | Run every edit through the largest model and pay 10x |
| Configure per-tool model selection (Cursor: autocomplete vs chat vs apply) | Use the same model for everything |
| Measure cost per task type once; adjust defaults | Guess and never revisit |

> **📌 Examples**
>
>
> - ✅ Cursor: set "Tabs autocomplete" to a small model (`gpt-4o-mini` / `claude-3.5-haiku`), "Chat" to mid-tier, "Composer/Agent" to flagship.
> - ✅ Claude Code: use `--model sonnet` for everyday edits, `--model opus` for design sessions. Toggle with `/model`.
> - ✅ Aider: use `--model gpt-4o-mini` for the "architect" mode of brainstorming, then switch to `--model sonnet` for the implementation edit.
> - ✅ Copilot: use the inline "accept suggestion" (small model) for boilerplate; switch to Copilot Chat with GPT-4-class for design Q&A.
>
> **Expected impact.** 5–10x cost reduction on simple tasks; 2–5x latency improvement. Often the single biggest cost lever after context engineering.
>

---

## 8. Caching & platform lever (E)

### 8.1. Prompt caching

**Definition.** Arranging your prompt so a stable prefix is reused across turns, letting the provider (Anthropic, OpenAI, Google) cache it and charge far less for repeated reads.

**Why it matters for coding agents.** API prompt caching gives ~10x discount on cached input tokens and 5–85% latency reduction. Agentic sessions naturally reuse large prefixes (system prompt + repo memory + project context), so this can be the difference between a $0.50 task and a $0.05 task on multi-turn flows.

**What it reduces.** Cost (not raw tokens—same bytes flow, but cached reads cost 10x less) and latency.

| ✅ Do | ❌ Don't |
|----|-------|
| Put stable content first: system prompt, conventions, repo memory, large reference files | Put a unique "today's question" at the top, pushing shared context down |
| Keep the volatile question / per-turn data at the end of the prompt | Randomize the order of sections each turn |
| Use tools that support caching (Claude API, OpenAI prompt caching, Gemini context caching) | Assume all providers cache automatically—they don't |
| Keep the cached prefix stable for as long as possible (hours, not minutes) | Tweak the system prompt every 5 minutes, invalidating the cache |
| For repo contexts: load CLAUDE.md / conventions once, reuse the session | Re-paste the conventions with small edits each turn |
| Structure retrieval results so the stable part (file list) comes before the volatile part (diffs) | Interleave stable and volatile content throughout |

> **📌 Examples**
>
>
> - ✅ In Claude Code: long sessions benefit from caching automatically because the system prompt + `CLAUDE.md` stays stable across turns. Keep it stable—don't edit `CLAUDE.md` mid-session.
> - ✅ When building your own agentic loop: system prompt = `"You are a code reviewer. Project conventions: {CONVENTIONS}. Reference file: {FILE}"` — all stable. User turn = `"Review this diff: {DIFF}"` — volatile. Order matters.
> - ✅ OpenAI prompt caching activates automatically for prompts ≥1024 tokens with a stable prefix; just make sure your prefix *is* stable.
> - ✅ Google Gemini's context caching lets you explicitly cache a body of content and reference it across many calls—useful for big-monorepo Q&A loops.
>
> **Expected impact.** 50–90% cost reduction on the cached prefix portion; 5–85% latency reduction. Most effective on multi-turn sessions with stable context.
>

---

## 9. Skills, tools & output control levers (F)

### 9.1. Skills & persistent agent workflows

**Definition.** Pre-defined, named workflows (skills, custom commands, slash commands) that bundle a system prompt + toolset + output format into one callable unit.

**Why it matters for coding agents.** Instead of re-explaining "review this PR for X, Y, Z" every time, you define a `/review-pr` skill once. Each call skips the 500-token preamble and goes straight to the work. Skills also constrain the model to a fixed toolset, which prevents context bloat from tool descriptions.

**What it reduces.** Input tokens (no re-explaining) and improves consistency across calls.

| ✅ Do | ❌ Don't |
|----|-------|
| Define a skill for any workflow you run 3+ times | Re-type the same 200-word instruction every session |
| Pin the toolset inside the skill (e.g., only `read_file` + `grep`) | Let the skill call any tool — expands tool-description context |
| Version skills in git alongside the codebase | Hardcode skills in your shell history |
| Compose skills: `/review-pr` calls `/lint` + `/test` | Build one mega-skill that does everything |
| Share skills across the team via `.claude/skills/` or similar | Keep skills local to your machine |

> **📌 Examples**
>
>
> - ✅ Claude Code: define `.claude/skills/pr-review.md` with `name: pr-review`, `tools: [read_file, grep, git_diff]`, and `prompt: "Review the diff for bugs, security, and style. Return JSON: {severity, file, line, issue}."`. Invoke with `/pr-review`.
> - ✅ Cursor: create a custom command in `.cursor/commands/review.mdc` that wraps the same logic.
> - ✅ Custom agent loop: store skills as YAML in `skills/` and have your orchestrator inject them by name.
>

**Tools that implement this lever**: Claude Code Skills (`.claude/skills/`), Cursor Commands (`.cursor/commands/*.mdc`), Continue.dev custom commands, Aider conventions + `--read`, custom system prompts in any agent framework, ChatGPT custom GPTs / Anthropic Projects.

**Expected impact.** 30–60% on repeated workflows; consistency gains are often the bigger win.

---

### 9.2. Tool set restriction per turn

**Definition.** Dynamically limiting which tools the agent can call in a given turn or sub-agent.

**Why it matters for coding agents.** Every tool you expose has a description that goes into the context (often 50–500 tokens each). Expose 20 tools "just in case" and you've burned 5–10k tokens on tool descriptions alone — every turn. Worse, the model sometimes calls the wrong tool just because it's available.

**What it reduces.** Input tokens (less tool-description payload) and prevents wrong-tool calls (saves retry loops).

| ✅ Do | ❌ Don't |
|----|-------|
| Expose only the tools the task needs | Load every available MCP server "for flexibility" |
| For exploration: just `grep` + `read_file` | Always expose `bash` + `write_file` + `edit_file` together |
| For editing: `read_file` + `edit_file` only | Include `web_search` when the task is purely local |
| Use sub-agents with scoped toolsets | Run everything through one mega-agent with all tools |
| Disable tools the agent keeps misusing | Re-enable a misused tool hoping "it'll learn" |

> **📌 Examples**
>
>
> - ✅ Claude Code: use `--allowedTools "Read Grep Glob"` to restrict to read-only tools for an exploration sub-task.
> - ✅ Custom agent loop: define tool groups (`explorer_tools`, `editor_tools`, `planner_tools`) and switch per phase.
> - ✅ OpenAI Assistants API: pass different `tools` arrays per request based on the task type.
>

**Tools that implement this lever**: Claude Code `--allowedTools`, OpenAI Assistants API `tools` parameter, LangChain `AgentExecutor(tools=...)`, any agent framework that lets you scope tools, MCP server per-request tool filtering.

**Expected impact.** 5–15% on tool-heavy setups; bigger win is preventing wrong-tool calls.

---

### 9.3. Repo graph & structural code tools

**Definition.** Tools that build a structural map of the codebase (call graph, AST, symbol index) the agent can query instead of reading files.

**Why it matters for coding agents.** "Who calls `processPayment`?" should return a 5-line answer, not require reading 20 files. Graph/AST tools give the agent a bird's-eye view in O(1) queries instead of O(N) file reads — often the difference between a 2k-token exploration and a 50k-token one.

**What it reduces.** Input tokens (dramatic on navigation tasks) and improves quality (less noise, better structural understanding).

| ✅ Do | ❌ Don't |
|----|-------|
| Use ast-grep for structural search: `processPayment($$$)` finds all call sites | Use regex `processPayment` and get false positives in strings/comments |
| Build a tree-sitter symbol index once per session | Have the agent re-grep the whole repo for every query |
| Use ctags/universal-ctags for fast symbol jumps | Manually `find` and `grep` for symbol definitions |
| Generate a repo-map (file tree + signatures only) for context | Paste 30 file headers to "show the structure" |
| Use LSP integration for go-to-definition / references | Re-implement symbol lookup in prompts |

> **📌 Examples**
>
>
> - ✅ Aider: uses tree-sitter to build `repo-map.txt` (just signatures, ~5% of full codebase size) and injects it as context. Result: agent knows the structure without reading files.
> - ✅ ast-grep: `ast-grep -p 'processPayment($$$)' -r '$$1'` lists all call sites with arguments, no false positives.
> - ✅ Universal-ctags: `ctags -R .` generates a `tags` file; the agent can `readtag processPayment` for instant location.
> - ✅ Cursor: built-in `@codebase` uses a hybrid symbol + embedding index.
> - ✅ Custom: run `tree-sitter parse` over the repo, store signatures as JSON, expose via MCP tool.
>

**Tools that implement this lever**:
- **Graphify / code-graph tools**: build call/dependency graphs from source — CodeGraph, git-graph, dependency-cruiser, madge (JS), pydeps (Python)
- **ast-grep** (https://ast-grep.github.io): structural code search using AST patterns
- **Universal-ctags** (https://github.com/universal-ctags/ctags): fast symbol index, language-agnostic
- **tree-sitter** (https://tree-sitter.github.io): incremental AST parsing, 200+ grammars
- **LSP / Language Server Protocol**: go-to-definition, find-references, hover — works with any LSP-enabled editor
- **Aider's repo-map**: tree-sitter-based signature map, built in
- **Sourcegraph**: code search + navigation at scale (self-hosted or cloud)
- **Cursor's `@codebase`**: hybrid symbol + embedding index, built in
- **ripgrep** (https://github.com/BurntSushi/ripgrep): fast regex search — not AST-aware but very fast
- **CTagsComplete / lsp-bridge**: editor-side completion from ctags/LSP

**Expected impact.** 50–80% on navigation-heavy tasks; the single best lever for large-repo work.

---

### 9.4. Caveman mode & ultra-terse output styles

**Definition.** Forcing the agent to reply in minimal, code-only, no-prose formats — sometimes literally "caveman speak" (just `file:line`, just the diff, just the function name).

**Why it matters for coding agents.** Default LLM output is conversational: *"Sure! Here's the function you requested..."* followed by the code, followed by *"Let me know if you need anything else!"* That's 80% waste. Caveman mode cuts it to: `auth.ts:42: if (!user) return null;`.

**What it reduces.** Output tokens (often 70–90%) and downstream input tokens when the output is fed back into the next turn.

| ✅ Do | ❌ Don't |
|----|-------|
| Use a system prompt like: *"Reply with ONLY the code. No prose. No markdown fences. No 'Here is...'"* | Accept default conversational style for tool-to-tool calls |
| For diffs: `"Output unified diff. No preamble."` | Get a 3-paragraph explanation before the diff |
| For lookups: `"Reply file:line only."` | Get a 200-word summary when you asked for a list |
| Use tool parsers that fail on prose → forces model to behave | Use lenient parsers that "extract" the answer from prose |
| Compose caveman tools: a `grep` MCP tool that returns just `file:line:match` | Let tools return rich JSON with explanations baked in |

> **📌 Examples**
>
>
> - ✅ Caveman system prompt: `"You are a code-finding agent. Reply ONLY with file:line:snippet. No commentary. No greeting. No summary. If multiple matches, list each on its own line. NO PROSE."`
> - ✅ Diff mode: `"Output unified diff format only. No \`\`\`diff fences. No 'Here is the fix:' intro. No 'This change...' explanation. Diff lines ONLY."`
> - ✅ Tool-design caveman: define an MCP `find_usages` tool whose return type is `string` (not `object`), format `"file:line"`, schema-validated to reject prose.
> - ✅ Custom agent: post-process the model's output through a regex `^\s*(file:\d+).*$` filter — if it doesn't match, retry with `"Output must match file:line format"`.
>

**Tools that implement this lever**:
- **Caveman / minimal-output prompts**: any agent — just system-prompt it
- **Aider's `--no-pretty` / `--no-fancy-input`**: strips conversational output
- **OpenAI Structured Outputs** (https://openai.com): schema-enforced JSON, no prose possible
- **Anthropic's tool_use with strict schemas**: forces tool-call format
- **Custom MCP tools with strict return types**: schema validation rejects prose
- **Instructor / Outlines / BAML**: framework-level structured output enforcement
- **`outlines` / `lm-format-enforcer`**: logit-level format forcing (regex, JSON schema)
- **lm-sys / short-mode community prompts**: shared terse-mode system prompts

**Expected impact.** 70–90% on output tokens; especially powerful in agentic loops where output feeds into next turn.

---

### 9.5. Tool call batching & parallelism

**Definition.** Calling multiple independent tools in a single turn (parallel) instead of sequentially across turns.

**Why it matters for coding agents.** Each sequential tool call costs a full round-trip (request → response → next request). If the agent needs to grep for 5 symbols, doing it in 5 turns = 5 round-trips = 5× latency and 5× accumulated context. Parallel = 1 turn.

**What it reduces.** Latency (often 5× improvement) and input tokens (less accumulated context across fewer turns).

| ✅ Do | ❌ Don't |
|----|-------|
| Batch independent reads: "Read these 3 files at once" | Read file 1, then file 2, then file 3 in sequence |
| Use parallel tool calling when the model supports it | Force one tool per turn out of caution |
| Group lookups: "Find all 5 symbols, return as JSON list" | Ask for one symbol at a time |
| Plan upfront: list all needed reads, batch them | Let the agent "discover" what it needs turn-by-turn |
| For independent edits: spawn parallel sub-agents | Serialize 5 file edits that touch different files |

> **📌 Examples**
>
>
> - ✅ Claude Code / Cursor: prompt the agent with *"Read `auth.ts`, `models/user.ts`, and `routes/login.ts` in parallel, then propose a fix."* — the agent issues 3 parallel `read_file` calls in one turn.
> - ✅ OpenAI Assistants API: pass `parallel_tool_calls=true` and the model batches independent calls.
> - ✅ Custom agent loop: in the system prompt, allow `"You may call multiple tools in one turn when independent."`
> - ✅ Parallel grep: *"Run these 3 greps in parallel: `audit\(`, `log\(`, `trace\(`. Return as JSON: {pattern, matches: [{file, line}]}."*
>

**Tools that implement this lever**:
- **OpenAI parallel tool calls**: native API support (set `parallel_tool_calls=true`)
- **Anthropic parallel tool use**: native API support in `tool_use` content blocks
- **Claude Code**: parallel tool calls in one turn when prompt allows
- **Cursor Composer**: parallel sub-task spawning for mechanical edits
- **LangGraph / AutoGen / CrewAI**: framework-level parallel branches
- **Aider's architect mode**: separate planning + implementation agents

**Expected impact.** 3–5× latency improvement on multi-tool tasks; 30–50% token reduction on accumulated context.

---

### 9.6. Token budgeting & live counting

**Definition.** Using token counters (tiktoken, Anthropic's counter, Gemini's) to measure and budget token usage in real time, and adjusting prompts/toolsets before hitting limits.

**Why it matters for coding agents.** Without a counter, you discover context overflow only when the model starts dropping instructions or returning errors. With one, you can: shrink context proactively, switch to a smaller model, summarize earlier, or abort doomed tasks before wasting tokens.

**What it reduces.** Failed runs (which waste 100% of tokens) and enables proactive compaction.

| ✅ Do | ❌ Don't |
|----|-------|
| Count tokens before sending: `tiktoken.count(prompt)` | Discover overflow only when the model returns an error |
| Log per-turn token usage to find the worst offenders | Run blind, hope the budget holds |
| Set thresholds: at 60% of context, trigger `/compact` | Wait until 100% and lose the conversation |
| Show the agent its own usage: *"You are at 70% of context. Summarize now."* | Let the agent obliviously keep going past 100% |
| Per-tool: count tool output sizes, prune the largest | Treat all tool outputs as equal in budget |

> **📌 Examples**
>
>
> - ✅ Python: `import tiktoken; enc = tiktoken.encoding_for_model("gpt-4"); count = len(enc.encode(prompt_text))`
> - ✅ Anthropic: `import anthropic; client.messages.count_tokens(...)` for full message format
> - ✅ Custom agent loop: wrap every tool call with `before = count_tokens(context); result = tool(); after = count_tokens(result); if after > 5000: result = summarize(result)`.
> - ✅ Claude Code: use `/context` to see current context usage; auto-compact at thresholds.
> - ✅ Cursor: the context indicator at the top shows live usage — watch it.
>

**Tools that implement this lever**:
- **tiktoken** (https://github.com/openai/tiktoken): OpenAI token counter, fast, Rust-backed
- **anthropic-sdk `count_tokens`**: Anthropic's official counter
- **google-generativeai `count_tokens()`**: Gemini's counter
- **LangChain `len()` on messages**: framework-level counting
- **Claude Code `/context`**: live usage display in CLI
- **Cursor context indicator**: live usage bar in UI
- **llm-cost / token-budget / literal-ai tracing libs**: cost + budget + tracing
- **LangSmith / Helicone / Langfuse**: observability platforms with per-turn token breakdowns

**Expected impact.** Prevents 5–20% wasted runs; enables proactive compaction (which multiplies with lever 4).

---

## 10. Closing — the high-ROI habits

If you do nothing else from this guide, adopt these seven habits. They cover ~80% of the wins.

**Quick-start checklist**

1. **One task per chat.** Start a fresh session when the task is done. Don't pile.
2. **Compact or summarize before a session passes ~20 turns.** Use `/compact` (Claude Code) or "summarize then restart" (Cursor, Copilot).
3. **Never paste whole files.** Pass symbols (`@function`), line ranges, or ask the agent to search.
4. **Maintain `CLAUDE.md` / `.cursorrules` / `AGENTS.md`.** ≤300 lines, top of file = most important rules. Commit it like code.
5. **Maintain an ignore file** (`.cursorignore` / `.aiderignore`) mirroring `.gitignore` *plus* lockfiles, `dist/`, `*.min.js`.
6. **Constrain outputs.** Default to "diff only, no prose." Pin JSON schemas when parsing matters.
7. **Right-size the model.** Small for autocomplete and mechanical edits; flagship for design and tricky bugs.

**Bonus from Section F (highest ROI of the new levers)**

8. **Install a structural code tool** — ast-grep or universal-ctags. Lets the agent answer "who calls X?" in 5 lines instead of reading 20 files. (Lever 15)
9. **Caveman your agentic loops** — system-prompt sub-agents to reply `file:line` only, no prose. 70–90% output savings in tool-to-tool flows. (Lever 16)
10. **Watch your token counter** — Claude Code's `/context`, Cursor's usage bar, or `tiktoken.count()` in your own scripts. Compact at 60%, not 100%. (Lever 18)

---

### Techniques compound

The biggest mental shift is this: token efficiency isn't a one-time optimization, it's a **per-turn multiplier**.

A session that runs 30 turns at 50k tokens each = 1.5M input tokens. Shave 30% off via context hygiene and you're at 1.05M. Add a 70% reduction on tool outputs in debug loops and you're at ~315k. Add prompt caching on the stable prefix and your *cost* drops another 5–10x, even though raw bytes are similar.

Small wins per turn multiply across long agentic sessions. A 10% saving per turn becomes a 60%+ saving over a 30-turn session, because each turn's savings also shrink the base the next turn re-reads.

Start with the quick-start checklist. Once those are habits, come back and pick off the next lever that matches your biggest current pain point (cost? latency? quality drift on long sessions?). The levers stack—none of them conflict, and the order of adoption is yours.

---

## Appendix A — Tools quick-reference

A consolidated index of every tool mentioned in this handbook, grouped by lever.

**Lever 6 — Repo memory files**
- `CLAUDE.md`, `.cursorrules`, `AGENTS.md`, `.github/copilot-instructions.md`, `WINDSURF_RULES`, `CONVENTIONS.md` (Aider)

**Lever 15 — Repo graph & structural code tools**
- **ast-grep** — https://ast-grep.github.io — structural code search via AST patterns
- **Universal-ctags** — https://github.com/universal-ctags/ctags — fast symbol index
- **tree-sitter** — https://tree-sitter.github.io — incremental AST parsing, 200+ grammars
- **LSP** — https://microsoft.github.io/language-server-protocol/ — go-to-def, find-refs, hover
- **Aider repo-map** — built-in tree-sitter-based signature map
- **Sourcegraph** — https://sourcegraph.com — code search + navigation at scale
- **Cursor `@codebase`** — built-in hybrid symbol + embedding index
- **ripgrep** — https://github.com/BurntSushi/ripgrep — fast regex search
- **Graphify / code-graph tools** — CodeGraph, dependency-cruiser, madge (JS), pydeps (Python)

**Lever 16 — Caveman / structured-output tools**
- **OpenAI Structured Outputs** — https://openai.com — schema-enforced JSON
- **Anthropic tool_use strict schemas** — https://docs.anthropic.com — forces tool-call format
- **Instructor** — https://github.com/jxnl/instructor — framework-level structured output
- **BAML** — https://baml.com — typed LLM function calls
- **outlines** — https://github.com/outlines-dev/outlines — logit-level format forcing
- **lm-format-enforcer** — https://github.com/noamgat/lm-format-enforcer — regex/JSON schema enforcement
- **Aider `--no-pretty` / `--no-fancy-input`** — strips conversational output

**Lever 17 — Parallel tool calling**
- **OpenAI parallel tool calls** — set `parallel_tool_calls=true`
- **Anthropic parallel tool_use** — native in `tool_use` content blocks
- **LangGraph** — https://github.com/langchain-ai/langgraph — framework-level parallel branches
- **AutoGen** — https://github.com/microsoft/autogen — multi-agent parallelism
- **CrewAI** — https://github.com/crewAIInc/crewAI — role-based parallel agents

**Lever 18 — Token budgeting & observability**
- **tiktoken** — https://github.com/openai/tiktoken — OpenAI token counter, Rust-backed
- **anthropic-sdk `count_tokens`** — Anthropic's official counter
- **google-generativeai `count_tokens()`** — Gemini's counter
- **LangSmith** — https://smith.langchain.com — observability + per-turn breakdown
- **Helicone** — https://helicone.ai — logging + cost tracking
- **Langfuse** — https://langfuse.com — open-source observability
- **Claude Code `/context`** — live usage display in CLI
- **Cursor context indicator** — live usage bar in UI

---

*End of handbook.*
