import random as _random

CORE_STATS = ["power", "speed", "technique", "toughness"]
STAT_MIN = 15
STAT_CAP = 95

TIER_ORDER = {"underground": 0, "contender": 1, "championship": 2}

RING_NAMES = [
    "Viper", "Blaze", "Phantom", "Crusher", "Storm", "Shadow", "Fury", "Hawk",
    "Razor", "Titan", "Cyclone", "Inferno", "Specter", "Bolt", "Fang", "Rogue",
    "Diesel", "Vandal", "Scorch", "Havoc", "Wraith", "Cobalt", "Onyx", "Sable",
    "Crimson", "Obsidian", "Jade", "Tempest", "Serpent", "Valkyrie", "Banshee",
    "Phoenix", "Raven", "Prowler", "Dagger", "Venom", "Ember", "Nova", "Eclipse",
    "Thunder", "Iron", "Steel", "Ghost", "Reaper", "Siren", "Widow", "Jackal",
    "Mantis", "Scorpion", "Lynx", "Panther", "Coyote", "Barracuda", "Condor",
    "Mamba", "Asp", "Hornet", "Stinger", "Talon", "Grizzly", "Wolverine",
    "Apex", "Brawler", "Rumble", "Bruiser", "Knuckles", "Sledge", "Hammer",
    "Spike", "Mayhem", "Chaos", "Riot", "Rampage", "Blitz", "Surge", "Torque",
    "Nitro", "Rocket", "Bullet", "Cannon", "Arsenal", "Warhead", "Shrapnel",
    "Tremor", "Quake", "Riptide", "Monsoon", "Avalanche", "Glacier", "Tundra",
    "Volcano", "Magma", "Cinder", "Ash", "Smoke", "Haze", "Mirage", "Prism",
    "Jinx", "Hex", "Curse", "Bane", "Doom", "Dread", "Malice", "Spite",
    "Vengeance", "Wrath", "Rage", "Savage", "Feral", "Predator", "Hunter",
    "Stalker", "Ambush", "Snare", "Trap", "Lure", "Decoy", "Bluff", "Gambit",
    "Comet", "Nebula", "Zenith", "Apex", "Summit", "Ridge", "Flint", "Granite",
    "Marble", "Slate", "Pyro", "Frost", "Sleet", "Hail", "Gale", "Breeze",
    "Typhoon", "Tsunami", "Torrent", "Cascade", "Raptor", "Falcon", "Osprey",
    "Kestrel", "Merlin", "Harrier", "Sparrow", "Wren", "Kingpin", "Baron",
    "Duke", "Knight", "Bishop", "Pawn", "Rook", "Ace", "Joker", "Maverick",
    "Rebel", "Outlaw", "Bandit", "Rascal", "Hustler", "Grifter", "Shark",
    "Wolf", "Fox", "Bear", "Boar", "Ram", "Buck", "Stag", "Moose",
    "Bison", "Cobra", "Venom", "Fist", "Claw", "Thorn", "Barb", "Edge",
    "Blade", "Saber", "Lance", "Pike", "Bolt", "Spark", "Flash", "Flare",
    "Blaze", "Torch", "Beacon", "Signal", "Sentry", "Scout", "Ranger", "Marshal",
    "Warden", "Captain", "Chief", "Boss", "Czar", "King", "Prince", "Titan",
]

PREFIXES = [
    "The", "Kid", "Big", "Lil", "Old", "Mad", "Iron", "Stone", "Red", "Black",
    "Silver", "Golden", "Dark", "White", "Blue", "Wild", "Raw", "Cold", "Hot",
]


def check_retirement(fighter: dict, rng: _random.Random = None) -> tuple[bool, str]:
    if rng is None:
        rng = _random.Random()

    age = fighter.get("age", 25)
    tier = fighter.get("tier", "underground")
    season_wins = fighter.get("season_wins", 0)
    season_losses = fighter.get("season_losses", 0)
    consecutive_losses = fighter.get("consecutive_losses", 0)
    seasons_in_tier = fighter.get("seasons_in_current_tier", 0)
    morale = fighter.get("condition", {}).get("morale", "neutral")
    belt_holder = fighter.get("_is_belt_holder", False)

    if age >= 34 and season_losses > season_wins:
        return True, "age_and_losing_record"

    if tier == "underground" and age >= 30 and seasons_in_tier >= 4:
        stagnation_chance = min(0.8, 0.3 + 0.1 * (seasons_in_tier - 4))
        if rng.random() < stagnation_chance:
            return True, "underground_stagnation"

    if consecutive_losses >= 5 and morale == "low" and age >= 25:
        return True, "morale_collapse"

    condition = fighter.get("condition", {})
    injuries = condition.get("injuries", [])
    has_severe = any(i.get("severity") == "severe" for i in injuries)
    if age >= 32 and has_severe and rng.random() < 0.30:
        return True, "severe_injury_retirement"

    if belt_holder and age >= 33 and rng.random() < 0.20:
        return True, "graceful_exit"

    return False, ""


def apply_aging(fighter: dict, rng: _random.Random = None) -> dict:
    if rng is None:
        rng = _random.Random()

    age = fighter.get("age", 25)
    stats = fighter.get("stats", {})

    fighter["age"] = age + 1

    if age < 26:
        num_boosts = rng.randint(2, 3)
        boosted = rng.sample(CORE_STATS, min(num_boosts, len(CORE_STATS)))
        for stat in boosted:
            boost_amount = 2 if age < 22 else 1
            current = stats.get(stat, 50)
            stats[stat] = min(current + boost_amount, STAT_CAP)
    elif 26 <= age <= 31:
        pass
    elif 32 <= age <= 35:
        for stat in ["speed", "toughness"]:
            current = stats.get(stat, 50)
            stats[stat] = max(current - 2, STAT_MIN)
        if rng.random() < 0.3:
            current = stats.get("power", 50)
            stats["power"] = max(current - 1, STAT_MIN)
    else:
        for stat in ["speed", "toughness"]:
            current = stats.get(stat, 50)
            stats[stat] = max(current - 3, STAT_MIN)
        for stat in ["power", "technique"]:
            current = stats.get(stat, 50)
            stats[stat] = max(current - 2, STAT_MIN)

    fighter["stats"] = stats
    return fighter


def update_promotion_desperation(fighter: dict) -> dict:
    age = fighter.get("age", 25)
    tier = fighter.get("tier", "underground")
    peak_tier = fighter.get("peak_tier", "underground")

    if tier != "underground" or age < 28:
        return fighter

    desperation = fighter.get("promotion_desperation", 0.0)
    desperation += 0.15

    if age >= 30 and TIER_ORDER.get(peak_tier, 0) == 0:
        desperation = 1.0

    fighter["promotion_desperation"] = min(desperation, 1.0)
    return fighter


def generate_replacement_fighter(fighter_id_counter: int, season: int, rng: _random.Random = None, used_names: set = None) -> dict:
    if rng is None:
        rng = _random.Random()
    if used_names is None:
        used_names = set()

    age_weights = [5, 4, 3, 2, 1]
    ages = [18, 19, 20, 21, 22]
    age = rng.choices(ages, weights=age_weights, k=1)[0]

    target_total = rng.randint(140, 200)
    stats = _distribute_stats(target_total, rng)

    for _ in range(100):
        prefix = rng.choice(PREFIXES) if rng.random() < 0.4 else ""
        name = rng.choice(RING_NAMES)
        ring_name = f"{prefix} {name}".strip() if prefix else name
        if ring_name not in used_names:
            break
    used_names.add(ring_name)

    fighter_id = f"sim-{fighter_id_counter:04d}"
    focus = rng.choice(CORE_STATS)

    return {
        "id": fighter_id,
        "ring_name": ring_name,
        "real_name": ring_name,
        "age": age,
        "gender": rng.choice(["female", "male"]),
        "primary_archetype": "",
        "stats": stats,
        "record": {"wins": 0, "losses": 0, "draws": 0, "kos": 0, "submissions": 0},
        "condition": {"health_status": "healthy", "injuries": [], "recovery_days_remaining": 0, "morale": "neutral", "momentum": "neutral"},
        "tier": "underground",
        "status": "active",
        "training_focus": focus,
        "training_days_accumulated": 0.0,
        "training_streak": 0,
        "seasons_in_current_tier": 0,
        "career_season_count": 0,
        "peak_tier": "underground",
        "promotion_desperation": 0.0,
        "season_wins": 0,
        "season_losses": 0,
        "consecutive_losses": 0,
        "last_fight_date": None,
        "rivalries": [],
        "storyline_log": [],
        "moves": [],
        "_entered_season": season,
        "_entered_age": age,
    }


def _distribute_stats(target_total: int, rng: _random.Random) -> dict:
    raw = [rng.randint(25, 60) for _ in CORE_STATS]
    raw_total = sum(raw)
    scaled = [max(STAT_MIN, min(STAT_CAP, round(v * target_total / raw_total))) for v in raw]

    diff = target_total - sum(scaled)
    while diff != 0:
        idx = rng.randint(0, len(CORE_STATS) - 1)
        if diff > 0 and scaled[idx] < STAT_CAP:
            scaled[idx] += 1
            diff -= 1
        elif diff < 0 and scaled[idx] > STAT_MIN:
            scaled[idx] -= 1
            diff += 1

    stats = {}
    for i, stat_name in enumerate(CORE_STATS):
        stats[stat_name] = scaled[i]
    stats["supernatural"] = 0
    return stats
