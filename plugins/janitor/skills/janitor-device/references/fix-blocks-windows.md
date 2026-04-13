# Windows fix blocks

**Last verified:** 2026-04 — update this date when you revise the fix recipes. Windows cmdlets and service names change between versions; PowerShell 7+ is assumed throughout.

Load this file when the user has approved fixes on Windows. Every admin block is given to the user as plaintext — they paste it into an elevated PowerShell themselves. The skill never enters an elevated context on its own.

---

## Shell requirements

All commands in this file assume **PowerShell 7+** (`pwsh`). If the user only has Windows PowerShell 5.1, most commands still work but some cmdlets behave differently — in that case, skip the fix and tell the user which specific diagnostic is unavailable rather than silently failing.

**Elevation:** anything that touches services, scheduled tasks, the Registry under `HKLM:\`, or `winget uninstall` requires an admin PowerShell. The skill **never** opens one itself. It hands the user a block like:

> Open PowerShell as Administrator (right-click the Start button → "Terminal (Admin)" or "Windows PowerShell (Admin)"), then paste this:
>
> ```powershell
> # ...the block...
> ```

---

## Rule 1 — Disable watchdogs BEFORE uninstalling or killing

Same principle as macOS. McAfee, HP/Dell/Lenovo suites, and "PC optimizer" apps all respawn if you stop the process before disabling the auto-start.

Correct order on Windows:
1. `Disable-ScheduledTask` on every task the app registered
2. Set the Run registry key to `.disabled` (rename the value name)
3. `Stop-Service` and `Set-Service -StartupType Disabled`
4. Uninstall via `winget uninstall` only after the watchdog is neutralized

---

## Reversible disable patterns

### Scheduled tasks

```powershell
# List the offender's tasks
Get-ScheduledTask | Where-Object { $_.TaskName -like "*McAfee*" -or $_.TaskPath -like "*McAfee*" } | Select-Object TaskName, TaskPath, State

# Disable one (reversible — `Enable-ScheduledTask` to restore)
Disable-ScheduledTask -TaskPath "\McAfee\" -TaskName "McAfee Update"

# Disable all tasks in a folder path
Get-ScheduledTask -TaskPath "\McAfee\*" | Disable-ScheduledTask
```

Reverse with:
```powershell
Get-ScheduledTask -TaskPath "\McAfee\*" | Enable-ScheduledTask
```

### Registry Run keys (reversible via rename)

The Mac plist-rename trick has a direct Windows analogue: rename the registry value instead of deleting it. The entry still exists, Windows just ignores it.

```powershell
# List current user Run entries
Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" |
    Select-Object * -ExcludeProperty PS*

# Rename an entry to disable it (reversible)
Rename-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" `
    -Name "OneDrive" -NewName "OneDrive.disabled"

# Reverse it
Rename-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" `
    -Name "OneDrive.disabled" -NewName "OneDrive"
```

`HKLM:\Software\Microsoft\Windows\CurrentVersion\Run` works the same way but requires admin — give the user a copy-paste block.

### Services

```powershell
# List running services (admin recommended for full list)
Get-Service | Where-Object Status -eq 'Running' | Select-Object Name, DisplayName

# Stop a service
Stop-Service -Name "McAPExe" -Force

# Disable its auto-start (reversible)
Set-Service -Name "McAPExe" -StartupType Disabled
```

Reverse with:
```powershell
Set-Service -Name "McAPExe" -StartupType Automatic
Start-Service -Name "McAPExe"
```

---

## Safe deletion: use the Recycle Bin, never `Remove-Item`

`Remove-Item -Force -Recurse` is **forbidden** for user files in janitor. It bypasses the Recycle Bin and the file is gone. Use the COM Shell object instead — it routes through Recycle Bin exactly like dragging a file there in Explorer.

```powershell
# Safe move-to-Recycle-Bin for a single file
$shell = New-Object -ComObject Shell.Application
$item  = $shell.Namespace((Split-Path 'C:\Users\<name>\Downloads\old_installer.zip')).ParseName('old_installer.zip')
$item.InvokeVerb('delete')
```

For batch moves, loop the same pattern. If the user explicitly asks for permanent deletion, make them confirm twice — and even then, only on machine-generated files (installer cruft, `*.tmp`), never user-authored files.

---

## The McAfee / Norton uninstall block

Give this to the user verbatim in an admin PowerShell. Reversible through `winget install` if they change their mind.

```powershell
# 1. Neutralize the watchdog
Get-ScheduledTask | Where-Object { $_.TaskPath -like "*McAfee*" -or $_.TaskName -like "*McAfee*" } | Disable-ScheduledTask

# 2. Stop and disable services
Get-Service | Where-Object { $_.Name -like "*McAfee*" -or $_.DisplayName -like "*McAfee*" } | ForEach-Object {
    Stop-Service -Name $_.Name -Force -ErrorAction SilentlyContinue
    Set-Service -Name $_.Name -StartupType Disabled -ErrorAction SilentlyContinue
}

# 3. Rename any Run key entries that mention McAfee (loop manually — show before changing)
Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" | Format-List

# 4. Uninstall via winget (look for McAfee, Norton, WebAdvisor packages)
winget list --name "McAfee"
winget uninstall --name "McAfee LiveSafe" --accept-source-agreements
winget uninstall --name "McAfee WebAdvisor" --accept-source-agreements
```

**Confirmation rule:** the user reads steps 1-3 output, confirms nothing else is going to break, *then* runs step 4. Do not chain these into a single `&&` block.

---

## OEM bloatware removal (HP / Dell / Lenovo)

Same pattern as McAfee. Example for HP:

```powershell
# List HP-related scheduled tasks
Get-ScheduledTask | Where-Object { $_.TaskPath -like "*HP*" -or $_.TaskName -like "*HP*" } | Select-Object TaskName, TaskPath, State

# Disable them (reversible)
Get-ScheduledTask | Where-Object { $_.TaskPath -like "*HP*" } | Disable-ScheduledTask

# List HP services
Get-Service | Where-Object { $_.Name -like "HP*" -or $_.DisplayName -like "HP*" }

# Optional uninstall (show list first, confirm, then uninstall individually)
winget list --name "HP"
# Example: winget uninstall --name "HP JumpStart Bridge"
```

Never use a wildcard uninstall. Always list first, confirm, uninstall one package at a time.

---

## OneDrive — pause, don't unlink

```powershell
# Pause OneDrive sync (reversible — right-click tray icon → Resume)
# This needs the OneDrive tray app, there's no clean CLI for it
# Give user manual instructions:
#   1. Right-click OneDrive icon in system tray
#   2. Settings → Account → Pause syncing → 2 hours
#   3. If still high CPU after restart, pause again or investigate which folder is stuck

# DO NOT auto-unlink. Unlinking will delete pending uploads.
# If the user wants full removal after understanding the risk:
# winget uninstall Microsoft.OneDrive
```

---

## Windows Search re-scoping

```powershell
# Confirm the service state
Get-Service WSearch

# Re-scope via Settings GUI:
#   Settings → Privacy & security → Searching Windows → Find my files → Classic
#   This removes Downloads/Documents from the default index scope

# Rebuild the index if it's wedged (safe, no data loss)
Stop-Service WSearch
Remove-Item "$env:ProgramData\Microsoft\Search\Data\Applications\Windows\Windows.edb" -Force
Start-Service WSearch
# Index will rebuild over the next few hours in the background
```

Rebuilding the index is reversible in the sense that nothing is permanently lost — search just returns incomplete results until the rebuild finishes. Warn the user about that.

---

## Xbox Game Bar / Game DVR disable

```powershell
# Disable Game DVR recording (reversible via same registry key)
New-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "GameDVR_Enabled" -Value 0 -PropertyType DWord -Force
New-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR" -Name "AllowGameDVR" -Value 0 -PropertyType DWord -Force
```

Reverse by setting the values back to `1` or removing the properties.

---

## What is strictly forbidden

- `Remove-Item -Force -Recurse` on user files
- Disabling Windows Defender (`Set-MpPreference -DisableRealtimeMonitoring $true`) — never
- Editing BCD / `bcdedit`
- Disabling `WinDefend`, `SecurityHealthService`, or any Defender component
- Silently uninstalling packages without user confirmation
- Network commands (`Invoke-WebRequest`, `Invoke-RestMethod`, `curl`, `wget`) — janitor is offline-only
- Running `.reg` files dropped to disk (all registry edits go through `Set-ItemProperty` / `New-ItemProperty` inline so the user can read them)
- Running `.ps1` script files dropped to disk (inline commands only)

---

## Quirks to know about

**PowerShell ExecutionPolicy.** Some Windows installs restrict running `.ps1` files. Janitor uses only inline commands (no script files), so this never applies — if the user gets "execution of scripts is disabled," they're running a file we shouldn't have written. Investigate.

**5.1 vs 7+ cmdlet differences.** `Get-CimInstance` is preferred over deprecated `Get-WmiObject`. Use `-ErrorAction SilentlyContinue` liberally because some WMI classes are missing on desktop SKUs but present on server SKUs.

**Quoting.** PowerShell uses double-quotes for interpolation and backticks for continuation. Single-quotes are literal. Test every block on Windows 11 (21H2 or later) before trusting it.

**Admin should never run silently.** Same rule as macOS sudo. Give the user a block to paste themselves. Trust matters more than speed.
