from __future__ import annotations
import os, subprocess, shlex, hashlib, pathlib, stat
from typing import Tuple

def run(cmd: str, check: bool = False, env: dict | None = None) -> Tuple[int, str, str]:
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env={**os.environ, **(env or {})})
    out, err = proc.communicate()
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {cmd}\n{err}")
    return proc.returncode, out.strip(), err.strip()

def is_root() -> bool:
    return os.geteuid() == 0

def expand(p: str) -> str:
    return os.path.expandvars(os.path.expanduser(p))

def sha256_of_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def ensure_mode(path: str, mode: int):
    st = os.stat(path)
    if stat.S_IMODE(st.st_mode) != mode:
        os.chmod(path, mode)

def which(binname: str) -> str | None:
    rc, out, _ = run(f"which {shlex.quote(binname)}")
    return out if rc == 0 and out else None

def sha256_of_file(path: str) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

