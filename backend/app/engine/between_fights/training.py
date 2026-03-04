import random as _random

TRAINING_RATES = {
    "apex": 0.035,
    "contender": 0.028,
    "underground": 0.023,
}

FIGHT_CAMP_BOOSTS = {
    "apex": 4,
    "contender": 3,
    "underground": 2,
}

CORE_STATS = ["power", "speed", "technique", "toughness"]
TRAINABLE_STATS = CORE_STATS + ["supernatural"]

STAT_CAP = 95
OVERTRAINING_THRESHOLD = 90
OVERTRAINING_INJURY_CHANCE = 0.05


MORALE_TRAINING_MULTIPLIERS = {
    "high": 1.3,
    "neutral": 1.0,
    "low": 0.6,
}


def process_daily_training(fighter: dict, rng: _random.Random = None) -> dict:
    if rng is None:
        rng = _random.Random()

    condition = fighter.get("condition", {})
    if condition.get("health_status") != "healthy":
        fighter["training_streak"] = 0
        return fighter

    work_ethic = fighter.get("work_ethic", 1.0)
    if work_ethic < 1.0 and rng.random() < (1.0 - work_ethic):
        fighter["training_streak"] = 0
        return fighter

    tier = fighter.get("tier", "underground")
    rate = TRAINING_RATES.get(tier, 0.08)

    age = fighter.get("age", 25)
    if age >= 36:
        rate *= 0.4
    elif age >= 32:
        rate *= 0.7

    rate *= fighter.get("learning_rate", 1.0)

    morale = condition.get("morale", "neutral")
    rate *= MORALE_TRAINING_MULTIPLIERS.get(morale, 1.0)

    if work_ethic >= 1.0:
        rate += (work_ethic - 1.0) * 0.5 * TRAINING_RATES.get(tier, 0.08)

    focus = fighter.get("training_focus", "technique")

    if focus not in TRAINABLE_STATS:
        focus = "technique"

    fighter["training_streak"] = fighter.get("training_streak", 0) + 1
    fighter["training_days_accumulated"] = fighter.get("training_days_accumulated", 0.0) + rate

    stats = fighter.get("stats", {})
    if fighter["training_days_accumulated"] >= 1.0:
        fighter["training_days_accumulated"] -= 1.0
        current_val = stats.get(focus, 50)
        if current_val < STAT_CAP:
            stats[focus] = min(current_val + 1, STAT_CAP)
            fighter["stats"] = stats

    if fighter["training_streak"] > OVERTRAINING_THRESHOLD:
        if rng.random() < OVERTRAINING_INJURY_CHANCE:
            recovery_days = rng.randint(3, 5)
            fighter["condition"] = {
                "health_status": "injured",
                "injuries": [{"type": "overtraining strain", "severity": "minor", "recovery_days_remaining": recovery_days}],
                "recovery_days_remaining": recovery_days,
                "morale": condition.get("morale", "neutral"),
                "momentum": condition.get("momentum", "neutral"),
            }
            fighter["training_streak"] = 0

    return fighter


def apply_fight_camp_boost(fighter: dict) -> dict:
    tier = fighter.get("tier", "underground")
    boost = FIGHT_CAMP_BOOSTS.get(tier, 2)
    focus = fighter.get("training_focus", "technique")

    if focus not in TRAINABLE_STATS:
        focus = "technique"

    boosted_stats = dict(fighter.get("stats", {}))
    current_val = boosted_stats.get(focus, 50)
    boosted_stats[focus] = min(current_val + boost, STAT_CAP)

    return boosted_stats
