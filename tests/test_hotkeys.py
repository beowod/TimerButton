import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tempfile

from src.hotkeys import HotkeyConfig, DEFAULT_BINDINGS, action_display_name, binding_display


def test_default_bindings():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "hotkeys.json"
        config = HotkeyConfig(config_path=path)
        assert config.bindings == DEFAULT_BINDINGS
        assert "speed_up" in config.bindings
        assert "speed_down" in config.bindings
        assert "pause_all" in config.bindings


def test_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "hotkeys.json"
        config = HotkeyConfig(config_path=path)
        config.set_binding("room_10", "<Control-Shift-Key-0>")
        config.save()

        config2 = HotkeyConfig(config_path=path)
        assert config2.get("room_10") == "<Control-Shift-Key-0>"


def test_remove_binding():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "hotkeys.json"
        config = HotkeyConfig(config_path=path)
        config.remove("room_1")
        assert config.get("room_1") is None


def test_update_all():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "hotkeys.json"
        config = HotkeyConfig(config_path=path)
        new_bindings = {"speed_up": "<Control-Key-plus>"}
        config.update_all(new_bindings)
        assert config.bindings == new_bindings


def test_action_display_name():
    assert action_display_name("room_1") == "Room 1"
    assert action_display_name("room_38") == "Room 38"
    assert action_display_name("speed_up") == "Speed Up"
    assert action_display_name("speed_down") == "Speed Down"


def test_binding_display():
    assert binding_display("<Control-Shift-Key-1>") == "Ctrl+Shift+1"
    assert binding_display("<Control-Shift-equal>") == "Ctrl+Shift+="
    assert binding_display("<Control-Shift-minus>") == "Ctrl+Shift+-"


def test_corrupt_config_falls_back():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "hotkeys.json"
        path.write_text("{invalid json", encoding="utf-8")
        config = HotkeyConfig(config_path=path)
        assert config.bindings == DEFAULT_BINDINGS


def test_get_nonexistent_action():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "hotkeys.json"
        config = HotkeyConfig(config_path=path)
        assert config.get("nonexistent_action") is None


def test_set_overwrites_existing():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "hotkeys.json"
        config = HotkeyConfig(config_path=path)
        config.set_binding("speed_up", "<Control-Key-x>")
        assert config.get("speed_up") == "<Control-Key-x>"


def test_save_creates_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "subdir" / "hotkeys.json"
        config = HotkeyConfig(config_path=path)
        config.save()
        assert path.exists()
