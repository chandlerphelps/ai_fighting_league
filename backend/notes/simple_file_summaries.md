# Backend - Simple File Summaries

Quick reference for finding code. ~10% of detailed summaries.

**app/config.py** - Central config dataclass (.env, API keys, league constants, stat ranges, combat tuning)
- Config - all settings: models, roster counts, stat bounds, tier sizes, combat params

**app/api.py** - Flask REST API for roster management, world state, day simulation, 3-stage generation pipeline
- _rebuild_prompts(fighter) - reconstructs all image_prompt dicts + body_ref + headshot
- _generate_stage1_images() - generates body_ref, portrait, headshot in parallel
- Endpoints: CRUD fighters, generate/regenerate characters/outfits/images, advance stages, roster plan CRUD, serve images (charsheet/portrait/headshot), simulate day

**app/engine/combat/__init__.py** - Package exports for combat engine
**app/engine/combat/models.py** - Combat data models (FighterCombatState, EmotionalState, TickResult, RoundSummary, CombatResult)
**app/engine/combat/moves.py** - 28 universal moves catalog + get_available_moves() filtering
**app/engine/combat/damage.py** - Hit resolution, damage calc, cost application
**app/engine/combat/conditions.py** - Emotional state transitions, mana gen, combat modifiers
**app/engine/combat/resolution.py** - Per-tick combat resolution (initiative, attack lifecycle, maintenance)
**app/engine/combat/strategy.py** - WeightedStrategy: probabilistic move selection via multiplicative scoring
**app/engine/combat/simulator.py** - Round-based fight orchestrator (simulate_combat)
**app/engine/combat/win_conditions.py** - KO/TKO/submission checks

**app/engine/between_fights/__init__.py** - Package exports for between-fight systems
**app/engine/between_fights/training.py** - Daily training with tier rates, age/morale/work_ethic modifiers, fight camp boosts
**app/engine/between_fights/retirement.py** - Retirement checks, aging stat decay/growth, replacement fighter generation (gender-aware)
**app/engine/between_fights/league_tiers.py** - Tier rankings, promotion/relegation matchups, title fight tracking
**app/engine/between_fights/season.py** - Season calendar, fight scheduling, end-of-season processing, tier event config

**app/engine/fight_simulator.py** - Fight pipeline adapter: combat engine -> Match model with moments/injuries/combat log
**app/engine/fighter_generator.py** - AI fighter creation: subtypes, body traits, fit styles, transparency, outfits, image prompts, stats via generate_archetype_stats()
- plan_roster() - AI roster planning with gender_mix
- generate_fighter() - full pipeline with gender-aware tiers, fit_style/transparency (female only)

**app/engine/fighter_config.py** - All fighter generation config data (2957 lines)
- Archetypes: 11 female + 8 male with subtypes, body profile biases
- Body traits: BODY_TRAIT_OPTIONS (16 eye_expressions), MALE_BODY_TRAIT_OPTIONS (5 eye_expressions)
- Body profiles: 4 female, 7 male with trait constraints
- Archetype weights: body traits, body profiles, height ranges, stat weights (all gender-aware)
- FIT_STYLES (5 styles), TRANSPARENCY_OPTIONS, _roll_fit_style(), _roll_transparency()
- ADORNMENT_COVERAGE, outfit coverage validation, clothing coverage annotations
- generate_archetype_stats() - stat generation with archetype weights + gender bonuses
- Hair/color classification, weight derivation, body directive builders

**app/engine/post_fight.py** - Post-fight state updates (records, stats, injuries, storylines, rivalries)
**app/engine/rankings.py** - Fighter rankings by win%, wins, recent form
**app/engine/image_style.py** - Dark indie comic art style (Mignola inspired) + painterly style for body refs
- get_art_style(gender) / get_art_style_tail(gender)

**app/prompts/fighter_prompts.py** - Character design guides + fighter creation prompt builders (gender-aware)
**app/prompts/outfit_prompts.py** - Tier-based outfit prompts with fit_style, transparency, coverage classification
**app/prompts/fight_prompts.py** - Fight analysis and moment choreography prompts
**app/prompts/move_prompts.py** - Fighting move generation prompts
**app/prompts/post_fight_prompts.py** - Post-fight storyline prompts
**app/prompts/image_builders.py** - Image prompt assembly (charsheets, body refs, portraits, headshots, moves)
- Eye expression integration in face panels
- Outfit coverage annotations
- build_headshot_prompt() / build_portrait_prompt() / build_body_reference_prompt()

**app/models/fighter.py** - Fighter dataclass (Stats, Record, Injury, Condition, Move, fit_style, transparency)
**app/models/match.py** - Match model with combat-enriched moments
**app/models/event.py** - Event model (fight night with matches)
**app/models/world_state.py** - Global league state (date, rankings, seasons, belt, rivalries)

**app/services/data_manager.py** - JSON file CRUD for all entities in /data/
**app/services/openrouter.py** - OpenRouter API client with retry + JSON extraction
**app/services/grok_image.py** - Grok image gen/edit API client, charsheet pipeline (body_ref -> tier charsheets)

**app/scripts/generate_roster.py** - Two-phase roster generation (plan + generate from plan)
**app/scripts/simulate_seasons.py** - Standalone league simulation (LeagueSimulator class, N seasons)
**app/scripts/initialize_league.py** - Initialize league via N seasons of simulation history
**app/scripts/initialize_league_llm.py** - Initialize league with LLM-generated fighters, tier assignment, optional full image generation
- initialize_league_llm() - plan roster via AI, batch generate, tier-appropriate stats/age
- _advance_fighter_to_stage3() - full 3-stage image pipeline

**app/engine/day_simulator.py** - Single-day simulation for frontend (recovery, training, fights, calendar, rankings)
- simulate_one_day() - main entry point
**app/engine/pool_summarizer.py** - Fighter pool summary for AI roster planning (archetypes, regions, ages, visual identity)
