from __future__ import annotations
from .base import Task
from ..utils import run

class SystemdManage(Task):
    name = "systemd_manage"

    def check(self):
        cfg = self.cfg.get("services", {})
        enable = cfg.get("enable", [])
        disable = cfg.get("disable", [])
        if not enable and not disable:
            return True, False, "no service changes requested"
        # We won't do deep state inspection here; always report would change if any requested
        return False, True, f"would enable {enable} and disable {disable}"

    def apply(self):
        cfg = self.cfg.get("services", {})
        enable = cfg.get("enable", [])
        disable = cfg.get("disable", [])
        for s in enable:
            run(f"sudo systemctl enable --now {s}", check=False)
        for s in disable:
            run(f"sudo systemctl disable --now {s}", check=False)
        return True, "services updated"
