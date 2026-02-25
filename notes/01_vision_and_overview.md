# AI Fighting League - Vision & Overview

> **Note**: This document describes the **finished-product vision** — the full scope of what
> AFL could become. We will cut this down to an MVP for the initial build and expand toward
> this vision over time.

## The Elevator Pitch

AI Fighting League is a **narrative-driven combat simulation** where AI-generated fighters
live, fight, rise, fall, and sometimes die in a persistent world. Think **WWE's storytelling**
meets **UFC's legitimacy** meets **Mortal Kombat's insanity** — all powered by AI that generates
rich, evolving narratives fans can follow in real-time.

Fights aren't pre-scripted. AI sets the odds, randomness determines outcomes, and then AI
crafts a blow-by-blow narrative of how it all went down. Characters have real stats, real
injuries, real grudges, and real consequences.

---

## Core Pillars

### 1. Narrative First
Every fight exists inside a story. Rivalries, betrayals, redemption arcs, tragic deaths,
unexpected comebacks — the league is a living soap opera with fists. Characters don't just
have stats; they have childhood traumas, mentors they lost, lovers who distract them, and
demons (sometimes literal ones) they're fighting.

### 2. Real Consequences
Fighters can be injured, permanently scarred, psychologically broken, or killed. When a
character dies, they're gone. This creates genuine stakes that keep fans invested. A beloved
character entering a death-match against a known killer should make fans sweat.

### 3. Controlled Chaos
Outcomes aren't scripted, but they aren't purely random either. A fighter's stats, mental
state, injuries, training, and even their emotional relationships all factor into win
probabilities. The AI sets odds; the dice decide fate; then AI tells us how it happened.

### 4. Deep Lore, Easy Entry
The league should be approachable for newcomers (here's tonight's fight card, here are the
two fighters, here's why they hate each other) while rewarding long-time followers with deep
interconnected storylines and callbacks to past events.

### 5. Fan Agency
Fans aren't passive. They can sponsor fighters, invest in their careers, fund training arcs,
and share in their glory (or their downfall). This creates personal attachment and a reason
to keep coming back.

---

## What Makes This Different

| Traditional Sports Sim | AI Fighting League |
|---|---|
| Stats-driven outcomes | Stats + narrative + psychology + chaos |
| Characters are interchangeable | Characters have deep, evolving stories |
| Injuries are mechanical | Injuries have narrative weight |
| Seasons reset | Consequences are permanent |
| Fans watch | Fans participate and invest |
| Fights are the product | Stories are the product; fights are climactic moments |

---

## The Experience Loop

```
1. BETWEEN FIGHTS (Days/Weeks)
   - Training montages and skill development
   - Rivalries brewing via trash talk, ambushes, betrayals
   - New fighters arriving with mysterious backstories
   - Injuries healing (or not healing)
   - Fan sponsorship and investment decisions
   - Alliances forming and breaking

2. FIGHT NIGHT (The Main Event)
   - Pre-fight narratives (weigh-ins, staredowns, last words)
   - AI calculates win probabilities based on all factors
   - Random outcome determination
   - AI generates beat-by-beat fight narrative
   - Post-fight consequences (injuries, deaths, emotional fallout)
   - Rankings update, new rivalries born

3. AFTERMATH
   - Winner's glory / loser's despair
   - Medical reports on injuries
   - Story threads advance
   - New matchups teased
   - Fan investments pay out (or don't)
```

---

## Tone & World

The world of AFL is **heightened reality**. It's not pure fantasy and it's not pure sports sim.
Think of it as our world but turned up to 11:

- Fighters can use **martial arts, street fighting, wrestling, magic, psychic powers,
  seduction, divine intervention, cybernetic enhancements, demonic pacts** — anything goes
  as long as it's narratively earned
- The league itself has **rules** (weight classes, match types, banned techniques) but those
  rules exist to be tested and sometimes broken
- There are **factions, crime syndicates, ancient orders, government experiments, and cosmic
  forces** all feeding fighters into the league
- **Death is real** but not common — maybe 2-5% of fights end in death depending on match type
- The **commentary and journalism** around the league treats everything with deadpan seriousness,
  like sports media covering genuinely insane events

---

## Visual Aesthetic & Art Direction

### Core Aesthetic: Retro Pixel Art

The visual identity of AFL draws directly from the **golden age of arcade fighters** —
specifically the **Mortal Kombat II** and **Street Fighter II** era. Think chunky, expressive
pixel art with bold colors, exaggerated proportions, and a style that oozes personality.

- **Resolution feel**: 16-bit era pixel art — detailed enough to read character and emotion,
  stylized enough to be iconic rather than realistic
- **Animation style**: Fluid sprite-style animations for idle poses, taunts, signature moves
- **Portraits**: Every fighter gets a large, detailed pixel art portrait (think the character
  select screen from SF2 Turbo) — these are the "face" of the fighter on profiles and fight cards
- **Fight scenes**: Pixel art stages with atmospheric backgrounds, animated crowds, and
  environmental details (rain, fire, flickering arena lights)
- **UI**: Pixel-styled health bars, stat displays, and menus — the whole interface should
  feel like you're inside a 90s arcade cabinet, but with modern polish

### Character Design Philosophy

Both male and female fighters should lean into **sex appeal and attractive physique design**.
This is a heightened, fantastical world — characters should look like they could be on the
cover of a pulp comic or a fighting game select screen. We are not afraid of skimpy outfits,
defined muscles, exposed skin, and provocative poses.

**Design Principles:**
- **Male fighters**: Chiseled, powerful builds. Shirtless, harness-wearing, torn-pants energy.
  Think Liu Kang, Johnny Cage, Ryu — idealized warrior physiques
- **Female fighters**: Strong, athletic, and sexy. Think Chun-Li's thighs, Cammy's leotard,
  Kitana's confidence. Outfits that are designed to turn
  heads — crop tops with underboob, thongs, micro and sling bikinis, high-cut leotards, thigh-highs, exposed midriffs
- **Both genders**: Attractiveness is a weapon in this world (literally — seduction is a stat).
  Characters should be designed to be visually striking and memorable. Every fighter should
  have a silhouette you could recognize instantly
- **Variety within sexiness**: Not everyone is the same body type. A massive brawler and a
  lithe assassin should both look good but in completely different ways
- **Supernatural flair**: Glowing tattoos, ethereal hair, demonic features, cybernetic
  enhancements — these layer on top of the base attractiveness to create truly unique designs

### Match Visualization Roadmap

The long-term vision for fight presentation evolves as AI visual technology matures:

**Phase 1 — Text & Pixel Art (MVP)**
- Fights are narrated in text with pixel art character portraits and sprite animations
  for key moments (signature moves, knockdowns, finishers)
- Static pixel art panels for major fight beats (like a comic book panel sequence)
- Think of it as a "visual novel" layer on top of the fight narrative JSON

**Phase 2 — Comic Book / Motion Comic Style**
- Full comic-book-style panel sequences generated by AI image generation
- Dynamic panel layouts (splash pages for knockouts, small rapid panels for combos)
- Speech bubbles for trash talk, crowd reactions, commentary
- The "live feed" of a match plays out as an animated comic — panels appearing one by one
  with sound effects and music
- This is the first version of a true "watchable" match experience

**Phase 3 — AI-Generated Video**
- As AI video generation technology matures, transition to actual animated fight sequences
- Start with short clips for key moments (finishing moves, knockouts, dramatic exchanges)
- Expand to full fight video generation as the tech allows
- Maintain the stylized aesthetic — this should never look like realistic footage, it should
  look like a beautifully animated fighting game or anime
- The pixel art DNA should still be visible: cel-shaded, bold outlines, exaggerated impact
  frames, screen shake

> **Key Principle**: Each visual phase should enhance the narrative, not replace it. The
> text-based fight narrative is the foundation — visual layers are added on top. A fight
> should be compelling to read even without visuals.

---

## Content Cadence

The league operates on a **daily timeline** where each day advances the world state:

- **Daily**: Minor story beats, training updates, social media posts from fighters, rumors
- **Weekly**: 1-2 smaller fight cards (undercard bouts, regional fights, proving grounds)
- **Bi-weekly**: Major fight nights with 4-6 bouts including at least one title fight
- **Monthly**: Special events (tournaments, grudge match nights, "The Crucible" death matches)
- **Quarterly**: Major PPV-style events with culminating storylines

---

## Success Metrics (North Stars)

1. **Fan retention**: Do people come back daily to check on their fighters?
2. **Emotional investment**: Are fans genuinely upset when a character loses/dies?
3. **Narrative quality**: Do the AI-generated stories feel cohesive and compelling?
4. **New character freshness**: Do new fighters feel distinct and interesting?
5. **Monetization engagement**: Are fans actively investing/sponsoring?

---

## Risks & Challenges

- **Narrative coherence**: Keeping AI-generated stories consistent over long timelines
- **Character freshness**: Avoiding repetitive archetypes as we generate dozens of fighters
- **Death economy**: Too many deaths = nihilism; too few = no stakes
- **Power creep**: Preventing fighters from becoming so powerful they break the system
- **Story complexity**: Managing an ever-growing web of relationships and history
- **AI reliability**: Ensuring fight narratives are exciting, not repetitive or nonsensical

---

## What We're Building (Phases)

### Phase 1: Core Engine (Now)
- Fighter creation system with stats and backstories
- Match simulation engine (probability + random + narrative)
- Basic league structure and rankings
- Day-by-day world state progression
- Story tracking system

### Phase 2: Live Experience + Pixel Art Layer
- Real-time fight feed (JSON-driven beat-by-beat display)
- Pixel art character portraits, sprites, and fight scene panels
- Fighter profiles and history pages with pixel art designs
- Leaderboard and rankings display
- Fight card announcements and pre-fight narratives

### Phase 3: Fan Engagement + Comic Book Visuals
- Sponsorship system
- Investment/wagering mechanics
- AI-generated comic book panel fight sequences (motion comic style)
- Fan influence on matchmaking
- Community features

### Phase 4: AI Video + Scale
- AI-generated video clips for key fight moments → full fight animation
- Multiple leagues/divisions
- Cross-promotion events
- Historical archive and lore wiki
- Content creator tools
