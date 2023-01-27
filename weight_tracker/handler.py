import datetime
import json
import logging
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from typing import Callable
from urllib.parse import parse_qs, urlparse

from weight_tracker.schema import Record

from .db import ConflictingEntryError, RecordDB

HandlerFunc = Callable[["Handler"], None]


class HTTPError(Exception):
    def __init__(self, code: int, message: str | None = None) -> None:
        self.code = code
        self.message = message
        return super().__init__(message)


class Handler(SimpleHTTPRequestHandler):
    _routes: dict[tuple[str, str], HandlerFunc] = {}

    def __init__(self, *args, database: RecordDB, **kwargs) -> None:
        self.db = database
        super().__init__(*args, **kwargs)

    @classmethod
    def route(cls, command: str, path: str):
        def decorator(func: HandlerFunc) -> HandlerFunc:
            cls._routes[(command, path)] = func
            return func

        return decorator

    def respond_with_json(self, data):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        try:
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as ex:  # pragma: no cover
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

    @property
    def clean_path(self) -> str:
        return urlparse(self.path).path

    def do_REQUEST(self):
        try:
            self._routes[(self.command, self.clean_path)](self)
        except HTTPError as ex:
            self.send_error(ex.code, ex.message)
        except KeyError:
            if self.command == "GET":
                return super().do_GET()
            self.send_error(HTTPStatus.NOT_FOUND)
        except Exception as ex:  # pragma: no cover
            logging.exception(ex)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    do_GET = do_REQUEST
    do_POST = do_REQUEST
    do_PUT = do_REQUEST


@Handler.route("GET", "/record")
def get_record(handler: Handler):
    url = urlparse(handler.path)
    query = parse_qs(url.query)
    try:
        date = datetime.date.fromisoformat(query["date"][0])
    except (KeyError, IndexError) as ex:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST, 'Missing "date" query parameter'
        ) from ex
    except ValueError as ex:
        raise HTTPError(HTTPStatus.BAD_REQUEST, "Invalid date format") from ex

    record = handler.db.get_record(date)
    if record is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "Record not found")
    handler.respond_with_json(record.to_dict())


@Handler.route("GET", "/records")
def get_records(handler: Handler):
    records = handler.db.get_records()
    records.records.sort(key=lambda r: r.date)
    handler.respond_with_json(records.to_dict())


@Handler.route("POST", "/record")
def post_record(handler: Handler):
    body = handler.read_json_body()
    try:
        record = Record(**body)
    except (TypeError, ValueError) as ex:
        raise HTTPError(HTTPStatus.BAD_REQUEST, "Invalid request body") from ex
    try:
        handler.db.add_record(record)
    except ConflictingEntryError as ex:
        raise HTTPError(HTTPStatus.CONFLICT, "Entry already exists") from ex
    handler.send_response(HTTPStatus.OK, "ok")
    handler.end_headers()
