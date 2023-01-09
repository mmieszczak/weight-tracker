import datetime
from abc import ABC, abstractmethod
from sqlite3 import Connection

from .schema import Record, Records


class DBError(Exception):
    ...


class MissingEntryError(DBError):
    ...


class ConflictingEntryError(DBError):
    ...


class RecordDB(ABC):
    @abstractmethod
    def add_record(self, record: Record):
        ...

    @abstractmethod
    def update_record(self, record: Record):
        ...

    @abstractmethod
    def get_record(self, date: datetime.date) -> Record:
        ...

    @abstractmethod
    def get_records(self) -> list[Record]:
        ...


class InMemoryRecordDB(RecordDB):
    def __init__(self) -> None:
        self.db: dict[datetime.date, float] = {}

    def add_record(self, record: Record):
        if record.date in self.db:
            raise ValueError(f"Entry for {record.date} already present")
        self.db[record.date] = record.value

    def update_record(self, record: Record):
        if record.date not in self.db:
            raise ValueError(f"Entry for {record.date} does not exist")
        self.db[record.date] = record.value

    def get_record(self, date: datetime.date) -> Record:
        return Record(date=date, value=self.db[date])

    def get_records(self) -> Records:
        return Records(
            [Record(date=date, value=value) for date, value in self.db.items()]
        )


class FileRecordDB(RecordDB):
    def __init__(self, con: Connection) -> None:
        self.con = con
        cur = con.cursor()
        res = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='record'"
        ).fetchone()
        if not res:
            cur.execute("CREATE TABLE record(date, value)")

    def add_record(self, record: Record):
        cur = self.con.cursor()
        cur.execute(
            f"""
                INSERT INTO record VALUES
                ('{record.date.isoformat()}', '{record.value}')
            """
        )
        self.con.commit()

    def update_record(self, record: Record):
        ...

    def get_record(self, date: datetime.date) -> Record:
        cur = self.con.cursor()
        res = cur.execute(f"SELECT * FROM record WHERE date='{date.isoformat()}'").fetchone()
        record = Record.from_tuple(res)
        if not Record:
            raise MissingEntryError(f"No record for date {date.isoformat()}")
        return record

    def get_records(self) -> Records:
        cur = self.con.cursor()
        res = cur.execute("SELECT * FROM record").fetchall()
        return Records(records=list(map(Record.from_tuple, res)))
