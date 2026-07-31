# AI Token Demand & Cost Estimation Framework

> A practical, calibration-ready framework to estimate token demand and AI cost for coding
> work, driven by **Jira story complexity**, **user role**, and other task criteria.
> Companion calculator: `docs/token-demand-estimator.py`.
> Related context: `docs/token-optimization-guide-github-copilot.md` (cost levers),
> `docs/token-optimization-tools-effectiveness-copilot.md` (optimization stack).

## 1. Goal and mental model

Estimate *before the work happens* how many tokens an AI coding agent will consume on a
task, and what that costs — so you can budget sprints, size plans, and prove the ROI of
token-optimization tools.

**Core principle:** token demand is a product of **how much the agent reads** (input)
and **how much it writes** (output), multiplied by **how many round-trips** it takes.
Everything else is a multiplier on one of those three numbers.

```
Total tokens ≈ turns × (avg input per turn + avg output per turn)
Cost         ≈ input_tokens × P_in × (cache_discount) + output_tokens × P_out
```

## 2. Token anatomy — where the tokens actually go

For an agentic task (e.g. an M-story, 3–5 story points), a typical session decomposes
into phases. This is the ground truth the estimation model is fitted to:

| Phase | What happens | Input (k) | Output (k) | Comment |
|---|---|---|---|---|
| Plan | read story, clarify, outline steps | 40 | 3 | system prompt + instructions dominate |
| Explore | grep / search / read files / repo map | 150 | 2 | **the biggest input sink** |
| Implement | write / edit code | 120 | 30 | output-heaviest phase |
| Verify | run tests, read failures, fix loops | 80 | 8 | bash output; shrinks with rtk/squeez |
| Review | self-review, refactor, edge cases | 40 | 5 | |
| Communicate | commit message, summary, PR description | 20 | 2 | |
| **Total** | | **450** | **50** | ≈ 500k tokens for an M story |

Two consequences that drive the whole framework:

1. **Input is ~90% of tokens.** Saving input (compressed tool output, symbol-level
   retrieval, memory, caching) matters far more than saving output.
2. **Turns multiply everything.** A story that takes 100 turns costs ~4× one that takes 25.

## 3. The estimation model

```
Input_tokens   = Base_input(complexity) × R × C × M × H × O
Output_tokens  = Base_output(complexity) × R × M × H × O
Billed_input   = Input_tokens × ( cache × 0.10 + (1 − cache) )        # cache reads ≈ 10% of input price
Cost           = Billed_input × P_in + Output_tokens × P_out
```

Where:
- **Base_input / Base_output** — from Jira story complexity (Section 4).
- **R — role factor** (Section 5).
- **C — codebase/context factor** (input only).
- **M — modality factor** (chat vs agent vs subagents).
- **H — rework/ambiguity factor**.
- **O — optimization factor** (what token-saving stack is installed).
- **cache** — fraction of input served from prompt cache (0.3–0.8 typical for agentic use).
- **P_in / P_out** — model price per million tokens (Section 6).

Estimate three numbers: **low** (all inputs at the bottom of their range), **central**
(midpoints), **high** (tops). Report the range, never a single point.

## 4. Criterion 1 — Jira story complexity

Map story points to a complexity level and a base token budget. These are fitted defaults;
calibrate them from your own telemetry (Section 9).

| Level | Story points | Files | Turns | Base input (k) | Base output (k) | Example |
|---|---|---|---|---|---|---|
| **XXS** | 0.5 | 1 | 4–6 | 15–35 | 2–6 | typo, config toggle, one-line fix |
| **S** | 1–2 | 1–2 | 10–20 | 80–160 | 8–20 | single-file bug fix |
| **M** | 3–5 | 2–4 | 25–50 | 300–600 | 30–70 | feature in 1–2 files, edge cases |
| **L** | 8 | 4–8 | 60–120 | 900–1800 | 90–200 | new module, multi-file integration |
| **XL** | 13+ | 8+ / several services | 150–400 | 3000–7000 | 300–800 | epic, cross-service architecture |

Quick in-session check: `base_input × 4 = total` and `90% of tokens are input`.

## 5. Criterion 2 — user role

Roles change the *profile* (read-heavy vs write-heavy) and the *volume*. The role factor
multiplies both input and output.

| Role | R | Profile | Why |
|---|:---:|---|---|
| Developer | 1.0 | implement + test | baseline |
| Senior Developer | 1.1 | + self-review | extra review turns |
| Architect | 1.4 | design + heavy reading | reads ADRs, diagrams, cross-service context 2–3×; output is design docs |
| Tech Lead | 1.3 | design + review | |
| Reviewer | 0.5 | read diffs only | minimal output |
| QA / Test Engineer | 1.2 | write tests, run suites | many test-run iterations, big bash output |
| DevOps / SRE | 1.3 | infra, deploys, logs | enormous command output (plans, logs) |
| Data Engineer | 1.2 | schemas, pipelines, data | large schema/data context |
| PM / BA | 0.4 | analysis + summaries | chat-heavy, few tool calls |

## 6. Criterion 3 — other task criteria

### C — codebase / context factor (input only)

| Codebase | C |
|---|---|
| small (<10 files, single module) | 0.8 |
| medium (single repo, familiar) | 1.0 |
| large (monorepo / many services) | 1.5 |
| very large or unfamiliar | 2.0 |

### M — modality factor

| Mode | M |
|---|:---:|
| chat only (no tool execution) | 0.3 |
| editor completions + light agent | 0.6 |
| agent mode (full tool use) | 1.0 |
| agent + subagents | 1.2 |
| agent + subagents + heavy MCP | 1.5 |

### H — rework / ambiguity factor (start at 1.0, add)

| Signal | Add |
|---|---|
| >6 acceptance criteria | +0.2 |
| ambiguous requirements / novel domain | +0.2 |
| flaky tests / cross-team dependencies | +0.3 |
| long feedback loops (deploy-heavy) | +0.3 |
| **Cap** | **1.5** |

### O — optimization factor

| Stack installed | O |
|---|:---:|
| none | 1.0 |
| basic (tiny instructions, ignore files, `#codebase`, `/compact`, cache discipline) | 0.75 |
| full stack (output-compressor hooks + style skill + symbol MCP + memory + caching) | 0.45 |

## 7. Pricing & Copilot credits

Per-model prices are parameters (adjust to your plan). Cache reads cost ~10% of input price.

| Tier | P_in ($/MTok) | P_out ($/MTok) | cache hit ($/MTok) |
|---|:---:|:---:|:---:|
| budget (haiku / gpt-mini class) | 0.80 | 4.00 | 0.08 |
| mid (sonnet / gpt-4.1-mini class) | 3.00 | 15.00 | 0.30 |
| max (opus / gpt-4o class) | 15.00 | 75.00 | 1.50 |

**GitHub Copilot:** AI credits are 1 credit = $0.01, so `credits ≈ cost / 0.01`.
- Pro $10/mo = 1,500 credits; Pro+ $39/mo = 7,000; Max $100/mo = 20,000.
- Inline completions and next-edit suggestions are **free** — push work there.
- Auto model selection gives a ~10% discount; cache hits are ~10% of input price.
- **Worked capacity rule:** a mid-tier agent mode M-story ≈ **$0.9–1.4** ≈ **90–140 credits**.
  At 20,000 credits/month (Max), budget **~150–220 agent-mode stories/month** for one user.

## 8. Worked examples

### Example 1 — Developer, S story (bug fix, 2 SP), medium repo, agent mode, no optimization, mid tier

```
Base in 120k, out 14k
R=1.0  C=1.0  M=1.0  H=1.0  O=1.0
Input ≈ 120k · (0.5·0.10 + 0.5) = 66k billed   → 66k × $3/MTok = $0.20
Output ≈ 14k → $0.21
Total ≈ $0.41  (≈ 41 Copilot credits)
```

### Example 2 — Architect, L story (new service design, 8 SP), large repo, agent+subagents, mid tier

```
Base in 1400k, out 150k
R=1.4  C=1.5  M=1.2  H=1.0  O=1.0
Input ≈ 1400 × 1.4 × 1.5 × 1.2 = 3528k · 0.55 = 1940k billed → $5.82
Output ≈ 150 × 1.4 × 1.2 = 252k → $3.78
Total ≈ $9.60  (≈ 960 credits)
```

Architect + L story + large repo is ~23× a developer + S story. This is the profile that
justifies architectural-level optimization.

### Example 3 — Developer, M story (3–5 SP) with the **full optimization stack**

```
Base in 450k, out 50k
R=1.0  C=1.0  M=1.0  H=1.3 (6+ AC)  O=0.45
Input ≈ 450 × 1.3 × 0.45 = 263k · 0.55 = 145k billed → $0.43
Output ≈ 50 × 1.3 × 0.45 = 29k → $0.44
Total ≈ $0.87  vs  unoptimized ≈ $2.33  →  ~63% saving
```

The optimization stack (rtk/squeez hooks + style skill + symbol MCP + memory + caching)
pays for itself in the first few M+ stories.

### Sprint budget example

| Story | SP | Role | Mode | Est. tokens (k) | Est. cost |
|------:|:--:|------|------|------:|------:|
| Fix login validation | 2 | Developer | agent | 200 | $0.42 |
| Add export endpoint | 5 | Developer | agent+sub | 750 | $1.55 |
| Design auth service | 8 | Architect | agent+sub | 3,600 | $9.60 |
| E2E suite for checkout | 5 | QA | agent | 700 | $1.35 |
| **Sprint total (1 user)** | 20 | | | **~5,250** | **~$12.9** |

A 5-developer sprint at this mix ≈ **$55–65/day** ≈ **5,500–6,500 credits/day**. Compare
against Max-tier monthly credit allocation to decide team sizing.

## 9. Calibration loop (the part that makes it *accurate*)

The framework is a starting model; fit it to reality with a measurement loop.

1. **Log actuals per story.** Record: story ID, points, role, mode, optimization level,
   actual input tokens, actual output tokens, cache rate, cost.
2. **Source actuals from the tools you already have:**
   - Copilot: **Cache Explorer** + usage/credits report in GitHub settings (or `gh api`
     on the usage endpoint).
   - rtk: `rtk gain --all --format json` (bash-output savings).
   - snip: `/snip-gain` (NET input savings).
   - claude-mem: session observations; context-mode: `ctx-stats`.
3. **After 5–10 stories**, recompute the Base table: for each complexity level,
   `Base_input = median(actual input)` and the same for output.
4. **Re-derive R per role** as `median(role_actual) / median(developer_actual)`.
5. Re-run forecasts; the low–high band should tighten each cycle.

**Template row** (copy to a sheet): `story_id | points | level | role | mode | opt | H | actual_in | actual_out | cache | cost | Δ forecast vs actual`.

## 10. Honest limitations

- **±50% band.** This is an estimation framework, not a meter. Report ranges.
- **Sessions are lumpy.** A single very large file read or a `pytest -v` dump can exceed a
  whole phase's budget; optimization factors exist precisely to cap these.
- **Cache assumptions move.** Cache rates depend on discipline (stable prefix, avoid
  re-inlining instructions). Measure, don't assume.
- **Output prices dominate per-token but lose in volume.** At ~90/10 input/output split,
  input cost usually still dominates — unless output model is max-tier.
- **Brevity ≠ cheap.** Aggressive style skills can trade correctness (see context-mode's
  kimi-k2.5 note); the H factor should absorb regression-fix loops.

## 11. Quick-reference steps

1. Classify story → complexity level → Base in/out (Section 4).
2. Pick role → R (Section 5).
3. Adjust C, M, H, O (Section 6).
4. Apply model + prices (Sections 3, 7).
5. Report low / central / high.
6. Log actuals and recalibrate after 5–10 stories (Section 9).
