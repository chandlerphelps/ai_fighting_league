import argparse
import sys
from pathlib import Path

from app.config import load_config
from app.engine.day_ticker import advance_day
from app.services import data_manager


def main():
    parser = argparse.ArgumentParser(description="AI Fighting League — Advance the league by one or more days")
    parser.add_argument("--days", type=int, default=1, help="Number of days to advance (default: 1)")
    parser.add_argument("--init", action="store_true", help="Initialize roster and world state if data is empty")
    args = parser.parse_args()

    config = load_config()

    if not config.openrouter_api_key:
        print("ERROR: OPENROUTER_API_KEY not set. Check your backend/.env file.")
        sys.exit(1)

    data_manager.ensure_data_dirs(config)

    if args.init:
        fighters = data_manager.load_all_fighters(config)
        if not fighters:
            print("Initializing roster...")
            from app.scripts.generate_roster import generate_roster
            generate_roster()
            print()

    ws = data_manager.load_world_state(config)
    if not ws:
        print("ERROR: No world state found. Run with --init to create one.")
        sys.exit(1)

    print(f"Starting from: Day {ws.get('day_number', 0)} — {ws.get('current_date', 'unknown')}")
    print(f"Advancing {args.days} day(s)...\n")

    for day in range(args.days):
        try:
            summary = advance_day(config)
            print(summary)
        except Exception as e:
            print(f"ERROR on day advance: {e}")
            import traceback
            traceback.print_exc()
            break

    ws = data_manager.load_world_state(config)
    if ws:
        print(f"\nFinal state: Day {ws.get('day_number', 0)} — {ws.get('current_date', 'unknown')}")
        print(f"Rankings: {ws.get('rankings', [])[:5]}{'...' if len(ws.get('rankings', [])) > 5 else ''}")
        completed = ws.get("completed_events", [])
        upcoming = ws.get("upcoming_events", [])
        print(f"Events: {len(completed)} completed, {len(upcoming)} upcoming")
        injuries = ws.get("active_injuries", {})
        if injuries:
            print(f"Injuries: {len(injuries)} fighters recovering")


if __name__ == "__main__":
    main()
