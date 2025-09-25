from __future__ import annotations
import os
from typing import Tuple
from .base import Task
from ..utils import run, expand, which

class PiAppsPresent(Task):
    name = "piapps_present"

    def _ensure_piapps(self):
        home = expand("~")
        path = os.path.join(home, ".local/share/pi-apps")
        if not os.path.exists(path):
            # install
            run("git clone https://github.com/Botspot/pi-apps ~/.local/share/pi-apps", check=False)
        # update quietly
        if os.path.exists(path):
            run("cd ~/.local/share/pi-apps && git pull --ff-only", check=False)
        return os.path.join(path, "pi-apps")

    def check(self):
        cfg = self.cfg.get("piapps", {})
        apps = cfg.get("apps", [])
        if not apps:
            return True, False, "no pi-apps requested"
        missing = []
        # naive check: look for markers under ~/.local/share/pi-apps/apps/<App>/installed
        base = expand("~/.local/share/pi-apps/apps")
        for app in apps:
            marker = os.path.join(base, app, "installed")
            if not os.path.exists(marker):
                missing.append(app)
        if missing:
            return False, True, f"missing: {', '.join(missing)}"
        return True, False, "all pi-apps present"

    def apply(self) -> Tuple[bool, str]:
        cfg = self.cfg.get("piapps", {})
        apps = cfg.get("apps", [])
        if not apps:
            return True, "nothing to install"
        binpath = self._ensure_piapps()
        ok = True
        msgs = []
        for app in apps:
            rc, out, err = run(f'bash {binpath} install "{app}"')
            if rc != 0:
                ok = False
                msgs.append(f"{app}: {err or 'install failed'}")
            else:
                msgs.append(f"{app}: installed")
        return ok, "; ".join(msgs)
