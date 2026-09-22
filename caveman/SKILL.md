---
name: caveman
description: Compress prompts, instructions, and responses into caveman-speak to cut tokens ~30-70% without losing meaning. Use when the user asks to compress, shorten, tighten, or "caveman" a prompt, message, or instruction file, or asks for a terse version of text. Also use to rewrite verbose copilot-instructions.md / AGENTS.md content.
---

# Caveman — token compression

## When to apply
- User asks to compress / shorten / tighten / "caveman" any prompt, message, or instructions
- User pastes verbose text and wants the minimal-token version
- Rewriting `copilot-instructions.md`, `AGENTS.md`, or prompt files for the repo

## Rules (priority order)
1. **Keep exact:** technical terms, code, constraints, file/function/line references, done-conditions, security rules
2. **Drop:** articles (a/an/the), fillers (just, really, basically, actually, simply), pleasantries ("Sure!", "Of course!"), hedging ("I think", "maybe", "probably", "you might want to")
3. **Fragment pattern:** `[thing] [action] [reason]. [next step].`
4. **Structured beats prose:** multi-part asks → bullets or key-value, never paragraphs
5. **Abbreviate repeated terms:** DB, auth, config, req/res, fn, impl, env, deps, repo, PR, e2e. (Project-specific shorthand: define once, then use.)
6. **Code beats prose:** pseudocode, type signatures, "Like `X` but `Y`."
7. **Guardrails declarative, not imperative:** "All exported fns: JSDoc required." — not step-by-step procedures

## Intensity levels
| Level | Style | Use for |
|---|---|---|
| `lite` | No fillers/hedges; keep articles + full sentences | Client-facing text, docs, onboarding |
| `full` (default) | Drop articles; fragments OK; short synonyms | Daily dev prompts, most tasks |
| `ultra` | Abbreviate common terms; arrows for causality (`A → B → C`) | High-volume chat, cold-known domain |

If the user doesn't specify, default to `full` and say which level was used.

## Output format when compressing
1. Compressed text first (in a code block if it's a prompt to reuse)
2. One line of savings estimate: `~NN% shorter (M → N tokens)`
3. Nothing else — no preamble, no explanation of what was removed, unless asked

## Never compress
- Security constraints (state them exactly)
- Novel or project-specific terms (define once first)
- Text the user marks as verbatim / legal / client-facing
- If ambiguity is possible, keep the longer form — an ambiguous short prompt costs more in rework than it saves in tokens

## Example
```text
In:  "Could you please review this pull request and let me know
     if there are any issues? Thanks!"
Out: "Review PR. Flag issues."
     ~71% shorter (~17 → ~5 tokens)
```
