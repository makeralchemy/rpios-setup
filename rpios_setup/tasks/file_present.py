from __future__ import annotations
import os, shutil
from .base import Task
from ..utils import expand, ensure_mode

class FilePresent(Task):
    name = "file_present"

    def check(self):
        items = self.cfg.get("files", [])
        if not items:
            return True, False, "no files requested"
        missing = []
        for it in items:
            dest = expand(it["dest"])
            if not os.path.exists(dest):
                missing.append(dest)
        if missing:
            return False, True, f"missing: {', '.join(missing[:3])}"
        return True, False, "all files present"

    def apply(self):
        items = self.cfg.get("files", [])
        if not items:
            return True, "nothing to write"
        for it in items:
            src = it["src"]
            dest = expand(it["dest"])
            mode = it.get("mode", "0644")
            backup = it.get("backup", True)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if os.path.exists(dest) and backup:
                bak = dest + ".bak"
                shutil.copy2(dest, bak)
            shutil.copy2(src, dest)
            ensure_mode(dest, int(mode, 8))
        return True, f"deployed {len(items)} file(s)"
