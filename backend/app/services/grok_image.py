import base64
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.config import Config

MAX_RETRIES = 2


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
            print(f"    Image gen error (attempt {attempt + 1}/{1 + MAX_RETRIES}): {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt + 1))
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
            print(f"    Image edit error (attempt {attempt + 1}/{1 + MAX_RETRIES}): {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt + 1))
    raise last_exc


def download_image(url: str, save_path: Path) -> Path:
    resp = requests.get(url, timeout=60)
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

    triple_data = (
        getattr(fighter, "image_prompt_triple", None)
        if hasattr(fighter, "image_prompt_triple")
        else fighter.get("image_prompt_triple", {})
    )
    triple_prompt = triple_data.get("full_prompt", "") if isinstance(triple_data, dict) else ""

    jobs = []
    for tier in tiers:
        prompt = _get_prompt(tier)
        if not prompt:
            print(f"    No prompt for tier '{tier}', skipping")
            continue
        filename = f"{base}_{tier}.png"
        jobs.append((tier, prompt, "3:2", output_dir / filename, filename))

    if triple_prompt:
        filename = f"{base}_triple.png"
        jobs.append(("triple", triple_prompt, "16:9", output_dir / filename, filename))

    def _gen_and_save(job):
        label, prompt, aspect, save_path, filename = job
        print(f"    Generating {label} charsheet...")
        urls = generate_image(
            prompt=prompt, config=config, aspect_ratio=aspect, resolution="2k", n=1,
        )
        download_image(urls[0], save_path)
        print(f"    Saved: {filename}")
        return label, save_path

    saved = {}
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = {pool.submit(_gen_and_save, job): job for job in jobs}
        for future in as_completed(futures):
            label, save_path = future.result()
            saved[label] = save_path

    return saved
