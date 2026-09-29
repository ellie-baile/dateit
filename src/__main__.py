# Author Ellie Baile
# Created: 19-03-2026
import argparse
import re
import sys
import time
from collections.abc import Iterable
from pathlib import Path


class Logger:
    def __init__(self, verbose: bool) -> None:
        self.verbose: bool = verbose
        self.errors: int = 0

    def info(self, message: str) -> None:
        if self.verbose:
            print(message)

    def error(self, message: str) -> None:
        print("Error: " + message, file=sys.stderr)
        self.errors += 1

    def has_errored(self) -> bool:
        return self.errors > 0


def get_file_creation_time(path: Path) -> time.struct_time | None:
    try:
        result = path.stat()
        return time.gmtime(int(min(result.st_atime, result.st_mtime, result.st_ctime)))
    except OSError:
        return None


def prefix_path_name(path: Path, prefix: str) -> Path:
    if path.name.startswith("."):
        return path.with_name(f".{prefix} {path.name[1:]}")
    else:
        return path.with_name(f"{prefix} {path.name}")


def parse_date(date: str) -> str:
    try:
        parsed_date = time.strptime(date, "%y-%m-%d")

        return time.strftime("%y-%m-%d", parsed_date)
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid date format")


def main(
    paths: Iterable[Path],
    verbose: bool = False,
    include_hidden_files: bool = False,
    custom_date: str | None = None,
) -> int:
    logger = Logger(verbose)

    for path in paths:
        if not path.exists():
            logger.error(f"Skipping {path}; doesn't exist.")
            continue

        if path.name.startswith(".") and not include_hidden_files:
            logger.info(f"Skipping {path}; it's hidden.")
            continue

        prepend_string: str

        if re.match(r"^\.?\d{2}-\d{2}-\d{2}", path.name):
            logger.info(f"Skipping {path}; date already present.")
            continue

        if custom_date:
            prepend_string = custom_date
        else:
            if creation_time := get_file_creation_time(path):
                prepend_string = time.strftime("%y-%m-%d", creation_time)
            else:
                logger.error(f"Skipping {path}; cannot determine creation date.")
                continue

        new_file_path = prefix_path_name(path, prepend_string)

        if new_file_path.exists():
            logger.error(f"Skipping {path}; renamed file exists.")
            continue

        try:
            path.replace(new_file_path)
            logger.info(f"Renamed '{path.name}' to '{new_file_path.name}'")
        except OSError as exception:
            logger.error(f"Skipping {path}; {exception}")

    return 1 if logger.has_errored() else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="%(prog) [OPTIONS] FILES...",
        description="Tries to guess the file creation date and add it to the start of the filename."
    )
    parser.add_argument("paths", nargs="*", metavar="FILES", type=Path)
    parser.add_argument("-v", "--verbose", action="store_true", help="Output extra information", dest="verbose")
    parser.add_argument("-d", "--date", metavar="DATE", type=parse_date, help="A custom date to prepend (YY-MM-DD)", dest="date")
    parser.add_argument("--hidden", action="store_true", help="Also prepend dates to hidden files", dest="include_hidden_files")
    arguments = parser.parse_args()

    raise SystemExit(
        main(
            paths = arguments.paths or Path.cwd().iterdir(),
            verbose = arguments.verbose,
            include_hidden_files = arguments.include_hidden_files,
            custom_date = arguments.date
        )
    )
