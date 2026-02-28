export interface MatchupAnalysis {
  fighter1_win_prob: number
  fighter2_win_prob: number
  fighter1_methods: Record<string, number>
  fighter2_methods: Record<string, number>
  key_factors: string[]
}

export interface MatchOutcome {
  winner_id: string
  loser_id: string | null
  method: string
  round_ended: number
  fighter1_performance: string
  fighter2_performance: string
  fighter1_injuries: Array<{ type: string; severity: string; recovery_days_remaining: number }>
  fighter2_injuries: Array<{ type: string; severity: string; recovery_days_remaining: number }>
  is_draw: boolean
}

export interface FightMoment {
  moment_number: number
  description: string
  attacker_id: string
  action: string
  image_prompt: string
  image_path: string
}

export interface Match {
  id: string
  event_id: string
  date: string
  fighter1_id: string
  fighter1_name: string
  fighter2_id: string
  fighter2_name: string
  analysis: MatchupAnalysis | null
  outcome: MatchOutcome | null
  narrative: string
  moments: FightMoment[]
  fighter1_snapshot: Record<string, unknown>
  fighter2_snapshot: Record<string, unknown>
  post_fight_updates: Record<string, unknown>
}
