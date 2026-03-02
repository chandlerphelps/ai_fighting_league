from app.engine.image_style import get_art_style, get_art_style_tail
from app.engine.fighter_config import _build_body_shape_line, _build_nsfw_anatomy_line
from app.services.grok_image import TIER_PROMPT_KEYS


CHARSHEET_LAYOUT = (
    "character model sheet, character reference sheet, "
    "three full-body views of the exact same character side by side: "
    "front-facing slightly angled view on the left, "
    "personality pose in the center, "
    "rear view on the right, "
    "consistent outfit across all three views, "
    "full body head to toe visible in each panel, "
    "plain flat color background, organized reference sheet layout"
)


def _charsheet_style_base(gender: str = "female") -> str:
    return get_art_style(gender) + ", character design reference sheet"


def _charsheet_style(
    gender: str = "female", tier: str = "barely", skimpiness_level: int = 4
) -> str:
    base = _charsheet_style_base(gender)
    if tier == "nsfw":
        if gender.lower() == "male":
            nudity_prefix = (
                "explicit uncensored NSFW, full frontal male nudity, fully naked man, "
            )
        elif skimpiness_level == 1:
            nudity_prefix = (
                "explicit uncensored NSFW, topless woman, bare breasts visible, "
            )
        else:
            nudity_prefix = "explicit uncensored NSFW, perfectly drawn bare pussy visible, full frontal female nudity, "
        return nudity_prefix + base + ", " + CHARSHEET_LAYOUT
    return base + ", " + CHARSHEET_LAYOUT


def _charsheet_tail(
    gender: str = "female", tier: str = "barely", skimpiness_level: int = 4
) -> str:
    tail_base = (
        get_art_style_tail(gender)
        + ", character reference sheet, three consistent views"
    )
    if tier == "nsfw":
        if gender.lower() == "male":
            return (
                get_art_style_tail(gender) + ", "
                "explicit full frontal male nudity, completely naked, muscular physique fully visible, "
                "character reference sheet, three consistent views"
            )
        if skimpiness_level == 1:
            return (
                get_art_style_tail(gender) + ", "
                "topless female nudity, bare breasts visible, "
                "character reference sheet, three consistent views"
            )
        return (
            get_art_style_tail(gender) + ", "
            "explicit full frontal female nudity, completely naked, bare breasts and perfectly drawn bare pussy visible, "
            "character reference sheet, three consistent views"
        )
    return tail_base


def _build_charsheet_prompt(
    body_parts: str,
    clothing: str,
    expression: str,
    personality_pose: str = "",
    tier: str = "barely",
    gender: str = "female",
    skimpiness_level: int = 4,
    body_type_details: dict | None = None,
    origin: str = "",
) -> dict:
    if not body_parts:
        return {}

    anatomy = ""
    if body_type_details:
        body_parts = f"{body_parts}, {_build_body_shape_line(body_type_details)}"
        if tier == "nsfw":
            anatomy = _build_nsfw_anatomy_line(body_type_details)

    style = _charsheet_style(gender, tier, skimpiness_level)

    pose_base = personality_pose or "dynamic signature pose"

    if tier == "nsfw":
        if skimpiness_level == 1:
            clothing_part = (
                f"topless, bare breasts, {clothing}"
                if clothing
                else "topless, bare breasts"
            )
        else:
            clothing_part = (
                f"completely naked except {clothing}"
                if clothing
                else "completely naked"
            )
    else:
        clothing_part = clothing

    character_desc = body_parts
    if clothing_part:
        character_desc = f"{body_parts}, {clothing_part}"
    if origin:
        character_desc = f"{character_desc}, from {origin}"

    front_view = "front slightly angled view standing tall"
    center_pose = f"center personality pose: {pose_base}"
    back_view = "rear view standing tall"

    tail = _charsheet_tail(gender, tier, skimpiness_level)

    sections = [
        f"[STYLE] {style}",
        f"[CHARACTER] {character_desc}",
        f"[ANATOMY] {anatomy}" if anatomy else "",
        f"[VIEWS] {front_view}, {center_pose}, {back_view}",
        f"[EXPRESSION] {expression}" if expression else "",
        f"[QUALITY] {tail}",
        f"[ANATOMY EMPHASIS] {anatomy}" if anatomy else "",
    ]
    full = "\n".join(s for s in sections if s)

    return {
        "style": style,
        "layout": CHARSHEET_LAYOUT,
        "body_parts": body_parts,
        "clothing": clothing_part,
        "character_desc": character_desc,
        "front_view": front_view,
        "center_pose": center_pose,
        "back_view": back_view,
        "expression": expression,
        "full_prompt": full,
    }


def _nsfw_prefix(gender: str, skimpiness_level: int) -> str:
    if gender.lower() == "male":
        return "explicit uncensored NSFW, full frontal male nudity, fully naked man, "
    if skimpiness_level == 1:
        return "explicit uncensored NSFW, topless woman, bare breasts visible, "
    return (
        "explicit uncensored NSFW, full frontal female nudity, "
        "fully naked woman, perfectly drawn bare pussy visible, "
    )


def _nsfw_tail(gender: str, skimpiness_level: int) -> str:
    if gender.lower() == "male":
        return (
            "explicit full frontal male nudity, completely naked, "
            "muscular physique fully visible"
        )
    if skimpiness_level == 1:
        return "topless female nudity, bare breasts visible"
    return (
        "explicit full frontal female nudity, completely naked, "
        "bare breasts and perfectly drawn bare pussy visible"
    )


BODY_REF_LAYOUT = (
    "anatomy study page, 2x2 grid layout, parchment background, "
    "four distinct panels showing the same character"
)


def build_body_reference_prompt(
    body_parts: str,
    expression: str,
    gender: str = "female",
    body_type_details: dict | None = None,
    origin: str = "",
) -> dict:
    if not body_parts:
        return {}

    style = get_art_style(gender)

    body_shape = ""
    anatomy = ""
    if body_type_details:
        body_shape = _build_body_shape_line(body_type_details)
        anatomy = _build_nsfw_anatomy_line(body_type_details)
        body_parts = f"{body_parts}, {body_shape}"

    subject = body_parts
    if origin:
        subject = f"{subject}, from {origin}"

    if gender.lower() == "male":
        chest_panel = (
            "collarbone to hips, bare chest, abs, pecs, front view"
        )
        butt_panel = (
            "bent forward, butt popped, rear view, muscular glutes"
        )
        intimate_panel = (
            "navel to mid-thigh, legs apart, front view, fully nude"
        )
        nudity_prefix = (
            "explicit uncensored NSFW, full frontal male nudity, "
            "fully naked man, "
        )
    else:
        chest_panel = (
            "collarbone to hips, bare breasts, abs, front view"
        )
        butt_panel = (
            "bent forward, butt popped, rear view, explicit detail, "
            "hands spreading"
        )
        intimate_panel = (
            "navel to mid-thigh, legs spread, detailed, front view"
        )
        nudity_prefix = (
            "explicit uncensored NSFW, full frontal female nudity, "
            "fully naked woman, perfectly drawn bare pussy visible, "
        )

    sections = [
        f"[STYLE] {nudity_prefix}{style}, anatomy study page, 2x2 grid, parchment background",
        f"[LAYOUT] face top-left, chest and torso top-right, butt bottom-left, intimate bottom-right",
        f"[SUBJECT] completely naked, {subject}",
        f"[TOP-LEFT: FACE] {expression}, three-quarter angle, head and shoulders",
        f"[TOP-RIGHT: CHEST AND TORSO] {chest_panel}",
        f"[BOTTOM-LEFT: BUTT] {butt_panel}",
        f"[BOTTOM-RIGHT: INTIMATE] {intimate_panel}",
        f"[ANATOMY] {anatomy}" if anatomy else "",
        f"[QUALITY] anatomical precision, figure drawing quality, {get_art_style_tail(gender)}",
    ]
    full = "\n".join(s for s in sections if s)

    return {
        "body_parts": body_parts,
        "expression": expression,
        "anatomy": anatomy,
        "full_prompt": full,
    }


def build_move_image_prompt(fighter: dict, move: dict, tier: str) -> str:
    gender = fighter.get("gender", "female")
    skimpiness = fighter.get("skimpiness_level", 2)

    prompt_key = TIER_PROMPT_KEYS.get(tier, "image_prompt")
    tier_prompt = fighter.get(prompt_key, {})
    body_parts = tier_prompt.get("body_parts", "")
    clothing = tier_prompt.get("clothing", "")
    expression = tier_prompt.get("expression", "")

    move_name = move.get("name", "")
    move_snapshot = move.get("image_snapshot", move.get("description", ""))

    style = get_art_style(gender)
    tail = get_art_style_tail(gender)

    parts = []

    if tier == "nsfw":
        parts.append(_nsfw_prefix(gender, skimpiness))

    parts.append(style)
    parts.append(
        "single full-body action pose, dynamic combat movement, "
        "fighting game screenshot, dramatic camera angle"
    )

    if body_parts:
        parts.append(body_parts)
    if clothing:
        parts.append(clothing)

    parts.append(f'performing "{move_name}": {move_snapshot}')

    if expression:
        parts.append(expression)

    if clothing:
        parts.append(clothing)

    parts.append(
        "motion blur on limbs, impact energy effects, "
        "dramatic volumetric lighting, arena background"
    )

    if tier == "nsfw":
        parts.append(_nsfw_tail(gender, skimpiness))

    parts.append(tail)

    return ", ".join(p.strip().rstrip(",") for p in parts if p.strip())
