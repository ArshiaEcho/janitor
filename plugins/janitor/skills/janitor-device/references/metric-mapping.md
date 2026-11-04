# Cross-OS metric mapping

**Last verified:** 2026-11 — covers macOS 26/27, Windows 11 25H2/26H2, and Linux (Ubuntu 24.04/26.04, Fedora 43/44).

This file is the source of truth for the before/after table in Phase 5. When a row's metric exists on the user's OS, include it. When it's OS-specific, include it only on that OS. **Never print "N/A" — omit the row entirely** so the table feels native to the user's OS instead of feeling like a half-working cross-platform abstraction.

---

## Metrics available on ALL THREE (macOS, Windows, Linux)

| Metric | macOS command | Windows (PowerShell 7+) command | Linux command |
|---|---|---|---|
| Top CPU process | `ps -Ao pid,pcpu,pmem,comm -r \| head -5` | `Get-Process \| Sort-Object CPU -Desc \| Select-Object -First 5 Id,Name,CPU` | `ps -eo pid,pcpu,pmem,comm --sort=-pcpu \| head -5` |
| Top memory process | `ps -Ao pid,pcpu,pmem,comm -m \| head -5` | `Get-Process \| Sort-Object WorkingSet -Desc \| Select-Object -First 5 Id,Name,@{n='WS_MB';e={[math]::Round($_.WorkingSet/1MB,0)}}` | `ps -eo pid,pcpu,pmem,comm --sort=-pmem \| head -5` |
| Disk space free | `df -h /` | `Get-PSDrive C \| Select-Object Used,Free` | `df -h /` |
| Total running processes | `ps ax \| wc -l` | `(Get-Process).Count` | `ps -e --no-headers \| wc -l` |
| Uptime | `uptime` | `(Get-CimInstance Win32_OperatingSystem).LastBootUpTime` | `uptime -p` |
| Hardware model | `system_profiler SPHardwareDataType` | `Get-CimInstance Win32_ComputerSystem \| Select Manufacturer, Model` | `cat /sys/class/dmi/id/product_name` |
| OS version | `sw_vers` | `(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').DisplayVersion` | `grep PRETTY_NAME /etc/os-release` |
| Dev caches (sum) | sum of the rows measured in the Developer disk hogs section | same | same |

Dev caches (sum) is only shown when the user is a developer and the section was run. Never count AI models or `node_modules` in it; if models were removed, add a separate dynamic row (`Ollama models`, `HF cache`).

---

## Metrics on macOS AND Linux (omit on Windows)

| Metric | macOS | Linux | Why not Windows |
|---|---|---|---|
| Load average (1/5/15) | `uptime` | `uptime` or `cat /proc/loadavg` | Windows has no load average concept. CPU percentage via `Get-Counter` is instantaneous, not windowed. Skip. |

Note: Linux load average also counts tasks stuck in uninterruptible disk wait, so it can be high on a slow disk with low CPU. Mention that if CPU looks idle.

---

## Metrics available on macOS ONLY (omit rows entirely on Windows and Linux)

| Metric | macOS command | Why there's no Windows equivalent |
|---|---|---|
| Memory compressor | `vm_stat \| grep compressor` | Windows uses a different memory model (page file + Modified Page List). The closest analogue is `Get-Counter '\Memory\Pages/sec'` but it measures a different thing — do not try to pretend it's equivalent. |
| Pages free | `vm_stat \| grep 'Pages free'` | Same — macOS reports in 4 KB pages, Windows reports in MB. Never cross-convert. Report Windows free memory separately via `FreePhysicalMemory`. |
| Memory pressure | `memory_pressure` | Windows has no single command that reports "are we under memory pressure right now." Use `Get-Counter '\Memory\Available MBytes'` + `Get-Counter '\Memory\Committed Bytes In Use'` together, but don't try to roll them into a single "pressure" metric. |
| Thermal state | `pmset -g therm` | Windows has no CLI equivalent. Some OEMs (HP, Dell) expose thermal data via WMI, but it's OEM-specific and unreliable. Skip this metric on Windows. |
| Low Power Mode | `pmset -g \| grep lowpowermode` | Windows has "Power Mode" which is different (it's a power plan, not a throttle override). Report the power plan separately as a Windows metric instead. |
| Battery max capacity | `system_profiler SPPowerDataType` | Windows Settings → System → Power & battery → Battery health shows this for laptops, but there's no universal CLI. Skip. |
| Time Machine local snapshots | `tmutil listlocalsnapshots /` | Windows has no equivalent (Shadow Copies are different and admin-only). Skip. |
| Spotlight indexer state | `mdutil -sa` | Windows has `Get-Service WSearch` which reports running/stopped but not "indexing progress." Report the service state as a separate Windows metric. |

---

## Metrics available on Windows ONLY (omit rows entirely on macOS and Linux)

| Metric | Windows command | Why there's no macOS equivalent |
|---|---|---|
| Power plan | `powercfg /getactivescheme` | macOS has Low Power Mode (reported on Mac side) but no multi-plan system. |
| Windows Search state | `Get-Service WSearch` | macOS has Spotlight state via `mdutil` (reported on Mac side). The semantics are different enough that a shared row is misleading. |
| Scheduled tasks count | `(Get-ScheduledTask \| Where State -eq Ready).Count` | macOS has launchd agents/daemons, which are reported differently. Keep these as separate rows per-OS rather than forcing a shared "autostart entries" row. |
| Services running count | `(Get-Service \| Where Status -eq Running).Count` | macOS has launchctl-managed services, reported differently. Keep separate. |
| Defender status | `Get-MpComputerStatus \| Select RealTimeProtectionEnabled` | macOS has XProtect which is opaque. Skip the parallel row. |
| WorkloadsSessionHost RAM (Copilot+ PCs) | `(Get-Process WorkloadsSessionHost -ErrorAction SilentlyContinue \| Measure-Object WorkingSet -Sum).Sum/1MB` | Windows-only AI model host. Include only where it was running. |

---

## Metrics available on Linux ONLY (omit rows entirely on macOS and Windows)

| Metric | Linux command | Notes |
|---|---|---|
| Available memory | `free -m` (the `available` column) | Never report the `free` column; Linux uses spare RAM as cache on purpose |
| Memory pressure (PSI) | `cat /proc/pressure/memory` (`some avg10`) | Kernel 4.20+. Omit the row if the file is missing |
| Swap used | `swapon --show` / `free -m` | On Fedora this is usually zram (compressed RAM); label it `zram used` there |
| Power profile | `powerprofilesctl get` | Omit if the command isn't installed |
| Journal size | `journalctl --disk-usage` | |
| Failed units | `systemctl --failed --no-legend \| wc -l` | Add `--user` for the session count |
| Snap disabled revisions | `snap list --all \| awk '/disabled/' \| wc -l` | Ubuntu / snap systems only |
| Unused Flatpak runtimes | `flatpak uninstall --unused` shows them (answer no to just count) | Flatpak systems only |

---

## The table-building rule

When building the before/after table in Phase 5:

1. **Always include the shared rows** (top CPU, top memory, disk free, process count).
2. **Include the OS-specific rows for whichever OS the user is on**, including the macOS-and-Linux load average row on those two. Never another OS's set.
3. **Include villain-specific rows** — these are dynamic based on what was found (e.g., "Adobe CPU", "McAfee CPU", "OneDrive CPU"). These are never in this mapping table because they depend on the diagnosis.
4. **Never emit "N/A" or "—" to indicate a missing metric.** Just omit the row.

Example output for a Mac run:
```
| Metric              | Before   | After    | Change  |
|---------------------|----------|----------|---------|
| Top CPU process     | Adobe    | Chrome   | fixed   |
| Top memory process  | Chrome   | Chrome   | -       |
| Free memory pages   | 3924     | 81547    | +77623  |
| Memory compressor   | 280K     | 120K     | -160K   |
| Disk space free     | 220 GB   | 226 GB   | +6 GB   |
| Low Power Mode      | ON       | OFF      | fixed   |
| Adobe CPU (sum)     | 247%     | 0%       | -247%   |
```

Example output for a Windows run:
```
| Metric              | Before   | After    | Change  |
|---------------------|----------|----------|---------|
| Top CPU process     | mcapexe  | chrome   | fixed   |
| Top memory process  | chrome   | chrome   | -       |
| Free memory (MB)    | 1240     | 4820     | +3580   |
| Disk space free     | 112 GB   | 118 GB   | +6 GB   |
| Power plan          | Balanced | Balanced | -       |
| Services running    | 182      | 171      | -11     |
| McAfee CPU (sum)    | 34%      | 0%       | -34%    |
```

Example output for a Linux run:
```
| Metric                | Before    | After     | Change   |
|-----------------------|-----------|-----------|----------|
| Top CPU process       | localsear | firefox   | fixed    |
| Top memory process    | firefox   | firefox   | -        |
| Available memory (MB) | 1900      | 5100      | +3200    |
| Memory pressure avg10 | 18.4      | 0.6       | -17.8    |
| Load average 1/5/15   | 6.1/5.8/5 | 1.2/1.4/2 | settling |
| Disk space free       | 21 GB     | 34 GB     | +13 GB   |
| Power profile         | power-sav | balanced  | fixed    |
| Dev caches (sum)      | 14.2 GB   | 3.1 GB    | -11.1 GB |
```

Notice the Mac table has `Free memory pages` and `Memory compressor` and `Low Power Mode`; the Windows table has `Free memory (MB)` and `Power plan` and `Services running`. Those are not the same metrics and the units are different. The Linux table has `Available memory (MB)` and `Memory pressure`, which are different again. Keep them separate and don't lie about parity.
