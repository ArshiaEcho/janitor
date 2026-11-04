# Changelog

All notable changes to the `janitor` plugin are documented in this file.

## [0.3.0] - Up to date for November 2026, Linux, and the Altocue house README

### Added
- **Linux support for `janitor-device`.** New `linux-villains.md` and `fix-blocks-linux.md`: GNOME LocalSearch, snapd, software-centre loops, KDE Baloo, power profiles, journald size, old kernels and unused Flatpak runtimes. Distro, desktop and WSL detection in `SKILL.md`. Trash through `gio trash`, every elevated step as a block the user runs.
- **Developer disk hogs on all three systems.** Xcode DerivedData and old simulators, Homebrew, npm, pnpm, yarn, uv and pip caches, and Hugging Face, Ollama and LM Studio model folders, sized first. Models move only with a yes for each one. Docker stays out of scope.
- **macOS 26 and 27 villains.** Post-upgrade settling, stuck Spotlight, Photos analysis, Liquid Glass costs, Apple Intelligence disk use, Time Machine and `dasd` on 27.0.x.
- **Windows 11 25H2 and 26H2 villains.** The Copilot+ AI host, Copilot auto-start, Phone Link, Widgets, the new Teams client, NVIDIA App, and the WSL disk image as report only. A reversible Recall removal block.
- **Claude Code config hygiene for `janitor-claude`.** Overlapping or long CLAUDE.md, CLAUDE.local.md and AGENTS.md files, `@imports` to missing files, rules whose paths match nothing, settings drift, hooks and `.mcp.json` servers whose commands are missing, broken skill frontmatter, duplicate agents and commands, stale worktrees, and other AI tools' folders reported only.
- **Opt-in `~/.claude` check.** Sizes of transcripts, plugin cache and other user-level state. Transcripts are never read.
- **README images made in code** under `scripts/brand/`: logos and tiles, a chrome broom rendered in Blender, the banner, the flow diagram and the terminal GIF, rebuilt with `scripts/brand/build_assets.sh`. Geist fonts ship with their OFL licence.

### Changed
- **README rewritten in the Altocue house structure:** banner, badges, demo GIF, what it does, install, use, tool tiles, how it works, what it never does, cost, honest limits and what is not proven yet.
- **Nothing is removed outright any more.** The CleanMyMac residue step and the Windows search index now go to the Trash or are renamed, where they used `rm -rf` or deletion before.
- **`janitor-claude` no longer reads `.claude/sessions/`.** That folder is gone from Claude Code, and transcripts are now off limits.
- **Every catalog's "Last verified" date is 2026-11.**

### Removed
- `assets/og-source.html`, replaced by `scripts/brand/social.html`.
- **The `commands/` stubs.** They shared the skills' names, so `/janitor-device` and `/janitor-claude` loaded a one-line stub instead of the skill, and Claude went looking for the skill files on disk. Skills are slash commands on their own, so both names still work.
- **The plan now has a "Commands only you run" bucket** in `janitor-claude`, so `git rm --cached` is always handed to the user.

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
