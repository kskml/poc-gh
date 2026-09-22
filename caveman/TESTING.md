# Caveman Skill — Test Plan (GitHub Copilot in IntelliJ)

Goal: prove the skill (a) is detected, (b) activates, (c) saves tokens, (d) doesn't hurt quality.

Run each test in a **fresh Copilot chat** (right-click → New Chat / the "+" button) so
results aren't contaminated by history.

---

## Test 0 — Skill is installed & visible

| Step | Action | Pass |
|---|---|---|
| 0.1 | IntelliJ: **Settings → Tools → GitHub Copilot → Chat → Agent** — Agent Skills enabled (JetBrains AI Assistant: *Skills Manager* shows `caveman`) | Skill listed |
| 0.2 | Ask in Copilot chat: `List the agent skills available in this project.` | "caveman" appears in the list |

If 0.2 fails: check the file path (§ below), restart the IDE (skills are indexed at
startup in some versions), or verify with the fallback instructions file.

**Where the file must live**
- Project: `<project-root>/.github/skills/caveman/SKILL.md`
- Global: `~/.copilot/skills/caveman/SKILL.md` (JetBrains Skills Manager picks up global skills)

---

## Test 1 — Explicit invocation (does it work at all?)

Prompt:
```text
Use the caveman skill. Compress this prompt:
"Could you please help me refactor this function? I think it might have some
issues with how it handles the authentication, and I'd really like it to be
more efficient. Thanks!"
```

**Pass:** returns roughly `Refactor function. Fix auth handling. Make efficient.`
with a `~75% shorter`-style estimate line and **no preamble** ("Sure! Here's...").
**Fail signals:** pleasantries in output, or verbose explanation of what was removed.

## Test 2 — Intensity levels

Run three times, each in a fresh chat:
```text
caveman lite: "Can you explain what this error message means and how I should fix it?"
caveman full: <same>
caveman ultra: <same>
```
**Pass:** three visibly different compressions — lite keeps full sentences, full drops
articles, ultra uses fragments/abbreviations. Length must strictly shrink lite > full > ultra.

## Test 3 — Auto-activation (no mention of the skill)

Prompt (deliberately normal, verbose):
```text
I need a shorter version of the following text for a prompt I paste into AI
tools every day. It currently costs too many tokens:
"I'd like you to add comprehensive error handling to this API endpoint,
including validation of the request body, and please make sure to log any
failures so we can debug them later."
```
**Pass:** model applies caveman style automatically (e.g.,
`Add error handling to endpoint. Validate request body. Log failures.`) —
optionally confirm with a follow-up: `Which skill did you use?`
**Fail:** returns a normal "paraphrase" without compression style → tighten the
`description:` frontmatter (it's the trigger Copilot matches on).

## Test 4 — A/B output terseness (the money test)

Same prompt, twice, fresh chats each:

```text
Explain why a React component re-renders when passed an inline object, and show the fix.
```

- **Run A:** caveman skill active
- **Run B:** skill disabled (Skills Manager → disable `caveman`, or temporarily rename
  `SKILL.md` → `SKILL.md.bak`; restart IDE if needed)

Measure: word count and line count of both answers (select text → status bar shows
word count in the editor, or paste into a word counter).

**Pass:** Run A is ≥ 30% shorter **and** contains the same key facts
(new reference each render → new ref → re-render; `useMemo`/extraction fix).
Expect 40–55% output savings with `full` (per the reference guide).

## Test 5 — Input side: caveman prompts still work

Write your own prompts in caveman-full and check the model executes them correctly:

| Caveman prompt | Expected behavior |
|---|---|
| `Refactor getUserById. Support emails too. 404 if missing.` | Modifies the function, no clarifying questions needed |
| `Add e2e test for login flow. Happy + fail paths.` | Test file created with both paths |
| `Fix null deref in pay() L42. Done: npm test green.` | Targets exactly that line, stops when tests pass |

**Pass:** all three executed with **zero clarification round-trips** and correct results.
Clarification round-trips are the real cost — they burn whole context windows in agent mode.

## Test 6 — Quality guard (compression must not break code)

```text
caveman full:
fn(nums) → filter(>0) → map(*2) → sum. Write it in Python with type hints + 3 tests.
```
Run the generated tests (IntelliJ: Run icon in the test gutter).

**Pass:** tests pass first try, output code unchanged/clean (caveman must NOT leak
into generated code — no `fn` shorthand in Python, no articles in docstrings if your
style forbids it).

## Test 7 — Persistence

Open a **brand-new project** (or new chat in the same project) and re-run Test 1.
- Project skill: works only in that project → as expected.
- Global skill (`~/.copilot/skills/...`): works in the new project → pass.

---

## Measuring hard token numbers (optional)

IntelliJ's chat UI doesn't expose a `/context`-style breakdown. Two practical options:

1. **Word/line-count proxy** (Test 4) — good enough for relative A/B.
2. **Copilot CLI** (works alongside IntelliJ, and JetBrains supports it): run the
   identical prompts in the CLI with the skill on/off and compare
   `/context` (context breakdown) and `/usage` (cumulative tokens + cache read/write).
   This is the only place you get per-request `prompt_tokens` / `completion_tokens`.

## Pass criteria (summary)

| # | Check | Threshold |
|---|---|---|
| 1 | Skill listed in project | yes |
| 2 | Explicit invocation works | compressed + ~% line, no preamble |
| 3 | lite > full > ultra | strictly shorter each step |
| 4 | A/B output length | ≥ 30% shorter, same facts |
| 5 | Caveman input prompts | 0 clarification round-trips |
| 6 | Generated code + tests | passes, no style leakage |
| 7 | New session/project | still active (global) |

If Test 6 fails or Test 5 needs clarifications: drop one intensity level
(`ultra` → `full` → `lite`) for that task class. Shorter ≠ better when it costs a rework loop.
