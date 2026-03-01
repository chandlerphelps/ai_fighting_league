from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Stats:
    power: int = 50
    speed: int = 50
    technique: int = 50
    toughness: int = 50
    supernatural: int = 0

    def core_total(self) -> int:
        return self.power + self.speed + self.technique + self.toughness

    @classmethod
    def from_dict(cls, d: dict) -> "Stats":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Record:
    wins: int = 0
    losses: int = 0
    draws: int = 0
    kos: int = 0
    submissions: int = 0

    def total_fights(self) -> int:
        return self.wins + self.losses + self.draws

    def win_percentage(self) -> float:
        total = self.total_fights()
        if total == 0:
            return 0.0
        return self.wins / total

    @classmethod
    def from_dict(cls, d: dict) -> "Record":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Injury:
    type: str = ""
    severity: str = "none"
    recovery_days_remaining: int = 0

    @classmethod
    def from_dict(cls, d: dict) -> "Injury":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Condition:
    health_status: str = "healthy"
    injuries: list[Injury] = field(default_factory=list)
    recovery_days_remaining: int = 0
    morale: str = "neutral"
    momentum: str = "neutral"

    @classmethod
    def from_dict(cls, d: dict) -> "Condition":
        injuries = [Injury.from_dict(i) for i in d.get("injuries", [])]
        return cls(
            health_status=d.get("health_status", "healthy"),
            injuries=injuries,
            recovery_days_remaining=d.get("recovery_days_remaining", 0),
            morale=d.get("morale", "neutral"),
            momentum=d.get("momentum", "neutral"),
        )


@dataclass
class Fighter:
    id: str = ""
    ring_name: str = ""
    real_name: str = ""
    age: int = 25
    origin: str = ""
    gender: str = ""
    height: str = ""
    weight: str = ""
    build: str = ""
    distinguishing_features: str = ""
    iconic_features: str = ""
    ring_attire: str = ""
    ring_attire_sfw: str = ""
    ring_attire_nsfw: str = ""
    skimpiness_level: int = 2
    image_prompt: dict = field(default_factory=dict)
    image_prompt_sfw: dict = field(default_factory=dict)
    image_prompt_nsfw: dict = field(default_factory=dict)
    image_prompt_triple: dict = field(default_factory=dict)
    stats: Stats = field(default_factory=Stats)
    record: Record = field(default_factory=Record)
    condition: Condition = field(default_factory=Condition)
    storyline_log: list[str] = field(default_factory=list)
    rivalries: list[str] = field(default_factory=list)
    last_fight_date: Optional[str] = None
    ranking: Optional[int] = None

    def total_core_stats(self) -> int:
        return self.stats.core_total()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Fighter":
        return cls(
            id=d.get("id", ""),
            ring_name=d.get("ring_name", ""),
            real_name=d.get("real_name", ""),
            age=d.get("age", 25),
            origin=d.get("origin", ""),
            gender=d.get("gender", ""),
            height=d.get("height", ""),
            weight=d.get("weight", ""),
            build=d.get("build", ""),
            distinguishing_features=d.get("distinguishing_features", ""),
            iconic_features=d.get("iconic_features", ""),
            ring_attire=d.get("ring_attire", ""),
            ring_attire_sfw=d.get("ring_attire_sfw", ""),
            ring_attire_nsfw=d.get("ring_attire_nsfw", ""),
            skimpiness_level=d.get("skimpiness_level", 2),
            image_prompt=d.get("image_prompt", {}),
            image_prompt_sfw=d.get("image_prompt_sfw", {}),
            image_prompt_nsfw=d.get("image_prompt_nsfw", {}),
            image_prompt_triple=d.get("image_prompt_triple", {}),
            stats=Stats.from_dict(d.get("stats", {})),
            record=Record.from_dict(d.get("record", {})),
            condition=Condition.from_dict(d.get("condition", {})),
            storyline_log=d.get("storyline_log", []),
            rivalries=d.get("rivalries", []),
            last_fight_date=d.get("last_fight_date"),
            ranking=d.get("ranking"),
        )
