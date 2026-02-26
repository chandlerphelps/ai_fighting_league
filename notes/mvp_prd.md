# AI Fighting League — MVP (v0) Product Requirements Document

## 1. Product Goal

A two-part system:

**Backend** — A Python engine that can:
1. Generate a roster of fighters with stats, backstories, abilities, and (for some) light supernatural traits
2. Auto-generate fight cards and simulate fights, producing text narratives
3. Update fighter records, stats, and personal storylines as a consequence of fights
4. Progress the league state day-by-day through an auto-generated schedule of fights

**Frontend** — A simple TypeScript web app that can:
1. Display today's fight card and results with full narratives
2. Browse fighter profiles — stats, records, backstory, fight history, storyline log
3. Show current rankings
4. Show upcoming schedule and recent results
5. Navigate between days to review past events

The core loop is: **generate fighters → schedule fights → fight → narrate → update state → repeat**. The frontend is a read-only viewer into that loop — no fan economy, no interactions beyond browsing. It exists so you can see the engine working and verify it's producing good output.

AI calls go through OpenRouter so we can swap models freely.

---

## 2. Core Requirements (Can't Ship Without)

### 2.1 Fighter Generation

A fighter must have:
- **Identity**: Ring name, real name, age, origin, alignment (face/heel/tweener)
- **Physical description**: Height, weight, build, distinguishing features, ring attire
- **Backstory**: Origin story, motivation, personality traits, fears/quirks (2-3 paragraphs)
- **Fighting style**: Primary style, secondary style, signature move, finishing move, known weaknesses
- **Stats** (1-100 scale, grouped):
  - *Physical*: Strength, Speed, Endurance, Durability, Recovery
  - *Combat*: Striking, Grappling, Defense, Fight IQ, Finishing Instinct
  - *Psychological*: Aggression, Composure, Confidence, Resilience, Killer Instinct
  - *Supernatural* (optional, most fighters have 0): Arcane Power, Chi Mastery, Elemental Affinity, Dark Arts — light touch only. A fighter might have 1-2 of these at modest levels (20-50). These flavor the narrative (a chi monk's strikes glow faintly, a dark arts practitioner unsettles opponents) but don't overpower the fundamentals.
- **Record**: Wins, losses, draws, KOs, submissions (starts at 0-0-0)
- **Current condition**: Health status, injuries (starts healthy), morale/momentum

Archetype templates (The Prodigy, The Veteran, The Monster, The Technician, The Wildcard, The Mystic, The Survivor, The Seductress/Seductor) can guide generation but fighters should feel unique.

**Roster size for v0**: ~16 fighters. At least 2-3 should have light supernatural traits. The rest are grounded.

**Generation method**: AI-generated via prompt through OpenRouter, with the engine providing archetype guidance and stat balance constraints. Stats should be balanced — no fighter should be elite at everything. Total stat points should fall within a defined band to ensure competitive balance.

---

### 2.2 Match Simulation (The Fight Engine)

Three-phase pipeline — this is the heart of the product:

**Phase 1 — Probability Calculation (AI-driven)**
- Input: Both fighters' full profiles, current condition, recent form, any rivalry context, supernatural traits if applicable
- Output: Win probability for each fighter (clamped 5%-95%), most likely victory methods, key matchup factors
- This is an AI call (via OpenRouter) that reasons about the matchup
- Supernatural abilities should be factored in as an edge, not a dominator

**Phase 2 — Outcome Determination (Deterministic / Random Roll)**
- Weighted random roll using Phase 1 probabilities to determine:
  - **Winner**
  - **Method**: KO/TKO, Submission, Decision (Unanimous/Split), or Draw
  - **Round** the fight ends (for finishes) — fights are 3 rounds by default
  - **Performance quality** for each fighter (dominant, competitive, poor, etc.)
  - **Injuries**: Any injuries sustained (none, minor, moderate, severe) — rolled with probability influenced by fight intensity and method
- No AI involved here — purely mechanical to keep outcomes honest

**Phase 3 — Narrative Generation (AI-driven)**
- Input: Both fighter profiles, the determined outcome from Phase 2, matchup analysis from Phase 1
- Output: A structured text narrative including:
  - Brief pre-fight scene setting (1 paragraph)
  - Round-by-round action (key moments, momentum shifts, signature moves used)
  - Supernatural flavor woven in naturally where applicable (not every exchange, just key moments)
  - The finish (or decision reading if it goes the distance)
  - Post-fight immediate aftermath (winner's reaction, loser's state, any story hooks for future)
- Written in exciting, dramatic prose — this IS the product for now
- Should reference each fighter's actual moves, personality, and style
- Target length: ~800-1500 words per fight

---

### 2.3 Post-Fight Updates (Consequences)

After every fight, the following must be updated:

- **Win/Loss record** for both fighters
- **Stats adjustments**: Small shifts based on performance (e.g., confidence goes up after a dominant win, composure drops after getting KO'd). Changes should be small (+/- 1-3 points) and logical. Supernatural stats stay fixed for now (they're innate, not trained).
- **Condition updates**: Apply any injuries from Phase 2. Injured fighters need recovery time and can't fight until healed. Minor = 1 week, Moderate = 2-4 weeks, Severe = 6-8 weeks.
- **Fighter storyline update**: A short paragraph appended to the fighter's ongoing story log. Captures what this fight meant for them narratively — building confidence, a humbling loss, a rivalry ignited, etc.
- **Rivalry/relationship tracking**: If two fighters have fought, record the history. Repeat matchups should be flagged as rivalries and this context should feed into future fight narratives.

---

### 2.4 Auto-Generated Matchmaking

The engine generates fight cards without manual intervention:

- **Inputs**: Current rankings, fighter availability (not injured), fight history, rivalry flags
- **Logic**:
  - Prefer matchups between similarly ranked fighters
  - Boost priority for active rivalries (fighters who have split previous bouts or had close fights)
  - Avoid immediate rematches (minimum 2 weeks between the same pairing)
  - Ensure all healthy fighters get regular rotation (no one sits idle for more than 2 weeks)
- **Output**: A fight card of 2-3 bouts for each event
- No manual approval needed — the engine runs autonomously

---

### 2.5 League State & Day-to-Day Progression

- **Rankings**: Simple ordered ranking based on record and recent performance. #1 is the top-ranked fighter. Updated after each fight.
- **Schedule**: Auto-generated weekly event cadence — 2-3 fights per event, ~2 events per week.
- **Daily tick**: The engine advances one day at a time:
  - Check if there's an event scheduled today → if yes, run the fights
  - Process injury recovery (decrement recovery timers)
  - Update rankings if fights occurred
  - Generate next event if the schedule is empty for the coming week
  - Output a "daily summary" of what happened
- **World state snapshot**: At any point, you should be able to see the current state — all fighter records, rankings, upcoming schedule, active injuries, recent storyline beats.

---

### 2.6 Basic Web Frontend (Viewer)

A simple TypeScript web app — read-only, no user interactions beyond navigation. Its purpose is to make the backend's output human-readable and verify the engine is producing good results.

**Pages / Views:**

1. **Dashboard / Today**
   - Current league date
   - Today's fight card (if any) with results and links to full narratives
   - Quick roster health overview (who's injured, who's active)
   - Next upcoming event

2. **Fight Narrative View**
   - Full text narrative for a specific fight
   - Fighter stats side-by-side at time of fight
   - Outcome summary (winner, method, round)
   - Post-fight stat changes and storyline updates shown

3. **Fighter Profile**
   - Full profile: identity, physical description, backstory, fighting style
   - Current stats (with recent changes highlighted)
   - Win/loss record with fight history (links to each fight narrative)
   - Current condition (healthy / injured + recovery timeline)
   - Storyline log — chronological story beats for this fighter
   - Rivalries list

4. **Rankings**
   - Ordered list of all fighters by current ranking
   - Record, streak, recent form indicator
   - Injured fighters marked

5. **Schedule / History**
   - Upcoming scheduled events
   - Past events with results (navigate by date)

**Technical approach:**
- Static site or simple SPA that reads from the JSON data files
- No backend API needed for v0 — the frontend reads the same `/data/` files the Python engine writes
- Could be as simple as a Next.js/Vite app that imports JSON at build time or reads via local file server
- Styling should be minimal but clean — dark theme preferred to match the league aesthetic
- No images needed — text and stats only

---

## 3. Explicitly Out of Scope for v0

- Image/art generation of any kind (no fighter portraits, fight scene art, etc.)
- Fan economy (sponsorships, investments, shares)
- Non-fight narrative beats (training montages, backstage drama, press conferences)
- NPC characters (The Siren, The Resurrectionist, etc.)
- Heavy supernatural (no reality-warping, resurrection, or supernatural-dominated fights)
- Death mechanics
- Multiple match types (only standard 3-round fights)
- Tournament structures
- Title belts / championship system
- Event hierarchy (weekly vs. PPV distinction)
- Commentary system
- Video or animation
- User accounts or authentication
- Any fan-facing interactive features

---

## 4. Data Model (v0)

File-based JSON storage. Clean schemas that both the Python backend writes and the TypeScript frontend reads.

```
/data/
  /fighters/         # One JSON file per fighter (full profile + history + story log)
  /matches/          # One JSON file per match (outcome + narrative)
  /events/           # One JSON file per event (fight card, date, results)
  /world_state.json  # Current rankings, schedule, date, active injuries, rivalry graph
```

No database. Just JSON files. The schemas serve as the contract between backend and frontend — both systems agree on the shape of the data.

---

## 5. Success Criteria

v0 is "done" when:

1. We can generate a 16-fighter roster where each fighter feels distinct and interesting, including 2-3 with light supernatural traits
2. We can run any matchup and get a compelling ~800-1500 word fight narrative
3. Fighter records and stats update correctly after fights
4. Injuries heal over time and prevent fighters from competing while hurt
5. The engine auto-generates sensible fight cards without manual input
6. We can advance the league day-by-day and see a coherent progression of events
7. Rivalries emerge naturally from repeated matchups and are reflected in narratives
8. Running the engine is a single command — `python run_day.py` (or similar) advances the world one day
9. The web frontend shows today's results, lets you browse any fighter's profile and history, and lets you navigate through past events
10. All data is in clean JSON files shared between backend and frontend

---

## 6. Open Questions

- **Narrative length/detail**: Target is ~800-1500 words. Should we offer a "quick recap" mode (~200 words) alongside the full narrative for catching up?
- **Stat evolution speed**: Stats change +/- 1-3 per fight. Over a 10-fight stretch, should a fighter's profile feel noticeably different, or should drift be very slow?
- **Roster expansion**: When/how do new fighters enter the league after the initial 16? Save for v1?
- **Model selection**: Which OpenRouter model(s) to start with for probability and narrative? Claude for reasoning, a different model for creative writing, or same model for both?
- **Frontend framework**: Next.js, Vite + React, or something simpler? Depends on preference and how the data serving works.
