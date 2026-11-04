---
name: janitor-claude
description: Audit and clean up the current Claude Code working directory or Obsidian vault. Read-only by default, every mutation requires explicit confirmation.
---

Load and run the `janitor-claude` skill on the current working directory. Walk the full five-phase workflow: diagnose read-only → identify villains (missing/stale/overlapping CLAUDE.md and AGENTS.md, broken @imports, settings and hook drift, broken .mcp.json commands and skill frontmatter, stale worktrees, broken wiki-links, orphaned cruft, oversized files; `~/.claude` weight only if asked) → present findings with specific file paths → fix only after per-item confirmation (move-to-Trash, never `rm -rf`; diff-gated CLAUDE.md edits; per-link wiki-link fixes) → verify with a before/after count table and close with a custom analogy. Never runs destructive git. Never overwrites CLAUDE.md. Never reads session transcripts.
