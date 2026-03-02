# Backend - Simple File Summaries

Quick reference for finding code.

## Config

- `app/config.py` - Config dataclass with API keys, league constants, stat bounds, recovery ranges; load_config() from .env

## Entry Point

- `app/run_day.py` - CLI: python -m app.run_day [--days N] [--init], advances league day-by-day

## Engine (`app/engine/`)

- `fight_simulator.py` - Fight pipeline: calculate_probabilities, determine_outcome, generate_moments, run_fight (orchestrator). Prompts imported from `prompts/fight_prompts.py`
- `fighter_generator.py` - Orchestration: plan_roster(), generate_fighter() (rolls subtype + body profile, builds body_ref + 3 tier image prompts), _generate_outfits(). Imports config from `fighter_config.py`, prompts from `prompts/`
- `fighter_config.py` - All config data: 11 female + 8 male archetypes, ARCHETYPE_SUBTYPES (5 subtypes per archetype with body_profile_bias), BODY_PROFILES (Petite/Slim/Athletic/Curvy), body trait options, outfit options, skimpiness levels, weight derivation tables, body trait utility functions
- `post_fight.py` - apply_fight_results: updates records, stats, injuries, storylines, rivalries. Prompt imported from `prompts/post_fight_prompts.py`
- `rankings.py` - calculate_rankings: sort by win%, total wins, recent form
- `matchmaker.py` - generate_fight_card: score pairings by rank proximity, rivalry, idle time
- `day_ticker.py` - advance_day: injury recovery, run events, schedule new events
- `image_style.py` - Arcane art style constants and gender-aware accessors (get_art_style, get_art_style_tail)
- `move_generator.py` - generate_moves (AI), generate_move_images (Grok). Prompts imported from `prompts/`

## Prompts (`app/prompts/`)

All LLM prompt text and image prompt assembly in one package. Each file has system prompt constants + builder functions with explicit parameters.

- `fighter_prompts.py` - Character design guide (GUIDE_CORE_PHILOSOPHY etc), _shuffled_archetype_names(), _shuffled_subtype_lines(), build_plan_roster_prompt() (with subtype requirements), build_generate_fighter_prompt()
- `outfit_prompts.py` - build_tier_prompt() for SFW/barely/NSFW outfit generation, OUTFIT_STYLE_RULES
- `fight_prompts.py` - build_probability_prompt(), build_moments_prompt() for fight simulation
- `move_prompts.py` - build_move_generation_prompt() for fighting move design
- `post_fight_prompts.py` - build_storyline_prompt() for post-fight narratives
- `image_builders.py` - _build_charsheet_prompt() (3-view charsheet), build_body_reference_prompt() (5-panel anatomy study: face, rear angled, chest, butt, intimate), build_move_image_prompt() (move action image), NSFW prefix/tail helpers, BODY_REF_STYLE/LAYOUT/QUALITY constants

## Models (`app/models/`)

- `fighter.py` - Fighter (with subtype, image_prompt_body_ref, moves), Stats, Record, Injury, Condition, Move dataclasses
- `match.py` - Match, FightMoment, MatchupAnalysis, MatchOutcome dataclasses
- `event.py` - Event, EventMatch dataclasses
- `world_state.py` - WorldState, RivalryRecord dataclasses

## Services (`app/services/`)

- `data_manager.py` - JSON file CRUD for fighters, matches, events, world_state
- `openrouter.py` - OpenRouter HTTP client (call_openrouter, call_openrouter_json) with retry and markdown fence stripping
- `grok_image.py` - Grok image API client: generate_image, edit_image, download_image, generate_charsheet_images (body_ref first as reference, then tier charsheets via edit_image)

## Scripts (`app/scripts/`)

- `generate_roster.py` - Two-phase: plan_roster_cmd (AI plan with subtypes) then generate_from_plan (create fighters + images); CLI: --plan, --generate, --images, --tiers, -n/--count
