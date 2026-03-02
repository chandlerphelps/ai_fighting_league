import json
import random
from pathlib import Path


def load_outfit_options(config) -> dict:
    path = Path(config.data_dir) / "outfit_options.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _parse_outfit_item(item) -> tuple[str, str]:
    if isinstance(item, dict):
        return item.get("name", ""), str(item.get("skimpiness_level", ""))
    return str(item), ""


def _skimpiness_matches(item_level_str: str, fighter_level: int | None) -> bool:
    if not item_level_str or fighter_level is None:
        return True
    item_level_str = item_level_str.strip()
    if "-" in item_level_str:
        parts = item_level_str.split("-")
        try:
            return int(parts[0]) <= fighter_level <= int(parts[1])
        except (ValueError, IndexError):
            return True
    try:
        return int(item_level_str) == fighter_level
    except ValueError:
        return True


def filter_outfit_options(
    options_for_tier: dict,
    skimpiness_level: int | None = None,
) -> dict:
    result = {}
    for key in ["tops", "bottoms", "one_pieces"]:
        full_list = list(options_for_tier.get(key, []))
        if skimpiness_level is not None:
            full_list = [
                item
                for item in full_list
                if _skimpiness_matches(_parse_outfit_item(item)[1], skimpiness_level)
            ]
        if not full_list:
            full_list = list(options_for_tier.get(key, []))
        keep_count = min(3, len(full_list))
        sampled = random.sample(full_list, keep_count)
        random.shuffle(sampled)
        result[key] = [_parse_outfit_item(item)[0] for item in sampled]

    return result


ARCHETYPES_FEMALE = [
    "The Siren",
    "The Witch",
    "The Viper",
    "The Prodigy",
    "The Doll",
    "The Huntress",
    "The Empress",
    "The Experiment",
]

ARCHETYPES_MALE = [
    "The Brute",
    "The Veteran",
    "The Monster",
    "The Technician",
    "The Wildcard",
    "The Mystic",
    "The Prodigy",
    "The Experiment",
]

BODY_TRAIT_OPTIONS = {
    "waist": ["narrow", "medium", "wide"],
    "abs_tone": [
        "soft with no definition",
        "slight definition",
        "toned and defined",
        "ripped and shredded",
    ],
    "body_fat_pct": ["lean 12-16%", "athletic 17-20%", "fit 21-24%", "soft 25-30%"],
    "butt_size": ["small tight", "medium round", "large full", "very large prominent"],
    "face_shape": [
        "sharp angular",
        "soft round",
        "heart-shaped",
        "oval",
        "diamond",
    ],
    "eye_shape": [
        "almond",
        "round",
        "hooded",
        "doe",
        "cat-like",
    ],
    "makeup_level": ["bare-faced", "light", "moderate", "heavy"],
    "breast_size": ["barely there", "small perky", "medium", "large", "very large"],
    "nipple_size": ["small pert", "medium", "perky pointed", "large puffy"],
    "vulva_type": [
        "tucked pussy, small hidden labia",
        "tasteful outer labia",
        "compact petite tight pussy",
        "visible labia minora peeking out",
    ],
}

BODY_PROFILES = {
    "Petite": {
        "body_fat_pct": ["lean 12-16%", "athletic 17-20%"],
        "abs_tone": ["slight definition", "toned and defined"],
        "waist": ["narrow"],
        "breast_size": ["barely there", "small perky", "medium"],
        "butt_size": ["small tight", "medium round"],
    },
    "Slim": {
        "body_fat_pct": ["lean 12-16%", "athletic 17-20%"],
        "abs_tone": ["soft with no definition", "slight definition", "toned and defined"],
        "waist": ["narrow", "medium"],
        "breast_size": ["barely there", "small perky", "medium"],
        "butt_size": ["small tight", "medium round"],
    },
    "Athletic": {
        "body_fat_pct": ["lean 12-16%", "athletic 17-20%"],
        "abs_tone": ["toned and defined", "ripped and shredded"],
        "waist": ["narrow", "medium"],
        "breast_size": ["small perky", "medium", "large"],
        "butt_size": ["medium round", "large full"],
    },
    "Curvy": {
        "body_fat_pct": ["athletic 17-20%", "fit 21-24%"],
        "abs_tone": ["soft with no definition", "slight definition", "toned and defined"],
        "waist": ["narrow", "medium"],
        "breast_size": ["medium", "large", "very large"],
        "butt_size": ["medium round", "large full", "very large prominent"],
    },
}

ARCHETYPE_BODY_PROFILE_WEIGHTS = {
    "The Siren": {"Petite": 5, "Slim": 20, "Athletic": 20, "Curvy": 55},
    "The Witch": {"Petite": 20, "Slim": 30, "Athletic": 20, "Curvy": 30},
    "The Viper": {"Petite": 10, "Slim": 30, "Athletic": 42, "Curvy": 18},
    "The Prodigy": {"Petite": 35, "Slim": 33, "Athletic": 22, "Curvy": 10},
    "The Doll": {"Petite": 35, "Slim": 25, "Athletic": 12, "Curvy": 28},
    "The Huntress": {"Petite": 5, "Slim": 20, "Athletic": 50, "Curvy": 25},
    "The Empress": {"Petite": 5, "Slim": 15, "Athletic": 25, "Curvy": 55},
    "The Experiment": {"Petite": 15, "Slim": 22, "Athletic": 30, "Curvy": 33},
}

MAKEUP_DESCRIPTIONS = {
    "bare-faced": "natural beauty, minimal or zero makeup",
    "light": "subtle enhancement, lip tint, light mascara",
    "moderate": "polished look, foundation, defined eyes, lipstick",
    "heavy": "full glam, smoky eyes, contoured, bold lip",
}

ARCHETYPE_HEIGHT_RANGES = {
    "The Siren": (62, 69),
    "The Witch": (60, 67),
    "The Viper": (62, 68),
    "The Prodigy": (59, 65),
    "The Doll": (59, 64),
    "The Huntress": (65, 71),
    "The Empress": (65, 70),
    "The Experiment": (60, 69),
}

ARCHETYPE_BODY_WEIGHTS = {
    "The Siren": {
        "breast_size": {"barely there": 2, "small perky": 5, "medium": 20, "large": 48, "very large": 25},
        "body_fat_pct": {
            "lean 12-16%": 2,
            "athletic 17-20%": 28,
            "fit 21-24%": 48,
            "soft 25-30%": 22,
        },
        "makeup_level": {
            "bare-faced": 3,
            "light": 35,
            "moderate": 47,
            "heavy": 15,
        },
        "abs_tone": {
            "soft with no definition": 22,
            "slight definition": 48,
            "toned and defined": 28,
            "ripped and shredded": 2,
        },
        "butt_size": {
            "small tight": 15,
            "medium round": 40,
            "large full": 30,
            "very large prominent": 15,
        },
        "waist": {"narrow": 40, "medium": 45, "wide": 15},
    },
    "The Witch": {
        "breast_size": {"barely there": 8, "small perky": 20, "medium": 32, "large": 27, "very large": 13},
        "body_fat_pct": {
            "lean 12-16%": 8,
            "athletic 17-20%": 30,
            "fit 21-24%": 35,
            "soft 25-30%": 27,
        },
        "makeup_level": {
            "bare-faced": 5,
            "light": 35,
            "moderate": 42,
            "heavy": 18,
        },
        "abs_tone": {
            "soft with no definition": 32,
            "slight definition": 42,
            "toned and defined": 24,
            "ripped and shredded": 2,
        },
        "butt_size": {
            "small tight": 20,
            "medium round": 40,
            "large full": 30,
            "very large prominent": 10,
        },
        "waist": {"narrow": 35, "medium": 45, "wide": 20},
    },
    "The Viper": {
        "breast_size": {"barely there": 10, "small perky": 25, "medium": 37, "large": 22, "very large": 6},
        "body_fat_pct": {
            "lean 12-16%": 15,
            "athletic 17-20%": 45,
            "fit 21-24%": 32,
            "soft 25-30%": 8,
        },
        "makeup_level": {
            "bare-faced": 10,
            "light": 35,
            "moderate": 40,
            "heavy": 15,
        },
        "abs_tone": {
            "soft with no definition": 8,
            "slight definition": 30,
            "toned and defined": 52,
            "ripped and shredded": 10,
        },
        "butt_size": {
            "small tight": 25,
            "medium round": 45,
            "large full": 23,
            "very large prominent": 7,
        },
        "waist": {"narrow": 50, "medium": 40, "wide": 10},
    },
    "The Prodigy": {
        "breast_size": {"barely there": 15, "small perky": 33, "medium": 32, "large": 16, "very large": 4},
        "body_fat_pct": {
            "lean 12-16%": 20,
            "athletic 17-20%": 48,
            "fit 21-24%": 25,
            "soft 25-30%": 7,
        },
        "makeup_level": {
            "bare-faced": 25,
            "light": 40,
            "moderate": 30,
            "heavy": 5,
        },
        "abs_tone": {
            "soft with no definition": 8,
            "slight definition": 22,
            "toned and defined": 58,
            "ripped and shredded": 12,
        },
        "butt_size": {
            "small tight": 35,
            "medium round": 40,
            "large full": 20,
            "very large prominent": 5,
        },
        "waist": {"narrow": 45, "medium": 45, "wide": 10},
    },
    "The Doll": {
        "breast_size": {"barely there": 12, "small perky": 28, "medium": 30, "large": 22, "very large": 8},
        "body_fat_pct": {
            "lean 12-16%": 8,
            "athletic 17-20%": 28,
            "fit 21-24%": 42,
            "soft 25-30%": 22,
        },
        "makeup_level": {
            "bare-faced": 8,
            "light": 37,
            "moderate": 42,
            "heavy": 13,
        },
        "abs_tone": {
            "soft with no definition": 27,
            "slight definition": 43,
            "toned and defined": 28,
            "ripped and shredded": 2,
        },
        "butt_size": {
            "small tight": 20,
            "medium round": 40,
            "large full": 30,
            "very large prominent": 10,
        },
        "waist": {"narrow": 45, "medium": 40, "wide": 15},
    },
    "The Huntress": {
        "breast_size": {"barely there": 8, "small perky": 20, "medium": 37, "large": 27, "very large": 8},
        "body_fat_pct": {
            "lean 12-16%": 18,
            "athletic 17-20%": 47,
            "fit 21-24%": 27,
            "soft 25-30%": 8,
        },
        "makeup_level": {
            "bare-faced": 20,
            "light": 40,
            "moderate": 32,
            "heavy": 8,
        },
        "abs_tone": {
            "soft with no definition": 8,
            "slight definition": 25,
            "toned and defined": 52,
            "ripped and shredded": 15,
        },
        "butt_size": {
            "small tight": 25,
            "medium round": 40,
            "large full": 25,
            "very large prominent": 10,
        },
        "waist": {"narrow": 35, "medium": 50, "wide": 15},
    },
    "The Empress": {
        "breast_size": {"barely there": 1, "small perky": 5, "medium": 24, "large": 45, "very large": 25},
        "body_fat_pct": {
            "lean 12-16%": 2,
            "athletic 17-20%": 22,
            "fit 21-24%": 44,
            "soft 25-30%": 32,
        },
        "makeup_level": {
            "bare-faced": 3,
            "light": 32,
            "moderate": 47,
            "heavy": 18,
        },
        "abs_tone": {
            "soft with no definition": 27,
            "slight definition": 43,
            "toned and defined": 28,
            "ripped and shredded": 2,
        },
        "butt_size": {
            "small tight": 15,
            "medium round": 40,
            "large full": 30,
            "very large prominent": 15,
        },
        "waist": {"narrow": 25, "medium": 45, "wide": 30},
    },
    "The Experiment": {
        "breast_size": {"barely there": 8, "small perky": 18, "medium": 28, "large": 28, "very large": 18},
        "body_fat_pct": {
            "lean 12-16%": 12,
            "athletic 17-20%": 40,
            "fit 21-24%": 30,
            "soft 25-30%": 18,
        },
        "makeup_level": {
            "bare-faced": 12,
            "light": 37,
            "moderate": 38,
            "heavy": 13,
        },
        "abs_tone": {
            "soft with no definition": 15,
            "slight definition": 30,
            "toned and defined": 43,
            "ripped and shredded": 12,
        },
        "butt_size": {
            "small tight": 25,
            "medium round": 40,
            "large full": 25,
            "very large prominent": 20,
        },
        "waist": {"narrow": 30, "medium": 45, "wide": 25},
    },
}


def _weighted_choice(
    category: str, archetype: str | None, allowed: list[str] | None = None
) -> str:
    options = allowed if allowed else BODY_TRAIT_OPTIONS[category]
    weights_dict = {}
    if archetype and archetype in ARCHETYPE_BODY_WEIGHTS:
        weights_dict = ARCHETYPE_BODY_WEIGHTS[archetype].get(category, {})
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
    "barely there": 0,
    "small perky": 1,
    "medium": 3,
    "large": 6,
    "very large": 10,
}

BUTT_WEIGHT_LBS = {
    "small tight": 0,
    "medium round": 2,
    "large full": 5,
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


def _roll_body_profile(archetype: str | None) -> str:
    profile_weights = ARCHETYPE_BODY_PROFILE_WEIGHTS.get(archetype, {})
    if profile_weights:
        profiles = list(profile_weights.keys())
        weights = [profile_weights[p] for p in profiles]
    else:
        profiles = list(BODY_PROFILES.keys())
        weights = [1] * len(profiles)
    return random.choices(profiles, weights=weights, k=1)[0]


def _roll_body_traits(archetype: str | None) -> dict:
    arch = (
        f"The {archetype}"
        if archetype and not archetype.startswith("The ")
        else archetype
    )

    profile = _roll_body_profile(arch)
    allowed = BODY_PROFILES[profile]

    height_range = ARCHETYPE_HEIGHT_RANGES.get(arch, (59, 71))
    height_inches = random.randint(height_range[0], height_range[1])

    traits = {
        "height_inches": height_inches,
        "body_profile": profile,
        "waist": _weighted_choice("waist", arch, allowed.get("waist")),
        "abs_tone": _weighted_choice("abs_tone", arch, allowed.get("abs_tone")),
        "body_fat_pct": _weighted_choice("body_fat_pct", arch, allowed.get("body_fat_pct")),
        "butt_size": _weighted_choice("butt_size", arch, allowed.get("butt_size")),
        "breast_size": _weighted_choice("breast_size", arch, allowed.get("breast_size")),
        "face_shape": _weighted_choice("face_shape", arch),
        "eye_shape": _weighted_choice("eye_shape", arch),
        "makeup_level": _weighted_choice("makeup_level", arch),
        "nipple_size": _weighted_choice("nipple_size", arch),
        "vulva_type": _weighted_choice("vulva_type", arch),
    }

    weight_lbs = _derive_weight(height_inches, traits)
    traits["height"] = _format_height(height_inches)
    traits["weight"] = f"{weight_lbs} lbs"

    return traits


def _build_body_directive(traits: dict) -> str:
    makeup_desc = MAKEUP_DESCRIPTIONS.get(
        traits["makeup_level"], traits["makeup_level"]
    )
    return (
        "BODY TYPE DIRECTIVE (you MUST incorporate these exact physical traits):\n"
        f"- Build: {traits.get('body_profile', 'Average')}\n"
        f"- Height: {traits['height']}\n"
        f"- Weight: {traits['weight']}\n"
        f"- Breast size: {traits['breast_size']}\n"
        f"- Waist: {traits['waist']}\n"
        f"- Abs/core: {traits['abs_tone']}\n"
        f"- Body fat: {traits['body_fat_pct']}\n"
        f"- Butt: {traits['butt_size']}\n"
        f"- Face: {traits['face_shape']}, {traits['eye_shape']} eyes\n"
        f"- Makeup: {traits['makeup_level']} — {makeup_desc}\n"
        "\nThe height and weight are EXACT — use these values directly.\n"
        "Work the other traits naturally into image_prompt_body_parts and image_prompt_expression.\n"
        "IMPORTANT: Interpret ALL facial and body traits through an attractive lens. "
        "Every combination should result in a beautiful, appealing character."
    )


def _build_body_shape_line(traits: dict) -> str:
    return f"{traits['breast_size']} breasts, " f"{traits['butt_size']} butt"


def _build_nsfw_anatomy_line(traits: dict) -> str:
    return (
        f"{traits['breast_size']} breasts, "
        f"{traits['nipple_size']} nipples, "
        f"{traits['butt_size']} butt, "
        f"{traits['vulva_type']}"
    )


SKIMPINESS_LEVELS = {
    1: {
        "sfw_label": "Covered & Composed",
        "sfw_skin_pct": "15-25",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Conservative — only face, hands, and forearms visible. Full coverage everywhere else.",
        "barely_label": "Flirty",
        "barely_skin_pct": "45-55",
        "barely_hard_rules": "No nipples, no areola, no genitalia directly visible. Cameltoe, sideboob, underbutt are OK. If using sheer or transparent fabric, nipples and anatomy MUST be visible through it — transparency means you can see through it.",
        "barely_guidance": "Suggestive — form-fitting silhouette, cleavage, legs showing. Covered but clearly sexy.",
        "nsfw_adjective": "Scandalous",
        "nsfw_hard_rules": "Topless — bare breasts fully visible. Bottoms stay on but must be ultra-sexy: thongs, micro-bikini bottoms, strappy lingerie, or sheer panties. Show off legs and hips.",
        "nsfw_description": "Topless and unapologetic. Sultry, confident posing. Bottoms are barely-there and designed to tease — maximum skin, minimum fabric below the waist.",
        "nsfw_nudity_level": "topless",
    },
    2: {
        "sfw_label": "Sporty & Attractive",
        "sfw_skin_pct": "30-45",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Moderate — bare arms, some leg, a peek of midriff. Sporty and attractive.",
        "barely_label": "Risqué",
        "barely_skin_pct": "60-70",
        "barely_hard_rules": "No nipples, no areola, no genitalia directly visible (but seen through transparent fabric is okay). Cameltoe, sideboob, underbutt are OK. If using sheer or transparent fabric, nipples and anatomy MUST be visible through it — transparency means you can see through it.",
        "barely_guidance": "Risqué — significant skin exposure, sideboob, underbutt. Clearly pushing boundaries.",
        "nsfw_adjective": "Confident",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, pussy visible.",
        "nsfw_description": "Confident pin-up energy. Completely nude, no bottom garment. Pussy fully visible.",
        "nsfw_nudity_level": "full",
    },
    3: {
        "sfw_label": "Bold",
        "sfw_skin_pct": "50-65",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Bold — shows skin confidently but still looks like a real outfit.",
        "barely_label": "Scandalous",
        "barely_skin_pct": "75-85",
        "barely_hard_rules": "No full nipples, but areola peeking out from micro pasties is OK. No genitalia directly visible (but seen through transparent fabric is okay). Cameltoe, sideboob, underbutt are OK. If using sheer or transparent fabric, nipples and anatomy MUST be visible through it — transparency means you can see through it.",
        "barely_guidance": "Scandalous — most skin exposed, coverage is minimal. Micro clothing only. Areola peeking out from tiny pasties is encouraged.",
        "nsfw_adjective": "Tease",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, pussy visible. Teasing posture — a finger resting playfully near her clit or cupping a breast or running her hands along her body - teasing sensually.",
        "nsfw_description": "Teasing, playful energy. Anatomy on display with flirty self-touching.",
        "nsfw_nudity_level": "full",
    },
    4: {
        "sfw_label": "Daring",
        "sfw_skin_pct": "60-75",
        "sfw_hard_rules": "No nipples, no genitalia. Sideboob hints are OK at this level.",
        "sfw_guidance": "Daring — the outfit is minimal but intentional. Looks great and happens to show skin.",
        "barely_label": "Extreme",
        "barely_skin_pct": "99",
        "barely_hard_rules": "No full nipples, but areola peeking out from micro pasties is OK. No genitalia directly visible (but seen through transparent fabric is okay). Cameltoe, sideboob, underbutt are OK. If using sheer or transparent fabric, nipples and anatomy MUST be visible through it — transparency means you can see through it.",
        "barely_guidance": "Extreme — micro pasties with areola peeking out and a tiny nail-sized strip over the clit. Areola exposure is expected at this level.",
        "nsfw_adjective": "Pornographic",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, legs apart or spread, pussy fully displayed. Explicit posing.",
        "nsfw_description": "Maximum explicit posing. Pierced nipples allowed or tiny subtle clit piercings allowed (tasteful small rings only). Spreading, legs open, erotic emphasis on genitalia. Nothing left to imagination.",
        "nsfw_nudity_level": "full",
    },
}


def _roll_skimpiness(weights: list[int] | None) -> int:
    if not weights or len(weights) != 4:
        weights = [10, 30, 38, 22]
    total = sum(weights)
    if total <= 0:
        weights = [10, 30, 38, 22]
        total = 100
    normalized = [w / total for w in weights]
    return random.choices([1, 2, 3, 4], weights=normalized, k=1)[0]
