# Between-Fight & League Tier System Design

## League Pyramid

```
        ┌─────────────────────┐
        │   AFL Apex   │  16 fighters - The elite
        │   (The Pros)         │  Full fight week, belt, max fanfare
        ├─────────────────────┤
        │  AFL Contender Series│  20 fighters - Minor leagues
        │  (The Minors)        │  Fight week, proving ground
        ├─────────────────────┤
        │                     │
        │   AFL Underground    │  100 fighters - The farm system
        │   (The Amateurs)     │  High turnover, raw talent
        │                     │  Abbreviated fight week
        └─────────────────────┘
```

**136 fighters total** in the ecosystem at any time.

### Tier Characteristics

**Apex (16 fighters)**
- 3 events per week, 2-3 fights per event
- Full 7-day fight week with all rituals
- Title belt for #1 ranked fighter
- Title defenses once per season (season finale main event)
- Events named: "AFL Apex: [Event Name]"

**Contender Series (20 fighters)**
- 3 events per week, 3 fights per event
- Full fight week (same rituals as Apex)
- No belt, but top performers earn promotion
- Events named: "AFL Contender Series: [Event Name]"

**Underground (100 fighters)**
- 5 events per week, 4-5 fights per event (more fighters = more frequent fights)
- Abbreviated fight week: weigh-in (day before) + fight day only
- No press conferences — these fighters haven't earned the mic yet
- Events named: "AFL Underground: [Event Name]"
- Higher injury tolerance in matchmaking (scrappier, less protected)

## Season Structure (1 in-game year = 1 season)

```
Months 1-10:  Regular season fights
Month 11:     Final regular season fights + promotion/relegation matches announced
Month 12:     Promotion/relegation fights + Apex title fight (season finale)
```

### Promotion & Relegation

End of each season, movement between tiers is decided by **head-to-head promotion fights**:

**Apex ↔ Contender:**
- Bottom 3 of Apex face Top 3 of Contender
- Three promotion fights: Champ #14 vs Contender #3, Champ #15 vs Contender #2, Champ #16 vs Contender #1
- Winner of each fight earns/keeps the Apex spot
- These fights happen ON a Apex card (big stage for Contender fighters)

**Contender ↔ Underground:**
- Bottom 3 of Contender face Top 3 of Underground
- Same format: three promotion fights
- Held on a Contender Series card

**Apex Title Fight:**
- #1 ranked challenger vs current belt holder
- Main event of Season Finale
- If no current champion (vacated), #1 vs #2

### Within-Season Rankings

Each tier has its own independent ranking. Rankings determine:
- Matchmaking priority (rank-adjacent fighters paired)
- Promotion/relegation candidates
- Title shot eligibility

## Fight Week Timeline

### Apex & Contender (7-day build)

| Day | Activity | Content Generated |
|-----|----------|-------------------|
| -7 | **Fight Announced** | Matchup graphic, tale of the tape, odds |
| -5 | **Training Camp Opens** | Training footage, sparring clips, conditioning reports |
| -3 | **Press Conference** | AI-narrated interview — trash talk, predictions, mental state |
| -2 | **Open Workout** | Technique showcase, form check, crowd interaction |
| -1 | **Weigh-In + Staredown** | Weight reveal (conditioning), face-off narrative |
| 0 | **FIGHT DAY** | The actual fight |
| +1 | **Post-Fight Presser** | Winner interview, loser reaction, callouts for next fight |

Each activity is an AI-generated narrative beat stored as a `FightWeekEvent`. These accumulate as the fight approaches, building anticipation. They also affect fighter state:

- **Press conference**: Can shift morale/momentum (dominant performance = confidence boost, gets rattled = morale dip)
- **Training camp**: Applies temporary stat adjustments (see Training section)
- **Weigh-in**: Reveals conditioning — if a fighter cut too much weight, stamina penalty for the fight

### Underground (2-day build)

| Day | Activity | Content Generated |
|-----|----------|-------------------|
| -1 | **Weigh-In** | Weight + brief face-off |
| 0 | **FIGHT DAY** | The fight |
| +1 | **Post-Fight Recap** | Brief summary |

Underground fighters haven't earned the full spectacle yet. Part of what makes promotion exciting — you finally get the full fight week treatment.

## Training System

### How Training Works

Between fights, healthy fighters train. Each fighter has a **training_focus** that can be set (or defaulted based on archetype):

**Training Focuses:**
- `power` — Heavy bag, strength work
- `speed` — Footwork drills, reaction training
- `technique` — Sparring, film study
- `toughness` — Conditioning, body hardening
- `supernatural` — Meditation, channeling practice (only if supernatural > 0)

### Mechanical Effects

**Daily training** (passive, happens automatically for healthy fighters):
- +0.1 to focused stat per training day (accumulates between fights)
- Applied as permanent stat change when enough accumulates (every 10 training days = +1 to stat)
- Stat caps still enforced (max 95)

**Fight camp** (active during fight week, -5 to -1 days before fight):
- Focused training gives a **temporary fight-night boost**: +3 to focused stat for the upcoming fight only
- This temporary boost does NOT persist after the fight

**Overtraining risk:**
- If a fighter trains more than 21 consecutive days without a fight, 5% daily chance of minor training injury (3-5 day recovery)
- Incentivizes regular fight scheduling

### Training Quality by Tier

- **Apex**: Best camps. +0.15/day base training rate, +4 fight-night boost
- **Contender**: Solid camps. +0.1/day, +3 fight-night boost
- **Underground**: Basic facilities. +0.08/day, +2 fight-night boost

This means Apex fighters develop faster, creating a compounding advantage — but a dominant Underground fighter who gets promoted can catch up with better training facilities.

## Fighter Lifecycle

### Entry
- New fighters enter Underground at age 18-26
- Generated with randomized stats within Underground-appropriate ranges (slightly lower total stats than established fighters)
- Each season, 8-12 new fighters are generated to replace retirees/cuts

### Peak & Decline
- **Rising (18-25)**: Slight natural stat growth each season (+1-2 random stats)
- **Peak (25-31)**: Stats stable, training improvements stick
- **Declining (32+)**: -1 to speed and toughness per season. Power and technique hold longer
- **Veteran (36+)**: -1 to all physical stats per season. Only supernatural holds

### Retirement Triggers

Fighters don't fight forever. A fighter retires when ANY of these conditions are met:

1. **Age + losses**: Age 34+ with losing record (losses > wins) in current season
2. **Underground stagnation**: 3+ consecutive seasons in Underground without promotion
3. **Morale collapse**: Morale at "broken" (new state below "low") after 3+ consecutive losses
4. **Career-ending injury**: Severe injury while age 32+ has 30% chance of forced retirement
5. **Graceful exit**: Fighter who just won a Apex title defense at age 33+ may retire on top (20% chance — rare, creates legacy moments)

When a fighter retires:
- Final storyline entry generated ("X hung up the gloves after...")
- Fighter data preserved (never deleted) but marked `status: "retired"`
- Opens roster spot in their tier, filled by promotion or new generation

### Giving Up on Promotion

Fighters in Underground who are aging (28+) and haven't been promoted develop a `promotion_desperation` value:
- Tracks how badly they want to move up
- High desperation → more aggressive fighting style, risk-taking
- After hitting age 30 without ever leaving Underground, desperation converts to resignation
- Resigned fighters become "gatekeepers" — still fight but no longer in promotion contention
- Eventually retire via the age+losses trigger

This creates natural story arcs: hungry young prospect vs grizzled Underground veteran who never made it.

## Data Model Changes

### Fighter (additions)

```python
tier: str = "underground"              # "apex", "contender", "underground"
status: str = "active"                 # "active", "injured", "retired"
training_focus: str = "technique"      # Current training focus
training_days_accumulated: int = 0     # Days trained since last stat bump
training_streak: int = 0              # Consecutive days trained (overtraining risk)
seasons_in_current_tier: int = 0       # For stagnation/promotion tracking
career_season_count: int = 0           # Total seasons fought
peak_ranking: int = 0                  # Highest ranking ever achieved (any tier)
promotion_desperation: float = 0.0     # 0.0-1.0, Underground aging mechanic
```

### WorldState (additions)

```python
season_number: int = 1
season_week: int = 1                          # 1-8
season_day_in_week: int = 1                   # 1-7

tier_rankings: dict = {                        # Rankings per tier
    "apex": ["f_id1", ...],
    "contender": ["f_id2", ...],
    "underground": ["f_id3", ...]
}

belt_holder_id: str = ""                       # Current apex belt holder
belt_history: list = [                         # Historical record
    {"fighter_id": "f_1", "won_date": "...", "lost_date": "...", "defenses": 2}
]

retired_fighters: list[str] = []               # IDs of retired fighters

promotion_fights: list = [                     # Scheduled for season week 8
    {"apex_fighter_id": "f_1", "contender_fighter_id": "f_2", "tier_boundary": "apex_contender"}
]
```

### New Model: FightWeekEvent

```python
@dataclass
class FightWeekEvent:
    id: str = ""
    event_id: str = ""                # The fight event this builds toward
    match_id: str = ""                # Which specific fight on the card
    fighter1_id: str = ""
    fighter2_id: str = ""
    activity_type: str = ""           # "announcement", "training_camp", "press_conference",
                                      # "open_workout", "weigh_in", "post_fight_presser"
    day_offset: int = 0               # Days relative to fight (negative = before)
    date: str = ""
    narrative: str = ""               # AI-generated narrative text
    fighter1_effects: dict = {}       # {"morale": +1, "momentum": "rising"}
    fighter2_effects: dict = {}
    image_prompt: str = ""            # For AI image generation
```

### New Model: TrainingLog

```python
@dataclass
class TrainingEntry:
    date: str = ""
    focus: str = ""                   # Which stat trained
    intensity: str = "normal"         # "light", "normal", "intense"
    stat_gained: float = 0.0          # Fractional stat gain for the day
    injury_occurred: bool = False
    notes: str = ""                   # Brief AI-generated training flavor text
```

## Engine Changes

### New Module: `backend/app/engine/between_fights/`

```
between_fights/
    __init__.py
    fight_week.py          # Generates fight week activities on the right days
    training.py            # Daily training processing
    league_tiers.py        # Tier management, promotion/relegation logic
    retirement.py          # Fighter lifecycle, retirement checks
    season.py              # Season progression, week tracking
```

### Updated day_ticker.py Flow

```python
def advance_day():
    # 1. Advance date, season tracking
    increment_date()
    update_season_week()

    # 2. Process injuries
    heal_injuries()

    # 3. Daily training for all healthy, non-fight-day fighters
    process_daily_training()

    # 4. Generate fight week content (check all upcoming fights)
    generate_fight_week_events()    # Press conferences, weigh-ins, etc.

    # 5. Run today's events (per tier)
    run_apex_events()
    run_contender_events()
    run_underground_events()

    # 6. Post-fight processing (existing + new)
    apply_post_fight_updates()
    update_tier_rankings()

    # 7. Season boundary checks
    if is_season_end():
        run_promotion_relegation()
        process_retirements()
        generate_new_underground_fighters()
        advance_season()

    # 8. Schedule future events (per tier)
    ensure_upcoming_schedule()
```

### Updated Matchmaker

- `generate_fight_card()` now takes a `tier` parameter
- Underground has its own scoring weights (less emphasis on rank proximity, more on activity)
- Promotion fights are manually scheduled, not auto-generated

## File Storage Changes

```
/data/
    /fighters/              # Same as before
    /matches/               # Same as before
    /events/                # Same, but events now have a "tier" field
    /fight_week/            # NEW - fight week narrative events
        fw_[id].json
    /seasons/               # NEW - season archives
        season_[n].json     # End-of-season snapshot (final rankings, promotions, retirements)
    /world_state.json       # Expanded with tier + season data
```

## Example Season Arc

```
Season 3, Week 1:
  - Apex: "Viper" defends belt. Underground phenom "Blaze" just got promoted to Contender.

Week 3:
  - Contender: Blaze wins second fight by KO. Fans buzzing.
  - Underground: Veteran "Iron Mike" (age 31, 3rd season in Underground) loses again. Morale dropping.

Week 5:
  - Apex: Two top fighters develop rivalry after heated press conference.
  - Underground: Iron Mike wins a gritty decision. Brief hope, but time is running out.

Week 7:
  - Promotion fights announced. Blaze earned Contender #1. Faces Apex #16 "Granite" next week.
  - Iron Mike finishes Underground #15. Not enough — he's #4. No promotion fight for him.

Week 8 (Season Finale):
  - Blaze beats Granite by TKO Round 3. Promoted to Apex. The crowd erupts.
  - Apex title fight: Viper retains by decision. Dominant.
  - Iron Mike retires. "Underground gatekeeper" storyline concludes. New fighters enter next season.

Season 4, Week 1:
  - Blaze enters Apex as the fresh face everyone's watching.
  - 8 new Underground fighters generated. The cycle continues.
```
