import datetime
from dataclasses import dataclass


@dataclass
class Record:
    date: datetime.date
    value: float | int

    def __post_init__(self):
        """Check field types."""
        if isinstance(self.date, str):
            self.date = datetime.date.fromisoformat(self.date)
        if not isinstance(self.date, datetime.date):
            raise TypeError

        if isinstance(self.value, str):
            self.value = float(self.value)
        if not isinstance(self.value, int | float):
            raise TypeError

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "value": self.value,
        }


@dataclass
class Records:
    records: list[Record]

    def to_dict(self):
        return {
            "records": [Record.to_dict(r) for r in self.records],
        }
