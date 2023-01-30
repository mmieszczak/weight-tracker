import logging
import os
from http.server import HTTPServer
from typing import Type

from . import handler, static
from .args import Args


def handler_class_factory(directory: str) -> Type[handler.Handler]:
    class Handler(handler.Handler):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, directory=directory, **kwargs)

    return Handler


def main():
    args = Args()
    host, port = args.host, args.port
    static_dir = os.path.dirname(static.__file__)
    log_level = logging._nameToLevel[args.log_level]
    logging.basicConfig(level=log_level)
    logging.debug(f"CLI arguments: {args}")

    print("hello")
    Handler = handler_class_factory(static_dir)
    httpd = HTTPServer(("localhost", 8080), Handler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
