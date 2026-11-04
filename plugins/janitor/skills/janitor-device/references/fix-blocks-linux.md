# Linux fix blocks

**Last verified:** 2026-11 — update this date when you revise the fix recipes. Tested against the conventions of Ubuntu 24.04/26.04 LTS (apt, snapd, GNOME) and Fedora 43/44 (dnf5, Flatpak, GNOME or KDE Plasma 6). Other distros: the systemd, gio and Flatpak blocks are universal; the package-manager blocks are not, so match them to what `/etc/os-release` says.

Load this file when the user has approved fixes on Linux. Every `sudo` block is given to the user as plaintext. They paste it themselves. The skill never runs `sudo` directly.

---

## Rule 1 — Disable the auto-start BEFORE killing the process

Same principle as macOS and Windows. On Linux the watchdog is usually systemd (system or `--user`) or an XDG autostart `.desktop` file. Kill first and it respawns on the next socket or D-Bus poke.

1. Mask or disable the unit (`systemctl --user` needs no sudo; system units do)
2. Rename the autostart `.desktop` file to `.desktop.disabled`
3. Then stop or kill the process
4. Re-measure to confirm it stayed down

---

## Reversible disable patterns

### systemd user units (no sudo)

```bash
# See what's running in the user session
systemctl --user list-units --type=service --state=running --no-pager

# Stop now and stop it starting again (reversible)
systemctl --user disable --now <unit>.service

# Stronger: mask, which also blocks socket/D-Bus activation through systemd
systemctl --user mask --now <unit>.service
```

Reverse with:
```bash
systemctl --user unmask <unit>.service
systemctl --user enable --now <unit>.service
```

### systemd system units (sudo, give the user a block)

```bash
sudo systemctl disable --now <unit>.service
```

Reverse with `sudo systemctl enable --now <unit>.service`. Never disable anything you can't name and explain to the user in one sentence.

### XDG autostart entries (no sudo)

```bash
ls ~/.config/autostart/
mv ~/.config/autostart/<app>.desktop ~/.config/autostart/<app>.desktop.disabled
```

Reverse by renaming back. For a system-wide entry in `/etc/xdg/autostart/`, do **not** edit it. Copy it to `~/.config/autostart/` and add `Hidden=true` to the copy; deleting the copy restores the default.

---

## Safe deletion: Trash, never `rm`

```bash
# Moves to the desktop Trash (recoverable from Files / Dolphin)
gio trash ~/Downloads/old-installer.iso

# Check what's in Trash
gio list trash://
```

If `gio` is missing (minimal installs), `mv <file> ~/.local/share/Trash/files/` works but won't record the original location. Prefer `gio`. Never `rm -rf` on user files.

---

## GNOME LocalSearch (Tracker) — calm it down

Gentle, no terminal: GNOME Settings → Search → Search Locations → switch off Downloads, dev folders and any big media drive.

Firmer, reversible, no sudo:
```bash
# Check status first
localsearch status

# Stop and mask the indexer units for this user
systemctl --user mask --now localsearch-3.service localsearch-control-3.service localsearch-writeback-3.service
```

Reverse with:
```bash
systemctl --user unmask localsearch-3.service localsearch-control-3.service localsearch-writeback-3.service
```

Tell the user: on some setups D-Bus can still wake the indexer after masking. Log out and back in, then re-check `ps -eo pcpu,comm --sort=-pcpu | head`.

Wedged index (CPU loops on files that are long gone):
```bash
# Clears the index only. Files and tags are untouched. It rebuilds on next start.
localsearch reset --filesystem
```

On releases before GNOME 47 the units and command are `tracker-miner-fs-3.service` and `tracker3 reset -s -r`.

---

## KDE Baloo — pause or turn off

```bash
balooctl6 status
balooctl6 suspend      # pause; `balooctl6 resume` to continue
balooctl6 disable      # off; `balooctl6 enable` to turn back on
```

If `baloo_file` is still hot a few minutes after `disable` (known KDE bug), end that user process:
```bash
pgrep -u "$USER" -fl baloo_file     # look first
pkill -u "$USER" -f baloo_file      # matches baloo_file and baloo_file_extractor
```

It stays down because indexing is now disabled.

---

## snapd — refresh timing, holds, retained revisions (sudo blocks)

Diagnose first (no sudo):
```bash
snap changes
systemd-cgtop -d 5
journalctl -u snapd -b --no-pager | tail -n 100
snap list --all | awk '/disabled/'
```

Give the user the block that fits:
```bash
# Refresh only overnight (reversible: `sudo snap unset system refresh.timer`)
sudo snap set system refresh.timer=00:00-04:00

# Hold all auto-refreshes for 3 days while they finish a deadline
# (reversible: `sudo snap refresh --unhold`)
sudo snap refresh --hold=72h

# Keep only 2 revisions of each snap from now on (default is 3; reversible)
sudo snap set system refresh.retain=2
```

Stuck change sitting in "Doing" for hours:
```bash
sudo snap abort <change-id>
```

Known 2026 snapd CPU loop (Ubuntu 26.04.1, profile regeneration): the fix is a newer snapd. This goes online, so it is the user's call and their command, not Janitor's:
```bash
sudo snap refresh snapd
```

---

## Software-center background downloads

GNOME (no sudo, reversible):
```bash
gsettings set org.gnome.software download-updates false
# Reverse:
gsettings reset org.gnome.software download-updates
```

KDE: System Settings → Software Update → lower the check/notification frequency.

---

## Power profile

```bash
powerprofilesctl get
powerprofilesctl set balanced
```

No sudo. Works with `power-profiles-daemon` (Ubuntu) and `tuned-ppd` (Fedora 41+).

---

## GNOME Shell extensions

```bash
gnome-extensions list --enabled
gnome-extensions disable <uuid>    # one at a time, re-measure after each
gnome-extensions enable <uuid>     # put back the innocent ones
```

---

## journald (sudo block — removes old logs only)

```bash
journalctl --disk-usage
sudo journalctl --vacuum-size=500M
```

Tell the user plainly: vacuum deletes the oldest archived logs. It is the tool's own documented cleanup and logs are not user files, but it is not reversible. If they want a permanent cap instead, that's a `SystemMaxUse=` line in a drop-in under `/etc/systemd/journald.conf.d/`, which they can remove later to undo.

---

## Old kernels (sudo blocks)

Always show `uname -r` first and say "this one stays."

Ubuntu / Debian:
```bash
dpkg --list 'linux-image-*' | grep ^ii
sudo apt autoremove --purge
```

`apt` prints the list and asks `[Y/n]`. The user reads it before saying yes.

Fedora (dnf5):
```bash
rpm -q kernel-core
sudo dnf remove --oldinstallonly
```

dnf shows the transaction and asks before removing. It never removes the running kernel.

---

## Flatpak and package caches

```bash
# Lists unused runtimes and asks before removing (user or system scope)
flatpak uninstall --unused

# Downloaded package installers only, re-downloadable
sudo apt clean
sudo dnf clean packages
```

---

## Orphaned Playwright / MCP browser cleanup

```bash
ps ax | grep -i 'mcp-chrome\|ms-playwright' | grep -v grep
pkill -f "ms-playwright/mcp-chrome" 2>/dev/null
ps ax | grep -i 'mcp-chrome' | grep -v grep || echo "all clean"
```

---

## Developer disk hogs (Linux)

Report sizes first (read-only commands are in `linux-villains.md`). Then each tool's own documented clean command goes to the user as a block. None need sudo.

```bash
# npm: verify garbage-collects the cache; clean empties it
npm cache verify
npm cache clean --force

# pnpm: removes only packages no project references
pnpm store prune

# Yarn 1
yarn cache clean

# pip
pip cache purge

# uv: prune is the safe one; clean empties everything
uv cache prune
uv cache clean

# Playwright browsers: only if the user knows no project pins these versions
gio trash ~/.cache/ms-playwright
```

### AI models — per-item yes, never bulk

Models are big, slow to re-download, and sometimes impossible to get again (pulled from a registry, gated, fine-tuned locally). Janitor lists them with sizes and the user picks, one at a time.

```bash
# Ollama: list, then remove one by name
ollama list
ollama rm <model:tag>

# Hugging Face hub cache: list, dry-run, then remove one repo
hf cache ls
hf cache rm <repo-id> --dry-run
hf cache rm <repo-id>
```

LM Studio: My Models tab → the model's menu → Delete. No terminal.

### `node_modules` — report only

Show the list of inactive projects and their sizes. The user deletes or re-installs per project themselves. Janitor never moves them.

### Docker — out of scope

Say so in one line: "Docker's images, volumes and build cache are Docker's to manage. Janitor doesn't measure or touch them."

---

## What is strictly forbidden on Linux

- `rm -rf` on user files (use `gio trash`)
- Disabling SELinux (`setenforce 0`, editing `/etc/selinux/config`) or AppArmor
- Editing GRUB / systemd-boot config, kernel command line, or running `update-grub` / `grub2-mkconfig`
- Removing the running kernel, or any kernel when only one is installed
- `apt purge` / `dnf remove` of desktop meta-packages or indexer packages that drag the desktop with them
- `chmod -x` on system binaries, or editing anything under `/usr` by hand
- `curl | sh`, `wget -O- | bash`, or any network fetch by the skill
- Writing a `.sh` file and executing it (inline commands only)

---

## Quirks to know about

**`sudo` never runs silently.** Give the user the block. Same as macOS and Windows.

**`systemctl --user` needs a session bus.** Over plain SSH it may fail with "Failed to connect to bus". Tell the user to run those from a terminal inside their desktop session.

**`pgrep` on Linux does support `-E`-style regex natively** (it's the default), unlike macOS. Patterns written for the Mac still work here.

**Snap vs Flatpak vs native.** The same app can exist in all three. Check `snap list`, `flatpak list --app`, and the native package manager before declaring something "not installed."
