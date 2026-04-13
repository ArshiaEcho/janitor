# Changelog

All notable changes to the `janitor` plugin are documented in this file.

## [0.1.0] — Initial release

Two-skill plugin for Claude Code.

### Added
- `janitor-device` — diagnose and fix slow Mac or Windows machines. Cross-platform five-phase workflow (diagnose, identify villains, present, fix, verify) with permission gates, reversible operations, and a custom closing analogy.
- `janitor-claude` — audit and clean the current Claude Code working directory and session. Finds orphaned scratchpads, broken Obsidian wiki-links, missing or stale CLAUDE.md, oversized files, and token-waste patterns. Read-only diagnostics; every mutation requires explicit user confirmation.
- Slash-command stubs for both skills (`/janitor-device`, `/janitor-claude`) in addition to natural-language triggering.
- Reference files split out of SKILL.md for token-efficient loading (villain catalogs, fix blocks, metric mapping, markdown audit patterns, CLAUDE.md scaffolding protocol).
- README with a "What it does NOT do" trust list enumerating every category of forbidden behavior.

### Philosophy
- No telemetry, no network calls, no auto-updates.
- Every elevated command is a copy-paste block the user runs themselves.
- Every deletion goes to Trash or Recycle Bin.
- Every CLAUDE.md change is shown as a diff first.
- Never mutates git state.
- Never disables Windows Defender or edits boot config.

### Known limitations
- Linux is not yet supported by `janitor-device` (deferred to v0.2).
- `janitor-device` targets PowerShell 7+ on Windows; Windows PowerShell 5.1 works but with reduced diagnostic coverage.
- Secret detection in `janitor-claude` uses a small high-precision pattern set and is not a substitute for dedicated tools like `gitleaks`.
