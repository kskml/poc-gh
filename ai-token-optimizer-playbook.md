# AI Token Optimizer Playbook

Practical stack for coding-agent users. Tools cut one stream. Measure the stream, not the invoice.

## Who this is for

You run a coding agent: Claude Code, Codex, Cursor, OpenCode, Gemini CLI, Copilot, or something similar. You pay for tokens, or you hit context limits, and you want a stack you can install in one sitting.

This is not for people building LLM apps. Skip LLMLingua, skip SDKs, skip custom compressors.

This is not an encyclopedia and not a cheat sheet. Install the default stack, then add Serena only if whole-file reads dominate.

## Cost model

An agent bill has four layers. Tools only help the layer they touch.

| Layer | What it is | Typical share of a long coding session | What cuts it |
| --- | --- | --- | --- |
| System / skills / tool schemas | Rules, MCP schemas, always-on prompts | Fixed overhead every turn | Diet `AGENTS.md` / `CLAUDE.md`; fewer MCP tools; pixel/skill compression |
| Input: shell and tool output | `git status/diff`, tests, logs, grep, JSON, docker/kubectl | Often the largest growing input | RTK, Headroom, Caveman proxy, Chisle PostToolUse hook |
| Input: source files | Whole-file reads, re-reads, RAG dumps | Large in big repos | Serena (symbol-level), grep-then-read rules, Token Optimizer MCP graph |
| Output: prose and generated code | Agent chat + the code it writes | Output is billed higher than input | Caveman (prose), Ponytail (YAGNI code), Chisle (both) |

Rules:

- Cutting bash output 90% does not cut the bill 90%. Bash is one input stream. Input is one part of the bill. Output is billed separately and usually costs more per token.
- Cached prompt prefixes bill cheaper than rewritten ones. Compressing history behind a cache breakpoint can raise cost even while bytes fall.
- Skill and ruleset tokens are input on every turn. On a one-line throwaway prompt they can cost more than they save.
- Per-request billing (some Copilot plans) is unchanged by shorter answers.
- Always measure on the provider usage page for the same task with and without the tool.

## Token types

Providers do not bill "tokens". They bill three meters, sometimes four.

**Input.** Prompts, tool results, files the model reads. This is the bulk of a long agent session.

**Cached input.** Unchanged prefix from the previous turn. Cheaper than rewritten input. If you rewrite that prefix (including by compressing history sitting behind the cache breakpoint), you lose the cheap reread and may pay a cache-write premium.

**Output.** Chat plus generated code. Billed higher per token than input.

**Reasoning / effort** (when the provider has it). Multiplies billed **output** only, not input. Turning effort from low to high does not make RTK or Headroom more valuable; it makes Ponytail and Caveman more valuable, because they shrink the expensive meter.

## Worked session bill

Invented session, not a measurement: fix a failing pytest in a mid-size Python repo, 8 turns. Round numbers so you can see dilution.

| Layer | Tokens this session | After default stack | What cut it |
| --- | ---: | ---: | --- |
| System / skills / schemas | 12,000 | 12,000 | nothing in the default stack; diet `AGENTS.md` separately |
| Input: shell / tests / git | 40,000 | 8,000 | RTK, ~80% of **bash output** |
| Input: logs / JSON / extra files | 20,000 | 12,000 | Headroom MCP, ~40% of **that JSON/log stream** |
| Input: source files | 18,000 | 18,000 | Serena would cut this in a monorepo; skip here |
| Output: chat prose | 4,000 | 3,600 | Caveman skill, ~10% of **output tokens** (JetBrains-shaped) |
| Output: generated code | 6,000 | 4,700 | Ponytail, ~22% of **tokens on that measured coding set** |

Session total: 100,000 tokens to about 58,300. RTK's 80% bash cut is 32,000 tokens, which is 32% of this session, not 80% of the bill. Headroom's 40% JSON/log cut is 8,000 tokens. Caveman and Ponytail look small in token count and still matter because output is billed higher per token.

Do not attach dollar rates. Do not map this to Copilot allowances. Run the same task twice on your provider usage page.

## Recommended stack

Install this first:

**RTK + Headroom MCP + Ponytail + Caveman skill**

- RTK: bash
- Headroom MCP: logs, JSON, files, RAG
- Ponytail: less code written
- Caveman skill: less chat

Substitutions:

- Want one persona/ruleset instead of two: **Chisle** instead of Caveman skill + Ponytail. Keep RTK. Keep Headroom MCP if you still have huge JSON/logs that Chisle's hook will not see (non-Claude/Pi agents, or payloads Chisle's allowlist skips).
- Large monorepo where whole-file reads dominate: add **Serena**.
- Codex user who already has RTK + Headroom: add the **Codex Token Optimizer** skill so the agent routes correctly. Still install RTK and Headroom yourself.
- Already running Caveman wrap (`caveman claude`): skip Headroom wrap. Skill-only Caveman is still fine with Headroom MCP.

Do not run two LLM proxies. Do not run two YAGNI personas. Do not run two terse-prose personas.

## Primary tools

### RTK (Rust Token Killer)

What it cuts: **bash output**. Up to 90% of that stream, not 90% of the bill. Token counts are `bytes / 4` estimates. Percentages are more trustworthy than absolute token numbers.

Repo: https://github.com/rtk-ai/rtk

Site: https://www.rtk-ai.app

Install:

```bash
# Homebrew (recommended)
brew install rtk
```

```bash
# Windows
winget install rtk-ai.rtk
```

```bash
# Linux / macOS curl installer (writes to ~/.local/bin)
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
```

```bash
# Cargo. crates.io has a name collision; use git.
cargo install --git https://github.com/rtk-ai/rtk
```

Wire to your agent:

```bash
# Claude Code / Copilot default
rtk init -g
```

```bash
# Codex
rtk init -g --codex
```

```bash
# OpenCode
rtk init -g --opencode
```

```bash
# Cursor
rtk init -g --agent cursor
```

```bash
# Gemini CLI
rtk init -g --gemini
```

Restart the agent. `git status` becomes `rtk git status` on Bash-tool calls.

Daily usage: do nothing. The hook rewrites shell commands. For file workflows that bypass the hook, call RTK yourself:

```bash
rtk read file.rs
rtk grep "pattern" .
rtk git diff
rtk test pytest -q
```

Measure:

```bash
rtk gain
```

Skip when: the session is almost all `Read`/`Grep`/`Glob` with no shell. Those Claude built-ins bypass the hook. Use shell equivalents or `rtk read` / `rtk grep`.

Do not stack with Caveman proxy. Do not put Headroom in front of the same bash stream RTK already rewrites. RTK + Headroom MCP is the intended pairing (different streams). RTK + Chisle is allowed (different intercept points).

### Headroom

What it cuts: tool outputs, logs, JSON, files, RAG, API responses before they reach the LLM. Typical coding-agent savings on measured scenarios: code search 21%, SRE logs 57%, exploration 42%, issue triage 30% of **that stream**. JSON arrays can be much higher. Source-code AST compression is opt-in and off by default.

Docs: https://docs.headroomlabs.ai/docs

MCP: https://docs.headroomlabs.ai/docs/mcp

Coding-agent path is MCP, not the Python/TS SDK.

Install:

```bash
# CLI with MCP extras, isolated tool env
uv tool install --python 3.13 "headroom-ai[mcp]"
```

Wire to Claude Code:

```bash
headroom mcp install
```

Then start `claude`. Tools: `headroom_compress`, `headroom_retrieve`, `headroom_stats`.

Wire to Codex or any stdio MCP host:

```toml
[mcp_servers.headroom]
command = "headroom"
args = ["mcp", "serve"]
```

If the host cannot see `headroom` on PATH, put the absolute path from `command -v headroom` in `command`.

Daily usage: let the model call `headroom_compress` on large logs, JSON, search dumps. Call `headroom_retrieve` with the hash when you need the original.

Do **not** start `headroom proxy` and point `ANTHROPIC_BASE_URL` at it unless you have chosen Headroom as your one LLM wrap. That is a proxy. Default stack is MCP only.

Measure: `headroom_stats`. Also compare the provider usage page.

Skip when: you already wrap the agent with Caveman (`caveman claude`) or Token Optimizer MCP proxy. Headroom **MCP** is compatible with the Caveman **skill** and with RTK. Headroom **wrap** is not compatible with Caveman wrap or Token Optimizer MCP proxy.

SDK `compress()` is for app builders. Ignore it.

### Caveman

What it cuts: **agent prose** (skill). Optional proxy shrinks what the agent reads and overlaps Headroom/RTK; skip the proxy in the default stack.

Repo: https://github.com/JuliusBrussee/caveman

Install the skill:

```bash
npx skills add JuliusBrussee/caveman -g
```

Type `/caveman` if the agent does not wake on its own.

JetBrains measured ~8.5% fewer **output tokens** on 86 coding tasks, no quality drop. Adobe CAVEWOMAN measured 1.4–2.4x output-side cost cut in chat-style evals. Agentic coding sessions, where most tokens are code and tool calls the skill never touches, see high-single-digit output cuts. Chat-style Q&A sees a much larger cut.

Does not rewrite user prompts, code, errors, or security warnings.

Before (invented):

> The test is failing because `parse_date` returns naive datetime objects while the assertion compares them to timezone-aware values. I'd recommend converting both sides to UTC before comparing.

After:

> Naive vs aware datetime. Convert both to UTC before assert.

Same diagnosis. Same fix. Less throat-clearing.

Daily usage: `/caveman lite` for tight-but-polite, `/caveman` default, `/caveman ultra` for grunts. `stop caveman` to leave.

Measure: same task with and without the skill on the provider usage page. There is no honest session counter for "tokens not written".

Skip when: billed per request, or the task is almost all code generation with no prose. Skip the **proxy** if Headroom or another LLM proxy already wraps the agent. Do not run with Chisle (overlapping prose rulesets).

Use with RTK + Headroom MCP + Ponytail.

### Ponytail

What it cuts: **generated code**, not chat prose. YAGNI / lazy-senior-dev persona.

Repo: https://github.com/DietrichGebert/ponytail

Measured on Claude Code editing a real FastAPI+React repo, 12 feature tasks, Haiku 4.5, versus the same agent with no skill: ~54% less LOC, ~22% fewer tokens, ~20% cheaper, ~27% faster, 100% safety guards kept. Biggest cuts where the agent would over-build (native `<input type="date">` instead of a date-picker library). Near zero on code that is already minimal.

Never cuts validation, security, accessibility, or data-loss handling.

Install, Claude Code (two separate prompts):

```
/plugin marketplace add DietrichGebert/ponytail
```

```
/plugin install ponytail@ponytail
```

Codex:

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

OpenCode, in `opencode.json`:

```json
{ "plugin": ["@dietrichgebert/ponytail"] }
```

Cursor:

```bash
git clone https://github.com/DietrichGebert/ponytail
node ponytail/scripts/cursor-hooks.js install
```

Gemini CLI:

```bash
gemini extensions install https://github.com/DietrichGebert/ponytail
```

Copilot CLI:

```bash
copilot plugin marketplace add DietrichGebert/ponytail
copilot plugin install ponytail@ponytail
```

Daily usage: on every session after install. `/ponytail lite|full|ultra|off` to change intensity.

Measure: `git diff` size and the provider usage page against a no-skill run. `/ponytail-gain` shows the published benchmark, not your bill.

Skip when: you installed Chisle. Ponytail or Chisle, not both. Combines with Caveman: Caveman shrinks talk, Ponytail shrinks builds.

### Chisle

What it cuts: three axes in one zero-dep tool — terse prose, YAGNI code, PostToolUse tool-output compression (Claude Code + Pi). Alternative to Caveman skill + Ponytail, not an addition.

Repo: https://github.com/JayPokale/Chisle

Install:

```bash
npx chisle
```

Auto-detects agents. Preview with `npx chisle --dry-run`. Remove with `npx chisle --uninstall`.

Claude Code + Pi get live `/chisle` and input-side compression. Cursor, Codex, Gemini, OpenCode, Copilot get always-on rules. OpenCode also gets a compression plugin.

Chisle never touches `Read`/`Edit`/`Write` bytes. RTK + Chisle is allowed: RTK rewrites at the source; Chisle catches subagents, MCP, and web that RTK never sees.

Chisle publishes losing runs. Quote it that way. On one Pi suite it lost billed output to Ponytail. Use that as the model for how you quote every tool here.

Measure:

```bash
npx chisle --stats
```

That number is the **input axis only** (chars the hook elided). Output-axis savings have no session counter; they come from A/B benchmarks.

Skip when: Caveman skill is on, or Ponytail is on. Overlapping rulesets fight. Skip personas if billed per request.

### Serena

What it cuts: **whole-file reads**. MCP semantic retrieval and symbol-level edit. Agent reads a symbol instead of a file. Orthogonal to compressors.

Repo: https://github.com/oraios/serena

Docs: https://oraios.github.io/serena

Install:

```bash
uv tool install -p 3.13 serena-agent
```

```bash
serena init
```

Then configure the MCP launch command in your client. Client matrix: https://oraios.github.io/serena/02-usage/030_clients.html

Do not install via MCP marketplaces. Upstream warning: those commands are outdated.

Daily usage: let the agent find/replace symbols through Serena instead of dumping files into context.

Measure: provider usage page on the same large-repo task with and without Serena. There is no `serena gain`.

Skip when: small single-package projects where whole-file reads are cheap. Add when the repo is large enough that file reads dominate.

## Also catalogued

**Codex Token Optimizer** (`HelloWorld668/codex-token-optimizer`). Codex skill that routes noisy shell to RTK and large context to Headroom MCP, then reports `rtk gain` / `headroom_stats`. Does not install anything. Mention under the Codex recipe, not as a primary tool. Install RTK and Headroom yourself.

**Token Optimizer MCP** (`ooples/token-optimizer-mcp`). Measure savings, deny huge Reads, per-project knowledge graph, optional cache-aware proxy. Sixteen CLI clients. Optional advanced layer. Do not run its proxy next to Headroom wrap or Caveman wrap. Claude Code install is the plugin, not the bare MCP server: `/plugin marketplace add ooples/token-optimizer-mcp` then `/plugin install token-optimizer@token-optimizer`.

**TOON.** Token-oriented object notation. Encode JSON more cheaply. Caveman ships `caveman toon encode/decode`. A format, not a stack item.

**LLMLingua.** Prompt compression library for app builders. Not for coding agents.

**OpenAI native compaction.** Provider-side context compaction in Codex/ChatGPT. Use when available. Do not double-compact the same history with a proxy.

**openrtk.** Community/fork relative of RTK. Prefer upstream `rtk-ai/rtk`.

**laconic / scrooge-mode / lean-mode.** Extra terse-prose skills. Redundant with Caveman or Chisle. Pick one persona.

**Compresr / Token Co. / Semble / Graphify.** Adjacent compression or graph products. Name them if you already use them. Do not add them to the default stack.

## Stack recipes

### 1. Claude Code default

```bash
brew install rtk
rtk init -g
```

```bash
uv tool install --python 3.13 "headroom-ai[mcp]"
headroom mcp install
```

In Claude Code, two separate prompts:

```
/plugin marketplace add DietrichGebert/ponytail
```

```
/plugin install ponytail@ponytail
```

```bash
npx skills add JuliusBrussee/caveman -g
```

Restart Claude Code. Confirm `rtk gain` works and `/mcp` lists Headroom.

### 2. Codex default

```bash
brew install rtk
rtk init -g --codex
```

```bash
uv tool install --python 3.13 "headroom-ai[mcp]"
```

Point Codex MCP at `headroom mcp serve` (absolute `command` if PATH is empty). Restart Codex or open a new thread until `headroom_compress`, `headroom_retrieve`, and `headroom_stats` are visible.

```bash
codex plugin marketplace add DietrichGebert/ponytail
codex plugin add ponytail@ponytail
```

```bash
npx skills add JuliusBrussee/caveman -g
```

Optional: install the Codex Token Optimizer skill from https://github.com/HelloWorld668/codex-token-optimizer so the agent routes noisy shell to RTK and large dumps to Headroom. It still does not install those tools.

### 3. One-tool persona + RTK

```bash
npx chisle
```

```bash
rtk init -g
```

Use `rtk init -g --codex`, `--opencode`, `--gemini`, or `--agent cursor` to match the agent. Keep Headroom MCP if you still have huge JSON/logs that Chisle's hook will not see.

OpenCode without Chisle:

```bash
rtk init -g --opencode
```

Put `{ "plugin": ["@dietrichgebert/ponytail"] }` in `opencode.json`, then add the Caveman skill.

### Stack picker

| Agent | Default recipe | One-persona alternative | Skip if |
| --- | --- | --- | --- |
| Claude Code | RTK + Headroom MCP + Ponytail + Caveman skill | `npx chisle` + RTK (keep Headroom MCP if JSON/logs are still huge) | already wrapping with Caveman/Headroom proxy; billed per request (skip personas) |
| Codex | RTK `--codex` + Headroom MCP + Ponytail + Caveman skill | Chisle + RTK `--codex` | already wrapping; tiny repo (skip Serena) |
| Cursor | RTK `--agent cursor` + Headroom MCP + Ponytail hooks + Caveman skill | Chisle + RTK | already wrapping |
| OpenCode | RTK `--opencode` + Ponytail plugin + Caveman skill | Chisle + RTK `--opencode` | already wrapping |
| Gemini CLI | RTK `--gemini` + Ponytail extension + Caveman skill | Chisle + RTK `--gemini` | already wrapping |
| Copilot | RTK `-g` or `--copilot` + Ponytail CLI plugin + Caveman skill | Chisle + RTK | billed per request (skip Caveman/Chisle/Ponytail for cost; they still change style) |

Add Serena on any row when whole-file reads dominate.

## Do not combine

1. **One LLM proxy.** Never Headroom wrap + Caveman wrap + Token Optimizer MCP proxy on the same agent. Headroom MCP + Caveman **skill** + RTK is the default and is not three proxies.
2. **One YAGNI persona.** Ponytail or Chisle, not both.
3. **One terse-prose persona.** Caveman skill or Chisle, not both. Chisle already includes prose rules.
4. **RTK + Chisle is allowed.** Different intercept points.
5. **Do not compress secrets** into model-visible summaries (keys, tokens, credentials, payment data, personal contact data).
6. **Retrieve originals** when correctness depends on exact lines, versions, stack frames, or config values.
7. **Do not claim session-wide savings** from a single-stream benchmark.

## Pitfalls and honest numbers

RTK's "90%" is 90% of **bash output**. In the worked bill that was 32% of session tokens, before output was billed at a higher rate.

Headroom's 21–57% figures are **those measured streams** (code search, SRE logs, exploration, triage), not your invoice.

Caveman skill's JetBrains number is ~8.5% of **output tokens** on coding tasks. Adobe's 1.4–2.4x is output-side cost in chat-style evals. Do not mix them.

Ponytail's ~54% is **LOC**, ~22% is **tokens**, on 12 Claude Code tasks against a no-skill baseline. Ceiling is higher on over-build traps; floor is near zero on already-minimal code.

Chisle publishes losing runs. If a tool only shows green rows, distrust it.

Cache trap: compressing conversation history behind a cache breakpoint can raise cost. Headroom MCP compresses content you hand it; a wrap that rewrites the cached prefix is a different product. Default stack uses MCP, not wrap.

Skill overhead: Caveman, Ponytail, and Chisle ride along as input every turn. On a one-line throwaway they can cost more than they save. Turn them off (`stop caveman`, `/ponytail off`, `stop chisle`) for that prompt.

Per-request Copilot billing: shorter answers are the same request. Personas still change style; they do not change that bill.

RTK does not see Claude `Read` / `Grep` / `Glob`. If those dominate, RTK's dashboard will look quiet while your bill does not.

Headroom MCP tool results occupy Claude context. `/usage` can show a large share under `headroom` even while Headroom is shrinking other payloads. `/compact` after big compress jobs. Compare `headroom_stats` tokens_saved to MCP call count.

Do not compress secrets. Retrieve originals for stack frames, versions, and config values.

Measure on the provider usage page. `rtk gain` and `npx chisle --stats` are stream counters. They are not the invoice.

## Sources

- https://github.com/rtk-ai/rtk
- https://www.rtk-ai.app
- https://docs.headroomlabs.ai/docs
- https://docs.headroomlabs.ai/docs/mcp
- https://github.com/JuliusBrussee/caveman
- https://github.com/DietrichGebert/ponytail
- https://github.com/JayPokale/Chisle
- https://github.com/oraios/serena
- https://oraios.github.io/serena
- https://github.com/HelloWorld668/codex-token-optimizer
- https://github.com/ooples/token-optimizer-mcp
