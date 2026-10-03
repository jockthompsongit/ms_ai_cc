# How to fill out CLAUDE.md

CLAUDE.md is loaded into context at the start of every session in this project. It is
a standing instruction set, not documentation. Treat every line as something you are
paying for on each turn.

## Principles

1. **Imperative, not descriptive.** "Use `uv` for all Python deps" beats "this project
   uses uv." Write the rule you want followed.
2. **Specific and checkable.** A rule Claude can verify it obeyed ("all new modules get
   a test file next to them") is worth ten vague ones ("write good code").
3. **Only non-obvious things.** If it is discoverable by reading the code, a config
   file, or `--help`, leave it out. Exception: commands - naming the exact test/lint
   invocation saves a wrong guess every session.
4. **No file or directory listings.** They go stale immediately and Claude can just
   look. Describe conventions instead: "HTTP handlers in `api/`, one file per resource."
5. **Not a changelog, diary, or postmortem.** No "fixed X on date Y", no reflections,
   no session notes. History belongs in git; decisions belong in ADRs or `docs/`.
6. **Short.** Aim under ~100 lines. When a section outgrows that, move the detail into
   a file and reference it, or use a nested CLAUDE.md (below).
7. **Say why for surprising rules.** A one-clause reason ("never call the billing API
   from tests - it charges real cards") stops it being "improved" away later.

## Section by section

- **Project** - one or two sentences of orientation. Enough to disambiguate intent, not
  a README.
- **Stack** - pinned versions where they matter, package manager, datastores. This is
  where you prevent Claude reaching for `npm` in a `pnpm` repo.
- **Commands** - the exact invocations, including any prefix (`make`, `uv run`,
  `docker compose exec app`). Delete rows that do not exist rather than leaving TODO.
- **Conventions** - naming, module boundaries, error handling, logging, how config and
  secrets are read, where a new thing of a given kind goes.
- **Rules** - hard constraints as always/never bullets. Good candidates: files or paths
  never to touch, commands never to run, things requiring your approval first
  (migrations, pushes, deploys), dependencies not to add, data never to log.
- **Workflow** - branching, whether to commit unprompted, commit message format, what
  must pass before work is called done.
- **Domain notes** - vocabulary and non-obvious concepts. Delete if empty.

Add or drop sections freely - the skeleton is a starting point, not a schema.

## Good vs. bad lines

| Bad | Good |
| --- | --- |
| "Write tests." | "Every bugfix starts with a failing test that reproduces it." |
| "The project has a src/ folder with utils.py, api.py..." | "Shared helpers go in `src/utils/`, one module per concern." |
| "Be careful with the database." | "Never run migrations; write the migration file and stop." |
| "Refactored the parser this week." | (delete - that is git's job) |

## Mechanics

- `@path/to/file.md` in CLAUDE.md inlines that file's contents. Use it to keep long
  style guides out of the main file while still loading them.
- A `CLAUDE.md` in a subdirectory is loaded only when Claude reads files there. Put
  subsystem-specific rules in one instead of bloating the root file.
- `.claude/settings.json` is committed and shared: permissions, env, hooks.
  `.claude/settings.local.json` is machine-local and gitignored.
- `.claude/commands/*.md` become slash commands. `.claude/agents/*.md` and
  `.claude/skills/*/SKILL.md` define project-scoped subagents and skills.
- To revise this file later, ask Claude to update it with what it learned, or use the
  `claude-md-improver` / `revise-claude-md` skills. Review the diff - these files drift
  toward bloat.
