import random
import time
from datetime import date

from app.config import load_config
from app.engine.fighter_generator import generate_fighter, ARCHETYPES
from app.models.world_state import WorldState
from app.services import data_manager


SUPERNATURAL_ARCHETYPES = {"The Mystic"}
POSSIBLE_SUPERNATURAL = {"The Wildcard", "The Seductress/Seductor", "The Survivor"}


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
    existing_fighters = [
        {"ring_name": f.get("ring_name"), "origin": f.get("origin"), "archetype": f.get("alignment")}
        for f in existing_on_disk
    ]

    fighter_ids = [f.get("id") for f in existing_on_disk]
    for i, (archetype, has_supernatural) in enumerate(slots):
        print(f"[{i + 1}/{len(slots)}] Generating {archetype} {'(supernatural)' if has_supernatural else ''}...")
        try:
            fighter = generate_fighter(
                config, archetype=archetype, has_supernatural=has_supernatural,
                existing_fighters=existing_fighters,
            )
            data_manager.save_fighter(fighter, config)
            fighter_ids.append(fighter.id)
            existing_fighters.append(
                {"ring_name": fighter.ring_name, "origin": fighter.origin, "archetype": archetype}
            )
            print(f"  Created: {fighter.ring_name} ({fighter.real_name}) - {fighter.origin}")
            print(f"  Stats total: {fighter.total_core_stats()}")
        except Exception as e:
            print(f"  ERROR generating fighter: {e}")
            continue

        if i < len(slots) - 1:
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


if __name__ == "__main__":
    generate_roster()
