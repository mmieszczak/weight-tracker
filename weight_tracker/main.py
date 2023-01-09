import logging
import os

from . import static
from .args import Args


def main():
    args = Args()
    host, port = args.host, args.port
    static_dir = os.path.dirname(static.__file__)
    log_level = logging._nameToLevel[args.log_level]
    logging.basicConfig(level=log_level)
    logging.debug(f"CLI arguments: {args}")


if __name__ == "__main__":
    main()
