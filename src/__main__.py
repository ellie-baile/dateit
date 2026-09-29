# Author Ellie Baile
# Created: 19-03-2026
import argparse
import os
import re
import shutil
import time
from pathlib import Path

def parse_date(date: str) -> str:
    if re.match(r"^\d{2}-\d{2}-\d{2}$", date):
        return date
    else:
        raise argparse.ArgumentTypeError("Invalid date format")

def main() -> int:
    parser = argparse.ArgumentParser(
        usage = "%(prog) [OPTIONS] FILES...",
        description = "Tries to guess the file creation date and add it to the start of the filename."
    )
    parser.add_argument("paths", nargs="*", metavar="FILES", type=Path)
    parser.add_argument("-v", "--verbose", action="store_true", help="Output extra information", dest="verbose")
    parser.add_argument("-o", "--overwrite", action="store_true", help="Overwrite files that already exist", dest="overwrite_existing_files")
    parser.add_argument("-d", "--date", metavar="DATE", type=parse_date, help="A custom date to prepend (YY-MM-DD)", dest="date")
    parser.add_argument("--hidden", action="store_true", help="Also prepend dates to hidden files", dest="include_hidden_files")
    arguments = parser.parse_args()

    def log(message: str):
        if arguments.verbose:
            print(message)

    paths = arguments.paths or os.listdir(os.getcwd())

    for file in paths:
        file_name = os.path.basename(file)

        if file_name.startswith(".") and not arguments.include_hidden_files:
            log(f"Skipping {file_name}; file is hidden.")
            continue

        file_path = os.path.abspath(file)

        if not os.path.exists(file_path):
            log(f"Skipping {file_name}; file not found")
            continue

        prepend_string: str

        if not arguments.date:
            if re.match(r"^\d{2}-\d{2}-\d{2} ", file_name):
                log(f"Skipping {file_name}; date already found.")
                continue

            result = os.stat(file_path)

            prepend_time = int(min(result.st_atime, result.st_mtime, result.st_ctime))
            prepend_string = time.strftime("%y-%m-%d", time.gmtime(prepend_time))
        else:
            prepend_string = arguments.date

        new_file_path = os.path.join(os.path.dirname(file_path), f"{prepend_string} {file_name}")

        if os.path.exists(new_file_path):
            if not arguments.overwrite_existing_files:
                log(f"Skipping {file_name}; renamed file already exists.")
                continue

            if os.path.isdir(new_file_path):
                shutil.rmtree(new_file_path)

        log(f"Renaming '{file_name}' to '{prepend_string} {file_name}'")

        os.replace(file_path, new_file_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
