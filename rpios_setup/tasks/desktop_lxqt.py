from __future__ import annotations
import os, json
from jinja2 import Template
from .base import Task
from ..utils import expand

class DesktopLXQt(Task):
    name = "desktop_lxqt"

    def check(self):
        dcfg = self.cfg.get("desktop", {})
        if not dcfg:
            return True, False, "no desktop config"
        # simplistic check: ensure autostart entries exist
        missing = []
        for app in dcfg.get("autostart", []):
            name = app["name"].replace(" ", "_") + ".desktop"
            path = expand(f"~/.config/autostart/{name}")
            if not os.path.exists(path):
                missing.append(name)
        # panel conf check
        panel = dcfg.get("lxqt", {}).get("panel", {})
        panel_conf = expand("~/.config/lxqt/panel.conf")
        if panel and not os.path.exists(panel_conf):
            missing.append("panel.conf")
        if missing:
            return False, True, f"missing: {', '.join(missing)}"
        return True, False, "desktop entries present"

    def apply(self):
        dcfg = self.cfg.get("desktop", {})
        os.makedirs(expand("~/.config/autostart"), exist_ok=True)
        # Autostart entries
        for app in dcfg.get("autostart", []):
            name = app["name"].replace(" ", "_") + ".desktop"
            path = expand(f"~/.config/autostart/{name}")
            content = self._desktop_entry(app["name"], app.get("exec",""), app.get("comment",""), app.get("enabled", True))
            with open(path, "w") as f:
                f.write(content)
        # Panel template (very simple demo)
        entries = dcfg.get("lxqt", {}).get("panel", {}).get("entries", [])
        if entries:
            os.makedirs(expand("~/.config/lxqt"), exist_ok=True)
            panel_conf = expand("~/.config/lxqt/panel.conf")
            from_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates", "lxqt", "panel.conf.j2")
            with open(from_path, "r") as f:
                tpl = Template(f.read())
            with open(panel_conf, "w") as f:
                f.write(tpl.render(entries=entries))
        return True, "desktop configured"

    def _desktop_entry(self, name, exec_cmd, comment, enabled):
        return f"""[Desktop Entry]
Type=Application
Name={name}
Comment={comment}
Exec={exec_cmd}
X-GNOME-Autostart-enabled={'true' if enabled else 'false'}
"""
