import random as _random

from app.engine.combat.models import (
    FighterCombatState,
    TickResult,
    TickOutcome,
    FinishMethod,
    Position,
)
from app.engine.combat.moves import MoveDefinition, get_available_moves
from app.engine.combat.damage import (
    resolve_attack,
    apply_damage,
    apply_attacker_costs,
    calculate_damage,
)
from app.engine.combat.conditions import (
    update_emotions_on_hit,
    update_emotions_on_miss,
    update_emotions_on_block,
    update_emotions_on_counter,
    update_emotions_tick_decay,
    update_mana,
)
from app.engine.combat.win_conditions import check_win_condition


def calculate_initiative(move: MoveDefinition, fighter: FighterCombatState) -> float:
    speed_factor = 1.0 - fighter.speed / 200.0
    stamina_factor = 0.7 + 0.3 * (fighter.stamina / fighter.max_stamina)
    return move.speed * speed_factor * stamina_factor


def resolve_single_attack(
    attacker: FighterCombatState,
    defender: FighterCombatState,
    att_move: MoveDefinition,
    def_move: MoveDefinition | None,
    round_number: int,
    rng: _random.Random,
) -> tuple[TickOutcome, float, FinishMethod | None]:
    outcome, damage = resolve_attack(att_move, attacker, defender, def_move, rng)

    apply_attacker_costs(attacker, att_move, outcome)

    if outcome == TickOutcome.HIT:
        apply_damage(defender, damage, att_move, outcome, rng, attacker=attacker)
        update_emotions_on_hit(attacker, defender, damage, attacker_guile=attacker.guile)
        attacker.combo_counter += 1

        if att_move.position_change is not None:
            attacker.position = att_move.position_change
            defender.position = att_move.position_change

    elif outcome == TickOutcome.BLOCKED:
        apply_damage(defender, damage, att_move, outcome, rng, attacker=attacker)
        update_emotions_on_block(attacker, defender)
        attacker.combo_counter = 0

    elif outcome == TickOutcome.COUNTER:
        counter_damage = calculate_damage(att_move, defender, attacker) * 0.7
        apply_damage(attacker, counter_damage, att_move, outcome, rng, attacker=defender)
        update_emotions_on_counter(attacker, defender, counter_guile=defender.guile)
        attacker.combo_counter = 0
        defender.combo_counter += 1
        damage = counter_damage

    elif outcome == TickOutcome.DODGED:
        update_emotions_on_miss(attacker)
        attacker.combo_counter = 0

        if att_move.base_damage == 0 and att_move.position_change is not None:
            pass

    win = check_win_condition(attacker, defender, att_move, outcome, round_number, rng)
    finish = None
    if win:
        finish = win[0]

    if outcome == TickOutcome.COUNTER:
        counter_win = check_win_condition(defender, attacker, att_move, TickOutcome.HIT, round_number, rng)
        if counter_win:
            finish = counter_win[0]

    return outcome, damage, finish


def resolve_tick(
    fighter1: FighterCombatState,
    fighter2: FighterCombatState,
    f1_move: MoveDefinition,
    f2_move: MoveDefinition,
    global_tick: int,
    round_number: int,
    tick_in_round: int,
    rng: _random.Random,
) -> list[TickResult]:
    results = []

    f1_init = calculate_initiative(f1_move, fighter1)
    f2_init = calculate_initiative(f2_move, fighter2)

    if f1_init < f2_init or (f1_init == f2_init and rng.random() < 0.5):
        first, second = fighter1, fighter2
        first_move, second_move = f1_move, f2_move
    else:
        first, second = fighter2, fighter1
        first_move, second_move = f2_move, f1_move

    outcome1, damage1, finish1 = resolve_single_attack(
        first, second, first_move, second_move, round_number, rng
    )

    results.append(TickResult(
        global_tick=global_tick,
        round_number=round_number,
        tick_in_round=tick_in_round,
        attacker_id=first.fighter_id,
        defender_id=second.fighter_id,
        move_used=first_move.id,
        defender_move=second_move.id,
        result=outcome1.value,
        damage_dealt=round(damage1, 1),
        attacker_state_after=first.snapshot(),
        defender_state_after=second.snapshot(),
        finish=finish1.value if finish1 else "",
    ))

    if finish1:
        return results

    if second.stun_ticks > 0 and outcome1 == TickOutcome.HIT:
        pass
    else:
        def_move_for_second = first_move if first_move.category == "defensive" else None
        outcome2, damage2, finish2 = resolve_single_attack(
            second, first, second_move, def_move_for_second, round_number, rng
        )

        results.append(TickResult(
            global_tick=global_tick,
            round_number=round_number,
            tick_in_round=tick_in_round,
            attacker_id=second.fighter_id,
            defender_id=first.fighter_id,
            move_used=second_move.id,
            defender_move=first_move.id,
            result=outcome2.value,
            damage_dealt=round(damage2, 1),
            attacker_state_after=second.snapshot(),
            defender_state_after=first.snapshot(),
            finish=finish2.value if finish2 else "",
        ))

    _end_of_tick_maintenance(fighter1, fighter2)

    return results


def _end_of_tick_maintenance(f1: FighterCombatState, f2: FighterCombatState):
    for f in (f1, f2):
        f.stamina = min(f.max_stamina, f.stamina + 3.0)
        f.guard = min(f.max_guard, f.guard + 3.0)
        if f.stun_ticks > 0:
            f.stun_ticks -= 1
        update_emotions_tick_decay(f)
        update_mana(f)
