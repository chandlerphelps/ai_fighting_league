import { useState, useEffect, useCallback, useContext, createContext, type ReactNode } from 'react'
import type { Fighter } from '../types/fighter'
import type { WorldState } from '../types/world_state'
import {
  loadWorldState,
  loadFighter,
  loadFightersForTier,
} from '../lib/data'

interface DataState<T> {
  data: T | null
  loading: boolean
  error: string | null
  refresh: () => void
}

function useDataLoader<T>(loader: () => Promise<T | null>, deps: unknown[] = []): DataState<T> {
  const [state, setState] = useState<{ data: T | null; loading: boolean; error: string | null }>({
    data: null, loading: true, error: null,
  })
  const [refreshKey, setRefreshKey] = useState(0)

  const refresh = useCallback(() => setRefreshKey(k => k + 1), [])

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
  }, [...deps, refreshKey])

  return { ...state, refresh }
}

const WorldStateContext = createContext<DataState<WorldState> | null>(null)

export function WorldStateProvider({ children }: { children: ReactNode }) {
  const state = useDataLoader(loadWorldState)
  return <WorldStateContext.Provider value={state}>{children}</WorldStateContext.Provider>
}

export function useWorldState(): DataState<WorldState> {
  const ctx = useContext(WorldStateContext)
  if (ctx) return ctx
  return useDataLoader(loadWorldState)
}

export function useFighter(id: string): DataState<Fighter> {
  return useDataLoader(() => loadFighter(id), [id])
}

export function useTierFighters(ids: string[]): DataState<Fighter[]> {
  return useDataLoader(async () => {
    if (!ids.length) return null
    const fighters = await loadFightersForTier(ids)
    return fighters.length > 0 ? fighters : null
  }, [ids.join(',')])
}
