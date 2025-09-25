from __future__ import annotations
from .base import Task
from ..utils import run

class RaspiConfig(Task):
    name = "raspi_config"

    def check(self):
        # Very light check: verify hostname matches, timezone is set (heuristic)
        changed = []
        # hostname
        desired = self.cfg.get("hostname")
        if desired:
            rc, out, _ = run("hostname")
            if out.strip() != desired:
                changed.append("hostname")
        # timezone
        tz = self.cfg.get("timezone")
        if tz:
            rc, out, _ = run("cat /etc/timezone 2>/dev/null || timedatectl show -p Timezone --value")
            if out.strip() != tz:
                changed.append("timezone")
        return (len(changed) == 0, bool(changed), "needs: " + ", ".join(changed) if changed else "ok")

    def apply(self):
        msgs = []
        # hostname
        desired = self.cfg.get("hostname")
        if desired:
            run(f"echo {desired} | sudo tee /etc/hostname >/dev/null")
            run(f"sudo hostnamectl set-hostname {desired}")
            msgs.append(f"hostname->{desired}")
        # timezone
        tz = self.cfg.get("timezone")
        if tz:
            run(f"sudo timedatectl set-timezone {tz}")
            msgs.append(f"timezone->{tz}")
        # locale
        loc = self.cfg.get("locale")
        if loc:
            # enable and set default locale
            run(f"sudo sed -i 's/^#\s*{loc}/{loc}/' /etc/locale.gen")
            run("sudo locale-gen")
            run(f"sudo update-locale LANG={loc}")
            msgs.append(f"locale->{loc}")
        # keyboard layout (console-setup)
        kb = self.cfg.get("keyboard_layout")
        if kb:
            run(f"""sudo bash -lc 'debconf-set-selections <<EOF
keyboard-configuration keyboard-configuration/layoutcode string {kb}
EOF'""")
            run("sudo dpkg-reconfigure -f noninteractive keyboard-configuration", check=False)
            msgs.append(f"keyboard->{kb}")
        # gpu_mem (bookworm uses /boot/firmware/config.txt)
        gm = self.cfg.get("gpu_mem")
        if gm:
            run("sudo sed -i '/^gpu_mem=/d' /boot/firmware/config.txt 2>/dev/null || true")
            run(f"echo 'gpu_mem={gm}' | sudo tee -a /boot/firmware/config.txt >/dev/null", check=False)
            msgs.append(f"gpu_mem->{gm}")
        return True, "; ".join(msgs) if msgs else "no changes"
