import logging
import os
import sqlite3
from contextlib import ExitStack, suppress
from http.server import HTTPServer

from . import handler, static
from .args import Args
from .db import SQLiteRecordDB


def handler_class_factory(con: sqlite3.Connection, directory: str):
    database = SQLiteRecordDB(con)

    class Handler(handler.Handler):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, database=database, directory=directory, **kwargs)

    return Handler


def main():
    args = Args()
    host, port = args.host, args.port
    static_dir = os.path.dirname(static.__file__)
    log_level = logging._nameToLevel[args.log_level]
    logging.basicConfig(level=log_level)
    logging.debug(f"CLI arguments: {args}")

    with ExitStack() as stack:
        stack.enter_context(suppress(KeyboardInterrupt))
        connection = stack.enter_context(sqlite3.connect(args.db_file))
        Handler = handler_class_factory(connection, static_dir)

        logging.info(f"Running HTTP server at {host}:{port}")
        httpd = stack.enter_context(HTTPServer((host, port), Handler))
        httpd.serve_forever()

    logging.info("Exiting. Bye...")


if __name__ == "__main__":
    main()
