# AI Assistant Usage Guidelines

| | |
|---|---|
| **Version** | 6.0 |
| **Audience** | Anyone using ChatGPT, Claude, Gemini, Copilot Chat, Perplexity, or similar |
| **Purpose** | Get better answers, faster, using fewer tokens |
| **Structure** | Four primary categories (Prompting Techniques, LLM Selection, Handling Context, Skill-Based) + additional categories |

---

## Table of Contents

1. Prompting Techniques
2. LLM Selection
3. Handling Context (Context Engineering)
4. Skill-Based Category
5. Additional Categories
   - 5.1 Cost Awareness
   - 5.2 Safety & Privacy
6. Cheat Sheet

---

## 1. Prompting Techniques

**How to craft your questions to get short, useful answers.**

| # | Rule | Don't | Do |
|---|---|---|---|
| 1.1 | **Say what you want first.** | `I was wondering if you could help me understand this article?` | `Summarize this article in 3 bullets.` |
| 1.2 | **Set a max length.** | `Summarize this.` | `Summarize in under 100 words.` |
| 1.3 | **Pick the simplest format.** | `Tell me about the bug.` | `Classify as [crash, error, slowdown, other]. Output only the label.` |
| 1.4 | **Say what NOT to do.** | — | `No explanation. No examples. Don't repeat my question.` |
| 1.5 | **Add "output only".** | `Translate to French.` | `Translate to French. Output only, no preamble.` |
| 1.6 | **One question per message.** | `Summarize, translate, and extract entities.` | Three separate messages. |
| 1.7 | **Skip politeness.** | `Please could you maybe summarize this?` | `Summarize this.` |
| 1.8 | **Give examples only when needed.** | Always include 3 examples. | Add 1 example only if the assistant gets it wrong. |
| 1.9 | **Use simple words.** | `Utilize your capabilities to facilitate analysis.` | `Analyze this.` |
| 1.10 | **Be specific.** | `Help with my email.` | `Rewrite this email to be professional, under 100 words.` |
| 1.11 | **Skip reasoning for simple tasks.** | Let it explain why Paris is the capital. | `Capital of France? Just the name.` |
| 1.12 | **Ask for the format.** | `Compare these phones.` | `Compare as a table: Price, Battery, Camera, Verdict.` |
| 1.13 | **Ask for a tone.** | — | `Tone: professional.` / `Tone: casual.` / `Tone: friendly, like texting a friend.` |
| 1.14 | **Ask for a reading level.** | — | `Explain like I'm 12.` / `Explain for a non-technical adult.` |
| 1.15 | **Ask for "just the answer".** | `Write a Python function to validate emails.` | `Write a Python function to validate emails. Output only the code, no explanation.` |
| 1.16 | **Ask for the diff, not the whole thing.** | `Rewrite this whole email.` | `Show only the lines you'd change, before/after.` |
| 1.17 | **Use "regenerate" sparingly.** | Click regenerate 5 times hoping for better. | Edit your question instead. |
| 1.18 | **Stop when you have enough.** | Let it finish 500 tokens you won't read. | Click Stop. |

### Question Template

```
[Action verb] [object] in [format] under [length limit].
[Constraints: what to do / not do].
[Context: only what's needed].
```

**Example:**
```
Summarize the attached PDF in a bullet list under 100 words.
Focus on the marketing recommendations. Skip intro and conclusion.
The PDF is a 2025 market research report for a SaaS startup.
```

---

## 2. LLM Selection

**Pick the smallest model that can do your task.**

| # | Rule | When |
|---|---|---|
| 2.1 | **Use the small/fast model by default.** | GPT-4o-mini, Claude Haiku, Gemini Flash — for summary, translate, short email, extraction, brainstorm. |
| 2.2 | **Use the big model for hard tasks.** | GPT-4o, Claude Sonnet/Opus, Gemini Pro — for reasoning, long docs (30+ pages), detailed writing, code architecture, legal/medical/financial. |
| 2.3 | **Use the reasoning model only when needed.** | GPT-o1/o3, Claude with extended thinking — for multi-step math, logic, complex planning. Don't use for emails or simple Q&A. |
| 2.4 | **Don't use vision for text-only tasks.** | Copy-paste text. Don't screenshot a paragraph. |
| 2.5 | **Switch models mid-chat if needed.** | If the small model fails, switch to big and re-ask. |
| 2.6 | **Re-test every quarter.** | Tasks that needed the big model may now work on the small one. |

---

## 3. Handling Context (Context Engineering)

**Give the assistant exactly what it needs — nothing more. Treat the conversation as a budget, not a bucket.**

| # | Rule | Don't | Do |
|---|---|---|---|
| 3.1 | **Attach files, don't paste long text.** | Paste 10 pages into chat. | Upload the PDF. |
| 3.2 | **Pin the specific file.** | `What does my contract say about termination?` (10 files attached) | `In "contract_2025.pdf", what does it say about termination?` |
| 3.3 | **Send only the section you need.** | Attach a 200-page manual to ask about one feature. | Copy the 2 relevant pages. |
| 3.4 | **Don't repeat context already in chat.** | Re-explain background every turn. | Say it once; the assistant remembers. |
| 3.5 | **Give background once, at the start.** | — | `I'm a small business owner. Need a 200-word email to a vendor asking for a discount. Tone: polite but firm.` |
| 3.6 | **Don't add irrelevant context.** | `So I've been at this company 5 years and my boss is Sarah... by the way summarize this article.` | `Summarize this article in 3 bullets.` |
| 3.7 | **Use web search for public info.** | Paste a Wikipedia article. | Let the assistant search the web. |
| 3.8 | **New chat when topic changes.** | One chat for vacation, work email, and coding. | One topic per chat. |
| 3.9 | **Don't let chats exceed ~10 turns.** | — | Summarize, then start fresh. |
| 3.10 | **Summarize before starting fresh.** | — | `Summarize our chat in 5 bullets. I'll paste into a new chat.` |
| 3.11 | **Edit your question instead of asking again.** | Ask a new question to fix a typo. | Edit the prior message; chat restarts from there. |
| 3.12 | **Stop and redirect when off-track.** | Let it finish a wrong answer. | `Stop. I want X, not Y. Try again.` |
| 3.13 | **Use descriptive chat titles.** | `Chat from Tuesday` | `Q4 marketing plan — draft 1` |
| 3.14 | **Don't ask it to remember across chats.** | "Remember this for next time." | Use the memory/custom-instructions feature. |

### When to Start Over

| Trigger | Action |
|---|---|
| Topic changes | New chat |
| Answers getting worse or generic | New chat |
| You switched models | New chat |
| Chat past ~10 turns | Summarize → new chat |
| 3+ back-and-forth trying to get it right | New chat with clearer question |

---

## 4. Skill-Based Category

**Use built-in tools, shortcuts, and saved patterns to do more with fewer tokens.**

### 4.1 Built-in Tools

| # | Rule | When |
|---|---|---|
| 4.1.1 | **Use web search for current info.** | News, prices, weather, recent events. |
| 4.1.2 | **Use code execution for math/data.** | Calculations, spreadsheet analysis. The assistant can't do mental math reliably. |
| 4.1.3 | **Upload files for document analysis.** | PDFs, Word, Excel, CSV. Don't paste their contents. |
| 4.1.4 | **Turn off tools you don't need.** | Active tools slow the response. |
| 4.1.5 | **Don't generate images if text works.** | Don't ask for a pie chart image — ask for a text table. |
| 4.1.6 | **Upload data files, don't type rows.** | Spreadsheets → upload as file. |

### 4.2 Custom Instructions & Memory

| # | Rule |
|---|---|
| 4.2.1 | **Use the assistant's custom-instructions/memory setting.** Set once: `Always short answers. No preamble. Plain text.` |
| 4.2.2 | **Save templates for repeated tasks.** E.g., `Summarize meeting notes. Format: [Decisions] [Action items] [Open questions]. Max 200 words.` |

### 4.3 Reusing Answers

| # | Rule |
|---|---|
| 4.3.1 | **Save good answers to your notes.** Searching notes is faster than re-asking. |
| 4.3.2 | **Bookmark important chats.** Use the star/pin feature. |
| 4.3.3 | **Export long chats.** You may lose access to old chats. |
| 4.3.4 | **Search history before re-asking.** Don't pay twice for the same answer. |
| 4.3.5 | **Reuse good prompts.** Keep a file of "prompts that worked". |

### 4.4 GitHub Copilot Chat Shortcuts

| # | Rule | Don't | Do |
|---|---|---|---|
| 4.4.1 | **Pin files with `#file:`** | `@workspace Why is auth failing?` | `#file:src/middleware/auth.ts Why does this return 401 with a valid token?` |
| 4.4.2 | **Use `#selection` for visible code.** | — | Select code → `#selection What happens if refresh token expires during retry?` |
| 4.4.3 | **Use `#problems` + `/fix` for errors.** | Describe error in prose. | `/fix #problems` |
| 4.4.4 | **Use `#changes` to review uncommitted work.** | — | `#changes Review for bugs. Table: Severity, File, Issue, Fix.` |
| 4.4.5 | **Use `#terminalLastCommand` for failures.** | Paste error output. | `#terminalLastCommand Why did this fail? Minimal fix.` |
| 4.4.6 | **Use `#git` for commit messages.** | Write by hand. | `#git Write a conventional commit message for staged changes.` |
| 4.4.7 | **Avoid `#codebase` when you know the file.** | `@workspace #codebase Where do we verify webhooks?` | `#file:src/webhooks/verify.ts Review signature verification.` |
| 4.4.8 | **Pick the narrowest `@` participant.** | `@workspace` for everything. | `@terminal` < `@vscode` < `@github` < `@workspace` (cheapest to priciest) |
| 4.4.9 | **Use slash commands.** | — | `/fix` · `/tests` · `/doc` · `/explain` · `/new` · `/clear` |
| 4.4.10 | **`/clear` between unrelated tasks.** | — | — |
| 4.4.11 | **Use inline chat (`Cmd/Ctrl+I`) for quick refactors.** | Open chat panel for one-shot change. | Select code → `Cmd/Ctrl+I` → `Extract to function validateEmail` |
| 4.4.12 | **Add `.github/copilot-instructions.md`.** | Repeat conventions in every chat. | `# Conventions: React + TS. Functional components. Named exports. kebab-case files.` |
| 4.4.13 | **Always cap the output.** | `Explain the auth flow` | `#file:src/auth.ts Explain the auth flow in ≤ 8 steps.` |
| 4.4.14 | **Stop the stream when you have enough.** | — | Click Stop. |
| 4.4.15 | **Use `@github` for issues/PRs.** | Paste issue body. | `@github Summarize issue #432 in 3 bullets.` |

---

## 5. Additional Categories

### 5.1 Cost Awareness

| # | Rule |
|---|---|
| 5.1.1 | **Know your plan.** Flat subscription vs. metered (pay-per-token). |
| 5.1.2 | **Use the small model by default.** 5–25× cheaper on metered plans. |
| 5.1.3 | **Don't re-ask the same question.** Search history first. |
| 5.1.4 | **Stop long generations.** Every extra token costs money or quota. |
| 5.1.5 | **Use batch APIs for big jobs.** Often 50% discount for 24h turnaround. |
| 5.1.6 | **Check usage weekly.** Catches runaway spend. |
| 5.1.7 | **Set spending alerts.** At 50%, 80%, 100% of budget. |
| 5.1.8 | **Don't share accounts.** Each user = own account. |

### 5.2 Safety & Privacy

| # | Rule |
|---|---|
| 5.2.1 | **Never paste passwords, API keys, tokens, or private keys.** |
| 5.2.2 | **Never paste customer PII** (names, emails, phones, addresses). |
| 5.2.3 | **Never paste confidential company info** (financials, trade secrets, internal docs marked confidential). |
| 5.2.4 | **Check the data policy.** Know whether your assistant trains on your data. Turn off training if possible. |
| 5.2.5 | **Don't trust for high-stakes decisions.** Medical, legal, financial — verify with a qualified human. |
| 5.2.6 | **Don't click links blindly.** Hover first. Assistants hallucinate URLs. |
| 5.2.7 | **Be skeptical of "facts".** Cross-check with a real source. |

---

## 6. Cheat Sheet

### Top 10 Rules

1. Say what you want first.
2. Always set a max length.
3. Add "output only".
4. One question per message.
5. Skip politeness.
6. Use the small model by default.
7. New chat when topic changes.
8. Stop when you have enough.
9. Don't re-ask questions you already asked.
10. Never paste secrets or customer data.

### One-Line Summary

> **Say exactly what you want, in the format you want, as short as possible — using the smallest model that works, in a fresh chat when the topic changes.**

### Quick Reference

| Situation | Do |
|---|---|
| Ask a question | Verb first, set length, output only |
| Pick a model | Small for simple, big for hard |
| Long document | Attach as file |
| Need one section | Copy just that section |
| Topic changes | New chat |
| Chat too long | Summarize, start fresh |
| Want a format | Say "table" / "bullets" / "JSON" |
| Have what you need | Click Stop |
| Asked before | Search history |
| Copilot Chat | `#file:`, `#selection`, `/fix #problems`, `/clear` |
| Cost matters | Small model, watch usage, stop early |
| Sharing data | No passwords, no PII, no confidential info |

---

*Try one rule today. You'll see the difference.*
