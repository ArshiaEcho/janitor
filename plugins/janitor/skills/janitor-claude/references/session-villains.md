# Session / directory villain catalog

**Last verified:** 2026-04 — update this date when you revise the catalog. Claude Code conventions and token-cost patterns evolve; a villain list that's stale will waste effort on things Claude now handles gracefully.

Load this file when janitor-claude has finished Phase 1 diagnostics and needs to match observations against known culprits. These are the things that actually slow down Claude Code sessions and waste tokens in real working directories, ranked by likelihood and blast radius.

Unlike janitor-device, **the default here is read-only**. A working directory is someone's in-progress work. Touching the wrong file means lost thought, not a slow fan. Every fix below is reversible or gated on explicit confirmation.

---

## Tier 1 — Almost always present, almost always safe to fix

### `.DS_Store` files everywhere

- **What it is:** Finder metadata files macOS writes into every folder you open. They have no value inside a code repo.
- **Why it matters:** They pollute `git status`, they get accidentally committed, and every `find` / `grep` / `ls -R` walks over them.
- **How to detect:**
  ```bash
  find . -name ".DS_Store" -type f 2>/dev/null | head -50
  find . -name ".DS_Store" -type f 2>/dev/null | wc -l
  ```
- **Fix (auto-allowed after the count is shown):** move each `.DS_Store` to `~/.Trash/` via `mv`. Never `rm`. Confirm the count with the user once, then batch the move. Also suggest adding `.DS_Store` to `.gitignore` if missing.

### Python bytecode cruft (`__pycache__`, `*.pyc`)

- **What it is:** Python compiler output. Regenerated automatically on next run.
- **Why it matters:** Bloats the directory, breaks some tooling, and frequently gets committed on accident when the user doesn't have a `.gitignore` entry.
- **How to detect:**
  ```bash
  find . -type d -name "__pycache__" 2>/dev/null | head -20
  find . -type f -name "*.pyc" 2>/dev/null | wc -l
  ```
- **Fix:** ask once, then move to Trash in one batch. Suggest `.gitignore` entries if missing.

### Dead symlinks

- **What it is:** Symlinks pointing at files or directories that no longer exist. Usually left over from moved/renamed targets.
- **Why it matters:** `find`, `rg`, and Claude's own Read tool all stumble over them. Error noise, no value.
- **How to detect:**
  ```bash
  find . -type l ! -exec test -e {} \; -print 2>/dev/null
  ```
- **Fix:** show each broken link with its intended target, confirm, then move to Trash. Never follow and delete the target — only the dangling link itself.

### Missing `CLAUDE.md` in a non-trivial directory

- **What it is:** No `CLAUDE.md` file at the repo root (or at a logical sub-root for monorepos).
- **Why it matters:** Every session starts Claude "blind." Claude re-learns the stack, the commands, and the conventions from scratch on every prompt. This is the single biggest token waste in most working directories.
- **How to detect:**
  ```bash
  test -f CLAUDE.md && echo "present" || echo "missing"
  # Also check sub-roots for monorepos:
  find . -maxdepth 3 -name "CLAUDE.md" 2>/dev/null
  ```
- **Fix:** **never auto-generate.** Trigger the scaffolding protocol (`references/claude-md-scaffold.md`): ask the user 5 questions, draft the file, show as diff, wait for explicit yes.
- **Trigger condition:** only offer if the directory is "non-trivial" — has `.git/`, has source files, has more than a handful of actual content files. Don't offer a CLAUDE.md for an empty scratch folder.

---

## Tier 2 — Common, usually worth a conversation

### Orphaned scratchpads and one-off files

- **What they are:** `scratch.py`, `test.js`, `untitled.md`, `notes.txt`, `foo.py`, `asdf.md` — files the user created during a debugging session and forgot to clean up.
- **Why they matter:** Clutter the file tree, show up in autocomplete, confuse future grep runs, waste tokens when Claude reads them looking for context.
- **How to detect:**
  ```bash
  find . -maxdepth 2 -type f \( -name "scratch*" -o -name "test.*" -o -name "untitled*" -o -name "temp*" -o -name "tmp*" -o -name "foo*" -o -name "bar*" -o -name "asdf*" \) 2>/dev/null
  ```
- **Fix:** **always list first.** Some of these are real ("test.js" might be the user's test file). Show each one with its last-modified date and first line. Ask per-file or in a batch — never auto-delete.

### Oversized files Claude keeps re-reading

- **What they are:** Large transcripts, logs, minified bundles, or generated files that Claude loaded into context at some point. The file itself may be legitimate, but pulling it into every session wastes tokens.
- **Why they matter:** A 10 MB JSON in the repo root is a 10 MB problem every time Claude indexes the directory.
- **How to detect:**
  ```bash
  # Files over 500 KB, not in node_modules / .git / dist
  find . -type f -size +500k \
    ! -path "./node_modules/*" \
    ! -path "./.git/*" \
    ! -path "./dist/*" \
    ! -path "./build/*" \
    ! -path "./.venv/*" 2>/dev/null | head -20
  ```
- **Fix:** **never auto-move.** Flag to the user, suggest either (a) moving to a sibling `archive/` folder, (b) adding to `.gitignore`, or (c) adding to a CLAUDE.md "don't read" section. User decides.

### Build artifacts not in `.gitignore`

- **What they are:** `dist/`, `build/`, `node_modules/`, `.venv/`, `.next/`, `target/`, `out/` — committed or staged when they shouldn't be.
- **Why they matter:** Bloats the repo, wastes tokens on every Claude read, and worst case leaks local machine state into git history.
- **How to detect:**
  ```bash
  # Compare tracked files to common build directory patterns
  git ls-files 2>/dev/null | grep -E "^(dist|build|node_modules|\.venv|\.next|target|out)/" | head -20
  # Check gitignore
  cat .gitignore 2>/dev/null
  ```
- **Fix:** **never run `git rm`.** Show the tracked paths, recommend the `.gitignore` entries needed, let the user run `git rm --cached` themselves.

### Broken Obsidian / markdown wiki-links

- **What they are:** `[[Some Page]]` or `[label](path/to/file.md)` references where the target doesn't resolve.
- **Why they matter:** In a knowledge vault, broken links are broken thoughts. In a docs folder, broken links are lies in the documentation.
- **How to detect:** see `references/markdown-audit-patterns.md` for the full regex + resolution rules.
- **Fix:** **never auto-rewrite.** Report broken links grouped by source file, with fuzzy-match suggestions (>85% similarity only), and present three choices per link: ignore, fix to suggested target, remove. The user resolves each one. **Forward-linking is a legitimate Obsidian pattern** — a link to a page that doesn't exist yet is often intentional.

### Stale `CLAUDE.md` facts

- **What it is:** A `CLAUDE.md` that references commands, file paths, or conventions that no longer match reality. Common staleness: "run `npm test`" when `package.json` has no test script, "see `src/old_api.py`" when the file has been moved, "we use Firebase" when the code has migrated to Supabase.
- **Why it matters:** Stale context is worse than no context. Claude confidently follows outdated instructions.
- **How to detect:** parse `CLAUDE.md`, extract claimed commands / file references / tech stack, cross-check against `package.json` / actual file existence / `requirements.txt` / etc.
- **Fix:** present a diff showing proposed changes, one block at a time. **Never overwrite `CLAUDE.md` without an explicit yes on the specific diff.** See `references/claude-md-scaffold.md` for the staleness audit protocol.

### Old git worktrees never cleaned up

- **What they are:** `git worktree add` directories the user created for a specific feature branch, finished, and forgot about.
- **Why they matter:** Each worktree is a full checkout. They eat disk space and show up in searches.
- **How to detect:**
  ```bash
  git worktree list 2>/dev/null
  ```
- **Fix:** **never auto-remove.** Show the list, flag worktrees whose branch has merged or been deleted upstream, ask per-worktree.

---

## Tier 3 — Less common but worth checking

### Orphaned markdown files (unreferenced from anywhere)

- **What they are:** `.md` files in a notes/docs directory that nothing else links to and that haven't been touched in months.
- **Why they matter:** In an Obsidian vault, they're usually abandoned drafts. In a docs folder, they might be abandoned designs.
- **How to detect:** for each `.md` file, check if any other `.md` file references it (via wiki-link or markdown link).
- **Fix:** report only — never move. Let the user decide if they're still needed. Some "orphans" are notes the user hasn't linked yet but still values.

### Stale front-matter dates

- **What it is:** A `.md` file with `date: 2023-01-15` in its front-matter but a git `mtime` of 2025-11-02. The user edited the file but forgot to bump the date.
- **Why it matters:** For Obsidian vaults organized by date, this shows up in the wrong place in dataview queries.
- **Fix:** report only — never auto-bump. Bumping dates is lying about history.

### Stale branches

- **What they are:** Local branches whose upstream is gone (merged PR, deleted branch on origin).
- **Why they matter:** Clutter in `git branch` output, occasional checkouts-to-the-wrong-thing.
- **How to detect:**
  ```bash
  git fetch --prune --dry-run 2>&1
  git branch -vv 2>/dev/null | grep ": gone]"
  ```
- **Fix:** **never run `git branch -D`.** Show the list, recommend the user review and delete manually. Janitor never destroys git history.

### Suspected secrets in tracked files

- **What they are:** Files committed to git that contain patterns matching API keys, tokens, or credentials.
- **Why they matter:** Obvious. Security incident waiting to happen.
- **How to detect:** small, high-precision regex set only. Patterns like `AKIA[0-9A-Z]{16}`, `ghp_[0-9a-zA-Z]{36}`, `sk-[A-Za-z0-9]{48}`, `sk-ant-[A-Za-z0-9-]{90,}`. **Report `file:line` only — never print the matched substring.** Also never print it into the chat log.
- **Fix:** **report and stop.** Tell the user exactly which file and line, recommend `git-filter-repo` or `gitleaks`, and explicitly state "janitor-claude does not rewrite git history." This is not a substitute for a real secret scanner.
- **Never** attempt to remediate this by editing the file — the secret is already in git history, editing the current file does nothing.

### Oversized `.git/` directory

- **What it is:** A `.git/` folder that's gotten huge, usually from a binary committed in the past and then "deleted."
- **Why it matters:** Clone times, disk use, and it's a sign there's something in git history that probably shouldn't be.
- **How to detect:**
  ```bash
  du -sh .git 2>/dev/null
  git count-objects -v 2>/dev/null
  ```
- **Fix:** **never run `git gc --aggressive` or `git filter-repo`.** Report the size, note that history rewriting is out of janitor's scope, and point the user at the dedicated tools.

---

## What janitor-claude NEVER does to a directory

These are load-bearing. Break them and you lose the user's trust for every future run.

- **Never `git add`, `git rm`, `git commit`, `git push`, `git reset`, `git branch -D`, `git clean`.** Read-only git only. `git status`, `git log`, `git diff`, `git ls-files`, `git worktree list` are fine.
- **Never overwrite `CLAUDE.md`.** If one exists, switch to staleness-audit mode. Never replace it wholesale.
- **Never auto-rewrite a broken wiki-link.** Report with options, let the user resolve.
- **Never touch files inside `.git/`.** Ever.
- **Never print secret contents.** File and line only.
- **Never `rm -rf`** anything. All deletions go through `~/.Trash/` (macOS) or Recycle Bin (Windows) so they're recoverable.
- **Never auto-edit a file the user authored.** Machine-generated cruft (`.DS_Store`, `__pycache__`) is the only category that can be moved without a per-file ask, and even then only after the count has been shown once.
- **Never walk into `node_modules/`, `.venv/`, `.git/`, `dist/`, `build/`, `.next/`.** Exclude these from all diagnostic passes — they'll dominate every result and waste everyone's time.

---

## Detection exclusion list (use everywhere)

Every `find` command in Phase 1 should exclude these paths so the output stays focused on the user's actual work:

```
./node_modules/*
./.git/*
./.venv/*
./venv/*
./dist/*
./build/*
./.next/*
./.nuxt/*
./target/*
./out/*
./__pycache__/*
./.pytest_cache/*
./.mypy_cache/*
./.ruff_cache/*
./coverage/*
./.coverage
./.tox/*
./.DS_Store
```

Don't audit cruft inside cruft. The whole point is signal, not a giant count of `.pyc` files inside a `.venv`.
