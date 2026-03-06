import random

from app.engine.fighter_config import (
    ARCHETYPE_SUBTYPES,
    ARCHETYPE_SUBTYPES_MALE,
    OUTFIT_COLOR_PALETTE,
    HAIR_COLOR_BUCKETS,
)


GUIDE_CORE_PHILOSOPHY = """## Core Philosophy — Read This First

Everything below flows from these four principles. If a new character violates any of
them, stop and rework.

### 1. Female Characters Are Attractive but Distinctive

Design for a predominantly male audience. Every female fighter should be attractive in a distinctive way.
Sex appeal is a feature, not a bug. Confidence, allure, and willingness to
weaponize beauty are core to female character design in AFL. But be tasteful so we can have a
good SFW version of each character which is family friendly. Most should be white / asian / latina.

### 2. Men Are Bigger and Stronger — Women Win Differently

Men should be physically larger and more powerful than women on average. No female fighters whose
primary identity is being big and strong compared to the men. Women compete through
seduction, charm, playing dirty, psychological warfare, debuffing, supernatural ability,
technical mastery, mysticism, poison, speed, precision — everything except raw physical
dominance. The size and strength gap is real and is part of what makes it interesting when
a woman beats a man twice her size through means other than out-muscling him.

### 3. Characters are interesting because of how they deal with adversity and hurting others

Attitude and personality alone don't make a character interesting. Magic alone doesn't make
a character interesting. What makes a character interesting is:

- How they hurt others — and how they feel about it. Do they enjoy it? Hate it? Feel
  nothing? Need it?
- How they get hurt — and how they react. Do they crumble? Get angry? Get quiet? Come
  back harder?


### 4. Steal From Everywhere — Archetypes From Popular Media

The roster shouldn't be 20 variations on "MMA fighter with magic." Reach into the full
vocabulary of popular media archetypes and bring them in pure form:

- Technology: Mech suits, cybernetic augmentation, powered armor, nanobots
- Weapons: Guns, blades, chains, exotic weaponry
- Science: Gene splicing, chemical enhancement, experimental drugs, combat stimulants
- Faith: Ancient Christian favor, divine wrath, holy warrior, exorcist
- Subterfuge: Poison, hypnotics, drugs, nerve agents, sleep darts
- Tradition: Ninja art, assassin training, monastery disciplines, tribal war magic
- Pop culture pulls: Find an archetype that works in anime, action movies, comics,
  video games, wrestling, mythology, or pulp fiction and ask "what does this look like
  as an AFL fighter?"

**CRITICAL: ALMOST ALL FEMALE CHARACTERS should be white / asian / latina.**

"""

GUIDE_VISUAL_DESIGN = """## Visual Design Principles

### The Strip Test

Remove all supernatural effects from the character. Are they still visually compelling
and distinct through human qualities alone? If not, the design needs more work.

This is the single most important design principle. Every fighter must pass it.

A chi fighter without the glow should still be a tiny, intense woman with an asymmetric
haircut, white hand wraps, and an unsettling stare. Compelling. An aristocrat without any
magical element should still be a statuesque blonde in a white leotard and thigh-highs
smirking at you like you're beneath her. Compelling.

If your character is only interesting because they glow, they are not interesting.

### Human Qualities Carry the Design

What makes a character visually memorable is always human:

- Expression: A cold intellectual appraisal. A feral grin. Dead calm. Righteous
  stillness. The face tells the story.
- Outfit: Ring attire expresses personality louder than any magical effect.
- Body language: How they carry themselves. 
- Physicality: Body type tells a story. 
- Style details: Scars, tattoos, jewelry, hair choices. These are the details
  fans remember.

### Silhouette Rule

A well-designed fighter is recognizable from their outline alone. A massive frame with
flowing hair is distinct from a hunched, gut-forward silhouette. A small, spiky profile
is distinct from a compact, ponytailed shape.

Test: describe the character's silhouette in one sentence. If it sounds like someone
else on the roster, differentiate further.


What NOT to do: Use "faint [color] energy emanates from their body" or "an aura of
desire radiates outward" as a substitute for actual visual design. Don't sanitize female
designs into modest athletic wear because it feels "safer" or "more realistic." This is a
fantasy fighting league inspired by Mortal Kombat and Street Fighter, not a UFC simulation.
Lean in.

### Distinguishing Features

Every fighter needs at least 1 unique physical detail that fans latch onto:

- Scars (a keloid across the jaw, a crocodile-bite scar, an eyebrow-to-cheekbone slash)
- Tattoos (full irezumi sleeves, Adinkra symbols, a snake on the ring finger)
- Heterochromia or unusual eyes (mismatched green/olive, amber-gold, solid white)
- Hair (a hot pink buzzcut, gold-thread braids, an asymmetric cut with a white streak)
- Body quirks (a missing pinky tip, a chipped tooth, scarred and calcified fists)

The rule: supernatural effects are one optional ingredient, never the main course.
When present, they should be subtle, ambiguous, or grounded in something physical
"""

GUIDE_CREATION_WORKFLOW = """## The Creation Workflow

### Archetype + Subtype

Each fighter gets ONE primary archetype and ONE subtype within that archetype.
The subtype specializes the archetype — it's where the character's unique angle lives.

Female archetypes: Siren, Witch, Viper, Prodigy, Doll, Huntress, Empress, Experiment, Demon, Assassin, Nymph
- Siren: weaponized beauty, seduction, charm
- Witch: mysticism, dark arts, supernatural
- Viper: poison, subterfuge, dirty tricks
- Prodigy: young technical genius, speed and precision
- Doll: deceptive innocence, psychological warfare
- Huntress: predatory, relentless, speed-based
- Empress: dominance through authority and manipulation
- Experiment: cybernetics, body modification, science
- Demon: infernal power, dark seduction, hellfire
- Assassin: lethal precision, stealth, silent killing
- Nymph: nature magic, fae trickery, ethereal allure

Male archetypes: Brute, Veteran, Monster, Technician, Wildcard, Mystic, Prodigy, Experiment
- Brute: raw physical power, intimidation
- Veteran: battle-scarred, tactical, experienced
- Monster: inhuman size and strength, terrifying
- Technician: precise, methodical, strategic
- Wildcard: unpredictable, chaotic
- Mystic: supernatural warrior, ancient traditions
- Prodigy: young phenom, natural talent
- Experiment: enhanced, modified, science project

The archetype defines the broad identity. The subtype sharpens it into something specific.
A "Siren (Femme Fatale)" is deadly allure. A "Siren (Muse)" is ethereal obsession.
Same archetype, completely different characters. The subtype is where personality lives.

### Identity & Origin

- Ring Name: Should be instantly evocative. One or two words that conjure an image or feeling.
- Real Name: Should feel authentic to the character's cultural background.
- Age: 18-22 = still developing. 23-28 = peak. 29-34 = veteran, peaking mentally.
- Hometown: Specific is better than vague. "Darwin, Northern Territory, Australia" not "Australia."

### Physical Design

For female characters: This is where sex appeal is designed in, not bolted on later.
The outfit should be the statement — high-cut leotards, crop tops, sling bikinis, thongs, mesh
panels, thigh-highs, micro shorts, plunging necklines. The outfit IS character design.

For male characters: Men should read as physically imposing, powerful, larger than the
women. Shirtless, muscular, scarred, weathered, massive — the visual vocabulary of
masculine threat.

### Concept Hook

Write one sentence that captures what makes this fighter unique. If you can't say it in
one sentence, the concept needs refinement.

The best hooks often start with a recognizable archetype from popular media — action
movies, anime, comics, video games, wrestling, mythology, pulp fiction — and translate it
into the AFL world. Don't default to "martial artist with magic." Think bigger.

Bad examples:
- "A strong fighter who uses magic" (generic, could be anyone)
- "A mysterious warrior from a hidden temple" (cliche without specificity)
- "A woman who is really strong and tough" (strength isn't the hook for women — see Core Philosophy #2)

For female characters specifically: The hook should make clear why she's compelling
to a male audience. Beauty, danger, allure, mystique, cleverness, cruelty, seduction —
these are the ingredients.
"""

GUIDE_COMMON_MISTAKES = """## Common Mistakes
1. **Sanitizing female designs** — #1 failure mode. If the outfit could pass on ESPN, it's too conservative. Think Mortal Kombat / Dead or Alive, not UFC.
2. **Repulsive female fighters** No monstrous designs, no strength-based identity.
3. **Black-and-white morality** — roster should be overwhelmingly grey. At most 1-2 extremes.
4. **"Martial artist + magic" default** — explore technology, weapons, science, faith, poison, cybernetics. If the concept is [martial art] + [magical ability], pivot.
5. **Glow effects as identity** — if the most notable visual feature is glowing, redo it. Pass the strip test.
6. **"Supernatural seduction"** — seduction works through specific human behaviors, not "mystical allure."
8. **Duplicate archetypes** — if 3 already exist, your version needs a strong reason to exist.
11. **Failing the strip test** — remove supernatural effects; still compelling? If not, rework the human foundation.
12. **Cheap diversity** — origin must serve the character concept. Tokenism is boring.
"""


FULL_CHARACTER_GUIDE = (
    GUIDE_CORE_PHILOSOPHY
    + GUIDE_CREATION_WORKFLOW
    + GUIDE_VISUAL_DESIGN
    + GUIDE_COMMON_MISTAKES
)


GUIDE_MALE_PHILOSOPHY = """## Male Character Design
Outfits serve function and threat: tactical gear, hand wraps, military/mercenary aesthetic,
gladiatorial leather and chains, traditional gi, street fighting torn jeans. "This guy fights
for real" not "this guy goes to the gym."

Avoid: too clean/pretty, generic MMA look, forgetting scars and wear, one-dimensional brutes.
"""

FULL_MALE_CHARACTER_GUIDE = (
    GUIDE_MALE_PHILOSOPHY
    + GUIDE_CREATION_WORKFLOW
    + GUIDE_VISUAL_DESIGN
    + GUIDE_COMMON_MISTAKES
)


SYSTEM_PROMPT_ROSTER_PLANNER = (
    "You are a roster architect for a fantasy fighting league. "
    "Design an interconnected cast of compelling characters. "
    "Always respond with valid JSON only \u2014 an array of objects."
)

SYSTEM_PROMPT_CHARACTER_DESIGNER = (
    "You are a character designer for a fighting league. "
    "Create unique, compelling fighters. Always respond with valid JSON only."
)


def _shuffled_archetype_names(gender: str = "female") -> str:
    source = ARCHETYPE_SUBTYPES_MALE if gender.lower() == "male" else ARCHETYPE_SUBTYPES
    names = [k.replace("The ", "") for k in source]
    random.shuffle(names)
    return ", ".join(names)


def _shuffled_subtype_lines(gender: str = "female") -> str:
    source = ARCHETYPE_SUBTYPES_MALE if gender.lower() == "male" else ARCHETYPE_SUBTYPES
    items = list(source.items())
    random.shuffle(items)
    lines = []
    for arch, subs in items:
        short = arch.replace("The ", "")
        sub_names = [s["name"] for s in subs]
        random.shuffle(sub_names)
        lines.append(f"- {short}: {', '.join(sub_names)}")
    return "\n".join(lines)


def build_plan_roster_prompt(
    roster_size: int, existing_roster_text: str = "", gender_mix: str = "female"
) -> str:
    if gender_mix == "mixed":
        female_archetype_list = _shuffled_archetype_names("female")
        male_archetype_list = _shuffled_archetype_names("male")
        female_subtype_block = _shuffled_subtype_lines("female")
        male_subtype_block = _shuffled_subtype_lines("male")
        archetype_line = (
            f"- Archetypes: use a mix of FEMALE archetypes ({female_archetype_list}) "
            f"and MALE archetypes ({male_archetype_list})"
        )
        gender_constraint = (
            "- Gender: include BOTH male and female fighters in this roster\n"
            "- Every female fighter should be attractive but distinctive\n"
            "- Power tiers MUST be distributed evenly across genders — do NOT cluster all males or all females into the same power_tier. Each tier (champion, contender, gatekeeper, prospect) should have a mix of both genders"
        )
        archetype_json_line = f'"primary_archetype": "<from female archetypes: {female_archetype_list} OR male archetypes: {male_archetype_list}>"'
        subtype_block = f"FEMALE SUBTYPES:\n{female_subtype_block}\n\nMALE SUBTYPES:\n{male_subtype_block}"
        guide = GUIDE_CORE_PHILOSOPHY + "\n" + GUIDE_MALE_PHILOSOPHY
    elif gender_mix == "male":
        archetype_list = _shuffled_archetype_names("male")
        subtype_block = _shuffled_subtype_lines("male")
        archetype_line = f"- Archetypes: cover at least 5 different primary archetypes from the MALE list: {archetype_list}"
        gender_constraint = "- Gender: ALL fighters must be male"
        archetype_json_line = (
            f'"primary_archetype": "<from the male archetypes: {archetype_list}>"'
        )
        guide = GUIDE_MALE_PHILOSOPHY
    else:
        archetype_list = _shuffled_archetype_names()
        subtype_block = _shuffled_subtype_lines()
        archetype_line = f"- Archetypes: cover at least 5 different primary archetypes from the FEMALE list: {archetype_list}"
        gender_constraint = (
            "- Gender: ALL fighters must be female\n"
            "- Every female fighter should be attractive but distinctive"
        )
        archetype_json_line = (
            f'"primary_archetype": "<from the female archetypes: {archetype_list}>"'
        )
        guide = GUIDE_CORE_PHILOSOPHY

    palette_str = ", ".join(OUTFIT_COLOR_PALETTE)
    bucket_str = ", ".join(HAIR_COLOR_BUCKETS)

    return f"""{existing_roster_text}

{guide}

{GUIDE_COMMON_MISTAKES}

You are planning a roster of {roster_size} fighters for the AI Fighting League.
Design all {roster_size} fighters as an interconnected ensemble — they should feel like
a cast, not a random collection.

ROSTER BALANCE CONSTRAINTS:
{gender_constraint}
- Supernatural: at least 2 fighters should have NO supernatural abilities
- Geography: at least 4 different countries/regions represented
{archetype_line}
- No two fighters should share the same primary fighting style concept
- Design rivalry seeds: each fighter should have 1-2 natural rivals within this roster
- Skimpiness: assign each fighter probability weights for skimpiness levels 1-4 based on personality. The weights represent how likely each level is for this character. Default bias should lean slightly toward the skimpier side — most fighters should center around levels 2-3. A Siren might weight heavily toward 3-4, a Prodigy toward 2-3, an Empress toward 2-3. The 4 weights must sum to 100.

SIGNATURE VISUAL IDENTITY — each fighter needs a unique visual signature that makes them
instantly recognizable. These elements are tracked across the entire roster to prevent duplicates:
- primary_outfit_color: MUST be one of these exact values: {palette_str}
- hair_style: distinctive hairstyle (e.g., "long flowing waves", "buzz cut", "twin braids", "mohawk", "slicked back ponytail")
- hair_color: detailed hair color description (e.g., "platinum blonde", "jet black", "fire red with orange streaks")
- hair_color_bucket: the broad category — MUST be one of: {bucket_str}
- face_adornment: mask, face paint, hat, headwear, or "none" (e.g., "oni half-mask", "tribal war paint", "crown of thorns", "eye patch", "wide-brim hat", "none")
No two fighters should share the same primary_outfit_color. Aim for maximum visual diversity in hair combos and face adornments.

Return ONLY valid JSON — an array of {roster_size} objects with this structure:
[
  {{
    "concept_hook": "<one-sentence hook that captures what makes this fighter unique>",
    "ring_name": "<evocative 1-2 word ring name>",
    "gender": "<male|female>",
    "age": <18-34>,
    "origin": "<specific city/region, country>",
    {archetype_json_line},
    "subtype": "<REQUIRED — pick from the SUBTYPES list below for the chosen primary_archetype>",
    "has_supernatural": <true|false>,
    "power_tier": "<prospect|gatekeeper|contender|champion>",
    "narrative_role": "<what they bring to the story>",
    "rivalry_seeds": ["<ring_name of 1-2 other fighters in this plan>"],
    "media_archetype_inspiration": "<what popular media archetype this draws from>",
    "skimpiness_weights": [<level1_pct>, <level2_pct>, <level3_pct>, <level4_pct>],
    "primary_outfit_color": "<MUST be one of the palette values listed above — unique across roster>",
    "hair_style": "<distinctive hairstyle>",
    "hair_color": "<detailed hair color description>",
    "hair_color_bucket": "<broad category from: {bucket_str}>",
    "face_adornment": "<mask, face paint, hat, headwear, or 'none'>"
  }}
]

SUBTYPES (REQUIRED — every fighter must have a subtype matching their primary archetype):
{subtype_block}"""


def build_generate_fighter_prompt(
    archetype_text: str,
    existing_roster_text: str,
    blueprint_text: str,
    body_directive: str,
    supernatural_instruction: str,
    min_total_stats: int,
    max_total_stats: int,
    subtype_info: dict | None = None,
    gender: str = "female",
) -> str:
    subtype_directive = ""
    if subtype_info:
        subtype_directive = (
            f"\n\nSUBTYPE IDENTITY — this is the character's specific angle within their archetype:\n"
            f"  Subtype: {subtype_info['name']}\n"
            f"  Concept: {subtype_info['description']}\n"
            f"The subtype MUST shape the character's visual identity. The image_prompt_body_parts, "
            f"image_prompt_expression, and image_prompt_personality_pose should all reflect "
            f"a \"{subtype_info['name']}\" specifically — not just a generic {archetype_text.replace('Primary archetype: ', '')}. "
            f"A {subtype_info['name']} should LOOK different from other subtypes of the same archetype."
        )

    guide = (
        FULL_MALE_CHARACTER_GUIDE if gender.lower() == "male" else FULL_CHARACTER_GUIDE
    )

    if gender.lower() == "male":
        body_trait_hint = (
            "MUST incorporate the rolled body traits (build type, muscle definition, "
            "shoulder width, chest, face shape, eye expression, facial hair) naturally "
            "into this description"
        )
        personality_example = (
            "e.g. 'silent predator who breaks bones without changing expression'"
        )
    else:
        body_trait_hint = (
            "MUST incorporate the rolled body traits (waist, abs, butt, face shape, "
            "eyes, makeup) naturally into this description"
        )
        personality_example = (
            "e.g. 'cold, calculating predator who enjoys breaking opponents slowly'"
        )

    return f"""{guide}

Generate a unique fighter for the AI Fighting League. {archetype_text}.{existing_roster_text}

{blueprint_text}{subtype_directive}

{body_directive}

{supernatural_instruction}

NOTE: Stats (power, speed, technique, toughness, guile, supernatural) are generated separately — do NOT include a "stats" field in your response.

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
  "personality": "<max 10 words — their vibe and attitude, {personality_example}>",
  "image_prompt_body_parts": "<physical build, skin tone, hair, face, distinguishing features — shared across all tiers. IMPORTANT: for skin tone descriptions NEVER use metaphorical terms like 'golden', 'olive', 'bronze', 'caramel', 'porcelain', 'ebony' — the image model takes these literally. {body_trait_hint}>",
  "image_prompt_expression": "<facial expression and attitude — shared across all tiers>",
  "image_prompt_personality_pose": "<a signature pose or action that shows off this character's personality — e.g. 'cracking knuckles with a cocky smirk', 'coiled fighting stance with one hand beckoning', 'hip cocked with arms crossed, looking down at viewer' — keep it short and visual>"
}}"""
