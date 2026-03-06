# Backend - Simple File Summaries

Quick reference for finding code. ~10% of detailed summaries.

**app/config.py** - Central configuration dataclass (.env, API keys, tier sizes, combat tuning)
- Config - all settings: models, stat bounds, recovery ranges, tier sizes, combat params

**app/api.py** - Flask REST API for roster management, day simulation, world state
- CRUD fighters, generate/regenerate characters/outfits/images
- Roster plan CRUD with AI planning, multi-stage generation pipeline
- GET/POST /api/fighters, /api/roster-plan, /api/simulate-day, /api/world-state

**app/engine/combat/__init__.py** - Package exports for combat engine
**app/engine/combat/models.py** - Combat data models (FighterCombatState, TickResult, RoundSummary, CombatResult)
**app/engine/combat/moves.py** - 28 universal moves catalog + get_available_moves()
**app/engine/combat/damage.py** - Hit resolution, damage calc, cost application
**app/engine/combat/conditions.py** - Emotional state transitions, mana generation, combat modifiers
**app/engine/combat/resolution.py** - Per-tick resolution: initiative, attack lifecycle, maintenance
**app/engine/combat/strategy.py** - WeightedStrategy: probabilistic move selection with 8 scoring factors
**app/engine/combat/simulator.py** - simulate_combat(): round/tick loop orchestrator
**app/engine/combat/win_conditions.py** - KO/TKO/submission checks

**app/engine/between_fights/__init__.py** - Package exports for between-fight systems
**app/engine/between_fights/training.py** - Daily training with tier rates, age/morale modifiers, fight camp boosts
- process_daily_training() / apply_fight_camp_boost()

**app/engine/between_fights/retirement.py** - Retirement, aging, gender-aware replacement fighter generation
- GENDER_STAT_BIAS / GENDER_SECONDARY_RANGES - per-gender stat adjustments
- check_retirement() - 5 retirement conditions
- apply_aging() / generate_replacement_fighter(gender_override) / _distribute_stats(bias)

**app/engine/between_fights/league_tiers.py** - Tier rankings, promotion/relegation matchups, title fight tracking
- calculate_tier_rankings() / get_promotion_matchups() / apply_promotion_results() / apply_title_fight_result()

**app/engine/between_fights/season.py** - Season calendar, fight scheduling, end-of-season processing
- TIER_SIZES / set_tier_sizes() - configurable roster sizes
- process_end_of_season() - aging, retirement, backfill (by season_tier_wins), stat reset

**app/engine/fight_simulator.py** - Fight pipeline adapter: combat engine -> Match model with moments/injuries
- run_fight() / _derive_injuries() / _filter_significant_moments()

**app/engine/fighter_generator.py** - AI fighter creation: subtypes, body profiles, outfits, image prompts
- plan_roster() / generate_fighter() / generate_fighter_json_only()

**app/engine/fighter_config.py** - Fighter generation config: archetypes, subtypes, body profiles, outfit options
- ARCHETYPES_FEMALE (11) / ARCHETYPES_MALE (8) / BODY_PROFILES (4) / SKIMPINESS_LEVELS (4)

**app/engine/post_fight.py** - Post-fight state updates: records, stats, injuries, storylines, rivalries
- apply_fight_results() / _update_records() / _apply_injuries() / _update_rivalry()

**app/engine/rankings.py** - calculate_rankings() by win%, total wins, recent form
**app/engine/image_style.py** - Arcane art style constants, gender-aware accessors

**app/prompts/fighter_prompts.py** - Character design guides + fighter/roster prompt builders
**app/prompts/outfit_prompts.py** - Tier-based outfit prompt builder with tech level/exotic support
**app/prompts/fight_prompts.py** - Fight analysis and moment choreography prompts
**app/prompts/move_prompts.py** - Fighting move generation prompt
**app/prompts/post_fight_prompts.py** - Post-fight storyline prompt
**app/prompts/image_builders.py** - Image prompt assembly for charsheets, body refs, portraits, moves

**app/models/fighter.py** - Fighter dataclass: Stats, Record, Injury, Condition, Move, generation pipeline
**app/models/match.py** - Match dataclass: FightMoment, MatchupAnalysis, MatchOutcome
**app/models/event.py** - Event dataclass: EventMatch, fight night structure
**app/models/world_state.py** - WorldState dataclass: rankings, seasons, belt history, scheduled fights

**app/services/data_manager.py** - JSON file CRUD for fighters/matches/events/world_state/roster_plan
**app/services/openrouter.py** - OpenRouter API client with retry and JSON extraction
**app/services/grok_image.py** - Grok image gen/edit API: body ref -> charsheet pipeline

**app/scripts/generate_roster.py** - Two-phase roster generation: AI plan -> fighter generation
**app/scripts/simulate_seasons.py** - Multi-season league simulation with gender-aware stats
- LeagueSimulator - generates roster, simulates seasons with fights/injuries/promotions/retirement
- Tracks season_tier_wins for backfill promotion sorting
- CLI: --seasons, --seed, --verbose, --apex/--contender/--underground tier sizes

**app/scripts/initialize_league.py** - Initialize league: simulate N seasons, save to disk

**app/engine/day_simulator.py** - Single-day simulation for frontend-driven progression
- simulate_one_day() - recovery, training, fights, calendar, rankings, next matchups
- _schedule_next_day() / _compute_next_matchups() - pre-schedule fights and predict matchups
- _advance_calendar() - season transitions with promotions/title fight
- Tracks season_tier_wins per fight for backfill sorting

**app/engine/pool_summarizer.py** - Fighter pool summary for AI roster planning
- summarize_fighter_pool() - archetype/region/age distribution, visual identity registry
