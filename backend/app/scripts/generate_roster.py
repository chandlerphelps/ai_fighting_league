import argparse
import json
import random
import time
from datetime import date

from app.config import load_config
from app.engine.fighter_generator import generate_fighter, plan_roster
from app.models.world_state import WorldState
from app.services import data_manager


def plan_roster_cmd():
    config = load_config()
    data_manager.ensure_data_dirs(config)

    existing_on_disk = data_manager.load_all_fighters(config)
    existing_fighters = [
        {
            "ring_name": f.get("ring_name"),
            "gender": f.get("gender", ""),
            "origin": f.get("origin"),
        }
        for f in existing_on_disk
    ] or None

    print(f"Planning roster of {config.roster_size} fighters...")
    roster_plan = plan_roster(config, roster_size=config.roster_size, existing_fighters=existing_fighters)

    plan_path = config.data_dir / "roster_plan.json"
    with open(plan_path, "w") as f:
        json.dump(roster_plan, f, indent=2)

    print(f"\nRoster plan saved to {plan_path}")
    print(f"  Fighters planned: {len(roster_plan)}")
    print()
    for i, entry in enumerate(roster_plan):
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


def generate_from_plan():
    config = load_config()
    data_manager.ensure_data_dirs(config)

    plan_path = config.data_dir / "roster_plan.json"
    if not plan_path.exists():
        print(f"No roster plan found at {plan_path}")
        print("Run with --plan first to create one.")
        return

    with open(plan_path) as f:
        roster_plan = json.load(f)

    print(f"Generating {len(roster_plan)} fighters from plan...")

    existing_on_disk = data_manager.load_all_fighters(config)
    existing_fighters = [
        {
            "ring_name": f.get("ring_name"),
            "gender": f.get("gender", ""),
            "height": f.get("height", ""),
            "origin": f.get("origin"),
            "build": f.get("build", ""),
            "distinguishing_features": f.get("distinguishing_features", ""),
            "ring_attire": f.get("ring_attire", ""),
        }
        for f in existing_on_disk
    ]

    fighter_ids = [f.get("id") for f in existing_on_disk]

    for i, entry in enumerate(roster_plan):
        print(f"[{i + 1}/{len(roster_plan)}] Generating {entry.get('ring_name', '?')}...")
        try:
            fighter = generate_fighter(
                config,
                existing_fighters=existing_fighters,
                roster_plan_entry=entry,
            )
            data_manager.save_fighter(fighter, config)
            fighter_ids.append(fighter.id)
            existing_fighters.append({
                "ring_name": fighter.ring_name,
                "gender": fighter.gender,
                "height": fighter.height,
                "origin": fighter.origin,
                "build": fighter.build,
                "distinguishing_features": fighter.distinguishing_features,
                "ring_attire": fighter.ring_attire,
            })
            print(f"  Created: {fighter.ring_name} ({fighter.real_name}) - {fighter.origin}")
            print(f"  Stats total: {fighter.total_core_stats()}")
        except Exception as e:
            print(f"  ERROR generating fighter: {e}")
            continue

        if i < len(roster_plan) - 1:
            time.sleep(1)

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


def generate_roster():
    plan_roster_cmd()
    print("\n" + "=" * 60 + "\n")
    generate_from_plan()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AFL roster")
    parser.add_argument("--plan", action="store_true", help="Phase 1: plan roster only (saves to data/roster_plan.json)")
    parser.add_argument("--generate", action="store_true", help="Phase 2: generate fighters from existing plan")
    args = parser.parse_args()

    if args.plan:
        plan_roster_cmd()
    elif args.generate:
        generate_from_plan()
    else:
        generate_roster()
