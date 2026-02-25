# Fighter System - Stats, Attributes & Character Design

## Overview

Every fighter in the AFL is a fully realized character with physical attributes, combat
skills, psychological traits, supernatural abilities (if any), and a rich personal history.
The stat system serves two purposes:

1. **Mechanical**: Feed into the match simulation engine to calculate win probabilities
2. **Narrative**: Give fans something tangible to follow, debate, and use to assess matchups

---

## Stat Categories

### Physical Attributes (1-100 scale)

These are the fighter's raw physical capabilities. They change slowly over time through
training, aging, injuries, and enhancements.

| Stat | Description | Example Impact |
|---|---|---|
| **Strength** | Raw hitting power, grappling force, ability to overpower | KO probability, clinch dominance |
| **Speed** | Striking speed, footwork, reaction time | Strike accuracy, evasion, first-strike advantage |
| **Endurance** | Cardio, ability to sustain output over rounds | Late-round performance, recovery between rounds |
| **Durability** | Chin, body toughness, resistance to damage | KO resistance, ability to absorb punishment |
| **Flexibility** | Range of motion, kick height, submission escape | Submission defense, kick variety, ground mobility |
| **Size** | Height and frame relative to other fighters | Reach advantage, clinch leverage, power differential |
| **Reach** | Arm and leg length relative to frame | Striking distance control, jab effectiveness |
| **Recovery** | How fast they heal between fights, bounce back in fights | Time between fights, mid-fight second winds |

### Combat Skills (1-100 scale)

Trained abilities that improve through practice, coaching, and fight experience.

| Stat | Description | Example Impact |
|---|---|---|
| **Striking** | Punching technique, combinations, timing | Damage output standing, counter-striking |
| **Kicking** | Kick technique, variety, power | Range attacks, leg damage, head kick KOs |
| **Wrestling** | Takedowns, takedown defense, top control | Fight location control, ground-and-pound |
| **Grappling** | Submissions, sweeps, guard work | Finish rate on ground, reversal ability |
| **Clinch Work** | Dirty boxing, knees, trips, wall work | Close-range damage, control |
| **Defense** | Head movement, blocking, parrying | Damage mitigation, counter opportunities |
| **Fight IQ** | Reading opponents, adapting mid-fight, game planning | Adjustments between rounds, exploiting weaknesses |
| **Finishing Instinct** | Ability to close out a hurt opponent | Finish rate when opponent is rocked |

### Psychological Attributes (1-100 scale)

The mental and emotional side of fighting. These fluctuate more than physical stats and are
heavily influenced by story events.

| Stat | Description | Example Impact |
|---|---|---|
| **Aggression** | Tendency to push forward and take risks | Pace of fight, risk/reward of exchanges |
| **Composure** | Staying calm under pressure, when hurt | Recovery from being rocked, not panicking |
| **Confidence** | Self-belief, swagger, performing when it matters | Performance in big fights, bouncing back from losses |
| **Intimidation** | Ability to psychologically affect opponents pre/during fight | Opponent confidence debuff, early aggression advantage |
| **Resilience** | Mental toughness, refusing to quit, comeback ability | Late stoppage resistance, heart in tough fights |
| **Focus** | Ability to stick to game plan, ignore distractions | Consistency, resistance to trash talk/mind games |
| **Killer Instinct** | Willingness to inflict serious damage, go for the kill | Finish rate, brutality of victories |
| **Emotional Stability** | Baseline mood regulation, resistance to tilt | Consistency across fights, handling adversity |

### Supernatural / Special Attributes (0-100 scale, 0 = none)

Not every fighter has these. They should be rare and narratively earned (demonic pact,
ancient bloodline, experimental program, etc.). A fighter might have 1-2 of these at most.

| Stat | Description | Example Impact |
|---|---|---|
| **Arcane Power** | Raw magical energy, spell potency | Magical attack damage, ability frequency |
| **Dark Arts** | Cursing, fear projection, life drain | Opponent debuffs, psychological warfare |
| **Divine Blessing** | Holy protection, healing, righteous fury | Damage resistance, recovery, anti-dark-arts |
| **Psychic Ability** | Mind reading, telekinesis, precognition | Anticipating attacks, mental attacks |
| **Elemental Affinity** | Control of fire, ice, lightning, etc. | Elemental strikes, environmental effects |
| **Chi Mastery** | Internal energy manipulation, pressure points | Precision strikes, energy projection, healing |
| **Blood Rage** | Power that grows with damage taken | Comeback mechanic, berserker state |
| **Seduction** | Charm, physical allure, psychological distraction, desire manipulation — ranges from natural charisma and attractiveness to supernaturally enhanced magnetism | Opponent hesitation, focus disruption, poor decision-making, emotional engagement that compromises tactical thinking |

> **Design Note**: Supernatural abilities should never be a guaranteed win button. A fighter
> with 80 Arcane Power can still lose to a disciplined martial artist with 90 Focus and 85
> Composure who simply doesn't let the magic rattle them. The supernatural stuff creates
> interesting matchup dynamics, not power imbalances.

---

## Derived / Situational Stats

These aren't set directly but are calculated from combinations of other stats and current
conditions:

| Derived Stat | Formula (conceptual) | Purpose |
|---|---|---|
| **Cardio Curve** | Endurance + Age + Training | How output changes across rounds |
| **Chin Rating** | Durability + Composure + Recovery | True KO resistance |
| **Ground Game** | (Wrestling + Grappling) / 2 | Overall ground effectiveness |
| **Standup Game** | (Striking + Kicking + Defense) / 3 | Overall standup effectiveness |
| **Threat Level** | Overall stat composite + special abilities | General power ranking metric |
| **Momentum** | Recent win/loss + confidence + crowd energy | In-fight momentum swings |
| **Heart** | Resilience + Composure + Confidence | Ability to survive when outmatched |

---

## Fighter Profile Structure

Every fighter should have these components:

### Identity
- **Ring Name**: Their fighting name (e.g., "The Crimson Widow")
- **Real Name**: Their actual name (sometimes unknown)
- **Age**: Current age (affects physical decline, experience)
- **Origin**: Where they're from (city, country, dimension, whatever)
- **Affiliation**: Faction, gym, syndicate, or independent

### Physical Description
- **Height & Weight**: Specific measurements
- **Build**: Body type description (lean, stocky, massive, wiry, etc.)
- **Distinguishing Features**: Scars, tattoos, cybernetics, glowing eyes, etc.
- **Ring Attire**: What they wear to fight
- **Entrance Style**: How they enter the arena

### Personality
- **Alignment**: Face (hero), Heel (villain), Tweener (ambiguous)
- **Personality Summary**: 2-3 sentences capturing their essence
- **Motivations**: Why they fight (money, glory, revenge, survival, fun, etc.)
- **Fears**: What haunts them
- **Quirks**: Unique behaviors, catchphrases, rituals
- **Relationships**: Key connections to other fighters (rivals, allies, lovers, mentors)

### Backstory
- **Origin Story**: How they got into fighting (2-3 paragraphs)
- **Rise to the League**: How they ended up in AFL
- **Key Life Events**: Formative moments that shaped them
- **Secrets**: Things not publicly known (for future story reveals)

### Fighting Style
- **Primary Style**: Their base martial art / approach
- **Secondary Style**: Supporting techniques
- **Signature Moves**: 2-3 named techniques they're known for
- **Finishing Move**: Their trademark fight-ender
- **Weaknesses**: Known exploitable gaps in their game
- **Style Description**: A prose description of how they actually fight

---

## Character Archetypes (Starter Templates)

These are starting points for character generation, NOT rigid categories. Characters should
blend and subvert archetypes.

### The Prodigy
Young, talented, maybe too confident. Incredible raw skills but untested mentally.
Fans love to root for them or watch them get humbled.
- High physical stats, high skills, lower psychological stats
- Story arc: Rise, hubris, fall, comeback (or destruction)

### The Veteran
Been here forever. Body is breaking down but fight IQ is unmatched.
Every fight might be their last.
- Declining physical stats, maxed skills and fight IQ, high composure
- Story arc: One last run, legacy fights, mentoring the next generation

### The Monster
Physically dominant, possibly enhanced. Not here for glory — here for destruction.
- Extreme physical stats, moderate skills, high aggression/killer instinct
- Story arc: Unstoppable force meets immovable object, finding humanity, or losing it

### The Technician
Boring to casual fans, terrifying to fighters. Clinical, efficient, always in control.
- Balanced physicals, very high skills, high fight IQ and composure, low aggression
- Story arc: Efficiency vs. heart, what happens when the plan fails

### The Wildcard
Unpredictable, unorthodox, maybe a little unhinged. Exciting to watch but inconsistent.
- Unusual stat distribution, high some areas and low in others
- Story arc: Genius or madman, moments of brilliance vs. self-destruction

### The Mystic
Taps into supernatural forces. Might be a monk, a warlock, a psychic, or something weirder.
- Moderate physicals, high supernatural stats, thematic skills
- Story arc: Power vs. corruption, mastery vs. losing control

### The Survivor
Has no business being here on paper. Outstatted in every fight. But they just won't die.
- Below-average physicals, average skills, extreme resilience/composure/heart
- Story arc: The ultimate underdog, Rocky Balboa energy, inspiring or tragic

### The Seductress/Seductor
Uses beauty, charm, and desire as a weapon. Fights dirty in every sense — how they dress,
how they move, how they talk to opponents, how they use proximity and body language in the
clinch, how they get under your skin.
- Moderate physicals, high seduction/intimidation, specialized skills
- Story arc: Manipulation, the line between weapon and vulnerability
- The best seductors don't need supernatural enhancement. Their weapon is human —
  confidence, style, the way they look at you, the way they make you feel. Supernatural
  charm is an amplifier, not a replacement. A fighter with Seduction 40 might have zero
  supernatural abilities — they're just genuinely attractive and know how to use it.

### The Experiment
Created, enhanced, or modified by some organization. Are they a person or a product?
- Artificially high stats in some areas, potential instability
- Story arc: Identity, rebellion against creators, humanity questions

### The Legacy
Son/daughter/student of a legendary past fighter. Living in someone else's shadow.
- Good all-around stats, strong foundation, confidence issues
- Story arc: Forge their own identity vs. live up to the legend

---

## Stat Progression & Change

Stats aren't static. Here's what causes them to change:

### Positive Changes
- **Training Arcs**: Focused training improves specific skills (+1-5 over weeks)
- **Fight Experience**: Competing improves fight IQ, finishing instinct (+1-2 per fight)
- **Confidence Boosts**: Big wins improve psychological stats (+2-5)
- **Mentorship**: Training under a veteran or master improves skills faster
- **Supernatural Growth**: Deepening connection to power source
- **Fan Sponsorship**: Funded training, better coaches, equipment

### Negative Changes
- **Injuries**: Physical stat reductions (temporary or permanent)
- **Aging**: Gradual physical decline after peak (varies by fighter, ~28-35 peak)
- **Psychological Damage**: Brutal losses can tank confidence, composure
- **Overtraining**: Pushing too hard without rest can reduce stats
- **Corruption**: Supernatural powers can have costs
- **Loss Streaks**: Compound psychological damage

### Catastrophic Changes
- **Career-Ending Injuries**: Massive permanent stat reductions
- **Psychological Breaks**: Mental stats crater after traumatic event
- **Supernatural Backlash**: Powers turning on the user
- **Death**: All stats go to zero. Permanently.

---

## Character Generation Guidelines

When AI generates new fighters, it should:

1. **Check existing roster** to avoid duplicating archetypes, origins, or fighting styles
2. **Consider current storyline needs** (do we need a new villain? a challenger for the champ?)
3. **Build from archetype blends** (e.g., Veteran + Mystic = aging sorcerer-warrior)
4. **Create at least one unique hook** that no other active fighter has
5. **Plant story seeds** in the backstory that connect to existing characters or future events
6. **Balance the roster** across size ranges, alignments, and fighting styles
7. **Vary the power level** — not every new fighter is a contender; some are jobbers, some are prospects
8. **Include flaws** — perfect characters are boring; every strength should imply a vulnerability

---

## Example Fighter Sketch

> **Ring Name**: "Sable" Morrigan Vex
> **Real Name**: Morrigan Vex
> **Age**: 26
> **Origin**: Dublin, Ireland (raised in a Traveller fighting family)
> **Affiliation**: Independent (formerly The Ashen Circle)
>
> **Physical**: 5'6", 145 lbs, lean and angular. Covered in Celtic knotwork tattoos that
> seem to shift in low light. Left eye is noticeably darker than the right. Moves like a
> dancer — always in motion, never flat-footed.
>
> **Personality**: Cold, calculating, darkly funny. Speaks softly and carries a devastating
> left hook. Trusts no one since leaving The Ashen Circle. Fights for money she sends home
> to her younger siblings.
>
> **Fighting Style**: Outfighter/counter-striker with chi mastery. Keeps opponents at range,
> reads their patterns, then dismantles them with precision counters. Her chi ability lets
> her sense attacks a split second before they land — but only when she's calm. Anger or
> emotional disruption breaks the connection.
>
> **Signature Moves**: "The Raven's Eye" (a perfectly timed counter cross that seems to
> anticipate the opponent's punch), "Thread the Needle" (slipping between combinations with
> impossible precision)
>
> **Finishing Move**: "Blackout Waltz" — a three-hit combination (slip, liver shot, delayed
> head kick) that she only throws when she's read the opponent completely. When it lands,
> they don't get up.
>
> **Weakness**: Pressure fighters who can get inside her range and stay there. When she can't
> keep distance, her chi sense gets overwhelmed by the chaos. Also: unresolved rage toward
> The Ashen Circle can be triggered, breaking her composure.
>
> **Story Hooks**: Why did she leave The Ashen Circle? Who taught her chi mastery? What
> happens when the Circle comes to collect?
