import type { SaveImportResponse, ShowcaseResponse, Snapshot } from './types'

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

export async function fetchSaveExport(name: string): Promise<Blob> {
  const response = await fetch(`/api/v1/saves/export?name=${encodeURIComponent(name)}`, {
    headers: { Accept: 'application/json' },
  })
  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as { detail?: string }
    throw new Error(payload.detail || `导出失败（${response.status}）`)
  }
  return response.blob()
}

export function importSave(data: Record<string, unknown>, preferredName = ''): Promise<SaveImportResponse> {
  return fetch('/api/v1/saves/import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ data, preferred_name: preferredName, overwrite: false }),
  }).then(decode<SaveImportResponse>)
}
