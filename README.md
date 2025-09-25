# rpios-setup

A small, idempotent CLI to configure Raspberry Pi OS from a declarative YAML file.  
Installs apt packages, Pi-Apps, sets desktop prefs (LXQt), manages services, wallpapers, VS Code extensions, and drops files.

## Table of Contents
- [Quick start (with Python venv)](#quick-start-with-python-venv)
- [Configuring APT and Pi-Apps](#configuring-apt-and-pi-apps)
- [Optional: Install a wallpaper file (simple approach)](#optional-install-a-wallpaper-file-simple-approach)
- [Visual Studio Code Extensions](#visual-studio-code-extensions)
- [Design Approach](#design-approach)

## Quick start (with Python venv)

```bash
# 1. Clone or unpack the repo
cd rpios-setup

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install the project in editable mode
pip install -e .

# 5. Run the CLI
rpios-setup facts
rpios-setup apply --config configs/config.sample.yml --profile base --dry-run
# If the plan looks good:
rpios-setup apply --config configs/config.sample.yml --profile base
```

When you’re done, exit the venv with `deactivate`.

## Configuring APT and Pi-Apps

You control which applications and packages are installed through the YAML config files.

### APT Packages

```yaml
apt:
  update: true        # run apt-get update first
  upgrade: false      # run apt-get upgrade
  packages:
    present:
      - git
      - curl
      - htop
      - vim
      - ffmpeg
      - python3-pip
    absent:
      - wolfram-engine   # remove this package if installed
```

- **present** → list of packages you want installed.  
- **absent** → list of packages you want explicitly removed.  
- Safe to re-run: already installed packages are skipped.

### Pi-Apps

```yaml
piapps:
  ensure_installed: true   # make sure Pi-Apps itself is installed/updated
  apps:
    - "VS Code"
    - "Audacity"
    - "Chromium Extensions Manager"
```

- Use the **exact app name** as it appears in Pi-Apps (case-sensitive).  
- The tool checks Pi-Apps’ `installed` marker so it won’t re-install unless missing.

### Full Example

```yaml
hostname: "my-pi"
timezone: "America/Los_Angeles"

services:
  enable: [ssh]
  disable: [bluetooth]

apt:
  update: true
  upgrade: false
  packages:
    present:
      - git
      - vim
      - neofetch
    absent:
      - libreoffice

piapps:
  ensure_installed: true
  apps:
    - "VS Code"
    - "Audacity"

desktop:
  wallpaper_asset:
    src: "assets/my-favorite.jpg"
    name: "my-favorite.jpg"

vscode:
  extensions:
    present:
      - ms-python.python
      - ms-toolsai.jupyter
    absent: []
```

Run with:

```bash
rpios-setup apply --config configs/myconfig.yml --profile base --dry-run
rpios-setup apply --config configs/myconfig.yml --profile base
```

## Optional: Install a wallpaper file (simple approach)

If you prefer to just drop a wallpaper into the system's shared wallpaper directory so you can pick it in the Desktop Preferences app, add:

```yaml
desktop:
  wallpaper_asset:
    src: "assets/my-favorite.jpg"   # path relative to your repo or absolute
    name: "my-favorite.jpg"         # optional; defaults to basename of src
```

This copies the file to `/usr/share/rpd-wallpaper/<name>` (requires sudo). It **does not** set the wallpaper automatically; you select it later via the desktop UI.

## Visual Studio Code Extensions

You can declare VS Code extensions to install (and optionally remove).  
The task looks for a VS Code CLI in this order: `code`, `code-oss`, `codium`. If none is found, it skips politely.

### Config

```yaml
vscode:
  extensions:
    present:
      - ms-python.python
      - ms-toolsai.jupyter
      - ms-vscode.cpptools
    absent:
      - ms-vscode.vscode-typescript-next  # example
```

### Wiring the task (one-time engine edit)

In `rpios_setup/engine.py`:

1. Import the task:

```python
from .tasks.vscode_extensions import VSCodeExtensions
```

2. Add it to the build list (e.g., after Pi-Apps):

```python
tasks.append(VSCodeExtensions(cfg, tags={"apps","vscode"}))
```

Now you can run:

```bash
rpios-setup apply --config configs/myconfig.yml --profile base --tags vscode --dry-run
rpios-setup apply --config configs/myconfig.yml --profile base --tags vscode
```

## Design Approach

This section summarizes the design principles of **rpios-setup**.

- **Declarative config → imperative execution.** YAML describes the desired state; the tool applies changes.  
- **Idempotent tasks.** Each task checks state before acting, safe to re-run.  
- **Profiles & roles.** Base + profile configs (`dev`, `media`, etc.).  
- **Dry-run + logging.** Show plan before applying; logs changes.  
- **Offline-tolerant.** Works with cached lists and pins.  
- **Python CLI.** Lightweight, task-based design.  

### Components
- Config schema (apt, pi-apps, system toggles, desktop prefs, files, services, vscode, hooks).  
- Task engine with `check()` / `apply()`.  
- CLI commands: `apply`, `diff`, `facts`, `verify`.  
- Detection of Pi model, OS, desktop (LXQt vs LXDE).  
- Safety (backups, logging, sudo).  

### Pi-Apps Integration
- Ensure Pi-Apps installed (git clone).  
- Install apps via Pi-Apps CLI.  
- Idempotent checks via markers.  

### Desktop Preferences
- LXQt: `~/.config/lxqt/` and `~/.config/autostart/`.  
- Legacy LXDE: `~/.config/lxsession/LXDE-pi/`.  
- Wallpaper handled via `wallpaper_asset` task.  

### VS Code Integration
- Uses `code`, `code-oss`, or `codium` CLI if available.  
- Supports installing/removing extensions declaratively.  
- Safe to re-run: only applies changes when needed.  

### Example Repo Layout
```
rpios-setup/
├─ rpios_setup/
│  ├─ cli.py
│  ├─ engine.py
│  ├─ facts.py
│  ├─ tasks/
│  │   ├─ piapps_present.py
│  │   ├─ wallpaper_asset.py
│  │   └─ vscode_extensions.py
│  └─ utils.py
├─ configs/
│  ├─ config.sample.yml
│  └─ profiles/
├─ templates/
└─ tests/
```
