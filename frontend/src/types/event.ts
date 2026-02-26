export interface EventMatch {
  match_id: string
  fighter1_id: string
  fighter1_name: string
  fighter2_id: string
  fighter2_name: string
  completed: boolean
  winner_id: string | null
  method: string | null
}

export interface Event {
  id: string
  date: string
  name: string
  matches: EventMatch[]
  completed: boolean
  summary: string
}
