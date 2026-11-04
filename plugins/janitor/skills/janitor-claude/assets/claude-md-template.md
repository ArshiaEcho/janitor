# {{REPO_NAME}}

{{AGENTS_IMPORT}}
{{ONE_LINE_PURPOSE}}

## Stack

{{STACK_LINES}}

## Commands

- **Dev:** `{{DEV_COMMAND}}`
- **Test:** `{{TEST_COMMAND}}`
- **Lint:** `{{LINT_COMMAND}}`
- **Build:** `{{BUILD_COMMAND}}`

## Conventions

{{CONVENTIONS}}

## Don't read / don't edit

{{DONT_READ_LIST}}

## Files Claude should know about

{{KEY_FILES_LIST}}

## Compact instructions

{{COMPACT_FOCUS}}

<!--
Template notes for janitor-claude. STRIP THIS WHOLE COMMENT BLOCK before showing the draft. (Last verified 2026-11 against code.claude.com/docs/en/memory and /costs.)

- Target under 100 lines. The docs target under 200 per file; this file loads every session. @imports don't reduce the cost.
- {{AGENTS_IMPORT}}: write `@AGENTS.md` only if the repo has an AGENTS.md. Otherwise delete the line. Never copy AGENTS.md text in here.
- Delete any section with nothing specific to say. No "N/A", no placeholders.
- "Compact instructions" is optional: one line on what to keep when the conversation is summarised (e.g. "keep test output and the list of files changed"). Delete the section if the user has no preference.
- Don't-read entries are guidance only. If the user needs a hard block, suggest a permissions.deny rule such as Read(./secrets/**) in .claude/settings.json instead.
- Personal preferences go in CLAUDE.local.md (gitignored), procedures in a skill, area-specific rules in .claude/rules/<topic>.md with a paths: list. Mention, don't create.
- Write `@path` only for a file that should load every session; mention a path without importing it by wrapping it in backticks.
-->
