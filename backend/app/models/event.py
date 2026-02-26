from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class EventMatch:
    match_id: str = ""
    fighter1_id: str = ""
    fighter1_name: str = ""
    fighter2_id: str = ""
    fighter2_name: str = ""
    completed: bool = False
    winner_id: Optional[str] = None
    method: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "EventMatch":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Event:
    id: str = ""
    date: str = ""
    name: str = ""
    matches: list[EventMatch] = field(default_factory=list)
    completed: bool = False
    summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        matches = [EventMatch.from_dict(m) for m in d.get("matches", [])]
        return cls(
            id=d.get("id", ""),
            date=d.get("date", ""),
            name=d.get("name", ""),
            matches=matches,
            completed=d.get("completed", False),
            summary=d.get("summary", ""),
        )
