### 1.
You are an expert in LLM token optimization and AI coding assistants (GitHub Copilot, Cursor, Claude Code, OpenCode, Windsurf, Aider, and similar agentic tools).

Generate a practical, user-facing guide titled:

**Token Optimization Levers for AI Coding Assistants**  
*A practical handbook for everyday developers*

### Structure & requirements

1. **Opening overview (short)**  
   - Explain why token efficiency matters for coding agents (cost, latency, context limits, quality degradation from context rot).  
   - Clarify that the biggest wins come from *context engineering* (what the model sees), not just shorter prompts.

2. **Complete list of optimization levers**  
   First present a clean numbered list of all major levers. Group them logically if helpful (e.g., Prompt-level, Context & Session, Tool & Retrieval, Output & Model, Caching & Platform).  
   Include at least these (and any others that are high-impact for coding agents):
   - Prompt engineering / concise instructions
   - Context engineering / selective context
   - Session management & context compaction
   - Just-in-time / selective retrieval (code search vs full files)
   - Tool output management & truncation
   - Repo memory / instruction files (CLAUDE.md, .cursorrules, AGENTS.md, etc.)
   - Output constraints & structured formats
   - Prompt caching
   - Model selection / cascading
   - Sub-agents / task decomposition
   - History summarization & fresh sessions
   - Exclusion of noise (build artifacts, lockfiles, etc.)

3. **Detailed section for each lever**  
   For every lever produce a consistent structure:

   **Lever name**  
   - One-sentence definition + why it matters for coding agents  
   - How it reduces tokens (input, output, or both)  
   - **Do’s and Don’ts table** (exactly this format):

   | Do | Don’t |
   |----|-------|
   | Concrete, actionable advice a normal developer can follow today | Common mistakes that waste tokens or hurt quality |
   | … | … |

   - 2–4 practical examples tailored to coding assistants (e.g., “Instead of pasting the whole 800-line file, ask the agent to search for the function and read only the relevant range”).
   - Expected impact range when possible (e.g., “often 30–70% fewer input tokens on navigation-heavy tasks”).

4. **Audience & tone**  
   - Written for a normal developer who uses AI coding assistants daily — not for prompt engineers or ML researchers.  
   - Practical, scannable, no jargon without explanation.  
   - Focus on actions the user can take inside the tools themselves (prompts, chat hygiene, settings, project files), not only backend/API changes.  
   - Mention tool-specific tips where relevant (Copilot, Cursor, Claude Code, etc.) but keep the advice general enough to apply across tools.

5. **Closing**  
   - Quick-start checklist (5–7 highest-ROI habits).  
   - Note that techniques compound: small savings per turn multiply across long agent sessions.

Output the full document in clean Markdown with tables. Make it comprehensive yet concise and immediately usable.
