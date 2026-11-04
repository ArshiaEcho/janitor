# macOS fix blocks

**Last verified:** 2026-11 — update this date when you revise the fix recipes. Checked against macOS 26 Tahoe and macOS 27. macOS internals change between major versions; re-check launchd labels and paths after each one.

Load this file when the user has approved fixes on a Mac. Every sudo block is given to the user as plaintext — they paste it themselves. The skill never runs sudo directly.

---

## Rule 1 — Disable watchdogs BEFORE killing processes

Many slow-Mac villains (Adobe, CleanMyMac) have watchdog systems that respawn killed children. If you kill the process first, it comes back within seconds. Correct sequence:

1. Disable the launch agent / bootout the launchd label
2. Move the app bundle to Trash (for dynamically-registered services)
3. Kill the process
4. Verify it stays dead

---

## Killing runaway processes

```bash
# By name (fastest for Adobe and similar)
killall "Adobe Desktop Service" "Creative Cloud" "AdobeIPCBroker" 2>&1

# By PID (for stubborn stragglers)
kill -9 <PID>

# By pattern
pkill -9 -f "macpaw.CleanMyMac"
```

**Gotcha**: macOS `pgrep` does NOT support the `-E` flag (extended regex) — unlike Linux. Use multiple `pgrep` calls or pipe through `grep`:

```bash
# WRONG (fails on macOS):
pgrep -E "adobe|macpaw"

# RIGHT:
pgrep -fl adobe
pgrep -fl macpaw
```

---

## Disabling launchd agents — three types

### Type A: user-level plist file (most common, no sudo needed)
```bash
launchctl bootout gui/$UID/<label> 2>/dev/null
mv ~/Library/LaunchAgents/<name>.plist{,.disabled}
```

### Type B: system-level plist file (requires sudo — give user a copy-paste block)
```bash
sudo launchctl bootout system /Library/LaunchDaemons/<file>.plist
sudo mv /Library/LaunchDaemons/<file>.plist{,.disabled}
```

### Type C: dynamically registered, no plist file exists
Apps using `SMAppService` or `launchctl submit` register services directly with launchd. `launchctl list | grep -i <app>` will show them, but `ls ~/Library/LaunchAgents/` won't find anything. For these, bootout the label AND move the app bundle so the service can't re-register:

```bash
launchctl bootout gui/$UID/<label>
mv "/Applications/<App Name>.app" ~/.Trash/
```

---

## The permanent Adobe kill

Give this block to the user verbatim. Fully reversible: rename `.disabled` back to `.plist` to restore.

```bash
sudo launchctl bootout system /Library/LaunchDaemons/com.adobe.ARMDC.Communicator.plist 2>/dev/null
sudo launchctl bootout system /Library/LaunchDaemons/com.adobe.ARMDC.SMJobBlessHelper.plist 2>/dev/null
sudo launchctl bootout system /Library/LaunchDaemons/com.adobe.acc.installer.v2.plist 2>/dev/null
sudo launchctl bootout system /Library/LaunchDaemons/com.adobe.agsservice.plist 2>/dev/null
sudo mv /Library/LaunchAgents/com.adobe.AdobeCreativeCloud.plist{,.disabled}
sudo mv /Library/LaunchAgents/com.adobe.AdobeDesktopService.plist{,.disabled}
sudo mv /Library/LaunchAgents/com.adobe.GC.Invoker-1.0.plist{,.disabled}
sudo mv /Library/LaunchDaemons/com.adobe.ARMDC.Communicator.plist{,.disabled}
sudo mv /Library/LaunchDaemons/com.adobe.ARMDC.SMJobBlessHelper.plist{,.disabled}
sudo mv /Library/LaunchDaemons/com.adobe.acc.installer.v2.plist{,.disabled}
sudo mv /Library/LaunchDaemons/com.adobe.agsservice.plist{,.disabled}
```

---

## The full CleanMyMac / MacPaw nuke sequence

CleanMyMac registers its services dynamically, so the removal order matters. Every step is reversible until the user empties the Trash.

```bash
# 1. Boot out all 4 labels (handles both CleanMyMac X/4 and CleanMyMac 5)
for label in com.macpaw.CleanMyMac4.HealthMonitor com.macpaw.CleanMyMac4.Menu com.macpaw.CleanMyMac5.HealthMonitor com.macpaw.CleanMyMac5.Menu; do
  launchctl bootout gui/$UID/$label 2>&1
done

# 2. Move app bundles to Trash BEFORE killing, so the watchdog can't find its binary
mv "/Applications/CleanMyMac X.app" ~/.Trash/ 2>/dev/null
mv "/Applications/CleanMyMac_5.app" ~/.Trash/ 2>/dev/null

# 3. Kill any remaining processes
pkill -9 -f "macpaw.CleanMyMac" 2>/dev/null

# 4. Residue (prefs, caches, logs, HTTP cookies): LIST it first, show the user
find ~/Library -maxdepth 3 \( -iname "*macpaw*" -o -iname "*cleanmymac*" \) -print 2>/dev/null

# 5. After a yes, move each listed item to Trash (recoverable until Trash is emptied)
mv "<path from the list>" ~/.Trash/
```

Do not batch step 5 with `find -exec`. Moving a parent folder out from under `find` mid-traversal makes it error, and the user should see each path go.

---

## Orphaned Playwright / MCP browser cleanup

Safe, idempotent, instantly reversible (the orphans will get recreated next time Playwright runs if needed).

```bash
# See what's orphaned first
ps ax | grep -i 'mcp-chrome\|ms-playwright' | grep -v grep

# Kill them all
pkill -9 -f "ms-playwright/mcp-chrome" 2>/dev/null

# Verify none remain
ps ax | grep -i 'mcp-chrome' | grep -v grep || echo "all clean"
```

---

## Cleaning up Downloads bloat (safe mode)

Always move to Trash, never `rm`, so the user can recover:

```bash
# Find large files older than 30 days
find ~/Downloads -type f -size +500M -mtime +30 -print

# Show the list to the user FIRST, get confirmation, then move to Trash
mv <file> ~/.Trash/
```

Common nuke-on-sight patterns:
- `DaVinci_Resolve_*.zip`, `DaVinci_Resolve_*.dmg`
- `Xcode_*.xip`
- Old iOS device backups (`*.ipsw`)
- Duplicated zips/dmgs with version numbers (user rarely needs more than the latest)

---

## Spotlight rebuild (macOS 26 / 27, only after ~72h of `mds_stores` / `corespotlightd` pinned)

Read-only check first:
```bash
mdutil -sa
```

Give this block to the user. It erases and rebuilds the Spotlight index for the startup disk. No files are touched; search results are incomplete for a few hours while it rebuilds, and CPU will be high during that time (that's expected).
```bash
sudo mdutil -E /
```

Gentler alternative with no terminal: System Settings → Spotlight → Search Privacy, add big folders that don't need searching (dev folders, a video archive drive).

---

## Liquid Glass / WindowServer (GUI only, all reversible)

You do these manually:
1. System Settings → Accessibility → Display → turn on **Reduce Transparency** (biggest single win)
2. Same pane → **Reduce Motion** (optional)
3. macOS 26.1+: System Settings → Appearance → choose the **Tinted** Liquid Glass style
4. Update Electron apps (Slack, Discord, VS Code, Notion, etc.). Builds from before October 2025 had a GPU slowdown bug on Tahoe

Turn any of these back off the same way.

---

## `dasd` pinned for days (macOS 27.0.x, last resort)

Only after: the latest macOS point release is installed, a restart didn't help, and `dasd` is still at 90%+ for 24 hours.

```bash
# Confirm first
ps -axo pid,%cpu,etime,command | grep '[d]asd'
```

Single-source workaround (OSXDaily, October 2026): reset the PowerLog background-processing database. Janitor's version **renames instead of deleting**, so it is reversible. Give the user this block, then they restart when convenient:

```bash
D=/private/var/db/powerlog/Library/PerfPowerTelemetry/BackgroundProcessing
sudo mv "$D/CurrentBackgroundProcessingDB.BGSQL" "$D/CurrentBackgroundProcessingDB.BGSQL.disabled"
sudo mv "$D/CurrentBackgroundProcessingDB.BGSQL-wal" "$D/CurrentBackgroundProcessingDB.BGSQL-wal.disabled"
sudo mv "$D/CurrentBackgroundProcessingDB.BGSQL-shm" "$D/CurrentBackgroundProcessingDB.BGSQL-shm.disabled"
```

To undo: rename the `.disabled` files back (after moving aside any new files macOS created). This is outside `/System`, so SIP is not involved. Tell the user plainly it's a community workaround, not an Apple fix, and that a Time Machine backup first is wise.

---

## Developer disk hogs (macOS)

Measure first with the read-only commands in `macos-villains.md`, show the size table, get a yes per row.

### Skill may do these itself after a yes (reversible moves to Trash)

```bash
# Quit Xcode first. DerivedData is build output; Xcode rebuilds it on next build.
mv ~/Library/Developer/Xcode/DerivedData ~/.Trash/DerivedData-$(date +%Y%m%d-%H%M)

# Old DeviceSupport folders: list, then move the versions the user no longer has devices on
ls ~/Library/Developer/Xcode/iOS\ DeviceSupport/
mv ~/Library/Developer/Xcode/iOS\ DeviceSupport/<old version folder> ~/.Trash/
```

Never touch `~/Library/Developer/Xcode/Archives` without the user naming the exact archive; those are needed to symbolicate crash reports for shipped builds.

### User-run blocks (each tool's own documented clean command)

```bash
# Simulators whose runtime is no longer installed (device records only)
xcrun simctl delete unavailable

# Simulator runtimes: list, then delete ONE the user picked (frees several GB each)
xcrun simctl runtime list
xcrun simctl runtime delete <runtime identifier from the list>

# Homebrew: dry run first, then clean old versions and the download cache
brew cleanup -n
brew cleanup --prune=all

# npm
npm cache verify
npm cache clean --force

# pnpm (only packages no project references)
pnpm store prune

# Yarn 1
yarn cache clean

# pip
pip cache purge

# uv (prune is the safe one; clean empties everything)
uv cache prune
uv cache clean
```

Close Xcode and Simulator before deleting runtimes. If `simctl runtime delete` says no matching runtime but the disk space is still gone, it's an orphan Apple's tools can't see; if it's under `/System/Library/AssetsV2` it's SIP-protected. Report it and stop.

### AI models — per-item yes, never bulk

```bash
# Ollama
ollama list
ollama rm <model:tag>

# Hugging Face hub cache: list, dry-run, then one repo at a time
hf cache ls
hf cache rm <repo-id> --dry-run
hf cache rm <repo-id>
```

LM Studio: My Models tab → model menu → Delete. Older Hugging Face installs have `huggingface-cli scan-cache` / `delete-cache` instead of `hf cache`; check `hf cache --help` first.

### `node_modules` — report only. Docker — out of scope.

Show inactive projects with sizes and let the user handle them. For Docker, one line: "Docker's disk image, images and build cache are Docker's to manage; Janitor doesn't touch them."

---

## Quirks to know about

**zsh errors on empty globs.** `/path/*pattern*` that matches nothing will return exit code 1 with "no matches found", which can cancel sibling parallel tool calls. Either use `2>/dev/null`, check the exit code, or wrap in a shell function that tolerates empty matches.

**`find` + `mv` or `find` + `rm` can fail mid-traversal** when a parent directory is moved out from under the iteration. If the first pass errors on some items, list first with `find ... -print`, then move each path to `~/.Trash/` individually. Janitor never uses `rm -rf` on user files, residue included.

**Sudo should never run silently.** Give the user a block to paste themselves. Trust is more important than speed.
