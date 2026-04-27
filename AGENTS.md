## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure.
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files.
- Use graphify first to identify relevant files before opening source files.
- Do not scan the whole repo unless graphify output is insufficient.
- After modifying code files in this session, run `graphify update .` to keep the graph current.

## gstack + graphify workflow

When using gstack commands like /investigate, /autoplan, /review, /qa, or /ship:

1. First read `graphify-out/GRAPH_REPORT.md`.
2. Identify the relevant community, god nodes, files, and functions.
3. Open only the minimum source files required.
4. Avoid unrelated refactoring.
5. Prefer investigation before implementation.
6. For implementation, make small scoped changes.
7. After code changes, summarize:
   - files changed
   - functions/classes changed
   - tests to run
   - graphify update command

Default workflow:
- `/investigate` = use graphify first, no edits.
- `/autoplan` = create file-level plan from graphify findings.
- `/review` = review only changed files and graph-related impacted files.
- `/qa` = create focused test checklist.
- `/ship` = final readiness summary.

Project-specific rule:
For StockAiAgent, do not mix Forex/Oanda flow with Indian market/Upstox flow unless explicitly requested.