# Backend - Detailed File Summaries

Comprehensive documentation of backend code.

## TABLE OF CONTENTS

1. [app/config.py](#appconfig)
2. [app/api.py](#appapi)
4. [app/engine/combat/__init__.py](#appenginecombat__init__)
5. [app/engine/combat/models.py](#appenginecombatmodels)
6. [app/engine/combat/moves.py](#appenginecombatmoves)
7. [app/engine/combat/damage.py](#appenginecombatdamage)
8. [app/engine/combat/conditions.py](#appenginecombatconditions)
9. [app/engine/combat/resolution.py](#appenginecombatresolution)
10. [app/engine/combat/strategy.py](#appenginecombatstrategy)
11. [app/engine/combat/simulator.py](#appenginecombatsimulator)
12. [app/engine/combat/win_conditions.py](#appenginecombatwin_conditions)
13. [app/engine/between_fights/__init__.py](#appenginebetween_fights__init__)
14. [app/engine/between_fights/training.py](#appenginebetween_fightstraining)
15. [app/engine/between_fights/retirement.py](#appenginebetween_fightsretirement)
16. [app/engine/between_fights/league_tiers.py](#appenginebetween_fightsleague_tiers)
17. [app/engine/between_fights/season.py](#appenginebetween_fightsseason)
18. [app/engine/fight_simulator.py](#appenginefight_simulator)
19. [app/engine/fighter_generator.py](#appenginefighter_generator)
20. [app/engine/fighter_config.py](#appenginefighter_config)
21. [app/engine/post_fight.py](#appenginepost_fight)
22. [app/engine/rankings.py](#appenginerankings)
23. [app/engine/image_style.py](#appengineimage_style)
26. [app/prompts/fighter_prompts.py](#apppromptsfighter_prompts)
27. [app/prompts/outfit_prompts.py](#apppromptsoutfit_prompts)
28. [app/prompts/fight_prompts.py](#apppromptsfight_prompts)
29. [app/prompts/move_prompts.py](#apppromptsmove_prompts)
30. [app/prompts/post_fight_prompts.py](#apppromptspost_fight_prompts)
31. [app/prompts/image_builders.py](#apppromptsimage_builders)
32. [app/models/fighter.py](#appmodelsfighter)
33. [app/models/match.py](#appmodelsmatch)
34. [app/models/event.py](#appmodelsevent)
35. [app/models/world_state.py](#appmodelsworld_state)
36. [app/services/data_manager.py](#appservicesdata_manager)
37. [app/services/openrouter.py](#appservicesopenrouter)
38. [app/services/grok_image.py](#appservicesgrok_image)
39. [app/scripts/generate_roster.py](#appscriptsgenerate_roster)
40. [app/scripts/simulate_seasons.py](#appscriptssimulate_seasons)
41. [app/scripts/initialize_league.py](#appscriptsinitialize_league)
42. [app/engine/day_simulator.py](#appengineday_simulator)
43. [app/engine/pool_summarizer.py](#appenginepool_summarizer)

---

## app/config.py
File: app/config.py
File Length: 60 lines
Purpose: Central configuration dataclass loaded from .env, holds API keys, league constants, tier sizes, stat ranges, recovery tuning, and combat engine parameters.

Artefacts
- Config - dataclass with openrouter_api_key, grok_api_key, model names (default_model, narrative_model), roster/event counts, stat bounds, recovery ranges, rematch_cooldown_days, max_idle_days, tier sizes (apex_size=16, contender_size=20, underground_size=100), season_length_months=8, combat tuning (ticks_per_round, base_stamina_recovery_pct, stamina_recovery_decay, tko params, max_combat_rounds), data_dir

---

## app/api.py
File: app/api.py
File Length: 1221 lines
Purpose: Flask REST API for roster management, world state access, day simulation, and 3-stage roster initialization pipeline. CRUD fighters, generate/regenerate characters/outfits/images, manage outfit options, roster plan CRUD with AI planning, multi-stage generation (JSON->portrait->charsheets), serve fighter images, poll async tasks.

Artefacts
- PROMPT_RELEVANT_FIELDS - set of fields that trigger prompt rebuild on update
- FIELD_DEPENDENCIES - maps fighter fields to downstream invalidation targets (outfits, image_prompts, images)
- _get_subtype_info(fighter) - lookup subtype info from archetype/subtype fields
- _rebuild_prompts(fighter) - reconstructs all 3 tier image_prompt dicts + body_ref from current fighter data; gender-aware (male nsfw = barely)
- _run_in_background(task_id, fn) - runs function in daemon thread, stores result in tasks dict
- _fighter_image_paths(fighter_id, ring_name) - returns dict of tier->Path for existing images (sfw, barely, nsfw, portrait)
- _build_outfit_options_for_fighter(skimpiness_level, archetype, subtype) - loads and filters outfit options per tier with exotic support

Endpoints
- GET /api/fighters - list all fighters with available image tiers
- GET /api/fighters/<id> - single fighter with available images
- PUT /api/fighters/<id> - update fighter fields, auto-rebuilds prompts if needed, tracks generation_dirty invalidation
- DELETE /api/fighters/<id> - delete fighter and all associated files
- POST /api/fighters/generate - async: generate new fighter from archetype/plan
- POST /api/fighters/<id>/regenerate-character - async: regenerate character preserving record/storyline
- POST /api/fighters/<id>/regenerate-outfits - async: regenerate outfits for specified tiers
- POST /api/fighters/<id>/regenerate-images - async: regenerate charsheet images for specified tiers
- POST /api/fighters/<id>/regenerate-move-image - async: regenerate single move image using charsheet as reference
- POST /api/fighters/<id>/advance-stage - async: advance fighter through generation stages (1->2: portrait, 2->3: full charsheets)
- POST /api/fighters/batch-advance - async: advance multiple fighters to a target stage (2 or 3)
- GET /api/tasks/<id> - poll async task status
- GET /api/archetypes - list female and male archetypes
- GET /api/fighter-images/<id>/<tier> - serve fighter charsheet image
- GET /api/fighter-images/<id>/portrait - serve fighter portrait image
- GET /api/outfit-options - get outfit options JSON
- PUT /api/outfit-options - save outfit options JSON
- GET /api/roster-plan - get current roster plan (auto-migrates legacy list format)
- POST /api/roster-plan - async: create new roster plan via AI with pool summary and gender_mix
- DELETE /api/roster-plan - delete pending entries from roster plan
- PUT /api/roster-plan/entries/<index> - update single plan entry
- DELETE /api/roster-plan/entries/<index> - remove single plan entry
- POST /api/roster-plan/entries/<index>/regenerate - async: reroll single plan entry via AI
- POST /api/roster-plan/entries/add - async: add more entries to existing plan via AI
- POST /api/roster-plan/generate - async: generate fighters from approved plan entries (stage 1 only)
- GET /api/pool-summary - get current fighter pool summary with stats
- GET /api/world-state - returns full world_state JSON
- POST /api/simulate-day - loads active fighters and world_state, calls simulate_one_day, saves all fighters and world_state, returns day_result

---

## app/engine/combat/__init__.py
File: app/engine/combat/__init__.py
File Length: 4 lines
Purpose: Package exports for deterministic combat engine.

Artefacts
- Exports: simulate_combat, CombatResult, FighterCombatState, TickResult, RoundSummary, MoveDefinition, UNIVERSAL_MOVES, get_available_moves, FightStrategy, WeightedStrategy

---

## app/engine/combat/models.py
File: app/engine/combat/models.py
File Length: 213 lines
Purpose: Core combat data models: fighter state, emotional state, tick/round results, and final combat outcome.

Artefacts
- Position - enum: STANDING, CLINCH, GROUND
- TickOutcome - enum: HIT, BLOCKED, DODGED, COUNTER
- FinishMethod - enum: KO, TKO, SUBMISSION
- EmotionalState - dataclass (composure/confidence/rage/fear/focus), clamp(), to_dict(), from_stats(technique)
- FighterCombatState - dataclass with hp/stamina/mana/guard/position/stun_ticks/accumulated_damage/supernatural_debt/combo_counter/emotional_state + stats; snapshot() returns state dict, from_fighter_data(fighter_dict) factory derives max_hp/stamina/mana/guard from stats, reads condition.momentum/morale to adjust starting emotional state (rising momentum boosts confidence/composure, falling adds fear; high morale boosts focus, low reduces it)
- TickResult - dataclass: global_tick, round_number, tick_in_round, attacker/defender IDs, move_used, defender_move, result, damage_dealt, state snapshots, finish
- RoundSummary - dataclass: per-round stats (damage dealt, hits landed/attempted, blocks, dodges, hp/stamina/mana end values per fighter)
- CombatResult - dataclass: winner/loser IDs, method, final_round, final_tick, tick_log, round_summaries, final states, seed

---

## app/engine/combat/moves.py
File: app/engine/combat/moves.py
File Length: 271 lines
Purpose: Universal move catalog (28 moves) and move availability filtering.

Artefacts
- MoveDefinition - dataclass: id, name, category, base_damage, stamina_cost, mana_cost, speed, accuracy, block_modifier, stun_chance, stun_duration, position_required, position_change, stat_scaling, stamina_damage, is_submission, is_finisher, is_signature
- UNIVERSAL_MOVES - dict of 28 moves: strikes (jab, cross, hook, uppercut, overhand, backfist, body_shot), kicks (front_kick, leg_kick, roundhouse, spinning_back_kick, knee), clinch (clinch_entry, clinch_elbow, clinch_knee, throw, clinch_break), ground (ground_and_pound, armbar_attempt, choke_attempt, sweep, ground_elbow), defensive (block, slip, recover), supernatural (spirit_blast, hex_drain, phantom_rush, dark_shield)
- get_available_moves(fighter_state, fighter_signature_moves) - filters moves by position, stamina, mana, stun status; falls back to block if none available

---

## app/engine/combat/damage.py
File: app/engine/combat/damage.py
File Length: 183 lines
Purpose: Hit resolution, damage calculation, and cost application for combat ticks.

Artefacts
- calculate_hit_chance(move, attacker, defender) - base accuracy * technique/stamina/combo/emotion modifiers minus evasion (speed/stamina/emotion, halved when stunned)
- calculate_block_chance(move, defender) - technique * block_modifier * guard_factor * emotion modifier
- calculate_damage(move, attacker, defender) - base_damage * stat scaling * stamina factor * emotion * combo bonus, reduced by toughness + guard
- calculate_block_damage(full_damage) - 30% of full damage
- resolve_attack(move, attacker, defender, defender_move, rng) - rolls hit/block/dodge/counter with slip and counter mechanics
- apply_damage(defender, damage, move, outcome, rng) - applies hp/guard/stamina damage and stun chance
- apply_attacker_costs(attacker, move, outcome) - deducts stamina/mana costs, adds supernatural_debt

---

## app/engine/combat/conditions.py
File: app/engine/combat/conditions.py
File Length: 162 lines
Purpose: Emotional state transitions, mana generation, and combat modifier calculations.

Artefacts
- composure_dampening(state) - returns 0.3-1.0 dampening factor based on composure
- update_emotions_on_hit(attacker, defender, damage) - attacker gains confidence/focus, defender gains rage, fear if low HP
- update_emotions_on_miss(attacker) - attacker loses confidence/focus
- update_emotions_on_block(attacker, defender) - defender gains confidence/focus
- update_emotions_on_counter(attacker, defender) - attacker loses confidence, gains fear; defender gains confidence/focus
- update_emotions_tick_decay(state) - per-tick regression of rage/fear/confidence/focus toward baselines
- update_mana(state) - mana gain from low HP, high rage/fear, scaled by supernatural stat
- apply_emotional_modifiers(state) - returns damage_mult/accuracy_mult/evasion_mult/block_mult/stamina_drain_mult from emotional state
- update_emotions_between_rounds(state) - larger inter-round decay/regression

---

## app/engine/combat/resolution.py
File: app/engine/combat/resolution.py
File Length: 167 lines
Purpose: Per-tick combat resolution: initiative ordering, attack lifecycle, and end-of-tick maintenance.

Artefacts
- calculate_initiative(move, fighter) - speed/stamina-weighted move speed (lower = faster)
- resolve_single_attack(attacker, defender, att_move, def_move, round_number, rng) - full attack lifecycle: resolve_attack, apply costs, apply damage, update emotions, check win conditions
- resolve_tick(fighter1, fighter2, f1_move, f2_move, ..., rng) - orders by initiative, resolves first attacker, skips second if stunned, runs end-of-tick maintenance
- _end_of_tick_maintenance(f1, f2) - stamina regen (+2), guard regen (+3), stun decrement, emotion tick decay, mana update

---

## app/engine/combat/strategy.py
File: app/engine/combat/strategy.py
File Length: 216 lines
Purpose: Pluggable move selection strategies for combat AI. Default is weighted probabilistic scoring.

Artefacts
- FightStrategy - ABC with select_move(own_state, opponent_state, available_moves, round_num, tick_num, rng)
- WeightedStrategy - probabilistic selection via multiplicative scoring:
  - _stamina_score - favors recover when low, penalizes expensive moves
  - _finishing_score - boosts finishers/big damage when opponent low HP or stunned
  - _defensive_score - boosts block/slip when own HP low, opponent on combo, or high fear
  - _supernatural_score - boosts supernatural when self or opponent low HP
  - _stat_affinity_score - matches moves to fighter's stat strengths (power->damage, speed->fast, technique->submissions)
  - _positional_score - context-aware clinch/ground transitions
  - _combo_score - boosts high-damage/finisher moves during combos
  - _fatigue_score - penalizes expensive moves in late rounds

---

## app/engine/combat/simulator.py
File: app/engine/combat/simulator.py
File Length: 172 lines
Purpose: Round-based fight orchestrator. Runs tick-by-tick combat until KO/TKO/submission or max rounds.

Artefacts
- TICKS_PER_ROUND=30, BASE_STAMINA_RECOVERY_PCT=0.30, STAMINA_RECOVERY_DECAY_PER_ROUND=0.03, MAX_ROUNDS=30
- _make_seed(fighter1_id, fighter2_id, date) - SHA-256 hash for deterministic seeding
- simulate_combat(fighter1_data, fighter2_data, seed, strategy1, strategy2, signature_moves) - creates FighterCombatState from dicts, runs round/tick loop with strategy move selection and resolve_tick, between-round recovery, returns CombatResult
- _between_rounds(f1, f2, round_just_finished) - stamina recovery (decays per round), guard reset, position reset to standing, emotion reset
- _update_round_summary(summary, tick_results, f1_id, f2_id) - accumulates per-round stats from tick results

---

## app/engine/combat/win_conditions.py
File: app/engine/combat/win_conditions.py
File Length: 56 lines
Purpose: Win condition checks: KO, TKO, and submission.

Artefacts
- check_ko(state) - hp <= 0
- check_tko(state, round_number) - accumulated_damage > threshold (60 + toughness*0.5, drops after round 10) and hp < 20%
- check_submission(move, attacker, defender) - is_submission move + defender hp<30% + stamina<20%
- check_win_condition(attacker, defender, move, outcome, round_number) - orchestrates all three checks

---

## app/engine/between_fights/__init__.py
File: app/engine/between_fights/__init__.py
File Length: 4 lines
Purpose: Package exports for between-fight systems: training, retirement, league tiers, and season processing.

Artefacts
- Exports: process_daily_training, apply_fight_camp_boost, check_retirement, apply_aging, update_promotion_desperation, generate_replacement_fighter, calculate_tier_rankings, get_promotion_matchups, apply_promotion_results, apply_title_fight_result, process_end_of_season, get_tier_event_config

---

## app/engine/between_fights/training.py
File: app/engine/between_fights/training.py
File Length: 104 lines
Purpose: Daily training system with tier-based progression rates, age/morale/work_ethic/learning_rate modifiers, overtraining injury risk, and fight camp stat boosts.

Artefacts
- TRAINING_RATES - tier->rate dict (apex 0.035, contender 0.028, underground 0.023)
- FIGHT_CAMP_BOOSTS - tier->boost dict (apex 4, contender 3, underground 2)
- MORALE_TRAINING_MULTIPLIERS - morale->multiplier (high 1.3, neutral 1.0, low 0.6)
- process_daily_training(fighter, rng) - accumulates training progress at tier rate modified by age (0.7x at 32+, 0.4x at 36+), learning_rate, morale, and work_ethic bonus; low work_ethic has skip chance; increments focus stat when accumulated >= 1.0; overtraining streak 5% injury chance above 90 days
- apply_fight_camp_boost(fighter) - returns copy of fighter stats with training_focus stat boosted by tier amount (capped at 95)

---

## app/engine/between_fights/retirement.py
File: app/engine/between_fights/retirement.py
File Length: 214 lines
Purpose: Fighter retirement logic, aging with stat decay/growth, promotion desperation tracking, and replacement fighter generation.

Artefacts
- RING_NAMES - 160+ ring name options for generated fighters
- PREFIXES - 19 name prefixes (The, Kid, Big, etc.)
- check_retirement(fighter, rng) - returns (should_retire, reason): age_and_losing_record (34+ with losing season), underground_stagnation (30+ stuck 4+ seasons, escalating chance), morale_collapse (5+ consecutive losses, age 25+), severe_injury_retirement (32+ with severe injury, 30% chance), graceful_exit (belt holder 33+, 20% chance)
- apply_aging(fighter, rng) - increments age, applies stat changes: under 26 gains 1-2 in 2-3 stats, 26-31 stable, 32-35 loses speed/toughness (-2) and maybe power (-1), 36+ loses all stats (-2 to -3)
- update_promotion_desperation(fighter) - increases desperation +0.15/season for underground fighters 28+, maxes at 1.0 for 30+ who never left underground
- generate_replacement_fighter(fighter_id_counter, season, rng, used_names) - creates new underground fighter aged 18-22 with 120-240 total stats, includes consecutive_wins, learning_rate (0.7-1.4), work_ethic (0.6-1.3), tier_records
- _distribute_stats(target_total, rng) - allocates stat points across 4 core stats within 25-60 range, scales to target

---

## app/engine/between_fights/league_tiers.py
File: app/engine/between_fights/league_tiers.py
File Length: 155 lines
Purpose: Tier ranking calculation, promotion/relegation matchup generation with protection for injured fighters, promotion result application, and apex title fight tracking.

Artefacts
- TIER_ORDER - dict mapping tier names to numeric order (underground=0, contender=1, apex=2)
- TIER_NAMES - ordered list of tier name strings
- calculate_tier_rankings(fighters, tier, season_matches) - ranks active fighters in a tier by (has_fought, season_wins, win_pct, recent_wins from last 5, core_total)
- get_promotion_matchups(tier_rankings, champ_contender_slots=4, contender_underground_slots=6, protected_fighter_ids=None) - pairs bottom N of upper tier vs top N of lower tier at each boundary, excludes protected fighters from relegation eligibility
- apply_promotion_results(fighters, promotion_results) - swaps tiers for winners who beat upper-tier fighters, resets seasons_in_current_tier, updates peak_tier
- apply_title_fight_result(ws, winner_id, loser_id, season) - tracks belt_holder_id and belt_history (defenses count, won/lost dates)

---

## app/engine/between_fights/season.py
File: app/engine/between_fights/season.py
File Length: 257 lines
Purpose: Season calendar system, date math, fight scheduling intervals, end-of-season processing, and tier event configuration.

Artefacts
- SEASON_START_MONTH=11, SEASON_MONTHS=[11,12,1-6], REGULAR_MONTHS=[11,12,1-5], PROMOTION_MONTH=6
- EVENT_INTERVAL - days between tier events (apex=10, contender=6, underground=1)
- TIER_START_TIMES - start time per tier (underground 14:00, contender 18:00, apex 21:00)
- get_fight_start_time(tier, fight_index) - returns staggered start time for nth fight (30min apart)
- is_fight_day(current, season_number, tier) - checks if date is a fight day based on EVENT_INTERVAL
- set_base_year(year) / season_start_year(season_number) / season_start_date / season_end_date - calendar date helpers
- is_promotion_month(month) / is_regular_month(month) / days_remaining_in_season(current, season_number) - season phase checks
- TIER_EVENT_CONFIG - events/month and fights/event (apex 6/mo 2-3, contender 10/mo 2-3, underground 30/mo 4-6)
- TIER_SIZES - target roster sizes (apex 16, contender 20, underground 100); set_tier_sizes() to override
- process_end_of_season(fighters, ws, fighter_counter, rng, used_names) - full pipeline: aging, retirement, desperation, backfill, reset stats/injuries, set current_date to next season start

---

## app/engine/fight_simulator.py
File: app/engine/fight_simulator.py
File Length: 292 lines
Purpose: Fight pipeline adapter: runs deterministic combat engine, converts results to Match model with moments, injuries (including career-ending and season-ending), and combat log.

Artefacts
- _make_seed(fighter1_id, fighter2_id, match_date) - SHA-256 seed from IDs and date
- _assess_performance(fighter_id, combat_result) - dominant/competitive/poor based on rounds and tick count
- _derive_injuries(fighter_id, combat_result, config) - probabilistic injury generation from accumulated damage and winner/loser status; losers face additional career-ending (0.5% * ko_multiplier, severity "career_ending", 999 recovery days) and season-ending (2% * ko_multiplier, severity "season_ending", 90-120 recovery days) injury chances
- _tick_to_moment(tick, moment_number, fighter names/IDs) - converts TickResult to FightMoment with full combat state (hp/stamina/mana/emotions)
- _filter_significant_moments(tick_log, max_moments=50) - selects most impactful ticks: finishers > big hits > counters > medium hits
- run_fight(fighter1_id, fighter2_id, event_id, match_date, config) - loads fighters, calls simulate_combat, converts tick log to moments, derives injuries, builds Match with combat_log and combat_seed
- _get_rivalry_context(fighter1_id, fighter2_id, config) - looks up rivalry record from world_state

---

## app/engine/fighter_generator.py
File: app/engine/fighter_generator.py
File Length: 472 lines
Purpose: Orchestration for AI fighter creation. Rolls subtypes, body profiles, generates outfits in parallel with tech level, builds body reference and charsheet image prompts. Supports gender-aware generation (male fighters get sfw/barely tiers only, nsfw=barely).

Artefacts
- plan_roster(config, roster_size, existing_fighters, pool_summary, gender_mix) - builds existing roster text from pool_summary or fighter list, calls build_plan_roster_prompt() with gender_mix, calls OpenRouter (minimax model)
- _generate_outfits(config, character_summary, skimpiness_level, tiers, outfit_options_by_tier, tech_level) - parallel tier outfit generation using build_tier_prompt() with tech_level; collects outfit_suggestions per tier
- generate_fighter_json_only(config, archetype, ...) - generates fighter with skip_image_prompts=True, sets generation_stage=1, copies signature visual identity fields from roster_plan_entry (primary_outfit_color, hair_style, hair_color, face_adornment)
- generate_fighter(config, archetype, has_supernatural, existing_fighters, roster_plan_entry, ..., skip_image_prompts) - full pipeline: rolls subtype, body traits, character JSON, tech_level, outfits, image prompts; generates learning_rate (0.7-1.4) and work_ethic (0.6-1.3); gender-aware (male: sfw/barely tiers only, nsfw=barely), returns Fighter
- _extract_stats(data, has_supernatural, config) - clamps stat values to config bounds
- _normalize_core_stats(stats, config) - scales core stats to target range if out of bounds

---

## app/engine/fighter_config.py
File: app/engine/fighter_config.py
File Length: 1285 lines
Purpose: All configuration data for fighter generation: archetypes with subtypes and body profile biases, body profiles constraining trait ranges, outfit options, skimpiness levels, weight derivation tables, tech levels, archetype descriptions, and body trait utility functions.

Artefacts
- load_outfit_options(config) / filter_outfit_options(options_for_tier, skimpiness_level) - outfit option loading and filtering
- ARCHETYPES_FEMALE - 11 archetypes (Siren, Witch, Viper, Prodigy, Doll, Huntress, Empress, Experiment, Demon, Assassin, Nymph)
- ARCHETYPES_MALE - 8 archetypes (Brute, Veteran, Monster, Technician, Wildcard, Mystic, Prodigy, Experiment)
- ARCHETYPE_DESCRIPTIONS - per-archetype one-line description dict
- TECH_LEVELS - predefined list of technology eras for outfit generation
- BODY_TRAIT_OPTIONS - category->options dict (waist, abs_tone, body_fat_pct, butt_size, breast_size, nipple_size, vulva_type, face_shape, eye_shape, makeup_level)
- BODY_PROFILES - 4 profiles (Petite, Slim, Athletic, Curvy) each constraining allowed trait ranges
- ARCHETYPE_BODY_PROFILE_WEIGHTS - per-archetype probability weights across the 4 body profiles
- ARCHETYPE_SUBTYPES - per-archetype list of 5 subtypes, each with name, description, body_profile_bias adjustments
- _roll_subtype(archetype) / _find_subtype(archetype, name) - random or lookup subtype selection
- ARCHETYPE_BODY_WEIGHTS - per-archetype weighted probability tables for individual body traits
- ARCHETYPE_HEIGHT_RANGES / MAKEUP_DESCRIPTIONS - height ranges and makeup descriptions per archetype
- BODY_FAT_MULTIPLIERS / BREAST_WEIGHT_LBS / BUTT_WEIGHT_LBS / WAIST_MULTIPLIERS - weight derivation tables
- _weighted_choice(category, archetype, allowed) - roll a body trait with archetype weights, optionally constrained by allowed list
- _format_height(inches) / _derive_weight(height_inches, traits) - height formatting and weight calculation
- _roll_body_profile(archetype, subtype_bias) - weighted body profile selection with optional subtype adjustments
- _roll_body_traits(archetype, subtype) - rolls body profile then all traits within profile constraints, adds subtype name
- _build_body_directive(traits) / _build_body_shape_line(traits) / _build_nsfw_anatomy_line(traits) - format traits for LLM/image prompts
- SKIMPINESS_LEVELS - 4-level dict of tier-specific outfit rules
- _roll_skimpiness(weights) - weighted random choice of skimpiness level 1-4

---

## app/engine/post_fight.py
File: app/engine/post_fight.py
File Length: 281 lines
Purpose: Applies fight results to persistent fighter state: records, stats, injuries, supernatural debt, storylines, rivalries, and tier records.

Artefacts
- apply_fight_results(match, config) - orchestrates all post-fight updates including supernatural debt, saves fighters and world_state
- _increment_tier_record(fighter, tier, result) - tracks per-tier win/loss/draw counts in fighter.tier_records
- _update_records(f1, f2, outcome) - increments wins/losses/draws/kos/submissions, tracks consecutive_wins/consecutive_losses, sets morale/momentum (high after 2+ wins, low after 2+ losses), records tier_records per fight
- _apply_stat_adjustments(fighter, outcome, is_fighter1) - stat +/- based on win/loss and performance; handles ko, tko, and legacy ko_tko
- _adjust_stat(stats, stat_name, delta, changes) - clamps stat between 15-95
- _apply_injuries(fighter, injuries) - creates Injury objects, sets health_status/morale
- _apply_supernatural_debt(fighter, combat_log, config) - reads round summaries for mana usage, adds extra recovery days, optionally degrades supernatural stat if debt > 30
- _generate_storyline_entry(fighter, opponent, outcome, match, config) - calls OpenRouter for 2-3 sentence narrative entry
- _update_rivalry(fighter1_id, fighter2_id, outcome, config) - creates or updates rivalry_graph entry, marks is_rivalry after 2+ fights

---

## app/engine/rankings.py
File: app/engine/rankings.py
File Length: 55 lines
Purpose: Calculates fighter rankings by win%, total wins, recent form (last 5 matches).

Artefacts
- calculate_rankings(fighters, recent_matches) - returns ordered list of fighter IDs sorted by (has_fought, win_pct, total_wins, recent_wins, last_fight)

---

## app/engine/image_style.py
File: app/engine/image_style.py
File Length: 44 lines
Purpose: Art style constants and gender-aware accessors for Arcane-inspired image generation prompts.

Artefacts
- ART_STYLE_BASE, ART_STYLE_FEMALE, ART_STYLE_MALE - base and gendered full art style strings
- ART_STYLE_TAIL_BASE, ART_STYLE_TAIL_FEMALE, ART_STYLE_TAIL_MALE - shorter tail variants
- get_art_style(gender) - returns gender-appropriate full art style
- get_art_style_tail(gender) - returns gender-appropriate tail art style

---

## app/prompts/fighter_prompts.py
File: app/prompts/fighter_prompts.py
File Length: 585 lines
Purpose: Character design guide constants and fighter creation prompt builders. Includes archetype/subtype system integration and gender-aware guides (separate male philosophy).

Artefacts
- GUIDE_CORE_PHILOSOPHY / GUIDE_VISUAL_DESIGN / GUIDE_CREATION_WORKFLOW / GUIDE_COMMON_MISTAKES / FULL_CHARACTER_GUIDE - design philosophy text; GUIDE_CREATION_WORKFLOW lists all 11 female + 8 male archetypes with subtypes
- GUIDE_MALE_PHILOSOPHY / FULL_MALE_CHARACTER_GUIDE - male-specific design philosophy emphasizing danger, intimidation, and physicality
- SYSTEM_PROMPT_ROSTER_PLANNER / SYSTEM_PROMPT_CHARACTER_DESIGNER - system prompts
- _shuffled_archetype_names(gender) - returns comma-separated archetype names in random order, gender-aware source selection
- _shuffled_subtype_lines(gender) - returns formatted subtype list per archetype in random order, gender-aware
- build_plan_roster_prompt(roster_size, existing_roster_text, gender_mix) - roster planning prompt with gender_mix support ("female", "male", "mixed"); includes signature visual identity fields (primary_outfit_color, hair_style, hair_color, face_adornment), skimpiness_weights, and subtype selection
- build_generate_fighter_prompt(archetype_text, existing_roster_text, blueprint_text, body_directive, supernatural_instruction, min_total_stats, max_total_stats, subtype_info, gender) - fighter generation prompt with gender-aware guide/stat hints/body trait hints, subtype identity directive, iconic features requirement

---

## app/prompts/outfit_prompts.py
File: app/prompts/outfit_prompts.py
File Length: 230 lines
Purpose: Tier-based outfit prompt builder for SFW/barely/NSFW tiers with archetype, subtype, personality, tech level context, and exotic outfit support.

Artefacts
- OUTFIT_STYLE_RULES - universal style rules applied to all tiers
- SYSTEM_PROMPT_OUTFIT_DESIGNER - system prompt
- build_tier_prompt(tier, skimpiness_level, character_summary, outfit_options, tech_level) - returns outfit generation prompt including archetype description (from ARCHETYPE_DESCRIPTIONS), subtype description (from ARCHETYPE_SUBTYPES), personality line, technology era design constraint, and exotic_one_pieces outfit options support for both NSFW and non-NSFW tiers

---

## app/prompts/fight_prompts.py
File: app/prompts/fight_prompts.py
Purpose: Fight analysis and moment choreography prompt builders.

Artefacts
- SYSTEM_PROMPT_FIGHT_ANALYST / SYSTEM_PROMPT_FIGHT_CHOREOGRAPHER - system prompts
- build_probability_prompt(f1_name, f1_stats, ..., rivalry_text) - returns matchup analysis prompt
- build_moments_prompt(target, f1_name, f1_id, ..., winner_name, loser_name) - returns fight moments prompt

---

## app/prompts/move_prompts.py
File: app/prompts/move_prompts.py
Purpose: Fighting move generation prompt builder.

Artefacts
- SYSTEM_PROMPT_MOVE_DESIGNER - system prompt
- build_move_generation_prompt(ring_name, build, personality, distinguishing, iconic, gender, stat_lines) - returns move design prompt

---

## app/prompts/post_fight_prompts.py
File: app/prompts/post_fight_prompts.py
Purpose: Post-fight storyline prompt builder.

Artefacts
- SYSTEM_PROMPT_STORYLINE - system prompt
- build_storyline_prompt(fighter_name, result_text, opponent_name, method, round_ended, wins, losses, draws) - returns storyline entry prompt

---

## app/prompts/image_builders.py
File: app/prompts/image_builders.py
File Length: 552 lines
Purpose: Image prompt assembly for charsheet images (Grok API), body reference sheets, portraits, and move action images. Not LLM prompts. Gender-aware with separate male body ref layout (3-panel vs 5-panel).

Artefacts
- CHARSHEET_LAYOUT - character reference sheet turnaround prompt template (3 views)
- _charsheet_style_base/style/tail(gender, tier, skimpiness_level) - charsheet art style with NSFW nudity prefixes when needed
- _enrich_body_parts(body_parts, body_type_details, subtype_info) - enriches body_parts with body shape line and subtype aesthetic
- _build_clothing_part(clothing, iconic_features, primary_outfit_color, tier, skimpiness_level) - builds clothing description with iconic features and primary color for SFW tier
- _build_character_desc(body_parts, clothing_part, age, origin) - builds character description string
- _build_charsheet_prompt(body_parts, clothing, expression, personality_pose, tier, gender, skimpiness_level, body_type_details, origin, subtype_info, iconic_features, age, primary_outfit_color) - assembles full charsheet image prompt dict with subtype aesthetic, iconic features, age, and primary color integration
- BODY_REF_STYLE_BASE / BODY_REF_STYLE_FEMALE / BODY_REF_STYLE_MALE - painterly anatomy study style strings
- BODY_REF_PAGE_STYLE / MALE_BODY_REF_PAGE_STYLE - anatomy study page layouts (5-panel female, 3-panel male)
- BODY_REF_LAYOUT / MALE_BODY_REF_LAYOUT - layout templates (female: face/rear-angled/chest/butt/intimate; male: face/front-body/back-body)
- BODY_REF_QUALITY / MALE_BODY_REF_QUALITY - quality descriptors
- build_body_reference_prompt(body_parts, expression, gender, body_type_details, origin, subtype_info, age) - assembles gender-aware body reference prompt (5-panel female, 3-panel male in underwear)
- _nsfw_prefix/tail(gender, skimpiness_level) - NSFW prefix/tail for move images
- build_move_image_prompt(fighter, move, tier) - assembles move action image prompt string
- PORTRAIT_STYLE - upper body portrait style constants
- build_portrait_prompt(body_parts, clothing_sfw, expression, gender, body_type_details, origin, subtype_info, iconic_features, primary_outfit_color, age) - assembles portrait image prompt dict for stage 2 generation

---

## app/models/fighter.py
File: app/models/fighter.py
File Length: 216 lines
Purpose: Fighter data model with nested Stats, Record, Injury, Condition, and Move dataclasses. Includes league season tracking fields and 3-stage generation pipeline fields.

Artefacts
- Stats - power, speed, technique, toughness, supernatural; core_total()
- Record - wins, losses, draws, kos, submissions; total_fights(), win_percentage()
- Injury - type, severity, recovery_days_remaining
- Condition - health_status, injuries list, recovery_days_remaining, morale, momentum
- Move - name, description, stat_affinity
- Fighter - full fighter profile: identity, physical, attire (3 tiers), image_prompt dicts (sfw, barely, nsfw, body_ref, portrait), stats, record, condition, moves, storyline_log, rivalries, signature visual identity (primary_outfit_color, hair_style, hair_color, face_adornment), generation pipeline (generation_stage 0-3, generation_dirty list), league fields (tier, status, training_focus, training_days_accumulated, training_streak, seasons_in_current_tier, career_season_count, peak_tier, promotion_desperation, season_wins, season_losses, consecutive_losses, consecutive_wins, learning_rate, work_ethic, tier_records)

---

## app/models/match.py
File: app/models/match.py
File Length: 113 lines
Purpose: Match data model with combat state-enriched moments and round-by-round combat log.

Artefacts
- FightMoment - moment_number, description, attacker/defender IDs, action, result, damage_dealt, tick/round numbers, hp/stamina/mana, emotions, image_prompt/path
- MatchupAnalysis - fighter1/2_win_prob, fighter1/2_methods, key_factors
- MatchOutcome - winner_id, loser_id, method, round_ended, fighter1/2_performance, fighter1/2_injuries, is_draw
- Match - full match record with fighter IDs/names, start_time, analysis, outcome, narrative, moments, snapshots, post_fight_updates, combat_log, combat_seed

---

## app/models/event.py
File: app/models/event.py
File Length: 45 lines
Purpose: Event data model representing a fight night with its scheduled matches and tier assignment.

Artefacts
- EventMatch - match_id, fighter1/2 IDs and names, completed, winner_id, method
- Event - id, date, name, matches list, completed, summary, tier; to_dict(), from_dict()

---

## app/models/world_state.py
File: app/models/world_state.py
File Length: 90 lines
Purpose: Global league state tracking date, rankings, events, injuries, rivalries, seasons, tiers, belt history, promotion/title fights, and scheduled fights.

Artefacts
- RivalryRecord - fighter1/2_id, fights, wins, draws, is_rivalry
- WorldState - current_date, day_number, rankings, upcoming/completed events, active_injuries, rivalry_graph, event_counter, season_number, season_month, season_day_in_month, tier_rankings (apex/contender/underground lists), belt_holder_id, belt_history, retired_fighter_ids, promotion_fights, title_fight, season_champions, scheduled_fights; from_dict auto-derives current_date from season_number if missing, derives season_month/season_day_in_month from parsed date

---

## app/services/data_manager.py
File: app/services/data_manager.py
File Length: 173 lines
Purpose: JSON file CRUD for all data entities (fighters, matches, events, world_state, roster_plan) in the /data/ directory.

Artefacts
- _slugify(name) - lowercase alphanumeric slug
- _get_data_dir(config) - resolves data directory from config or defaults to project root /data/
- ensure_data_dirs(config) - creates fighters/matches/events subdirectories
- _save_json(path, data) / _load_json(path) - generic JSON serialization with dataclass support
- _fighter_filename(fighter_id, ring_name) / _find_fighter_path(fighters_dir, fighter_id) - fighter file naming and lookup
- save_fighter(fighter, config) / load_fighter(fighter_id, config) / load_all_fighters(config) - fighter CRUD with slugified filenames, handles rename by cleaning old file
- save_match(match, config) / load_match(match_id, config) / load_all_matches(config) - match CRUD
- save_event(event, config) / load_event(event_id, config) / load_all_events(config) - event CRUD
- save_world_state(world_state, config) / load_world_state(config) - world_state CRUD
- save_roster_plan(plan, config) / load_roster_plan(config) / delete_roster_plan(config) - roster plan CRUD
- delete_fighter(fighter_id, config) - deletes fighter JSON and associated PNG images

---

## app/services/openrouter.py
File: app/services/openrouter.py
File Length: 96 lines
Purpose: HTTP client for OpenRouter API with retry logic and JSON extraction from markdown-fenced responses.

Artefacts
- call_openrouter(prompt, config, model, system_prompt, temperature, max_tokens) - sends chat completion request with 3 retries, returns text
- call_openrouter_json(prompt, config, ...) - wraps call_openrouter with JSON parsing and retry on parse failure
- _strip_markdown_fences(text) - extracts JSON from markdown code blocks or raw text

---

## app/services/grok_image.py
File: app/services/grok_image.py
File Length: 256 lines
Purpose: Grok (x.ai) image generation and editing API client. Generates body reference image first, then uses it as reference input for tier charsheets via edit_image. Gender-aware tier defaults (male: sfw/barely only).

Artefacts
- MAX_RETRIES = 5
- TIER_PROMPT_KEYS - maps tier names ("sfw","barely","nsfw") to fighter prompt dict keys
- _slugify(name) - lowercase alphanumeric slug for filenames
- _encode_image(path) - base64-encode image file with MIME type detection
- generate_image(prompt, config, aspect_ratio, resolution, n) - calls Grok image generation API with retries, returns URL list
- edit_image(prompt, image_paths, config, ...) - calls Grok image edit API with base64-encoded reference images
- download_image(url, save_path) - downloads image URL to disk
- generate_charsheet_images(fighter, config, output_dir, tiers) - generates body_ref image at 1:1 first (or reuses existing), then uses it as reference for each tier charsheet via edit_image in parallel (falls back to generate_image if no body_ref); default tiers gender-aware (male: sfw/barely)

---

## app/scripts/generate_roster.py
File: app/scripts/generate_roster.py
File Length: 227 lines
Purpose: Two-phase roster generation script: plan roster via AI, then generate fighters from plan with optional image generation. Saves roster plan as structured JSON.

Artefacts
- plan_roster_cmd() - calls plan_roster (passes existing fighters including subtypes/build/personality), saves roster_plan.json as structured dict with plan_id/created_at/mode/entries including signature visual identity defaults
- generate_from_plan(generate_images, tiers, count) - reads roster_plan.json (handles both dict and list formats), generates each fighter via generate_fighter with skimpiness, exotic outfit options, and archetype/subtype filtering; initializes or updates WorldState
- generate_roster(generate_images, tiers, count) - runs both phases sequentially
- CLI: --plan, --generate, --images, --tiers [sfw barely nsfw], -n/--count

---

## app/scripts/simulate_seasons.py
File: app/scripts/simulate_seasons.py
File Length: 925 lines
Purpose: Standalone league season simulation script. Generates a full roster across 3 tiers, simulates N seasons with month-based events, promotion/relegation, title fights, injuries (including career-ending and season-ending), training, aging, and retirement. Outputs comprehensive career arc statistics.

Artefacts
- EVENT_DAYS - tier->weekday list (apex days 3/6, contender days 2/4/7, underground daily)
- INJURY_TYPES_WINNER/LOSER_KO/LOSER_OTHER - injury type pools by outcome
- MINOR/MODERATE/SEVERE_RECOVERY - recovery day ranges by severity
- SEASON_ENDING_INJURY_TYPES - pool of 4 season-ending injury types
- CAREER_ENDING_INJURY_TYPES - pool of 3 career-ending injury types
- SEASON_ENDING_RECOVERY - (90, 120) day recovery range
- LeagueSimulator - main simulation class:
  - __init__(seed, verbose, total_seasons, tier_sizes) - initializes RNG, empty roster, world_state, season_logs, season_matches, total_fights_run counter, used_names set; accepts optional tier_sizes dict
  - generate_initial_roster() - creates fighters per tier_sizes (default 16/20/100) with tier-appropriate age/stat/record ranges, assigns initial belt holder
  - _make_fighter(counter, tier, age_range, stat_range, career_seasons_range, tier_seasons_range) - creates fighter dict with consecutive_wins, learning_rate, work_ethic, tier_records
  - _distribute_stats(target_total) - allocates stat points across 4 core stats
  - simulate_season() - runs 8-month season: months 1-6 regular, month 7 regular + promotion prep, month 8 promotion/title fights, then process_end_of_season; builds season_logs and season_matches
  - _simulate_regular_month(month) - 7 days of recovery/training + tier events on scheduled days
  - _process_daily_recovery() - decrements injury recovery days, clears healed fighters
  - _process_daily_training_all() - runs process_daily_training for all active fighters
  - _run_tier_event(tier) - schedules and runs fights for a tier based on tier event config
  - _run_single_fight(f1_id, f2_id) - runs combat via simulate_combat with fight camp boosts, updates records/injuries/morale
  - _apply_injury(fighter, is_winner, method) - probabilistic injury assignment (10% winner, 40% loser, +15% KO/TKO); age-scaled career/season-ending chances
  - _prepare_promotion_month() - calculates tier rankings, protects belt holder and injured fighters, generates promotion matchups and title fight
  - _simulate_promotion_month() - runs promotion fights, applies tier swaps, runs title fight
  - _recalculate_all_rankings() - recalculates tier rankings for all tiers from season matches
  - print_final_summary(num_seasons) - outputs career arc stats, tier mobility, belt history, notable careers
- main() - CLI entry (--seasons N, --seed, --verbose)

---

## app/scripts/initialize_league.py
File: app/scripts/initialize_league.py
File Length: 154 lines
Purpose: Initializes the league by running N seasons of simulation history, then saves active fighters and world_state to disk for the frontend viewer.

Artefacts
- initialize_league(seasons, seed, verbose, tier_sizes) - backs up existing fighter JSONs, clears matches/events, runs LeagueSimulator for N seasons, saves active fighters, builds world_state with recent_matches/season_logs/tier_rankings/belt_history/season_champions
- main() - CLI entry (--seasons, --seed, --verbose, --apex, --contender, --underground tier size overrides)

---

## app/engine/day_simulator.py
File: app/engine/day_simulator.py
File Length: 599 lines
Purpose: Single-day simulation engine for frontend-driven day-by-day league progression. Orchestrates daily recovery, training, fight scheduling/execution, calendar advancement, rankings recalculation, and season transitions.

Artefacts
- _current_date(ws) - parses current_date from world_state or derives from season_number
- _sync_date_fields(ws, d) - writes date, month, day to world_state
- simulate_one_day(fighters, ws) - main entry point: processes recovery/training, runs scheduled or auto-matched fights during regular months, handles promotion month, advances calendar (triggers season-end when past end date), recalculates rankings, schedules next day's fights, returns day_result dict
- _process_daily_recovery(fighters, day_result) - decrements recovery days, clears healed fighters
- _process_daily_training(fighters, rng) - runs process_daily_training for all active healthy fighters
- _schedule_next_day(fighters, ws) - pre-schedules next day's fights per tier using is_fight_day intervals, pairs available healthy fighters
- _run_tier_event(fighters, ws, tier, rng) - runs tier event: pairs and fights available fighters per tier config
- _run_single_fight(fighters, ws, f1_id, f2_id, rng, start_time) - applies fight camp boosts, runs simulate_combat, updates records/injuries/morale, returns match result dict
- _apply_injury(fighter, ws, rng, is_winner, method) - probabilistic injury (10% winner, 40%+15% KO loser), age-scaled career-ending and season-ending injury chances for losers
- _advance_calendar(fighters, ws, rng, day_result) - advances to tomorrow; triggers season-end (promotions, title fight, process_end_of_season, season_logs) when past end date; triggers promotion prep when entering promotion month
- _prepare_promotions(fighters, ws) - recalculates tier rankings, protects belt holder and injured fighters with winning records, generates promotion matchups and title fight
- _run_promotions(fighters, ws, rng, day_result) - runs promotion fights, applies tier swaps
- _run_title_fight(fighters, ws, rng, day_result) - runs title fight with eligibility fallbacks, updates belt_holder/belt_history/season_champions
- _recalculate_rankings(fighters, ws) - recalculates tier rankings from season matches, builds flat rankings list
- _build_summary(day_result) - returns one-line text summary of the day

---

## app/engine/pool_summarizer.py
File: app/engine/pool_summarizer.py
File Length: 126 lines
Purpose: Generates a text summary of the existing fighter pool for AI roster planning prompts. Analyzes archetype distribution, geographic spread, age brackets, and signature visual identity registry to prevent duplicates.

Artefacts
- REGION_MAP - dict mapping 13 geographic regions to lists of country keywords
- _classify_region(origin) - classifies a fighter's origin string into a region via keyword matching
- _age_bracket(age) - returns age bracket string (18-22, 23-27, 28-32, 33+)
- summarize_fighter_pool(fighters, for_display) - generates comprehensive pool summary text: total count, gender counts, archetype distribution (with missing archetypes highlighted), geographic spread (with underrepresented regions), age distribution, signature visual identity registry (outfit colors, hair style+color combos, face adornments); when for_display=True also lists individual fighters with archetype/subtype/origin and signature details
