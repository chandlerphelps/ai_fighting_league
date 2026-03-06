# League Mechanics

How the league operates: seasons, fights, rankings, promotions, injuries, training, and retirement.

## Season Structure

Each season = 1 in-game year spanning **8 months** (November through June).

| Phase | Months | What Happens |
|-------|--------|-------------|
| Regular season | Nov - May (months 1-7) | Fights + daily training |
| Promotion month | June (month 8) | Promotion/relegation announced |
| Season end | After June 30 | Promotion fights, title fight, retirement, aging, backfill, stat reset |

Season dates: starts Nov 1, ends June 30 of the following year. Base year = 2024 for season 1.

---

## Day Simulation Flow

Each day is processed as a single atomic step. The sequence:

1. **Recovery**: decrement injury timers; fighters whose recovery expires return to "healthy"
2. **Training**: all healthy active fighters accumulate fractional stat progress
3. **Fights**: if the calendar has fights scheduled for today, run them (combat + post-fight updates)
4. **Calendar advance**: move to next day; if season ends, trigger end-of-season processing
5. **Rankings**: recalculate tier and global rankings
6. **Schedule next day**: pre-compute tomorrow's fights for frontend preview

Each day's RNG is seeded by day ordinal, making simulations fully reproducible.

Source: `engine/day_simulator.py`

---

## Determinism

All fights are deterministic. The combat seed is a SHA-256 hash of `fighter1_id:fighter2_id:date`, and daily RNG is seeded by day ordinal. Running the same simulation twice produces identical results.

---

## Tier System

Three tiers, each with target roster sizes:

| Tier | Default Size | Event Interval | Fights/Event | Start Time |
|------|-------------|----------------|-------------|------------|
| Apex | 16 | Every 10 days | 2-3 | 21:00 |
| Contender | 20 | Every 6 days | 2-3 | 18:00 |
| Underground | 100 | Every day | 4-6 | 14:00 |

Fights within an event are staggered 30 minutes apart.

---

## Matchmaking

During regular season months, fights are scheduled automatically per tier:

1. Load all healthy, active fighters in the tier
2. Shuffle them using the date-seeded RNG (deterministic)
3. Pair fighters greedily: iterate through the shuffled list, pairing each fighter with the next unpaired one
4. Cap the number of fights per event based on tier config

No fighter fights twice in one day. Pre-scheduled fights (from `scheduled_fights` in world state) bypass automatic matchmaking when present.

Source: `engine/day_simulator.py`

---

## Fighter Stats

### Core Stats (15-100)

| Stat | Role |
|------|------|
| **Power** | Scales strike damage; favors heavy-damage moves |
| **Speed** | Acts first (lower initiative), increases evasion, favors fast moves |
| **Technique** | Increases hit/block/counter chance; favors submissions |
| **Toughness** | Increases max HP and damage reduction |

### Secondary Stats (0-100)

| Stat | Role |
|------|------|
| **Supernatural** | Determines max mana and supernatural move scaling |
| **Guile** | Bypasses damage reduction, boosts slip success, amplifies psychological warfare, drains opponent stamina |

### Derived Resources

Four combat resources — **HP**, **Stamina**, **Mana**, **Guard** — are derived from core/secondary stats. Each has its own regeneration and depletion mechanics during combat.

Formulas: `engine/combat/models.py`, `engine/combat/damage.py`

---

## Gender System

Males and females have different stat biases and archetype pools:

- **Males**: stat bias toward power and toughness; lower supernatural/guile ranges
- **Females**: stat bias toward speed and technique; broader supernatural/guile potential

Gender also determines available archetypes (11 female, 8 male). New fighters are assigned 50/50 gender unless overridden. These biases apply during procedural fighter generation (LLM-generated fighters may vary).

Source: `engine/between_fights/retirement.py`, `engine/fighter_config.py`

---

## Combat System

### Structure

- Up to **30 rounds**, **30 ticks per round**
- Each tick: both fighters pick a move via strategy AI, resolve by initiative order (faster fighter acts first)

### Move Catalog

28 universal moves across six categories:

| Category | Role | Positions |
|----------|------|-----------|
| **Strikes** | Damage ranging from light jabs to heavy overhands; some cause stun | Standing |
| **Kicks** | Mix of damage and stamina drain; includes finishers | Standing |
| **Clinch** | Transition to/from clinch; close-range elbows, knees, throws | Clinch |
| **Ground** | Ground-and-pound, elbows, submission attempts | Ground |
| **Supernatural** | High-damage abilities that cost mana | Any |
| **Defensive** | Block, slip (can trigger counter), stamina recovery | Any |

Some moves are tagged as **finishers** (bonus damage on low-HP opponents). Full catalog: `engine/combat/moves.py`

### Position System

Three positions: **Standing**, **Clinch**, **Ground**. Moves are position-locked. Specific transition moves change position (Clinch Entry, Hip Throw, Break Clinch, Sweep). Position resets to Standing between rounds.

### Hit Resolution

When a move targets an opponent, the system checks (in order): slip → block → hit → counter-on-miss. Hit chance scales with technique and stamina; evasion scales with speed. Consecutive hits build a **combo counter** that boosts accuracy and damage, reset on any non-hit.

### Damage

Raw damage scales with the relevant stat (power for strikes, technique for submissions, supernatural for magic). Toughness provides damage reduction; guile partially bypasses it. Blocked attacks deal reduced damage.

Formulas: `engine/combat/damage.py`

---

## Emotional System

Five emotional dimensions (0-100) shift dynamically during combat:

| Emotion | Role |
|---------|------|
| **Composure** | Dampens all emotional swings — high-technique fighters stay stable |
| **Confidence** | When high: boosts accuracy and damage |
| **Rage** | When high: boosts damage but reduces accuracy and blocking |
| **Fear** | When high: reduces damage but boosts evasion; increases stamina drain |
| **Focus** | When high: boosts accuracy and blocking |

Emotions shift based on fight events (landing hits, getting countered, taking heavy damage). Guile amplifies negative emotions inflicted on opponents. All emotions decay each tick and partially reset between rounds.

Source: `engine/combat/conditions.py`

---

## Mana & Supernatural

Mana starts at 0 and builds each tick. It's a **comeback mechanic**: fighters in trouble (low HP, high rage/fear) generate mana much faster. High supernatural stat increases the gain rate.

Using mana accumulates **supernatural debt**, which can cause post-fight recovery days and permanent supernatural stat degradation.

Source: `engine/combat/conditions.py`

---

## Win Conditions

| Condition | Trigger |
|-----------|---------|
| **KO** | HP reaches 0 |
| **TKO** | High accumulated damage + low HP; probability increases as fight progresses |
| **Submission** | From grappling moves when defender has low HP and stamina; technique advantage helps |
| **Decision** | After 30 rounds, fighter with higher HP wins |

Source: `engine/combat/win_conditions.py`

---

## Between-Round Recovery

Each round break restores a percentage of stamina (decreasing as the fight progresses), fully restores guard, clears stun, resets position to standing, and applies emotional decay.

Source: `engine/combat/simulator.py`

---

## Strategy AI (WeightedStrategy)

Move selection uses probabilistic weighted scoring across 8 factors: stamina management, finishing opportunities, defensive needs, supernatural timing, stat affinity (e.g. power fighters favor heavy hits), positional preference, combo exploitation, and fatigue management. Scores are normalized to probabilities with a small minimum floor so nothing is truly impossible.

Source: `engine/combat/strategy.py`

---

## Pre-Fight: Fight Camp Boost

Before each fight, the fighter's training focus stat gets a temporary boost scaled by tier (higher tiers get larger boosts). Applied to a copy of stats — doesn't persist.

Source: `engine/between_fights/training.py`

---

## Morale & Momentum

Tracked on `fighter.condition`:

| Field | Values | Trigger |
|-------|--------|---------|
| **Morale** | high / neutral / low | High: 2+ consecutive wins. Low: 2+ consecutive losses, or injured |
| **Momentum** | rising / neutral / falling | Rising: 2+ consecutive wins. Falling: 2+ consecutive losses |

**Combat effects**: momentum and morale adjust starting emotional state (e.g. rising momentum starts with higher confidence and composure).

**Training effect**: morale multiplies daily training rate — high morale trains faster, low morale trains slower.

Morale resets: low → neutral at season end. Winning with low morale bumps to neutral. 5+ consecutive losses forces morale to low.

---

## Daily Training

Each day, healthy active fighters accumulate fractional progress toward +1 in their focus stat. The daily rate is influenced by tier (higher tiers train faster), age (young fighters learn faster), hidden stats (learning rate, work ethic), and morale.

Low work ethic fighters may skip training days entirely. After 90+ consecutive training days, there's a small chance of overtraining strain (minor injury).

Source: `engine/between_fights/training.py`

---

## Injuries

### Severity Tiers

Five severity levels from **minor** (a few days) to **career-ending** (permanent retirement). Season-ending injuries cause the fighter to miss the rest of the season.

### Post-Fight Injuries

Winners rarely get injured (minor only). Losers have a significant injury chance, especially after KO/TKO losses. Older fighters face escalating risk of season-ending and career-ending injuries.

### Supernatural Debt

Heavy mana usage during a fight causes extra recovery days and can permanently reduce the supernatural stat.

### Recovery

Recovery days tick down 1 per day. All non-career-ending injuries heal at season end.

Source: `engine/post_fight.py`

---

## Post-Fight Updates

After each fight, several permanent changes apply:

- **Records**: win/loss/draw updated, streak tracking, season stats
- **Stat adjustments**: winners tend to gain technique/power; losers may lose technique but can gain toughness (from KO losses) or technique (from submission losses)
- **Injuries**: rolled based on outcome and fighter age
- **Storylines**: LLM generates a 2-3 sentence narrative entry capturing the fight's dramatic significance (confidence building, humbling loss, rivalry intensifying, etc.), stored in the fighter's `storyline_log`
- **Rivalries**: head-to-head record updated; marked as rivalry after 2+ meetings
- **Morale/momentum**: updated based on win/loss streaks

Source: `engine/post_fight.py`, `prompts/post_fight_prompts.py`

---

## Rankings

### Global Rankings

Sort by tier, then within tier: win percentage → total wins → recent form → last fight date.

### Tier Rankings (used for promotions)

Sort within tier: **season wins** (primary) → win percentage → recent form → core stat total.

Source: `engine/rankings.py`, `engine/between_fights/league_tiers.py`

---

## Promotion & Relegation

### Timeline

- Promotion month (June): matchups announced
- Season end (after June 30): promotion fights occur

### Matchup Selection

- **Apex vs Contender**: bottom 4 Apex fighters vs top 4 Contender fighters
- **Contender vs Underground**: bottom 6 Contender fighters vs top 6 Underground fighters

### Protected Fighters

Cannot be selected for relegation: current belt holder, and season-ending injury victims with a winning record or 3+ wins.

### Fight Outcomes

Lower-tier fighter wins → tiers swap. Upper-tier fighter wins → both stay.

### Backfill Promotions

After retirements create vacancies: promote top performers from the tier below (sorted by season wins, then core stat total). Underground deficit is filled by generating new fighters.

Source: `engine/between_fights/league_tiers.py`, `engine/between_fights/season.py`

---

## Title Fight

At season end, the belt holder defends against the #1 ranked Apex fighter. If no belt holder exists, the top 2 Apex fighters fight for the vacant belt. Belt history tracks each reign with defenses count.

Source: `engine/between_fights/league_tiers.py`

---

## Fighter Generation

New fighters enter through two paths:

1. **LLM-based** (primary): AI plans a roster entry (archetype, personality, backstory) → generates full fighter JSON with stats → generates portrait and charsheet images. Uses gender-specific archetype pools and body profiles.
2. **Procedural fallback**: if LLM fails, generates a fighter with gender-biased stat distribution and minimal backstory.

New fighters always enter at Underground tier, age 18-22. The generation pipeline is also used for initial roster creation.

Source: `engine/fighter_generator.py`, `engine/between_fights/season.py`, `engine/between_fights/retirement.py`

---

## Aging

Applied once per season at season end, before retirement. Young fighters gain stats, prime-age fighters are stable, and veterans decline (speed and toughness degrade first, then all stats at advanced age).

Source: `engine/between_fights/retirement.py`

---

## Retirement

Checked at season end after aging. Five conditions: age + losing record, underground stagnation (old fighters stuck in lowest tier), morale collapse (long losing streak), severe injury at advanced age, and graceful exit (champion choosing to retire). Retired fighters are removed from active roster; if the retiree holds the belt, it becomes vacant.

Source: `engine/between_fights/retirement.py`

---

## Rivalries

Tracked in `rivalry_graph` on world state. Created automatically after any fight. A pair is marked as a **rivalry** once they've fought 2+ times. Tracks head-to-head record. Used for narrative and display — no direct gameplay effect.

---

## Hidden Stats

| Stat | Role |
|------|------|
| **learning_rate** | Permanent multiplier on daily training rate |
| **work_ethic** | Low: may skip training. High: bonus training rate |
| **promotion_desperation** | Accumulates for old Underground fighters (reserved for future narrative use) |
| **training_days_accumulated** | Fractional progress toward next stat point |
| **training_streak** | Consecutive training days; overtraining risk when high |

---

## Season End Processing

Full sequence:

1. **Aging**: all active fighters age 1 year, stats adjusted
2. **Retirement**: 5 conditions evaluated, retirees removed
3. **Promotion desperation**: updated for qualifying Underground fighters
4. **Backfill tiers**: promote from below to fill vacancies, generate new Underground fighters
5. **Stat reset**: season records zeroed, `seasons_in_current_tier` increments, low morale reset, non-career injuries healed
6. **Calendar reset**: season number increments, date set to Nov 1 of next year

Source: `engine/between_fights/season.py`

---

## File Locations

| Concern | File |
|---------|------|
| Day-by-day simulation | `engine/day_simulator.py` |
| Combat models | `engine/combat/models.py` |
| Move catalog | `engine/combat/moves.py` |
| Damage, hit/block/counter resolution | `engine/combat/damage.py` |
| Emotional states, mana, modifiers | `engine/combat/conditions.py` |
| Tick resolution, initiative | `engine/combat/resolution.py` |
| Strategy AI | `engine/combat/strategy.py` |
| Combat loop | `engine/combat/simulator.py` |
| Win conditions | `engine/combat/win_conditions.py` |
| Fight pipeline (combat → Match model) | `engine/fight_simulator.py` |
| Post-fight updates (records, injuries, rivalries, storylines) | `engine/post_fight.py` |
| Post-fight storyline prompts | `prompts/post_fight_prompts.py` |
| Global rankings | `engine/rankings.py` |
| Daily training | `engine/between_fights/training.py` |
| Retirement, aging, replacement generation | `engine/between_fights/retirement.py` |
| Tier rankings, promotion/relegation, title fights | `engine/between_fights/league_tiers.py` |
| Season calendar, end-of-season processing | `engine/between_fights/season.py` |
| Fighter generation | `engine/fighter_generator.py` |
| Fighter config (archetypes, body profiles) | `engine/fighter_config.py` |
| Fighter data model | `models/fighter.py` |
| World state data model | `models/world_state.py` |
| Global config | `config.py` |
