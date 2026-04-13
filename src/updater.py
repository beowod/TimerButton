import json
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

    old_exe = current_exe_path()
    backup = old_exe.with_suffix(".exe.bak")

    script = (
        f'@echo off\r\n'
        f'echo Updating {EXE_ASSET_NAME}...\r\n'
        f'ping -n 3 127.0.0.1 >nul\r\n'
        f'if exist "{backup}" del /f "{backup}"\r\n'
        f'move /y "{old_exe}" "{backup}"\r\n'
        f'move /y "{new_exe}" "{old_exe}"\r\n'
        f'start "" "{old_exe}"\r\n'
        f'del "%~f0"\r\n'
    )

    script_path = Path(tempfile.gettempdir()) / "_timerbutton_update.bat"
    script_path.write_text(script, encoding="utf-8")

    subprocess.Popen(
        ["cmd.exe", "/c", str(script_path)],
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
        close_fds=True,
    )
