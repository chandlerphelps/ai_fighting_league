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


ARCHETYPE_DESCRIPTIONS = {
    "The Siren": "weaponized beauty, seduction, charm",
    "The Witch": "mysticism, dark arts, supernatural",
    "The Viper": "poison, subterfuge, dirty tricks",
    "The Prodigy": "young technical genius, speed and precision",
    "The Doll": "deceptive innocence, psychological warfare",
    "The Huntress": "predatory, relentless, speed-based",
    "The Empress": "dominance through authority and manipulation",
    "The Experiment": "cybernetics, body modification, science",
    "The Demon": "infernal power, dark seduction, hellfire",
    "The Assassin": "lethal precision, stealth, silent killing",
    "The Nymph": "nature magic, fae trickery, ethereal allure",
    "The Brute": "raw physical power, intimidation",
    "The Veteran": "battle-scarred, tactical, experienced",
    "The Monster": "inhuman size and strength, terrifying",
    "The Technician": "precise, methodical, strategic",
    "The Wildcard": "unpredictable, chaotic",
    "The Mystic": "supernatural warrior, ancient traditions",
}


ARCHETYPES_FEMALE = [
    "The Siren",
    "The Witch",
    "The Viper",
    "The Prodigy",
    "The Doll",
    "The Huntress",
    "The Empress",
    "The Experiment",
    "The Demon",
    "The Assassin",
    "The Nymph",
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
        "tucked pussy, small labia",
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
        "abs_tone": [
            "soft with no definition",
            "slight definition",
            "toned and defined",
        ],
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
        "abs_tone": [
            "soft with no definition",
            "slight definition",
            "toned and defined",
        ],
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
    "The Demon": {"Petite": 15, "Slim": 25, "Athletic": 20, "Curvy": 40},
    "The Assassin": {"Petite": 20, "Slim": 30, "Athletic": 40, "Curvy": 10},
    "The Nymph": {"Petite": 30, "Slim": 35, "Athletic": 15, "Curvy": 20},
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
    "The Demon": (62, 69),
    "The Assassin": (61, 67),
    "The Nymph": (58, 66),
}

ARCHETYPE_BODY_WEIGHTS = {
    "The Siren": {
        "breast_size": {
            "barely there": 2,
            "small perky": 7,
            "medium": 23,
            "large": 50,
            "very large": 18,
        },
        "body_fat_pct": {
            "lean 12-16%": 5,
            "athletic 17-20%": 32,
            "fit 21-24%": 53,
            "soft 25-30%": 10,
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
            "small tight": 18,
            "medium round": 43,
            "large full": 33,
            "very large prominent": 6,
        },
        "waist": {"narrow": 40, "medium": 45, "wide": 15},
    },
    "The Witch": {
        "breast_size": {
            "barely there": 9,
            "small perky": 22,
            "medium": 34,
            "large": 27,
            "very large": 8,
        },
        "body_fat_pct": {
            "lean 12-16%": 11,
            "athletic 17-20%": 35,
            "fit 21-24%": 40,
            "soft 25-30%": 14,
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
            "small tight": 22,
            "medium round": 42,
            "large full": 32,
            "very large prominent": 4,
        },
        "waist": {"narrow": 35, "medium": 45, "wide": 20},
    },
    "The Viper": {
        "breast_size": {
            "barely there": 10,
            "small perky": 26,
            "medium": 38,
            "large": 23,
            "very large": 3,
        },
        "body_fat_pct": {
            "lean 12-16%": 16,
            "athletic 17-20%": 47,
            "fit 21-24%": 34,
            "soft 25-30%": 3,
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
            "small tight": 26,
            "medium round": 47,
            "large full": 25,
            "very large prominent": 2,
        },
        "waist": {"narrow": 50, "medium": 40, "wide": 10},
    },
    "The Prodigy": {
        "breast_size": {
            "barely there": 15,
            "small perky": 33,
            "medium": 33,
            "large": 17,
            "very large": 2,
        },
        "body_fat_pct": {
            "lean 12-16%": 21,
            "athletic 17-20%": 50,
            "fit 21-24%": 26,
            "soft 25-30%": 3,
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
            "small tight": 36,
            "medium round": 41,
            "large full": 21,
            "very large prominent": 2,
        },
        "waist": {"narrow": 45, "medium": 45, "wide": 10},
    },
    "The Doll": {
        "breast_size": {
            "barely there": 12,
            "small perky": 29,
            "medium": 31,
            "large": 23,
            "very large": 5,
        },
        "body_fat_pct": {
            "lean 12-16%": 11,
            "athletic 17-20%": 32,
            "fit 21-24%": 47,
            "soft 25-30%": 10,
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
            "small tight": 22,
            "medium round": 42,
            "large full": 32,
            "very large prominent": 4,
        },
        "waist": {"narrow": 45, "medium": 40, "wide": 15},
    },
    "The Huntress": {
        "breast_size": {
            "barely there": 8,
            "small perky": 21,
            "medium": 38,
            "large": 28,
            "very large": 5,
        },
        "body_fat_pct": {
            "lean 12-16%": 19,
            "athletic 17-20%": 49,
            "fit 21-24%": 29,
            "soft 25-30%": 3,
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
            "small tight": 27,
            "medium round": 42,
            "large full": 27,
            "very large prominent": 4,
        },
        "waist": {"narrow": 35, "medium": 50, "wide": 15},
    },
    "The Empress": {
        "breast_size": {
            "barely there": 2,
            "small perky": 7,
            "medium": 26,
            "large": 47,
            "very large": 18,
        },
        "body_fat_pct": {
            "lean 12-16%": 6,
            "athletic 17-20%": 28,
            "fit 21-24%": 50,
            "soft 25-30%": 16,
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
            "small tight": 18,
            "medium round": 43,
            "large full": 33,
            "very large prominent": 6,
        },
        "waist": {"narrow": 25, "medium": 45, "wide": 30},
    },
    "The Experiment": {
        "breast_size": {
            "barely there": 8,
            "small perky": 20,
            "medium": 30,
            "large": 30,
            "very large": 12,
        },
        "body_fat_pct": {
            "lean 12-16%": 14,
            "athletic 17-20%": 44,
            "fit 21-24%": 34,
            "soft 25-30%": 8,
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
            "small tight": 28,
            "medium round": 42,
            "large full": 22,
            "very large prominent": 8,
        },
        "waist": {"narrow": 30, "medium": 45, "wide": 25},
    },
    "The Demon": {
        "breast_size": {
            "barely there": 4,
            "small perky": 10,
            "medium": 24,
            "large": 44,
            "very large": 18,
        },
        "body_fat_pct": {
            "lean 12-16%": 8,
            "athletic 17-20%": 30,
            "fit 21-24%": 50,
            "soft 25-30%": 12,
        },
        "makeup_level": {
            "bare-faced": 3,
            "light": 12,
            "moderate": 40,
            "heavy": 45,
        },
        "abs_tone": {
            "soft with no definition": 20,
            "slight definition": 45,
            "toned and defined": 30,
            "ripped and shredded": 5,
        },
        "butt_size": {
            "small tight": 9,
            "medium round": 31,
            "large full": 48,
            "very large prominent": 12,
        },
        "waist": {"narrow": 35, "medium": 45, "wide": 20},
    },
    "The Assassin": {
        "breast_size": {
            "barely there": 15,
            "small perky": 35,
            "medium": 33,
            "large": 15,
            "very large": 2,
        },
        "body_fat_pct": {
            "lean 12-16%": 35,
            "athletic 17-20%": 46,
            "fit 21-24%": 18,
            "soft 25-30%": 1,
        },
        "makeup_level": {
            "bare-faced": 35,
            "light": 40,
            "moderate": 20,
            "heavy": 5,
        },
        "abs_tone": {
            "soft with no definition": 3,
            "slight definition": 15,
            "toned and defined": 52,
            "ripped and shredded": 30,
        },
        "butt_size": {
            "small tight": 31,
            "medium round": 44,
            "large full": 23,
            "very large prominent": 2,
        },
        "waist": {"narrow": 50, "medium": 40, "wide": 10},
    },
    "The Nymph": {
        "breast_size": {
            "barely there": 10,
            "small perky": 31,
            "medium": 36,
            "large": 19,
            "very large": 4,
        },
        "body_fat_pct": {
            "lean 12-16%": 12,
            "athletic 17-20%": 34,
            "fit 21-24%": 44,
            "soft 25-30%": 10,
        },
        "makeup_level": {
            "bare-faced": 30,
            "light": 45,
            "moderate": 20,
            "heavy": 5,
        },
        "abs_tone": {
            "soft with no definition": 25,
            "slight definition": 45,
            "toned and defined": 25,
            "ripped and shredded": 5,
        },
        "butt_size": {
            "small tight": 17,
            "medium round": 43,
            "large full": 35,
            "very large prominent": 5,
        },
        "waist": {"narrow": 45, "medium": 40, "wide": 15},
    },
}


ARCHETYPE_SUBTYPES = {
    "The Siren": [
        {
            "name": "Chanteuse",
            "description": "Hypnotic voice, musical seduction",
            "body_profile_bias": {"Slim": +25, "Curvy": -20, "Athletic": -5},
        },
        {
            "name": "Femme Fatale",
            "description": "Deadly beauty, lethal allure",
            "body_profile_bias": {"Curvy": +20, "Athletic": +10, "Petite": -30},
        },
        {
            "name": "Temptress",
            "description": "Overt seduction, irresistible magnetism",
            "body_profile_bias": {"Curvy": +25, "Slim": -15, "Petite": -10},
        },
        {
            "name": "Enchantress",
            "description": "Mystical charm, spellbinding presence",
            "body_profile_bias": {"Slim": +20, "Athletic": -10, "Curvy": -10},
        },
        {
            "name": "Muse",
            "description": "Inspires obsession, ethereal beauty",
            "body_profile_bias": {"Petite": +25, "Slim": +15, "Curvy": -35},
        },
    ],
    "The Witch": [
        {
            "name": "Hexcaster",
            "description": "Curse specialist, hex-focused combat",
            "body_profile_bias": {"Slim": +20, "Athletic": -10, "Curvy": -10},
        },
        {
            "name": "Oracle",
            "description": "Sees the future, fights with foreknowledge",
            "body_profile_bias": {"Petite": +20, "Slim": +10, "Curvy": -25},
        },
        {
            "name": "Necromancer",
            "description": "Death magic, drains life force",
            "body_profile_bias": {"Slim": +25, "Petite": +10, "Curvy": -30},
        },
        {
            "name": "Alchemist",
            "description": "Potions, transmutation, chemical warfare",
            "body_profile_bias": {"Athletic": +20, "Petite": -15, "Slim": -5},
        },
        {
            "name": "Coven Mother",
            "description": "Ritual power, commands dark authority",
            "body_profile_bias": {"Curvy": +25, "Slim": -15, "Petite": -10},
        },
    ],
    "The Viper": [
        {
            "name": "Poisoner",
            "description": "Toxic specialist, venomous attacks",
            "body_profile_bias": {"Slim": +20, "Curvy": -15, "Athletic": -5},
        },
        {
            "name": "Schemer",
            "description": "Manipulative mastermind, always three steps ahead",
            "body_profile_bias": {"Athletic": +15, "Curvy": +10, "Petite": -25},
        },
        {
            "name": "Blackmailer",
            "description": "Leverages secrets, psychological torment",
            "body_profile_bias": {"Curvy": +25, "Athletic": -15, "Petite": -10},
        },
        {
            "name": "Saboteur",
            "description": "Disables opponents before the fight begins",
            "body_profile_bias": {"Athletic": +25, "Curvy": -20, "Slim": -5},
        },
        {
            "name": "Infiltrator",
            "description": "Master of disguise, strikes from within",
            "body_profile_bias": {
                "Slim": +15,
                "Petite": +10,
                "Curvy": -15,
                "Athletic": -10,
            },
        },
    ],
    "The Prodigy": [
        {
            "name": "Wunderkind",
            "description": "Impossibly talented youth",
            "body_profile_bias": {
                "Petite": +25,
                "Slim": +10,
                "Curvy": -20,
                "Athletic": -15,
            },
        },
        {
            "name": "Savant",
            "description": "One transcendent skill, narrow brilliance",
            "body_profile_bias": {"Slim": +25, "Athletic": -15, "Curvy": -10},
        },
        {
            "name": "Phenom",
            "description": "Natural athlete, explosive raw talent",
            "body_profile_bias": {"Athletic": +30, "Petite": -20, "Slim": -10},
        },
        {
            "name": "Virtuoso",
            "description": "Technical perfection, flawless execution",
            "body_profile_bias": {
                "Slim": +20,
                "Athletic": +10,
                "Curvy": -20,
                "Petite": -10,
            },
        },
        {
            "name": "Ingenue",
            "description": "Deceptively innocent, underestimated",
            "body_profile_bias": {
                "Petite": +30,
                "Curvy": +5,
                "Athletic": -25,
                "Slim": -10,
            },
        },
    ],
    "The Doll": [
        {
            "name": "Porcelain",
            "description": "Fragile appearance, eerie perfection",
            "body_profile_bias": {
                "Petite": +25,
                "Slim": +10,
                "Athletic": -25,
                "Curvy": -10,
            },
        },
        {
            "name": "Marionette",
            "description": "Moves like she's controlled by strings",
            "body_profile_bias": {"Slim": +25, "Petite": +5, "Curvy": -25},
        },
        {
            "name": "Ragdoll",
            "description": "Limp and loose until she strikes",
            "body_profile_bias": {"Slim": +15, "Curvy": +10, "Athletic": -20},
        },
        {
            "name": "China Doll",
            "description": "Delicate beauty hiding sharp edges",
            "body_profile_bias": {
                "Petite": +20,
                "Slim": +15,
                "Curvy": -25,
                "Athletic": -10,
            },
        },
        {
            "name": "Wind-Up",
            "description": "Mechanical precision, clockwork violence",
            "body_profile_bias": {"Athletic": +25, "Curvy": -15, "Petite": -10},
        },
    ],
    "The Huntress": [
        {
            "name": "Stalker",
            "description": "Patient tracker, wears opponents down",
            "body_profile_bias": {"Athletic": +15, "Slim": +10, "Curvy": -20},
        },
        {
            "name": "Apex",
            "description": "Top predator, dominant aggression",
            "body_profile_bias": {"Athletic": +25, "Curvy": +5, "Petite": -25},
        },
        {
            "name": "Trapper",
            "description": "Sets up opponents, controls the cage",
            "body_profile_bias": {"Slim": +20, "Petite": +10, "Athletic": -20},
        },
        {
            "name": "Bloodhound",
            "description": "Relentless pursuit, never loses the scent",
            "body_profile_bias": {"Athletic": +20, "Curvy": -10, "Slim": -10},
        },
        {
            "name": "Falconer",
            "description": "Precision strikes from distance",
            "body_profile_bias": {
                "Slim": +25,
                "Petite": +5,
                "Curvy": -20,
                "Athletic": -10,
            },
        },
    ],
    "The Empress": [
        {
            "name": "Sovereign",
            "description": "Born to rule, unquestioned authority",
            "body_profile_bias": {"Curvy": +15, "Athletic": +10, "Petite": -20},
        },
        {
            "name": "Warlord",
            "description": "Conquers through force of will",
            "body_profile_bias": {"Athletic": +30, "Slim": -15, "Petite": -15},
        },
        {
            "name": "Matriarch",
            "description": "Protective fury, motherly wrath",
            "body_profile_bias": {"Curvy": +25, "Petite": -20, "Slim": -5},
        },
        {
            "name": "Tyrant",
            "description": "Rules through fear and dominance",
            "body_profile_bias": {"Athletic": +20, "Curvy": +5, "Petite": -20},
        },
        {
            "name": "Regent",
            "description": "Graceful authority, silk over steel",
            "body_profile_bias": {
                "Slim": +25,
                "Petite": +5,
                "Athletic": -15,
                "Curvy": -15,
            },
        },
    ],
    "The Experiment": [
        {
            "name": "Cyborg",
            "description": "Mechanical augmentation, part machine",
            "body_profile_bias": {"Athletic": +30, "Curvy": -20, "Slim": -10},
        },
        {
            "name": "Chimera",
            "description": "Gene-spliced hybrid, unstable biology",
            "body_profile_bias": {
                "Curvy": +20,
                "Athletic": +5,
                "Slim": -15,
                "Petite": -10,
            },
        },
        {
            "name": "Prototype",
            "description": "First of her kind, untested potential",
            "body_profile_bias": {"Athletic": +20, "Slim": +10, "Petite": -20},
        },
        {
            "name": "Splice",
            "description": "DNA rewritten, evolved beyond human",
            "body_profile_bias": {"Slim": +25, "Petite": +5, "Curvy": -25},
        },
        {
            "name": "Ghost in the Machine",
            "description": "Digital consciousness in synthetic body",
            "body_profile_bias": {"Slim": +20, "Petite": +15, "Curvy": -30},
        },
    ],
    "The Demon": [
        {
            "name": "Succubus",
            "description": "Feeds on desire, drains through seduction",
            "body_profile_bias": {"Curvy": +30, "Petite": -20, "Slim": -10},
        },
        {
            "name": "Hellion",
            "description": "Chaotic hellfire, wild destruction",
            "body_profile_bias": {"Athletic": +25, "Slim": -15, "Curvy": -10},
        },
        {
            "name": "Infernal",
            "description": "Ancient evil, smoldering menace",
            "body_profile_bias": {"Curvy": +15, "Athletic": +10, "Petite": -20},
        },
        {
            "name": "Corrupted",
            "description": "Once pure, now twisted by dark power",
            "body_profile_bias": {"Slim": +20, "Petite": +10, "Curvy": -25},
        },
        {
            "name": "Abyssal",
            "description": "Deep darkness, void-touched horror",
            "body_profile_bias": {
                "Slim": +25,
                "Petite": +5,
                "Curvy": -20,
                "Athletic": -10,
            },
        },
    ],
    "The Assassin": [
        {
            "name": "Shadow",
            "description": "Invisible until the killing blow",
            "body_profile_bias": {
                "Slim": +25,
                "Petite": +5,
                "Curvy": -20,
                "Athletic": -10,
            },
        },
        {
            "name": "Blade",
            "description": "Edged weapon master, surgical precision",
            "body_profile_bias": {
                "Athletic": +25,
                "Slim": +5,
                "Petite": -20,
                "Curvy": -10,
            },
        },
        {
            "name": "Phantom",
            "description": "Ghost-like movement, untouchable",
            "body_profile_bias": {
                "Petite": +25,
                "Slim": +10,
                "Curvy": -20,
                "Athletic": -15,
            },
        },
        {
            "name": "Silencer",
            "description": "Ends fights before they start",
            "body_profile_bias": {
                "Slim": +20,
                "Athletic": +15,
                "Curvy": -25,
                "Petite": -10,
            },
        },
        {
            "name": "Venom",
            "description": "Poisoned weapons, toxic specialist",
            "body_profile_bias": {
                "Slim": +15,
                "Athletic": +10,
                "Petite": -15,
                "Curvy": -10,
            },
        },
    ],
    "The Nymph": [
        {
            "name": "Dryad",
            "description": "Forest spirit, nature's living weapon",
            "body_profile_bias": {
                "Slim": +20,
                "Petite": +10,
                "Curvy": -20,
                "Athletic": -10,
            },
        },
        {
            "name": "Naiad",
            "description": "Water spirit, fluid and unpredictable",
            "body_profile_bias": {
                "Curvy": +20,
                "Slim": +10,
                "Petite": -20,
                "Athletic": -10,
            },
        },
        {
            "name": "Pixie",
            "description": "Tiny chaos agent, mischievous trickster",
            "body_profile_bias": {
                "Petite": +30,
                "Slim": +5,
                "Curvy": -25,
                "Athletic": -10,
            },
        },
        {
            "name": "Sylph",
            "description": "Air spirit, impossibly graceful",
            "body_profile_bias": {
                "Slim": +25,
                "Athletic": +5,
                "Curvy": -20,
                "Petite": -10,
            },
        },
        {
            "name": "Fae Queen",
            "description": "Otherworldly royalty, beautiful and cruel",
            "body_profile_bias": {
                "Curvy": +25,
                "Athletic": +5,
                "Petite": -20,
                "Slim": -10,
            },
        },
    ],
}


def _roll_subtype(archetype: str) -> dict | None:
    arch = (
        f"The {archetype}"
        if archetype and not archetype.startswith("The ")
        else archetype
    )
    subtypes = ARCHETYPE_SUBTYPES.get(arch, [])
    if not subtypes:
        return None
    return random.choice(subtypes)


def _find_subtype(archetype: str, name: str) -> dict | None:
    arch = (
        f"The {archetype}"
        if archetype and not archetype.startswith("The ")
        else archetype
    )
    subtypes = ARCHETYPE_SUBTYPES.get(arch, [])
    for st in subtypes:
        if st["name"].lower() == name.lower():
            return st
    return None


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


def _roll_body_profile(archetype: str | None, subtype_bias: dict | None = None) -> str:
    profile_weights = dict(ARCHETYPE_BODY_PROFILE_WEIGHTS.get(archetype, {}))
    if profile_weights:
        if subtype_bias:
            for key, adj in subtype_bias.items():
                if key in profile_weights:
                    profile_weights[key] = max(1, profile_weights[key] + adj)
        profiles = list(profile_weights.keys())
        weights = [profile_weights[p] for p in profiles]
    else:
        profiles = list(BODY_PROFILES.keys())
        weights = [1] * len(profiles)
    return random.choices(profiles, weights=weights, k=1)[0]


def _roll_body_traits(archetype: str | None, subtype: dict | None = None) -> dict:
    arch = (
        f"The {archetype}"
        if archetype and not archetype.startswith("The ")
        else archetype
    )

    subtype_bias = subtype.get("body_profile_bias") if subtype else None
    profile = _roll_body_profile(arch, subtype_bias=subtype_bias)
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
