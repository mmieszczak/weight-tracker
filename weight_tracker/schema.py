import datetime
from dataclasses import dataclass


@dataclass
class Record:
    date: datetime.date
    value: float | int

    def __post_init__(self):
        match self.date:
            case datetime.date():
                pass
            case str():
                self.date = datetime.date.fromisoformat(self.date)
            case _:
                raise TypeError(
                    f"Data argument must be a datetime.date or string, got {type(self.date)}"
                )

        match self.value:
            case float() | int():
                pass
            case str():
                self.value = float(self.value)
            case _:
                raise TypeError(
                    f"Value argument must be a float, got {type(self.value)}"
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
