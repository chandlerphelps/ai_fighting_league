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
    exotic_one_pieces: list[str] | None = None,
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

    if exotic_one_pieces:
        extras = random.sample(exotic_one_pieces, min(2, len(exotic_one_pieces)))
        result["exotic_one_pieces"] = extras

    return result


def load_exotic_outfit_options(config) -> list[dict]:
    path = Path(config.data_dir) / "exotic_outfit_options.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []


def filter_exotic_for_fighter(
    exotics: list[dict],
    archetype: str = "",
    subtype: str = "",
    tier: str = "sfw",
    skimpiness_level: int = 2,
) -> list[str]:
    matched = []
    for item in exotics:
        if archetype in item.get("archetypes", []) or subtype in item.get(
            "subtypes", []
        ):
            tier_vars = item.get("variations", {}).get(tier, [])
            candidates = [
                _parse_outfit_item(v)[0]
                for v in tier_vars
                if _skimpiness_matches(_parse_outfit_item(v)[1], skimpiness_level)
            ]
            if not candidates and tier_vars:
                candidates = [_parse_outfit_item(tier_vars[0])[0]]
            matched.extend(candidates)
    return matched


SKIMPINESS_LEVELS = {
    1: {
        "sfw_label": "Covered",
        "sfw_skin_pct": "5-20",
        "sfw_hard_rules": "No nipples, no nipple outline, no genitalia, no underboob, no sideboob, no cameltoe. Near-total skin coverage.",
        "sfw_guidance": "Near-total coverage — arms, legs, torso all covered. Only hands, neck, and face exposed. She looks ready to fight.",
        "barely_label": "Flirty",
        "barely_skin_pct": "30-65",
        "barely_hard_rules": "Nipples MUST be fully covered. Groin MUST be fully covered. No exceptions.",
        "barely_guidance": "Flirty — midriff, cleavage, legs showing. Sexy but covered where it counts.",
        "nsfw_adjective": "Scandalous",
        "nsfw_hard_rules": "Topless — bare breasts fully visible. Bottoms stay on but must be ultra-sexy: thongs, micro-bikini bottoms, strappy lingerie, or sheer panties. Show off legs and hips.",
        "nsfw_description": "Topless and unapologetic. Sultry, confident posing. Bottoms are barely-there and designed to tease — maximum skin, minimum fabric below the waist.",
        "nsfw_nudity_level": "topless",
    },
    2: {
        "sfw_label": "Modest",
        "sfw_skin_pct": "5-30",
        "sfw_hard_rules": "No nipples, no nipple outline, no genitalia, no underboob, no sideboob, no cameltoe. Full coverage.",
        "sfw_guidance": "Mostly covered — some forearm, lower-leg, or neckline exposure allowed. The outfit is practical and combat-ready.",
        "barely_label": "Risqué",
        "barely_skin_pct": "30-75",
        "barely_hard_rules": "Nipples MUST be fully covered. Groin MUST be fully covered. Sideboob and underbutt OK.",
        "barely_guidance": "Risqué — significant skin exposure, sideboob, underbutt. Pushing boundaries but key areas stay covered.",
        "nsfw_adjective": "Confident",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, pussy visible.",
        "nsfw_description": "Confident pin-up energy. Completely nude, no bottom garment. Pussy fully visible.",
        "nsfw_nudity_level": "full",
    },
    3: {
        "sfw_label": "Revealing",
        "sfw_skin_pct": "20-50",
        "sfw_hard_rules": "No bare nipples, no nipple outline, no genitalia, no cameltoe, no sideboob. Cleavage and midriff OK.",
        "sfw_guidance": "Moderate skin showing — exposed midriff, cleavage, bare arms and shoulders, thigh-high slits. Still has substantial garment pieces but deliberately shows skin.",
        "barely_label": "Scandalous",
        "barely_skin_pct": "35-80",
        "barely_hard_rules": "Nipples MUST be covered (pasties or fabric). Groin MUST be covered. Areola edge peeking is OK but nipple itself stays hidden.",
        "barely_guidance": "Scandalous — most skin exposed, micro clothing only. Pasties and minimal bottoms but everything important stays covered.",
        "nsfw_adjective": "Tease",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, pussy visible. Teasing posture — a finger resting playfully near her clit or cupping a breast or running her hands along her body - teasing sensually.",
        "nsfw_description": "Teasing, playful energy. Anatomy on display with flirty self-touching.",
        "nsfw_nudity_level": "full",
    },
    4: {
        "sfw_label": "Skimpy",
        "sfw_skin_pct": "40-65",
        "sfw_hard_rules": "No bare nipples, no genitalia. Sideboob hints OK. Strategic cutouts, bare midriff, bare legs expected.",
        "sfw_guidance": "Maximum skin for SFW — crop tops, short shorts, cutout panels, bare backs, thigh windows. Coverage is minimal but nipples and groin stay hidden.",
        "barely_label": "Extreme",
        "barely_skin_pct": "60-99",
        "barely_hard_rules": "Nipples MUST be covered (micro pasties minimum). Groin MUST be covered (micro strip or patch minimum). Areola edge visible is OK.",
        "barely_guidance": "Extreme — near-total skin exposure. Micro pasties and tiny bottom coverage. As revealing as possible while keeping nipples and groin covered.",
        "nsfw_adjective": "Pornographic",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, legs apart or spread, pussy fully displayed. Explicit posing.",
        "nsfw_description": "Maximum explicit posing. Pierced nipples allowed or tiny subtle clit piercings allowed (tasteful small rings only). Spreading, legs open, erotic emphasis on genitalia. Nothing left to imagination.",
        "nsfw_nudity_level": "full",
    },
}

MALE_SKIMPINESS_LEVELS = {
    1: {
        "sfw_label": "Battle Ready",
        "sfw_skin_pct": "15-30",
        "sfw_hard_rules": "Full coverage. Tactical and imposing. No bare chest required.",
        "sfw_guidance": "Covered and dangerous — tactical gear, armor, jackets, full coverage combat attire. Think military, mercenary, or gladiator in full kit.",
        "barely_label": "Stripped Down",
        "barely_skin_pct": "40-55",
        "barely_hard_rules": "Shirtless or open-chested. Pants/shorts must stay on. Scars and muscle definition should be visible.",
        "barely_guidance": "Shirtless and imposing — bare chest, dog tags, wraps, combat pants. The body IS the intimidation.",
    },
    2: {
        "sfw_label": "Combat Ready",
        "sfw_skin_pct": "25-40",
        "sfw_hard_rules": "No full nudity. Arms and some chest can show. Athletic and dangerous.",
        "sfw_guidance": "Athletic — tank tops, open vests, sleeveless shirts, combat shorts. Muscular and ready to fight.",
        "barely_label": "Bare-Knuckle",
        "barely_skin_pct": "50-65",
        "barely_hard_rules": "Shirtless. Pants/shorts/trunks stay on. Muscle and scars on full display.",
        "barely_guidance": "Shirtless warrior — fight trunks, wraps, boots. Raw physicality on display.",
    },
    3: {
        "sfw_label": "Aggressive",
        "sfw_skin_pct": "35-50",
        "sfw_hard_rules": "No full nudity. Confident skin exposure. Arms, chest hints, legs showing.",
        "sfw_guidance": "Bold — cut-off shirts, open jackets, short shorts. Confident and dangerous.",
        "barely_label": "Gladiator",
        "barely_skin_pct": "55-70",
        "barely_hard_rules": "Shirtless. Minimal bottoms acceptable — fight trunks, compression shorts, gladiator skirt. Muscle and scars visible.",
        "barely_guidance": "Arena warrior — maximum muscle on display, minimal clothing, gladiatorial energy.",
    },
    4: {
        "sfw_label": "Intimidating",
        "sfw_skin_pct": "40-55",
        "sfw_hard_rules": "No full nudity. Significant skin showing but still clothed. Imposing presence.",
        "sfw_guidance": "Maximum intimidation while clothed — open vest, no shirt underneath, low-slung pants. Every scar visible.",
        "barely_label": "Primal",
        "barely_skin_pct": "65-80",
        "barely_hard_rules": "Shirtless. Minimal coverage — fight trunks, loincloth, or compression shorts only. Primal warrior energy.",
        "barely_guidance": "Primal — barely clothed, maximum muscle, tribal/warrior energy. The outfit is scars, tattoos, and attitude.",
    },
}


FIT_STYLES = {
    "skin-tight": {
        "description": "Catsuits, compression suits, bodysuits. Every contour visible.",
        "weights_by_skimpiness": {1: 10, 2: 15, 3: 25, 4: 30},
    },
    "form-fitted": {
        "description": "Athletic wear that follows the body's shape but isn't painted on.",
        "weights_by_skimpiness": {1: 30, 2: 35, 3: 25, 4: 15},
    },
    "loose": {
        "description": "Baggy pants, oversized jackets, flowing fabrics, draped wraps.",
        "weights_by_skimpiness": {1: 30, 2: 20, 3: 10, 4: 5},
    },
    "layered": {
        "description": "Fitted base with loose outer layer — jacket, vest, hoodie over sports bra.",
        "weights_by_skimpiness": {1: 20, 2: 20, 3: 15, 4: 10},
    },
    "structured": {
        "description": "Rigid pieces — armor plates, corsets, tailored jackets.",
        "weights_by_skimpiness": {1: 10, 2: 10, 3: 25, 4: 40},
    },
}


TRANSPARENCY_OPTIONS = {
    "opaque": 70,
    "some mesh/sheer panels": 30,
}


SKIN_POINT_MAP = {
    0: "0-10",
    1: "5-20",
    2: "15-30",
    3: "25-40",
    4: "35-55",
    5: "50-70",
    6: "65-85",
    7: "80-95",
    8: "95-99",
}

TIGHTNESS_POINT_MAP = {
    0: "loose",
    1: "layered",
    2: "form-fitted",
    3: "skin-tight",
    4: "body-paint",
}

TRANSPARENCY_POINT_MAP = {
    0: "opaque",
    1: "some mesh/sheer panels",
    2: "significant sheer/transparent sections",
    3: "fully transparent/sheer",
}

EXPOSURE_BUDGETS = {
    ("sfw", 1): {"budget": 3, "skin_max": 1, "tightness_max": 2, "transparency_max": 1},
    ("sfw", 2): {"budget": 4, "skin_max": 2, "tightness_max": 3, "transparency_max": 1},
    ("sfw", 3): {"budget": 6, "skin_max": 4, "tightness_max": 3, "transparency_max": 2},
    ("sfw", 4): {"budget": 7, "skin_max": 5, "tightness_max": 3, "transparency_max": 2},
    ("barely", 1): {"budget": 6, "skin_max": 4, "tightness_max": 3, "transparency_max": 2},
    ("barely", 2): {"budget": 8, "skin_max": 5, "tightness_max": 3, "transparency_max": 2},
    ("barely", 3): {"budget": 10, "skin_max": 7, "tightness_max": 4, "transparency_max": 3},
    ("barely", 4): {"budget": 13, "skin_max": 8, "tightness_max": 4, "transparency_max": 3},
}


def _roll_exposure_budget(tier: str, skimpiness_level: int) -> dict:
    config = EXPOSURE_BUDGETS.get((tier, skimpiness_level))
    if not config:
        config = EXPOSURE_BUDGETS.get(("sfw", 2))

    budget = config["budget"]
    skin_max = min(config["skin_max"], max(SKIN_POINT_MAP.keys()))
    tight_max = min(config["tightness_max"], max(TIGHTNESS_POINT_MAP.keys()))
    trans_max = min(config["transparency_max"], max(TRANSPARENCY_POINT_MAP.keys()))

    skin = random.randint(0, skin_max)
    tight = random.randint(0, tight_max)
    trans = random.randint(0, trans_max)

    total = skin + tight + trans
    if total > budget:
        dims = [("skin", skin, skin_max), ("tight", tight, tight_max), ("trans", trans, trans_max)]
        random.shuffle(dims)
        overflow = total - budget
        reduced = {}
        for name, val, _ in dims:
            cut = min(val, overflow)
            reduced[name] = val - cut
            overflow -= cut
        skin = reduced["skin"]
        tight = reduced["tight"]
        trans = reduced["trans"]

    return {
        "skin_pct": SKIN_POINT_MAP[skin],
        "fit_style": TIGHTNESS_POINT_MAP[tight],
        "transparency": TRANSPARENCY_POINT_MAP[trans],
        "skin_points": skin,
        "tightness_points": tight,
        "transparency_points": trans,
    }


def _roll_fit_style(skimpiness_level: int) -> str:
    styles = list(FIT_STYLES.keys())
    weights = [FIT_STYLES[s]["weights_by_skimpiness"].get(skimpiness_level, 20) for s in styles]
    return random.choices(styles, weights=weights, k=1)[0]


def _roll_transparency() -> str:
    options = list(TRANSPARENCY_OPTIONS.keys())
    weights = list(TRANSPARENCY_OPTIONS.values())
    return random.choices(options, weights=weights, k=1)[0]


OUTFIT_COLOR_PALETTE = [
    "Crimson Red",
    "Royal Blue",
    "Midnight Black",
    "Pure White",
    "Emerald Green",
    "Gold",
    "Silver",
    "Deep Purple",
    "Hot Pink",
    "Orange",
    "Teal",
    "Burgundy",
    "Navy Blue",
    "Forest Green",
    "Copper",
    "Lavender",
    "Scarlet",
    "Ice Blue",
    "Charcoal",
    "Rose",
    "Bronze",
    "Jade",
    "Ivory",
    "Electric Yellow",
]


OUTFIT_COVERABLE_TRAITS_FEMALE = ["breast_size", "nipple_size", "vulva_type", "butt_size", "waist", "abs_tone"]
OUTFIT_COVERABLE_TRAITS_MALE = ["chest_build", "muscle_definition", "shoulder_width", "waist"]
VALID_COVERAGE_STATES = {"exposed", "transparent", "form-fitted", "half-obscured", "covered"}


def validate_outfit_coverage(raw: dict, gender: str) -> dict:
    valid_keys = OUTFIT_COVERABLE_TRAITS_MALE if gender.lower() == "male" else OUTFIT_COVERABLE_TRAITS_FEMALE
    return {
        k: v for k, v in raw.items()
        if k in valid_keys and v in VALID_COVERAGE_STATES and v != "exposed"
    }


def _roll_skimpiness(weights: list[int] | None) -> int:
    if not weights or len(weights) != 4:
        weights = [30, 35, 22, 13]
    total = sum(weights)
    if total <= 0:
        weights = [30, 35, 22, 13]
        total = 100
    normalized = [w / total for w in weights]
    return random.choices([1, 2, 3, 4], weights=normalized, k=1)[0]
