import base64
import random
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

from app.config import Config

MAX_RETRIES = 5


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


TIER_PROMPT_KEYS = {
    "sfw": "image_prompt_sfw",
    "barely": "image_prompt",
    "nsfw": "image_prompt_nsfw",
    "portrait": "image_prompt_portrait",
    "headshot": "image_prompt_headshot",
}


_PAD_TMP = Path(__file__).resolve().parents[3] / "data" / "_tmp_padded.png"


def _pad_to_aspect(image_path: Path, aspect_ratio: str) -> Path:
    aw, ah = (int(x) for x in aspect_ratio.split(":"))
    img = Image.open(image_path)
    w, h = img.size
    target_ratio = aw / ah
    current_ratio = w / h
    if abs(current_ratio - target_ratio) < 0.01:
        return image_path
    if current_ratio < target_ratio:
        new_w = int(h * target_ratio)
        new_h = h
    else:
        new_w = w
        new_h = int(w / target_ratio)
    padded = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    offset_x = (new_w - w) // 2
    offset_y = (new_h - h) // 2
    padded.paste(img, (offset_x, offset_y))
    _PAD_TMP.parent.mkdir(parents=True, exist_ok=True)
    padded.save(_PAD_TMP, format="PNG")
    return _PAD_TMP


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
    pad_to_aspect: bool = False,
) -> list[str]:
    if pad_to_aspect:
        encoded = [
            {"url": _encode_image(_pad_to_aspect(p, aspect_ratio)), "type": "image_url"}
            for p in image_paths
        ]
    else:
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
    gender = (
        fighter.gender if hasattr(fighter, "gender") else fighter.get("gender", "female")
    )
    is_male = gender.lower() == "male"
    if tiers is None:
        if is_male:
            tiers = ["sfw", "barely"]
        else:
            tiers = ["sfw", "barely", "nsfw"]

    fighter_id = fighter.id if hasattr(fighter, "id") else fighter["id"]
    ring_name = (
        fighter.ring_name
        if hasattr(fighter, "ring_name")
        else fighter.get("ring_name", "")
    )
    slug = _slugify(ring_name)
    base = f"{fighter_id}_{slug}" if slug else fighter_id

    def _get_prompt(key):
        prompt_data = (
            getattr(fighter, key, None)
            if hasattr(fighter, key)
            else fighter.get(key, {})
        )
        if isinstance(prompt_data, dict):
            return prompt_data.get("full_prompt", "")
        return ""

    regen_body_ref = "body_ref" in tiers
    actual_tiers = [t for t in tiers if t != "body_ref"]

    body_ref_prompt = _get_prompt("image_prompt_body_ref")

    tier_prompts = {}
    for tier in actual_tiers:
        key = TIER_PROMPT_KEYS.get(tier)
        if not key:
            print(f"    Unknown tier '{tier}', skipping")
            continue
        prompt = _get_prompt(key)
        if not prompt:
            print(f"    No prompt for tier '{tier}', skipping")
            continue
        tier_prompts[tier] = prompt

    saved = {}
    body_ref_path = None
    body_ref_filename = f"{base}_body_ref.png"
    body_ref_save_path = output_dir / body_ref_filename

    def _gen_body_ref():
        female_ref = config.data_dir / "reference_images" / "female" / "pussy_asshole_behind2.png"
        if not is_male and female_ref.exists():
            return edit_image(
                prompt=body_ref_prompt,
                image_paths=[female_ref],
                config=config,
                aspect_ratio="1:1",
                resolution="2k",
                n=1,
                pad_to_aspect=True,
            )
        return generate_image(
            prompt=body_ref_prompt,
            config=config,
            aspect_ratio="1:1",
            resolution="2k",
            n=1,
        )

    if regen_body_ref and body_ref_prompt:
        print(f"    Generating body reference image...")
        urls = _gen_body_ref()
        download_image(urls[0], body_ref_save_path)
        print(f"    Saved: {body_ref_filename}")
        saved["body_ref"] = body_ref_save_path
        body_ref_path = body_ref_save_path
    elif body_ref_save_path.exists():
        body_ref_path = body_ref_save_path
    elif body_ref_prompt and actual_tiers:
        print(f"    Generating body reference image...")
        urls = _gen_body_ref()
        download_image(urls[0], body_ref_save_path)
        print(f"    Saved: {body_ref_filename}")
        saved["body_ref"] = body_ref_save_path
        body_ref_path = body_ref_save_path

    if tier_prompts:
        def _gen_and_save(tier, prompt):
            filename = f"{base}_{tier}.png"
            save_path = output_dir / filename
            print(f"    Generating {tier} charsheet...")
            use_body_ref = body_ref_path and not is_male
            if use_body_ref:
                urls = edit_image(
                    prompt=prompt,
                    image_paths=[body_ref_path],
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

        with ThreadPoolExecutor(max_workers=len(tier_prompts)) as pool:
            futures = {
                pool.submit(_gen_and_save, tier, prompt): tier
                for tier, prompt in tier_prompts.items()
            }
            for future in as_completed(futures):
                label, save_path = future.result()
                saved[label] = save_path

    return saved
