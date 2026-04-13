# CLAUDE.md scaffold & staleness audit protocol

Load this file when janitor-claude is either (a) going to offer to create a new `CLAUDE.md` for a directory that doesn't have one, or (b) going to audit an existing `CLAUDE.md` for staleness. These are two related but distinct flows. Do not conflate them.

**The single most important rule in this file: never overwrite an existing `CLAUDE.md`.** If one exists, even if it's half-written or stale, switch to staleness-audit mode. The user wrote it. Never replace it wholesale.

---

## Part 1 — Scaffold mode (no existing CLAUDE.md)

### Entry conditions

All of these must be true before offering to scaffold:

- No `CLAUDE.md` exists at the repo root.
- The directory is "non-trivial" — it has a `.git/` directory, AND at least 5 source files (not counting config / lockfiles / generated files), AND is not a pure scratch folder.
- The user has accepted the offer explicitly. **Never scaffold without being asked.** Offering is fine; generating-without-yes is not.

If any of these fail, don't scaffold. For an empty folder or a one-file scratch directory, a `CLAUDE.md` is overhead with no payoff.

### The auto-detection step (before asking the user)

Before asking questions, gather what you can from the filesystem. Run all of these **in parallel**:

```bash
# What kind of project is this?
ls -la
test -f package.json && cat package.json | head -50
test -f pyproject.toml && cat pyproject.toml | head -50
test -f Cargo.toml && cat Cargo.toml | head -30
test -f go.mod && cat go.mod | head -10
test -f Gemfile && cat Gemfile | head -20

# What does the README say?
test -f README.md && head -80 README.md

# What commands are defined?
test -f package.json && cat package.json | grep -A1 '"scripts"'
test -f Makefile && grep -E "^[a-zA-Z_-]+:" Makefile
test -f justfile && cat justfile | head -40

# What's in .gitignore (tells you what NOT to read)
test -f .gitignore && cat .gitignore

# Directory shape
find . -maxdepth 2 -type d \
  ! -path "./node_modules*" \
  ! -path "./.git*" \
  ! -path "./.venv*" \
  ! -path "./dist*" \
  ! -path "./build*" 2>/dev/null
```

From this you can usually auto-fill:
- **Stack**: inferred from the manifest file (`package.json` → Node, `pyproject.toml` → Python, etc.)
- **Commands**: lifted from `scripts:` in `package.json`, `Makefile` targets, `justfile` recipes
- **Directory structure**: from the `find` output
- **Don't-read paths**: from `.gitignore` + standard build directories

### The 5-question protocol

After auto-detecting, ask the user these 5 questions in **one batch** (one message, numbered). Don't drip them one at a time — that's five round-trips instead of one.

The questions:

1. **One-line purpose** — "What does this repo do, in one sentence? (I'll write this as the first line.)"
2. **What Claude should never touch** — "Are there files or directories Claude should never read or edit? (e.g. legacy code you're migrating away from, generated files, vendor code.)"
3. **Conventions that aren't obvious** — "Any conventions Claude should follow that aren't obvious from the code? (e.g. 'all new code in TypeScript, don't touch the Python scripts', 'use tabs not spaces', 'always add tests for new handlers'.)"
4. **The 3-5 most important files** — "Which 3-5 files should Claude know about by name? (The files you'd point a new contributor at on day one.)"
5. **Anything I got wrong in the auto-detection** — show the user what you auto-filled for stack / commands / structure, and ask if anything is wrong or missing.

**Why these 5 and not more**: every additional question risks losing the user's attention. The answers to these five cover ~90% of what a useful `CLAUDE.md` actually contains. The rest of the template has sensible defaults.

**Why these 5 and not fewer**: fewer and you end up with a boilerplate file that says nothing. The point of `CLAUDE.md` is personal, specific guidance — all five questions produce information that can't be auto-detected.

### Generating the file

1. Load `assets/claude-md-template.md`.
2. Fill in each section from (a) auto-detected values, (b) user answers, (c) sensible defaults for anything missing.
3. **Show the full file as a diff** (treating the current state as an empty file) before writing anything to disk.
4. Ask: "Does this look right? Reply with 'write it', 'change <section>', or 'cancel'."
5. Only write the file on explicit "write it" or equivalent. **Never write on an ambiguous response.** If the user says "sure" or "okay", confirm once more — those can mean "okay I saw it" rather than "yes go ahead."

### If the user wants to iterate

Accept iteration. Edit the draft in-chat, show the diff again, ask again. There's no limit on iteration, but after 3 rounds gently check in: "Do you want to write what we have and iterate in git, or keep drafting in chat?"

### What the generated file should always contain

Every generated `CLAUDE.md` should have these sections, in this order:

1. **Title + one-line purpose** (from question 1)
2. **Stack** (auto-detected + user corrections from question 5)
3. **Commands** (auto-detected from scripts / Makefile / etc.)
4. **Conventions** (from question 3)
5. **Don't read / don't edit** (from question 2 + `.gitignore` + standard build dirs)
6. **Files Claude should know about** (from question 4)

Do **not** add these without being asked:

- Contributing guide stubs
- License boilerplate
- "About the team" sections
- "Future roadmap" sections
- Anything longer than 100 lines total — if the draft is longer, trim it. A 400-line `CLAUDE.md` is itself a token-waste problem.

---

## Part 2 — Staleness audit mode (CLAUDE.md already exists)

### Entry conditions

- `CLAUDE.md` exists at the repo root (or at the directory the user named).
- The user has either (a) explicitly asked for an audit, or (b) the file has obvious staleness that janitor noticed during Phase 1.

### What to check for

Parse the existing file, extract claims, and cross-check each claim against current reality:

| Claim type | How to verify | Example staleness |
|---|---|---|
| Build/test/dev command | Compare to `package.json` scripts, `Makefile` targets, `justfile` recipes, `pyproject.toml` scripts | `CLAUDE.md` says `npm test` but `package.json` has no `test` script |
| Tech stack / framework | Compare to manifest files | `CLAUDE.md` says "React 17" but `package.json` has "react": "^19.0.0" |
| File path references | For every file path mentioned, check it exists | `CLAUDE.md` says "see `src/old_api.py`" but the file was moved to `src/api/v1.py` |
| "Don't read" list | For every path, check it still exists (stale entries for deleted directories are harmless but noise) | `CLAUDE.md` lists `legacy/` as don't-read but `legacy/` was deleted 6 months ago |
| Named conventions (tabs vs spaces, etc.) | Sample a handful of files, check compliance | `CLAUDE.md` says "use tabs" but 90% of files use spaces |
| External dependencies named | Check `package.json` / `requirements.txt` / etc. | `CLAUDE.md` says "we use Firebase" but `package.json` has `@supabase/supabase-js` |

### Reporting format

Group findings by **severity**, not by section:

```
### Stale facts in CLAUDE.md

⚠️ High confidence:
- Line 23: "Run `npm test`" — no `test` script in package.json
- Line 47: "See src/old_api.py" — file does not exist (closest match: src/api/v1.py)

⚠️ Medium confidence:
- Line 12: "React 17" — package.json shows react ^19.0.0
- Line 31: "Use tabs" — sampled 10 files, 9 use spaces

ℹ️ Low confidence / noise:
- Line 58: "Don't read legacy/" — legacy/ directory no longer exists (harmless)
```

### How to propose fixes

For each finding, ask **per-block** not **per-file**. The user may want to fix some and keep others. The protocol:

1. Present the list above.
2. Ask: "Which of these do you want me to fix? Reply with numbers (e.g. 1, 2) or 'all' or 'none'."
3. For each accepted fix, show the exact diff: old line → new line.
4. Ask for final confirmation on the combined diff.
5. Only then write.

**Never**:

- Never write the whole file — only edit the specific lines.
- Never auto-fix a medium or low confidence finding without showing the diff first.
- Never fix a "don't read" entry for a deleted directory silently — it's harmless and the user may be keeping it as a historical marker.

---

## Diff presentation rules

Whether scaffolding or auditing, diffs should be presented as unified diffs in the chat, clearly labeled:

```
--- CLAUDE.md (current)
+++ CLAUDE.md (proposed)
@@ -23,1 +23,1 @@
-Run `npm test` to run the test suite.
+Run `npm run check` to run the test suite.
```

For a full scaffold where the original file is empty, just show the full proposed content as a code block with the header "**Proposed `CLAUDE.md`:**" and ask for confirmation.

---

## What janitor-claude NEVER does to CLAUDE.md

- **Never overwrites an existing file wholesale.** Edit specific lines or switch to audit mode.
- **Never writes without an explicit "write it" / "yes" / "apply" response.** Ambiguous responses get a re-ask.
- **Never writes to `CLAUDE.md` in a parent directory** unless the user explicitly named that file. A `CLAUDE.md` inside a sub-repo is scoped to that sub-repo.
- **Never generates a `CLAUDE.md` over 100 lines.** If the auto-detected content plus user answers push past 100, trim — `CLAUDE.md` loaded on every prompt; every line costs tokens.
- **Never copies content from another project's `CLAUDE.md`.** Every file is written from this repo's current state. No templates-from-memory.
- **Never commits the file.** Write it to disk, tell the user "I wrote it, review it with `git diff CLAUDE.md` and commit when you're happy." Janitor does not run `git add` or `git commit`.
