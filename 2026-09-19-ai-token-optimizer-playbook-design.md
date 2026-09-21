# AI Token Optimizer Playbook — Design Spec

Date: 2026-09-19
Status: approved (pending user review of this written spec)
Audience: coding-agent users (Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Copilot, and similar)
Deliverable: one practical markdown playbook at `docs/ai-token-optimizer-playbook.md`

## 1. Goal

Write a single practical playbook that tells a coding-agent user:

1. Where tokens actually go in an agent session.
2. Which tools cut which stream.
3. What to install first.
4. How to combine tools without stacking two proxies.
5. How to measure savings without overstating them.

This is not an encyclopedia, not a cheat sheet, and not a product comparison matrix for LLM app builders.

## 2. Non-goals

- No installers, wrappers, or new software in this repo.
- No vendor marketing copy pasted wholesale.
- No claim that any tool cuts the whole bill by 60–90%. Those percentages apply to one stream (bash output, JSON, prose), not the invoice.
- No how-to for building custom compressors, MCP servers, or agent frameworks.
- No political, historical, or unrelated content.

## 3. Cost model the playbook must teach

An agent bill has four layers. Tools only help the layer they touch.

| Layer | What it is | Typical share of a long coding session | What cuts it |
| --- | --- | --- | --- |
| System / skills / tool schemas | Rules, MCP schemas, always-on prompts | Fixed overhead every turn | Diet `AGENTS.md` / `CLAUDE.md`; fewer MCP tools; pixel/skill compression |
| Input: shell and tool output | `git status/diff`, tests, logs, grep, JSON, docker/kubectl | Often the largest growing input | RTK, Headroom, Caveman proxy, Chisle PostToolUse hook |
| Input: source files | Whole-file reads, re-reads, RAG dumps | Large in big repos | Serena (symbol-level), grep-then-read rules, Token Optimizer MCP graph |
| Output: prose and generated code | Agent chat + the code it writes | Output is billed higher than input | Caveman (prose), Ponytail (YAGNI code), Chisle (both) |

Rules the playbook must state in plain language:

- Cutting bash output 90% does not cut the bill 90%. Bash is one input stream; input is one part of the bill; output is billed separately and usually more expensive per token.
- Cached prompt prefixes bill cheaper than rewritten ones. Compressing history behind a cache breakpoint can raise cost even while bytes fall.
- Skill/ruleset tokens are input on every turn. On a one-line throwaway prompt they can cost more than they save.
- Per-request billing (some Copilot plans) is unchanged by shorter answers.
- Always measure on the provider usage page for the same task with and without the tool.

## 4. Playbook architecture

One markdown file, roughly 400–800 lines, with this section order:

1. **Who this is for / what this is not**
2. **Cost model** (the table above)
3. **Recommended stack** (install these first)
4. **Primary tools** — one subsection each: what, why, install, usage, measure, pitfalls
5. **Also catalogued** — shorter entries for the rest
6. **Stack recipes** — three concrete combos by agent
7. **Do not combine** — proxy collisions and persona collisions
8. **Pitfalls and honest numbers**
9. **Sources**

Tone: second person, imperative, short paragraphs. Commands on their own line with a comment on the line above (never end-of-line comments). No emoji. No local-file markdown hyperlinks; use repo-relative paths as plain code or full URLs for external docs.

## 5. Primary stack (full treatment)

These six get a full subsection in the playbook: what it is, what stream it cuts, install, usage, how to measure, when to skip.

### 5.1 RTK (Rust Token Killer)

- Repo: https://github.com/rtk-ai/rtk
- Site: https://www.rtk-ai.app
- Role: CLI proxy / PreToolUse hook that rewrites bash commands (`git status` → `rtk git status`) and compresses their output.
- Claim to quote carefully: up to 90% of **bash output**, not 90% of the bill. Token counts are `bytes / 4` estimates.
- Install:
  - Homebrew: `brew install rtk`
  - Linux: curl install script to `~/.local/bin`
  - Windows: `winget install rtk-ai.rtk`
  - Cargo: `cargo install --git https://github.com/rtk-ai/rtk` (crates.io has a name collision)
- Wire to agents: `rtk init -g` (Claude Code default), `rtk init -g --codex`, `rtk init -g --opencode`, `rtk init -g --agent cursor`
- Measure: `rtk gain`
- Limit: only Bash-tool calls. Claude Code `Read` / `Grep` / `Glob` bypass the hook. Built-in file tools need `rtk read` / `rtk grep` or shell equivalents.
- Stacks with: Headroom (different stream: files/JSON/RAG vs bash), Ponytail, Caveman skill, Chisle, Serena.
- Do not stack with: Caveman proxy. RTK + Headroom MCP is the intended pairing. Do not also put Headroom in front of the same bash stream RTK already rewrites.

### 5.2 Headroom

- Docs: https://docs.headroomlabs.ai/docs
- Packages: PyPI/npm `headroom-ai` (SDK path is for app builders; playbook uses MCP/proxy only).
- Role: compress tool outputs, logs, JSON, files, RAG, API responses before they reach the LLM. Library, local proxy, or MCP (`headroom_compress`, `headroom_retrieve`, `headroom_stats`).
- Typical coding-agent savings: ~20–57% on measured scenarios (code search 21%, SRE logs 57%, exploration 42%, issue triage 30%). JSON arrays can be much higher. Source-code AST compression is opt-in and off by default.
- Reversible: CCR store; model can `headroom_retrieve` originals.
- Coding-agent path: MCP in Claude Code / Codex, not the Python/TS SDK. Playbook install commands must be copied from current Headroom docs at write time (quickstart + MCP/proxy pages), not invented.
- Limit: do not run two LLM proxies. Headroom MCP is compatible with the Caveman skill and with RTK. Headroom wrap/proxy is not compatible with Caveman wrap or Token Optimizer MCP proxy.
- Does not auto-install. Codex Token Optimizer skill routes to it but does not install it.

### 5.3 Caveman

- Repo: https://github.com/JuliusBrussee/caveman
- Role: two products.
  - **Skill** (MIT, start here): terse agent prose. `npx skills add JuliusBrussee/caveman -g`. JetBrains: ~8.5% fewer output tokens on 86 coding tasks, no quality drop. Adobe CAVEWOMAN: 1.4–2.4× output-side cost cut in chat-style evals. Does not rewrite user prompts, code, errors, or security warnings.
  - **Proxy** (BSL-1.1 engine): shrinks what the agent reads. Optional; overlaps Headroom/RTK.
- Use the skill with RTK + Headroom. Do not enable the Caveman proxy if Headroom or another LLM proxy is already wrapping the agent.
- Skip if billed per request, or if the task is almost all code generation with no prose.

### 5.4 Ponytail

- Repo: https://github.com/DietrichGebert/ponytail
- Role: YAGNI / lazy-senior-dev persona. Cuts **generated code**, not chat prose.
- Measured (Claude Code on FastAPI+React, 12 tasks, Haiku 4.5): ~54% less LOC, ~22% fewer tokens, ~20% cheaper, ~27% faster, 100% safety guards kept.
- Install: Claude `/plugin marketplace add DietrichGebert/ponytail` then `/plugin install ponytail@ponytail`; Codex `codex plugin marketplace add DietrichGebert/ponytail`; OpenCode plugin `@dietrichgebert/ponytail`.
- Combines with Caveman: Caveman shrinks talk, Ponytail shrinks builds. Ponytail authors recommend this.
- Never cuts validation, security, accessibility, or data-loss handling.

### 5.5 Chisle

- Repo: https://github.com/JayPokale/Chisle
- Role: one zero-dep tool on three axes — terse prose, YAGNI code, PostToolUse tool-output compression (Claude Code + Pi).
- Alternative to Caveman skill + Ponytail, not an addition. Do not run Chisle with Caveman skill, and do not run Chisle with Ponytail. Overlapping rulesets fight.
- Input axis still stacks with RTK: RTK rewrites at the source; Chisle catches subagents, MCP, and web that RTK never sees. Chisle never touches `Read`/`Edit`/`Write` bytes.
- Install: `npx chisle` (auto-detects agents). Claude + Pi get live `/chisle` and compression; Cursor/Codex/Gemini/OpenCode get always-on rules.
- Honest numbers policy: playbook must mention Chisle publishes losing runs. Use that as the model for how we quote all tools.

### 5.6 Serena

- Repo: https://github.com/oraios/serena
- Docs: https://oraios.github.io/serena
- Role: MCP semantic retrieval and symbol-level edit. Agent reads a symbol instead of a whole file. Orthogonal to compressors.
- Install: `uv tool install -p 3.13 serena-agent` then `serena init`. Do not install via MCP marketplaces (upstream warning: outdated commands).
- Add when the repo is large enough that whole-file reads dominate. Skip for small single-package projects.

## 6. Also catalogued (short entries)

Each gets 4–8 lines: one-sentence job, install hint, when it belongs, when to skip.

| Tool | Job | Playbook stance |
| --- | --- | --- |
| Codex Token Optimizer (`HelloWorld668/codex-token-optimizer`) | Codex skill that routes noisy shell → RTK and large context → Headroom MCP; reports `rtk gain` / `headroom_stats`. Does not install anything. | Mention under Codex recipe, not as a primary tool. |
| Token Optimizer MCP (`ooples/token-optimizer-mcp`) | Measure savings, deny huge Reads, per-project knowledge graph, optional cache-aware proxy. 16 CLI clients. | Optional advanced layer. Do not run its proxy next to Headroom or Caveman wrap. |
| TOON | Token-oriented object notation; encode JSON more cheaply. Caveman ships `caveman toon encode/decode`. | Mention as a format, not a stack item. |
| LLMLingua | Prompt compression library for app builders. | Out of audience. One-line "not for coding agents." |
| OpenAI native compaction | Provider-side context compaction in Codex/ChatGPT. | Use when available; do not double-compact the same history with a proxy. |
| openrtk | Community/fork relative of RTK. | Prefer upstream `rtk-ai/rtk`. |
| laconic / scrooge-mode / lean-mode | Extra terse-prose skills. | Redundant with Caveman or Chisle. Pick one persona. |
| Compresr / Token Co. / Semble / Graphify | Adjacent compression or graph products. | Name only if still public at write time; no install steps unless verified. |

If a listed product has vanished or the URL 404s at write time, drop it rather than leaving a dead link.

## 7. Recommended combos

Default recommendation (most coding-agent users):

**RTK + Headroom MCP + Ponytail + Caveman skill**

- RTK: bash
- Headroom: logs/JSON/files/RAG
- Ponytail: less code written
- Caveman skill: less chat

Substitutions:

- Want one persona/ruleset instead of two: **Chisle** instead of Caveman skill + Ponytail. Keep RTK. Keep Headroom if you still have huge JSON/logs that Chisle's hook will not see (non-Claude/Pi agents, or payloads Chisle allowlist skips).
- Large monorepo: add **Serena**.
- Codex user who already has RTK + Headroom: add the **Codex Token Optimizer** skill so the agent routes correctly. Still install RTK and Headroom yourself.
- Already running Caveman wrap (`caveman claude`): skip Headroom proxy. Skill-only Caveman is still fine with Headroom MCP.

Three named recipes the playbook will spell out with exact commands:

1. **Claude Code default:** `brew install rtk && rtk init -g`, Headroom MCP, Ponytail plugin, `npx skills add JuliusBrussee/caveman -g`
2. **Codex default:** `rtk init -g --codex`, Headroom MCP tools visible, Ponytail Codex plugin, Caveman skill for Codex, optional Codex Token Optimizer skill
3. **One-tool persona + RTK:** `npx chisle` + `rtk init -g` (and agent-specific RTK flag)

OpenCode: `rtk init -g --opencode`, Ponytail via `opencode.json` plugin, Caveman skill or Chisle.

## 8. Hard constraints the playbook must enforce

1. **One LLM proxy.** Never Headroom wrap + Caveman wrap + Token Optimizer MCP proxy on the same agent.
2. **One YAGNI persona.** Ponytail or Chisle, not both.
3. **One terse-prose persona.** Caveman skill or Chisle, not both (Chisle already includes prose rules).
4. **RTK + Chisle is allowed.** Different intercept points.
5. **Do not compress secrets** into model-visible summaries (keys, tokens, credentials, payment data, personal contact data).
6. **Retrieve originals** when correctness depends on exact lines, versions, stack frames, or config values.
7. **Do not claim session-wide savings** from a single-stream benchmark.

## 9. Implementation plan for the playbook file

The implementation (next phase, after this spec is accepted) is:

1. Create `docs/ai-token-optimizer-playbook.md` with the section order in §4.
2. Each primary tool subsection uses this template:

   ```
   ## Tool name
   What it cuts
   Install
   Wire to your agent
   Daily usage
   Measure
   Skip when
   ```

3. All install commands verified against the upstream README at write time. If a command disagrees with upstream, upstream wins.
4. No screenshots. No mermaid unless a label is a single quoted line.
5. Sources section lists upstream URLs only.

## 10. Success criteria

- A reader can pick a stack and install it in one sitting without opening a second essay.
- Percentages always name the stream (bash output / output tokens / LOC / JSON).
- Default stack is unambiguous.
- Conflicts (two proxies, two personas) are stated once in a dedicated section and repeated as one-liners under the affected tools.

## 11. Out of scope for v1 of the playbook

- Per-agent screenshot walkthroughs
- Windows-only deep dive beyond RTK winget and Caveman install.ps1 pointers
- Building or vendoring any of these tools
- Translating the playbook
