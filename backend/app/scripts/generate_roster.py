import argparse
import json
import random
import time
from datetime import date

from app.config import load_config
from app.engine.fighter_generator import generate_fighter, plan_roster, load_outfit_options, filter_outfit_options, load_exotic_outfit_options, filter_exotic_for_fighter, _roll_skimpiness
from app.models.world_state import WorldState
from app.services import data_manager
from app.services.grok_image import generate_charsheet_images


def plan_roster_cmd():
    config = load_config()
    data_manager.ensure_data_dirs(config)

    existing_on_disk = data_manager.load_all_fighters(config)
    existing_fighters = [
        {
            "ring_name": f.get("ring_name"),
            "gender": f.get("gender", ""),
            "origin": f.get("origin"),
            "primary_archetype": f.get("primary_archetype", ""),
            "subtype": f.get("subtype", ""),
            "build": f.get("build", ""),
            "personality": f.get("personality", ""),
        }
        for f in existing_on_disk
    ] or None

    print(f"Planning roster of {config.roster_size} fighters...")
    entries = plan_roster(config, roster_size=config.roster_size, existing_fighters=existing_fighters)

    for entry in entries:
        entry.setdefault("status", "pending")
        entry.setdefault("fighter_id", None)
        entry.setdefault("primary_outfit_color", "")
        entry.setdefault("hair_style", "")
        entry.setdefault("hair_color", "")
        entry.setdefault("face_adornment", "")

    import uuid as _uuid
    roster_plan = {
        "plan_id": f"rp_{_uuid.uuid4().hex[:8]}",
        "created_at": str(date.today()),
        "mode": "initial",
        "pool_summary": "",
        "entries": entries,
    }

    plan_path = config.data_dir / "roster_plan.json"
    with open(plan_path, "w") as f:
        json.dump(roster_plan, f, indent=2)

    print(f"\nRoster plan saved to {plan_path}")
    print(f"  Fighters planned: {len(entries)}")
    print()
    for i, entry in enumerate(entries):
        supernatural_tag = f" [{entry.get('supernatural_type', '')}]" if entry.get("has_supernatural") else ""
        print(
            f"  {i + 1}. {entry.get('ring_name', '?')} — {entry.get('gender', '?')}, "
            f"{entry.get('alignment', '?')}, {entry.get('primary_archetype', '?')}"
            f"{supernatural_tag}"
        )
        print(f"     {entry.get('concept_hook', '')}")
        print(f"     Style: {entry.get('fighting_style_concept', '')}")
        print(f"     From: {entry.get('origin', '?')} | Tier: {entry.get('power_tier', '?')}")
        rivals = entry.get("rivalry_seeds", [])
        if rivals:
            print(f"     Rivals: {', '.join(rivals)}")
        print()

    print("Review the plan, then run with --generate to create the fighters.")


def generate_from_plan(generate_images: bool = False, tiers: list[str] | None = None, count: int | None = None):
    config = load_config()
    data_manager.ensure_data_dirs(config)

    plan_path = config.data_dir / "roster_plan.json"
    if not plan_path.exists():
        print(f"No roster plan found at {plan_path}")
        print("Run with --plan first to create one.")
        return

    with open(plan_path) as f:
        raw = json.load(f)

    roster_plan = raw.get("entries", raw) if isinstance(raw, dict) else raw

    if count is not None:
        roster_plan = roster_plan[:count]

    print(f"Generating {len(roster_plan)} fighters from plan...")

    all_outfit_options = load_outfit_options(config)
    all_exotics = load_exotic_outfit_options(config)

    existing_on_disk = data_manager.load_all_fighters(config)
    existing_fighters = [
        {
            "ring_name": f.get("ring_name"),
            "gender": f.get("gender", ""),
            "height": f.get("height", ""),
            "origin": f.get("origin"),
            "primary_archetype": f.get("primary_archetype", ""),
            "subtype": f.get("subtype", ""),
            "build": f.get("build", ""),
            "personality": f.get("personality", ""),
            "distinguishing_features": f.get("distinguishing_features", ""),
            "ring_attire": f.get("ring_attire", ""),
        }
        for f in existing_on_disk
    ]

    fighter_ids = [f.get("id") for f in existing_on_disk]

    for i, entry in enumerate(roster_plan):
        print(f"[{i + 1}/{len(roster_plan)}] Generating {entry.get('ring_name', '?')}...")

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
                config,
                existing_fighters=existing_fighters,
                roster_plan_entry=entry,
                tiers=tiers,
                outfit_options_by_tier=outfit_options_by_tier,
                skimpiness_level=skimpiness_level,
            )
            data_manager.save_fighter(fighter, config)
            fighter_ids.append(fighter.id)
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
            print(f"  Created: {fighter.ring_name} ({fighter.real_name}) - {fighter.origin}")
            print(f"  Stats total: {fighter.total_core_stats()}")

            if generate_images:
                try:
                    fighters_dir = config.data_dir / "fighters"
                    generate_charsheet_images(fighter, config, fighters_dir)
                except Exception as img_err:
                    print(f"  WARNING: Image generation failed: {img_err}")
        except Exception as e:
            print(f"  ERROR generating fighter: {e}")
            continue

        if i < len(roster_plan) - 1:
            time.sleep(1)

    existing_ws = data_manager.load_world_state(config)
    if existing_ws:
        for fid in fighter_ids:
            if fid not in existing_ws.get("rankings", []):
                existing_ws["rankings"].append(fid)
        data_manager.save_world_state(existing_ws, config)
    else:
        random.shuffle(fighter_ids)
        start_date = date.today().isoformat()
        world_state = WorldState(
            current_date=start_date,
            day_number=0,
            rankings=fighter_ids,
            upcoming_events=[],
            completed_events=[],
            active_injuries={},
            rivalry_graph=[],
            last_daily_summary="League initialized. Let the fights begin.",
            event_counter=0,
        )
        data_manager.save_world_state(world_state, config)

    print(f"\nRoster generation complete!")
    print(f"  Fighters created: {len(fighter_ids)}")
    print(f"  Start date: {start_date}")
    print(f"  World state saved to data/world_state.json")


def generate_roster(generate_images: bool = False, tiers: list[str] | None = None, count: int | None = None):
    plan_roster_cmd()
    print("\n" + "=" * 60 + "\n")
    generate_from_plan(generate_images=generate_images, tiers=tiers, count=count)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AFL roster")
    parser.add_argument("--plan", action="store_true", help="Phase 1: plan roster only (saves to data/roster_plan.json)")
    parser.add_argument("--generate", action="store_true", help="Phase 2: generate fighters from existing plan")
    parser.add_argument("--images", action="store_true", help="Generate character sheet images for each fighter via Grok API")
    parser.add_argument("--tiers", nargs="+", choices=["sfw", "barely", "nsfw"], help="Which outfit tiers to generate (default: all three)")
    parser.add_argument("-n", "--count", type=int, help="Number of fighters to generate from the plan")
    args = parser.parse_args()

    if args.plan:
        plan_roster_cmd()
    elif args.generate:
        generate_from_plan(generate_images=args.images, tiers=args.tiers, count=args.count)
    else:
        generate_roster(generate_images=args.images, tiers=args.tiers, count=args.count)
