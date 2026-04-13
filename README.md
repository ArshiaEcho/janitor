# janitor

**Janitor is a Claude Code plugin that cleans up two things for you: your computer, and your Claude Code working directory. It diagnoses what's wrong, tells you in plain English, asks your permission, then fixes it. No telemetry. No nagging. No menu bar icon that somehow uses 43% CPU to remind you your Mac is dirty.**

> 🧹 *"Janitor here. What are we cleaning up today?"*

Janitor is a warm, cheerful, unfazed character who shows up when you call, tidies what needs tidying, then leaves cleanly. You can come back any time — Janitor doesn't mind the repeat visits.

---

## What janitor actually does

Janitor ships two skills. You install the plugin once, and both become available in any Claude Code session.

### 🧹 `janitor-device` — cleans up your computer

Tell Claude your machine feels slow, or that the fans won't stop, or that the battery is dying in two hours, and `janitor-device` will:

1. **Diagnose** the machine with a handful of read-only shell commands (top CPU, top memory, load average, thermal state, disk space, battery health, launch agents, background services).
2. **Identify the 3–5 specific background processes actually causing the slowdown** — not generic advice. Real names, real CPU percentages, real explanations for why they're misbehaving.
3. **Present a plan** separated into three buckets:
   - ✅ Things janitor can fix automatically (with your permission)
   - 🔧 Things that need your password — handed to you as a plaintext copy-paste block you read before running
   - 📋 Things you need to do manually (e.g. toggle a setting janitor can't touch)
4. **Fix** only what you approved. Files go to Trash, disabled services get renamed to `.disabled`, everything is reversible.
5. **Verify** the fix worked by re-running the diagnostics and showing you a before/after table.

Works on **macOS and Windows**. Detects the OS automatically and loads the right villain catalog. Linux is planned for v0.2.

### 🧹 `janitor-claude` — cleans up your Claude Code working directory

Tell Claude that your repo is a mess, or that Claude keeps re-reading the same files, or that your `CLAUDE.md` is stale, and `janitor-claude` will:

1. **Walk your current working directory read-only** — no writes, no git mutations, no surprises.
2. **Identify the clutter** — missing or stale `CLAUDE.md`, orphaned scratchpad files from six weeks ago, oversized files in the read path wasting tokens on every turn, broken `[[wiki-links]]` in markdown, `.DS_Store` files, `__pycache__` directories, tracked build artifacts, and suspected secrets (reported as `file:line` only, never printed to chat).
3. **Ask permission per fix** — nothing is ever auto-deleted. `.DS_Store` cleanup is one confirmation; everything else is per-item.
4. **Fix** what you approved. Files go to Trash, never to `rm`. `CLAUDE.md` edits are shown as diffs before writing. Broken wiki-links are never silently rewritten.
5. **Verify** with a before/after count table.

Works on any Claude Code working directory — code repos, Obsidian vaults, docs folders, wherever.

---

## What janitor doesn't do

- **Doesn't run in the background.** It only does anything when you invoke it. No daemon, no scheduled scan, no "let me silently check in on your Mac every 6 hours."
- **Doesn't phone home.** No telemetry, no analytics, no version checks, no auto-updates, no "anonymized usage statistics." Completely offline.
- **Doesn't delete anything automatically.** Files go to Trash (macOS) or Recycle Bin (Windows). Config changes are reversible by renaming `.disabled` back. You can recover anything.
- **Doesn't need your password silently.** Any command that needs `sudo` or admin is handed to you as a plaintext copy-paste block. You read it, you paste it. The skill never enters an elevated context on its own.
- **Doesn't run destructive git.** Ever. No `git rm`, no `git commit`, no `git reset --hard`. Janitor reads git state; it doesn't change it.
- **Doesn't cost $40/year.** Or $40. Or $4. It's MIT-licensed and free.

The full non-negotiable safety rules are documented in [the "What it does NOT do" section below](#what-it-does-not-do) and enforced in the skill instructions themselves on every invocation. Read them before installing. (Healthy paranoia is welcome here.)

---

## How to summon the skills

You never have to remember commands. Describe your problem in plain English and the right skill auto-triggers from the phrasing.

**For [`janitor-device`](plugins/janitor/skills/janitor-device/SKILL.md)**, any of these will do:
> *"my mac is slow"* · *"my pc is laggy"* · *"clean up my laptop"* · *"fans won't shut up"* · *"why is my battery dying in two hours"* · *"my machine is overheating"* · `/janitor-device`

**For [`janitor-claude`](plugins/janitor/skills/janitor-claude/SKILL.md)**, any of these will do:
> *"clean up my session"* · *"audit my CLAUDE.md"* · *"find broken wiki-links"* · *"tidy this directory"* · *"Claude keeps re-reading the same files"* · *"this repo is a mess"* · `/janitor-claude`

Both skills follow the same five-phase loop: **diagnose → identify villains → present and ask → fix → verify.** You're never surprised by what janitor did. Janitor is fluent in complaint — if you have a vague sense that something is wrong, describe the vague sense.

---

## Install

### Recommended: marketplace install (CLI)

```bash
claude plugin marketplace add https://github.com/ArshiaEcho/janitor
claude plugin install janitor
```

This registers janitor as a marketplace, then installs the plugin from it. Works in any Claude Code environment with the `claude plugin` CLI subcommand.

Then **fully quit and relaunch Claude Code.** Not `/clear`. Not `⌘R`. A full quit. Plugins are discovered at session start, and `/clear` doesn't count as a start. This is the single most common "it doesn't work" report, and it's always this.

### Interactive: `/plugin` from inside a Claude Code session

If your Claude Code build supports the `/plugin` slash command (most recent builds do), you can also do it interactively:

```
/plugin marketplace add https://github.com/ArshiaEcho/janitor
/plugin install janitor
```

Then fully quit and relaunch Claude Code.

### Verify

```bash
claude plugin list
```

You should see `janitor@janitor` in the list. If you don't, the install didn't take — see Troubleshooting below.

### For development (local clone, edits propagate)

```bash
git clone https://github.com/ArshiaEcho/janitor.git ~/Code/janitor
claude plugin marketplace add ~/Code/janitor
claude plugin install janitor
```

Now when you edit files in `~/Code/janitor`, they take effect on the next Claude Code restart. Use this if you want to hack on janitor itself.

---

## Quick start

**Fix a slow machine:**
```
> my mac is slow
```
or
```
> /janitor-device
```

**Clean up a messy Claude session:**
```
> clean up this directory
```
or
```
> /janitor-claude
```

Both skills diagnose first, show you a structured report, ask permission before changing anything, then verify the results. You never have to remember commands. You do have to read the sudo blocks before pasting them, but that's true of everything.

---

## What it does NOT do

This section exists because you should be skeptical of any tool that asks for permission to touch your machine. Every line below is a hard rule, enforced in the skill instructions themselves — not in a "please be good" disclaimer, but as non-negotiable rules the skill reads on every invocation.

- **No network calls.** Janitor never connects to the internet. No telemetry, no version checks, no analytics, no GitHub API pings, no auto-updates, no "anonymized usage statistics to help us improve." Completely offline. If you see it reach for the network, that's a bug — please file an issue.
- **No automatic deletion of your files.** Everything goes to Trash (macOS) or Recycle Bin (Windows) via OS-native mechanisms. You can recover anything that was moved. Yes, even the thing you're panicking about right now.
- **No silent sudo or admin commands.** Anything that needs your password is shown to you as a plaintext copy-paste block. You read it, you paste it, you run it. The skill never enters an elevated context on its own. This is the most important rule in the whole plugin and it's the one most likely to matter if something goes wrong.
- **No git mutations.** Janitor will never run `git rm`, `git commit`, `git push`, `git reset --hard`, `git branch -D`, `git clean`, or any state-changing git command. It reads `status`, `log`, `diff`, `branch -vv`. That's it. Your branches are safe, your uncommitted work is safe, your creative commit messages are safe.
- **No `CLAUDE.md` edits without a diff.** Janitor will never silently rewrite your `CLAUDE.md`. If you have one, it audits for staleness and shows a diff before touching a single line. If you don't, it asks five questions and scaffolds one — still shown as a diff before writing.
- **No obfuscated commands.** No base64, no `curl | bash`, no minified one-liners, no "just trust me and run this." Every command is plaintext and you can read it before execution. If you can't read shell, ask Claude what it does before pasting.
- **No malware-adjacent behavior.** Janitor uses only documented OS APIs. No kernel extensions, no boot config edits, no SIP or Gatekeeper changes, no Windows Defender disables. Real malware would love it if you disabled Defender. Janitor is not going to help with that. Janitor would like Defender to continue defending, thank you.
- **No wiki-link auto-rewrites.** Broken `[[links]]` in markdown are *reported*, never fixed silently. Forward-linking to a file you plan to create is a normal Obsidian workflow; janitor respects that instead of "helpfully" rewriting your notes while you sleep.
- **No secret leaking.** The directory scan flags potential API keys by `file:line` only. It never prints the matched string to the conversation, so your transcript doesn't accidentally log the key you were trying to protect. (If a key is already in git history, janitor will tell you to rotate it and use `gitleaks`. Editing the current file does nothing because git remembers.)
- **No rename operations.** Janitor won't rename your files even if you ask. Renames break wiki-links, break `git blame`, break Claude's memory of the repo, and break anything else that knew the old name. Out of scope on purpose.
- **May read `.claude/sessions/` transcripts if present.** This is the one thing janitor *reads* that isn't obvious from the name. `janitor-claude` can use transcript content to infer which files Claude re-reads most often, which is useful for token-waste recommendations. If that's not something you want touched, delete or move `.claude/sessions/` before running the skill. Transcript content stays local — it's read, not uploaded.
- **Fully open source.** Every line is in this repo. Read it before installing. Verify the commit hash if you're paranoid. (Healthy paranoia is welcome here.)

---

## Troubleshooting

**"The skills don't appear in autocomplete after I installed them."**
Fully quit Claude Code and relaunch it. Not `/clear`. Not `⌘R`. Cmd+Q, then reopen. Skills are discovered at session start — new ones don't appear mid-session. This is ~90% of all "it's broken" reports.

**"I'm on Linux."**
`janitor-device` currently supports macOS and Windows. Linux support is planned for v0.2, mostly because the Linux villain catalog is genuinely different (systemd services, snapd, tracker-miners, etc.) and deserves its own reference file rather than a half-hearted port. `janitor-claude` works fine on Linux today — it's filesystem-agnostic.

**"I'm on a work laptop with MDM / corporate device management."**
Be careful. Some of the things janitor wants to disable (OEM updaters, scheduled tasks, launch agents) may be managed by your IT team and will either refuse to disable or generate audit alerts. Run the skill, read the plan, and skip anything you don't recognize. When in doubt, ask IT before pasting a sudo block.

**"It suggested something and I'm not sure."**
Don't paste the block. Janitor's output is a recommendation, not a prescription. If anything feels wrong, say so — the skill is designed to explain its reasoning and back off on request.

**"It didn't find anything but my machine is still slow."**
Then the problem is probably not in janitor's villain catalog. Common culprits outside the catalog: a failing SSD, thermal throttling from dust in the vents, a BIOS/firmware issue, or a kernel panic loop. Janitor's `janitor-device` skill will tell you this explicitly if diagnostics come back clean — read its fallback section.

**"`janitor-claude` took forever on my 5,000-file Obsidian vault."**
This is a known limit. The broken-link audit builds an in-memory basename index once and processes all links against it, but the initial walk is still O(n) in vault size. A run on a large vault can take 30+ seconds. Not broken, just slow.

---

## Known limitations

Things janitor does *not* try to do, and probably shouldn't:

- **No GPU or graphics diagnostics.** "My game stutters" is out of scope — janitor looks at CPU/memory/disk, not shaders.
- **No server-side diagnosis.** If you SSH'd into a slow VPS and ran janitor, it'll detect the remote OS correctly but most of its villain catalog is desktop-flavored (launch agents, OEM bloat). Limited value on a headless server.
- **No Docker or VM cleanup.** Containers, images, and volumes have their own cleanup ecosystem (`docker system prune`, etc.) and janitor doesn't get involved.
- **No compile-time slowdowns.** "My Rust build takes 5 minutes" is a build-system problem, not a machine problem. Janitor won't help.
- **No "my internet is slow" diagnosis.** Network is a whole other thing. Janitor stays on the machine.
- **No code refactoring via `janitor-claude`.** It's about clutter, not code quality. It will not tell you your functions are too long. It has opinions but keeps them to itself.

---

## The funny part

The most popular paid Mac cleaner costs about $40/year and is itself frequently one of the worst slowdowns on the Macs of people who installed it specifically to make their Macs faster. It runs its own background daemons, its own menu bar helper, its own updater, and fights back aggressively when you try to kill it. It is the problem it claims to solve. It is a firefighter who started the fire, charged you for water, and then billed you monthly for a subscription to not-setting-more-fires.

Janitor is free, open source, respawns nothing, does not register a launchd agent named `JanitorMenuHelper.HealthMonitor`, and will never interrupt your work with a popup asking you to renew. Janitor will also never tell you your Mac has "342 issues" when it has maybe three, and one of them is Janitor's competitor.

A janitor built on top of a frontier AI model. The internet's most overqualified cleaning service. A system that can write a Shakespearean sonnet now also runs `find . -name .DS_Store` on your behalf. Your grandchildren will study this era and wonder what we were thinking. So do we, honestly. It's fine.

---

## How it's built

Two skills live under `skills/`, each following the same progressive-disclosure pattern:

- `SKILL.md` is short and loaded on every invocation. It contains the workflow, the safety rules, and pointers.
- `references/*.md` contain long-form content (villain catalogs, fix blocks, regexes) loaded only when needed — e.g., the macOS villain catalog is not loaded on a Windows machine, and vice versa.
- `assets/*` contain static templates the skill offers to users.

The cross-platform half of `janitor-device` detects the OS at the start of the workflow and routes to the right reference file. Mac and Windows share the philosophy, the phases, the report format, and the closing analogy — they only diverge at the command layer. You can read Mac first or Windows first; the structure is identical.

The `janitor-claude` skill treats a messy Claude Code working directory the same way `janitor-device` treats a slow machine: same five-phase loop, session-flavored villains (missing `CLAUDE.md`, orphaned scratchpads, broken wiki-links) instead of machine ones.

Villain catalogs carry a `last-verified` date in their frontmatter because the world changes — a villain that was a nightmare in 2026 might be fixed by 2028, and a new one will have taken its place. PRs to update the catalogs are the easiest path to a merged contribution.

---

## Contributing

Issues and PRs welcome. Every contribution must respect the non-negotiable rules:

- No network calls.
- No automatic deletion.
- No silent sudo.
- No git mutations.
- No obfuscation.
- No disabling Windows Defender. Seriously. Not even a little.

If you have a new villain to add — an OEM bloatware suite, a background service, a common Mac tool that ships with a misbehaving helper — open an issue with:

1. A detection command (shows the villain exists and is misbehaving)
2. A reversible fix recipe (disable, not delete; rename, not rm)
3. The OS and version you saw it on
4. Ideally, the CPU/memory percentage you saw it burn so future contributors can verify

That's the fastest path to a merged PR.

---

## License

[MIT](LICENSE).

## Acknowledgments

- [Anthropic](https://www.anthropic.com/) / Claude Code for the plugin and skills system that makes any of this possible.
- The `clean-your-mac` skill that this plugin's `janitor-device` half is built on top of.
- Every `AdobeIPCBroker` process that has ever burned 104% CPU at 3 AM for no reason. You are the reason this plugin exists. You are also, somehow, still running.
