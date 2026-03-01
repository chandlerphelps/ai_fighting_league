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

export interface CharsheetPrompt {
  style: string
  layout: string
  body_parts: string
  clothing: string
  front_view: string
  center_pose: string
  back_view: string
  expression: string
  full_prompt: string
}

export interface Move {
  name: string
  description: string
  stat_affinity: string
  image_snapshot?: string
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
  iconic_features?: string
  personality?: string
  image_prompt_personality_pose?: string
  ring_attire: string
  ring_attire_sfw: string
  ring_attire_nsfw: string
  skimpiness_level?: number
  image_prompt: CharsheetPrompt
  image_prompt_sfw: CharsheetPrompt
  image_prompt_nsfw: CharsheetPrompt
  stats: Stats
  record: Record
  condition: Condition
  storyline_log: string[]
  moves?: Move[]
  rivalries: string[]
  last_fight_date: string | null
  ranking: number | null
  _available_images?: string[]
}
