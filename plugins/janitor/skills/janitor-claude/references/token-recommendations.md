# Token-waste recommendations — observation → rule

**Last verified:** 2026-11 (code.claude.com/docs/en/costs, /memory, /skills, /mcp; changelog through v2.1.318). Re-check the numbers below when you revise this file.

Load this file when janitor-claude is generating the recommendations section of its report. **Every recommendation in this file must cite a specific file, path, or pattern in the user's actual directory.** Generic essays about "tokens are expensive" are forbidden.

The test for whether a recommendation belongs here: if you could have said the same thing before running any diagnostics, it doesn't belong. Only ship advice that's grounded in what you just observed.

---

## The rule table

Each row is an observation → recommendation. Each recommendation includes the exact form of advice to give the user. Never hand-wave.

| # | Observation | Recommendation | Form of advice |
|---|---|---|---|
| 1 | No `CLAUDE.md`, `.claude/CLAUDE.md`, or `AGENTS.md` in a non-trivial repo | Offer to scaffold one via the 5-question protocol | "There's no project instruction file here, so Claude re-learns the stack every session. I can ask you 5 questions and show you a draft. (Claude Code's own `/init` can also generate one.)" |
| 2 | An instruction file is over 200 lines (count `@imports` too: they load with the file that imports them) | Flag as oversized, suggest where each part should live | "`<file>` is N lines (M with imports). The docs target under 200 lines; it loads on every session. The `<section>` procedure fits a skill (loads only when used), and the `<area>` rules fit `.claude/rules/<topic>.md` with a `paths:` list (loads only when Claude touches matching files)." |
| 3 | `CLAUDE.md` references a command that doesn't exist (e.g. "run `npm test`" but no test script in `package.json`) | Stale fact — show diff | "`CLAUDE.md` line N says `<command>`. That script isn't in `package.json`. Want me to show you a diff updating it?" |
| 4 | Oversized file (`.json`, `.log`, `.txt` > 500 KB) in the repo root or a frequently-read path | Flag for `.gitignore`, `archive/`, or a deny rule | "`<path>` is X MB. Options: add to `.gitignore`, move to `archive/`, add it to `CLAUDE.md`'s 'don't read' list, or add a `Read(./<path>)` deny rule in `.claude/settings.json` so Claude Code enforces it instead of just being asked." |
| 5 | Multiple `.md` files with near-duplicate names (`notes.md`, `notes-final.md`, `notes-final-v2.md`) | Flag as version drift | "Found N versions of <basename>. These all get loaded when Claude greps for the topic. Recommend consolidating into one canonical file and archiving the rest." |
| 6 | Repeated test/scratch files (`test.py`, `test2.py`, `test_old.py`) | Suggest consolidation | "Found N scratch test files at the top level. Claude reads them all when looking for test patterns. Move the real test to `tests/` and trash the rest?" |
| 7 | `.DS_Store` count > 10 | Batch cleanup + gitignore | "N `.DS_Store` files in this tree. I can move them to Trash in one batch. Also recommend adding `.DS_Store` to `.gitignore` (not currently there)." |
| 8 | `.gitignore` missing common entries (`node_modules/`, `.venv/`, `__pycache__/`, `.DS_Store`, `.claude/worktrees/`, `CLAUDE.local.md`) given what's in use | Recommend the specific missing entries | "Detected <stack> in this repo. `.gitignore` is missing: <list>." |
| 9 | `node_modules/`, `.venv/`, or `dist/` is tracked in git | Flag as critical | "`<path>` is committed to git. Run `git rm -r --cached <path>` after adding it to `.gitignore`. Janitor will not run this for you." |
| 10 | Broken wiki-links in a vault with > 10 broken links | Schedule a cleanup session | "Found N broken wiki-links across M files. Want me to report them grouped by file so you can work through them over time?" |
| 11 | Orphaned scratchpads at top level (`scratch.py`, `untitled.md`, `tmp.js`) with mtime > 30 days | Ask about archiving | "Found N top-level files that look like scratchpads, last modified > 30 days ago. Want me to list them with first-lines so you can decide what to keep?" |
| 12 | `git worktree list` shows entries whose folder is gone, or `.claude/worktrees/*` folders untouched for 30+ days | Hand over the git commands | "`<path>` is listed as a worktree but the folder is gone. Run `git worktree prune --dry-run`, then `git worktree prune`. `<other path>` hasn't been touched in N days and has M uncommitted files; review before `git worktree remove`. Janitor won't run these." |
| 13 | `AGENTS.md` has content but a `CLAUDE.md` also exists and doesn't import it | Explain it's being ignored | "Claude Code reads `AGENTS.md` only when there's no `CLAUDE.md`. Yours is being skipped. Adding `@AGENTS.md` as the first line of `CLAUDE.md` loads it once, without duplicating the text." |
| 14 | Repo has a `README.md` that's significantly more up to date than `CLAUDE.md` | Recommend sync | "`README.md` mentions `<fact>` but `CLAUDE.md` doesn't. Want me to diff them?" |
| 15 | `CLAUDE.md` has no "Don't read / don't edit" section AND the repo has obvious don't-read candidates (`dist/`, `build/`, generated files) | Recommend the section, or deny rules for real enforcement | "Adding a 'Don't read' section with `<candidates>` helps. `CLAUDE.md` is guidance, not enforcement; `Read(./dist/**)` in `permissions.deny` makes Claude Code block it." |
| 16 | Multiple stale local branches (> 5 with upstream gone) | Flag for manual prune | "You have N local branches whose upstream is gone. Run `git fetch --prune` and review before deleting. Janitor will not delete branches." |
| 17 | Empty directories (possibly left after moves) | Flag as harmless but cleanable | "Found N empty directories. Want me to move them to Trash? Reversible." |
| 18 | A file in the repo matches a suspected-secret regex | Report file:line only, recommend tooling | "⚠️ Possible secret in `<file>:<line>`. I am not showing the matched string. Janitor will not edit the file or rewrite git history. Run a real secret scanner and rotate any exposed credentials." |
| 19 | A skill's `description` + `when_to_use` is over 1,536 characters, or a `SKILL.md` body is over 500 lines | Trim description, split body | "`<skill>`'s description is N characters; Claude Code truncates the listing at 1,536, so the end never reaches Claude, and the description sits in context every session. The body is M lines; the docs say under 500, with reference material in linked files that load only when read." |
| 20 | Several MCP servers in `.mcp.json` that the user says they don't use, or whose command is missing | Disable, don't delete | "`<server>` fails to start every session (`<command>` not found). Run `/mcp` to disable servers you don't use. Claude Code defers MCP tool definitions by default, but server names and instructions still load." |
| 21 | `settings.local.json` has a long pile of one-off allow rules | Suggest `/permissions` review | "`.claude/settings.local.json` has N allow rules; about M look single-use (hashes, temp paths, branch names). `/permissions` lists every rule with its source file so you can prune them." |
| 22 | User asks why sessions feel heavy or expensive | Point at the built-in meters, with what they show | "Run `/context` to see what's filling the context window (memory files, MCP tools, skills). On a subscription plan, `/usage` also attributes recent usage to skills, subagents, plugins and MCP servers and suggests fixes. `/clear` between unrelated tasks; `/compact <focus>` to keep what matters when you want continuity. A `# Compact instructions` section in `CLAUDE.md` steers every compaction." |
---

## Recommendation phrasing rules

1. **Name the specific file or count in every line.** "Found 37 `.DS_Store` files" beats "You have some `.DS_Store` cruft."
2. **Say what would change if the user accepts.** "This will save ~X tokens per session" when you can estimate it, otherwise "This will reduce the noise Claude walks through on every read."
3. **Never lecture about tokens in the abstract.** Users who have been using Claude Code for a week already know tokens are expensive. Skip the explanation, just point at the thing.
4. **Never recommend "add more documentation."** That's the opposite of what the user wants. Recommend *consolidating*, *archiving*, or *removing*, not adding.
5. **If a recommendation requires a git mutation, state clearly that janitor will not run it.** The user has to run `git rm --cached` / `git branch -D` / `git filter-repo` themselves. Give them the exact command, let them paste it.
6. **If an observation has no recommendation, don't mention it.** Don't fill space with "you have 3 markdown files and that's fine."
7. **Cap the recommendations list at ~7 items.** More than that and the report stops being a plan and starts being a lecture. Prioritize by impact: stale CLAUDE.md beats orphan count beats .gitignore hygiene.

---

## What NOT to recommend

These are things janitor-claude must never suggest, even if they'd technically save tokens:

- **Don't recommend installing more tooling.** No "you should use `pre-commit`" / "install `ruff`" / "set up `husky`." Janitor cleans what's here, it doesn't push new dependencies.
- **Don't recommend reorganizing the whole repo.** "Move everything into `src/`" is not janitor's call. The user's directory layout is their call.
- **Don't recommend deleting files with historical/archival value** even if they look "unused." `NOTES.md`, `IDEAS.md`, `archive/` — never flag these. They're intentional.
- **Don't recommend renaming files.** Renames break links, break git blame, and break Claude's memory. Out of scope.
- **Don't recommend adding comments to code.** Completely outside scope.
- **Don't recommend "refactoring" anything.** Janitor is about clutter, not code quality.
- **Don't recommend AI tooling changes.** No "switch to a different model" / "use Opus for this." Not the skill's job. Pointing at Claude Code's own built-in commands (`/context`, `/usage`, `/compact`, `/permissions`, `/mcp`, `/doctor prompt-audit`, `claude doctor`) is fine: they're already installed.
- **Don't recommend deleting `~/.claude` folders by hand.** Claude Code sweeps them on `cleanupPeriodDays`; the supported per-project removal is `claude purge` (irreversible, the user runs it).
- **Don't recommend cleaning up commit history.** No rebase suggestions. Git history is sacred.

---

## Recommendation ordering

When building the final report, order recommendations by **impact on the next session**, not alphabetically or by tier:

1. **Missing or stale `CLAUDE.md`, or instruction files that overlap / exceed 200 lines** — biggest per-session token cost, biggest win.
2. **Oversized files in the read path** — next biggest per-session cost.
3. **Broken wiki-links** (if it's a vault) — affects the user's ability to navigate.
4. **Broken Claude Code config** (missing hook scripts, dead MCP commands, skipped agents, truncated skill descriptions) — silent failures every session.
5. **Build artifacts in git** — low per-session cost, but high risk if left alone.
6. **Orphaned scratchpads + cruft** — smallest impact but highest "feels cleaner" dividend.
7. **`.gitignore` hygiene** — prevents future cruft from getting committed.
8. **Stale branches / worktrees, `~/.claude` weight** — disk, not tokens; last.

If a secret is detected, it jumps to the top of the list regardless of this ordering.
