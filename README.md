# janitor

**A Claude Code plugin for cleaning up slow machines and messy Claude Code sessions.**
Two skills. No telemetry. No malware. No $40/year. No menu bar icon that somehow uses 43% CPU to remind you your Mac is dirty.

```
> my mac is slow
janitor-device: running diagnostics...

## What's slowing your Mac
1. Adobe Creative Cloud (247% CPU combined) — stuck in an updater loop,
   has been since Tuesday, appears to be fighting itself
2. CleanMyMac Menu (43% CPU) — actively cleaning nothing, using
   enough electricity to light a small room
3. Low Power Mode is ON — has been since last week, which explains
   roughly everything

## The plan
I can fix these automatically if you say "go ahead":
- Kill Adobe (will respawn; use the sudo block below to kill it permanently)
- Nuke CleanMyMac (ironic, I know)

Needs your password (copy-paste block provided, read before pasting):
- Permanent Adobe launch agent disable

You do this manually:
- Toggle Low Power Mode off in System Settings > Battery
  (I can't touch that menu. Apple says so.)
```

---

## The two skills

| Skill | Trigger phrases | What it does |
|---|---|---|
| [`/janitor-device`](skills/janitor-device/SKILL.md) | *"my mac is slow"*, *"my pc is laggy"*, *"clean up my laptop"*, *"fans won't shut up"*, *"why is my battery dying in two hours"* | Diagnoses your Mac or Windows machine, identifies the 3–5 villains slowing it down, fixes what's safe, hands you copy-paste blocks for anything that needs sudo or admin. Cross-platform. |
| [`/janitor-claude`](skills/janitor-claude/SKILL.md) | *"clean up my session"*, *"audit my CLAUDE.md"*, *"find broken wiki-links"*, *"tidy this directory"*, *"Claude keeps re-reading the same files"* | Walks your current Claude Code working directory, finds orphaned scratchpads, broken wiki-links, missing or stale `CLAUDE.md`, oversized files getting re-read on every turn, and token-waste patterns. Read-only by default. |

Both skills follow the same five-phase loop: **diagnose → identify villains → present and ask → fix → verify with a before/after table and (usually) a closing analogy about a haunted house or a dysfunctional orchestra.** You can invoke them as slash commands or just describe your problem in natural language. Janitor is fluent in complaint.

---

## Install

### From the plugin marketplace (recommended)

```
/plugin marketplace add https://github.com/ArshiaEcho/janitor
/plugin install janitor
```

Then **fully quit and relaunch Claude Code.** Not `/clear`. Not `⌘R`. A full quit. Skills are discovered at session start, and `/clear` doesn't count as a start. This is the single most common "it doesn't work" report, and it's always this.

### From a local clone (manual)

```bash
git clone https://github.com/ArshiaEcho/janitor.git ~/.claude/plugins/janitor
```

Then, yes, fully restart Claude Code. (Sorry. We tried.)

### For development (symlink so edits propagate)

```bash
git clone https://github.com/ArshiaEcho/janitor.git ~/Code/janitor
ln -s ~/Code/janitor ~/.claude/plugins/janitor
```

Restart Claude Code, then `/janitor-device` and `/janitor-claude` should appear in autocomplete. If they don't, see Troubleshooting below.

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
