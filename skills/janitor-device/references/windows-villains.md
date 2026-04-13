# Windows villain catalog

**Last verified:** 2026-04 — update this date when you revise the catalog. Villains come and go; a list that's three years stale will flag things that aren't problems anymore and miss new ones. See the Contributing section in the README for the update process.

Load this file when the user's machine is Windows. These are the common causes of slow Windows machines in the real world, ranked by likelihood.

---

## Tier 1 — Almost always the problem

### OEM bloatware (HP, Dell, Lenovo, Acer, ASUS)

- The single biggest cause of slow Windows laptops is the pre-installed OEM "helper" suite
- Common offenders: **HP JumpStart**, **HP Support Assistant**, **Dell SupportAssist**, **Dell Update**, **Lenovo Vantage**, **Lenovo OneKey Optimizer**, **Lenovo System Update**, **ASUS ArmouryCrate**, **Acer Care Center**
- Can burn 10-20% CPU constantly in the background while doing nothing useful
- Usually runs under Task Scheduler with triggers at boot, user logon, and daily
- Reversible fix: `Disable-ScheduledTask` on every task in the OEM's folder, plus disable the OEM service(s)

### Antivirus trial bloat

- **McAfee LiveSafe**, **McAfee LifeLock**, **Norton 360**, **WebAdvisor** — almost always a 30-day trial that ships pre-installed and refuses to die quietly
- McAfee specifically runs 3-5 background processes (`mcapexe`, `McCSPServiceHost`, `McUICnt`) with a watchdog that respawns them
- Burns 5-20% CPU constantly, generates dozens of popup nags, makes file operations slow because every open/save triggers a real-time scan
- **Never disable Windows Defender alongside this.** Uninstall the trial, let Defender take over. Defender is free, always-on, and does not burn CPU in the way the trial antivirus suites do.

### Fake "PC optimizer" malware-adjacent apps

- **Advanced SystemCare**, **PC Optimizer Pro**, **Smart PC Care**, **iObit Driver Booster**, **CCleaner for Windows** (post-acquisition), **Glary Utilities**, **WinZip System Utilities**
- Pattern matches the CleanMyMac cruelty: a "speed booster" that is itself one of the biggest slowdowns
- All of them register scheduled tasks, tray helpers, and registry Run entries
- Treat the same way as McAfee: disable every scheduled task, stop and disable every service, move registry Run entries to `.disabled`, then uninstall via `winget uninstall` (with user confirmation)

### OneDrive sync churn

- Symptom: `OneDrive.exe` constantly at 15-40% CPU, disk activity never drops to zero
- Usually stuck re-scanning a folder with many small files, or looping on a file with a name conflict
- Common after major Windows Feature Updates (the index gets rebuilt from scratch)
- **Never auto-unlink OneDrive.** That's destructive — files pending upload will be lost. Instead: pause sync via the tray icon, let the user decide whether to unlink.

### Microsoft Teams background

- Even when "closed," Teams runs a background process that uses 100-300 MB of RAM and periodically spikes CPU for presence-sync
- Auto-launches via both a Task Scheduler task (`TeamsMachineInstaller`) AND a registry Run key (`com.squirrel.Teams.Teams`) — belt and suspenders
- The "classic" Teams and the "new" Teams both install by default now — often both running at once
- Fix: disable the Run key (rename to `.disabled`), disable the Task Scheduler task, quit from the tray

### Windows Search over-indexing

- `SearchIndexer.exe` + `SearchProtocolHost.exe` at 15-30% CPU sustained = indexer stuck or over-scoped
- Often gets worse after Feature Updates, or when a user adds Documents/Downloads to the index
- Diagnosis: `Get-Service WSearch` to confirm state, and check Indexer Options in Settings for the scope
- Fix: trim the index scope (exclude Downloads, large dev folders), or restart the service. Never disable it entirely — Start Menu and Explorer search both depend on it.

### OEM driver updaters

- **NVIDIA GeForce Experience**, **AMD Radeon Software Updater**, **Intel Driver & Support Assistant**, **Logitech G HUB**, **Razer Synapse**, **Corsair iCUE**
- Each runs its own auto-update checker on boot + periodic intervals
- Individually ~1-3% CPU; collectively on a gaming-hardware-heavy machine they add up to 10%+
- Disable the auto-update scheduled tasks; leave the drivers themselves alone

### Xbox Game Bar / Game DVR

- Pre-enabled on every Windows 10/11 install, even on non-gaming machines
- Game DVR captures the last 30 seconds of video continuously in the background if "Background recording" is on
- Can burn 5-15% CPU + GPU doing this on machines the user never games on
- Fix: disable via Settings → Gaming → Captures → "Record what happened" → Off

---

## Tier 2 — Common secondary

### Edge background tasks

- Microsoft Edge runs background tasks even when closed (prefetch, sync, push notifications)
- The `msedge.exe` process count on a fresh reboot should be 0; if it's 4-6, Edge is doing background work
- Settings → System → "Continue running background extensions and apps when Microsoft Edge is closed" → Off

### Cortana

- `SearchApp.exe` + Cortana-related processes — usually transient but can get stuck
- Mostly harmless on modern Windows 11 (Cortana is largely removed), more of an issue on Windows 10

### Third-party "free VPN" trials

- Bundled with OEM installs. Norton VPN, McAfee VPN, random freemium VPNs with network drivers that hijack traffic
- Network drivers especially — they intercept every packet, measurably slowing network throughput
- Remove via `winget uninstall` after confirmation

### Discord

- Same behavior as on Mac — 40-60% CPU in background with voice channels or animated emoji-heavy servers
- Auto-launches on Windows by default (Run key `com.squirrel.Discord.Discord`)

### Chrome with too many tabs

- Same behavior as on Mac. Task Manager (Shift+Esc inside Chrome) shows per-tab usage.

### Huge Downloads folder

- Windows Search indexes it aggressively. Same recommendation as Mac: move old installers to Recycle Bin.

---

## Tier 3 — Less common

- Orphaned scheduled tasks from uninstalled apps (remove via `Get-ScheduledTask`, filter by missing binary path)
- Stale Windows Defender exclusions left by uninstalled antivirus trials
- Third-party print spoolers from deprecated printer drivers
- WSL (Windows Subsystem for Linux) instances running in the background when the user doesn't need them
- Hyper-V services enabled but unused
- Windows Telemetry (`DiagTrack`, `dmwappushservice`) — always-on by design, impact varies, generally leave it alone

---

## Windows-specific things to never touch

- **Windows Defender** — the only always-on, free antivirus on Windows. Disabling it in the name of "speed" is a textbook malware setup. Never suggest disabling it.
- **Windows Update** — deferring updates is fine (Settings UI only); disabling the service entirely is not.
- **Explorer.exe, SearchIndexer, svchost, wininit, lsass, csrss** — system-critical. Killing them breaks the user session.
- **BCD / Boot Configuration Data** — outside scope. Never use `bcdedit`.
- **Registry HKLM edits without the user seeing the key path** — registry Run keys under HKCU are fine (rename to `.disabled`). HKLM changes require admin + full disclosure.

---

## What to watch for in diagnostic output

### Process CPU
- Any process over 40% CPU that isn't something the user is actively using = suspect
- Look for clusters of related names (`McAfee*`, `HP*`, `Dell*`) and sum them
- `SearchIndexer` + `SearchProtocolHost` clustered hot = over-indexing
- `svchost` at 40%+ CPU — expand it in Task Manager to find the actual service inside; common culprits are `wuauserv` (Windows Update), `BITS` (Background Intelligent Transfer), `Superfetch`/`SysMain`

### Memory
- `Get-CimInstance Win32_OperatingSystem` → compare `FreePhysicalMemory` to `TotalVisibleMemorySize`
- Less than 10% free on a machine with 16 GB+ of RAM = under pressure
- Committed Bytes on the page file > physical RAM = paging heavily, system feels slow

### Disk
- If the disk is a mechanical HDD (still common on budget laptops from 2020-2022), the machine is permanently slow and no amount of janitor work will fix it. Flag this to the user gently: "Your disk is a 5400 RPM spinning drive — that's the hardware floor. Upgrading to an SSD would do more than anything janitor can."
- SSD with >95% used capacity is a separate problem: TRIM gets slow and writes amplify. Target under 85% used.

### Startup count
- `Get-ScheduledTask | Where State -eq Ready | Measure | Select Count` — on a fresh install this is ~50-80. Over 150 on a consumer machine is a big red flag.

---

## Expected final state of a healthy Windows machine

- Top CPU process is something the user is actively using
- Background services count < 150
- No OEM "helper" app from HP/Dell/Lenovo/ASUS/Acer in running services
- Windows Defender is ON, no third-party AV trial running
- No McAfee/Norton trial processes
- OneDrive syncing cleanly or paused deliberately
- Game Bar / Game DVR disabled on non-gaming machines
- Windows Search service running but scope trimmed
