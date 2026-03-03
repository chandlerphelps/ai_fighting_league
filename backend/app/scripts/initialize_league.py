import argparse
import json
import shutil
import sys
from pathlib import Path

from app.scripts.simulate_seasons import LeagueSimulator
from app.services import data_manager
from app.config import load_config


def initialize_league(seasons=30, seed=42, verbose=False):
    config = load_config()
    data_dir = config.data_dir

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

    data_manager.ensure_data_dirs(config)

    print(f"Generating league and simulating {seasons} seasons (seed={seed})...")
    sim = LeagueSimulator(seed=seed, verbose=verbose)
    sim.generate_initial_roster()

    for s in range(seasons):
        sim.simulate_season()
        season_num = sim.world_state["season_number"] - 1
        champions = sim.world_state.get("season_champions", [])
        season_champ = next((c for c in champions if c["season"] == season_num), None)
        champ_name = season_champ["ring_name"] if season_champ else "None"
        active = sum(1 for f in sim.fighters.values() if f.get("status") == "active")
        sys.stdout.write(f"\r  Season {season_num:3d}/{seasons} | Champion: {champ_name:20s} | Active: {active} | Fights: {sim.total_fights_run}")
        sys.stdout.flush()

    print(f"\n  Simulation complete. {sim.total_fights_run} total fights.")

    active_count = 0
    for fid, fighter in sim.fighters.items():
        if fighter.get("status") != "active":
            continue
        data_manager.save_fighter(fighter, config)
        active_count += 1
    print(f"  Saved {active_count} active fighters to {fighters_dir}")

    recent_matches = []
    for match in sim.season_matches[-100:]:
        outcome = match.get("outcome", {})
        f1 = sim.fighters.get(match["fighter1_id"], {})
        f2 = sim.fighters.get(match["fighter2_id"], {})
        recent_matches.append({
            "fighter1_id": match["fighter1_id"],
            "fighter1_name": f1.get("ring_name", match["fighter1_id"]),
            "fighter2_id": match["fighter2_id"],
            "fighter2_name": f2.get("ring_name", match["fighter2_id"]),
            "winner_id": outcome.get("winner_id", ""),
            "method": outcome.get("method", ""),
            "round_ended": outcome.get("round_ended", 0),
            "tier": f1.get("tier", "underground"),
            "date": match.get("date", ""),
        })

    season_summaries = []
    for log in sim.season_logs:
        season_champ = next((c for c in sim.world_state.get("season_champions", []) if c["season"] == log["season"]), None)
        season_summaries.append({
            "season": log["season"],
            "champion_name": season_champ["ring_name"] if season_champ else "None",
            "champion_id": season_champ["fighter_id"] if season_champ else "",
            "belt_holder_name": sim.fighters.get(sim.world_state.get("belt_holder_id", ""), {}).get("ring_name", "VACANT"),
            "belt_holder_id": sim.world_state.get("belt_holder_id", ""),
            "retirements": len(log.get("retirements", [])),
            "new_fighters": len(log.get("new_fighters", [])),
            "tier_counts": log.get("tier_counts_after", {}),
        })

    ws = {
        "current_date": "2026-03-03",
        "day_number": sim.world_state.get("day_number", 0),
        "season_number": sim.world_state["season_number"],
        "season_month": sim.world_state["season_month"],
        "season_day_in_month": sim.world_state["season_day_in_month"],
        "tier_rankings": sim.world_state["tier_rankings"],
        "belt_holder_id": sim.world_state.get("belt_holder_id", ""),
        "belt_history": sim.world_state.get("belt_history", []),
        "season_champions": sim.world_state.get("season_champions", []),
        "retired_fighter_ids": sim.world_state.get("retired_fighter_ids", []),
        "active_injuries": {},
        "rivalry_graph": [],
        "recent_matches": recent_matches,
        "season_logs": season_summaries,
        "promotion_fights": [],
        "title_fight": {},
        "rankings": list(sim.world_state["tier_rankings"].get("championship", []))
            + list(sim.world_state["tier_rankings"].get("contender", []))
            + list(sim.world_state["tier_rankings"].get("underground", [])),
        "upcoming_events": [],
        "completed_events": [],
        "last_daily_summary": f"League initialized after {seasons} seasons of history.",
        "event_counter": 0,
    }

    data_manager.save_world_state(ws, config)
    print(f"  Saved world_state.json (Season {ws['season_number']}, Month {ws['season_month']})")

    champions = ws.get("season_champions", [])
    latest_champ = champions[-1] if champions else None
    if latest_champ:
        print(f"\n  Latest Season Champion: {latest_champ['ring_name']}")
    else:
        print(f"\n  Latest Season Champion: None")
    print(f"  Championship: {len(ws['tier_rankings']['championship'])} fighters")
    print(f"  Contender: {len(ws['tier_rankings']['contender'])} fighters")
    print(f"  Underground: {len(ws['tier_rankings']['underground'])} fighters")


def main():
    parser = argparse.ArgumentParser(description="Initialize AI Fighting League with history")
    parser.add_argument("--seasons", type=int, default=30, help="Number of seasons to pre-simulate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-season details")
    args = parser.parse_args()

    initialize_league(seasons=args.seasons, seed=args.seed, verbose=args.verbose)


if __name__ == "__main__":
    main()
