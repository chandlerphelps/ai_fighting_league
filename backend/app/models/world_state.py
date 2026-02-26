from dataclasses import dataclass, field, asdict


@dataclass
class RivalryRecord:
    fighter1_id: str = ""
    fighter2_id: str = ""
    fights: int = 0
    fighter1_wins: int = 0
    fighter2_wins: int = 0
    draws: int = 0
    is_rivalry: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "RivalryRecord":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class WorldState:
    current_date: str = ""
    day_number: int = 0
    rankings: list[str] = field(default_factory=list)
    upcoming_events: list[str] = field(default_factory=list)
    completed_events: list[str] = field(default_factory=list)
    active_injuries: dict = field(default_factory=dict)
    rivalry_graph: list[RivalryRecord] = field(default_factory=list)
    last_daily_summary: str = ""
    event_counter: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "WorldState":
        rivalry_graph = [RivalryRecord.from_dict(r) for r in d.get("rivalry_graph", [])]
        return cls(
            current_date=d.get("current_date", ""),
            day_number=d.get("day_number", 0),
            rankings=d.get("rankings", []),
            upcoming_events=d.get("upcoming_events", []),
            completed_events=d.get("completed_events", []),
            active_injuries=d.get("active_injuries", {}),
            rivalry_graph=rivalry_graph,
            last_daily_summary=d.get("last_daily_summary", ""),
            event_counter=d.get("event_counter", 0),
        )
