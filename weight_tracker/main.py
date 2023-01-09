from http.server import HTTPServer
import sqlite3

from weight_tracker.db import FileRecordDB

from .handler import Handler


def main():
    with sqlite3.connect("db.sqlite3") as con:
        handler_class = Handler
        handler_class.set_db(FileRecordDB(con))
        httpd = HTTPServer(("", 8080), handler_class)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
