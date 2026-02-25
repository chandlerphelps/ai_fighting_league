# Narrative & Story System

## Overview

The narrative system is the connective tissue of AFL. It's what turns a sequence of simulated
fights into a **living, breathing story world**. This document covers how stories are tracked,
how they evolve, and how we keep the narrative coherent as it branches and grows.

---

## Core Narrative Concepts

### Story Arcs

A story arc is a narrative thread that spans multiple events over time. Every active arc has:

- **Arc ID**: Unique identifier
- **Title**: Human-readable name (e.g., "The Ashen Circle Conspiracy")
- **Type**: Personal, rivalry, faction, league-wide, mystery
- **Status**: Seeding, active, climax, resolution, dormant
- **Participants**: Which fighters/entities are involved
- **Key Beats**: Ordered list of story moments that have occurred
- **Planned Beats**: Upcoming story moments (flexible, not locked)
- **Tension Level**: 1-10, how close this arc is to its climax
- **Priority**: How much screen time this arc should get

### Arc Types

| Type | Description | Duration | Example |
|---|---|---|---|
| **Personal** | Single fighter's internal journey | Weeks to months | "Can Vex control her rage?" |
| **Rivalry** | Two fighters' conflict | 2-6 fights | "Cole vs. Vex: Unfinished Business" |
| **Faction** | Group dynamics, power struggles | Months | "The Ashen Circle's Power Play" |
| **Romance** | Love/lust between characters | Ongoing | "The forbidden attraction between X and Y" |
| **Mystery** | Something unknown that unfolds | Variable | "Who poisoned the champion?" |
| **League-Wide** | Events affecting the whole league | Seasonal | "The Crucible Tournament" |
| **Legacy** | Generational stories, mentorship | Long-running | "Master Chen's Final Student" |
| **Corruption** | Power/supernatural decay | Slow burn | "The price of dark magic" |

### Arc Lifecycle

```
SEEDING (Tension: 1-3)
  Plant hints, introduce elements, audience doesn't know where it's going yet
  → "A mysterious figure watches from the crowd at three consecutive events"

DEVELOPMENT (Tension: 4-6)
  Story becomes visible, stakes become clear, audience is invested
  → "The figure is revealed as Vex's former mentor. He wants something."

ESCALATION (Tension: 7-8)
  Conflict intensifies, alliances shift, no going back
  → "The mentor challenges Vex: return to the Circle or he reveals her secret"

CLIMAX (Tension: 9-10)
  The decisive moment — a fight, a betrayal, a revelation
  → "Vex faces her mentor in the cage. Win, and she's free. Lose, and..."

RESOLUTION (Tension: winding down)
  Aftermath, consequences, new status quo
  → "Vex won, but at what cost? The secret is out. Everything changes."

DORMANT
  Arc is resolved but can be reactivated by new events
  → "Months later, someone else from the Circle appears..."
```

---

## The Story Graph

### Concept

All narrative elements exist in a **graph structure** where:

- **Nodes** are entities (fighters, factions, locations, objects, secrets)
- **Edges** are relationships with types and intensities

This allows us to:
1. Track how every character relates to every other character
2. Find organic story connections ("these two fighters both trained under the same master")
3. Prevent contradictions ("wait, she can't be in Tokyo, she's recovering in Dublin")
4. Generate new story ideas from existing connections

### Relationship Types

| Relationship | Description | Intensity Range |
|---|---|---|
| **Rivalry** | Competitive antagonism | 1 (mild dislike) to 10 (blood feud) |
| **Respect** | Professional admiration | 1 (grudging) to 10 (profound) |
| **Alliance** | Working together | 1 (convenience) to 10 (ride-or-die) |
| **Mentorship** | Teacher/student | 1 (casual) to 10 (life-defining) |
| **Romance** | Romantic/sexual connection | 1 (attraction) to 10 (consuming love) |
| **Family** | Blood or chosen family | 1 (estranged) to 10 (unbreakable) |
| **Betrayal** | Broken trust | 1 (minor slight) to 10 (unforgivable) |
| **Fear** | One fears the other | 1 (uneasy) to 10 (paralyzed) |
| **Debt** | Owes something | 1 (small favor) to 10 (life debt) |
| **Mystery** | Unknown connection | Revealed over time |
| **Faction** | Belong to same group | 1 (peripheral) to 10 (core member) |

### Relationship Evolution

Relationships change based on events:

```
EVENT: Fighter A defeats Fighter B in a close, respectful fight
→ Rivalry: +1, Respect: +2

EVENT: Fighter A trash-talks Fighter B's dead mentor
→ Rivalry: +3, Respect: -4, potential new arc: "Vengeance for Master X"

EVENT: Fighter A saves Fighter B from a post-fight attack
→ Rivalry: -2, Respect: +3, Alliance: +2, potential new arc: "Unlikely Allies"

EVENT: Fighter A and Fighter B's romantic tension boils over
→ Romance: +3, Focus (both): -5 for next fight, new arc: "Love in the League"
```

---

## Daily World State

The league advances **one day at a time**. Each day, the system processes:

### The Daily Tick

```
1. SCHEDULED EVENTS
   - Are there fights today? Process them.
   - Are there weigh-ins, press conferences, or events?
   - Any scheduled story beats?

2. INJURY & RECOVERY
   - Update all injured fighters' recovery timelines
   - Check if anyone is cleared to return
   - Check if any injuries worsened

3. TRAINING
   - Fighters in training camps progress their stats
   - Training incidents can occur (injury, breakthrough, conflict with training partner)

4. STORY PROGRESSION
   - AI reviews all active arcs and advances them where appropriate
   - Generate 1-3 minor story beats for the day
   - Social media posts from fighters, journalists, fans

5. RELATIONSHIP UPDATES
   - Process any relationship changes from today's events
   - Check for emerging organic storylines from relationship states

6. NEW CONTENT CHECK
   - Does the roster need fresh blood? Flag for new character generation.
   - Are any arcs stale? Flag for resolution or twist.
   - Any real-world calendar hooks? (holidays, anniversaries, etc.)

7. WORLD STATE SNAPSHOT
   - Save the complete state: all fighters, relationships, arcs, rankings
   - This becomes the foundation for tomorrow
```

### Story Beat Types

| Beat Type | Description | Frequency |
|---|---|---|
| **Social Media Post** | Fighter posts something revealing or provocative | Daily |
| **Training Update** | Fighter's camp reports progress or issues | Every few days |
| **Backstage Encounter** | Two fighters cross paths, tension or bonding | Weekly |
| **Press Conference** | Public statements, trash talk, announcements | Pre-fight week |
| **Ambush/Attack** | One fighter attacks another outside a match | Rare, high impact |
| **Revelation** | A secret is revealed | Arc-dependent |
| **Alliance Formed** | Two+ fighters officially team up | As story demands |
| **Betrayal** | An ally turns enemy | Rare, very high impact |
| **Injury Report** | Medical update changes a fighter's trajectory | Post-fight |
| **New Arrival** | A new fighter enters the league | Monthly or so |
| **Death Aftermath** | The ripple effects of a fighter's death | When it happens |
| **Title Challenge** | A fighter formally challenges for a belt | Bi-weekly |
| **Faction Move** | A faction makes a power play | Monthly |
| **Mysterious Event** | Something unexplained happens | Irregular |

---

## Character Voice & Consistency

### The Character Bible

Every fighter has an AI-accessible "character bible" that includes:

1. **Speech patterns**: How they talk (formal? slang? accent notes? terse? verbose?)
2. **Behavioral tendencies**: How they react to provocation, victory, defeat, love, fear
3. **Values**: What they won't compromise on, what they'll sacrifice anything for
4. **Knowledge state**: What this character knows and doesn't know in-story
5. **Emotional state**: Current mood, recent events affecting them
6. **Relationships summary**: Quick reference for all active connections

### Consistency Rules

When generating any story content involving a character:

- Always reference the character bible
- Check recent events that would affect their mood/behavior
- Verify factual consistency (location, injury status, knowledge state)
- Match their established speech patterns
- Evolve naturally — characters change, but changes must be earned

---

## Introducing New Characters

New characters should never feel random. They should feel **inevitable** — like the story
was building toward their arrival. Methods:

### The Tease (2-4 weeks before debut)
1. Mysterious references from existing characters ("I heard someone's coming from the Eastern Circuit...")
2. Cryptic social media posts from an unknown account
3. Brief appearances in crowd/background of events
4. Journalists reporting rumors
5. A known character's past is revealed to involve someone new

### The Debut
- **Challenge Debut**: New fighter interrupts a post-fight celebration to issue a challenge
- **Rescue Debut**: New fighter saves someone from a post-fight beating
- **Attack Debut**: New fighter ambushes a known character
- **Tournament Debut**: New fighter enters through an open qualifier
- **Faction Debut**: Revealed as a new member of an existing faction
- **Legacy Debut**: Revealed as connected to a retired/dead fighter
- **Mysterious Debut**: Appears with no explanation, identity unknown at first

### Integration
After debut, the new character needs:
- At least 2 connections to existing characters within 2 weeks
- A clear initial arc established within 1 week
- A debut fight within 2 weeks
- At least one mystery/hook that makes fans want to know more

---

## WWE-Inspired Narrative Patterns

These are proven storytelling structures we should use as building blocks:

### The Heel Turn
A beloved character betrays their allies or values. Requirements:
- Must be foreshadowed (subtle signs over weeks)
- Must have a believable motivation (not random evil)
- Must create at least 2 new story arcs (betrayal aftermath + villain arc)
- The turn moment should be a genuinely shocking scene

### The Face Turn / Redemption Arc
A villain finds their humanity. Requirements:
- Must be earned through suffering or genuine change
- Must not erase what they did — consequences persist
- Should be gradual, not a single moment
- The audience should be divided on whether to trust them

### The Unbeatable Monster
One fighter becomes seemingly unstoppable. Requirements:
- Needs at least 4-5 dominant wins to establish the threat
- Every other fighter should react with fear/strategy
- The eventual defeat must be built up as a seemingly impossible task
- Can end with a David vs. Goliath moment OR the monster wins and the story continues

### The Underdog Journey
A lesser fighter rises through heart and determination. Requirements:
- Must start with legitimate losses and setbacks
- Every win should feel earned, never easy
- The big moment (title shot, revenge match) must be delayed and built toward
- Works best when paired with a dominant champion to contrast against

### The Forbidden Romance
Two characters on opposing sides develop feelings. Requirements:
- Creates conflict with their respective allies/factions
- Must affect their fighting (loss of focus, pulling punches, etc.)
- Should force a choice: love or loyalty
- Can end in tragedy, betrayal, or unlikely unity

### The Mystery
Something unexplained that the audience wants to solve. Requirements:
- Plant genuine clues that fans can piece together
- Red herrings that are fair but misleading
- The reveal must be satisfying and make sense retroactively
- Should connect to existing characters in surprising ways

### The Passing of the Torch
A veteran's final chapter anoints a new star. Requirements:
- The veteran must be established as legendary
- The new fighter must earn the veteran's respect
- The final fight between them should be the emotional peak
- The veteran's retirement/death should resonate through the story

---

## Handling Fighter Death

Death is the highest-stakes narrative tool. It must be handled carefully:

### Before Death
- Death should be foreshadowed (dangerous match type, powerful opponent, declining health)
- The audience should feel genuine dread, not certainty
- The fighter's open story arcs should be at interesting points (not all resolved)
- Other characters should react to the danger beforehand

### The Death Itself
- Should be narrated with gravity, not gratuitously
- The fight leading to death should be the fighter's best narrative — going out swinging
- Other characters' real-time reactions matter
- The moment should feel significant, not random

### After Death
- Immediate shockwaves through the roster (grief, rage, guilt, fear)
- The killer faces consequences (guilt, celebration, reputation change)
- The dead fighter's open arcs become other characters' arcs
  - "Vex was investigating the Circle. Now that she's gone, who picks up the thread?"
- Memorial events, tribute fights, legacy effects
- Their training partners, lovers, rivals all get new story material
- The death should affect the league for weeks/months, not be forgotten quickly

### Death Frequency
- **Target**: ~2-5% of fights in dangerous match types, much less in standard bouts
- **Rough pace**: Maybe 1-3 deaths per quarter across the whole league
- **Never**: Two fan-favorite deaths in close succession (let the first one breathe)
- **Always**: Death should feel possible but never expected

---

## Story Quality Metrics

How we assess whether the narrative system is working:

1. **Coherence Score**: Do story beats contradict each other? (Check via AI review)
2. **Character Consistency**: Do characters behave in-character? (Check against bible)
3. **Arc Completion Rate**: Are arcs reaching satisfying conclusions?
4. **Arc Diversity**: Is there a healthy mix of arc types active at any time?
5. **Connection Density**: Are new characters integrated into the story graph quickly?
6. **Surprise Factor**: Are there genuine twists, or is everything predictable?
7. **Emotional Range**: Does the story hit different emotions (joy, fear, anger, sadness)?
8. **Fan Engagement Proxies**: Which arcs generate the most discussion/investment?
