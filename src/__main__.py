# Author Ellie Baile
# Created: 19-03-2026
import argparse
import re
import shutil
import time
from collections.abc import Iterator
from pathlib import Path


def get_file_creation_time(path: Path) -> time.struct_time:
    result = path.stat()

    return time.gmtime(int(min(result.st_atime, result.st_mtime, result.st_ctime)))


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
    paths: Iterator[Path],
    verbose: bool = False,
    include_hidden_files: bool = False,
    custom_date: str | None = None,
) -> int:
    def log(message: str):
        if verbose:
            print(message)

    for path in paths:
        if not path.exists():
            print(f"Error: Skipping {path}; doesn't exist.")
            continue

        if path.name.startswith(".") and not include_hidden_files:
            log(f"Skipping {path}; it's hidden.")
            continue

        prepend_string: str

        if re.match(r"^\.?\d{2}-\d{2}-\d{2}", path.name):
            log(f"Skipping {path}; date already present.")
            continue

        if custom_date:
            prepend_string = custom_date
        else:
            prepend_string = time.strftime("%y-%m-%d", get_file_creation_time(path))

        new_file_path = prefix_path_name(path, prepend_string)

        if new_file_path.exists():
            print(f"Error: Skipping {path}; renamed file exists.")


        path.replace(new_file_path)
        log(f"Renamed '{path.name}' to '{new_file_path.name}'")

    return 0


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
