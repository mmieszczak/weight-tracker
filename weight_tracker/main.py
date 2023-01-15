import logging
import os
import sqlite3
from http.server import HTTPServer

from . import static as static_
from .args import Args
from .db import SQLiteRecordDB
from .handler import Handler as Handler_


def main():
    args = Args()
    host, port = args.host, args.port
    static = os.path.dirname(static_.__file__)
    log_level = logging._nameToLevel[args.log_level]
    logging.basicConfig(level=log_level)
    logging.debug(f"CLI arguments: {args}")

    with sqlite3.connect(args.db_file) as con:

        class Handler(Handler_):
            def __init__(self, *args, **kwargs) -> None:
                self.db = SQLiteRecordDB(con)
                super().__init__(*args, directory=static, **kwargs)

        logging.info(f"Running HTTP server at {host}:{port}")
        httpd = HTTPServer((host, port), Handler)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Exiting. Bye...")


if __name__ == "__main__":
    main()
