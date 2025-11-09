import sys
from src.helpers.manga_update import update_manga


if  __name__ == "__main__":
    start_letter = sys.argv[1] if len(sys.argv) > 1 else None
    update_manga(start_letter)
