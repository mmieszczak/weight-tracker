import datetime
import json
import logging
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from .db import ConflictingEntryError, RecordDB
from .schema import Record


class HTTPError(Exception):
    def __init__(self, code: int, message: str | None = None) -> None:
        self.code = code
        self.message = message
        return super().__init__(message)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, database: RecordDB, **kwargs) -> None:
        self.db = database
        super().__init__(*args, **kwargs)

    def respond_with_json(self, data: dict):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        try:
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except Exception as ex:
            logging.exception(ex)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)

    def read_json_body(self) -> dict | None:
        if self.headers.get("Content-Type") != "application/json":
            return None
        length = int(self.headers["Content-Length"])
        body_data = self.rfile.read(length)
        return json.loads(body_data)

    def do_GET(self) -> None:
        if self.path == "/records":
            records = self.db.get_records()
            records.records.sort(key=lambda r: r.date)
            self.respond_with_json(records.to_dict())
            return
        if self.path.startswith("/record"):
            url = urlparse(self.path)
            query = parse_qs(url.query)
            try:
                date = datetime.date.fromisoformat(query["date"][0])
            except (TypeError, ValueError, KeyError):
                self.send_error(HTTPStatus.BAD_REQUEST)
                self.end_headers()
                return
            record = self.db.get_record(date)

            if record is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                self.end_headers()
                return
            self.respond_with_json(record.to_dict())
            return
        return super().do_GET()

    def do_POST(self) -> None:
        if self.path == "/record":
            request_data = self.read_json_body()
            if request_data is None:
                self.send_error(HTTPStatus.BAD_REQUEST)
                return

            try:
                record = Record(**request_data)
            except (TypeError, ValueError):
                self.send_error(HTTPStatus.BAD_REQUEST)
                return

            try:
                self.db.add_record(record)
            except ConflictingEntryError:
                self.send_error(HTTPStatus.CONFLICT)
                return

            self.send_response(HTTPStatus.OK)
            self.end_headers()
            return
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()

    def do_PUT(self) -> None:
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()
