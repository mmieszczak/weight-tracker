from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any


@dataclass
class Record:
    date: datetime.date
    value: float

    def __post_init__(self):
        assert isinstance(self.date, datetime.date)
        assert isinstance(self.value, float)

    @classmethod
    def from_tuple(cls, data: tuple) -> Record:
        assert len(data) == 2
        return cls(
            date=datetime.date.fromisoformat(data[0]),
            value=float(data[1]),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Record:
        assert "date" in data
        assert "value" in data
        return cls(
            date=datetime.date.fromisoformat(data["date"]),
            value=float(data["value"]),
        )

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "value": self.value,
        }


@dataclass
class Records:
    records: list[Record]

    def to_dict(self):
        return {"records": list(map(Record.to_dict, self.records))}
