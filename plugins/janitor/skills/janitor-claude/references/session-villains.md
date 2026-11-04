# Session / directory villain catalog

**Last verified:** 2026-11 (against code.claude.com/docs and the Claude Code changelog through v2.1.318) — update this date when you revise the catalog. Claude Code conventions and token-cost patterns evolve; a villain list that's stale will waste effort on things Claude now handles gracefully.

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

### Tool & test caches (`.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.ipynb_checkpoints`)

- **What they are:** Caches written by modern Python tooling — pytest, mypy, ruff — and Jupyter checkpoint snapshots. All regenerated automatically on the next run.
- **Why they matter:** Same blast radius as `__pycache__`: they bloat the tree, get committed by accident when there's no `.gitignore` entry, and every directory walk steps over them. They're more common now than `.pyc` files because the tools that write them ship in nearly every Python project.
- **How to detect:**
  ```bash
  find . -maxdepth 4 -type d \
    \( -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name ".ipynb_checkpoints" \) \
    ! -path "./node_modules/*" ! -path "./.git/*" ! -path "./.venv/*" 2>/dev/null
  ```
- **Fix:** machine-generated, so treat them exactly like `__pycache__` — show the count once, then batch-move to Trash on one confirmation. Suggest `.gitignore` entries if any were tracked. Never `rm`.

### Dead symlinks

- **What it is:** Symlinks pointing at files or directories that no longer exist. Usually left over from moved/renamed targets.
- **Why it matters:** `find`, `rg`, and Claude's own Read tool all stumble over them. Error noise, no value.
- **How to detect:**
  ```bash
  find . -type l ! -exec test -e {} \; -print 2>/dev/null
  ```
- **Fix:** show each broken link with its intended target, confirm, then move to Trash. Never follow and delete the target — only the dangling link itself.

### Missing project instructions in a non-trivial directory

- **What it is:** No project instruction file at the repo root. Claude Code accepts `./CLAUDE.md` **or** `./.claude/CLAUDE.md`, and (v2.1.277+) reads `AGENTS.md` instead when no `CLAUDE.md` / `.claude/CLAUDE.md` / `CLAUDE.local.md` exists in the working directory or above it. Only call it "missing" when **none** of these exist.
- **Why it matters:** Every session starts Claude "blind." Claude re-learns the stack, the commands, and the conventions from scratch on every prompt. This is the single biggest token waste in most working directories.
- **How to detect:**
  ```bash
  for f in CLAUDE.md .claude/CLAUDE.md CLAUDE.local.md AGENTS.md .claude/AGENTS.md; do
    test -f "$f" && echo "present: $f"
  done
  # Sub-roots in monorepos (these load on demand, not at launch):
  find . -maxdepth 3 \( -name "CLAUDE.md" -o -name "AGENTS.md" \) -type f \
    ! -path "./node_modules/*" ! -path "./.git/*" ! -path "./.claude/worktrees/*" 2>/dev/null
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
  # Compare tracked files to common build / cache directory patterns
  git ls-files 2>/dev/null | grep -E "^(dist|build|node_modules|\.venv|venv|\.next|\.nuxt|target|out|coverage|\.pytest_cache|\.mypy_cache|\.ruff_cache|__pycache__)/" | head -20
  # Check gitignore
  cat .gitignore 2>/dev/null
  ```
- **Fix:** **never run `git rm`.** Show the tracked paths, recommend the `.gitignore` entries needed, let the user run `git rm --cached` themselves.

### Committed `.env` and secret-bearing dotfiles

- **What they are:** `.env`, `.env.local`, `.env.production`, or similar files tracked in git. Unlike `.env.example` (a template, legitimate), a real `.env` almost always holds credentials.
- **Why they matter:** This is the most common way secrets leak into a repo. Once committed, the values are in git history even after deletion — a tracked `.env` is both a token-waste villain and a security incident waiting to happen.
- **How to detect:**
  ```bash
  # Tracked dotenv files, excluding example/template variants
  git ls-files 2>/dev/null | grep -E "(^|/)\.env($|\.)" | grep -vE "\.(example|sample|template|dist)$"
  ```
- **Fix:** **report and stop — never print the file contents.** Tell the user the path, recommend they (a) `git rm --cached <file>` themselves, (b) add it to `.gitignore`, and (c) **rotate any credentials it held**, because removing the file does nothing about git history. Point them at `gitleaks` / `git-filter-repo`. This connects to the "Suspected secrets" rule in Tier 3 — same handling, never remediate by editing.

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

### Stale git worktrees (including ones agent sessions left behind)

- **What they are:** Two kinds. (a) `git worktree add` checkouts the user made and forgot. (b) Worktrees Claude Code made: `claude --worktree <name>` and subagents with `isolation: worktree` create them under `.claude/worktrees/<name>/` on a branch named `worktree-<name>`. Claude Code removes a clean one at exit and sweeps subagent / background-session worktrees older than `cleanupPeriodDays` (default 30) **only when they hold no work**. Worktrees with uncommitted changes or unpushed commits, `-p` runs, and anything made with plain `git worktree add` stay until someone removes them.
- **Why they matter:** Each worktree is a full checkout. They eat disk, show up in `find` / `grep` from the main checkout, and a `.claude/worktrees/` folder that isn't gitignored floods `git status` with untracked files.
- **How to detect (read-only git only):**
  ```bash
  git worktree list --porcelain 2>/dev/null     # "prunable" lines = folder is gone
  git worktree list 2>/dev/null
  # Folders under .claude/worktrees/ untouched for 30+ days
  find .claude/worktrees -mindepth 1 -maxdepth 1 -type d -mtime +30 2>/dev/null
  # Is .claude/worktrees/ ignored? (no output = not ignored)
  git check-ignore -q .claude/worktrees/x 2>/dev/null && echo "ignored" || echo "not ignored"
  ```
  For each entry report: path, branch, whether the folder exists, last-modified date, and `git -C <path> status --short | wc -l` (uncommitted file count). Use `git log --oneline @{u}..` inside it only if it has an upstream.
- **Fix:** **report and hand over commands. Janitor never mutates git.**
  - Folder gone (`prunable`): tell the user to run `git worktree prune --dry-run`, then `git worktree prune`.
  - Folder present and clean: `git worktree remove <path>`. If git says it is locked, Claude Code may still be using it; only `git worktree unlock <path>` once the user knows no session is running there.
  - Folder present with work in it: say so plainly and let the user decide. Never suggest `--force` without naming what would be lost.
  - `.claude/worktrees/` not ignored: suggest adding `.claude/worktrees/` to `.gitignore` (the docs recommend this). That edit is diff-gated like any other.

---

## Tier 2b — Claude Code configuration hygiene

These are the files Claude Code itself reads every session. Most of them load before the user types anything, so drift here costs tokens and causes confusing behaviour on every prompt. **Read them with the Read tool and reason about them yourself.** Never edit any of them without a shown diff and an explicit "apply". Reference: code.claude.com/docs/en/memory, /settings, /permissions, /hooks, /mcp, /skills, /sub-agents, /claude-directory.

### Instruction files that overlap, contradict, or grew too big

- **What loads:** at launch, every `CLAUDE.md` and `CLAUDE.local.md` from the working directory **up to the filesystem root** (concatenated, not overriding), plus `.claude/CLAUDE.md`, `~/.claude/CLAUDE.md`, `.claude/rules/*.md` without a `paths:` field, and the first 200 lines / 25KB of auto memory's `MEMORY.md`. `CLAUDE.md` files in subdirectories load on demand when Claude touches a file there. `AGENTS.md` is read **instead of** `CLAUDE.md` only when no `CLAUDE.md` / `.claude/CLAUDE.md` / `CLAUDE.local.md` exists (default `claude-md-or-agents-md` mode); if both exist, `AGENTS.md` is ignored unless `CLAUDE.md` imports it with `@AGENTS.md`.
- **Villains to look for:**
  - **Size:** any instruction file over **200 lines** (the docs' target). `@imports` do *not* reduce cost: imported files load with the file that imports them, so add their lines to the total.
  - **AGENTS.md shadowed:** an `AGENTS.md` with real content next to a `CLAUDE.md` that does not contain `@AGENTS.md`. Claude Code is silently ignoring the `AGENTS.md`. Common surprise: adding a personal `CLAUDE.local.md` makes `AGENTS.md` stop loading.
  - **Duplicated content:** `CLAUDE.md` and `AGENTS.md` (or a parent and nested `CLAUDE.md`) repeating the same paragraphs. Every copy costs tokens; contradictory copies make Claude pick one arbitrarily.
  - **Old workarounds:** a `CLAUDE.md` that says "read AGENTS.md" in words (Claude may never open it; `@AGENTS.md` is the fix), or a `SessionStart` hook that prints `AGENTS.md` (now loads it twice).
  - **Tracked `CLAUDE.local.md`:** it is meant to be personal and gitignored. `git ls-files CLAUDE.local.md` returning a path means it is being shared.
- **How to detect:**
  ```bash
  for f in CLAUDE.md .claude/CLAUDE.md CLAUDE.local.md AGENTS.md .claude/AGENTS.md ~/.claude/CLAUDE.md; do
    test -f "$f" && printf "%6s lines  %s\n" "$(wc -l < "$f")" "$f"
  done
  find . -mindepth 2 -maxdepth 4 \( -name CLAUDE.md -o -name CLAUDE.local.md -o -name AGENTS.md \) -type f \
    ! -path "./node_modules/*" ! -path "./.git/*" ! -path "./.claude/worktrees/*" 2>/dev/null
  find .claude/rules ~/.claude/rules -name "*.md" -type f 2>/dev/null
  grep -n "@AGENTS.md" CLAUDE.md .claude/CLAUDE.md 2>/dev/null
  git ls-files CLAUDE.local.md 2>/dev/null
  ```
- **Fix:** report, then offer diff-gated edits only. Suggested moves, never applied silently: an `@AGENTS.md` import at the top of `CLAUDE.md` instead of duplicated text; workflow procedures out of `CLAUDE.md` into a skill; area-specific rules into a path-scoped `.claude/rules/<topic>.md` with a `paths:` list. Mention that `/doctor prompt-audit` (v2.1.283+) is Claude Code's own read-only audit for outdated or conflicting instruction files.

### `@imports` that point at nothing

- **What it is:** `@path/to/file` lines in `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md` or rules files whose target no longer exists. Relative paths resolve from the **file containing the import**, not the working directory; `~/` paths resolve from home; imports nest up to four hops. Text inside backticks or fenced code blocks is not an import. A path with spaces needs `\ ` escapes; a quoted path is not imported at all.
- **Why it matters:** the instruction the user thinks Claude has is silently missing.
- **How to detect:** extract `@` tokens outside code spans/fences from each instruction file (skip emails and `@scope/package` names that clearly aren't paths), resolve each against the importing file's directory, and `test -e` it. Report `file:line → target (missing)`.
- **Fix:** per-import menu (fix path / remove line / leave), diff-gated. Never guess a replacement below the 85% fuzzy-match rule in `markdown-audit-patterns.md`.

### Path-scoped rules that match nothing

- **What it is:** a `.claude/rules/*.md` file whose `paths:` frontmatter globs match no file in the repo (often after a rename like `src/api` → `apps/api`). Patterns are relative to the directory holding the rule's `.claude` folder.
- **How to detect:** read each rule's `paths:` list, then check each glob with `find`/`git ls-files` (e.g. `git ls-files 'src/api/**/*.ts' | head -1`). A rule where every glob returns nothing never loads.
- **Fix:** report only, with the closest existing directory if obvious. Diff-gated edit if the user asks.

### `settings.json` / `settings.local.json` drift

- **Files:** `.claude/settings.json` (shared, committed), `.claude/settings.local.json` (personal; Claude Code writes every "Yes, and don't ask again" approval here as a `permissions.allow` rule and adds it to the global git excludes), `~/.claude/settings.json` (user). Lists such as `permissions.allow` **merge** across files.
- **Villains to look for:**
  - **Invalid JSON:** settings files are strict JSON; a `//` comment or trailing comma makes Claude Code skip the file. Report the file and line; point the user at `claude doctor`, which lists rejected entries.
  - **One-off allow piles:** dozens of `Bash(...)` rules in `settings.local.json` that each name one exact command with a hash, temp path, date or PR number baked in (`Bash(git checkout fix-1234)`, `Bash(rm /tmp/x7f3)`). Count them, show the five oldest-looking, and suggest the user review them in `/permissions`, which shows every rule and the file it came from.
  - **Rules for paths that no longer exist:** `Read(...)` / `Edit(...)` rules whose path is gone. Path syntax: `//abs/path` is absolute, `~/path` is home, `/path` is relative to the settings source (project root for project/local files, **`~/.claude/` for user settings**), bare `path` is relative to cwd. A rule like `Read(/Users/alice/x)` with a single slash is a common bug: it is *not* absolute.
  - **Redundant rules:** an `allow` rule that a `deny` or `ask` rule always beats (evaluation order is deny → ask → allow; specificity does not matter), or exact duplicates across the merged files.
  - **Tracked local file:** `git ls-files .claude/settings.local.json` returning a path means personal approvals are being committed.
- **How to detect:** Read each file. Count `permissions.allow` entries per file. For path rules, resolve per the table above and `test -e`. Don't print `env` values from settings (they may hold tokens); name the key only.
- **Fix:** **report only by default.** If the user wants a rule removed, show the exact JSON diff and wait for "apply". Never touch `~/.claude/settings.json` unless the user named it.

### Hooks that call scripts that don't exist

- **What it is:** a `hooks` entry (in any settings file, a plugin's `hooks/hooks.json`, or skill/agent frontmatter) whose `type: "command"` points at a missing or non-executable script. A missing script is a **non-blocking error**: the action proceeds and the user sees `hook error: Failed with non-blocking status code ... No such file or directory`. So a "safety" hook with a typo'd path has never protected anything, unless it sets `"onFailure": "block"` (v2.1.295+).
- **How to detect:** for each hook command, take the first path-like token (or the path inside `args`), expand `${CLAUDE_PROJECT_DIR}` to the project root and `~` to home, then `test -f` and `test -x`. Skip commands that are plain binaries on PATH (`npx`, `node`, `python3`) but do check the script path in their arguments. `${CLAUDE_PLUGIN_ROOT}` hooks belong to plugins; report them, don't resolve into the cache.
- **Fix:** report `settings file → event → matcher → missing path`. Flag policy-looking hooks (names like `guard`, `block`, `deny`) first. The user fixes the path or removes the entry; diff-gated if they ask janitor to do it. `/hooks` in a session shows what's registered.

### `.mcp.json` servers whose command is missing

- **What it is:** project-scoped MCP servers live in `.mcp.json` at the project root under `mcpServers`. A `stdio` server (or one with no `type`) runs `command` + `args`; if the binary or script is gone, the server fails to connect every session. A `url` entry with no `type` is rejected. `${VAR}` with no default and an unset variable stays as literal text.
- **How to detect:** Read `.mcp.json`. For each stdio server, `command -v <command>` (or `test -x` for a path). For script args under the repo, `test -f`. For `${VAR}` references with no `:-default`, report the variable **name** only, never its value. User- and local-scope servers live in `~/.claude.json`; don't open that file unless the user asks (it also holds account state).
- **Fix:** report only. Point the user at `claude mcp list` (shows `✘ Failed to connect`) and `/mcp` to disable servers they don't use. Unused MCP servers add tool names and server instructions to context every session.

### Skills with broken or bloated frontmatter

- **Where:** `.claude/skills/<name>/SKILL.md` (project), `~/.claude/skills/<name>/SKILL.md` (personal), and nested `<subdir>/.claude/skills/`. Legacy single-file prompts in `.claude/commands/*.md` still work.
- **Villains to look for:**
  - **Frontmatter not on line 1:** frontmatter is only read when the opening `---` is the first line. A blank line or BOM above it means no fields load.
  - **YAML that doesn't parse:** the skill loads with no fields set (no description, so Claude falls back to the first content line).
  - **No `description`:** recommended field; without it the listing uses the body's first line, which rarely says when to use the skill.
  - **Over-long description:** `description` + `when_to_use` are truncated at **1,536 characters** in the skill listing, so anything past that never reaches Claude. Every description is in context every session (unless `disable-model-invocation: true`), so long ones are a standing token cost.
  - **Huge body:** the docs say keep `SKILL.md` under **500 lines**; move reference material into supporting files the skill links to (they load only when read).
  - **A folder with no `SKILL.md`** under `.claude/skills/`, or a folder named `synced` (reserved).
- **How to detect:**
  ```bash
  find .claude/skills ~/.claude/skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | while read d; do
    f="$d/SKILL.md"; if [ ! -f "$f" ]; then echo "no SKILL.md: $d"; continue; fi
    head -1 "$f" | grep -q '^---$' || echo "frontmatter not on line 1: $f"
    printf "%5s lines  %s\n" "$(wc -l < "$f")" "$f"
  done
  ```
  Then Read the frontmatter of each and measure `description` + `when_to_use` length yourself.
- **Fix:** report only. Description rewrites are user-authored content: diff-gated, per file.

### Duplicate agents and commands

- **Agents:** `.claude/agents/*.md` and `~/.claude/agents/*.md` (scanned recursively). `name` and `description` are both **required**; a file with no `name` is treated as documentation, a file with `name` but no `description`, a `name` containing `:` or starting with `-`, or unparseable YAML is **skipped silently** (reason only in the `--debug` log). Two files in the same `agents/` tree with the same `name` load only one, by filesystem order. Same name across scopes: project beats user beats plugin.
- **Commands vs skills:** a skill and a `.claude/commands/<name>.md` with the same name collide. The docs say the skill wins, but inside a plugin the command file was seen loading instead of the skill (janitor 0.3 testing, November 2026). Either way one of them is dead weight: report the pair and suggest keeping the skill. Personal beats project for skills of the same name.
- **How to detect:** list `name:` values across `.claude/agents/`, `~/.claude/agents/`; list command basenames in `.claude/commands/` and `~/.claude/commands/` against skill folder names. Report collisions and skipped files.
- **Fix:** report only. Suggest which copy is shadowed; the user decides which to keep. Moving a shadowed file to Trash is a per-file confirmation.

### Other AI tools' clutter in the repo

- **What it is:** instruction and config folders other coding agents leave behind: `.cursor/` and `.cursorrules`, `.windsurf/` and `.windsurfrules`, `.clinerules`, `.devin/`, `.codex/`, `.github/copilot-instructions.md`, `GEMINI.md`. (Claude Code's own `/init` can read `.cursor/rules/`, `.cursorrules`, `.windsurf/rules/`, `.windsurfrules`, `.clinerules`, `.devin/rules/`; the rest are other tools' conventions.)
- **Why it matters:** usually harmless, but stale copies drift from `CLAUDE.md` and confuse teammates using other tools.
- **How to detect:**
  ```bash
  ls -d .cursor .cursorrules .windsurf .windsurfrules .clinerules .devin .codex .github/copilot-instructions.md GEMINI.md 2>/dev/null
  ```
- **Fix:** **report only, never move.** Other people may depend on them. Note any obvious contradictions with `CLAUDE.md`.

---

## Tier 4 — User-level `~/.claude` weight (opt-in only)

**Only run this tier when the user explicitly asks** ("check my ~/.claude", "how much space is Claude using", "clean up Claude's own files"). It is outside the working directory. Everything here is **sizes and counts only.**

**Hard rules for this tier:**
- **Never open, cat, grep, or summarise `.jsonl` transcripts** unless the user asks for a specific one. Transcripts are plaintext and can contain file contents, command output, and credentials that passed through a tool.
- **Never touch `~/.claude/projects/<project>/memory/`** (auto memory), `.credentials.json`, `agent-memory/`, `jobs/`, `daemon/`, `settings.json`, `plugins/`, or `~/.claude.json`.
- **Janitor does not delete Claude Code's application data.** Claude Code already sweeps most of it. Report, explain what Claude Code does on its own, and hand the user the built-in command.

### What Claude Code already cleans

Per the docs (claude-directory, "Cleaned up automatically"), Claude Code deletes files older than `cleanupPeriodDays` (**default 30, minimum 1**) from: `projects/<project>/<session>.jsonl` and each session's `subagents/`, `tool-results/`, `mcp-tasks/` folders, `file-history/`, `plans/`, `debug/`, `paste-cache/`, `image-cache/`, `uploads/`, `session-env/`, `tasks/`, `shell-snapshots/` (removed on clean exit; the sweep clears crash leftovers), `backups/` (keeps 5), `usage-data/`, and the legacy `todos/`, `statsig/`, `logs/` folders. Auto memory is excluded. The sweep is skipped in `--bare` runs and pauses when a settings file can't be parsed (a warning shows in `/status`).

Not swept: `history.jsonl`, `stats-cache.json`, and orphaned worktrees with work in them.

### How to measure

```bash
du -sh ~/.claude 2>/dev/null
du -sh ~/.claude/projects ~/.claude/file-history ~/.claude/plugins/cache \
       ~/.claude/shell-snapshots ~/.claude/todos ~/.claude/debug ~/.claude/paste-cache \
       ~/.claude/usage-data ~/.claude/history.jsonl 2>/dev/null
# Biggest project transcript folders (sizes only, contents never read)
du -sh ~/.claude/projects/*/ 2>/dev/null | sort -rh | head -10
ls ~/.claude/projects 2>/dev/null | wc -l
# Oldest transcript age, to tell whether the sweep is running
find ~/.claude/projects -maxdepth 2 -name "*.jsonl" -type f -mtime +31 2>/dev/null | wc -l
# Effective retention setting, if set anywhere the user owns
grep -n '"cleanupPeriodDays"' ~/.claude/settings.json .claude/settings.json .claude/settings.local.json 2>/dev/null
```

Respect `CLAUDE_CONFIG_DIR` and `CLAUDE_CODE_PLUGIN_CACHE_DIR` if set: then `~/.claude` (or the plugin root) lives there instead.

### Villains in this tier

- **Transcripts older than the retention period still on disk:** many `*.jsonl` older than `cleanupPeriodDays` means the sweep is paused (broken settings file) or the user set a very large value. Report the count and total size, then point at `/status` and `claude doctor`.
- **A huge `projects/` folder by design:** the user may have raised `cleanupPeriodDays`. Tell them the current value and that lowering it shrinks the folder and shortens how long plaintext transcripts sit on disk. Changing it is a settings edit, diff-gated.
- **Projects for repos that no longer exist:** folder names are the project path with non-alphanumerics replaced by `-`. If the decoded path doesn't exist, list it with its size. The removal tool is Claude Code's own `claude purge <path> --dry-run` (then `claude purge <path>`, which asks `[y/N]` and **cannot be undone**; it also deletes that project's auto memory). Hand the user the command; janitor never runs it.
- **Old plugin versions:** each installed version sits in `plugins/cache/<marketplace>/<plugin>/<version>/`. On update or uninstall Claude Code writes an `.orphaned_at` marker in the old version and removes it **14 days later**, but only while at least one plugin is still installed. Report versions whose `.orphaned_at` is older than 14 days, and plugins with several version folders and no marker. Fix: `/plugin` or `claude plugin uninstall`; janitor never edits the cache.
  ```bash
  find ~/.claude/plugins/cache -mindepth 3 -maxdepth 3 -type d 2>/dev/null | while read v; do
    printf "%8s  %s%s\n" "$(du -sh "$v" | cut -f1)" "$v" "$( [ -f "$v/.orphaned_at" ] && echo '  (orphaned)')"
  done
  ```
- **Leftover shell snapshots and legacy folders:** a non-empty `shell-snapshots/` while no Claude session is running means crashed sessions; `todos/`, `statsig/`, `logs/` are legacy and no longer written. All of these the next sweep removes. Report and say so; nothing for janitor to do.
- **`.heapsnapshot` files from `/heapdump`:** neither the sweep nor `claude purge` removes them, and they contain the full conversation and any credentials the process held. Report path and size only; offer Trash with per-file confirmation.

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

- **Never `git add`, `git rm`, `git commit`, `git push`, `git reset`, `git branch -D`, `git clean`, `git worktree remove`, `git worktree prune`.** Read-only git only. `git status`, `git log`, `git diff`, `git ls-files`, `git check-ignore`, `git worktree list` are fine.
- **Never edit `settings.json`, `settings.local.json`, `.mcp.json`, hook config, skills, or agents without a shown diff and an explicit "apply".**
- **Never read transcript contents** under `~/.claude/projects/`, never touch auto memory, and never run `claude purge`, `claude mcp`, or `claude plugin` commands for the user. Hand them the command.
- **Never overwrite `CLAUDE.md`.** If one exists, switch to staleness-audit mode. Never replace it wholesale.
- **Never auto-rewrite a broken wiki-link.** Report with options, let the user resolve.
- **Never touch files inside `.git/`.** Ever.
- **Never print secret contents.** File and line only.
- **Never `rm -rf`** anything. All deletions go through `~/.Trash/` (macOS) or Recycle Bin (Windows) so they're recoverable.
- **Never auto-edit a file the user authored.** Machine-generated cruft (`.DS_Store`, `__pycache__`) is the only category that can be moved without a per-file ask, and even then only after the count has been shown once.
- **Never walk into `node_modules/`, `.venv/`, `.git/`, `dist/`, `build/`, `.next/`, `.claude/worktrees/`.** Exclude these from all diagnostic passes — they'll dominate every result and waste everyone's time.

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
./.claude/worktrees/*
./.DS_Store
```

Don't audit cruft inside cruft. The whole point is signal, not a giant count of `.pyc` files inside a `.venv`. `.claude/worktrees/*` is excluded because each one is a full second checkout; audit worktrees with the dedicated villain above, not by walking into them.
