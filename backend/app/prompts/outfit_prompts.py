from app.engine.fighter_config import (
    SKIMPINESS_LEVELS,
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


def build_tier_prompt(
    tier: str,
    skimpiness_level: int,
    character_summary: dict,
    outfit_options: dict | None = None,
) -> str:
    level = SKIMPINESS_LEVELS.get(skimpiness_level, SKIMPINESS_LEVELS[2])
    sig = character_summary.get("iconic_features", "")
    ring_name = character_summary.get("ring_name", "Unknown")
    body_parts = character_summary.get("image_prompt_body_parts", "")
    expression = character_summary.get("image_prompt_expression", "")

    if tier == "barely":
        effective_skimpiness = skimpiness_level + 4
    else:
        effective_skimpiness = skimpiness_level

    char_base = f"""CHARACTER: {ring_name}
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
        tops = outfit_options.get("tops", [])
        bottoms = outfit_options.get("bottoms", [])
        one_pieces = outfit_options.get("one_pieces", [])
        lines = []
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

    if tier == "sfw":
        return f"""{char_context}

Generate the "{level['sfw_label']}" tier outfit for this character (skimpiness {effective_skimpiness}/8).

{OUTFIT_STYLE_RULES}
{outfit_examples_text}
RULES:
  HARD RULES: {level['sfw_hard_rules']}
  SKIN TARGET: ~{level['sfw_skin_pct']}% of skin visible.
  VIBE: {level['sfw_label']} — {level['sfw_guidance']}
  Iconic features + additional clothing pieces to hit the skin target.

You have FULL creative freedom on what clothing items to use. The rules above only constrain HOW MUCH skin shows, not WHAT the outfit looks like.

POSE: Also generate a short personality pose for this tier — a confident, powerful pose that fits a family-friendly context. 5-10 words max describing the body position and attitude.

Return ONLY valid JSON:
{{
  "ring_attire_sfw": "<concise SFW outfit description — list each item plainly, no flowery language>",
  "image_prompt_clothing_sfw": "<SFW clothing for image gen — just the clothing pieces, no adjective fluff>",
  "image_prompt_pose_sfw": "<concise personality pose for this tier — 5-10 words>"
}}"""

    elif tier == "barely":
        return f"""{char_context}

Generate the "{level['barely_label']}" tier outfit for this character (skimpiness {effective_skimpiness}/8).

{OUTFIT_STYLE_RULES}
{outfit_examples_text}
RULES:
  HARD RULES: {level['barely_hard_rules']}
  SKIN TARGET: ~{level['barely_skin_pct']}% of skin visible.
  VIBE: {level['barely_label']} — {level['barely_guidance']}
  Iconic features + additional pieces to hit the skin target.

You have FULL creative freedom on what clothing items to use. The rules above only constrain HOW MUCH skin shows, not WHAT the outfit looks like.

POSE: Also generate a short personality pose for this tier — suggestive, flirty, showing off the outfit and sex appeal. 5-10 words max.

Return ONLY valid JSON:
{{
  "ring_attire": "<concise outfit description — list each item plainly, no flowery language>",
  "image_prompt_clothing": "<clothing for image gen — just the clothing pieces, no adjective fluff>",
  "image_prompt_pose": "<concise personality pose for this tier — 5-10 words>"
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

Return ONLY valid JSON:
{{
  "ring_attire_nsfw": "<concise NSFW description — {attire_hint}>",
  "image_prompt_clothing_nsfw": "<NSFW clothing for image gen — {clothing_hint}>",
  "image_prompt_pose_nsfw": "<concise NSFW pose matching the {level['nsfw_adjective']} tone — 5-15 words>"}}"""
