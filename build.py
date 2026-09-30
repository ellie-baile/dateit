#!/usr/bin/env python
# Author Ellie Baile
# Created: 21-09-2026
import argparse
import os
import stat
import zipapp
import zipfile
from pathlib import Path

FILE_NAME = "dateit"
BUILD_ROOT = Path(__file__).resolve().parent
SOURCE_FILE_PATH = BUILD_ROOT / "src"
OUTPUT_FILE_PATH = BUILD_ROOT / f"build/{FILE_NAME}.pyz"


def create_compiled(source_path: Path, target_file: Path) -> None:
    # Create a zip with everything from the src directory.
    with zipfile.PyZipFile(str(target_file), "w") as output:
        output.writepy(str(source_path))

    # Rewrite the file with a shebang prepended.
    with open(target_file, "r+b") as output:
        contents = output.read()
        output.seek(0, os.SEEK_SET)
        output.truncate()
        output.write(b"#!/usr/bin/env python\n" + contents)

    # Make the file executable.
    os.chmod(target_file, target_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def filter_only_python_files(path: Path) -> bool:
    return path.suffix == ".py"


def create_zip_app(source_path: Path, target_file: Path) -> None:
    zipapp.create_archive(
        source=source_path,
        target=target_file,
        interpreter="/usr/bin/env python",
        filter=filter_only_python_files,
        compressed=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS]",
        description="Creates a zip app, optionally compiling the code."
    )
    parser.add_argument("-c", "--compiled", action="store_true", help="Compile the python code", dest="compiled")
    arguments = parser.parse_args()

    OUTPUT_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if arguments.compiled:
        create_compiled(SOURCE_FILE_PATH, OUTPUT_FILE_PATH)
    else:
        create_zip_app(SOURCE_FILE_PATH, OUTPUT_FILE_PATH)
