# Frontend - Simple File Summaries

Quick reference for finding components and code. Updated as files are added.

## Pages (`src/pages/`)

- `Dashboard.tsx` — League date, today's fights, roster health, next event, recent results
- `FighterProfile.tsx` — Full fighter profile with stats, backstory, record, fight history, storyline, rivalries
- `FightNarrative.tsx` — Full fight narrative, stat comparison, outcome banner, post-fight changes
- `Rankings.tsx` — Ranked table with record, streak, recent form indicators, injury badges
- `Schedule.tsx` — Upcoming and past events with fight cards

## Components (`src/components/`)

- `Layout.tsx` — Top nav (Dashboard, Rankings, Schedule) + league date + content area
- `FightCard.tsx` — Displays fights for an event with results and links
- `FighterLink.tsx` — Fighter name as link to profile, optional record display
- `StatBar.tsx` — Stat name + value + colored bar (red/amber/green tiers)
- `InjuryBadge.tsx` — Inline injury indicator with days remaining
- `NoData.tsx` — "Run backend first" fallback message

## Hooks (`src/hooks/`)

- `useData.ts` — Generic useDataLoader + typed hooks: useWorldState, useFighter, useAllFighters, useMatch, useAllMatches, useEvent, useAllEvents

## Lib (`src/lib/`)

- `data.ts` — Fetch-based loaders for all data types from /data/ JSON files

## Types (`src/types/`)

- `fighter.ts` — Fighter, FightingStyle, PhysicalStats, CombatStats, PsychologicalStats, SupernaturalStats, Record, Injury, Condition
- `match.ts` — Match, MatchupAnalysis, MatchOutcome
- `event.ts` — Event, EventMatch
- `world_state.ts` — WorldState, RivalryRecord

## Design System

- `design-system.ts` — Dark theme tokens (colors, fonts, spacing), withAlpha() helper
- `index.css` — Global reset, dark background, scrollbar styling
