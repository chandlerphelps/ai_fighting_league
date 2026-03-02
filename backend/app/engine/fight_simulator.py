import hashlib
import random
import uuid

from app.config import Config
from app.models.match import MatchupAnalysis, MatchOutcome, Match, FightMoment
from app.engine.combat.simulator import simulate_combat
from app.engine.combat.models import CombatResult, TickResult
from app.engine.combat.moves import MoveDefinition, UNIVERSAL_MOVES
from app.services import data_manager


def _make_seed(fighter1_id: str, fighter2_id: str, match_date: str) -> int:
    raw = f"{fighter1_id}:{fighter2_id}:{match_date}"
    return int(hashlib.sha256(raw.encode()).hexdigest()[:8], 16)


def _assess_performance(fighter_id: str, combat_result: CombatResult) -> str:
    is_winner = combat_result.winner_id == fighter_id
    total_ticks = len(combat_result.tick_log)

    if is_winner:
        if combat_result.final_round <= 2:
            return "dominant"
        if total_ticks < 60:
            return "dominant"
        return "competitive"
    else:
        if combat_result.final_round <= 2:
            return "poor"
        if total_ticks < 60:
            return "poor"
        return "competitive"


def _derive_injuries(
    fighter_id: str, combat_result: CombatResult, config: Config
) -> list[dict]:
    is_winner = combat_result.winner_id == fighter_id

    final_state = (
        combat_result.fighter1_final_state
        if combat_result.tick_log and combat_result.tick_log[0].attacker_id == fighter_id
        or (len(combat_result.tick_log) > 1 and combat_result.tick_log[1].attacker_id == fighter_id)
        else combat_result.fighter2_final_state
    )

    for rs in combat_result.round_summaries:
        if rs.fighter1_id == fighter_id:
            final_state = {
                "hp": rs.fighter1_hp_end,
                "stamina": rs.fighter1_stamina_end,
            }
        elif rs.fighter2_id == fighter_id:
            final_state = {
                "hp": rs.fighter2_hp_end,
                "stamina": rs.fighter2_stamina_end,
            }

    accumulated = final_state.get("accumulated_damage", 0)

    if is_winner:
        base_chance = 0.10
    else:
        base_chance = 0.40

    if accumulated > 80:
        base_chance += 0.20
    elif accumulated > 50:
        base_chance += 0.10

    if random.random() > base_chance:
        return []

    severity_roll = random.random()
    if accumulated > 80:
        severity_roll += 0.15

    if severity_roll < 0.50:
        severity = "minor"
        recovery_range = config.minor_recovery
    elif severity_roll < 0.80:
        severity = "moderate"
        recovery_range = config.moderate_recovery
    else:
        severity = "severe"
        recovery_range = config.severe_recovery

    recovery_days = random.randint(recovery_range[0], recovery_range[1])

    method = combat_result.method
    if method in ("ko", "tko") and not is_winner:
        injury_type = random.choice(["concussion", "orbital fracture", "broken nose"])
    else:
        injury_type = random.choice(["facial laceration", "broken nose", "hand fracture", "bruised ribs"])

    return [{
        "type": injury_type,
        "severity": severity,
        "recovery_days_remaining": recovery_days,
    }]


def _tick_to_moment(
    tick: TickResult,
    moment_number: int,
    fighter1_name: str,
    fighter2_name: str,
    fighter1_id: str,
    fighter2_id: str,
) -> FightMoment:
    if tick.attacker_id == fighter1_id:
        attacker_name = fighter1_name
        defender_name = fighter2_name
    else:
        attacker_name = fighter2_name
        defender_name = fighter1_name

    move_def = UNIVERSAL_MOVES.get(tick.move_used)
    move_display = move_def.name if move_def else tick.move_used

    result = tick.result
    if result == "hit":
        description = f"{attacker_name} lands {move_display} on {defender_name}"
        if tick.damage_dealt > 20:
            description += " — devastating impact!"
    elif result == "blocked":
        description = f"{defender_name} blocks {attacker_name}'s {move_display}"
    elif result == "dodged":
        description = f"{defender_name} dodges {attacker_name}'s {move_display}"
    elif result == "counter":
        description = f"{defender_name} counters {attacker_name}'s {move_display}"
    else:
        description = f"{attacker_name} attempts {move_display}"

    if tick.finish:
        finish_display = tick.finish.upper().replace("_", " ")
        description += f" — {finish_display}!"

    att_state = tick.attacker_state_after
    def_state = tick.defender_state_after

    return FightMoment(
        moment_number=moment_number,
        description=description,
        attacker_id=tick.attacker_id,
        defender_id=tick.defender_id,
        action=tick.move_used,
        defender_action=tick.defender_move,
        result=tick.result,
        damage_dealt=tick.damage_dealt,
        tick_number=tick.global_tick,
        round_number=tick.round_number,
        attacker_hp=att_state.get("hp", 0),
        attacker_stamina=att_state.get("stamina", 0),
        attacker_mana=att_state.get("mana", 0),
        defender_hp=def_state.get("hp", 0),
        defender_stamina=def_state.get("stamina", 0),
        defender_mana=def_state.get("mana", 0),
        attacker_emotions=att_state.get("emotions", {}),
        defender_emotions=def_state.get("emotions", {}),
    )


def _filter_significant_moments(tick_log: list[TickResult], max_moments: int = 50) -> list[TickResult]:
    significant = []
    for tick in tick_log:
        if tick.finish:
            significant.append(tick)
        elif tick.result == "hit" and tick.damage_dealt > 8:
            significant.append(tick)
        elif tick.result == "counter":
            significant.append(tick)
        elif tick.result == "hit" and tick.damage_dealt > 0:
            significant.append(tick)

    if len(significant) > max_moments:
        finishers = [t for t in significant if t.finish]
        big_hits = [t for t in significant if not t.finish and t.damage_dealt > 15]
        medium_hits = [t for t in significant if not t.finish and 8 < t.damage_dealt <= 15]
        counters = [t for t in significant if t.result == "counter" and not t.finish]
        rest = [t for t in significant if t not in finishers + big_hits + medium_hits + counters]

        combined = finishers + big_hits + counters + medium_hits + rest
        significant = combined[:max_moments]
        significant.sort(key=lambda t: t.global_tick)

    return significant


def run_fight(
    fighter1_id: str, fighter2_id: str, event_id: str, match_date: str, config: Config
) -> Match:
    fighter1 = data_manager.load_fighter(fighter1_id, config)
    fighter2 = data_manager.load_fighter(fighter2_id, config)

    if not fighter1 or not fighter2:
        raise ValueError(f"Could not load fighters: {fighter1_id}, {fighter2_id}")

    fighter1_snapshot = dict(fighter1)
    fighter2_snapshot = dict(fighter2)

    seed = _make_seed(fighter1_id, fighter2_id, match_date)

    combat_result = simulate_combat(
        fighter1_data=fighter1,
        fighter2_data=fighter2,
        seed=seed,
    )

    f1_name = fighter1.get("ring_name", "")
    f2_name = fighter2.get("ring_name", "")

    significant_ticks = _filter_significant_moments(combat_result.tick_log)
    moments = [
        _tick_to_moment(tick, i + 1, f1_name, f2_name, fighter1_id, fighter2_id)
        for i, tick in enumerate(significant_ticks)
    ]

    f1_injuries = _derive_injuries(fighter1_id, combat_result, config)
    f2_injuries = _derive_injuries(fighter2_id, combat_result, config)

    outcome = MatchOutcome(
        winner_id=combat_result.winner_id,
        loser_id=combat_result.loser_id,
        method=combat_result.method,
        round_ended=combat_result.final_round,
        fighter1_performance=_assess_performance(fighter1_id, combat_result),
        fighter2_performance=_assess_performance(fighter2_id, combat_result),
        fighter1_injuries=f1_injuries,
        fighter2_injuries=f2_injuries,
        is_draw=False,
    )

    combat_log = [rs.to_dict() for rs in combat_result.round_summaries]

    match_id = f"m_{uuid.uuid4().hex[:8]}"

    return Match(
        id=match_id,
        event_id=event_id,
        date=match_date,
        fighter1_id=fighter1_id,
        fighter1_name=f1_name,
        fighter2_id=fighter2_id,
        fighter2_name=f2_name,
        analysis=None,
        outcome=outcome,
        moments=moments,
        fighter1_snapshot=fighter1_snapshot,
        fighter2_snapshot=fighter2_snapshot,
        combat_log=combat_log,
        combat_seed=seed,
    )


def _get_rivalry_context(
    fighter1_id: str, fighter2_id: str, config: Config
) -> dict | None:
    ws = data_manager.load_world_state(config)
    if not ws:
        return None

    for rivalry in ws.get("rivalry_graph", []):
        ids = {rivalry.get("fighter1_id"), rivalry.get("fighter2_id")}
        if {fighter1_id, fighter2_id} == ids:
            return rivalry
    return None
