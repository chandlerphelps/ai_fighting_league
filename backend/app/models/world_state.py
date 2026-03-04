from dataclasses import dataclass, field, asdict
from datetime import date as _date


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

    season_number: int = 1
    season_month: int = 1
    season_day_in_month: int = 1
    tier_rankings: dict = field(default_factory=lambda: {
        "championship": [],
        "contender": [],
        "underground": [],
    })
    belt_holder_id: str = ""
    belt_history: list = field(default_factory=list)
    retired_fighter_ids: list = field(default_factory=list)
    promotion_fights: list = field(default_factory=list)
    title_fight: dict = field(default_factory=dict)
    season_champions: list = field(default_factory=list)
    scheduled_fights: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "WorldState":
        rivalry_graph = [RivalryRecord.from_dict(r) for r in d.get("rivalry_graph", [])]

        current_date = d.get("current_date", "")
        season_number = d.get("season_number", 1)
        if not current_date:
            start_year = 2024 + season_number - 1
            current_date = _date(start_year, 11, 1).isoformat()

        parsed = _date.fromisoformat(current_date)
        season_month = parsed.month
        season_day_in_month = parsed.day

        return cls(
            current_date=current_date,
            day_number=d.get("day_number", 0),
            rankings=d.get("rankings", []),
            upcoming_events=d.get("upcoming_events", []),
            completed_events=d.get("completed_events", []),
            active_injuries=d.get("active_injuries", {}),
            rivalry_graph=rivalry_graph,
            last_daily_summary=d.get("last_daily_summary", ""),
            event_counter=d.get("event_counter", 0),
            season_number=season_number,
            season_month=season_month,
            season_day_in_month=season_day_in_month,
            tier_rankings=d.get("tier_rankings", {
                "championship": [],
                "contender": [],
                "underground": [],
            }),
            belt_holder_id=d.get("belt_holder_id", ""),
            belt_history=d.get("belt_history", []),
            retired_fighter_ids=d.get("retired_fighter_ids", []),
            promotion_fights=d.get("promotion_fights", []),
            title_fight=d.get("title_fight", {}),
            season_champions=d.get("season_champions", []),
            scheduled_fights=d.get("scheduled_fights", []),
        )
