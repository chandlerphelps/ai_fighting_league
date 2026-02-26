import type { Fighter } from '../types/fighter'
import type { Match } from '../types/match'
import type { Event } from '../types/event'
import type { WorldState } from '../types/world_state'

async function fetchJson<T>(url: string): Promise<T | null> {
  try {
    const response = await fetch(url)
    if (!response.ok) return null
    return await response.json() as T
  } catch {
    return null
  }
}

export async function loadWorldState(): Promise<WorldState | null> {
  return fetchJson<WorldState>('/data/world_state.json')
}

export async function loadFighter(id: string): Promise<Fighter | null> {
  return fetchJson<Fighter>(`/data/fighters/${id}.json`)
}

export async function loadAllFighters(): Promise<Fighter[]> {
  const ws = await loadWorldState()
  if (!ws) return []

  const fighters: Fighter[] = []
  for (const id of ws.rankings) {
    const fighter = await loadFighter(id)
    if (fighter) fighters.push(fighter)
  }
  return fighters
}

export async function loadMatch(id: string): Promise<Match | null> {
  return fetchJson<Match>(`/data/matches/${id}.json`)
}

export async function loadAllMatches(): Promise<Match[]> {
  const ids = await fetchJson<string[]>('/data/matches')
  if (!ids) return []

  const matches: Match[] = []
  for (const id of ids) {
    const match = await loadMatch(id)
    if (match) matches.push(match)
  }
  return matches
}

export async function loadEvent(id: string): Promise<Event | null> {
  return fetchJson<Event>(`/data/events/${id}.json`)
}

export async function loadAllEvents(): Promise<Event[]> {
  const ws = await loadWorldState()
  if (!ws) return []

  const allIds = [...ws.completed_events, ...ws.upcoming_events]
  const events: Event[] = []
  for (const id of allIds) {
    const event = await loadEvent(id)
    if (event) events.push(event)
  }
  return events
}
