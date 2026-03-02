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
    subtype_info: dict | None = None,
    iconic_features: str = "",
) -> dict:
    if not body_parts:
        return {}

    anatomy = ""
    if body_type_details:
        body_parts = f"{body_parts}, {_build_body_shape_line(body_type_details)}"
        if tier == "nsfw":
            anatomy = _build_nsfw_anatomy_line(body_type_details)

    if subtype_info:
        body_parts = f"{body_parts}, {subtype_info['name'].lower()} aesthetic, {subtype_info['description'].lower()}"

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

    if iconic_features and clothing_part:
        clothing_part = f"{clothing_part}, {iconic_features}"
    elif iconic_features:
        clothing_part = iconic_features

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


BODY_REF_STYLE_BASE = (
    "hand-painted textures over detailed 3D forms, "
    "extremely detailed skin textures, painterly brushstroke overlay, "
    "soft even studio lighting, highly detailed anatomy, "
    "professional perfect shading"
)

BODY_REF_STYLE_FEMALE = (
    BODY_REF_STYLE_BASE + ", strictly female character, beautiful features"
)

BODY_REF_STYLE_MALE = (
    BODY_REF_STYLE_BASE + ", male character, masculine build, rugged handsome features"
)

BODY_REF_PAGE_STYLE = (
    "artist anatomy study page, figure drawing body part studies, "
    "separate isolated body part drawings arranged on the page with three on top and two on the bottom, "
    "each body part cropped and drawn individually with space between them, "
    "clean off-white parchment background, organized sketchbook page layout, "
    "absolutely no text no words no letters no labels no captions no watermarks, "
    "drawing guide extremely detailed anatomy"
)

BODY_REF_LAYOUT = (
    "five separate drawings arranged with three on top and two on the bottom: "
    "face portrait in the top-left, "
    "nude rear angled view in the top-center, "
    "nude torso with {torso_detail} in the top-right, "
    "nude rear butt study in the bottom-left, "
    "nude {intimate_label} intimate study in the bottom-right, "
    "clear empty space between each drawing, "
    "each drawing floats independently"
)

BODY_REF_QUALITY = (
    "hand-painted textures, extremely detailed, anatomical precision, "
    "figure drawing study quality, "
    "each body part rendered as its own separate floating illustration, "
    "soft even lighting, clean parchment background, "
    "no text no words no labels no watermarks"
)


def build_body_reference_prompt(
    body_parts: str,
    expression: str,
    gender: str = "female",
    body_type_details: dict | None = None,
    origin: str = "",
    subtype_info: dict | None = None,
) -> dict:
    if not body_parts:
        return {}

    is_male = gender.lower() == "male"
    anatomy = ""
    if body_type_details:
        body_parts = f"{body_parts}, {_build_body_shape_line(body_type_details)}"
        anatomy = _build_nsfw_anatomy_line(body_type_details)

    if subtype_info:
        body_parts = f"{body_parts}, {subtype_info['name'].lower()} aesthetic, {subtype_info['description'].lower()}"

    subject = body_parts
    if origin:
        subject = f"{subject}, from {origin}"

    base_style = BODY_REF_STYLE_MALE if is_male else BODY_REF_STYLE_FEMALE

    if is_male:
        layout = BODY_REF_LAYOUT.format(
            torso_detail="chest and abs",
            intimate_label="male",
        )
        butt_size = body_type_details.get("butt_size", "muscular") if body_type_details else "muscular"
        rear_angled_panel = (
            f"isolated nude rear view at an angle, "
            f"bent forward back very arched, "
            f"{butt_size} muscular glutes, low rear angle looking up, "
            f"hands raised above head"
        )
        chest_panel = (
            f"isolated nude male torso drawing from collarbone to hips, "
            f"bare chest, defined pecs, abs, navel visible, front view"
        )
        butt_panel = (
            f"isolated nude male butt study, rear view directly behind, "
            f"bent forward with back arched and butt popped out toward viewer, "
            f"{butt_size} muscular glutes, low rear angle looking up"
        )
        intimate_panel = (
            f"isolated nude male intimate study from navel to mid-thigh, "
            f"legs apart, front view, fully nude, extremely detailed"
        )
    else:
        layout = BODY_REF_LAYOUT.format(
            torso_detail="breasts",
            intimate_label="spread-leg",
        )
        breast_size = body_type_details.get("breast_size", "medium") if body_type_details else "medium"
        nipple_size = body_type_details.get("nipple_size", "medium") if body_type_details else "medium"
        butt_size = body_type_details.get("butt_size", "medium round") if body_type_details else "medium round"
        vulva_type = body_type_details.get("vulva_type", "") if body_type_details else ""
        rear_angled_panel = (
            f"isolated nude rear view at an angle, "
            f"bent forward back very arched sensuously, "
            f"{butt_size} butt with natural curvature, low rear angle looking up, "
            f"explicit detail, hands raised above head"
        )
        chest_panel = (
            f"isolated nude female torso drawing from collarbone to hips, "
            f"{breast_size} breasts with {nipple_size} nipples, "
            f"natural breast shape and weight, defined collarbone, "
            f"slight ab definition on toned flat stomach, navel visible, "
            f"medium waist, front view"
        )
        butt_panel = (
            f"isolated nude female butt study, rear view directly behind, "
            f"bent forward sensuously with back arched and butt popped out toward viewer, "
            f"{butt_size} butt with natural curvature, "
            f"asshole and pussy visible from behind between spread cheeks, "
            f"low rear angle looking up, explicit detail, hands spreading ass cheeks"
        )
        intimate_panel = (
            f"isolated nude female intimate study from navel to mid-thigh, "
            f"legs up and spread apart, "
            f"{vulva_type} fully visible and detailed, "
            f"front view, extremely detailed pussy, perfectly drawn anatomically accurate"
            if vulva_type
            else
            "isolated nude female intimate study from navel to mid-thigh, "
            "legs up and spread apart, "
            "tasteful outer labia fully visible and detailed, "
            "front view, extremely detailed pussy, perfectly drawn anatomically accurate"
        )

    face_panel = (
        f"isolated face and neck portrait drawing, "
        f"{expression}, three-quarter angle"
    )

    sections = [
        f"[STYLE] {base_style}, {BODY_REF_PAGE_STYLE}",
        f"[LAYOUT] {layout}",
        f"[SUBJECT] {subject}, all body parts belong to the same single character",
        f"[TOP-LEFT: FACE] {face_panel}",
        f"[TOP-CENTER: REAR ANGLED VIEW] {rear_angled_panel}",
        f"[TOP-RIGHT: CHEST AND TORSO] {chest_panel}",
        f"[BOTTOM-LEFT: BUTT] {butt_panel}",
        f"[BOTTOM-RIGHT: INTIMATE] {intimate_panel}",
        f"[ANATOMY] {anatomy}" if anatomy else "",
        f"[QUALITY] {BODY_REF_QUALITY}",
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
    iconic_features = fighter.get("iconic_features", "")
    if iconic_features and clothing:
        clothing = f"{clothing}, {iconic_features}"
    elif iconic_features:
        clothing = iconic_features

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
