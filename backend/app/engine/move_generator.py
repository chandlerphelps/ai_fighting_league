import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.config import Config
from app.services.grok_image import (
    download_image,
    edit_image,
)
from app.services.openrouter import call_openrouter_json

from app.prompts.move_prompts import (
    SYSTEM_PROMPT_MOVE_DESIGNER,
    build_move_generation_prompt,
)
from app.prompts.image_builders import (
    build_move_image_prompt,
    _nsfw_prefix,
    _nsfw_tail,
)


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

    prompt = build_move_generation_prompt(
        ring_name=ring_name,
        build=build,
        personality=personality,
        distinguishing=distinguishing,
        iconic=iconic,
        gender=gender,
        stat_lines=stat_lines,
    )

    result = call_openrouter_json(
        prompt,
        config,
        model="anthropic/claude-sonnet-4.6",
        system_prompt=SYSTEM_PROMPT_MOVE_DESIGNER,
        temperature=0.6,
        max_tokens=2048,
    )

    if isinstance(result, dict) and "moves" in result:
        result = result["moves"]
    if not isinstance(result, list):
        raise RuntimeError(f"Expected a JSON array of moves, got: {type(result)}")

    return result[:3]


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
