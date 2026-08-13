# AI Assistant Usage Guidelines

**Version:** 7.0  
**Audience:** Anyone using ChatGPT, Claude, Gemini, Copilot Chat, Perplexity, or similar  
**Purpose:** Get better answers, faster, using fewer tokens

---

## Table of Contents

1. [Overview & Objective](#overview--objective)
2. [Strategy](#strategy)
3. [Prompting Techniques](#1-prompting-techniques)
4. [LLM Selection](#2-llm-selection)
5. [Handling Context (Context Engineering)](#3-handling-context-context-engineering)
6. [Skill-Based Category](#4-skill-based-category)
7. [Additional Categories](#5-additional-categories)
8. [Cheat Sheet](#6-cheat-sheet)

---

## Overview & Objective

AI assistants — ChatGPT, Claude, Gemini, Copilot Chat, Perplexity — run on **tokens**: the small chunks of text they read (input) and write (output). Tokens drive cost, speed, and quality. Most users waste 30–70% of theirs through long chats, pasted documents, repeated context, over-powered models, and avoidable re-asks.

**Objective:** Get faster, cheaper, better answers by changing how you use AI assistants — without learning prompt engineering jargon.

**Outcomes when applied:**

- 2–5× faster responses
- 50–90% lower token cost on metered plans
- Higher quality answers (less noise for the assistant)
- Longer effective quota (each chat stays small)
- Lower risk of leaking sensitive data

**Scope:** For end-users of AI assistants. Not for developers building assistants, and not for coding-specific dev agents (Cursor, Devin, Aider — separate guides).

---

## Strategy

Token optimization is a **system of reinforcing levers**. Apply any one and you'll see modest gains. Apply several together and the gains compound — typically 70–90% cost reduction with no loss of quality.

### The Levers

| Lever | What You Control | Typical Impact |
|---|---|---|
| **Prompting** | How you word your question | 30–60% output reduction |
| **Model Selection** | Which model you pick | 5–25× cost difference |
| **Context Engineering** | What's in the chat when you ask | 30–70% input reduction |
| **Skills & Tools** | Built-in tools, shortcuts, templates | 20–50% across-the-board |
| **Caching & Reuse** | Saving and reusing answers/prompts | Eliminates repeat cost |
| **Multimodal Choices** | Text vs. image vs. audio decisions | 5–10× on vision/audio tasks |
| **Output Control** | When to stop, regenerate, or edit | 10–30% output reduction |
| **Conversation Hygiene** | When to start over, archive, or branch | Prevents context rot |
| **Cost & Usage Management** | Plans, budgets, monitoring | Catches runaway spend |
| **Safety & Privacy** | What not to share | Prevents data leaks |

These multiply. A 50% cut from prompting × a 10× cut from model selection × a 50% cut from context = **25× net reduction** in cost-per-answer — before counting the savings from reuse, output control, and hygiene.

### Core Principle

> **Smallest input. Smallest capable model. Smallest useful output. Fresh chat when the topic changes. Reuse what worked. Share nothing sensitive.**

### Strategy in Plain Terms

1. **Be ruthless about input.** Don't paste what you don't need. Don't repeat what you said. Don't attach a 200-page manual to ask about one paragraph.
2. **Default to cheap.** Use the smallest, fastest model by default. Escalate only when it fails. Most everyday tasks don't need the big model.
3. **Constrain the output.** Always set a length. Always pick a format. Always say what *not* to include.
4. **Keep chats short and focused.** One topic per chat. Past 10 turns = summarize and start fresh.
5. **Use the assistant's built-in tools.** Web search, file upload, code execution, custom instructions, slash commands. They exist to save you time and tokens.
6. **Stop early.** Click Stop the moment you have what you need.
7. **Don't re-ask.** Search history first. Save good answers. Reuse good prompts.
8. **Pick the right modality.** Don't upload an image when copy-pasted text works. Don't generate audio when text-to-speech on your device works.
9. **Watch your spend.** Know your plan. Check usage weekly. Set alerts.
10. **Protect sensitive data.** No passwords, no customer PII, no confidential company info.

### When to Apply Each Lever

| Situation | Most Important Lever |
|---|---|
| Quick factual question | Model selection (small model) |
| Long document analysis | Context (attach as file) |
| Writing a tricky email | Prompting (tone, length, format) |
| Multi-turn research session | Context + Conversation hygiene |
| Repetitive task | Skills + Caching (save a template, reuse) |
| Using Copilot Chat | Skills (`#file:`, `#selection`, `/fix`, `/clear`) |
| Image, audio, or PDF input | Multimodal choices (extract text first) |
| Cost spike on metered plan | Model selection + Context + Cost management |
| About to paste a password or customer data | Safety & privacy (don't) |
| Assistant going off-track | Output control (Stop, edit, redirect) |

### Maturity Ladder

| Stage | Behavior | Cost vs. Novice |
|---|---|---|
| **1. Novice** | Long chats, no limits, big model for everything, pastes everything | Baseline (highest) |
| **2. Aware** | Sets length limits, uses "output only", small model sometimes, stops early | –30 to –40% |
| **3. Skilled** | New chats per topic, files instead of pasting, templates, knows model fit, reuses answers | –60 to –70% |
| **4. Expert** | All levers fluent, prompt library, multimodal-aware, monitors spend, never leaks data | –80 to –90% |

Novice → Aware takes a day. Aware → Skilled takes a week. Skilled → Expert takes a month.

### What to Do This Week

1. **Set custom instructions:** `Short answers. No preamble. Plain text.`
2. **Always set a max length:** add `in under 100 words` or `in 3 bullets`.
3. **Use the small model** for your next 10 questions. Switch to big only when it fails.
4. **New chat when the topic changes.** Always.
5. **Click Stop** the moment you have what you need.

These five habits cut token usage in half within a week.

### What to Do This Month

6. **Build a prompt library.** Save 5–10 prompts that worked.
7. **Learn the Copilot Chat shortcuts** (if you use Copilot): `#file:`, `#selection`, `#problems`, `#changes`, `/fix`, `/clear`.
8. **Audit chat history.** Delete what you don't need. Rename what you keep.
9. **Check usage dashboard weekly.** Spot runaway spend early.
10. **Re-test old tasks on the small model.** Models improve; yesterday's big-model task may work on the cheap model today.
11. **Extract text from images/PDFs before sending.** Don't pay vision-token prices for text.

---

## 1. Prompting Techniques

*How to craft your questions to get short, useful answers.*

### 1.1 Front-Load the Task

**Rule:** Start your question with the action you want.

The assistant pays the most attention to the first sentence. If you bury the request, the answer is worse.

- **Don't:** `I was wondering if you could help me understand this article?`
- **Do:** `Summarize this article in 3 bullets.`

### 1.2 Set a Maximum Length

**Rule:** Always tell the assistant how long the answer should be.

Without a limit, the assistant writes a long essay. With a limit, you get exactly what you need.

- **Don't:** `Summarize this article.`
- **Do:** `Summarize in under 100 words.`

### 1.3 Pick the Simplest Format

**Rule:** Ask for the format that fits your need — bullet list, table, single word, or paragraph.

A bullet list is shorter and clearer than paragraphs. A single label is shorter than a bullet list.

- **Don't:** `Tell me about the bug.`
- **Do:** `Classify as [crash, error, slowdown, other]. Output only the label.`

### 1.4 Say What NOT to Do

**Rule:** Tell the assistant what you don't want.

A small "don't" saves a lot of unwanted text. Use phrases like:

- `No explanation.`
- `No examples.`
- `Don't repeat my question.`
- `Don't suggest improvements unless I ask.`

### 1.5 Add "Output Only"

**Rule:** Append "output only" or "no preamble" to your question.

The assistant often starts with "Sure! Here's..." — that's wasted text.

- **Don't:** `Translate to French.`
- **Do:** `Translate to French. Output only, no preamble.`

### 1.6 One Question per Message

**Rule:** Ask one thing per message.

Multi-part questions get long, confused answers. Break them into separate messages.

- **Don't:** `Summarize this, translate it to French, and extract the key points.`
- **Do:** Ask three separate questions, one at a time.

### 1.7 Skip Politeness

**Rule:** Skip "please", "could you", "I was wondering if".

Politeness words add tokens without adding meaning. The assistant doesn't care about manners.

- **Don't:** `Please could you maybe summarize this for me?`
- **Do:** `Summarize this.`

### 1.8 Give Examples Only When Needed

**Rule:** Don't add examples unless the assistant is getting it wrong.

Examples make your question longer. Use them only when the assistant needs help understanding.

### 1.9 Use Simple Words

**Rule:** Write the way you talk. Don't use fancy words.

Simple words are easier for you to write and easier for the assistant to understand.

- **Don't:** `Utilize your capabilities to facilitate analysis.`
- **Do:** `Analyze this.`

### 1.10 Be Specific

**Rule:** Give details. Don't make the assistant guess.

Vague questions get generic answers. Specific questions get useful answers.

- **Don't:** `Help with my email.`
- **Do:** `Rewrite this email to be professional, under 100 words.`

### 1.11 Skip Reasoning for Simple Tasks

**Rule:** For simple questions, tell the assistant to skip the reasoning. For hard questions (math, logic, planning), let it show its work — but cap the length.

- **Don't:** Let the assistant explain why Paris is the capital of France.
- **Do (simple):** `Capital of France? Just the name.`
- **Do (hard):** `Solve this step by step. Show reasoning in 4 bullets or fewer. Then give the final answer.`

### 1.12 Ask for the Format

**Rule:** Say "as a table", "as bullets", "as JSON", "as a numbered list".

- **Don't:** `Compare these three phones.`
- **Do:** `Compare as a table with columns: Price, Battery, Camera, Verdict.`

### 1.13 Ask for a Tone

**Rule:** If tone matters, say so.

Examples:

- `Tone: professional.`
- `Tone: casual.`
- `Tone: friendly, like texting a friend.`
- `Tone: technical, for engineers.`

### 1.14 Ask for a Reading Level

**Rule:** Say who the audience is.

Examples:

- `Explain like I'm 12.`
- `Explain for a non-technical adult.`
- `Explain for a PhD in physics.`

### 1.15 Ask for "Just the Answer"

**Rule:** If you only need the final output, say so.

- **Don't:** `Write a Python function to validate emails.`
- **Do:** `Write a Python function to validate emails. Output only the code, no explanation.`

### 1.16 Ask for the Diff, Not the Whole Thing

**Rule:** When you want changes, ask for only the changed parts.

- **Don't:** `Rewrite this whole email.`
- **Do:** `Show only the lines you'd change, before/after.`

### 1.17 Use "Regenerate" Sparingly

**Rule:** Don't click "regenerate" over and over hoping for a better answer.

Each regenerate is a full new response — costs tokens and time. If the answer is bad, edit your question instead.

### 1.18 Stop When You Have Enough

**Rule:** Click "Stop generating" the moment you have what you need.

The assistant will keep writing otherwise. Stop saves time and tokens.

### Question Template

Use this template for any non-trivial question:

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

*Pick the smallest model that can do your task.*

### 2.1 Use the Small/Fast Model by Default

For everyday tasks, pick the small/fast model: GPT-4o-mini, Claude Haiku, Gemini Flash.

**Use for:**

- Summarizing short text
- Translating common languages
- Writing a short email
- Extracting info from a document
- Classifying something
- Simple Q&A
- Brainstorming

Faster, cheaper, just as good for these tasks.

### 2.2 Use the Big Model for Hard Tasks

For hard tasks, pick the big model: GPT-4o, Claude Sonnet/Opus, Gemini Pro.

**Use for:**

- Complex reasoning
- Math
- Long documents (over 30 pages)
- Detailed writing
- Code architecture
- Legal/medical/financial questions

The big model thinks better. Worth the extra cost and time for hard tasks.

### 2.3 Use the Reasoning Model Only When Needed

Models like GPT-o1, GPT-o3, Claude with "extended thinking" are slow and expensive. Use them only for genuinely hard problems.

**Use for:**

- Multi-step math
- Logic puzzles
- Complex planning
- Hard coding problems

**Don't use for:**

- Writing emails
- Summarizing
- Translating
- Simple questions

### 2.4 Don't Use a Vision Model for Text-Only Tasks

If your question is about text, don't upload an image of the text. Images cost more tokens than text.

- **Don't:** Screenshot a paragraph and ask the assistant to summarize.
- **Do:** Copy the paragraph text and paste it.

### 2.5 Switch Models Mid-Conversation If Needed

If the small model gives a bad answer, switch to the big model and ask the same question. You don't have to start over. The conversation stays.

### 2.6 Re-test Old Tasks Every Few Months

Models improve over time. A task that needed the big model last year might work on the small model now. Try the small model first every quarter.

---

## 3. Handling Context (Context Engineering)

*Give the assistant exactly what it needs — nothing more. Treat the conversation as a budget, not a bucket.*

### 3.1 Attach Files Instead of Pasting Long Text

If you have a long document, upload it as a file. Don't paste 10 pages of text into the chat box. Files are stored once. Pasted text gets re-read on every follow-up, wasting tokens.

### 3.2 Pin Specific Files When Asking About Them

Tell the assistant exactly which file or section you're asking about. If you don't, the assistant searches everything — slow and unfocused.

- **Don't:** `What does my contract say about termination?` (with 10 files attached)
- **Do:** `In "contract_2025.pdf", what does it say about termination?`

### 3.3 Send Only the Section You Need

If you only need one part, copy just that part. Smaller input = faster answer, lower cost.

- **Don't:** Attach a 200-page manual to ask about one feature.
- **Do:** Copy the 2 pages about that feature and paste them.

### 3.4 Don't Repeat Context Already in Chat

If you already gave the assistant your background, don't give it again. The assistant remembers the conversation. Repeating wastes tokens.

### 3.5 Give Background Once, at the Start

On your first message, give any background the assistant needs (who you are, what you're trying to do, what the constraints are). One clear setup at the start saves rambling later.

**Example:**

> `I'm a small business owner. I need a 200-word email to a vendor asking for a discount. Tone: polite but firm. Budget: under $500.`

### 3.6 Don't Add Irrelevant Context

Don't tell the assistant your life story if it's not related to the question. Extra context = extra tokens = slower, more expensive answers.

- **Don't:** `So I've been working at this company for 5 years and my boss is named Sarah and we use Slack and... by the way, can you summarize this article?`
- **Do:** `Summarize this article in 3 bullets.`

### 3.7 Use Web Search for Public Information

If you're asking about something publicly available (a news article, a Wikipedia topic, a product), let the assistant search the web instead of pasting content. Less for you to type, less for the assistant to read.

### 3.8 Start a New Chat When the Topic Changes

Don't ask about your vacation, then your work email, then a coding question — all in one chat. The assistant carries old context into new questions. That makes answers worse (and slower, and more expensive).

**One topic per chat. New topic = new chat.**

### 3.9 Don't Let Chats Run Too Long

If a chat gets past ~10 back-and-forth turns, start a new one. Long chats accumulate context. Every turn gets slower and more confused.

### 3.10 Summarize Before Starting Fresh

If you need to start a new chat but want to keep context, ask the assistant to summarize first:

> `Summarize our conversation so far in 5 bullets. I'll paste this into a new chat.`

Then copy the summary into a new chat.

### 3.11 Edit Your Question Instead of Asking Again

If your question was unclear, edit it (most assistants let you edit a previous message). Don't ask a new question to fix it. Editing restarts from that point. Asking again adds another turn to the chat.

### 3.12 Stop and Redirect When Off-Track

If the answer is going the wrong way, click "Stop" and clarify. Don't let it finish a useless answer.

> `Stop. That's not what I meant. I want X, not Y. Try again.`

### 3.13 Use Descriptive Chat Titles

Rename chats to something you'll recognize. "Q4 marketing plan draft" is better than "Chat from Tuesday".

### 3.14 Don't Ask the Assistant to Remember Across Chats

Each chat is independent (unless you use the memory feature). Don't say "remember this for next time" — it won't. Use the assistant's "memory" or "custom instructions" feature for things you want it to always know.

### When to Start Over

| Trigger | Action |
|---|---|
| Topic changes | New chat |
| Answers getting worse or generic | New chat |
| You switched models | New chat |
| Chat past ~10 turns | Summarize → new chat |
| 3+ back-and-forth trying to get it right | New chat with clearer question |
| Don't be afraid to abandon a chat that isn't working | Chats are free to start |

---

## 4. Skill-Based Category

*Use built-in tools, shortcuts, and saved patterns to do more with fewer tokens.*

### 4.1 Built-in Tools

#### 4.1.1 Use Web Search for Current Information

For anything that changes (news, prices, weather, recent events), use the assistant's web search. The assistant's training data has a cutoff. Without search, it may give old info.

#### 4.1.2 Use Code Execution for Math and Data

For math, calculations, or analyzing a spreadsheet, use the assistant's code tool (ChatGPT's "Code Interpreter" / "Advanced Data Analysis", for example). The assistant is bad at mental math. It's good at writing code that does math correctly.

#### 4.1.3 Upload Files for Document Analysis

For PDFs, Word docs, Excel files, CSVs — upload them. Don't paste their contents. The assistant can read the file directly and you don't have to copy-paste.

#### 4.1.4 Turn Off Tools You Don't Need

Turn off web search, code execution, or other tools when you don't need them. Active tools slow down the response and may add cost.

#### 4.1.5 Don't Generate Images If Text Works

Don't ask for an image if text would do. Image generation is slow and expensive.

- **Don't:** `Generate an image of a pie chart showing 60% / 40% split.`
- **Do:** `Show a 60/40 split as a text table.`

#### 4.1.6 Upload Data Files Instead of Typing Rows

If you have data in a spreadsheet, upload the file. Don't type rows into the chat. Faster, fewer errors, and the assistant can use code to analyze it.

### 4.2 Custom Instructions & Memory

#### 4.2.1 Use the Assistant's Custom-Instructions/Memory Setting

If the assistant has a "custom instructions" or "memory" setting, fill it in once with your usual preferences. You don't have to repeat "I prefer short answers, no markdown, plain text" every time.

**Example (ChatGPT custom instructions):**

> `Always give short answers. No preamble. Plain text, no markdown.`

#### 4.2.2 Save Templates for Repeated Tasks

If you often ask for the same kind of thing (e.g., weekly meeting notes summary), keep a template.

**Example template:**

> `Summarize the meeting notes below. Format: [Decisions] [Action items with owners] [Open questions]. Max 200 words.`

### 4.3 Reusing Answers

#### 4.3.1 Save Useful Answers to Your Notes

When you get a great answer, copy it to your own notes app (Notion, Obsidian, Apple Notes, etc.). Searching your notes is faster than re-asking the assistant.

#### 4.3.2 Bookmark Important Chats

Most assistants let you pin or star chats. Use it for chats you'll return to.

#### 4.3.3 Export Long Chats

If a chat is valuable, export it (most assistants have an export option). You may lose access to old chats. Exporting keeps a copy.

#### 4.3.4 Search History Before Re-Asking

If you asked it last week, the answer is still there. Re-asking wastes tokens.

#### 4.3.5 Reuse Good Prompts

When you write a prompt that works well, save it. Keep a file of "prompts that worked" and copy-paste from it.

### 4.4 GitHub Copilot Chat Shortcuts

*If you use GitHub Copilot Chat (in VS Code, GitHub.com, or GitHub Mobile), use these shortcuts to scope the assistant's context.*

#### 4.4.1 Pin Files with `#file:`

When asking about a specific file, type `#file:` and pick the file.

- **Don't:** `@workspace Why is auth failing?` (searches everything)
- **Do:** `#file:src/middleware/auth.ts Why does this return 401 even with a valid token?`

#### 4.4.2 Use `#selection` for Visible Code

Highlight the code in your editor, then type `#selection` in the chat.

**Example:** Select a function → `#selection What happens if the refresh token expires during retry?`

#### 4.4.3 Use `#problems` + `/fix` for Errors

Don't describe errors in your own words. Let Copilot pull them directly.

**Do:** `/fix #problems`

#### 4.4.4 Use `#changes` to Review Uncommitted Work

Before committing, ask Copilot to review what changed.

**Do:** `#changes Review for bugs and security issues. Format as a table: Severity, File, Issue, Suggestion.`

#### 4.4.5 Use `#terminalLastCommand` for "What Just Broke"

When a command fails in the terminal, don't paste the error. Reference it.

**Do:** `#terminalLastCommand Why did this fail? Show the minimal fix.`

#### 4.4.6 Use `#git` for Commit Messages

Don't write commit messages by hand. Let Copilot draft them from your staged changes.

**Do:** `#git Write a conventional commit message for my staged changes.`

**Or:** Click the ✨ sparkle icon in the Source Control panel.

#### 4.4.7 Don't Use `#codebase` When You Know the File

`#codebase` searches the whole repo. Use it only when you don't know which file to look at.

- **Don't:** `@workspace #codebase Where do we verify webhook signatures?`
- **Do:** `#file:src/webhooks/verify.ts Review the signature verification logic.`

#### 4.4.8 Pick the Narrowest `@` Participant

Use the most specific `@` for your question. Cheapest to priciest:

1. `@terminal`
2. `@vscode`
3. `@extensions`
4. `@github`
5. `@workspace`

#### 4.4.9 Use Slash Commands for Common Tasks

Use these instead of writing the request yourself:

- `/fix` — fix errors
- `/tests` — write tests
- `/doc` — add documentation
- `/explain` — explain code
- `/new` — scaffold a new project
- `/clear` — wipe chat history

#### 4.4.10 Use `/clear` Between Unrelated Tasks

When you switch topics, type `/clear` to wipe the chat history. Long chats carry old context that wastes tokens and confuses Copilot.

#### 4.4.11 Use Inline Chat (`Cmd/Ctrl+I`) for Quick Refactors

For one-shot changes to selected code, use inline chat instead of the chat panel.

**Do:** Select code → `Cmd/Ctrl+I` → `Extract this into a function called validateEmail`

#### 4.4.12 Add `.github/copilot-instructions.md` to Your Repo

Put your project's conventions in a file at `.github/copilot-instructions.md`. Copilot loads it once per session. You stop repeating the same rules in every chat.

**Example:**

```
# Conventions: React + TypeScript. Functional components only.
Named exports. kebab-case files. Tests with Vitest.
```

#### 4.4.13 Always Cap the Output

- **Don't:** `Explain the auth flow` (gets a long rambling answer)
- **Do:** `#file:src/auth.ts Explain the auth flow in 8 numbered steps or fewer.`

#### 4.4.14 Stop the Stream When You Have Enough

Click "Stop" the moment you have the answer you need. Don't let Copilot finish a long response you won't read.

#### 4.4.15 Use `@github` for Issues and PRs

Don't paste issue text into the chat. Let Copilot fetch it.

**Do:** `@github Summarize issue #432 in 3 bullets and tell me which file most likely needs the fix.`

---

## 5. Additional Categories

### 5.1 Cost Awareness

#### 5.1.1 Know Your Plan's Limits

Check whether you're on a flat subscription or metered (pay-per-token). On metered plans, every token costs money. On flat plans, you still have rate limits.

#### 5.1.2 Use the Small Model by Default

Pick the small model (GPT-4o-mini, Claude Haiku, Gemini Flash) for everyday tasks. On metered plans, small models are 5–25× cheaper. On flat plans, they're faster and don't burn your quota as fast.

#### 5.1.3 Don't Re-Ask the Same Question

If you asked it before, search your chat history. Re-asking = paying twice for the same answer.

#### 5.1.4 Stop Long Generations You Don't Need

Click "Stop" when you have what you need. Every extra token the assistant generates costs money (on metered) or quota (on flat).

#### 5.1.5 Use Batch Features for Big Jobs

If you have a big batch job (e.g., "summarize these 100 documents"), check if your assistant has a batch API. Batch APIs often give 50% discount for 24-hour turnaround.

#### 5.1.6 Watch Your Usage Dashboard

Check your usage weekly. Catches runaway spend early. Most assistants have a usage page in settings.

#### 5.1.7 Set Spending Alerts

If your assistant supports spending alerts, set them at 50%, 80%, 100% of your budget.

#### 5.1.8 Don't Share Your Account

Each user should have their own account. Shared accounts burn through limits faster and you can't tell who spent what.

### 5.2 Safety & Privacy

#### 5.2.1 Never Paste Passwords, API Keys, or Secrets

Never paste passwords, API keys, tokens, or private keys into an AI assistant. Your input may be logged, used for training, or seen by humans reviewing the system.

#### 5.2.2 Never Paste Customer PII

Don't paste PII (names, emails, phone numbers, addresses) of customers, patients, or users. Privacy laws (GDPR, HIPAA, etc.) may apply.

#### 5.2.3 Never Paste Confidential Company Information

Don't paste unreleased financials, trade secrets, source code you don't have permission to share, internal documents marked confidential. May violate your employment agreement or NDA.

#### 5.2.4 Check Your Assistant's Data Policy

Know whether your assistant trains on your data. If it does, turn off training in settings, or use a plan that doesn't train on your data (most paid plans don't).

#### 5.2.5 Don't Trust for High-Stakes Decisions

For medical, legal, or financial decisions, treat the assistant as a starting point — not the final answer. Verify with a qualified human.

#### 5.2.6 Don't Click Links Blindly

If the assistant gives you a link, hover over it before clicking. Assistants can hallucinate URLs that look real but aren't.

#### 5.2.7 Be Skeptical of "Facts"

Cross-check important facts with a real source. Assistants make things up (hallucinate) confidently.

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
