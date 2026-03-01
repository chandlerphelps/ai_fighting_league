# Backend - Simple File Summaries

Quick reference for finding code.

## Config

- `app/config.py` - Config dataclass with API keys, league constants, stat bounds, recovery ranges; load_config() from .env

## Entry Point

- `app/run_day.py` - CLI: python -m app.run_day [--days N] [--init], advances league day-by-day

## Engine (`app/engine/`)

- `fight_simulator.py` - Fight pipeline: calculate_probabilities (AI), determine_outcome (random roll), generate_moments (AI choreography), run_fight (orchestrator)
- `fighter_generator.py` - AI fighter creation with character design guide, archetype system (8F/8M), tiered image prompts (SFW/barely/NSFW/triple), stat validation
  - plan_roster() - AI roster planning
  - generate_fighter() - full fighter generation from plan entry
  - _build_charsheet_prompt() / _build_triple_prompt() - image prompt assembly
- `post_fight.py` - apply_fight_results: updates records, stats, injuries, storylines, rivalries
- `rankings.py` - calculate_rankings: sort by win%, total wins, recent form
- `matchmaker.py` - generate_fight_card: score pairings by rank proximity, rivalry, idle time
- `day_ticker.py` - advance_day: injury recovery, run events, schedule new events
- `image_style.py` - Arcane art style constants and gender-aware accessors (get_art_style, get_art_style_tail)

## Models (`app/models/`)

- `fighter.py` - Fighter, Stats, Record, Injury, Condition dataclasses
- `match.py` - Match, FightMoment, MatchupAnalysis, MatchOutcome dataclasses
- `event.py` - Event, EventMatch dataclasses
- `world_state.py` - WorldState, RivalryRecord dataclasses

## Services (`app/services/`)

- `data_manager.py` - JSON file CRUD for fighters, matches, events, world_state
- `openrouter.py` - OpenRouter HTTP client (call_openrouter, call_openrouter_json) with retry and markdown fence stripping
- `grok_image.py` - Grok image API client: generate_image, edit_image, download_image, generate_charsheet_images

## Scripts (`app/scripts/`)

- `generate_roster.py` - Two-phase: plan_roster_cmd (AI plan) then generate_from_plan (create fighters + images); CLI: --plan, --generate, --images
