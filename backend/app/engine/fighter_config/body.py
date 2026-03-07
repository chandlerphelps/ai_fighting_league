import random

from .archetypes import ARCHETYPE_SUBTYPES, ARCHETYPE_SUBTYPES_MALE
from .body_data import (
    ARCHETYPE_BODY_PROFILE_WEIGHTS,
    ARCHETYPE_BODY_WEIGHTS,
    ARCHETYPE_HEIGHT_RANGES,
    BODY_PROFILES,
    BODY_TRAIT_OPTIONS,
    MAKEUP_DESCRIPTIONS,
    MALE_ARCHETYPE_BODY_PROFILE_WEIGHTS,
    MALE_ARCHETYPE_BODY_WEIGHTS,
    MALE_ARCHETYPE_HEIGHT_RANGES,
    MALE_BODY_PROFILES,
    MALE_BODY_TRAIT_OPTIONS,
)


def _get_subtypes_dict(gender: str = "female") -> dict:
    if gender.lower() == "male":
        return ARCHETYPE_SUBTYPES_MALE
    return ARCHETYPE_SUBTYPES


def _roll_subtype(archetype: str, gender: str = "female") -> dict | None:
    arch = (
        f"The {archetype}"
        if archetype and not archetype.startswith("The ")
        else archetype
    )
    subtypes = _get_subtypes_dict(gender).get(arch, [])
    if not subtypes:
        return None
    return random.choice(subtypes)


def _find_subtype(archetype: str, name: str, gender: str = "female") -> dict | None:
    arch = (
        f"The {archetype}"
        if archetype and not archetype.startswith("The ")
        else archetype
    )
    subtypes = _get_subtypes_dict(gender).get(arch, [])
    for st in subtypes:
        if st["name"].lower() == name.lower():
            return st
    return None


def _weighted_choice(
    category: str,
    archetype: str | None,
    allowed: list[str] | None = None,
    gender: str = "female",
) -> str:
    trait_options = (
        MALE_BODY_TRAIT_OPTIONS if gender.lower() == "male" else BODY_TRAIT_OPTIONS
    )
    body_weights = (
        MALE_ARCHETYPE_BODY_WEIGHTS
        if gender.lower() == "male"
        else ARCHETYPE_BODY_WEIGHTS
    )
    options = allowed if allowed else trait_options[category]
    weights_dict = {}
    if archetype and archetype in body_weights:
        weights_dict = body_weights[archetype].get(category, {})
    if weights_dict:
        weights = [weights_dict.get(opt, 1) for opt in options]
    else:
        weights = [1] * len(options)
    return random.choices(options, weights=weights, k=1)[0]


def _format_height(inches: int) -> str:
    feet = inches // 12
    remaining = inches % 12
    return f"{feet}'{remaining}\""


BODY_FAT_MULTIPLIERS = {
    "lean 12-16%": 0.90,
    "athletic 17-20%": 0.95,
    "fit 21-24%": 1.00,
    "soft 25-30%": 1.08,
}

BREAST_WEIGHT_LBS = {
    "tiny flat-chested": 0,
    "small perky": 1,
    "medium": 3,
    "large heavy": 6,
    "massive oversized": 10,
}

BUTT_WEIGHT_LBS = {
    "tiny tight": 0,
    "medium round": 2,
    "large thick": 5,
    "very large prominent": 9,
}

WAIST_MULTIPLIERS = {
    "narrow": 0.97,
    "medium": 1.00,
    "wide": 1.04,
}


def _derive_weight(height_inches: int, traits: dict) -> int:
    lean_mass = (height_inches - 60) * 3.0 + 105
    bf_mult = BODY_FAT_MULTIPLIERS.get(traits.get("body_fat_pct", ""), 1.0)
    waist_mult = WAIST_MULTIPLIERS.get(traits.get("waist", ""), 1.0)
    base = lean_mass * bf_mult * waist_mult
    base += BREAST_WEIGHT_LBS.get(traits.get("breast_size", ""), 0)
    base += BUTT_WEIGHT_LBS.get(traits.get("butt_size", ""), 0)
    base += random.randint(-3, 3)
    return round(base)


MALE_BODY_FAT_MULTIPLIERS = {
    "shredded 8-12%": 0.92,
    "athletic 12-18%": 1.00,
    "average 18-25%": 1.10,
    "heavy 25-35%": 1.25,
    "obese 35-45%": 1.45,
}

MALE_BUILD_WEIGHT_BONUS = {
    "skinny and bony": -15,
    "lean and wiry": -5,
    "athletic and cut": 0,
    "thick and powerful": 15,
    "heavy and massive": 35,
}

MALE_WAIST_MULTIPLIERS = {
    "skinny and narrow": 0.93,
    "narrow v-taper": 0.97,
    "medium": 1.00,
    "soft belly": 1.06,
    "big gut": 1.14,
}


def _derive_male_weight(height_inches: int, traits: dict) -> int:
    lean_mass = (height_inches - 60) * 5.0 + 140
    bf_mult = MALE_BODY_FAT_MULTIPLIERS.get(traits.get("body_fat_pct", ""), 1.0)
    waist_mult = MALE_WAIST_MULTIPLIERS.get(traits.get("waist", ""), 1.0)
    base = lean_mass * bf_mult * waist_mult
    base += MALE_BUILD_WEIGHT_BONUS.get(traits.get("build_type", ""), 0)
    base += random.randint(-5, 5)
    return round(base)


def _roll_body_profile(
    archetype: str | None,
    subtype_bias: dict | None = None,
    gender: str = "female",
) -> str:
    profile_weights_source = (
        MALE_ARCHETYPE_BODY_PROFILE_WEIGHTS
        if gender.lower() == "male"
        else ARCHETYPE_BODY_PROFILE_WEIGHTS
    )
    profiles_source = MALE_BODY_PROFILES if gender.lower() == "male" else BODY_PROFILES
    profile_weights = dict(profile_weights_source.get(archetype, {}))
    if profile_weights:
        if subtype_bias:
            for key, adj in subtype_bias.items():
                if key in profile_weights:
                    profile_weights[key] = max(1, profile_weights[key] + adj)
        profiles = list(profile_weights.keys())
        weights = [profile_weights[p] for p in profiles]
    else:
        profiles = list(profiles_source.keys())
        weights = [1] * len(profiles)
    return random.choices(profiles, weights=weights, k=1)[0]


def _roll_body_traits(
    archetype: str | None,
    subtype: dict | None = None,
    gender: str = "female",
) -> dict:
    arch = (
        f"The {archetype}"
        if archetype and not archetype.startswith("The ")
        else archetype
    )

    subtype_bias = subtype.get("body_profile_bias") if subtype else None
    is_male = gender.lower() == "male"
    profile = _roll_body_profile(arch, subtype_bias=subtype_bias, gender=gender)

    if is_male:
        allowed = MALE_BODY_PROFILES[profile]
        height_range = MALE_ARCHETYPE_HEIGHT_RANGES.get(arch, (69, 76))
        height_inches = random.randint(height_range[0], height_range[1])

        traits = {
            "height_inches": height_inches,
            "body_profile": profile,
            "build_type": _weighted_choice(
                "build_type", arch, allowed.get("build_type"), gender="male"
            ),
            "muscle_definition": _weighted_choice(
                "muscle_definition",
                arch,
                allowed.get("muscle_definition"),
                gender="male",
            ),
            "body_fat_pct": _weighted_choice(
                "body_fat_pct", arch, allowed.get("body_fat_pct"), gender="male"
            ),
            "shoulder_width": _weighted_choice(
                "shoulder_width", arch, allowed.get("shoulder_width"), gender="male"
            ),
            "chest_build": _weighted_choice(
                "chest_build", arch, allowed.get("chest_build"), gender="male"
            ),
            "waist": _weighted_choice(
                "waist", arch, allowed.get("waist"), gender="male"
            ),
            "face_shape": _weighted_choice("face_shape", arch, gender="male"),
            "eye_expression": _weighted_choice("eye_expression", arch, gender="male"),
            "facial_hair": _weighted_choice("facial_hair", arch, gender="male"),
        }

        if subtype:
            traits["subtype"] = subtype["name"]

        weight_lbs = _derive_male_weight(height_inches, traits)
        traits["height"] = _format_height(height_inches)
        traits["weight"] = f"{weight_lbs} lbs"

        return traits

    allowed = BODY_PROFILES[profile]
    height_range = ARCHETYPE_HEIGHT_RANGES.get(arch, (59, 71))
    height_inches = random.randint(height_range[0], height_range[1])

    traits = {
        "height_inches": height_inches,
        "body_profile": profile,
        "waist": _weighted_choice("waist", arch, allowed.get("waist")),
        "abs_tone": _weighted_choice("abs_tone", arch, allowed.get("abs_tone")),
        "body_fat_pct": _weighted_choice(
            "body_fat_pct", arch, allowed.get("body_fat_pct")
        ),
        "butt_size": _weighted_choice("butt_size", arch, allowed.get("butt_size")),
        "breast_size": _weighted_choice(
            "breast_size", arch, allowed.get("breast_size")
        ),
        "face_shape": _weighted_choice("face_shape", arch),
        "eye_shape": _weighted_choice("eye_shape", arch),
        "eye_expression": _weighted_choice("eye_expression", arch),
        "nose_shape": _weighted_choice("nose_shape", arch),
        "lip_shape": _weighted_choice("lip_shape", arch),
        "brow_shape": _weighted_choice("brow_shape", arch),
        "cheekbone": _weighted_choice("cheekbone", arch),
        "jawline": _weighted_choice("jawline", arch),
        "makeup_level": _weighted_choice("makeup_level", arch),
        "nipple_size": _weighted_choice("nipple_size", arch),
        "vulva_type": _weighted_choice("vulva_type", arch),
    }

    if subtype:
        traits["subtype"] = subtype["name"]

    weight_lbs = _derive_weight(height_inches, traits)
    traits["height"] = _format_height(height_inches)
    traits["weight"] = f"{weight_lbs} lbs"

    return traits


ADORNMENT_COVERAGE = {
    "full_face": {
        "covers_face": ["face_shape", "eye_shape", "eye_expression", "nose_shape", "lip_shape", "brow_shape", "cheekbone", "jawline", "makeup_level"],
        "male_covers": ["face_shape", "eye_expression", "facial_hair"],
        "covers_hair": False,
    },
    "upper_face": {
        "covers_face": ["eye_shape", "eye_expression", "brow_shape"],
        "male_covers": ["eye_expression"],
        "covers_hair": False,
    },
    "lower_face": {
        "covers_face": ["nose_shape", "lip_shape"],
        "male_covers": ["facial_hair"],
        "covers_hair": False,
    },
    "eyes_only": {
        "covers_face": ["eye_shape", "eye_expression"],
        "male_covers": ["eye_expression"],
        "covers_hair": False,
    },
    "head_covering": {
        "covers_face": [],
        "male_covers": [],
        "covers_hair": True,
    },
    "face_paint": {
        "covers_face": [],
        "male_covers": [],
        "covers_hair": False,
    },
    "decorative": {
        "covers_face": [],
        "male_covers": [],
        "covers_hair": False,
    },
    "none": {
        "covers_face": [],
        "male_covers": [],
        "covers_hair": False,
    },
}


def get_adornment_coverage(category: str) -> dict:
    return ADORNMENT_COVERAGE.get(category, ADORNMENT_COVERAGE["none"])


ABS_TONE_SHORT = {
    "soft with no definition": "soft",
    "slight definition": "toned",
    "toned and defined": "defined",
    "ripped and shredded": "shredded",
}

TRAIT_LABELS = {
    "breast_size": lambda v: f"{v} breasts",
    "nipple_size": lambda v: f"{v} nipples",
    "vulva_type": lambda v: v,
    "butt_size": lambda v: f"{v} butt",
    "waist": lambda v: f"{v} waist",
    "abs_tone": lambda v: f"{ABS_TONE_SHORT.get(v, v)} midsection",
    "chest_build": lambda v: f"{v} chest",
    "muscle_definition": lambda v: f"{v} build",
    "shoulder_width": lambda v: f"{v} shoulders",
}


INTIMATE_TRAITS = {"nipple_size", "vulva_type"}


def build_clothing_coverage_annotations(outfit_coverage: dict, traits: dict, tier: str = "sfw") -> str:
    skip = INTIMATE_TRAITS if tier != "nsfw" else set()
    annotations = []
    for trait_key, state in outfit_coverage.items():
        if trait_key in skip:
            continue
        val = traits.get(trait_key)
        if not val:
            continue
        label_fn = TRAIT_LABELS.get(trait_key)
        if not label_fn:
            continue
        readable = label_fn(val)
        if state == "transparent":
            annotations.append(f"{readable} visible through outfit")
        elif state == "form-fitted":
            annotations.append(f"outfit hugging {readable}")
        elif state == "half-obscured":
            annotations.append(f"partially revealing {readable}")
    return ", ".join(annotations)


def _build_body_directive(traits: dict, face_adornment: str = "", adornment_coverage: str = "") -> str:
    if "chest_build" in traits:
        return _build_male_body_directive(traits, face_adornment, adornment_coverage)
    coverage = get_adornment_coverage(adornment_coverage)
    covered = set(coverage["covers_face"])
    makeup_desc = MAKEUP_DESCRIPTIONS.get(
        traits["makeup_level"], traits["makeup_level"]
    )
    lines = [
        "BODY TYPE DIRECTIVE (you MUST incorporate these exact physical traits):",
        f"- Build: {traits.get('body_profile', 'Average')}",
        f"- Height: {traits['height']}",
        f"- Weight: {traits['weight']}",
        f"- Breast size: {traits['breast_size']}",
        f"- Waist: {traits['waist']}",
        f"- Abs/core: {traits['abs_tone']}",
        f"- Body fat: {traits['body_fat_pct']}",
        f"- Butt: {traits['butt_size']}",
    ]
    if "face_shape" not in covered:
        lines.append(f"- Face shape: {traits['face_shape']}")
    if "eye_shape" not in covered and "eye_expression" not in covered:
        lines.append(f"- Eyes: {traits['eye_shape']}, {traits.get('eye_expression', 'piercing')} gaze")
    elif "eye_shape" not in covered:
        lines.append(f"- Eye shape: {traits['eye_shape']}")
    elif "eye_expression" not in covered:
        lines.append(f"- Eye expression: {traits.get('eye_expression', 'piercing')} gaze")
    if "nose_shape" not in covered:
        lines.append(f"- Nose: {traits.get('nose_shape', 'straight narrow')}")
    if "lip_shape" not in covered:
        lines.append(f"- Lips: {traits.get('lip_shape', 'full pouty')}")
    if "brow_shape" not in covered:
        lines.append(f"- Brows: {traits.get('brow_shape', 'high arched')}")
    if "cheekbone" not in covered:
        lines.append(f"- Cheekbones: {traits.get('cheekbone', 'soft subtle')}")
    if "jawline" not in covered:
        lines.append(f"- Jawline: {traits.get('jawline', 'soft rounded')}")
    if "makeup_level" not in covered:
        lines.append(f"- Makeup: {traits['makeup_level']} — {makeup_desc}")
    if face_adornment and face_adornment.lower() != "none":
        lines.append(f"- Face/head adornment: {face_adornment} (MUST be visible in all images)")
    lines.append("")
    lines.append("The height and weight are EXACT — use these values directly.")
    lines.append("Work the other traits naturally into image_prompt_body_parts and image_prompt_expression.")
    lines.append(
        "IMPORTANT: Interpret ALL facial and body traits through a DANGEROUS yet ATTRACTIVE lens. "
        "Every combination should result in a beautiful, lethal-looking character — "
        "someone stunning but clearly capable of killing you."
    )
    return "\n".join(lines)


def _build_male_body_directive(traits: dict, face_adornment: str = "", adornment_coverage: str = "") -> str:
    coverage = get_adornment_coverage(adornment_coverage)
    covered = set(coverage["male_covers"])
    lines = [
        "BODY TYPE DIRECTIVE (you MUST incorporate these exact physical traits):",
        f"- Build: {traits.get('body_profile', 'Athletic')} — {traits.get('build_type', 'athletic and cut')}",
        f"- Height: {traits['height']}",
        f"- Weight: {traits['weight']}",
        f"- Muscle definition: {traits.get('muscle_definition', 'toned and defined')}",
        f"- Shoulders: {traits.get('shoulder_width', 'broad')}",
        f"- Chest: {traits.get('chest_build', 'defined pecs')}",
        f"- Waist: {traits.get('waist', 'medium')}",
        f"- Body fat: {traits.get('body_fat_pct', 'average 18-25%')}",
    ]
    if "face_shape" not in covered and "eye_expression" not in covered:
        lines.append(f"- Face: {traits.get('face_shape', 'square jaw')}, {traits.get('eye_expression', 'focused intense')} eyes")
    elif "face_shape" not in covered:
        lines.append(f"- Face shape: {traits.get('face_shape', 'square jaw')}")
    elif "eye_expression" not in covered:
        lines.append(f"- Eye expression: {traits.get('eye_expression', 'focused intense')}")
    if "facial_hair" not in covered:
        lines.append(f"- Facial hair: {traits.get('facial_hair', 'stubble')}")
    if face_adornment and face_adornment.lower() != "none":
        lines.append(f"- Face/head adornment: {face_adornment} (MUST be visible in all images)")
    lines.append("")
    lines.append("The height and weight are EXACT — use these values directly.")
    lines.append("Work the other traits naturally into image_prompt_body_parts and image_prompt_expression.")
    lines.append(
        "IMPORTANT: Interpret ALL traits through a DANGEROUS, IMPOSING lens. "
        "Every combination should result in a threatening, confident character who looks like "
        "someone you would cross the street to avoid."
    )
    return "\n".join(lines)


def _height_adjective(inches: int) -> str:
    if inches <= 61:
        return "petite"
    if inches <= 64:
        return "short"
    if inches <= 67:
        return "average height"
    return "tall"


def _apply_coverage(trait_name: str, trait_text: str, outfit_coverage: dict | None) -> str | None:
    if not outfit_coverage:
        return trait_text
    state = outfit_coverage.get(trait_name, "exposed")
    if state == "covered":
        return None
    if state == "form-fitted":
        return f"{trait_text} shape visible under outfit"
    if state == "transparent":
        return f"{trait_text} visible through outfit"
    if state == "half-obscured":
        return f"partially visible {trait_text}"
    return trait_text


def _build_body_shape_line(traits: dict, tier: str = "", outfit_coverage: dict | None = None) -> str:
    if "chest_build" in traits:
        parts = []
        chest = _apply_coverage("chest_build", f"{traits['chest_build']} chest", outfit_coverage)
        if chest:
            parts.append(chest)
        shoulders = _apply_coverage("shoulder_width", f"{traits.get('shoulder_width', 'broad')} shoulders", outfit_coverage)
        if shoulders:
            parts.append(shoulders)
        return ", ".join(parts) if parts else ""
    if tier == "sfw" and not outfit_coverage:
        covered = " (covered)"
    else:
        covered = ""
    height_inches = traits.get("height_inches")
    if height_inches:
        feet = height_inches // 12
        remaining = height_inches % 12
        adj = _height_adjective(height_inches)
        height_part = f"{adj} {feet}'{remaining}\", "
    else:
        height_part = ""
    parts = []
    breast_text = _apply_coverage("breast_size", f"{traits['breast_size']} breasts{covered}", outfit_coverage)
    if breast_text:
        parts.append(breast_text)
    butt_text = _apply_coverage("butt_size", f"{traits['butt_size']} butt", outfit_coverage)
    if butt_text:
        parts.append(butt_text)
    return f"{height_part}{', '.join(parts)}" if parts else height_part.rstrip(", ")


def _build_nsfw_anatomy_line(traits: dict, tier: str = "nsfw", outfit_coverage: dict | None = None) -> str:
    if "chest_build" in traits:
        parts = []
        chest = _apply_coverage("chest_build", f"{traits['chest_build']} chest", outfit_coverage)
        if chest:
            parts.append(chest)
        muscle = _apply_coverage("muscle_definition", f"{traits.get('muscle_definition', 'toned and defined')} build", outfit_coverage)
        if muscle:
            parts.append(muscle)
        shoulders = _apply_coverage("shoulder_width", f"{traits.get('shoulder_width', 'broad')} shoulders", outfit_coverage)
        if shoulders:
            parts.append(shoulders)
        return ", ".join(parts) if parts else ""
    if tier == "barely":
        parts = []
        breast = _apply_coverage("breast_size", f"{traits['breast_size']} breasts", outfit_coverage)
        if breast:
            parts.append(breast)
        butt = _apply_coverage("butt_size", f"{traits['butt_size']} butt", outfit_coverage)
        if butt:
            parts.append(butt)
        return ", ".join(parts) if parts else ""
    parts = []
    breast = _apply_coverage("breast_size", f"{traits['breast_size']} breasts", outfit_coverage)
    if breast:
        parts.append(breast)
    nipple = _apply_coverage("nipple_size", f"{traits['nipple_size']} nipples", outfit_coverage)
    if nipple:
        parts.append(nipple)
    butt = _apply_coverage("butt_size", f"{traits['butt_size']} butt", outfit_coverage)
    if butt:
        parts.append(butt)
    vulva = _apply_coverage("vulva_type", traits['vulva_type'], outfit_coverage)
    if vulva:
        parts.append(vulva)
    return ", ".join(parts) if parts else ""
