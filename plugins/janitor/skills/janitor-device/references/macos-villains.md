# macOS villain catalog

**Last verified:** 2026-04 — update this date when you revise the catalog. Villains come and go; a list that's three years stale will flag things that aren't problems anymore and miss new ones. See the Contributing section in the README for the update process.

Load this file when the user's machine is a Mac. These are the actual common causes of slow Macs in the real world, ranked by likelihood.

---

## Tier 1 — Almost always the problem

### Adobe Creative Cloud background processes

- Process names: `AdobeIPCBroker`, `Adobe Desktop Service`, `Creative Cloud`, `Core Sync`, `CCLibrary Synchronizer`
- Can burn **200-400% CPU combined** in a stuck "updater loop" even when no Adobe app is open
- Has a watchdog called "vulcan" that **automatically respawns** killed processes
- Fix requires disabling launchd agents **before** killing the processes, otherwise they come right back
- See the permanent-kill sudo block in `fix-blocks-mac.md`

### CleanMyMac / MacPaw — the cruel irony

- A "cleaner" app that is often one of the biggest slowdowns on a Mac
- Runs `com.macpaw.CleanMyMac4.HealthMonitor`, `Menu`, and `Updater` background daemons
- **Often installed twice** — both CleanMyMac X (version 4) AND CleanMyMac 5 — check for both
- Registers its launchd services **dynamically** (via `SMAppService`), so there's **no plist file** in `~/Library/LaunchAgents/`. You cannot disable it by renaming a plist. You must use `launchctl bootout` on the label directly AND move the app bundle, otherwise it reattaches
- The Menu process fights back aggressively when killed, sometimes spiking to 100%+ CPU trying to re-register. Move the `.app` bundles to Trash first so the watchdog can't find its binary
- Full nuke sequence: see `fix-blocks-mac.md`

### Low Power Mode left on

- Check with `pmset -g | grep lowpowermode`
- On M-series, this throttles performance dramatically
- User must toggle off manually: System Settings → Battery → Low Power Mode → "Never" (or "Only on Battery")
- This is one of the most common "accidental" slowdowns: users enable it once for a flight and forget

---

## Tier 2 — Common secondary causes

### iCloud Drive / File Provider churn

- Symptoms: `fileproviderd` + `bird` + `Finder` all hot simultaneously (20-30% CPU each)
- Usually iCloud is stuck syncing a large folder, or there's a conflict
- `fileproviderd` also handles Dropbox, Google Drive, OneDrive — multiple cloud sync apps fighting over the same folder can trigger it
- Fix: pause iCloud temporarily, or identify the offending folder with `lsof` on the bird PID

### Discord running idle

- Can burn 40-60% CPU in the background even with no active conversation, especially with voice channels connected or animated-emoji-heavy servers open
- Check: `pgrep -fl Discord`
- Quitting Discord entirely (not just closing the window) is usually the fix

### Chrome with too many tabs

- Each renderer process uses ~80-150 MB. On a 16 GB Mac, 30+ tabs is a noticeable tax
- To see per-tab usage: in Chrome, `Window → Task Manager` (or Shift+Esc)
- Don't suggest deleting Chrome's cache to fix this — it just makes browsing slow for a day while the cache rebuilds

### Huge Downloads folder with old installers

- Check: `du -sh ~/Downloads && find ~/Downloads -type f -size +500M`
- Common offenders: DaVinci Resolve installers (people hoard every version), Xcode DMGs, iOS backups, video project exports
- A bloated Downloads folder slows the Mac in three places at once: Spotlight indexes it, Finder stats every file when the folder opens, and Time Machine snapshots include it

### Known Mac bloatware / malware-adjacent apps (treat same as CleanMyMac)

- `MacKeeper`, `Advanced Mac Cleaner`, `Smart Mac Care`, `Smart Mac Booster`, `Dr. Cleaner`, `Mac Cleaner Pro`, `CCleaner for Mac`
- Check: `ls /Applications/ | grep -iE "clean|keeper|booster|optimiz"`
- All of these should be removed the same way as CleanMyMac: bootout any launchd labels, trash the app bundle, then the residue after confirmation

### Orphaned Playwright / MCP browser sessions

- Pattern: multiple `Google Chrome Helper` or `chromium` processes with `mcp-chrome` or `ms-playwright` in the command line
- Cause: a prior Claude Code session called `browser_navigate` or similar and never called `browser_close`. The browser lives on until killed.
- Detection: `ps ax | grep -i 'mcp-chrome\|ms-playwright' | grep -v grep`
- Fix: `pkill -9 -f "ms-playwright/mcp-chrome"` — clean and idempotent

---

## Tier 3 — Less common but worth checking

- Orphaned launchd agents from uninstalled apps in `~/Library/LaunchAgents/`
- Unused duplicate browsers (Arc, Brave, Edge, Firefox, Opera) — check last-access with `stat -f "%Sa" /Applications/<browser>.app`
- Massive `~/Library/Caches/` subdirectories from infrequently-used apps
- Spotlight stuck reindexing (`mdutil -sa` shows status) — usually self-resolves in 15-60 minutes, observation only
- 17+ Time Machine local snapshots — normal (macOS rotates them), but delays disk-space reclamation for up to 24h after you delete files
- Homebrew packages deeply outdated (`brew outdated`) — hygiene, not a speed issue on its own
- `nsurlsessiond` high network/CPU = iCloud Photos or Backup upload in progress

---

## What to watch for in diagnostic output

### CPU section
- Any process over 40% CPU that isn't something the user is actively using = suspect
- Multiple related processes (e.g. `Adobe*`, `com.macpaw.CleanMyMac*`) often sum to 200%+
- `kernel_task` > 30% = thermal throttling, the Mac is overheating
- `WindowServer` > 30% = too many windows, broken display driver, or heavy GUI animation
- `sandboxd` spikes are often transient — re-check before acting
- `mds`, `mdworker` high = Spotlight reindexing, usually self-resolves in 15-60 min

### Memory section
- `Pages occupied by compressor` > 300K (~5 GB) = RAM under pressure, even if macOS isn't warning
- `Pages free` < 10K = genuinely out of RAM
- **Ignore cumulative counters** (`Swapouts`, `Swapins`): these never decrease until reboot. They reflect lifetime activity, not current health. Use compressor + free pages as your live signals.

### Load average
- Healthy on M-series: load average < (number of cores)
- The real health signal is **convergence**: 1-min, 5-min, and 15-min load averages all within ~10% of each other. Convergence = stable steady state. Divergence means spikes are still happening.

### Battery
- `Maximum Capacity` below 80% = genuinely aging hardware. Rare on anything under 3 years old.
- `Cycle Count` alone isn't a speed issue unless the battery capacity has dropped.

---

## Quick reference — what each symptom means

| Symptom | Likely cause | Quick check |
|---|---|---|
| `kernel_task` > 30% CPU | Thermal throttling (Mac is hot) | Close heavy apps, check airflow |
| `WindowServer` > 30% CPU | Too many windows / visual effects / display driver | Close windows, reduce transparency |
| `fileproviderd` + `bird` hot | iCloud Drive syncing | Wait, or pause iCloud |
| `mds`, `mdworker` high CPU | Spotlight reindexing | Wait 15-60 min, it self-resolves |
| `sandboxd` spike | Usually transient | Re-check twice before acting |
| `sharingd`, `rapportd` hot | AirDrop/Handoff stuck | Toggle Bluetooth |
| `nsurlsessiond` high net/CPU | iCloud Photos/Backup upload | Pause in Settings |
| Low Power Mode on | Accidental throttle | System Settings → Battery |
| `mcp-chrome` processes hot | Orphaned Playwright session | `pkill -9 -f ms-playwright/mcp-chrome` |

---

## Expected final state of a healthy M-series Mac

- Load average 1/5/15-min all < (cores / 2), and within 10% of each other
- Top CPU process is something the user is actively using (browser, IDE, creative tool)
- `Pages free` > 10,000
- `Pages occupied by compressor` < 300,000 (~5 GB)
- Low Power Mode off (when plugged in)
- No process > 40% CPU that isn't a user-facing app
- Chrome tab count < 30 ideal, < 50 tolerable
- Downloads folder < 5 GB
- Adobe / CleanMyMac / MacKeeper / other "cleaners": not installed
