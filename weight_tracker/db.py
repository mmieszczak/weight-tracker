import datetime
from abc import ABC, abstractmethod
from sqlite3 import Connection

from .schema import Record, Records


class DBError(Exception):
    ...


class ConflictingEntryError(DBError):
    ...


class RecordDB(ABC):
    @abstractmethod
    def add_record(self, record: Record):
        """Add new record to the database.
        If a record with the same date exists,
        raise ConflictingEntryError.
        """
        raise NotImplementedError

    @abstractmethod
    def get_record(self, date: datetime.date) -> Record | None:
        """Get record from the database.
        If a record for given date does not exist,
        return None.
        """
        raise NotImplementedError

    @abstractmethod
    def get_records(self) -> Records:
        """Get all records from the database."""
        raise NotImplementedError


class InMemoryRecordDB(RecordDB):
    def __init__(self) -> None:
        self.db: dict[datetime.date, float] = {}

    def add_record(self, record: Record):
        if record.date in self.db:
            raise ConflictingEntryError
        self.db[record.date] = record.value

    def get_record(self, date: datetime.date) -> Record | None:
        record = self.db.get(date)
        if record is None:
            return None
        return Record(date, record)

    def get_records(self) -> Records:
        return Records(
            records=[Record(date, value) for date, value in self.db.items()],
        )


class SQLiteRecordDB(RecordDB):
    def __init__(self, con: Connection) -> None:
        ...

    def add_record(self, record: Record):
        ...

    def get_record(self, date: datetime.date) -> Record | None:
        ...

    def get_records(self) -> Records:
        ...
