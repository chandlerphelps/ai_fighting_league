# Frontend - Detailed File Summaries

Comprehensive documentation of frontend code.

## TABLE OF CONTENTS

1. [src/App.tsx](#srcapptsx)
2. [src/design-system.ts](#srcdesign-systemts)
3. [src/pages/Dashboard.tsx](#srcpagesdashboardtsx)
4. [src/pages/FighterProfile.tsx](#srcpagesfighterprofiletsx)
5. [src/pages/FightNarrative.tsx](#srcpagesfightnarrativetsx)
6. [src/pages/Rankings.tsx](#srcpagesrankingstsx)
7. [src/pages/Schedule.tsx](#srcpagesscheduletsx)
8. [src/pages/RosterManager.tsx](#srcpagesrostermanagertsx)
9. [src/components/Layout.tsx](#srccomponentslayouttsx)
10. [src/components/FightCard.tsx](#srccomponentsfightcardtsx)
11. [src/components/FighterLink.tsx](#srccomponentsfighterlinktsx)
12. [src/components/FighterPortrait.tsx](#srccomponentsfighterportraittsx)
13. [src/components/StatBar.tsx](#srccomponentsstattsx)
14. [src/components/InjuryBadge.tsx](#srccomponentsinjurybadgetsx)
15. [src/components/NoData.tsx](#srccomponentsnodatatsx)
16. [src/hooks/useData.ts](#srchooksusedatats)
17. [src/lib/data.ts](#srclibdatats)
18. [src/lib/images.ts](#srclibimagests)
19. [src/lib/api.ts](#srclibapits)
20. [src/types/fighter.ts](#srctypesfighterts)
21. [src/types/match.ts](#srctypesmatchts)
22. [src/types/event.ts](#srctypeseventts)
23. [src/types/world_state.ts](#srctypesworld_statets)

---

## src/App.tsx
File: src/App.tsx
File Length: 23 lines
Purpose: Root component with React Router route definitions.

Artefacts
- App - Routes: / (Dashboard), /fighter/:id (FighterProfile), /rankings (Rankings), /schedule (Schedule), /match/:id (FightNarrative), /roster (RosterManager)

---

## src/design-system.ts
File: src/design-system.ts
File Length: 64 lines
Purpose: Dark theme design tokens for colors, fonts, font sizes, and spacing.

Artefacts
- colors - dark theme palette: background, surface, text, accent (gold), semantic colors (healthy, injured, win, loss, draw, stat tiers, etc.)
- withAlpha(hex, alpha) - converts hex color to rgba string with given alpha
- fonts - monospace font stacks for body and heading
- fontSizes - xs through xxxl rem values
- spacing - xs through xxl pixel values

---

## src/pages/Dashboard.tsx
File: src/pages/Dashboard.tsx
File Length: 216 lines
Purpose: League overview showing current day, today's fights, roster health, next event, and recent results.

Artefacts
- Dashboard - loads worldState and fighters; fetches today's completed event, next upcoming event, and 5 most recent matches
- Sections: day/date header, today's fights (FightCard), roster health (active/injured counts with FighterLink + InjuryBadge), next event, recent results with portraits and outcome badges

---

## src/pages/FighterProfile.tsx
File: src/pages/FighterProfile.tsx
File Length: 308 lines
Purpose: Full fighter profile with expandable tiered image viewer, stats, record, fight history, storyline, and rivalries.

Artefacts
- FighterProfile - loads fighter by URL param, fetches fight history and rival fighters
- TIERS = ['sfw', 'barely', 'nsfw', 'body_ref'] - image tier cycling with keyboard arrows and click
- Sections: header with FighterPortrait, expandable image viewer with tier tabs, physical description, stats (StatBar), record (W-L-D), condition/injuries, fight history with result indicators and narrative links, storyline log, rivalries

---

## src/pages/FightNarrative.tsx
File: src/pages/FightNarrative.tsx
File Length: 203 lines
Purpose: Full fight narrative page showing matchup analysis, stat comparison, key moments, and post-fight updates.

Artefacts
- FightNarrative - loads match by URL param, displays fighter matchup header
- StatSnapshot - sub-component showing stats for one fighter with winner highlight
- Sections: outcome banner (winner/draw/method), key matchup factors, stat comparison (2-column), key moments with attacker highlighting, post-fight updates

---

## src/pages/Rankings.tsx
File: src/pages/Rankings.tsx
File Length: 166 lines
Purpose: Ranked fighter table with record, streak, and recent form indicators.

Artefacts
- Rankings - loads worldState, all fighters, all matches; displays ranked table sorted by worldState.rankings
- getStreak(matches, fighterId) - computes current win/loss streak string (e.g. "W3")
- getRecentForm(matches, fighterId, count) - returns last N results as W/L/D array

---

## src/pages/Schedule.tsx
File: src/pages/Schedule.tsx
File Length: 95 lines
Purpose: Upcoming and past events with fight cards.

Artefacts
- Schedule - loads all events, splits into upcoming (sorted asc) and past (sorted desc), renders each with FightCard
- Past events include optional event summary text

---

## src/pages/RosterManager.tsx
File: src/pages/RosterManager.tsx
File Length: 1797 lines
Purpose: Admin page for managing roster: view/edit/delete fighters, generate new fighters, regenerate character/outfits/images, manage outfit options.

Artefacts
- RosterManager - loads all fighters via loadAllFighterFiles, manages expanded/editing state per fighter
- Fighter editing: inline edit form for ring_name, real_name, age, origin, personality, build, distinguishing_features, image prompt body_parts/expression/pose
- Generation: GeneratePanel sub-component with archetype/gender/origin/concept fields, calls generateFighter API
- Regeneration: character, outfits (with tier/skimpiness selection), images (with tier selection), individual move images
- Task polling: tracks active async tasks via pollUntilDone, shows progress indicators
- Outfit options manager: fetch/edit/save outfit_options.json via API
- Image viewer: tiered image display (SFW/BARELY/NSFW/BODY_REF) per fighter, move image display per move per tier

---

## src/components/Layout.tsx
File: src/components/Layout.tsx
File Length: 76 lines
Purpose: App shell with top navigation bar and content area.

Artefacts
- Layout - nav bar with AFL logo, links (Dashboard, Rankings, Schedule, Roster), league date; max-width 1200px content area

---

## src/components/FightCard.tsx
File: src/components/FightCard.tsx
File Length: 78 lines
Purpose: Displays fight matchups for an event with results and narrative links.

Artefacts
- FightCard({ matches: EventMatch[] }) - renders fighter vs fighter rows with portraits, winner highlighting, method badge, and "Read" link to narrative

---

## src/components/FighterLink.tsx
File: src/components/FighterLink.tsx
File Length: 23 lines
Purpose: Fighter name as link to their profile page.

Artefacts
- FighterLink({ id, name, record? }) - Link to /fighter/:id, optionally showing W-L-D record

---

## src/components/FighterPortrait.tsx
File: src/components/FighterPortrait.tsx
File Length: 54 lines
Purpose: Fighter thumbnail image with fallback to initial letter.

Artefacts
- FighterPortrait({ fighterId, name, size }) - loads SFW image via fighterImagePath, falls back to styled initial on error

---

## src/components/StatBar.tsx
File: src/components/StatBar.tsx
File Length: 63 lines
Purpose: Horizontal stat bar with name, value, and colored fill.

Artefacts
- StatBar({ name, value }) - renders stat name, numeric value, and colored bar (statLow/statMid/statHigh based on thresholds)

---

## src/components/InjuryBadge.tsx
File: src/components/InjuryBadge.tsx
File Length: 28 lines
Purpose: Inline injury indicator showing days remaining.

Artefacts
- InjuryBadge({ daysRemaining }) - red-tinted badge showing "X days" recovery time

---

## src/components/NoData.tsx
File: src/components/NoData.tsx
File Length: 29 lines
Purpose: Fallback message when no data is available.

Artefacts
- NoData - displays "Run the backend first" message with instructions

---

## src/hooks/useData.ts
File: src/hooks/useData.ts
File Length: 83 lines
Purpose: Generic data loading hook and typed convenience hooks for all data entities.

Artefacts
- useDataLoader<T>(loader, deps) - generic hook managing loading/data/error state with cancellation
- useWorldState() / useFighter(id) / useAllFighters() / useMatch(id) / useAllMatches() / useEvent(id) / useAllEvents() - typed hooks wrapping useDataLoader

---

## src/lib/data.ts
File: src/lib/data.ts
File Length: 79 lines
Purpose: Fetch-based loaders for all data types from /data/ JSON files.

Artefacts
- fetchJson<T>(url) - generic fetch with error handling returning null on failure
- loadWorldState / loadFighter(id) / loadAllFighters / loadAllFighterFiles / loadMatch(id) / loadAllMatches / loadEvent(id) / loadAllEvents - data loaders fetching from /data/ directory

---

## src/lib/images.ts
File: src/lib/images.ts
File Length: 15 lines
Purpose: Image path construction for fighter charsheets and move images.

Artefacts
- slugify(name) - lowercase alphanumeric slug
- fighterImagePath(fighterId, ringName, tier) - returns /data/fighters/{id}_{slug}_{tier}.png
- moveImagePath(fighterId, ringName, moveIndex, tier) - returns /data/fighters/{id}_{slug}_move{N}_{tier}.png

---

## src/lib/api.ts
File: src/lib/api.ts
File Length: 151 lines
Purpose: API client for backend REST endpoints used by RosterManager.

Artefacts
- apiFetch<T>(url, options) - generic fetch wrapper with error handling against /api base
- fetchAllFighters / fetchFighter(id) / updateFighter(id, updates) / deleteFighter(id) - fighter CRUD
- generateFighter(options) / regenerateCharacter(id, options) / regenerateOutfits(id, options) / regenerateImages(id, options) / regenerateMoveImage(id, moveIndex, tier) - async task-based generation endpoints
- pollTask(taskId) / pollUntilDone(taskId, onPoll) - task status polling with 2s interval, 120 attempt max
- fetchOutfitOptions / saveOutfitOptions(options) / fetchArchetypes - config endpoints

---

## src/types/fighter.ts
File: src/types/fighter.ts
File Length: 81 lines
Purpose: TypeScript interfaces for fighter data model.

Artefacts
- Stats - power, speed, technique, toughness, supernatural
- Record - wins, losses, draws, kos, submissions
- Injury / Condition - health status and injury tracking
- CharsheetPrompt - style, layout, body_parts, clothing, front_view, center_pose, back_view, expression, full_prompt
- Move - name, description, stat_affinity, image_snapshot
- Fighter - full fighter interface with image_prompt_body_ref (optional CharsheetPrompt), image_prompt/sfw/nsfw, moves, rivalries, _available_images

---

## src/types/match.ts
File: src/types/match.ts
File Length: 45 lines
Purpose: TypeScript interfaces for match data model.

Artefacts
- FightMoment - moment_number, description, attacker_id, action, image_prompt, image_path
- MatchupAnalysis - fighter win probs, methods, key_factors
- MatchOutcome - winner_id, loser_id, method, round_ended, performances, injuries, is_draw
- Match - full match with fighters, analysis, outcome, narrative, moments, snapshots, post_fight_updates

---

## src/types/event.ts
File: src/types/event.ts
File Length: 19 lines
Purpose: TypeScript interfaces for event data model.

Artefacts
- EventMatch - match_id, fighter1/2 IDs and names, completed, winner_id, method
- Event - id, date, name, matches, completed, summary

---

## src/types/world_state.ts
File: src/types/world_state.ts
File Length: 21 lines
Purpose: TypeScript interfaces for world state data model.

Artefacts
- RivalryRecord - fighter1/2_id, fights, wins, draws, is_rivalry
- WorldState - current_date, day_number, rankings, upcoming/completed_events, active_injuries, rivalry_graph, last_daily_summary, event_counter
