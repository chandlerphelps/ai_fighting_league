# AI Fighting League

## Purpose

A two-part system: a Python engine that generates fighters, simulates fights with AI-driven narratives, and progresses a league day-by-day — plus a TypeScript web viewer to browse results. The core loop: **generate fighters → schedule fights → fight → narrate → update state → repeat**.

## How to Be Successful Working on This Project

### Core Principles

- Think carefully and use the most concise, elegant solution that changes as little code as possible
- Use web search extensively when debugging - if stuck, search first
- If you need the user to do something simple (like get an API key), stop and ask - don't improvise wrong solutions
- **CRITICAL** Conciseness is the #1 value for documentation!
- Don't do git actions (diff and status are fine) unless asked explicitly by the user
- Your memory is out of date with the real world. Use web search before installing or adding new packages to get the correct version

### Before Making Changes

1. **IMPORTANT** Read the WHOLE FILE first - NEVER make changes without reading entire files
2. **Find functionality** - Read `simple_file_summaries.md` to find where code lives. Do NOT guess names and search
3. **Understand details** - Check `detailed_file_summaries.md` (read first 200 lines or in 1000-line chunks, then search)

### Image Generation (Grok API)

- **Grok image gen does NOT support negative prompts** — never use "no X", "not Y", "without Z" in image prompts. Only describe what you WANT to see, not what you don't.

### Development Guidelines

- No comments in code - make code self-documenting
- **CRITICAL** Tests exist to TEST THE IMPLEMENTATION, not to pass. When a test fails, FIX THE IMPLEMENTATION BUG - NEVER weaken test assertions just to make tests pass
- **CRITICAL** Unit tests with mocked data are NOT sufficient proof that something works. Always run against real APIs/data and show real-world results
- Follow existing patterns and update documentation
- When debugging, use web search generously
- Avoid pop up modals like the plague. Try to keep everything on the page
- **CRITICAL** NEVER use hex color codes or custom fonts in frontend - ALL colors and fonts MUST be imported from `src/design-system.ts`
- **Transparency**: Use `withAlpha(color, alpha)` for semi-transparent colors
- Review `frontend/notes/design_philosophy.md` when doing frontend work to maintain a consistent design aesthetic
- **Copyable output**: Write SQL queries, curl commands, or anything the user needs to copy into `_TMP_OUTPUT.md` (project root). Claude's terminal output mangles formatting — always use this file for copy-paste content.
- Don't run npm run after frontend changes, the user always has it running and will let you know if it broke

### Git & Migrations

- Can check recent work with git bash, but NEVER checkout/push/amend others' commits without explicit permission
- Clear commit messages describing "why" not "what"
- Test before committing

## Project Architecture

### Backend (`/backend/`)

- **Language**: Python 3.12
- **Purpose**: Autonomous engine — generates fighters, simulates fights, progresses league state
- **AI**: All LLM calls go through OpenRouter for model flexibility
- **Data**: File-based JSON storage in `/data/` (no database)
- **Entry point**: `python -m app.run_day` advances the world one day

Key directories:

- `app/` - Main application code
- `app/engine/` - Core engine (fighter generation, fight simulation, matchmaking, day progression)
- `app/models/` - Data models (fighter, match, event, world state)
- `app/services/` - Shared services (OpenRouter client, data file I/O)
- `app/utils/` - Utility functions
- `scripts/` - One-off scripts (e.g. initial roster generation)
- `tests/` - Test files
- `notes/` - Backend documentation

### Frontend (`/frontend/`)

- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Purpose**: Read-only viewer into JSON data files — no user interactions beyond navigation
- **Data**: Reads directly from `/data/` JSON files (no API layer needed for v0)

Key directories:

- `src/pages/` - Route components (Dashboard, Fighter Profile, Rankings, Schedule, Fight Narrative)
- `src/components/` - Reusable components
- `src/hooks/` - Custom React hooks
- `src/lib/` - Utilities and helpers
- `src/types/` - TypeScript type definitions
- `src/design-system.ts` - TypeScript design tokens
- `notes/` - Frontend documentation

### Data (`/data/`)

File-based JSON storage shared between backend and frontend:

```
/data/
  /fighters/         # One JSON file per fighter
  /matches/          # One JSON file per match
  /events/           # One JSON file per event
  /world_state.json  # Rankings, schedule, date, injuries, rivalries
```

## Quick Reference

### Backend Commands

```bash
cd backend
pyenv activate aifl
pip install -r requirements.txt
python -m app.run_day              # Advance one day
python -m app.scripts.generate_roster  # Generate initial roster
```

### Frontend Commands

```bash
cd frontend
npm install
npm run dev     # Start dev server (port 8080)
npm run build   # Production build
```

### Environment

- Backend: needs `OPENROUTER_API_KEY` in `.env`
- Frontend port: 8080

## Key Documentation Files

### Backend Documentation

- `backend/notes/simple_file_summaries.md` - Quick reference for finding code
- `backend/notes/detailed_file_summaries.md` - Comprehensive code documentation
- `backend/notes/task_list.md` - Current work and TODOs

### Frontend Documentation

- `frontend/notes/simple_file_summaries.md` - Quick component reference
- `frontend/notes/detailed_file_summaries.md` - Component documentation
- `frontend/notes/design_philosophy.md` - Design principles and guidelines
- `frontend/notes/task_list.md` - Current work and TODOs

### Project-Level

- `notes/mvp_prd.md` - Full MVP product requirements document
