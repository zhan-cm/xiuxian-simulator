import { afterEach, describe, expect, it, vi } from 'vitest'
import { fetchSaveExport, fetchShowcase, fetchSnapshot, importSave, performAction } from './client'

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

  it('loads isolated showcase pages', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ pages: [] }), { status: 200 }))
    const result = await fetchShowcase()
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/showcase', { headers: { Accept: 'application/json' } })
    expect(result.pages).toEqual([])
  })

  it('downloads one portable save', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('{"format":"wendao-changsheng-save"}', { status: 200, headers: { 'Content-Type': 'application/json' } }))
    const result = await fetchSaveExport('筑基之前')
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/saves/export?name=%E7%AD%91%E5%9F%BA%E4%B9%8B%E5%89%8D', { headers: { Accept: 'application/json' } })
    expect(result.type).toContain('application/json')
  })

  it('imports json without allowing implicit overwrite', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ name: '旧档_导入1', source_format: 'legacy' }), { status: 200 }))
    await importSave({ phase: 'playing' }, '旧档')
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/saves/import', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ data: { phase: 'playing' }, preferred_name: '旧档', overwrite: false }),
    }))
  })
})
