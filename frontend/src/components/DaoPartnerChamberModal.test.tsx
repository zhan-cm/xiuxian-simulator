// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { DaoPartnerChamberModal } from './DaoPartnerChamberModal'
import type { DaoPartnerSystemSnapshot } from '../api/types'

afterEach(() => cleanup())

const mockPartnerSystem: DaoPartnerSystemSnapshot = {
  has_partners: true,
  partners: [
    {
      name: '白凝霜',
      affinity: 100,
      dual_count: 3,
      preset_blessing: {
        name: '玄冥冰魄印',
        description: '极北冰魄护持灵台，万寒不侵。受创减伤 +25 点，气血上限临时提升 30 点。',
        duration_months: 6,
        defense_bonus: 25,
      },
      active_blessing: {
        name: '玄冥冰魄印',
        partner_name: '白凝霜',
        description: '极北冰魄护持灵台，万寒不侵。',
        remaining_months: 5,
        defense_bonus: 25,
      },
      can_conceive: true,
    },
    {
      name: '顾清玄',
      affinity: 85,
      dual_count: 1,
      preset_blessing: {
        name: '青云剑罡印',
        description: '青云纯阳剑意入体，攻击穿透提升 20%。',
        duration_months: 6,
        attack_multiplier: 1.2,
      },
      active_blessing: null,
      can_conceive: false,
    },
  ],
  children: [
    {
      id: 'child-1',
      name: '白凌霜',
      gender: '女',
      partner: '白凝霜',
      parent_player: '林渡',
      birth_year: 387,
      birth_turn: 1,
      age: 16,
      stage: '筑基成道',
      spiritual_root: '极北玄冰天灵根',
      constitution: '太古九阴玄魄体',
      realm: '筑基·初期',
      cultivation: 120,
      adventure_log: [],
    },
  ],
  messages: [
    {
      turn: 2,
      partner: '白凝霜',
      user_text: '近来安好？',
      reply: '北原夜深，知君心意自暖。',
      gift_item: '冰莲',
      gift_count: 1,
      gift_stones: 100,
    },
  ],
  active_blessings: {
    白凝霜: {
      name: '玄冥冰魄印',
      partner_name: '白凝霜',
      description: '极北冰魄护持灵台',
      remaining_months: 5,
    },
  },
}

describe('DaoPartnerChamberModal', () => {
  it('renders empty state when no dao partners', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    render(
      <DaoPartnerChamberModal
        open={true}
        onOpenChange={handleOpenChange}
        partnerSystem={{
          has_partners: false,
          partners: [],
          children: [],
          messages: [],
          active_blessings: {},
        }}
        onAction={handleAction}
      />
    )

    expect(screen.getByText('红尘孤身 · 尚待知己')).toBeInTheDocument()
    expect(screen.getByText('寻访红颜知己')).toBeInTheDocument()

    fireEvent.click(screen.getByText('寻访红颜知己'))
    expect(handleAction).toHaveBeenCalledWith('情缘')
    expect(handleOpenChange).toHaveBeenCalledWith(false)
  })

  it('renders partner details, active blessing, and triggers dual cultivation', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    render(
      <DaoPartnerChamberModal
        open={true}
        onOpenChange={handleOpenChange}
        partnerSystem={mockPartnerSystem}
        onAction={handleAction}
      />
    )

    expect(screen.getByText('仙侣同修阁')).toBeInTheDocument()
    expect(screen.getAllByText('玄冥冰魄印').length).toBeGreaterThan(0)
    expect(screen.getByText(/生效中 · 余 5 月/)).toBeInTheDocument()
    expect(screen.getByText(/合修周天/)).toBeInTheDocument()

    // Click dual cultivate button
    const dualBtn = screen.getByText('阴阳性命合修一月')
    fireEvent.click(dualBtn)
    expect(handleAction).toHaveBeenCalledWith('仙侣同修 白凝霜')

    // Click conceive button (can_conceive is true)
    const conceiveBtn = screen.getByText('孕育仙家麟儿')
    fireEvent.click(conceiveBtn)
    expect(handleAction).toHaveBeenCalledWith('孕育仙胎 白凝霜')
  })

  it('switches to soul transmission tab and sends preset message', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    render(
      <DaoPartnerChamberModal
        open={true}
        onOpenChange={handleOpenChange}
        partnerSystem={mockPartnerSystem}
        onAction={handleAction}
      />
    )

    // Switch to transmission tab
    fireEvent.click(screen.getByText('心印传音'))

    expect(screen.getByText(/北原夜深，知君心意自暖/)).toBeInTheDocument()
    expect(screen.getByText(/【冰莲】×1/)).toBeInTheDocument()

    // Click preset message
    const presetBtn = screen.getByText('道友近日安好？心印微温，甚是念卿。')
    fireEvent.click(presetBtn)
    expect(handleAction).toHaveBeenCalledWith('传音 白凝霜 道友近日安好？心印微温，甚是念卿。')
  })

  it('switches to lineage children tab and renders child information', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    render(
      <DaoPartnerChamberModal
        open={true}
        onOpenChange={handleOpenChange}
        partnerSystem={mockPartnerSystem}
        onAction={handleAction}
      />
    )

    // Switch to lineage tab
    fireEvent.click(screen.getByRole('button', { name: /仙家子嗣/ }))

    expect(screen.getByText('白凌霜')).toBeInTheDocument()
    expect(screen.getByText('极北玄冰天灵根')).toBeInTheDocument()
    expect(screen.getByText('太古九阴玄魄体')).toBeInTheDocument()
    expect(screen.getByText('筑基·初期')).toBeInTheDocument()
    expect(screen.getByText(/已达筑基，游历各州寻觅机缘/)).toBeInTheDocument()
  })
})
