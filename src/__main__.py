# Author Ellie Baile
# Created: 19-03-2026
import argparse
import re
import stat
import sys
import time
from collections.abc import Iterable
from pathlib import Path


class Logger:
    def __init__(self, verbose: bool) -> None:
        self.verbose: bool = verbose
        self.errored: bool = False

    def info(self, message: str) -> None:
        if self.verbose:
            print(message)

    def error(self, message: str) -> None:
        print("Error: " + message, file=sys.stderr)
        self.errored = True

    def has_errored(self) -> bool:
        return self.errored


def guess_creation_time(path: Path) -> time.struct_time | None:
    try:
        result = path.stat()

        if hasattr(result, "st_birthtime"):
            return time.localtime(result.st_birthtime)

        return time.localtime(min(result.st_atime, result.st_mtime, result.st_ctime))
    except OSError:
        return None


def prefix_path_name(path: Path, prefix: str) -> Path:
    if path.name.startswith("."):
        return path.with_name(f".{prefix} {path.name[1:]}")

    return path.with_name(f"{prefix} {path.name}")


def parse_date(date: str) -> str:
    try:
        parsed_date = time.strptime(date, "%y-%m-%d")

        return time.strftime("%y-%m-%d", parsed_date)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Invalid date format") from error


def main(
    paths: Iterable[Path],
    logger: Logger,
    custom_date: str | None = None,
) -> int:
    for path in paths:
        if not path.exists(follow_symlinks=False):
            logger.error(f"Skipping {path}; doesn't exist.")
            continue

        if path.is_symlink() or path.is_junction():
            logger.info(f"Skipping {path}; it's a link.")
            continue

        if not path.is_file(follow_symlinks=False) and not path.is_dir(follow_symlinks=False):
            logger.error(f"Skipping {path}; it's not a file or directory.")
            continue

        if path.name in ["", ".."]:
            logger.error(f"Skipping {path}; it's special.")
            continue

        if re.match(r"^\.?\d{2}-\d{2}-\d{2} ", path.name):
            logger.info(f"Skipping {path}; date already present.")
            continue

        prepend_string: str

        if custom_date:
            prepend_string = custom_date
        else:
            if creation_time := guess_creation_time(path):
                prepend_string = time.strftime("%y-%m-%d", creation_time)
            else:
                logger.error(f"Skipping {path}; cannot determine creation date.")
                continue

        new_path = prefix_path_name(path, prepend_string)

        if new_path.exists(follow_symlinks=False):
            logger.error(f"Skipping {path}; renamed path exists.")
            continue

        try:
            path.replace(new_path)
            logger.info(f"Renamed '{path.name}' to '{new_path.name}'")
        except OSError as exception:
            logger.error(f"Skipping {path}; {exception}")

    return 1 if logger.has_errored() else 0


def is_hidden(path: Path) -> bool:
    if path.name.startswith("."):
        return True

    return sys.platform == "win32" and bool(path.stat(follow_symlinks=False).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)


def should_include_path(path: Path, logger: Logger) -> bool:
    try:
        if not is_hidden(path):
            return True

        logger.info(f"Skipping {path}; it's hidden.")
        return False
    except OSError:
        logger.error(f"Skipping {path}; cannot determine if hidden.")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tries to guess the path creation date and add it to the start of the filename.")
    parser.add_argument("paths", nargs="*", metavar="PATHS", type=Path)
    parser.add_argument("-v", "--verbose", action="store_true", help="Output extra information", dest="verbose")
    parser.add_argument("-d", "--date", metavar="DATE", type=parse_date, help="A custom date to prepend (YY-MM-DD)", dest="date")
    parser.add_argument("--hidden", action="store_true", help="Also prepend dates to hidden paths when no paths are given", dest="include_hidden_paths")
    arguments = parser.parse_args()

    logger = Logger(arguments.verbose)
    paths = arguments.paths

    if not paths:
        paths = Path.cwd().iterdir()

        if not arguments.include_hidden_paths:
            paths = filter(lambda path: should_include_path(path, logger), paths)

    raise SystemExit(
        main(
            paths=paths,
            logger=logger,
            custom_date=arguments.date
        )
    )
