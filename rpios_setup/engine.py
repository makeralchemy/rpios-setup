from __future__ import annotations
import os, yaml, copy
from typing import Any, List, Dict
from .tasks.apt_present import AptPresent
from .tasks.piapps_present import PiAppsPresent
from .tasks.file_present import FilePresent
from .tasks.systemd_manage import SystemdManage
from .tasks.desktop_lxqt import DesktopLXQt
from .tasks.wallpaper_asset import WallpaperAsset
from .tasks.raspi_config import RaspiConfig
from .tasks.vscode_extensions import VSCodeExtensions
from .utils import expand

class Planner:
    def __init__(self, cfg: dict, tags: List[str] | None = None):
        self.cfg = cfg
        self.tags = set([t for t in (tags or []) if t])
        self.tasks = self._build_tasks(cfg)

    @classmethod
    def from_config(cls, path: str, profile: str = "base", tags: List[str] | None = None) -> "Planner":
        with open(path, "r") as f:
            base_cfg = yaml.safe_load(f) or {}
        # Merge profile file if present
        prof_path = os.path.join(os.path.dirname(path), "profiles", f"{profile}.yml")
        if os.path.exists(prof_path):
            with open(prof_path, "r") as f:
                prof_cfg = yaml.safe_load(f) or {}
            cfg = deep_merge(copy.deepcopy(base_cfg), prof_cfg)
        else:
            cfg = base_cfg
        return cls(cfg, tags)

    def _build_tasks(self, cfg: dict):
        tasks = []
        # Core system settings
        tasks.append(RaspiConfig(cfg, tags={"system"}))
        # Services
        tasks.append(SystemdManage(cfg, tags={"system","services"}))
        # APT
        tasks.append(AptPresent(cfg, tags={"apt","apps"}))
        # Desktop
        tasks.append(DesktopLXQt(cfg, tags={"desktop"}))
        tasks.append(WallpaperAsset(cfg, tags={"desktop","files"}))
        # Files
        tasks.append(FilePresent(cfg, tags={"files"}))
        # Pi-Apps
        tasks.append(PiAppsPresent(cfg, tags={"apps","piapps"}))
        # VSCode Extensions
        tasks.append(VSCodeExtensions(cfg, tags={"apps","vscode"}))
        return tasks

    def preflight(self):
        pass

    def render(self):
        pass

    def execute(self) -> List[dict]:
        results = []
        for task in self.tasks:
            if self.tags and self.tags.isdisjoint(task.tags):
                continue
            res = task.run()
            results.append(res)
        return results

    def summary(self) -> str:
        return "Plan complete."

def deep_merge(a: dict, b: dict) -> dict:
    out = copy.deepcopy(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        elif isinstance(v, list) and isinstance(out.get(k), list):
            out[k] = out[k] + v
        else:
            out[k] = v
    return out
