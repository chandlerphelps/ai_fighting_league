# Backend - Task List

## Current

## Backlog

## Done

---

# PROJECT: AI Fighting League — MVP (v0) Backend Engine

## OVERARCHING GOAL

Build a fully autonomous Python engine that generates fighters, simulates fights with AI-driven narratives via OpenRouter, and progresses a league day-by-day. After this is complete, running `python -m app.run_day` will advance the world one day — checking for scheduled events, running fights through a 3-phase pipeline (AI probability → random outcome roll → AI narrative), updating fighter records/stats/injuries, and auto-generating future fight cards. All state lives in JSON files under `/data/` that the frontend will read directly.

Key scope decisions for v0 (from PRD):
- 15 core stats (5 physical + 5 combat + 5 psychological) + 4 optional supernatural — NOT the expanded 8+8+8+8 from the detailed design docs
- Standard 3-round fights only — no match type variants
- No death mechanics, no story graph, no factions, no fan economy
- Narrative output is prose text (~800-1500 words), not structured JSON event timeline
- Rankings are simple ordered list by record + recent performance
- Rivalry tracking is lightweight (fight history between pairs, auto-flag after 2+ fights)

---

**Step 1: Data Models + JSON Schemas + Data Manager**
- 1.1: Define `Fighter` dataclass in `app/models/fighter.py` with all fields from PRD §2.1:
  - Identity (id, ring_name, real_name, age, origin, alignment)
  - Physical description (height, weight, build, distinguishing_features, ring_attire)
  - Backstory (text), personality_traits (list), fears_quirks (list)
  - FightingStyle (primary_style, secondary_style, signature_move, finishing_move, known_weaknesses)
  - PhysicalStats (strength, speed, endurance, durability, recovery) — 1-100
  - CombatStats (striking, grappling, defense, fight_iq, finishing_instinct) — 1-100
  - PsychologicalStats (aggression, composure, confidence, resilience, killer_instinct) — 1-100
  - SupernaturalStats (arcane_power, chi_mastery, elemental_affinity, dark_arts) — 0-100
  - Record (wins, losses, draws, kos, submissions)
  - Condition (health_status, injuries list, recovery_days_remaining, morale, momentum)
  - storyline_log (list of strings), rivalries (list of fighter IDs), last_fight_date, ranking
- 1.2: Define `Match` dataclass in `app/models/match.py`:
  - MatchupAnalysis (win probabilities, likely methods, key factors)
  - MatchOutcome (winner_id, loser_id, method, round_ended, performance ratings, injuries, is_draw)
  - Match (id, event_id, date, fighter IDs/names, analysis, outcome, narrative text, stat snapshots, post-fight updates)
- 1.3: Define `Event` dataclass in `app/models/event.py`:
  - EventMatch (match_id, fighter IDs/names, completed flag, winner, method)
  - Event (id, date, name, matches list, completed flag, summary)
- 1.4: Define `WorldState` dataclass in `app/models/world_state.py`:
  - current_date, day_number, rankings (ordered list of fighter IDs), upcoming_events, completed_events
  - active_injuries (fighter_id → recovery_days), rivalry_graph (list of fighter-pair records), last_daily_summary
- 1.5: Build `app/services/data_manager.py` with CRUD functions for each model:
  - save/load/load_all for fighters, matches, events
  - save/load for world_state
  - All reads return dicts (from JSON), all writes accept dataclass instances
  - Include `ensure_data_dirs()` that creates `/data/fighters/`, `/data/matches/`, `/data/events/`
- 1.6: Create `app/config.py` with Config dataclass:
  - OpenRouter settings (api_key from env, base_url, default_model, narrative_model)
  - League constants (roster_size=16, fights_per_event=3, events_per_week=2, rounds_per_fight=3)
  - Stat constraints (min_total_stats=900, max_total_stats=1100)
  - Injury recovery ranges (minor=7d, moderate=14-28d, severe=42-56d)
  - Other tunables (rematch_cooldown=14d, max_idle=14d, narrative word range)

**Validation:** Write a test in `tests/test_models.py` that creates instances of each dataclass, serializes to JSON via `dataclasses.asdict()`, and deserializes back. Run `pytest tests/test_models.py` — all pass. Manually verify a fighter JSON file is written to `data/fighters/` and can be read back.

---

**Step 2: OpenRouter Service**
- 2.1: Create `app/services/openrouter.py` with async HTTP client (httpx):
  - `call_openrouter(prompt, config, model=None, system_prompt="", temperature=0.7, max_tokens=4096) → str`
  - `call_openrouter_json(prompt, config, ...) → dict` — same but parses response as JSON, strips markdown fences
- 2.2: Load API key from `OPENROUTER_API_KEY` env var (via config)
- 2.3: Add `requirements.txt` with initial deps: httpx, pytest, python-dotenv
- 2.4: Create `backend/env.development` template with `OPENROUTER_API_KEY=` placeholder

**Validation:** Write a small script or test that calls OpenRouter with a simple prompt ("Say hello in JSON format") and prints the response. Confirm the round-trip works with a real API key. Test both text and JSON response parsing.

---

**Step 3: Fighter Generation Engine**
- 3.1: Create `app/engine/fighter_generator.py`:
  - `generate_fighter(config, archetype=None, has_supernatural=False) → Fighter`
  - Constructs a detailed prompt including: archetype guidance, stat constraints (total 900-1100 for 15 core stats), supernatural rules, character creation philosophy from `08_character_creation_guide.md`
  - Parses AI JSON response into Fighter dataclass
  - Validates stat totals and clamps individual stats (15-95 range, supernatural 0-50 for v0)
  - Generates a short UUID as fighter ID
- 3.2: Create `app/scripts/generate_roster.py`:
  - Generates 16 fighters: assign archetypes from the 8 templates (2 each), mark 2-3 for supernatural
  - Saves each fighter to `/data/fighters/`
  - Initializes world_state.json with day 1 date, all fighters in rankings (random initial order), empty schedule
- 3.3: The generation prompt should reference the character creation guide's core philosophies and archetype descriptions to produce distinctive, well-designed fighters

**Validation:** Run `python -m app.scripts.generate_roster`. Inspect 3-4 generated fighter JSON files — verify: all required fields populated, stat totals within 900-1100 band, supernatural fighters have 1-2 non-zero supernatural stats at 20-50, grounded fighters have all supernatural at 0, backstories are 2-3 paragraphs, fighting styles have named signature/finishing moves. Verify `world_state.json` exists with 16 fighters in rankings.

---

**Step 4: Fight Engine — Phase 1 (Probability Calculation)**
- 4.1: Create `app/engine/fight_simulator.py`:
  - `calculate_probabilities(fighter1: dict, fighter2: dict, config, rivalry_context=None) → MatchupAnalysis`
  - Constructs prompt with both fighters' full profiles, current condition, recent record, rivalry history if any
  - Asks AI to return JSON: win probabilities (clamped 5%-95%), likely victory methods for each fighter, key matchup factors
  - Parses and validates the response
- 4.2: Handle supernatural traits in the prompt — instruct AI to factor them as an edge, not a dominator

**Validation:** Load two fighters from data, run probability calculation, print result. Verify: probabilities sum to 1.0 (within rounding), both between 0.05-0.95, victory methods are valid enums (ko_tko, submission, decision_unanimous, decision_split, draw), key factors reference actual fighter attributes.

---

**Step 5: Fight Engine — Phase 2 (Outcome Determination)**
- 5.1: Add to `fight_simulator.py`:
  - `determine_outcome(fighter1: dict, fighter2: dict, analysis: MatchupAnalysis, config) → MatchOutcome`
  - Pure Python, no AI — weighted random rolls:
    - Winner: random float vs win probability (with draw carved out at ~2-3%)
    - Method: weighted roll from winner's likely methods
    - Round: weighted by method (KO earlier, submission mid-late, decision always round 3)
    - Performance quality: based on probability gap and method
    - Injuries: probability roll influenced by method and fight intensity (KO/TKO → higher injury chance)
  - Injury severity: none/minor/moderate/severe with recovery days from config ranges

**Validation:** Run outcome determination 100 times for the same matchup, collect statistics. Verify: winner distribution roughly matches probabilities, method distribution roughly matches likely methods, injury rates are reasonable (most fights produce no or minor injuries, severe injuries are rare ~5-10%).

---

**Step 6: Fight Engine — Phase 3 (Narrative Generation)**
- 6.1: Add to `fight_simulator.py`:
  - `generate_narrative(fighter1: dict, fighter2: dict, analysis: MatchupAnalysis, outcome: MatchOutcome, config) → str`
  - Constructs prompt with: both fighter profiles, matchup analysis from Phase 1, determined outcome from Phase 2
  - Instructs AI to write: pre-fight scene (1 paragraph), round-by-round action, supernatural flavor where applicable, the finish or decision, post-fight aftermath with story hooks
  - Target: 800-1500 words of dramatic prose
  - Uses the narrative_model from config (may differ from default_model)
- 6.2: Add `run_fight(fighter1_id, fighter2_id, event_id, config) → Match`:
  - Orchestrates the full 3-phase pipeline
  - Loads fighters, runs phases 1-2-3, assembles Match object with stat snapshots
  - Returns the complete Match (does NOT save — caller handles persistence)

**Validation:** Run a full fight between two generated fighters. Read the narrative output — verify: it's 800-1500 words, references both fighters by name, mentions their actual fighting styles and signature moves, the narrative outcome matches the determined outcome (correct winner, correct method, correct round), supernatural elements appear only for fighters who have them. The prose should be dramatic and engaging, not a dry report.

---

**Step 7: Post-Fight Updates**
- 7.1: Create `app/engine/post_fight.py`:
  - `apply_fight_results(match: Match, config) → dict` — returns a summary of all changes made
  - Updates both fighters' records (wins/losses/draws/kos/submissions)
  - Applies stat adjustments: small +/- 1-3 based on performance (confidence up after dominant win, composure down after KO loss, etc.). Supernatural stats stay fixed.
  - Applies condition updates: injuries from outcome, sets recovery_days_remaining, updates health_status
  - Appends to fighters' storyline_log: AI-generated short paragraph about what this fight meant for them
    - This is a small AI call — given the fight result and fighter profile, write 2-3 sentences
  - Updates rivalry tracking: if these fighters have now fought 2+ times, flag as rivalry in world_state
  - Saves updated fighters to disk
- 7.2: Storyline generation prompt should capture narrative significance — confidence building, humbling loss, rivalry intensifying, etc.

**Validation:** Run a fight, then apply post-fight updates. Reload both fighters from disk and verify: records incremented correctly, stats shifted by small amounts in logical directions, injured fighter has recovery_days > 0, storyline_log has a new entry, rivalry graph updated if applicable.

---

**Step 8: Rankings System**
- 8.1: Create `app/engine/rankings.py`:
  - `calculate_rankings(fighters: list[dict], recent_matches: list[dict]) → list[str]`
  - Simple ranking algorithm: primary sort by win percentage, secondary by total wins, tertiary by recent form (last 3-5 fights)
  - Returns ordered list of fighter IDs from #1 to #N
  - Handles ties (more recent activity wins)
- 8.2: Initial rankings (day 0, no fights yet) are randomized

**Validation:** Create a set of fighters with known records, run ranking calculation, verify the order is logical. A 5-1 fighter should rank above a 3-3 fighter. Among fighters with same record, one with more recent wins should rank higher.

---

**Step 9: Auto-Generated Matchmaking**
- 9.1: Create `app/engine/matchmaker.py`:
  - `generate_fight_card(world_state: dict, fighters: list[dict], matches: list[dict], config) → list[tuple[str, str]]`
  - Returns list of fighter ID pairs for the event
  - Logic:
    - Filter to available fighters (not injured, recovery_days_remaining == 0)
    - Prefer similarly ranked fighters (within 3-4 ranking positions of each other)
    - Boost priority for active rivalries
    - Enforce rematch cooldown (minimum 14 days between same pairing)
    - Enforce activity rotation (no fighter idle more than 14 days — prioritize those who haven't fought recently)
    - Generate config.fights_per_event matchups (default 3)
- 9.2: Handle edge cases: not enough healthy fighters (reduce card size), odd number of available fighters, new fighters with no history

**Validation:** Set up a world state with 16 fighters (some injured, some with recent fights, some with rivalries). Run matchmaking. Verify: no injured fighters are matched, no same-day double bookings, matchups are between reasonably ranked fighters, rivalries are prioritized, recently idle fighters get scheduled.

---

**Step 10: Day-to-Day Progression (The Daily Tick)**
- 10.1: Create `app/engine/day_ticker.py`:
  - `advance_day(config) → str` — returns daily summary text
  - Loads world state
  - Increments current_date by 1 day
  - Processes injury recovery: decrement all recovery_days_remaining, update health_status to "healthy" when timer hits 0
  - Checks if there's an event scheduled for today:
    - If yes: run all fights on the card via `run_fight()`, apply post-fight updates, update rankings
    - If no: check if schedule needs new events (if no events in the next 7 days, generate one or two)
  - Generates event scheduling: place events on Tuesdays and Saturdays (or similar ~2/week cadence)
  - Creates Event objects for newly scheduled events with matchmaking
  - Saves updated world_state
  - Returns a daily summary string (what happened today: fights run, injuries healed, events scheduled)
- 10.2: Create `app/run_day.py` as the entry point:
  - Loads config, calls `advance_day(config)`, prints summary
  - Can accept `--days N` argument to advance multiple days in sequence

**Validation:** Generate roster (step 3), then run `python -m app.run_day --days 14`. This should produce ~4 events (2/week) with ~12 total fights. Verify:
- Events are spaced out through the 14 days
- Fight narratives exist in `/data/matches/`
- Fighter records updated correctly (total wins + losses across roster should equal 2x fights run, minus draws)
- Injured fighters sit out appropriately
- Rankings change over the 14 days
- No fighter goes more than 14 days without a fight (if healthy)
- Daily summaries printed to console describe what happened each day

---

**Step 11: End-to-End Testing + Polish**
- 11.1: Write integration test that runs the full cycle: generate roster → advance 7 days → verify world state integrity
  - All fighter records sum correctly
  - No data corruption (all referenced IDs exist)
  - Rankings list includes all active fighters
  - Scheduled events have valid fighter pairings
- 11.2: Add error handling: graceful failure if OpenRouter returns bad JSON (retry up to 3 times), handle missing data files
- 11.3: Add `--init` flag to run_day.py that generates roster and initial world state if `/data/` is empty
- 11.4: Verify the full data contract: all JSON files written by the backend should have consistent schemas that the frontend can rely on

**Validation:** Run `python -m app.run_day --init --days 14` from a clean `/data/` directory. The entire system should bootstrap and produce 14 days of league progression with zero manual intervention. Inspect the data directory — it should contain 16 fighter files, multiple match files, multiple event files, and a world_state.json with current rankings and schedule.
