import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
import tempfile
from datetime import datetime, timezone

from src.models.timer import Session, format_elapsed


def test_csv_export_content():
    sessions = [
        Session(
            id="s1", room_number=10,
            start_time=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 1, 14, 0, 0, tzinfo=timezone.utc),
            total_elapsed_seconds=7200.0,
        ),
        Session(
            id="s2", room_number=20,
            start_time=datetime(2026, 1, 2, 8, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 1, 2, 9, 30, 0, tzinfo=timezone.utc),
            total_elapsed_seconds=5400.0,
        ),
    ]

    rows = []
    for s in sessions:
        start_local = s.start_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        end_local = (s.end_time.astimezone().strftime("%Y-%m-%d %H:%M:%S")
                     if s.end_time else "---")
        elapsed = (format_elapsed(s.total_elapsed_seconds)
                   if s.total_elapsed_seconds is not None else "---")
        rows.append((s.room_number, start_local, end_local, elapsed))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv",
                                     delete=False, newline="",
                                     encoding="utf-8") as f:
        path = f.name
        writer = csv.writer(f)
        writer.writerow(["Room", "Start Time", "End Time", "Elapsed"])
        for row in rows:
            writer.writerow(row)

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        lines = list(reader)

    assert lines[0] == ["Room", "Start Time", "End Time", "Elapsed"]
    assert len(lines) == 3
    assert lines[1][0] == "10"
    assert lines[1][3] == "02:00:00"
    assert lines[2][0] == "20"
    assert lines[2][3] == "01:30:00"

    Path(path).unlink()


def test_csv_default_filename_format():
    now = datetime.now()
    name = now.strftime("history_%Y-%m-%d_%H-%M-%S.csv")
    assert name.startswith("history_")
    assert name.endswith(".csv")
    assert len(name) == len("history_2026-04-03_12-00-00.csv")
