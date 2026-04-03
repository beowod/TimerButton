import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import ROOM_LAYOUT, get_all_room_numbers


def test_room_layout_dimensions():
    assert len(ROOM_LAYOUT) == 11
    for row in ROOM_LAYOUT:
        assert len(row) == 4


def test_room_layout_null_positions():
    assert ROOM_LAYOUT[0][0] is None
    null_count = sum(1 for row in ROOM_LAYOUT for cell in row if cell is None)
    assert null_count == 1


def test_room_count():
    rooms = get_all_room_numbers()
    assert len(rooms) == 43


def test_room_numbers_unique():
    rooms = get_all_room_numbers()
    assert len(rooms) == len(set(rooms))


def test_room_layout_specific_positions():
    assert ROOM_LAYOUT[0][1] == 38
    assert ROOM_LAYOUT[0][2] == 15
    assert ROOM_LAYOUT[0][3] == 13
    assert ROOM_LAYOUT[1][0] == 45
    assert ROOM_LAYOUT[10][0] == 55
    assert ROOM_LAYOUT[10][3] == 1


def test_expected_room_numbers():
    rooms = set(get_all_room_numbers())
    expected = (set(range(1, 7)) | set(range(9, 26)) | set(range(28, 39))
                | set(range(45, 56)))
    expected -= {14, 50}
    assert rooms == expected
