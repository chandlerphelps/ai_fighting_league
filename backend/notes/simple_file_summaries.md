# Backend - Simple File Summaries

Quick reference for finding code. See detailed_file_summaries.md for full documentation.

**app/config.py** - Config dataclass with API keys, tier sizes (16/20/100), season length, combat tuning, data_dir
- Config, load_config()

**app/api.py** - Flask REST API for roster management, fighter CRUD, image generation
- GET/PUT/DELETE /api/fighters, POST generate/regenerate-character/outfits/images
- GET /api/tasks/<id>, GET /api/archetypes, GET/PUT /api/outfit-options

**app/engine/combat/__init__.py** - Package exports for deterministic combat engine
**app/engine/combat/models.py** - Position, TickOutcome, FinishMethod enums; EmotionalState, FighterCombatState, TickResult, RoundSummary, CombatResult dataclasses
**app/engine/combat/moves.py** - MoveDefinition, UNIVERSAL_MOVES (28 moves), get_available_moves()
**app/engine/combat/damage.py** - calculate_hit_chance(), calculate_damage(), resolve_attack(), apply_damage()
**app/engine/combat/conditions.py** - Emotional state updates (hit/miss/block/counter), mana generation, apply_emotional_modifiers()
**app/engine/combat/resolution.py** - calculate_initiative(), resolve_single_attack(), resolve_tick()
**app/engine/combat/strategy.py** - FightStrategy ABC, WeightedStrategy with scoring (stamina/finishing/defensive/supernatural/affinity/positional/combo/fatigue)
**app/engine/combat/simulator.py** - simulate_combat(), _between_rounds(), round/tick loop orchestrator
**app/engine/combat/win_conditions.py** - check_ko(), check_tko(), check_submission(), check_win_condition()

**app/engine/between_fights/__init__.py** - Package exports for training, retirement, league tiers, season processing
**app/engine/between_fights/training.py** - Daily training with tier-based rates, age modifiers, overtraining risk
- process_daily_training(), apply_fight_camp_boost()
**app/engine/between_fights/retirement.py** - Retirement checks, aging stat decay/growth, replacement fighter generation
- check_retirement(), apply_aging(), update_promotion_desperation(), generate_replacement_fighter()
**app/engine/between_fights/league_tiers.py** - Tier rankings, promotion/relegation matchups, title fight tracking
- calculate_tier_rankings(), get_promotion_matchups(), apply_promotion_results(), apply_title_fight_result()
**app/engine/between_fights/season.py** - End-of-season processing, tier event config, backfill promotions
- TIER_EVENT_CONFIG, TIER_SIZES, process_end_of_season(), get_tier_event_config()

**app/engine/fight_simulator.py** - Fight pipeline: combat engine -> Match model with moments/injuries
- run_fight(), _derive_injuries(), _filter_significant_moments()
**app/engine/fighter_generator.py** - AI fighter creation: subtypes, body profiles, outfits, image prompts
- plan_roster(), generate_fighter(), _generate_outfits()
**app/engine/fighter_config.py** - Archetypes (11F/8M) with subtypes, body profiles, outfit options, skimpiness levels, weight tables, tech levels
- ARCHETYPES_FEMALE/MALE, ARCHETYPE_SUBTYPES, BODY_PROFILES, SKIMPINESS_LEVELS
**app/engine/post_fight.py** - Post-fight state updates: records, stats, injuries, storylines, rivalries
- apply_fight_results(), _apply_supernatural_debt(), _update_rivalry()
**app/engine/rankings.py** - calculate_rankings() by win%, wins, recent form
**app/engine/image_style.py** - Arcane art style constants, get_art_style()/get_art_style_tail()

**app/prompts/fighter_prompts.py** - Character design guide, roster planning and fighter generation prompts
- build_plan_roster_prompt(), build_generate_fighter_prompt()
**app/prompts/outfit_prompts.py** - Tier outfit prompt builder with archetype/subtype/tech level/exotic support
- build_tier_prompt()
**app/prompts/fight_prompts.py** - build_probability_prompt(), build_moments_prompt()
**app/prompts/move_prompts.py** - build_move_generation_prompt()
**app/prompts/post_fight_prompts.py** - build_storyline_prompt()
**app/prompts/image_builders.py** - Charsheet, body ref, and move image prompt assembly (not LLM prompts)
- _build_charsheet_prompt(), build_body_reference_prompt(), build_move_image_prompt()

**app/models/fighter.py** - Fighter dataclass with Stats, Record, Injury, Condition, Move + league fields (tier, status, training, season tracking)
**app/models/match.py** - Match dataclass with FightMoment, MatchupAnalysis, MatchOutcome, combat_log
**app/models/event.py** - Event dataclass with EventMatch list and tier field
**app/models/world_state.py** - WorldState with season/tier tracking, belt history, promotion/title fights

**app/services/data_manager.py** - JSON file CRUD for fighters, matches, events, world_state
**app/services/openrouter.py** - OpenRouter API client with retry and JSON extraction
**app/services/grok_image.py** - Grok image gen/edit client, generate_charsheet_images()

**app/scripts/generate_roster.py** - Two-phase roster generation: plan via AI then generate fighters
**app/scripts/simulate_seasons.py** - LeagueSimulator: 136-fighter roster, N-season sim with training/injuries/promotion/title fights/retirement stats
