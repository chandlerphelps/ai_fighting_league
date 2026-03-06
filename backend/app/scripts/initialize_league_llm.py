import argparse
import random
import shutil
import time
from dataclasses import replace
from datetime import date

from app.config import load_config
from app.engine.fighter_generator import (
    generate_fighter,
    plan_roster,
    load_outfit_options,
    filter_outfit_options,
    load_exotic_outfit_options,
    filter_exotic_for_fighter,
    _roll_skimpiness,
)
from app.engine.fighter_config import generate_archetype_stats
from app.engine.between_fights.league_tiers import calculate_tier_rankings
from app.engine.between_fights.retirement import CORE_STATS
from app.services import data_manager


TIER_STAT_RANGES = {
    "apex":        (260, 320),
    "contender":   (210, 270),
    "underground": (150, 220),
}

TIER_AGE_RANGES = {
    "apex":        (27, 32),
    "contender":   (23, 28),
    "underground": (18, 24),
}

TIER_CAREER_SEASONS = {
    "apex":        (5, 10),
    "contender":   (2, 6),
    "underground": (0, 2),
}

POWER_TIER_TO_LEAGUE = {
    "champion":   "apex",
    "contender":  "contender",
    "gatekeeper": "underground",
    "prospect":   "underground",
}


def _rebalance_tiers(entries, target_counts):
    tier_buckets = {"apex": [], "contender": [], "underground": []}
    for entry in entries:
        power_tier = entry.get("power_tier", "prospect").lower()
        league_tier = POWER_TIER_TO_LEAGUE.get(power_tier, "underground")
        entry["_league_tier"] = league_tier
        tier_buckets[league_tier].append(entry)

    for tier in ["apex", "contender"]:
        target = target_counts[tier]
        while len(tier_buckets[tier]) > target:
            demoted = tier_buckets[tier].pop()
            next_tier = "contender" if tier == "apex" else "underground"
            demoted["_league_tier"] = next_tier
            tier_buckets[next_tier].append(demoted)

    for tier in ["apex", "contender"]:
        target = target_counts[tier]
        while len(tier_buckets[tier]) < target:
            source = "contender" if tier == "apex" else "underground"
            if tier_buckets[source]:
                promoted = tier_buckets[source].pop(0)
                promoted["_league_tier"] = tier
                tier_buckets[tier].append(promoted)

    result = []
    for tier in ["apex", "contender", "underground"]:
        result.extend(tier_buckets[tier])
    return result


def initialize_league_llm(apex=8, contender=8, underground=20):
    config = load_config()
    data_dir = config.data_dir
    total = apex + contender + underground

    fighters_dir = data_dir / "fighters"
    if fighters_dir.exists():
        existing_jsons = list(fighters_dir.glob("*.json"))
        if existing_jsons:
            backup_dir = fighters_dir / "bkp_pre_init"
            backup_dir.mkdir(exist_ok=True)
            for f in existing_jsons:
                shutil.move(str(f), str(backup_dir / f.name))
            print(f"Backed up {len(existing_jsons)} existing fighters to {backup_dir}")

    for subdir in ["matches", "events"]:
        d = data_dir / subdir
        if d.exists():
            for f in d.glob("*.json"):
                f.unlink()

    ws_path = data_dir / "world_state.json"
    if ws_path.exists():
        ws_path.unlink()

    data_manager.ensure_data_dirs(config)

    print(f"Planning roster of {total} fighters...")
    entries = plan_roster(config, roster_size=total)
    print(f"  Planned {len(entries)} fighters")

    target_counts = {"apex": apex, "contender": contender, "underground": underground}
    entries = _rebalance_tiers(entries, target_counts)

    tier_counts = {"apex": 0, "contender": 0, "underground": 0}
    for e in entries:
        tier_counts[e["_league_tier"]] += 1
    print(f"  Tier distribution: apex={tier_counts['apex']}, contender={tier_counts['contender']}, underground={tier_counts['underground']}")

    all_outfit_options = load_outfit_options(config)
    all_exotics = load_exotic_outfit_options(config)

    existing_fighters = []
    fighter_ids = []
    fighters_by_tier = {"apex": [], "contender": [], "underground": []}
    rng = random.Random()

    for i, entry in enumerate(entries):
        league_tier = entry["_league_tier"]
        stat_lo, stat_hi = TIER_STAT_RANGES[league_tier]
        tier_config = replace(config, min_total_stats=stat_lo, max_total_stats=stat_hi)

        print(f"[{i + 1}/{len(entries)}] Generating {entry.get('ring_name', '?')} ({league_tier})...")

        skimpiness_level = _roll_skimpiness(entry.get("skimpiness_weights"))
        entry_archetype = entry.get("primary_archetype", "")
        entry_subtype = entry.get("subtype", "")
        outfit_options_by_tier = {}
        for tier in ["sfw", "barely", "nsfw"]:
            tier_options = all_outfit_options.get(tier, {})
            tier_exotics = None
            if entry_archetype or entry_subtype:
                tier_exotics = filter_exotic_for_fighter(
                    all_exotics, archetype=entry_archetype, subtype=entry_subtype,
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

            age_lo, age_hi = TIER_AGE_RANGES[league_tier]
            career_lo, career_hi = TIER_CAREER_SEASONS[league_tier]
            fighter.age = rng.randint(age_lo, age_hi)
            fighter.tier = league_tier
            fighter.status = "active"
            fighter.peak_tier = league_tier
            fighter.career_season_count = rng.randint(career_lo, career_hi)
            fighter.training_focus = rng.choice(list(CORE_STATS))
            fighter.generation_stage = 1

            data_manager.save_fighter(fighter, config)
            fighter_ids.append(fighter.id)
            fighters_by_tier[league_tier].append(fighter)

            existing_fighters.append({
                "ring_name": fighter.ring_name,
                "gender": fighter.gender,
                "height": fighter.height,
                "origin": fighter.origin,
                "primary_archetype": fighter.primary_archetype,
                "subtype": fighter.subtype,
                "build": fighter.build,
                "personality": fighter.personality,
                "distinguishing_features": fighter.distinguishing_features,
                "ring_attire": fighter.ring_attire,
            })
            print(f"  Created: {fighter.ring_name} ({fighter.real_name}) - {fighter.origin} | Stats: {fighter.total_core_stats()}")
        except Exception as e:
            print(f"  ERROR generating fighter: {e}")
            continue

        if i < len(entries) - 1:
            time.sleep(1)

    all_fighters_dicts = []
    for tier in ["apex", "contender", "underground"]:
        for f in fighters_by_tier[tier]:
            all_fighters_dicts.append(f.to_dict())

    tier_rankings = {}
    for tier in ["apex", "contender", "underground"]:
        tier_rankings[tier] = calculate_tier_rankings(all_fighters_dicts, tier)

    belt_holder_id = ""
    apex_fighters = fighters_by_tier["apex"]
    if apex_fighters:
        strongest = max(apex_fighters, key=lambda f: f.total_core_stats())
        belt_holder_id = strongest.id

    today = date.today()
    ws = {
        "current_date": today.isoformat(),
        "day_number": 0,
        "season_number": 1,
        "season_month": today.month,
        "season_day_in_month": today.day,
        "tier_rankings": tier_rankings,
        "belt_holder_id": belt_holder_id,
        "belt_history": [{
            "fighter_id": belt_holder_id,
            "won_date": "season_0",
            "lost_date": None,
            "defenses": 0,
        }] if belt_holder_id else [],
        "season_champions": [],
        "retired_fighter_ids": [],
        "active_injuries": {},
        "rivalry_graph": [],
        "recent_matches": [],
        "season_logs": [],
        "promotion_fights": [],
        "title_fight": {},
        "rankings": list(tier_rankings.get("apex", []))
            + list(tier_rankings.get("contender", []))
            + list(tier_rankings.get("underground", [])),
        "upcoming_events": [],
        "completed_events": [],
        "last_daily_summary": "League initialized with LLM-generated fighters.",
        "event_counter": 0,
        "tier_sizes": {"apex": apex, "contender": contender, "underground": underground},
    }

    data_manager.save_world_state(ws, config)

    print(f"\nLeague initialized!")
    print(f"  Fighters created: {len(fighter_ids)}")
    print(f"  Apex: {len(tier_rankings['apex'])} fighters")
    print(f"  Contender: {len(tier_rankings['contender'])} fighters")
    print(f"  Underground: {len(tier_rankings['underground'])} fighters")
    if belt_holder_id:
        champ = next((f for f in apex_fighters if f.id == belt_holder_id), None)
        if champ:
            print(f"  Belt holder: {champ.ring_name}")
    print(f"  World state saved to {data_dir / 'world_state.json'}")


def main():
    parser = argparse.ArgumentParser(description="Initialize AI Fighting League with LLM-generated fighters")
    parser.add_argument("--apex", type=int, default=8, help="Number of Apex tier fighters (default: 8)")
    parser.add_argument("--contender", type=int, default=8, help="Number of Contender tier fighters (default: 8)")
    parser.add_argument("--underground", type=int, default=20, help="Number of Underground tier fighters (default: 20)")
    args = parser.parse_args()

    initialize_league_llm(apex=args.apex, contender=args.contender, underground=args.underground)


if __name__ == "__main__":
    main()
