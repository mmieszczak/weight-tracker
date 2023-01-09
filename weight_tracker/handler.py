from __future__ import annotations

import datetime
import json
import logging
from dataclasses import asdict
from functools import cache
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, urlparse

from weight_tracker.schema import Record

from . import static as static_
from .db import InMemoryRecordDB, RecordDB

static = Path(static_.__file__).parent


class HTTPError(Exception):
    def __init__(self, code: int, message: str | None = None) -> None:
        self.code = code
        self.message = message
        return super().__init__(message)


@cache
def index(file_name: str) -> bytes:
    file_path = (static / file_name).resolve(strict=True)
    if not file_path.is_relative_to(static):
        raise FileNotFoundError
    with open(file_path, "rb") as f:
        return f.read()


class Handler(BaseHTTPRequestHandler):
    db: RecordDB = InMemoryRecordDB()

    _get_routes: dict[str, Callable[[Handler], None]] = {}
    _put_routes: dict[str, Callable[[Handler], None]] = {}
    _post_routes: dict[str, Callable[[Handler], None]] = {}

    @classmethod
    def set_db(cls, db: RecordDB):
        cls.db = db

    @classmethod
    def GET(cls, path: str):
        def inner(func: Callable[[Handler], None]):
            cls._get_routes[path] = func

        return inner

    @classmethod
    def POST(cls, path: str):
        def inner(func: Callable[[Handler], None]):
            cls._post_routes[path] = func

        return inner

    @classmethod
    def PUT(cls, path: str):
        def inner(func: Callable[[Handler], None]):
            cls._put_routes[path] = func

        return inner

    def respond_with_file(self, file_name: str):
        headers = {}
        if file_name.endswith(".html"):
            headers["Content-Type"] = "text/html"
        elif file_name.endswith(".js"):
            headers["Content-Type"] = "application/javascript"
        self.send_response(HTTPStatus.OK)
        for header, value in headers.items():
            self.send_header(header, value)
        self.end_headers()
        try:
            self.wfile.write(index(file_name))
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND)
        except Exception:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    def respond_with_json(self, data):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        try:
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as ex:
            logging.exception(ex)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    def read_json_body(self) -> dict:
        if self.headers.get("Content-Type") != "application/json":
            raise HTTPError(
                HTTPStatus.BAD_REQUEST, "Invalid content type, expected json"
            )
        length = int(self.headers["Content-Length"])
        body_data = self.rfile.read(length)
        return json.loads(body_data)

    def do_GET(self):
        try:
            path = urlparse(self.path).path
            self._get_routes[path](self)
        except HTTPError as ex:
            self.send_error(ex.code, ex.message)
        except KeyError:
            self.respond_with_file(self.path.removeprefix("/"))
        except Exception as ex:
            logging.exception(ex)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self):
        try:
            self._post_routes[self.path](self)
        except HTTPError as ex:
            self.send_error(ex.code, ex.message)
        except KeyError:
            self.send_error(HTTPStatus.NOT_FOUND)
        except Exception as ex:
            logging.exception(ex)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_PUT(self):
        try:
            self._put_routes[self.path](self)
        except HTTPError as ex:
            self.send_error(ex.code, ex.message)
        except KeyError:
            self.send_error(HTTPStatus.NOT_FOUND)
        except Exception as ex:
            logging.exception(ex)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)


@Handler.GET("/")
def get_root(handler: Handler):
    handler.send_response(HTTPStatus.MOVED_PERMANENTLY)
    handler.send_header("Location", "/index.html")
    handler.end_headers()


@Handler.GET("/record")
def get_record(handler: Handler):
    url = urlparse(handler.path)
    query = parse_qs(url.query)
    try:
        date = datetime.date.fromisoformat(query["date"][0])
    except (KeyError, IndexError) as ex:
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Missing "date" query parameter') from ex
    except ValueError as ex:
        raise HTTPError(HTTPStatus.BAD_REQUEST, "Invalid date format") from ex
    try:
        record = handler.db.get_record(date)
    except KeyError as ex:
        raise HTTPError(HTTPStatus.NOT_FOUND, "Record not found") from ex
    handler.respond_with_json(asdict(record))


@Handler.GET("/records")
def get_records(handler: Handler):
    records = handler.db.get_records()
    handler.respond_with_json(asdict(records))


@Handler.POST("/record")
def post_record(handler: Handler):
    body = handler.read_json_body()
    try:
        record = Record.from_dict(body)
    except (AssertionError, ValueError) as ex:
        raise HTTPError(HTTPStatus.BAD_REQUEST, "Invalid request body") from ex
    handler.db.add_record(record)
    handler.send_response(HTTPStatus.OK, "ok")
    handler.end_headers()


@Handler.PUT("/record")
def put_record(handler: Handler):
    body = handler.read_json_body()
    try:
        record = Record.from_dict(body)
    except (AssertionError, ValueError) as ex:
        raise HTTPError(HTTPStatus.BAD_REQUEST, "Invalid request body") from ex
    handler.db.update_record(record)
    handler.send_response(HTTPStatus.OK, "ok")
    handler.end_headers()
