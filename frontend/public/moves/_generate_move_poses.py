import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.config import load_config
from app.services.grok_image import edit_image, download_image

config = load_config()

STYLE_IMAGE = Path(__file__).parent / "pose_style.png"
OUTPUT_DIR = Path(__file__).parent / "frontend" / "public" / "moves"

MOVES = {
    "jab": "Jab — Quick straight punch from the lead hand",
    "cross": "Cross — Straight power punch from the rear hand",
    "hook": "Hook — Looping punch aimed at the side of the head",
    "uppercut": "Uppercut — Rising punch driven upward into the chin",
    "overhand": "Overhand Right — Arcing punch thrown over the top",
    "backfist": "Spinning Backfist — Full rotation into a backhand strike",
    "body_shot": "Body Shot — Punch driven into the ribs/midsection",
    "front_kick": "Front Kick — Straight kick thrust forward with the lead leg",
    "leg_kick": "Leg Kick — Low kick chopping into the opponent's thigh",
    "roundhouse": "Roundhouse Kick — Sweeping kick rotating through the hips into the head/body",
    "spinning_back_kick": "Spinning Back Kick — Full turn launching the heel backward into the opponent",
    "knee": "Knee Strike — Driving the knee upward into the body or head",
    "clinch_entry": "Clinch Entry — Closing distance and locking arms around the opponent",
    "clinch_elbow": "Elbow — Short, sharp elbow strike in close range",
    "clinch_knee": "Clinch Knee — Pulling the opponent's head down into a rising knee",
    "throw": "Hip Throw — Turning the hips to toss the opponent to the ground",
    "clinch_break": "Break Clinch — Shoving off and creating distance to separate",
    "ground_and_pound": "Ground & Pound — Mounted striking, raining punches down",
    "armbar_attempt": "Armbar — Isolating the arm and hyperextending the elbow",
    "choke_attempt": "Rear Naked Choke — Wrapping the arm around the neck from behind",
    "sweep": "Sweep — Reversing position from the bottom to stand back up",
    "ground_elbow": "Ground Elbow — Short elbow strikes from top position",
    "block": "Block — Arms raised to absorb incoming strikes",
    "slip": "Slip — Head movement to dodge a punch",
    "recover": "Recover — Stepping back, catching breath, resetting stance",
    "spirit_blast": "Spirit Blast — Channeling supernatural energy into a ranged burst",
    "hex_drain": "Hex Drain — Dark energy siphoning stamina from the opponent",
    "phantom_rush": "Phantom Rush — Supernatural speed blitz, appearing to teleport forward",
    "dark_shield": "Dark Shield — Conjuring a protective barrier of energy",
}

PROMPT_TEMPLATE = (
    "Using this style (female generic outline no clothing, just pose) give me:\n\n"
    "{move_desc}\n\n"
    "Fighter facing to the right. Minimal anatomy to help distinguish direction. "
    "Just the pose, no text or descriptions"
)


def generate_move(move_id, move_desc):
    prompt = PROMPT_TEMPLATE.format(move_desc=move_desc)
    save_path = OUTPUT_DIR / f"{move_id}.png"

    if save_path.exists():
        print(f"  SKIP {move_id} (already exists)")
        return move_id, save_path, False

    print(f"  START {move_id}")
    urls = edit_image(
        prompt=prompt,
        image_paths=[STYLE_IMAGE],
        config=config,
        aspect_ratio="1:1",
        resolution="2k",
        n=1,
    )
    download_image(urls[0], save_path)
    print(f"  DONE  {move_id}")
    return move_id, save_path, True


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(MOVES)} move poses -> {OUTPUT_DIR}")
    print(f"Style reference: {STYLE_IMAGE}")
    print()

    results = {}
    errors = {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(generate_move, mid, desc): mid for mid, desc in MOVES.items()
        }
        for future in as_completed(futures):
            mid = futures[future]
            try:
                move_id, path, generated = future.result()
                results[move_id] = path
            except Exception as e:
                print(f"  FAIL  {mid}: {e}")
                errors[mid] = str(e)

    print()
    print(f"Done: {len(results)} succeeded, {len(errors)} failed")
    if errors:
        print("Failed moves:")
        for mid, err in errors.items():
            print(f"  {mid}: {err}")


if __name__ == "__main__":
    main()
