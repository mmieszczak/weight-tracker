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
        ...
