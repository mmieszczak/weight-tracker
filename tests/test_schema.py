import datetime

import pytest

from weight_tracker.schema import Record


@pytest.mark.parametrize(
    ["date", "value"],
    (
        ("2023-01-22", 80),
        ("2023-01-22", 15.5),
        ("1995-12-31", "21"),
        (datetime.date(2012, 12, 21), "21"),
    ),
)
def test_valid_schema(date, value):
    record = Record(date, value)
    assert isinstance(record.date, datetime.date)
    assert isinstance(record.value, float | int)


@pytest.mark.parametrize(
    ["date", "value", "error"],
    (
        ("", "", ValueError),
        ("2023-13-45", "15.5", ValueError),
        ("2023-12-31", "qwerty", ValueError),
        ("2023-12-31", None, TypeError),
        (15, 80, TypeError),
    ),
)
def test_invalid_schema(date, value, error):
    with pytest.raises(error):
        Record(date, value)
