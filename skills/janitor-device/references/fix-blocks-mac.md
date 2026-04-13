# macOS fix blocks

**Last verified:** 2026-04 — update this date when you revise the fix recipes. macOS internals change between major versions; a fix that worked on macOS 14 may need adjustment on macOS 16.

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

CleanMyMac registers its services dynamically, so the removal order matters. This block is reversible up to step 2 (empty the Trash to commit).

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

# 4. Delete residue (prefs, caches, logs, HTTP cookies)
# Only after confirming the apps are in Trash. This step is not reversible.
find ~/Library \( -iname "*macpaw*" -o -iname "*cleanmymac*" \) -exec rm -rf {} + 2>/dev/null
```

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

## Quirks to know about

**zsh errors on empty globs.** `/path/*pattern*` that matches nothing will return exit code 1 with "no matches found", which can cancel sibling parallel tool calls. Either use `2>/dev/null`, check the exit code, or wrap in a shell function that tolerates empty matches.

**`find` + `mv` or `find` + `rm` can fail mid-traversal** when a parent directory is moved out from under the iteration. If the first pass errors on some items, run a second pass or, for known-safe garbage like app residue after the app is already trashed, use `find ... -exec rm -rf {} +`.

**Sudo should never run silently.** Give the user a block to paste themselves. Trust is more important than speed.
