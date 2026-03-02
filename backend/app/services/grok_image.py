import base64
import random
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.config import Config

MAX_RETRIES = 5


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


TIER_PROMPT_KEYS = {
    "sfw": "image_prompt_sfw",
    "barely": "image_prompt",
    "nsfw": "image_prompt_nsfw",
}


def _encode_image(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
    }
    mime_type = mime.get(suffix.lstrip("."), "image/png")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime_type};base64,{b64}"


def generate_image(
    prompt: str,
    config: Config,
    aspect_ratio: str = "16:9",
    resolution: str = "2k",
    n: int = 1,
) -> list[str]:
    last_exc = None
    for attempt in range(1 + MAX_RETRIES):
        try:
            resp = requests.post(
                f"{config.grok_base_url}/images/generations",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.grok_api_key}",
                },
                json={
                    "model": "grok-imagine-image",
                    "prompt": prompt,
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                    "n": n,
                    "response_format": "url",
                },
                timeout=120,
            )
            resp.raise_for_status()
            return [item["url"] for item in resp.json()["data"]]
        except (requests.RequestException, KeyError) as exc:
            last_exc = exc
            print(
                f"    Image gen error (attempt {attempt + 1}/{1 + MAX_RETRIES}): {exc}"
            )
            if attempt < MAX_RETRIES:
                delay = min(2 ** (attempt + 1), 30) + random.uniform(0, 2)
                time.sleep(delay)
    raise last_exc


def edit_image(
    prompt: str,
    image_paths: list[Path],
    config: Config,
    aspect_ratio: str = "16:9",
    resolution: str = "2k",
    n: int = 1,
) -> list[str]:
    encoded = [{"url": _encode_image(p), "type": "image_url"} for p in image_paths]

    body = {
        "model": "grok-imagine-image",
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "n": n,
        "response_format": "url",
    }

    if len(encoded) == 1:
        body["image"] = encoded[0]
    else:
        body["images"] = encoded

    last_exc = None
    for attempt in range(1 + MAX_RETRIES):
        try:
            resp = requests.post(
                f"{config.grok_base_url}/images/edits",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.grok_api_key}",
                },
                json=body,
                timeout=120,
            )
            resp.raise_for_status()
            return [item["url"] for item in resp.json()["data"]]
        except (requests.RequestException, KeyError) as exc:
            last_exc = exc
            print(
                f"    Image edit error (attempt {attempt + 1}/{1 + MAX_RETRIES}): {exc}"
            )
            if attempt < MAX_RETRIES:
                delay = min(2 ** (attempt + 1), 30) + random.uniform(0, 2)
                time.sleep(delay)
    raise last_exc


def download_image(url: str, save_path: Path) -> Path:
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(resp.content)
    return save_path


def generate_charsheet_images(
    fighter,
    config: Config,
    output_dir: Path,
    tiers: list[str] | None = None,
) -> dict[str, Path]:
    if tiers is None:
        tiers = ["sfw", "barely", "nsfw"]

    fighter_id = fighter.id if hasattr(fighter, "id") else fighter["id"]
    ring_name = (
        fighter.ring_name
        if hasattr(fighter, "ring_name")
        else fighter.get("ring_name", "")
    )
    slug = _slugify(ring_name)
    base = f"{fighter_id}_{slug}" if slug else fighter_id

    def _get_prompt(tier):
        key = TIER_PROMPT_KEYS[tier]
        prompt_data = (
            getattr(fighter, key, None)
            if hasattr(fighter, key)
            else fighter.get(key, {})
        )
        if isinstance(prompt_data, dict):
            return prompt_data.get("full_prompt", "")
        return ""

    tier_prompts = {}
    for tier in tiers:
        prompt = _get_prompt(tier)
        if not prompt:
            print(f"    No prompt for tier '{tier}', skipping")
            continue
        tier_prompts[tier] = prompt

    saved = {}
    barely_path = None

    if "barely" in tier_prompts:
        barely_filename = f"{base}_barely.png"
        barely_save_path = output_dir / barely_filename
        print(f"    Generating barely charsheet (reference)...")
        urls = generate_image(
            prompt=tier_prompts["barely"],
            config=config,
            aspect_ratio="1:1",
            resolution="2k",
            n=1,
        )
        download_image(urls[0], barely_save_path)
        print(f"    Saved: {barely_filename}")
        saved["barely"] = barely_save_path
        barely_path = barely_save_path

    remaining = {t: p for t, p in tier_prompts.items() if t != "barely"}

    if remaining:
        def _gen_and_save(tier, prompt):
            filename = f"{base}_{tier}.png"
            save_path = output_dir / filename
            print(f"    Generating {tier} charsheet...")
            if barely_path:
                urls = edit_image(
                    prompt=prompt,
                    image_paths=[barely_path],
                    config=config,
                    aspect_ratio="1:1",
                    resolution="2k",
                    n=1,
                )
            else:
                urls = generate_image(
                    prompt=prompt,
                    config=config,
                    aspect_ratio="1:1",
                    resolution="2k",
                    n=1,
                )
            download_image(urls[0], save_path)
            print(f"    Saved: {filename}")
            return tier, save_path

        with ThreadPoolExecutor(max_workers=len(remaining)) as pool:
            futures = {
                pool.submit(_gen_and_save, tier, prompt): tier
                for tier, prompt in remaining.items()
            }
            for future in as_completed(futures):
                label, save_path = future.result()
                saved[label] = save_path

    return saved
