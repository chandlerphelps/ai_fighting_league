# Frontend - Simple File Summaries

Quick reference for finding components and code.

## App

- `src/App.tsx` - Routes: / (Dashboard), /fighter/:id, /rankings, /schedule, /match/:id, /roster (RosterManager)

## Pages (`src/pages/`)

- `Dashboard.tsx` - League date, today's fights, roster health, next event, recent results
- `FighterProfile.tsx` - Full fighter profile with tiered image viewer (sfw/barely/nsfw/body_ref), stats, record, fight history, storyline, rivalries
- `FightNarrative.tsx` - Full fight narrative, stat comparison, outcome banner, key moments, post-fight changes
- `Rankings.tsx` - Ranked table with record, streak, recent form indicators, injury badges
- `Schedule.tsx` - Upcoming and past events with fight cards
- `RosterManager.tsx` - Admin roster management: view/edit/delete fighters, generate/regenerate character/outfits/images, outfit options manager, tiered image viewer (SFW/BARELY/NSFW/BODY_REF)

## Components (`src/components/`)

- `Layout.tsx` - Top nav (Dashboard, Rankings, Schedule, Roster) + league date + content area
- `FightCard.tsx` - Displays fights for an event with results and links
- `FighterLink.tsx` - Fighter name as link to profile, optional record display
- `FighterPortrait.tsx` - Fighter thumbnail (SFW image) with fallback to initial letter
- `StatBar.tsx` - Stat name + value + colored bar (red/amber/green tiers)
- `InjuryBadge.tsx` - Inline injury indicator with days remaining
- `NoData.tsx` - "Run backend first" fallback message

## Hooks (`src/hooks/`)

- `useData.ts` - Generic useDataLoader + typed hooks: useWorldState, useFighter, useAllFighters, useMatch, useAllMatches, useEvent, useAllEvents

## Lib (`src/lib/`)

- `data.ts` - Fetch-based loaders for all data types from /data/ JSON files (loadWorldState, loadFighter, loadAllFighters, loadAllFighterFiles, etc.)
- `images.ts` - slugify(), fighterImagePath(id, name, tier), moveImagePath(id, name, moveIndex, tier)
- `api.ts` - API client for backend REST: fighter CRUD, generate/regenerate endpoints, task polling (pollUntilDone), outfit options, archetypes

## Types (`src/types/`)

- `fighter.ts` - Fighter (with image_prompt_body_ref, moves), Stats, Record, Injury, Condition, CharsheetPrompt, Move
- `match.ts` - Match, FightMoment, MatchupAnalysis, MatchOutcome
- `event.ts` - Event, EventMatch
- `world_state.ts` - WorldState, RivalryRecord

## Design System

- `design-system.ts` - Dark theme tokens (colors, fonts, spacing), withAlpha() helper
- `index.css` - Global reset, dark background, scrollbar styling
