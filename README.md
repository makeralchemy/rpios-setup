# rpios-setup

## Table of Contents
- [Visual Studio Code Extensions](#visual-studio-code-extensions)
  - [Config](#config)
  - [Wiring the task (one-time engine edit)](#wiring-the-task-one-time-engine-edit)



## Visual Studio Code Extensions

You can declare VS Code extensions to install (and optionally remove). The task looks for a VS Code CLI in this order: `code`, `code-oss`, `codium`. If none is found, it skips politely.

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
