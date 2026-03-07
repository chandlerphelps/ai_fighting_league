from app.engine.fighter_config import (
    SKIMPINESS_LEVELS,
    MALE_SKIMPINESS_LEVELS,
    FIT_STYLES,
    TRANSPARENCY_OPTIONS,
    ARCHETYPE_DESCRIPTIONS,
    ARCHETYPE_SUBTYPES,
    ARCHETYPE_SUBTYPES_MALE,
    OUTFIT_COVERABLE_TRAITS_FEMALE,
    OUTFIT_COVERABLE_TRAITS_MALE,
    _build_body_shape_line,
    _build_nsfw_anatomy_line,
)


OUTFIT_STYLE_RULES = """STYLE RULES (apply to ALL tiers):
- Be CONCISE. No fluff or purple prose. "chain necklace with sickle pendant" not "kusarigama chain necklace with sickle pendant swaying menacingly".
- List MORE pieces of apparel. Include footwear, gloves/hand wraps, jewelry, belts, and accessories.
- Above all, the character needs to LOOK COOL and dangerous in their outift.
- Every outfit should have at least 4-5 distinct items. Even minimal outfits should specify shoes, jewelry, gloves, and accessories.
- FOOTWEAR: Avoid stilettos unless a strong personality match with the character. Prefer combat boots, sneakers, bare feet, platform boots, or flats."""


SYSTEM_PROMPT_OUTFIT_DESIGNER = (
    "You are an outfit designer for a fighting league. "
    "Design outfits that match the character's personality and the tier's rules. "
    "Always respond with valid JSON only."
)


def _coverage_instruction(gender: str) -> str:
    traits = OUTFIT_COVERABLE_TRAITS_MALE if gender.lower() == "male" else OUTFIT_COVERABLE_TRAITS_FEMALE
    return f"""
BODY COVERAGE: For the outfit you just designed, classify how each of these body traits
is affected. Only include traits that are NOT "exposed" (exposed is the default).
Traits to classify: {", ".join(traits)}

States:
- "exposed": bare skin, fully visible
- "transparent": sheer/mesh fabric, trait visible through material
- "form-fitted": tight opaque fabric, shape/outline clearly visible
- "half-obscured": partially covered (sideboob, underbutt, cutouts, etc.)
- "covered": fully hidden, not discernible through clothing"""


def build_tier_prompt(
    tier: str,
    skimpiness_level: int,
    character_summary: dict,
    outfit_options: dict | None = None,
    tech_level: str = "",
    fit_style: str = "",
    transparency: str = "",
) -> str:
    gender = character_summary.get("gender", "female")
    is_male = gender.lower() == "male"

    if is_male:
        if tier == "nsfw":
            tier = "barely"
        level = MALE_SKIMPINESS_LEVELS.get(skimpiness_level, MALE_SKIMPINESS_LEVELS[2])
    else:
        level = SKIMPINESS_LEVELS.get(skimpiness_level, SKIMPINESS_LEVELS[2])

    sig = character_summary.get("iconic_features", "")
    ring_name = character_summary.get("ring_name", "Unknown")
    body_parts = character_summary.get("image_prompt_body_parts", "")
    expression = character_summary.get("image_prompt_expression", "")
    primary_archetype = character_summary.get("primary_archetype", "")
    subtype = character_summary.get("subtype", "")
    personality = character_summary.get("personality", "")

    if tier == "barely":
        effective_skimpiness = skimpiness_level + 4
    else:
        effective_skimpiness = skimpiness_level

    archetype_line = ""
    if primary_archetype:
        arch_key = (
            f"The {primary_archetype}"
            if not primary_archetype.startswith("The ")
            else primary_archetype
        )
        arch_desc = ARCHETYPE_DESCRIPTIONS.get(arch_key, "")
        archetype_str = primary_archetype
        if arch_desc:
            archetype_str += f" — {arch_desc}"
        if subtype:
            subtype_source = ARCHETYPE_SUBTYPES_MALE if is_male else ARCHETYPE_SUBTYPES
            subtype_desc = ""
            for st in subtype_source.get(arch_key, []):
                if st["name"].lower() == subtype.lower():
                    subtype_desc = st["description"]
                    break
            if subtype_desc:
                archetype_str += f"\n  Subtype: {subtype} — {subtype_desc}"
            else:
                archetype_str += f"\n  Subtype: {subtype}"
        archetype_line = f"\nArchetype: {archetype_str}"

    personality_line = ""
    if personality:
        personality_line = f"\nPersonality: {personality}"

    tech_line = ""
    if tech_level:
        tech_line = f"\nTechnology Era: {tech_level} — design the outfit using materials, construction, and aesthetics from this era"

    char_base = f"""CHARACTER: {ring_name}{archetype_line}{personality_line}{tech_line}
Iconic features (MUST be visible in every tier): {sig}
Body: {body_parts}
Expression: {expression}"""

    body_details = character_summary.get("body_type_details", {})
    if body_details:
        char_base += f"\n{_build_body_shape_line(body_details)}"
        if tier == "nsfw":
            char_base += f"\n{_build_nsfw_anatomy_line(body_details)}"

    if tier == "nsfw":
        char_context = char_base
    else:
        char_context = char_base + f"\nSKIMPINESS LEVEL: {effective_skimpiness} of 8"

    outfit_examples_text = ""
    if outfit_options:
        exotic_one_pieces = outfit_options.get("exotic_one_pieces", [])
        tops = outfit_options.get("tops", [])
        bottoms = outfit_options.get("bottoms", [])
        one_pieces = outfit_options.get("one_pieces", [])
        if tier == "nsfw":
            all_accessories = exotic_one_pieces + tops + bottoms + one_pieces
            if all_accessories:
                outfit_examples_text = (
                    "\nExample accessories to consider: "
                    + ", ".join(all_accessories)
                    + "\n"
                )
        else:
            lines = []
            if exotic_one_pieces:
                lines.append(
                    f"Exotic one-pieces unique to this character (use instead of top+bottom): {', '.join(exotic_one_pieces)}"
                )
            if tops:
                lines.append(f"Example tops to consider: {', '.join(tops)}")
            if bottoms:
                lines.append(f"Example bottoms to consider: {', '.join(bottoms)}")
            if one_pieces:
                lines.append(
                    f"Example one-pieces to consider (use instead of top+bottom): {', '.join(one_pieces)}"
                )
            if lines:
                outfit_examples_text = "\n" + "\n".join(lines) + "\n"

    fit_line = ""
    transparency_line = ""
    if tier == "sfw" and fit_style:
        fit_desc = FIT_STYLES.get(fit_style, {}).get("description", "")
        fit_line = f"\n  FIT: {fit_style} — {fit_desc}" if fit_desc else f"\n  FIT: {fit_style}"
        if transparency and transparency != "opaque":
            transparency_line = f"\n  TRANSPARENCY: {transparency}"
        else:
            transparency_line = "\n  TRANSPARENCY: opaque — all fabric is fully opaque"

    if tier == "sfw":
        return f"""{char_context}

Generate the "{level['sfw_label']}" tier outfit for this character (skimpiness {effective_skimpiness}/8).

{OUTFIT_STYLE_RULES}
You are encouraged (but not required) to include pieces from the following in your outfit design:
{outfit_examples_text}
RULES:
  HARD RULES: {level['sfw_hard_rules']}
  SKIN TARGET: ~{level['sfw_skin_pct']}% of skin visible.
  VIBE: {level['sfw_label']} — {level['sfw_guidance']}{fit_line}{transparency_line}
  Iconic features + additional clothing pieces to hit the skin target.

Skin target and fit style are INDEPENDENT. A "skin-tight" outfit at low skimpiness covers lots of skin with tight fabric. A "loose" outfit at high skimpiness shows lots of skin with baggy/flowing pieces. Design accordingly.

POSE: Also generate a short personality pose for this tier — a confident, powerful pose that fits a family-friendly context. 5-10 words max describing the body position and attitude.
{_coverage_instruction(gender)}

Return ONLY valid JSON:
{{
  "ring_attire_sfw": "<concise SFW outfit description — list each item plainly, no flowery language>",
  "image_prompt_clothing_sfw": "<SFW clothing for image gen — just the clothing pieces, no adjective fluff>",
  "image_prompt_pose_sfw": "<concise personality pose for this tier — 5-10 words>",
  "outfit_body_coverage": {{}}
}}"""

    elif tier == "barely":
        return f"""{char_context}

Generate the "{level['barely_label']}" tier outfit for this character (skimpiness {effective_skimpiness}/8).

{OUTFIT_STYLE_RULES}
You are encouraged to include pieces from the following in your outfit design:
{outfit_examples_text}
RULES:
  HARD RULES: {level['barely_hard_rules']}
  SKIN TARGET: ~{level['barely_skin_pct']}% of skin visible.
  VIBE: {level['barely_label']} — {level['barely_guidance']}
  Iconic features + additional pieces to hit the skin target.

The rules above only constrain HOW MUCH skin shows, not WHAT the outfit looks like.

POSE: Also generate a short personality pose for this tier — {"intimidating, powerful, showing off raw physicality. 5-10 words max." if is_male else "dangerous with alluring sex appeal. 5-10 words max."}
{_coverage_instruction(gender)}

Return ONLY valid JSON:
{{
  "ring_attire": "<concise outfit description — list each item plainly, no flowery language>",
  "image_prompt_clothing": "<clothing for image gen — just the clothing pieces, no adjective fluff>",
  "image_prompt_pose": "<concise personality pose for this tier — 5-10 words>",
  "outfit_body_coverage": {{}}
}}"""

    else:
        nudity_level = level.get("nsfw_nudity_level", "full")
        if nudity_level == "topless":
            additional = (
                "ADDITIONAL: The character is topless but keeps bottoms on. "
                "The bottoms (if they can be called that) must be ultra-sexy - tape, jewelry, insanely tiny triangle bottom gstring, etc"
                "Still include accessories — boots/heels, gloves, jewelry, chokers, belts, etc. "
                "The image_prompt_clothing_nsfw MUST include the sexy bottom garment plus accessories."
            )
            attire_hint = "topless plus ultra-sexy bottom and each remaining accessory listed plainly"
            clothing_hint = "sexy bottom garment plus accessories"
            image_prompt_rules = (
                "## IMAGE PROMPT RULES — FOLLOW EXACTLY\n\n"
                "image_prompt_clothing_nsfw rules:\n"
                "- Keep it short\n"
                "- Always start with the remaining iconic features\n"
                "- This is Level 1 (topless only): include the sexy bottom garment."
                "- The charsheet prompt automatically adds the topless framing"
            )
        else:
            additional = (
                "ADDITIONAL: Even fully NSFW characters should still have accessories — "
                "boots/heels, gloves, jewelry, chokers, belts, etc. "
                "The nudity is the nipples and crotch; the outfit is what remains ON the body."
            )
            attire_hint = "nude plus each remaining accessory listed plainly"
            clothing_hint = "remaining accessories only"
            image_prompt_rules = (
                "## IMAGE PROMPT RULES — FOLLOW EXACTLY\n\n"
                "image_prompt_clothing_nsfw rules:\n"
                "- Keep it short\n"
                "- Always start with the remaining iconic features\n"
                "- This is Levels 2-4 (fully nude): only accessories remain."
                "- The charsheet prompt automatically adds the nudity framing"
            )

        return f"""{char_context}

Generate the NSFW outfit for this character. Tone: {level['nsfw_adjective']}.

{OUTFIT_STYLE_RULES}
{outfit_examples_text}
{additional}

RULES:
  HARD RULES: {level['nsfw_hard_rules']}. Only iconic features and accessories remain.
  TONE: {level['nsfw_adjective']} — {level['nsfw_description']}

{image_prompt_rules}

POSE: Also generate a short personality pose for this NSFW tier that matches the tone: {level['nsfw_adjective']}. 5-15 words max describing body position and attitude.
{_coverage_instruction(gender)}

Return ONLY valid JSON:
{{
  "ring_attire_nsfw": "<concise NSFW description — {attire_hint}>",
  "image_prompt_clothing_nsfw": "<NSFW clothing for image gen — {clothing_hint}>",
  "image_prompt_pose_nsfw": "<concise NSFW pose matching the {level['nsfw_adjective']} tone — 5-15 words>",
  "outfit_body_coverage": {{}}
}}"""
