import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


def non_negative_int(value: str) -> int:
    integer_value = int(value)
    if integer_value < 0:
        raise ValueError("Value cannot be negative")
    return integer_value


@dataclass(init=False)
class Args:
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"
    db_file: Path = Path("db.sqlite3")

    def __init__(self, args: Sequence[str] | None = None):
        cls = self.__class__
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument(
            "--host",
            default=cls.host,
            help="Hostname or IP address to listen on",
        )
        parser.add_argument(
            "--port",
            type=non_negative_int,
            default=cls.port,
            help="Port to lisen on",
        )
        parser.add_argument(
            "--log-level",
            type=str.upper,
            choices=logging._nameToLevel.keys(),
            default=cls.log_level,
            help="Level set for the default logger",
        )
        parser.add_argument(
            "--db-file",
            type=Path,
            default=cls.db_file,
            help="Path to sqlite database file",
        )
        parser.parse_args(args, namespace=self)
