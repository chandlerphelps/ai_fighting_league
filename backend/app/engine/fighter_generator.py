import json
import random
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.config import Config
from app.models.fighter import Fighter, Stats, Record, Condition
from app.services.openrouter import call_openrouter_json

from app.engine.fighter_config import (
    ARCHETYPES_FEMALE,
    ARCHETYPES_MALE,
    SKIMPINESS_LEVELS,
    TECH_LEVELS,
    _roll_skimpiness,
    _roll_body_traits,
    _roll_subtype,
    _find_subtype,
    _build_body_directive,
    _build_body_shape_line,
    _build_nsfw_anatomy_line,
    load_outfit_options,
    filter_outfit_options,
    load_exotic_outfit_options,
    filter_exotic_for_fighter,
)
from app.prompts.fighter_prompts import (
    GUIDE_CORE_PHILOSOPHY,
    GUIDE_VISUAL_DESIGN,
    GUIDE_CREATION_WORKFLOW,
    GUIDE_COMMON_MISTAKES,
    FULL_CHARACTER_GUIDE,
    SYSTEM_PROMPT_ROSTER_PLANNER,
    SYSTEM_PROMPT_CHARACTER_DESIGNER,
    build_plan_roster_prompt,
    build_generate_fighter_prompt,
)
from app.prompts.outfit_prompts import (
    OUTFIT_STYLE_RULES,
    SYSTEM_PROMPT_OUTFIT_DESIGNER,
    build_tier_prompt as _build_tier_prompt,
)
from app.prompts.image_builders import (
    CHARSHEET_LAYOUT,
    _charsheet_style_base,
    _charsheet_style,
    _charsheet_tail,
    _build_charsheet_prompt,
    build_body_reference_prompt,
)


def plan_roster(
    config: Config, roster_size: int = 8, existing_fighters: list[dict] = None
) -> list[dict]:
    existing_roster_text = ""
    if existing_fighters:
        roster_lines = []
        for ef in existing_fighters:
            parts = [f"- {ef.get('ring_name', '?')} ({ef.get('gender', '?')})"]
            parts.append(f"from {ef.get('origin', '?')}")
            if ef.get("primary_archetype"):
                arch_str = ef["primary_archetype"]
                if ef.get("subtype"):
                    arch_str += f"/{ef['subtype']}"
                parts.append(arch_str)
            build = ef.get("build", "")
            if build:
                parts.append(build[:60])
            personality = ef.get("personality", "")
            if personality:
                parts.append(personality[:40])
            roster_lines.append(" — ".join(parts))
        existing_roster_text = (
            "\n\nEXISTING ROSTER (design around these — no duplicates):\n"
            + "\n".join(roster_lines)
        )

    prompt = build_plan_roster_prompt(roster_size, existing_roster_text)

    result = call_openrouter_json(
        prompt,
        config,
        model="minimax/minimax-m2.5",
        system_prompt=SYSTEM_PROMPT_ROSTER_PLANNER,
        temperature=0.9,
        max_tokens=8192,
    )

    if isinstance(result, dict) and "roster" in result:
        result = result["roster"]
    if not isinstance(result, list):
        raise RuntimeError(
            f"Expected a JSON array from roster planning, got: {type(result)}"
        )

    return result


def _generate_outfits(
    config: Config,
    character_summary: dict,
    skimpiness_level: int,
    tiers: list[str] | None = None,
    outfit_options_by_tier: dict | None = None,
    tech_level: str = "",
) -> dict:
    if tiers is None:
        tiers = ["sfw", "barely", "nsfw"]

    def _fetch_tier(tier):
        tier_opts = (outfit_options_by_tier or {}).get(tier)
        prompt = _build_tier_prompt(
            tier, skimpiness_level, character_summary, outfit_options=tier_opts,
            tech_level=tech_level,
        )
        result = call_openrouter_json(
            prompt, config, system_prompt=SYSTEM_PROMPT_OUTFIT_DESIGNER, temperature=0.5
        )
        return tier, result

    outfit_data = {}
    outfit_suggestions = {}
    with ThreadPoolExecutor(max_workers=len(tiers)) as pool:
        results = pool.map(_fetch_tier, tiers)
    for tier, result in results:
        tier_opts = (outfit_options_by_tier or {}).get(tier)
        if tier_opts:
            outfit_suggestions[tier] = tier_opts
        outfit_data.update(result)

    outfit_data["_outfit_suggestions"] = outfit_suggestions
    return outfit_data


def generate_fighter(
    config: Config,
    archetype: str = None,
    has_supernatural: bool = False,
    existing_fighters: list[dict] = None,
    roster_plan_entry: dict = None,
    tiers: list[str] | None = None,
    outfit_options_by_tier: dict | None = None,
    skimpiness_level: int | None = None,
) -> Fighter:
    if roster_plan_entry:
        blueprint_text = (
            "BLUEPRINT DIRECTIVE — you MUST follow this plan for the character:\n"
            + json.dumps(roster_plan_entry, indent=2)
            + "\n\nFollow the blueprint closely: use the ring name, origin, gender, "
            "archetype, and supernatural status exactly "
            "as specified. Flesh out the full character from this skeleton."
        )
        has_supernatural = roster_plan_entry.get("has_supernatural", False)
        archetype = roster_plan_entry.get("primary_archetype", archetype)
        if skimpiness_level is None:
            skimpiness_level = _roll_skimpiness(
                roster_plan_entry.get("skimpiness_weights")
            )
    else:
        blueprint_text = ""
        if skimpiness_level is None:
            skimpiness_level = _roll_skimpiness(None)

    subtype_info = None
    if roster_plan_entry and roster_plan_entry.get("subtype"):
        subtype_info = _find_subtype(archetype, roster_plan_entry["subtype"])
    if subtype_info is None:
        subtype_info = _roll_subtype(archetype)

    if subtype_info:
        blueprint_text += (
            f"\n\nSUBTYPE: {subtype_info['name']} — {subtype_info['description']}"
        )

    body_traits = _roll_body_traits(archetype, subtype=subtype_info)
    body_directive = _build_body_directive(body_traits)

    supernatural_instruction = ""
    if has_supernatural:
        supernatural_instruction = (
            "This fighter HAS supernatural abilities. Give the supernatural stat "
            "a value between 20-50. The supernatural ability should tie into "
            "their concept naturally."
        )
    else:
        supernatural_instruction = "This fighter has NO supernatural abilities. The supernatural stat must be 0."

    archetype_text = (
        f"Primary archetype: {archetype}" if archetype else "Choose a fitting archetype"
    )

    existing_roster_text = ""
    if existing_fighters:
        roster_lines = []
        for ef in existing_fighters:
            line = (
                f"- {ef.get('ring_name', '?')} ({ef.get('gender', '?')}, {ef.get('height', '?')})"
                f" — from {ef.get('origin', '?')}"
                f" | {ef.get('build', '?')}, {ef.get('distinguishing_features', '?')}"
                f" | Attire: {ef.get('ring_attire', '?')}"
            )
            roster_lines.append(line)
        existing_roster_text = (
            "\n\nEXISTING ROSTER (you MUST create a COMPLETELY DIFFERENT character — "
            "no duplicate ring names, different origin/nationality, "
            "different physical appearance):\n" + "\n".join(roster_lines)
        )

    prompt = build_generate_fighter_prompt(
        archetype_text=archetype_text,
        existing_roster_text=existing_roster_text,
        blueprint_text=blueprint_text,
        body_directive=body_directive,
        supernatural_instruction=supernatural_instruction,
        min_total_stats=config.min_total_stats,
        max_total_stats=config.max_total_stats,
        subtype_info=subtype_info,
    )

    result = call_openrouter_json(
        prompt, config, system_prompt=SYSTEM_PROMPT_CHARACTER_DESIGNER, temperature=0.5
    )

    fighter_id = f"f_{uuid.uuid4().hex[:8]}"

    stats = _extract_stats(result.get("stats", {}), has_supernatural, config)
    _normalize_core_stats(stats, config)

    body_parts = result.get("image_prompt_body_parts", "")
    expression = result.get("image_prompt_expression", "")
    personality_pose = result.get("image_prompt_personality_pose", "")
    gender = result.get("gender", "female")
    origin = result.get("origin", "")

    result["body_type_details"] = body_traits
    result["primary_archetype"] = archetype or ""
    result["subtype"] = subtype_info["name"] if subtype_info else ""

    tech_level = random.choice(TECH_LEVELS)

    outfit_data = _generate_outfits(
        config,
        result,
        skimpiness_level,
        tiers=tiers,
        outfit_options_by_tier=outfit_options_by_tier,
        tech_level=tech_level,
    )

    outfit_suggestions = outfit_data.pop("_outfit_suggestions", {})

    clothing_sfw = outfit_data.get("image_prompt_clothing_sfw", "")
    clothing = outfit_data.get("image_prompt_clothing", "")
    clothing_nsfw = outfit_data.get("image_prompt_clothing_nsfw", "")

    pose_sfw = outfit_data.get("image_prompt_pose_sfw", "") or personality_pose
    pose_barely = outfit_data.get("image_prompt_pose", "") or personality_pose
    pose_nsfw = outfit_data.get("image_prompt_pose_nsfw", "") or personality_pose

    iconic_features = result.get("iconic_features", "")

    return Fighter(
        id=fighter_id,
        ring_name=result.get("ring_name", "Unknown"),
        real_name=result.get("real_name", "Unknown"),
        age=result.get("age", 25),
        origin=result.get("origin", "Unknown"),
        gender=gender,
        primary_archetype=archetype or "",
        subtype=subtype_info["name"] if subtype_info else "",
        height=body_traits["height"],
        weight=body_traits["weight"],
        build=result.get("build", ""),
        distinguishing_features=result.get("distinguishing_features", ""),
        iconic_features=result.get("iconic_features", ""),
        personality=result.get("personality", ""),
        image_prompt_personality_pose=personality_pose,
        ring_attire=outfit_data.get("ring_attire", ""),
        ring_attire_sfw=outfit_data.get("ring_attire_sfw", ""),
        ring_attire_nsfw=outfit_data.get("ring_attire_nsfw", ""),
        skimpiness_level=skimpiness_level,
        tech_level=tech_level,
        image_prompt_body_ref=build_body_reference_prompt(
            body_parts,
            expression,
            gender=gender,
            body_type_details=body_traits,
            origin=origin,
            subtype_info=subtype_info,
            age=result.get("age", 25),
        ),
        image_prompt=_build_charsheet_prompt(
            body_parts,
            clothing,
            expression,
            personality_pose=pose_barely,
            tier="barely",
            gender=gender,
            skimpiness_level=skimpiness_level,
            body_type_details=body_traits,
            origin=origin,
            subtype_info=subtype_info,
            iconic_features=iconic_features,
            age=result.get("age", 25),
        ),
        image_prompt_sfw=_build_charsheet_prompt(
            body_parts,
            clothing_sfw,
            expression,
            personality_pose=pose_sfw,
            tier="sfw",
            gender=gender,
            skimpiness_level=skimpiness_level,
            body_type_details=body_traits,
            origin=origin,
            subtype_info=subtype_info,
            iconic_features=iconic_features,
            age=result.get("age", 25),
        ),
        image_prompt_nsfw=_build_charsheet_prompt(
            body_parts,
            clothing_nsfw,
            expression,
            personality_pose=pose_nsfw,
            tier="nsfw",
            gender=gender,
            skimpiness_level=skimpiness_level,
            body_type_details=body_traits,
            origin=origin,
            subtype_info=subtype_info,
            iconic_features=iconic_features,
            age=result.get("age", 25),
        ),
        stats=stats,
        record=Record(),
        condition=Condition(),
        storyline_log=[],
        outfit_suggestions=outfit_suggestions,
        body_type_details=body_traits,
        rivalries=[],
        last_fight_date=None,
        ranking=None,
    )


def _extract_stats(data: dict, has_supernatural: bool, config: Config) -> Stats:
    power = max(config.stat_min, min(config.stat_max, int(data.get("power", 50))))
    speed = max(config.stat_min, min(config.stat_max, int(data.get("speed", 50))))
    technique = max(
        config.stat_min, min(config.stat_max, int(data.get("technique", 50)))
    )
    toughness = max(
        config.stat_min, min(config.stat_max, int(data.get("toughness", 50)))
    )

    supernatural = 0
    if has_supernatural:
        supernatural = max(
            0, min(config.supernatural_cap, int(data.get("supernatural", 0)))
        )

    return Stats(
        power=power,
        speed=speed,
        technique=technique,
        toughness=toughness,
        supernatural=supernatural,
    )


def _normalize_core_stats(stats: Stats, config: Config):
    total = stats.core_total()

    if config.min_total_stats <= total <= config.max_total_stats:
        return

    target = (config.min_total_stats + config.max_total_stats) // 2
    ratio = target / total if total > 0 else 1.0

    for field_name in ("power", "speed", "technique", "toughness"):
        old_val = getattr(stats, field_name)
        new_val = max(config.stat_min, min(config.stat_max, round(old_val * ratio)))
        setattr(stats, field_name, new_val)
