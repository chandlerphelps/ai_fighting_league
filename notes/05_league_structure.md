# League Structure - Rankings & Events

## Overview

The AFL needs a structured competitive framework that serves two purposes:
1. **Competitive legitimacy**: Rankings and titles that feel meaningful
2. **Story engine**: The structure itself generates narratives (title chases, rivalries, tournament drama)

The structure borrows from UFC's competitive framework but adds WWE's theatrical event
hierarchy and fighting game tournament formats.

> **Design Note**: AFL has **no weight classes**. This is a fantasy league where a 112 lb chi
> monk can face a 278 lb cartel enforcer. Size differences are reflected in stats (Strength,
> Size, Reach, Durability, etc.) and factor into the match engine's probability calculations,
> but they don't restrict matchmaking. This creates inherently dramatic matchups and lets
> narrative drive who fights whom, not arbitrary weight limits.

---

## Ranking System

### League Rankings

The league maintains a single unified ranking:
- **Champion**: The belt holder
- **Ranked #1-10**: Contenders with official rankings
- **Unranked**: Active fighters not yet in the top 10
- **Prospects**: New fighters building their record
- **Gatekeepers**: Experienced fighters who test up-and-comers

### How Rankings Change

Rankings update after every fight card based on:

| Factor | Weight | Description |
|---|---|---|
| **Win/Loss** | High | Winning moves you up, losing moves you down |
| **Opponent Quality** | High | Beating a #3 ranked fighter matters more than beating an unranked one |
| **Method of Victory** | Medium | Finishes are worth more than decisions |
| **Dominance** | Medium | A one-sided destruction moves you up faster |
| **Recency** | Medium | Recent results matter more than old ones |
| **Activity** | Low | Inactive fighters slowly drift down |
| **Streak** | Medium | Win/loss streaks amplify movement |

### Title Fights

- The champion defends against the #1 contender (or a compelling challenger the story demands)
- Champions must defend within 90 days or risk being stripped
- Interim titles can be created if the champion is injured/unavailable for 90+ days
- Title fights are always 5 rounds
- Title changes are major narrative events with weeks of buildup

---

## Event Hierarchy

### Weekly Shows: "The Circuit"

The bread-and-butter content. 1-2 events per week featuring:

- 4-6 fights per card
- Mix of ranked and unranked bouts
- Story segments between fights (backstage, interviews, confrontations)
- At least one fight with meaningful ranking implications
- Prospects and new debuts get showcased here

### Bi-Weekly Major Cards: "Prime Time"

Bigger events with higher stakes:

- 6-8 fights per card
- At least one title fight or #1 contender bout
- Main event is always a significant matchup
- Multiple ongoing storylines converge
- Higher production value in narratives

### Monthly Special Events

Themed events that shake up the status quo:

| Event | Format | Description |
|---|---|---|
| **The Gauntlet** | Tournament bracket | 8-fighter single-elimination, one night |
| **The Crucible** | Special match type | Enhanced danger, environmental hazards |
| **Grudge Night** | All rivalry matches | Every fight on the card is a personal beef |
| **Fresh Blood** | Debut showcase | 4-6 new fighters debut in one event |
| **The Challenge** | Open challenges | Champions accept any challenger |
| **Dark Night** | Supernatural focus | Matches emphasize supernatural abilities |
| **Legacy Night** | Tribute event | Honoring retired/fallen fighters, legacy matches |

### Quarterly Mega-Events (The "PPVs")

These are the tent-pole events that seasons build toward. Each has a unique identity:

| Event | Season | Theme |
|---|---|---|
| **Genesis** | Q1 (Jan) | New beginnings, debut of the year's major storylines |
| **Inferno** | Q2 (Apr) | Peak chaos, multiple title fights, high death-match risk |
| **The Reckoning** | Q3 (Jul) | Grudge matches, story climaxes, scores settled |
| **Ascension** | Q4 (Oct) | Year-end event, crowning moments, legacy-defining fights |

Each mega-event features:
- 8-10 fights across the roster
- 2-3 title fights
- At least one special match type (death match, Blood Pact, etc.)
- The culmination of 2-3 major story arcs
- New major storylines launched in the aftermath

---

## Tournament Formats

Tournaments are special competitive structures used for specific events:

### Single Elimination
- 8 or 16 fighters
- Win or go home
- Can be single-night (3 fights per winner) or spread over weeks
- Creates bracket drama, cinderella stories, and cumulative damage narratives

### Round Robin
- 4-6 fighters
- Everyone fights everyone
- Best record wins, tiebreakers by head-to-head then method of victory
- Good for establishing roster hierarchy

### King of the Hill
- Champion defends against a queue of challengers
- Each fight happens on consecutive events
- Champion's accumulated damage carries over
- Tests endurance and dominance

### The Crucible (Special)
- Variable number of fighters
- Multi-stage with elimination and environmental hazards
- Unique rules per iteration
- The league's most dangerous and prestigious tournament
- Used once per year at the Inferno mega-event

---

## Records & Statistics

### Fighter Records

Every fighter's record tracks:
- **Win/Loss/Draw/NC**: Overall record
- **Method breakdown**: KOs, submissions, decisions
- **Streak data**: Current streak, longest win/loss streak
- **Title history**: Belts held and defended
- **Notable wins**: Ranked opponents defeated
- **Fight of the Night awards**: Entertainment value recognition
- **KO/Sub of the Night awards**: Best finish recognition
- **Rivalry records**: Head-to-head vs specific opponents

### League Records

All-time records that fighters can chase:
- Longest win streak
- Most title defenses
- Fastest knockout
- Most Fight of the Night awards
- Most finishes
- Longest career (time active)
- Most fights survived at The Crucible
- Highest single-fight damage dealt
- Most comebacks from behind

### Hall of Fame

Retired (or dead) fighters who left a significant mark on the league:
- Inducted annually at the Ascension mega-event
- Criteria: legacy, entertainment, competitive excellence
- Hall of Fame fighters' stories live on through legacy characters and lore

---

## The Fight Calendar

### Seasonal Structure

The AFL operates on a **quarterly season** structure:

```
MONTH 1 of Quarter:
  Week 1: Circuit + Monthly Special setup
  Week 2: Circuit (2 events)
  Week 3: Prime Time
  Week 4: Monthly Special Event

MONTH 2 of Quarter:
  Week 1: Circuit + Story development
  Week 2: Circuit (2 events)
  Week 3: Prime Time
  Week 4: Monthly Special Event

MONTH 3 of Quarter:
  Week 1: Circuit + Mega-Event buildup
  Week 2: Circuit + intense buildup
  Week 3: Prime Time (final before mega)
  Week 4: MEGA EVENT (quarterly PPV)
```

### Matchmaking

Fights are made through a combination of:

1. **Ranking logic**: #1 contender gets the title shot, ranked fighters fight each other
2. **Story demands**: A rivalry needs to culminate, a character needs a specific challenge
3. **Fan input**: Highly requested matchups get priority (future feature)
4. **Character agency**: Fighters calling each other out, issuing challenges
5. **Promoter manipulation**: The league itself has characters (promoters, commissioners) who make matches for their own reasons — which is itself a story

### Avoiding Rematches

To keep things fresh:
- Immediate rematches only for title fights or incredibly close/controversial results
- Standard fighters shouldn't fight the same opponent within 8 weeks
- Trilogy fights (3-fight series) should be reserved for the biggest rivalries
- When a rematch happens, the story between the fighters must have evolved
