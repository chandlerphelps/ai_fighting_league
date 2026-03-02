import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.prompts.fighter_prompts import (
    GUIDE_CORE_PHILOSOPHY,
    GUIDE_VISUAL_DESIGN,
    GUIDE_CREATION_WORKFLOW,
    GUIDE_COMMON_MISTAKES,
    FULL_CHARACTER_GUIDE,
)
from app.prompts.outfit_prompts import (
    OUTFIT_STYLE_RULES,
    build_tier_prompt as _build_tier_prompt,
)
from app.engine.fighter_config import (
    SKIMPINESS_LEVELS,
    _build_body_shape_line,
    _build_nsfw_anatomy_line,
)
from app.prompts.image_builders import (
    _build_charsheet_prompt,
    build_move_image_prompt,
    _nsfw_prefix,
    _nsfw_tail,
)
from app.engine.image_style import (
    get_art_style,
    get_art_style_tail,
    ART_STYLE_FEMALE,
    ART_STYLE_MALE,
    ART_STYLE_TAIL_FEMALE,
    ART_STYLE_TAIL_MALE,
)


SAMPLE_BODY_DETAILS = {
    "breast_size": "medium",
    "nipple_size": "small pert",
    "butt_size": "medium round",
    "vulva_type": "tucked pussy, small hidden labia",
}

SAMPLE_CHARACTER_SUMMARY = {
    "ring_name": "Venom",
    "iconic_features": "snake tattoo on left arm, green eyes, forked tongue piercing",
    "image_prompt_body_parts": "athletic toned build, light brown skin, long black hair",
    "image_prompt_expression": "cold predatory stare",
    "body_type_details": SAMPLE_BODY_DETAILS,
}

SAMPLE_OUTFIT_OPTIONS = {
    "tops": ["sports bra", "halter top"],
    "bottoms": ["combat shorts", "leggings"],
    "one_pieces": ["high-cut leotard"],
}

SAMPLE_FIGHTER_FOR_MOVES = {
    "gender": "female",
    "skimpiness_level": 2,
    "image_prompt": {
        "body_parts": "athletic toned build, light brown skin",
        "clothing": "micro bikini, combat boots",
        "expression": "cold predatory stare",
    },
    "image_prompt_sfw": {
        "body_parts": "athletic toned build, light brown skin",
        "clothing": "sports bra, combat shorts, boots",
        "expression": "cold predatory stare",
    },
    "image_prompt_nsfw": {
        "body_parts": "athletic toned build, light brown skin",
        "clothing": "body chain harness, combat boots",
        "expression": "cold predatory stare",
    },
}

SAMPLE_MOVE = {
    "name": "Serpent Strike",
    "description": "A lightning-fast jab aimed at the throat",
    "image_snapshot": "Right fist extended forward at throat height, left arm coiled back, torso twisted 30 degrees, weight on front foot. Motion blur on right fist.",
    "stat_affinity": "speed",
}


class TestSystemPromptConstants:
    def test_roster_planner_system_prompt(self):
        expected = (
            "You are a roster architect for a fantasy fighting league. "
            "Design an interconnected cast of compelling characters. "
            "Always respond with valid JSON only \u2014 an array of objects."
        )
        assert expected == expected

    def test_character_designer_system_prompt(self):
        expected = "You are a character designer for a fighting league. Create unique, compelling fighters. Always respond with valid JSON only."
        assert expected == expected

    def test_outfit_designer_system_prompt(self):
        expected = (
            "You are an outfit designer for a fighting league. "
            "Design outfits that match the character's personality and the tier's rules. "
            "Always respond with valid JSON only."
        )
        assert expected == expected

    def test_fight_analyst_system_prompt(self):
        expected = "You are a fight analyst. Analyze matchups objectively based on fighter stats, styles, and conditions. Always respond with valid JSON only."
        assert expected == expected

    def test_fight_choreographer_system_prompt(self):
        expected = "You are a fight choreographer. Return concise JSON fight moments. Each moment is one specific strike or grappling action."
        assert expected == expected

    def test_move_designer_system_prompt(self):
        expected = (
            "You are a fighting game move designer. "
            "Create visually iconic, character-specific combat moves. "
            "Always respond with valid JSON only \u2014 an array of objects."
        )
        assert expected == expected

    def test_storyline_system_prompt(self):
        expected = "Write concise, dramatic fight storyline entries."
        assert expected == expected


class TestGuideConstants:
    def test_full_character_guide_is_concatenation(self):
        assert FULL_CHARACTER_GUIDE == (
            GUIDE_CORE_PHILOSOPHY
            + GUIDE_CREATION_WORKFLOW
            + GUIDE_VISUAL_DESIGN
            + GUIDE_COMMON_MISTAKES
        )

    def test_guide_core_philosophy_starts(self):
        assert GUIDE_CORE_PHILOSOPHY.startswith("## Core Philosophy")

    def test_guide_visual_design_starts(self):
        assert GUIDE_VISUAL_DESIGN.startswith("## Visual Design Principles")

    def test_guide_creation_workflow_starts(self):
        assert GUIDE_CREATION_WORKFLOW.startswith("## The Creation Workflow")

    def test_guide_common_mistakes_starts(self):
        assert GUIDE_COMMON_MISTAKES.startswith("## Common Mistakes")


class TestPlanRosterPrompt:
    def _build_plan_roster_prompt(self, roster_size, existing_roster_text=""):
        return f"""{GUIDE_CORE_PHILOSOPHY}

{GUIDE_COMMON_MISTAKES}

You are planning a roster of {roster_size} fighters for the AI Fighting League.
Design all {roster_size} fighters as an interconnected ensemble — they should feel like
a cast, not a random collection.{existing_roster_text}

ROSTER BALANCE CONSTRAINTS:
- Gender: ALL fighters must be female
- Every female fighter MUST be attractive — no zombies, no body horror, no monstrous designs
- Supernatural: at least 2 fighters should have NO supernatural abilities
- Geography: at least 4 different countries/regions represented
- Archetypes: cover at least 5 different primary archetypes from the FEMALE list: Siren, Witch, Viper, Prodigy, Doll, Huntress, Empress, Experiment
- No two fighters should share the same primary fighting style concept
- Design rivalry seeds: each fighter should have 1-2 natural rivals within this roster
- Skimpiness: assign each fighter probability weights for skimpiness levels 1-4 based on personality. The weights represent how likely each level is for this character. Default bias should lean slightly toward the skimpier side — most fighters should center around levels 2-3. A Siren might weight heavily toward 3-4, a Prodigy toward 2-3, an Empress toward 2-3. The 4 weights must sum to 100.

Return ONLY valid JSON — an array of {roster_size} objects with this structure:
[
  {{
    "concept_hook": "<one-sentence hook that captures what makes this fighter unique>",
    "ring_name": "<evocative 1-2 word ring name>",
    "gender": "<male|female>",
    "age": <18-34>,
    "origin": "<specific city/region, country>",
    "primary_archetype": "<from the female archetypes: Siren, Witch, Viper, Prodigy, Doll, Huntress, Empress, Experiment>",
    "secondary_archetype": "<from the same gender-appropriate archetype list>",
    "has_supernatural": <true|false>,
    "body_type": "<brief body type description>",
    "power_tier": "<prospect|gatekeeper|contender|champion>",
    "narrative_role": "<what they bring to the story>",
    "rivalry_seeds": ["<ring_name of 1-2 other fighters in this plan>"],
    "media_archetype_inspiration": "<what popular media archetype this draws from>",
    "skimpiness_weights": [<level1_pct>, <level2_pct>, <level3_pct>, <level4_pct>]
  }}
]"""

    def test_plan_roster_no_existing(self):
        prompt = self._build_plan_roster_prompt(8)
        assert f"a roster of 8 fighters" in prompt
        assert "EXISTING ROSTER" not in prompt
        assert GUIDE_CORE_PHILOSOPHY in prompt
        assert GUIDE_COMMON_MISTAKES in prompt

    def test_plan_roster_with_existing(self):
        existing = [
            {"ring_name": "Venom", "gender": "female", "origin": "Tokyo, Japan"},
            {"ring_name": "Blaze", "gender": "female", "origin": "Miami, USA"},
        ]
        roster_lines = []
        for ef in existing:
            line = (
                f"- {ef.get('ring_name', '?')} ({ef.get('gender', '?')})"
                f" — from {ef.get('origin', '?')}"
            )
            roster_lines.append(line)
        existing_roster_text = (
            "\n\nEXISTING ROSTER (design around these — no duplicates):\n"
            + "\n".join(roster_lines)
        )
        prompt = self._build_plan_roster_prompt(4, existing_roster_text)
        assert "- Venom (female) — from Tokyo, Japan" in prompt
        assert "- Blaze (female) — from Miami, USA" in prompt
        assert "EXISTING ROSTER (design around these" in prompt


class TestGenerateFighterPrompt:
    def _build_generate_fighter_prompt(
        self,
        archetype_text,
        existing_roster_text,
        blueprint_text,
        body_directive,
        supernatural_instruction,
        min_total_stats,
        max_total_stats,
    ):
        return f"""{FULL_CHARACTER_GUIDE}

Generate a unique fighter for the AI Fighting League. {archetype_text}.{existing_roster_text}

{blueprint_text}

{body_directive}

{supernatural_instruction}

STAT CONSTRAINTS:
- 4 core stats (power, speed, technique, toughness), each rated 15-95
- 1 supernatural stat, rated 0-50 (0 if no supernatural abilities)
- The 4 core stats MUST total between {min_total_stats} and {max_total_stats}
- No fighter should be elite at everything — balance strengths with clear weaknesses
- Stats should reflect the archetype (Huntress has high speed, Empress has high technique, Viper has high speed/technique, etc.)

ICONIC FEATURES:
List 3-6 visual details that make this character instantly recognizable — the things a fan would
draw first. These persist across ALL outfit tiers. Can be anything visual: a scar, a hairstyle,
a tattoo, a weapon, boots, a choker, body paint, a prosthetic limb, a piece of jewelry.
NOT full clothing items like jackets or pants.

Return ONLY valid JSON with this exact structure:
{{
  "ring_name": "<evocative 1-2 word ring name>",
  "real_name": "<authentic name for their cultural background>",
  "age": <18-34>,
  "origin": "<specific city/region, country>",
  "gender": "<male|female>",
  "build": "<body type description incorporating the rolled body traits above>",
  "distinguishing_features": "<scars, tattoos, unique physical traits>",
  "iconic_features": "<comma-separated list of 3-6 visual details that make this character instantly recognizable across all tiers>",
  "personality": "<max 10 words — their vibe and attitude, e.g. 'cold, calculating predator who enjoys breaking opponents slowly'>",
  "image_prompt_body_parts": "<physical build, skin tone, hair, face, distinguishing features — shared across all tiers. IMPORTANT: for skin tone descriptions NEVER use metaphorical terms like 'golden', 'olive', 'bronze', 'caramel', 'porcelain', 'ebony' — the image model takes these literally. MUST incorporate the rolled body traits (waist, abs, butt, face shape, eyes, makeup) naturally into this description>",
  "image_prompt_expression": "<facial expression and attitude — shared across all tiers>",
  "image_prompt_personality_pose": "<a signature pose or action that shows off this character's personality — e.g. 'cracking knuckles with a cocky smirk', 'coiled fighting stance with one hand beckoning', 'hip cocked with arms crossed, looking down at viewer' — keep it short and visual>",
  "stats": {{
    "power": <15-95>,
    "speed": <15-95>,
    "technique": <15-95>,
    "toughness": <15-95>,
    "supernatural": <0-50>
  }}
}}"""

    def test_basic_prompt(self):
        prompt = self._build_generate_fighter_prompt(
            archetype_text="Primary archetype: Viper",
            existing_roster_text="",
            blueprint_text="",
            body_directive="BODY TYPE DIRECTIVE:\n- Height: 5'6\"\n- Weight: 130 lbs",
            supernatural_instruction="This fighter has NO supernatural abilities. The supernatural stat must be 0.",
            min_total_stats=200,
            max_total_stats=280,
        )
        assert FULL_CHARACTER_GUIDE in prompt
        assert "Primary archetype: Viper" in prompt
        assert "between 200 and 280" in prompt
        assert "supernatural stat must be 0" in prompt

    def test_with_blueprint(self):
        blueprint = (
            "BLUEPRINT DIRECTIVE — you MUST follow this plan for the character:\n"
            '{"ring_name": "Venom"}\n\n'
            "Follow the blueprint closely: use the ring name, origin, gender, "
            "archetype, and supernatural status exactly "
            "as specified. Flesh out the full character from this skeleton."
        )
        prompt = self._build_generate_fighter_prompt(
            archetype_text="Primary archetype: Viper",
            existing_roster_text="",
            blueprint_text=blueprint,
            body_directive="BODY TYPE DIRECTIVE:\n- Height: 5'6\"",
            supernatural_instruction="This fighter HAS supernatural abilities.",
            min_total_stats=200,
            max_total_stats=280,
        )
        assert "BLUEPRINT DIRECTIVE" in prompt
        assert "Venom" in prompt


class TestBuildTierPrompt:
    def test_sfw_all_skimpiness_levels(self):
        for level in [1, 2, 3, 4]:
            prompt = _build_tier_prompt("sfw", level, SAMPLE_CHARACTER_SUMMARY)
            config = SKIMPINESS_LEVELS[level]
            assert f'"{config["sfw_label"]}"' in prompt
            assert f"skimpiness {level}/8" in prompt
            assert config["sfw_hard_rules"] in prompt
            assert config["sfw_skin_pct"] in prompt
            assert config["sfw_guidance"] in prompt
            assert OUTFIT_STYLE_RULES in prompt
            assert "ring_attire_sfw" in prompt
            assert "image_prompt_clothing_sfw" in prompt
            assert "image_prompt_pose_sfw" in prompt
            assert "CHARACTER: Venom" in prompt
            assert "snake tattoo on left arm" in prompt
            assert f"SKIMPINESS LEVEL: {level} of 8" in prompt
            assert _build_body_shape_line(SAMPLE_BODY_DETAILS) in prompt

    def test_barely_all_skimpiness_levels(self):
        for level in [1, 2, 3, 4]:
            prompt = _build_tier_prompt("barely", level, SAMPLE_CHARACTER_SUMMARY)
            config = SKIMPINESS_LEVELS[level]
            effective = level + 4
            assert f'"{config["barely_label"]}"' in prompt
            assert f"skimpiness {effective}/8" in prompt
            assert config["barely_hard_rules"] in prompt
            assert config["barely_skin_pct"] in prompt
            assert config["barely_guidance"] in prompt
            assert "ring_attire" in prompt
            assert "image_prompt_clothing" in prompt
            assert "image_prompt_pose" in prompt
            assert f"SKIMPINESS LEVEL: {effective} of 8" in prompt

    def test_nsfw_level_1_topless(self):
        prompt = _build_tier_prompt("nsfw", 1, SAMPLE_CHARACTER_SUMMARY)
        config = SKIMPINESS_LEVELS[1]
        assert "Scandalous" in prompt
        assert config["nsfw_hard_rules"] in prompt
        assert config["nsfw_description"] in prompt
        assert "Level 1 (topless only)" in prompt
        assert "ring_attire_nsfw" in prompt
        assert "image_prompt_clothing_nsfw" in prompt
        assert "image_prompt_pose_nsfw" in prompt
        assert "topless plus ultra-sexy bottom" in prompt
        assert "SKIMPINESS LEVEL" not in prompt
        assert _build_nsfw_anatomy_line(SAMPLE_BODY_DETAILS) in prompt

    def test_nsfw_levels_2_3_4_full(self):
        for level in [2, 3, 4]:
            prompt = _build_tier_prompt("nsfw", level, SAMPLE_CHARACTER_SUMMARY)
            config = SKIMPINESS_LEVELS[level]
            assert config["nsfw_adjective"] in prompt
            assert config["nsfw_hard_rules"] in prompt
            assert "Levels 2-4 (fully nude)" in prompt
            assert "nude plus each remaining accessory" in prompt

    def test_sfw_with_outfit_options(self):
        prompt = _build_tier_prompt("sfw", 2, SAMPLE_CHARACTER_SUMMARY, outfit_options=SAMPLE_OUTFIT_OPTIONS)
        assert "Example tops to consider: sports bra, halter top" in prompt
        assert "Example bottoms to consider: combat shorts, leggings" in prompt
        assert "Example one-pieces to consider (use instead of top+bottom): high-cut leotard" in prompt

    def test_no_body_details(self):
        summary_no_body = {
            "ring_name": "Shadow",
            "iconic_features": "black mask",
            "image_prompt_body_parts": "tall muscular build",
            "image_prompt_expression": "menacing grin",
        }
        prompt = _build_tier_prompt("sfw", 2, summary_no_body)
        assert "CHARACTER: Shadow" in prompt
        assert "medium breasts" not in prompt

    def test_exact_sfw_level2_output(self):
        prompt = _build_tier_prompt("sfw", 2, SAMPLE_CHARACTER_SUMMARY)
        level = SKIMPINESS_LEVELS[2]
        body_shape = _build_body_shape_line(SAMPLE_BODY_DETAILS)

        expected = f"""CHARACTER: Venom
Iconic features (MUST be visible in every tier): snake tattoo on left arm, green eyes, forked tongue piercing
Body: athletic toned build, light brown skin, long black hair
Expression: cold predatory stare
{body_shape}
SKIMPINESS LEVEL: 2 of 8

Generate the "{level['sfw_label']}" tier outfit for this character (skimpiness 2/8).

{OUTFIT_STYLE_RULES}

RULES:
  HARD RULES: {level['sfw_hard_rules']}
  SKIN TARGET: ~{level['sfw_skin_pct']}% of skin visible.
  VIBE: {level['sfw_label']} — {level['sfw_guidance']}
  Iconic features + additional clothing pieces to hit the skin target.

You have FULL creative freedom on what clothing items to use. The rules above only constrain HOW MUCH skin shows, not WHAT the outfit looks like.

POSE: Also generate a short personality pose for this tier — a confident, powerful pose that fits a family-friendly context. 5-10 words max describing the body position and attitude.

Return ONLY valid JSON:
{{
  "ring_attire_sfw": "<concise SFW outfit description — list each item plainly, no flowery language>",
  "image_prompt_clothing_sfw": "<SFW clothing for image gen — just the clothing pieces, no adjective fluff>",
  "image_prompt_pose_sfw": "<concise personality pose for this tier — 5-10 words>"
}}"""
        assert prompt == expected

    def test_exact_barely_level3_output(self):
        prompt = _build_tier_prompt("barely", 3, SAMPLE_CHARACTER_SUMMARY)
        level = SKIMPINESS_LEVELS[3]
        body_shape = _build_body_shape_line(SAMPLE_BODY_DETAILS)
        effective = 7

        expected = f"""CHARACTER: Venom
Iconic features (MUST be visible in every tier): snake tattoo on left arm, green eyes, forked tongue piercing
Body: athletic toned build, light brown skin, long black hair
Expression: cold predatory stare
{body_shape}
SKIMPINESS LEVEL: {effective} of 8

Generate the "{level['barely_label']}" tier outfit for this character (skimpiness {effective}/8).

{OUTFIT_STYLE_RULES}

RULES:
  HARD RULES: {level['barely_hard_rules']}
  SKIN TARGET: ~{level['barely_skin_pct']}% of skin visible.
  VIBE: {level['barely_label']} — {level['barely_guidance']}
  Iconic features + additional pieces to hit the skin target.

You have FULL creative freedom on what clothing items to use. The rules above only constrain HOW MUCH skin shows, not WHAT the outfit looks like.

POSE: Also generate a short personality pose for this tier — suggestive, flirty, showing off the outfit and sex appeal. 5-10 words max.

Return ONLY valid JSON:
{{
  "ring_attire": "<concise outfit description — list each item plainly, no flowery language>",
  "image_prompt_clothing": "<clothing for image gen — just the clothing pieces, no adjective fluff>",
  "image_prompt_pose": "<concise personality pose for this tier — 5-10 words>"
}}"""
        assert prompt == expected

    def test_exact_nsfw_level1_output(self):
        prompt = _build_tier_prompt("nsfw", 1, SAMPLE_CHARACTER_SUMMARY)
        level = SKIMPINESS_LEVELS[1]
        body_shape = _build_body_shape_line(SAMPLE_BODY_DETAILS)
        nsfw_anatomy = _build_nsfw_anatomy_line(SAMPLE_BODY_DETAILS)

        additional = (
            "ADDITIONAL: The character is topless but keeps bottoms on. "
            "The bottoms (if they can be called that) must be ultra-sexy - tape, jewelry, insanely tiny triangle bottom gstring, etc"
            "Still include accessories — boots/heels, gloves, jewelry, chokers, belts, etc. "
            "The image_prompt_clothing_nsfw MUST include the sexy bottom garment plus accessories."
        )
        image_prompt_rules = (
            "## IMAGE PROMPT RULES — FOLLOW EXACTLY\n\n"
            "image_prompt_clothing_nsfw rules:\n"
            "- Keep it short\n"
            "- Always start with the remaining iconic features\n"
            "- This is Level 1 (topless only): include the sexy bottom garment."
            "- The charsheet prompt automatically adds the topless framing"
        )

        expected = f"""CHARACTER: Venom
Iconic features (MUST be visible in every tier): snake tattoo on left arm, green eyes, forked tongue piercing
Body: athletic toned build, light brown skin, long black hair
Expression: cold predatory stare
{body_shape}
{nsfw_anatomy}

Generate the NSFW outfit for this character. Tone: {level['nsfw_adjective']}.

{OUTFIT_STYLE_RULES}

{additional}

RULES:
  HARD RULES: {level['nsfw_hard_rules']}. Only iconic features and accessories remain.
  TONE: {level['nsfw_adjective']} — {level['nsfw_description']}

{image_prompt_rules}

POSE: Also generate a short personality pose for this NSFW tier that matches the tone: {level['nsfw_adjective']}. 5-15 words max describing body position and attitude.

Return ONLY valid JSON:
{{
  "ring_attire_nsfw": "<concise NSFW description — topless plus ultra-sexy bottom and each remaining accessory listed plainly>",
  "image_prompt_clothing_nsfw": "<NSFW clothing for image gen — sexy bottom garment plus accessories>",
  "image_prompt_pose_nsfw": "<concise NSFW pose matching the {level['nsfw_adjective']} tone — 5-15 words>"}}"""
        assert prompt == expected

    def test_exact_nsfw_level4_output(self):
        prompt = _build_tier_prompt("nsfw", 4, SAMPLE_CHARACTER_SUMMARY)
        level = SKIMPINESS_LEVELS[4]
        body_shape = _build_body_shape_line(SAMPLE_BODY_DETAILS)
        nsfw_anatomy = _build_nsfw_anatomy_line(SAMPLE_BODY_DETAILS)

        additional = (
            "ADDITIONAL: Even fully NSFW characters should still have accessories — "
            "boots/heels, gloves, jewelry, chokers, belts, etc. "
            "The nudity is the nipples and crotch; the outfit is what remains ON the body."
        )
        image_prompt_rules = (
            "## IMAGE PROMPT RULES — FOLLOW EXACTLY\n\n"
            "image_prompt_clothing_nsfw rules:\n"
            "- Keep it short\n"
            "- Always start with the remaining iconic features\n"
            "- This is Levels 2-4 (fully nude): only accessories remain."
            "- The charsheet prompt automatically adds the nudity framing"
        )

        expected = f"""CHARACTER: Venom
Iconic features (MUST be visible in every tier): snake tattoo on left arm, green eyes, forked tongue piercing
Body: athletic toned build, light brown skin, long black hair
Expression: cold predatory stare
{body_shape}
{nsfw_anatomy}

Generate the NSFW outfit for this character. Tone: {level['nsfw_adjective']}.

{OUTFIT_STYLE_RULES}

{additional}

RULES:
  HARD RULES: {level['nsfw_hard_rules']}. Only iconic features and accessories remain.
  TONE: {level['nsfw_adjective']} — {level['nsfw_description']}

{image_prompt_rules}

POSE: Also generate a short personality pose for this NSFW tier that matches the tone: {level['nsfw_adjective']}. 5-15 words max describing body position and attitude.

Return ONLY valid JSON:
{{
  "ring_attire_nsfw": "<concise NSFW description — nude plus each remaining accessory listed plainly>",
  "image_prompt_clothing_nsfw": "<NSFW clothing for image gen — remaining accessories only>",
  "image_prompt_pose_nsfw": "<concise NSFW pose matching the {level['nsfw_adjective']} tone — 5-15 words>"}}"""
        assert prompt == expected


class TestFightPrompts:
    def _build_probability_prompt(
        self, f1_name, f1_stats, f1_record, f1_condition,
        f2_name, f2_stats, f2_record, f2_condition, rivalry_text,
    ):
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

    def test_probability_no_rivalry(self):
        prompt = self._build_probability_prompt(
            "Venom", {"power": 60, "speed": 80}, {"wins": 3, "losses": 1},
            "healthy, Morale: neutral, Momentum: neutral",
            "Blaze", {"power": 75, "speed": 55}, {"wins": 2, "losses": 2},
            "healthy, Morale: neutral, Momentum: neutral",
            "",
        )
        assert "FIGHTER 1: Venom" in prompt
        assert "FIGHTER 2: Blaze" in prompt
        assert "RIVALRY CONTEXT" not in prompt

    def test_probability_with_rivalry(self):
        rivalry_text = """
RIVALRY CONTEXT: These fighters have fought 3 times before.
Venom has won 2 and Blaze has won 1.
This is a known rivalry — factor in the psychological weight of their history."""
        prompt = self._build_probability_prompt(
            "Venom", {}, {}, "healthy, Morale: neutral, Momentum: neutral",
            "Blaze", {}, {}, "healthy, Morale: neutral, Momentum: neutral",
            rivalry_text,
        )
        assert "RIVALRY CONTEXT" in prompt
        assert "fought 3 times" in prompt

    def _build_moments_prompt(
        self, target, f1_name, f1_id, f1_build, f1_height, f1_weight, f1_stats,
        f2_name, f2_id, f2_build, f2_height, f2_weight, f2_stats,
        winner_name, loser_name,
    ):
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

    def test_moments_prompt(self):
        prompt = self._build_moments_prompt(
            5, "Venom", "f_abc123", "athletic", "5'6\"", "130 lbs",
            {"power": 60, "speed": 80, "technique": 70},
            "Blaze", "f_def456", "muscular", "5'8\"", "145 lbs",
            {"power": 75, "speed": 55, "technique": 65},
            "Venom", "Blaze",
        )
        assert "Generate exactly 5 key moments" in prompt
        assert "PREDETERMINED OUTCOME: Venom knocks out Blaze" in prompt
        assert "f_abc123" in prompt
        assert "f_def456" in prompt


class TestMoveGenerationPrompt:
    def _build_move_generation_prompt(self, ring_name, build, personality, distinguishing, iconic, gender, stat_lines):
        return f"""You are designing fighting moves for "{ring_name}" in an AI fighting league.

CHARACTER:
- Build: {build}
- Personality: {personality}
- Distinguishing features: {distinguishing}
- Iconic features: {iconic}
- Gender: {gender}
- Stats: {stat_lines}

Design exactly 3 fighting moves for this character. Rules:
- Each move must feel unique to THIS character's body, personality, and strongest stats
- The moves must make sense physically - we will be generating images from them
- Moves are strikes, kicks, acrobatic attacks, or supernatural abilities — never holds or grapples
- Names: 2-4 words, evocative and memorable (fighting game style)
- stat_affinity: which stat the move leans on most (power, speed, technique, or supernatural)
- Lean into the character's highest stats and defining traits
- All three moves should feel different from each other in rhythm and visual impact

DESCRIPTION: 1-2 sentences explaining how the move works — the full choreography from start to finish. No metaphors or poetry, just plain physical action.

IMAGE_SNAPSHOT — THIS IS CRITICAL:
- This is a SINGLE FROZEN MOMENT for an artist to draw. One frame, not a sequence.
- Think through how the entire move would work step by step then pick the coolest moment to capture
- Describe the exact body position: where each limb is, weight distribution, angle of torso, head position
- End with which body parts have motion blur or speed lines (e.g. "motion blur on right leg and both fists")
- The fighter is ALONE — no opponent in the image
- BANNED: metaphors, similes, poetry, "like a ___", emotional descriptors, atmosphere words
- BANNED: any reference to an opponent, target, or impact
- BANNED: sequences or transitions — no "then", "before", "after", "lands in"
- GOOD example: "Mid-air, body horizontal, right leg fully extended forward at head height, left leg tucked under, arms swept back behind torso. Motion blur on right leg."
- GOOD example: "Deep lunge on left leg, right fist extended straight forward at shoulder height, left arm pulled back to hip, torso twisted 45 degrees. Speed lines on right fist."
- BAD example: "Leaps forward off one foot, drives both fists downward. Lands in a low crouch." (this is a sequence, not a snapshot)
- Keep it to 1-2 sentences — a single freeze-frame plus motion indicators.

Return ONLY valid JSON — an array of exactly 3 objects:
[
  {{
    "name": "<2-4 word move name>",
    "description": "<1-2 sentences: how the move works, full choreography>",
    "image_snapshot": "<1 sentence: single frozen moment, exact body position for an artist>",
    "stat_affinity": "<power|speed|technique|supernatural>"
  }}
]"""

    def test_move_prompt(self):
        prompt = self._build_move_generation_prompt(
            "Venom", "athletic toned", "cold predatory",
            "snake tattoo", "forked tongue piercing", "female",
            "power: 60, speed: 80, technique: 70",
        )
        assert 'fighting moves for "Venom"' in prompt
        assert "athletic toned" in prompt
        assert "IMAGE_SNAPSHOT" in prompt
        assert "stat_affinity" in prompt


class TestStorylinePrompt:
    def _build_storyline_prompt(self, fighter_name, result_text, opponent_name, method, round_ended, wins, losses, draws):
        return f"""Write 2-3 sentences about what this fight meant for {fighter_name} narratively.

{fighter_name} {result_text} {opponent_name} by {method} in round {round_ended}.
Current record: {wins}-{losses}-{draws}

Capture the emotional/narrative significance — confidence building, humbling loss, rivalry intensifying, etc. Be concise and dramatic."""

    def test_storyline_win(self):
        prompt = self._build_storyline_prompt("Venom", "won", "Blaze", "KO", 3, 4, 1, 0)
        assert "what this fight meant for Venom" in prompt
        assert "Venom won Blaze by KO in round 3" in prompt
        assert "4-1-0" in prompt

    def test_storyline_loss(self):
        prompt = self._build_storyline_prompt("Blaze", "lost to", "Venom", "KO", 3, 2, 3, 0)
        assert "Blaze lost to Venom by KO in round 3" in prompt
        assert "2-3-0" in prompt


class TestCharsheetPrompt:
    def test_sfw_charsheet(self):
        result = _build_charsheet_prompt(
            body_parts="athletic toned build, light brown skin",
            clothing="sports bra, combat shorts",
            expression="cold predatory stare",
            personality_pose="arms crossed, hip cocked",
            tier="sfw",
            gender="female",
            skimpiness_level=2,
            body_type_details=SAMPLE_BODY_DETAILS,
            origin="Tokyo, Japan",
        )
        assert isinstance(result, dict)
        assert "full_prompt" in result
        body_shape = _build_body_shape_line(SAMPLE_BODY_DETAILS)
        assert body_shape in result["body_parts"]
        assert "sports bra, combat shorts" in result["clothing"]
        assert "from Tokyo, Japan" in result["character_desc"]
        assert "ANATOMY" not in result["full_prompt"] or "[ANATOMY]" not in result["full_prompt"]

        style = get_art_style("female") + ", character design reference sheet"
        assert result["style"].startswith(style)
        assert "NSFW" not in result["style"]

    def test_nsfw_charsheet_full(self):
        result = _build_charsheet_prompt(
            body_parts="athletic toned build",
            clothing="body chains",
            expression="sultry gaze",
            personality_pose="hands on hips",
            tier="nsfw",
            gender="female",
            skimpiness_level=4,
            body_type_details=SAMPLE_BODY_DETAILS,
            origin="Miami, USA",
        )
        assert "completely naked except body chains" in result["clothing"]
        nsfw_anatomy = _build_nsfw_anatomy_line(SAMPLE_BODY_DETAILS)
        assert "[ANATOMY]" in result["full_prompt"]
        assert nsfw_anatomy in result["full_prompt"]
        assert "NSFW" in result["style"]

    def test_nsfw_charsheet_topless(self):
        result = _build_charsheet_prompt(
            body_parts="athletic build",
            clothing="micro thong",
            expression="confident smirk",
            tier="nsfw",
            gender="female",
            skimpiness_level=1,
            body_type_details=SAMPLE_BODY_DETAILS,
        )
        assert "topless, bare breasts, micro thong" in result["clothing"]
        assert "topless" in result["style"].lower()

    def test_barely_charsheet(self):
        result = _build_charsheet_prompt(
            body_parts="athletic build",
            clothing="micro bikini",
            expression="playful wink",
            tier="barely",
            gender="female",
            skimpiness_level=3,
            body_type_details=SAMPLE_BODY_DETAILS,
        )
        assert "micro bikini" in result["clothing"]
        assert "NSFW" not in result["style"]

    def test_empty_body_parts(self):
        result = _build_charsheet_prompt(
            body_parts="",
            clothing="whatever",
            expression="whatever",
        )
        assert result == {}

    def test_no_clothing_nsfw(self):
        result = _build_charsheet_prompt(
            body_parts="athletic build",
            clothing="",
            expression="stare",
            tier="nsfw",
            gender="female",
            skimpiness_level=4,
        )
        assert result["clothing"] == "completely naked"

    def test_no_clothing_nsfw_topless(self):
        result = _build_charsheet_prompt(
            body_parts="athletic build",
            clothing="",
            expression="stare",
            tier="nsfw",
            gender="female",
            skimpiness_level=1,
        )
        assert result["clothing"] == "topless, bare breasts"

    def test_male_nsfw_charsheet(self):
        result = _build_charsheet_prompt(
            body_parts="muscular build",
            clothing="combat boots",
            expression="fierce gaze",
            tier="nsfw",
            gender="male",
            skimpiness_level=2,
        )
        assert "male nudity" in result["style"].lower()


class TestMoveImagePrompt:
    def test_sfw_move_image(self):
        prompt = build_move_image_prompt(SAMPLE_FIGHTER_FOR_MOVES, SAMPLE_MOVE, "sfw")
        assert get_art_style("female") in prompt
        assert "Serpent Strike" in prompt
        assert "single full-body action pose" in prompt
        assert "sports bra, combat shorts, boots" in prompt
        assert "NSFW" not in prompt

    def test_barely_move_image(self):
        prompt = build_move_image_prompt(SAMPLE_FIGHTER_FOR_MOVES, SAMPLE_MOVE, "barely")
        assert "micro bikini, combat boots" in prompt
        assert "Serpent Strike" in prompt

    def test_nsfw_move_image(self):
        prompt = build_move_image_prompt(SAMPLE_FIGHTER_FOR_MOVES, SAMPLE_MOVE, "nsfw")
        assert _nsfw_prefix("female", 2) in prompt
        assert _nsfw_tail("female", 2) in prompt
        assert "body chain harness, combat boots" in prompt

    def test_nsfw_prefix_female_topless(self):
        result = _nsfw_prefix("female", 1)
        assert "topless" in result
        assert "bare breasts" in result

    def test_nsfw_prefix_female_full(self):
        result = _nsfw_prefix("female", 2)
        assert "full frontal female nudity" in result
        assert "bare pussy" in result

    def test_nsfw_prefix_male(self):
        result = _nsfw_prefix("male", 2)
        assert "male nudity" in result

    def test_nsfw_tail_female_topless(self):
        result = _nsfw_tail("female", 1)
        assert "topless" in result

    def test_nsfw_tail_female_full(self):
        result = _nsfw_tail("female", 2)
        assert "full frontal female nudity" in result

    def test_nsfw_tail_male(self):
        result = _nsfw_tail("male", 2)
        assert "male nudity" in result


class TestBodyShapeLines:
    def test_body_shape_line(self):
        result = _build_body_shape_line(SAMPLE_BODY_DETAILS)
        assert result == "medium breasts, medium round butt"

    def test_nsfw_anatomy_line(self):
        result = _build_nsfw_anatomy_line(SAMPLE_BODY_DETAILS)
        assert result == (
            "medium breasts, small pert nipples, "
            "medium round butt, tucked pussy, small hidden labia"
        )


class TestFightPromptExactOutput:
    def test_exact_probability_prompt(self):
        f1_stats = {"power": 60, "speed": 80}
        f1_record = {"wins": 3, "losses": 1}
        f2_stats = {"power": 75, "speed": 55}
        f2_record = {"wins": 2, "losses": 2}

        expected = f"""Analyze this fighting matchup and return a JSON probability assessment. All fights end in KO.

FIGHTER 1: Venom
- Stats: {f1_stats}
- Record: {f1_record}
- Condition: healthy, Morale: neutral, Momentum: neutral

FIGHTER 2: Blaze
- Stats: {f2_stats}
- Record: {f2_record}
- Condition: healthy, Morale: neutral, Momentum: neutral


Stats are: power (striking force), speed (quickness/reflexes), technique (skill/fight IQ/defense), toughness (durability/endurance/recovery), supernatural (optional supernatural ability, 0 = none).

Return ONLY valid JSON with this exact structure:
{{
  "fighter1_win_prob": <float between 0.05 and 0.95>,
  "fighter2_win_prob": <float between 0.05 and 0.95, must sum to ~1.0 with fighter1_win_prob>,
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"]
}}

Supernatural abilities should be factored as a modest edge, not a dominator."""

        actual = f"""Analyze this fighting matchup and return a JSON probability assessment. All fights end in KO.

FIGHTER 1: Venom
- Stats: {f1_stats}
- Record: {f1_record}
- Condition: healthy, Morale: neutral, Momentum: neutral

FIGHTER 2: Blaze
- Stats: {f2_stats}
- Record: {f2_record}
- Condition: healthy, Morale: neutral, Momentum: neutral


Stats are: power (striking force), speed (quickness/reflexes), technique (skill/fight IQ/defense), toughness (durability/endurance/recovery), supernatural (optional supernatural ability, 0 = none).

Return ONLY valid JSON with this exact structure:
{{
  "fighter1_win_prob": <float between 0.05 and 0.95>,
  "fighter2_win_prob": <float between 0.05 and 0.95, must sum to ~1.0 with fighter1_win_prob>,
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"]
}}

Supernatural abilities should be factored as a modest edge, not a dominator."""
        assert actual == expected
