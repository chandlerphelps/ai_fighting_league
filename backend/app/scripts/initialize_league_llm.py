import argparse
import random
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from datetime import date
from pathlib import Path

from app.config import load_config
from app.engine.fighter_generator import (
    generate_fighter,
    plan_roster,
    load_outfit_options,
    filter_outfit_options,
    load_exotic_outfit_options,
    filter_exotic_for_fighter,
    _roll_skimpiness,
    _find_subtype,
    _build_charsheet_prompt,
)
from app.engine.fighter_config import generate_archetype_stats
from app.engine.between_fights.league_tiers import calculate_tier_rankings
from app.engine.between_fights.retirement import CORE_STATS
from app.models.fighter import Fighter
from app.prompts.image_builders import build_portrait_prompt, build_body_reference_prompt, build_headshot_prompt
from app.services import data_manager
from app.services.grok_image import generate_charsheet_images, generate_image, edit_image, download_image, _slugify as img_slugify


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
            elif tier == "apex" and tier_buckets["underground"]:
                promoted = tier_buckets["underground"].pop(0)
                promoted["_league_tier"] = tier
                tier_buckets[tier].append(promoted)
            else:
                break

    result = []
    for tier in ["apex", "contender", "underground"]:
        result.extend(tier_buckets[tier])
    return result


def initialize_league_llm(apex=8, contender=8, underground=20, full_generate=False, gender_mix="mixed"):
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
    entries = plan_roster(config, roster_size=total, gender_mix=gender_mix)
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

    BATCH_SIZE = 4

    def _prepare_and_generate(entry, entry_index, existing_snapshot):
        league_tier = entry["_league_tier"]
        stat_lo, stat_hi = TIER_STAT_RANGES[league_tier]
        tier_config = replace(config, min_total_stats=stat_lo, max_total_stats=stat_hi)

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

        fighter = generate_fighter(
            tier_config,
            existing_fighters=existing_snapshot,
            roster_plan_entry=entry,
            outfit_options_by_tier=outfit_options_by_tier,
            skimpiness_level=skimpiness_level,
            skip_image_prompts=not full_generate,
        )
        return entry_index, entry, fighter

    for batch_start in range(0, len(entries), BATCH_SIZE):
        batch = entries[batch_start:batch_start + BATCH_SIZE]
        existing_snapshot = list(existing_fighters)

        batch_labels = [f"{e.get('ring_name', '?')} ({e['_league_tier']})" for e in batch]
        print(f"[Batch {batch_start // BATCH_SIZE + 1}] Generating: {', '.join(batch_labels)}...")

        results = []
        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as pool:
            futures = {
                pool.submit(_prepare_and_generate, entry, batch_start + j, existing_snapshot): batch_start + j
                for j, entry in enumerate(batch)
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    print(f"  ERROR [{idx + 1}/{len(entries)}]: {e}")

        results.sort(key=lambda r: r[0])

        for entry_index, entry, fighter in results:
            league_tier = entry["_league_tier"]
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
            print(f"  [{entry_index + 1}/{len(entries)}] Created: {fighter.ring_name} ({fighter.real_name}) - {fighter.origin} | Stats: {fighter.total_core_stats()}")

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

    if full_generate:
        print(f"\nAdvancing all fighters through stages 2 and 3...")
        fighters_dir = data_dir / "fighters"
        _advance_all_fighters(fighter_ids, config, fighters_dir)
        print(f"  All fighters fully generated (stage 3).")


def _get_subtype_info(fighter_data: dict) -> dict | None:
    archetype = fighter_data.get("primary_archetype", "")
    subtype_name = fighter_data.get("subtype", "")
    if archetype and subtype_name:
        return _find_subtype(archetype, subtype_name, gender=fighter_data.get("gender", "female"))
    return None


def _rebuild_prompts(fighter_data: dict):
    body_parts = fighter_data.get("image_prompt_body_parts", "")
    if not body_parts:
        body_parts = fighter_data.get("image_prompt", {}).get("body_parts", "")
    if not body_parts:
        body_parts = fighter_data.get("image_prompt_sfw", {}).get("body_parts", "")
    expression = fighter_data.get("image_prompt_expression", "")
    if not expression:
        expression = fighter_data.get("image_prompt", {}).get("expression", "")
    if not expression:
        expression = fighter_data.get("image_prompt_sfw", {}).get("expression", "")
    personality_pose = fighter_data.get("image_prompt_personality_pose", "")
    gender = fighter_data.get("gender", "female")
    skimpiness = fighter_data.get("skimpiness_level", 2)
    subtype_info = _get_subtype_info(fighter_data)
    iconic_features = fighter_data.get("iconic_features", "")

    clothing_sfw = fighter_data.get("ring_attire_sfw", "") or fighter_data.get("image_prompt_sfw", {}).get("clothing", "")
    clothing_barely = fighter_data.get("ring_attire", "") or fighter_data.get("image_prompt", {}).get("clothing", "")
    clothing_nsfw = fighter_data.get("ring_attire_nsfw", "") or fighter_data.get("image_prompt_nsfw", {}).get("clothing", "")

    age = fighter_data.get("age", 0)
    origin = fighter_data.get("origin", "")
    body_type_details = fighter_data.get("body_type_details")
    primary_outfit_color = fighter_data.get("primary_outfit_color", "")
    fighter_data["image_prompt_sfw"] = _build_charsheet_prompt(
        body_parts, clothing_sfw, expression,
        personality_pose=personality_pose, tier="sfw",
        gender=gender, skimpiness_level=skimpiness,
        body_type_details=body_type_details, origin=origin,
        subtype_info=subtype_info, iconic_features=iconic_features,
        age=age, primary_outfit_color=primary_outfit_color,
    )
    fighter_data["image_prompt"] = _build_charsheet_prompt(
        body_parts, clothing_barely, expression,
        personality_pose=personality_pose, tier="barely",
        gender=gender, skimpiness_level=skimpiness,
        body_type_details=body_type_details, origin=origin,
        subtype_info=subtype_info, iconic_features=iconic_features,
        age=age, primary_outfit_color=primary_outfit_color,
    )
    if gender.lower() == "male":
        fighter_data["image_prompt_nsfw"] = fighter_data["image_prompt"]
    else:
        fighter_data["image_prompt_nsfw"] = _build_charsheet_prompt(
            body_parts, clothing_nsfw, expression,
            personality_pose=personality_pose, tier="nsfw",
            gender=gender, skimpiness_level=skimpiness,
            body_type_details=body_type_details, origin=origin,
            subtype_info=subtype_info, iconic_features=iconic_features,
            age=age, primary_outfit_color=primary_outfit_color,
        )
    if not fighter_data.get("image_prompt_body_ref", {}).get("full_prompt"):
        fighter_data["image_prompt_body_ref"] = build_body_reference_prompt(
            body_parts, expression,
            gender=gender, body_type_details=body_type_details,
            origin=origin, subtype_info=subtype_info,
            age=age, iconic_features=iconic_features,
        )
    fighter_data["image_prompt_headshot"] = build_headshot_prompt(
        body_parts, expression,
        gender=gender, body_type_details=body_type_details,
        origin=origin, subtype_info=subtype_info,
        iconic_features=iconic_features, age=age,
    )


def _generate_stage1_images(fighter_data: dict, config, fighters_dir: Path) -> None:
    fid = fighter_data.get("id", "")
    gender = fighter_data.get("gender", "female")
    is_male = gender.lower() == "male"
    slug = img_slugify(fighter_data.get("ring_name", ""))
    base = f"{fid}_{slug}" if slug else fid

    body_ref_prompt = fighter_data.get("image_prompt_body_ref", {}).get("full_prompt", "")
    body_ref_path = fighters_dir / f"{base}_body_ref.png"

    if body_ref_prompt and not body_ref_path.exists():
        print(f"    Generating body reference image for {fid}...")
        female_ref = config.data_dir / "reference_images" / "female" / "pussy_asshole_behind2.png"
        if not is_male and female_ref.exists():
            urls = edit_image(
                prompt=body_ref_prompt, image_paths=[female_ref],
                config=config, aspect_ratio="1:1", resolution="2k", n=1, pad_to_aspect=True,
            )
        else:
            urls = generate_image(
                prompt=body_ref_prompt, config=config,
                aspect_ratio="1:1", resolution="2k", n=1,
            )
        if urls:
            download_image(urls[0], body_ref_path)

    def _gen_variant(prompt_full, save_path, label):
        if not prompt_full:
            return
        if body_ref_path.exists():
            print(f"    Generating {label} from body reference for {fid}...")
            urls = edit_image(
                prompt=prompt_full, image_paths=[body_ref_path],
                config=config, aspect_ratio="1:1", resolution="2k", n=1,
            )
        else:
            print(f"    Generating {label} for {fid}...")
            urls = generate_image(
                prompt=prompt_full, config=config,
                aspect_ratio="1:1", resolution="2k", n=1,
            )
        if urls:
            download_image(urls[0], save_path)

    portrait_full = fighter_data.get("image_prompt_portrait", {}).get("full_prompt", "")
    headshot_full = fighter_data.get("image_prompt_headshot", {}).get("full_prompt", "")
    portrait_path = fighters_dir / f"{base}_portrait.png"
    headshot_path = fighters_dir / f"{base}_headshot.png"

    with ThreadPoolExecutor(max_workers=2) as pool:
        futs = []
        if portrait_full:
            futs.append(pool.submit(_gen_variant, portrait_full, portrait_path, "portrait"))
        if headshot_full:
            futs.append(pool.submit(_gen_variant, headshot_full, headshot_path, "headshot"))
        for fut in as_completed(futs):
            fut.result()


def _advance_fighter_to_stage3(fid: str, config, fighters_dir: Path) -> str:
    fighter_data = data_manager.load_fighter(fid, config)
    if not fighter_data:
        return f"{fid}: not found"

    current = fighter_data.get("generation_stage", 0)
    ring_name = fighter_data.get("ring_name", fid)

    if current < 1:
        return f"{ring_name}: skipped (stage 0)"
    if current >= 3:
        return f"{ring_name}: already at stage 3"

    if current == 1:
        print(f"  [{ring_name}] Stage 1 -> 2: generating reference images...")
        body_parts = fighter_data.get("image_prompt_body_parts", "")
        if not body_parts:
            body_parts = fighter_data.get("image_prompt", {}).get("body_parts", "")
        if not body_parts:
            body_parts = fighter_data.get("image_prompt_sfw", {}).get("body_parts", "")
        expression = fighter_data.get("image_prompt_expression", "")
        if not expression:
            expression = fighter_data.get("image_prompt", {}).get("expression", "")
        if not expression:
            expression = fighter_data.get("image_prompt_sfw", {}).get("expression", "")

        gender = fighter_data.get("gender", "female")
        subtype_info = _get_subtype_info(fighter_data)
        iconic_features = fighter_data.get("iconic_features", "")
        age = fighter_data.get("age", 0)

        fighter_data["image_prompt_portrait"] = build_portrait_prompt(
            body_parts, fighter_data.get("ring_attire_sfw", ""), expression,
            gender=gender, body_type_details=fighter_data.get("body_type_details"),
            origin=fighter_data.get("origin", ""), subtype_info=subtype_info,
            iconic_features=iconic_features,
            primary_outfit_color=fighter_data.get("primary_outfit_color", ""),
            age=age,
        )
        if not fighter_data.get("image_prompt_body_ref"):
            fighter_data["image_prompt_body_ref"] = build_body_reference_prompt(
                body_parts, expression, gender=gender,
                body_type_details=fighter_data.get("body_type_details"),
                origin=fighter_data.get("origin", ""), subtype_info=subtype_info,
                age=age, iconic_features=iconic_features,
            )
        fighter_data["image_prompt_headshot"] = build_headshot_prompt(
            body_parts, expression, gender=gender,
            body_type_details=fighter_data.get("body_type_details"),
            origin=fighter_data.get("origin", ""), subtype_info=subtype_info,
            iconic_features=iconic_features, age=age,
        )

        _generate_stage1_images(fighter_data, config, fighters_dir)
        fighter_data["generation_stage"] = 2
        fighter_data["generation_dirty"] = [
            d for d in fighter_data.get("generation_dirty", []) if d != "images"
        ]
        data_manager.save_fighter(fighter_data, config)

    print(f"  [{ring_name}] Stage 2 -> 3: generating charsheet images...")
    fighter = Fighter.from_dict(fighter_data)
    if not fighter.image_prompt_body_ref:
        body_parts = fighter_data.get("image_prompt_body_parts", "")
        if not body_parts:
            body_parts = fighter_data.get("image_prompt", {}).get("body_parts", "")
        expression = fighter_data.get("image_prompt_expression", "")
        if not expression:
            expression = fighter_data.get("image_prompt", {}).get("expression", "")
        subtype_info = _get_subtype_info(fighter_data)
        fighter.image_prompt_body_ref = build_body_reference_prompt(
            body_parts, expression, gender=fighter.gender,
            body_type_details=fighter_data.get("body_type_details"),
            origin=fighter.origin, subtype_info=subtype_info,
            age=fighter.age, iconic_features=fighter_data.get("iconic_features", ""),
        )
    if not fighter.image_prompt_sfw or not fighter.image_prompt_sfw.get("full_prompt"):
        _rebuild_prompts(fighter_data)
        fighter = Fighter.from_dict(fighter_data)

    generate_charsheet_images(fighter, config, fighters_dir)
    fighter_data = fighter.to_dict()
    fighter_data["generation_stage"] = 3
    fighter_data["generation_dirty"] = []
    data_manager.save_fighter(fighter_data, config)

    return f"{ring_name}: fully generated (stage 3)"


def _advance_all_fighters(fighter_ids: list, config, fighters_dir: Path):
    PARALLEL = 2
    for batch_start in range(0, len(fighter_ids), PARALLEL):
        batch = fighter_ids[batch_start:batch_start + PARALLEL]
        with ThreadPoolExecutor(max_workers=PARALLEL) as pool:
            futures = {pool.submit(_advance_fighter_to_stage3, fid, config, fighters_dir): fid for fid in batch}
            for future in as_completed(futures):
                fid = futures[future]
                try:
                    result = future.result()
                    print(f"    {result}")
                except Exception as e:
                    print(f"    ERROR advancing {fid}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Initialize AI Fighting League with LLM-generated fighters")
    parser.add_argument("--apex", type=int, default=8, help="Number of Apex tier fighters (default: 8)")
    parser.add_argument("--contender", type=int, default=8, help="Number of Contender tier fighters (default: 8)")
    parser.add_argument("--underground", type=int, default=20, help="Number of Underground tier fighters (default: 20)")
    parser.add_argument("--full-generate", action="store_true", help="Fully generate all fighters through stage 3 (images)")
    parser.add_argument("--gender", choices=["mixed", "female", "male"], default="mixed", help="Gender mix for roster (default: mixed)")
    args = parser.parse_args()

    initialize_league_llm(apex=args.apex, contender=args.contender, underground=args.underground, full_generate=args.full_generate, gender_mix=args.gender)


if __name__ == "__main__":
    main()
