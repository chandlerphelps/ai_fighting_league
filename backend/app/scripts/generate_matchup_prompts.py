import argparse
import random
import itertools
from pathlib import Path

from app.config import load_config
from app.engine.image_style import ART_STYLE_BASE, get_art_style_tail
from app.services import data_manager
from app.services.grok_image import edit_image, download_image


MATCHUP_COMPOSITION = (
    "strict profile view, two fighters in silhouette-style side view facing each other, "
    "hostile pre-fight staredown, inches apart, locked eyes, "
    "clenched jaws, cold fury, menacing glares, deadly serious expressions, "
    "fight-night tension, dramatic backlit arena lighting, dark moody atmosphere, "
    "full body head to toe visible, both standing on the same ground plane, "
    "height difference clearly visible between them"
)

MATCHUP_TAIL_BASE = (
    "exactly two distinct characters, no merging, no blending, "
    "each character maintains their exact original design from their reference sheet"
)


def build_matchup_prompt(fighter_a: dict, fighter_b: dict, tier: str = "barely") -> dict:
    name_a = fighter_a["ring_name"]
    name_b = fighter_b["ring_name"]
    gender_a = fighter_a.get("gender", "female")
    gender_b = fighter_b.get("gender", "female")
    height_a = fighter_a.get("height", "")
    height_b = fighter_b.get("height", "")
    weight_a = fighter_a.get("weight", "")
    weight_b = fighter_b.get("weight", "")

    tier_key = {
        "sfw": "image_prompt_sfw",
        "barely": "image_prompt",
        "nsfw": "image_prompt_nsfw",
    }[tier]

    prompt_a = fighter_a.get(tier_key, {})
    prompt_b = fighter_b.get(tier_key, {})

    body_a = prompt_a.get("body_parts", "")
    clothing_a = prompt_a.get("clothing", "")

    body_b = prompt_b.get("body_parts", "")
    clothing_b = prompt_b.get("clothing", "")

    char_a_desc = ", ".join(p for p in [body_a, clothing_a] if p)
    char_b_desc = ", ".join(p for p in [body_b, clothing_b] if p)

    gender_tag_a = "female" if gender_a.lower() != "male" else "male"
    gender_tag_b = "female" if gender_b.lower() != "male" else "male"

    left_fighter = f"left fighter ({gender_tag_a}, {name_a}, {height_a}, {weight_a} lbs): {char_a_desc}"
    right_fighter = f"right fighter ({gender_tag_b}, {name_b}, {height_b}, {weight_b} lbs): {char_b_desc}"

    size_note = (
        f"{name_a} is {height_a} and {name_b} is {height_b}, "
        f"show accurate relative height difference between them"
    )

    tail_a = get_art_style_tail(gender_a)
    tail_b = get_art_style_tail(gender_b)
    combined_tail = tail_a if tail_a == tail_b else f"{tail_a}, {tail_b}"
    matchup_tail = combined_tail + ", " + MATCHUP_TAIL_BASE

    full = ", ".join([
        ART_STYLE_BASE,
        MATCHUP_COMPOSITION,
        "first image is the character sheet for the left fighter, second image is the character sheet for the right fighter",
        left_fighter,
        right_fighter,
        size_note,
        matchup_tail,
    ])

    return {
        "fighter_a_id": fighter_a["id"],
        "fighter_b_id": fighter_b["id"],
        "fighter_a": name_a,
        "fighter_b": name_b,
        "tier": tier,
        "left_fighter": left_fighter,
        "right_fighter": right_fighter,
        "full_prompt": full,
    }


def find_fighter_image(fighter_id: str, data_dir: Path, tier: str = "barely") -> Path | None:
    fighters_dir = data_dir / "fighters"
    tier_matches = list(fighters_dir.glob(f"{fighter_id}*_{tier}.png"))
    if tier_matches:
        return tier_matches[0]
    tier_matches = list(fighters_dir.glob(f"{fighter_id}*_{tier}.jpg"))
    if tier_matches:
        return tier_matches[0]
    all_matches = list(fighters_dir.glob(f"{fighter_id}*.png"))
    if not all_matches:
        all_matches = list(fighters_dir.glob(f"{fighter_id}*.jpg"))
    return all_matches[0] if all_matches else None


def generate_matchup_image(prompt_data: dict, config, output_dir: Path) -> Path | None:
    data_dir = config.data_dir
    tier = prompt_data["tier"]
    img_a = find_fighter_image(prompt_data["fighter_a_id"], data_dir, tier=tier)
    img_b = find_fighter_image(prompt_data["fighter_b_id"], data_dir, tier=tier)

    if not img_a or not img_b:
        missing = []
        if not img_a:
            missing.append(f"{prompt_data['fighter_a']} ({prompt_data['fighter_a_id']})")
        if not img_b:
            missing.append(f"{prompt_data['fighter_b']} ({prompt_data['fighter_b_id']})")
        print(f"  Missing {tier} character sheet images: {', '.join(missing)}")
        return None

    print(f"  Ref images: {img_a.name}, {img_b.name}")
    print(f"  Calling Grok image edit API ({tier})...")

    urls = edit_image(
        prompt=prompt_data["full_prompt"],
        image_paths=[img_a, img_b],
        config=config,
        aspect_ratio="2:3",
        resolution="2k",
        n=1,
    )

    slug_a = prompt_data["fighter_a"].lower().replace(" ", "_")
    slug_b = prompt_data["fighter_b"].lower().replace(" ", "_")
    filename = f"matchup_{slug_a}_vs_{slug_b}_{tier}.png"
    save_path = output_dir / filename

    download_image(urls[0], save_path)
    return save_path


TIERS = ["barely", "sfw", "nsfw"]


def main():
    parser = argparse.ArgumentParser(description="Generate matchup face-off images")
    parser.add_argument("--count", type=int, default=3, help="Number of matchups to generate")
    parser.add_argument("--tiers", nargs="*", default=TIERS, choices=TIERS, help="Tiers to generate (default: all three)")
    parser.add_argument("--prompt-only", action="store_true", help="Only generate prompts, skip image generation")
    args = parser.parse_args()

    config = load_config()
    fighters = data_manager.load_all_fighters(config)
    if len(fighters) < 2:
        print("Need at least 2 fighters in the roster.")
        return

    pairs = list(itertools.combinations(fighters, 2))
    random.shuffle(pairs)
    selected = pairs[:args.count]

    output_dir = config.data_dir / "matchups"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = Path(__file__).resolve().parent.parent.parent.parent / "_TMP_OUTPUT.md"
    lines = ["# Matchup Image Prompts\n"]

    for i, (a, b) in enumerate(selected, 1):
        print(f"\n{'='*60}")
        ring_a = a.get("ring_name", a.get("id", "?"))
        ring_b = b.get("ring_name", b.get("id", "?"))
        print(f"Matchup {i}: {ring_a} vs {ring_b}")
        print(f"{'='*60}")

        lines.append(f"## Matchup {i}: {ring_a} vs {ring_b}\n")

        for tier in args.tiers:
            prompt_data = build_matchup_prompt(a, b, tier=tier)
            print(f"\n  --- {tier.upper()} ---")

            lines.append(f"### {tier.upper()}\n")
            lines.append(f"```\n{prompt_data['full_prompt']}\n```\n")

            if args.prompt_only:
                print(f"  Prompt generated (--prompt-only mode)")
            else:
                try:
                    saved = generate_matchup_image(prompt_data, config, output_dir)
                    if saved:
                        print(f"  Saved: {saved}")
                        lines.append(f"**Image:** `{saved.name}`\n")
                except Exception as e:
                    print(f"  ERROR: {e}")
                    lines.append(f"**Error:** {e}\n")

            lines.append("")

    output_path.write_text("\n".join(lines))
    print(f"\nPrompts written to {output_path}")
    if not args.prompt_only:
        print(f"Images saved to {output_dir}")


if __name__ == "__main__":
    main()
