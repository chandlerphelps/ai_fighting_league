import random as _random

from app.engine.combat.models import FighterCombatState, FinishMethod, TickOutcome
from app.engine.combat.moves import MoveDefinition


def check_ko(state: FighterCombatState) -> bool:
    return state.hp <= 0


def check_tko(state: FighterCombatState, round_number: int, rng: _random.Random | None = None) -> bool:
    base_threshold = 65.0 + state.toughness * 0.6
    if round_number > 10:
        base_threshold -= (round_number - 10) * 5.0
        base_threshold = max(30.0, base_threshold)

    hp_pct = state.hp / state.max_hp
    if state.accumulated_damage <= base_threshold or hp_pct >= 0.25:
        return False

    tko_rng = rng or _random.Random()
    tko_chance = 0.025 + 0.05 * (1.0 - hp_pct / 0.25)
    return tko_rng.random() < tko_chance


def check_submission(
    move: MoveDefinition,
    attacker: FighterCombatState,
    defender: FighterCombatState,
    rng: _random.Random,
) -> bool:
    if not move.is_submission:
        return False

    hp_pct = defender.hp / defender.max_hp
    stamina_pct = defender.stamina / defender.max_stamina

    if hp_pct > 0.60 or stamina_pct > 0.50:
        return False

    technique_diff = attacker.technique - defender.technique
    hp_factor = 1.0 + 1.0 * (0.60 - hp_pct)
    stamina_factor = 1.0 + 0.8 * (0.50 - stamina_pct)
    sub_chance = (0.55 + technique_diff * 0.01) * hp_factor * stamina_factor
    sub_chance = max(0.20, min(0.90, sub_chance))

    return rng.random() < sub_chance


def check_win_condition(
    attacker: FighterCombatState,
    defender: FighterCombatState,
    move: MoveDefinition,
    outcome: TickOutcome,
    round_number: int,
    rng: _random.Random | None = None,
) -> tuple[FinishMethod, str] | None:
    if check_ko(defender):
        return FinishMethod.KO, attacker.fighter_id

    _rng = rng or _random.Random()
    if check_tko(defender, round_number, _rng):
        return FinishMethod.TKO, attacker.fighter_id
    if outcome == TickOutcome.HIT and check_submission(move, attacker, defender, _rng):
        return FinishMethod.SUBMISSION, attacker.fighter_id

    return None
