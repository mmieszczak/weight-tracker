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
        ...

    def add_record(self, record: Record):
        ...

    def get_record(self, date: datetime.date) -> Record | None:
        ...

    def get_records(self) -> Records:
        ...


class SQLiteRecordDB(RecordDB):
    def __init__(self, con: Connection) -> None:
        ...

    def add_record(self, record: Record):
        ...

    def get_record(self, date: datetime.date) -> Record | None:
        ...

    def get_records(self) -> Records:
        ...
