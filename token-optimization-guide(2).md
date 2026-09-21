# AI Coding Agent Token Optimization — The Complete Practitioner Guide

> **Scope:** Techniques to cut token consumption (and therefore cost) across GitHub Copilot, Claude Code, Cursor, Codex CLI, and similar AI coding agents — without sacrificing code quality.
>
> **Source basis:** Synthesized from [olivomarco/github-copilot-token-optimization](https://github.com/olivomarco/github-copilot-token-optimization) (community field guide, 13 chapters + workshop material) and ~35 similar repositories, tools, and research projects identified via GitHub search, topic graphs, and cross-references (verified September 2026).
>
> **Disclaimer:** Figures marked *(vendor-reported)* come from the projects themselves and have not been independently benchmarked. Star counts are approximate as of Sep 2026.

---

## Table of Contents

1. [Why Tokens Are Now Money](#1-why-tokens-are-now-money)
2. [Token Cost Anatomy — Where Your Budget Actually Goes](#2-token-cost-anatomy--where-your-budget-actually-goes)
3. [The Source Repo at a Glance](#3-the-source-repo-at-a-glance)
4. [Technique Playbook](#4-technique-playbook)
   - 4.1 [Output Control (highest ROI)](#41-output-control--highest-roi)
   - 4.2 [Prompt Compression](#42-prompt-compression)
   - 4.3 [Context Management & Caching](#43-context-management--caching)
   - 4.4 [Always-On Instruction Files: The "Landmines Only" Rule](#44-always-on-instruction-files-the-landmines-only-rule)
   - 4.5 [MCP & Tool Costs: The Hidden Tax](#45-mcp--tool-costs-the-hidden-tax)
   - 4.6 [Workflow Optimization: Modes, Planning, Routing](#46-workflow-optimization-modes-planning-routing)
   - 4.7 [Language & Format Efficiency](#47-language--format-efficiency)
   - 4.8 [Enterprise Governance](#48-enterprise-governance)
   - 4.9 [Outcome per Token: Stop Minimizing, Start Valuing](#49-outcome-per-token-stop-minimizing-start-valuing)
5. [Similar Repos & Tools — The Ecosystem Map](#5-similar-repos--tools--the-ecosystem-map)
6. [Choosing Your Stack: Decision Matrix](#6-choosing-your-stack-decision-matrix)
7. [The Complete Technique Matrix](#7-the-complete-technique-matrix)
8. [Anti-Patterns — What Actively Wastes Tokens](#8-anti-patterns--what-actively-wastes-tokens)
9. [Measurement: Baseline Before You Optimize](#9-measurement-baseline-before-you-optimize)
10. [4-Week Adoption Plan](#10-4-week-adoption-plan)
11. [Research Backing & Further Reading](#11-research-backing--further-reading)

---

## 1. Why Tokens Are Now Money

**June 1, 2026 changed everything.** GitHub Copilot moved from premium-request counters (PRUs with model multipliers) to **Usage-Based Billing (UBB)**: real tokens — input, output, and cached — are billed against pooled AI credits (1 AI credit = $0.01). Plans include a pooled allowance (**$30/seat/month Business, $70/seat/month Enterprise**) with optional budgets for overage ([GitHub Docs: what changed with billing](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/what-changed-with-billing)).

Three pricing facts drive every technique in this guide:

| Fact | Detail | Consequence |
|---|---|---|
| **Output costs ~5× input** | Anthropic public pricing: $1/$5 (Haiku), $3/$15 (Sonnet), $5/$25 (Opus) per MTok input/output. Copilot's per-model table mirrors this asymmetry (e.g., Gemini 3.5 Flash: $1.50 in / $9.00 out; promo Gemini 3.6–3.8 Flash: $0.75 in / $3.75 out through Dec 31, 2026) | **Output control is the #1 lever.** One instruction line saves on every call forever |
| **Cached input is ~10× cheaper** | Anthropic: cache reads at 0.1× input (explicit `cache_control`, 1,024-token minimum, 1.25× write for 5-min TTL). OpenAI: automatic, 0.5× discount. Copilot caches the stable prefix (system prompt + tools + instructions) | **Cache stability is a hard constraint** in long sessions. Don't churn the prefix |
| **Input tokens are mostly invisible** | Your typed prompt is a tiny fraction. File context, conversation history, instruction files, and tool schemas dominate input | **Structural wins** (context pruning, MCP audits) beat prompt-wordsmithing |

> Example Copilot model pricing from [GitHub Docs: Models and pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) (per 1M tokens): Gemini 3.5 Flash — $1.50 input / $0.15 cached / $9.00 output. Cached input is **10× cheaper** than fresh input on this tier.

---

## 2. Token Cost Anatomy — Where Your Budget Actually Goes

For a typical agent task (15 steps), token consumption breaks down roughly as:

```text
┌────────────────────────────────────────────────────────────────┐
│ WHAT GETS BILLED PER AGENT TASK                                │
├────────────────────────────────────────────────────────────────┤
│ Tool/MCP schemas      ██████████████████  ~5K–18K per STEP     │
│ (reloaded every step)                    → 75K–265K per task   │
│                                                                │
│ Always-on instructions ███               ~50–1,500 per step    │
│ (copilot-instructions, AGENTS.md, CLAUDE.md)                   │
│                                                                │
│ File reads / grep /    █████████         varies; orientation   │
│ shell output                             reads dominate large  │
│                                          repos                 │
│                                                                │
│ Conversation history   ███████           grows every turn,     │
│                                          replayed each step    │
│                                                                │
│ YOUR TYPED PROMPT      █                 ~10–50 tokens         │
│                                                                │
│ Model OUTPUT           ██████            5× price per token    │
│ (code + explanations)                    ← explanations are    │
│                                            pure waste unless   │
│                                            explicitly asked    │
└────────────────────────────────────────────────────────────────┘
```

Real-world data point: a Microsoft/GitHub contributor measured a production Copilot CLI setup with `/context` and found **a single Azure plugin loading ~27K tokens per message** — invisible until measured ([writeup](https://dfberry.github.io/2026-05-06-tuning-up-copilot-context)).

**Inspect your own baseline right now** (Copilot CLI):

```text
/context

Context Usage  claude-opus-4.6 · 104k/200k tokens (52%)
System/Tools:  62.5k (31%)   ← always-loaded: MCPs + instructions + system prompt
Messages:      41.8k (21%)   ← conversation history
Free Space:    55.3k (28%)
Buffer:        40.4k (20%)
```

Everything in `System/Tools` is billed on **every step** of **every task** — and it is also your cacheable prefix. That dual role makes it the most important number in your setup.

---

## 3. The Source Repo at a Glance

**[olivomarco/github-copilot-token-optimization](https://github.com/olivomarco/github-copilot-token-optimization)** (⭐~159, 20 forks, MkDocs site, 18-slide practitioner briefing + 8-hour workshop) is a community field guide — explicitly *not* official GitHub/Microsoft guidance — structured as:

| Part | Chapters | Core content |
|---|---|---|
| **1. Why Tokens Matter** | 01 | BPE tokenization, cost/speed/limit mechanics, how Copilot consumes tokens behind the scenes |
| **2. The Techniques** | 02–08 | Prompt compression (caveman-speak), language comparison, context management & caching, output control, workflow optimization, the always-on context problem (`AGENTS.md` research), MCP & tool costs |
| **3. Comparisons & Data** | 09 | Head-to-head prompt comparisons, 8-language tokenization tables, 40+ technique matrix, quality-impact curve |
| **4. Practical Setup** | 10 | VS Code settings, coding-agent config, MCPs-vs-skills (eager vs lazy loading), decision frameworks, 4-week adoption plan |
| **Companions** | 11–13 | Model selection & pricing under UBB; enterprise governance (budgets, FinOps-as-code); outcome-per-token |

Its own `.github/copilot-instructions.md` practices what it preaches — **6 lines, ~50 tokens**:

```text
Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles, filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift.
Code/commits/PRs: normal. Off: "stop caveman" / "normal mode".
```

Compare typical `/init`-generated output: **200+ lines, ~1,500 tokens** — that's ~1,450 wasted tokens *per interaction*, and per the ETH Zurich research (§4.4) it likely makes agents **worse**, not better.

---

## 4. Technique Playbook

### 4.1 Output Control — Highest ROI

Output tokens cost ~5× input. These instructions, placed once in your instructions file, save 40–70% of output on every code task, permanently:

```text
Code only, no explanation.
Bullets over paragraphs. No explanations unless asked.
```

**Format constraints and their effect:**

| Instruction | Output savings |
|---|---|
| "Answer in one sentence" | ~60–80% |
| "3 bullet points max" | ~50–70% |
| "Reply as JSON" | ~30–60% |
| "Table format" | ~40–60% |
| "Yes or no, then one line why" | ~70–90% |
| "Ask for diffs, not full-file rewrites" | ~50–90% on modifications |

**When to override:** learning, debugging, architecture discussions — just ask ("Explain why this approach beats X"). Terse defaults don't prevent explanations on explicit request.

**Anthropic's API-level equivalent:** the `token-efficient tool use` flag / token-efficient-tools beta reduces tool-call verbosity by **14–70%** *(vendor-reported)* — flip it if you build agents on the Claude API.

---

### 4.2 Prompt Compression

**Caveman-speak** — drop linguistic scaffolding that adds tokens without information:

- **Drop:** articles (a/an/the), filler (just, really, basically, actually), pleasantries, hedging ("I think maybe…")
- **Keep:** exact technical terms, code, specificity
- **Pattern:** `[thing] [action] [reason]. [next step].`

```text
Verbose  (~40 tok): "Hey, could you please help me refactor this function? I think
                     it might have some issues with how it handles the authentication,
                     and I'd really like it to be more efficient. Thanks!"
Caveman  (~10 tok): "Refactor function. Fix auth handling. Make efficient."
```

**Three intensity levels:**

| Level | Style | Input savings | Output savings¹ | Quality risk |
|---|---|---|---|---|
| **Lite** | professional but tight; drop filler/hedging, keep sentences | 15–25% | 15–25% | None |
| **Full** (default sweet spot) | drop articles, fragments OK, short synonyms | 30–50% | 40–55% | Negligible |
| **Ultra** | abbreviations, arrows for causality ("Inline obj prop → new ref → re-render. useMemo.") | 55–70% | 55–70% | Ambiguity in complex instructions |

¹Output savings only materialize when combined with system-level terse-output instructions (§4.1). Terse prompts alone don't make models terse.

**Head-to-head (same task: "add error handling"):** six phrasings from verbose English (~40 tok) to ultra caveman (~7 tok) all produced correct code — a **5.7× cost difference for identical results**.

**Structured over prose** (~36% savings, and clearer):

```text
POST /api/users
Validate:
- name: string, required
- email: string, required, valid format
400 on validation fail (include errors)
201 on success (return created user)
Save to DB
```

**Code-centric prompting** — pseudocode/type signatures beat natural language descriptions:

```text
Natural (~30 tok): "Create a function that takes a list of numbers, filters out the
                    negative ones, doubles each remaining number, and returns the sum."
Pseudocode (~15):  fn(nums) → filter(>0) → map(*2) → sum
Type sig (~12):    def process(nums: list[int]) -> int:  # filter positive, double, sum
"Like X but Y":    Like getUserById but for emails. Return 404 if missing.  (~10)
```

**Declarative guardrails over imperative procedures** — invariants stack cleanly, procedures interfere:

| Imperative (~25 tok) | Declarative (~10 tok) |
|---|---|
| "First read the file, then identify all the public functions, then for each one check whether it has a JSDoc comment, and if it doesn't, add one." | `All exported functions: JSDoc required.` |
| "Make sure that whenever you write a SQL query you always parameterize the values…" | `SQL: parameterized queries only. No concatenation.` |
| "Please write tests for any new code… cover happy path and error cases." | `New code → tests. Cover happy + error paths.` |

**Safe abbreviations** (1 token vs 2–3): DB, auth, config, req/res, fn, impl, env, deps, repo, PR, e2e. *Novel/project-specific shorthand must be defined in the instructions file first.*

**Academic ceiling** — for programmatic compression at scale (RAG pipelines, bulk prompts): Microsoft's **LLMLingua** achieves up to **20× prompt compression** with minimal performance loss; **Chain of Draft** reasoning uses only **7.6% of CoT tokens**; Concise-CoT cuts reasoning length ~48.7% at negligible quality loss. See §5.7 and §11.

---

### 4.3 Context Management & Caching

**a) Scope with `applyTo:` paths.** Split one giant instructions file into small scoped ones that load only when relevant:

```markdown
---
applyTo: "src/api/**"
---
REST endpoints: validate request bodies. Return 400 with error details.
```

Shared conventions → one `applyTo: "**/*"` file; per-layer specifics → scoped files; workflow guidance → on-demand notes/prompt files.

**b) Close unused editor tabs / detach unused context.** Open files feed the context picker. Choose your context up front and don't churn it.

**c) Start fresh conversations.** New topic → new chat. Long histories replay every turn; ~80%+ of history tokens vanish with a fresh session plus a 5-line handoff summary.

**d) Convert rich files to Markdown before AI work.** `.docx/.pdf/.pptx/.xlsx/HTML` carry a "format tax" — Marc Bara measured **~33% budget waste** on a cited DOCX. Use [microsoft/markitdown](https://github.com/microsoft/markitdown) (⭐~186k) to normalize before chat/agent/RAG ingestion.

**e) Persistent codebase graphs.** On large repos, agents burn most input on *orientation reads*. Build the map once, query it many times:

```bash
uv tool install graphifyy     # Graphify-Labs/graphify
graphify build                # writes graphify-out/graph.json (tree-sitter AST)
# agents query the graph instead of re-reading structural files each session
```

*(Vendor-reported: 6.8× average, up to 71.5× on structural-navigation best cases — treat high end as best case, not guarantee.)* Alternatives: `code-review-graph`, `claude-context` (hybrid BM25 + dense vectors), `jcodemunch-mcp` (symbol-level AST retrieval) — see §5.3.

**f) Caching — the biggest lever in long sessions.** Cached input can be billed at ~10% of standard rate (Anthropic) or 50% (OpenAI). Copilot caches the stable prefix: system prompt + tool/MCP definitions + instruction files.

**The cache-stability tuple — pick it before work starts, hold it fixed all thread:**

```text
{ model, reasoning effort, loaded skills, active MCP/tool set, agent/profile }
```

| Mid-session change | Effect |
|---|---|
| Switch model / reasoning effort | Caches are per-model; prefix discarded; carried history re-billed in the new lane |
| Switch custom agent | System prompt + tools swap → cache invalid; prior context becomes pollution |
| Toggle MCP servers / tools / skills | Prefix rewritten → cache invalidated + always-loaded tokens change |
| Attach/detach big files, paste blobs | Reshuffles context, undercuts prefix stability |

**Safe handoff pattern:** if you genuinely need a different lane, start a **fresh chat** with only a short summary + relevant files. Never mutate a long, expensive thread.

Prompt structure rule (API builders): *static content first (system prompt, tool defs, docs), volatile content last (user query, session data).* Inserting a timestamp or user ID at the top breaks every cache hit downstream.

---

### 4.4 Always-On Instruction Files: The "Landmines Only" Rule

`AGENTS.md` (cross-tool), `.github/copilot-instructions.md` (Copilot-native), and `CLAUDE.md` (Claude Code) are **distinct conventions with the same cost profile**: every token is billed on every interaction *and every agent step*.

**The research (ETH Zurich, AGENTBENCH, Feb 2026 — 138 tasks, 12 repos, 4 agents):**

| Finding | Data |
|---|---|
| LLM-generated context files hurt performance | declined in 5/8 experimental settings |
| Average correctness change | **−2%** |
| Cost with LLM-generated context | **+20–23% tokens** |
| Reasoning overhead (GPT-5.2) | +22% reasoning tokens |

Human-written files: ~4% average improvement, inconsistent; Claude Code got *worse*. File-discovery rates identical with or without — **agents already know how to `ls` and `grep`.**

**Four mechanisms why more context hurts:**

1. **Redundancy tax** — context files repeat what the agent reads from code anyway (double tokens, zero new info)
2. **Attention tax** — U-shaped attention ("Lost in the Middle", Liu et al. 2023): lines 50–150 of a 200-line file get ignored
3. **Anchoring trap** — agents follow context-file instructions too faithfully; a mentioned tool gets used **1.6× more**, even when a better tool exists
4. **Signal dilution** — routine facts crowd out high-value cautions

**The filter (Addy Osmani, Google):**

> "Can the agent discover this on its own by reading your code? If yes, delete it."

| Keep (landmines) | Delete (discoverable) |
|---|---|
| "Use `uv` instead of `pip`" | "This is a Python project" |
| "Run tests with `--no-cache`" | "Tests are in the `tests/` directory" |
| "Don't refactor the auth module" | "We use JWT for authentication" |
| "Deploy requires VPN" | "Main branch is protected" |
| "DB migrations must run in order" | "We use PostgreSQL" |

**Bug-tracker workflow:**

```text
Start with almost empty file.
Agent trips on something → add ONE line.
Root cause gets fixed → DELETE that line.
If it only grows, you're doing it wrong.
```

Claude Code specifics (from `claude-cost-optimizer`): keep `CLAUDE.md` **under ~4,000 characters** — content beyond that is silently truncated in some surfaces, so you pay for tokens that never help. Add `.claudeignore` (or Copilot Content Exclusion for Business/Enterprise admins) so `node_modules`, `dist`, and lockfiles never enter context.

---

### 4.5 MCP & Tool Costs: The Hidden Tax

**Every enabled tool's full definition loads into context on every agent step:**

| Component | ~Tokens |
|---|---|
| Tool name + description | 20–50 |
| Parameter schema (simple) | 30–80 |
| Parameter schema (complex) | 100–300 |
| **Total per tool** | **100–500** |

**The multiplication problem:**

```text
10 MCP servers × 5 tools × 200 tok avg = 10,000 tokens/step
× 15 agent steps = 150,000 tokens just announcing which tools exist
```

**Worked before/after audit:**

| Setup | Servers | Tools | Tok/step | 15-step task |
|---|---|---|---|---|
| "I enabled everything" | 15 (GitHub, Docker, Postgres, Redis, Slack, Jira, AWS, GCP, K8s, Datadog, Email, Calendar, Brave, Context7, FS) | 187 | ~17,700 | **265,500** |
| "Only what coding needs" | 3 (GitHub, Context7, Filesystem) | 50 | ~5,000 | **75,000** |

**Savings: ~190K tokens per agent task (72% of schema overhead).**

**Audit checklist:**

1. Run `/context` (Copilot CLI) or count servers × tools × ~200 tok (VS Code) to get your `System/Tools` baseline
2. Disable unused MCP servers; enable per-task ("DB migrations today? Enable Postgres MCP. Done? Disable.")
3. Prefer built-in tools — VS Code's file read/write/terminal/search are already loaded; an MCP filesystem server on top is redundant
4. Configure per-workspace (`.vscode/mcp.json`), not globally
5. Keep a lean VS Code **profile** for coding sessions — extensions inject skills/agents/tool surfaces too
6. **Skills vs MCPs (eager vs lazy loading):** MCP schemas load on every step whether used or not; skills load only title+description upfront and pull full content on demand. If a capability is used in <50% of sessions → skill, not MCP
7. Add "Minimize tool calls. Read files only when necessary." to instructions
8. **Compress shell output at the source** — a failing `cargo test` or big `git diff` can dump 10–25K raw tokens. Filters before the agent reads:

| Tool | Mechanism | Claimed reduction |
|---|---|---|
| [rtk-ai/rtk](https://github.com/rtk-ai/rtk) (⭐~81k) | Rust CLI proxy; per-command filters (keep failing tests only, dedupe logs, group listings); rewrites `git status` → `rtk git status` | 60–90%: `ls/tree` −80%, `git status` −80%, `git diff` −75%, `cargo/npm test` −90%, `grep/rg` −80% *(vendor benchmarks, medium TS/Rust project)* |
| [edouard-claude/snip](https://github.com/edouard-claude/snip) (⭐~451) | Go CLI proxy; declarative YAML filters; rtk alternative for Claude Code/Cursor/Copilot/Gemini | 60–90% *(vendor-reported)* |
| [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) (⭐~73k) | Transparent proxy compressing tool outputs, logs, files, RAG chunks | ~20% overall for coding agents, 60–95% on JSON *(vendor-reported)* |
| `minimal-context-tools` (skills for `rg`, `fd`, `jq`, `yq`, `ast-grep`) | Steers agent to precise one-shot commands *before* large output exists | 70–95% on targeted search/query patterns *(tool-reported)* |

⚠️ **Do not stack multiple output filters on the same command path without measuring** — lost detail becomes rework, and rework costs more than the tokens you saved. RTK on Windows is pilot-grade (PowerShell/Git Bash/WSL path handling can be brittle).

9. **CodeAct for long tool chains** (Copilot CLI only): [jsturtevant/copilot-codeact-plugin](https://github.com/jsturtevant/copilot-codeact-plugin) collapses many small tool hops into **one sandboxed code execution** — plugin benchmarks report **49–69% input-token reduction** on exploration/audit sessions *(vendor-reported)*, since the system prompt + history + tool defs replay fewer times.

**Beyond 15 tools:** Anthropic's context-engineering guidance recommends **tool search / deferred loading** (agent searches a registry; matched definitions get appended to the conversation, *not* the cached prefix) and **programmatic tool calling** — both keep huge tool catalogs out of every request.

---

### 4.6 Workflow Optimization: Modes, Planning, Routing

**a) Ask vs Edit vs Agent — mode selection is free savings:**

| Situation | Mode | Savings |
|---|---|---|
| Question, explanation, lookup, syntax | **Ask** | 60–90% vs Agent (no tool loop, no step overhead) |
| Known small change in open file | **Edit/Inline** | avoids full agent harness |
| Multi-file, multi-step task | **Agent** | reserve for genuine multi-step work |

Agent mode's internal loop re-reads context every step — 5–25 steps per task. Every avoided step is one full context reload saved.

**b) Plan first, then execute in a fresh session (the two-phase pattern):**

```text
Phase 1 (strong model, plan mode/Ask): agree approach — files, order, edge cases,
                                        acceptance criteria → save to plan.md or an issue
Phase 2 (fresh session, cheaper model): execute against the saved plan
Phase 3: verify acceptance criteria
```

Why it wins: (1) fewer wasted steps — no exploring/guessing/backtracking; (2) cheaper execution lane — mechanical work runs on Auto/included models; (3) clean cache-friendly context — planning conversation isn't dragged through every execution turn. **The most expensive tokens are the ones spent reaching a wrong outcome.**

**c) Model routing defaults (Copilot under UBB):**

| Task | Choice |
|---|---|
| Syntax lookup, quick explanation, tiny edit | Included model or **Auto** |
| Typical implementation, bug fix, refactor | **Auto** (paid-plan discount on eligible usage, zero effort) |
| Architecture, threat modeling, novel decomposition | Manually pin premium model |
| Draft-then-polish | Cheap model drafts → premium polishes |

Anti-patterns: leaving a premium model pinned all session; assuming Auto escalates to premium when tasks get hard (it won't); switching models mid-chat without accounting for carried context.

**d) Retune prompts per model.** Provider prompting guides change by model/version. Paste the official guide URL into Copilot and ask it to adapt your instruction files / agent profiles for the model you actually use (~10 min per model change; cuts rework).

**e) Terse everything the agent reads:** commit messages (~5–15 tokens: `fix: null deref in getUser`), one-line PR review comments (60–80% output savings on reviews), precise issue descriptions for the Coding Agent (+ acceptance criteria = 30–60% savings).

**f) Copilot CLI feedback loops (experimental):** `/chronicle cost tips` (analyzes token spend, suggests reductions) and `/chronicle improve` (finds recurring misread intent in session history, generates instruction fixes so the same mistake stops costing tokens). Run weekly. *(Copilot CLI only — not VS Code Chat.)*

**g) Cap agent runs:** set `maxRequests`/step limits so runaway loops truncate instead of billing 25 steps.

---

### 4.7 Language & Format Efficiency

Tokenizers are English-optimized. Same sentence, different language (GPT-4 tokenizer):

| Language | Tokens | Cost vs English |
|---|---|---|
| English ("I met a huge dog") | 5 | 1.0× |
| Spanish / Polish | 8 | 1.6× |
| Icelandic | 10 | 2.0× |
| Chinese / Japanese | 11 | 2.2× |
| Russian | 14 | 2.8× |
| Hebrew | 16 | 3.2× |

Large-sample averages: Mandarin ~1.76×, Japanese ~2.12×, Korean ~2.36×, Russian ~2.5–2.8×. **Prompt in English; keep code/comments in English; let explanations be delivered in your language if needed** (output-side only).

**Classical Chinese (wenyan) compression is a trap:** measured **negative** savings — models understand it less reliably, causing rework. Demo only.

**The quality curve (diminishing returns):**

```text
Savings:  0% ──── 30% ──── 50% ──── 70% ──── 90%
Risk:     none     none    minor    real     rework
          └─ lite ─┘└─ full ─┘└ ultra ┘└ extreme ┘
                        ▲ sweet spot
```

**Threshold rule:** when you catch yourself re-explaining or getting wrong results, you compressed too far — back off one level. Rework costs more than the tokens you saved.

---

### 4.8 Enterprise Governance

Budgets don't shrink prompts — they cap spend. Combine both. (GitHub Docs: [usage-based billing for orgs](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises), [metered-product budgets](https://docs.github.com/en/billing/how-tos/budgets/setting-up-budgets-to-control-spending-on-metered-products).)

1. **Set budgets first** — org / enterprise / cost-center scope; enable alerts early; enable *stop usage at budget* once reporting looks sane; review monthly
2. **User-level AI-credit budgets** for per-user tightening; **$0 user budget = no UBB feature access** (clean kill-switch)
3. **Review models before enablement** — premium model access should expand intentionally, not by drift
4. **Org-level instructions in the right scope** — organization instructions load into every interaction org-wide; keep them landmines-only too
5. **FinOps-as-code:** [amgdy/copilot-finops-automation](https://github.com/amgdy/copilot-finops-automation) — one version-controlled YAML defines AI-credit spend policies + team→cost-center mappings; GitHub Actions validates, dry-runs, applies budgets idempotently, syncs membership, writes audit reports. Keep live config in a private repo
6. **Separate orgs** as spend-isolation workaround: works, but treat as caveated (identity/duplication overhead)
7. **Measure the right thing** — cost per *merged outcome*, not cost per prompt; spend cohorts (who/what burns credits) before optimizing

**Team reference numbers** (from `claude-cost-optimizer` before/after, Claude Code): system prompt ~15,000 → ~5,500 tok/turn; session cost $2.85 → $1.12; monthly (3 sessions/day) **$188 → $74 (61% savings)** from: CLAUDE.md < 4K chars, `.claudeignore` (12 patterns), MCP servers 6 → 2, Haiku for simple tasks, plan mode, subagent delegation.

---

### 4.9 Outcome per Token: Stop Minimizing, Start Valuing

The endgame isn't minimum tokens — it's **maximum merged value per token**. A $0.50 agent run that lands a correct PR beats a $0.05 run that produces rework.

- **Plan-first + acceptance criteria** converts spend into verified outcomes
- **Skills as reusable procedures** (not one-off prompts): small named playbooks the agent loads on demand
- **Guardrail skills** prevent the most expensive waste of all: wrong-direction work, leaked secrets, unsafe mutations, retry loops
- **Benchmark caveat:** vendor "×-reduction" claims are usually input-token or best-case-navigation numbers; validate on *your* tasks with *your* pass rates

Skill libraries worth borrowing structure from:

| Repo | ⭐ | Strength |
|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | ~289k | TDD, planning, verification, branch-finish discipline — reference pattern for skills-as-procedures |
| [mattpocock/skills](https://github.com/mattpocock/skills) | ~266k | TDD, bug diagnosis, code review, domain modeling |
| [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) | ~2.5k | Planning orchestration, handoff, entropy control for long sessions |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | ~43k | Browser QA without DOM floods — accessibility-tree snapshots over raw HTML |
| catpilotai/catpilot-ai-guardrails | — | Security/tool-loop guardrails before expensive mistakes |

---

## 5. Similar Repos & Tools — The Ecosystem Map

Beyond the source repo, the token-optimization ecosystem clusters into eight categories. (Stars ≈ Sep 2026; *v.r.* = vendor-reported claims.)

### 5.1 Knowledge Guides & Awesome Lists (closest analogues)

| Repo | ⭐ | What it is | Overlap with source repo |
|---|---|---|---|
| [Sagargupta16/claude-cost-optimizer](https://github.com/Sagargupta16/claude-cost-optimizer) | ~36 | 12 deep-dive guides (billing, context, model selection, caching TTL economics, 3-tier task routing, speed-vs-cost), 9 CLAUDE.md templates, token-estimator CLI, benchmarks | **Closest sibling for Claude Code** — same landmines-only + plan-mode + MCP-audit doctrine, with copy-paste configs and $ math |
| [pleasedodisturb/awesome-llm-token-optimization](https://github.com/pleasedodisturb/awesome-llm-token-optimization) | ~78 | Curated strategies/tools/papers: prompt caching 90%, token-efficient tool use 70% out, Batch API 50%, routing 60–95%, LLMLingua 5–20×; deep KV-cache & speculative-decoding paper tables | Same technique space, more API/infra-oriented + research depth |
| [enhansome/enhansome-llm-token-optimization](https://github.com/enhansome/enhansome-llm-token-optimization) | ~0 | Combined-pipeline framing: cache prefix + cheapest model + batch + compress + response cache = "95–99% vs naive"; academic paper index (LLMLingua-2, LongLLMLingua, RECOMP, 500xCompressor, LongCodeZip, Chain of Draft, CROP…) | Paper-level backing for compression claims |
| [AmadeusITGroup/token-usage-optimisation-tutorial-cache-aspects](https://github.com/AmadeusITGroup/token-usage-optimisation-tutorial-cache-aspects) | ~1 | **Hands-on Copilot CLI experiment harness** measuring prompt caching, token usage, cost trade-offs | Rare *empirical* Copilot-CLI companion to the source guide |
| [drona23/claude-token-efficient](https://github.com/drona23/claude-token-efficient) | ~6k | One drop-in CLAUDE.md that keeps responses terse | = source repo's technique #1–#2 packaged as a file |
| [nadimtuhin/claude-token-optimizer](https://github.com/nadimtuhin/claude-token-optimizer) | ~580 | Reusable setup prompts; doc tokens 11K → 1.3K *(v.r.)* | = "shrink always-on context" as a service |
| [SebastienDegodez/copilot-instructions](https://github.com/SebastienDegodez/copilot-instructions) | ~196 | Copilot instruction-file best practices (DDD, Clean Architecture) incl. `minimal-context-tools` skills plugin | Copilot-native instruction patterns + minimal-context skills (referenced by source repo) |
| [steipete/agent-rules](https://github.com/steipete/agent-rules) | ~5.7k | Battle-tested rules for Claude Code/Cursor agents | Rule-file doctrine overlap |
| [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) | ~78k | Broad prompt/context-engineering/RAG/agents guides | Upstream general reference |
| [brexhq/prompt-engineering](https://github.com/brexhq/prompt-engineering) | ~9.6k | Classic enterprise LLM tips (archived 2023) | Historical prompting baseline |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | ~54k | Mega-index of Claude Code resources incl. cost/usage tools | Discovery hub for category 5.4 tools |

### 5.2 Output & Context Compression (filters, proxies, gateways)

| Repo | ⭐ | Mechanism | Claim |
|---|---|---|---|
| [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | ~81k | Rust CLI proxy; per-command filters before output hits context; works with Claude Code/Cursor/Copilot; custom TOML filters; full output saved on failure | 60–90% on common dev commands *(v.r.)* |
| [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | ~73k | Transparent proxy; compresses tool outputs/logs/files/RAG chunks; reversible retrieval | ~20% coding agents, 60–95% JSON *(v.r.)* |
| [alexgreensh/token-optimizer](https://github.com/alexgreensh/token-optimizer) | ~2.3k | Hook-wired "ghost token" finder; raw archived pre-compression; live dashboard + context-quality score; cache-safe (never modifies existing prefix); keep-warm cache pings; **installs for Copilot, Claude Code, Cursor, Codex, OpenCode, Antigravity** | Survives compaction without quality decay *(v.r.)* |
| [Paritok-official/paritok-4b-v1](https://github.com/Paritok-official/paritok-4b-v1) | ~1.5k | Non-destructive compression gateway w/ own 4B model | 25% turn 1 → 85%+ in long/saturated sessions *(v.r.)* |
| [ojuschugh1/sqz](https://github.com/ojuschugh1/sqz) | ~624 | CLI/context compressor | — |
| [edouard-claude/snip](https://github.com/edouard-claude/snip) | ~451 | Go CLI proxy, declarative YAML filters | 60–90% *(v.r.)* |
| [yvgude/lean-ctx](https://github.com/yvgude/lean-ctx) | ~3.8k | MCP server + context runtime: session caching, AST-aware compression, 90+ shell patterns; `lean-ctx init --agent claude-code`; supports Copilot | — |
| [edgee-ai/edgee](https://github.com/edgee-ai/edgee) | ~133 | Hosted **agent gateway**: route Claude Code/Codex/Cursor/VS Code+Copilot through Edgee | Cuts token spend centrally *(v.r.)* |
| [The-Distillery-dev/thedistillery](https://github.com/The-Distillery-dev/thedistillery) | ~132 | Token-optimization proxy for Claude/Anthropic traffic | *(v.r.)* |

### 5.3 Codebase Graphs & Retrieval (kill orientation reads)

| Repo | ⭐ | Mechanism | Claim |
|---|---|---|---|
| [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | ~120k | Tree-sitter AST → queryable `graph.json` (code + docs + SQL schemas + configs + PDFs); skill for Claude Code/Cursor/Codex/Gemini; **referenced by source repo** | 6.8× avg, ≤71.5× structural nav *(v.r.)* |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | ~43k | Browser automation CLI; a11y-tree snapshots instead of DOM dumps | — |
| [tirth8205/code-review-graph](https://github.com/tirth8205/code-review-graph) | ~32k | Local-first code-intelligence graph for MCP/CLI; agents read only what matters | 49× large monorepos, 6.8× avg reviews *(v.r.)* |
| [zilliztech/claude-context](https://github.com/zilliztech/claude-context) | ~12.6k | Code-search MCP: hybrid BM25 + dense-vector retrieval over whole codebase | ~40% reduction at equal retrieval quality *(v.r.)* |
| [jgravelle/jcodemunch-mcp](https://github.com/jgravelle/jcodemunch-mcp) | ~2.7k | Symbol-level GitHub code retrieval via tree-sitter AST | 95%+ on code exploration *(v.r.)* |
| [Madhan230205/token-reducer](https://github.com/Madhan230205/token-reducer) | ~46 | Local-first hybrid RAG (BM25 + ONNX vectors), AST chunking, reranking; no API needed | 90%+ *(v.r.)* |

### 5.4 Usage Analytics & Observability (measure first)

| Repo | ⭐ | What it covers |
|---|---|---|
| [ccusage/ccusage](https://github.com/ccusage/ccusage) | ~18.6k | The de-facto local usage analyzer: reads session JSONL from **17+ CLIs incl. GitHub Copilot CLI**, Claude Code, Codex, Gemini CLI, OpenCode, Amp, Goose…; daily/weekly/monthly/session/5-hour-block reports; per-model cost breakdown; statusline integration |
| [crwdla/tokentab](https://github.com/crwdla/tokentab) | ~1.1k | Cost by model/project/day from Claude Code, Codex, Gemini CLI logs |
| [ooples/token-optimizer-mcp](https://github.com/ooples/token-optimizer-mcp) | ~531 | MCP server: measures savings per agent, caching + compression of repeated tool outputs, shared local knowledge graph across 16 CLI clients |
| [tokentopapp/tokentop](https://github.com/tokentopapp/tokentop) | ~73 | "htop for AI costs": live terminal dashboard — session/model/tokens/cost/burn-rate across providers; **referenced by source repo**; set budget alerts before optimizing |

### 5.5 Memory & Session Persistence (stop re-explaining)

| Repo | ⭐ | Mechanism |
|---|---|---|
| [mksglu/context-mode](https://github.com/mksglu/context-mode) | ~23.7k | **Sandboxes raw tool output into SQLite** instead of dumping into context — only clean summaries enter the conversation; 98% reduction on Playwright/GitHub/logs *(v.r.)*; session memory; routing across 17 platforms |
| [cytostack/openwolf](https://github.com/cytostack/openwolf) | ~2.4k | Portable project memory across Claude Code/Codex/OpenCode + token accounting measured from harness transcripts; local file I/O |
| [lucasrosati/claude-code-memory-setup](https://github.com/lucasrosati/claude-code-memory-setup) | ~989 | Obsidian + Graphify persistent memory; up to 71.5× fewer tokens/session *(v.r.)* |
| [felixsim/bonsai-memory](https://github.com/felixsim/bonsai-memory) | ~30 | Hierarchical "bonsai" memory tree replacing flat MEMORY.md; progressive disclosure; 70–95% *(v.r.)* |
| [mehmetdemirci/comb-ai](https://github.com/mehmetdemirci/comb-ai) | ~13 | Context-optimized memory bank: structured docs + **cache-aware reading strategies** |

### 5.6 File Conversion & Ingestion Hygiene

| Repo | ⭐ | Use |
|---|---|---|
| [microsoft/markitdown](https://github.com/microsoft/markitdown) | ~186k | DOCX/PDF/PPTX/XLSX/HTML/images/audio → Markdown before any AI workflow; removes ~33% format tax *(per Marc Bara's measurement)* |

### 5.7 Research & Programmatic Compression (API-scale)

| Repo / work | ⭐ | Relevance |
|---|---|---|
| [microsoft/LLMLingua](https://github.com/microsoft/LLMLingua) | ~6.7k | EMNLP'23/ACL'24 prompt + KV-cache compression; up to 20× with minimal loss; LLMLingua-2 (BERT-distilled, 3–6× faster); LongLLMLingua (4× fewer tokens long-context) |
| [3DAgentWorld/Toolkit-for-Prompt-Compression](https://github.com/3DAgentWorld/Toolkit-for-Prompt-Compression) | ~292 | PCToolkit: Selective-Context (50% via self-information pruning) & LLMLingua wrappers |
| [openai/openai-cookbook](https://github.com/openai/openai-cookbook) | ~76k | Official examples incl. cost/token optimization patterns, batching, caching |
| [anthropics/claude-cookbooks](https://github.com/anthropics/claude-cookbooks) | ~53k | Official Claude recipes; context engineering, prompt caching, tool use |
| Papers indexed by the awesome-lists | — | Chain of Draft (7.6% of CoT tokens), Concise-CoT (−48.7%), RECOMP (5% ratio), 500xCompressor, LongCodeZip (code-aware 5.6×), PagedAttention/vLLM, RadixAttention/SGLang, LMCache (15× throughput), speculative decoding family |

### 5.8 Copilot-Specific Plugins, Skills & Governance

| Repo | ⭐ | Use |
|---|---|---|
| [jsturtevant/copilot-codeact-plugin](https://github.com/jsturtevant/copilot-codeact-plugin) | ~43 | CodeAct skills for **Copilot CLI**: collapse tool chains into one sandboxed execution (49–69% input *(v.r.)*) |
| [amgdy/copilot-finops-automation](https://github.com/amgdy/copilot-finops-automation) | ~26 | Copilot budgets/cost-centers as code via GitHub Actions (see §4.8) |
| [obra/superpowers](https://github.com/obra/superpowers) | ~289k | Skills framework — planning/TDD/verification procedures (see §4.9) |
| [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) | ~2.5k | Planning orchestration, handoff, entropy control |
| [mattpocock/skills](https://github.com/mattpocock/skills) | ~266k | Engineering skills: TDD, bug diagnosis, review, domain modeling |
| Official GitHub Docs | — | [Models & pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing), [UBB for orgs](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises), [budgets how-to](https://docs.github.com/en/billing/how-tos/budgets/setting-up-budgets-to-control-spending-on-metered-products), Content Exclusion |

---

## 6. Choosing Your Stack: Decision Matrix

You don't need all of these. **Pick 2–3 tools matched to your dominant waste source** (after measuring with §9):

| Your dominant pain | First tool | Second tool |
|---|---|---|
| Heavy terminal/test/build output | **rtk** (or snip on Go/YAML preference) | headroom (transparent proxy, JSON-heavy) |
| Large codebase, agents re-reading files constantly | **Graphify** or code-review-graph | claude-context / jcodemunch-mcp (retrieval instead of graphs) |
| Too many MCP servers/tools loaded | **context-mode** (sandbox outputs) | lean-ctx (session cache + AST compression) |
| No idea where tokens go | **ccusage** (17+ CLIs incl. Copilot) | tokentop (live burn-rate) / tokentab (per-project) |
| Context rots after compaction; quality decay | **alexgreensh/token-optimizer** (quality score + recovery) | bonsai-memory / openwolf (persistent memory) |
| Org-wide spend control (Copilot) | **native budgets + user-level caps** | copilot-finops-automation (policy as code) |
| DOCX/PDF/PPTX into AI workflows | **markitdown** | — |
| Building agents on APIs at scale | **prompt caching (Anthropic `cache_control` / OpenAI auto)** | LLMLingua (compression) + Batch API (50%) |

**Stacking rules:**
1. Guides/knowledge repos are free — read `claude-cost-optimizer` (Claude Code) and the source repo (Copilot) regardless of stack
2. One output filter per command path (rtk **or** snip **or** headroom — not layered)
3. Graph/retrieval tools replace orientation reads; they don't replace cache discipline
4. Gateways (edgee, distillery, paritok) route *all* traffic — security-review before org adoption
5. Analytics first, optimization second: set budget alerts in ccusage/tokentop **before** changing anything

---

## 7. The Complete Technique Matrix

Condensed from the source repo's 40+ technique matrix, extended with ecosystem additions. **Not additive** — figures are per-mechanism estimates.

| # | Technique | Input savings | Output savings | Quality | Effort | Category |
|---|---|---|---|---|---|---|
| 1 | Code-only / terse-output instructions | — | **40–70%** | good | 0 min | Output |
| 2 | Constrain response format (1-sentence/JSON/bullets) | — | 30–80% | depends | 0 min | Output |
| 3 | Diffs not rewrites | — | 50–90% | neutral+ | habit | Output |
| 4 | Caveman-speak (full) | 30–50% | 40–55%¹ | negligible | habit | Prompt |
| 5 | Structured/key-value prompts | 20–40% | 30–50% | improves | habit | Prompt |
| 6 | Code-centric prompting (pseudocode/sig/"like X but Y") | 50–67% of prompt | — | equal | habit | Prompt |
| 7 | Declarative guardrails | ~60% of rule text | — | improves | one-time | Prompt |
| 8 | Precise prompts (file+function+done-condition) | 30–60% of prompt | 30–60% | improves | habit | Prompt |
| 9 | One task per prompt | 20–40% | 20–40% | improves | habit | Prompt |
| 10 | Compress always-on instruction files | 40–60% of file | — | none | 15 min | Context |
| 11 | Landmines-only prune / delete `/init` boilerplate | **20–23% of agent task** | — | **improves** (ETH) | 15 min | Context |
| 12 | `applyTo:` scoped instruction files | 60–90% of optional guidance | — | positive | 15 min | Context |
| 13 | Close tabs / choose context up front | 50–90% of file context | — | varies | habit | Context |
| 14 | Fresh conversations + handoff summary | 80%+ of history | — | lose context | habit | Context |
| 15 | Cache-stability tuple (no mid-thread switches) | up to ~90% discount on cached input | — | none | discipline | Context |
| 16 | markitdown conversion of rich files | ~33% on office docs | — | improves | 5 min | Context |
| 17 | Codebase graph (Graphify et al.) | 6.8–71.5× nav reads *(v.r.)* | — | improves | 10 min | Context |
| 18 | Ask/Edit mode for non-agentic work | **60–90%** | — | good | 0 min | Workflow |
| 19 | Plan-first, execute fresh, cheaper lane | avoids wrong-direction rework | — | improves | sequencing | Workflow |
| 20 | Auto model default | discount on eligible usage | — | good | 0 min | Workflow |
| 21 | 3-tier routing (skip LLM / cheap / premium) | 38–79% of requests to cheaper tiers² | — | none | low | Workflow |
| 22 | Reasoning-effort tuning | vendor-reported | — | vendor-recommended | low | Workflow |
| 23 | Retune prompts per model | indirect (less rework) | indirect | improves | 10 min | Workflow |
| 24 | Terse commits / PR comments | 5–15 tok each | 60–80% (reviews) | none | habit | Workflow |
| 25 | MCP audit (disable unused servers) | **5K–190K/task** | — | none | 10 min | Tools |
| 26 | Per-workspace MCP config; lean VS Code profile | variable | — | none | medium | Tools |
| 27 | Skills instead of MCPs for occasional capabilities | schema → on-demand | — | improves | medium | Tools |
| 28 | Output filters (rtk/snip/headroom) | 60–90% of shell output *(v.r.)* | — | none | 5–15 min | Tools |
| 29 | minimal-context-tools skills (rg/fd/jq/yq/ast-grep) | 70–95% search patterns *(v.r.)* | — | improves | medium | Tools |
| 30 | CodeAct (Copilot CLI) | 49–69% on long chains *(v.r.)* | — | depends | 15 min | Tools |
| 31 | Tool search / deferred loading (>15 tools, API builds) | removes unused schemas per request | — | none | high | Tools |
| 32 | Token-efficient tool use flag (Anthropic API) | — | 14–70% *(v.r.)* | none | flag | Tools |
| 33 | Cap `maxRequests` / agent steps | variable | — | truncation risk | low | Agent |
| 34 | Plan files + acceptance criteria for Coding Agent | 15–40% | — | improves | medium | Agent |
| 35 | `copilot-setup-steps.yml` (env pre-built) | 10–30% | — | improves | medium | Agent |
| 36 | Custom agent profiles (narrow tool list, pinned model) | 10–30% | — | improves | medium | Agent |
| 37 | Prompt in English | vs 1.6–3.2× other languages | — | none | habit | Language |
| 38 | Compress memory files; cache-aware memory (comb-ai) | 40–60% per load | — | none | low | Memory |
| 39 | Sandbox tool output (context-mode) | 98% on noisy tools *(v.r.)* | — | none | medium | Memory |
| 40 | Enterprise budgets + $0 user caps + FinOps-as-code | caps spend (≠ shrinks prompts) | — | n/a | admin | Governance |
| 41 | Prompt caching (API: cache_control / auto) | **up to 90% of cached prefix** | — | none | API work | Infra |
| 42 | Batch API for non-urgent work | 50% rate | — | none | API work | Infra |
| 43 | LLMLingua-style compression (bulk/RAG) | 5–20× *(v.r.)* | — | minimal loss | high | Infra |

¹ Requires terse-output system instruction (#1). ² SWE-bench model-mixing data cited by source repo.

**The Big Eight (impact-to-effort ranking):** ① terse output instructions → ② landmines-only context files → ③ Ask mode by default → ④ MCP audit → ⑤ Auto routing → ⑥ markitdown before ingestion → ⑦ codebase graph on big repos → ⑧ plan-first execution.

---

## 8. Anti-Patterns — What Actively Wastes Tokens

| Anti-pattern | Why it burns money |
|---|---|
| Running `/init` and keeping the 200-line output | ~1,500 tokens every interaction; ETH data says −2% correctness, +20–23% cost |
| "Fix it" by adding more global instructions | Bigger always-on file × every step; scoped one-shot mention is cheaper and works better |
| Agent mode for questions | 5–25 tool-loop steps for what Ask answers in one turn (60–90% waste) |
| Switching model/agent/MCP mid-thread | Discards cached prefix; carried history re-billed in new lane |
| Premium model pinned all day | Paying Opus rates for syntax lookups |
| Enabling every MCP server "just in case" | 100–500 tokens × tools × steps, even when unused (27K-tok Azure plugin story) |
| Vague prompts ("improve robustness") | Triggers 30-step exploration sessions |
| Pasting raw DOCX/PDF/HTML/log floods | Format tax ~33%+; truncation may hide the part that matters |
| Stacking two output filters | Lost detail → rework → costs more than saved |
| Compressing to extreme/wenyan levels | Misreads → re-explaining → net-negative |
| One mega-session for plan+build+debug | Every turn replays the whole history; cache churns |
| Optimizing before measuring | You'll compress the 5% and miss the 60% (measure `/context`, ccusage first) |
| Treating vendor "×" claims as guarantees | Most are input-side, best-case, self-benchmarked |

---

## 9. Measurement: Baseline Before You Optimize

1. **Per-session context audit** — Copilot CLI: `/context` mid-session; note `System/Tools` vs `Messages`. VS Code: estimate `servers × tools × ~200 tok`.
2. **Historical spend** — `npx ccusage` (daily/monthly/session, per-model breakdown, 5-hour blocks; supports Copilot CLI + 16 other CLIs). Live burn-rate: **tokentop**. Per-project: **tokentab**.
3. **Instruction-file cost** — token-estimator from `claude-cost-optimizer`: `estimate.py CLAUDE.md --per-turn 30` → tokens & $ per session per model.
4. **Set alerts before optimizing** — budget alerts in ccusage/tokentop; org budgets + stop-usage in GitHub billing.
5. **A/B one change at a time** — apply a technique, re-run the same representative task, compare tokens *and* pass rate. The source repo's rule: figures are per-mechanism, not additive, and never equal total bill reduction.
6. **Track outcome per token** — cost per merged PR / per resolved issue, not cost per prompt.

---

## 10. 4-Week Adoption Plan

**Week 1 — Zero-cost habits (0 setup):**
- Add to instructions file: `Code only, no explanation.` + `Bullets over paragraphs. No explanations unless asked.`
- Use Ask mode for questions; Agent only for multi-step tasks
- Set model to **Auto**; stop mid-thread model/MCP switching
- Precise prompts: name file, function, done-condition

**Week 2 — Structural cleanup (~1 h):**
- Compress instructions file to landmines-only (bug-tracker rule); delete `/init` boilerplate; dedupe `AGENTS.md` vs `copilot-instructions.md` (consolidate to one)
- Split per-layer guidance into `applyTo:`-scoped files
- Audit MCP servers + VS Code extensions; per-workspace configs; lean coding profile
- Add `.claudeignore` / Content Exclusion for build artifacts

**Week 3 — Tooling (pilot 2–3):**
- Install **ccusage** + **tokentop**; record one-week baseline
- Pilot **one** output filter (rtk or snip) on your noisiest commands; A/B measure
- Large repo? Build **Graphify**/code-review-graph index
- markitdown for any office-doc ingestion

**Week 4 — Workflow & governance:**
- Plan-first pattern: plan mode → `plan.md` → fresh cheaper-lane execution → verify acceptance criteria
- Terse commits/PR reviews as team convention
- `/chronicle cost tips` + `/chronicle improve` weekly (Copilot CLI)
- Enterprise: budgets at org/cost-center scope, user-level caps, model-access review, FinOps-as-code if multi-team
- Re-measure vs Week-3 baseline; keep what worked, drop what didn't

**Monthly maintenance:** re-audit MCPs; prune instruction files (delete fixed landmines); re-tune prompts after model changes; review spend cohorts.

---

## 11. Research Backing & Further Reading

**Studies & data cited by the source repo:**
- Gloaguen et al., **AGENTBENCH** (ETH Zurich, Feb 2026) — 138 tasks/12 repos/4 agents: LLM-generated context files −2% correctness, +20–23% tokens
- Lulla et al. (Jan 2026) — human-written `AGENTS.md`: −29% runtime, −17% output tokens (efficiency ≠ correctness)
- Liu et al., **"Lost in the Middle"** (2023) — U-shaped attention; middle of long context ignored
- Addy Osmani (Google, 2026) — discoverability filter for context files
- Ivan Krivyakov / Capodieci-Castillo — cross-language tokenization tables
- Marc Bara — "Your DOCX is wasting 33% of your AI budget" ([Medium](https://medium.com/@marc.bara.iniesta/your-docx-is-wasting-33-of-your-ai-budget-86a3d229d042))
- Dina Berry — Copilot CLI `/context` field measurement ([writeup](https://dfberry.github.io/2026-05-06-tuning-up-copilot-context))

**Compression research (indexed in the awesome-lists):** LLMLingua (EMNLP'23, ≤20×), LLMLingua-2 (ACL'24, 3–6× faster), LongLLMLingua (4× long-context), Selective Context (−50%), RECOMP (5% ratio), 500xCompressor, LongCodeZip (code-aware 5.6×), Chain of Draft (7.6% of CoT tokens), Concise-CoT (−48.7%), CROP (≤80.6% output), KV-cache family (PagedAttention/vLLM, RadixAttention/SGLang, LMCache, KeepKV), speculative decoding family.

**Official docs:** [Copilot models & pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing) · [UBB for organizations](https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-organizations-and-enterprises) · [Budgets how-to](https://docs.github.com/en/billing/how-tos/budgets/setting-up-budgets-to-control-spending-on-metered-products) · [Anthropic prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) · [OpenAI prompt caching & Batch API](https://platform.openai.com/docs/guides/prompt-caching)

**Source repo chapters (for deep dives):** [01 why-tokens-matter](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/01-why-tokens-matter.md) · [02 prompt-compression](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/02-prompt-compression.md) · [03 language-comparison](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/03-language-comparison.md) · [04 context-management](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/04-context-management.md) · [05 output-control](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/05-output-control.md) · [06 workflow-optimization](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/06-workflow-optimization.md) · [07 agents-md-problem](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/07-agents-md-problem.md) · [08 mcp-tool-costs](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/08-mcp-tool-costs.md) · [09 comparisons-data](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/09-comparisons-data.md) · [10 practical-setup](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/10-practical-setup.md) · [11 models-and-pricing](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/11-models-and-pricing.md) · [12 enterprise-governance](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/12-enterprise-governance.md) · [13 outcome-per-token](https://github.com/olivomarco/github-copilot-token-optimization/blob/main/docs/13-outcome-per-token.md)

---

*Generated September 2026. Token figures are per-mechanism estimates, not additive guarantees; validate every vendor-reported claim against your own tasks and pass rates before org-wide rollout.*
