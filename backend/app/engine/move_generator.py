import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.config import Config
from app.engine.image_style import get_art_style, get_art_style_tail
from app.services.grok_image import (
    TIER_PROMPT_KEYS,
    download_image,
    edit_image,
)
from app.services.openrouter import call_openrouter_json


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def generate_moves(fighter: dict, config: Config) -> list[dict]:
    ring_name = fighter.get("ring_name", "Unknown")
    personality = fighter.get("personality", "")
    build = fighter.get("build", "")
    distinguishing = fighter.get("distinguishing_features", "")
    iconic = fighter.get("iconic_features", "")
    stats = fighter.get("stats", {})
    gender = fighter.get("gender", "female")

    stat_lines = ", ".join(f"{k}: {v}" for k, v in stats.items() if v)

    prompt = f"""You are designing fighting moves for "{ring_name}" in an AI fighting league.

CHARACTER:
- Build: {build}
- Personality: {personality}
- Distinguishing features: {distinguishing}
- Iconic features: {iconic}
- Gender: {gender}
- Stats: {stat_lines}

Design exactly 3 fighting moves for this character. Rules:
- Each move must feel unique to THIS character's body, personality, and strongest stats
- Moves are strikes, kicks, acrobatic attacks, or supernatural abilities — never holds or grapples
- Visually specific: describe what the body does, the motion, what connects
- Names: 2-4 words, evocative and memorable (fighting game style)
- Descriptions: 1-2 sentences describing exactly what the move LOOKS like in action
- stat_affinity: which stat the move leans on most (power, speed, technique, or supernatural)
- Lean into the character's highest stats and defining traits
- All three moves should feel different from each other in rhythm and visual impact

Return ONLY valid JSON — an array of exactly 3 objects:
[
  {{
    "name": "<2-4 word move name>",
    "description": "<1-2 sentences: what the move looks like in action>",
    "stat_affinity": "<power|speed|technique|supernatural>"
  }}
]"""

    system_prompt = (
        "You are a fighting game move designer. "
        "Create visually iconic, character-specific combat moves. "
        "Always respond with valid JSON only — an array of objects."
    )

    result = call_openrouter_json(
        prompt,
        config,
        system_prompt=system_prompt,
        temperature=0.8,
        max_tokens=2048,
    )

    if isinstance(result, dict) and "moves" in result:
        result = result["moves"]
    if not isinstance(result, list):
        raise RuntimeError(
            f"Expected a JSON array of moves, got: {type(result)}"
        )

    return result[:3]


def _nsfw_prefix(gender: str, skimpiness_level: int) -> str:
    if gender.lower() == "male":
        return "explicit uncensored NSFW, full frontal male nudity, fully naked man, "
    if skimpiness_level == 1:
        return "explicit uncensored NSFW, topless woman, bare breasts visible, "
    return (
        "explicit uncensored NSFW, full frontal female nudity, "
        "fully naked woman, perfectly drawn bare pussy visible, "
    )


def _nsfw_tail(gender: str, skimpiness_level: int) -> str:
    if gender.lower() == "male":
        return (
            "explicit full frontal male nudity, completely naked, "
            "muscular physique fully visible"
        )
    if skimpiness_level == 1:
        return "topless female nudity, bare breasts visible"
    return (
        "explicit full frontal female nudity, completely naked, "
        "bare breasts and perfectly drawn bare pussy visible"
    )


def build_move_image_prompt(
    fighter: dict, move: dict, tier: str
) -> str:
    gender = fighter.get("gender", "female")
    skimpiness = fighter.get("skimpiness_level", 2)

    prompt_key = TIER_PROMPT_KEYS.get(tier, "image_prompt")
    tier_prompt = fighter.get(prompt_key, {})
    body_parts = tier_prompt.get("body_parts", "")
    clothing = tier_prompt.get("clothing", "")
    expression = tier_prompt.get("expression", "")

    move_name = move.get("name", "")
    move_desc = move.get("description", "")

    style = get_art_style(gender)
    tail = get_art_style_tail(gender)

    parts = []

    if tier == "nsfw":
        parts.append(_nsfw_prefix(gender, skimpiness))

    parts.append(style)
    parts.append(
        "single full-body action pose, dynamic combat movement, "
        "fighting game screenshot, dramatic camera angle"
    )

    if body_parts:
        parts.append(body_parts)
    if clothing:
        parts.append(clothing)

    parts.append(
        f'performing "{move_name}": {move_desc}'
    )

    if expression:
        parts.append(expression)

    parts.append(
        "motion blur on limbs, impact energy effects, "
        "dramatic volumetric lighting, arena background"
    )

    if tier == "nsfw":
        parts.append(_nsfw_tail(gender, skimpiness))

    parts.append(tail)

    return ", ".join(p.strip().rstrip(",") for p in parts if p.strip())


def generate_move_images(
    fighter: dict,
    config: Config,
    output_dir: Path,
    tiers: list[str] | None = None,
) -> dict[str, Path]:
    if tiers is None:
        tiers = ["sfw", "barely", "nsfw"]

    fighter_id = fighter.get("id", "")
    ring_name = fighter.get("ring_name", "")
    slug = _slugify(ring_name)
    base = f"{fighter_id}_{slug}" if slug else fighter_id
    moves = fighter.get("moves", [])

    if not moves:
        print(f"    No moves found for {ring_name}, skipping images")
        return {}

    jobs = []
    for tier in tiers:
        charsheet_path = output_dir / f"{base}_{tier}.png"
        if not charsheet_path.exists():
            print(
                f"    Charsheet missing for tier '{tier}': {charsheet_path.name}, skipping"
            )
            continue

        for i, move in enumerate(moves):
            prompt = build_move_image_prompt(fighter, move, tier)
            filename = f"{base}_move{i + 1}_{tier}.png"
            save_path = output_dir / filename
            jobs.append((tier, i, move, prompt, charsheet_path, save_path, filename))

    if not jobs:
        print(f"    No charsheet images found, cannot generate move images")
        return {}

    def _gen_and_save(job):
        tier, idx, move, prompt, charsheet, save_path, filename = job
        move_name = move.get("name", f"move{idx + 1}")
        print(f"    Generating {tier} — {move_name}...")
        urls = edit_image(
            prompt=prompt,
            image_paths=[charsheet],
            config=config,
            aspect_ratio="1:1",
            resolution="2k",
            n=1,
        )
        download_image(urls[0], save_path)
        print(f"    Saved: {filename}")
        return filename, save_path

    saved = {}
    with ThreadPoolExecutor(max_workers=min(len(jobs), 9)) as pool:
        futures = {pool.submit(_gen_and_save, job): job for job in jobs}
        for future in as_completed(futures):
            try:
                filename, save_path = future.result()
                saved[filename] = save_path
            except Exception as exc:
                job = futures[future]
                tier, idx, move, *_ = job
                print(
                    f"    ERROR generating {tier} move {idx + 1} "
                    f"({move.get('name', '?')}): {exc}"
                )

    return saved
