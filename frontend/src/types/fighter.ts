export interface Stats {
  power: number
  speed: number
  technique: number
  toughness: number
  supernatural: number
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
  gender: string
  height: string
  weight: string
  build: string
  distinguishing_features: string
  ring_attire: string
  image_prompt: string
  stats: Stats
  record: Record
  condition: Condition
  storyline_log: string[]
  rivalries: string[]
  last_fight_date: string | null
  ranking: number | null
}
