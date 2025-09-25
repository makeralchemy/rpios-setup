from __future__ import annotations
import os
from .base import Task
from ..utils import run, expand, sha256_of_file

class WallpaperAsset(Task):
    name = "wallpaper_asset"

    def _cfg(self):
        return self.cfg.get("desktop", {}).get("wallpaper_asset", {})

    def check(self):
        cfg = self._cfg()
        if not cfg:
            return True, False, "no wallpaper asset requested"
        src = expand(cfg.get("src", ""))
        name = cfg.get("name") or os.path.basename(src)
        if not src or not os.path.exists(src):
            return False, True, f"source missing: {src}"
        dest = f"/usr/share/rpd-wallpaper/{name}"
        if os.path.exists(dest):
            try:
                if sha256_of_file(src) == sha256_of_file(dest):
                    return True, False, f"installed: {dest}"
            except Exception:
                pass
        return False, True, f"would install to {dest}"

    def apply(self):
        cfg = self._cfg()
        if not cfg:
            return True, "nothing to do"
        src = expand(cfg.get("src", ""))
        if not os.path.exists(src):
            return False, f"source not found: {src}"
        name = cfg.get("name") or os.path.basename(src)
        destdir = "/usr/share/rpd-wallpaper"
        dest = f"{destdir}/{name}"
        run(f"sudo mkdir -p {destdir}", check=False)
        rc, out, err = run(f"sudo install -m 0644 {src} {dest}")
        if rc != 0:
            return False, err or "install failed"
        return True, f"installed {dest}"
