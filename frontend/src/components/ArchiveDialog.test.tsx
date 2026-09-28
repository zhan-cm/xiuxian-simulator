// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, expect, it, vi } from 'vitest'
import { ArchiveDialog } from './ArchiveDialog'

afterEach(() => { cleanup(); vi.restoreAllMocks() })

it('only deletes a selected save after confirmation and refreshes the list', async () => {
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ name: '旧档', recovery_directory: '/recovery/old' }), { status: 200 }))
  const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
  const changed = vi.fn()
  render(<ArchiveDialog open saves={[{ name: '旧档', player_name: '沈砚' }]} busy={false} canSave onAction={() => undefined} onChanged={changed} onNotice={() => undefined} />)
  fireEvent.click(screen.getByRole('button', { name: '删除 旧档' }))
  expect(fetchMock).not.toHaveBeenCalled()
  confirm.mockReturnValue(true)
  fireEvent.click(screen.getByRole('button', { name: '删除 旧档' }))
  await waitFor(() => expect(changed).toHaveBeenCalledOnce())
  expect(fetchMock).toHaveBeenCalledWith('/api/v1/saves?name=%E6%97%A7%E6%A1%A3', expect.objectContaining({ method: 'DELETE' }))
  expect(screen.getByText(/不会重置当前角色/)).toBeInTheDocument()
})

it('reports failed deletion without refreshing or claiming success', async () => {
  vi.spyOn(window, 'confirm').mockReturnValue(true)
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(JSON.stringify({ detail: '删除失败' }), { status: 400 }))
  const changed = vi.fn()
  render(<ArchiveDialog open saves={[{ name: '坏档', corrupt: true }]} busy={false} canSave onAction={() => undefined} onChanged={changed} onNotice={() => undefined} />)
  fireEvent.click(screen.getByRole('button', { name: '删除 坏档' }))
  await waitFor(() => expect(screen.getByText('删除失败')).toBeInTheDocument())
  expect(changed).not.toHaveBeenCalled()
})
