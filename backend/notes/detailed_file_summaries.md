# Backend - Detailed File Summaries

Comprehensive documentation of backend code.

## TABLE OF CONTENTS

1. [app/config.py](#appconfig)
2. [app/run_day.py](#apprun_day)
3. [app/engine/fight_simulator.py](#appenginefight_simulator)
4. [app/engine/fighter_generator.py](#appenginefighter_generator)
5. [app/engine/post_fight.py](#appenginepost_fight)
6. [app/engine/rankings.py](#appenginerankings)
7. [app/engine/matchmaker.py](#appenginematchmaker)
8. [app/engine/day_ticker.py](#appengineday_ticker)
9. [app/engine/image_style.py](#appengineimage_style)
10. [app/models/fighter.py](#appmodelsfighter)
11. [app/models/match.py](#appmodelsmatch)
12. [app/models/event.py](#appmodelsevent)
13. [app/models/world_state.py](#appmodelsworld_state)
14. [app/services/data_manager.py](#appservicesdata_manager)
15. [app/services/openrouter.py](#appservicesopenrouter)
16. [app/services/grok_image.py](#appservicesgrok_image)
17. [app/scripts/generate_roster.py](#appscriptsgenerate_roster)

---

## app/config.py
File: app/config.py
File Length: 46 lines
Purpose: Central configuration dataclass loaded from .env, holds API keys, league constants, stat ranges, and recovery tuning.

Artefacts
- Config - dataclass with openrouter_api_key, grok_api_key, model names (default_model, narrative_model), roster/event counts, stat bounds, recovery ranges, rematch_cooldown_days, max_idle_days, data_dir

---

## app/run_day.py
File: app/run_day.py
File Length: 63 lines
Purpose: CLI entry point that advances the league by N days, optionally initializing the roster first.

Artefacts
- main() - argparse CLI (--days N, --init), loads config, calls advance_day in loop, prints summary/rankings/injuries

---

## app/engine/fight_simulator.py
File: app/engine/fight_simulator.py
File Length: 260 lines
Purpose: Core fight pipeline: AI probability analysis, random outcome determination, AI moment generation, and full fight orchestration.

Artefacts
- _calc_moment_count(winner_prob) - maps lopsidedness to 3-6 moments
- _assess_performance(winner_prob) - returns ("dominant","poor") or ("competitive","competitive")
- determine_outcome(fighter1, fighter2, analysis, config) - rolls winner via analysis.fighter1_win_prob, assigns method ko_tko, injuries, performance labels
- _roll_injuries(config, base_chance) - probabilistic injury generation (minor/moderate/severe with recovery ranges)
- calculate_probabilities(fighter1, fighter2, config, rivalry_context) - calls OpenRouter for win probability JSON with key_factors
- generate_moments(fighter1, fighter2, analysis, outcome, config) - calls OpenRouter for choreographed strike-by-strike moments building to KO
- run_fight(fighter1_id, fighter2_id, event_id, match_date, config) - loads fighters, runs full pipeline (probabilities -> outcome -> moments), returns Match
- _get_rivalry_context(fighter1_id, fighter2_id, config) - looks up rivalry record from world_state

---

## app/engine/fighter_generator.py
File: app/engine/fighter_generator.py
File Length: 812 lines
Purpose: AI-driven fighter creation with extensive character design guide, archetype system, tiered image prompt generation, and stat validation.

Artefacts
- ARCHETYPES_FEMALE - 8 female archetypes (Siren, Witch, Viper, Prodigy, Doll, Huntress, Empress, Experiment)
- ARCHETYPES_MALE - 8 male archetypes (Brute, Veteran, Monster, Technician, Wildcard, Mystic, Prodigy, Experiment)
- GUIDE_CORE_PHILOSOPHY - design principles: attractiveness, gender power dynamics, violence-driven character depth, popular media archetypes
- GUIDE_VISUAL_DESIGN - strip test, silhouette rule, sex appeal guidelines, distinguishing features
- GUIDE_CREATION_WORKFLOW - archetype blending, identity/origin, physical design, concept hook
- GUIDE_COMMON_MISTAKES - 12 anti-patterns to avoid in character design
- GUIDE_IMAGE_PROMPT_RULES - NSFW tier image prompt formatting rules
- FULL_CHARACTER_GUIDE - concatenation of all guide sections
- plan_roster(config, roster_size, existing_fighters) - calls OpenRouter to generate interconnected roster plan as JSON array
- generate_fighter(config, archetype, has_supernatural, existing_fighters, roster_plan_entry) - calls OpenRouter to create full Fighter from plan entry or archetype
- _extract_stats(data, has_supernatural, config) - clamps stat values to config bounds
- CHARSHEET_LAYOUT - character reference sheet turnaround prompt template
- _charsheet_style_base(gender) - art style + reference sheet prefix
- _charsheet_style(gender, tier) - adds NSFW nudity prefix when needed
- _charsheet_tail(gender, tier) - art style tail with tier-specific nudity descriptors
- _triple_prompt_style(gender) - three-panel SFW/barely/NSFW layout prompt
- _build_charsheet_prompt(body_parts, clothing, expression, tier, gender) - assembles full charsheet image prompt dict with front/3Q/rear views
- _build_triple_prompt(body_parts, clothing_sfw, clothing, clothing_nsfw, expression, gender) - assembles three-panel comparison prompt dict
- _normalize_core_stats(stats, config) - scales core stats to target range if out of bounds

---

## app/engine/post_fight.py
File: app/engine/post_fight.py
File Length: 214 lines
Purpose: Applies fight results to persistent fighter state: records, stats, injuries, storylines, and rivalries.

Artefacts
- apply_fight_results(match, config) - orchestrates all post-fight updates, saves fighters and world_state
- _update_records(f1, f2, outcome) - increments wins/losses/draws/kos/submissions
- _apply_stat_adjustments(fighter, outcome, is_fighter1) - stat +/- based on win/loss and performance
- _adjust_stat(stats, stat_name, delta, changes) - clamps stat between 15-95
- _apply_injuries(fighter, injuries) - creates Injury objects, sets health_status/morale
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
File Length: 42 lines
Purpose: Art style constants and gender-aware accessors for Arcane-inspired image generation prompts.

Artefacts
- ART_STYLE_BASE, ART_STYLE_FEMALE, ART_STYLE_MALE - base and gendered full art style strings
- ART_STYLE_TAIL_BASE, ART_STYLE_TAIL_FEMALE, ART_STYLE_TAIL_MALE - shorter tail variants
- get_art_style(gender) - returns gender-appropriate full art style
- get_art_style_tail(gender) - returns gender-appropriate tail art style

---

## app/models/fighter.py
File: app/models/fighter.py
File Length: 134 lines
Purpose: Fighter data model with nested Stats, Record, Injury, and Condition dataclasses.

Artefacts
- Stats - power, speed, technique, toughness, supernatural; core_total()
- Record - wins, losses, draws, kos, submissions; total_fights(), win_percentage()
- Injury - type, severity, recovery_days_remaining
- Condition - health_status, injuries list, recovery_days_remaining, morale, momentum
- Fighter - full fighter profile with identity, physical, attire (3 tiers), image_prompt dicts (3 tiers + triple), stats, record, condition, storyline_log, rivalries

---

## app/models/match.py
File: app/models/match.py
File Length: 93 lines
Purpose: Match data model with analysis, outcome, and moment sub-models.

Artefacts
- FightMoment - moment_number, description, attacker_id, action, image_prompt, image_path
- MatchupAnalysis - fighter1/2_win_prob, fighter1/2_methods, key_factors
- MatchOutcome - winner_id, loser_id, method, round_ended, performances, injuries, is_draw
- Match - full match record with fighter IDs/names, analysis, outcome, narrative, moments, snapshots, post_fight_updates

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
File Length: 200 lines
Purpose: Grok (x.ai) image generation and editing API client for character sheet images.

Artefacts
- TIER_PROMPT_KEYS - maps tier names to fighter prompt dict keys
- generate_image(prompt, config, aspect_ratio, resolution, n) - calls Grok image generation API with retries, returns URL list
- edit_image(prompt, image_paths, config, ...) - calls Grok image edit API with base64-encoded reference images
- download_image(url, save_path) - downloads image URL to disk
- generate_charsheet_images(fighter, config, output_dir, tiers) - generates per-tier charsheet images + optional triple panel, saves to output_dir

---

## app/scripts/generate_roster.py
File: app/scripts/generate_roster.py
File Length: 162 lines
Purpose: Two-phase roster generation script: plan roster via AI, then generate fighters from plan with optional image generation.

Artefacts
- plan_roster_cmd() - calls plan_roster, saves roster_plan.json, prints summary
- generate_from_plan(generate_images) - reads roster_plan.json, generates each fighter via generate_fighter, optionally generates charsheet images, initializes WorldState
- generate_roster(generate_images) - runs both phases sequentially
- CLI: --plan (phase 1 only), --generate (phase 2 only), --images (include charsheet generation)
