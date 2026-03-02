# Backend - Detailed File Summaries

Comprehensive documentation of backend code.

## TABLE OF CONTENTS

1. [app/config.py](#appconfig)
2. [app/run_day.py](#apprun_day)
3. [app/api.py](#appapi)
4. [app/engine/combat/__init__.py](#appenginecombat__init__)
5. [app/engine/combat/models.py](#appenginecombatmodels)
6. [app/engine/combat/moves.py](#appenginecombatmoves)
7. [app/engine/combat/damage.py](#appenginecombatdamage)
8. [app/engine/combat/conditions.py](#appenginecombatconditions)
9. [app/engine/combat/resolution.py](#appenginecombatresolution)
10. [app/engine/combat/strategy.py](#appenginecombatstrategy)
11. [app/engine/combat/simulator.py](#appenginecombatsimulator)
12. [app/engine/combat/win_conditions.py](#appenginecombatwin_conditions)
13. [app/engine/fight_simulator.py](#appenginefight_simulator)
14. [app/engine/fighter_generator.py](#appenginefighter_generator)
15. [app/engine/fighter_config.py](#appenginefighter_config)
16. [app/engine/post_fight.py](#appenginepost_fight)
17. [app/engine/rankings.py](#appenginerankings)
18. [app/engine/matchmaker.py](#appenginematchmaker)
19. [app/engine/day_ticker.py](#appengineday_ticker)
20. [app/engine/image_style.py](#appengineimage_style)
21. [app/prompts/fighter_prompts.py](#apppromptsfighter_prompts)
22. [app/prompts/outfit_prompts.py](#apppromptsoutfit_prompts)
23. [app/prompts/fight_prompts.py](#apppromptsfight_prompts)
24. [app/prompts/move_prompts.py](#apppromptsmove_prompts)
25. [app/prompts/post_fight_prompts.py](#apppromptspost_fight_prompts)
26. [app/prompts/image_builders.py](#apppromptsimage_builders)
27. [app/models/fighter.py](#appmodelsfighter)
28. [app/models/match.py](#appmodelsmatch)
29. [app/models/event.py](#appmodelsevent)
30. [app/models/world_state.py](#appmodelsworld_state)
31. [app/services/data_manager.py](#appservicesdata_manager)
32. [app/services/openrouter.py](#appservicesopenrouter)
33. [app/services/grok_image.py](#appservicesgrok_image)
34. [app/scripts/generate_roster.py](#appscriptsgenerate_roster)

---

## app/config.py
File: app/config.py
File Length: 55 lines
Purpose: Central configuration dataclass loaded from .env, holds API keys, league constants, stat ranges, recovery tuning, and combat engine parameters.

Artefacts
- Config - dataclass with openrouter_api_key, grok_api_key, model names (default_model, narrative_model), roster/event counts, stat bounds, recovery ranges, rematch_cooldown_days, max_idle_days, combat tuning (ticks_per_round, base_stamina_recovery_pct, stamina_recovery_decay, tko_base_threshold, tko_toughness_factor, tko_late_round_drop, tko_late_round_start, max_combat_rounds), data_dir

---

## app/run_day.py
File: app/run_day.py
File Length: 63 lines
Purpose: CLI entry point that advances the league by N days, optionally initializing the roster first.

Artefacts
- main() - argparse CLI (--days N, --init), loads config, calls advance_day in loop, prints summary/rankings/injuries

---

## app/api.py
File: app/api.py
File Length: 550 lines
Purpose: Flask REST API for roster management: CRUD fighters, generate/regenerate characters/outfits/images, manage outfit options, serve fighter images, poll async tasks.

Artefacts
- PROMPT_RELEVANT_FIELDS - set of fields that trigger prompt rebuild on update
- _get_subtype_info(fighter) - lookup subtype info from archetype/subtype fields
- _rebuild_prompts(fighter) - reconstructs all 3 tier image_prompt dicts from current fighter data
- _run_in_background(task_id, fn) - runs function in daemon thread, stores result in tasks dict
- _fighter_image_paths(fighter_id, ring_name) - returns dict of tier->Path for existing images
- _build_outfit_options_for_fighter(skimpiness_level) - loads and filters outfit options per tier

Endpoints
- GET /api/fighters - list all fighters with available image tiers
- GET /api/fighters/<id> - single fighter with available images
- PUT /api/fighters/<id> - update fighter fields, auto-rebuilds prompts if needed
- DELETE /api/fighters/<id> - delete fighter and all associated files
- POST /api/fighters/generate - async: generate new fighter from archetype/plan
- POST /api/fighters/<id>/regenerate-character - async: regenerate character preserving record/storyline
- POST /api/fighters/<id>/regenerate-outfits - async: regenerate outfits for specified tiers
- POST /api/fighters/<id>/regenerate-images - async: regenerate charsheet images for specified tiers
- POST /api/fighters/<id>/regenerate-move-image - async: regenerate single move image using charsheet as reference
- GET /api/tasks/<id> - poll async task status
- GET /api/archetypes - list female and male archetypes
- GET /api/fighter-images/<id>/<tier> - serve fighter charsheet image
- GET /api/outfit-options - get outfit options JSON
- PUT /api/outfit-options - save outfit options JSON

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
File Length: 193 lines
Purpose: Core combat data models: fighter state, emotional state, tick/round results, and final combat outcome.

Artefacts
- Position - enum: STANDING, CLINCH, GROUND
- TickOutcome - enum: HIT, BLOCKED, DODGED, COUNTER
- FinishMethod - enum: KO, TKO, SUBMISSION
- EmotionalState - dataclass (composure/confidence/rage/fear/focus), clamp(), to_dict(), from_stats(technique)
- FighterCombatState - dataclass with hp/stamina/mana/guard/position/stun_ticks/accumulated_damage/supernatural_debt/combo_counter/emotional_state + stats; snapshot() returns state dict, from_fighter_data(fighter_dict) factory derives max_hp/stamina/mana/guard from stats
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

## app/engine/fight_simulator.py
File: app/engine/fight_simulator.py
File Length: 268 lines
Purpose: Fight pipeline adapter: runs deterministic combat engine, converts results to Match model with moments, injuries, and combat log.

Artefacts
- _make_seed(fighter1_id, fighter2_id, match_date) - SHA-256 seed from IDs and date
- _assess_performance(fighter_id, combat_result) - dominant/competitive/poor based on rounds and tick count
- _derive_injuries(fighter_id, combat_result, config) - probabilistic injury generation from accumulated damage and winner/loser status
- _tick_to_moment(tick, moment_number, fighter names/IDs) - converts TickResult to FightMoment with full combat state (hp/stamina/mana/emotions)
- _filter_significant_moments(tick_log, max_moments=50) - selects most impactful ticks: finishers > big hits > counters > medium hits
- run_fight(fighter1_id, fighter2_id, event_id, match_date, config) - loads fighters, calls simulate_combat, converts tick log to moments, derives injuries, builds Match with combat_log and combat_seed
- _get_rivalry_context(fighter1_id, fighter2_id, config) - looks up rivalry record from world_state

---

## app/engine/fighter_generator.py
File: app/engine/fighter_generator.py
File Length: 379 lines
Purpose: Orchestration for AI fighter creation. Rolls subtypes, body profiles, generates outfits in parallel with tech level, builds body reference and charsheet image prompts.

Artefacts
- plan_roster(config, roster_size, existing_fighters) - builds existing roster text (including subtypes), calls build_plan_roster_prompt(), calls OpenRouter
- _generate_outfits(config, character_summary, skimpiness_level, tiers, outfit_options_by_tier, tech_level) - parallel tier outfit generation using build_tier_prompt() with tech_level
- generate_fighter(config, archetype, has_supernatural, existing_fighters, roster_plan_entry, ...) - full pipeline: rolls subtype via _find_subtype/_roll_subtype, rolls body traits with subtype bias, generates character JSON, picks random tech_level, generates outfits with tech_level, builds image_prompt_body_ref + 3 tier charsheet prompts, returns Fighter with tech_level field
- _extract_stats(data, has_supernatural, config) - clamps stat values to config bounds
- _normalize_core_stats(stats, config) - scales core stats to target range if out of bounds

---

## app/engine/fighter_config.py
File: app/engine/fighter_config.py
File Length: 1250 lines
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
File Length: 248 lines
Purpose: Applies fight results to persistent fighter state: records, stats, injuries, supernatural debt, storylines, and rivalries.

Artefacts
- apply_fight_results(match, config) - orchestrates all post-fight updates including supernatural debt, saves fighters and world_state
- _update_records(f1, f2, outcome) - increments wins/losses/draws/kos/submissions; handles ko, tko, and legacy ko_tko methods
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

## app/engine/matchmaker.py
File: app/engine/matchmaker.py
File Length: 123 lines
Purpose: Generates fight cards by scoring fighter pairings on rank proximity, rivalry, and idle time.

Artefacts
- generate_fight_card(world_state, fighters, matches, config) - filters available fighters, scores all pairs, greedily selects top non-overlapping pairs
- _score_pairing(fighter1, fighter2, rank_map, world_state, current_date) - scoring: rank proximity (+10/+5), rivalry (+15), idle time bonus (up to +20)
- _get_recent_pairings(matches, current_date, cooldown_days) - returns set of fighter-pair tuples within cooldown window

---

## app/engine/day_ticker.py
File: app/engine/day_ticker.py
File Length: 225 lines
Purpose: Advances the league one day: heals injuries, runs scheduled events, auto-schedules future events.

Artefacts
- advance_day(config) - increments date/day_number, processes injuries, runs events, ensures schedule, saves world_state
- _process_injury_recovery(ws, config) - decrements injury days, heals at 0, returns list of healed fighter names
- _run_todays_event(ws, config) - finds today's event, runs each fight via run_fight, applies results, recalculates rankings
- _ensure_upcoming_schedule(ws, config) - maintains 2 future events within 7-day horizon
- _create_event(ws, event_date, config) - calls generate_fight_card, creates Event with EventMatches, saves to disk

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
File Length: 442 lines
Purpose: Character design guide constants and fighter creation prompt builders. Includes archetype/subtype system integration.

Artefacts
- GUIDE_CORE_PHILOSOPHY / GUIDE_VISUAL_DESIGN / GUIDE_CREATION_WORKFLOW / GUIDE_COMMON_MISTAKES / FULL_CHARACTER_GUIDE - design philosophy text; GUIDE_CREATION_WORKFLOW lists all 11 female + 8 male archetypes with subtypes
- SYSTEM_PROMPT_ROSTER_PLANNER / SYSTEM_PROMPT_CHARACTER_DESIGNER - system prompts
- _shuffled_archetype_names() - returns comma-separated archetype names in random order (for prompt variety)
- _shuffled_subtype_lines() - returns formatted subtype list per archetype in random order
- build_plan_roster_prompt(roster_size, existing_roster_text) - roster planning prompt with shuffled archetypes/subtypes, requires subtype selection
- build_generate_fighter_prompt(archetype_text, existing_roster_text, blueprint_text, body_directive, supernatural_instruction, min_total_stats, max_total_stats, subtype_info) - fighter generation prompt with subtype identity directive

---

## app/prompts/outfit_prompts.py
File: app/prompts/outfit_prompts.py
File Length: 210 lines
Purpose: Tier-based outfit prompt builder for SFW/barely/NSFW tiers with archetype, subtype, personality, and tech level context.

Artefacts
- OUTFIT_STYLE_RULES - universal style rules applied to all tiers
- SYSTEM_PROMPT_OUTFIT_DESIGNER - system prompt
- build_tier_prompt(tier, skimpiness_level, character_summary, outfit_options, tech_level) - returns outfit generation prompt including archetype description (from ARCHETYPE_DESCRIPTIONS), subtype description (from ARCHETYPE_SUBTYPES), personality line, and technology era design constraint

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
File Length: 400 lines
Purpose: Image prompt assembly for charsheet images (Grok API), body reference sheets, and move action images. Not LLM prompts.

Artefacts
- CHARSHEET_LAYOUT - character reference sheet turnaround prompt template (3 views)
- _charsheet_style_base/style/tail(gender, tier, skimpiness_level) - charsheet art style with NSFW nudity prefixes when needed
- _build_charsheet_prompt(body_parts, clothing, expression, personality_pose, tier, gender, skimpiness_level, body_type_details, origin, subtype_info, iconic_features) - assembles full charsheet image prompt dict with subtype aesthetic and iconic features integration
- BODY_REF_STYLE_BASE / BODY_REF_STYLE_FEMALE / BODY_REF_STYLE_MALE - painterly anatomy study style strings
- BODY_REF_PAGE_STYLE - anatomy study page layout description (5 isolated body part drawings)
- BODY_REF_LAYOUT - template string with {torso_detail} and {intimate_label} format slots for gendered 5-panel layout
- BODY_REF_QUALITY - quality descriptors for body reference images
- build_body_reference_prompt(body_parts, expression, gender, body_type_details, origin, subtype_info) - assembles 5-panel body reference prompt with subtype aesthetic
- _nsfw_prefix/tail(gender, skimpiness_level) - NSFW prefix/tail for move images
- build_move_image_prompt(fighter, move, tier) - assembles move action image prompt string

---

## app/models/fighter.py
File: app/models/fighter.py
File Length: 165 lines
Purpose: Fighter data model with nested Stats, Record, Injury, Condition, and Move dataclasses.

Artefacts
- Stats - power, speed, technique, toughness, supernatural; core_total()
- Record - wins, losses, draws, kos, submissions; total_fights(), win_percentage()
- Injury - type, severity, recovery_days_remaining
- Condition - health_status, injuries list, recovery_days_remaining, morale, momentum
- Move - name, description, stat_affinity
- Fighter - full fighter profile: identity (id, ring_name, real_name, age, origin, gender, primary_archetype, subtype), physical (height, weight, build, distinguishing_features, iconic_features), attire (3 tiers), skimpiness_level, tech_level, image_prompt dicts (body_ref + 3 tiers), stats, record, condition, moves, storyline_log, body_type_details, rivalries

---

## app/models/match.py
File: app/models/match.py
File Length: 111 lines
Purpose: Match data model with combat state-enriched moments and round-by-round combat log.

Artefacts
- FightMoment - moment_number, description, attacker_id, defender_id, action, defender_action, result, damage_dealt, tick_number, round_number, attacker_hp/stamina/mana, defender_hp/stamina/mana, attacker_emotions, defender_emotions, image_prompt, image_path
- MatchupAnalysis - fighter1/2_win_prob, fighter1/2_methods, key_factors
- MatchOutcome - winner_id, loser_id, method, round_ended, fighter1/2_performance, fighter1/2_injuries, is_draw
- Match - full match record with fighter IDs/names, analysis, outcome, narrative, moments, snapshots, post_fight_updates, combat_log (round summaries), combat_seed (for reproducibility)

---

## app/models/event.py
File: app/models/event.py
File Length: 43 lines
Purpose: Event data model representing a fight night with its scheduled matches.

Artefacts
- EventMatch - match_id, fighter1/2 IDs and names, completed, winner_id, method
- Event - id, date, name, matches list, completed, summary; to_dict(), from_dict()

---

## app/models/world_state.py
File: app/models/world_state.py
File Length: 47 lines
Purpose: Global league state tracking date, rankings, events, injuries, and rivalries.

Artefacts
- RivalryRecord - fighter1/2_id, fights, wins, draws, is_rivalry
- WorldState - current_date, day_number, rankings, upcoming/completed events, active_injuries, rivalry_graph, event_counter

---

## app/services/data_manager.py
File: app/services/data_manager.py
File Length: 144 lines
Purpose: JSON file CRUD for all data entities (fighters, matches, events, world_state) in the /data/ directory.

Artefacts
- ensure_data_dirs(config) - creates fighters/matches/events subdirectories
- save_fighter(fighter, config) / load_fighter(fighter_id, config) / load_all_fighters(config) - fighter CRUD with slugified filenames
- save_match(match, config) / load_match(match_id, config) / load_all_matches(config) - match CRUD
- save_event(event, config) / load_event(event_id, config) / load_all_events(config) - event CRUD
- save_world_state(world_state, config) / load_world_state(config) - world_state CRUD

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
File Length: 250 lines
Purpose: Grok (x.ai) image generation and editing API client. Generates body reference image first, then uses it as reference input for tier charsheets via edit_image.

Artefacts
- MAX_RETRIES = 5
- TIER_PROMPT_KEYS - maps tier names ("sfw","barely","nsfw") to fighter prompt dict keys
- _encode_image(path) - base64-encode image file with MIME type detection
- generate_image(prompt, config, aspect_ratio, resolution, n) - calls Grok image generation API with retries, returns URL list
- edit_image(prompt, image_paths, config, ...) - calls Grok image edit API with base64-encoded reference images
- download_image(url, save_path) - downloads image URL to disk
- generate_charsheet_images(fighter, config, output_dir, tiers) - generates body_ref image at 1:1 first, then uses it as reference for each tier charsheet via edit_image in parallel (falls back to generate_image if no body_ref)

---

## app/scripts/generate_roster.py
File: app/scripts/generate_roster.py
File Length: 191 lines
Purpose: Two-phase roster generation script: plan roster via AI, then generate fighters from plan with optional image generation.

Artefacts
- plan_roster_cmd() - calls plan_roster (passes existing fighters including subtypes), saves roster_plan.json, prints summary
- generate_from_plan(generate_images, tiers, count) - reads roster_plan.json, generates each fighter via generate_fighter with skimpiness and outfit options, optionally generates charsheet images, initializes WorldState
- generate_roster(generate_images, tiers, count) - runs both phases sequentially
- CLI: --plan, --generate, --images, --tiers [sfw barely nsfw], -n/--count
