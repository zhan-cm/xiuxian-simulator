import type { ShowcaseResponse, Snapshot } from './types'

async function decode<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as { detail?: string }
    throw new Error(payload.detail || `请求失败（${response.status}）`)
  }
  return response.json() as Promise<T>
}

export function fetchSnapshot(): Promise<Snapshot> {
  return fetch('/api/v1/state', { headers: { Accept: 'application/json' } }).then(decode<Snapshot>)
}

export function performAction(action: string): Promise<Snapshot> {
  return fetch('/api/v1/actions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ action }),
  }).then(decode<Snapshot>)
}

export function fetchShowcase(): Promise<ShowcaseResponse> {
  return fetch('/api/v1/showcase', { headers: { Accept: 'application/json' } }).then(decode<ShowcaseResponse>)
}
