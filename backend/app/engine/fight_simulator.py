import random
import uuid
from dataclasses import asdict

from app.config import Config
from app.models.match import MatchupAnalysis, MatchOutcome, Match
from app.services import data_manager


VALID_METHODS = ["ko_tko", "submission", "decision_unanimous", "decision_split"]


def determine_outcome(
    fighter1: dict, fighter2: dict, analysis: MatchupAnalysis, config: Config
) -> MatchOutcome:
    if random.random() < config.draw_probability:
        return MatchOutcome(
            winner_id="",
            loser_id=None,
            method="draw",
            round_ended=config.rounds_per_fight,
            fighter1_performance="competitive",
            fighter2_performance="competitive",
            fighter1_injuries=_roll_injuries("decision", config, 0.1),
            fighter2_injuries=_roll_injuries("decision", config, 0.1),
            is_draw=True,
        )

    f1_id = fighter1["id"]
    f2_id = fighter2["id"]

    if random.random() < analysis.fighter1_win_prob:
        winner_id, loser_id = f1_id, f2_id
        winner_methods = analysis.fighter1_methods
        prob = analysis.fighter1_win_prob
    else:
        winner_id, loser_id = f2_id, f1_id
        winner_methods = analysis.fighter2_methods
        prob = analysis.fighter2_win_prob

    method = _roll_method(winner_methods)
    round_ended = _roll_round(method, config.rounds_per_fight)
    winner_perf, loser_perf = _assess_performance(prob, method)

    loser_injury_base = {"ko_tko": 0.40, "submission": 0.30}.get(method, 0.15)
    winner_injury_base = 0.10

    return MatchOutcome(
        winner_id=winner_id,
        loser_id=loser_id,
        method=method,
        round_ended=round_ended,
        fighter1_performance=winner_perf if winner_id == f1_id else loser_perf,
        fighter2_performance=winner_perf if winner_id == f2_id else loser_perf,
        fighter1_injuries=_roll_injuries(method, config, winner_injury_base if winner_id == f1_id else loser_injury_base),
        fighter2_injuries=_roll_injuries(method, config, winner_injury_base if winner_id == f2_id else loser_injury_base),
        is_draw=False,
    )


def _roll_method(methods: dict) -> str:
    if not methods:
        methods = {
            "ko_tko": 0.3,
            "submission": 0.2,
            "decision_unanimous": 0.35,
            "decision_split": 0.15,
        }

    items = list(methods.items())
    total = sum(w for _, w in items)
    if total <= 0:
        return random.choice(VALID_METHODS)

    roll = random.random() * total
    cumulative = 0
    for method, weight in items:
        cumulative += weight
        if roll <= cumulative:
            return method
    return items[-1][0]


def _roll_round(method: str, max_rounds: int) -> int:
    if method in ("decision_unanimous", "decision_split"):
        return max_rounds

    if method == "ko_tko":
        weights = [0.30, 0.40, 0.30]
    elif method == "submission":
        weights = [0.15, 0.35, 0.50]
    else:
        weights = [0.33, 0.34, 0.33]

    weights = weights[:max_rounds]
    total = sum(weights)
    roll = random.random() * total
    cumulative = 0
    for i, w in enumerate(weights):
        cumulative += w
        if roll <= cumulative:
            return i + 1
    return max_rounds


def _assess_performance(winner_prob: float, method: str) -> tuple[str, str]:
    if winner_prob >= 0.70:
        winner_perf = "dominant"
        loser_perf = "poor"
    elif winner_prob >= 0.55:
        winner_perf = "competitive"
        loser_perf = "competitive"
    elif winner_prob >= 0.35:
        winner_perf = "competitive"
        loser_perf = "competitive"
    else:
        winner_perf = "dominant"
        loser_perf = "poor"

    if method == "ko_tko" and winner_prob < 0.35:
        winner_perf = "dominant"

    return winner_perf, loser_perf


def _roll_injuries(method: str, config: Config, base_chance: float) -> list[dict]:
    if random.random() > base_chance:
        return []

    severity_roll = random.random()
    if severity_roll < 0.60:
        severity = "minor"
        recovery_range = config.minor_recovery
    elif severity_roll < 0.85:
        severity = "moderate"
        recovery_range = config.moderate_recovery
    else:
        severity = "severe"
        recovery_range = config.severe_recovery

    recovery_days = random.randint(recovery_range[0], recovery_range[1])

    injury_types = {
        "ko_tko": ["concussion", "facial laceration", "broken nose", "orbital fracture"],
        "submission": ["hyperextended elbow", "torn ligament", "neck strain", "dislocated shoulder"],
    }
    default_types = ["bruised ribs", "sprained wrist", "muscle strain", "cut above eye"]
    injury_type = random.choice(injury_types.get(method, default_types))

    return [{
        "type": injury_type,
        "severity": severity,
        "recovery_days_remaining": recovery_days,
    }]


def calculate_probabilities(
    fighter1: dict, fighter2: dict, config: Config, rivalry_context: dict = None
) -> MatchupAnalysis:
    from app.services.openrouter import call_openrouter_json

    f1_name = fighter1.get("ring_name", "Fighter 1")
    f2_name = fighter2.get("ring_name", "Fighter 2")

    rivalry_text = ""
    if rivalry_context:
        rivalry_text = f"""
RIVALRY CONTEXT: These fighters have fought {rivalry_context.get('fights', 0)} times before.
{f1_name} has won {rivalry_context.get('fighter1_wins', 0)} and {f2_name} has won {rivalry_context.get('fighter2_wins', 0)}.
This is a known rivalry — factor in the psychological weight of their history."""

    prompt = f"""Analyze this fighting matchup and return a JSON probability assessment.

FIGHTER 1: {f1_name}
- Stats: {fighter1.get('stats', {})}
- Record: {fighter1.get('record', {})}
- Condition: {fighter1.get('condition', {}).get('health_status', 'healthy')}, Morale: {fighter1.get('condition', {}).get('morale', 'neutral')}, Momentum: {fighter1.get('condition', {}).get('momentum', 'neutral')}

FIGHTER 2: {f2_name}
- Stats: {fighter2.get('stats', {})}
- Record: {fighter2.get('record', {})}
- Condition: {fighter2.get('condition', {}).get('health_status', 'healthy')}, Morale: {fighter2.get('condition', {}).get('morale', 'neutral')}, Momentum: {fighter2.get('condition', {}).get('momentum', 'neutral')}
{rivalry_text}

Stats are: power (striking/grappling force), speed (quickness/reflexes), technique (skill/fight IQ/defense), toughness (durability/endurance/recovery), supernatural (optional supernatural ability, 0 = none).

Return ONLY valid JSON with this exact structure:
{{
  "fighter1_win_prob": <float between 0.05 and 0.95>,
  "fighter2_win_prob": <float between 0.05 and 0.95, must sum to ~1.0 with fighter1_win_prob>,
  "fighter1_methods": {{"ko_tko": <float>, "submission": <float>, "decision_unanimous": <float>, "decision_split": <float>}},
  "fighter2_methods": {{"ko_tko": <float>, "submission": <float>, "decision_unanimous": <float>, "decision_split": <float>}},
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"]
}}

Supernatural abilities should be factored as a modest edge, not a dominator. Method probabilities for each fighter should sum to approximately 1.0."""

    system_prompt = "You are a fight analyst. Analyze matchups objectively based on fighter stats, styles, and conditions. Always respond with valid JSON only."

    result = call_openrouter_json(prompt, config, system_prompt=system_prompt)

    f1_prob = max(0.05, min(0.95, float(result.get("fighter1_win_prob", 0.5))))
    f2_prob = 1.0 - f1_prob

    return MatchupAnalysis(
        fighter1_win_prob=round(f1_prob, 3),
        fighter2_win_prob=round(f2_prob, 3),
        fighter1_methods=result.get("fighter1_methods", {"ko_tko": 0.3, "submission": 0.2, "decision_unanimous": 0.35, "decision_split": 0.15}),
        fighter2_methods=result.get("fighter2_methods", {"ko_tko": 0.3, "submission": 0.2, "decision_unanimous": 0.35, "decision_split": 0.15}),
        key_factors=result.get("key_factors", []),
    )


def generate_narrative(
    fighter1: dict, fighter2: dict, analysis: MatchupAnalysis, outcome: MatchOutcome, config: Config
) -> str:
    from app.services.openrouter import call_openrouter

    f1_name = fighter1.get("ring_name", "Fighter 1")
    f2_name = fighter2.get("ring_name", "Fighter 2")

    if outcome.is_draw:
        outcome_text = f"The fight ends in a DRAW after {outcome.round_ended} rounds."
    else:
        winner_name = f1_name if outcome.winner_id == fighter1["id"] else f2_name
        loser_name = f2_name if outcome.winner_id == fighter1["id"] else f1_name
        method_display = outcome.method.replace("_", " ").upper()
        outcome_text = f"{winner_name} defeats {loser_name} by {method_display} in Round {outcome.round_ended}."

    f1_stats = fighter1.get('stats', {})
    f2_stats = fighter2.get('stats', {})

    prompt = f"""Write a dramatic fight narrative for this match. The outcome is predetermined — you must write toward it.

FIGHTER 1: {f1_name}
- Real Name: {fighter1.get('real_name', '')}
- Origin: {fighter1.get('origin', '')}
- Build: {fighter1.get('build', '')}, {fighter1.get('height', '')}, {fighter1.get('weight', '')}
- Distinguishing Features: {fighter1.get('distinguishing_features', '')}
- Attire: {fighter1.get('ring_attire', '')}
- Stats: Power {f1_stats.get('power', 50)}, Speed {f1_stats.get('speed', 50)}, Technique {f1_stats.get('technique', 50)}, Toughness {f1_stats.get('toughness', 50)}, Supernatural {f1_stats.get('supernatural', 0)}

FIGHTER 2: {f2_name}
- Real Name: {fighter2.get('real_name', '')}
- Origin: {fighter2.get('origin', '')}
- Build: {fighter2.get('build', '')}, {fighter2.get('height', '')}, {fighter2.get('weight', '')}
- Distinguishing Features: {fighter2.get('distinguishing_features', '')}
- Attire: {fighter2.get('ring_attire', '')}
- Stats: Power {f2_stats.get('power', 50)}, Speed {f2_stats.get('speed', 50)}, Technique {f2_stats.get('technique', 50)}, Toughness {f2_stats.get('toughness', 50)}, Supernatural {f2_stats.get('supernatural', 0)}

MATCHUP ANALYSIS:
- Key Factors: {', '.join(analysis.key_factors)}

PREDETERMINED OUTCOME: {outcome_text}

Write the narrative including:
1. Pre-fight scene setting (1 paragraph — atmosphere, crowd, fighters entering)
2. Round-by-round action (key moments, momentum shifts)
3. The finish or decision
4. Post-fight aftermath (winner's reaction, loser's state, any story hooks for future)

Use each fighter's physical description, attire, and distinguishing features to make the prose vivid. If a fighter has supernatural > 0, weave subtle supernatural flavor into key moments — but keep it grounded.

Target length: {config.narrative_min_words}-{config.narrative_max_words} words of dramatic prose. Write in present tense for immediacy."""

    system_prompt = "You are an elite combat sports writer. Write vivid, dramatic fight narratives that bring characters to life. Your prose should be exciting and immersive, referencing each fighter's unique traits and fighting style."

    narrative = call_openrouter(
        prompt, config, model=config.narrative_model, system_prompt=system_prompt, temperature=0.8
    )
    return narrative


def run_fight(
    fighter1_id: str, fighter2_id: str, event_id: str, match_date: str, config: Config
) -> Match:
    fighter1 = data_manager.load_fighter(fighter1_id, config)
    fighter2 = data_manager.load_fighter(fighter2_id, config)

    if not fighter1 or not fighter2:
        raise ValueError(f"Could not load fighters: {fighter1_id}, {fighter2_id}")

    fighter1_snapshot = dict(fighter1)
    fighter2_snapshot = dict(fighter2)

    rivalry_context = _get_rivalry_context(fighter1_id, fighter2_id, config)

    analysis = calculate_probabilities(fighter1, fighter2, config, rivalry_context)
    outcome = determine_outcome(fighter1, fighter2, analysis, config)
    narrative = generate_narrative(fighter1, fighter2, analysis, outcome, config)

    match_id = f"m_{uuid.uuid4().hex[:8]}"

    return Match(
        id=match_id,
        event_id=event_id,
        date=match_date,
        fighter1_id=fighter1_id,
        fighter1_name=fighter1.get("ring_name", ""),
        fighter2_id=fighter2_id,
        fighter2_name=fighter2.get("ring_name", ""),
        analysis=analysis,
        outcome=outcome,
        narrative=narrative,
        fighter1_snapshot=fighter1_snapshot,
        fighter2_snapshot=fighter2_snapshot,
    )


def _get_rivalry_context(fighter1_id: str, fighter2_id: str, config: Config) -> dict | None:
    ws = data_manager.load_world_state(config)
    if not ws:
        return None

    for rivalry in ws.get("rivalry_graph", []):
        ids = {rivalry.get("fighter1_id"), rivalry.get("fighter2_id")}
        if {fighter1_id, fighter2_id} == ids:
            return rivalry
    return None
