# Personas

Invoke by name in Cursor chat (e.g. “Librarian: ingest this Granola note”).

| Persona | Rule file | Use when |
|---------|-----------|----------|
| **Librarian** | `.cursor/rules/librarian.mdc` | New source, session merge, lint, index/log |
| **Tutor** | `.cursor/rules/tutor.mdc` | Learn concepts, quiz, exam prep |
| **Homework Coach** | `.cursor/rules/homework.mdc` | Assignments, rubrics, drafts |
| **US Signal Advisor** | `.cursor/rules/us-signal.mdc` | Work applications, monthly brief |

All personas share [AGENTS.md](../AGENTS.md) paths and source-priority rules.
