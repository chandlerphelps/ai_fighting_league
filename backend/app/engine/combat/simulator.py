import hashlib
import random as _random

from app.engine.combat.models import (
    FighterCombatState,
    CombatResult,
    RoundSummary,
    TickResult,
    Position,
    FinishMethod,
)
from app.engine.combat.moves import MoveDefinition, get_available_moves
from app.engine.combat.resolution import resolve_tick
from app.engine.combat.strategy import FightStrategy, WeightedStrategy
from app.engine.combat.conditions import update_emotions_between_rounds

TICKS_PER_ROUND = 30
BASE_STAMINA_RECOVERY_PCT = 0.40
STAMINA_RECOVERY_DECAY_PER_ROUND = 0.02
MAX_ROUNDS = 30


def _make_seed(fighter1_id: str, fighter2_id: str, date: str = "") -> int:
    raw = f"{fighter1_id}:{fighter2_id}:{date}"
    return int(hashlib.sha256(raw.encode()).hexdigest()[:8], 16)


def simulate_combat(
    fighter1_data: dict,
    fighter2_data: dict,
    seed: int | None = None,
    strategy1: FightStrategy | None = None,
    strategy2: FightStrategy | None = None,
    fighter1_signature_moves: list[MoveDefinition] | None = None,
    fighter2_signature_moves: list[MoveDefinition] | None = None,
) -> CombatResult:
    f1 = FighterCombatState.from_fighter_data(fighter1_data)
    f2 = FighterCombatState.from_fighter_data(fighter2_data)

    if seed is None:
        seed = _make_seed(f1.fighter_id, f2.fighter_id)

    rng = _random.Random(seed)
    strat1 = strategy1 or WeightedStrategy()
    strat2 = strategy2 or WeightedStrategy()

    all_ticks: list[TickResult] = []
    round_summaries: list[RoundSummary] = []
    global_tick = 0
    finish_method = None
    winner_id = ""

    for round_num in range(1, MAX_ROUNDS + 1):
        round_summary = RoundSummary(
            round_number=round_num,
            fighter1_id=f1.fighter_id,
            fighter2_id=f2.fighter_id,
        )

        for tick_in_round in range(1, TICKS_PER_ROUND + 1):
            global_tick += 1

            f1_available = get_available_moves(f1, fighter1_signature_moves)
            f2_available = get_available_moves(f2, fighter2_signature_moves)

            f1_move = strat1.select_move(f1, f2, f1_available, round_num, tick_in_round, rng)
            f2_move = strat2.select_move(f2, f1, f2_available, round_num, tick_in_round, rng)

            tick_results = resolve_tick(
                f1, f2, f1_move, f2_move,
                global_tick, round_num, tick_in_round, rng,
            )

            all_ticks.extend(tick_results)
            _update_round_summary(round_summary, tick_results, f1.fighter_id, f2.fighter_id)

            for tr in tick_results:
                if tr.finish:
                    finish_method = tr.finish
                    if tr.result == "counter":
                        winner_id = tr.defender_id
                    else:
                        winner_id = tr.attacker_id
                    break

            if finish_method:
                break

        round_summary.fighter1_hp_end = round(f1.hp, 1)
        round_summary.fighter2_hp_end = round(f2.hp, 1)
        round_summary.fighter1_stamina_end = round(f1.stamina, 1)
        round_summary.fighter2_stamina_end = round(f2.stamina, 1)
        round_summary.fighter1_mana_end = round(f1.mana, 1)
        round_summary.fighter2_mana_end = round(f2.mana, 1)
        round_summaries.append(round_summary)

        if finish_method:
            break

        _between_rounds(f1, f2, round_num)

    if not finish_method:
        finish_method = FinishMethod.TKO
        winner_id = f1.fighter_id if f1.hp > f2.hp else f2.fighter_id

    loser_id = f2.fighter_id if winner_id == f1.fighter_id else f1.fighter_id

    return CombatResult(
        winner_id=winner_id,
        loser_id=loser_id,
        method=finish_method,
        final_round=round_summaries[-1].round_number if round_summaries else 1,
        final_tick=global_tick,
        tick_log=all_ticks,
        round_summaries=round_summaries,
        fighter1_final_state=f1.snapshot(),
        fighter2_final_state=f2.snapshot(),
        seed=seed,
    )


def _between_rounds(
    f1: FighterCombatState, f2: FighterCombatState, round_just_finished: int
):
    recovery_pct = max(
        0.05,
        BASE_STAMINA_RECOVERY_PCT - round_just_finished * STAMINA_RECOVERY_DECAY_PER_ROUND,
    )

    for f in (f1, f2):
        f.stamina = min(f.max_stamina, f.stamina + f.max_stamina * recovery_pct)
        f.guard = f.max_guard
        f.stun_ticks = 0
        f.position = Position.STANDING
        update_emotions_between_rounds(f)


def _update_round_summary(
    summary: RoundSummary,
    tick_results: list[TickResult],
    f1_id: str,
    f2_id: str,
):
    for tr in tick_results:
        is_f1_attacker = tr.attacker_id == f1_id

        if is_f1_attacker:
            summary.fighter1_hits_attempted += 1
            if tr.result == "hit":
                summary.fighter1_hits_landed += 1
                summary.fighter1_damage_dealt += tr.damage_dealt
            elif tr.result == "blocked":
                summary.fighter2_blocks += 1
                summary.fighter1_damage_dealt += tr.damage_dealt
            elif tr.result == "dodged":
                summary.fighter2_dodges += 1
            elif tr.result == "counter":
                summary.fighter2_hits_landed += 1
                summary.fighter2_damage_dealt += tr.damage_dealt
        else:
            summary.fighter2_hits_attempted += 1
            if tr.result == "hit":
                summary.fighter2_hits_landed += 1
                summary.fighter2_damage_dealt += tr.damage_dealt
            elif tr.result == "blocked":
                summary.fighter1_blocks += 1
                summary.fighter2_damage_dealt += tr.damage_dealt
            elif tr.result == "dodged":
                summary.fighter1_dodges += 1
            elif tr.result == "counter":
                summary.fighter1_hits_landed += 1
                summary.fighter1_damage_dealt += tr.damage_dealt
