# Changelog

All notable changes to the `janitor` plugin are documented in this file.

## [0.2.0] — Stratos branding + modern cruft detection

### Added
- **Stratos House AI brand identity.** New `assets/social-preview.png` (1280×640) built on the shared Stratos card system — dark stage, mint/gold palette, `STRATOS HOUSE AI` header, chip row — with a broom mark replacing the diamond logo as the product hero. The source `assets/og-source.html` is committed so the card is reproducible.
- **README rebrand.** Centered header block with `shields.io` badges (Claude Code Plugin / Platforms / MIT / by Stratos House AI) matching the sibling Stratos repos (`stratos-memory-stack`, `stratos-carousel-creator`).
- **New `janitor-claude` villains:**
  - **Tool & test caches** — `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.ipynb_checkpoints` detected and batch-cleaned to Trash like `__pycache__` (machine-generated, one confirmation).
  - **Committed `.env` files** — tracked dotenv files (excluding `.example`/`.sample`/`.template`) flagged as a credential leak. Report-only: path shown, contents never printed, with `git rm --cached` + gitignore + rotate-credentials guidance.
- **`obsidian` and `vault` keywords** added to `plugin.json` and `marketplace.json` for discoverability — `janitor-claude` explicitly supports Obsidian vaults.

### Changed
- **Plugin author → `Arshia Navabi` / `arshia@stratosagency.ai`** and **marketplace owner → `Stratos House AI`**, matching the other public Stratos plugins.
- Broadened the tracked-build-artifact detector to also catch `coverage/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.nuxt/`, and `venv/`.
- Villain-catalog `last-verified` date bumped to 2026-06.

## [0.1.1] — Personality and marketplace release

### Added
- **Marketplace manifest** (`.claude-plugin/marketplace.json`) so the repo can be installed directly via `claude plugin marketplace add https://github.com/ArshiaEcho/janitor`. Plugin files moved into `plugins/janitor/` to support the marketplace-root-vs-plugin-source split required by the schema.
- **Personality and voice section** in both `SKILL.md` files. Janitor now consistently opens with a warm greeting, frames findings as observational ("caught Adobe doing laps in the background"), and signs off with a line that invites the user to come back. Character is warm, cheerful, unfazed, and leaves cleanly.
- **Broom emoji (🧹)** as the visual anchor for Janitor across the README and skill output.

### Changed
- **README rewrite.** Opening replaced with a clear what-janitor-actually-does section (five concrete steps per skill) instead of a simulated session. Install instructions updated to use the `claude plugin` CLI subcommand as the primary path with a verify step. One-line character intro added under the title.
- **Softened the "always close with an analogy" rule** in both skills. The rule is now conditional ("when one lands naturally") so forced analogies don't ship. All 15 analogies in both skills remain in the catalog, just pitched differently.
- **Last-verified dates** added to all villain and fix-block catalogs (`macos-villains`, `windows-villains`, `fix-blocks-mac`, `fix-blocks-windows`, `session-villains`) so future contributors can maintain them over time.

### Fixed
- Removed three tracked-on-disk `.DS_Store` files from the repo. (A janitor plugin with `.DS_Store` files in its own tree was an embarrassment that `janitor-claude` would have found on first run.)

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
