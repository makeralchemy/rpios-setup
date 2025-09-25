from __future__ import annotations
from typing import Tuple, Set, List
import shutil
from .base import Task
from ..utils import run, which

class VSCodeExtensions(Task):
    name = "vscode_extensions"

    def __init__(self, cfg: dict, tags: Set[str] | None = None):
        super().__init__(cfg, tags)
        self.cfg = cfg
        self.code_cmd = which("code") or which("code-oss") or which("codium")

    def _desired(self):
        return self.cfg.get("vscode", {}).get("extensions", {})

    def _installed(self) -> List[str]:
        if not self.code_cmd:
            return []
        rc, out, err = run(f"{self.code_cmd} --list-extensions")
        if rc != 0:
            return []
        return [line.strip() for line in out.splitlines() if line.strip()]

    def check(self) -> Tuple[bool, bool, str]:
        desired = self._desired()
        if not desired:
            return True, False, "no vscode extensions requested"
        if not self.code_cmd:
            return True, False, "vscode cli not found; skipping"
        present = set(desired.get("present", []))
        absent = set(desired.get("absent", []))
        current = set(self._installed())
        need_install = list(present - current)
        need_uninstall = list(current & absent)
        if need_install or need_uninstall:
            pieces = []
            if need_install:
                pieces.append("install: " + ", ".join(sorted(need_install)))
            if need_uninstall:
                pieces.append("uninstall: " + ", ".join(sorted(need_uninstall)))
            return False, True, "; ".join(pieces)
        return True, False, "extensions match desired state"

    def apply(self) -> Tuple[bool, str]:
        desired = self._desired()
        if not desired or not self.code_cmd:
            return True, "nothing to do"
        present = set(desired.get("present", []))
        absent = set(desired.get("absent", []))
        current = set(self._installed())
        ok = True
        msgs = []
        for ext in sorted(present - current):
            rc, out, err = run(f"{self.code_cmd} --install-extension {ext}")
            if rc != 0:
                ok = False
                msgs.append(f"{ext}: install failed: {err or out}")
            else:
                msgs.append(f"{ext}: installed")
        for ext in sorted(current & absent):
            rc, out, err = run(f"{self.code_cmd} --uninstall-extension {ext}")
            if rc != 0:
                ok = False
                msgs.append(f"{ext}: uninstall failed: {err or out}")
            else:
                msgs.append(f"{ext}: uninstalled")
        return ok, "; ".join(msgs) if msgs else "no changes"
