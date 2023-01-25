import sqlite3
from http.server import HTTPServer
from pathlib import Path
from threading import Thread

import pytest

from weight_tracker import db, handler


@pytest.fixture()
def in_memory_database():
    yield db.InMemoryRecordDB()


@pytest.fixture()
def sqlite_database(tmp_path: Path):
    with sqlite3.connect(tmp_path / "db.sqlite3", check_same_thread=False) as con:
        yield db.SQLiteRecordDB(con)


@pytest.fixture(params=["in_memory_database", "sqlite_database"])
def database(request):
    yield request.getfixturevalue(request.param)


@pytest.fixture()
def server(database: db.RecordDB):
    """Run HTTPServer in a separate thread for each test.
    Uses both InMemory and SQLite database implementations from fixtures.
    Database is cleared after each test.
    """

    class Handler(handler.Handler):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, database=database, **kwargs)

    http_server = HTTPServer(("0.0.0.0", 38888), Handler)
    try:
        t = Thread(target=http_server.serve_forever)
        t.daemon = True
        t.start()
        yield "localhost:38888"
    finally:
        http_server.shutdown()
