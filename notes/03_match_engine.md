# Match Engine - Fight Simulation & Narrative Generation

## Overview

The Match Engine is the heart of AFL. It takes two fighters, their stats, the match
context (stakes, history, crowd, match type), and produces:

1. **Win probabilities** for each fighter
2. **A decisive outcome** (via weighted random roll)
3. **A beat-by-beat fight narrative** in structured JSON
4. **Post-fight consequences** (injuries, stat changes, story beats)

The engine has three distinct phases that run sequentially:

```
PHASE 1: PROBABILITY CALCULATION (AI + Math)
    Fighter stats + context → win % for each fighter

PHASE 2: OUTCOME DETERMINATION (Random Roll)
    Weighted random number → winner, method of victory, round

PHASE 3: NARRATIVE GENERATION (AI)
    Winner + method + fighter profiles + context → blow-by-blow story
```

---

## Phase 1: Probability Calculation

### Inputs

The AI receives a structured prompt containing:

```
Fighter A:
  - Full stat block (physical, combat, psychological, supernatural)
  - Current condition (injuries, emotional state, training camp quality)
  - Recent form (last 5 fight results and how they went)
  - Stylistic tendencies (counter-fighter, pressure fighter, grappler, etc.)

Fighter B:
  - Same as above

Match Context:
  - Match type (standard, title fight, grudge match, death match, tournament)
  - Stakes (what's on the line narratively)
  - Relationship history (have they fought before? personal beef?)
  - Venue/crowd factor (home crowd? hostile territory? neutral?)
  - Round count (3 rounds, 5 rounds, unlimited)

Stylistic Matchup Notes:
  - How does A's style interact with B's?
  - Historical data: how have similar matchups gone in this league?
```

### Output from AI

The AI returns a structured assessment:

```json
{
  "fighter_a_win_probability": 0.62,
  "fighter_b_win_probability": 0.38,
  "confidence": "high",
  "reasoning": "Fighter A's pressure style historically gives counter-fighters trouble...",
  "likely_methods": {
    "fighter_a": {
      "ko_tko": 0.25,
      "submission": 0.05,
      "decision": 0.30,
      "special": 0.02
    },
    "fighter_b": {
      "ko_tko": 0.15,
      "submission": 0.10,
      "decision": 0.12,
      "special": 0.01
    }
  },
  "key_factors": [
    "A's reach advantage neutralizes B's counter-striking",
    "B's chi mastery could be disrupted if A maintains pressure",
    "A's cardio advantage becomes critical in later rounds"
  ],
  "upset_scenario": "If B can keep distance and land her counter combinations early, she could crack A's confidence and control the fight from the outside",
  "wild_card_factors": [
    "B's unresolved anger toward A's faction could compromise her composure",
    "A has been dealing with a nagging shoulder injury that hasn't been publicized"
  ]
}
```

### Probability Guardrails

To keep fights interesting, we enforce some constraints:

- **No fighter can have less than 5% win probability** — upsets must always be possible
- **No fighter can have more than 95% win probability** — guaranteed wins don't exist
- **Death probability** is calculated separately and only applies to specific match types:
  - Standard matches: 0-2% death chance
  - Grudge matches: 1-5% death chance
  - Death matches: 5-15% death chance
  - Special events: Varies (some matches are specifically death stakes)
- **Draw probability**: 1-5% for standard, 0% for death matches

---

## Phase 2: Outcome Determination

This is the **purely mechanical** step. No AI involved — just math and randomness.

### Step 1: Determine Winner

```
Roll a random float between 0.0 and 1.0
If roll <= fighter_a_win_probability: Fighter A wins
Else: Fighter B wins

(With draw chance carved out of both probabilities if applicable)
```

### Step 2: Determine Method of Victory

Using the winner's method probabilities, roll again to determine how they won:

- **KO/TKO**: Fight stopped due to strikes, referee stoppage, corner stoppage
- **Submission**: Tap out, choke unconscious, joint break
- **Decision**: Goes to judges (unanimous, split, majority)
- **Special**: Supernatural finish, disqualification, forfeit, death of opponent
- **Draw**: Both fighters unable to continue, or judges can't decide

### Step 3: Determine Round

Based on the method:
- **KO/TKO**: Weighted toward earlier rounds for power punchers, later for grinders
- **Submission**: Weighted toward mid-to-late rounds (setups take time)
- **Decision**: Always final round
- **Special**: Weighted by narrative context

### Step 4: Determine Specific Timing

For non-decision outcomes, roll for the specific time within the round (e.g., 2:47 of Round 3).

### Step 5: Determine Secondary Outcomes

- **Injury severity** for loser (and possibly winner)
- **Performance rating** for both fighters (affects rankings/reputation)
- **Bonus flags**: Fight of the Night, KO of the Night, etc.
- **Death check** (if applicable for match type)

### Output

```json
{
  "winner": "fighter_a",
  "method": "ko_tko",
  "round": 3,
  "time": "2:47",
  "stoppage_type": "referee",
  "loser_injury": {
    "type": "concussion",
    "severity": "moderate",
    "recovery_weeks": 6
  },
  "winner_injury": {
    "type": "cut_above_eye",
    "severity": "minor",
    "recovery_weeks": 2
  },
  "performance_ratings": {
    "fighter_a": 8.5,
    "fighter_b": 6.2
  },
  "bonuses": ["ko_of_the_night"],
  "death": false
}
```

---

## Phase 3: Narrative Generation

### The Big Moment

This is where the magic happens. The AI takes the outcome and all context and crafts a
**round-by-round, moment-by-moment fight narrative**.

### Inputs

```
Everything from Phase 1 (fighter profiles, context)
+
Phase 2 outcome (winner, method, round, time, injuries)
+
Narrative directives:
  - Tone (dramatic? clinical? chaotic?)
  - Key story beats to hit (e.g., "B's composure breaks in round 2")
  - Crowd reaction guidance
  - Commentary style
```

### Output: Fight Narrative JSON

The narrative is structured as a timeline of events that can be programmatically displayed:

```json
{
  "fight_id": "AFL-2024-0147",
  "fighter_a": { "id": "fighter_001", "name": "Marcus 'The Hammer' Cole" },
  "fighter_b": { "id": "fighter_047", "name": "Sable Morrigan Vex" },
  "venue": "The Iron Cathedral, Neo-Tokyo",
  "match_type": "Championship Bout - 5 Rounds",
  "pre_fight": {
    "atmosphere": "Electric. The crowd is split — Cole's power vs Vex's precision. The giant screens replay their confrontation from last week's weigh-in where Vex whispered something that made Cole's face go white.",
    "ring_entrance_a": "Cole enters to thundering drums. No theatrics tonight — just a death stare at the cage. He's 245 lbs of coiled fury.",
    "ring_entrance_b": "Vex glides in silently. The Celtic tattoos on her arms seem to pulse under the arena lights. She doesn't look at Cole. She looks through him.",
    "staredown": "The referee brings them center. Cole towers over Vex by eight inches. She tilts her head, smiles, and mouths: 'I already know.' Cole's jaw tightens."
  },
  "rounds": [
    {
      "round_number": 1,
      "events": [
        {
          "time": "0:00",
          "type": "round_start",
          "description": "The bell rings. Cole storms forward immediately — no feeling out process tonight."
        },
        {
          "time": "0:08",
          "type": "strike_attempt",
          "attacker": "fighter_a",
          "technique": "overhand right",
          "result": "missed",
          "description": "Cole launches a massive overhand right that Vex slides under like water. She was already moving before he threw it."
        },
        {
          "time": "0:11",
          "type": "strike_landed",
          "attacker": "fighter_b",
          "technique": "counter jab",
          "target": "head",
          "damage": "light",
          "description": "Vex snaps a jab into Cole's exposed chin on the way out. First blood to the counter-striker."
        },
        {
          "time": "0:30",
          "type": "exchange",
          "description": "Cole cuts the cage, trying to trap Vex against the fence. She circles out but he clips her with a body jab. She absorbs it but you can see she felt the power difference.",
          "significance": "minor"
        },
        {
          "time": "1:15",
          "type": "momentum_shift",
          "favor": "fighter_b",
          "description": "Vex finds her rhythm. Three consecutive counter combinations land clean — jab, cross, pivot away. Cole is walking into shots he can't see coming. Her chi sense is dialed in.",
          "crowd_reaction": "The Vex faithful erupt. 'SABLE! SABLE! SABLE!'"
        },
        {
          "time": "2:45",
          "type": "special_ability",
          "user": "fighter_b",
          "ability": "chi_sense",
          "description": "Vex's eyes narrow. For a moment she seems to see Cole's next combination before he throws it — slipping the jab, ducking the hook, and landing a devastating liver shot as he overextends. Cole grimaces and backs off for the first time tonight.",
          "visual_effect": "Faint blue shimmer along Vex's forearms as she moves"
        },
        {
          "time": "4:50",
          "type": "round_end_summary",
          "description": "Clear round for Vex. She outboxed Cole from the outside, landing 23 of 31 significant strikes to Cole's 8 of 27. But Cole's 8 all had bad intentions — Vex's ribs are already reddening.",
          "scorecard": { "fighter_a": 9, "fighter_b": 10 },
          "stats": {
            "fighter_a": { "sig_strikes_landed": 8, "sig_strikes_thrown": 27, "takedowns": 0 },
            "fighter_b": { "sig_strikes_landed": 23, "sig_strikes_thrown": 31, "takedowns": 0 }
          }
        }
      ]
    }
  ],
  "finish": {
    "round": 3,
    "time": "2:47",
    "type": "ko_tko",
    "description": "Cole, desperate and bleeding from a cut over his right eye, rushes forward with everything he has. But Vex has been waiting for this moment all fight. She reads the right hand, slips outside, and uncorks the Blackout Waltz — a scything liver shot that buckles Cole's knees, followed by a picture-perfect head kick as he drops his guard in pain. Cole crumbles. The referee doesn't even start counting. It's over.",
    "finishing_move_name": "Blackout Waltz",
    "crowd_reaction": "Stunned silence, then an eruption. Half the arena can't believe what they just saw. The other half always knew.",
    "winner_celebration": "Vex doesn't celebrate. She stands over Cole for a long moment, then kneels beside him and whispers something in his ear. His face changes. She stands, nods to the crowd once, and walks out.",
    "post_fight_mystery": "What did she whisper?"
  },
  "post_fight": {
    "winner_interview": "Vex declines the in-ring interview. Her corner says she'll speak when she's ready.",
    "loser_status": "Cole is helped to his feet at 3:15. He walks out under his own power but looks shaken — and not just by the knockout.",
    "medical_report": {
      "fighter_a": "Moderate concussion. Cut requiring 6 stitches. Recommended 6-week suspension.",
      "fighter_b": "Bruised ribs, left side. Minor swelling right hand. Cleared for training in 2 weeks."
    },
    "narrative_hooks": [
      "What did Vex whisper to Cole?",
      "Cole's corner looked furious — at Cole, not Vex. What's going on internally?",
      "The Ashen Circle had representatives in the crowd tonight. They were watching Vex very closely."
    ]
  }
}
```

---

## Event Types Within a Fight

The narrative should use a consistent vocabulary of event types so the frontend can
render them appropriately:

| Event Type | Description | Visual Treatment |
|---|---|---|
| `round_start` | Bell rings, round begins | Timer starts, stance animations |
| `round_end` | Bell rings, round ends | Scorecard display |
| `round_end_summary` | Stats and scoring | Stats overlay |
| `strike_attempt` | A strike is thrown (hit or miss) | Attack animation |
| `strike_landed` | A strike connects | Impact effect, damage indicator |
| `combination` | Multiple strikes in sequence | Rapid sequence animation |
| `exchange` | Both fighters trading blows | Chaotic exchange animation |
| `takedown_attempt` | Grappling attempt | Grapple animation |
| `takedown_landed` | Successful takedown | Position change to ground |
| `submission_attempt` | Submission hold applied | Submission animation + tension meter |
| `submission_escape` | Fighter escapes submission | Escape animation |
| `position_change` | Transition on the ground | Position indicator update |
| `clinch` | Fighters in close grappling range | Clinch animation |
| `momentum_shift` | Notable shift in who's winning | Visual atmosphere change |
| `special_ability` | Supernatural/special technique used | Unique visual effect |
| `knockdown` | Fighter dropped but not finished | Knockdown count animation |
| `injury_event` | Notable injury occurs | Injury indicator |
| `crowd_moment` | Crowd reaction moment | Crowd audio/visual change |
| `corner_advice` | Between rounds, corner speaks | Corner dialogue box |
| `referee_action` | Referee intervenes | Referee animation |
| `stoppage` | Fight is stopped | Stoppage sequence |
| `commentary` | Color commentary moment | Commentary text overlay |
| `psychological_moment` | Mental/emotional turning point | Mood/atmosphere shift |
| `taunt` | Fighter taunts opponent | Taunt animation |
| `dirty_move` | Borderline or illegal technique | Warning/controversy indicator |

---

## Fight Pacing Guidelines

Fights should feel like real fights with ebbs and flows:

### Standard Pacing
- **Rounds 1-2**: Feeling out, establishing range, early exchanges
- **Middle rounds**: The fight's identity emerges, momentum swings
- **Late rounds**: Fatigue sets in, desperation, final pushes

### Event Density
- ~8-15 significant events per round for a standard pace
- ~15-25 events for high-action rounds
- ~5-8 events for slower, tactical rounds
- Major moments should have more detailed descriptions
- Not every exchange needs to be narrated — summarize stretches of control

### Time Gaps
- Events don't need to be continuous. Gaps of 10-30 seconds between events are normal
  (fighters resetting, circling, feinting)
- Narrate the gaps occasionally: "30 seconds of Vex circling, keeping Cole at the end
  of her jab, neither willing to commit"

---

## Match Types

Different match types affect probability calculations and narrative tone:

| Match Type | Rounds | Death Risk | Tone | Special Rules |
|---|---|---|---|---|
| **Standard** | 3 | ~1% | Professional | Normal rules |
| **Main Event** | 5 | ~1% | Epic | Normal rules, higher stakes |
| **Title Fight** | 5 | ~2% | Grand | Championship on the line |
| **Grudge Match** | 5 | ~3% | Intense/Personal | Looser refereeing |
| **Death Match** | Unlimited | ~10% | Brutal | No referee stoppage, fight to finish |
| **The Crucible** | Varies | ~15% | Horrific | Special arena, environmental hazards |
| **Exhibition** | 3 | 0% | Fun/Casual | No rankings impact |
| **Tournament** | 3 | ~2% | Urgent | Must win to advance, cumulative damage |
| **Battle Royale** | 1 | ~5% per person | Chaos | Multi-fighter, last standing wins |
| **Blood Pact** | 5 | ~5% | Supernatural | Both fighters' special abilities amplified |

---

## Post-Fight Processing

After the narrative is generated, the system processes consequences:

1. **Stat Adjustments**: Winner gets confidence boost, loser takes psychological hit
2. **Injury Processing**: Injuries from the fight are logged with recovery timelines
3. **Relationship Updates**: Rivalry intensifies, respect grows, new beef starts
4. **Ranking Updates**: Win/loss records update, rankings recalculate
5. **Story Hook Generation**: AI identifies 2-3 narrative threads to follow from the fight
6. **Fan Impact**: Investment payouts, sponsorship effects
7. **Death Processing**: If a fighter died, handle permanent removal and story impact

---

## Quality Checks

Every generated narrative should be validated for:

- **Consistency**: Does the narrative match the determined outcome?
- **Stat Alignment**: Does the described fighting match the fighters' actual stats?
- **Continuity**: Does it reference relevant history between the fighters correctly?
- **Pacing**: Is there a natural arc to the fight, not just random events?
- **Character Voice**: Do the fighters behave in ways consistent with their personalities?
- **Injury Logic**: Are injuries from the fight reflected in the blow-by-blow?
- **Time Logic**: Do event timestamps make sense sequentially?
