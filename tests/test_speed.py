import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.speed import SpeedController


def test_initial_speed():
    sc = SpeedController()
    assert sc.speed == 1


def test_speed_up():
    sc = SpeedController()
    assert sc.speed_up() == 2
    assert sc.speed == 2


def test_speed_up_max():
    sc = SpeedController()
    for _ in range(12):
        sc.speed_up()
    assert sc.speed == 10


def test_speed_down():
    sc = SpeedController()
    sc.speed_up()
    sc.speed_up()
    assert sc.speed_down() == 2
    assert sc.speed == 2


def test_speed_down_min():
    sc = SpeedController()
    sc.speed_down()
    assert sc.speed == 1


def test_tick_no_offset_at_1x():
    sc = SpeedController()
    sc.tick(["s1"])
    assert sc.get_offset("s1") == 0.0


def test_tick_offset_at_2x():
    sc = SpeedController()
    sc.speed_up()
    sc.tick(["s1"])
    assert sc.get_offset("s1") == 1.0
    sc.tick(["s1"])
    assert sc.get_offset("s1") == 2.0


def test_tick_offset_at_10x():
    sc = SpeedController()
    for _ in range(9):
        sc.speed_up()
    assert sc.speed == 10
    sc.tick(["s1"])
    assert sc.get_offset("s1") == 9.0


def test_clear_offset():
    sc = SpeedController()
    sc.speed_up()
    sc.tick(["s1"])
    sc.clear_offset("s1")
    assert sc.get_offset("s1") == 0.0


def test_reset():
    sc = SpeedController()
    sc.speed_up()
    sc.tick(["s1"])
    sc.reset()
    assert sc.speed == 1
    assert sc.get_offset("s1") == 0.0


def test_multiple_sessions():
    sc = SpeedController()
    sc.speed_up()
    sc.speed_up()  # 3x
    sc.tick(["s1", "s2"])
    assert sc.get_offset("s1") == 2.0
    assert sc.get_offset("s2") == 2.0
    sc.tick(["s1"])
    assert sc.get_offset("s1") == 4.0
    assert sc.get_offset("s2") == 2.0


def test_offset_untracked_session():
    sc = SpeedController()
    assert sc.get_offset("nonexistent") == 0.0


def test_clear_nonexistent_offset():
    sc = SpeedController()
    sc.clear_offset("nonexistent")  # should not raise


def test_speed_change_mid_tick():
    sc = SpeedController()
    sc.speed_up()  # 2x
    sc.tick(["s1"])
    assert sc.get_offset("s1") == 1.0
    sc.speed_up()  # 3x
    sc.tick(["s1"])
    assert sc.get_offset("s1") == 3.0  # 1 + 2
    sc.speed_down()  # 2x
    sc.tick(["s1"])
    assert sc.get_offset("s1") == 4.0  # 3 + 1
