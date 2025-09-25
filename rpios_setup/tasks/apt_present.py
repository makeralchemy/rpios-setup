from __future__ import annotations
from typing import Tuple, List
from .base import Task
from ..utils import run

class AptPresent(Task):
    name = "apt_present"

    def check(self) -> Tuple[bool, bool, str]:
        pkgs = self.cfg.get("apt", {}).get("packages", {}).get("present", [])
        if not pkgs:
            return True, False, "no packages requested"
        missing = []
        for p in pkgs:
            rc, _, _ = run(f"dpkg -s {p} >/dev/null 2>&1")
            if rc != 0:
                missing.append(p)
        if missing:
            return False, True, f"missing: {', '.join(missing)}"
        return True, False, "all packages present"

    def apply(self) -> Tuple[bool, str]:
        aptcfg = self.cfg.get("apt", {})
        if aptcfg.get("update", True):
            run("sudo apt-get update")
        pkgs = aptcfg.get("packages", {}).get("present", [])
        if not pkgs:
            return True, "nothing to install"
        rc, out, err = run("sudo apt-get install -y " + " ".join(pkgs))
        return (rc == 0, err if rc else f"installed: {', '.join(pkgs)}")
