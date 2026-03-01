import argparse
import json
import time
from pathlib import Path

from app.config import load_config
from app.engine.move_generator import generate_move_images, generate_moves


def _load_fighters(fighters_dir: Path) -> list[dict]:
    if not fighters_dir.exists():
        return []
    fighters = []
    for path in sorted(fighters_dir.glob("*.json")):
        with open(path) as f:
            fighters.append(json.load(f))
    return fighters


def _save_fighter(fighter: dict, fighters_dir: Path):
    fighter_id = fighter.get("id", "unknown")
    ring_name = fighter.get("ring_name", "")
    slug = ring_name.lower().replace(" ", "_").replace("-", "_")
    slug = "".join(c for c in slug if c.isalnum() or c == "_").strip("_")
    filename = f"{fighter_id}_{slug}.json" if slug else f"{fighter_id}.json"
    path = fighters_dir / filename
    with open(path, "w") as f:
        json.dump(fighter, f, indent=2, default=str)


def run(
    fighters_dir: Path,
    do_images: bool = False,
    images_only: bool = False,
    tiers: list[str] | None = None,
    fighter_id: str | None = None,
):
    config = load_config()

    fighters = _load_fighters(fighters_dir)
    if not fighters:
        print(f"No fighters found in {fighters_dir}")
        return

    if fighter_id:
        fighters = [f for f in fighters if f.get("id") == fighter_id]
        if not fighters:
            print(f"Fighter {fighter_id} not found in {fighters_dir}")
            return

    print(f"Processing {len(fighters)} fighter(s) from {fighters_dir}")
    if images_only:
        print("  Mode: images only (using existing moves)")
    elif do_images:
        print("  Mode: generate moves + images")
    else:
        print("  Mode: generate moves only")
    print()

    for i, fighter in enumerate(fighters):
        name = fighter.get("ring_name", "?")
        fid = fighter.get("id", "?")
        print(f"[{i + 1}/{len(fighters)}] {name} ({fid})")

        try:
            if not images_only:
                print("  Generating moves...")
                moves = generate_moves(fighter, config)
                fighter["moves"] = moves
                _save_fighter(fighter, fighters_dir)
                for m in moves:
                    print(
                        f"    {m['name']} [{m['stat_affinity']}] — {m['description']}"
                    )

            if do_images or images_only:
                current_moves = fighter.get("moves", [])
                if not current_moves:
                    print("  No moves to generate images for, skipping")
                    continue

                print(f"  Generating move images ({len(current_moves)} moves)...")
                saved = generate_move_images(
                    fighter, config, fighters_dir, tiers=tiers
                )
                print(f"  Generated {len(saved)} image(s)")

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        if i < len(fighters) - 1:
            time.sleep(1)

    print("\nDone!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate fighter move sets")
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Fighters directory (default: data/fighters)",
    )
    parser.add_argument(
        "--fighter",
        type=str,
        default=None,
        help="Generate for a single fighter ID only",
    )
    parser.add_argument(
        "--images",
        action="store_true",
        help="Also generate move images via Grok edit API",
    )
    parser.add_argument(
        "--images-only",
        action="store_true",
        help="Skip move generation, only generate images from existing moves",
    )
    parser.add_argument(
        "--tiers",
        nargs="+",
        choices=["sfw", "barely", "nsfw"],
        help="Which tiers to generate images for (default: all three)",
    )
    args = parser.parse_args()

    if args.dir:
        fighters_dir = Path(args.dir)
        if not fighters_dir.is_absolute():
            fighters_dir = Path(__file__).resolve().parent.parent.parent.parent / args.dir
    else:
        fighters_dir = (
            Path(__file__).resolve().parent.parent.parent.parent / "data" / "fighters"
        )

    run(
        fighters_dir=fighters_dir,
        do_images=args.images or args.images_only,
        images_only=args.images_only,
        tiers=args.tiers,
        fighter_id=args.fighter,
    )
