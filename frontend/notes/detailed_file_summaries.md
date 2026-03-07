# Frontend - Detailed File Summaries

Comprehensive documentation of frontend code.

## TABLE OF CONTENTS

1. [src/App.tsx](#srcapptsx)
2. [src/design-system.ts](#srcdesign-systemts)
3. [src/pages/Home.tsx](#srcpagehometsx)
4. [src/pages/FighterProfile.tsx](#srcpagesfighterprofiletsx)
5. [src/pages/MatchSummary.tsx](#srcpagesmatchsummarytsx)
5b. [src/pages/FightReplay.tsx](#srcpagesfightreplaytsx)
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
16. [src/components/DirtyWarning.tsx](#srccomponentsdirtywarningtsx)
17. [src/components/PlanView.tsx](#srccomponentsplanviewtsx)
18. [src/components/StageFilter.tsx](#srccomponentsstagefiltertsx)
19. [src/hooks/useData.ts](#srchooksusedatats)
20. [src/lib/data.ts](#srclibdatats)
21. [src/lib/images.ts](#srclibimagests)
22. [src/lib/api.ts](#srclibapits)
23. [src/types/fighter.ts](#srctypesfighterts)
24. [src/types/match.ts](#srctypesmatchts)
25. [src/types/event.ts](#srctypeseventts)
26. [src/types/world_state.ts](#srctypesworld_statets)

---

## src/App.tsx
File: src/App.tsx
File Length: 23 lines
Purpose: Root component with React Router route definitions.

Artefacts
- App - Routes: / (Home), /rankings (Rankings), /roster (RosterManager), /match/:matchKey (MatchSummary which embeds FightReplay)

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

## src/pages/Home.tsx
File: src/pages/Home.tsx
File Length: 216 lines
Purpose: League overview showing current day, today's fights, roster health, next event, and recent results.

Artefacts
- Home - loads worldState and fighters; fetches today's completed event, next upcoming event, and 5 most recent matches
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

## src/pages/MatchSummary.tsx
File: src/pages/MatchSummary.tsx
File Length: ~300 lines
Purpose: Match summary page showing fight overview with stat comparison, outcome, and embedded fight replay. Replaces the old FightNarrative page.

Artefacts
- MatchSummary - loads match by URL param (matchKey), displays fighter matchup with portraits, stat comparison, outcome banner, tier logo, and embeds FightReplay component
- StatSnapshot - sub-component showing stats for one fighter with winner highlight using getStatColor
- formatTime/formatDate - helpers for display formatting
- TIER_LOGOS/TIER_LABELS - maps tier names to logo image paths and display labels
- Sections: fight card header with tier badge and time, fighter portraits with links, stat comparison (6 stats), outcome banner with method, embedded FightReplay

---

## src/pages/FightReplay.tsx
File: src/pages/FightReplay.tsx
File Length: ~993 lines
Purpose: Interactive animated fight replay with tick-by-tick combat playback.

Artefacts
- FightReplay - main component. Accepts a MatchResult and both Fighter objects. Generates mock fight moments from match outcome data, then animates them in sequence.
- generateMockMoments(match) - creates synthetic FightMoment array from match result (round-by-round, with HP tracking, damage, blocks, misses, finishers)
- DAMAGE_VERBS/BLOCK_VERBS/MISS_VERBS - random verb pools for event descriptions
- METHOD_COLORS/METHOD_LABELS - maps finish methods to colors and display text
- Animated playback: auto-advances through moments with configurable speed, shows HP bars, round counter, event log with attacker/defender highlights, position indicators (standing/clinch/ground), finish animation on final moment

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
File Length: 2053 lines
Purpose: Admin page for 3-stage roster initialization pipeline and fighter management. Stage-based workflow: plan (AI roster planning) -> stage 1 (JSON generation) -> stage 2 (portrait) -> stage 3 (full charsheets). View/edit/delete fighters, regenerate character/outfits/images, manage outfit options.

Artefacts
- RosterManager - loads all fighters via API, manages expanded/editing state per fighter, integrates PlanView, StageFilter, and DirtyWarning components
- 3-stage pipeline: PlanView for roster planning -> batch generation to stage 1 -> advance-stage to stage 2 (portrait) -> advance-stage to stage 3 (charsheets)
- StageFilter tabs: All, Plan, Stage 1 (JSON), Stage 2 (Portrait), Stage 3 (Ready) with fighter counts
- Fighter editing: inline edit form for ring_name, real_name, age, origin, personality, build, distinguishing_features, iconic_features, primary_outfit_color, hair_style, hair_color, face_adornment, image prompt body_parts/expression/pose
- DirtyWarning: shows invalidated downstream artifacts (outfits, image_prompts, images) with regen buttons
- Generation: GeneratePanel sub-component with archetype/gender/origin/concept fields, calls generateFighter API; roster plan creation with count/gender_mix
- Regeneration: character, outfits (with tier/skimpiness selection), images (with tier selection), individual move images
- Batch operations: advance multiple fighters to stage 2 or 3, pool summary display
- Task polling: tracks active async tasks via pollUntilDone, shows progress indicators
- Outfit options manager: fetch/edit/save outfit_options.json via API
- Image viewer: tiered image display (SFW/BARELY/NSFW/BODY_REF/PORTRAIT) per fighter, move image display per move per tier

---

## src/components/Layout.tsx
File: src/components/Layout.tsx
File Length: 76 lines
Purpose: App shell with top navigation bar and content area.

Artefacts
- Layout - nav bar with AFL logo, links (Home, Rankings, Roster), league date; max-width 1200px content area

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

## src/components/DirtyWarning.tsx
File: src/components/DirtyWarning.tsx
File Length: 75 lines
Purpose: Inline warning banner showing which downstream artifacts are invalidated after fighter field edits, with regeneration action buttons.

Artefacts
- DirtyWarning({ dirty, onRegenerateOutfits, onRegenerateImages }) - renders warning banner listing outdated items (outfits, image prompts, images) with optional "Regen Outfits" and "Regen Images" buttons; returns null if no dirty items

---

## src/components/PlanView.tsx
File: src/components/PlanView.tsx
File Length: 411 lines
Purpose: Roster plan management UI for reviewing, editing, approving, and generating fighters from AI-created roster plans.

Artefacts
- PlanView({ plan, onPlanChange, onTask, onError }) - displays roster plan with entry count, approve all, add more, generate approved, discard pending controls; shows pool summary in collapsible details; renders plan entries as a grid of cards with approve/edit/reroll/remove actions
- PlanCardContent({ entry, index, statusColor }) - renders plan entry card content: ring name, gender, archetype/subtype, origin, concept hook, power tier, and signature visual identity badges (outfit color, hair style+color, face adornment)
- PlanEntryEditor({ data, onChange, onSave, onCancel }) - inline edit form for plan entry fields (ring name, gender, origin, archetype, subtype, concept hook, power tier, outfit color, hair style, hair color, face adornment)

---

## src/components/StageFilter.tsx
File: src/components/StageFilter.tsx
File Length: 70 lines
Purpose: Tab bar for filtering fighters by generation stage in the roster manager.

Artefacts
- StageTab - type union: 'all' | 'plan' | 'stage1' | 'stage2' | 'stage3'
- StageFilter({ fighters, hasPlan, planCount, activeTab, onTabChange }) - renders tab buttons with counts for each stage (All, Plan, Stage 1: JSON, Stage 2: Portrait, Stage 3: Ready)
- filterByStage(fighters, tab) - filters fighter array by generation_stage matching the selected tab

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
File Length: 217 lines
Purpose: API client for backend REST endpoints used by RosterManager. Covers fighter CRUD, generation pipeline, roster plan management, and stage advancement.

Artefacts
- apiFetch<T>(url, options) - generic fetch wrapper with error handling against /api base
- fetchAllFighters / fetchFighter(id) / updateFighter(id, updates) / deleteFighter(id) - fighter CRUD
- generateFighter(options) / regenerateCharacter(id, options) / regenerateOutfits(id, options) / regenerateImages(id, options) / regenerateMoveImage(id, moveIndex, tier) - async task-based generation endpoints
- pollTask(taskId) / pollUntilDone(taskId, onPoll) - task status polling with 2s interval, 120 attempt max
- fetchOutfitOptions / saveOutfitOptions(options) / fetchArchetypes - config endpoints
- fighterImageUrl(fighterId, tier) / fighterPortraitUrl(fighterId) - image URL builders
- fetchRosterPlan / createRosterPlan(count, mode, gender_mix) / deleteRosterPlan - roster plan lifecycle
- updatePlanEntry(index, updates) / deletePlanEntry(index) / regeneratePlanEntry(index) / addPlanEntries(count) - plan entry CRUD
- generateFromPlan() - batch generate fighters from approved plan entries
- advanceStage(fighterId) / batchAdvance(fighterIds, targetStage) - stage advancement (1->2->3)
- fetchPoolSummary() - get fighter pool summary stats

---

## src/types/fighter.ts
File: src/types/fighter.ts
File Length: 138 lines
Purpose: TypeScript interfaces for fighter data model, roster plan entries, and roster plan structure.

Artefacts
- Stats - power, speed, technique, toughness, supernatural
- Record - wins, losses, draws, kos, submissions
- Injury / Condition - health status and injury tracking
- CharsheetPrompt - style, layout, body_parts, clothing, front_view, center_pose, back_view, expression, full_prompt
- Move - name, description, stat_affinity, image_snapshot
- TierRecord - wins, losses, draws per tier
- PlanEntry - roster plan entry with ring_name, gender, primary_archetype, subtype, has_supernatural, concept_hook, power_tier, signature visual identity (primary_outfit_color, hair_style, hair_color, face_adornment), status (pending/approved/rejected/generating), fighter_id
- RosterPlan - plan_id, created_at, mode, pool_summary, entries array
- Fighter - full fighter interface with image_prompt_body_ref/portrait/sfw/nsfw (CharsheetPrompt), signature visual identity fields, generation_stage (0-3), generation_dirty list, moves, rivalries, tier_records, _available_images

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
