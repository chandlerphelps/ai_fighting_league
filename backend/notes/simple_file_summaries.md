# Backend - Simple File Summaries

Quick reference for finding code.

## Config

- `app/config.py` - Config dataclass with API keys, league constants, stat bounds, recovery ranges, combat engine params (ticks_per_round, tko thresholds, max_combat_rounds); load_config() from .env

## Entry Point

- `app/run_day.py` - CLI: python -m app.run_day [--days N] [--init], advances league day-by-day

## API

- `app/api.py` - Flask REST API: CRUD fighters, async generate/regenerate character/outfits/images, outfit options, serve images, poll tasks. Endpoints: /api/fighters, /api/fighters/<id>, /api/fighters/generate, /api/fighters/<id>/regenerate-{character,outfits,images,move-image}, /api/tasks/<id>, /api/archetypes, /api/fighter-images/<id>/<tier>, /api/outfit-options

## Combat Engine (`app/engine/combat/`)

Deterministic tick-by-tick fight simulation with game mechanics: HP, stamina, mana, guard, emotional state, 28 universal moves.

- `__init__.py` - Package exports: simulate_combat, CombatResult, FighterCombatState, MoveDefinition, UNIVERSAL_MOVES, FightStrategy, WeightedStrategy
- `models.py` - Position/TickOutcome/FinishMethod enums, EmotionalState, FighterCombatState (from_fighter_data factory), TickResult, RoundSummary, CombatResult
- `moves.py` - MoveDefinition dataclass, UNIVERSAL_MOVES (28 moves: strikes/kicks/clinch/ground/defensive/supernatural), get_available_moves()
- `damage.py` - calculate_hit_chance, calculate_block_chance, calculate_damage, resolve_attack (hit/block/dodge/counter/slip), apply_damage, apply_attacker_costs
- `conditions.py` - Emotional updates on hit/miss/block/counter, tick decay, mana generation, apply_emotional_modifiers (damage/accuracy/evasion/block/stamina mults)
- `resolution.py` - calculate_initiative, resolve_single_attack (full lifecycle), resolve_tick (initiative ordering, stun skip, end-of-tick maintenance)
- `strategy.py` - FightStrategy ABC, WeightedStrategy (probabilistic scoring: stamina/finishing/defensive/supernatural/stat_affinity/positional/combo/fatigue)
- `simulator.py` - simulate_combat (round/tick loop, between-round recovery, max-round TKO fallback), _make_seed, _between_rounds, _update_round_summary
- `win_conditions.py` - check_ko (hp<=0), check_tko (accumulated damage + low hp), check_submission (grappling + exhausted), check_win_condition

## Engine (`app/engine/`)

- `fight_simulator.py` - Fight pipeline adapter: run_fight calls simulate_combat, converts tick log to FightMoments (with hp/stamina/mana/emotions), derives injuries, builds Match with combat_log and combat_seed
- `fighter_generator.py` - Orchestration: plan_roster(), generate_fighter() (rolls subtype + body profile, picks tech_level, builds body_ref + 3 tier image prompts), _generate_outfits() with tech_level. Imports config from `fighter_config.py`, prompts from `prompts/`
- `fighter_config.py` - All config data: 11 female + 8 male archetypes, ARCHETYPE_DESCRIPTIONS, TECH_LEVELS, ARCHETYPE_SUBTYPES (5 subtypes per archetype with body_profile_bias), BODY_PROFILES (Petite/Slim/Athletic/Curvy), body trait options, outfit options, skimpiness levels, weight derivation tables, body trait utility functions
- `post_fight.py` - apply_fight_results: updates records, stats, injuries, supernatural debt (from mana usage), storylines, rivalries. Handles ko/tko/submission methods
- `rankings.py` - calculate_rankings: sort by win%, total wins, recent form
- `matchmaker.py` - generate_fight_card: score pairings by rank proximity, rivalry, idle time
- `day_ticker.py` - advance_day: injury recovery, run events, schedule new events
- `image_style.py` - Arcane art style constants and gender-aware accessors (get_art_style, get_art_style_tail)
- `move_generator.py` - generate_moves (AI), generate_move_images (Grok). Prompts imported from `prompts/`

## Prompts (`app/prompts/`)

All LLM prompt text and image prompt assembly in one package. Each file has system prompt constants + builder functions with explicit parameters.

- `fighter_prompts.py` - Character design guide (GUIDE_CORE_PHILOSOPHY etc), _shuffled_archetype_names(), _shuffled_subtype_lines(), build_plan_roster_prompt() (with subtype requirements), build_generate_fighter_prompt() (with subtype_info param)
- `outfit_prompts.py` - build_tier_prompt() for SFW/barely/NSFW outfit generation with archetype description, subtype description, personality, and tech_level context
- `fight_prompts.py` - build_probability_prompt(), build_moments_prompt() for fight simulation
- `move_prompts.py` - build_move_generation_prompt() for fighting move design
- `post_fight_prompts.py` - build_storyline_prompt() for post-fight narratives
- `image_builders.py` - _build_charsheet_prompt() (3-view charsheet with subtype_info and iconic_features), build_body_reference_prompt() (5-panel anatomy study with subtype aesthetic), build_move_image_prompt() (move action image), NSFW prefix/tail helpers, BODY_REF_STYLE/LAYOUT/QUALITY constants

## Models (`app/models/`)

- `fighter.py` - Fighter (with subtype, tech_level, image_prompt_body_ref, moves), Stats, Record, Injury, Condition, Move dataclasses
- `match.py` - Match (with combat_log, combat_seed), FightMoment (with defender_id, result, damage, hp/stamina/mana/emotions for both fighters), MatchupAnalysis, MatchOutcome
- `event.py` - Event, EventMatch dataclasses
- `world_state.py` - WorldState, RivalryRecord dataclasses

## Services (`app/services/`)

- `data_manager.py` - JSON file CRUD for fighters, matches, events, world_state
- `openrouter.py` - OpenRouter HTTP client (call_openrouter, call_openrouter_json) with retry and markdown fence stripping
- `grok_image.py` - Grok image API client: generate_image, edit_image, download_image, generate_charsheet_images (body_ref first as reference, then tier charsheets via edit_image in parallel); MAX_RETRIES=5

## Scripts (`app/scripts/`)

- `generate_roster.py` - Two-phase: plan_roster_cmd (AI plan with subtypes) then generate_from_plan (create fighters + images); CLI: --plan, --generate, --images, --tiers, -n/--count
