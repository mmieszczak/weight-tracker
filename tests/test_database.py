import datetime

import pytest

from weight_tracker.db import ConflictingEntryError, RecordDB
from weight_tracker.schema import Record

mk_date = datetime.date.fromisoformat


def test_add_existing(database: RecordDB):
    database.add_record(Record(mk_date("2020-03-20"), 78.9))
    with pytest.raises(ConflictingEntryError):
        database.add_record(Record(mk_date("2020-03-20"), 78.9))


def test_get_non_existing(database: RecordDB):
    assert database.get_record(mk_date("2020-03-20")) is None


def test_add_and_get(database: RecordDB):
    record = Record(mk_date("2020-05-03"), 79.9)
    database.add_record(record)
    new_record = database.get_record(record.date)
    assert new_record == record
