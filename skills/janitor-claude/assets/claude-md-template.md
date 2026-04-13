# {{REPO_NAME}}

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

<!--
Template notes for whoever is reading this (janitor-claude fills these in from the 5-question protocol + auto-detection):

- Keep this file under 100 lines. It loads on every session. Every line is a token cost on every prompt.
- If a section has nothing useful to say, delete the section entirely — don't leave "N/A" or placeholder text.
- Update this file when conventions change. Janitor-claude can help you audit it later with "audit my CLAUDE.md".
-->
