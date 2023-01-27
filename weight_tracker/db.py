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
        raise NotImplementedError

    @abstractmethod
    def get_record(self, date: datetime.date) -> Record | None:
        raise NotImplementedError

    @abstractmethod
    def get_records(self) -> Records:
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
        return Record(date=date, value=record)

    def get_records(self) -> Records:
        return Records(
            [Record(date=date, value=value) for date, value in self.db.items()]
        )


class SQLiteRecordDB(RecordDB):
    def __init__(self, con: Connection) -> None:
        self.con = con
        cur = con.cursor()
        result = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='record'"
        ).fetchone()
        if not result:
            cur.execute("CREATE TABLE record(date, value)")

    def add_record(self, record: Record):
        existing_record = self.get_record(record.date)
        if existing_record is not None:
            raise ConflictingEntryError

        cur = self.con.cursor()
        cur.execute(
            f"""
                INSERT INTO record VALUES
                ('{record.date.isoformat()}', '{record.value}')
            """
        )
        self.con.commit()

    def get_record(self, date: datetime.date) -> Record | None:
        cur = self.con.cursor()
        result = cur.execute(
            f"SELECT * FROM record WHERE date='{date.isoformat()}'"
        ).fetchone()
        if not result:
            return None
        return Record(*result)

    def get_records(self) -> Records:
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM record").fetchall()
        return Records(records=[Record(*record) for record in result])
