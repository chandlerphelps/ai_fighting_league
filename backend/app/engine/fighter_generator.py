import uuid

from app.config import Config
from app.models.fighter import (
    Fighter, FightingStyle, PhysicalStats, CombatStats,
    PsychologicalStats, SupernaturalStats, Record, Condition,
)
from app.services.openrouter import call_openrouter_json


ARCHETYPES = [
    "The Prodigy", "The Veteran", "The Monster", "The Technician",
    "The Wildcard", "The Mystic", "The Survivor", "The Seductress/Seductor",
]

CHARACTER_PHILOSOPHY = """CORE DESIGN PHILOSOPHY:
1. Female fighters are sexy and appealing — crop tops, high-cut leotards, mesh panels, thigh-highs. Confidence and allure are features. Design for a male audience.
2. Men are bigger and stronger. Women win through seduction, charm, dirty tactics, psychological warfare, supernatural ability, technical mastery, speed, precision — NOT raw physical dominance.
3. Characters are interesting because of violence. What makes them compelling: how they hurt others (and feel about it), how they get hurt (and react). Every fighter has a relationship with violence.
4. Steal archetypes from popular media — anime, action movies, comics, wrestling, mythology, pulp fiction. A cyberpunk street samurai, a voodoo priestess, a cartel chemist who poisons opponents. Think beyond "MMA fighter with magic."

ARCHETYPE GUIDELINES:
- The Prodigy: Young, gifted, untested at highest level. Natural talent that borders on unfair.
- The Veteran: Battle-scarred, experienced, declining physically but sharp mentally.
- The Monster: Physically imposing, intimidating presence, raw power (MALE ONLY for physical dominance).
- The Technician: Precise, methodical, wins through superior technique and game planning.
- The Wildcard: Unpredictable, chaotic, fights differently every time.
- The Mystic: Supernatural connection, fights with otherworldly enhancement.
- The Survivor: Came from hardship, refuses to quit, thrives in adversity.
- The Seductress/Seductor: Uses charm, beauty, and psychological manipulation as weapons."""


def plan_roster(config: Config, slots: list[tuple[str, bool]]) -> list[dict]:
    slot_lines = []
    for i, (archetype, has_super) in enumerate(slots):
        super_tag = " [SUPERNATURAL]" if has_super else ""
        slot_lines.append(f"{i + 1}. {archetype}{super_tag}")

    prompt = f"""{CHARACTER_PHILOSOPHY}

You are planning a 16-fighter roster for the AI Fighting League. Each fighter must be COMPLETELY UNIQUE — no two should share the same country of origin, primary fighting style, body type, or visual concept.

Here are the {len(slots)} character slots to fill:
{chr(10).join(slot_lines)}

For each slot, create a fighter blueprint. Return a JSON array of {len(slots)} objects, one per slot, in order. Each object must have:
{{
  "ring_name": "<evocative 1-2 word ring name>",
  "real_name": "<authentic name for their cultural background>",
  "gender": "<male|female>",
  "age": <18-45>,
  "origin": "<specific city/region, country>",
  "alignment": "<face|heel|tweener>",
  "height": "<height in feet/inches>",
  "weight": "<weight in lbs>",
  "build": "<body type description>",
  "distinguishing_features": "<scars, tattoos, unique physical traits>",
  "ring_attire": "<detailed outfit description>",
  "primary_style": "<main fighting discipline>",
  "secondary_style": "<secondary discipline>",
  "concept": "<1-sentence creative pitch for this character>"
}}

DIVERSITY RULES:
- At least 6 female fighters and at least 6 male fighters
- Every fighter must come from a DIFFERENT country
- Every fighter must have a DIFFERENT primary fighting style
- Mix alignments: roughly equal face/heel/tweener split
- Vary body types, ages, and visual aesthetics widely
- [SUPERNATURAL] fighters should have concepts that naturally incorporate mystical/otherworldly elements

Return ONLY valid JSON — an array of {len(slots)} objects."""

    system_prompt = "You are a character designer for a fighting league. Plan a diverse, compelling roster. Always respond with valid JSON only."

    result = call_openrouter_json(prompt, config, system_prompt=system_prompt, temperature=0.9, max_tokens=8192)

    if isinstance(result, dict) and "roster" in result:
        result = result["roster"]
    if not isinstance(result, list):
        raise RuntimeError(f"Expected JSON array from roster planning, got {type(result)}")

    for i, bp in enumerate(result):
        if i < len(slots):
            bp["archetype"] = slots[i][0]
            bp["has_supernatural"] = slots[i][1]

    return result


def generate_fighter(
    config: Config, archetype: str = None, has_supernatural: bool = False,
    existing_fighters: list[dict] = None, blueprint: dict = None,
) -> Fighter:
    if blueprint:
        archetype = blueprint.get("archetype", archetype)
        has_supernatural = blueprint.get("has_supernatural", has_supernatural)

    supernatural_instruction = ""
    if has_supernatural:
        supernatural_instruction = """This fighter HAS supernatural abilities. Give 1-2 supernatural stats values between 20-50. The rest should be 0. Choose from: arcane_power, chi_mastery, elemental_affinity, dark_arts. The supernatural ability should tie into their backstory and fighting style naturally."""
    else:
        supernatural_instruction = """This fighter has NO supernatural abilities. All supernatural stats must be 0."""

    archetype_text = f"Primary archetype: {archetype}" if archetype else "Choose a fitting archetype"

    blueprint_text = ""
    if blueprint:
        blueprint_text = f"""

LOCKED CHARACTER IDENTITY (you MUST use these exactly):
- Ring Name: {blueprint.get('ring_name', '')}
- Real Name: {blueprint.get('real_name', '')}
- Gender: {blueprint.get('gender', '')}
- Age: {blueprint.get('age', '')}
- Origin: {blueprint.get('origin', '')}
- Alignment: {blueprint.get('alignment', '')}
- Height: {blueprint.get('height', '')}
- Weight: {blueprint.get('weight', '')}
- Build: {blueprint.get('build', '')}
- Distinguishing Features: {blueprint.get('distinguishing_features', '')}
- Ring Attire: {blueprint.get('ring_attire', '')}
- Primary Style: {blueprint.get('primary_style', '')}
- Secondary Style: {blueprint.get('secondary_style', '')}
- Character Concept: {blueprint.get('concept', '')}

You MUST use the identity fields above verbatim in your JSON output. Your job is to flesh out: backstory, personality_traits, fears_quirks, signature_move, finishing_move, known_weaknesses, and all stats — while staying true to the character concept."""

    existing_roster_text = ""
    if not blueprint and existing_fighters:
        roster_lines = []
        for ef in existing_fighters:
            style = ef.get("fighting_style", {})
            if isinstance(style, str):
                style_text = style
            else:
                primary = style.get("primary_style", "?")
                secondary = style.get("secondary_style", "")
                style_text = f"{primary} / {secondary}" if secondary else primary
            line = (
                f"- {ef.get('ring_name', '?')} ({ef.get('gender', '?')}, {ef.get('height', '?')})"
                f" — {ef.get('alignment', '?')}, from {ef.get('origin', '?')}"
                f" | {ef.get('build', '?')}, {ef.get('distinguishing_features', '?')}"
                f" | Attire: {ef.get('ring_attire', '?')}"
                f" | {style_text}"
            )
            roster_lines.append(line)
        existing_roster_text = (
            "\n\nEXISTING ROSTER (you MUST create a COMPLETELY DIFFERENT character — "
            "no duplicate ring names, different origin/nationality, different fighting style concept, "
            "different physical appearance, different personality):\n"
            + "\n".join(roster_lines)
        )

    prompt = f"""{CHARACTER_PHILOSOPHY}

Generate a unique fighter for the AI Fighting League. {archetype_text}.{blueprint_text}{existing_roster_text}

{supernatural_instruction}

STAT CONSTRAINTS:
- 15 core stats (5 physical + 5 combat + 5 psychological), each rated 1-100
- Individual stats should fall in the 15-95 range
- The 15 core stats MUST total between 900 and 1100
- No fighter should be elite at everything — balance strengths with clear weaknesses
- Stats should reflect the archetype (Monsters have high strength/durability, Technicians have high fight_iq/defense, etc.)

Return ONLY valid JSON with this exact structure:
{{
  "ring_name": "<evocative 1-2 word ring name>",
  "real_name": "<authentic name for their cultural background>",
  "age": <18-45>,
  "origin": "<specific city/region, country>",
  "gender": "<male|female>",
  "alignment": "<face|heel|tweener>",
  "height": "<height in feet/inches>",
  "weight": "<weight in lbs>",
  "build": "<body type description>",
  "distinguishing_features": "<scars, tattoos, unique physical traits>",
  "ring_attire": "<detailed outfit description>",
  "backstory": "<2-3 paragraphs origin story, motivation, personality>",
  "personality_traits": ["<trait1>", "<trait2>", "<trait3>", "<trait4>"],
  "fears_quirks": ["<fear/quirk1>", "<fear/quirk2>"],
  "fighting_style": {{
    "primary_style": "<main fighting discipline>",
    "secondary_style": "<secondary discipline>",
    "signature_move": "<named signature move with description>",
    "finishing_move": "<named finishing move with description>",
    "known_weaknesses": ["<weakness1>", "<weakness2>"]
  }},
  "physical_stats": {{
    "strength": <15-95>,
    "speed": <15-95>,
    "endurance": <15-95>,
    "durability": <15-95>,
    "recovery": <15-95>
  }},
  "combat_stats": {{
    "striking": <15-95>,
    "grappling": <15-95>,
    "defense": <15-95>,
    "fight_iq": <15-95>,
    "finishing_instinct": <15-95>
  }},
  "psychological_stats": {{
    "aggression": <15-95>,
    "composure": <15-95>,
    "confidence": <15-95>,
    "resilience": <15-95>,
    "killer_instinct": <15-95>
  }},
  "supernatural_stats": {{
    "arcane_power": <0-50>,
    "chi_mastery": <0-50>,
    "elemental_affinity": <0-50>,
    "dark_arts": <0-50>
  }}
}}"""

    system_prompt = "You are a character designer for a fighting league. Create unique, compelling fighters with rich backstories. Always respond with valid JSON only."

    result = call_openrouter_json(prompt, config, system_prompt=system_prompt, temperature=0.9)

    fighter_id = f"f_{uuid.uuid4().hex[:8]}"

    physical = _extract_stats(result.get("physical_stats", {}), PhysicalStats)
    combat = _extract_stats(result.get("combat_stats", {}), CombatStats)
    psychological = _extract_stats(result.get("psychological_stats", {}), PsychologicalStats)
    supernatural = _extract_supernatural(result.get("supernatural_stats", {}), has_supernatural, config)

    _normalize_core_stats(physical, combat, psychological, config)

    style_data = result.get("fighting_style", {})
    fighting_style = FightingStyle(
        primary_style=style_data.get("primary_style", ""),
        secondary_style=style_data.get("secondary_style", ""),
        signature_move=style_data.get("signature_move", ""),
        finishing_move=style_data.get("finishing_move", ""),
        known_weaknesses=style_data.get("known_weaknesses", []),
    )

    return Fighter(
        id=fighter_id,
        ring_name=result.get("ring_name", "Unknown"),
        real_name=result.get("real_name", "Unknown"),
        age=result.get("age", 25),
        origin=result.get("origin", "Unknown"),
        alignment=result.get("alignment", "tweener"),
        gender=result.get("gender", ""),
        height=result.get("height", ""),
        weight=result.get("weight", ""),
        build=result.get("build", ""),
        distinguishing_features=result.get("distinguishing_features", ""),
        ring_attire=result.get("ring_attire", ""),
        backstory=result.get("backstory", ""),
        personality_traits=result.get("personality_traits", []),
        fears_quirks=result.get("fears_quirks", []),
        fighting_style=fighting_style,
        physical_stats=physical,
        combat_stats=combat,
        psychological_stats=psychological,
        supernatural_stats=supernatural,
        record=Record(),
        condition=Condition(),
        storyline_log=[],
        rivalries=[],
        last_fight_date=None,
        ranking=None,
    )


def _extract_stats(data: dict, stat_cls):
    fields = stat_cls.__dataclass_fields__
    kwargs = {}
    for field_name in fields:
        val = data.get(field_name, 50)
        kwargs[field_name] = max(15, min(95, int(val)))
    return stat_cls(**kwargs)


def _extract_supernatural(data: dict, has_supernatural: bool, config: Config) -> SupernaturalStats:
    if not has_supernatural:
        return SupernaturalStats()

    return SupernaturalStats(
        arcane_power=max(0, min(config.supernatural_cap, int(data.get("arcane_power", 0)))),
        chi_mastery=max(0, min(config.supernatural_cap, int(data.get("chi_mastery", 0)))),
        elemental_affinity=max(0, min(config.supernatural_cap, int(data.get("elemental_affinity", 0)))),
        dark_arts=max(0, min(config.supernatural_cap, int(data.get("dark_arts", 0)))),
    )


def _normalize_core_stats(physical: PhysicalStats, combat: CombatStats, psychological: PsychologicalStats, config: Config):
    total = physical.total() + combat.total() + psychological.total()

    if config.min_total_stats <= total <= config.max_total_stats:
        return

    target = (config.min_total_stats + config.max_total_stats) // 2
    ratio = target / total if total > 0 else 1.0

    for stat_group in [physical, combat, psychological]:
        for field_name in stat_group.__dataclass_fields__:
            old_val = getattr(stat_group, field_name)
            new_val = max(15, min(95, round(old_val * ratio)))
            setattr(stat_group, field_name, new_val)
