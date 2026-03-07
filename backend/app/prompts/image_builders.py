from app.engine.image_style import get_art_style, get_art_style_tail
from app.engine.fighter_config import _build_body_shape_line, _build_nsfw_anatomy_line, MAKEUP_DESCRIPTIONS, get_adornment_coverage, build_clothing_coverage_annotations
from app.services.grok_image import TIER_PROMPT_KEYS


CHARSHEET_LAYOUT = (
    "character model sheet, character reference sheet, "
    "two full-body views of the exact same character side by side: "
    "front-facing view on the left, "
    "rear view on the right, "
    "consistent outfit across both views, "
    "full body head to toe visible in each panel, "
    "dark background, organized reference sheet layout"
)


def _charsheet_style_base(gender: str = "female") -> str:
    return (
        get_art_style(gender)
        + ", character (strictly over 18 years old), character design reference sheet"
    )


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
        + ", character reference sheet, two consistent views"
    )
    if tier == "nsfw":
        if gender.lower() == "male":
            return (
                get_art_style_tail(gender) + ", "
                "explicit full frontal male nudity, completely naked, muscular physique fully visible, "
                "character reference sheet, two consistent views"
            )
        if skimpiness_level == 1:
            return (
                get_art_style_tail(gender) + ", "
                "topless female nudity, bare breasts visible, "
                "character reference sheet, two consistent views"
            )
        return (
            get_art_style_tail(gender) + ", "
            "explicit full frontal female nudity, completely naked, bare breasts and perfectly drawn bare pussy visible, "
            "character reference sheet, two consistent views"
        )
    return tail_base


def _enrich_body_parts(
    body_parts: str,
    body_type_details: dict | None = None,
    subtype_info: dict | None = None,
    tier: str = "",
    outfit_coverage: dict | None = None,
) -> str:
    if body_type_details:
        shape_line = _build_body_shape_line(body_type_details, tier, outfit_coverage=outfit_coverage)
        if shape_line:
            body_parts = f"{body_parts}, {shape_line}"
    if subtype_info:
        body_parts = f"{body_parts}, {subtype_info['name'].lower()} aesthetic, {subtype_info['description'].lower()}"
    return body_parts


def _build_clothing_part(
    clothing: str,
    iconic_features: str = "",
    primary_outfit_color: str = "",
    tier: str = "sfw",
    skimpiness_level: int = 4,
    outfit_coverage: dict | None = None,
    body_type_details: dict | None = None,
) -> str:
    if primary_outfit_color and clothing:
        clothing = f"{primary_outfit_color} {clothing}"

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

    if outfit_coverage and body_type_details:
        annotations = build_clothing_coverage_annotations(outfit_coverage, body_type_details)
        if annotations and clothing_part:
            clothing_part = f"{clothing_part}, {annotations}"
        elif annotations:
            clothing_part = annotations

    if iconic_features and clothing_part:
        clothing_part = f"{clothing_part}, {iconic_features}"
    elif iconic_features:
        clothing_part = iconic_features
    return clothing_part


def _build_character_desc(
    body_parts: str,
    clothing_part: str = "",
    age: int = 0,
    origin: str = "",
) -> str:
    character_desc = body_parts
    if age:
        character_desc = f"{character_desc}, {age} years old"
    if clothing_part:
        character_desc = f"{character_desc}, {clothing_part}"
    if origin:
        character_desc = f"{character_desc}, from {origin}"
    return character_desc


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
    age: int = 0,
    primary_outfit_color: str = "",
    face_adornment: str = "",
    outfit_coverage: dict | None = None,
) -> dict:
    if not body_parts:
        return {}

    anatomy = ""
    body_parts = _enrich_body_parts(body_parts, body_type_details, subtype_info, tier, outfit_coverage=outfit_coverage)
    if body_type_details and tier in ("nsfw", "barely"):
        anatomy = _build_nsfw_anatomy_line(body_type_details, tier, outfit_coverage=outfit_coverage)

    style = _charsheet_style(gender, tier, skimpiness_level)

    clothing_part = _build_clothing_part(
        clothing, iconic_features, primary_outfit_color, tier, skimpiness_level,
        outfit_coverage=outfit_coverage, body_type_details=body_type_details,
    )

    character_desc = _build_character_desc(body_parts, clothing_part, age, origin)
    if face_adornment and face_adornment.lower() != "none":
        character_desc = f"{character_desc}, wearing {face_adornment}"

    pose_hint = f", {personality_pose}" if personality_pose else ""
    front_view = f"front-facing slightly angled view standing tall{pose_hint}"
    back_view = "rear view standing tall"

    tail = _charsheet_tail(gender, tier, skimpiness_level)

    sections = [
        f"[STYLE] {style}",
        f"[CHARACTER] {character_desc}",
        f"[BODY TYPE] {anatomy}" if anatomy else "",
        f"[VIEWS] {front_view}, {back_view}",
        f"[EXPRESSION] {expression}" if expression else "",
        f"[QUALITY] {tail}",
        f"[BODY TYPE REFERENCE] {anatomy}" if anatomy else "",
    ]
    full = "\n".join(s for s in sections if s)

    return {
        "style": style,
        "layout": CHARSHEET_LAYOUT,
        "body_parts": body_parts,
        "clothing": clothing_part,
        "character_desc": character_desc,
        "front_view": front_view,
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

BODY_REF_STYLE_FEMALE = BODY_REF_STYLE_BASE + ", female character, beautiful and dangerous"

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


MALE_BODY_REF_PAGE_STYLE = (
    "artist anatomy study page, figure drawing body part studies, "
    "separate isolated body part drawings arranged on the page, "
    "three drawings in a row: face on the left, front body in the center, back body on the right, "
    "each body part cropped and drawn individually with space between them, "
    "clean off-white parchment background, organized sketchbook page layout, "
    "absolutely no text no words no letters no labels no captions no watermarks, "
    "drawing guide extremely detailed anatomy"
)

MALE_BODY_REF_LAYOUT = (
    "three separate drawings arranged in a row: "
    "face portrait on the left, "
    "front full-body view in underwear in the center, "
    "rear full-body view in underwear on the right, "
    "clear empty space between each drawing, "
    "each drawing floats independently"
)

MALE_BODY_REF_QUALITY = (
    "hand-painted textures, extremely detailed, anatomical precision, "
    "figure drawing study quality, "
    "each drawing rendered as its own separate floating illustration, "
    "soft even lighting, clean parchment background, "
    "masculine imposing physique, "
    "no text no words no labels no watermarks"
)


def build_body_reference_prompt(
    body_parts: str,
    expression: str,
    gender: str = "female",
    body_type_details: dict | None = None,
    origin: str = "",
    subtype_info: dict | None = None,
    age: int = 0,
    iconic_features: str = "",
    face_adornment: str = "",
    adornment_coverage: str = "",
) -> dict:
    if not body_parts:
        return {}

    is_male = gender.lower() == "male"
    coverage = get_adornment_coverage(adornment_coverage)
    has_adornment = face_adornment and face_adornment.lower() != "none"
    anatomy = ""
    body_parts = _enrich_body_parts(body_parts, body_type_details, subtype_info)
    if body_type_details and not is_male:
        anatomy = _build_nsfw_anatomy_line(body_type_details)

    subject = _build_character_desc(body_parts, age=age, origin=origin)

    base_style = BODY_REF_STYLE_MALE if is_male else BODY_REF_STYLE_FEMALE

    if is_male:
        male_covered = set(coverage["male_covers"])
        chest_build = (
            body_type_details.get("chest_build", "defined pecs")
            if body_type_details
            else "defined pecs"
        )
        muscle_def = (
            body_type_details.get("muscle_definition", "toned and defined")
            if body_type_details
            else "toned and defined"
        )
        shoulder_width = (
            body_type_details.get("shoulder_width", "broad")
            if body_type_details
            else "broad"
        )

        iconic_part = f", {iconic_features}" if iconic_features else ""
        face_detail_parts = []
        if "face_shape" not in male_covered and body_type_details:
            face_detail_parts.append(f"{body_type_details.get('face_shape', 'square jaw')} face")
        if "eye_expression" not in male_covered and body_type_details:
            face_detail_parts.append(f"{body_type_details.get('eye_expression', 'focused intense')} eyes")
        if "facial_hair" not in male_covered and body_type_details:
            face_detail_parts.append(body_type_details.get("facial_hair", "stubble"))
        face_extras_male = f", {', '.join(face_detail_parts)}" if face_detail_parts else ""
        adornment_part = f", wearing {face_adornment}" if has_adornment else ""
        face_panel = (
            f"isolated face and neck portrait drawing, "
            f"{expression}{face_extras_male}, three-quarter angle, masculine features{adornment_part}{iconic_part}"
        )
        front_panel = (
            f"isolated full-body front view in fitted boxer briefs, "
            f"standing tall, {chest_build} chest, {muscle_def} physique, "
            f"{shoulder_width} shoulders, imposing stance, "
            f"detailed muscle definition visible, front view{iconic_part}"
        )
        back_panel = (
            f"isolated full-body rear view in fitted boxer briefs, "
            f"standing tall, {shoulder_width} shoulders, muscular back, "
            f"{muscle_def} physique, rear view{iconic_part}"
        )

        subject_iconic = f", {iconic_features}" if iconic_features else ""
        sections = [
            f"[STYLE] {base_style}, {MALE_BODY_REF_PAGE_STYLE}",
            f"[LAYOUT] {MALE_BODY_REF_LAYOUT}",
            f"[SUBJECT] {subject}{subject_iconic}, all drawings belong to the same single character",
            f"[LEFT: FACE] {face_panel}",
            f"[CENTER: FRONT BODY] {front_panel}",
            f"[RIGHT: BACK BODY] {back_panel}",
            f"[QUALITY] {MALE_BODY_REF_QUALITY}",
        ]
        full = "\n".join(s for s in sections if s)

        return {
            "body_parts": body_parts,
            "expression": expression,
            "anatomy": "",
            "full_prompt": full,
        }

    female_covered = set(coverage["covers_face"])
    layout = BODY_REF_LAYOUT.format(
        torso_detail="breasts",
        intimate_label="spread-leg",
    )
    breast_size = (
        body_type_details.get("breast_size", "medium")
        if body_type_details
        else "medium"
    )
    nipple_size = (
        body_type_details.get("nipple_size", "medium")
        if body_type_details
        else "medium"
    )
    butt_size = (
        body_type_details.get("butt_size", "medium round")
        if body_type_details
        else "medium round"
    )
    vulva_type = (
        body_type_details.get("vulva_type", "") if body_type_details else ""
    )
    waist = (
        body_type_details.get("waist", "medium") if body_type_details else "medium"
    )
    abs_tone = (
        body_type_details.get("abs_tone", "slight definition")
        if body_type_details
        else "slight definition"
    )
    body_fat_pct = (
        body_type_details.get("body_fat_pct", "") if body_type_details else ""
    )
    face_shape = (
        body_type_details.get("face_shape", "") if body_type_details else ""
    )
    eye_shape = (
        body_type_details.get("eye_shape", "") if body_type_details else ""
    )
    makeup_level = (
        body_type_details.get("makeup_level", "") if body_type_details else ""
    )
    makeup_desc = MAKEUP_DESCRIPTIONS.get(makeup_level, makeup_level) if makeup_level else ""
    nose_shape = (
        body_type_details.get("nose_shape", "") if body_type_details else ""
    )
    lip_shape = (
        body_type_details.get("lip_shape", "") if body_type_details else ""
    )
    brow_shape = (
        body_type_details.get("brow_shape", "") if body_type_details else ""
    )
    cheekbone = (
        body_type_details.get("cheekbone", "") if body_type_details else ""
    )
    jawline = (
        body_type_details.get("jawline", "") if body_type_details else ""
    )

    rear_angled_panel = (
        f"isolated nude rear view at an angle, "
        f"bent forward back arched casually, "
        f"{butt_size} butt with natural curvature, "
        f"hands raised above head, profile"
    )
    vulva_detail = f", {vulva_type} fully visible and detailed" if vulva_type else ""
    body_fat_detail = f", {body_fat_pct} body fat" if body_fat_pct else ""
    chest_panel = (
        f"isolated nude female torso drawing from collarbone to thighs, "
        f"{breast_size} breasts with {nipple_size} nipples, "
        f"natural breast shape and weight, defined collarbone, "
        f"{abs_tone} abs/core on toned flat stomach{body_fat_detail}, navel visible, "
        f"{waist} waist{vulva_detail}, front view"
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
        else "isolated nude female intimate study from navel to mid-thigh, "
        "legs up and spread apart, "
        "tasteful outer labia fully visible and detailed, "
        "front view, extremely detailed pussy, perfectly drawn anatomically accurate"
    )

    iconic_part = f", {iconic_features}" if iconic_features else ""
    face_details = []
    if face_shape and "face_shape" not in female_covered:
        face_details.append(f"{face_shape} face shape")
    if jawline and "jawline" not in female_covered:
        face_details.append(f"{jawline} jaw")
    if cheekbone and "cheekbone" not in female_covered:
        face_details.append(f"{cheekbone} cheekbones")
    if eye_shape and "eye_shape" not in female_covered:
        face_details.append(f"{eye_shape} eyes")
    if brow_shape and "brow_shape" not in female_covered:
        face_details.append(f"{brow_shape} brows")
    if nose_shape and "nose_shape" not in female_covered:
        face_details.append(f"{nose_shape} nose")
    if lip_shape and "lip_shape" not in female_covered:
        face_details.append(f"{lip_shape} lips")
    if makeup_desc and "makeup_level" not in female_covered:
        face_details.append(f"{makeup_desc}")
    face_extras = f", {', '.join(face_details)}" if face_details else ""
    adornment_part = f", wearing {face_adornment}" if has_adornment else ""
    face_panel = (
        f"isolated face and neck portrait drawing, "
        f"{expression}{face_extras}, three-quarter angle{adornment_part}{iconic_part}"
    )

    if body_type_details:
        anatomy = _build_nsfw_anatomy_line(body_type_details)

    subject_iconic = f", {iconic_features}" if iconic_features else ""
    sections = [
        f"[STYLE] {base_style}, {BODY_REF_PAGE_STYLE}",
        f"[LAYOUT] {layout}",
        f"[SUBJECT] {subject}{subject_iconic}, all body parts belong to the same single character",
        f"[TOP-LEFT: FACE] {face_panel}",
        f"[TOP-CENTER: REAR ANGLED VIEW] {rear_angled_panel}",
        f"[TOP-RIGHT: CHEST AND CROTCH STANDING] {chest_panel}",
        f"[BOTTOM-LEFT: BUTT] {butt_panel}",
        f"[BOTTOM-RIGHT: INTIMATE] {intimate_panel}",
        f"[BODY TYPE] {anatomy}" if anatomy else "",
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


PORTRAIT_STYLE = (
    "high quality illustration, single character portrait, upper body shot, "
    "dark background, professional character art, detailed face and expression, dangerous fighter"
)

HEADSHOT_STYLE = (
    "high quality illustration, extreme close-up headshot, zoomed in on face, "
    "face fills the entire frame, cropped tight from forehead to chin, "
    "dramatic dark moody background with subtle gradient, cinematic lighting from the side, "
    "fighting game character select screen, intense stare toward viewer, "
    "sharp focus on face, shallow depth of field, professional character art"
)


def build_portrait_prompt(
    body_parts: str,
    clothing_sfw: str,
    expression: str,
    gender: str = "female",
    body_type_details: dict | None = None,
    origin: str = "",
    subtype_info: dict | None = None,
    iconic_features: str = "",
    primary_outfit_color: str = "",
    age: int = 0,
    face_adornment: str = "",
    outfit_coverage: dict | None = None,
) -> dict:
    if not body_parts:
        return {}

    style = get_art_style(gender)

    body_parts = _enrich_body_parts(body_parts, body_type_details, subtype_info, tier="sfw", outfit_coverage=outfit_coverage)

    clothing_part = _build_clothing_part(
        clothing_sfw, iconic_features, primary_outfit_color, tier="sfw",
        outfit_coverage=outfit_coverage, body_type_details=body_type_details,
    )

    character_desc = _build_character_desc(body_parts, clothing_part, age, origin)
    if face_adornment and face_adornment.lower() != "none":
        character_desc = f"{character_desc}, wearing {face_adornment}"

    sections = [
        f"[STYLE] {style}, {PORTRAIT_STYLE}",
        f"[CHARACTER] {character_desc}",
        f"[EXPRESSION] {expression}" if expression else "",
        f"[QUALITY] {get_art_style_tail(gender)}, portrait, upper body shot",
    ]
    full = "\n".join(s for s in sections if s)

    return {
        "body_parts": body_parts,
        "clothing": clothing_part,
        "expression": expression,
        "character_desc": character_desc,
        "full_prompt": full,
    }


def build_headshot_prompt(
    body_parts: str,
    expression: str,
    gender: str = "female",
    body_type_details: dict | None = None,
    origin: str = "",
    subtype_info: dict | None = None,
    iconic_features: str = "",
    age: int = 0,
    face_adornment: str = "",
) -> dict:
    if not body_parts:
        return {}

    style = get_art_style(gender)

    body_parts = _enrich_body_parts(body_parts, body_type_details, subtype_info, tier="sfw")

    character_desc = _build_character_desc(body_parts, age=age, origin=origin)
    iconic_part = f", {iconic_features}" if iconic_features else ""
    has_adornment = face_adornment and face_adornment.lower() != "none"
    adornment_part = f", wearing {face_adornment}" if has_adornment else ""

    expression_line = expression
    if has_adornment and expression_line:
        expression_line = f"{expression_line}, wearing {face_adornment}"

    sections = [
        f"[STYLE] {style}, {HEADSHOT_STYLE}",
        f"[CHARACTER] {character_desc}{iconic_part}{adornment_part}, close-up headshot filling the frame",
        f"[EXPRESSION] {expression_line}, intense fighting spirit" if expression_line else "",
        f"[BACKGROUND] dark moody background, deep shadows, subtle dark gradient, cinematic",
        f"[QUALITY] {get_art_style_tail(gender)}, headshot, extreme close-up zoomed in on face, character select screen",
    ]
    full = "\n".join(s for s in sections if s)

    return {
        "body_parts": body_parts,
        "expression": expression,
        "character_desc": character_desc,
        "full_prompt": full,
    }
