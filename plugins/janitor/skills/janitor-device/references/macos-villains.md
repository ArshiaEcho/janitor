# macOS villain catalog

**Last verified:** 2026-11 — update this date when you revise the catalog. Villains come and go; a list that's three years stale will flag things that aren't problems anymore and miss new ones. See the Contributing section in the README for the update process.

Load this file when the user's machine is a Mac. These are the actual common causes of slow Macs in the real world, ranked by likelihood.

**Versions in the wild (late 2026):** macOS 27 (shipped fall 2026; 27.0.x point releases out by late October) and macOS 26 Tahoe are what most people run. `sw_vers` tells you which. Several entries below are version-specific; the tag in each heading says so.

---

## Tier 1 — Almost always the problem

### Post-upgrade settling (macOS 26 and 27) — check this FIRST

- If `sw_vers` shows a major version installed in the last ~3 days, most "my Mac got slow" is the Mac doing its homework: Spotlight reindexing (`mds`, `mds_stores`, `mdworker_shared`, `corespotlightd`), Photos analysis (`mediaanalysisd`, `photoanalysisd`), iCloud resync (`bird`, `fileproviderd`), and Apple Intelligence model downloads.
- Ask when they upgraded. Janitor's fix here is a schedule, not a command: leave it plugged in, awake and idle (overnight is ideal) for a day or two, then re-measure.
- It becomes a villain when one of these stays hot **after ~72 hours**. Then go to the specific entries in Tier 2.

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

### Spotlight stuck reindexing (macOS 26 and 27)

- `mds_stores` and/or `corespotlightd` at 40%+ for days, not hours. Some Tahoe users report a CoreSpotlight loop that never finishes (user reports, not an Apple-confirmed bug).
- Read-only check: `mdutil -sa`.
- Fixes, gentlest first: install the latest point release (user does it in Software Update); exclude big folders in System Settings → Spotlight (Search Privacy); rebuild the index with the user-run sudo block in `fix-blocks-mac.md`. Search is incomplete for a few hours afterwards, nothing is lost.

### Photos / media analysis (`mediaanalysisd`, `photoanalysisd`)

- Apple's on-device photo and video analysis (faces, objects, scene search, Apple Intelligence features). Large libraries keep it busy for days after an upgrade or a big import. Reported overheating MacBook Pros on Tahoe.
- No disable switch and nothing to kill (it respawns, and it's doing real work). The fix is time: plugged in, awake, idle. If it is still hot after a week, it's worth an Apple Feedback report.
- Observation only. Never touch its databases in `~/Library/Containers/com.apple.mediaanalysisd`.

### WindowServer and Liquid Glass (macOS 26 Tahoe and later)

- `WindowServer` is the compositor. Tahoe's Liquid Glass transparency costs GPU, more so with multiple or high-refresh external displays, lots of open windows, and on base M1/M2 machines.
- Reversible fixes, all in System Settings: Accessibility → Display → **Reduce Transparency** (biggest effect), Accessibility → Display → Reduce Motion; on 26.1+ Appearance offers a more opaque **Tinted** Liquid Glass style. Some third-party apps honour these late.
- Also check Electron apps (Slack, Discord, VS Code, Notion and friends): versions from before October 2025 had a bug that clashed with Tahoe's graphics stack and slowed the whole Mac. Updating those apps fixed it.

### Apple Intelligence disk usage (macOS 26 and 27)

- macOS 26: Apple says up to ~7 GB; reviewers saw ~11 GB. It can be turned off in System Settings → Apple Intelligence & Siri.
- macOS 27: the larger on-device model downloads automatically after upgrade. Apple states up to 14 GB on M3-or-later Macs with 12 GB+ memory and up to 8 GB on others; MacRumors, Ars Technica and Reddit users measured 14 to 30 GB. macOS 27 removed the single off switch, so it can't be prevented from downloading.
- Where to see it: System Settings → General → Storage → (i) next to macOS.
- Janitor **reports** this and moves on. Never touch `/System/Library/AssetsV2` or anything under `/System` (SIP-protected, and correctly so), and do not recommend third-party "remove Apple Intelligence" tools; they modify system assets.
- On a tight disk the honest advice is "this space is the OS now; free it elsewhere" (Downloads, dev caches, old simulators).

### Time Machine (`backupd`)

- First backup to a new disk, or the first after an upgrade, can run for hours and make everything feel sticky.
- Read-only: `tmutil status` (look for `Running = 1` and the percentage).
- Fix: let it finish, or the user clicks Skip This Backup in the menu-bar Time Machine icon. Never disable Time Machine for speed.

### iCloud Drive / File Provider churn

- Symptoms: `fileproviderd` + `bird` + `Finder` all hot simultaneously (20-30% CPU each); on 26/27 this is also normal for a day or so after an upgrade while iCloud resyncs
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

- **`dasd` pinned at 90-100% for days (macOS 27.0.x).** `dasd` is the background-task scheduler. One detailed October 2026 report (OSXDaily, 27.0.1) traced it to its PowerLog background-processing database; another report shows `dasd` and `appstoreagent` spiking around midnight. Apple hasn't published a known issue. First fix is the latest point release. Only if it's still pinned for 24h+ after that, the rename-not-delete block in `fix-blocks-mac.md` is a last resort.
- Orphaned launchd agents from uninstalled apps in `~/Library/LaunchAgents/`
- Unused duplicate browsers (Arc, Brave, Edge, Firefox, Opera) — check last-access with `stat -f "%Sa" /Applications/<browser>.app`
- Massive `~/Library/Caches/` subdirectories from infrequently-used apps
- 17+ Time Machine local snapshots — normal (macOS rotates them), but delays disk-space reclamation for up to 24h after you delete files
- Homebrew packages deeply outdated (`brew outdated`) — hygiene, not a speed issue on its own
- `nsurlsessiond` high network/CPU = iCloud Photos or Backup upload in progress

---

## Developer disk hogs (macOS)

A modern big win: on a developer's Mac, caches and toolchains often outweigh everything in Downloads. Rules: measure with read-only commands first, show the table, and then

- **reversible moves** (DerivedData, old DeviceSupport folders) the skill can do itself after a yes, into `~/.Trash/`
- **each tool's own clean command** is a block the user runs
- **AI models** are never touched without a per-item yes
- **`node_modules`** is report-only
- **Docker is out of scope.** Docker Desktop's disk image, images, volumes and build cache belong to Docker's own tooling. Janitor doesn't measure or clean them, and says so in one line.

| Hog | Measure (read-only) | Notes |
|---|---|---|
| Xcode DerivedData | `du -sh ~/Library/Developer/Xcode/DerivedData` | Build products only. Xcode rebuilds it. Often 10-50 GB |
| Xcode Archives | `du -sh ~/Library/Developer/Xcode/Archives` | **Report only.** Needed to symbolicate crash reports for shipped builds |
| iOS/watchOS DeviceSupport | `du -sh ~/Library/Developer/Xcode/*DeviceSupport/* 2>/dev/null` | One folder per OS version a device was plugged in with. Old versions are safe to trash per item |
| Simulator devices | `du -sh ~/Library/Developer/CoreSimulator/Devices` and `xcrun simctl list devices unavailable` | Devices whose runtime is gone are dead weight |
| Simulator runtimes | `xcrun simctl runtime list` | Each runtime is several GB in `/Library/Developer/CoreSimulator/Volumes`. Removing through Xcode → Settings → Components can leave the disk image behind; `simctl runtime delete` is the reliable route |
| Homebrew cache | `du -sh "$(brew --cache)"` and `brew cleanup -n` | `-n` is a dry run: lists what would go |
| npm cache | `du -sh "$(npm config get cache)"` | Usually `~/.npm` |
| pnpm store | `du -sh "$(pnpm store path)"` | |
| Yarn cache | `du -sh "$(yarn cache dir 2>/dev/null)"` | Yarn 1 |
| pip cache | `du -sh "$(pip cache dir)"` | Usually `~/Library/Caches/pip` |
| uv cache | `du -sh "$(uv cache dir)"` | Default `~/.cache/uv` |
| Hugging Face hub | `du -sh ~/.cache/huggingface/hub` and `hf cache ls` | Models. Report only |
| Ollama models | `du -sh ~/.ollama/models` and `ollama list` | Models. Report only. `OLLAMA_MODELS` can relocate it |
| LM Studio models | `du -sh ~/.lmstudio/models` | Models. Report only. My Models tab shows the real path |
| Old `node_modules` | `find ~ -maxdepth 6 -type d -name node_modules -prune -mtime +90 2>/dev/null \| head -30`, then `du -sh` each | **Report only.** The user decides per project |

Orphaned simulator runtimes that `simctl` can no longer see sometimes sit under `/System/Library/AssetsV2`. That's SIP territory: report the size, suggest the user raises it with Apple, never touch it.

Fix blocks for every row are in `fix-blocks-mac.md`.

---

## What to watch for in diagnostic output

### CPU section
- Any process over 40% CPU that isn't something the user is actively using = suspect
- Multiple related processes (e.g. `Adobe*`, `com.macpaw.CleanMyMac*`) often sum to 200%+
- `kernel_task` > 30% = thermal throttling, the Mac is overheating
- `WindowServer` > 30% = too many windows, Liquid Glass transparency on 26+, external displays, or an outdated Electron app
- `sandboxd` spikes are often transient — re-check before acting
- `mds`, `mds_stores`, `mdworker_shared`, `corespotlightd` high = Spotlight reindexing. Normal for up to a day or two after an upgrade; a villain after ~72 hours
- `mediaanalysisd` / `photoanalysisd` high = Photos analysis. Same timeline, observation only
- `dasd` > 90% for hours on macOS 27 = see Tier 3

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
| `WindowServer` > 30% CPU | Liquid Glass / too many windows / old Electron app | Reduce Transparency, update Electron apps |
| `fileproviderd` + `bird` hot | iCloud Drive syncing | Wait, or pause iCloud |
| `mds_stores`, `corespotlightd` high CPU | Spotlight reindexing | Wait up to ~72h after an upgrade, then rebuild |
| `mediaanalysisd`, `photoanalysisd` hot | Photos analysis after upgrade/import | Plugged in + idle, give it time |
| `backupd` hot | Time Machine backup running | `tmutil status` |
| `dasd` pinned for days (27.x) | Background scheduler bug | Update, then last-resort block |
| Disk suddenly ~10-30 GB fuller after upgrade | Apple Intelligence models | Settings → General → Storage → macOS (i) |
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
- No Spotlight / Photos analysis process still pinned 72h+ after an upgrade
- Dev caches reported, and trimmed where the user said yes
- Adobe / CleanMyMac / MacKeeper / other "cleaners": not installed
