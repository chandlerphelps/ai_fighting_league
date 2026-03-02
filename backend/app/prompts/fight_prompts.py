SYSTEM_PROMPT_FIGHT_ANALYST = (
    "You are a fight analyst. Analyze matchups objectively based on fighter stats, "
    "styles, and conditions. Always respond with valid JSON only."
)

SYSTEM_PROMPT_FIGHT_CHOREOGRAPHER = (
    "You are a fight choreographer. Return concise JSON fight moments. "
    "Each moment is one specific strike or grappling action."
)


def build_probability_prompt(
    f1_name: str,
    f1_stats: dict,
    f1_record: dict,
    f1_condition: str,
    f2_name: str,
    f2_stats: dict,
    f2_record: dict,
    f2_condition: str,
    rivalry_text: str,
) -> str:
    return f"""Analyze this fighting matchup and return a JSON probability assessment. All fights end in KO.

FIGHTER 1: {f1_name}
- Stats: {f1_stats}
- Record: {f1_record}
- Condition: {f1_condition}

FIGHTER 2: {f2_name}
- Stats: {f2_stats}
- Record: {f2_record}
- Condition: {f2_condition}
{rivalry_text}

Stats are: power (striking force), speed (quickness/reflexes), technique (skill/fight IQ/defense), toughness (durability/endurance/recovery), supernatural (optional supernatural ability, 0 = none).

Return ONLY valid JSON with this exact structure:
{{
  "fighter1_win_prob": <float between 0.05 and 0.95>,
  "fighter2_win_prob": <float between 0.05 and 0.95, must sum to ~1.0 with fighter1_win_prob>,
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"]
}}

Supernatural abilities should be factored as a modest edge, not a dominator."""


def build_moments_prompt(
    target: int,
    f1_name: str,
    f1_id: str,
    f1_build: str,
    f1_height: str,
    f1_weight: str,
    f1_stats: dict,
    f2_name: str,
    f2_id: str,
    f2_build: str,
    f2_height: str,
    f2_weight: str,
    f2_stats: dict,
    winner_name: str,
    loser_name: str,
) -> str:
    return f"""Generate exactly {target} key moments for this fight. Every fight ends in KO.

FIGHTER 1: {f1_name} (ID: {f1_id})
- Build: {f1_build}, {f1_height}, {f1_weight}
- Stats: Power {f1_stats.get('power', 50)}, Speed {f1_stats.get('speed', 50)}, Technique {f1_stats.get('technique', 50)}

FIGHTER 2: {f2_name} (ID: {f2_id})
- Build: {f2_build}, {f2_height}, {f2_weight}
- Stats: Power {f2_stats.get('power', 50)}, Speed {f2_stats.get('speed', 50)}, Technique {f2_stats.get('technique', 50)}

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
