from dataclasses import dataclass, field, asdict
from enum import Enum


class Position(Enum):
    STANDING = "standing"
    CLINCH = "clinch"
    GROUND = "ground"


class TickOutcome(Enum):
    HIT = "hit"
    BLOCKED = "blocked"
    DODGED = "dodged"
    COUNTER = "counter"


class FinishMethod(Enum):
    KO = "ko"
    TKO = "tko"
    SUBMISSION = "submission"


@dataclass
class EmotionalState:
    composure: float = 50.0
    confidence: float = 50.0
    rage: float = 0.0
    fear: float = 0.0
    focus: float = 50.0

    def clamp(self):
        self.composure = max(0.0, min(100.0, self.composure))
        self.confidence = max(0.0, min(100.0, self.confidence))
        self.rage = max(0.0, min(100.0, self.rage))
        self.fear = max(0.0, min(100.0, self.fear))
        self.focus = max(0.0, min(100.0, self.focus))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_stats(cls, technique: int) -> "EmotionalState":
        return cls(
            composure=min(100.0, technique / 1.2),
            confidence=50.0,
            rage=0.0,
            fear=0.0,
            focus=min(100.0, technique * 0.8),
        )


@dataclass
class FighterCombatState:
    fighter_id: str = ""
    fighter_name: str = ""

    hp: float = 100.0
    max_hp: float = 100.0
    stamina: float = 100.0
    max_stamina: float = 100.0
    mana: float = 0.0
    max_mana: float = 0.0
    guard: float = 80.0
    max_guard: float = 80.0

    position: Position = Position.STANDING
    stun_ticks: int = 0
    accumulated_damage: float = 0.0
    supernatural_debt: float = 0.0
    combo_counter: int = 0

    emotional_state: EmotionalState = field(default_factory=EmotionalState)

    power: int = 50
    speed: int = 50
    technique: int = 50
    toughness: int = 50
    supernatural: int = 0

    def snapshot(self) -> dict:
        return {
            "hp": round(self.hp, 1),
            "max_hp": round(self.max_hp, 1),
            "stamina": round(self.stamina, 1),
            "max_stamina": round(self.max_stamina, 1),
            "mana": round(self.mana, 1),
            "max_mana": round(self.max_mana, 1),
            "guard": round(self.guard, 1),
            "position": self.position.value,
            "stun_ticks": self.stun_ticks,
            "accumulated_damage": round(self.accumulated_damage, 1),
            "combo_counter": self.combo_counter,
            "supernatural_debt": round(self.supernatural_debt, 1),
            "emotions": self.emotional_state.to_dict(),
        }

    @classmethod
    def from_fighter_data(cls, fighter: dict) -> "FighterCombatState":
        stats = fighter.get("stats", {})
        power = stats.get("power", 50)
        speed = stats.get("speed", 50)
        technique = stats.get("technique", 50)
        toughness = stats.get("toughness", 50)
        supernatural = stats.get("supernatural", 0)

        max_hp = 80.0 + toughness * 0.7
        max_stamina = 80.0 + (speed + toughness) * 0.3
        max_mana = float(supernatural * 2)
        max_guard = min(100.0, technique * 0.8)

        emotions = EmotionalState.from_stats(technique)

        condition = fighter.get("condition", {})
        momentum = condition.get("momentum", "neutral")
        morale = condition.get("morale", "neutral")

        if momentum == "rising":
            emotions.confidence += 15
            emotions.composure += 10
        elif momentum == "falling":
            emotions.confidence -= 10
            emotions.fear += 10

        if morale == "high":
            emotions.focus += 10
        elif morale == "low":
            emotions.focus -= 10

        emotions.clamp()

        return cls(
            fighter_id=fighter.get("id", ""),
            fighter_name=fighter.get("ring_name", ""),
            hp=max_hp,
            max_hp=max_hp,
            stamina=max_stamina,
            max_stamina=max_stamina,
            mana=0.0,
            max_mana=max_mana,
            guard=max_guard,
            max_guard=max_guard,
            position=Position.STANDING,
            stun_ticks=0,
            accumulated_damage=0.0,
            supernatural_debt=0.0,
            combo_counter=0,
            emotional_state=emotions,
            power=power,
            speed=speed,
            technique=technique,
            toughness=toughness,
            supernatural=supernatural,
        )


@dataclass
class TickResult:
    global_tick: int = 0
    round_number: int = 1
    tick_in_round: int = 0
    attacker_id: str = ""
    defender_id: str = ""
    move_used: str = ""
    defender_move: str = ""
    result: str = ""
    damage_dealt: float = 0.0
    attacker_state_after: dict = field(default_factory=dict)
    defender_state_after: dict = field(default_factory=dict)
    finish: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RoundSummary:
    round_number: int = 1
    fighter1_id: str = ""
    fighter2_id: str = ""
    fighter1_damage_dealt: float = 0.0
    fighter2_damage_dealt: float = 0.0
    fighter1_hits_landed: int = 0
    fighter2_hits_landed: int = 0
    fighter1_hits_attempted: int = 0
    fighter2_hits_attempted: int = 0
    fighter1_blocks: int = 0
    fighter2_blocks: int = 0
    fighter1_dodges: int = 0
    fighter2_dodges: int = 0
    fighter1_hp_end: float = 0.0
    fighter2_hp_end: float = 0.0
    fighter1_stamina_end: float = 0.0
    fighter2_stamina_end: float = 0.0
    fighter1_mana_end: float = 0.0
    fighter2_mana_end: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CombatResult:
    winner_id: str = ""
    loser_id: str = ""
    method: str = ""
    final_round: int = 1
    final_tick: int = 0
    tick_log: list[TickResult] = field(default_factory=list)
    round_summaries: list[RoundSummary] = field(default_factory=list)
    fighter1_final_state: dict = field(default_factory=dict)
    fighter2_final_state: dict = field(default_factory=dict)
    seed: int = 0
