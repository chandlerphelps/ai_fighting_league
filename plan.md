# Match Summary Page — Design Plan

## NBA Gamecast Inspiration — Key Elements Adapted

From the ESPN NBA gamecast screenshot, the design patterns I'm adapting:

| NBA Element | Our Adaptation |
|---|---|
| Team logos + names flanking score | Fighter portraits + names flanking result badge |
| "FINAL" status + quarter scores | "FINAL" + round-by-round HP timeline |
| Tab bar (Summary/Box Score/etc) | Tab bar (Summary / Replay) — Replay is future |
| Play-by-play key moments | Key fight moments with AI-generated snapshot images |
| Player stat leaders | Fighter stat comparison (power/speed/technique/etc) |
| Score timeline graph | HP over time graph per round |

## Page Layout

### 1. Fight Header (top, full-width)
Inspired by NBA's scoreboard header:

```
┌─────────────────────────────────────────────────────────┐
│  [Tier Logo] APEX TIER  •  Season 3 — Month 4          │
│                                                         │
│   ┌──────┐                              ┌──────┐       │
│   │ F1   │   IRON EMPRESS              │  F2  │       │
│   │ img  │     12-3-0                    │ img  │       │
│   │      │                              │      │       │
│   └──────┘                              └──────┘       │
│              COBRA KISS                                  │
│                8-5-1                                     │
│                                                         │
│          ┌─────────────────────┐                        │
│          │   KO  •  ROUND 2   │                        │
│          │      FINAL         │                        │
│          └─────────────────────┘                        │
│                                                         │
│   Winner name highlighted green, loser in muted red     │
└─────────────────────────────────────────────────────────┘
```

- Large fighter portraits (120px) on left and right
- Names in large font, winner highlighted in `colors.win`
- Result badge centered: method colored by type (KO=orange, SUB=purple, DEC=blue)
- Records shown under names
- Tier logo + label at top

### 2. Tab Bar
```
[ Summary ]  [ Replay ]
```
- Summary active by default, Replay grayed out / coming soon
- Sticky below header

### 3. Summary Content — Two Column Layout

#### Left Column (wider, ~65%)

**Round-by-Round HP Chart**
- Simple visual showing HP depletion per round
- Two horizontal bars per round (one per fighter), shrinking from 100%
- Color: winner's bar stays greener, loser's bar turns redder

**Key Moments Timeline**
- Vertical timeline of `FightMoment[]` entries
- Each moment card shows:
  - Round number badge on the left edge
  - Large snapshot image (from `image_path` / `image_prompt`) — this is the hero visual
  - Action description text
  - Damage dealt indicator
  - Attacker/defender names
- Moments with images get large cards (like NBA highlight plays)
- Moments without images get compact text rows

**Fight Narrative**
- Full AI narrative text in a styled card
- Collapsible if long

#### Right Column (~35%)

**Pre-Fight Analysis**
- Win probability bar (e.g., 65% vs 35%)
- Key factors list
- Predicted finish methods

**Fighter Stats Comparison**
- Side-by-side stat bars for both fighters (from snapshots)
- Power, Speed, Technique, Toughness, Supernatural
- Using existing `StatBar` component pattern

**Fight Impact**
- Injuries sustained (with InjuryBadge)
- Performance ratings
- Post-fight stat changes

## Files to Create/Modify

1. **`src/pages/MatchSummary.tsx`** — New page component (the main page)
2. **`src/hooks/useData.ts`** — Add `useMatch(id)` hook
3. **`src/lib/data.ts`** — Add `loadMatch(id)` function
4. **`src/types/match.ts`** — Extend `FightMoment` with missing fields (round_number, HP, stamina, emotions, damage, etc.)
5. **`src/App.tsx`** — Add `/match/:id` route

## Implementation Order

1. Extend types to include all FightMoment fields from backend
2. Add data loading for matches
3. Build the page component with mock/real data
4. Wire up routing
