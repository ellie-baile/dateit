#!/usr/bin/env python
# Author Ellie Baile
# Created: 21-09-2026
import os
import stat
import sys
import zipapp
import zipfile
from pathlib import Path

FILE_NAME = "dateit"
SOURCE_FILE_PATH = "src"
OUTPUT_FILE_PATH = f"build/{FILE_NAME}.pyz"

def create_compiled(source_path: str, target_file: str) -> None:
    # Create a zip with everything from the src directory.
    with zipfile.PyZipFile(target_file, "w") as output:
        output.writepy(source_path)

    # Rewrite the file with a shebang prepended.
    with open(target_file, "r+b") as output:
        contents = output.read()
        output.seek(0, os.SEEK_SET)
        output.truncate()
        output.write(b"#!/usr/bin/env python\n" + contents)

    # Make the file executable.
    os.chmod(target_file, os.stat(target_file).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

def filter_only_python_files(path: Path) -> bool:
    return path.full_match("**/*.py")

def create_zip_app(source_path: str, target_file: str) -> None:
    zipapp.create_archive(
        source=source_path,
        target=target_file,
        interpreter="/usr/bin/env python",
        filter=filter_only_python_files,
        compressed=True
    )

if __name__ == "__main__":
    if not os.path.exists("build"):
        os.mkdir("build")

    compiled = False

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "-c" or arg == "--compile":
                compiled = True
            else:
                print("Unknown argument:", arg)
                sys.exit(1)

    if compiled:
        create_compiled(SOURCE_FILE_PATH, OUTPUT_FILE_PATH)
    else:
        create_zip_app(SOURCE_FILE_PATH, OUTPUT_FILE_PATH)
