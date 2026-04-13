# Token-waste recommendations — observation → rule

Load this file when janitor-claude is generating the recommendations section of its report. **Every recommendation in this file must cite a specific file, path, or pattern in the user's actual directory.** Generic essays about "tokens are expensive" are forbidden.

The test for whether a recommendation belongs here: if you could have said the same thing before running any diagnostics, it doesn't belong. Only ship advice that's grounded in what you just observed.

---

## The rule table

Each row is an observation → recommendation. Each recommendation includes the exact form of advice to give the user. Never hand-wave.

| # | Observation | Recommendation | Form of advice |
|---|---|---|---|
| 1 | `CLAUDE.md` is missing from a non-trivial repo | Offer to scaffold one via the 5-question protocol | "I can draft a `CLAUDE.md` for you. It'll save ~X tokens per session by removing the re-learn step. Want me to ask you 5 questions and show you a draft?" |
| 2 | `CLAUDE.md` exists but is over 400 lines | Flag as oversized | "Your `CLAUDE.md` is N lines. Most of it is loaded on every prompt. The top-loaded sections should be: stack, commands, file map, conventions. Anything reference-grade should move to `docs/` or a sub-file you only pull when needed." |
| 3 | `CLAUDE.md` references a command that doesn't exist (e.g. "run `npm test`" but no test script in `package.json`) | Stale fact — show diff | "`CLAUDE.md` line N says `<command>`. That script isn't in `package.json`. Want me to show you a diff updating it?" |
| 4 | Oversized file (`.json`, `.log`, `.txt` > 500 KB) in the repo root or a frequently-read path | Flag for `.gitignore` or `archive/` move | "`<path>` is X MB. Every time I read this directory, that's a large chunk of context. Options: add to `.gitignore`, move to `archive/`, or add to a `CLAUDE.md` 'don't read' list." |
| 5 | Multiple `.md` files with near-duplicate names (`notes.md`, `notes-final.md`, `notes-final-v2.md`) | Flag as version drift | "Found N versions of <basename>. These all get loaded when Claude greps for the topic. Recommend consolidating into one canonical file and archiving the rest." |
| 6 | Repeated test/scratch files (`test.py`, `test2.py`, `test_old.py`) | Suggest consolidation | "Found N scratch test files at the top level. Claude reads them all when looking for test patterns. Move the real test to `tests/` and trash the rest?" |
| 7 | `.DS_Store` count > 10 | Batch cleanup + gitignore | "N `.DS_Store` files in this tree. I can move them to Trash in one batch. Also recommend adding `.DS_Store` to `.gitignore` (not currently there)." |
| 8 | `.gitignore` missing common entries (`node_modules/`, `.venv/`, `__pycache__/`, `.DS_Store`) given the stack in use | Recommend the specific missing entries | "Detected <stack> in this repo. `.gitignore` is missing: <list>. These should be added to prevent committing build cruft." |
| 9 | `node_modules/`, `.venv/`, or `dist/` is tracked in git | Flag as critical | "`<path>` is committed to git. This is almost always unintentional — it bloats history and leaks machine-local state. Run `git rm -r --cached <path>` after adding it to `.gitignore`. Janitor will not run this for you." |
| 10 | Broken wiki-links in a vault with > 10 broken links | Schedule a cleanup session | "Found N broken wiki-links across M files. That's too many to fix in one turn. Want me to report them grouped by file so you can work through them over time?" |
| 11 | Orphaned scratchpads at top level (`scratch.py`, `untitled.md`, `tmp.js`) with mtime > 30 days | Ask about archiving | "Found N top-level files that look like scratchpads, last modified > 30 days ago. Want me to list them with first-lines so you can decide what to keep?" |
| 12 | Git worktree list shows directories for branches that are gone upstream | Flag for removal | "Worktree `<path>` tracks branch `<name>` which is gone upstream (PR merged or branch deleted). Review and `git worktree remove` manually." |
| 13 | Same file repeatedly appears in `.claude/sessions/` transcripts as a re-read target | Recommend adding to CLAUDE.md file map | "`<path>` gets read on almost every session. Adding it to the `## Files to know about` section of `CLAUDE.md` would save tokens by putting it in the first read instead of a follow-up." |
| 14 | Repo has a `README.md` that's significantly more up to date than `CLAUDE.md` | Recommend sync | "`README.md` mentions `<fact>` but `CLAUDE.md` doesn't. If the README is accurate, `CLAUDE.md` should reflect the same. Want me to diff them?" |
| 15 | `CLAUDE.md` has no "Don't read / don't edit" section AND the repo has obvious don't-read candidates (`dist/`, `build/`, generated files) | Recommend adding the section | "`CLAUDE.md` has no 'Don't read' section. Adding one with `<specific candidates>` would save tokens and prevent Claude from walking into generated code." |
| 16 | Multiple stale local branches (> 5 with upstream gone) | Flag for manual prune | "You have N local branches whose upstream is gone. Run `git fetch --prune` and review before deleting. Janitor will not delete branches." |
| 17 | Empty directories (possibly left after moves) | Flag as harmless but cleanable | "Found N empty directories (likely leftover from moves). Want me to remove them? They go to Trash, reversible." |
| 18 | A file in the repo matches a suspected-secret regex | Report file:line only, recommend tooling | "⚠️ Possible secret in `<file>:<line>`. I am not showing the matched string. This is not a substitute for `gitleaks`. Janitor will not edit the file and will not rewrite git history. Recommend running a real secret scanner and rotating any exposed credentials." |

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
- **Don't recommend AI tooling changes.** No "switch to a different model" / "use Opus for this." Not the skill's job.
- **Don't recommend cleaning up commit history.** No rebase suggestions. Git history is sacred.

---

## Recommendation ordering

When building the final report, order recommendations by **impact on the next session**, not alphabetically or by tier:

1. **Missing or stale `CLAUDE.md`** — biggest per-session token cost, biggest win.
2. **Oversized files in the read path** — next biggest per-session cost.
3. **Broken wiki-links** (if it's a vault) — affects the user's ability to navigate.
4. **Build artifacts in git** — low per-session cost, but high risk if left alone.
5. **Orphaned scratchpads + cruft** — smallest impact but highest "feels cleaner" dividend.
6. **`.gitignore` hygiene** — prevents future cruft from getting committed.
7. **Stale branches / worktrees** — cosmetic, last.

If a secret is detected, it jumps to the top of the list regardless of this ordering.
