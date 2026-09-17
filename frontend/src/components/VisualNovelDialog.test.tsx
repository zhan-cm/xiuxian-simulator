// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { InventorySnapshot, NpcProfile } from '../api/types'
import { VisualNovelDialog, getAffinityRank } from './VisualNovelDialog'

afterEach(() => cleanup())

const mockNpc: NpcProfile = {
  name: '顾清玄',
  gender: '男',
  identity: '青云宗真传·温润剑修',
  age: 24,
  lifespan: 180,
  realm: '筑基·后期',
  location: '东洲青岳',
  greeting: '剑有锋芒，道心却不必处处伤人。',
  likes: ['剑穗', '清茶'],
  dislikes: ['情蛊'],
  affinity: 65,
  relation: '知己',
  alive: true,
  status: '静修',
}

const mockInventory = {
  items: [
    { name: '剑穗', count: 2, category: '礼物' },
    { name: '雪莲', count: 1, category: '礼物' },
    { name: '青锋剑', count: 1, category: '法宝' },
  ],
  categories: ['全部', '礼物', '法宝'],
  total_types: 3,
  total_count: 4,
  equipped: { weapon: '', armor: '' },
} as unknown as InventorySnapshot

describe('VisualNovelDialog', () => {
  it('computes correct affinity rank labels', () => {
    expect(getAffinityRank(10).label).toContain('素未谋面')
    expect(getAffinityRank(30).label).toContain('泛泛之交')
    expect(getAffinityRank(65).label).toContain('相知甚深')
    expect(getAffinityRank(85).label).toContain('莫逆之交')
    expect(getAffinityRank(90, '道侣').label).toContain('倾心道侣')
  })

  it('renders character stage, name, realm, identity and affinity', () => {
    render(
      <VisualNovelDialog
        npc={mockNpc}
        inventory={mockInventory}
        open={true}
        onClose={vi.fn()}
        onAction={vi.fn()}
      />
    )

    expect(screen.getByRole('heading', { name: '顾清玄' })).toBeInTheDocument()
    expect(screen.getByText('筑基·后期')).toBeInTheDocument()
    expect(screen.getByText('青云宗真传·温润剑修')).toBeInTheDocument()
    expect(screen.getByText(/东洲青岳/)).toBeInTheDocument()
    expect(screen.getByText(/65 \/ 100/)).toBeInTheDocument()
    // Character dialogue text
    expect(screen.getByText(/剑有锋芒/)).toBeInTheDocument()
  })

  it('triggers dialogue, dao discussion, and sparring actions on click', () => {
    const handleAction = vi.fn()
    render(
      <VisualNovelDialog
        npc={mockNpc}
        inventory={mockInventory}
        open={true}
        onClose={vi.fn()}
        onAction={handleAction}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /前往交谈/ }))
    expect(handleAction).toHaveBeenCalledWith('对话 顾清玄')

    fireEvent.click(screen.getByRole('button', { name: /论道印证/ }))
    expect(handleAction).toHaveBeenCalledWith('论道 顾清玄')

    fireEvent.click(screen.getByRole('button', { name: /同道切磋/ }))
    expect(handleAction).toHaveBeenCalledWith('切磋 顾清玄')
  })

  it('allows navigating to gifts tab and gifting liked items', () => {
    const handleAction = vi.fn()
    render(
      <VisualNovelDialog
        npc={mockNpc}
        inventory={mockInventory}
        open={true}
        onClose={vi.fn()}
        onAction={handleAction}
      />
    )

    // Switch to gifts tab
    fireEvent.click(screen.getByRole('button', { name: /奉赠仙珍/ }))
    expect(screen.getByText('心头所好：')).toBeInTheDocument()
    expect(screen.getAllByText('剑穗').length).toBeGreaterThanOrEqual(1)

    // Gift button for '剑穗'
    const sendButtons = screen.getAllByRole('button', { name: '奉赠' })
    expect(sendButtons.length).toBe(2) // 剑穗 and 雪莲
    fireEvent.click(sendButtons[0])
    expect(handleAction).toHaveBeenCalledWith('送礼 顾清玄 剑穗')
  })

  it('renders bio tab with appearance details', () => {
    render(
      <VisualNovelDialog
        npc={mockNpc}
        inventory={mockInventory}
        open={true}
        onClose={vi.fn()}
        onAction={vi.fn()}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /相貌浮生/ }))
    expect(screen.getByText('相貌风仪案卷')).toBeInTheDocument()
    expect(screen.getByText(/青云玉簪/)).toBeInTheDocument()
  })
})
