import hashlib
import random
from datetime import date as _date, timedelta

from app.engine.combat.simulator import simulate_combat
from app.engine.between_fights.training import process_daily_training, apply_fight_camp_boost
from app.engine.between_fights.league_tiers import (
    calculate_tier_rankings,
    get_promotion_matchups,
    apply_promotion_results,
    apply_title_fight_result,
)
from app.engine.between_fights.season import (
    process_end_of_season,
    get_tier_event_config,
    get_fight_start_time,
    is_fight_day,
    REGULAR_MONTHS,
    PROMOTION_MONTH,
    season_start_date,
    season_end_date,
    days_remaining_in_season,
    set_base_year,
)
from app.scripts.simulate_seasons import (
    INJURY_TYPES_WINNER,
    INJURY_TYPES_LOSER_KO,
    INJURY_TYPES_LOSER_OTHER,
    MINOR_RECOVERY,
    MODERATE_RECOVERY,
    SEVERE_RECOVERY,
    SEASON_ENDING_INJURY_TYPES,
    CAREER_ENDING_INJURY_TYPES,
    SEASON_ENDING_RECOVERY,
)
from app.engine.between_fights.retirement import CORE_STATS


def _current_date(ws: dict) -> _date:
    date_str = ws.get("current_date", "")
    if date_str:
        return _date.fromisoformat(date_str)
    season = ws.get("season_number", 1)
    return season_start_date(season)


def _sync_date_fields(ws: dict, d: _date):
    ws["current_date"] = d.isoformat()
    ws["season_month"] = d.month
    ws["season_day_in_month"] = d.day


def simulate_one_day(fighters: dict, ws: dict) -> dict:
    season = ws["season_number"]
    today = _current_date(ws)
    base = today.year - season + 1
    if today.month < 11:
        base -= 1
    set_base_year(base)
    month = today.month
    day_of_month = today.day

    seed_base = today.toordinal()
    rng = random.Random(seed_base)

    day_result = {
        "season": season,
        "month": month,
        "day": day_of_month,
        "date": today.isoformat(),
        "matches": [],
        "recoveries": [],
        "phase": "regular",
    }

    _process_daily_recovery(fighters, day_result)
    _process_daily_training(fighters, rng)

    if month in REGULAR_MONTHS:
        scheduled = ws.get("scheduled_fights", [])
        if scheduled:
            for sf in scheduled:
                f1_id = sf["fighter1_id"]
                f2_id = sf["fighter2_id"]
                f1 = fighters.get(f1_id)
                f2 = fighters.get(f2_id)
                if (f1 and f2
                    and f1.get("status") == "active" and f2.get("status") == "active"
                    and f1.get("condition", {}).get("health_status") == "healthy"
                    and f2.get("condition", {}).get("health_status") == "healthy"):
                    match = _run_single_fight(fighters, ws, f1_id, f2_id, rng, start_time=sf.get("start_time", ""))
                    day_result["matches"].append(match)
            ws["scheduled_fights"] = []
        else:
            for tier in ["apex", "contender", "underground"]:
                if is_fight_day(today, season, tier):
                    matches = _run_tier_event(fighters, ws, tier, rng)
                    day_result["matches"].extend(matches)
        day_result["phase"] = "regular"

    if month == PROMOTION_MONTH:
        day_result["phase"] = "promotion_month"

    _advance_calendar(fighters, ws, rng, day_result)

    _recalculate_rankings(fighters, ws)

    for m in day_result["matches"]:
        ws.setdefault("recent_matches", []).append(m)
    ws["recent_matches"] = ws.get("recent_matches", [])[-200:]

    ws["last_daily_summary"] = _build_summary(day_result)

    _schedule_next_day(fighters, ws)

    return day_result


def _process_daily_recovery(fighters: dict, day_result: dict):
    for fid, fighter in fighters.items():
        if fighter.get("status") != "active":
            continue
        condition = fighter.get("condition", {})
        if condition.get("health_status") == "injured":
            remaining = condition.get("recovery_days_remaining", 0) - 1
            if remaining <= 0:
                fighter["condition"] = {
                    "health_status": "healthy",
                    "injuries": [],
                    "recovery_days_remaining": 0,
                    "morale": condition.get("morale", "neutral"),
                    "momentum": condition.get("momentum", "neutral"),
                }
                day_result["recoveries"].append({
                    "fighter_id": fid,
                    "fighter_name": fighter.get("ring_name", fid),
                })
            else:
                condition["recovery_days_remaining"] = remaining
                for inj in condition.get("injuries", []):
                    inj["recovery_days_remaining"] = max(0, inj.get("recovery_days_remaining", 0) - 1)


def _process_daily_training(fighters: dict, rng):
    for fid, fighter in fighters.items():
        if fighter.get("status") != "active":
            continue
        process_daily_training(fighter, rng)


def _schedule_next_day(fighters: dict, ws: dict):
    next_date = _current_date(ws)
    next_month = next_date.month
    next_day = next_date.day

    if next_month not in REGULAR_MONTHS:
        ws["scheduled_fights"] = []
        return

    seed_base = next_date.toordinal()
    rng = random.Random(seed_base)

    scheduled = []
    season = ws["season_number"]
    for tier in ["apex", "contender", "underground"]:
        if not is_fight_day(next_date, season, tier):
            continue

        config = get_tier_event_config(tier)
        num_fights = rng.randint(config["fights_min"], config["fights_max"])

        available = [
            f for f in fighters.values()
            if f.get("tier") == tier
            and f.get("status") == "active"
            and f.get("condition", {}).get("health_status") == "healthy"
        ]

        if len(available) < 2:
            continue

        rng.shuffle(available)
        used = set()

        for i in range(len(available)):
            if len([s for s in scheduled if s["tier"] == tier]) >= num_fights:
                break
            for j in range(i + 1, len(available)):
                if available[i]["id"] in used or available[j]["id"] in used:
                    continue
                tier_count = len([s for s in scheduled if s["tier"] == tier])
                scheduled.append({
                    "tier": tier,
                    "fighter1_id": available[i]["id"],
                    "fighter1_name": available[i].get("ring_name", "?"),
                    "fighter2_id": available[j]["id"],
                    "fighter2_name": available[j].get("ring_name", "?"),
                    "start_time": get_fight_start_time(tier, tier_count),
                })
                used.add(available[i]["id"])
                used.add(available[j]["id"])
                break

    ws["scheduled_fights"] = scheduled


def _run_tier_event(fighters: dict, ws: dict, tier: str, rng) -> list:
    config = get_tier_event_config(tier)
    num_fights = rng.randint(config["fights_min"], config["fights_max"])

    available = [
        f for f in fighters.values()
        if f.get("tier") == tier
        and f.get("status") == "active"
        and f.get("condition", {}).get("health_status") == "healthy"
    ]

    if len(available) < 2:
        return []

    rng.shuffle(available)
    fights_scheduled = []
    used = set()

    for i in range(len(available)):
        if len(fights_scheduled) >= num_fights:
            break
        for j in range(i + 1, len(available)):
            if available[i]["id"] in used or available[j]["id"] in used:
                continue
            fights_scheduled.append((available[i]["id"], available[j]["id"]))
            used.add(available[i]["id"])
            used.add(available[j]["id"])
            break

    matches = []
    for idx, (f1_id, f2_id) in enumerate(fights_scheduled):
        match = _run_single_fight(fighters, ws, f1_id, f2_id, rng, start_time=get_fight_start_time(tier, idx))
        matches.append(match)

    return matches


def _run_single_fight(fighters: dict, ws: dict, f1_id: str, f2_id: str, rng, start_time: str = "") -> dict:
    f1 = fighters[f1_id]
    f2 = fighters[f2_id]

    f1_boosted = apply_fight_camp_boost(f1)
    f2_boosted = apply_fight_camp_boost(f2)

    f1_data = dict(f1)
    f1_data["stats"] = f1_boosted
    f2_data = dict(f2)
    f2_data["stats"] = f2_boosted

    today = _current_date(ws)
    date_str = today.isoformat()
    seed_str = f"{f1_id}:{f2_id}:{date_str}"
    seed = int(hashlib.sha256(seed_str.encode()).hexdigest()[:8], 16)

    result = simulate_combat(f1_data, f2_data, seed=seed)

    winner_id = result.winner_id
    loser_id = result.loser_id
    method = result.method
    final_round = result.final_round

    winner = fighters[winner_id]
    loser = fighters[loser_id]

    w_record = winner.get("record", {})
    w_record["wins"] = w_record.get("wins", 0) + 1
    if method in ("ko", "tko"):
        w_record["kos"] = w_record.get("kos", 0) + 1
    elif method == "submission":
        w_record["submissions"] = w_record.get("submissions", 0) + 1
    winner["record"] = w_record
    winner["season_wins"] = winner.get("season_wins", 0) + 1
    winner["consecutive_losses"] = 0
    winner["training_streak"] = 0

    l_record = loser.get("record", {})
    l_record["losses"] = l_record.get("losses", 0) + 1
    loser["record"] = l_record
    loser["season_losses"] = loser.get("season_losses", 0) + 1
    loser["consecutive_losses"] = loser.get("consecutive_losses", 0) + 1
    loser["training_streak"] = 0

    if loser["consecutive_losses"] >= 5:
        loser.setdefault("condition", {})["morale"] = "low"
    if winner.get("condition", {}).get("morale") == "low":
        winner["condition"]["morale"] = "neutral"

    _apply_injury(fighter=winner, ws=ws, rng=rng, is_winner=True, method=method)
    _apply_injury(fighter=loser, ws=ws, rng=rng, is_winner=False, method=method)

    if loser.get("status") == "retired":
        ws.setdefault("retired_fighter_ids", []).append(loser_id)

    return {
        "fighter1_id": f1_id,
        "fighter1_name": f1.get("ring_name", f1_id),
        "fighter2_id": f2_id,
        "fighter2_name": f2.get("ring_name", f2_id),
        "winner_id": winner_id,
        "method": method,
        "round_ended": final_round,
        "tier": f1.get("tier", "underground"),
        "date": date_str,
        "start_time": start_time,
    }


def _apply_injury(fighter: dict, ws: dict, rng, is_winner: bool, method: str):
    base_chance = 0.10 if is_winner else 0.40
    if method in ("ko", "tko") and not is_winner:
        base_chance += 0.15

    if rng.random() >= base_chance:
        return

    if is_winner:
        injury_type = rng.choice(INJURY_TYPES_WINNER)
        severity = "minor"
        recovery = rng.randint(*MINOR_RECOVERY)
    else:
        if method in ("ko", "tko"):
            injury_type = rng.choice(INJURY_TYPES_LOSER_KO)
            if injury_type == "concussion":
                severity = rng.choice(["moderate", "severe"])
                recovery = rng.randint(*MODERATE_RECOVERY) if severity == "moderate" else rng.randint(*SEVERE_RECOVERY)
            else:
                severity = "moderate"
                recovery = rng.randint(*MODERATE_RECOVERY)
        else:
            injury_type = rng.choice(INJURY_TYPES_LOSER_OTHER)
            severity = rng.choice(["minor", "moderate"])
            recovery = rng.randint(*MINOR_RECOVERY) if severity == "minor" else rng.randint(*MODERATE_RECOVERY)

    fighter["condition"] = {
        "health_status": "injured",
        "injuries": [{"type": injury_type, "severity": severity, "recovery_days_remaining": recovery}],
        "recovery_days_remaining": recovery,
        "morale": fighter.get("condition", {}).get("morale", "neutral"),
        "momentum": fighter.get("condition", {}).get("momentum", "neutral"),
    }

    if is_winner:
        return

    age = fighter.get("age", 25)
    ko_multiplier = 2.0 if method in ("ko", "tko") else 1.0

    career_end_chance = max(0, 0.005 + 0.005 * (age - 30)) * ko_multiplier
    if rng.random() < career_end_chance:
        injury_type = rng.choice(CAREER_ENDING_INJURY_TYPES)
        fighter["condition"] = {
            "health_status": "injured",
            "injuries": [{"type": injury_type, "severity": "career_ending", "recovery_days_remaining": 999}],
            "recovery_days_remaining": 999,
            "morale": fighter.get("condition", {}).get("morale", "neutral"),
            "momentum": fighter.get("condition", {}).get("momentum", "neutral"),
        }
        fighter["status"] = "retired"
        return

    season_end_chance = max(0, 0.02 + 0.005 * (age - 28)) * ko_multiplier
    if rng.random() < season_end_chance:
        injury_type = rng.choice(SEASON_ENDING_INJURY_TYPES)
        today = _current_date(ws)
        remaining = days_remaining_in_season(today, ws["season_number"])
        recovery = max(rng.randint(*SEASON_ENDING_RECOVERY), remaining)
        fighter["condition"] = {
            "health_status": "injured",
            "injuries": [{"type": injury_type, "severity": "season_ending", "recovery_days_remaining": recovery}],
            "recovery_days_remaining": recovery,
            "morale": fighter.get("condition", {}).get("morale", "neutral"),
            "momentum": fighter.get("condition", {}).get("momentum", "neutral"),
        }
        fighter["_season_record_at_injury"] = {
            "season_wins": fighter.get("season_wins", 0),
            "season_losses": fighter.get("season_losses", 0),
        }


def _advance_calendar(fighters: dict, ws: dict, rng, day_result: dict):
    today = _current_date(ws)
    season = ws["season_number"]
    tomorrow = today + timedelta(days=1)

    end = season_end_date(season)
    old_month = today.month

    if tomorrow > end:
        _prepare_promotions(fighters, ws)
        day_result["phase"] = "promotions_announced"

        _run_promotions(fighters, ws, rng, day_result)
        _run_title_fight(fighters, ws, rng, day_result)

        used_names = {f.get("ring_name", "") for f in fighters.values()}
        fighter_counter = max(
            (int(fid.split("-")[1]) for fid in fighters if fid.startswith("sim-")),
            default=0,
        )
        season_summary = process_end_of_season(fighters, ws, fighter_counter, rng, used_names)
        day_result["season_end"] = {
            "retirements": len(season_summary.get("retirements", [])),
            "new_fighters": len(season_summary.get("new_fighters", [])),
            "backfill_promotions": len(season_summary.get("backfill_promotions", [])),
        }

        for nf_info in season_summary.get("new_fighters", []):
            fid = nf_info["fighter_id"]
            if fid in fighters:
                continue
        day_result["phase"] = "season_end"

        champions = ws.get("season_champions", [])
        season_champ = next((c for c in champions if c["season"] == season), None)
        ws.setdefault("season_logs", []).append({
            "season": season,
            "champion_name": season_champ["ring_name"] if season_champ else "None",
            "champion_id": season_champ["fighter_id"] if season_champ else "",
            "belt_holder_name": fighters.get(ws.get("belt_holder_id", ""), {}).get("ring_name", "VACANT"),
            "belt_holder_id": ws.get("belt_holder_id", ""),
            "retirements": len(season_summary.get("retirements", [])),
            "new_fighters": len(season_summary.get("new_fighters", [])),
            "tier_counts": season_summary.get("tier_counts_after", {}),
        })
        return

    if tomorrow.month == PROMOTION_MONTH and old_month != PROMOTION_MONTH:
        _prepare_promotions(fighters, ws)
        day_result["phase"] = "promotions_announced"

    _sync_date_fields(ws, tomorrow)


def _prepare_promotions(fighters: dict, ws: dict):
    active = [f for f in fighters.values() if f.get("status") == "active"]
    season_start = season_start_date(ws["season_number"]).isoformat()
    season_matches = []
    for m in ws.get("recent_matches", []):
        if m.get("date", "") >= season_start:
            season_matches.append({
                "fighter1_id": m.get("fighter1_id"),
                "fighter2_id": m.get("fighter2_id"),
                "outcome": {"winner_id": m.get("winner_id")},
                "date": m.get("date", ""),
            })

    for tier in ["apex", "contender", "underground"]:
        ws["tier_rankings"][tier] = calculate_tier_rankings(active, tier, season_matches)

    protected = set()
    belt_holder = ws.get("belt_holder_id", "")
    if belt_holder:
        protected.add(belt_holder)

    for fid, fighter in fighters.items():
        if fighter.get("status") != "active":
            continue
        injuries = fighter.get("condition", {}).get("injuries", [])
        if any(i.get("severity") == "season_ending" for i in injuries):
            snap = fighter.get("_season_record_at_injury", {})
            sw = snap.get("season_wins", 0)
            sl = snap.get("season_losses", 0)
            if sw > sl or sw >= 3:
                protected.add(fid)

    matchups = get_promotion_matchups(
        ws["tier_rankings"],
        champ_contender_slots=4,
        contender_underground_slots=6,
        protected_fighter_ids=protected,
    )
    ws["promotion_fights"] = matchups

    champ_rankings = ws["tier_rankings"].get("apex", [])
    if belt_holder and belt_holder in [f["id"] for f in fighters.values() if f.get("status") == "active" and f.get("tier") == "apex"]:
        challengers = [fid for fid in champ_rankings if fid != belt_holder]
        if challengers:
            ws["title_fight"] = {"champion_id": belt_holder, "challenger_id": challengers[0]}
    elif champ_rankings and len(champ_rankings) >= 2:
        ws["title_fight"] = {"champion_id": champ_rankings[0], "challenger_id": champ_rankings[1]}


def _run_promotions(fighters: dict, ws: dict, rng, day_result: dict):
    results = []
    fight_idx = 0
    for matchup in ws.get("promotion_fights", []):
        upper_id = matchup["upper_fighter_id"]
        lower_id = matchup["lower_fighter_id"]
        upper = fighters.get(upper_id)
        lower = fighters.get(lower_id)
        if not upper or not lower or upper.get("status") != "active" or lower.get("status") != "active":
            continue

        match = _run_single_fight(fighters, ws, upper_id, lower_id, rng, start_time=get_fight_start_time("contender", fight_idx))
        fight_idx += 1
        day_result["matches"].append(match)
        results.append({
            "upper_fighter_id": upper_id,
            "lower_fighter_id": lower_id,
            "winner_id": match["winner_id"],
            "loser_id": [fid for fid in [upper_id, lower_id] if fid != match["winner_id"]][0],
            "tier_boundary": matchup["tier_boundary"],
        })

    apply_promotion_results(fighters, results)
    ws["promotion_fights"] = []


def _run_title_fight(fighters: dict, ws: dict, rng, day_result: dict):
    tf = ws.get("title_fight", {})
    champ_id = tf.get("champion_id", "")
    challenger_id = tf.get("challenger_id", "")

    eligible_champs = [
        fid for fid, f in fighters.items()
        if f.get("status") == "active" and f.get("tier") == "apex"
    ]

    def _is_eligible(fid):
        f = fighters.get(fid)
        return f and f.get("status") == "active" and f.get("tier") == "apex"

    if not _is_eligible(champ_id):
        champ_id = ""
    if not _is_eligible(challenger_id) or challenger_id == champ_id:
        challenger_id = ""

    if not champ_id and eligible_champs:
        champ_id = eligible_champs[0]
    if not challenger_id:
        fallbacks = [fid for fid in eligible_champs if fid != champ_id]
        if fallbacks:
            challenger_id = fallbacks[0]

    if not champ_id or not challenger_id:
        ws["title_fight"] = {}
        return

    match = _run_single_fight(fighters, ws, champ_id, challenger_id, rng, start_time=get_fight_start_time("apex", 0))
    match["is_title_fight"] = True
    day_result["matches"].append(match)

    winner_id = match["winner_id"]
    loser_id = [fid for fid in [champ_id, challenger_id] if fid != winner_id][0]
    season = ws["season_number"]
    apply_title_fight_result(ws, winner_id, loser_id, season)

    season_champion = {
        "season": season,
        "fighter_id": winner_id,
        "ring_name": fighters[winner_id].get("ring_name", "?"),
        "defeated_id": loser_id,
        "defeated_name": fighters[loser_id].get("ring_name", "?"),
    }
    ws.setdefault("season_champions", []).append(season_champion)

    ws["title_fight"] = {}


def _recalculate_rankings(fighters: dict, ws: dict):
    active = [f for f in fighters.values() if f.get("status") == "active"]
    season_start = season_start_date(ws["season_number"]).isoformat()
    season_matches = []
    for m in ws.get("recent_matches", []):
        if m.get("date", "") >= season_start:
            season_matches.append({
                "fighter1_id": m.get("fighter1_id"),
                "fighter2_id": m.get("fighter2_id"),
                "outcome": {"winner_id": m.get("winner_id")},
                "date": m.get("date", ""),
            })

    for tier in ["apex", "contender", "underground"]:
        ws["tier_rankings"][tier] = calculate_tier_rankings(active, tier, season_matches)

    ws["rankings"] = (
        list(ws["tier_rankings"].get("apex", []))
        + list(ws["tier_rankings"].get("contender", []))
        + list(ws["tier_rankings"].get("underground", []))
    )


def _build_summary(day_result: dict) -> str:
    parts = [f"Season {day_result['season']}, {day_result.get('date', '')}"]
    if day_result["matches"]:
        parts.append(f"{len(day_result['matches'])} matches fought")
    if day_result["recoveries"]:
        names = [r["fighter_name"] for r in day_result["recoveries"]]
        parts.append(f"Recovered: {', '.join(names)}")
    if day_result.get("season_end"):
        se = day_result["season_end"]
        parts.append(f"Season ended: {se['retirements']} retirements, {se['new_fighters']} new fighters")
    return " | ".join(parts)
