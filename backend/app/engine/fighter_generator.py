import json
import random
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.config import Config
from app.engine.image_style import get_art_style, get_art_style_tail
from app.models.fighter import Fighter, Stats, Record, Condition
from app.services.openrouter import call_openrouter_json


DEFAULT_OUTFIT_OPTIONS = {
    "sfw": {
        "tops": [
            "sports bra",
            "tank top",
            "halter top",
            "crop top",
            "bustier",
            "bandeau top",
            "fitted combat vest",
            "structured corset armor",
        ],
        "bottoms": [
            "combat shorts",
            "leggings",
            "mini-skirt with bike shorts",
            "cargo pants",
            "high-waisted tactical pants",
            "short battle skirt",
            "micro shorts",
        ],
        "one_pieces": [
            "high-cut leotard",
            "combat romper",
            "armored leotard with shorts",
            "tactical jumpsuit",
            "fitted mini-dress",
        ],
    },
    "barely": {
        "tops": [
            "micro bikini top",
            "tape crosses",
            "nano adhesive nipple pasties",
            "tiny triangle bralette",
            "low-cut wrap top",
            "sideboob slit crop top",
            "deep plunge halter",
            "underboob sling harness",
        ],
        "bottoms": [
            "micro thong",
            "g-string",
            "cut-out shorts",
            "high-leg cut bottoms",
            "nano string bottom",
            "micro adhesive strip covering slit",
        ],
        "one_pieces": [
            "cut-out bodysuit",
            "strappy harness bodysuit",
            "sling-shot micro suit",
            "extreme cut monokini",
            "fishnet body stocking",
        ],
    },
    "nsfw": {
        "tops": [
            "body chains framing bare breasts",
            "chest harness framing bare breasts",
            "shoulder armor only",
            "suspenders framing bare breasts",
            "nipple chain harness",
            "collar with body chains",
            "strappy harness top with bare breasts",
            "cut-out sports bra with bare nipples",
        ],
        "bottoms": [
            "micro thong",
            "g-string",
            "thigh-high boots",
            "garter belt with thigh-highs",
            "thigh harness straps",
            "crotchless thigh straps framing bare pussy",
        ],
        "one_pieces": [
            "chain web full body harness",
            "leather strap open harness",
            "combat harness with open crotch and bare breasts",
            "open-chest bodysuit with bare breasts and thong bottom",
        ],
    },
}


def load_outfit_options(config: Config) -> dict:
    path = Path(config.data_dir) / "outfit_options.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    with open(path, "w") as f:
        json.dump(DEFAULT_OUTFIT_OPTIONS, f, indent=2)
    return dict(DEFAULT_OUTFIT_OPTIONS)


def _parse_outfit_item(item) -> tuple[str, str]:
    if isinstance(item, dict):
        return item.get("name", ""), str(item.get("skimpiness_level", ""))
    return str(item), ""


def _skimpiness_matches(item_level_str: str, fighter_level: int | None) -> bool:
    if not item_level_str or fighter_level is None:
        return True
    item_level_str = item_level_str.strip()
    if "-" in item_level_str:
        parts = item_level_str.split("-")
        try:
            return int(parts[0]) <= fighter_level <= int(parts[1])
        except (ValueError, IndexError):
            return True
    try:
        return int(item_level_str) == fighter_level
    except ValueError:
        return True


def filter_outfit_options(
    options_for_tier: dict,
    skimpiness_level: int | None = None,
) -> dict:
    result = {}
    for key in ["tops", "bottoms", "one_pieces"]:
        full_list = list(options_for_tier.get(key, []))
        if skimpiness_level is not None:
            full_list = [
                item
                for item in full_list
                if _skimpiness_matches(_parse_outfit_item(item)[1], skimpiness_level)
            ]
        if not full_list:
            full_list = list(options_for_tier.get(key, []))
        keep_count = min(3, len(full_list))
        sampled = random.sample(full_list, keep_count)
        random.shuffle(sampled)
        result[key] = [_parse_outfit_item(item)[0] for item in sampled]

    return result


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

BODY_TRAIT_OPTIONS = {
    "waist": ["narrow", "medium", "wide"],
    "abs_tone": [
        "soft with no definition",
        "slight definition",
        "toned and defined",
        "ripped and shredded",
    ],
    "body_fat_pct": ["lean 12-16%", "athletic 17-20%", "fit 21-24%", "soft 25-30%"],
    "butt_size": ["small tight", "medium round", "large full", "very large prominent"],
    "face_shape": [
        "sharp angular",
        "soft round",
        "heart-shaped",
        "oval",
        "diamond",
    ],
    "lip_type": ["full pouty", "bow-shaped", "wide", "plump"],
    "nose_type": [
        "button",
        "upturned",
        "straight",
        "small delicate",
        "petite",
    ],
    "eye_shape": [
        "almond",
        "round",
        "hooded",
        "doe",
        "cat-like",
    ],
    "brow_shape": ["strong thick", "arched", "straight", "delicate thin"],
    "makeup_level": ["bare-faced", "light", "moderate", "heavy", "dramatic"],
    "breast_size": ["small perky", "medium", "large", "very large"],
    "nipple_size": ["small pert", "medium", "perky pointed", "large puffy"],
    "vulva_type": [
        "tucked pussy, small hidden labia",
        "tasteful outer labia",
        "compact petite tight pussy",
        "visible labia minora peeking out",
    ],
}

MAKEUP_DESCRIPTIONS = {
    "bare-faced": "natural beauty, minimal or zero makeup",
    "light": "subtle enhancement, lip tint, light mascara",
    "moderate": "polished look, foundation, defined eyes, lipstick",
    "heavy": "full glam, smoky eyes, contoured, bold lip",
    "dramatic": "theatrical, extreme eye makeup, painted, avant-garde",
}

ARCHETYPE_HEIGHT_RANGES = {
    "The Siren": (62, 69),
    "The Witch": (60, 67),
    "The Viper": (62, 68),
    "The Prodigy": (59, 65),
    "The Doll": (59, 64),
    "The Huntress": (65, 71),
    "The Empress": (65, 70),
    "The Experiment": (60, 69),
}

ARCHETYPE_BODY_WEIGHTS = {
    "The Siren": {
        "breast_size": {"small perky": 5, "medium": 20, "large": 50, "very large": 25},
        "body_fat_pct": {
            "lean 12-16%": 5,
            "athletic 17-20%": 25,
            "fit 21-24%": 50,
            "soft 25-30%": 20,
        },
        "makeup_level": {
            "bare-faced": 2,
            "light": 10,
            "moderate": 30,
            "heavy": 56,
            "dramatic": 2,
        },
        "abs_tone": {
            "soft with no definition": 20,
            "slight definition": 45,
            "toned and defined": 30,
            "ripped and shredded": 5,
        },
        "butt_size": {
            "small tight": 5,
            "medium round": 25,
            "large full": 45,
            "very large prominent": 25,
        },
        "waist": {"narrow": 40, "medium": 45, "wide": 15},
    },
    "The Witch": {
        "breast_size": {"small perky": 20, "medium": 35, "large": 30, "very large": 15},
        "body_fat_pct": {
            "lean 12-16%": 15,
            "athletic 17-20%": 25,
            "fit 21-24%": 35,
            "soft 25-30%": 25,
        },
        "makeup_level": {
            "bare-faced": 5,
            "light": 15,
            "moderate": 30,
            "heavy": 48,
            "dramatic": 2,
        },
        "abs_tone": {
            "soft with no definition": 30,
            "slight definition": 40,
            "toned and defined": 25,
            "ripped and shredded": 5,
        },
        "butt_size": {
            "small tight": 15,
            "medium round": 35,
            "large full": 35,
            "very large prominent": 15,
        },
        "waist": {"narrow": 35, "medium": 45, "wide": 20},
    },
    "The Viper": {
        "breast_size": {"small perky": 25, "medium": 40, "large": 25, "very large": 10},
        "body_fat_pct": {
            "lean 12-16%": 30,
            "athletic 17-20%": 40,
            "fit 21-24%": 25,
            "soft 25-30%": 5,
        },
        "makeup_level": {
            "bare-faced": 10,
            "light": 27,
            "moderate": 36,
            "heavy": 25,
            "dramatic": 2,
        },
        "abs_tone": {
            "soft with no definition": 5,
            "slight definition": 25,
            "toned and defined": 50,
            "ripped and shredded": 20,
        },
        "butt_size": {
            "small tight": 20,
            "medium round": 40,
            "large full": 30,
            "very large prominent": 10,
        },
        "waist": {"narrow": 50, "medium": 40, "wide": 10},
    },
    "The Prodigy": {
        "breast_size": {"small perky": 35, "medium": 40, "large": 20, "very large": 5},
        "body_fat_pct": {
            "lean 12-16%": 40,
            "athletic 17-20%": 40,
            "fit 21-24%": 15,
            "soft 25-30%": 5,
        },
        "makeup_level": {
            "bare-faced": 40,
            "light": 35,
            "moderate": 20,
            "heavy": 5,
            "dramatic": 0,
        },
        "abs_tone": {
            "soft with no definition": 5,
            "slight definition": 15,
            "toned and defined": 55,
            "ripped and shredded": 25,
        },
        "butt_size": {
            "small tight": 30,
            "medium round": 40,
            "large full": 25,
            "very large prominent": 5,
        },
        "waist": {"narrow": 45, "medium": 45, "wide": 10},
    },
    "The Doll": {
        "breast_size": {"small perky": 30, "medium": 35, "large": 25, "very large": 10},
        "body_fat_pct": {
            "lean 12-16%": 15,
            "athletic 17-20%": 25,
            "fit 21-24%": 40,
            "soft 25-30%": 20,
        },
        "makeup_level": {
            "bare-faced": 10,
            "light": 28,
            "moderate": 38,
            "heavy": 22,
            "dramatic": 2,
        },
        "abs_tone": {
            "soft with no definition": 25,
            "slight definition": 40,
            "toned and defined": 30,
            "ripped and shredded": 5,
        },
        "butt_size": {
            "small tight": 15,
            "medium round": 35,
            "large full": 35,
            "very large prominent": 15,
        },
        "waist": {"narrow": 45, "medium": 40, "wide": 15},
    },
    "The Huntress": {
        "breast_size": {"small perky": 20, "medium": 40, "large": 30, "very large": 10},
        "body_fat_pct": {
            "lean 12-16%": 35,
            "athletic 17-20%": 45,
            "fit 21-24%": 15,
            "soft 25-30%": 5,
        },
        "makeup_level": {
            "bare-faced": 35,
            "light": 35,
            "moderate": 20,
            "heavy": 8,
            "dramatic": 2,
        },
        "abs_tone": {
            "soft with no definition": 5,
            "slight definition": 15,
            "toned and defined": 50,
            "ripped and shredded": 30,
        },
        "butt_size": {
            "small tight": 15,
            "medium round": 35,
            "large full": 35,
            "very large prominent": 15,
        },
        "waist": {"narrow": 35, "medium": 50, "wide": 15},
    },
    "The Empress": {
        "breast_size": {"small perky": 5, "medium": 25, "large": 45, "very large": 25},
        "body_fat_pct": {
            "lean 12-16%": 5,
            "athletic 17-20%": 20,
            "fit 21-24%": 45,
            "soft 25-30%": 30,
        },
        "makeup_level": {
            "bare-faced": 2,
            "light": 10,
            "moderate": 38,
            "heavy": 48,
            "dramatic": 2,
        },
        "abs_tone": {
            "soft with no definition": 25,
            "slight definition": 40,
            "toned and defined": 30,
            "ripped and shredded": 5,
        },
        "butt_size": {
            "small tight": 5,
            "medium round": 25,
            "large full": 45,
            "very large prominent": 25,
        },
        "waist": {"narrow": 25, "medium": 45, "wide": 30},
    },
    "The Experiment": {
        "breast_size": {"small perky": 20, "medium": 30, "large": 30, "very large": 20},
        "body_fat_pct": {
            "lean 12-16%": 25,
            "athletic 17-20%": 35,
            "fit 21-24%": 25,
            "soft 25-30%": 15,
        },
        "makeup_level": {
            "bare-faced": 22,
            "light": 25,
            "moderate": 28,
            "heavy": 21,
            "dramatic": 2,
        },
        "abs_tone": {
            "soft with no definition": 10,
            "slight definition": 25,
            "toned and defined": 40,
            "ripped and shredded": 25,
        },
        "butt_size": {
            "small tight": 20,
            "medium round": 30,
            "large full": 30,
            "very large prominent": 20,
        },
        "waist": {"narrow": 30, "medium": 45, "wide": 25},
    },
}


def _weighted_choice(category: str, archetype: str | None) -> str:
    options = BODY_TRAIT_OPTIONS[category]
    weights_dict = {}
    if archetype and archetype in ARCHETYPE_BODY_WEIGHTS:
        weights_dict = ARCHETYPE_BODY_WEIGHTS[archetype].get(category, {})
    if weights_dict:
        weights = [weights_dict.get(opt, 1) for opt in options]
    else:
        weights = [1] * len(options)
    return random.choices(options, weights=weights, k=1)[0]


def _format_height(inches: int) -> str:
    feet = inches // 12
    remaining = inches % 12
    return f"{feet}'{remaining}\""


BODY_FAT_MULTIPLIERS = {
    "lean 12-16%": 0.90,
    "athletic 17-20%": 0.95,
    "fit 21-24%": 1.00,
    "soft 25-30%": 1.08,
}

BREAST_WEIGHT_LBS = {
    "small perky": 1,
    "medium": 3,
    "large": 6,
    "very large": 10,
}

BUTT_WEIGHT_LBS = {
    "small tight": 0,
    "medium round": 2,
    "large full": 5,
    "very large prominent": 9,
}

WAIST_MULTIPLIERS = {
    "narrow": 0.97,
    "medium": 1.00,
    "wide": 1.04,
}


def _derive_weight(height_inches: int, traits: dict) -> int:
    lean_mass = (height_inches - 60) * 3.0 + 105
    bf_mult = BODY_FAT_MULTIPLIERS.get(traits.get("body_fat_pct", ""), 1.0)
    waist_mult = WAIST_MULTIPLIERS.get(traits.get("waist", ""), 1.0)
    base = lean_mass * bf_mult * waist_mult
    base += BREAST_WEIGHT_LBS.get(traits.get("breast_size", ""), 0)
    base += BUTT_WEIGHT_LBS.get(traits.get("butt_size", ""), 0)
    base += random.randint(-3, 3)
    return round(base)


def _roll_body_traits(archetype: str | None) -> dict:
    arch = (
        f"The {archetype}"
        if archetype and not archetype.startswith("The ")
        else archetype
    )

    height_range = ARCHETYPE_HEIGHT_RANGES.get(arch, (59, 71))
    height_inches = random.randint(height_range[0], height_range[1])

    traits = {
        "height_inches": height_inches,
        "waist": _weighted_choice("waist", arch),
        "abs_tone": _weighted_choice("abs_tone", arch),
        "body_fat_pct": _weighted_choice("body_fat_pct", arch),
        "butt_size": _weighted_choice("butt_size", arch),
        "face_shape": _weighted_choice("face_shape", arch),
        "lip_type": _weighted_choice("lip_type", arch),
        "nose_type": _weighted_choice("nose_type", arch),
        "eye_shape": _weighted_choice("eye_shape", arch),
        "brow_shape": _weighted_choice("brow_shape", arch),
        "makeup_level": _weighted_choice("makeup_level", arch),
        "breast_size": _weighted_choice("breast_size", arch),
        "nipple_size": _weighted_choice("nipple_size", arch),
        "vulva_type": _weighted_choice("vulva_type", arch),
    }

    weight_lbs = _derive_weight(height_inches, traits)
    traits["height"] = _format_height(height_inches)
    traits["weight"] = f"{weight_lbs} lbs"

    return traits


def _build_body_directive(traits: dict) -> str:
    makeup_desc = MAKEUP_DESCRIPTIONS.get(
        traits["makeup_level"], traits["makeup_level"]
    )
    return (
        "BODY TYPE DIRECTIVE (you MUST incorporate these exact physical traits):\n"
        f"- Height: {traits['height']}\n"
        f"- Weight: {traits['weight']}\n"
        f"- Breast size: {traits['breast_size']}\n"
        f"- Waist: {traits['waist']}\n"
        f"- Abs/core: {traits['abs_tone']}\n"
        f"- Body fat: {traits['body_fat_pct']}\n"
        f"- Butt: {traits['butt_size']}\n"
        f"- Face: {traits['face_shape']}, {traits['lip_type']} lips, "
        f"{traits['nose_type']} nose, {traits['eye_shape']} eyes, "
        f"{traits['brow_shape']} brows\n"
        f"- Makeup: {traits['makeup_level']} — {makeup_desc}\n"
        "\nThe height and weight are EXACT — use these values directly.\n"
        "Work the other traits naturally into image_prompt_body_parts and image_prompt_expression.\n"
        "IMPORTANT: Interpret ALL facial and body traits through an attractive lens. "
        "Every combination should result in a beautiful, appealing character."
    )


def _build_body_shape_line(traits: dict) -> str:
    return f"{traits['breast_size']} breasts, " f"{traits['butt_size']} butt"


def _build_nsfw_anatomy_line(traits: dict) -> str:
    return (
        f"{traits['breast_size']} breasts, "
        f"{traits['nipple_size']} nipples, "
        f"{traits['butt_size']} butt, "
        f"{traits['vulva_type']}"
    )


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
good SFW version of each character which is family friendly. Most should be white / asian / latina.

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


SKIMPINESS_LEVELS = {
    1: {
        "sfw_label": "Covered & Composed",
        "sfw_skin_pct": "15-25",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Conservative — only face, hands, and forearms visible. Full coverage everywhere else.",
        "barely_label": "Flirty",
        "barely_skin_pct": "45-55",
        "barely_hard_rules": "No nipples, no areola, no genitalia directly visible. Cameltoe, sideboob, underbutt are OK.",
        "barely_guidance": "Suggestive — form-fitting silhouette, cleavage, legs showing. Covered but clearly sexy.",
        "nsfw_adjective": "Scandalous",
        "nsfw_hard_rules": "Topless — bare breasts fully visible. Bottoms stay on but must be ultra-sexy: thongs, micro-bikini bottoms, strappy lingerie, or sheer panties. Show off legs and hips.",
        "nsfw_description": "Topless and unapologetic. Sultry, confident posing. Bottoms are barely-there and designed to tease — maximum skin, minimum fabric below the waist.",
        "nsfw_nudity_level": "topless",
    },
    2: {
        "sfw_label": "Sporty & Attractive",
        "sfw_skin_pct": "30-45",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Moderate — bare arms, some leg, a peek of midriff. Sporty and attractive.",
        "barely_label": "Risqué",
        "barely_skin_pct": "60-70",
        "barely_hard_rules": "No nipples, no areola, no genitalia directly visible. Cameltoe, sideboob, underbutt are OK.",
        "barely_guidance": "Risqué — significant skin exposure, sideboob, underbutt. Clearly pushing boundaries.",
        "nsfw_adjective": "Confident",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, pussy visible.",
        "nsfw_description": "Confident pin-up energy. Completely nude, no bottom garment. Pussy fully visible.",
        "nsfw_nudity_level": "full",
    },
    3: {
        "sfw_label": "Bold",
        "sfw_skin_pct": "50-65",
        "sfw_hard_rules": "No nipples, no genitalia, no underboob, no sideboob, no cameltoe. Family-friendly.",
        "sfw_guidance": "Bold — shows skin confidently but still looks like a real outfit.",
        "barely_label": "Scandalous",
        "barely_skin_pct": "75-85",
        "barely_hard_rules": "No full nipples, but areola peeking out from micro pasties is OK. No genitalia directly visible. Cameltoe, sideboob, underbutt are OK.",
        "barely_guidance": "Scandalous — most skin exposed, coverage is minimal. Micro clothing only. Areola peeking out from tiny pasties is encouraged.",
        "nsfw_adjective": "Tease",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, pussy visible. Teasing posture — a finger resting playfully near her clit or cupping a breast or running her hands along her body - teasing sensually.",
        "nsfw_description": "Teasing, playful energy. Anatomy on display with flirty self-touching.",
        "nsfw_nudity_level": "full",
    },
    4: {
        "sfw_label": "Daring",
        "sfw_skin_pct": "60-75",
        "sfw_hard_rules": "No nipples, no genitalia. Sideboob hints are OK at this level.",
        "sfw_guidance": "Daring — the outfit is minimal but intentional. Looks great and happens to show skin.",
        "barely_label": "Extreme",
        "barely_skin_pct": "99",
        "barely_hard_rules": "No full nipples, but areola peeking out from micro pasties is OK. No genitalia directly visible. Cameltoe, sideboob, underbutt are OK.",
        "barely_guidance": "Extreme — micro pasties with areola peeking out and a tiny nail-sized strip over the clit. Areola exposure is expected at this level.",
        "nsfw_adjective": "Pornographic",
        "nsfw_hard_rules": "Fully nude — topless and bottomless, legs apart or spread, pussy fully displayed. Explicit posing.",
        "nsfw_description": "Maximum explicit posing. Pierced nipples allowed or tiny subtle clit piercings allowed (tasteful small rings only). Spreading, legs open, erotic emphasis on genitalia. Nothing left to imagination.",
        "nsfw_nudity_level": "full",
    },
}


OUTFIT_STYLE_RULES = """STYLE RULES (apply to ALL tiers):
- Be CONCISE. No fluff or purple prose. "chain necklace with sickle pendant" not "kusarigama chain necklace with sickle pendant swaying menacingly".
- List MORE pieces of apparel. Include footwear, gloves/hand wraps, jewelry, belts, and accessories.
- Above all, the character needs to LOOK COOL and dangerous in their outift.
- Every outfit should have at least 4-5 distinct items. Even minimal outfits should specify shoes, jewelry, gloves, and accessories.
- FOOTWEAR: Avoid stilettos unless a strong personality match with the character. Prefer combat boots, sneakers, bare feet, platform boots, or flats."""


def _build_tier_prompt(
    tier: str,
    skimpiness_level: int,
    character_summary: dict,
    outfit_options: dict | None = None,
) -> str:
    level = SKIMPINESS_LEVELS.get(skimpiness_level, SKIMPINESS_LEVELS[2])
    sig = character_summary.get("iconic_features", "")
    ring_name = character_summary.get("ring_name", "Unknown")
    body_parts = character_summary.get("image_prompt_body_parts", "")
    expression = character_summary.get("image_prompt_expression", "")

    if tier == "barely":
        effective_skimpiness = skimpiness_level + 4
    else:
        effective_skimpiness = skimpiness_level

    char_base = f"""CHARACTER: {ring_name}
Iconic features (MUST be visible in every tier): {sig}
Body: {body_parts}
Expression: {expression}"""

    body_details = character_summary.get("body_type_details", {})
    if body_details:
        char_base += f"\n{_build_body_shape_line(body_details)}"
        if tier == "nsfw":
            char_base += f"\n{_build_nsfw_anatomy_line(body_details)}"

    if tier == "nsfw":
        char_context = char_base
    else:
        char_context = char_base + f"\nSKIMPINESS LEVEL: {effective_skimpiness} of 8"

    outfit_examples_text = ""
    if outfit_options:
        tops = outfit_options.get("tops", [])
        bottoms = outfit_options.get("bottoms", [])
        one_pieces = outfit_options.get("one_pieces", [])
        lines = []
        if tops:
            lines.append(f"Example tops to consider: {', '.join(tops)}")
        if bottoms:
            lines.append(f"Example bottoms to consider: {', '.join(bottoms)}")
        if one_pieces:
            lines.append(
                f"Example one-pieces to consider (use instead of top+bottom): {', '.join(one_pieces)}"
            )
        if lines:
            outfit_examples_text = "\n" + "\n".join(lines) + "\n"

    if tier == "sfw":
        return f"""{char_context}

Generate the "{level['sfw_label']}" tier outfit for this character (skimpiness {effective_skimpiness}/8).

{OUTFIT_STYLE_RULES}
{outfit_examples_text}
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

    elif tier == "barely":
        return f"""{char_context}

Generate the "{level['barely_label']}" tier outfit for this character (skimpiness {effective_skimpiness}/8).

{OUTFIT_STYLE_RULES}
{outfit_examples_text}
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

    else:
        nudity_level = level.get("nsfw_nudity_level", "full")
        if nudity_level == "topless":
            additional = (
                "ADDITIONAL: The character is topless but keeps bottoms on. "
                "The bottoms (if they can be called that) must be ultra-sexy - tape, jewelry, insanely tiny triangle bottom gstring, etc"
                "Still include accessories — boots/heels, gloves, jewelry, chokers, belts, etc. "
                "The image_prompt_clothing_nsfw MUST include the sexy bottom garment plus accessories."
            )
            attire_hint = "topless plus ultra-sexy bottom and each remaining accessory listed plainly"
            clothing_hint = "sexy bottom garment plus accessories"
            image_prompt_rules = (
                "## IMAGE PROMPT RULES — FOLLOW EXACTLY\n\n"
                "image_prompt_clothing_nsfw rules:\n"
                "- Keep it short\n"
                "- Always start with the remaining iconic features\n"
                "- This is Level 1 (topless only): include the sexy bottom garment."
                "- The charsheet prompt automatically adds the topless framing"
            )
        else:
            additional = (
                "ADDITIONAL: Even fully NSFW characters should still have accessories — "
                "boots/heels, gloves, jewelry, chokers, belts, etc. "
                "The nudity is the nipples and crotch; the outfit is what remains ON the body."
            )
            attire_hint = "nude plus each remaining accessory listed plainly"
            clothing_hint = "remaining accessories only"
            image_prompt_rules = (
                "## IMAGE PROMPT RULES — FOLLOW EXACTLY\n\n"
                "image_prompt_clothing_nsfw rules:\n"
                "- Keep it short\n"
                "- Always start with the remaining iconic features\n"
                "- This is Levels 2-4 (fully nude): only accessories remain."
                "- The charsheet prompt automatically adds the nudity framing"
            )

        return f"""{char_context}

Generate the NSFW outfit for this character. Tone: {level['nsfw_adjective']}.

{OUTFIT_STYLE_RULES}
{outfit_examples_text}
{additional}

RULES:
  HARD RULES: {level['nsfw_hard_rules']}. Only iconic features and accessories remain.
  TONE: {level['nsfw_adjective']} — {level['nsfw_description']}

{image_prompt_rules}

POSE: Also generate a short personality pose for this NSFW tier that matches the tone: {level['nsfw_adjective']}. 5-15 words max describing body position and attitude.

Return ONLY valid JSON:
{{
  "ring_attire_nsfw": "<concise NSFW description — {attire_hint}>",
  "image_prompt_clothing_nsfw": "<NSFW clothing for image gen — {clothing_hint}>",
  "image_prompt_pose_nsfw": "<concise NSFW pose matching the {level['nsfw_adjective']} tone — 5-15 words>"}}"""


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
    outfit_options_by_tier: dict | None = None,
) -> dict:
    if tiers is None:
        tiers = ["sfw", "barely", "nsfw"]

    system_prompt = (
        "You are an outfit designer for a fighting league. "
        "Design outfits that match the character's personality and the tier's rules. "
        "Always respond with valid JSON only."
    )

    def _fetch_tier(tier):
        tier_opts = (outfit_options_by_tier or {}).get(tier)
        prompt = _build_tier_prompt(
            tier, skimpiness_level, character_summary, outfit_options=tier_opts
        )
        result = call_openrouter_json(
            prompt, config, system_prompt=system_prompt, temperature=0.5
        )
        return tier, result

    outfit_data = {}
    outfit_suggestions = {}
    with ThreadPoolExecutor(max_workers=len(tiers)) as pool:
        results = pool.map(_fetch_tier, tiers)
    for tier, result in results:
        tier_opts = (outfit_options_by_tier or {}).get(tier)
        if tier_opts:
            outfit_suggestions[tier] = tier_opts
        outfit_data.update(result)

    outfit_data["_outfit_suggestions"] = outfit_suggestions
    return outfit_data


def generate_fighter(
    config: Config,
    archetype: str = None,
    has_supernatural: bool = False,
    existing_fighters: list[dict] = None,
    roster_plan_entry: dict = None,
    tiers: list[str] | None = None,
    outfit_options_by_tier: dict | None = None,
    skimpiness_level: int | None = None,
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
        if skimpiness_level is None:
            skimpiness_level = _roll_skimpiness(
                roster_plan_entry.get("skimpiness_weights")
            )
    else:
        blueprint_text = ""
        if skimpiness_level is None:
            skimpiness_level = _roll_skimpiness(None)

    body_traits = _roll_body_traits(archetype)
    body_directive = _build_body_directive(body_traits)

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

{body_directive}

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
  "age": <18-34>,
  "origin": "<specific city/region, country>",
  "gender": "<male|female>",
  "build": "<body type description incorporating the rolled body traits above>",
  "distinguishing_features": "<scars, tattoos, unique physical traits>",
  "iconic_features": "<comma-separated list of 3-6 visual details that make this character instantly recognizable across all tiers>",
  "personality": "<max 10 words — their vibe and attitude, e.g. 'cold, calculating predator who enjoys breaking opponents slowly'>",
  "image_prompt_body_parts": "<physical build, skin tone, hair, face, distinguishing features — shared across all tiers. IMPORTANT: for skin tone descriptions NEVER use metaphorical terms like 'golden', 'olive', 'bronze', 'caramel', 'porcelain', 'ebony' — the image model takes these literally. MUST incorporate the rolled body traits (waist, abs, butt, face shape, lips, nose, eyes, brows, makeup) naturally into this description>",
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

    system_prompt = "You are a character designer for a fighting league. Create unique, compelling fighters. Always respond with valid JSON only."

    result = call_openrouter_json(
        prompt, config, system_prompt=system_prompt, temperature=0.5
    )

    fighter_id = f"f_{uuid.uuid4().hex[:8]}"

    stats = _extract_stats(result.get("stats", {}), has_supernatural, config)
    _normalize_core_stats(stats, config)

    body_parts = result.get("image_prompt_body_parts", "")
    expression = result.get("image_prompt_expression", "")
    personality_pose = result.get("image_prompt_personality_pose", "")
    gender = result.get("gender", "female")

    result["body_type_details"] = body_traits

    outfit_data = _generate_outfits(
        config,
        result,
        skimpiness_level,
        tiers=tiers,
        outfit_options_by_tier=outfit_options_by_tier,
    )

    outfit_suggestions = outfit_data.pop("_outfit_suggestions", {})

    clothing_sfw = outfit_data.get("image_prompt_clothing_sfw", "")
    clothing = outfit_data.get("image_prompt_clothing", "")
    clothing_nsfw = outfit_data.get("image_prompt_clothing_nsfw", "")

    pose_sfw = outfit_data.get("image_prompt_pose_sfw", "") or personality_pose
    pose_barely = outfit_data.get("image_prompt_pose", "") or personality_pose
    pose_nsfw = outfit_data.get("image_prompt_pose_nsfw", "") or personality_pose

    return Fighter(
        id=fighter_id,
        ring_name=result.get("ring_name", "Unknown"),
        real_name=result.get("real_name", "Unknown"),
        age=result.get("age", 25),
        origin=result.get("origin", "Unknown"),
        gender=gender,
        height=body_traits["height"],
        weight=body_traits["weight"],
        build=result.get("build", ""),
        distinguishing_features=result.get("distinguishing_features", ""),
        iconic_features=result.get("iconic_features", ""),
        personality=result.get("personality", ""),
        image_prompt_personality_pose=personality_pose,
        ring_attire=outfit_data.get("ring_attire", ""),
        ring_attire_sfw=outfit_data.get("ring_attire_sfw", ""),
        ring_attire_nsfw=outfit_data.get("ring_attire_nsfw", ""),
        skimpiness_level=skimpiness_level,
        image_prompt=_build_charsheet_prompt(
            body_parts,
            clothing,
            expression,
            personality_pose=pose_barely,
            tier="barely",
            gender=gender,
            skimpiness_level=skimpiness_level,
            body_type_details=body_traits,
        ),
        image_prompt_sfw=_build_charsheet_prompt(
            body_parts,
            clothing_sfw,
            expression,
            personality_pose=pose_sfw,
            tier="sfw",
            gender=gender,
            skimpiness_level=skimpiness_level,
            body_type_details=body_traits,
        ),
        image_prompt_nsfw=_build_charsheet_prompt(
            body_parts,
            clothing_nsfw,
            expression,
            personality_pose=pose_nsfw,
            tier="nsfw",
            gender=gender,
            skimpiness_level=skimpiness_level,
            body_type_details=body_traits,
        ),
        stats=stats,
        record=Record(),
        condition=Condition(),
        storyline_log=[],
        outfit_suggestions=outfit_suggestions,
        body_type_details=body_traits,
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
    "character model sheet, character reference sheet, "
    "three full-body views of the exact same character side by side: "
    "front-facing slightly angled view on the left, "
    "personality pose in the center, "
    "rear view on the right, "
    "consistent outfit across all three views, "
    "full body head to toe visible in each panel, "
    "plain flat color background, organized reference sheet layout"
)


def _charsheet_style_base(gender: str = "female") -> str:
    return get_art_style(gender) + ", character design reference sheet"


def _charsheet_style(
    gender: str = "female", tier: str = "barely", skimpiness_level: int = 4
) -> str:
    base = _charsheet_style_base(gender)
    if tier == "nsfw":
        if gender.lower() == "male":
            nudity_prefix = (
                "explicit uncensored NSFW, full frontal male nudity, fully naked man, "
            )
        elif skimpiness_level == 1:
            nudity_prefix = (
                "explicit uncensored NSFW, topless woman, bare breasts visible, "
            )
        else:
            nudity_prefix = "explicit uncensored NSFW, perfectly drawn bare pussy visible, full frontal female nudity, "
        return nudity_prefix + base + ", " + CHARSHEET_LAYOUT
    return base + ", " + CHARSHEET_LAYOUT


def _charsheet_tail(
    gender: str = "female", tier: str = "barely", skimpiness_level: int = 4
) -> str:
    tail_base = (
        get_art_style_tail(gender)
        + ", character reference sheet, three consistent views"
    )
    if tier == "nsfw":
        if gender.lower() == "male":
            return (
                get_art_style_tail(gender) + ", "
                "explicit full frontal male nudity, completely naked, muscular physique fully visible, "
                "character reference sheet, three consistent views"
            )
        if skimpiness_level == 1:
            return (
                get_art_style_tail(gender) + ", "
                "topless female nudity, bare breasts visible, "
                "character reference sheet, three consistent views"
            )
        return (
            get_art_style_tail(gender) + ", "
            "explicit full frontal female nudity, completely naked, bare breasts and perfectly drawn bare pussy visible, "
            "character reference sheet, three consistent views"
        )
    return tail_base


def _build_charsheet_prompt(
    body_parts: str,
    clothing: str,
    expression: str,
    personality_pose: str = "",
    tier: str = "barely",
    gender: str = "female",
    skimpiness_level: int = 4,
    body_type_details: dict | None = None,
) -> dict:
    if not body_parts:
        return {}

    anatomy = ""
    if body_type_details:
        body_parts = f"{body_parts}, {_build_body_shape_line(body_type_details)}"
        if tier == "nsfw":
            anatomy = _build_nsfw_anatomy_line(body_type_details)

    style = _charsheet_style(gender, tier, skimpiness_level)

    pose_base = personality_pose or "dynamic signature pose"

    if tier == "nsfw":
        if skimpiness_level == 1:
            clothing_part = (
                f"topless, bare breasts, {clothing}"
                if clothing
                else "topless, bare breasts"
            )
        else:
            clothing_part = (
                f"completely naked except {clothing}"
                if clothing
                else "completely naked"
            )
    else:
        clothing_part = clothing

    character_desc = body_parts
    if clothing_part:
        character_desc = f"{body_parts}, {clothing_part}"

    front_view = "front slightly angled view standing tall"
    center_pose = f"center personality pose: {pose_base}"
    back_view = "rear view standing tall"

    tail = _charsheet_tail(gender, tier, skimpiness_level)

    sections = [
        f"[STYLE] {style}",
        f"[CHARACTER] {character_desc}",
        f"[ANATOMY] {anatomy}" if anatomy else "",
        f"[VIEWS] {front_view}, {center_pose}, {back_view}",
        f"[EXPRESSION] {expression}" if expression else "",
        f"[QUALITY] {tail}",
        f"[ANATOMY EMPHASIS] {anatomy}" if anatomy else "",
    ]
    full = "\n".join(s for s in sections if s)

    return {
        "style": style,
        "layout": CHARSHEET_LAYOUT,
        "body_parts": body_parts,
        "clothing": clothing_part,
        "character_desc": character_desc,
        "front_view": front_view,
        "center_pose": center_pose,
        "back_view": back_view,
        "expression": expression,
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
