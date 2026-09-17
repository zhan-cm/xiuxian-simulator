// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { RedDustEncounterModal } from './RedDustEncounterModal'
import type { PendingEncounterData } from '../api/types'

afterEach(() => cleanup())

const mockEncounter: PendingEncounterData = {
  id: 'ancient_remains',
  title: '古修士遗蜕与残魂传道',
  category: 'ancient_secret',
  character: {
    name: '太古剑尊残魂',
    identity: '古修残灵',
    realm: '化神·圆满',
    temperament: 'aloof',
    avatar_type: 'procedural',
    quote: '后辈修士，能破吾三千禁制踏足此地，也算有机缘。',
  },
  scene: '踏入万年古修封印石室，一尊不朽金身端坐蒲团之上，周身剑气如虹。',
  choices: [
    {
      id: 'worship',
      label: '躬身叩拜，求承衣钵',
      dao_stance: '慈悲仁善',
      tone: 'safe',
      summary: '功德 +3 · 道法感悟 +25 · 悟道点 +1 · 声望 +5',
      description: '执弟子之礼向古尊行三跪九叩大礼，心怀敬畏承继衣钵。',
      disabled: false,
      disabled_reason: '',
    },
    {
      id: 'plunder',
      label: '强破残魂，搜刮遗珍',
      dao_stance: '杀人夺宝',
      tone: 'danger',
      summary: '业障 +4 · 灵石 +300 · 天材地宝 +1',
      description: '趁残魂虚弱强行以术法轰杀残灵，搜刮金身储物古戒。',
      disabled: true,
      disabled_reason: '境界需达筑基',
    },
  ],
}

describe('RedDustEncounterModal', () => {
  it('renders encounter details, character quote, scene, and choices when open', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    render(
      <RedDustEncounterModal
        open={true}
        onOpenChange={handleOpenChange}
        encounter={mockEncounter}
        onAction={handleAction}
      />
    )

    // Check title and category
    expect(screen.getByText('《古修士遗蜕与残魂传道》')).toBeInTheDocument()
    expect(screen.getByText('太古秘境机缘')).toBeInTheDocument()

    // Check character quote and scene
    expect(screen.getByText(/后辈修士，能破吾三千禁制踏足此地/)).toBeInTheDocument()
    expect(screen.getByText(/踏入万年古修封印石室/)).toBeInTheDocument()

    // Check choices
    expect(screen.getByText('躬身叩拜，求承衣钵')).toBeInTheDocument()
    expect(screen.getByText('【慈悲仁善】')).toBeInTheDocument()
    expect(screen.getByText('强破残魂，搜刮遗珍')).toBeInTheDocument()
    expect(screen.getByText('【杀人夺宝】')).toBeInTheDocument()
    expect(screen.getByText('境界需达筑基')).toBeInTheDocument()
  })

  it('triggers onAction when an enabled choice is clicked', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    render(
      <RedDustEncounterModal
        open={true}
        onOpenChange={handleOpenChange}
        encounter={mockEncounter}
        onAction={handleAction}
      />
    )

    const worshipBtn = screen.getByText('躬身叩拜，求承衣钵').closest('button')
    expect(worshipBtn).not.toBeNull()
    expect(worshipBtn).not.toBeDisabled()
    fireEvent.click(worshipBtn!)

    expect(handleAction).toHaveBeenCalledWith('奇遇选择 worship')
  })

  it('does not trigger onAction when a disabled choice is clicked', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    render(
      <RedDustEncounterModal
        open={true}
        onOpenChange={handleOpenChange}
        encounter={mockEncounter}
        onAction={handleAction}
      />
    )

    const plunderBtn = screen.getByText('强破残魂，搜刮遗珍').closest('button')
    expect(plunderBtn).not.toBeNull()
    expect(plunderBtn).toBeDisabled()
    fireEvent.click(plunderBtn!)

    expect(handleAction).not.toHaveBeenCalled()
  })

  it('does not render content when closed', () => {
    render(
      <RedDustEncounterModal
        open={false}
        onOpenChange={vi.fn()}
        encounter={mockEncounter}
        onAction={vi.fn()}
      />
    )

    expect(screen.queryByText('《古修士遗蜕与残魂传道》')).not.toBeInTheDocument()
  })
})
