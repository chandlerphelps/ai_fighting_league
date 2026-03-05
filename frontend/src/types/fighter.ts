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

export interface TierRecord {
  wins: number
  losses: number
  draws: number
}

export interface PlanEntry {
  ring_name: string
  real_name?: string
  gender: string
  age?: number
  origin?: string
  primary_archetype: string
  subtype?: string
  has_supernatural: boolean
  supernatural_type?: string
  power_tier: string
  concept_hook: string
  alignment?: string
  fighting_style_concept?: string
  narrative_role?: string
  rivalry_seeds?: string[]
  media_archetype_inspiration?: string
  skimpiness_weights?: number[]
  primary_outfit_color: string
  hair_style: string
  hair_color: string
  face_adornment: string
  status: 'pending' | 'approved' | 'rejected' | 'generating'
  fighter_id?: string | null
}

export interface RosterPlan {
  plan_id: string
  created_at: string
  mode: 'initial' | 'addition'
  pool_summary: string
  entries: PlanEntry[]
}

export interface Fighter {
  id: string
  ring_name: string
  real_name: string
  age: number
  origin?: string
  gender: string
  height?: string
  weight?: string
  build?: string
  distinguishing_features?: string
  iconic_features?: string
  personality?: string
  primary_archetype?: string
  image_prompt_personality_pose?: string
  ring_attire?: string
  ring_attire_sfw?: string
  ring_attire_nsfw?: string
  skimpiness_level?: number
  primary_outfit_color?: string
  hair_style?: string
  hair_color?: string
  face_adornment?: string
  generation_stage?: number
  generation_dirty?: string[]
  image_prompt_portrait?: CharsheetPrompt
  image_prompt_headshot?: CharsheetPrompt
  image_prompt_body_ref?: CharsheetPrompt
  image_prompt?: CharsheetPrompt
  image_prompt_sfw?: CharsheetPrompt
  image_prompt_nsfw?: CharsheetPrompt
  stats: Stats
  record: Record
  condition: Condition
  storyline_log?: string[]
  moves?: Move[]
  rivalries?: string[]
  last_fight_date?: string | null
  ranking?: number | null
  tier?: string
  status?: string
  season_wins?: number
  season_losses?: number
  consecutive_losses?: number
  peak_tier?: string
  career_season_count?: number
  seasons_in_current_tier?: number
  tier_records?: { [key: string]: TierRecord }
  _available_images?: string[]
}
