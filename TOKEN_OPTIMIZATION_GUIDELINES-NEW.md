# GitHub Copilot Token Optimization Guidelines

> **Purpose.** Practical, copy-paste rules for using GitHub Copilot (and VS Code Copilot Chat) while spending fewer tokens — cheaper, faster, and less context bloat. No theory; each rule is followed by a concrete example.

---

## 1. Use references (`#`) instead of pasting code

Never paste file bodies into a prompt. Reference them and let Copilot pull the relevant part.

| Reference | Meaning | Example |
|---|---|---|
| `#file:path` | A specific file | `Fix the bug in #file:src/auth.ts` |
| `#selection` | Your current selection | `Review #selection` |
| `#editor` | The visible editor tab | `Document #editor` |
| `#terminal` | Current terminal selection | `Why does this error occur? #terminal` |
| `#localChanges` | Your uncommitted diff | `Write tests for #localChanges` |
| `#symlink` | Contents of a symlinked file | `Explain #symlink` |
| `#tree` | Folder structure (VS Code Insiders) | `Map #tree` |

**Guideline 1.1** — Reference, don't paste.
- ❌ Paste 300 lines of a file plus "review this."
- ✅ `Review #file:src/auth.ts` — Copilot reads only what it needs.

**Guideline 1.2** — Reference the *smallest* unit that answers the question. Prefer `#selection` over `#editor`, `#editor` over `#file`, a single file over multiple.

**Guideline 1.3** — When a symbol is enough, name it instead of referencing a whole file.
- ✅ `Explain the `authenticate()` function in #file:src/auth.ts`

**Guideline 1.4** — Reference only files relevant to the task. Every `#file` adds tokens; two files are usually enough, five is context bloat.

---

## 2. Use scopes (`@`) to point Copilot at context

| Scope | What it does | Example |
|---|---|---|
| `@workspace` | Searches the whole workspace with agentic tools | `Where is rate limiting configured? @workspace` |
| `@terminal` | Reads terminal output to answer | `The build failed; diagnose it @terminal` |
| `@` + model/agent pickers | Select model or agent mode | Pick the model via the chat model dropdown |

**Guideline 2.1** — Use `@workspace` for *search* questions ("where is X?") — it indexes the codebase instead of you pasting files.

**Guideline 2.2** — Do not use `@workspace` for a question you can answer with one `#file`. Scopes are more token-expensive than references.

**Guideline 2.3** — For a failing command, attach `@terminal` rather than copy-pasting the error log. Copilot gets the output without you formatting it.

- ❌ Paste the whole stack trace.
- ✅ `The npm build fails on this machine. Diagnose @terminal`

---

## 3. Use slash commands for boilerplate-heavy tasks

Slash commands supply the instruction; you supply only the subject. That removes your essay from the prompt.

| Command | Task | Example |
|---|---|---|
| `/explain` | Explain the selection concisely | `/explain` on a function |
| `/tests` | Generate tests for the selection | `/tests #selection` |
| `/fix` | Fix errors in the selection/terminal | `/fix @terminal` |
| `/simplify` | Shorten/refactor the selection | `/simplify #selection` |
| `/doc` | Add documentation/comments | `/doc #file:src/api.ts` |
| `/new` | Scaffold a new file from one line | `/new a React hook for debouncing` |
| `/diagram` | Visualize code structure | `/diagram #file:src/main.ts` |
| `/clear` | Reset the chat and free the context window | `/clear` before each new task |
| `/help` | Show available commands | `/help` |

**Guideline 3.1** — Prefer a slash command over a free-text prompt when one matches the task. The command already contains the optimal instruction.

**Guideline 3.2** — Combine command + reference in one line:
- ✅ `/tests #file:src/validate.ts`
- ✅ `/fix @terminal`

**Guideline 3.3** — Use `/clear` between unrelated tasks. Stale chat history re-bills old tokens on every turn and degrades answers.

**Guideline 3.4** — Use `/new` with a one-line spec; let Copilot scaffold instead of you describing structure in prose.

---

## 4. Write short, high-signal prompts

Keep the instruction small: task first, then the one or two constraints that matter, then the reference.

**Guideline 4.1** — State the task, not the backstory.
- ❌ "I've been working on this auth module for a while and the token refresh keeps failing intermittently and I'm not sure if it's a race condition or a caching issue, could you take a look at the relevant parts and let me know what you think might be going wrong and maybe suggest some fixes?"
- ✅ `The refresh token endpoint intermittently fails. Find the cause in #file:src/auth/refresh.ts and propose a fix.`

**Guideline 4.2** — Cap the output with one constraint.
- ✅ `Suggest a fix in ≤3 bullet points.`
- ✅ `Explain in 1 paragraph.`
- ❌ "Give me a detailed comprehensive analysis with options, trade-offs, and a full rewrite."

**Guideline 4.3** — Ask for a diff, not an explanation.
- ✅ `Fix it` / `Refactor it` — you get code back.
- ❌ `Describe the problem and tell me how you would fix it.`

**Guideline 4.4** — One task per message. Multi-part prompts produce long answers and wasted tokens.

**Guideline 4.5** — Use terse, unambiguous verbs: `Explain`, `Fix`, `Refactor`, `Rewrite`, `Convert`, `Test`, `Document`, `Simplify`.

---

## 5. Don'ts that waste tokens (anti-patterns)

- ❌ **Politeness padding:** "Please, if you wouldn't mind, could you possibly…" — say it in one sentence.
- ❌ **Restating capability:** "You are an expert senior engineer with 20 years of experience…" — add nothing.
- ❌ **Pasting full files** when `#file` works.
- ❌ **Re-explaining context already visible:** the editor, selection, and terminal are already visible — don't re-describe them.
- ❌ **One giant chat for everything:** history grows every turn; start a new chat per task, or `/clear`.
- ❌ **Asking for alternatives you won't use:** "give me three approaches" pays for three outputs, uses one.
- ❌ **Pasting your expected answer in the prompt** — the model echoes it back and you paid for both.
- ❌ **Unbounded verbosity:** no length cap on a "explain" prompt on paid output tokens.

---

## 6. Model and mode selection

**Guideline 6.1** — Use the cheapest model that finishes the task.
- Simple explain/refactor of a small function → smaller/faster model.
- Multi-file refactor, agentic search, hard debugging → larger model.

**Guideline 6.2** — Use Agent mode (`@workspace` / agent) only for multi-file or search tasks. For a single-file edit, plain chat or inline chat is cheaper.

**Guideline 6.3** — Set the model once per session; switching models mid-chat restarts reasoning and wastes context.

**Guideline 6.4** — For predictable, repeated edits, use **inline chat / quick actions** (select code → Ctrl+I / right-click → "Fix", "Generate Docs") — they ship a fixed minimal prompt instead of your typed one.

---

## 7. Workspace and environment hygiene

**Guideline 7.1** — Keep files small and focused. Copilot context grows with open tabs; close editors you're not using.

**Guideline 7.2** — Configure Copilot to skip context you don't need (node_modules, build output) so the model isn't fed junk.
- Keep large/generated dirs out of the indexing scope.

**Guideline 7.3** — For big refactors, break into steps: one file at a time, one `/tests` run at a time. Each step is cheaper and easier to verify than one mega-prompt.

**Guideline 7.4** — After a model/tooling update, re-test prompt style. Token behavior and defaults change between Copilot versions.

---

## Putting It All Together

**Worked example — "fix the failing login test":**
1. `/clear` to start fresh.
2. ✅ `The login spec fails intermittently. Fix #file:src/login.spec.ts` (reference, not paste).
3. If the failure is in output, ✅ `/fix @terminal` instead of re-pasting logs.
4. Then ✅ `/tests #selection` to regenerate coverage from the fixed code.
5. End with `/clear`.

Each step uses a reference, a scope, or a command — no pasting, no essays, minimal history.

**Quick reference card**

| Rule | One-liner |
|---|---|
| Reference, don't paste | `#file:`, `#selection`, `#editor`, `#localChanges` |
| Scope search, not chat | `@workspace`, `@terminal` |
| Prefer commands | `/explain` `/fix` `/tests` `/simplify` `/doc` `/new` |
| Fresh chat per task | `/clear` |
| Cap output | "≤3 bullets", "1 paragraph" |
| Ask for the diff | `Fix it`, not "describe the problem" |
| Smallest model that works | bigger ≠ better for small edits |
| One task per prompt | single verb, single subject |
