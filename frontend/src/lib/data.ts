import type { Fighter } from '../types/fighter'
import type { WorldState, DaySimulationResult } from '../types/world_state'

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
  return fetchJson<WorldState>('/api/world-state')
}

export async function loadFighter(id: string): Promise<Fighter | null> {
  return fetchJson<Fighter>(`/api/fighters/${id}`)
}

export async function loadFightersForTier(ids: string[]): Promise<Fighter[]> {
  const fighters: Fighter[] = []
  const batchSize = 20
  for (let i = 0; i < ids.length; i += batchSize) {
    const batch = ids.slice(i, i + batchSize)
    const results = await Promise.all(batch.map(id => loadFighter(id)))
    for (const f of results) {
      if (f) fighters.push(f)
    }
  }
  return fighters
}

export async function loadAllFighterFiles(): Promise<Fighter[]> {
  const names = await fetchJson<string[]>('/data/fighters')
  if (!names) return []

  const fighters: Fighter[] = []
  for (const name of names) {
    const fighter = await fetchJson<Fighter>(`/data/fighters/${name}.json`)
    if (fighter) fighters.push(fighter)
  }
  return fighters
}

export async function simulateDay(): Promise<DaySimulationResult | null> {
  try {
    const response = await fetch('/api/simulate-day', { method: 'POST' })
    if (!response.ok) return null
    return await response.json() as DaySimulationResult
  } catch {
    return null
  }
}
