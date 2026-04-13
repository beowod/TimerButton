import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import BytesIO

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.updater import (
    parse_version, is_newer, check_for_update, download_update, ReleaseInfo,
)


def test_parse_version_basic():
    assert parse_version("v2.1.0") == (2, 1, 0)
    assert parse_version("1.0.0") == (1, 0, 0)
    assert parse_version("V3.10.2") == (3, 10, 2)


def test_parse_version_no_prefix():
    assert parse_version("2.0.0") == (2, 0, 0)


def test_parse_version_partial():
    assert parse_version("v2") == (2,)
    assert parse_version("v2.1") == (2, 1)


def test_is_newer_true():
    assert is_newer("v3.0.0", "2.1.0") is True
    assert is_newer("v2.2.0", "2.1.0") is True
    assert is_newer("v2.1.1", "2.1.0") is True


def test_is_newer_false():
    assert is_newer("v2.1.0", "2.1.0") is False
    assert is_newer("v2.0.0", "2.1.0") is False
    assert is_newer("v1.9.9", "2.1.0") is False


def test_is_newer_same():
    assert is_newer("v2.1.0", "2.1.0") is False


MOCK_RELEASE_JSON = json.dumps({
    "tag_name": "v99.0.0",
    "body": "Test release notes",
    "assets": [
        {
            "name": "MotelRoomTimer.exe",
            "browser_download_url": "https://example.com/MotelRoomTimer.exe",
            "size": 12345678,
        }
    ],
}).encode("utf-8")


@patch("src.updater.urlopen")
def test_check_for_update_found(mock_urlopen: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.read.return_value = MOCK_RELEASE_JSON
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_resp

    result = check_for_update()
    assert result is not None
    assert result.tag == "v99.0.0"
    assert result.version == "99.0.0"
    assert result.asset_size == 12345678
    assert "example.com" in result.download_url


MOCK_SAME_VERSION_JSON = json.dumps({
    "tag_name": "v2.1.0",
    "body": "",
    "assets": [],
}).encode("utf-8")


@patch("src.updater.APP_VERSION", "2.1.0")
@patch("src.updater.urlopen")
def test_check_for_update_up_to_date(mock_urlopen: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.read.return_value = MOCK_SAME_VERSION_JSON
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_resp

    result = check_for_update()
    assert result is None


@patch("src.updater.urlopen", side_effect=OSError("No network"))
def test_check_for_update_network_error(mock_urlopen: MagicMock) -> None:
    result = check_for_update()
    assert result is None


MOCK_NO_EXE_JSON = json.dumps({
    "tag_name": "v99.0.0",
    "body": "",
    "assets": [
        {"name": "SomeOtherFile.zip", "browser_download_url": "https://x.com/f", "size": 100},
    ],
}).encode("utf-8")


@patch("src.updater.urlopen")
def test_check_for_update_no_exe_asset(mock_urlopen: MagicMock) -> None:
    mock_resp = MagicMock()
    mock_resp.read.return_value = MOCK_NO_EXE_JSON
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_resp

    result = check_for_update()
    assert result is None


@patch("src.updater.urlopen")
def test_download_update(mock_urlopen: MagicMock, tmp_path: Path) -> None:
    exe_data = b"\x00" * 1024
    mock_resp = MagicMock()
    mock_resp.read = BytesIO(exe_data).read
    mock_resp.headers = {"Content-Length": str(len(exe_data))}
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_resp

    release = ReleaseInfo(
        tag="v99.0.0",
        version="99.0.0",
        download_url="https://example.com/MotelRoomTimer.exe",
        asset_size=1024,
        release_notes="",
    )

    progress_calls: list[tuple[int, int]] = []

    def on_progress(done: int, total: int) -> None:
        progress_calls.append((done, total))

    dest = download_update(release, on_progress=on_progress)
    assert dest.exists()
    assert dest.stat().st_size == 1024
    assert len(progress_calls) > 0
    assert progress_calls[-1][0] == 1024
    dest.unlink()


@patch("src.updater.urlopen")
def test_download_size_mismatch(mock_urlopen: MagicMock) -> None:
    exe_data = b"\x00" * 500
    mock_resp = MagicMock()
    mock_resp.read = BytesIO(exe_data).read
    mock_resp.headers = {"Content-Length": "500"}
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_urlopen.return_value = mock_resp

    release = ReleaseInfo(
        tag="v99.0.0",
        version="99.0.0",
        download_url="https://example.com/MotelRoomTimer.exe",
        asset_size=9999,
        release_notes="",
    )

    import pytest
    with pytest.raises(RuntimeError, match="size mismatch"):
        download_update(release)
