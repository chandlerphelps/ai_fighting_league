# Frontend - Task List

## Current

## Backlog

## Done

---

# PROJECT: AI Fighting League — MVP (v0) Frontend Viewer

## OVERARCHING GOAL

Build a read-only TypeScript web app (Vite + React) that reads from the JSON data files produced by the backend engine and displays: today's fight card with results, fighter profiles with stats/records/storylines, current rankings, schedule/history navigation, and full fight narratives. No API layer — the frontend reads `/data/` files directly via static import or local file serving. Dark theme, minimal styling, text and stats only, no images.

After this is complete, a user can start the dev server, browse to localhost:8080, and explore the full state of the league — today's fights, every fighter's profile and history, the rankings, and past events — all rendered from the same JSON files the Python engine writes.

---

**Step 1: Project Setup + Design System + Routing**
- 1.1: Initialize Vite + React + TypeScript project in `frontend/`:
  - `package.json`, `vite.config.ts` (port 8080), `tsconfig.json`, `index.html`
  - Install deps: react, react-dom, react-router-dom, @types/react, @types/react-dom, typescript, vite
- 1.2: Create `src/design-system.ts` with dark theme tokens:
  - Colors: background (dark), surface (slightly lighter), text (light), accent (gold/amber for fight league aesthetic), muted text, borders, status colors (healthy=green, injured=red, rivalry=orange)
  - Typography: monospace/system font stack, size scale
  - Spacing scale, withAlpha() helper
- 1.3: Create `src/index.css` with global dark theme reset styles
- 1.4: Create `src/App.tsx` with React Router setup — routes for:
  - `/` → Dashboard
  - `/fighter/:id` → Fighter Profile
  - `/rankings` → Rankings
  - `/schedule` → Schedule/History
  - `/match/:id` → Fight Narrative
- 1.5: Create a shared layout component with navigation sidebar or top nav:
  - Links to Dashboard, Rankings, Schedule
  - Current league date displayed

**Validation:** Run `npm run dev`. The app loads at localhost:8080 with a dark-themed layout. All routes render placeholder pages. Navigation between pages works. Design system colors are applied globally.

---

**Step 2: TypeScript Types + Data Loading**
- 2.1: Create `src/types/fighter.ts` — TypeScript interfaces matching the backend Fighter JSON schema exactly
- 2.2: Create `src/types/match.ts` — interfaces for Match, MatchupAnalysis, MatchOutcome
- 2.3: Create `src/types/event.ts` — interfaces for Event, EventMatch
- 2.4: Create `src/types/world_state.ts` — interface for WorldState
- 2.5: Create `src/lib/data.ts` — data loading utilities:
  - For v0, serve the `/data/` directory as static assets via Vite config (symlink or copy, or configure Vite's public dir to point to project-root `/data/`)
  - Functions: `loadWorldState()`, `loadFighter(id)`, `loadAllFighters()`, `loadMatch(id)`, `loadAllMatches()`, `loadEvent(id)`, `loadAllEvents()`
  - Each function fetches the JSON file and returns typed data
- 2.6: Create `src/hooks/useData.ts` — React hooks wrapping the data loaders with loading/error states

**Validation:** Add a temporary debug component that loads and displays the world state JSON. Verify it shows the current date, rankings list, and upcoming events from the actual data files. If data doesn't exist yet, show a clear "No data — run the backend engine first" message.

---

**Step 3: Dashboard Page**
- 3.1: Build `src/pages/Dashboard.tsx`:
  - Current league date (from world_state)
  - Today's fight card: if there's an event today, show the matchups with results
    - Each fight: fighter names (linked to profiles), winner, method, round — click to view full narrative
    - If no event today, show "No fights today"
  - Quick roster health overview: count of healthy/injured fighters, list injured fighters with recovery timelines
  - Next upcoming event: date + scheduled matchups
  - Recent results: last 3-5 completed fights with quick summaries
- 3.2: Create reusable components as needed:
  - `FightCard` — displays a list of fights for an event
  - `FighterLink` — name that links to profile, with optional record display
  - `InjuryBadge` — shows injury status inline

**Validation:** With backend data generated (at least a few days of league progression), the dashboard shows: current date, today's event (if any), roster health breakdown, next upcoming event, and recent results. All fighter names link to their profiles. All fight results link to narrative pages.

---

**Step 4: Fighter Profile Page**
- 4.1: Build `src/pages/FighterProfile.tsx`:
  - Header: ring name, real name, age, origin, alignment badge
  - Physical description section: height, weight, build, distinguishing features, ring attire
  - Stats display: grouped by category (Physical, Combat, Psychological, Supernatural)
    - Each stat shown as name + value + visual bar (colored by value tier: low/mid/high)
    - Supernatural stats only shown if fighter has any non-zero values
  - Fighting style section: primary/secondary style, signature move, finishing move, weaknesses
  - Backstory section: full text
  - Record: W-L-D with KOs and submissions breakdown
  - Fight history: list of past fights with date, opponent, result, method — each links to narrative
  - Current condition: healthy badge or injury details with recovery timeline
  - Storyline log: chronological list of story beat paragraphs
  - Rivalries: list of rival fighters (linked)
- 4.2: Create reusable stat bar component: `StatBar` — name, value (1-100), colored fill

**Validation:** Navigate to a fighter's profile from the dashboard. All sections display correctly: stats with visual bars, backstory text, fight history with working links, condition status, storyline entries. The page feels information-dense but scannable.

---

**Step 5: Fight Narrative Page**
- 5.1: Build `src/pages/FightNarrative.tsx`:
  - Header: Fighter 1 vs Fighter 2, event name, date
  - Outcome banner: winner, method, round
  - Side-by-side stat comparison at time of fight (from stat snapshots in match data)
  - Full narrative text — rendered as formatted prose with good typography
  - Post-fight section: stat changes for both fighters, storyline updates
  - Links back to both fighters' profiles

**Validation:** Click a fight result from the dashboard or a fighter's history. The full narrative displays with good formatting. Stats are shown side-by-side. Winner/method/round match what's in the data. Post-fight changes are visible.

---

**Step 6: Rankings Page**
- 6.1: Build `src/pages/Rankings.tsx`:
  - Ordered table/list of all fighters by current ranking
  - Columns: rank, fighter name (linked), record (W-L-D), current streak (e.g. "W3" or "L2"), recent form (last 5 results as W/L indicators)
  - Injured fighters marked with injury badge and grayed slightly
  - Optional: highlight fighters who moved up/down in rankings recently

**Validation:** Rankings page shows all 16 fighters in order. Records are accurate. Streak information is correct (verify against fight history). Injured fighters are visually distinguished. Clicking a fighter name goes to their profile.

---

**Step 7: Schedule / History Page**
- 7.1: Build `src/pages/Schedule.tsx`:
  - Two sections: Upcoming Events and Past Events
  - Upcoming: list of scheduled events with date and matchups (fighter names linked)
  - Past: list of completed events with date, matchups, and results
    - Each past fight shows: fighter names, winner, method — click for narrative
  - Navigation: ability to browse past events (simple list, most recent first)
  - Optional: calendar-style view or date picker for jumping to specific dates

**Validation:** Schedule page shows upcoming events with correct fighter pairings. Past events show results. Clicking a past fight opens the narrative. Events are in chronological order. After running the backend for 14 days, there should be ~4 completed events and 1-2 upcoming events visible.

---

**Step 8: Polish + Responsive + Error States**
- 8.1: Add loading states for all data fetches (skeleton or spinner)
- 8.2: Add error states: "No data found — run the backend engine first" when data files don't exist
- 8.3: Add empty states: "No fights today", "No upcoming events", "No fight history yet"
- 8.4: Responsive design: ensure pages are usable on mobile (stack layouts, collapsible sections)
- 8.5: Verify all links work across the app: dashboard → fighter, dashboard → narrative, fighter → narrative, fighter → rival, rankings → fighter, schedule → narrative
- 8.6: Run `npm run build` — ensure clean production build with no TypeScript errors

**Validation:** Build succeeds. Navigate every page and every link. Loading states appear briefly. Error states display correctly when data is missing. The app looks clean on both desktop and a narrow mobile viewport. All inter-page navigation works correctly.
