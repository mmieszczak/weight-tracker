from http.server import SimpleHTTPRequestHandler
from typing import Union

from .db import RecordDB


class HTTPError(Exception):
    def __init__(self, code: int, message: str | None = None) -> None:
        self.code = code
        self.message = message
        return super().__init__(message)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, database: Union[RecordDB, None] = None, **kwargs) -> None:
        self.db = database
        super().__init__(*args, **kwargs)
