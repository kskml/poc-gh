# AI Productivity Evidence — Two-Team Sprint Analysis

> **Scope:** Historical two-team sprint evidence · story-point productivity per FTE · monthly scaling · EUR cost impact · industry-standard adjusted scenarios
> **Cost model:** FTE cost €1,200/month · AI cost €100 per FTE per month · 2 sprints per month
> **Companion tool:** `ai-two-team-evidence-dashboard.html` — interactive dashboard (euro edition · story-point terminology · default multiplier **+8.69%** from the Accenture × GitHub RCT · collapsible formula, assumption and evidence reference)
> **Edition 2 — October 26, 2026:** aligned with the dashboard's updated edition — euro figures, "story points" terminology throughout, the **+8.69% Accenture × GitHub RCT** as the default industry multiplier, capacity measured in FTE (not hours), no implementation/amortization layer, and the simplified F1–F16 formula set.

---

## Contents

1. [Executive Summary](#executive-summary)
2. [Baseline Evidence — Sprint Inputs](#1-baseline-evidence--sprint-inputs)
3. [Productivity per FTE — Sprint View](#2-productivity-per-fte--sprint-view)
4. [Monthly View — Scaling to Two Sprints per Month](#3-monthly-view--scaling-to-two-sprints-per-month)
5. [Cost Impact](#4-cost-impact)
6. [Industry-Standard Multiplier Analysis](#5-industry-standard-multiplier-analysis)
7. [Overall Findings](#6-overall-findings)
8. [Methodology, Assumptions and Formulas](#7-methodology-assumptions-and-formulas)

---

## Executive Summary

This report analyses one sprint of historical delivery data from two development teams, each observed in a **without-AI baseline** state and a **with-AI** state, and then scales the results to a monthly view at two sprints per month. Because headcount moved between the two states, the only fair way to compare the states is **productivity per FTE** (story points per full-time engineer), which is the decision metric used throughout this report. Raw story-point totals are reported as context, but they reward team size rather than efficiency, and the cost analysis shows why that distinction matters.

The two teams tell two different stories. **Team 1 played efficiency**: it absorbed an 8.3% headcount reduction (6.0 → 5.5 FTE) while giving up only 3.8% of output (58.6 → 56.4 story points), which lifts per-FTE productivity by **+5.0%** (9.77 → 10.25 story points/FTE). **Team 2 played scale**: it grew headcount by 21.1% (9.5 → 11.5 FTE) and output by 18.6% (66.8 → 79.2 story points), but output grew slower than headcount, so per-FTE productivity **fell 2.1%** (7.03 → 6.89 story points/FTE).

Neither team crossed the **+8.33% break-even gain** that a team needs before a €100/month AI licence pays for itself on a €1,200/month FTE (see §4.3), so the effective cost per story point **rose for both teams**: Team 1 from €61.43 to €63.39 (+3.2%), Team 2 from €85.33 to €94.38 (+10.6%). Priced honestly — what it would cost to deliver the same baseline monthly output at the observed per-FTE efficiency — the evidence-only **Phase 1** result is a combined cost **increase of €1,438/month** (Team 1 −€229, Team 2 −€1,209). Today's data does not yet support a savings claim. **Phase 2** is where the industry multiplier enters: applied additively on top of each team's observed gain, and **defaulted to +8.69% — the Accenture × GitHub enterprise RCT**, the measured floor for a structured, process-redesigned rollout. At that default the portfolio flips to **+€157/month** (+0.8% of the €18,600 baseline spend) and releases **1.31 FTE** of capacity: Team 1 saves €339, comfortably clearing its 3.3% parity bar, while Team 2 is still €182/month below its 10.4% bar. At the 25% Gartner-floor stop the combined saving reaches **€2,555/month** (13.7% below baseline spend).

| # | Metric | Team 1 | Team 2 |
|---|--------|--------|--------|
| 1 | Story-point productivity gain per FTE (observed · Phase 1) | **+5.0%** | **−2.1%** |
| 2 | Story points per FTE per sprint (base → with AI) | 9.77 → 10.25 | 7.03 → 6.89 |
| 3 | Monthly team cost change (actuals) | −€50 (−0.7%) | +€3,550 (+31.1%) |
| 4 | Effective cost per story point | €61.43 → €63.39 (+3.2%) | €85.33 → €94.38 (+10.6%) |
| 5 | Break-even gain (AI seat on a €1,200 FTE) | +8.33% | +8.33% |
| 6 | Industry multiplier needed for cost parity | ≥ 3.3% | ≥ 10.4% |
| 7 | Phase 1 monthly cost reduction (same-baseline-output costing) | −€229 | −€1,209 |
| 8 | Phase 2 monthly cost reduction at the +8.69% default | +€339 (+4.7%) | −€182 (−1.6%) |
| 9 | FTE capacity released at the +8.69% default | 0.72 FTE | 0.59 FTE |
| 10 | Phase 2 monthly cost reduction at 25% (Gartner floor) | +€1,200 (+16.7%) | +€1,355 (+11.9%) |

**Portfolio line:** combined baseline spend €18,600/month · Phase 1 combined **−€1,438/month** · Phase 2 at the +8.69% default **+€157/month and +1.31 FTE released** (FTE-weighted adjusted gain +9.4%) · at 25% **+€2,555/month**.

---

## 1. Baseline Evidence — Sprint Inputs

The evidence base is a single sprint per team per state, provided as historical data. Each team has two observed states: the **without-AI baseline** (the reference level for productivity and cost) and the **with-AI sprint** (the same team delivering with AI assistance). Note that headcount changed between the two states for both teams — Team 1 shrank by 0.5 FTE and Team 2 grew by 2.0 FTE — so the with-AI observation bundles the effect of AI assistance with a deliberate staffing decision. That is exactly what makes per-FTE normalization necessary: it prices the delivery system, not the payroll size.

**Table 1 — Sprint inputs (one sprint, as observed)**

| Team | Scenario | FTE | Story points | Story points per FTE |
|------|----------|----:|-------------:|---------------:|
| Team 1 | Without AI (baseline) | 6.0 | 58.6 | 9.77 |
| Team 1 | With AI | 5.5 | 56.4 | 10.25 |
| Team 2 | Without AI (baseline) | 9.5 | 66.8 | 7.03 |
| Team 2 | With AI | 11.5 | 79.2 | 6.89 |

Three features of this dataset deserve attention before any arithmetic. First, the teams have very different baseline productivity levels (9.77 vs 7.03 story points/FTE), so cross-team comparisons of absolute output are meaningless; every comparison below is within-team. Second, the staffing moves are large enough to dominate raw output changes, which is why §2 computes gains on a per-FTE basis. Third, a single sprint is a small sample — sprint-to-sprint volatility, story-point estimation drift, and work-mix changes are all uncontrolled here, and the limitations in §7 list the guardrails to apply before acting on these numbers.

---

## 2. Productivity per FTE — Sprint View

Productivity per FTE is defined as story points divided by the FTE count that produced them, and the productivity gain is the relative change of that ratio between the with-AI and baseline states. This is the standard normalization when headcount moves between the two states being compared: it answers "how much does one engineer deliver per sprint in each state?" rather than "how much did the team deliver?" — the latter grows mechanically whenever you add people, even if every individual slows down.

```text
Story points per FTE  =  story points ÷ FTE
Productivity gain     =  (story points per FTE with AI ÷ story points per FTE baseline) − 1
```

**Table 2 — Productivity per FTE and gain (sprint view)**

| Team | Baseline story pts/FTE | With-AI story pts/FTE | Δ story pts/FTE | Gain per FTE | Team output Δ | Team FTE Δ |
|------|----------------:|----------------:|----------:|-------------:|--------------:|-----------:|
| Team 1 | 9.77 | 10.25 | +0.49 | **+5.0%** | −2.2 story pts (−3.8%) | −0.5 (−8.3%) |
| Team 2 | 7.03 | 6.89 | −0.14 | **−2.1%** | +12.4 story pts (+18.6%) | +2.0 (+21.1%) |

**Team 1 — the efficiency play.** Team 1 delivered 56.4 story points with 5.5 FTE against a baseline of 58.6 story points with 6.0 FTE. The 8.3% headcount reduction cost only 3.8% of output, so each remaining FTE now produces 10.25 story points per sprint instead of 9.77 — a **+5.0% gain**, worth +0.49 story points per FTE per sprint. Held at its current size of 5.5 FTE, the team produces about **+5.4 story points per month** (two sprints) more than the same 5.5 FTE would have produced at baseline pace. In other words, the AI-assisted team nearly replaced the capacity of the 0.5 FTE it gave up.

**Team 2 — the scale play.** Team 2 delivered 79.2 story points with 11.5 FTE against a baseline of 66.8 story points with 9.5 FTE. Output grew an impressive +18.6%, but headcount grew faster at +21.1%, so each FTE now produces 6.89 story points per sprint instead of 7.03 — a **−2.1% loss** per FTE. Held at its current size of 11.5 FTE, the team produces about **3.3 story points per month less** than the same 11.5 FTE would have produced at baseline pace. The expansion bought throughput, but the per-engineer delivery rate dipped — the classic signature of scaling costs (onboarding, coordination, review load) landing faster than AI-assisted efficiency does.

The management reading of §2 is not that AI failed for Team 2 — throughput rose 18.6%, which may be exactly what the business needed. The point is that **throughput was bought with headcount, not unlocked by AI**, and the cost section shows what that difference does to unit economics.

---

## 3. Monthly View — Scaling to Two Sprints per Month

The sprint evidence scales to a monthly operating view by assuming **two sprints per month** per team. Absolute quantities (story points, costs) double; rates such as story points-per-FTE-per-sprint simply double into a per-month figure; and all percentage results are invariant to the scaling because they are ratios of like quantities. The monthly view is the unit the cost model lives in — €1,200 per FTE per month and €100 per AI-enabled FTE per month are monthly charges — so this is the basis used for the remainder of the report.

**Table 3 — Monthly view (2 sprints per month)**

| Team | Scenario | FTE | Story points / month | Story pts / FTE / month | Monthly cost | Cost per story point |
|------|----------|----:|---------------------:|-----------------------:|-------------:|---------------:|
| Team 1 | Without AI | 6.0 | 117.2 | 19.53 | €7,200 | €61.43 |
| Team 1 | With AI | 5.5 | 112.8 | 20.51 | €7,150 | €63.39 |
| Team 2 | Without AI | 9.5 | 133.6 | 14.06 | €11,400 | €85.33 |
| Team 2 | With AI | 11.5 | 158.4 | 13.77 | €14,950 | €94.38 |

Read per team, the monthly table makes the operating picture concrete. Team 1 ships 112.8 story points per month with 5.5 FTE — 4.4 story points fewer than its 6.0-FTE baseline, produced for €50 less. Team 2 ships 158.4 story points per month with 11.5 FTE — 24.8 story points more than its 9.5-FTE baseline, produced for €3,550 more. The per-FTE percentages carry over exactly from §2: **+5.0%** for Team 1 (20.51 vs 19.53 story points/FTE/month) and **−2.1%** for Team 2 (13.77 vs 14.06), because doubling both sides of a ratio leaves it unchanged.

---

## 4. Cost Impact

### 4.1 Cost model

The cost model has two components. Every FTE costs **€1,200 per month** (fully loaded labour cost), and every FTE working in the with-AI state additionally carries an **AI licence of €100 per FTE per month**. The loaded monthly cost of one AI-enabled FTE is therefore **€1,300**, and the AI licence represents **7.7%** of that loaded cost — a figure that quietly sets the entire economic analysis, because it defines how much per-FTE productivity AI must buy before it pays for itself.

```text
Loaded cost per with-AI FTE  =  €1,200 + €100  =  €1,300 / month
Monthly team cost             =  FTE × loaded cost
Effective cost per story point =  monthly team cost ÷ monthly story points
```

### 4.2 Team cost and effective cost per story point

**Table 4 — Monthly cost impact**

| Team | Cost without AI | Cost with AI | Cost change (€) | Cost change (%) | Cost per story point without AI | Cost per story point with AI | Cost per story point Δ |
|------|----------------:|-------------:|----------------:|----------------:|----------------------:|-------------------:|-------------:|
| Team 1 | €7,200 | €7,150 | **−€50** | **−0.7%** | €61.43 | €63.39 | **+€1.95 (+3.2%)** |
| Team 2 | €11,400 | €14,950 | **+€3,550** | **+31.1%** | €85.33 | €94.38 | **+€9.05 (+10.6%)** |
| Portfolio | €18,600 | €22,100 | +€3,500 | +18.8% | €74.16 | €81.49 | +€7.33 (+9.9%) |

Team 1's spend is essentially flat (−0.7%) — the €550 AI licence is almost exactly offset by the €600 of labour it stopped buying — yet its **cost per story point still rose 3.2%**, from €61.43 to €63.39. Team 2's spend rose +31.1% to buy its +18.6% output growth, so its cost per story point rose faster, **+10.6%**, from €85.33 to €94.38. The portfolio rows combine both teams: 271.2 monthly story points now cost €22,100 (€81.49 per story point) against a baseline of 250.8 story points for €18,600 (€74.16 per story point).

The lesson in Table 4 is the one executives most often miss: **near-flat spend is not the same as good value**. Team 1 spent 0.7% less money but each story point it delivers became 3.2% more expensive, because the story points it stopped buying were cheaper than the ones it kept. Value is decided on the unit price of a story point, not on the payroll delta.

### 4.3 Break-even: the +8.33% threshold

The AI licence is worth buying exactly when the per-FTE productivity it unlocks exceeds its share of loaded cost. The licence adds €100 to a €1,200 FTE (a +8.33% cost per FTE), so per-FTE productivity must rise by **+8.33%** for the effective cost per story point to stay flat — this is the break-even gain, independent of team or baseline:

```text
Break-even gain  =  (€1,200 + €100) ÷ €1,200 − 1  =  +8.33% per FTE
```

Against that threshold: Team 1's observed **+5.0%** falls 3.3 percentage points short (hence cost per story point +3.2% — the two gaps are two views of the same shortfall), and Team 2's observed **−2.1%** falls 10.4 percentage points short (hence +10.6%). Expressed as the industry-standard multiplier that each team needs on top of its observed gain to reach cost parity: **Team 1 needs ≥ 3.3%, Team 2 needs ≥ 10.4%**. Those two numbers are the practical decision rule for §5.

### 4.4 Combined portfolio

At portfolio level the two adoption stories partly offset each other. Combined headcount rose 15.5 → 17.0 FTE (+9.7%) and combined monthly output rose 250.8 → 271.2 story points (+8.1%). Output grew slightly slower than headcount, so combined per-FTE productivity slipped **−1.4%** (16.18 → 15.95 story points/FTE/month) while combined spend rose **+18.8%** to €22,100. The blended cost per story point for the portfolio moved €74.16 → €81.49 (**+9.9%**), sitting between the two teams' outcomes, weighted toward Team 2 because it carries the larger budget.

### 4.5 Phase 1 result — the evidence-only cost reduction

Everything so far is measurement. The dashboard's **Phase 1** turns it into a single honest number by asking one question: *what would it cost to deliver each team's baseline monthly output at its observed with-AI per-FTE efficiency?* The baseline headcount is divided by the observed gain to get the **FTE-months needed**; the difference against baseline headcount is the **capacity released**; and the monthly cost reduction is the value of that capacity minus the AI spend for the FTE-months actually needed — already net of tool cost, with no industry multiplier involved.

**Table 5 — Phase 1: same-baseline-output costing (measured evidence only)**

| Team | FTE-months needed | Capacity released (FTE) | Capacity value | AI tool spend | Monthly cost reduction |
|------|-----------------:|-----------------------:|---------------:|--------------:|-----------------------:|
| Team 1 | 5.71 | 0.29 | €343 | €571 | **−€229** |
| Team 2 | 9.70 | −0.20 | −€239 | €970 | **−€1,209** |
| Portfolio | 15.41 | 0.09 | €103 | €1,541 | **−€1,438** |

Both teams price **below the +8.33% break-even**, so the evidence-based answer today is a cost increase, not a saving — Team 1 by a modest €229/month, Team 2 by a substantial €1,209/month. This is the number to beat, and the multiplier analysis in §5 is what converts it: Phase 2 adds the industry-standard uplift for a structured, process-redesigned rollout and re-runs exactly the same chain.

---

## 5. Industry-Standard Multiplier Analysis

### 5.1 Method — how the multiplier is applied

Industry evidence places typical AI-assisted productivity gains in a **10–30% band** — commonly cited reference benchmarks include Bain (10–30%) and Gartner (25–30%), alongside Capgemini (7–18% at organization level) and Microsoft field data (up to +22%). The tool's default is deliberately more conservative: **+8.69%, the Accenture × GitHub randomized controlled trial**, measured on pull requests per developer in a real enterprise repository (with +15% merge rate and +84% build success alongside). It is treated here as the **measured floor for a structured rollout** — what a disciplined, process-redesigned programme should at minimum beat — rather than an aspiration. The dashboard's slider runs continuously from 0% to 30%, with quick-set stops at 8.69% (default), 10%, 15%, 20%, 25% and 30%.

The multiplier applies **additively on top of each team's observed gain**, and the same transparent chain that priced Phase 1 then prices the projection:

```text
Adjusted gain (F7)      =  observed gain + industry multiplier
FTE-months needed (F8)  =  baseline FTE ÷ (1 + adjusted gain)
Capacity released (F9)  =  baseline FTE − FTE-months needed
Capacity value (F10)    =  capacity released × €1,200
AI tool spend (F11)    =  FTE-months needed × €100
Monthly cost
reduction (F12)         =  capacity value − AI tool spend
```

Three assumptions pin the scenario. First, the frame is **same baseline output**: every scenario asks what it costs to deliver the team's baseline monthly story points (Team 1: 117.2; Team 2: 133.6) at the adjusted per-FTE efficiency, compared against the baseline monthly cost — the cleanest like-for-like cost question. The result is already net of tool cost, because F11 charges the licence only for the FTE-months actually needed. Second, the adjusted gain is **additive** (observed + multiplier), which is conservative relative to compounding, since (1+g)·(1+m) − 1 would add roughly another 0.5 point at these magnitudes. Third, the multipliers are **planning benchmarks from industry evidence, not observations of these two teams**; the observed rows in §2–§4 remain the only measured data in this report.

### 5.2 Adjusted scenarios — the default and the canonical stops

**Table 6 — Team 1 adjusted scenarios** (observed gain +5.0% · baseline €7,200/mo · €61.43 per story point)

| Multiplier | Adjusted gain | Story pts/FTE/month | Output/month | Cost per story point | FTE released | Monthly cost reduction |
|-----------:|--------------:|--------------------:|-------------:|---------------------:|-------------:|-----------------------:|
| **8.69% — default** | **+13.7%** | 22.21 | 122.1 | €58.54 | **0.72** | **+€339 (+4.7%)** |
| 10% | +15.0% | 22.46 | 123.5 | €57.87 | 0.78 | +€417 (+5.8%) |
| 15% | +20.0% | 23.44 | 128.9 | €55.46 | 1.00 | +€700 (+9.7%) |
| 20% | +25.0% | 24.42 | 134.3 | €53.24 | 1.20 | +€960 (+13.3%) |
| 25% | +30.0% | 25.39 | 139.7 | €51.20 | 1.38 | +€1,200 (+16.7%) |
| 30% | +35.0% | 26.37 | 145.0 | €49.30 | 1.56 | +€1,422 (+19.8%) |

**Table 7 — Team 2 adjusted scenarios** (observed gain −2.1% · baseline €11,400/mo · €85.33 per story point)

| Multiplier | Adjusted gain | Story pts/FTE/month | Output/month | Cost per story point | FTE released | Monthly cost reduction |
|-----------:|--------------:|--------------------:|-------------:|---------------------:|-------------:|-----------------------:|
| **8.69% — default** | **+6.6%** | 15.00 | 172.5 | €86.69 | **0.59** | **−€182 (−1.6%)** |
| 10% | +7.9% | 15.18 | 174.6 | €85.64 | 0.70 | −€41 (−0.4%) |
| 15% | +12.9% | 15.88 | 182.7 | €81.85 | 1.09 | +€465 (+4.1%) |
| 20% | +17.9% | 16.59 | 190.7 | €78.38 | 1.45 | +€929 (+8.1%) |
| 25% | +22.9% | 17.29 | 198.8 | €75.19 | 1.77 | +€1,355 (+11.9%) |
| 30% | +27.9% | 17.99 | 206.9 | €72.25 | 2.07 | +€1,747 (+15.3%) |

**Table 8 — Portfolio adjusted results** (baseline spend €18,600/mo; combined figures are exact sums of the rounded team figures)

| | **8.69% — default** | 10% | 15% | 20% | 25% | 30% |
|---|----:|----:|----:|----:|----:|----:|
| Combined monthly cost reduction | **+€157 (+0.8%)** | +€376 (+2.0%) | +€1,165 (+6.3%) | +€1,889 (+10.2%) | +€2,555 (+13.7%) | +€3,169 (+17.0%) |
| Combined FTE capacity released | **1.31** | 1.48 | 2.09 | 2.65 | 3.15 | 3.63 |

*Erratum, Edition 2: the 20% stop for Team 2 was shown as "+8.2%" in Edition 1 — a rounding slip; the correct figure on this cost base is +8.1%.*

### 5.3 Reading the scenarios

Four readings matter. **First, at the +8.69% default the portfolio is barely positive**: +€157/month overall, with Team 1 at +€339 (well above its 3.3% parity bar) and Team 2 at −€182 (still below its 10.4% bar). The honest summary for stakeholders: the tool spend is covered at portfolio level, but one team has not yet earned its licences. **Second, Team 1 is above water almost immediately**: any multiplier ≥ 3.3% clears its cost-parity bar, so the default already yields +€339/month, the 10% stop yields +€417, and by 25% the team delivers its baseline output for €1,200/month less. **Third, Team 2 is the marginal case**: its observed −2.1% drags even a 10% multiplier down to a combined +7.9% — still below the +8.33% threshold — so it remains €41/month under water at the 10% stop and only turns solidly positive from 15% upward (+€465/month), reaching €1,355–€1,747/month across the Gartner 25–30% range. **Fourth, the portfolio is positive from the 10% stop** (+€376/month) because Team 1's efficiency cushions Team 2's learning-curve drag, reaching +€2,555/month at 25% and +€3,169/month at 30%.

The strategic asymmetry deserves emphasis. Team 1's observed +5.0% means industry-standard evidence is mostly *confirmation* — its economics are already near break-even and any modest additional uplift compounds into savings. Team 2's observed −2.1% means industry-standard evidence is a *gap to close* — it must convert its AI investment into per-FTE efficiency (not just per-team throughput) before the licence pays for itself, and §6's recommendations address exactly that conversion.

---

## 6. Overall Findings

**Finding 1 — The two teams adopted AI in opposite directions, and per-FTE productivity exposes it.** Team 1 used AI to protect output while shrinking (−8.3% FTE, −3.8% output, **+5.0% per FTE**); Team 2 used it to boost throughput while growing (+21.1% FTE, +18.6% output, **−2.1% per FTE**). Raw output would flatter Team 2 and punish Team 1; story points per FTE show Team 1 actually improved its delivery system while Team 2's per-engineer rate dipped under scaling costs. Both are legitimate business choices, but they have opposite unit economics, and only the per-FTE metric tells them apart.

**Finding 2 — Neither observation cleared the +8.33% cost break-even, so story points got more expensive for both teams.** The €100 licence is 8.33% of a €1,200 FTE, so cost per story point stays flat only at ≥ +8.33% per-FTE gain. Team 1 (+5.0%) fell 3.3 percentage points short and its cost per story point rose 3.2% to €63.39; Team 2 (−2.1%) fell 10.4 percentage points short and its cost per story point rose 10.6% to €94.38. The observed data therefore does **not** yet support a "cheaper delivery" claim for either team — only a "slightly fewer people, nearly same output" claim for Team 1 and a "bought capacity at a unit premium" claim for Team 2. Priced as same-baseline-output delivery (§4.5), Phase 1 is a combined −€1,438/month.

**Finding 3 — Industry-standard evidence, applied on top of the observed baseline, turns the portfolio cash-positive at the default — but on different schedules per team.** At the +8.69% default the portfolio is already slightly positive (+€157/month, 1.31 FTE released, +9.4% FTE-weighted adjusted gain): Team 1 saves €339/month, Team 2 is still €182/month short of parity. Across the band, Team 1 saves €339–€1,422/month (default through 30%), while Team 2 moves from −€182/month at the default to +€1,747/month at 30%, breaking even between the 10% and 15% stops. The portfolio reaches +€2,555/month at 25% — the Gartner floor — worth 13.7% of baseline spend.

**Finding 4 — The decision metric for AI investment should be unit cost of a story point, not spend or raw velocity.** Team 1's spend fell 0.7% yet each story point became 3.2% more expensive; Team 2's velocity rose 18.6% yet each story point became 10.6% more expensive. Spend deltas and velocity deltas both mislead in isolation; effective cost per story point (monthly cost ÷ monthly story points) is the number that captures value, and the break-even gain of +8.33% is its simple decision rule at this price ratio.

**Recommendations.**

1. **Adopt story-points-per-FTE and cost-per-story-point as the standing KPI pair** for AI value tracking, reported per sprint against each team's own baseline, with the +8.33% break-even stated explicitly in the dashboard.
2. **For Team 2, prioritise converting throughput into efficiency before adding further headcount** — its 2.1% per-FTE slip under a 21% expansion is the classic coordination-and-onboarding drag, and the §5 scenarios show its licence only pays once per-FTE gain turns positive; target the 10.4% multiplier threshold as the improvement backlog's success criterion.
3. **For Team 1, bank the efficiency win and test the next 3–5%** — it sits 3.3 percentage points below break-even on observed data alone, so targeted AI use in its weakest workflow stage (e.g., review turnaround or test writing) is the cheapest available ROI, and every point beyond +8.33% is direct savings.
4. **Set slider-based planning targets rather than a single number**: **+8.69% as the evidence-default case** (portfolio just positive, Team 2 still under water — the honest baseline for commitments), 10% as the floor case (Team 1 positive, Team 2 near parity), 25% as the central case (both strongly positive, +€2,555/month portfolio), 30% as the stretch case (+€3,169/month).
5. **Extend the evidence base before hard commitments**: one sprint per state is a direction, not a rate — collect at least 3–4 sprints per state, hold story-point estimation practice constant, and re-run this analysis as a rolling baseline.

---

## 7. Methodology, Assumptions and Formulas

**Formulas.** The formula set below is identical to the dashboard's collapsible Formula Reference (F1–F16). Symbols: **FTE_B** baseline headcount · **SP** sprint story points · **s** sprints/month · **L** labour €/FTE/month (€1,200) · **A** AI seat €/FTE-month (€100) · **m** industry multiplier · **g** the gain in question (observed g, or adjusted g_adj in Phase 2).

```text
F1  Story points per FTE (sprint)  =  SP ÷ FTE
F2  Monthly output O               =  baseline sprint story points × s
F3  Monthly cost C                 =  FTE_B × L
F4  Productivity                   =  O ÷ FTE_B          (story points/FTE/month)
F5  Cost per story point CP         =  C ÷ O
F6  Observed gain g                =  (SP with-AI ÷ FTE with-AI) ÷ (SP baseline ÷ FTE_B) − 1   [Phase 1]
F7  Adjusted gain g_adj            =  g + m               (additive)                        [Phase 2]
F8  FTE-months needed              =  FTE_B ÷ (1 + g)
F9  Capacity released              =  FTE_B − FTE-months needed  =  FTE_B × g ÷ (1 + g)
F10 Capacity value                 =  capacity released × L
F11 AI tool spend                  =  FTE-months needed × A
F12 Monthly cost reduction S       =  C − FTE-months needed × (L + A)  =  capacity value − AI tool spend
F13 Break-even gain g_be          =  (L + A) ÷ L − 1  =  +8.33%
F14 Parity multiplier             =  g_be − g            (Team 1: 3.3% · Team 2: 10.4%)
F15 Combined % gain                =  Σ(FTE_i × g_i) ÷ Σ FTE_i                          (FTE-weighted)
F16 Combined € per story point    =  Σ(O_i × CP_i) ÷ Σ O_i                             (output-weighted)
```

**Worked example (Team 1, default inputs — matches the dashboard's Formula Reference).** O = 58.6 × 2 = 117.2 story points · C = 6 × €1,200 = €7,200 · g = (56.4 ÷ 5.5) ÷ (58.6 ÷ 6) − 1 = **+5.0%** · Phase 1: FTE-months needed = 6 ÷ 1.05 = 5.71 → capacity released 0.29 FTE, value €343; AI spend = 5.71 × €100 = €571 → S = €343 − €571 = **−€229** (a cost increase). Phase 2 at the +8.69% default: g_adj = +13.7% → FTE-months needed = 6 ÷ 1.137 = 5.28 → capacity released 0.72 FTE, value €867; AI spend = €528 → S = **+€339**.

**Assumptions.**

- **A1 · Cadence:** 2 sprints/month per team, stable sprint composition; no vacation or holiday effects modelled.
- **A2 · Labour:** €1,200 per FTE per month, fully loaded, identical in both states.
- **A3 · AI tool:** €100 per FTE-month for every active FTE-month; a loaded AI-enabled FTE-month costs €1,300.
- **A4 · Same-output framing:** every scenario delivers the *baseline monthly output* at the adjusted per-FTE efficiency; freed capacity is redeployed, not treated as a headcount cut.
- **A5 · Additive multiplier:** adjusted gain = observed + multiplier. Compounding would add only ~0.5 point at these values; additive is the conservative choice.
- **A6 · Rounding and combined rows:** per-team euros are rounded to whole euro; combined figures are exact sums of the rounded parts; combined percentages are FTE-weighted (F15); combined cost per story point is output-weighted (F16).
- **A7 · Confounding:** the with-AI sprint bundles AI with concurrent staffing changes (Team 1 −0.5 FTE, Team 2 +2.0 FTE); per-FTE normalization controls for size but cannot separate the two effects.
- **A8 · Evidence depth:** one sprint per team per state — treat observed results as directions, not rates, until a rolling multi-sprint baseline confirms them.
- **A9 · Multipliers are benchmarks:** Accenture × GitHub, Bain, Gartner, Capgemini and Microsoft figures are external planning evidence, not measurements of these two teams; the observed rows are the only measured data here.
- **A10 · Currency:** figures display in euro (€); the arithmetic is currency-agnostic.

**Limitations.** Story points are an output proxy, not a value measure, and one sprint per state is thin evidence: ±2 story points per FTE of estimation noise alone would move every observed delta materially. Team 2's negative per-FTE result may partly reflect transient onboarding cost that fades over subsequent sprints, and Team 1's +5.0% may partly reflect the healthy survivor effect after a staffing reduction. The staffing changes confound the with-AI observation; industry multipliers are external benchmarks; and the model is linear per month — it does not simulate ramp-up, quality rework, or scope mix. Use the observed rows for "what happened", the Phase 2 rows for "what a disciplined programme should beat", and re-baseline every sprint.
