import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.app import Application


def main() -> None:
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
