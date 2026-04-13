# Cross-OS metric mapping

This file is the source of truth for the before/after table in Phase 5. When a row's metric exists on both macOS and Windows, include it. When it's OS-specific, include it only on that OS. **Never print "N/A" — omit the row entirely** so the table feels native to the user's OS instead of feeling like a half-working cross-platform abstraction.

---

## Metrics available on BOTH macOS and Windows

| Metric | macOS command | Windows (PowerShell 7+) command |
|---|---|---|
| Top CPU process | `ps -Ao pid,pcpu,pmem,comm -r \| head -5` | `Get-Process \| Sort-Object CPU -Desc \| Select-Object -First 5 Id,Name,CPU` |
| Top memory process | `ps -Ao pid,pcpu,pmem,comm -m \| head -5` | `Get-Process \| Sort-Object WorkingSet -Desc \| Select-Object -First 5 Id,Name,@{n='WS_MB';e={[math]::Round($_.WorkingSet/1MB,0)}}` |
| Disk space free | `df -h /` | `Get-PSDrive C \| Select-Object Used,Free` |
| Total running processes | `ps ax \| wc -l` | `(Get-Process).Count` |
| Uptime | `uptime` | `(Get-CimInstance Win32_OperatingSystem).LastBootUpTime` |
| Hardware model | `system_profiler SPHardwareDataType` | `Get-CimInstance Win32_ComputerSystem \| Select Manufacturer, Model` |
| OS version | `sw_vers` | `[System.Environment]::OSVersion` |

---

## Metrics available on macOS ONLY (omit rows entirely on Windows)

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
| Load average (1/5/15) | `uptime` | Windows has no load average concept. CPU percentage via `Get-Counter` is the closest, but it's instantaneous, not windowed. Skip load average on Windows. |

---

## Metrics available on Windows ONLY (omit rows entirely on macOS)

| Metric | Windows command | Why there's no macOS equivalent |
|---|---|---|
| Power plan | `powercfg /getactivescheme` | macOS has Low Power Mode (reported on Mac side) but no multi-plan system. |
| Windows Search state | `Get-Service WSearch` | macOS has Spotlight state via `mdutil` (reported on Mac side). The semantics are different enough that a shared row is misleading. |
| Scheduled tasks count | `(Get-ScheduledTask \| Where State -eq Ready).Count` | macOS has launchd agents/daemons, which are reported differently. Keep these as separate rows per-OS rather than forcing a shared "autostart entries" row. |
| Services running count | `(Get-Service \| Where Status -eq Running).Count` | macOS has launchctl-managed services, reported differently. Keep separate. |
| Defender status | `Get-MpComputerStatus \| Select RealTimeProtectionEnabled` | macOS has XProtect which is opaque. Skip the parallel row. |

---

## The table-building rule

When building the before/after table in Phase 5:

1. **Always include the shared rows** (top CPU, top memory, disk free, process count).
2. **Include the OS-specific rows for whichever OS the user is on.** Never both sets.
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

Notice the Mac table has `Free memory pages` and `Memory compressor` and `Low Power Mode`; the Windows table has `Free memory (MB)` and `Power plan` and `Services running`. Those are not the same metrics and the units are different. Keep them separate and don't lie about parity.
