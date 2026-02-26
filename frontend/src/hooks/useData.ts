import { useState, useEffect } from 'react'
import type { Fighter } from '../types/fighter'
import type { Match } from '../types/match'
import type { Event } from '../types/event'
import type { WorldState } from '../types/world_state'
import {
  loadWorldState,
  loadFighter,
  loadAllFighters,
  loadMatch,
  loadAllMatches,
  loadEvent,
  loadAllEvents,
} from '../lib/data'

interface DataState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

function useDataLoader<T>(loader: () => Promise<T | null>, deps: unknown[] = []): DataState<T> {
  const [state, setState] = useState<DataState<T>>({ data: null, loading: true, error: null })

  useEffect(() => {
    let cancelled = false
    setState(prev => ({ ...prev, loading: true, error: null }))

    loader()
      .then(data => {
        if (!cancelled) {
          setState({ data, loading: false, error: data === null ? 'No data found' : null })
        }
      })
      .catch(err => {
        if (!cancelled) {
          setState({ data: null, loading: false, error: String(err) })
        }
      })

    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return state
}

export function useWorldState(): DataState<WorldState> {
  return useDataLoader(loadWorldState)
}

export function useFighter(id: string): DataState<Fighter> {
  return useDataLoader(() => loadFighter(id), [id])
}

export function useAllFighters(): DataState<Fighter[]> {
  return useDataLoader(async () => {
    const fighters = await loadAllFighters()
    return fighters.length > 0 ? fighters : null
  })
}

export function useMatch(id: string): DataState<Match> {
  return useDataLoader(() => loadMatch(id), [id])
}

export function useAllMatches(): DataState<Match[]> {
  return useDataLoader(async () => {
    const matches = await loadAllMatches()
    return matches.length > 0 ? matches : null
  })
}

export function useEvent(id: string): DataState<Event> {
  return useDataLoader(() => loadEvent(id), [id])
}

export function useAllEvents(): DataState<Event[]> {
  return useDataLoader(async () => {
    const events = await loadAllEvents()
    return events.length > 0 ? events : null
  })
}
