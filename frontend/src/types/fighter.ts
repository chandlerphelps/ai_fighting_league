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

export interface ImagePrompt {
  style: string
  pose: string
  body_parts: string
  clothing: string
  expression: string
  full_prompt: string
}

export interface ImagePromptTriple {
  style: string
  composition: string
  pose: string
  body_parts: string
  left: string
  center: string
  right: string
  expression: string
  full_prompt: string
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
  ring_attire_sfw: string
  ring_attire_nsfw: string
  image_prompt: ImagePrompt
  image_prompt_sfw: ImagePrompt
  image_prompt_nsfw: ImagePrompt
  image_prompt_triple: ImagePromptTriple
  stats: Stats
  record: Record
  condition: Condition
  storyline_log: string[]
  rivalries: string[]
  last_fight_date: string | null
  ranking: number | null
}
