import random
import uuid

from app.config import Config
from app.models.match import MatchupAnalysis, MatchOutcome, Match, FightMoment
from app.services import data_manager


def _calc_moment_count(winner_prob: float) -> int:
    lopsidedness = abs(winner_prob - 0.5) * 2
    return 3 + round(3 * (1 - lopsidedness))


def _assess_performance(winner_prob: float) -> tuple[str, str]:
    if winner_prob >= 0.70:
        return "dominant", "poor"
    if winner_prob <= 0.30:
        return "dominant", "poor"
    return "competitive", "competitive"


def determine_outcome(
    fighter1: dict, fighter2: dict, analysis: MatchupAnalysis, config: Config
) -> MatchOutcome:
    f1_id = fighter1["id"]
    f2_id = fighter2["id"]

    if random.random() < analysis.fighter1_win_prob:
        winner_id, loser_id = f1_id, f2_id
        prob = analysis.fighter1_win_prob
    else:
        winner_id, loser_id = f2_id, f1_id
        prob = analysis.fighter2_win_prob

    winner_perf, loser_perf = _assess_performance(prob)
    moment_count = _calc_moment_count(prob)

    return MatchOutcome(
        winner_id=winner_id,
        loser_id=loser_id,
        method="ko_tko",
        round_ended=moment_count,
        fighter1_performance=winner_perf if winner_id == f1_id else loser_perf,
        fighter2_performance=winner_perf if winner_id == f2_id else loser_perf,
        fighter1_injuries=_roll_injuries(config, 0.10 if winner_id == f1_id else 0.40),
        fighter2_injuries=_roll_injuries(config, 0.10 if winner_id == f2_id else 0.40),
        is_draw=False,
    )


def _roll_injuries(config: Config, base_chance: float) -> list[dict]:
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
    injury_type = random.choice(["concussion", "facial laceration", "broken nose", "orbital fracture"])

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

    prompt = f"""Analyze this fighting matchup and return a JSON probability assessment. All fights end in KO.

FIGHTER 1: {f1_name}
- Stats: {fighter1.get('stats', {})}
- Record: {fighter1.get('record', {})}
- Condition: {fighter1.get('condition', {}).get('health_status', 'healthy')}, Morale: {fighter1.get('condition', {}).get('morale', 'neutral')}, Momentum: {fighter1.get('condition', {}).get('momentum', 'neutral')}

FIGHTER 2: {f2_name}
- Stats: {fighter2.get('stats', {})}
- Record: {fighter2.get('record', {})}
- Condition: {fighter2.get('condition', {}).get('health_status', 'healthy')}, Morale: {fighter2.get('condition', {}).get('morale', 'neutral')}, Momentum: {fighter2.get('condition', {}).get('momentum', 'neutral')}
{rivalry_text}

Stats are: power (striking force), speed (quickness/reflexes), technique (skill/fight IQ/defense), toughness (durability/endurance/recovery), supernatural (optional supernatural ability, 0 = none).

Return ONLY valid JSON with this exact structure:
{{
  "fighter1_win_prob": <float between 0.05 and 0.95>,
  "fighter2_win_prob": <float between 0.05 and 0.95, must sum to ~1.0 with fighter1_win_prob>,
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"]
}}

Supernatural abilities should be factored as a modest edge, not a dominator."""

    system_prompt = "You are a fight analyst. Analyze matchups objectively based on fighter stats, styles, and conditions. Always respond with valid JSON only."

    result = call_openrouter_json(prompt, config, system_prompt=system_prompt)

    f1_prob = max(0.05, min(0.95, float(result.get("fighter1_win_prob", 0.5))))
    f2_prob = 1.0 - f1_prob

    return MatchupAnalysis(
        fighter1_win_prob=round(f1_prob, 3),
        fighter2_win_prob=round(f2_prob, 3),
        key_factors=result.get("key_factors", []),
    )


def generate_moments(
    fighter1: dict, fighter2: dict, analysis: MatchupAnalysis, outcome: MatchOutcome, config: Config
) -> list[FightMoment]:
    from app.services.openrouter import call_openrouter_json

    f1_id = fighter1["id"]
    f2_id = fighter2["id"]
    f1_name = fighter1.get("ring_name", "Fighter 1")
    f2_name = fighter2.get("ring_name", "Fighter 2")

    winner_name = f1_name if outcome.winner_id == f1_id else f2_name
    loser_name = f2_name if outcome.winner_id == f1_id else f1_name
    target = outcome.round_ended

    prompt = f"""Generate exactly {target} key moments for this fight. Every fight ends in KO.

FIGHTER 1: {f1_name} (ID: {f1_id})
- Build: {fighter1.get('build', '')}, {fighter1.get('height', '')}, {fighter1.get('weight', '')}
- Stats: Power {fighter1.get('stats', {}).get('power', 50)}, Speed {fighter1.get('stats', {}).get('speed', 50)}, Technique {fighter1.get('stats', {}).get('technique', 50)}

FIGHTER 2: {f2_name} (ID: {f2_id})
- Build: {fighter2.get('build', '')}, {fighter2.get('height', '')}, {fighter2.get('weight', '')}
- Stats: Power {fighter2.get('stats', {}).get('power', 50)}, Speed {fighter2.get('stats', {}).get('speed', 50)}, Technique {fighter2.get('stats', {}).get('technique', 50)}

PREDETERMINED OUTCOME: {winner_name} knocks out {loser_name}

Return ONLY valid JSON with this structure:
{{
  "moments": [
    {{
      "moment_number": 1,
      "attacker_id": "<fighter ID of who lands the strike>",
      "action": "<short action phrase: e.g. 'spinning back kick to the ribs', 'right cross to the jaw', 'devastating uppercut'>"
    }}
  ]
}}

Rules:
- Each moment is one fighter landing a clean strike on the other
- The action should be a specific striking move (punch, kick, elbow, knee)
- Build momentum toward the KO — the last moment MUST be the knockout blow from {winner_name}
- Keep actions simple and visual — one clear strike per moment
- Both fighters should land hits, but {winner_name} should land more/harder ones"""

    system_prompt = "You are a fight choreographer. Return concise JSON fight moments. Each moment is one specific strike or grappling action."

    result = call_openrouter_json(prompt, config, model=config.narrative_model, system_prompt=system_prompt)
    raw_moments = result.get("moments", [])

    moments = []
    for m in raw_moments:
        attacker_id = m.get("attacker_id", "")
        if attacker_id == f1_id:
            attacker_name = f1_name
            defender_name = f2_name
        else:
            attacker_name = f2_name
            defender_name = f1_name

        action = m.get("action", "")
        description = f"{attacker_name} lands {action} on {defender_name}"

        moments.append(FightMoment(
            moment_number=m.get("moment_number", 0),
            description=description,
            attacker_id=attacker_id,
            action=action,
        ))

    return moments


def _generate_action_description(atk_name: str, def_name: str, action: str, config: Config) -> str:
    from app.services.openrouter import call_openrouter

    prompt = f"""You are writing a concise image prompt for a fight scene. The action is:

{atk_name}'s {action} on {def_name}

Write a SHORT image-generator description (3 sentences max) that specifies:
1. EXACTLY where on {def_name}'s body the strike makes contact (be anatomically specific)
2. {atk_name}'s exact body position, form, and facial expression appropriate for this specific strike
3. {def_name}'s exact physical reaction specific to WHERE they were hit (face hit = head snap, body hit = doubling over, etc.)
4. The single most cinematic camera angle to capture this specific strike

Rules:
- Be concise and visual — this is for an image generator
- Only describe what to show, never say what to avoid
- Use fighter names, not pronouns
- Return ONLY the description, nothing else"""

    system_prompt = "You are an expert fight choreographer writing concise image prompts. Return only the visual description."

    return call_openrouter(
        prompt, config, system_prompt=system_prompt,
        temperature=0.9, max_tokens=256,
    ).strip()


def build_moment_image_prompt(
    fighter1: dict, fighter2: dict, attacker_id: str, action: str,
    config: Config, tier: str = "barely",
) -> str:
    from app.engine.image_style import ART_STYLE_BASE, get_art_style_tail

    if attacker_id == fighter1["id"]:
        attacker, defender = fighter1, fighter2
    else:
        attacker, defender = fighter2, fighter1

    atk_name = attacker.get("ring_name", "Attacker")
    def_name = defender.get("ring_name", "Defender")
    atk_gender = attacker.get("gender", "female")

    ref_sheet = "first image is the character sheet for the attacking fighter, second image is the character sheet for the defending fighter"
    consistency = "exactly two distinct characters, each maintains their exact original design from their reference sheet"
    tail = get_art_style_tail(atk_gender)

    atk_fighter = f"attacking fighter ({atk_name})"
    def_fighter = f"defending fighter ({def_name})"

    action_desc = _generate_action_description(atk_name, def_name, action, config)

    scene = (
        "fighting game action shot, skilled brutal combat, visceral physical impact, "
        "arena lighting, dark moody atmosphere, full body visible for both fighters"
    )

    return ", ".join([
        ART_STYLE_BASE, ref_sheet, atk_fighter, def_fighter,
        action_desc, scene, tail, consistency,
    ])


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
    moments = generate_moments(fighter1, fighter2, analysis, outcome, config)

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
        moments=moments,
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
