# Personas

Invoke by name in Claude Code or Cursor chat (e.g. “Librarian: ingest this Granola note”).

| Persona | Rule file | Use when |
|---------|-----------|----------|
| **Librarian** | `.cursor/rules/librarian.mdc` | New source, session merge, lint, index/log |
| **Tutor** | `.cursor/rules/tutor.mdc` → `.claude/skills/study/` | Learn concepts, quiz, spaced review, exam prep |
| **Homework Coach** | `.cursor/rules/homework.mdc` | Assignments, rubrics, drafts |
| **US Signal Advisor** | `.cursor/rules/us-signal.mdc` | Work applications, monthly brief |

All personas share [AGENTS.md](../AGENTS.md) paths and source-priority rules and the working contract in [operating.md](../.claude/identity/operating.md).

**Voice:** [voices/house.md](../voices/house.md) for every role. Professor packs (`voices/professors/`) — Tutor and Homework Coach only. AI 5100: [darrah.md](../voices/professors/darrah.md).
