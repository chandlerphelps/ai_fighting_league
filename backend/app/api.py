import json
import threading
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

from app.config import load_config
from app.engine.fighter_generator import (
    generate_fighter,
    generate_fighter_json_only,
    plan_roster,
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
from app.engine.pool_summarizer import summarize_fighter_pool
from app.models.fighter import Fighter, Stats
from app.services import data_manager
from app.services.grok_image import generate_charsheet_images
from app.engine.move_generator import build_move_image_prompt, _slugify as move_slugify
from app.services.grok_image import edit_image, download_image
from app.prompts.image_builders import build_portrait_prompt, build_body_reference_prompt

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

FIELD_DEPENDENCIES = {
    "primary_outfit_color": ["outfits", "image_prompts", "images"],
    "hair_style":           ["image_prompts", "images"],
    "hair_color":           ["image_prompts", "images"],
    "face_adornment":       ["image_prompts", "images"],
    "primary_archetype":    ["outfits", "image_prompts", "images"],
    "subtype":              ["outfits", "image_prompts", "images"],
    "build":                ["outfits", "image_prompts", "images"],
    "height":               ["image_prompts", "images"],
    "weight":               ["image_prompts", "images"],
    "body_type_details":    ["image_prompts", "images"],
    "distinguishing_features": ["outfits", "image_prompts", "images"],
    "iconic_features":      ["image_prompts", "images"],
    "personality":          ["outfits", "image_prompts", "images"],
    "ring_attire":          ["image_prompts", "images"],
    "ring_attire_sfw":      ["image_prompts", "images"],
    "ring_attire_nsfw":     ["image_prompts", "images"],
    "skimpiness_level":     ["outfits", "image_prompts", "images"],
    "image_prompt_personality_pose": ["image_prompts", "images"],
    "image_prompt_body_ref": ["images"],
    "image_prompt_sfw":      ["images"],
    "image_prompt":          ["images"],
    "image_prompt_nsfw":     ["images"],
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
    for tier in ["sfw", "barely", "nsfw", "portrait"]:
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
    new_dirty = set(existing.get("generation_dirty", []))

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

        deps = FIELD_DEPENDENCIES.get(key, [])
        for dep in deps:
            new_dirty.add(dep)

    if needs_prompt_rebuild:
        _rebuild_prompts(existing)

    if new_dirty:
        existing["generation_dirty"] = sorted(new_dirty)
        stage = existing.get("generation_stage", 0)
        if "images" in new_dirty and stage >= 2:
            existing["generation_stage"] = 1

    data_manager.save_fighter(existing, config)

    response = dict(existing)
    if new_dirty:
        response["_invalidated"] = sorted(new_dirty)
    return jsonify(response)


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


@app.get("/api/roster-plan")
def get_roster_plan():
    plan = data_manager.load_roster_plan(config)
    if not plan:
        return jsonify(None)
    return jsonify(plan)


@app.post("/api/roster-plan")
def create_roster_plan():
    body = request.json or {}
    count = body.get("count", 8)
    mode = body.get("mode", "initial")

    existing_on_disk = data_manager.load_all_fighters(config)
    pool_summary = summarize_fighter_pool(existing_on_disk) if existing_on_disk else ""

    task_id = f"plan_{uuid.uuid4().hex[:8]}"

    def do_plan():
        existing_summaries = [
            {
                "ring_name": f.get("ring_name"),
                "gender": f.get("gender", ""),
                "origin": f.get("origin"),
                "primary_archetype": f.get("primary_archetype", ""),
                "subtype": f.get("subtype", ""),
                "build": f.get("build", ""),
                "personality": f.get("personality", ""),
            }
            for f in existing_on_disk
        ]

        entries = plan_roster(
            config,
            roster_size=count,
            existing_fighters=existing_summaries,
            pool_summary=pool_summary,
        )

        for entry in entries:
            entry.setdefault("status", "pending")
            entry.setdefault("fighter_id", None)
            entry.setdefault("primary_outfit_color", "")
            entry.setdefault("hair_style", "")
            entry.setdefault("hair_color", "")
            entry.setdefault("face_adornment", "")

        plan = {
            "plan_id": f"rp_{uuid.uuid4().hex[:8]}",
            "created_at": str(__import__("datetime").date.today()),
            "mode": mode,
            "pool_summary": pool_summary,
            "entries": entries,
        }
        data_manager.save_roster_plan(plan, config)
        return plan

    _run_in_background(task_id, do_plan)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.put("/api/roster-plan/entries/<int:index>")
def update_plan_entry(index: int):
    plan = data_manager.load_roster_plan(config)
    if not plan:
        return jsonify({"error": "No roster plan found"}), 404

    entries = plan.get("entries", [])
    if index < 0 or index >= len(entries):
        return jsonify({"error": f"Invalid index: {index}"}), 400

    updates = request.json or {}
    for key, value in updates.items():
        entries[index][key] = value

    data_manager.save_roster_plan(plan, config)
    return jsonify(entries[index])


@app.delete("/api/roster-plan/entries/<int:index>")
def delete_plan_entry(index: int):
    plan = data_manager.load_roster_plan(config)
    if not plan:
        return jsonify({"error": "No roster plan found"}), 404

    entries = plan.get("entries", [])
    if index < 0 or index >= len(entries):
        return jsonify({"error": f"Invalid index: {index}"}), 400

    removed = entries.pop(index)
    data_manager.save_roster_plan(plan, config)
    return jsonify({"removed": removed, "remaining": len(entries)})


@app.post("/api/roster-plan/entries/<int:index>/regenerate")
def regenerate_plan_entry(index: int):
    plan = data_manager.load_roster_plan(config)
    if not plan:
        return jsonify({"error": "No roster plan found"}), 404

    entries = plan.get("entries", [])
    if index < 0 or index >= len(entries):
        return jsonify({"error": f"Invalid index: {index}"}), 400

    task_id = f"replan_{uuid.uuid4().hex[:8]}"

    def do_regen():
        existing_on_disk = data_manager.load_all_fighters(config)
        pool_summary = plan.get("pool_summary", "")
        if not pool_summary and existing_on_disk:
            pool_summary = summarize_fighter_pool(existing_on_disk)

        new_entries = plan_roster(
            config, roster_size=1,
            existing_fighters=[
                {"ring_name": f.get("ring_name"), "gender": f.get("gender", ""),
                 "origin": f.get("origin"), "primary_archetype": f.get("primary_archetype", "")}
                for f in existing_on_disk
            ],
            pool_summary=pool_summary,
        )
        if new_entries:
            new_entry = new_entries[0]
            new_entry["status"] = "pending"
            new_entry["fighter_id"] = None
            new_entry.setdefault("primary_outfit_color", "")
            new_entry.setdefault("hair_style", "")
            new_entry.setdefault("hair_color", "")
            new_entry.setdefault("face_adornment", "")
            entries[index] = new_entry
            data_manager.save_roster_plan(plan, config)
            return new_entry
        return entries[index]

    _run_in_background(task_id, do_regen)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.post("/api/roster-plan/entries/add")
def add_plan_entries():
    plan = data_manager.load_roster_plan(config)
    if not plan:
        return jsonify({"error": "No roster plan found"}), 404

    body = request.json or {}
    count = body.get("count", 1)
    task_id = f"addplan_{uuid.uuid4().hex[:8]}"

    def do_add():
        existing_on_disk = data_manager.load_all_fighters(config)
        pool_summary = plan.get("pool_summary", "")
        if not pool_summary and existing_on_disk:
            pool_summary = summarize_fighter_pool(existing_on_disk)

        new_entries = plan_roster(
            config, roster_size=count,
            existing_fighters=[
                {"ring_name": f.get("ring_name"), "gender": f.get("gender", ""),
                 "origin": f.get("origin"), "primary_archetype": f.get("primary_archetype", "")}
                for f in existing_on_disk
            ],
            pool_summary=pool_summary,
        )
        for entry in new_entries:
            entry["status"] = "pending"
            entry["fighter_id"] = None
            entry.setdefault("primary_outfit_color", "")
            entry.setdefault("hair_style", "")
            entry.setdefault("hair_color", "")
            entry.setdefault("face_adornment", "")
        plan["entries"].extend(new_entries)
        data_manager.save_roster_plan(plan, config)
        return new_entries

    _run_in_background(task_id, do_add)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.post("/api/roster-plan/generate")
def generate_from_plan():
    plan = data_manager.load_roster_plan(config)
    if not plan:
        return jsonify({"error": "No roster plan found"}), 404

    approved = [
        (i, e) for i, e in enumerate(plan.get("entries", []))
        if e.get("status") == "approved"
    ]
    if not approved:
        return jsonify({"error": "No approved entries to generate"}), 400

    task_id = f"genbatch_{uuid.uuid4().hex[:8]}"

    def do_generate():
        existing_on_disk = data_manager.load_all_fighters(config)
        existing_summaries = [
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

        generated = []
        for idx, entry in approved:
            entry["status"] = "generating"
            data_manager.save_roster_plan(plan, config)

            weights = entry.get("skimpiness_weights", [15, 35, 35, 15])
            skimpiness = _roll_skimpiness(weights)
            archetype = entry.get("primary_archetype")
            outfit_opts = _build_outfit_options_for_fighter(
                skimpiness_level=skimpiness, archetype=archetype or ""
            )

            fighter = generate_fighter_json_only(
                config,
                archetype=archetype,
                has_supernatural=entry.get("has_supernatural", False),
                existing_fighters=existing_summaries,
                roster_plan_entry=entry,
                outfit_options_by_tier=outfit_opts,
                skimpiness_level=skimpiness,
            )

            data_manager.save_fighter(fighter, config)

            ws = data_manager.load_world_state(config)
            if ws:
                if fighter.id not in ws.get("rankings", []):
                    ws["rankings"].append(fighter.id)
                    data_manager.save_world_state(ws, config)

            entry["status"] = "approved"
            entry["fighter_id"] = fighter.id
            data_manager.save_roster_plan(plan, config)

            existing_summaries.append({
                "ring_name": fighter.ring_name,
                "gender": fighter.gender,
                "height": fighter.height,
                "origin": fighter.origin,
                "build": fighter.build,
                "distinguishing_features": fighter.distinguishing_features,
                "ring_attire": fighter.ring_attire,
            })

            generated.append(fighter.to_dict())

        return {"generated_count": len(generated), "fighter_ids": [f["id"] for f in generated]}

    _run_in_background(task_id, do_generate)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.delete("/api/roster-plan")
def delete_roster_plan():
    data_manager.delete_roster_plan(config)
    return jsonify({"deleted": True})


@app.post("/api/fighters/<fighter_id>/advance-stage")
def advance_stage(fighter_id: str):
    existing = data_manager.load_fighter(fighter_id, config)
    if not existing:
        return jsonify({"error": "Fighter not found"}), 404

    current_stage = existing.get("generation_stage", 0)

    if current_stage >= 3:
        return jsonify({"error": "Fighter is already at stage 3 (fully generated)"}), 400

    task_id = f"advance_{uuid.uuid4().hex[:8]}"

    if current_stage < 1:
        return jsonify({"error": "Fighter must be at stage 1+ to advance"}), 400

    def do_advance():
        fighter_data = data_manager.load_fighter(fighter_id, config)
        stage = fighter_data.get("generation_stage", 0)

        if stage == 1:
            body_parts = fighter_data.get("image_prompt", {}).get("body_parts", "")
            if not body_parts:
                body_parts = fighter_data.get("image_prompt_sfw", {}).get("body_parts", "")
            expression = fighter_data.get("image_prompt", {}).get("expression", "")
            if not expression:
                expression = fighter_data.get("image_prompt_sfw", {}).get("expression", "")
            clothing_sfw = fighter_data.get("ring_attire_sfw", "")
            gender = fighter_data.get("gender", "female")
            subtype_info = _get_subtype_info(fighter_data)
            iconic_features = fighter_data.get("iconic_features", "")
            age = fighter_data.get("age", 0)

            portrait_prompt = build_portrait_prompt(
                body_parts, clothing_sfw, expression,
                gender=gender,
                body_type_details=fighter_data.get("body_type_details"),
                origin=fighter_data.get("origin", ""),
                subtype_info=subtype_info,
                iconic_features=iconic_features,
                hair_style=fighter_data.get("hair_style", ""),
                hair_color=fighter_data.get("hair_color", ""),
                face_adornment=fighter_data.get("face_adornment", ""),
                primary_outfit_color=fighter_data.get("primary_outfit_color", ""),
                age=age,
            )

            fighter_data["image_prompt_portrait"] = portrait_prompt

            from app.services.grok_image import generate_image, download_image as dl_img, _slugify as img_slugify
            fighters_dir = config.data_dir / "fighters"
            slug = img_slugify(fighter_data.get("ring_name", ""))
            base = f"{fighter_id}_{slug}" if slug else fighter_id
            save_path = fighters_dir / f"{base}_portrait.png"

            urls = generate_image(
                prompt=portrait_prompt.get("full_prompt", ""),
                config=config,
                aspect_ratio="1:1",
                resolution="2k",
                n=1,
            )
            if urls:
                dl_img(urls[0], save_path)

            fighter_data["generation_stage"] = 2
            fighter_data["generation_dirty"] = [
                d for d in fighter_data.get("generation_dirty", []) if d != "images"
            ]
            data_manager.save_fighter(fighter_data, config)
            return fighter_data

        elif stage == 2:
            fighter = Fighter.from_dict(fighter_data)

            if not fighter.image_prompt_body_ref:
                body_parts = fighter_data.get("image_prompt", {}).get("body_parts", "")
                if not body_parts:
                    body_parts = fighter_data.get("image_prompt_sfw", {}).get("body_parts", "")
                expression = fighter_data.get("image_prompt", {}).get("expression", "")
                if not expression:
                    expression = fighter_data.get("image_prompt_sfw", {}).get("expression", "")
                subtype_info = _get_subtype_info(fighter_data)

                fighter.image_prompt_body_ref = build_body_reference_prompt(
                    body_parts, expression,
                    gender=fighter.gender,
                    body_type_details=fighter_data.get("body_type_details"),
                    origin=fighter.origin,
                    subtype_info=subtype_info,
                    age=fighter.age,
                )

            if not fighter.image_prompt_sfw or not fighter.image_prompt_sfw.get("full_prompt"):
                _rebuild_prompts(fighter_data)
                fighter = Fighter.from_dict(fighter_data)

            fighters_dir = config.data_dir / "fighters"
            saved = generate_charsheet_images(fighter, config, fighters_dir)

            fighter_data = fighter.to_dict()
            fighter_data["generation_stage"] = 3
            fighter_data["generation_dirty"] = []
            data_manager.save_fighter(fighter_data, config)
            return fighter_data

    _run_in_background(task_id, do_advance)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.post("/api/fighters/batch-advance")
def batch_advance():
    body = request.json or {}
    fighter_ids = body.get("fighter_ids", [])
    target_stage = body.get("target_stage", 2)

    if not fighter_ids:
        return jsonify({"error": "No fighter_ids provided"}), 400
    if target_stage not in (2, 3):
        return jsonify({"error": "target_stage must be 2 or 3"}), 400

    task_id = f"batch_{uuid.uuid4().hex[:8]}"

    def do_batch():
        results = {}
        for fid in fighter_ids:
            fighter_data = data_manager.load_fighter(fid, config)
            if not fighter_data:
                results[fid] = {"error": "not found"}
                continue

            current = fighter_data.get("generation_stage", 0)
            if current >= target_stage:
                results[fid] = {"status": "already_at_stage", "stage": current}
                continue

            steps = []
            if current < 2 and target_stage >= 2:
                steps.append(1)
            if current < 3 and target_stage >= 3:
                steps.append(2)

            for step_from in steps:
                body_parts = fighter_data.get("image_prompt", {}).get("body_parts", "")
                if not body_parts:
                    body_parts = fighter_data.get("image_prompt_sfw", {}).get("body_parts", "")
                expression = fighter_data.get("image_prompt", {}).get("expression", "")
                if not expression:
                    expression = fighter_data.get("image_prompt_sfw", {}).get("expression", "")

                if step_from == 1:
                    subtype_info = _get_subtype_info(fighter_data)
                    portrait_prompt = build_portrait_prompt(
                        body_parts,
                        fighter_data.get("ring_attire_sfw", ""),
                        expression,
                        gender=fighter_data.get("gender", "female"),
                        body_type_details=fighter_data.get("body_type_details"),
                        origin=fighter_data.get("origin", ""),
                        subtype_info=subtype_info,
                        iconic_features=fighter_data.get("iconic_features", ""),
                        hair_style=fighter_data.get("hair_style", ""),
                        hair_color=fighter_data.get("hair_color", ""),
                        face_adornment=fighter_data.get("face_adornment", ""),
                        primary_outfit_color=fighter_data.get("primary_outfit_color", ""),
                        age=fighter_data.get("age", 0),
                    )
                    fighter_data["image_prompt_portrait"] = portrait_prompt

                    from app.services.grok_image import generate_image, download_image as dl_img, _slugify as img_slugify
                    fighters_dir = config.data_dir / "fighters"
                    slug = img_slugify(fighter_data.get("ring_name", ""))
                    base = f"{fid}_{slug}" if slug else fid
                    save_path = fighters_dir / f"{base}_portrait.png"
                    urls = generate_image(
                        prompt=portrait_prompt.get("full_prompt", ""),
                        config=config, aspect_ratio="1:1", resolution="2k", n=1,
                    )
                    if urls:
                        dl_img(urls[0], save_path)
                    fighter_data["generation_stage"] = 2

                elif step_from == 2:
                    fighter = Fighter.from_dict(fighter_data)
                    if not fighter.image_prompt_body_ref:
                        subtype_info = _get_subtype_info(fighter_data)
                        fighter.image_prompt_body_ref = build_body_reference_prompt(
                            body_parts, expression,
                            gender=fighter.gender,
                            body_type_details=fighter_data.get("body_type_details"),
                            origin=fighter.origin,
                            subtype_info=subtype_info,
                            age=fighter.age,
                        )
                    if not fighter.image_prompt_sfw or not fighter.image_prompt_sfw.get("full_prompt"):
                        _rebuild_prompts(fighter_data)
                        fighter = Fighter.from_dict(fighter_data)
                    fighters_dir = config.data_dir / "fighters"
                    generate_charsheet_images(fighter, config, fighters_dir)
                    fighter_data = fighter.to_dict()
                    fighter_data["generation_stage"] = 3
                    fighter_data["generation_dirty"] = []

                data_manager.save_fighter(fighter_data, config)

            results[fid] = {"status": "advanced", "stage": fighter_data.get("generation_stage", 0)}
        return results

    _run_in_background(task_id, do_batch)
    return jsonify({"task_id": task_id, "status": "running"}), 202


@app.get("/api/fighter-images/<fighter_id>/portrait")
def get_fighter_portrait(fighter_id: str):
    fighter = data_manager.load_fighter(fighter_id, config)
    if not fighter:
        return jsonify({"error": "Fighter not found"}), 404

    from app.services.grok_image import _slugify as img_slugify
    fighters_dir = config.data_dir / "fighters"
    slug = img_slugify(fighter.get("ring_name", ""))
    base = f"{fighter_id}_{slug}" if slug else fighter_id
    portrait_path = fighters_dir / f"{base}_portrait.png"

    if not portrait_path.exists():
        return jsonify({"error": "No portrait image found"}), 404

    return send_file(portrait_path, mimetype="image/png")


@app.get("/api/pool-summary")
def get_pool_summary():
    fighters = data_manager.load_all_fighters(config)
    summary = summarize_fighter_pool(fighters, for_display=True)
    return jsonify({"summary": summary, "count": len(fighters)})


@app.get("/api/world-state")
def get_world_state():
    ws = data_manager.load_world_state(config)
    if not ws:
        return jsonify({"error": "No world state found"}), 404
    return jsonify(ws)


@app.post("/api/simulate-day")
def simulate_day():
    from app.engine.day_simulator import simulate_one_day

    ws = data_manager.load_world_state(config)
    if not ws:
        return jsonify({"error": "No world state found. Run initialize_league first."}), 404

    all_fighters = data_manager.load_all_fighters(config)
    fighters = {f["id"]: f for f in all_fighters if f.get("status") == "active"}

    day_result = simulate_one_day(fighters, ws)

    for fid, fighter in fighters.items():
        data_manager.save_fighter(fighter, config)

    data_manager.save_world_state(ws, config)

    return jsonify(day_result)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
