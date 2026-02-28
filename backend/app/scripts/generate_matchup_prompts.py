import argparse
import random
import itertools
from pathlib import Path

from app.config import load_config
from app.engine.image_style import ART_STYLE, ART_STYLE_TAIL
from app.services import data_manager
from app.services.grok_image import edit_image, download_image


MATCHUP_COMPOSITION = (
    "two fighters standing face to face in a tense pre-fight staredown, "
    "full body head to toe visible, both standing on the same ground plane, "
    "height difference clearly visible between them, "
    "close proximity confrontational stance, "
    "neutral arena background"
)

MATCHUP_TAIL = (
    ART_STYLE_TAIL + ", "
    "exactly two distinct characters, no merging, no blending, "
    "each character maintains their exact original design from their reference sheet"
)


def build_matchup_prompt(fighter_a: dict, fighter_b: dict, tier: str = "barely") -> dict:
    name_a = fighter_a["ring_name"]
    name_b = fighter_b["ring_name"]
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
    expression_a = prompt_a.get("expression", "")

    body_b = prompt_b.get("body_parts", "")
    clothing_b = prompt_b.get("clothing", "")
    expression_b = prompt_b.get("expression", "")

    char_a_desc = ", ".join(p for p in [body_a, clothing_a, expression_a] if p)
    char_b_desc = ", ".join(p for p in [body_b, clothing_b, expression_b] if p)

    left_fighter = f"left fighter ({name_a}, {height_a}, {weight_a} lbs): {char_a_desc}"
    right_fighter = f"right fighter ({name_b}, {height_b}, {weight_b} lbs): {char_b_desc}"

    size_note = (
        f"{name_a} is {height_a} and {name_b} is {height_b}, "
        f"show accurate relative height difference between them"
    )

    full = ", ".join([
        ART_STYLE,
        MATCHUP_COMPOSITION,
        "first image is the character sheet for the left fighter, second image is the character sheet for the right fighter",
        left_fighter,
        right_fighter,
        size_note,
        MATCHUP_TAIL,
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


def find_fighter_image(fighter_id: str, data_dir: Path) -> Path | None:
    fighters_dir = data_dir / "fighters"
    matches = list(fighters_dir.glob(f"{fighter_id}*.png"))
    if not matches:
        matches = list(fighters_dir.glob(f"{fighter_id}*.jpg"))
    return matches[0] if matches else None


def generate_matchup_image(prompt_data: dict, config, output_dir: Path) -> Path | None:
    data_dir = config.data_dir
    img_a = find_fighter_image(prompt_data["fighter_a_id"], data_dir)
    img_b = find_fighter_image(prompt_data["fighter_b_id"], data_dir)

    if not img_a or not img_b:
        missing = []
        if not img_a:
            missing.append(f"{prompt_data['fighter_a']} ({prompt_data['fighter_a_id']})")
        if not img_b:
            missing.append(f"{prompt_data['fighter_b']} ({prompt_data['fighter_b_id']})")
        print(f"  Missing character sheet images: {', '.join(missing)}")
        return None

    print(f"  Ref images: {img_a.name}, {img_b.name}")
    print(f"  Calling Grok image edit API...")

    urls = edit_image(
        prompt=prompt_data["full_prompt"],
        image_paths=[img_a, img_b],
        config=config,
        aspect_ratio="16:9",
        resolution="2k",
        n=1,
    )

    slug_a = prompt_data["fighter_a"].lower().replace(" ", "_")
    slug_b = prompt_data["fighter_b"].lower().replace(" ", "_")
    filename = f"matchup_{slug_a}_vs_{slug_b}.png"
    save_path = output_dir / filename

    download_image(urls[0], save_path)
    return save_path


def main():
    parser = argparse.ArgumentParser(description="Generate matchup face-off images")
    parser.add_argument("--count", type=int, default=3, help="Number of matchups to generate")
    parser.add_argument("--tier", default="barely", choices=["sfw", "barely", "nsfw"])
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
        prompt_data = build_matchup_prompt(a, b, tier=args.tier)
        print(f"\n{'='*60}")
        print(f"Matchup {i}: {prompt_data['fighter_a']} vs {prompt_data['fighter_b']}")
        print(f"{'='*60}")

        lines.append(f"## Matchup {i}: {prompt_data['fighter_a']} vs {prompt_data['fighter_b']}\n")
        lines.append(f"**Tier:** {prompt_data['tier']}\n")
        lines.append(f"### Full Prompt\n")
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
