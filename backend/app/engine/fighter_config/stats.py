import random


ARCHETYPE_STAT_WEIGHTS = {
    "The Siren": {"power": 15, "speed": 25, "technique": 30, "toughness": 15},
    "The Witch": {"power": 15, "speed": 20, "technique": 25, "toughness": 15},
    "The Viper": {"power": 20, "speed": 30, "technique": 25, "toughness": 15},
    "The Prodigy": {"power": 20, "speed": 30, "technique": 30, "toughness": 20},
    "The Doll": {"power": 15, "speed": 25, "technique": 25, "toughness": 15},
    "The Huntress": {"power": 25, "speed": 35, "technique": 20, "toughness": 20},
    "The Empress": {"power": 20, "speed": 20, "technique": 30, "toughness": 20},
    "The Experiment": {"power": 30, "speed": 20, "technique": 25, "toughness": 30},
    "The Demon": {"power": 30, "speed": 20, "technique": 20, "toughness": 20},
    "The Assassin": {"power": 20, "speed": 35, "technique": 30, "toughness": 15},
    "The Nymph": {"power": 15, "speed": 30, "technique": 20, "toughness": 15},
    "The Brute": {"power": 35, "speed": 15, "technique": 15, "toughness": 30},
    "The Veteran": {"power": 25, "speed": 20, "technique": 30, "toughness": 25},
    "The Monster": {"power": 35, "speed": 15, "technique": 15, "toughness": 35},
    "The Technician": {"power": 20, "speed": 25, "technique": 35, "toughness": 20},
    "The Wildcard": {"power": 25, "speed": 30, "technique": 20, "toughness": 20},
    "The Mystic": {"power": 20, "speed": 20, "technique": 25, "toughness": 20},
}

GENDER_FLAT_BONUS = {
    "male": {"power": 15, "toughness": 10},
    "female": {"power": 0, "toughness": 0},
}

GENDER_GUILE_RANGE = {
    "male": (0, 15),
    "female": (45, 100),
}

GENDER_SUPERNATURAL_RANGE = {
    "male": (0, 20),
    "female": (30, 100),
}


def _normal_between(lo: int, hi: int, rng: random.Random) -> int:
    mu = (lo + hi) / 2.0
    sigma = (hi - lo) / 4.0
    val = rng.gauss(mu, sigma)
    return max(lo, min(hi, round(val)))


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

    core_total = _normal_between(config.min_total_stats, config.max_total_stats, rng)

    weights = {}
    for stat in ("power", "speed", "technique", "toughness"):
        jitter = round(rng.gauss(0, 2))
        weights[stat] = max(5, profile[stat] + jitter)

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

    bonus = GENDER_FLAT_BONUS.get(gender.lower(), {})
    for stat, val in bonus.items():
        if val:
            bonus_val = round(rng.gauss(val, val * 0.2))
            stats[stat] = min(config.stat_max, stats[stat] + max(0, bonus_val))

    guile_lo, guile_hi = GENDER_GUILE_RANGE.get(gender.lower(), (0, 15))
    stats["guile"] = _normal_between(guile_lo, guile_hi, rng)

    sup_lo, sup_hi = GENDER_SUPERNATURAL_RANGE.get(gender.lower(), (0, 20))
    if has_supernatural:
        sup_lo = max(sup_lo, 20)
        sup_hi = max(sup_hi, 100)
    else:
        sup_lo = 0
        sup_hi = 0
    stats["supernatural"] = _normal_between(
        sup_lo, min(config.supernatural_cap, sup_hi), rng
    )

    return stats
