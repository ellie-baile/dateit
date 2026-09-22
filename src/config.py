# Author Ellie Baile
# Created: 19-03-2026
import os
import re
import sys
from abc import ABC, abstractmethod
from collections.abc import Iterator
from enum import StrEnum

__all__ = [
    "GenericConfig",
    "header",
    "trim_margin"
]

MARGIN_REGEX = re.compile(r'^\s+\|')

class TermColors(StrEnum):
    RESET = "\33[0m"
    BLUE = "\33[34m"

class GenericConfig(ABC):
    verbose_output: bool = False

    def __init__(self, options: Iterator[str]):
        for option in options:
            if option == "-h" or option == "--help":
                GenericConfig.print_help()
            elif option == "-v" or option == "--verbose":
                self.verbose_output = True
            elif self.parse_option(option):
                continue
            else: break

    @staticmethod
    def _print_help(output: str):
        os.system("")  # Hack to enable coloured output on Windows.
        print(output)
        sys.exit(0)

    @classmethod
    @abstractmethod
    def print_help(cls):
        pass

    def parse_option(self, option: str) -> bool:
        return False

    def log(self, message: str):
        if self.verbose_output: print(message)


def header(text: str) -> str:
    return f"{TermColors.BLUE}{text}{TermColors.RESET}"

def trim_margin(text: str) -> str:
    return "\n".join(
        [re.sub(MARGIN_REGEX, '', line) for line in text.splitlines()[1::] if line.rstrip()]
    )
