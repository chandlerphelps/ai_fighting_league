import type { Fighter } from '../types/fighter'

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

export async function fetchArchetypes(): Promise<{ female: string[]; male: string[] }> {
  return apiFetch('/archetypes')
}

export function fighterImageUrl(fighterId: string, tier: string): string {
  return `${API_BASE}/fighter-images/${fighterId}/${tier}`
}
