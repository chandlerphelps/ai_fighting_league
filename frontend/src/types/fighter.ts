export interface FightingStyle {
  primary_style: string
  secondary_style: string
  signature_move: string
  finishing_move: string
  known_weaknesses: string[]
}

export interface PhysicalStats {
  strength: number
  speed: number
  endurance: number
  durability: number
  recovery: number
}

export interface CombatStats {
  striking: number
  grappling: number
  defense: number
  fight_iq: number
  finishing_instinct: number
}

export interface PsychologicalStats {
  aggression: number
  composure: number
  confidence: number
  resilience: number
  killer_instinct: number
}

export interface SupernaturalStats {
  arcane_power: number
  chi_mastery: number
  elemental_affinity: number
  dark_arts: number
}

export interface Record {
  wins: number
  losses: number
  draws: number
  kos: number
  submissions: number
}

export interface Injury {
  type: string
  severity: string
  recovery_days_remaining: number
}

export interface Condition {
  health_status: string
  injuries: Injury[]
  recovery_days_remaining: number
  morale: string
  momentum: string
}

export interface Fighter {
  id: string
  ring_name: string
  real_name: string
  age: number
  origin: string
  alignment: string
  gender: string
  height: string
  weight: string
  build: string
  distinguishing_features: string
  ring_attire: string
  backstory: string
  personality_traits: string[]
  fears_quirks: string[]
  fighting_style: FightingStyle
  physical_stats: PhysicalStats
  combat_stats: CombatStats
  psychological_stats: PsychologicalStats
  supernatural_stats: SupernaturalStats
  record: Record
  condition: Condition
  storyline_log: string[]
  rivalries: string[]
  last_fight_date: string | null
  ranking: number | null
}
