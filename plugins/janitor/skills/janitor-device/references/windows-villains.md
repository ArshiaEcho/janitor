# Windows villain catalog

**Last verified:** 2026-11 — update this date when you revise the catalog. Villains come and go; a list that's three years stale will flag things that aren't problems anymore and miss new ones. See the Contributing section in the README for the update process.

Load this file when the user's machine is Windows. These are the common causes of slow Windows machines in the real world, ranked by likelihood.

**Versions in the wild (late 2026):** Windows 11 **25H2** and **26H2** (26H2 began rolling out September 29, 2026 as a small enablement update on top of 24H2/25H2). **26H1** exists only on new Snapdragon X2 laptops. **24H2 Home/Pro stopped getting updates on October 13, 2026**, and Windows 10 is past end of support. Read the version with `(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').DisplayVersion` (read-only). If it's 24H2 Home/Pro or Windows 10, say so kindly in the report: not a speed villain, but the user should update (their call, done in Settings).

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

### Copilot+ PC AI stack (`WorkloadsSessionHost.exe`)

- On Copilot+ PCs (NPU laptops, Snapdragon X / Ryzen AI / Core Ultra 200V and newer), Windows preloads on-device AI models for Recall, Click to Do and semantic search. That shows up as **several `WorkloadsSessionHost.exe` processes**, commonly 2-8 GB of RAM combined in user reports on 24H2/25H2, sometimes with the NPU busy at idle.
- It can't be killed or disabled directly (MSI's own FAQ says so; Microsoft documents no supported switch). The reversible route is turning off the features that wake it: Settings → Privacy & security → **Recall & snapshots** (save snapshots off), and Click to Do off. Settings → System → **AI components** lists what's installed.
- If the user never wants Recall, it can be removed as an optional feature (admin block in `fix-blocks-windows.md`, reversible by re-enabling it). This removes Recall and its own AI components only; other AI features are unaffected.
- Don't recommend third-party "remove all Windows AI" scripts. Some of them block Windows servicing to keep the AI from coming back, which can quietly break updates.
- On 8 GB or 16 GB Copilot+ machines this is often the single biggest memory consumer. On 32 GB it's usually just noise.

### OneDrive sync churn

- Symptom: `OneDrive.exe` constantly at 15-40% CPU, disk activity never drops to zero
- Usually stuck re-scanning a folder with many small files, or looping on a file with a name conflict
- Common after major Windows Feature Updates (the index gets rebuilt from scratch)
- **Never auto-unlink OneDrive.** That's destructive — files pending upload will be lost. Instead: pause sync via the tray icon, let the user decide whether to unlink.

### Microsoft Teams background

- Classic Teams is retired; what's installed now is the "new" Teams, process `ms-teams.exe` (plus `msedgewebview2.exe` children). Even when "closed" it can sit on several hundred MB and wake up for presence sync.
- It auto-starts by default. Reversible fix, no admin: Settings → Apps → Startup → Microsoft Teams → Off. Then quit from the tray.
- Leftovers on machines that once had classic Teams: a `com.squirrel.Teams.Teams` Run key or a `TeamsMachineInstaller` scheduled task. Rename / disable them the usual reversible way; the app they launch is gone.

### Windows Search over-indexing

- `SearchIndexer.exe` + `SearchProtocolHost.exe` at 15-30% CPU sustained = indexer stuck or over-scoped
- Often gets worse after Feature Updates, or when a user adds Documents/Downloads to the index
- Diagnosis: `Get-Service WSearch` to confirm state, and check Indexer Options in Settings for the scope
- Fix: trim the index scope (exclude Downloads, large dev folders), or restart the service. Never disable it entirely — Start Menu and Explorer search both depend on it.

### OEM driver updaters

- **NVIDIA App** (replaced GeForce Experience in late 2024; old installs may still have GeForce Experience), **AMD Radeon Software Updater**, **Intel Driver & Support Assistant**, **Logitech G HUB**, **Razer Synapse**, **Corsair iCUE**
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

### Copilot app auto-starting

- The free Copilot app launches at sign-in by default on many installs. Modest on its own, but it's one more WebView-based app living in RAM.
- Reversible fix: Settings → Apps → Startup → Copilot → Off. As of 2026 it can also be uninstalled like any app (Settings → Apps → Installed apps), and reinstalled from the Store any time. Updates occasionally bring it back.
- Microsoft 365 Copilot (the Office hub app) is a separate app. Don't remove it on a work machine without the user checking with IT.

### Phone Link / Cross Device Service

- `CrossDeviceService.exe` ("Microsoft Cross Device Service") and Phone Link can sit at high CPU, mostly from continuous background sync with a linked phone (photos, files in Explorer). Microsoft acknowledged a CPU bug in this service in 2024; reports continue.
- Reversible fixes, no admin: Settings → Bluetooth & devices → Mobile devices → turn off "Allow this PC to access your mobile devices" if they don't use it; or Settings → Apps → Installed apps → Phone Link → Advanced options → Background apps permissions → Never; and turn Phone Link off in Settings → Apps → Startup.

### Widgets

- The taskbar Widgets board keeps a WebView-based news feed process around (`Widgets.exe` and `WidgetService.exe` in Task Manager on most builds).
- Reversible fix: Settings → Personalization → Taskbar → Widgets → Off. Removal of the whole Windows Web Experience Pack is possible but the Store tends to reinstall it, so the toggle is the better answer.

### Cortana (Windows 10 only, demoted)

- The standalone Cortana app is retired on Windows 11. Only relevant on a leftover Windows 10 machine, and there the bigger news is that Windows 10 is out of support.

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

## Developer disk hogs (Windows)

Same rules as every OS: measure first, show the table, reversible moves into the Recycle Bin after a yes, each tool's own clean command as a block the user runs, AI models only with a per-item yes, `node_modules` report-only. **Docker is out of scope**: Docker Desktop's WSL disk image, images, volumes and build cache belong to Docker's own tooling. Say so in one line and move on.

Size helper (read-only), reuse it for every row:
```powershell
function Get-JanitorSize($p) { if (Test-Path $p) { "{0,8:N1} GB  {1}" -f ((Get-ChildItem $p -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum/1GB), $p } }
```

| Hog | Measure (read-only) | Notes |
|---|---|---|
| npm cache | `Get-JanitorSize (npm config get cache)` | Usually `%LOCALAPPDATA%\npm-cache` |
| pnpm store | `Get-JanitorSize (pnpm store path)` | |
| Yarn cache | `Get-JanitorSize (yarn cache dir)` | Yarn 1 |
| pip cache | `Get-JanitorSize (pip cache dir)` | Usually `%LOCALAPPDATA%\pip\Cache` |
| uv cache | `Get-JanitorSize (uv cache dir)` | Default `%LOCALAPPDATA%\uv\cache` |
| NuGet caches | `dotnet nuget locals all --list` then size each | .NET developers only |
| Hugging Face hub | `Get-JanitorSize "$env:USERPROFILE\.cache\huggingface\hub"` and `hf cache ls` | Models. Report only |
| Ollama models | `Get-JanitorSize "$env:USERPROFILE\.ollama\models"` and `ollama list` | Models. Report only. `OLLAMA_MODELS` can relocate it |
| LM Studio models | `Get-JanitorSize "$env:USERPROFILE\.lmstudio\models"` | Models. Report only. My Models tab shows the real path |
| WSL distro disks | `Get-ChildItem "$env:LOCALAPPDATA\Packages" -Recurse -Filter ext4.vhdx -ErrorAction SilentlyContinue \| Select FullName, @{n='GB';e={[math]::Round($_.Length/1GB,1)}}` | **Report only.** These virtual disks grow and don't shrink on their own. Shrinking them is the user's job with WSL's own tooling |
| Old `node_modules` | `Get-ChildItem $env:USERPROFILE -Directory -Recurse -Depth 5 -Filter node_modules -ErrorAction SilentlyContinue \| Where-Object LastWriteTime -lt (Get-Date).AddDays(-90) \| Select-Object -First 30 FullName` | **Report only.** The user decides per project |

Fix blocks are in `fix-blocks-windows.md`.

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
- Several `WorkloadsSessionHost` processes on a Copilot+ PC = the on-device AI stack preloading models (Tier 1)
- `ms-teams`, `CrossDeviceService`, `Widgets` + lots of `msedgewebview2` = WebView-based background apps; sum them
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
- On Copilot+ PCs: Recall / Click to Do off unless the user actually uses them
- Teams, Copilot, Phone Link not auto-starting unless the user wants them
- Running 25H2 or 26H2 (not 24H2 Home/Pro or Windows 10)
