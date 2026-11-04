# Linux villain catalog

**Last verified:** 2026-11 — update this date when you revise the catalog. Villains come and go; a list that's three years stale will flag things that aren't problems anymore and miss new ones. See the Contributing section in the README for the update process.

Load this file when the user's machine is Linux. Written against the desktops people actually run in late 2026: **Ubuntu 24.04 LTS and 26.04 LTS** (GNOME, snaps), **Fedora 43/44** (GNOME or KDE Plasma 6, dnf5, Flatpak), and their close relatives (Debian 13, Pop!_OS, Mint, Kubuntu). Servers and minimal window managers have far fewer villains; most of this is desktop-specific.

**WSL note:** if `/proc/version` contains `microsoft`, this is Linux running inside Windows (WSL). The "slow computer" is almost always the Windows side. Say so, offer to check the Windows host instead, and only run the Linux catalog for the WSL distro itself (its disk hogs and dev caches still count).

---

## Tier 1 — Almost always the problem

### GNOME LocalSearch (formerly Tracker) indexing loop

- Process names on GNOME 47 and later: `localsearch-3`, `localsearch-extractor-3`. On older releases the same job was `tracker-miner-fs-3` and `tracker-extract-3`. Same villain, new name tag.
- Normal: a burst of CPU for an hour or so after first login, a big copy, or an upgrade. Not normal: hours of sustained CPU, or the extractor chewing on one file over and over (bug reports show it looping on files that no longer exist, and on single corrupt media files).
- `ps` truncates process names to 15 characters, so the extractor shows up as `localsearch-ext` (and KDE's as `baloo_file_extr`). Use `ps -eo pid,pcpu,args` when a name looks cut off.
- Check what it thinks it's doing: `localsearch status` (read-only).
- Gentle fix (reversible, no sudo): GNOME Settings → Search → Search Locations, switch off big folders it has no business indexing (Downloads, dev folders, a mounted media drive).
- Firmer fix (reversible): mask the user units. `systemctl --user unmask` restores them. Heads-up for the user: on some setups D-Bus activation can still wake the indexer after masking, so verify after a re-login. See `fix-blocks-linux.md`.
- Nuclear-but-safe: `localsearch reset` wipes the **index only** (files and tags are untouched) and lets it rebuild from scratch. Useful when it is wedged on stale entries.
- **Never** `apt purge` the localsearch packages or `chmod -x` its binaries. Purging can drag Files (Nautilus) and other desktop pieces out with it, and chmod-ing system binaries is exactly the kind of quiet breakage Janitor does not do.

### snapd churning (Ubuntu)

- Symptoms: `snapd` hot, `snap` commands taking minutes, whole desktop sluggish while snaps refresh.
- Late 2026 known bug: on Ubuntu 26.04.1, snapd could loop on regenerating security profiles (Launchpad #2161845); the reported fix shipped in snapd 2.78. The cure is a newer snapd, which means the user updating it themselves (it goes online, so it's their block to run, not Janitor's).
- Read-only checks: `snap changes` (anything stuck in "Doing" for ages?), `systemd-cgtop -d 5` to see which `snap.*` scope is eating CPU, `journalctl -u snapd -b --no-pager | tail -n 100`.
- Refreshes landing mid-work: snapd can be told to refresh at night (`refresh.timer`) or to hold refreshes for a while. Both are settings, both reversible. See `fix-blocks-linux.md`.
- Disk side: snapd keeps old revisions of every snap (shown as `disabled` in `snap list --all`). `refresh.retain` controls how many; lowering it to 2 is a reversible setting that trims them over time.

### Software-center background refreshes (packagekitd, gnome-software, Discover)

- `packagekitd` and `gnome-software` (or KDE's `plasma-discover` / its notifier) waking up to refresh metadata and download updates. Spiky CPU, disk and network for a few minutes, sometimes stuck retrying in a loop.
- Usually transient: if it's hot right after login, wait 10 minutes and re-measure before calling it a villain.
- GNOME: `gsettings set org.gnome.software download-updates false` stops automatic downloads (reverse with `gsettings reset org.gnome.software download-updates`). Honest caveat: reports show gnome-software can still poke PackageKit for metadata even with this off. It reduces the noise; it doesn't silence it.
- KDE: System Settings → Software Update → set the notification/check frequency down. No terminal needed.
- Never remove PackageKit or the software center to "fix" this. The user loses their update GUI and won't notice until something important goes unpatched.

### KDE Baloo file indexer (Plasma)

- Process names: `baloo_file`, `baloo_file_extractor`. Same story as LocalSearch: fine in bursts, a villain when it pins a core for hours.
- Read-only check: `balooctl6 status` (Plasma 6; older Plasma used `balooctl`).
- Reversible fix: `balooctl6 suspend` (pause) or `balooctl6 disable` (off; `balooctl6 enable` brings it back). Or System Settings → Search → File Search → untick Enabled / exclude folders.
- Known quirk (KDE bugs 487916 and 514150): `disable` can report "stopped" while a busy `baloo_file` keeps running. If it's still hot a few minutes later, a plain `kill` on that user process finishes the job. It won't come back because indexing is now disabled.
- One field report traced endless extractor CPU to a single corrupt PDF. If it's always the extractor, ask whether something odd landed in their home folder recently.

### Power profile stuck on "power-saver"

- Linux's Low Power Mode. Ubuntu ships `power-profiles-daemon`; Fedora 41+ ships `tuned-ppd`, which answers to the same `powerprofilesctl` command.
- Check: `powerprofilesctl get` (read-only). `power-saver` on a plugged-in machine is the classic ankle-weights mistake.
- Fix (no sudo, reversible): `powerprofilesctl set balanced`, or the quick-settings menu in the top bar.

---

## Tier 2 — Common secondary causes

### Browsers and Electron apps

- Chrome/Chromium/Firefox with 30+ tabs, plus Slack, Discord, VS Code, Teams-for-web wrappers. Each Electron app is a whole browser.
- Firefox: `about:processes` shows per-tab cost. Chrome: Shift+Esc.
- Snap and Flatpak browsers are a little heavier on first launch; that's not a villain, just packaging.

### GNOME Shell extensions

- `gnome-shell` itself high CPU (it is also the compositor, like macOS `WindowServer`) often means a misbehaving extension.
- Read-only: `gnome-extensions list --enabled`.
- Reversible fix: `gnome-extensions disable <uuid>` one at a time, re-measure, re-enable the innocent ones with `gnome-extensions enable <uuid>`.

### journald grown huge

- Check: `journalctl --disk-usage` (read-only). Default caps are a percentage of the disk, so on a big disk it can sit at several GB. A crash-looping service can also flood it.
- Not a speed issue unless the disk is nearly full; then it's an easy win. Fix block in `fix-blocks-linux.md` (it's the tool's own vacuum command; it removes old logs only).

### Old kernels piling up

- Ubuntu: `dpkg --list 'linux-image-*' | grep ^ii`. Fedora: `rpm -q kernel-core`.
- Fedora keeps 3 by default (`installonly_limit`); Ubuntu keeps whatever `apt autoremove` hasn't swept. Each one is a few hundred MB in `/boot` and `/lib/modules`, and a full `/boot` breaks updates.
- Always note the running kernel (`uname -r`) in the report. The package managers never remove it, and Janitor never asks them to.

### Unused Flatpak runtimes

- Every Flatpak app pulls a runtime (GNOME 47, 48, 49, KDE 6.x, freedesktop...). Uninstall the app and the runtime often stays.
- Read-only: `flatpak list --runtime` and `du -sh /var/lib/flatpak ~/.local/share/flatpak 2>/dev/null`.
- Fix: `flatpak uninstall --unused` lists what it would remove and asks before doing it. Give it as a block.

### Package caches

- APT: `/var/cache/apt/archives` (`du -sh`). DNF: `/var/cache/libdnf5` on Fedora 41+ (older: `/var/cache/dnf`).
- Fix: `sudo apt clean` or `sudo dnf clean packages`. These are downloaded installers only, re-downloadable at will.

### Huge Downloads folder / thumbnail cache

- `du -sh ~/Downloads ~/.cache/thumbnails`. Same as Mac and Windows: old ISOs, AppImages, `.deb`/`.rpm` installers, video exports.
- Move to Trash with `gio trash <file>` (recoverable from the Files trash), never `rm`.

### Orphaned Playwright / MCP browser sessions

- Same pattern as macOS: `chromium` / `chrome` processes with `ms-playwright` or `mcp-chrome` in the command line, left behind by a prior Claude Code session.
- Detection: `ps ax | grep -i 'mcp-chrome\|ms-playwright' | grep -v grep`.
- Fix: `pkill -f "ms-playwright/mcp-chrome"`. Match the profile path, never a bare browser name.

---

## Tier 3 — Less common but worth checking

- `systemctl --failed` and `systemctl --user --failed`: a unit in a restart loop burns CPU forever. Report it; the fix depends on what it is.
- `kswapd0` high CPU = genuine memory pressure. Confirm with `free -h` and `/proc/pressure/memory`. The fix is closing things or more RAM, not tuning swappiness.
- `unattended-upgrades`, `fwupd`, `apt.systemd.daily`, `dnf-makecache`: transient. Wait and re-measure.
- `evolution-data-server` / `evolution-calendar-factory` busy on machines with a big online calendar account. Usually settles.
- Mechanical HDD as the system disk: `lsblk -d -o NAME,ROTA,SIZE,MODEL` shows `ROTA 1`. Same gentle message as Windows: an SSD would do more than anything Janitor can.
- Duplicate formats of the same app (the snap AND the Flatpak AND the .deb of Firefox or Spotify) all auto-starting. Report; let the user pick which one stays.
- Autostart entries in `~/.config/autostart/` from apps long gone.

---

## Developer disk hogs (Linux)

Same rules as every OS: report sizes first, the tool's own clean command is a block the user runs, models are never touched without a per-item yes, `node_modules` is report-only, and **Docker is out of scope** (its images, volumes and build cache belong to Docker's own tooling; Janitor doesn't measure or clean them, just says so).

| Hog | Where / how to measure (read-only) | Notes |
|---|---|---|
| npm cache | `du -sh "$(npm config get cache)"` | Usually `~/.npm` |
| pnpm store | `du -sh "$(pnpm store path)"` | Shared across projects; prune only removes unreferenced packages |
| Yarn cache | `du -sh "$(yarn cache dir 2>/dev/null)"` | Yarn 1; Yarn 2+ keeps per-project caches |
| pip cache | `du -sh "$(pip cache dir)"` | |
| uv cache | `du -sh "$(uv cache dir)"` | Default `~/.cache/uv` |
| Hugging Face hub | `du -sh ~/.cache/huggingface/hub` and `hf cache ls` | Models. Report only. `~/.cache/huggingface/datasets` is separate and not covered by `hf cache` |
| Ollama models | `du -sh ~/.ollama/models /usr/share/ollama/.ollama/models 2>/dev/null` and `ollama list` | The standard Linux installer runs as the `ollama` user, so models usually live under `/usr/share/ollama/.ollama/models`. `OLLAMA_MODELS` overrides it |
| LM Studio models | `du -sh ~/.lmstudio/models` | Older installs used `~/.cache/lm-studio/models`. The My Models tab shows the real path |
| Old `node_modules` | `find ~ -maxdepth 6 -type d -name node_modules -prune -mtime +90 2>/dev/null \| head -30`, then `du -sh` each | **Report only.** Janitor never moves these; the user decides per project |
| Playwright browsers | `du -sh ~/.cache/ms-playwright` | Re-downloadable, but only the user knows which versions their projects pin |

Fix blocks for every row are in `fix-blocks-linux.md`.

---

## What to watch for in diagnostic output

### CPU
- Any process over 40% CPU that isn't something the user is actively using = suspect.
- Clusters: `localsearch*`, `baloo*`, `snap*`, `packagekitd` + `gnome-software`. Sum them.
- `gnome-shell` or `kwin_wayland` > 30% at idle = extension, too many windows, or a GPU driver problem.
- Load average works like on a Mac: healthy is below the core count (`nproc`), and the 1/5/15-minute numbers converging means things have settled.

### Memory
- Read `free -h` by the **available** column, not "free". Linux fills spare RAM with cache on purpose.
- `/proc/pressure/memory` (PSI): `some avg10` above ~10 means tasks are regularly waiting on memory. Near 0 = fine.
- Swap in heavy use plus `kswapd0` hot = real pressure. Fedora uses zram by default, so "swap used" there is compressed RAM and less alarming.

### Disk
- `/` over 90% or `/boot` over 80% is worth fixing before anything else; package updates start failing.
- `ROTA 1` in `lsblk` on the system disk = spinning drive, hardware floor.

---

## Quick reference — what each symptom means

| Symptom | Likely cause | Quick check |
|---|---|---|
| `localsearch-3` / `tracker-miner-fs-3` hot for hours | GNOME indexer looping | `localsearch status` |
| `baloo_file*` hot | KDE indexer | `balooctl6 status` |
| `snapd` hot, snap commands slow | Refresh or profile-regeneration loop | `snap changes`, `systemd-cgtop -d 5` |
| `packagekitd` + `gnome-software` busy | Background update refresh | Wait 10 min, re-check |
| `gnome-shell` hot at idle | Extension misbehaving | `gnome-extensions list --enabled` |
| `kswapd0` hot | Out of RAM | `free -h`, `/proc/pressure/memory` |
| Everything slow on battery | Power profile on power-saver | `powerprofilesctl get` |
| `/boot` full, updates fail | Old kernels | `dpkg --list 'linux-image-*'` or `rpm -q kernel-core` |
| `mcp-chrome` processes hot | Orphaned Playwright session | `pkill -f ms-playwright/mcp-chrome` |

---

## Expected final state of a healthy Linux desktop

- Load average 1/5/15 below `nproc` and within ~10% of each other
- Top CPU process is something the user is actively using
- `available` memory comfortably above 15% of total, memory PSI near 0
- No indexer (`localsearch*`, `baloo*`) pinned for more than a few minutes
- No snap change stuck in "Doing"
- Power profile `balanced` or `performance` when plugged in
- `/` under 85% used, `/boot` under 80%
- Journal under ~1 GB on a typical desktop
