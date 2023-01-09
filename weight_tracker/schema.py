import datetime
from dataclasses import dataclass


@dataclass
class Record:
    date: datetime.date
    value: float | int

    def __post_init__(self):
        """Check field types."""

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
