import argparse
import logging
from dataclasses import dataclass


@dataclass(init=False)
class Args:
    host: str
    port: int
    log_level: str
    db_file: str

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--host",
            default="0.0.0.0",
            help="Hostname or IP address to listen on",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8080,
            help="Port to lisen on",
        )
        parser.add_argument(
            "--log-level",
            type=str.upper,
            choices=logging._nameToLevel.keys(),
            default="INFO",
            help="Level set for the default logger",
        )
        parser.add_argument(
            "--db-file",
            default="db.sqlite3",
            help="Path to sqlite database file",
        )
        parser.parse_args(namespace=self)
