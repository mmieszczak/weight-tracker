import sqlite3
from http.server import HTTPServer
from pathlib import Path

from weight_tracker.db import FileRecordDB

from . import static as static_
from .handler import Handler as Handler_


def main():
    static = Path(static_.__file__).parent

    class Handler(Handler_):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, directory=str(static), **kwargs)

    with sqlite3.connect("db.sqlite3") as con:
        handler_class = Handler
        handler_class.set_db(FileRecordDB(con))
        httpd = HTTPServer(("", 8080), handler_class)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
