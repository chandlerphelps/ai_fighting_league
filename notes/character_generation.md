# Character Generation System

How fighters are created, from abstract roster plan to final image prompts.

## Pipeline Overview

```
Roster Plan (LLM)
  -> Fighter JSON (LLM)
     -> Body Traits (random, weighted)
     -> Stats (random, weighted)
     -> Outfits x3 tiers (LLM)
        -> Image Prompts (deterministic assembly)
           -> Images via Grok (body_ref -> charsheets)
```

Generation stages tracked on `Fighter.generation_stage`:
- **0**: Not started
- **1**: JSON only (character + outfits, no image prompts) — `generate_fighter_json_only()`
- **2**: Portrait/headshot generated
- **3**: Full charsheets generated

---

## Stage 0: Roster Planning

**Entry**: `plan_roster()` in `fighter_generator.py`
**LLM call**: minimax/minimax-m2.5, temp 0.9, system prompt = `SYSTEM_PROMPT_ROSTER_PLANNER`

The planner gets:
- `GUIDE_CORE_PHILOSOPHY` (or male/mixed variant) + `GUIDE_COMMON_MISTAKES`
- Existing roster summary (pool summary or fighter list) for deduplication
- Shuffled archetype + subtype lists (randomized order to reduce LLM position bias)
- Constraints: archetype diversity, geography, supernatural mix, skimpiness weights, visual identity uniqueness

Returns JSON array of plan entries with: `ring_name`, `gender`, `age`, `origin`, `primary_archetype`, `subtype`, `has_supernatural`, `power_tier`, `skimpiness_weights[4]`, `primary_outfit_color`, `hair_style`, `hair_color`, `hair_color_bucket`, `face_adornment`.

**Visual identity palette** — enforced uniqueness across roster:
- `OUTFIT_COLOR_PALETTE`: 24 colors (Crimson Red, Royal Blue, etc.)
- `HAIR_COLOR_BUCKETS`: 10 categories (Black, Brown, Blonde, Red/Auburn, etc.)
- `classify_hair_color()`: keyword-matching classifier maps freetext -> bucket

---

## Stage 1: Fighter Generation

**Entry**: `generate_fighter()` in `fighter_generator.py`
**LLM call**: OpenRouter default model, temp 0.5, system prompt = `SYSTEM_PROMPT_CHARACTER_DESIGNER`

### Inputs assembled before the LLM call

1. **Blueprint** (from roster plan entry, if any): ring name, origin, gender, archetype, supernatural, subtype — injected as `BLUEPRINT DIRECTIVE`
2. **Subtype** (from plan or random roll via `_roll_subtype()`): injected as `SUBTYPE IDENTITY` block
3. **Body traits** (random roll, see below): injected as `BODY TYPE DIRECTIVE`
4. **Character guide** (gender-appropriate): `FULL_CHARACTER_GUIDE` or `FULL_MALE_CHARACTER_GUIDE`
5. **Existing roster** (dedup list): names, origins, builds, attire
6. **Supernatural instruction**: stat range guidance

### Body Trait Rolling (`_roll_body_traits()`)

This is the core physical randomization system. All traits are pre-rolled before the LLM sees them.

**Flow**:
```
archetype + subtype -> body profile (weighted) -> trait options (constrained) -> per-trait weighted choice
```

#### Female body profiles (4): Petite, Slim, Athletic, Curvy
Each profile constrains which options are available for: body_fat_pct, abs_tone, waist, breast_size, butt_size.

`ARCHETYPE_BODY_PROFILE_WEIGHTS` maps archetype -> profile probabilities:
- Siren: 55% Curvy, 20% Slim/Athletic, 5% Petite
- Assassin: 40% Athletic, 30% Slim, 20% Petite, 10% Curvy
- Doll: 35% Petite, 28% Curvy, 25% Slim, 12% Athletic

Subtype `body_profile_bias` adjusts these weights (e.g., Succubus adds +30 Curvy, -20 Petite).

#### Female traits rolled (17 total):
- **Body**: waist, abs_tone, body_fat_pct, butt_size, breast_size, nipple_size, vulva_type
- **Face**: face_shape, eye_shape, nose_shape, lip_shape, brow_shape, cheekbone, jawline, makeup_level
- **Derived**: height (from `ARCHETYPE_HEIGHT_RANGES`, e.g. Siren 5'2"-5'9"), weight (formula using height + body fat + breast/butt modifiers)

`ARCHETYPE_BODY_WEIGHTS` provides per-archetype weighted distributions for many traits. Example: Siren breast_size weights `{tiny: 2, small: 7, medium: 23, large: 50, massive: 18}`.

`_weighted_choice()` picks a trait value using archetype weights if available, uniform otherwise.

#### Male body profiles (7): Skinny, Wiry, Athletic, Muscular, Stocky, Heavy, Massive

Each constrains: body_fat_pct, muscle_definition, shoulder_width, chest_build, build_type, waist.

`MALE_ARCHETYPE_BODY_PROFILE_WEIGHTS`: e.g. Monster = 50% Massive, 25% Heavy, 15% Muscular.

#### Male traits rolled (10 total):
- **Body**: build_type, muscle_definition, body_fat_pct, shoulder_width, chest_build, waist
- **Face**: face_shape, eye_expression, facial_hair
- **Derived**: height (from `MALE_ARCHETYPE_HEIGHT_RANGES`, e.g. Monster 6'2"-6'8"), weight (different formula: higher base, build bonus)

#### Weight derivation
- **Female**: `base = (height_in - 60) * 3.0 + 105`, modified by body_fat multiplier, waist multiplier, breast weight (+0-10 lbs), butt weight (+0-9 lbs), +/- 3 random
- **Male**: `base = (height_in - 60) * 5.0 + 140`, modified by body_fat multiplier, waist multiplier, build bonus (+/- 15-35 lbs), +/- 5 random

### LLM output (character JSON)

The LLM returns: `ring_name`, `real_name`, `age`, `origin`, `gender`, `build`, `distinguishing_features`, `iconic_features`, `personality`, `image_prompt_body_parts`, `image_prompt_expression`, `image_prompt_personality_pose`.

Key constraint in the prompt: skin tone descriptions must avoid metaphorical terms (golden, olive, bronze, etc.) because the image model takes them literally.

### Stats Generation (`generate_archetype_stats()`)

Stats are NOT from the LLM — they're generated independently.

**Core stats** (power, speed, technique, toughness):
- Target total drawn from normal distribution between `config.min_total_stats` and `config.max_total_stats`
- Distributed according to `ARCHETYPE_STAT_WEIGHTS` with per-stat jitter (gaussian noise sigma=2)
- Males get flat bonus: power +6, toughness +4 (gaussian around those values)

**Secondary stats**:
- `guile`: female 45-100 (normal), male 0-15
- `supernatural`: female 30-100 if has_supernatural (else 0), male 0-20 if has_supernatural (else 0)

---

## Stage 1b: Outfit Generation

**Entry**: `_generate_outfits()` in `fighter_generator.py`
**LLM calls**: 3 parallel calls (one per tier), temp 0.5, system prompt = `SYSTEM_PROMPT_OUTFIT_DESIGNER`
**Prompt builder**: `build_tier_prompt()` in `outfit_prompts.py`

### Tiers

| Tier | Female | Male |
|------|--------|------|
| `sfw` | Family-friendly, skin % varies by skimpiness | Battle Ready to Intimidating |
| `barely` | Suggestive to extreme, effective_skimpiness = level + 4 | Stripped Down to Primal |
| `nsfw` | Topless (level 1) or fully nude (levels 2-4) | Same as barely (no nsfw tier for males) |

### Skimpiness System

`_roll_skimpiness()`: weighted random 1-4. Plan entries can specify `skimpiness_weights[4]` (must sum to 100). Default: `[10, 30, 38, 22]`.

**Female `SKIMPINESS_LEVELS`** (4 levels, each defines sfw/barely/nsfw rules):
- Level 1: SFW 15-25% skin, Barely "Flirty" 45-55%, NSFW "Scandalous" (topless only)
- Level 2: SFW 30-45% "Sporty", Barely "Risque" 60-70%, NSFW "Confident" (full nude)
- Level 3: SFW 50-65% "Bold", Barely "Scandalous" 75-85%, NSFW "Tease" (full nude, self-touching)
- Level 4: SFW 60-75% "Daring", Barely "Extreme" 99%, NSFW "Pornographic" (explicit posing)

**Male `MALE_SKIMPINESS_LEVELS`** (4 levels, sfw/barely only):
- Level 1: SFW "Battle Ready" 15-30%, Barely "Stripped Down" 40-55%
- Level 4: SFW "Intimidating" 40-55%, Barely "Primal" 65-80%

### Outfit context injected into prompts

Each tier prompt receives:
- Character summary (ring_name, archetype, subtype with description, personality, iconic_features, body_parts, expression)
- `_build_body_shape_line()`: e.g. "petite 5'2\", small perky breasts (covered), tiny tight butt"
- NSFW tiers also get `_build_nsfw_anatomy_line()`: breast/nipple/butt/vulva details
- `OUTFIT_STYLE_RULES`: conciseness, 4-5 items minimum, combat footwear preference
- Tier-specific rules: hard rules, skin target %, vibe guidance
- Optional `outfit_options` (from `outfit_options.json`): sampled tops, bottoms, one-pieces, exotic one-pieces
- `tech_level`: random from 6 options (Fantasy Medieval through Sci-Fi / Far Future)

### Outfit options system

Two JSON files in `/data/`:
- `outfit_options.json`: generic tops/bottoms/one_pieces per tier, filtered by skimpiness level
- `exotic_outfit_options.json`: archetype/subtype-specific items with tier variations

`filter_outfit_options()`: samples up to 3 items per category, filtered by skimpiness compatibility.
`filter_exotic_for_fighter()`: matches by archetype or subtype, returns tier-appropriate variants.

### LLM output (per tier)

- `ring_attire[_sfw|_nsfw]`: text description of the outfit
- `image_prompt_clothing[_sfw||_nsfw]`: clothing string for image generation
- `image_prompt_pose[_sfw||_nsfw]`: tier-appropriate pose (5-15 words)

---

## Image Prompt Assembly

All prompt assembly happens in `image_builders.py`. These are **deterministic** — no LLM calls, just string concatenation from previously generated data.

### Art Style (`image_style.py`)

Base style: "hand-painted textures over detailed 3D forms, extremely detailed skin and fabric textures, painterly brushstroke overlay, rich moody color grading, dramatic volumetric lighting with atmospheric haze..."

- Female adds: "strictly female character, feminine curves and anatomy, beautiful face"
- Male adds: "male character, masculine build and anatomy, imposing physique, chiseled jaw"
- Tail variants reinforce style at end of prompt

### Charsheet Prompt (`_build_charsheet_prompt()`)

Output: dict with `style`, `layout`, `body_parts`, `clothing`, `character_desc`, `front_view`, `back_view`, `expression`, `full_prompt`.

**Assembly order in `full_prompt`**:
```
[STYLE] art_style + charsheet_layout + (NSFW prefix if nsfw tier)
[CHARACTER] body_parts + body_shape_line + subtype_aesthetic + clothing + iconic_features + age + origin
[ANATOMY] nsfw_anatomy_line (barely/nsfw tiers only)
[VIEWS] front-facing view with personality_pose, rear view
[EXPRESSION] expression
[QUALITY] art_style_tail + (NSFW tail if nsfw tier)
[ANATOMY EMPHASIS] repeated anatomy line (for emphasis)
```

**Key helper functions**:
- `_enrich_body_parts()`: appends body shape line + subtype aesthetic to base body_parts
- `_build_clothing_part()`: prepends outfit color, handles nsfw framing ("topless, bare breasts" or "completely naked except...")
- `_build_character_desc()`: combines body_parts + clothing + age + origin

**NSFW framing**:
- Skimpiness 1: "topless woman, bare breasts visible"
- Skimpiness 2-4: "full frontal female nudity, perfectly drawn bare pussy visible"
- Males: "full frontal male nudity, fully naked man"

### Body Reference Prompt (`build_body_reference_prompt()`)

**Female**: 5-panel anatomy study page (face, rear angled, torso, butt, intimate). Uses `BODY_REF_STYLE_FEMALE`, `BODY_REF_PAGE_STYLE`, `BODY_REF_LAYOUT`. Each panel is a detailed standalone description using rolled body traits (breast_size, nipple_size, butt_size, vulva_type, face details, etc.).

**Male**: 3-panel anatomy study (face, front body in underwear, rear body in underwear). Uses `MALE_BODY_REF_*` variants. Less explicit — no intimate panels.

### Other prompts
- `build_portrait_prompt()`: SFW upper-body shot with `PORTRAIT_STYLE`
- `build_headshot_prompt()`: extreme close-up face shot with `HEADSHOT_STYLE` (character select screen energy)
- `build_move_image_prompt()`: action pose with move name + snapshot, dynamic combat style

---

## Image Generation (`grok_image.py`)

Uses Grok `grok-imagine-image` model via REST API.

### Generation flow in `generate_charsheet_images()`

```
1. Generate body_ref (or reuse existing)
   - Female: edit_image() using reference_images/female/pussy_asshole_behind2.png as base
   - Male: generate_image() from scratch
2. For each tier (sfw, barely, nsfw):
   - Female: edit_image() using body_ref as base (consistency)
   - Male: generate_image() from scratch
3. All tier images generated in parallel via ThreadPoolExecutor
```

The body_ref -> charsheet pipeline is key: female charsheets use `edit_image()` with the body_ref as input, so the body reference image anchors visual consistency across all tiers.

### API details
- `generate_image()`: POST to `/images/generations`, returns URLs
- `edit_image()`: POST to `/images/edits` with base64-encoded input images
- Both: 5 retries with exponential backoff, 120s timeout
- Default: 1:1 aspect ratio, 2k resolution
- `_pad_to_aspect()`: pads reference images to match target aspect ratio

---

## File Locations

| Concern | File |
|---------|------|
| Archetypes, subtypes, body profiles, trait options, weights | `engine/fighter_config.py` |
| Roster planning + fighter generation orchestration | `engine/fighter_generator.py` |
| Character design guides + prompt builders | `prompts/fighter_prompts.py` |
| Outfit tier prompts | `prompts/outfit_prompts.py` |
| Image prompt assembly (charsheets, body_ref, portraits, moves) | `prompts/image_builders.py` |
| Art style constants | `engine/image_style.py` |
| Grok image gen/edit + charsheet pipeline | `services/grok_image.py` |
| Fighter data model | `models/fighter.py` |
| Outfit option data | `data/outfit_options.json`, `data/exotic_outfit_options.json` |

## Data Stored on Fighter

After generation, the Fighter object carries everything needed to regenerate images without re-running the LLM:

- `body_type_details`: full dict of rolled traits (breast_size, vulva_type, face_shape, etc.)
- `skimpiness_level`: 1-4
- `tech_level`: random era string
- `image_prompt_body_parts`, `image_prompt_expression`, `image_prompt_personality_pose`: from LLM
- `ring_attire`, `ring_attire_sfw`, `ring_attire_nsfw`: outfit text descriptions
- `image_prompt`, `image_prompt_sfw`, `image_prompt_nsfw`: assembled charsheet prompt dicts (each has `full_prompt`)
- `image_prompt_body_ref`: assembled body ref prompt dict
- `image_prompt_portrait`, `image_prompt_headshot`: assembled portrait/headshot prompt dicts
- `iconic_features`: persistent visual details across all tiers
- `primary_outfit_color`: outfit color from palette
- `outfit_suggestions`: per-tier outfit option samples (for regeneration)
