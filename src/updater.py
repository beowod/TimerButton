import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from src.config import APP_VERSION, GITHUB_REPO


GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
EXE_ASSET_NAME = "MotelRoomTimer.exe"


@dataclass
class ReleaseInfo:
    tag: str
    version: str
    download_url: str
    asset_size: int
    release_notes: str


def parse_version(tag: str) -> tuple[int, ...]:
    cleaned = tag.lstrip("vV")
    parts: list[int] = []
    for segment in cleaned.split("."):
        try:
            parts.append(int(segment))
        except ValueError:
            break
    return tuple(parts)


def is_newer(remote_tag: str, local_version: str) -> bool:
    return parse_version(remote_tag) > parse_version(local_version)


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def current_exe_path() -> Path:
    return Path(sys.executable)


def check_for_update() -> Optional[ReleaseInfo]:
    req = Request(GITHUB_API_URL, headers={"Accept": "application/vnd.github.v3+json"})
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError):
        return None

    tag: str = data.get("tag_name", "")
    if not tag or not is_newer(tag, APP_VERSION):
        return None

    assets = data.get("assets", [])
    for asset in assets:
        if asset.get("name") == EXE_ASSET_NAME:
            return ReleaseInfo(
                tag=tag,
                version=tag.lstrip("vV"),
                download_url=asset["browser_download_url"],
                asset_size=asset.get("size", 0),
                release_notes=data.get("body", ""),
            )
    return None


def download_update(
    release: ReleaseInfo,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> Path:
    req = Request(release.download_url)
    tmp_dir = Path(tempfile.gettempdir())
    dest = tmp_dir / f"MotelRoomTimer_{release.tag}.exe"

    with urlopen(req, timeout=120) as resp:
        total = release.asset_size or int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 65536
        with open(dest, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                if on_progress and total > 0:
                    on_progress(downloaded, total)

    if release.asset_size and dest.stat().st_size != release.asset_size:
        dest.unlink(missing_ok=True)
        raise RuntimeError("Download size mismatch; update aborted.")

    return dest


def apply_update(new_exe: Path) -> None:
    if not is_frozen():
        raise RuntimeError("Cannot self-update when running from source.")

    pid = os.getpid()
    old_exe = current_exe_path()
    backup = old_exe.parent / (old_exe.stem + ".bak")
    log = Path(tempfile.gettempdir()) / "_timerbutton_update.log"

    ps_script = f'''
$ErrorActionPreference = 'Stop'
$log = '{log}'
$appPid = {pid}
$old = '{old_exe}'
$bak = '{backup}'
$new = '{new_exe}'

"[$(Get-Date)] Update started for PID $appPid" | Out-File $log
"Waiting for PID $appPid to exit..." | Out-File $log -Append

for ($i = 0; $i -lt 30; $i++) {{
    try {{
        $p = Get-Process -Id $appPid -ErrorAction Stop
        Start-Sleep -Seconds 1
    }} catch {{
        break
    }}
}}

try {{
    Get-Process -Id $appPid -ErrorAction Stop
    "Timeout. Force killing PID $appPid" | Out-File $log -Append
    Stop-Process -Id $appPid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}} catch {{}}

"Process exited. Swapping exe..." | Out-File $log -Append
Start-Sleep -Seconds 1

if (Test-Path $bak) {{ Remove-Item $bak -Force }}

for ($r = 0; $r -lt 15; $r++) {{
    try {{
        Move-Item $old $bak -Force -ErrorAction Stop
        break
    }} catch {{
        "Retry $($r+1) - file locked" | Out-File $log -Append
        Start-Sleep -Seconds 1
    }}
}}

if (-not (Test-Path $bak)) {{
    "FAILED: could not move exe to backup" | Out-File $log -Append
    exit 1
}}

"Backup done. Installing new version..." | Out-File $log -Append

try {{
    Move-Item $new $old -Force -ErrorAction Stop
}} catch {{
    "FAILED: could not install new exe. Restoring backup." | Out-File $log -Append
    Move-Item $bak $old -Force -ErrorAction SilentlyContinue
    exit 1
}}

"Update successful." | Out-File $log -Append

# Clean up leftover _MEI* dirs from the old PyInstaller extraction.
Get-ChildItem $env:TEMP -Directory -Filter '_MEI*' -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
"Cleaned _MEI temp dirs" | Out-File $log -Append

# Write a launcher bat that will start the exe from a completely clean
# process with no PowerShell involvement whatsoever.
$launcher = Join-Path $env:TEMP "_timerbutton_launch.bat"
@"
@echo off
timeout /t 3 /nobreak >nul
start "" "$old"
"@ | Out-File $launcher -Encoding ASCII

"Launching via $launcher ..." | Out-File $log -Append
Start-Process -WindowStyle Hidden cmd.exe -ArgumentList "/c `"$launcher`""
'''

    script_path = Path(tempfile.gettempdir()) / "_timerbutton_update.ps1"
    script_path.write_text(ps_script, encoding="utf-8")

    # Use a minimal .bat wrapper to launch the PS1 in a hidden window.
    # cmd.exe /c start launches a fully detached process that survives
    # the parent's os._exit().
    bat_path = Path(tempfile.gettempdir()) / "_timerbutton_update.bat"
    bat_path.write_text(
        f'@start /b powershell.exe -ExecutionPolicy Bypass '
        f'-WindowStyle Hidden -File "{script_path}"' + '\r\n',
        encoding="utf-8",
    )

    subprocess.Popen(
        f'cmd.exe /c "{bat_path}"',
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
    )

    import time
    time.sleep(1)
    os._exit(0)
