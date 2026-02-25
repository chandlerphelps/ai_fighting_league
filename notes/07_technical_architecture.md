# Technical Architecture

## Overview

This document outlines how the AFL system is structured technically. The architecture
needs to handle:

1. **Persistent world state** that grows and evolves daily
2. **AI integration** for probability calculation, narrative generation, and story management
3. **Structured data output** (JSON) for programmatic display of fights
4. **Complex relationship graphs** between characters
5. **Historical continuity** across potentially thousands of events
6. **Future frontend integration** for live fight displays and fan interaction

---

## System Architecture (High Level)

```
┌─────────────────────────────────────────────────────────┐
│                     AFL CORE ENGINE                      │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│  World   │  Match   │ Narrative│  League  │    Fan      │
│  State   │  Engine  │  Engine  │  Manager │  Economy    │
│  Manager │          │          │          │             │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│                    DATA LAYER                             │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│ Fighters │  Story   │  Match   │ Rankings │ Transactions│
│    DB    │  Graph   │ History  │   DB     │     DB      │
├──────────┴──────────┴──────────┴──────────┴─────────────┤
│                   AI SERVICES LAYER                       │
├──────────┬──────────┬──────────┬────────────────────────┤
│Probability│Narrative │  Story   │  Character             │
│Calculator │Generator │Progressor│  Generator             │
└──────────┴──────────┴──────────┴────────────────────────┘
```

---

## Core Components

### 1. World State Manager

The central authority on "what is true right now" in the AFL universe.

**Responsibilities:**
- Maintain the current state of every fighter (stats, condition, location, mood)
- Track the current date and upcoming schedule
- Process daily ticks (advance the world by one day)
- Ensure consistency (no contradictions in world state)
- Provide snapshots for AI context

**Data Model:**

```
WorldState {
  current_date: Date
  active_fighters: [FighterId]
  retired_fighters: [FighterId]
  deceased_fighters: [FighterId]
  active_arcs: [ArcId]
  upcoming_events: [Event]
  recent_results: [FightResult]  // last 30 days
  league_announcements: [Announcement]
  global_modifiers: [Modifier]  // e.g., "Dark energy surge — supernatural abilities +10% this week"
}
```

### 2. Fighter Database

Every fighter's complete record.

**Data Model:**

```
Fighter {
  id: FighterId
  ring_name: String
  real_name: String
  age: Number
  origin: String
  affiliation: AffiliationId | null

  // Physical description (for AI narrative generation)
  physical_description: {
    height: String
    weight: Number
    build: String
    distinguishing_features: [String]
    ring_attire: String
    entrance_style: String
  }

  // Stats
  physical_stats: {
    strength: 1-100
    speed: 1-100
    endurance: 1-100
    durability: 1-100
    flexibility: 1-100
    size: 1-100
    reach: 1-100
    recovery: 1-100
  }

  combat_skills: {
    striking: 1-100
    kicking: 1-100
    wrestling: 1-100
    grappling: 1-100
    clinch_work: 1-100
    defense: 1-100
    fight_iq: 1-100
    finishing_instinct: 1-100
  }

  psychological: {
    aggression: 1-100
    composure: 1-100
    confidence: 1-100
    intimidation: 1-100
    resilience: 1-100
    focus: 1-100
    killer_instinct: 1-100
    emotional_stability: 1-100
  }

  supernatural: {
    arcane_power: 0-100
    dark_arts: 0-100
    divine_blessing: 0-100
    psychic_ability: 0-100
    elemental_affinity: 0-100
    chi_mastery: 0-100
    blood_rage: 0-100
    seduction: 0-100
  }

  // Character info
  personality: {
    alignment: "face" | "heel" | "tweener"
    summary: String
    motivations: [String]
    fears: [String]
    quirks: [String]
    speech_patterns: String
    behavioral_tendencies: String
  }

  backstory: {
    origin_story: String
    rise_to_league: String
    key_life_events: [LifeEvent]
    secrets: [Secret]
  }

  fighting_style: {
    primary_style: String
    secondary_style: String
    signature_moves: [SignatureMove]
    finishing_move: FinishingMove
    weaknesses: [String]
    style_description: String
  }

  // Current condition
  condition: {
    health: 1-100  // overall health
    injuries: [Injury]
    emotional_state: String
    training_status: String
    available: Boolean
    next_available_date: Date | null
  }

  // Record
  record: {
    wins: Number
    losses: Number
    draws: Number
    no_contests: Number
    ko_wins: Number
    submission_wins: Number
    decision_wins: Number
    special_wins: Number
    ko_losses: Number
    submission_losses: Number
    decision_losses: Number
    current_streak: { type: "win" | "loss", count: Number }
    title_history: [TitleReign]
    fight_history: [FightResultSummary]
  }

  // Meta
  status: "active" | "injured" | "retired" | "deceased"
  division: DivisionId
  ranking: Number | null  // null = unranked
  created_date: Date
  debut_date: Date
  retirement_date: Date | null
  death_date: Date | null

  // Fan economy
  share_price: Number
  total_sponsorship: Number
  sponsor_list: [SponsorId]
}
```

### 3. Story Graph

The relationship and narrative tracking system. This is where the complexity lives.

**Technology Choice**: A graph database (like Neo4j) or a graph-structured document
store would be ideal here, but we could start with a simpler approach using adjacency
lists in a document DB or even flat JSON files for the prototype.

**Data Model:**

```
StoryGraph {
  nodes: {
    fighters: [FighterNode]
    factions: [FactionNode]
    locations: [LocationNode]
    artifacts: [ArtifactNode]  // mystical items, weapons, etc.
    secrets: [SecretNode]
    events: [EventNode]
  }

  edges: [Relationship]

  arcs: [StoryArc]
}

Relationship {
  id: RelationshipId
  source: NodeId
  target: NodeId
  type: "rivalry" | "respect" | "alliance" | "mentorship" | "romance" |
        "family" | "betrayal" | "fear" | "debt" | "mystery" | "faction"
  intensity: 1-10
  history: [RelationshipEvent]  // timestamped changes
  current_status: String  // brief description
  public: Boolean  // is this known to the audience?
}

StoryArc {
  id: ArcId
  title: String
  type: "personal" | "rivalry" | "faction" | "romance" | "mystery" |
        "league_wide" | "legacy" | "corruption"
  status: "seeding" | "active" | "climax" | "resolution" | "dormant"
  participants: [NodeId]
  tension_level: 1-10
  priority: 1-10
  beats: [StoryBeat]  // what has happened
  planned_beats: [PlannedBeat]  // what might happen next (flexible)
  created_date: Date
  resolved_date: Date | null
  summary: String
}

StoryBeat {
  id: BeatId
  arc_id: ArcId
  date: Date
  type: String  // "social_media", "backstage", "press_conference", etc.
  description: String
  participants: [NodeId]
  impact: {
    relationship_changes: [RelationshipChange]
    stat_changes: [StatChange]
    arc_tension_change: Number
    new_arcs_spawned: [ArcId]
  }
  public: Boolean
  content: String  // the actual narrative text
}
```

### 4. Match Engine

Covered in detail in the Match Engine document (03). Technical notes:

**Pipeline:**
```
1. PREPARE CONTEXT
   - Load both fighter profiles from DB
   - Load relationship history between them
   - Load relevant active story arcs
   - Load match context (event, match type, stakes)
   - Compile into structured AI prompt

2. AI: CALCULATE PROBABILITIES
   - Send context to AI with probability calculation prompt
   - Receive structured probability response
   - Validate (within guardrails: 5-95% range, etc.)

3. RANDOM ROLL
   - Pure code, no AI: weighted random for winner, method, round, time
   - Calculate secondary outcomes (injuries, performance ratings)

4. AI: GENERATE NARRATIVE
   - Send full context + determined outcome to AI
   - Receive structured JSON fight narrative
   - Validate structure, consistency, timestamps

5. POST-PROCESS
   - Update fighter records, stats, conditions
   - Update rankings
   - Process injuries
   - Update story graph (relationships, arc progression)
   - Generate post-fight story hooks
   - Process fan economy (investment values, sponsorship effects)

6. PERSIST
   - Save fight result to match history
   - Save updated fighter states
   - Save updated story graph
   - Save narrative JSON for frontend consumption
```

### 5. Narrative Engine

The AI-powered system that generates all non-fight story content.

**Daily Story Generation Pipeline:**

```
1. LOAD CONTEXT
   - Current world state
   - All active story arcs with recent beats
   - All fighters' current conditions and emotional states
   - Scheduled upcoming events
   - What happened yesterday

2. AI: PLAN THE DAY
   - "Given this world state, what 2-5 story beats should happen today?"
   - AI returns a plan with beat types, participants, and brief descriptions
   - System validates (no contradictions, appropriate pacing)

3. AI: GENERATE EACH BEAT
   - For each planned beat, generate the full narrative content
   - Maintain character voice consistency
   - Reference relevant history

4. POST-PROCESS
   - Update story graph with new beats
   - Update relationship intensities
   - Update fighter emotional states
   - Advance arc tension levels
   - Check for arc status transitions (seeding → active, etc.)

5. PUBLISH
   - Story beats become available in chronological order
   - Some beats are "public" (social media, press conferences)
   - Some are "backstage" (revealed later or to premium subscribers)
```

### 6. League Manager

Handles the competitive structure.

**Responsibilities:**
- Maintain rankings per division
- Schedule events and fight cards
- Manage title lineages
- Track records and statistics
- Generate matchmaking recommendations

---

## AI Integration Strategy

### Which AI and When

The system makes heavy use of AI for creative content but keeps mechanical decisions
deterministic.

| Task | AI Role | Deterministic Role |
|---|---|---|
| **Fight probabilities** | AI analyzes matchup and sets odds | System validates within guardrails |
| **Fight outcome** | None | Random roll with weighted probabilities |
| **Fight narrative** | AI writes the entire blow-by-blow | System validates structure/consistency |
| **Daily story beats** | AI plans and writes story content | System validates timing/consistency |
| **New character generation** | AI creates the character | System validates stat balance/uniqueness |
| **Matchmaking** | AI suggests compelling matchups | System ensures ranking/scheduling logic |
| **Rankings** | None | Algorithm based on results |
| **Fan economy** | None | Deterministic formulas |

### AI Context Management

This is one of the trickiest technical challenges. The AI needs enough context to be
consistent, but we can't send it everything.

**Strategy: Layered Context**

```
Layer 1: ALWAYS INCLUDED (every AI call)
  - Current date
  - The specific fighters/entities involved in this request
  - Their full profiles and current condition
  - Direct relationships between them

Layer 2: RELEVANT CONTEXT (included when applicable)
  - Active story arcs involving these entities
  - Recent events (last 7-14 days) involving these entities
  - Upcoming scheduled events they're part of

Layer 3: BACKGROUND CONTEXT (summarized)
  - League-wide state summary
  - Major ongoing storylines not directly involving these entities
  - Tone/style guidelines

Layer 4: HISTORICAL CONTEXT (on demand)
  - Full fight history between specific fighters
  - Deep backstory details when needed for specific story beats
  - Long-running arc summaries when arcs need to reference old events
```

### Prompt Templates

Standardized prompt templates for each AI task:

1. **Probability Calculation Prompt**: Fighter profiles, matchup context, recent form → probabilities
2. **Fight Narrative Prompt**: Full context + determined outcome → JSON fight narrative
3. **Daily Story Beat Prompt**: World state + active arcs → story beat plan
4. **Story Beat Content Prompt**: Beat plan + character bibles → narrative content
5. **Character Generation Prompt**: Roster needs + existing roster → new character profile
6. **Matchmaking Prompt**: Rankings + active arcs + scheduling → fight card suggestions

---

## Data Storage

### For Prototype (Phase 1)

Start simple with file-based storage:

```
/data
  /fighters
    fighter_001.json
    fighter_002.json
    ...
  /matches
    match_001.json  (includes full fight narrative)
    match_002.json
    ...
  /story
    story_graph.json  (relationships and arcs)
    /beats
      2024-01-15.json  (all story beats for a day)
      2024-01-16.json
      ...
  /events
    event_001.json  (fight cards, results)
    ...
  /world
    current_state.json
    /snapshots
      2024-01-15_state.json  (daily snapshots for rollback)
      ...
  /rankings
    current_rankings.json
    /history
      2024-01-15_rankings.json
      ...
  /economy
    market_state.json
    /transactions
      ...
```

### For Production (Phase 2+)

- **Fighters & World State**: PostgreSQL or MongoDB (structured data with complex queries)
- **Story Graph**: Neo4j or similar graph database (relationship traversal is the key operation)
- **Match History & Narratives**: Document store (large JSON blobs, mostly read)
- **Rankings**: Redis for live data, PostgreSQL for history
- **Fan Economy**: PostgreSQL with strong transaction support
- **Daily Snapshots**: Object storage (S3 or similar) for point-in-time world states

---

## Fight Narrative Display Architecture

For the "live" fight experience on the frontend:

```
1. Fight narrative JSON is stored as complete document

2. Frontend loads the fight and displays it as a timed sequence:
   - Pre-fight intro plays
   - Round 1 begins
   - Events are revealed one at a time with appropriate timing delays
   - Between events, a timer advances
   - Crowd reactions, commentary appear at appropriate moments
   - Round ends, scorecard displays
   - Repeat for each round
   - Finish sequence plays
   - Post-fight content displays

3. The JSON structure supports:
   - Pause/resume (it's just a timeline)
   - Skip ahead (jump to any event)
   - Replay specific moments
   - Speed control (1x, 2x, skip to decision)
   - Different "camera angles" (fighter A focus, fighter B focus, neutral)
```

### Live vs. Replay

- **First viewing**: Events are revealed in real-time with dramatic pacing
- **Replay**: Full fight available with scrubbing, speed control, etc.
- **Highlights**: Auto-generated clips of key moments

---

## Visual Rendering Pipeline

The fight narrative JSON is the **single source of truth** for all visual layers. Each
rendering phase adds fidelity on top of the same underlying data.

### Phase 1: Pixel Art Layer (MVP)

**Assets Needed:**
- Character portrait sprites (pixel art, MK2/SF2 aesthetic) — idle, attack, defend, hurt,
  knockout, signature move, victory, defeat poses
- Stage backgrounds (pixel art arenas) — 5-10 distinct venues
- UI elements — health bars, round indicators, stat overlays, fight cards
- Effect sprites — impact flashes, blood, elemental effects, supernatural auras

**Rendering Approach:**
```
Fight Narrative JSON
  → Event Parser (maps narrative events to sprite animations)
  → Sprite Sequencer (assembles animation frames with timing from JSON)
  → Canvas/WebGL Renderer (displays pixel art fight sequence)
```

- Key narrative events trigger specific sprite animations
- Between events, fighters display idle/stance animations
- Knockdowns, signature moves, and finishers get special multi-frame sequences
- Pixel art style means the asset pipeline is manageable for a small team or AI generation

**Character Sprite Generation:**
- AI image generation (with pixel art fine-tuning/LoRA) can produce character sprites
  from fighter descriptions
- Each fighter needs: idle, jab, kick, block, hurt, knockdown, victory, defeat, entrance
- Signature/finishing moves get unique sprite sequences
- The pixel art style is forgiving — stylization hides imperfections in AI generation

### Phase 2: Comic Book / Motion Comic

**Assets Needed:**
- AI-generated comic panels for key fight moments
- Panel layout templates (action sequences, splash pages, dramatic reveals)
- Speech bubble system for trash talk and commentary
- Sound effect typography (WHAM, CRACK, etc.)

**Rendering Approach:**
```
Fight Narrative JSON
  → Panel Planner (selects key moments, assigns panel types/sizes)
  → AI Image Generator (generates each panel from narrative description + character refs)
  → Comic Layout Engine (assembles panels into pages with speech bubbles & SFX)
  → Animated Reveal (panels appear sequentially with transitions)
```

- The fight narrative JSON contains enough detail to prompt AI image generation for each panel
- Character reference sheets (generated from pixel art portraits + descriptions) ensure
  visual consistency across panels
- Key moments get splash pages; rapid exchanges get small sequential panels
- The motion comic player reveals panels with timing, zoom, and transition effects

### Phase 3: AI Video Generation

**Rendering Approach:**
```
Fight Narrative JSON
  → Scene Planner (breaks narrative into video shots/sequences)
  → AI Video Generator (generates short clips per scene)
  → Video Compositor (stitches clips, adds HUD, sound, commentary)
  → Streaming Player (delivers fight as video stream)
```

- Start with **key moment clips only** (10-30 second clips for knockdowns, finishers, etc.)
- Expand to **full fight generation** as model capabilities and cost allow
- Maintain stylized aesthetic — cel-shaded / anime-inspired, NOT photorealistic
- Character consistency across clips is the main technical challenge — solve with
  character LoRAs or reference-based generation
- The pixel art / comic book layers remain available as fallback and for lower-bandwidth
  viewing

---

## System Reliability

### Consistency Guarantees

- **World state snapshots**: Daily snapshots allow rollback if something goes wrong
- **AI output validation**: Every AI response is validated against schemas
- **Contradiction detection**: Before publishing any content, check against known facts
- **Manual override**: Admin tools to correct AI errors and adjust world state

### Failure Modes

| Failure | Mitigation |
|---|---|
| AI generates contradictory content | Validation layer catches it; retry with corrected context |
| AI generates low-quality narrative | Quality scoring; retry or flag for human review |
| Random outcome feels wrong | It's random — upsets happen. The narrative makes it work. |
| Story arc goes nowhere | AI story review flags stale arcs; force resolution or twist |
| Fighter power creep | Stat caps, aging mechanics, and narrative consequences keep things balanced |
| World state corruption | Daily snapshots allow rollback; event sourcing for full audit trail |

---

## Technology Stack (Recommended)

### Phase 1 (Prototype / CLI)

- **Language**: Python (fast to prototype, great AI library support)
- **Data Storage**: JSON files organized in directories
- **AI Provider**: Anthropic Claude API (strong narrative capability)
- **Random Number Generation**: Python's `random` module with seeded reproducibility
- **CLI Interface**: Rich library for terminal-based display during development

### Phase 2 (Web Application)

- **Backend**: Python (FastAPI) or Node.js (Express/Next.js)
- **Frontend**: React or Next.js with real-time fight display
- **Database**: PostgreSQL + Redis (or MongoDB if schema flexibility is valued)
- **Graph DB**: Neo4j for story graph (or start with PostgreSQL + adjacency tables)
- **AI Provider**: Anthropic Claude API
- **Hosting**: Cloud provider (AWS, GCP, or Vercel/Railway for simplicity)
- **Real-time**: WebSockets for live fight feed

### Phase 3 (Scale)

- **Add**: CDN for fight narratives, queue system for AI calls, caching layer
- **Add**: Payment processing (Stripe) for fan economy
- **Add**: Analytics pipeline for engagement metrics
- **Add**: Admin dashboard for league management

---

## Key Technical Decisions to Make

1. **AI model selection**: Which model for which task? Larger models for narrative,
   smaller/faster for daily beats?
2. **Context window management**: How much history can we fit in a prompt? Do we need
   RAG (retrieval augmented generation) for long histories?
3. **Reproducibility**: Should fights be reproducible from a seed? (Useful for debugging
   but reduces "magic")
4. **Event sourcing**: Should we store all events and rebuild state from them? (More
   robust but more complex)
5. **Human-in-the-loop**: Where do we need human review/override? (At least initially,
   probably quality-check major narrative moments)
6. **API rate limits**: How do we batch AI calls efficiently for daily story generation?
7. **Schema evolution**: How do we handle changes to fighter/match data models over time?
