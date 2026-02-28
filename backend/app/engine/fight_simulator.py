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


TIER_PROMPT_KEYS = {
    "sfw": "image_prompt_sfw",
    "barely": "image_prompt",
    "nsfw": "image_prompt_nsfw",
}


MOMENT_VARIANTS = ["A", "B", "C", "D", "E"]


def _extract_moment_context(fighter1, fighter2, attacker_id, action, tier):
    from app.engine.image_style import ART_STYLE_BASE, get_art_style_tail

    tier_key = TIER_PROMPT_KEYS.get(tier, "image_prompt")

    if attacker_id == fighter1["id"]:
        attacker, defender = fighter1, fighter2
    else:
        attacker, defender = fighter2, fighter1

    atk_prompt = attacker.get(tier_key, attacker.get("image_prompt", {}))
    def_prompt = defender.get(tier_key, defender.get("image_prompt", {}))
    atk_body = atk_prompt.get("body_parts", "")
    atk_clothing = atk_prompt.get("clothing", "")
    def_body = def_prompt.get("body_parts", "")
    def_clothing = def_prompt.get("clothing", "")

    atk_name = attacker.get("ring_name", "Attacker")
    def_name = defender.get("ring_name", "Defender")
    atk_gender = attacker.get("gender", "female")
    def_gender = defender.get("gender", "female")
    atk_height = attacker.get("height", "")
    def_height = defender.get("height", "")

    atk_desc = ", ".join(p for p in [atk_body, atk_clothing] if p)
    def_desc = ", ".join(p for p in [def_body, def_clothing] if p)

    ref_sheet = "first image is the character sheet for the attacking fighter, second image is the character sheet for the defending fighter"
    consistency = "exactly two distinct characters, each maintains their exact original design from their reference sheet"
    tail = get_art_style_tail(atk_gender)

    return {
        "ART_STYLE_BASE": ART_STYLE_BASE,
        "atk_name": atk_name, "def_name": def_name,
        "atk_gender": atk_gender, "def_gender": def_gender,
        "atk_height": atk_height, "def_height": def_height,
        "atk_desc": atk_desc, "def_desc": def_desc,
        "atk_body": atk_body, "atk_clothing": atk_clothing,
        "def_body": def_body, "def_clothing": def_clothing,
        "action": action,
        "ref_sheet": ref_sheet, "consistency": consistency, "tail": tail,
    }


def _build_variant_a(c):
    action_composition = (
        f"dynamic combat action shot, {c['atk_name']} landing {c['action']}, "
        f"dramatic impact moment, motion blur on strike, "
        f"arena lighting, dark moody atmosphere, "
        f"full body visible for both fighters"
    )
    impact_reaction = (
        f"{c['def_name']} recoiling from the hit, grimacing in pain, "
        f"head snapping back, sweat and spit flying from impact, staggering off-balance"
    )
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_desc']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_desc']}"
    return [
        c["ART_STYLE_BASE"], action_composition, impact_reaction,
        c["ref_sheet"], atk_fighter, def_fighter, c["tail"], c["consistency"],
    ]


def _build_variant_b(c):
    defender_reaction = (
        f"devastating impact on {c['def_name']}, face contorted in agony, "
        f"body crumpling from the force, eyes wide with shock and pain, "
        f"jaw twisted from the blow, sweat spraying on impact"
    )
    attack = (
        f"{c['atk_name']} delivering {c['action']} with full force, "
        f"fist connecting flush, muscles tensed at moment of impact"
    )
    scene = "dynamic combat shot, arena lighting, dark moody atmosphere, full body visible for both fighters, motion blur on strike"
    def_fighter = f"defending fighter taking the hit ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_desc']}"
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_desc']}"
    return [
        c["ART_STYLE_BASE"], defender_reaction, attack, scene,
        c["ref_sheet"], def_fighter, atk_fighter, c["tail"], c["consistency"],
    ]


def _build_variant_c(c):
    frozen_moment = (
        f"frozen instant of impact, {c['atk_name']}'s {c['action']} connecting hard against {c['def_name']}, "
        f"visible shockwave ripple at point of contact, skin deforming under the strike"
    )
    atk_detail = (
        f"{c['atk_name']} fully committed to the strike, fierce determined expression, "
        f"weight behind the blow, aggressive fighting stance"
    )
    def_detail = (
        f"{c['def_name']} absorbing the hit, face twisted in pain, eyes squeezed shut, "
        f"body buckling, guard broken, knocked off balance"
    )
    scene = "extreme dynamic angle, arena spotlights, dark moody atmosphere, full body visible for both fighters, speed lines and motion blur"
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_desc']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_desc']}"
    return [
        c["ART_STYLE_BASE"], frozen_moment, atk_detail, def_detail, scene,
        c["ref_sheet"], atk_fighter, def_fighter, c["tail"], c["consistency"],
    ]


def _build_variant_d(c):
    camera = (
        f"low-angle action shot focused on the point of impact, "
        f"close enough to see the damage, showing both fighters full body"
    )
    impact_desc = (
        f"{c['atk_name']} smashing {c['action']} into {c['def_name']}, "
        f"brutal visible contact, flesh compressing at strike point, "
        f"sweat droplets exploding off {c['def_name']}'s body"
    )
    expressions = (
        f"{c['atk_name']}: aggressive snarl, killer intent in eyes. "
        f"{c['def_name']}: mouth open in pain, eyes rolling, dazed expression, body going limp"
    )
    scene = "arena lighting, dark moody atmosphere, motion blur on the strike, dramatic volumetric lighting"
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_desc']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_desc']}"
    return [
        c["ART_STYLE_BASE"], camera, impact_desc, expressions, scene,
        c["ref_sheet"], atk_fighter, def_fighter, c["tail"], c["consistency"],
    ]


def _build_variant_e(c):
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_desc']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_desc']}"
    sequence = (
        f"the exact moment {c['atk_name']}'s {c['action']} lands square on {c['def_name']}, "
        f"{c['atk_name']} lunging forward with full body rotation behind the strike, "
        f"{c['def_name']}'s head whipping sideways from the force, "
        f"spit and sweat flying from {c['def_name']}'s face, "
        f"{c['def_name']}'s legs buckling, expression of shock and pain"
    )
    scene = (
        "brutal combat action shot, visceral impact, "
        "arena lighting, dark moody atmosphere, full body visible for both fighters, "
        "motion blur on strike, dramatic angle"
    )
    return [
        c["ART_STYLE_BASE"], c["ref_sheet"], atk_fighter, def_fighter,
        sequence, scene, c["tail"], c["consistency"],
    ]


def _e_sequence(c):
    return (
        f"the exact moment {c['atk_name']}'s {c['action']} lands square on {c['def_name']}, "
        f"{c['atk_name']} lunging forward with full body rotation behind the strike, "
        f"{c['def_name']}'s head whipping sideways from the force, "
        f"spit and sweat flying from {c['def_name']}'s face, "
        f"{c['def_name']}'s legs buckling, expression of shock and pain"
    )


def _e_scene():
    return (
        "brutal combat action shot, visceral impact, "
        "arena lighting, dark moody atmosphere, full body visible for both fighters, "
        "motion blur on strike, dramatic angle"
    )


def _build_variant_e1_no_body(c):
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_clothing']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_clothing']}"
    return [
        c["ART_STYLE_BASE"], c["ref_sheet"], atk_fighter, def_fighter,
        _e_sequence(c), _e_scene(), c["tail"], c["consistency"],
    ]


def _build_variant_e2_no_clothing(c):
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_body']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_body']}"
    return [
        c["ART_STYLE_BASE"], c["ref_sheet"], atk_fighter, def_fighter,
        _e_sequence(c), _e_scene(), c["tail"], c["consistency"],
    ]


def _build_variant_e3_no_body_or_clothing(c):
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']})"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']})"
    return [
        c["ART_STYLE_BASE"], c["ref_sheet"], atk_fighter, def_fighter,
        _e_sequence(c), _e_scene(), c["tail"], c["consistency"],
    ]


def _build_variant_e4_no_height(c):
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}): {c['atk_desc']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}): {c['def_desc']}"
    return [
        c["ART_STYLE_BASE"], c["ref_sheet"], atk_fighter, def_fighter,
        _e_sequence(c), _e_scene(), c["tail"], c["consistency"],
    ]


def _build_variant_e5_no_gender(c):
    atk_fighter = f"attacking fighter ({c['atk_name']}, {c['atk_height']}): {c['atk_desc']}"
    def_fighter = f"defending fighter ({c['def_name']}, {c['def_height']}): {c['def_desc']}"
    return [
        c["ART_STYLE_BASE"], c["ref_sheet"], atk_fighter, def_fighter,
        _e_sequence(c), _e_scene(), c["tail"], c["consistency"],
    ]


def _build_variant_e6_no_tail(c):
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_desc']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_desc']}"
    return [
        c["ART_STYLE_BASE"], c["ref_sheet"], atk_fighter, def_fighter,
        _e_sequence(c), _e_scene(), c["consistency"],
    ]


def _build_variant_e7_no_style(c):
    atk_fighter = f"attacking fighter ({c['atk_gender']}, {c['atk_name']}, {c['atk_height']}): {c['atk_desc']}"
    def_fighter = f"defending fighter ({c['def_gender']}, {c['def_name']}, {c['def_height']}): {c['def_desc']}"
    return [
        c["ref_sheet"], atk_fighter, def_fighter,
        _e_sequence(c), _e_scene(), c["tail"], c["consistency"],
    ]


_VARIANT_BUILDERS = {
    "A": _build_variant_a,
    "B": _build_variant_b,
    "C": _build_variant_c,
    "D": _build_variant_d,
    "E": _build_variant_e,
    "E1": _build_variant_e1_no_body,
    "E2": _build_variant_e2_no_clothing,
    "E3": _build_variant_e3_no_body_or_clothing,
    "E4": _build_variant_e4_no_height,
    "E5": _build_variant_e5_no_gender,
    "E6": _build_variant_e6_no_tail,
    "E7": _build_variant_e7_no_style,
}


def build_moment_image_prompt(
    fighter1: dict, fighter2: dict, attacker_id: str, action: str,
    tier: str = "barely", variant: str = "A",
) -> str:
    c = _extract_moment_context(fighter1, fighter2, attacker_id, action, tier)
    builder = _VARIANT_BUILDERS.get(variant, _build_variant_a)
    return ", ".join(builder(c))


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
