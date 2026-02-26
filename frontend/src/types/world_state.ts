export interface RivalryRecord {
  fighter1_id: string
  fighter2_id: string
  fights: number
  fighter1_wins: number
  fighter2_wins: number
  draws: number
  is_rivalry: boolean
}

export interface WorldState {
  current_date: string
  day_number: number
  rankings: string[]
  upcoming_events: string[]
  completed_events: string[]
  active_injuries: Record<string, number>
  rivalry_graph: RivalryRecord[]
  last_daily_summary: string
  event_counter: number
}
