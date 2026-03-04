import random as _random
from datetime import date as _date

from .retirement import check_retirement, apply_aging, update_promotion_desperation, generate_replacement_fighter
from .league_tiers import calculate_tier_rankings, TIER_ORDER

SEASON_START_MONTH = 11
SEASON_MONTHS = [11, 12, 1, 2, 3, 4, 5, 6]
REGULAR_MONTHS = [11, 12, 1, 2, 3, 4, 5]
PROMOTION_MONTH = 6

EVENT_INTERVAL = {
    "apex": 10,
    "contender": 6,
    "underground": 1,
}

TIER_START_TIMES = {
    "underground": "14:00",
    "contender": "18:00",
    "apex": "21:00",
}

FIGHT_STAGGER_MINUTES = 30


def get_fight_start_time(tier: str, fight_index: int) -> str:
    base = TIER_START_TIMES.get(tier, "14:00")
    h, m = int(base.split(":")[0]), int(base.split(":")[1])
    total_minutes = h * 60 + m + fight_index * FIGHT_STAGGER_MINUTES
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def is_fight_day(current: _date, season_number: int, tier: str) -> bool:
    start = season_start_date(season_number)
    days_since = (current - start).days
    interval = EVENT_INTERVAL.get(tier, 1)
    return days_since > 0 and days_since % interval == 0


_BASE_YEAR = 2024


def set_base_year(year: int):
    global _BASE_YEAR
    _BASE_YEAR = year


def season_start_year(season_number: int) -> int:
    return _BASE_YEAR + season_number - 1


def season_start_date(season_number: int) -> _date:
    return _date(season_start_year(season_number), SEASON_START_MONTH, 1)


def season_end_date(season_number: int) -> _date:
    return _date(season_start_year(season_number) + 1, 6, 30)


def is_promotion_month(month: int) -> bool:
    return month == PROMOTION_MONTH


def is_regular_month(month: int) -> bool:
    return month in REGULAR_MONTHS


def days_remaining_in_season(current: _date, season_number: int) -> int:
    end = season_end_date(season_number)
    return max(0, (end - current).days)

TIER_EVENT_CONFIG = {
    "apex": {"events_per_month": 6, "fights_min": 2, "fights_max": 3},
    "contender": {"events_per_month": 10, "fights_min": 2, "fights_max": 3},
    "underground": {"events_per_month": 30, "fights_min": 4, "fights_max": 6},
}

TIER_SIZES = {
    "apex": 16,
    "contender": 20,
    "underground": 100,
}


def set_tier_sizes(apex: int = None, contender: int = None, underground: int = None):
    if apex is not None:
        TIER_SIZES["apex"] = apex
    if contender is not None:
        TIER_SIZES["contender"] = contender
    if underground is not None:
        TIER_SIZES["underground"] = underground


def get_tier_event_config(tier: str) -> dict:
    return TIER_EVENT_CONFIG.get(tier, TIER_EVENT_CONFIG["underground"])


def process_end_of_season(
    fighters: dict,
    ws: dict,
    fighter_counter: int,
    rng: _random.Random = None,
    used_names: set = None,
) -> dict:
    if rng is None:
        rng = _random.Random()

    season = ws.get("season_number", 1)
    summary = {
        "season": season,
        "retirements": [],
        "aging_changes": [],
        "new_fighters": [],
        "backfill_promotions": [],
        "tier_counts_before": _count_tiers(fighters),
    }

    for fid, fighter in list(fighters.items()):
        if fighter.get("status") != "active":
            continue
        apply_aging(fighter, rng)

    for fid, fighter in list(fighters.items()):
        if fighter.get("status") != "active":
            continue

        is_belt_holder = ws.get("belt_holder_id") == fid
        fighter["_is_belt_holder"] = is_belt_holder
        should_retire, reason = check_retirement(fighter, rng)
        fighter.pop("_is_belt_holder", None)

        if should_retire:
            fighter["status"] = "retired"
            summary["retirements"].append({
                "fighter_id": fid,
                "ring_name": fighter.get("ring_name", ""),
                "age": fighter.get("age", 0),
                "tier": fighter.get("tier", ""),
                "reason": reason,
                "career_seasons": fighter.get("career_season_count", 0),
                "peak_tier": fighter.get("peak_tier", "underground"),
                "record": dict(fighter.get("record", {})),
            })

            if is_belt_holder:
                for entry in ws.get("belt_history", []):
                    if entry.get("fighter_id") == fid and not entry.get("lost_date"):
                        entry["lost_date"] = f"season_{season}_retired"
                        break
                ws["belt_holder_id"] = ""

            ws.setdefault("retired_fighter_ids", []).append(fid)

    for fid, fighter in fighters.items():
        if fighter.get("status") != "active":
            continue
        if fighter.get("tier") == "underground":
            update_promotion_desperation(fighter)

    _backfill_tiers(fighters, ws, summary, fighter_counter, rng, season, used_names)

    for fid, fighter in fighters.items():
        if fighter.get("status") != "active":
            continue
        fighter["season_wins"] = 0
        fighter["season_losses"] = 0
        fighter["seasons_in_current_tier"] = fighter.get("seasons_in_current_tier", 0) + 1
        fighter["career_season_count"] = fighter.get("career_season_count", 0) + 1
        fighter["consecutive_losses"] = 0
        condition = fighter.get("condition", {})
        if condition.get("morale") == "low":
            condition["morale"] = "neutral"

        fighter.pop("_season_record_at_injury", None)
        injuries = condition.get("injuries", [])
        has_career_ending = any(i.get("severity") == "career_ending" for i in injuries)
        if not has_career_ending and condition.get("health_status") == "injured":
            fighter["condition"] = {
                "health_status": "healthy",
                "injuries": [],
                "recovery_days_remaining": 0,
                "morale": condition.get("morale", "neutral"),
                "momentum": condition.get("momentum", "neutral"),
            }

    ws["season_number"] = season + 1
    ws["current_date"] = season_start_date(season + 1).isoformat()
    ws["season_month"] = SEASON_START_MONTH
    ws["season_day_in_month"] = 1

    summary["tier_counts_after"] = _count_tiers(fighters)
    return summary


def _count_tiers(fighters: dict) -> dict:
    counts = {"apex": 0, "contender": 0, "underground": 0}
    for f in fighters.values():
        if f.get("status") == "active":
            tier = f.get("tier", "underground")
            counts[tier] = counts.get(tier, 0) + 1
    return counts


def _backfill_tiers(
    fighters: dict,
    ws: dict,
    summary: dict,
    fighter_counter: int,
    rng: _random.Random,
    season: int,
    used_names: set = None,
) -> int:
    for upper_tier, lower_tier in [("apex", "contender"), ("contender", "underground")]:
        target = TIER_SIZES[upper_tier]
        active_in_tier = [f for f in fighters.values() if f.get("tier") == upper_tier and f.get("status") == "active"]
        deficit = target - len(active_in_tier)

        if deficit > 0:
            lower_candidates = [
                f for f in fighters.values()
                if f.get("tier") == lower_tier and f.get("status") == "active"
            ]
            lower_candidates.sort(
                key=lambda f: (f.get("season_wins", 0), sum(f.get("stats", {}).get(s, 0) for s in ["power", "speed", "technique", "toughness"])),
                reverse=True,
            )

            for i in range(min(deficit, len(lower_candidates))):
                promoted = lower_candidates[i]
                promoted["tier"] = upper_tier
                promoted["seasons_in_current_tier"] = 0
                if TIER_ORDER.get(upper_tier, 0) > TIER_ORDER.get(promoted.get("peak_tier", "underground"), 0):
                    promoted["peak_tier"] = upper_tier
                summary["backfill_promotions"].append({
                    "fighter_id": promoted["id"],
                    "ring_name": promoted.get("ring_name", ""),
                    "from_tier": lower_tier,
                    "to_tier": upper_tier,
                })

    underground_target = TIER_SIZES["underground"]
    active_underground = [f for f in fighters.values() if f.get("tier") == "underground" and f.get("status") == "active"]
    underground_deficit = underground_target - len(active_underground)

    new_counter = fighter_counter
    for _ in range(max(0, underground_deficit)):
        new_counter += 1
        new_fighter = generate_replacement_fighter(new_counter, season, rng, used_names)
        fighters[new_fighter["id"]] = new_fighter
        summary["new_fighters"].append({
            "fighter_id": new_fighter["id"],
            "ring_name": new_fighter["ring_name"],
            "age": new_fighter["age"],
        })

    return new_counter
