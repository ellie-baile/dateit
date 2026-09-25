# Author Ellie Baile
# Created: 19-03-2026
import os
import re
import shutil
import sys
import time
from collections.abc import Iterator

from config import GenericConfig, header, trim_margin


class AppConfig(GenericConfig):
    overwrite_existing_files: bool = False
    custom_date: str | None = None
    include_hidden_files: bool = False

    @classmethod
    def print_help(cls):
        output = trim_margin(f"""
            |{header('Usage:')}
            |  {os.path.basename(sys.argv[0])} [OPTIONS] (CWD or FILES...)
            |
            |{header('Description:')}
            |  By default, tries to guess the date the file was created and prepend it to the file name.
            |
            |{header('Options:')}
            |  -h, --help:     Output this help information
            |  -v, --verbose:  Output extra information
            |  -o, --overwrite: Overwrite existing files
            |  -d DATE:        A custom date to prepend
            |      --hidden:    Also prepend dates to hidden files
        """)
        GenericConfig._print_help(output)

    def parse_option(self, option: str, remaining_options: Iterator[str]) -> bool:
        if option == "-o" or option == "--overwrite":
            self.overwrite_existing_files = True
        elif option == "-d":
            if given_date := next(remaining_options, None):
                self.custom_date = given_date
            else:
                raise SystemExit("Please specify a custom date.")
        elif option == "--hidden":
            self.include_hidden_files = True
        else:
            return False

        return True


def main(args: list[str]) -> int:
    if not args:
        AppConfig.print_help()

    arguments = iter(args)

    app = AppConfig(arguments)

    paths: list = []

    if argument := next(arguments, None):
        if argument == "CWD":
            paths = os.listdir(os.getcwd())
        else:
            paths.append(argument)
            paths.extend(argument)
    else:
        raise SystemExit("Please specify either file paths or CWD.")

    for file in paths:
        file_name = os.path.basename(file)

        if file_name.startswith(".") and not app.include_hidden_files:
            app.log(f"Skipping {file_name}; file is hidden.")
            continue

        file_path = os.path.abspath(file)

        if not os.path.exists(file_path):
            app.log(f"Skipping {file_name}; file not found")
            continue

        prepend_string: str

        if not app.custom_date:
            if re.match(r"^\d{2}-\d{2}-\d{2} ", file_name):
                app.log(f"Skipping {file_name}; date already found.")
                continue

            result = os.stat(file_path)

            prepend_time = int(min(result.st_atime, result.st_mtime, result.st_ctime))
            prepend_string = time.strftime("%y-%m-%d", time.gmtime(prepend_time))
        else:
            prepend_string = app.custom_date

        new_file_path = os.path.join(os.path.dirname(file_path), f"{prepend_string} {file_name}")

        if os.path.exists(new_file_path):
            if not app.overwrite_existing_files:
                app.log(f"Skipping {file_name}; renamed file already exists.")
                continue

            if os.path.isdir(new_file_path):
                shutil.rmtree(new_file_path)

        app.log(f"Renaming '{file_name}' to '{prepend_string} {file_name}'")

        os.replace(file_path, new_file_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(sys.argv[1:])
    )
