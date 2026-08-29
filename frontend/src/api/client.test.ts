import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchSnapshot, performAction } from './client'

afterEach(() => vi.restoreAllMocks())

describe('game api client', () => {
  it('loads the versioned state endpoint', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ state: { phase: 'new' } }), { status: 200 }))
    const result = await fetchSnapshot()
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/state', { headers: { Accept: 'application/json' } })
    expect(result.state.phase).toBe('new')
  })

  it('posts one action as json', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ state: { phase: 'playing' } }), { status: 200 }))
    await performAction('修炼')
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/actions', expect.objectContaining({ method: 'POST', body: JSON.stringify({ action: '修炼' }) }))
  })
})
