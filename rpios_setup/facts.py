from __future__ import annotations
import os, platform, json, subprocess
from .utils import run

def detect_facts() -> dict:
    facts = {}
    facts["platform"] = platform.platform()
    facts["kernel"] = platform.release()
    # OS release
    facts["os_release"] = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip().replace('"', '')
                if "=" in line:
                    k, v = line.split("=", 1)
                    facts["os_release"][k] = v
    except FileNotFoundError:
        pass
    # Desktop
    facts["desktop"] = os.environ.get("XDG_CURRENT_DESKTOP", "")
    facts["wayland"] = bool(os.environ.get("WAYLAND_DISPLAY"))
    # Pi model if available
    rc, out, _ = run("tr -d '\\0' </proc/device-tree/model 2>/dev/null")
    facts["pi_model"] = out if rc == 0 else ""
    return facts
