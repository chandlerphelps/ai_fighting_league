from dataclasses import dataclass, field
from app.engine.combat.models import Position


@dataclass
class MoveDefinition:
    id: str = ""
    name: str = ""
    category: str = "strike"
    base_damage: float = 0.0
    stamina_cost: float = 5.0
    mana_cost: float = 0.0
    speed: float = 5.0
    accuracy: float = 0.5
    block_modifier: float = 1.0
    stun_chance: float = 0.0
    stun_duration: int = 1
    position_required: list[Position] = field(default_factory=lambda: [Position.STANDING])
    position_change: Position | None = None
    stat_scaling: dict = field(default_factory=lambda: {"power": 1.0})
    stamina_damage: float = 0.0
    is_submission: bool = False
    is_finisher: bool = False
    is_signature: bool = False


UNIVERSAL_MOVES: dict[str, MoveDefinition] = {
    "jab": MoveDefinition(
        id="jab", name="Jab", category="strike",
        base_damage=5.0, stamina_cost=5.0, speed=2.0, accuracy=0.85,
        block_modifier=1.0, stun_chance=0.02,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.5, "speed": 0.5},
    ),
    "cross": MoveDefinition(
        id="cross", name="Cross", category="strike",
        base_damage=12.0, stamina_cost=10.0, speed=4.0, accuracy=0.70,
        block_modifier=0.9, stun_chance=0.08,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.8, "speed": 0.2},
    ),
    "hook": MoveDefinition(
        id="hook", name="Hook", category="strike",
        base_damage=18.0, stamina_cost=14.0, speed=6.0, accuracy=0.60,
        block_modifier=0.7, stun_chance=0.15,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.9, "speed": 0.1},
    ),
    "uppercut": MoveDefinition(
        id="uppercut", name="Uppercut", category="strike",
        base_damage=22.0, stamina_cost=16.0, speed=7.0, accuracy=0.50,
        block_modifier=0.6, stun_chance=0.30, stun_duration=2,
        position_required=[Position.STANDING],
        stat_scaling={"power": 1.0},
        is_finisher=True,
    ),
    "overhand": MoveDefinition(
        id="overhand", name="Overhand Right", category="strike",
        base_damage=25.0, stamina_cost=18.0, speed=8.0, accuracy=0.45,
        block_modifier=0.5, stun_chance=0.25, stun_duration=2,
        position_required=[Position.STANDING],
        stat_scaling={"power": 1.0},
        is_finisher=True,
    ),
    "backfist": MoveDefinition(
        id="backfist", name="Spinning Backfist", category="strike",
        base_damage=10.0, stamina_cost=8.0, speed=3.0, accuracy=0.75,
        block_modifier=0.8, stun_chance=0.05,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.4, "speed": 0.6},
    ),
    "body_shot": MoveDefinition(
        id="body_shot", name="Body Shot", category="strike",
        base_damage=10.0, stamina_cost=10.0, speed=5.0, accuracy=0.70,
        block_modifier=0.8, stun_chance=0.03,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.7, "technique": 0.3},
        stamina_damage=12.0,
    ),
    "front_kick": MoveDefinition(
        id="front_kick", name="Front Kick", category="kick",
        base_damage=10.0, stamina_cost=8.0, speed=4.0, accuracy=0.70,
        block_modifier=0.9, stun_chance=0.05,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.6, "speed": 0.4},
    ),
    "leg_kick": MoveDefinition(
        id="leg_kick", name="Leg Kick", category="kick",
        base_damage=8.0, stamina_cost=7.0, speed=3.0, accuracy=0.80,
        block_modifier=0.7, stun_chance=0.02,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.5, "speed": 0.5},
        stamina_damage=10.0,
    ),
    "roundhouse": MoveDefinition(
        id="roundhouse", name="Roundhouse Kick", category="kick",
        base_damage=20.0, stamina_cost=15.0, speed=6.0, accuracy=0.55,
        block_modifier=0.6, stun_chance=0.20, stun_duration=2,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.7, "speed": 0.3},
        is_finisher=True,
    ),
    "spinning_back_kick": MoveDefinition(
        id="spinning_back_kick", name="Spinning Back Kick", category="kick",
        base_damage=28.0, stamina_cost=20.0, speed=9.0, accuracy=0.35,
        block_modifier=0.4, stun_chance=0.35, stun_duration=3,
        position_required=[Position.STANDING],
        stat_scaling={"power": 0.8, "speed": 0.2},
        is_finisher=True,
    ),
    "knee": MoveDefinition(
        id="knee", name="Knee Strike", category="kick",
        base_damage=16.0, stamina_cost=12.0, speed=5.0, accuracy=0.65,
        block_modifier=0.7, stun_chance=0.12,
        position_required=[Position.STANDING, Position.CLINCH],
        stat_scaling={"power": 0.8, "speed": 0.2},
    ),
    "clinch_entry": MoveDefinition(
        id="clinch_entry", name="Clinch Entry", category="clinch",
        base_damage=0.0, stamina_cost=10.0, speed=5.0, accuracy=0.55,
        block_modifier=0.5, stun_chance=0.0,
        position_required=[Position.STANDING],
        position_change=Position.CLINCH,
        stat_scaling={"technique": 0.6, "power": 0.4},
    ),
    "clinch_elbow": MoveDefinition(
        id="clinch_elbow", name="Elbow", category="clinch",
        base_damage=15.0, stamina_cost=10.0, speed=4.0, accuracy=0.70,
        block_modifier=0.6, stun_chance=0.18, stun_duration=2,
        position_required=[Position.CLINCH],
        stat_scaling={"power": 0.7, "technique": 0.3},
    ),
    "clinch_knee": MoveDefinition(
        id="clinch_knee", name="Clinch Knee", category="clinch",
        base_damage=18.0, stamina_cost=12.0, speed=5.0, accuracy=0.65,
        block_modifier=0.5, stun_chance=0.15,
        position_required=[Position.CLINCH],
        stat_scaling={"power": 0.8, "speed": 0.2},
    ),
    "throw": MoveDefinition(
        id="throw", name="Hip Throw", category="clinch",
        base_damage=12.0, stamina_cost=15.0, speed=7.0, accuracy=0.50,
        block_modifier=0.3, stun_chance=0.10,
        position_required=[Position.CLINCH],
        position_change=Position.GROUND,
        stat_scaling={"technique": 0.6, "power": 0.4},
    ),
    "clinch_break": MoveDefinition(
        id="clinch_break", name="Break Clinch", category="defensive",
        base_damage=0.0, stamina_cost=8.0, speed=3.0, accuracy=0.80,
        block_modifier=0.0, stun_chance=0.0,
        position_required=[Position.CLINCH],
        position_change=Position.STANDING,
        stat_scaling={"speed": 0.5, "technique": 0.5},
    ),
    "ground_and_pound": MoveDefinition(
        id="ground_and_pound", name="Ground & Pound", category="ground",
        base_damage=14.0, stamina_cost=10.0, speed=4.0, accuracy=0.75,
        block_modifier=0.5, stun_chance=0.10,
        position_required=[Position.GROUND],
        stat_scaling={"power": 0.8, "technique": 0.2},
    ),
    "armbar_attempt": MoveDefinition(
        id="armbar_attempt", name="Armbar", category="ground",
        base_damage=8.0, stamina_cost=20.0, speed=8.0, accuracy=0.35,
        block_modifier=0.3, stun_chance=0.0,
        position_required=[Position.GROUND],
        stat_scaling={"technique": 1.0},
        is_submission=True, is_finisher=True,
    ),
    "choke_attempt": MoveDefinition(
        id="choke_attempt", name="Rear Naked Choke", category="ground",
        base_damage=8.0, stamina_cost=20.0, speed=8.0, accuracy=0.30,
        block_modifier=0.3, stun_chance=0.0,
        position_required=[Position.GROUND],
        stat_scaling={"technique": 1.0},
        is_submission=True, is_finisher=True,
    ),
    "sweep": MoveDefinition(
        id="sweep", name="Sweep", category="ground",
        base_damage=0.0, stamina_cost=12.0, speed=5.0, accuracy=0.50,
        block_modifier=0.3, stun_chance=0.0,
        position_required=[Position.GROUND],
        position_change=Position.STANDING,
        stat_scaling={"technique": 0.6, "speed": 0.4},
    ),
    "ground_elbow": MoveDefinition(
        id="ground_elbow", name="Ground Elbow", category="ground",
        base_damage=12.0, stamina_cost=8.0, speed=3.0, accuracy=0.80,
        block_modifier=0.5, stun_chance=0.08,
        position_required=[Position.GROUND],
        stat_scaling={"power": 0.7, "technique": 0.3},
    ),
    "block": MoveDefinition(
        id="block", name="Block", category="defensive",
        base_damage=0.0, stamina_cost=3.0, speed=1.0, accuracy=1.0,
        block_modifier=0.0, stun_chance=0.0,
        position_required=[Position.STANDING, Position.CLINCH, Position.GROUND],
        stat_scaling={},
    ),
    "slip": MoveDefinition(
        id="slip", name="Slip", category="defensive",
        base_damage=0.0, stamina_cost=5.0, speed=2.0, accuracy=0.70,
        block_modifier=0.0, stun_chance=0.0,
        position_required=[Position.STANDING, Position.CLINCH],
        stat_scaling={"speed": 0.6, "technique": 0.4},
    ),
    "recover": MoveDefinition(
        id="recover", name="Recover", category="defensive",
        base_damage=0.0, stamina_cost=-15.0, speed=10.0, accuracy=1.0,
        block_modifier=0.0, stun_chance=0.0,
        position_required=[Position.STANDING, Position.CLINCH, Position.GROUND],
        stat_scaling={},
    ),
    "spirit_blast": MoveDefinition(
        id="spirit_blast", name="Spirit Blast", category="supernatural",
        base_damage=35.0, stamina_cost=15.0, mana_cost=40.0, speed=5.0, accuracy=0.60,
        block_modifier=0.3, stun_chance=0.25, stun_duration=2,
        position_required=[Position.STANDING, Position.CLINCH, Position.GROUND],
        stat_scaling={"supernatural": 1.0},
        is_finisher=True,
    ),
    "hex_drain": MoveDefinition(
        id="hex_drain", name="Hex Drain", category="supernatural",
        base_damage=20.0, stamina_cost=10.0, mana_cost=50.0, speed=6.0, accuracy=0.55,
        block_modifier=0.2, stun_chance=0.10,
        position_required=[Position.STANDING, Position.CLINCH, Position.GROUND],
        stat_scaling={"supernatural": 1.0},
        stamina_damage=20.0,
    ),
    "phantom_rush": MoveDefinition(
        id="phantom_rush", name="Phantom Rush", category="supernatural",
        base_damage=30.0, stamina_cost=20.0, mana_cost=60.0, speed=3.0, accuracy=0.70,
        block_modifier=0.2, stun_chance=0.20, stun_duration=2,
        position_required=[Position.STANDING],
        stat_scaling={"supernatural": 0.7, "speed": 0.3},
        is_finisher=True,
    ),
    "dark_shield": MoveDefinition(
        id="dark_shield", name="Dark Shield", category="supernatural",
        base_damage=0.0, stamina_cost=5.0, mana_cost=35.0, speed=1.0, accuracy=1.0,
        block_modifier=0.0, stun_chance=0.0,
        position_required=[Position.STANDING, Position.CLINCH, Position.GROUND],
        stat_scaling={"supernatural": 1.0},
    ),
}


def get_available_moves(
    fighter_state, fighter_signature_moves: list[MoveDefinition] | None = None
) -> list[MoveDefinition]:
    all_moves = list(UNIVERSAL_MOVES.values())
    if fighter_signature_moves:
        all_moves.extend(fighter_signature_moves)

    available = []
    for move in all_moves:
        if fighter_state.position not in move.position_required:
            continue
        if move.stamina_cost > 0 and fighter_state.stamina < move.stamina_cost:
            continue
        if move.mana_cost > 0 and fighter_state.mana < move.mana_cost:
            continue
        if fighter_state.stun_ticks > 0 and move.category != "defensive":
            continue
        available.append(move)

    if not available:
        available = [UNIVERSAL_MOVES["block"]]

    return available
