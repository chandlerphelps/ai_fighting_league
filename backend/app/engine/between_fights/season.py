import logging
import random as _random
from dataclasses import replace as _dc_replace
from datetime import date as _date

from .retirement import check_retirement, apply_aging, update_promotion_desperation, generate_replacement_fighter, CORE_STATS
from .league_tiers import calculate_tier_rankings, TIER_ORDER

_log = logging.getLogger(__name__)

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
    config=None,
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

    _backfill_tiers(fighters, ws, summary, fighter_counter, rng, season, used_names, config=config)

    for fid, fighter in fighters.items():
        if fighter.get("status") != "active":
            continue
        fighter["season_wins"] = 0
        fighter["season_losses"] = 0
        fighter["season_tier_wins"] = {}
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
    config=None,
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
                key=lambda f: (f.get("season_tier_wins", {}).get(lower_tier, 0), sum(f.get("stats", {}).get(s, 0) for s in ["power", "speed", "technique", "toughness"])),
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

    if underground_deficit <= 0:
        return fighter_counter

    new_counter = fighter_counter
    llm_generated = _backfill_via_llm(fighters, summary, rng, season, underground_deficit, config)

    if llm_generated < underground_deficit:
        remaining = underground_deficit - llm_generated
        for _ in range(remaining):
            new_counter += 1
            new_fighter = generate_replacement_fighter(new_counter, season, rng, used_names)
            fighters[new_fighter["id"]] = new_fighter
            summary["new_fighters"].append({
                "fighter_id": new_fighter["id"],
                "ring_name": new_fighter["ring_name"],
                "age": new_fighter["age"],
            })

    return new_counter


def _backfill_via_llm(fighters, summary, rng, season, deficit, config) -> int:
    try:
        from app.config import load_config
        from app.engine.fighter_generator import generate_fighter, plan_roster
        from app.engine.fighter_config import (
            load_outfit_options,
            filter_outfit_options,
            _roll_skimpiness,
            load_exotic_outfit_options,
            filter_exotic_for_fighter,
        )
        from app.services import data_manager
    except Exception:
        _log.warning("Could not import LLM fighter generation modules, falling back to procedural")
        return 0

    if config is None:
        config = load_config()

    existing_fighters = [
        {"ring_name": f.get("ring_name"), "gender": f.get("gender"),
         "height": f.get("height", ""), "origin": f.get("origin", ""),
         "primary_archetype": f.get("primary_archetype", ""),
         "subtype": f.get("subtype", ""),
         "build": f.get("build", ""), "personality": f.get("personality", ""),
         "distinguishing_features": f.get("distinguishing_features", ""),
         "ring_attire": f.get("ring_attire", "")}
        for f in fighters.values() if f.get("status") == "active"
    ]

    try:
        entries = plan_roster(config, roster_size=deficit, existing_fighters=existing_fighters)
    except Exception:
        _log.warning("LLM roster planning failed, falling back to procedural", exc_info=True)
        return 0

    all_outfit_options = load_outfit_options(config)
    all_exotics = load_exotic_outfit_options(config)

    tier_config = _dc_replace(config, min_total_stats=150, max_total_stats=220)

    generated = 0
    for entry in entries[:deficit]:
        skimpiness_level = _roll_skimpiness(entry.get("skimpiness_weights"))
        archetype = entry.get("primary_archetype", "")
        subtype = entry.get("subtype", "")
        outfit_options_by_tier = {}
        for tier in ["sfw", "barely", "nsfw"]:
            tier_options = all_outfit_options.get(tier, {})
            tier_exotics = None
            if archetype or subtype:
                tier_exotics = filter_exotic_for_fighter(
                    all_exotics, archetype=archetype, subtype=subtype,
                    tier=tier, skimpiness_level=skimpiness_level,
                ) or None
            outfit_options_by_tier[tier] = filter_outfit_options(
                tier_options, skimpiness_level=skimpiness_level,
                exotic_one_pieces=tier_exotics,
            )

        try:
            fighter = generate_fighter(
                tier_config,
                existing_fighters=existing_fighters,
                roster_plan_entry=entry,
                outfit_options_by_tier=outfit_options_by_tier,
                skimpiness_level=skimpiness_level,
                skip_image_prompts=True,
            )

            fighter.age = rng.randint(18, 22)
            fighter.tier = "underground"
            fighter.status = "active"
            fighter.peak_tier = "underground"
            fighter.career_season_count = 0
            fighter.training_focus = rng.choice(CORE_STATS)
            fighter.generation_stage = 1

            data_manager.save_fighter(fighter, config)

            fighter_dict = fighter.to_dict()
            fighter_dict.update({
                "training_days_accumulated": 0.0,
                "training_streak": 0,
                "seasons_in_current_tier": 0,
                "promotion_desperation": 0.0,
                "season_wins": 0,
                "season_losses": 0,
                "season_tier_wins": {},
                "consecutive_losses": 0,
                "consecutive_wins": 0,
                "tier_records": {},
                "_entered_season": season,
                "_entered_age": fighter.age,
            })

            fighters[fighter.id] = fighter_dict
            summary["new_fighters"].append({
                "fighter_id": fighter.id,
                "ring_name": fighter.ring_name,
                "age": fighter.age,
            })

            existing_fighters.append({
                "ring_name": fighter.ring_name, "gender": fighter.gender,
                "height": fighter.height, "origin": fighter.origin,
                "primary_archetype": fighter.primary_archetype,
                "subtype": fighter.subtype, "build": fighter.build,
                "personality": fighter.personality,
                "distinguishing_features": fighter.distinguishing_features,
                "ring_attire": fighter.ring_attire,
            })
            generated += 1
        except Exception:
            _log.warning("LLM fighter generation failed for entry %s, skipping", entry.get("ring_name", "?"), exc_info=True)
            continue

    return generated
