import logging
import os
import sqlite3
from contextlib import ExitStack, suppress
from http.server import HTTPServer

from . import static as static_
from .args import Args
from .db import SQLiteRecordDB
from .handler import Handler as Handler_


def handler_class_factory(con: sqlite3.Connection, directory: str):
    class Handler(Handler_):
        def __init__(self, *args, **kwargs) -> None:
            self.db = SQLiteRecordDB(con)
            super().__init__(*args, directory=directory, **kwargs)

    return Handler


def main():
    args = Args()
    host, port = args.host, args.port
    static = os.path.dirname(static_.__file__)
    log_level = logging._nameToLevel[args.log_level]
    logging.basicConfig(level=log_level)
    logging.debug(f"CLI arguments: {args}")

    with ExitStack() as stack:
        stack.enter_context(suppress(KeyboardInterrupt))
        connection = stack.enter_context(sqlite3.connect(args.db_file))
        Handler = handler_class_factory(connection, static)

        logging.info(f"Running HTTP server at {host}:{port}")
        httpd = stack.enter_context(HTTPServer((host, port), Handler))
        httpd.serve_forever()

    logging.info("Exiting. Bye...")


if __name__ == "__main__":
    main()
