from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any


@dataclass
class Record:
    date: datetime.date
    value: float

    @classmethod
    def from_tuple(cls, data: tuple) -> Record:
        assert len(data) == 2
        return cls(
            date=datetime.date.fromisoformat(data[0]).isoformat(),
            value=float(data[1]),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Record:
        assert "date" in data
        assert "value" in data
        return cls(
            date=datetime.date.fromisoformat(data["date"]).isoformat(),
            value=float(data["value"]),
        )


@dataclass
class Records:
    records: list[Record]
