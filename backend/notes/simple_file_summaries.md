# Backend - Simple File Summaries

Quick reference for finding code. Updated as files are added.

## Engine (`app/engine/`)

- `fight_simulator.py` — 3-phase fight pipeline: calculate_probabilities (AI), determine_outcome (random), generate_narrative (AI), run_fight (orchestrator)
- `fighter_generator.py` — AI-driven fighter creation with archetype guidance and stat validation
- `post_fight.py` — apply_fight_results: updates records, stats, injuries, storylines, rivalries
- `rankings.py` — calculate_rankings: sort by win%, total wins, recent form
- `matchmaker.py` — generate_fight_card: score pairings by rank proximity, rivalry, idle time
- `day_ticker.py` — advance_day: injury recovery, run events, schedule new events

## Models (`app/models/`)

- `fighter.py` — Fighter, FightingStyle, PhysicalStats, CombatStats, PsychologicalStats, SupernaturalStats, Record, Injury, Condition
- `match.py` — Match, MatchupAnalysis, MatchOutcome
- `event.py` — Event, EventMatch
- `world_state.py` — WorldState, RivalryRecord

## Services (`app/services/`)

- `data_manager.py` — JSON file CRUD for fighters, matches, events, world_state
- `openrouter.py` — HTTP client for OpenRouter API (call_openrouter, call_openrouter_json)

## Config

- `app/config.py` — Config dataclass with all league constants, load_config() from .env

## Scripts (`app/scripts/`)

- `generate_roster.py` — Generate 16 fighters (2 per archetype), initialize world_state

## Entry Point

- `app/run_day.py` — CLI: python -m app.run_day [--days N] [--init]

## Tests (`tests/`)

- `test_models.py` — Dataclass serialization round-trip tests
- `test_outcome.py` — Outcome distribution validation (1000 iterations)
- `test_rankings.py` — Ranking order correctness
- `test_matchmaker.py` — Matchmaker logic (injuries, cooldown, rivalry)
