import type { ScheduleResponse, ContentData, GenerateRequest } from './types'

const API_BASE = import.meta.env.VITE_API_URL || 'https://bws-social-content.fly.dev'

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`${res.status}: ${text}`)
  }

  return res.json()
}

export const api = {
  getSchedule: () => apiFetch<ScheduleResponse>('/schedule'),

  getContent: (date: string) => apiFetch<ContentData>(`/content/${date}`),

  generate: (req: GenerateRequest) =>
    apiFetch<ContentData>('/generate', {
      method: 'POST',
      body: JSON.stringify(req),
    }),
}
