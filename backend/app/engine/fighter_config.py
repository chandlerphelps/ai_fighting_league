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
        if archetype in item.get("archetypes", []) or subtype in item.get("subtypes", []):
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


TECH_LEVELS = [
    "Fantasy Medieval",
    "Ancient / Mythological",
    "1800s Industrial",
    "Contemporary / Modern",
    "Near-Future",
    "Sci-Fi / Far Future",
]


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

MALE_BODY_TRAIT_OPTIONS = {
    "build_type": [
        "lean and wiry",
        "athletic and cut",
        "thick and powerful",
        "massive and hulking",
    ],
    "muscle_definition": [
        "naturally lean",
        "toned and defined",
        "heavily muscled",
        "freakishly jacked",
    ],
    "body_fat_pct": [
        "shredded 8-12%",
        "lean 12-15%",
        "athletic 15-18%",
        "thick 18-22%",
    ],
    "shoulder_width": ["narrow", "broad", "very broad", "impossibly wide"],
    "chest_build": [
        "flat and lean",
        "defined pecs",
        "barrel-chested",
        "massive slabs",
    ],
    "waist": ["narrow v-taper", "medium", "thick core", "blocky powerlifter"],
    "face_shape": [
        "sharp angular",
        "square jaw",
        "broad and flat",
        "gaunt hollow",
        "rugged weathered",
    ],
    "eye_expression": [
        "cold dead",
        "predatory",
        "calculating",
        "wild unhinged",
        "focused intense",
    ],
    "facial_hair": [
        "clean-shaven",
        "stubble",
        "full beard",
        "mustache",
        "goatee",
    ],
}

MALE_BODY_PROFILES = {
    "Lean": {
        "body_fat_pct": ["shredded 8-12%", "lean 12-15%"],
        "muscle_definition": ["naturally lean", "toned and defined"],
        "shoulder_width": ["narrow", "broad"],
        "chest_build": ["flat and lean", "defined pecs"],
        "build_type": ["lean and wiry"],
        "waist": ["narrow v-taper", "medium"],
    },
    "Athletic": {
        "body_fat_pct": ["lean 12-15%", "athletic 15-18%"],
        "muscle_definition": ["toned and defined", "heavily muscled"],
        "shoulder_width": ["broad", "very broad"],
        "chest_build": ["defined pecs", "barrel-chested"],
        "build_type": ["athletic and cut"],
        "waist": ["narrow v-taper", "medium"],
    },
    "Muscular": {
        "body_fat_pct": ["athletic 15-18%", "thick 18-22%"],
        "muscle_definition": ["heavily muscled", "freakishly jacked"],
        "shoulder_width": ["very broad", "impossibly wide"],
        "chest_build": ["barrel-chested", "massive slabs"],
        "build_type": ["thick and powerful"],
        "waist": ["medium", "thick core"],
    },
    "Massive": {
        "body_fat_pct": ["thick 18-22%", "athletic 15-18%"],
        "muscle_definition": ["freakishly jacked", "heavily muscled"],
        "shoulder_width": ["impossibly wide", "very broad"],
        "chest_build": ["massive slabs", "barrel-chested"],
        "build_type": ["massive and hulking"],
        "waist": ["thick core", "blocky powerlifter"],
    },
}

MALE_ARCHETYPE_BODY_PROFILE_WEIGHTS = {
    "The Brute": {"Lean": 5, "Athletic": 15, "Muscular": 30, "Massive": 50},
    "The Veteran": {"Lean": 20, "Athletic": 40, "Muscular": 30, "Massive": 10},
    "The Monster": {"Lean": 0, "Athletic": 10, "Muscular": 30, "Massive": 60},
    "The Technician": {"Lean": 35, "Athletic": 40, "Muscular": 20, "Massive": 5},
    "The Wildcard": {"Lean": 30, "Athletic": 35, "Muscular": 25, "Massive": 10},
    "The Mystic": {"Lean": 35, "Athletic": 35, "Muscular": 25, "Massive": 5},
    "The Prodigy": {"Lean": 30, "Athletic": 45, "Muscular": 20, "Massive": 5},
    "The Experiment": {"Lean": 10, "Athletic": 25, "Muscular": 40, "Massive": 25},
}

MALE_ARCHETYPE_HEIGHT_RANGES = {
    "The Brute": (72, 78),
    "The Veteran": (69, 75),
    "The Monster": (74, 80),
    "The Technician": (68, 74),
    "The Wildcard": (68, 75),
    "The Mystic": (69, 75),
    "The Prodigy": (69, 74),
    "The Experiment": (70, 77),
}

MALE_ARCHETYPE_BODY_WEIGHTS = {
    "The Brute": {
        "muscle_definition": {
            "naturally lean": 5,
            "toned and defined": 15,
            "heavily muscled": 40,
            "freakishly jacked": 40,
        },
        "body_fat_pct": {
            "shredded 8-12%": 5,
            "lean 12-15%": 15,
            "athletic 15-18%": 35,
            "thick 18-22%": 45,
        },
        "shoulder_width": {
            "narrow": 2,
            "broad": 15,
            "very broad": 40,
            "impossibly wide": 43,
        },
        "chest_build": {
            "flat and lean": 2,
            "defined pecs": 13,
            "barrel-chested": 40,
            "massive slabs": 45,
        },
        "facial_hair": {
            "clean-shaven": 10,
            "stubble": 30,
            "full beard": 35,
            "mustache": 10,
            "goatee": 15,
        },
        "eye_expression": {
            "cold dead": 20,
            "predatory": 35,
            "calculating": 5,
            "wild unhinged": 30,
            "focused intense": 10,
        },
        "waist": {
            "narrow v-taper": 5,
            "medium": 20,
            "thick core": 40,
            "blocky powerlifter": 35,
        },
    },
    "The Veteran": {
        "muscle_definition": {
            "naturally lean": 10,
            "toned and defined": 40,
            "heavily muscled": 40,
            "freakishly jacked": 10,
        },
        "body_fat_pct": {
            "shredded 8-12%": 10,
            "lean 12-15%": 35,
            "athletic 15-18%": 40,
            "thick 18-22%": 15,
        },
        "shoulder_width": {
            "narrow": 5,
            "broad": 40,
            "very broad": 40,
            "impossibly wide": 15,
        },
        "chest_build": {
            "flat and lean": 5,
            "defined pecs": 40,
            "barrel-chested": 40,
            "massive slabs": 15,
        },
        "facial_hair": {
            "clean-shaven": 15,
            "stubble": 35,
            "full beard": 25,
            "mustache": 15,
            "goatee": 10,
        },
        "eye_expression": {
            "cold dead": 15,
            "predatory": 20,
            "calculating": 35,
            "wild unhinged": 5,
            "focused intense": 25,
        },
        "waist": {
            "narrow v-taper": 15,
            "medium": 45,
            "thick core": 30,
            "blocky powerlifter": 10,
        },
    },
    "The Monster": {
        "muscle_definition": {
            "naturally lean": 0,
            "toned and defined": 5,
            "heavily muscled": 35,
            "freakishly jacked": 60,
        },
        "body_fat_pct": {
            "shredded 8-12%": 5,
            "lean 12-15%": 10,
            "athletic 15-18%": 30,
            "thick 18-22%": 55,
        },
        "shoulder_width": {
            "narrow": 0,
            "broad": 5,
            "very broad": 30,
            "impossibly wide": 65,
        },
        "chest_build": {
            "flat and lean": 0,
            "defined pecs": 5,
            "barrel-chested": 35,
            "massive slabs": 60,
        },
        "facial_hair": {
            "clean-shaven": 20,
            "stubble": 20,
            "full beard": 35,
            "mustache": 10,
            "goatee": 15,
        },
        "eye_expression": {
            "cold dead": 30,
            "predatory": 30,
            "calculating": 5,
            "wild unhinged": 30,
            "focused intense": 5,
        },
        "waist": {
            "narrow v-taper": 0,
            "medium": 10,
            "thick core": 40,
            "blocky powerlifter": 50,
        },
    },
    "The Technician": {
        "muscle_definition": {
            "naturally lean": 25,
            "toned and defined": 45,
            "heavily muscled": 25,
            "freakishly jacked": 5,
        },
        "body_fat_pct": {
            "shredded 8-12%": 20,
            "lean 12-15%": 45,
            "athletic 15-18%": 30,
            "thick 18-22%": 5,
        },
        "shoulder_width": {
            "narrow": 20,
            "broad": 45,
            "very broad": 30,
            "impossibly wide": 5,
        },
        "chest_build": {
            "flat and lean": 20,
            "defined pecs": 50,
            "barrel-chested": 25,
            "massive slabs": 5,
        },
        "facial_hair": {
            "clean-shaven": 35,
            "stubble": 30,
            "full beard": 10,
            "mustache": 10,
            "goatee": 15,
        },
        "eye_expression": {
            "cold dead": 10,
            "predatory": 10,
            "calculating": 45,
            "wild unhinged": 5,
            "focused intense": 30,
        },
        "waist": {
            "narrow v-taper": 35,
            "medium": 40,
            "thick core": 20,
            "blocky powerlifter": 5,
        },
    },
    "The Wildcard": {
        "muscle_definition": {
            "naturally lean": 20,
            "toned and defined": 35,
            "heavily muscled": 30,
            "freakishly jacked": 15,
        },
        "body_fat_pct": {
            "shredded 8-12%": 15,
            "lean 12-15%": 30,
            "athletic 15-18%": 35,
            "thick 18-22%": 20,
        },
        "shoulder_width": {
            "narrow": 15,
            "broad": 35,
            "very broad": 35,
            "impossibly wide": 15,
        },
        "chest_build": {
            "flat and lean": 15,
            "defined pecs": 35,
            "barrel-chested": 35,
            "massive slabs": 15,
        },
        "facial_hair": {
            "clean-shaven": 20,
            "stubble": 25,
            "full beard": 20,
            "mustache": 15,
            "goatee": 20,
        },
        "eye_expression": {
            "cold dead": 10,
            "predatory": 15,
            "calculating": 10,
            "wild unhinged": 45,
            "focused intense": 20,
        },
        "waist": {
            "narrow v-taper": 20,
            "medium": 35,
            "thick core": 30,
            "blocky powerlifter": 15,
        },
    },
    "The Mystic": {
        "muscle_definition": {
            "naturally lean": 30,
            "toned and defined": 40,
            "heavily muscled": 25,
            "freakishly jacked": 5,
        },
        "body_fat_pct": {
            "shredded 8-12%": 25,
            "lean 12-15%": 40,
            "athletic 15-18%": 30,
            "thick 18-22%": 5,
        },
        "shoulder_width": {
            "narrow": 15,
            "broad": 40,
            "very broad": 35,
            "impossibly wide": 10,
        },
        "chest_build": {
            "flat and lean": 15,
            "defined pecs": 45,
            "barrel-chested": 30,
            "massive slabs": 10,
        },
        "facial_hair": {
            "clean-shaven": 25,
            "stubble": 20,
            "full beard": 30,
            "mustache": 10,
            "goatee": 15,
        },
        "eye_expression": {
            "cold dead": 15,
            "predatory": 10,
            "calculating": 30,
            "wild unhinged": 10,
            "focused intense": 35,
        },
        "waist": {
            "narrow v-taper": 30,
            "medium": 40,
            "thick core": 25,
            "blocky powerlifter": 5,
        },
    },
    "The Prodigy": {
        "muscle_definition": {
            "naturally lean": 20,
            "toned and defined": 50,
            "heavily muscled": 25,
            "freakishly jacked": 5,
        },
        "body_fat_pct": {
            "shredded 8-12%": 20,
            "lean 12-15%": 45,
            "athletic 15-18%": 30,
            "thick 18-22%": 5,
        },
        "shoulder_width": {
            "narrow": 10,
            "broad": 45,
            "very broad": 35,
            "impossibly wide": 10,
        },
        "chest_build": {
            "flat and lean": 10,
            "defined pecs": 50,
            "barrel-chested": 30,
            "massive slabs": 10,
        },
        "facial_hair": {
            "clean-shaven": 40,
            "stubble": 35,
            "full beard": 5,
            "mustache": 5,
            "goatee": 15,
        },
        "eye_expression": {
            "cold dead": 5,
            "predatory": 20,
            "calculating": 20,
            "wild unhinged": 15,
            "focused intense": 40,
        },
        "waist": {
            "narrow v-taper": 35,
            "medium": 40,
            "thick core": 20,
            "blocky powerlifter": 5,
        },
    },
    "The Experiment": {
        "muscle_definition": {
            "naturally lean": 5,
            "toned and defined": 20,
            "heavily muscled": 40,
            "freakishly jacked": 35,
        },
        "body_fat_pct": {
            "shredded 8-12%": 15,
            "lean 12-15%": 25,
            "athletic 15-18%": 35,
            "thick 18-22%": 25,
        },
        "shoulder_width": {
            "narrow": 5,
            "broad": 20,
            "very broad": 40,
            "impossibly wide": 35,
        },
        "chest_build": {
            "flat and lean": 5,
            "defined pecs": 20,
            "barrel-chested": 40,
            "massive slabs": 35,
        },
        "facial_hair": {
            "clean-shaven": 30,
            "stubble": 25,
            "full beard": 15,
            "mustache": 15,
            "goatee": 15,
        },
        "eye_expression": {
            "cold dead": 25,
            "predatory": 20,
            "calculating": 15,
            "wild unhinged": 25,
            "focused intense": 15,
        },
        "waist": {
            "narrow v-taper": 10,
            "medium": 25,
            "thick core": 40,
            "blocky powerlifter": 25,
        },
    },
}

BODY_TRAIT_OPTIONS = {
    "waist": ["narrow", "medium", "wide"],
    "abs_tone": [
        "soft with no definition",
        "slight definition",
        "toned and defined",
        "ripped and shredded",
    ],
    "body_fat_pct": ["lean 12-16%", "athletic 17-20%", "fit 21-24%", "soft 25-30%"],
    "butt_size": ["tiny tight", "medium round", "large thick", "very large prominent"],
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
    "breast_size": ["tiny flat-chested", "small perky", "medium", "large heavy", "massive oversized"],
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
        "breast_size": ["tiny flat-chested", "small perky", "medium"],
        "butt_size": ["tiny tight", "medium round"],
    },
    "Slim": {
        "body_fat_pct": ["lean 12-16%", "athletic 17-20%"],
        "abs_tone": [
            "soft with no definition",
            "slight definition",
            "toned and defined",
        ],
        "waist": ["narrow", "medium"],
        "breast_size": ["tiny flat-chested", "small perky", "medium"],
        "butt_size": ["tiny tight", "medium round"],
    },
    "Athletic": {
        "body_fat_pct": ["lean 12-16%", "athletic 17-20%"],
        "abs_tone": ["toned and defined", "ripped and shredded"],
        "waist": ["narrow", "medium"],
        "breast_size": ["small perky", "medium", "large heavy"],
        "butt_size": ["medium round", "large thick"],
    },
    "Curvy": {
        "body_fat_pct": ["athletic 17-20%", "fit 21-24%"],
        "abs_tone": [
            "soft with no definition",
            "slight definition",
            "toned and defined",
        ],
        "waist": ["narrow", "medium"],
        "breast_size": ["medium", "large heavy", "massive oversized"],
        "butt_size": ["medium round", "large thick", "very large prominent"],
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
            "tiny flat-chested": 2,
            "small perky": 7,
            "medium": 23,
            "large heavy": 50,
            "massive oversized": 18,
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
            "tiny tight": 18,
            "medium round": 43,
            "large thick": 33,
            "very large prominent": 6,
        },
        "waist": {"narrow": 40, "medium": 45, "wide": 15},
    },
    "The Witch": {
        "breast_size": {
            "tiny flat-chested": 9,
            "small perky": 22,
            "medium": 34,
            "large heavy": 27,
            "massive oversized": 8,
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
            "tiny tight": 22,
            "medium round": 42,
            "large thick": 32,
            "very large prominent": 4,
        },
        "waist": {"narrow": 35, "medium": 45, "wide": 20},
    },
    "The Viper": {
        "breast_size": {
            "tiny flat-chested": 10,
            "small perky": 26,
            "medium": 38,
            "large heavy": 23,
            "massive oversized": 3,
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
            "tiny tight": 26,
            "medium round": 47,
            "large thick": 25,
            "very large prominent": 2,
        },
        "waist": {"narrow": 50, "medium": 40, "wide": 10},
    },
    "The Prodigy": {
        "breast_size": {
            "tiny flat-chested": 15,
            "small perky": 33,
            "medium": 33,
            "large heavy": 17,
            "massive oversized": 2,
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
            "tiny tight": 36,
            "medium round": 41,
            "large thick": 21,
            "very large prominent": 2,
        },
        "waist": {"narrow": 45, "medium": 45, "wide": 10},
    },
    "The Doll": {
        "breast_size": {
            "tiny flat-chested": 12,
            "small perky": 29,
            "medium": 31,
            "large heavy": 23,
            "massive oversized": 5,
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
            "tiny tight": 22,
            "medium round": 42,
            "large thick": 32,
            "very large prominent": 4,
        },
        "waist": {"narrow": 45, "medium": 40, "wide": 15},
    },
    "The Huntress": {
        "breast_size": {
            "tiny flat-chested": 8,
            "small perky": 21,
            "medium": 38,
            "large heavy": 28,
            "massive oversized": 5,
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
            "tiny tight": 27,
            "medium round": 42,
            "large thick": 27,
            "very large prominent": 4,
        },
        "waist": {"narrow": 35, "medium": 50, "wide": 15},
    },
    "The Empress": {
        "breast_size": {
            "tiny flat-chested": 2,
            "small perky": 7,
            "medium": 26,
            "large heavy": 47,
            "massive oversized": 18,
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
            "tiny tight": 18,
            "medium round": 43,
            "large thick": 33,
            "very large prominent": 6,
        },
        "waist": {"narrow": 25, "medium": 45, "wide": 30},
    },
    "The Experiment": {
        "breast_size": {
            "tiny flat-chested": 8,
            "small perky": 20,
            "medium": 30,
            "large heavy": 30,
            "massive oversized": 12,
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
            "tiny tight": 28,
            "medium round": 42,
            "large thick": 22,
            "very large prominent": 8,
        },
        "waist": {"narrow": 30, "medium": 45, "wide": 25},
    },
    "The Demon": {
        "breast_size": {
            "tiny flat-chested": 4,
            "small perky": 10,
            "medium": 24,
            "large heavy": 44,
            "massive oversized": 18,
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
            "tiny tight": 9,
            "medium round": 31,
            "large thick": 48,
            "very large prominent": 12,
        },
        "waist": {"narrow": 35, "medium": 45, "wide": 20},
    },
    "The Assassin": {
        "breast_size": {
            "tiny flat-chested": 15,
            "small perky": 35,
            "medium": 33,
            "large heavy": 15,
            "massive oversized": 2,
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
            "tiny tight": 31,
            "medium round": 44,
            "large thick": 23,
            "very large prominent": 2,
        },
        "waist": {"narrow": 50, "medium": 40, "wide": 10},
    },
    "The Nymph": {
        "breast_size": {
            "tiny flat-chested": 10,
            "small perky": 31,
            "medium": 36,
            "large heavy": 19,
            "massive oversized": 4,
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
            "tiny tight": 17,
            "medium round": 43,
            "large thick": 35,
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


ARCHETYPE_SUBTYPES_MALE = {
    "The Brute": [
        {
            "name": "Berserker",
            "description": "Uncontrollable rage, fights like a cornered animal",
            "body_profile_bias": {"Massive": +15, "Lean": -15},
        },
        {
            "name": "Enforcer",
            "description": "Calculated brutality, breaks bones on purpose",
            "body_profile_bias": {"Muscular": +15, "Lean": -10},
        },
        {
            "name": "Juggernaut",
            "description": "Unstoppable forward pressure, walks through damage",
            "body_profile_bias": {"Massive": +20, "Athletic": -15},
        },
        {
            "name": "Brawler",
            "description": "Street-fighting savagery, no technique just violence",
            "body_profile_bias": {"Athletic": +10, "Muscular": +10, "Lean": -15},
        },
        {
            "name": "Mauler",
            "description": "Ground-and-pound specialist, smothering aggression",
            "body_profile_bias": {"Muscular": +10, "Massive": +10, "Lean": -15},
        },
    ],
    "The Veteran": [
        {
            "name": "Grizzled",
            "description": "Decades of scars, fights on muscle memory alone",
            "body_profile_bias": {"Athletic": +10, "Muscular": +10, "Lean": -15},
        },
        {
            "name": "Tactician",
            "description": "Reads opponents like books, always three moves ahead",
            "body_profile_bias": {"Athletic": +15, "Massive": -10},
        },
        {
            "name": "Warhorse",
            "description": "Refuses to stay down, legendary toughness",
            "body_profile_bias": {"Muscular": +15, "Lean": -10},
        },
        {
            "name": "Mentor",
            "description": "Old guard, still dangerous, teaches through pain",
            "body_profile_bias": {"Athletic": +10, "Lean": +5, "Massive": -10},
        },
        {
            "name": "Survivor",
            "description": "Should have died a dozen times, too stubborn to quit",
            "body_profile_bias": {"Lean": +15, "Massive": -15},
        },
    ],
    "The Monster": [
        {
            "name": "Titan",
            "description": "Godlike size, moves mountains",
            "body_profile_bias": {"Massive": +20, "Lean": -20},
        },
        {
            "name": "Behemoth",
            "description": "Living siege engine, destroys everything in his path",
            "body_profile_bias": {"Massive": +15, "Athletic": -10},
        },
        {
            "name": "Aberration",
            "description": "Something wrong with his proportions, uncanny and terrifying",
            "body_profile_bias": {"Muscular": +15, "Athletic": -10},
        },
        {
            "name": "Goliath",
            "description": "Towering giant, makes other big men look small",
            "body_profile_bias": {"Massive": +20, "Lean": -15},
        },
        {
            "name": "Nightmare",
            "description": "The thing you see in the dark, primal fear made flesh",
            "body_profile_bias": {"Muscular": +10, "Massive": +10, "Lean": -15},
        },
    ],
    "The Technician": [
        {
            "name": "Surgeon",
            "description": "Dissects opponents with clinical precision",
            "body_profile_bias": {"Lean": +15, "Massive": -15},
        },
        {
            "name": "Analyst",
            "description": "Studies film obsessively, knows every weakness",
            "body_profile_bias": {"Athletic": +15, "Massive": -10},
        },
        {
            "name": "Counter-Puncher",
            "description": "Waits for mistakes then punishes them brutally",
            "body_profile_bias": {"Athletic": +10, "Lean": +10, "Massive": -15},
        },
        {
            "name": "Chessmaster",
            "description": "Every move is a setup for the next three",
            "body_profile_bias": {"Lean": +10, "Athletic": +10, "Massive": -15},
        },
        {
            "name": "Pressure Fighter",
            "description": "Relentless technical volume, drowns opponents in output",
            "body_profile_bias": {"Athletic": +15, "Lean": -5},
        },
    ],
    "The Wildcard": [
        {
            "name": "Lunatic",
            "description": "Genuinely unhinged, nobody knows what he'll do next",
            "body_profile_bias": {"Lean": +15, "Massive": -10},
        },
        {
            "name": "Gambler",
            "description": "Throws everything on one big moment",
            "body_profile_bias": {"Athletic": +10, "Lean": +5, "Massive": -10},
        },
        {
            "name": "Trickster",
            "description": "Dirty tricks, misdirection, fights with his brain",
            "body_profile_bias": {"Lean": +15, "Athletic": +5, "Massive": -15},
        },
        {
            "name": "Anarchist",
            "description": "Fights the rules, the ref, and the opponent simultaneously",
            "body_profile_bias": {"Athletic": +10, "Muscular": +5, "Lean": -10},
        },
        {
            "name": "Showman",
            "description": "Every fight is a performance, lives for the crowd",
            "body_profile_bias": {"Athletic": +15, "Lean": -5, "Massive": -5},
        },
    ],
    "The Mystic": [
        {
            "name": "Monk",
            "description": "Disciplined spiritual warrior, fights with inner peace",
            "body_profile_bias": {"Lean": +15, "Athletic": +5, "Massive": -15},
        },
        {
            "name": "Shaman",
            "description": "Channels ancestral spirits, fights with otherworldly guidance",
            "body_profile_bias": {"Athletic": +10, "Lean": +5, "Massive": -10},
        },
        {
            "name": "Sage",
            "description": "Ancient knowledge, sees the flow of combat",
            "body_profile_bias": {"Lean": +15, "Massive": -15},
        },
        {
            "name": "Prophet",
            "description": "Fights with divine conviction, terrifying certainty",
            "body_profile_bias": {"Athletic": +10, "Muscular": +5, "Lean": -10},
        },
        {
            "name": "Ascetic",
            "description": "Denied himself everything, forged in deprivation",
            "body_profile_bias": {"Lean": +20, "Massive": -15},
        },
    ],
    "The Prodigy": [
        {
            "name": "Phenom",
            "description": "Natural athlete, explosive raw talent beyond his years",
            "body_profile_bias": {"Athletic": +15, "Lean": +5, "Massive": -15},
        },
        {
            "name": "Wunderkind",
            "description": "Impossibly talented youth, makes veterans look slow",
            "body_profile_bias": {"Lean": +10, "Athletic": +10, "Massive": -15},
        },
        {
            "name": "Natural",
            "description": "Born to fight, instinct over training",
            "body_profile_bias": {"Athletic": +20, "Massive": -15},
        },
        {
            "name": "Heir Apparent",
            "description": "Next in a legendary bloodline, born with expectations",
            "body_profile_bias": {"Athletic": +10, "Muscular": +5, "Lean": -10},
        },
        {
            "name": "Prodigy Son",
            "description": "Father was a legend, son might be better",
            "body_profile_bias": {"Athletic": +15, "Massive": -10},
        },
    ],
    "The Experiment": [
        {
            "name": "Cyborg",
            "description": "Mechanical augmentation, part machine",
            "body_profile_bias": {"Muscular": +15, "Lean": -10},
        },
        {
            "name": "Subject Zero",
            "description": "First successful test subject, unstable but powerful",
            "body_profile_bias": {"Massive": +15, "Lean": -15},
        },
        {
            "name": "Weapon X",
            "description": "Military black project, built to kill",
            "body_profile_bias": {"Muscular": +10, "Athletic": +5, "Lean": -10},
        },
        {
            "name": "Lab Rat",
            "description": "Escaped experimental facility, body permanently altered",
            "body_profile_bias": {"Massive": +10, "Muscular": +10, "Athletic": -15},
        },
        {
            "name": "Evolved",
            "description": "Next stage of human development, something beyond",
            "body_profile_bias": {"Athletic": +10, "Muscular": +10, "Lean": -15},
        },
    ],
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
    trait_options = MALE_BODY_TRAIT_OPTIONS if gender.lower() == "male" else BODY_TRAIT_OPTIONS
    body_weights = MALE_ARCHETYPE_BODY_WEIGHTS if gender.lower() == "male" else ARCHETYPE_BODY_WEIGHTS
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
    "lean 12-15%": 0.97,
    "athletic 15-18%": 1.02,
    "thick 18-22%": 1.10,
}

MALE_BUILD_WEIGHT_BONUS = {
    "lean and wiry": -5,
    "athletic and cut": 0,
    "thick and powerful": 15,
    "massive and hulking": 35,
}

MALE_WAIST_MULTIPLIERS = {
    "narrow v-taper": 0.97,
    "medium": 1.00,
    "thick core": 1.04,
    "blocky powerlifter": 1.08,
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
    profiles_source = (
        MALE_BODY_PROFILES if gender.lower() == "male" else BODY_PROFILES
    )
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
                "muscle_definition", arch, allowed.get("muscle_definition"), gender="male"
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
    if "chest_build" in traits:
        return _build_male_body_directive(traits)
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


def _build_male_body_directive(traits: dict) -> str:
    return (
        "BODY TYPE DIRECTIVE (you MUST incorporate these exact physical traits):\n"
        f"- Build: {traits.get('body_profile', 'Athletic')} — {traits.get('build_type', 'athletic and cut')}\n"
        f"- Height: {traits['height']}\n"
        f"- Weight: {traits['weight']}\n"
        f"- Muscle definition: {traits.get('muscle_definition', 'toned and defined')}\n"
        f"- Shoulders: {traits.get('shoulder_width', 'broad')}\n"
        f"- Chest: {traits.get('chest_build', 'defined pecs')}\n"
        f"- Waist: {traits.get('waist', 'medium')}\n"
        f"- Body fat: {traits.get('body_fat_pct', 'athletic 15-18%')}\n"
        f"- Face: {traits.get('face_shape', 'square jaw')}, {traits.get('eye_expression', 'focused intense')} eyes\n"
        f"- Facial hair: {traits.get('facial_hair', 'stubble')}\n"
        "\nThe height and weight are EXACT — use these values directly.\n"
        "Work the other traits naturally into image_prompt_body_parts and image_prompt_expression.\n"
        "IMPORTANT: Interpret ALL traits through a DANGEROUS, IMPOSING lens. "
        "Every combination should result in a threatening, confident character who looks like "
        "someone you would cross the street to avoid."
    )


def _height_adjective(inches: int) -> str:
    if inches <= 61:
        return "petite"
    if inches <= 64:
        return "short"
    if inches <= 67:
        return "average height"
    return "tall"


def _build_body_shape_line(traits: dict, tier: str = "") -> str:
    if "chest_build" in traits:
        return f"{traits['chest_build']} chest, {traits.get('shoulder_width', 'broad')} shoulders"
    if tier == "sfw":
        covered = " (covered)"
    elif tier == "barely":
        covered = " (barely covered)"
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
    return f"{height_part}{traits['breast_size']} breasts{covered}, {traits['butt_size']} butt"


def _build_nsfw_anatomy_line(traits: dict, tier: str = "nsfw") -> str:
    if "chest_build" in traits:
        return (
            f"{traits['chest_build']} chest, "
            f"{traits.get('muscle_definition', 'toned and defined')} build, "
            f"{traits.get('shoulder_width', 'broad')} shoulders"
        )
    barely = " (barely covered)" if tier == "barely" else ""
    return (
        f"{traits['breast_size']} breasts{barely}, "
        f"{traits['nipple_size']} nipples{barely}, "
        f"{traits['butt_size']} butt, "
        f"{traits['vulva_type']}{barely}"
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


OUTFIT_COLOR_PALETTE = [
    "Crimson Red", "Royal Blue", "Midnight Black", "Pure White", "Emerald Green",
    "Gold", "Silver", "Deep Purple", "Hot Pink", "Orange", "Teal", "Burgundy",
    "Navy Blue", "Forest Green", "Copper", "Lavender", "Scarlet", "Ice Blue",
    "Charcoal", "Rose", "Bronze", "Jade", "Ivory", "Electric Yellow",
]

HAIR_COLOR_BUCKETS = [
    "Black", "Brown", "Blonde", "Red/Auburn", "White/Silver",
    "Blue", "Pink", "Green", "Purple", "Multicolor",
]

_HAIR_BUCKET_KEYWORDS = {
    "Black": ["black", "jet black", "raven", "ebony", "onyx", "dark black"],
    "Brown": ["brown", "brunette", "chestnut", "chocolate", "mocha", "mahogany", "walnut", "coffee", "hazel", "caramel", "tawny"],
    "Blonde": ["blonde", "blond", "golden", "platinum", "honey", "sandy", "ash blonde", "strawberry blonde", "flaxen", "wheat", "champagne", "butter"],
    "Red/Auburn": ["red", "auburn", "ginger", "copper", "crimson", "scarlet", "rust", "fire", "flame", "cherry", "ruby", "vermillion", "cinnamon"],
    "White/Silver": ["white", "silver", "grey", "gray", "platinum white", "snow", "frost", "ice", "steel", "pearl", "ivory"],
    "Blue": ["blue", "navy", "cerulean", "cobalt", "azure", "sapphire", "teal", "cyan", "indigo"],
    "Pink": ["pink", "magenta", "fuchsia", "rose", "bubblegum", "coral", "salmon", "hot pink"],
    "Green": ["green", "emerald", "lime", "olive", "mint", "jade", "forest", "sage", "teal green"],
    "Purple": ["purple", "violet", "lavender", "lilac", "plum", "amethyst", "mauve", "orchid"],
    "Multicolor": ["multicolor", "rainbow", "ombre", "gradient", "streaks", "highlights", "tips", "two-tone", "split"],
}


def classify_hair_color(raw: str) -> str:
    if not raw:
        return ""
    lower = raw.lower().strip()
    for bucket, keywords in _HAIR_BUCKET_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                if bucket == "White/Silver" and ("platinum blonde" in lower or "strawberry" in lower):
                    continue
                return bucket
    return "Brown"


ARCHETYPE_STAT_WEIGHTS = {
    "The Siren":      {"power": 15, "speed": 25, "technique": 30, "toughness": 15, "guile": (30, 50), "supernatural": (0, 15)},
    "The Witch":      {"power": 15, "speed": 20, "technique": 25, "toughness": 15, "guile": (20, 40), "supernatural": (25, 50)},
    "The Viper":      {"power": 20, "speed": 30, "technique": 25, "toughness": 15, "guile": (35, 50), "supernatural": (0, 10)},
    "The Prodigy":    {"power": 20, "speed": 30, "technique": 30, "toughness": 20, "guile": (5, 25),  "supernatural": (0, 10)},
    "The Doll":       {"power": 15, "speed": 25, "technique": 25, "toughness": 15, "guile": (35, 50), "supernatural": (0, 20)},
    "The Huntress":   {"power": 25, "speed": 35, "technique": 20, "toughness": 20, "guile": (10, 30), "supernatural": (0, 10)},
    "The Empress":    {"power": 20, "speed": 20, "technique": 30, "toughness": 20, "guile": (30, 50), "supernatural": (0, 15)},
    "The Experiment": {"power": 30, "speed": 20, "technique": 25, "toughness": 30, "guile": (5, 20),  "supernatural": (10, 35)},
    "The Demon":      {"power": 30, "speed": 20, "technique": 20, "toughness": 20, "guile": (15, 35), "supernatural": (30, 50)},
    "The Assassin":   {"power": 20, "speed": 35, "technique": 30, "toughness": 15, "guile": (25, 45), "supernatural": (0, 10)},
    "The Nymph":      {"power": 15, "speed": 30, "technique": 20, "toughness": 15, "guile": (20, 40), "supernatural": (25, 45)},
    "The Brute":      {"power": 35, "speed": 15, "technique": 15, "toughness": 30, "guile": (0, 15),  "supernatural": (0, 10)},
    "The Veteran":    {"power": 25, "speed": 20, "technique": 30, "toughness": 25, "guile": (10, 30), "supernatural": (0, 10)},
    "The Monster":    {"power": 35, "speed": 15, "technique": 15, "toughness": 35, "guile": (0, 10),  "supernatural": (0, 15)},
    "The Technician": {"power": 20, "speed": 25, "technique": 35, "toughness": 20, "guile": (10, 25), "supernatural": (0, 10)},
    "The Wildcard":   {"power": 25, "speed": 30, "technique": 20, "toughness": 20, "guile": (15, 35), "supernatural": (0, 20)},
    "The Mystic":     {"power": 20, "speed": 20, "technique": 25, "toughness": 20, "guile": (10, 25), "supernatural": (30, 50)},
}

GENDER_CORE_BIAS = {
    "male":   {"power": 10, "speed": -5, "technique": -5, "toughness": 5},
    "female": {"power": -5, "speed": 5, "technique": 5, "toughness": -5},
}

GENDER_GUILE_SHIFT = {
    "male": -10,
    "female": 10,
}


def generate_archetype_stats(
    archetype: str,
    gender: str,
    config,
    has_supernatural: bool = False,
    rng: random.Random = None,
) -> dict:
    if rng is None:
        rng = random.Random()

    profile = ARCHETYPE_STAT_WEIGHTS.get(archetype)
    if not profile:
        profile = ARCHETYPE_STAT_WEIGHTS["The Prodigy"]

    core_total = rng.randint(config.min_total_stats, config.max_total_stats)

    bias = GENDER_CORE_BIAS.get(gender.lower(), {})
    weights = {}
    for stat in ("power", "speed", "technique", "toughness"):
        base_w = profile[stat] + bias.get(stat, 0)
        weights[stat] = max(5, base_w + rng.randint(-5, 5))

    weight_total = sum(weights.values())
    stats = {}
    for stat, w in weights.items():
        raw = round(core_total * w / weight_total)
        stats[stat] = max(config.stat_min, min(config.stat_max, raw))

    diff = core_total - sum(stats.values())
    core_keys = list(stats.keys())
    while diff != 0:
        key = rng.choice(core_keys)
        if diff > 0 and stats[key] < config.stat_max:
            stats[key] += 1
            diff -= 1
        elif diff < 0 and stats[key] > config.stat_min:
            stats[key] -= 1
            diff += 1

    guile_lo, guile_hi = profile["guile"]
    guile_shift = GENDER_GUILE_SHIFT.get(gender.lower(), 0)
    guile_lo = max(0, guile_lo + guile_shift)
    guile_hi = min(config.guile_cap, guile_hi + guile_shift)
    stats["guile"] = rng.randint(guile_lo, guile_hi)

    sup_lo, sup_hi = profile["supernatural"]
    if has_supernatural:
        sup_lo = max(sup_lo, 20)
        sup_hi = max(sup_hi, 40)
    else:
        sup_lo = 0
        sup_hi = 0
    stats["supernatural"] = rng.randint(sup_lo, min(config.supernatural_cap, sup_hi))

    return stats


def _roll_skimpiness(weights: list[int] | None) -> int:
    if not weights or len(weights) != 4:
        weights = [10, 30, 38, 22]
    total = sum(weights)
    if total <= 0:
        weights = [10, 30, 38, 22]
        total = 100
    normalized = [w / total for w in weights]
    return random.choices([1, 2, 3, 4], weights=normalized, k=1)[0]
