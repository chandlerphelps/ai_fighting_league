import random

from app.config import Config
from app.models.fighter import Fighter, Injury, Condition
from app.models.match import Match
from app.services import data_manager
from app.services.openrouter import call_openrouter


def apply_fight_results(match: Match, config: Config) -> dict:
    f1_data = data_manager.load_fighter(match.fighter1_id, config)
    f2_data = data_manager.load_fighter(match.fighter2_id, config)

    if not f1_data or not f2_data:
        raise ValueError(f"Could not load fighters for match {match.id}")

    f1 = Fighter.from_dict(f1_data)
    f2 = Fighter.from_dict(f2_data)

    outcome = match.outcome
    changes = {"fighter1": {}, "fighter2": {}}

    _update_records(f1, f2, outcome)
    changes["fighter1"]["record"] = f"W:{f1.record.wins} L:{f1.record.losses} D:{f1.record.draws}"
    changes["fighter2"]["record"] = f"W:{f2.record.wins} L:{f2.record.losses} D:{f2.record.draws}"

    f1_stat_changes = _apply_stat_adjustments(f1, outcome, is_fighter1=True)
    f2_stat_changes = _apply_stat_adjustments(f2, outcome, is_fighter1=False)
    changes["fighter1"]["stat_changes"] = f1_stat_changes
    changes["fighter2"]["stat_changes"] = f2_stat_changes

    _apply_injuries(f1, outcome.fighter1_injuries)
    _apply_injuries(f2, outcome.fighter2_injuries)
    changes["fighter1"]["injuries"] = [i.type for i in f1.condition.injuries] if f1.condition.injuries else ["none"]
    changes["fighter2"]["injuries"] = [i.type for i in f2.condition.injuries] if f2.condition.injuries else ["none"]

    f1.last_fight_date = match.date
    f2.last_fight_date = match.date

    try:
        f1_story = _generate_storyline_entry(f1, f2, outcome, match, config)
        f1.storyline_log.append(f1_story)
        changes["fighter1"]["storyline"] = f1_story
    except Exception:
        f1.storyline_log.append(f"Fought {f2.ring_name} on {match.date}.")

    try:
        f2_story = _generate_storyline_entry(f2, f1, outcome, match, config)
        f2.storyline_log.append(f2_story)
        changes["fighter2"]["storyline"] = f2_story
    except Exception:
        f2.storyline_log.append(f"Fought {f1.ring_name} on {match.date}.")

    _update_rivalry(f1.id, f2.id, outcome, config)

    data_manager.save_fighter(f1, config)
    data_manager.save_fighter(f2, config)

    ws_data = data_manager.load_world_state(config)
    if ws_data:
        active_injuries = ws_data.get("active_injuries", {})
        if f1.condition.health_status == "injured":
            active_injuries[f1.id] = f1.condition.recovery_days_remaining
        if f2.condition.health_status == "injured":
            active_injuries[f2.id] = f2.condition.recovery_days_remaining
        ws_data["active_injuries"] = active_injuries
        data_manager.save_world_state(ws_data, config)

    return changes


def _update_records(f1: Fighter, f2: Fighter, outcome):
    if outcome.is_draw:
        f1.record.draws += 1
        f2.record.draws += 1
        return

    if outcome.winner_id == f1.id:
        winner, loser = f1, f2
    else:
        winner, loser = f2, f1

    winner.record.wins += 1
    loser.record.losses += 1

    if outcome.method == "ko_tko":
        winner.record.kos += 1
    elif outcome.method == "submission":
        winner.record.submissions += 1


def _apply_stat_adjustments(fighter: Fighter, outcome, is_fighter1: bool) -> dict:
    changes = {}

    if outcome.is_draw:
        _adjust_stat(fighter.stats, "toughness", 1, changes)
        return changes

    performance = outcome.fighter1_performance if is_fighter1 else outcome.fighter2_performance
    is_winner = outcome.winner_id == fighter.id

    if is_winner:
        if performance == "dominant":
            _adjust_stat(fighter.stats, "technique", random.randint(1, 2), changes)
            _adjust_stat(fighter.stats, "power", 1, changes)
        else:
            _adjust_stat(fighter.stats, "technique", 1, changes)

        if outcome.method == "ko_tko":
            _adjust_stat(fighter.stats, "power", 1, changes)
        elif outcome.method == "submission":
            _adjust_stat(fighter.stats, "technique", 1, changes)
    else:
        if performance == "poor":
            _adjust_stat(fighter.stats, "technique", -2, changes)
        else:
            _adjust_stat(fighter.stats, "technique", -1, changes)

        if outcome.method == "ko_tko":
            _adjust_stat(fighter.stats, "toughness", 1, changes)
        elif outcome.method == "submission":
            _adjust_stat(fighter.stats, "technique", 1, changes)

    return changes


def _adjust_stat(stats, stat_name: str, delta: int, changes: dict):
    old_val = getattr(stats, stat_name)
    new_val = max(15, min(95, old_val + delta))
    setattr(stats, stat_name, new_val)
    if new_val != old_val:
        changes[stat_name] = {"old": old_val, "new": new_val, "delta": new_val - old_val}


def _apply_injuries(fighter: Fighter, injuries: list[dict]):
    if not injuries:
        return

    fighter.condition.injuries = []
    max_recovery = 0

    for inj in injuries:
        injury = Injury(
            type=inj.get("type", "unknown"),
            severity=inj.get("severity", "minor"),
            recovery_days_remaining=inj.get("recovery_days_remaining", 7),
        )
        fighter.condition.injuries.append(injury)
        max_recovery = max(max_recovery, injury.recovery_days_remaining)

    if max_recovery > 0:
        fighter.condition.health_status = "injured"
        fighter.condition.recovery_days_remaining = max_recovery
        fighter.condition.morale = "low"


def _generate_storyline_entry(
    fighter: Fighter, opponent: Fighter, outcome, match: Match, config: Config
) -> str:
    is_winner = outcome.winner_id == fighter.id
    result_text = "won" if is_winner else ("drew with" if outcome.is_draw else "lost to")
    method = outcome.method.replace("_", " ")

    prompt = f"""Write 2-3 sentences about what this fight meant for {fighter.ring_name} narratively.

{fighter.ring_name} {result_text} {opponent.ring_name} by {method} in round {outcome.round_ended}.
Current record: {fighter.record.wins}-{fighter.record.losses}-{fighter.record.draws}

Capture the emotional/narrative significance — confidence building, humbling loss, rivalry intensifying, etc. Be concise and dramatic."""

    return call_openrouter(
        prompt, config, system_prompt="Write concise, dramatic fight storyline entries.", max_tokens=200
    )


def _update_rivalry(fighter1_id: str, fighter2_id: str, outcome, config: Config):
    ws_data = data_manager.load_world_state(config)
    if not ws_data:
        return

    rivalry_graph = ws_data.get("rivalry_graph", [])
    existing = None

    for rivalry in rivalry_graph:
        ids = {rivalry.get("fighter1_id"), rivalry.get("fighter2_id")}
        if {fighter1_id, fighter2_id} == ids:
            existing = rivalry
            break

    if existing:
        existing["fights"] = existing.get("fights", 0) + 1
        if outcome.is_draw:
            existing["draws"] = existing.get("draws", 0) + 1
        elif outcome.winner_id == existing.get("fighter1_id"):
            existing["fighter1_wins"] = existing.get("fighter1_wins", 0) + 1
        else:
            existing["fighter2_wins"] = existing.get("fighter2_wins", 0) + 1

        if existing["fights"] >= 2:
            existing["is_rivalry"] = True
    else:
        new_rivalry = {
            "fighter1_id": fighter1_id,
            "fighter2_id": fighter2_id,
            "fights": 1,
            "fighter1_wins": 1 if outcome.winner_id == fighter1_id and not outcome.is_draw else 0,
            "fighter2_wins": 1 if outcome.winner_id == fighter2_id and not outcome.is_draw else 0,
            "draws": 1 if outcome.is_draw else 0,
            "is_rivalry": False,
        }
        rivalry_graph.append(new_rivalry)

    ws_data["rivalry_graph"] = rivalry_graph
    data_manager.save_world_state(ws_data, config)
