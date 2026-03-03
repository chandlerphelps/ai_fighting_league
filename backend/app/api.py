import json
import threading
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from app.config import load_config
from app.engine.fighter_generator import (
    generate_fighter,
    _generate_outfits,
    _build_charsheet_prompt,
    _roll_skimpiness,
    _find_subtype,
    load_outfit_options,
    filter_outfit_options,
    load_exotic_outfit_options,
    filter_exotic_for_fighter,
    ARCHETYPES_FEMALE,
    ARCHETYPES_MALE,
)
from app.models.fighter import Fighter, Stats
from app.services import data_manager
from app.services.grok_image import generate_charsheet_images
from app.engine.move_generator import build_move_image_prompt, _slugify as move_slugify
from app.services.grok_image import edit_image, download_image

app = Flask(__name__)
CORS(app)

config = load_config()
data_manager.ensure_data_dirs(config)

tasks: dict[str, dict] = {}

PROMPT_RELEVANT_FIELDS = {
    "ring_attire", "ring_attire_sfw", "ring_attire_nsfw",
    "skimpiness_level", "gender", "image_prompt_personality_pose",
    "image_prompt", "image_prompt_sfw", "image_prompt_nsfw",
}


def _get_subtype_info(fighter: dict) -> dict | None:
    archetype = fighter.get("primary_archetype", "")
    subtype_name = fighter.get("subtype", "")
    if archetype and subtype_name:
        return _find_subtype(archetype, subtype_name)
    return None


def _rebuild_prompts(fighter: dict):
    body_parts = fighter.get("image_prompt", {}).get("body_parts", "")
    expression = fighter.get("image_prompt", {}).get("expression", "")
    personality_pose = fighter.get("image_prompt_personality_pose", "")
    gender = fighter.get("gender", "female")
    skimpiness = fighter.get("skimpiness_level", 2)
    subtype_info = _get_subtype_info(fighter)
    iconic_features = fighter.get("iconic_features", "")

    clothing_sfw = fighter.get("ring_attire_sfw", "") or fighter.get("image_prompt_sfw", {}).get("clothing", "")
    clothing_barely = fighter.get("ring_attire", "") or fighter.get("image_prompt", {}).get("clothing", "")
    clothing_nsfw = fighter.get("ring_attire_nsfw", "") or fighter.get("image_prompt_nsfw", {}).get("clothing", "")

    age = fighter.get("age", 0)
    fighter["image_prompt_sfw"] = _build_charsheet_prompt(
        body_parts, clothing_sfw, expression,
        personality_pose=personality_pose, tier="sfw",
        gender=gender, skimpiness_level=skimpiness,
        subtype_info=subtype_info,
        iconic_features=iconic_features,
        age=age,
    )
    fighter["image_prompt"] = _build_charsheet_prompt(
        body_parts, clothing_barely, expression,
        personality_pose=personality_pose, tier="barely",
        gender=gender, skimpiness_level=skimpiness,
        subtype_info=subtype_info,
        iconic_features=iconic_features,
        age=age,
    )
    fighter["image_prompt_nsfw"] = _build_charsheet_prompt(
        body_parts, clothing_nsfw, expression,
        personality_pose=personality_pose, tier="nsfw",
        gender=gender, skimpiness_level=skimpiness,
        subtype_info=subtype_info,
        iconic_features=iconic_features,
        age=age,
    )


def _run_in_background(task_id: str, fn, *args, **kwargs):
    def wrapper():
        try:
            result = fn(*args, **kwargs)
            tasks[task_id]["status"] = "completed"
            tasks[task_id]["result"] = result
        except Exception as e:
            tasks[task_id]["status"] = "failed"
            tasks[task_id]["error"] = str(e)

    tasks[task_id] = {"status": "running", "result": None, "error": None}
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()


def _fighter_image_paths(fighter_id: str, ring_name: str = "") -> dict[str, Path]:
    from app.services.grok_image import _slugify
    fighters_dir = config.data_dir / "fighters"
    slug = _slugify(ring_name) if ring_name else ""
    base = f"{fighter_id}_{slug}" if slug else fighter_id
    result = {}
    for tier in ["sfw", "barely", "nsfw"]:
        path = fighters_dir / f"{base}_{tier}.png"
        if path.exists():
            result[tier] = path
    return result


@app.get("/api/fighters")
def list_fighters():
    fighters = data_manager.load_all_fighters(config)
    for f in fighters:
        fid = f.get("id", "")
        rname = f.get("ring_name", "")
        images = _fighter_image_paths(fid, rname)
        f["_available_images"] = list(images.keys())
    return jsonify(fighters)


@app.get("/api/fighters/<fighter_id>")
def get_fighter(fighter_id: str):
    fighter = data_manager.load_fighter(fighter_id, config)
    if not fighter:
        return jsonify({"error": "Fighter not found"}), 404
    images = _fighter_image_paths(fighter_id, fighter.get("ring_name", ""))
    fighter["_available_images"] = list(images.keys())
    return jsonify(fighter)


@app.put("/api/fighters/<fighter_id>")
def update_fighter(fighter_id: str):
    existing = data_manager.load_fighter(fighter_id, config)
    if not existing:
        return jsonify({"error": "Fighter not found"}), 404

    updates = request.json
    if not updates:
        return jsonify({"error": "No data provided"}), 400

    needs_prompt_rebuild = False
    for key, value in updates.items():
        if key.startswith("_"):
            continue
        if key == "stats" and isinstance(value, dict):
            existing["stats"] = {**existing.get("stats", {}), **value}
        elif key == "record" and isinstance(value, dict):
            existing["record"] = {**existing.get("record", {}), **value}
        elif key == "condition" and isinstance(value, dict):
            existing["condition"] = {**existing.get("condition", {}), **value}
        elif key in ("image_prompt", "image_prompt_sfw", "image_prompt_nsfw") and isinstance(value, dict):
            existing[key] = {**existing.get(key, {}), **value}
            needs_prompt_rebuild = True
        else:
            existing[key] = value
            if key in PROMPT_RELEVANT_FIELDS:
                needs_prompt_rebuild = True

    if needs_prompt_rebuild:
        _rebuild_prompts(existing)

    data_manager.save_fighter(existing, config)
    return jsonify(existing)


@app.delete("/api/fighters/<fighter_id>")
def delete_fighter(fighter_id: str):
    existing = data_manager.load_fighter(fighter_id, config)
    if not existing:
        return jsonify({"error": "Fighter not found"}), 404

    fighters_dir = config.data_dir / "fighters"
    for path in fighters_dir.glob(f"{fighter_id}*"):
        path.unlink()

    ws = data_manager.load_world_state(config)
    if ws and fighter_id in ws.get("rankings", []):
        ws["rankings"].remove(fighter_id)
        data_manager.save_world_state(ws, config)

    return jsonify({"deleted": fighter_id})


@app.post("/api/fighters/generate")
def generate_new_fighter():
    body = request.json or {}
    archetype = body.get("archetype")
    has_supernatural = body.get("has_supernatural", False)
    tiers = body.get("tiers")

    roster_plan_entry = None
    if archetype or body.get("concept_hook"):
        roster_plan_entry = {
            "primary_archetype": archetype or "The Huntress",
            "has_supernatural": has_supernatural,
            "concept_hook": body.get("concept_hook", ""),
            "ring_name": body.get("ring_name", ""),
            "gender": body.get("gender", "female"),
            "age": body.get("age", 0),
            "origin": body.get("origin", ""),
            "skimpiness_weights": body.get("skimpiness_weights", [15, 35, 35, 15]),
        }
        roster_plan_entry = {k: v for k, v in roster_plan_entry.items() if v}

    existing_on_disk = data_manager.load_all_fighters(config)
    existing_fighters = [
        {
            "ring_name": f.get("ring_name"),
            "gender": f.get("gender", ""),
            "height": f.get("height", ""),
            "origin": f.get("origin"),
            "build": f.get("build", ""),
            "distinguishing_features": f.get("distinguishing_features", ""),
            "ring_attire": f.get("ring_attire", ""),
        }
        for f in existing_on_disk
    ]

    task_id = f"gen_{uuid.uuid4().hex[:8]}"

    def do_generate():
        weights = body.get("skimpiness_weights", [15, 35, 35, 15])
        skimpiness = _roll_skimpiness(weights)
        outfit_opts = _build_outfit_options_for_fighter(skimpiness_level=skimpiness, archetype=archetype or "")
        fighter = generate_fighter(
            config,
            archetype=archetype,
            has_supernatural=has_supernatural,
            existing_fighters=existing_fighters,
            roster_plan_entry=roster_plan_entry,
            tiers=tiers,
            outfit_options_by_tier=outfit_opts,
            skimpiness_level=skimpiness,
        )
        data_manager.save_fighter(fighter, config)

        ws = data_manager.load_world_state(config)
        if ws:
            if fighter.id not in ws.get("rankings", []):
                ws["rankings"].append(fighter.id)
                data_manager.save_world_state(ws, config)

        return fighter.to_dict()

    _run_in_background(task_id, do_generate)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.post("/api/fighters/<fighter_id>/regenerate-character")
def regenerate_character(fighter_id: str):
    existing = data_manager.load_fighter(fighter_id, config)
    if not existing:
        return jsonify({"error": "Fighter not found"}), 404

    body = request.json or {}
    archetype = body.get("archetype", existing.get("primary_archetype"))
    has_supernatural = body.get("has_supernatural", existing.get("stats", {}).get("supernatural", 0) > 0)

    roster_plan_entry = {
        "primary_archetype": archetype or "The Huntress",
        "has_supernatural": has_supernatural,
        "concept_hook": body.get("concept_hook", ""),
        "ring_name": body.get("ring_name", existing.get("ring_name", "")),
        "gender": existing.get("gender", "female"),
        "origin": body.get("origin", existing.get("origin", "")),
        "skimpiness_weights": body.get("skimpiness_weights", [15, 35, 35, 15]),
    }
    roster_plan_entry = {k: v for k, v in roster_plan_entry.items() if v}

    existing_on_disk = data_manager.load_all_fighters(config)
    existing_fighters = [
        {
            "ring_name": f.get("ring_name"),
            "gender": f.get("gender", ""),
            "height": f.get("height", ""),
            "origin": f.get("origin"),
            "build": f.get("build", ""),
            "distinguishing_features": f.get("distinguishing_features", ""),
            "ring_attire": f.get("ring_attire", ""),
        }
        for f in existing_on_disk
        if f.get("id") != fighter_id
    ]

    task_id = f"regen_{uuid.uuid4().hex[:8]}"

    def do_regenerate():
        weights = body.get("skimpiness_weights", [15, 35, 35, 15])
        skimpiness = _roll_skimpiness(weights)
        outfit_opts = _build_outfit_options_for_fighter(skimpiness_level=skimpiness, archetype=archetype or "")
        fighter = generate_fighter(
            config,
            archetype=archetype,
            has_supernatural=has_supernatural,
            existing_fighters=existing_fighters,
            roster_plan_entry=roster_plan_entry,
            outfit_options_by_tier=outfit_opts,
            skimpiness_level=skimpiness,
        )

        fighter_dict = fighter.to_dict()
        fighter_dict["id"] = fighter_id
        fighter_dict["record"] = existing.get("record", {"wins": 0, "losses": 0, "draws": 0, "kos": 0, "submissions": 0})
        fighter_dict["condition"] = existing.get("condition", {})
        fighter_dict["storyline_log"] = existing.get("storyline_log", [])
        fighter_dict["rivalries"] = existing.get("rivalries", [])
        fighter_dict["last_fight_date"] = existing.get("last_fight_date")
        fighter_dict["ranking"] = existing.get("ranking")

        data_manager.save_fighter(fighter_dict, config)
        return fighter_dict

    _run_in_background(task_id, do_regenerate)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.post("/api/fighters/<fighter_id>/regenerate-outfits")
def regenerate_outfits(fighter_id: str):
    existing = data_manager.load_fighter(fighter_id, config)
    if not existing:
        return jsonify({"error": "Fighter not found"}), 404

    body = request.json or {}
    tiers = body.get("tiers")
    skimpiness_level = body.get("skimpiness_level", existing.get("skimpiness_level", 2))

    task_id = f"outfit_{uuid.uuid4().hex[:8]}"

    def do_regenerate():
        character_summary = {
            "ring_name": existing.get("ring_name", ""),
            "real_name": existing.get("real_name", ""),
            "gender": existing.get("gender", "female"),
            "build": existing.get("build", ""),
            "distinguishing_features": existing.get("distinguishing_features", ""),
            "iconic_features": existing.get("iconic_features", ""),
            "personality": existing.get("personality", ""),
            "primary_archetype": existing.get("primary_archetype", ""),
            "subtype": existing.get("subtype", ""),
            "image_prompt_body_parts": existing.get("image_prompt", {}).get("body_parts", ""),
            "image_prompt_expression": existing.get("image_prompt", {}).get("expression", ""),
            "body_type_details": existing.get("body_type_details", {}),
        }

        tech_level = existing.get("tech_level", "")
        outfit_opts = _build_outfit_options_for_fighter(
            skimpiness_level=skimpiness_level,
            archetype=existing.get("primary_archetype", ""),
            subtype=existing.get("subtype", ""),
        )
        outfit_data = _generate_outfits(config, character_summary, skimpiness_level, tiers=tiers, outfit_options_by_tier=outfit_opts, tech_level=tech_level)

        new_suggestions = outfit_data.pop("_outfit_suggestions", {})
        if new_suggestions:
            current_suggestions = existing.get("outfit_suggestions", {})
            current_suggestions.update(new_suggestions)
            existing["outfit_suggestions"] = current_suggestions

        body_parts = existing.get("image_prompt", {}).get("body_parts", "")
        expression = existing.get("image_prompt", {}).get("expression", "")
        personality_pose = existing.get("image_prompt_personality_pose", "")
        gender = existing.get("gender", "female")
        subtype_info = _get_subtype_info(existing)
        iconic_features = existing.get("iconic_features", "")

        clothing_sfw = outfit_data.get("image_prompt_clothing_sfw", "")
        clothing = outfit_data.get("image_prompt_clothing", "")
        clothing_nsfw = outfit_data.get("image_prompt_clothing_nsfw", "")

        pose_sfw = outfit_data.get("image_prompt_pose_sfw", "") or personality_pose
        pose_barely = outfit_data.get("image_prompt_pose", "") or personality_pose
        pose_nsfw = outfit_data.get("image_prompt_pose_nsfw", "") or personality_pose

        age = existing.get("age", 0)
        if not tiers or "sfw" in tiers:
            existing["ring_attire_sfw"] = outfit_data.get("ring_attire_sfw", existing.get("ring_attire_sfw", ""))
            existing["image_prompt_sfw"] = _build_charsheet_prompt(
                body_parts, clothing_sfw, expression,
                personality_pose=pose_sfw, tier="sfw",
                gender=gender, skimpiness_level=skimpiness_level,
                subtype_info=subtype_info,
                iconic_features=iconic_features,
                age=age,
            )
        if not tiers or "barely" in tiers:
            existing["ring_attire"] = outfit_data.get("ring_attire", existing.get("ring_attire", ""))
            existing["image_prompt"] = _build_charsheet_prompt(
                body_parts, clothing, expression,
                personality_pose=pose_barely, tier="barely",
                gender=gender, skimpiness_level=skimpiness_level,
                subtype_info=subtype_info,
                iconic_features=iconic_features,
                age=age,
            )
        if not tiers or "nsfw" in tiers:
            existing["ring_attire_nsfw"] = outfit_data.get("ring_attire_nsfw", existing.get("ring_attire_nsfw", ""))
            existing["image_prompt_nsfw"] = _build_charsheet_prompt(
                body_parts, clothing_nsfw, expression,
                personality_pose=pose_nsfw, tier="nsfw",
                gender=gender, skimpiness_level=skimpiness_level,
                subtype_info=subtype_info,
                iconic_features=iconic_features,
                age=age,
            )

        existing["skimpiness_level"] = skimpiness_level
        data_manager.save_fighter(existing, config)
        return existing

    _run_in_background(task_id, do_regenerate)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.post("/api/fighters/<fighter_id>/regenerate-images")
def regenerate_images(fighter_id: str):
    existing = data_manager.load_fighter(fighter_id, config)
    if not existing:
        return jsonify({"error": "Fighter not found"}), 404

    body = request.json or {}
    tiers = body.get("tiers", ["sfw", "barely", "nsfw"])

    task_id = f"img_{uuid.uuid4().hex[:8]}"

    def do_regenerate():
        fighter = Fighter.from_dict(existing)
        fighters_dir = config.data_dir / "fighters"
        saved = generate_charsheet_images(fighter, config, fighters_dir, tiers=tiers)
        return {tier: str(path) for tier, path in saved.items()}

    _run_in_background(task_id, do_regenerate)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.post("/api/fighters/<fighter_id>/regenerate-move-image")
def regenerate_move_image(fighter_id: str):
    existing = data_manager.load_fighter(fighter_id, config)
    if not existing:
        return jsonify({"error": "Fighter not found"}), 404

    body = request.json or {}
    move_index = body.get("move_index")
    tier = body.get("tier", "sfw")

    if move_index is None:
        return jsonify({"error": "move_index is required"}), 400

    moves = existing.get("moves", [])
    if move_index < 0 or move_index >= len(moves):
        return jsonify({"error": f"Invalid move_index: {move_index}"}), 400

    if tier not in ("sfw", "barely", "nsfw"):
        return jsonify({"error": f"Invalid tier: {tier}"}), 400

    task_id = f"moveimg_{uuid.uuid4().hex[:8]}"

    def do_regenerate():
        ring_name = existing.get("ring_name", "")
        slug = move_slugify(ring_name)
        base = f"{fighter_id}_{slug}" if slug else fighter_id
        fighters_dir = config.data_dir / "fighters"

        charsheet_path = fighters_dir / f"{base}_{tier}.png"
        if not charsheet_path.exists():
            raise RuntimeError(f"No charsheet for tier '{tier}': {charsheet_path.name}")

        move = moves[move_index]
        prompt = build_move_image_prompt(existing, move, tier)
        filename = f"{base}_move{move_index + 1}_{tier}.png"
        save_path = fighters_dir / filename

        urls = edit_image(
            prompt=prompt,
            image_paths=[charsheet_path],
            config=config,
            aspect_ratio="1:1",
            resolution="2k",
            n=1,
        )
        download_image(urls[0], save_path)
        return {"filename": filename, "path": str(save_path)}

    _run_in_background(task_id, do_regenerate)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.get("/api/tasks/<task_id>")
def get_task(task_id: str):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    response = {"task_id": task_id, "status": task["status"]}
    if task["status"] == "completed":
        response["result"] = task["result"]
    elif task["status"] == "failed":
        response["error"] = task["error"]
    return jsonify(response)


@app.get("/api/archetypes")
def get_archetypes():
    return jsonify({
        "female": ARCHETYPES_FEMALE,
        "male": ARCHETYPES_MALE,
    })


@app.get("/api/fighter-images/<fighter_id>/<tier>")
def get_fighter_image(fighter_id: str, tier: str):
    if tier not in ("sfw", "barely", "nsfw"):
        return jsonify({"error": "Invalid tier"}), 400

    fighter = data_manager.load_fighter(fighter_id, config)
    if not fighter:
        return jsonify({"error": "Fighter not found"}), 404

    images = _fighter_image_paths(fighter_id, fighter.get("ring_name", ""))
    if tier not in images:
        return jsonify({"error": f"No {tier} image found"}), 404

    return send_file(images[tier], mimetype="image/png")


@app.get("/api/outfit-options")
def get_outfit_options():
    options = load_outfit_options(config)
    return jsonify(options)


@app.put("/api/outfit-options")
def save_outfit_options():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    path = config.data_dir / "outfit_options.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return jsonify(data)


def _build_outfit_options_for_fighter(
    skimpiness_level: int | None = None,
    archetype: str = "",
    subtype: str = "",
) -> dict:
    all_options = load_outfit_options(config)
    exotics = None
    if archetype or subtype:
        exotics = load_exotic_outfit_options(config)
    base = skimpiness_level or 2
    result = {}
    for tier in ["sfw", "barely", "nsfw"]:
        tier_options = all_options.get(tier, {})
        tier_exotics = None
        if exotics:
            tier_exotics = filter_exotic_for_fighter(
                exotics, archetype=archetype, subtype=subtype,
                tier=tier, skimpiness_level=base,
            ) or None
        result[tier] = filter_outfit_options(
            tier_options, skimpiness_level=skimpiness_level,
            exotic_one_pieces=tier_exotics,
        )
    return result


if __name__ == "__main__":
    app.run(port=5001, debug=True)
