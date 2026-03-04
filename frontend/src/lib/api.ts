import type { Fighter, RosterPlan, PlanEntry } from '../types/fighter'

const API_BASE = '/api'

async function apiFetch<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const err = await response.json().catch(() => ({ error: response.statusText }))
    throw new Error(err.error || `API error: ${response.status}`)
  }
  return response.json()
}

export interface TaskResponse {
  task_id: string
  status: 'running' | 'completed' | 'failed'
  result?: unknown
  error?: string
}

export async function fetchAllFighters(): Promise<Fighter[]> {
  return apiFetch<Fighter[]>('/fighters')
}

export async function fetchFighter(id: string): Promise<Fighter> {
  return apiFetch<Fighter>(`/fighters/${id}`)
}

export async function updateFighter(id: string, updates: Partial<Fighter>): Promise<Fighter> {
  return apiFetch<Fighter>(`/fighters/${id}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  })
}

export async function deleteFighter(id: string): Promise<void> {
  await apiFetch(`/fighters/${id}`, { method: 'DELETE' })
}

export interface GenerateOptions {
  archetype?: string
  has_supernatural?: boolean
  concept_hook?: string
  ring_name?: string
  gender?: string
  origin?: string
}

export async function generateFighter(options: GenerateOptions): Promise<TaskResponse> {
  return apiFetch<TaskResponse>('/fighters/generate', {
    method: 'POST',
    body: JSON.stringify(options),
  })
}

export async function regenerateCharacter(
  id: string,
  options?: { archetype?: string; has_supernatural?: boolean; concept_hook?: string }
): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/fighters/${id}/regenerate-character`, {
    method: 'POST',
    body: JSON.stringify(options || {}),
  })
}

export async function regenerateOutfits(
  id: string,
  options?: { tiers?: string[]; skimpiness_level?: number }
): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/fighters/${id}/regenerate-outfits`, {
    method: 'POST',
    body: JSON.stringify(options || {}),
  })
}

export async function regenerateImages(
  id: string,
  options?: { tiers?: string[] }
): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/fighters/${id}/regenerate-images`, {
    method: 'POST',
    body: JSON.stringify(options || {}),
  })
}

export async function regenerateMoveImage(
  id: string,
  moveIndex: number,
  tier: string
): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/fighters/${id}/regenerate-move-image`, {
    method: 'POST',
    body: JSON.stringify({ move_index: moveIndex, tier }),
  })
}

export async function pollTask(taskId: string): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/tasks/${taskId}`)
}

export async function pollUntilDone(taskId: string, onPoll?: () => void): Promise<TaskResponse> {
  const maxAttempts = 120
  for (let i = 0; i < maxAttempts; i++) {
    await new Promise(resolve => setTimeout(resolve, 2000))
    onPoll?.()
    const task = await pollTask(taskId)
    if (task.status === 'completed' || task.status === 'failed') {
      return task
    }
  }
  throw new Error('Task timed out')
}

export interface OutfitItem {
  name: string
  skimpiness_level: string
}

export interface OutfitTierOptions {
  tops: OutfitItem[]
  bottoms: OutfitItem[]
  one_pieces: OutfitItem[]
}

export interface OutfitOptions {
  sfw: OutfitTierOptions
  barely: OutfitTierOptions
  nsfw: OutfitTierOptions
}

export async function fetchOutfitOptions(): Promise<OutfitOptions> {
  return apiFetch<OutfitOptions>('/outfit-options')
}

export async function saveOutfitOptions(options: OutfitOptions): Promise<OutfitOptions> {
  return apiFetch<OutfitOptions>('/outfit-options', {
    method: 'PUT',
    body: JSON.stringify(options),
  })
}

export async function fetchArchetypes(): Promise<{ female: string[]; male: string[] }> {
  return apiFetch('/archetypes')
}

export function fighterImageUrl(fighterId: string, tier: string): string {
  return `${API_BASE}/fighter-images/${fighterId}/${tier}`
}

export function fighterPortraitUrl(fighterId: string): string {
  return `${API_BASE}/fighter-images/${fighterId}/portrait`
}

export async function fetchRosterPlan(): Promise<RosterPlan | null> {
  return apiFetch<RosterPlan | null>('/roster-plan')
}

export async function createRosterPlan(count: number, mode: 'initial' | 'addition' = 'initial'): Promise<TaskResponse> {
  return apiFetch<TaskResponse>('/roster-plan', {
    method: 'POST',
    body: JSON.stringify({ count, mode }),
  })
}

export async function deleteRosterPlan(): Promise<void> {
  await apiFetch('/roster-plan', { method: 'DELETE' })
}

export async function updatePlanEntry(index: number, updates: Partial<PlanEntry>): Promise<PlanEntry> {
  return apiFetch<PlanEntry>(`/roster-plan/entries/${index}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  })
}

export async function deletePlanEntry(index: number): Promise<void> {
  await apiFetch(`/roster-plan/entries/${index}`, { method: 'DELETE' })
}

export async function regeneratePlanEntry(index: number): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/roster-plan/entries/${index}/regenerate`, {
    method: 'POST',
  })
}

export async function addPlanEntries(count: number): Promise<TaskResponse> {
  return apiFetch<TaskResponse>('/roster-plan/entries/add', {
    method: 'POST',
    body: JSON.stringify({ count }),
  })
}

export async function generateFromPlan(): Promise<TaskResponse> {
  return apiFetch<TaskResponse>('/roster-plan/generate', {
    method: 'POST',
  })
}

export async function advanceStage(fighterId: string): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/fighters/${fighterId}/advance-stage`, {
    method: 'POST',
  })
}

export async function batchAdvance(fighterIds: string[], targetStage: number): Promise<TaskResponse> {
  return apiFetch<TaskResponse>('/fighters/batch-advance', {
    method: 'POST',
    body: JSON.stringify({ fighter_ids: fighterIds, target_stage: targetStage }),
  })
}

export async function fetchPoolSummary(): Promise<{ summary: string; count: number }> {
  return apiFetch('/pool-summary')
}
