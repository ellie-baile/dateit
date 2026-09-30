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


def is_hidden(path: Path) -> bool:
    if path.name.startswith("."):
        return True

    return sys.platform == "win32" and bool(path.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)


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
    verbose: bool = False,
    include_hidden_paths: bool = False,
    custom_date: str | None = None,
) -> int:
    logger = Logger(verbose)

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

        if path == Path(".") or path == Path(".."):
            logger.error(f"Skipping {path}; it's special.")
            continue

        if not include_hidden_paths:
            try:
                if is_hidden(path):
                    logger.info(f"Skipping {path}; it's hidden.")
                    continue
            except OSError as exception:
                logger.error(f"Skipping {path}; Cannot determine hidden status: {exception}")
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS] PATHS...",
        description="Tries to guess the path creation date and add it to the start of the filename."
    )
    parser.add_argument("paths", nargs="*", metavar="PATHS", type=Path)
    parser.add_argument("-v", "--verbose", action="store_true", help="Output extra information", dest="verbose")
    parser.add_argument("-d", "--date", metavar="DATE", type=parse_date, help="A custom date to prepend (YY-MM-DD)", dest="date")
    parser.add_argument("--hidden", action="store_true", help="Also prepend dates to hidden paths", dest="include_hidden_paths")
    arguments = parser.parse_args()

    raise SystemExit(
        main(
            paths=arguments.paths or Path.cwd().iterdir(),
            verbose=arguments.verbose,
            include_hidden_paths=arguments.include_hidden_paths,
            custom_date=arguments.date
        )
    )
