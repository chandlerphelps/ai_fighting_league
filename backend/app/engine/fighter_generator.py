import json
import random
import uuid

from app.config import Config
from app.engine.image_style import get_art_style, get_art_style_tail
from app.models.fighter import Fighter, Stats, Record, Condition
from app.services.openrouter import call_openrouter_json


ARCHETYPES_FEMALE = [
    "The Siren",
    "The Witch",
    "The Viper",
    "The Prodigy",
    "The Doll",
    "The Huntress",
    "The Empress",
    "The Experiment",
]

ARCHETYPES_MALE = [
    "The Brute",
    "The Veteran",
    "The Monster",
    "The Technician",
    "The Wildcard",
    "The Mystic",
    "The Prodigy",
    "The Experiment",
]

GUIDE_CORE_PHILOSOPHY = """## Core Philosophy — Read This First

Everything below flows from these four principles. If a new character violates any of
them, stop and rework.

### 1. Female Characters Are Attractive — Always

Design for a predominantly male audience. Every female fighter must be attractive — no exceptions.
No zombies, no body horror, no monstrous designs, no grotesque features. Female fighters should
be charismatic, beautiful, and this should be blatantly obvious in their outfit and gear design.
Crop tops, high-cut leotards, sling bikinis, thongs, thigh-highs, mesh panels, cameltoe, loose
shirts with no bra, short skirts, loin cloths, semi-transparency, body paint — lean into it
without apology. Sex appeal is a feature, not a bug. Confidence, allure, and willingness to
weaponize beauty are core to female character design in AFL. But be tasteful so we can have a
good SFW version of each character which is family friendly.

### 2. Men Are Bigger and Stronger — Women Win Differently

Men should be physically larger and more powerful than women. No female fighters whose
primary identity is being big and strong compared to the men. Women compete through
seduction, charm, playing dirty, psychological warfare, debuffing, supernatural ability,
technical mastery, mysticism, poison, speed, precision — everything except raw physical
dominance. The size and strength gap is real and is part of what makes it interesting when
a woman beats a man twice her size through means other than out-muscling him.

### 3. Characters Are Interesting Because of Violence, Not Despite It

Attitude and personality alone don't make a character interesting. Magic alone doesn't make
a character interesting. What makes a character interesting is:

- How they hurt others — and how they feel about it. Do they enjoy it? Hate it? Feel
  nothing? Need it?
- How they get hurt — and how they react. Do they crumble? Get angry? Get quiet? Come
  back harder?

We want to know how they deal with hurting and being hurt - and not just physical hurt. Avoid purely
evil or purely good characters as a general rule. Keep 1-2 at most, and even those should
be 95/5 — the saint with one dark impulse, the monster with one shred of something human.

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

The best new characters often come from identifying a classic archetype from existing
media and translating it faithfully into the AFL world. A cyberpunk street samurai. A
voodoo priestess. A disgraced priest who fights with righteous fury. A cartel chemist
who poisons her opponents before the bell. These are more interesting starting points
than "fighter with unusual martial art."
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
- Outfit: Ring attire expresses personality louder than any magical effect. A white
  leotard with gold filigree says "I'm at a gala, not a cage fight." Ripped denim shorts
  and ratty Converse say "I came here to break things." An olive sports bra and khaki
  shorts say "I'm here to work." Immaculate white-and-gold says "I'm already better
  than you."
- Body language: How they carry themselves. A warrior's posture. A deliberate hip
  roll. Coiled, restless scanning. Focused shadowboxing.
- Physicality: Body type tells a story. A massive gut hiding slabs of core muscle.
  A coiled-spring wiry frame. Weathered, dense muscle. An angular, forged-by-hardship build.
- Style details: Scars, tattoos, jewelry, hair choices. A keloid scar and gold-tipped
  locs. Gold-thread braids. A crocodile scar and twice-broken nose. These are the details
  fans remember.

### Silhouette Rule

A well-designed fighter is recognizable from their outline alone. A massive frame with
flowing hair is distinct from a hunched, gut-forward silhouette. A small, spiky profile
is distinct from a compact, ponytailed shape.

Test: describe the character's silhouette in one sentence. If it sounds like someone
else on the roster, differentiate further.

### Sex Appeal — Especially for Female Characters

This is not optional. This is core to the product. AFL is designed for a predominantly
male audience and female characters should be designed accordingly.

For every female fighter, the outfit and physical design should be overtly sexy. This means:

- Revealing outfits are encouraged: High-cut leotards, plunging necklines, sling
  bikinis, crop tops showing underboob, micro shorts, mesh panels, thigh-highs, painted-on
  bodysuits, micro bikinis, cameltoe, loose shirts with no bra, short skirts,
  loin cloths, semi-transparency, body paint. The outfit should turn heads, but be tasteful.
- Physique matters: Athletic, toned, curves emphasized. Different body types are fine
  (petite, hourglass, athletic, compact) but all should be attractive. No female fighter
  should be designed to be visually unremarkable.
- Confidence amplifies everything: Amused condescension. A predatory smile. Cold
  clinical beauty. The attitude in the eyes and the body language multiply the visual
  impact of the outfit.
- The outfit IS the character: An aristocrat in a standard sports bra and shorts
  loses her identity. A genius in anything less than immaculate couture loses hers.
  The outfit choice reveals personality as much as any dialogue.

For male fighters, sex appeal comes through physicality — sculpted builds, shirtless by
default, chiseled jaws, imposing frames. A magazine-cover body. Greek-god proportions.
Terrifying mass.

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

### What NOT to Do

These are bad patterns to avoid:

| Bad Pattern | Better Replacement |
|---|---|
| "Faint emerald energy wisps around her hands" | Celtic knotwork sleeve tattoos that seem to shift in low light |
| "An aura of supernatural allure radiates from her" | "Too-perfect proportions, cold clinical beauty — disturbing, not enchanting" |
| "Mystical golden light surrounds his fists" | Faint shimmer around fists "that could be sweat catching the light, or something else" |
| "Her eyes glow with psychic power" | "Cool, appraising dark brown eyes with cutting intellectual intensity" |
| Generic "energy crackling" as identity | Specific human details (scars, expression, outfit, posture) |

The rule: supernatural effects are one optional ingredient, never the main course.
When present, they should be subtle, ambiguous, or grounded in something physical (tattoos
that seem to move, veins that darken, eyes that catch light strangely).
"""

GUIDE_CREATION_WORKFLOW = """## The Creation Workflow

### Archetype Blend

Archetypes are gender-specific. Pick 2 from the appropriate list:

Female archetypes: Siren, Witch, Viper, Prodigy, Doll, Huntress, Empress, Experiment
- Siren: weaponized beauty, seduction, charm
- Witch: mysticism, dark arts, supernatural
- Viper: poison, subterfuge, dirty tricks
- Prodigy: young technical genius, speed and precision
- Doll: deceptive innocence, psychological warfare
- Huntress: predatory, relentless, speed-based
- Empress: dominance through authority and manipulation
- Experiment: cybernetics, body modification, science

Male archetypes: Brute, Veteran, Monster, Technician, Wildcard, Mystic, Prodigy, Experiment
- Brute: raw physical power, intimidation
- Veteran: battle-scarred, tactical, experienced
- Monster: inhuman size and strength, terrifying
- Technician: precise, methodical, strategic
- Wildcard: unpredictable, chaotic
- Mystic: supernatural warrior, ancient traditions
- Prodigy: young phenom, natural talent
- Experiment: enhanced, modified, science project

Identify which is primary (dominant personality/approach) and which is secondary
(adds texture and complication).

The blend should create internal tension. A Viper-Empress has ruthless cunning wrapped
in regal authority. A Siren-Huntress weaponizes beauty but fights with predatory
aggression underneath. The tension within the blend is where personality lives.

### Identity & Origin

- Ring Name: Should be instantly evocative. One or two words that conjure an image or feeling.
- Real Name: Should feel authentic to the character's cultural background.
- Age: Under 25 = still developing. 25-32 = peak. 33+ = declining physically, peaking mentally.
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

1. Sanitizing female character designs. This is the #1 most likely failure mode. The
   AI generating characters will instinctively pull toward modest athletic wear, "practical"
   outfits, and de-sexualized designs for women. Fight this. Female fighters in AFL wear
   revealing, attention-grabbing outfits by design. If a female character's outfit could
   pass in a real UFC broadcast, it's too conservative. Think Mortal Kombat, Dead or Alive,
   Street Fighter — not ESPN.

2. Making a female fighter who isn't attractive. Every female fighter must be beautiful.
   No zombies, no body horror, no monstrous designs. Women in AFL do not compete with men
   on physicality. No female character should be designed around being physically imposing
   relative to the male roster. Rethink around the female archetypes: Siren, Witch, Viper,
   Prodigy, Doll, Huntress, Empress, or Experiment.

3. Making every character clearly good or clearly evil. The roster should be
   overwhelmingly grey. Characters who hurt people and feel complicated about it. Characters
   who do bad things for understandable reasons. Characters who do good things for selfish
   reasons. At most 1-2 characters at the moral extremes, and even those get a 5% crack in
   the armor.

4. Defaulting to "martial artist with supernatural power." New characters should explore
   technology, weapons, science, faith, poison, drugs, hypnotics, ninja tradition, mech
   suits, cybernetics, and other archetypes borrowed from popular media. If the concept is
   "[martial art] + [magical ability]," pivot to something with a different vocabulary.

5. Generic glow effects as primary visual identity. If the character's most notable
   visual feature is that they glow, redo the design. Pass the strip test.

6. "Supernatural seduction" substituting for actual personality. Seduction should work
   through specific human behaviors: how they dress, move, talk, look at you. "Mystical
   allure" without specific mechanism is lazy.

7. No genuine weaknesses. Every fighter needs weaknesses that specific other roster
   members can exploit.

8. Duplicate archetype/style in an already crowded slot. Check the roster. If there are
   already three of an archetype, your version needs a strong reason to exist.

9. Power levels that break matchup dynamics. A new fighter shouldn't be unbeatable by
   anyone on the current roster. If you can't identify their bad matchups, they're
   overpowered.

10. Overly complex supernatural systems for a new character. A debut fighter should
    have 0-2 supernatural stats, not a bespoke magic system.

11. Forgetting the strip test. Remove the supernatural effects. Is the character still
    visually compelling, personality-rich, and distinct? If not, do more work on the human
    foundation before adding anything else.

12. Cheap diversity. Don't add geographic/cultural origins just to check boxes. The origin
    must serve the character concept. Tokenism is boring.
"""

GUIDE_IMAGE_PROMPT_RULES = """## IMAGE PROMPT RULES — FOLLOW EXACTLY

The LLM decides the exact erotic level of the NSFW tier. Do not force visible clit/labia in every character.

image_prompt_clothing_nsfw rules:
- Keep it short (max 8 words total)
- Always start with the remaining iconic features
- Then add whatever nudity level fits the character (examples):
  - "thigh-high boots, choker"
  - "thigh-high boots, choker, completely topless and bottomless"
  - "thigh-high boots, completely topless bottomless shaved pussy visible"
- Never use "crotchless", "transparent", "pulled aside", or long descriptions
- The triple prompt will automatically add "full frontal female nudity" so the image model stays safe and clean

This gives full creative freedom to the character designer while guaranteeing feminine results and consistent style."""

SKIMPINESS_LEVELS = {
    1: {
        "sfw_label": "Covered & Composed",
        "sfw_skin_pct": "15-25",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Conservative — only face, hands, and forearms visible. Full coverage everywhere else.",
        "barely_label": "Flirty",
        "barely_skin_pct": "45-55",
        "barely_guidance": "Suggestive — form-fitting silhouette, cleavage, legs showing. Covered but clearly sexy.",
        "nsfw_adjective": "Tasteful",
        "nsfw_description": "Artistic, elegant posing, minimal anatomical detail. Classical painting energy.",
    },
    2: {
        "sfw_label": "Sporty & Attractive",
        "sfw_skin_pct": "30-45",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Moderate — bare arms, some leg, a peek of midriff. Sporty and attractive.",
        "barely_label": "Risqué",
        "barely_skin_pct": "60-70",
        "barely_guidance": "Risqué — significant skin exposure, sideboob, underbutt. Clearly pushing boundaries.",
        "nsfw_adjective": "Confident",
        "nsfw_description": "Unapologetic nudity, pin-up energy, some anatomical detail.",
    },
    3: {
        "sfw_label": "Revealing",
        "sfw_skin_pct": "50-65",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Revealing — exposed midriff, thighs, cleavage, bare back. Fighting-game sexy.",
        "barely_label": "Scandalous",
        "barely_skin_pct": "75-85",
        "barely_guidance": "Scandalous — most skin exposed, coverage is minimal. Micro clothing only.",
        "nsfw_adjective": "Explicit",
        "nsfw_description": "Anatomical detail visible, nothing hidden. Full display.",
    },
    4: {
        "sfw_label": "Maximum Skin",
        "sfw_skin_pct": "70-85",
        "sfw_hard_rules": "No nipples, no genitalia. Sideboob and cameltoe hints are OK at this level.",
        "sfw_guidance": "Maximum SFW — as much skin as possible without showing nipples or genitalia. Sideboob and cameltoe hints allowed.",
        "barely_label": "Extreme",
        "barely_skin_pct": "95-99",
        "barely_guidance": "Extreme — nipple tape and a tiny strip over the crotch would qualify. Only the absolute anatomical minimums are covered. Body chains, adhesive strips, micro pasties, or paint standing in for actual clothing.",
        "nsfw_adjective": "Provocative",
        "nsfw_description": "Maximum anatomical detail, erotic emphasis. Nothing left to imagination.",
    },
}


OUTFIT_STYLE_RULES = """STYLE RULES (apply to ALL tiers):
- Be CONCISE. No fluff or purple prose. "chain necklace with sickle pendant" not "kusarigama chain necklace with sickle pendant swaying menacingly".
- List MORE pieces of apparel. Include footwear (boots, heels, sandals, sneakers), gloves/hand wraps, jewelry (rings, earrings, bracelets, anklets, chokers), belts, and accessories.
- Every outfit should have at least 4-5 distinct items. Even minimal outfits should specify shoes, jewelry, and accessories."""


def _build_tier_prompt(tier: str, skimpiness_level: int, character_summary: dict) -> str:
    level = SKIMPINESS_LEVELS.get(skimpiness_level, SKIMPINESS_LEVELS[2])
    sig = character_summary.get("iconic_features", "")
    ring_name = character_summary.get("ring_name", "Unknown")
    body_parts = character_summary.get("image_prompt_body_parts", "")
    expression = character_summary.get("image_prompt_expression", "")

    char_context = f"""CHARACTER: {ring_name}
Iconic features (MUST be visible in every tier): {sig}
Body: {body_parts}
Expression: {expression}
SKIMPINESS LEVEL: {skimpiness_level} of 4"""

    if tier == "sfw":
        return f"""{char_context}

Generate the "{level['sfw_label']}" tier outfit for this character (skimpiness {skimpiness_level}/4).

{OUTFIT_STYLE_RULES}

RULES:
  HARD RULES: {level['sfw_hard_rules']}
  SKIN TARGET: ~{level['sfw_skin_pct']}% of skin visible.
  VIBE: {level['sfw_label']} — {level['sfw_guidance']}
  Iconic features + additional clothing pieces to hit the skin target.

You have FULL creative freedom on what clothing items to use. The rules above only constrain HOW MUCH skin shows, not WHAT the outfit looks like.

Return ONLY valid JSON:
{{
  "ring_attire_sfw": "<concise SFW outfit description — list each item plainly, no flowery language>",
  "image_prompt_clothing_sfw": "<SFW clothing for image gen — just the clothing pieces, no adjective fluff>"
}}"""

    elif tier == "barely":
        return f"""{char_context}

Generate the "{level['barely_label']}" tier outfit for this character (skimpiness {skimpiness_level}/4).

{OUTFIT_STYLE_RULES}

RULES:
  HARD RULES: No nipples, no genitalia directly visible. Cameltoe, sideboob, underbutt are OK.
  SKIN TARGET: ~{level['barely_skin_pct']}% of skin visible.
  VIBE: {level['barely_label']} — {level['barely_guidance']}
  Iconic features + additional pieces to hit the skin target.

You have FULL creative freedom on what clothing items to use. The rules above only constrain HOW MUCH skin shows, not WHAT the outfit looks like.

Return ONLY valid JSON:
{{
  "ring_attire": "<concise outfit description — list each item plainly, no flowery language>",
  "image_prompt_clothing": "<clothing for image gen — just the clothing pieces, no adjective fluff>"
}}"""

    else:
        return f"""{char_context}

Generate the NSFW outfit for this character. Tone: {level['nsfw_adjective']}.

{OUTFIT_STYLE_RULES}
ADDITIONAL: Even fully nude characters should still have accessories — boots/heels, gloves, jewelry, chokers, belts, etc. The nudity is the body; the outfit is what remains ON the body.

RULES:
  HARD RULES: Fully nude — topless AND bottomless. Only iconic features and accessories remain.
  TONE: {level['nsfw_adjective']} — {level['nsfw_description']}

{GUIDE_IMAGE_PROMPT_RULES}

Return ONLY valid JSON:
{{
  "ring_attire_nsfw": "<concise NSFW description — nude plus each remaining accessory listed plainly>",
  "image_prompt_clothing_nsfw": "<NSFW clothing for image gen — max 8 words, remaining accessories only>"
}}"""


FULL_CHARACTER_GUIDE = (
    GUIDE_CORE_PHILOSOPHY
    + GUIDE_CREATION_WORKFLOW
    + GUIDE_VISUAL_DESIGN
    + GUIDE_COMMON_MISTAKES
)


def plan_roster(
    config: Config, roster_size: int = 8, existing_fighters: list[dict] = None
) -> list[dict]:
    existing_roster_text = ""
    if existing_fighters:
        roster_lines = []
        for ef in existing_fighters:
            line = (
                f"- {ef.get('ring_name', '?')} ({ef.get('gender', '?')})"
                f" — from {ef.get('origin', '?')}"
            )
            roster_lines.append(line)
        existing_roster_text = (
            "\n\nEXISTING ROSTER (design around these — no duplicates):\n"
            + "\n".join(roster_lines)
        )

    prompt = f"""{GUIDE_CORE_PHILOSOPHY}

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
- Skimpiness: assign each fighter probability weights for skimpiness levels 1-4 based on personality. The weights represent how likely each level is for this character. A Siren might weight heavily toward 3-4, a Prodigy toward 1-2, an Empress toward 2-3. The 4 weights must sum to 100.

Return ONLY valid JSON — an array of {roster_size} objects with this structure:
[
  {{
    "concept_hook": "<one-sentence hook that captures what makes this fighter unique>",
    "ring_name": "<evocative 1-2 word ring name>",
    "gender": "<male|female>",
    "age": <18-45>,
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

    system_prompt = (
        "You are a roster architect for a fantasy fighting league. "
        "Design an interconnected cast of compelling characters. "
        "Always respond with valid JSON only — an array of objects."
    )

    result = call_openrouter_json(
        prompt,
        config,
        system_prompt=system_prompt,
        temperature=0.9,
        max_tokens=8192,
    )

    if isinstance(result, dict) and "roster" in result:
        result = result["roster"]
    if not isinstance(result, list):
        raise RuntimeError(
            f"Expected a JSON array from roster planning, got: {type(result)}"
        )

    return result


def _roll_skimpiness(weights: list[int] | None) -> int:
    if not weights or len(weights) != 4:
        weights = [15, 35, 35, 15]
    total = sum(weights)
    if total <= 0:
        weights = [15, 35, 35, 15]
        total = 100
    normalized = [w / total for w in weights]
    return random.choices([1, 2, 3, 4], weights=normalized, k=1)[0]


def _generate_outfits(
    config: Config,
    character_summary: dict,
    skimpiness_level: int,
    tiers: list[str] | None = None,
) -> dict:
    if tiers is None:
        tiers = ["sfw", "barely", "nsfw"]

    system_prompt = (
        "You are an outfit designer for a fighting league. "
        "Design outfits that match the character's personality and the tier's rules. "
        "Always respond with valid JSON only."
    )

    outfit_data = {}
    for tier in tiers:
        prompt = _build_tier_prompt(tier, skimpiness_level, character_summary)
        result = call_openrouter_json(
            prompt, config, system_prompt=system_prompt, temperature=0.5
        )
        outfit_data.update(result)

    return outfit_data


def generate_fighter(
    config: Config,
    archetype: str = None,
    has_supernatural: bool = False,
    existing_fighters: list[dict] = None,
    roster_plan_entry: dict = None,
) -> Fighter:
    if roster_plan_entry:
        blueprint_text = (
            "BLUEPRINT DIRECTIVE — you MUST follow this plan for the character:\n"
            + json.dumps(roster_plan_entry, indent=2)
            + "\n\nFollow the blueprint closely: use the ring name, origin, gender, "
            "archetype, and supernatural status exactly "
            "as specified. Flesh out the full character from this skeleton."
        )
        has_supernatural = roster_plan_entry.get("has_supernatural", False)
        archetype = roster_plan_entry.get("primary_archetype", archetype)
        skimpiness_level = _roll_skimpiness(roster_plan_entry.get("skimpiness_weights"))
    else:
        blueprint_text = ""
        skimpiness_level = _roll_skimpiness(None)

    supernatural_instruction = ""
    if has_supernatural:
        supernatural_instruction = (
            "This fighter HAS supernatural abilities. Give the supernatural stat "
            "a value between 20-50. The supernatural ability should tie into "
            "their concept naturally."
        )
    else:
        supernatural_instruction = "This fighter has NO supernatural abilities. The supernatural stat must be 0."

    archetype_text = (
        f"Primary archetype: {archetype}" if archetype else "Choose a fitting archetype"
    )

    existing_roster_text = ""
    if existing_fighters:
        roster_lines = []
        for ef in existing_fighters:
            line = (
                f"- {ef.get('ring_name', '?')} ({ef.get('gender', '?')}, {ef.get('height', '?')})"
                f" — from {ef.get('origin', '?')}"
                f" | {ef.get('build', '?')}, {ef.get('distinguishing_features', '?')}"
                f" | Attire: {ef.get('ring_attire', '?')}"
            )
            roster_lines.append(line)
        existing_roster_text = (
            "\n\nEXISTING ROSTER (you MUST create a COMPLETELY DIFFERENT character — "
            "no duplicate ring names, different origin/nationality, "
            "different physical appearance):\n" + "\n".join(roster_lines)
        )

    prompt = f"""{FULL_CHARACTER_GUIDE}

Generate a unique fighter for the AI Fighting League. {archetype_text}.{existing_roster_text}

{blueprint_text}

{supernatural_instruction}

STAT CONSTRAINTS:
- 4 core stats (power, speed, technique, toughness), each rated 15-95
- 1 supernatural stat, rated 0-50 (0 if no supernatural abilities)
- The 4 core stats MUST total between {config.min_total_stats} and {config.max_total_stats}
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
  "age": <18-45>,
  "origin": "<specific city/region, country>",
  "gender": "<male|female>",
  "height": "<height in feet/inches>",
  "weight": "<weight in lbs>",
  "build": "<body type description>",
  "distinguishing_features": "<scars, tattoos, unique physical traits>",
  "iconic_features": "<comma-separated list of 3-6 visual details that make this character instantly recognizable across all tiers>",
  "image_prompt_body_parts": "<physical build, skin tone, hair, face, distinguishing features — shared across all tiers>",
  "image_prompt_expression": "<facial expression and attitude — shared across all tiers>",
  "stats": {{
    "power": <15-95>,
    "speed": <15-95>,
    "technique": <15-95>,
    "toughness": <15-95>,
    "supernatural": <0-50>
  }}
}}"""

    system_prompt = "You are a character designer for a fighting league. Create unique, compelling fighters. Always respond with valid JSON only."

    result = call_openrouter_json(
        prompt, config, system_prompt=system_prompt, temperature=0.5
    )

    fighter_id = f"f_{uuid.uuid4().hex[:8]}"

    stats = _extract_stats(result.get("stats", {}), has_supernatural, config)
    _normalize_core_stats(stats, config)

    body_parts = result.get("image_prompt_body_parts", "")
    expression = result.get("image_prompt_expression", "")
    gender = result.get("gender", "female")

    outfit_data = _generate_outfits(config, result, skimpiness_level)

    clothing_sfw = outfit_data.get("image_prompt_clothing_sfw", "")
    clothing = outfit_data.get("image_prompt_clothing", "")
    clothing_nsfw = outfit_data.get("image_prompt_clothing_nsfw", "")

    return Fighter(
        id=fighter_id,
        ring_name=result.get("ring_name", "Unknown"),
        real_name=result.get("real_name", "Unknown"),
        age=result.get("age", 25),
        origin=result.get("origin", "Unknown"),
        gender=gender,
        height=result.get("height", ""),
        weight=result.get("weight", ""),
        build=result.get("build", ""),
        distinguishing_features=result.get("distinguishing_features", ""),
        iconic_features=result.get("iconic_features", ""),
        ring_attire=outfit_data.get("ring_attire", ""),
        ring_attire_sfw=outfit_data.get("ring_attire_sfw", ""),
        ring_attire_nsfw=outfit_data.get("ring_attire_nsfw", ""),
        skimpiness_level=skimpiness_level,
        image_prompt=_build_charsheet_prompt(
            body_parts, clothing, expression, tier="barely", gender=gender,
        ),
        image_prompt_sfw=_build_charsheet_prompt(
            body_parts, clothing_sfw, expression, tier="sfw", gender=gender,
        ),
        image_prompt_nsfw=_build_charsheet_prompt(
            body_parts, clothing_nsfw, expression, tier="nsfw", gender=gender,
        ),
        image_prompt_triple=_build_triple_prompt(
            body_parts, clothing_sfw, clothing, clothing_nsfw, expression,
            gender=gender,
        ),
        stats=stats,
        record=Record(),
        condition=Condition(),
        storyline_log=[],
        rivalries=[],
        last_fight_date=None,
        ranking=None,
    )


def _extract_stats(data: dict, has_supernatural: bool, config: Config) -> Stats:
    power = max(config.stat_min, min(config.stat_max, int(data.get("power", 50))))
    speed = max(config.stat_min, min(config.stat_max, int(data.get("speed", 50))))
    technique = max(
        config.stat_min, min(config.stat_max, int(data.get("technique", 50)))
    )
    toughness = max(
        config.stat_min, min(config.stat_max, int(data.get("toughness", 50)))
    )

    supernatural = 0
    if has_supernatural:
        supernatural = max(
            0, min(config.supernatural_cap, int(data.get("supernatural", 0)))
        )

    return Stats(
        power=power,
        speed=speed,
        technique=technique,
        toughness=toughness,
        supernatural=supernatural,
    )


CHARSHEET_LAYOUT = (
    "character model sheet, character reference sheet turnaround, "
    "three full-body views of the exact same character side by side: "
    "front-facing view on the left, three-quarter angle view in the center, "
    "rear view on the right, "
    "consistent pose and outfit across all three views, "
    "full body head to toe visible in each panel, standing tall at full height, "
    "plain flat color background, organized reference sheet layout"
)

def _charsheet_style_base(gender: str = "female") -> str:
    return get_art_style(gender) + ", character design reference sheet"


def _charsheet_style(gender: str = "female", tier: str = "barely") -> str:
    base = _charsheet_style_base(gender)
    if tier == "nsfw":
        if gender.lower() == "male":
            nudity_prefix = "explicit uncensored NSFW, full frontal male nudity, fully naked man, "
        else:
            nudity_prefix = "explicit uncensored NSFW, full frontal female nudity, fully naked woman, "
        return nudity_prefix + base + ", " + CHARSHEET_LAYOUT
    return base + ", " + CHARSHEET_LAYOUT


def _charsheet_tail(gender: str = "female", tier: str = "barely") -> str:
    tail_base = get_art_style_tail(gender) + ", character reference sheet turnaround, three consistent views"
    if tier == "nsfw":
        if gender.lower() == "male":
            return (
                get_art_style_tail(gender) + ", "
                "explicit full frontal male nudity, completely naked, muscular physique fully visible, "
                "character reference sheet turnaround, three consistent views"
            )
        return (
            get_art_style_tail(gender) + ", "
            "explicit full frontal female nudity, completely naked, bare breasts and perfectly drawn bare pussy visible, "
            "character reference sheet turnaround, three consistent views"
        )
    return tail_base


def _triple_prompt_style(gender: str = "female") -> str:
    if gender.lower() == "male":
        nsfw_part = "explicit uncensored NSFW right with full frontal male nudity"
    else:
        nsfw_part = "explicit uncensored NSFW right with full frontal female nudity, bare breasts and perfectly drawn bare pussy visible"
    return (
        get_art_style(gender) + ", "
        "stylized fighting game triple portrait, three full-body exact same character standing "
        "side by side left to right in one clean vertical panel layout, "
        "SFW left, barely-SFW center, " + nsfw_part
    )


def _build_charsheet_prompt(
    body_parts: str, clothing: str, expression: str,
    tier: str = "barely", gender: str = "female",
) -> dict:
    if not body_parts:
        return {}

    style = _charsheet_style(gender, tier)

    if tier == "nsfw":
        clothing_part = (
            f"completely naked except {clothing}" if clothing else "completely naked"
        )
    else:
        clothing_part = clothing

    front_view = (
        f"front view: {body_parts}, {clothing_part}"
        if clothing_part
        else f"front view: {body_parts}"
    )
    three_quarter_view = (
        f"three-quarter angle view: {body_parts}, {clothing_part}"
        if clothing_part
        else f"three-quarter angle view: {body_parts}"
    )
    back_view = (
        f"rear view: {body_parts}, {clothing_part}"
        if clothing_part
        else f"rear view: {body_parts}"
    )

    tail = _charsheet_tail(gender, tier)

    full = ", ".join(
        p
        for p in [style, front_view, three_quarter_view, back_view, expression, tail]
        if p
    )
    return {
        "style": style,
        "layout": CHARSHEET_LAYOUT,
        "body_parts": body_parts,
        "clothing": clothing_part,
        "front_view": front_view,
        "three_quarter_view": three_quarter_view,
        "back_view": back_view,
        "expression": expression,
        "full_prompt": full,
    }


def _build_triple_prompt(
    body_parts: str,
    clothing_sfw: str,
    clothing: str,
    clothing_nsfw: str,
    expression: str,
    gender: str = "female",
) -> dict:
    if not body_parts:
        return {}

    triple_style = _triple_prompt_style(gender)
    expr_all = f"{expression} (identical on all three)" if expression else ""

    if gender.lower() == "male":
        nsfw_right = f"right explicit NSFW full male nudity: completely naked except {clothing_nsfw or 'minimal accessories'}"
    else:
        nsfw_right = f"right explicit NSFW full female nudity: completely naked except {clothing_nsfw or 'minimal accessories'}"

    tail = get_art_style_tail(gender) + " across all panels"

    full = ", ".join(
        p
        for p in [
            triple_style,
            body_parts,
            f"left SFW: {clothing_sfw}" if clothing_sfw else "",
            f"center barely-SFW: {clothing}" if clothing else "",
            nsfw_right,
            expr_all,
            tail,
        ]
        if p
    )

    return {
        "style": triple_style,
        "composition": "SFW left, barely-SFW center, explicit NSFW right, identical pose/expression/background",
        "body_parts": body_parts,
        "left": f"SFW: {clothing_sfw}" if clothing_sfw else "",
        "center": f"barely-SFW: {clothing}" if clothing else "",
        "right": f"NSFW: {clothing_nsfw}" if clothing_nsfw else "",
        "expression": expr_all,
        "full_prompt": full,
    }


def _normalize_core_stats(stats: Stats, config: Config):
    total = stats.core_total()

    if config.min_total_stats <= total <= config.max_total_stats:
        return

    target = (config.min_total_stats + config.max_total_stats) // 2
    ratio = target / total if total > 0 else 1.0

    for field_name in ("power", "speed", "technique", "toughness"):
        old_val = getattr(stats, field_name)
        new_val = max(config.stat_min, min(config.stat_max, round(old_val * ratio)))
        setattr(stats, field_name, new_val)
