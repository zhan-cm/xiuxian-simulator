// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { LifeboundArtifactModal } from './LifeboundArtifactModal'
import type { ArtifactGrowthSnapshot } from '../api/types'

afterEach(() => cleanup())

const mockArtifacts: ArtifactGrowthSnapshot = {
  count: 2,
  bonded_name: '玄铁剑',
  bonded: {
    name: '玄铁剑',
    level: 2,
    level_label: '二炼',
    resonance: 65,
    effect: '攻势额外 +17.5%',
  },
  level_cap: 3,
  level_cap_label: '结晶境 · 最多三炼',
  artifacts: [
    {
      name: '玄铁剑',
      mark: '玄',
      grade: '玄阶',
      slot: '武器',
      element: '金',
      level: 2,
      level_label: '二炼',
      level_cap: 3,
      resonance: 65,
      victories: 4,
      equipped: true,
      bonded: true,
      effect: '攻势额外 +17.5%',
      refine_cost: '灵石 240 · 灵铁×2',
      refine_chance: 75,
      can_refine: true,
      refine_reason: '',
      refine_action: '淬炼法宝 玄铁剑',
      can_bind: false,
      bind_reason: '已是本命法宝',
      bind_action: '',
      can_nourish: true,
      nourish_reason: '',
      nourish_action: '温养法宝 玄铁剑',
      inscriptions: ['锋锐'],
      max_slots: 4,
      spirit_stage: 2,
      spirit_stage_label: '形意相依',
      spirit_dialogue: '灵影伴随左右，器心温热。',
      spirit_awakened: true,
      spirit_commune_action: '器灵感应 玄铁剑',
      available_inscriptions: [
        {
          id: '锋锐',
          name: '锋锐之纹',
          desc: '物理攻势提升 15%',
          effect_text: '攻势额外 +15%',
          cost_stones: 150,
          cost_materials: { 灵铁: 3 },
          req_grade: '黄阶',
          slot_type: '通用',
          inscribed: true,
          can_inscribe: false,
          inscribe_reason: '该器纹已铭刻在法宝上',
          inscribe_action: '',
          wash_action: '洗练器纹 玄铁剑 锋锐',
        },
        {
          id: '固本',
          name: '固本之纹',
          desc: '防御额外提升',
          effect_text: '防御额外 +20',
          cost_stones: 150,
          cost_materials: { 灵铁: 3 },
          req_grade: '黄阶',
          slot_type: '通用',
          inscribed: false,
          can_inscribe: true,
          inscribe_reason: '',
          inscribe_action: '铭刻器纹 玄铁剑 固本',
          wash_action: '',
        },
      ],
      infused_materials: { 天工万象铁: 1 },
    },
  ],
  all_inscriptions: [
    {
      id: '锋锐',
      name: '锋锐之纹',
      slot_type: '通用',
      desc: '物理攻势提升 15%',
      cost_stones: 150,
      cost_materials: { 灵铁: 3 },
      req_grade: '黄阶',
      effect_text: '攻势额外 +15%',
    },
    {
      id: '固本',
      name: '固本之纹',
      slot_type: '通用',
      desc: '防御额外提升',
      cost_stones: 150,
      cost_materials: { 灵铁: 3 },
      req_grade: '黄阶',
      effect_text: '防御额外 +20',
    },
  ],
  infusable_materials: [
    {
      name: '天工万象铁',
      desc: '天机神铁',
      bonus_text: '攻防 +3%',
      resonance_gain: 8,
      count: 2,
      can_infuse: true,
      infuse_action: '熔铸神料 玄铁剑 天工万象铁',
    },
  ],
  materials: {
    spirit_stones: 1500,
    spirit: 80,
    spirit_max: 100,
    spirit_iron: 12,
    beast_materials: 6,
  },
  history: ['在玄铁剑上铭刻【锋锐之纹】'],
}

describe('LifeboundArtifactModal', () => {
  it('renders modal with bonded artifact info and inscriptions tab', () => {
    const handleAction = vi.fn()
    render(
      <LifeboundArtifactModal
        open={true}
        onOpenChange={() => {}}
        artifacts={mockArtifacts}
        busy={false}
        onAction={handleAction}
      />
    )

    expect(screen.getByText('本命灵宝阁 · 九重器纹')).toBeInTheDocument()
    expect(screen.getByText('玄铁剑（二炼）')).toBeInTheDocument()
    expect(screen.getByText('65 / 100')).toBeInTheDocument()
    expect(screen.getByText('1 / 4 孔')).toBeInTheDocument()
    expect(screen.getByText('太古九重器纹谱系')).toBeInTheDocument()
    expect(screen.getByText('★ 已铭刻')).toBeInTheDocument()

    // Test inscribe button on available inscription
    const inscribeBtn = screen.getByText('铭刻器纹')
    fireEvent.click(inscribeBtn)
    expect(handleAction).toHaveBeenCalledWith('铭刻器纹 玄铁剑 固本')
  })

  it('navigates to infusion and spirit tabs', () => {
    const handleAction = vi.fn()
    render(
      <LifeboundArtifactModal
        open={true}
        onOpenChange={() => {}}
        artifacts={mockArtifacts}
        busy={false}
        onAction={handleAction}
      />
    )

    // Click infusion tab
    const infusionTab = screen.getByText('神料熔铸')
    fireEvent.click(infusionTab)
    expect(screen.getByText('天工万象铁')).toBeInTheDocument()
    const infuseBtn = screen.getByText('熔铸入胚')
    fireEvent.click(infuseBtn)
    expect(handleAction).toHaveBeenCalledWith('熔铸神料 玄铁剑 天工万象铁')

    // Click spirit tab
    const spiritTab = screen.getByText('器灵通微')
    fireEvent.click(spiritTab)
    expect(screen.getByText('器灵法相 · 形意相依')).toBeInTheDocument()
    const communeBtn = screen.getByText('器灵神识感应')
    fireEvent.click(communeBtn)
    expect(handleAction).toHaveBeenCalledWith('器灵感应 玄铁剑')
  })
})
