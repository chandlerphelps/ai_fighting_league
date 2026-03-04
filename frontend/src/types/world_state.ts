export interface RivalryRecord {
  fighter1_id: string
  fighter2_id: string
  fights: number
  fighter1_wins: number
  fighter2_wins: number
  draws: number
  is_rivalry: boolean
}

export interface MatchResult {
  fighter1_id: string
  fighter1_name: string
  fighter2_id: string
  fighter2_name: string
  winner_id: string
  method: string
  round_ended: number
  tier: string
  date: string
  start_time?: string
  is_title_fight?: boolean
}

export interface BeltHistoryEntry {
  fighter_id: string
  won_date: string
  lost_date: string | null
  defenses: number
}

export interface SeasonChampion {
  season: number
  fighter_id: string
  ring_name: string
  defeated_id: string
  defeated_name: string
}

export interface SeasonLog {
  season: number
  champion_name: string
  champion_id: string
  belt_holder_name: string
  belt_holder_id: string
  retirements: number
  new_fighters: number
  tier_counts: Record<string, number>
}

export interface ScheduledFight {
  tier: string
  fighter1_id: string
  fighter1_name: string
  fighter2_id: string
  fighter2_name: string
  start_time?: string
}

export interface WorldState {
  current_date: string
  day_number: number
  season_number: number
  season_month: number
  season_day_in_month: number
  tier_rankings: {
    apex: string[]
    contender: string[]
    underground: string[]
  }
  belt_holder_id: string
  belt_history: BeltHistoryEntry[]
  season_champions: SeasonChampion[]
  retired_fighter_ids: string[]
  active_injuries: Record<string, number>
  rivalry_graph: RivalryRecord[]
  recent_matches: MatchResult[]
  season_logs: SeasonLog[]
  promotion_fights: unknown[]
  title_fight: Record<string, string>
  scheduled_fights: ScheduledFight[]
  rankings: string[]
  upcoming_events: string[]
  completed_events: string[]
  last_daily_summary: string
  event_counter: number
}

export interface DaySimulationResult {
  season: number
  month: number
  day: number
  date: string
  matches: MatchResult[]
  recoveries: { fighter_id: string; fighter_name: string }[]
  phase: string
  season_end?: {
    retirements: number
    new_fighters: number
    backfill_promotions: number
  }
}
