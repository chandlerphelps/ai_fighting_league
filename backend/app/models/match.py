from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class FightMoment:
    moment_number: int = 0
    description: str = ""
    attacker_id: str = ""
    action: str = ""
    image_prompt: str = ""
    image_path: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "FightMoment":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class MatchupAnalysis:
    fighter1_win_prob: float = 0.5
    fighter2_win_prob: float = 0.5
    fighter1_methods: dict = field(default_factory=dict)
    fighter2_methods: dict = field(default_factory=dict)
    key_factors: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "MatchupAnalysis":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class MatchOutcome:
    winner_id: str = ""
    loser_id: Optional[str] = None
    method: str = "ko_tko"
    round_ended: int = 3
    fighter1_performance: str = "competitive"
    fighter2_performance: str = "competitive"
    fighter1_injuries: list[dict] = field(default_factory=list)
    fighter2_injuries: list[dict] = field(default_factory=list)
    is_draw: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "MatchOutcome":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Match:
    id: str = ""
    event_id: str = ""
    date: str = ""
    fighter1_id: str = ""
    fighter1_name: str = ""
    fighter2_id: str = ""
    fighter2_name: str = ""
    analysis: Optional[MatchupAnalysis] = None
    outcome: Optional[MatchOutcome] = None
    narrative: str = ""
    moments: list[FightMoment] = field(default_factory=list)
    fighter1_snapshot: dict = field(default_factory=dict)
    fighter2_snapshot: dict = field(default_factory=dict)
    post_fight_updates: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Match":
        analysis = None
        if d.get("analysis"):
            analysis = MatchupAnalysis.from_dict(d["analysis"])
        outcome = None
        if d.get("outcome"):
            outcome = MatchOutcome.from_dict(d["outcome"])
        moments = [FightMoment.from_dict(m) for m in d.get("moments", [])]
        return cls(
            id=d.get("id", ""),
            event_id=d.get("event_id", ""),
            date=d.get("date", ""),
            fighter1_id=d.get("fighter1_id", ""),
            fighter1_name=d.get("fighter1_name", ""),
            fighter2_id=d.get("fighter2_id", ""),
            fighter2_name=d.get("fighter2_name", ""),
            analysis=analysis,
            outcome=outcome,
            narrative=d.get("narrative", ""),
            moments=moments,
            fighter1_snapshot=d.get("fighter1_snapshot", {}),
            fighter2_snapshot=d.get("fighter2_snapshot", {}),
            post_fight_updates=d.get("post_fight_updates", {}),
        )
