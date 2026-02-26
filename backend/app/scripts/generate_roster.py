import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

from app.config import load_config
from app.engine.fighter_generator import generate_fighter, plan_roster, ARCHETYPES
from app.models.world_state import WorldState
from app.services import data_manager


SUPERNATURAL_ARCHETYPES = {"The Mystic"}
POSSIBLE_SUPERNATURAL = {"The Wildcard", "The Seductress/Seductor", "The Survivor"}

MAX_WORKERS = 4


def _generate_one(config, blueprint, index, total):
    label = f"{blueprint.get('ring_name', '?')} ({blueprint.get('archetype', '?')})"
    print(f"  [{index + 1}/{total}] Generating {label}...")
    fighter = generate_fighter(config, blueprint=blueprint)
    print(f"  [{index + 1}/{total}] Done: {fighter.ring_name} ({fighter.real_name}) - {fighter.origin} | Stats: {fighter.total_core_stats()}")
    return fighter


def generate_roster():
    config = load_config()
    data_manager.ensure_data_dirs(config)

    slots = []
    for archetype in ARCHETYPES:
        slots.append((archetype, archetype in SUPERNATURAL_ARCHETYPES))
        has_super = archetype in POSSIBLE_SUPERNATURAL and random.random() < 0.5
        slots.append((archetype, has_super))

    random.shuffle(slots)

    existing_on_disk = data_manager.load_all_fighters(config)
    fighter_ids = [f.get("id") for f in existing_on_disk]
    remaining_slots = slots[len(existing_on_disk):]

    if not remaining_slots:
        print("Roster already complete on disk.")
    else:
        print(f"Planning {len(remaining_slots)} fighters...")
        blueprints = plan_roster(config, remaining_slots)
        print(f"Roster planned! Generating {len(blueprints)} fighters in parallel (workers={MAX_WORKERS})...\n")

        fighters = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(_generate_one, config, bp, i, len(blueprints)): i
                for i, bp in enumerate(blueprints)
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    fighter = future.result()
                    data_manager.save_fighter(fighter, config)
                    fighters.append(fighter)
                except Exception as e:
                    print(f"  ERROR on fighter {idx + 1}: {e}")

        fighter_ids.extend(f.id for f in fighters)

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


if __name__ == "__main__":
    generate_roster()
