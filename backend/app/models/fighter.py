from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class FightingStyle:
    primary_style: str = ""
    secondary_style: str = ""
    signature_move: str = ""
    finishing_move: str = ""
    known_weaknesses: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "FightingStyle":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class PhysicalStats:
    strength: int = 50
    speed: int = 50
    endurance: int = 50
    durability: int = 50
    recovery: int = 50

    def total(self) -> int:
        return self.strength + self.speed + self.endurance + self.durability + self.recovery

    @classmethod
    def from_dict(cls, d: dict) -> "PhysicalStats":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class CombatStats:
    striking: int = 50
    grappling: int = 50
    defense: int = 50
    fight_iq: int = 50
    finishing_instinct: int = 50

    def total(self) -> int:
        return self.striking + self.grappling + self.defense + self.fight_iq + self.finishing_instinct

    @classmethod
    def from_dict(cls, d: dict) -> "CombatStats":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class PsychologicalStats:
    aggression: int = 50
    composure: int = 50
    confidence: int = 50
    resilience: int = 50
    killer_instinct: int = 50

    def total(self) -> int:
        return self.aggression + self.composure + self.confidence + self.resilience + self.killer_instinct

    @classmethod
    def from_dict(cls, d: dict) -> "PsychologicalStats":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class SupernaturalStats:
    arcane_power: int = 0
    chi_mastery: int = 0
    elemental_affinity: int = 0
    dark_arts: int = 0

    def total(self) -> int:
        return self.arcane_power + self.chi_mastery + self.elemental_affinity + self.dark_arts

    def has_any(self) -> bool:
        return self.total() > 0

    @classmethod
    def from_dict(cls, d: dict) -> "SupernaturalStats":
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
    alignment: str = "tweener"
    gender: str = ""
    height: str = ""
    weight: str = ""
    build: str = ""
    distinguishing_features: str = ""
    ring_attire: str = ""
    backstory: str = ""
    personality_traits: list[str] = field(default_factory=list)
    fears_quirks: list[str] = field(default_factory=list)
    fighting_style: FightingStyle = field(default_factory=FightingStyle)
    physical_stats: PhysicalStats = field(default_factory=PhysicalStats)
    combat_stats: CombatStats = field(default_factory=CombatStats)
    psychological_stats: PsychologicalStats = field(default_factory=PsychologicalStats)
    supernatural_stats: SupernaturalStats = field(default_factory=SupernaturalStats)
    record: Record = field(default_factory=Record)
    condition: Condition = field(default_factory=Condition)
    storyline_log: list[str] = field(default_factory=list)
    rivalries: list[str] = field(default_factory=list)
    last_fight_date: Optional[str] = None
    ranking: Optional[int] = None

    def total_core_stats(self) -> int:
        return (
            self.physical_stats.total()
            + self.combat_stats.total()
            + self.psychological_stats.total()
        )

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
            alignment=d.get("alignment", "tweener"),
            gender=d.get("gender", ""),
            height=d.get("height", ""),
            weight=d.get("weight", ""),
            build=d.get("build", ""),
            distinguishing_features=d.get("distinguishing_features", ""),
            ring_attire=d.get("ring_attire", ""),
            backstory=d.get("backstory", ""),
            personality_traits=d.get("personality_traits", []),
            fears_quirks=d.get("fears_quirks", []),
            fighting_style=FightingStyle.from_dict(d.get("fighting_style", {})),
            physical_stats=PhysicalStats.from_dict(d.get("physical_stats", {})),
            combat_stats=CombatStats.from_dict(d.get("combat_stats", {})),
            psychological_stats=PsychologicalStats.from_dict(d.get("psychological_stats", {})),
            supernatural_stats=SupernaturalStats.from_dict(d.get("supernatural_stats", {})),
            record=Record.from_dict(d.get("record", {})),
            condition=Condition.from_dict(d.get("condition", {})),
            storyline_log=d.get("storyline_log", []),
            rivalries=d.get("rivalries", []),
            last_fight_date=d.get("last_fight_date"),
            ranking=d.get("ranking"),
        )
