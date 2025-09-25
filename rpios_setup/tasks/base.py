from __future__ import annotations
from typing import Tuple, Set

class Task:
    name = "task"
    def __init__(self, cfg: dict, tags: Set[str] | None = None):
        self.cfg = cfg
        self.tags = tags or set()

    def check(self) -> Tuple[bool, bool, str]:
        """Return (ok/present, changed?, message). `changed` here is informational."""
        raise NotImplementedError

    def apply(self) -> Tuple[bool, str]:
        raise NotImplementedError

    def run(self):
        ok, _, msg = self.check()
        if ok:
            return {"task": self.name, "changed": False, "msg": msg}
        ok2, msg2 = self.apply()
        return {"task": self.name, "changed": ok2, "msg": msg2}
