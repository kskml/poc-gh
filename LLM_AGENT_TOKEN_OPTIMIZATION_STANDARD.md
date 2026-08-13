# LLM Agent Token Optimization Standard

> Engineering standard for building AI agents and assistants that are fast, cheap, and reliable. This document is the checklist teams follow at design, code review, and release.

| | |
|---|---|
| **Status** | Approved |
| **Version** | 4.0 |
| **Last Updated** | 2026-08-13 |
| **Next Review** | Quarterly, or upon major model/provider pricing changes |
| **Owner** | TBD — Head of AI Engineering |

## Table of Contents

1. [Purpose](#1-purpose)
2. [Agent Architecture — Design a Tight Loop](#2-agent-architecture--design-a-tight-loop)
3. [Prompting — Bounded and Dense](#3-prompting--bounded-and-dense)
4. [Model Selection — Route by Step](#4-model-selection--route-by-step)
5. [Context Management — The Highest Leverage](#5-context-management--the-highest-leverage)
6. [Tools and Skills — Bounded Capabilities](#6-tools-and-skills--bounded-capabilities)
7. [Production Assistants — Route and Cache](#7-production-assistants--route-and-cache)
8. [Supplementary — Cache, Measure, Evaluate](#8-supplementary--cache-measure-evaluate)
9. [Compliance Checklist](#9-compliance-checklist)
10. [References](#10-references)

---

## 1. Purpose

Agent cost = **steps × tokens-per-step**. This standard reduces both. It is the checklist teams follow at design, code review, and release.

---

## 2. Agent Architecture — Design a Tight Loop

| Rule | Level | What to do |
|---|---|---|
| Reduce LLM calls | SHOULD | Replace any step with a script or code where possible. Batch reads into one call. |
| Planner/executor split | SHOULD | One plan (paid once), deterministic or cheap execution. Never re-derive the plan each step. |
| Compact plans | SHOULD | Plans are short JSON steps, revisited only on failure. |
| Stopping condition | MUST | Every agent has an explicit end: done signal, failure threshold, or max steps. |
| Cap steps/tool calls | MUST | Hard limits per task (e.g., max 25 tool calls). A runaway agent is the costliest failure. |
| Reuse results | SHOULD | Never re-fetch data the agent already holds. |
| Checkpoints | SHOULD | Persist state; resume from the last checkpoint on failure, not from scratch. |
| Structured state | SHOULD | State lives in a JSON/DB record; inject only the delta, not the transcript. |

> **Golden rule:** Fewer steps first, then smaller steps. Zero-token steps are cheaper than any optimization of a paid step.

---

## 3. Prompting — Bounded and Dense

> Agent outputs (reasoning, tool scaffolding, summaries) are all billed at output rates.

| Rule | Level | What to do |
|---|---|---|
| Dense system prompt | SHOULD | Role + key constraints + output contract only. Stable across steps (cacheable). |
| Terse reasoning | SHOULD | Instruct keyword notes, not essays. Prune the scratchpad after use. |
| Output caps | MUST | `max_output_tokens` + in-prompt length limits on every generation. |
| One goal per invocation | SHOULD | Single, scoped objective per agent or sub-agent. |
| Structured decisions | SHOULD | JSON schemas for tool choice / next action / state updates. |
| Fixed templates | SHOULD | Same template each step; only the variable part changes. |
| Stop/escalate condition | SHOULD | Prompt defines when to stop or hand off (unknown input, repeated failure). |

---

## 4. Model Selection — Route by Step

> Not every step needs a frontier model.

| Rule | Level | What to do |
|---|---|---|
| Planner ≠ executor | SHOULD | Frontier/reasoning model plans once; smallest capable model executes. |
| Route per step | SHOULD | Parsing/formats → small; tool orchestration/summaries → mid; debugging/planning → frontier. |
| Reasoning budget | SHOULD | High reasoning effort only on planning/hard steps. |
| Escalate on failure | SHOULD | Cheap first → validator → mid-tier → frontier, only for detected failures. |
| Re-validate quarterly | SHOULD | Re-run selection evals after provider price/capability changes. |
| Count before overflow | MUST | Estimate tokens before large injections; truncate or widen instead of failing mid-task. |

---

## 5. Context Management — The Highest Leverage

> **Why this matters:** Every step re-reads the whole window. Anthropic measured an 84% token reduction on a 100-turn eval by clearing old tool results.

| Rule | Level | What to do |
|---|---|---|
| Prune consumed tool results | MUST | Remove outputs not needed for the next step, immediately. |
| Compact history | SHOULD | Recent turns verbatim; older turns summarized (decisions, open items). |
| External state | SHOULD | Durable facts in memory/file/DB; pull in only when needed. |
| Sub-agent isolation | SHOULD | Sub-agents explore in their own window, return 1–2k-token summaries. |
| Budget the window | SHOULD | Allocate: system 2–5k, tools 5–10k, task 5–10k, turns 10–20k, retrieval 20–30k, headroom. |
| Gate retrieval | SHOULD | Rank by relevance density; top-3 gated chunks beat top-10 ungated. |
| Stable cached prefix | MUST | System prompt + tools identical and first, so they cache at a discount. |
| Compress before injecting | SHOULD | Summarize long passages; verbatim only code/numbers/quotes. |
| Reference, don't paste | SHOULD | Pointers/IDs resolved by tools, not pasted content. |
| Avoid context rot | SHOULD | Keep headroom; prune aggressively on long runs. |

---

## 6. Tools and Skills — Bounded Capabilities

> Tool schemas and results live in context on every step.

| Rule | Level | What to do |
|---|---|---|
| Targeted tools | SHOULD | `search_logs` over `list_logs`; overlap confuses models and adds schema tokens. |
| Bound responses | MUST | Paginate, filter, truncate with defaults. Never dump unbounded results into the window. |
| Consolidate chains | SHOULD | One composite tool beats three tools whose outputs re-enter context. |
| Namespace tools | SHOULD | `asana_projects_search`, not generic names. |
| Terse descriptions | SHOULD | Write for a new hire; unambiguous params; keep short (billed every step). |
| Meaningful results | SHOULD | Resolve UUIDs to human-readable identifiers. |
| Actionable errors | SHOULD | Tell the model what to fix, not a stack trace. |
| Selective loading | SHOULD | Expose only the tool schemas relevant to the current task. |
| Skills encapsulate | SHOULD | Procedures live in named skills (name + args), not prompt prose. |
| Summarized output | SHOULD | Skills return status + summary, not transcripts. |
| Pipeline composition | SHOULD | Chain skills; deterministic pipelines approach zero agent tokens. |
| Build for repetition | SHOULD | Skills pay off when reused; one-off work is a plain prompt. |

---

## 7. Production Assistants — Route and Cache

> Assistants see the same questions at scale; replies must be short and fast.

| Rule | Level | What to do |
|---|---|---|
| Short replies | SHOULD | Cap length in prompt and `max_output_tokens`; offer to expand. |
| Session compaction | SHOULD | Recent turns verbatim; older turns summarized. |
| Cache intents | SHOULD | FAQ/near-identical queries hit a semantic cache; stable prefix cached. |
| Route all traffic | MUST | Cache → small model → mid-tier → human handoff. Never all-frontier. |
| Bound retrieval | SHOULD | Top 3–5 gated chunks; never the whole knowledge base. |
| Loop guards | SHOULD | Turn caps and escalation for ambiguous/repeated queries. |

---

## 8. Supplementary — Cache, Measure, Evaluate

| Rule | Level | What to do |
|---|---|---|
| Cache hits | SHOULD | Static prefix first; verify `cached_tokens`. |
| Cache thresholds | SHOULD | Caching needs a minimum prefix length (varies by model, ~1k–4k). |
| Steady patterns | SHOULD | Keep tool order/effort consistent or the cache misses. |
| Semantic cache | SHOULD | Embedding-similarity match for repeats; exact key where determinism matters. |
| Structured outputs | MUST | Enforce JSON Schema where supported. |
| Count before send | SHOULD | Token-count the exact payload to catch overflow before spending. |
| Instrument | SHOULD | Log input/output tokens, cache hits, reasoning share, steps, tool calls, retries. |
| Cost per task KPI | SHOULD | Track cost per completed task (and per session); alert on drift. |
| Eval-gated changes | SHOULD | Pin snapshots; gate prompt/model changes behind evals. |

---

## 9. Compliance Checklist

**MUST items (waiver required):**

- [ ] Stopping condition + max-steps/tool-call caps (Section 2)
- [ ] Output caps on every generation (Section 3)
- [ ] Token count checked before large injections (Section 4)
- [ ] Consumed tool results pruned (Section 5)
- [ ] Stable cached prefix (Section 5)
- [ ] Bounded tool responses (Section 6)
- [ ] Assistant traffic routed (Section 7)
- [ ] Schemas enforced where supported (Section 8)

**Review checklist:**

- [ ] Max steps / caps set?
- [ ] Output caps set?
- [ ] Tool results pruned?
- [ ] State checkpointed outside the window?
- [ ] Stable prefix cacheable?
- [ ] Tools targeted and bounded?
- [ ] Token count checked before large injections?
- [ ] Assistants route intents and cache repeats?
- [ ] Cost per task instrumented?

---

## 10. References

**Context engineering**

- Anthropic — Effective context engineering for AI agents: <https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents>
- Anthropic — Managing context (context editing, memory tool): <https://www.anthropic.com/news/context-management>
- Anthropic — Building effective agents: <https://www.anthropic.com/research/building-effective-agents>
- Anthropic — Multi-agent research system: <https://www.anthropic.com/engineering/multi-agent-research-system>
- Chroma — Context rot research: <https://research.trychroma.com/context-rot>

**Prompting and models**

- OpenAI — Prompt engineering guide: <https://platform.openai.com/docs/guides/prompt-engineering>
- OpenAI — Reasoning models: <https://platform.openai.com/docs/guides/reasoning>
- OpenAI — Structured Outputs: <https://platform.openai.com/docs/guides/structured-outputs>
- Anthropic — Prompt engineering overview: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview>

**Tools and skills**

- Anthropic — Writing effective tools for agents: <https://www.anthropic.com/engineering/writing-tools-for-agents>
- Model Context Protocol (MCP) — Introduction: <https://modelcontextprotocol.io/docs/getting-started/intro>

**Caching and measurement**

- OpenAI — Prompt caching: <https://platform.openai.com/docs/guides/prompt-caching>
- Anthropic — Prompt caching: <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>
- Google Gemini — Context caching: <https://ai.google.dev/gemini-api/docs/caching>
- OpenAI — Counting tokens: <https://developers.openai.com/api/docs/guides/token-counting>
- OpenAI — Token usage overview: <https://platform.openai.com/docs/guides/text-generation>

> Model names, prices, context windows, and cache thresholds change frequently. Treat figures in this document as illustrative; re-check provider pages before deciding. If a link is dead, search the provider's docs for the same title.
