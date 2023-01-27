from dataclasses import asdict
from pathlib import Path
from typing import Any

import pytest

from weight_tracker.args import Args

DEFAULT = asdict(Args([]))


@pytest.mark.parametrize(
    ["args", "result"],
    (
        ([], {}),
        (["--port", "80"], {"port": 80}),
        (["--host", "localhost"], {"host": "localhost"}),
        (["--db-file", "/path/to/db"], {"db_file": Path("/path/to/db")}),
        (["--log-level", "DEBUG"], {"log_level": "DEBUG"}),
        (["--log-level", "INFO"], {"log_level": "INFO"}),
        (["--log-level", "WARN"], {"log_level": "WARN"}),
        (["--log-level", "ERROR"], {"log_level": "ERROR"}),
        (["--log-level", "debug"], {"log_level": "DEBUG"}),
        (["--log-level", "info"], {"log_level": "INFO"}),
        (["--log-level", "warn"], {"log_level": "WARN"}),
        (["--log-level", "error"], {"log_level": "ERROR"}),
    ),
)
def test_args(args: list[str], result: dict[str, Any]):
    assert asdict(Args(args)) == {**DEFAULT, **result}


@pytest.mark.parametrize(
    ["args"],
    (
        [["--port", "invalid port"]],
        [["--port", "-80"]],
        [["--log-level", "invalid level"]],
    ),
)
def test_invalid_args(args):
    with pytest.raises(SystemExit):
        Args(args)
