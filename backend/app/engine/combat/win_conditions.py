from app.engine.combat.models import FighterCombatState, FinishMethod, TickOutcome
from app.engine.combat.moves import MoveDefinition


def check_ko(state: FighterCombatState) -> bool:
    return state.hp <= 0


def check_tko(state: FighterCombatState, round_number: int) -> bool:
    base_threshold = 60.0 + state.toughness * 0.5
    if round_number > 10:
        base_threshold -= (round_number - 10) * 5.0
        base_threshold = max(30.0, base_threshold)

    hp_pct = state.hp / state.max_hp
    return state.accumulated_damage > base_threshold and hp_pct < 0.20


def check_submission(
    move: MoveDefinition,
    attacker: FighterCombatState,
    defender: FighterCombatState,
) -> bool:
    if not move.is_submission:
        return False

    hp_pct = defender.hp / defender.max_hp
    stamina_pct = defender.stamina / defender.max_stamina

    if hp_pct > 0.30 or stamina_pct > 0.20:
        return False

    technique_diff = attacker.technique - defender.technique
    sub_chance = 0.5 + technique_diff * 0.01
    sub_chance = max(0.15, min(0.85, sub_chance))

    return True


def check_win_condition(
    attacker: FighterCombatState,
    defender: FighterCombatState,
    move: MoveDefinition,
    outcome: TickOutcome,
    round_number: int,
) -> tuple[FinishMethod, str] | None:
    if check_ko(defender):
        return FinishMethod.KO, attacker.fighter_id

    if check_tko(defender, round_number):
        return FinishMethod.TKO, attacker.fighter_id

    if outcome == TickOutcome.HIT and check_submission(move, attacker, defender):
        return FinishMethod.SUBMISSION, attacker.fighter_id

    return None
