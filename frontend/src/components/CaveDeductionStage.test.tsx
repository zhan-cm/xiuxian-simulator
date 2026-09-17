// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CaveSnapshot } from '../api/types'
import { CaveDeductionStage, type FacilityItem } from './CaveDeductionStage'

afterEach(() => cleanup())

const mockCave: CaveSnapshot = {
  name: '青岳石屋',
  aura: '浓郁',
  spirit_energy: 18,
  spirit_energy_cap: 30,
  monthly_generation: 4,
  focus: '蕴养灵脉',
  focuses: [],
  capacity: 2,
  active_jobs: 0,
  jobs: [],
  blueprints: [
    {
      name: '聚气丹',
      craft: '炼丹',
      facility: '丹房',
      duration: 2,
      ingredients: { 灵药: 2 },
      output: '聚气丹',
      output_count: 2,
      chance: 85,
      available: true,
      disabled_reason: '',
      action: '洞府生产 聚气丹',
      instant_action: '炼丹 聚气丹',
      instant_available: true,
      instant_disabled_reason: '',
    },
    {
      name: '青锋剑',
      craft: '炼器',
      facility: '器坊',
      duration: 3,
      ingredients: { 灵铁: 4, 妖兽材料: 1 },
      output: '青锋剑',
      output_count: 1,
      chance: 75,
      available: true,
      disabled_reason: '',
      action: '洞府生产 青锋剑',
      instant_action: '炼器 青锋剑',
      instant_available: true,
      instant_disabled_reason: '',
    },
    {
      name: '火球符',
      craft: '符箓',
      facility: '静室',
      duration: 1,
      ingredients: { 符纸: 3, 灵药: 1 },
      output: '火球符',
      output_count: 2,
      chance: 80,
      available: true,
      disabled_reason: '',
      action: '洞府生产 火球符',
      instant_action: '制符 火球符',
      instant_available: true,
      instant_disabled_reason: '',
    },
  ],
  crops: [
    {
      name: '灵药',
      due_turn: 15,
      remaining_months: 2,
      ready: false,
      progress: 50,
      stage: '抽叶期',
      harvest_action: '收获 灵药',
      expected_yield: 4,
    },
  ],
  skills: {
    炼丹: '熟练',
    炼器: '初窥',
    符箓: '初窥',
    灵植: '精通',
    阵法: '初窥',
  },
  facilities: {
    丹房: 1,
    灵田: 1,
    器坊: 1,
    聚灵阵: 1,
    静室: 1,
    禁制: 1,
  },
  last_event: '灵田轮作催熟灵药',
  ledger: [],
  can_recuperate: true,
  recuperate_reason: '',
}

describe('CaveDeductionStage', () => {
  it('renders alchemy deduction and triggers instant and queue crafting', () => {
    const act = vi.fn()
    const facilityItem: FacilityItem = {
      name: '丹房',
      level: 1,
      cost_stones: 250,
      materials: { 灵铁: 2 },
      affordable: true,
      disabled_reason: '',
      action: '升级洞府 丹房',
    }

    render(
      <CaveDeductionStage
        facilityName="丹房"
        facilityItem={facilityItem}
        cave={mockCave}
        onAction={act}
      />
    )

    expect(screen.getByRole('heading', { name: '丹房' })).toBeInTheDocument()
    expect(screen.getByText(/炼丹 ·/)).toBeInTheDocument()
    expect(screen.getByText('聚气丹')).toBeInTheDocument()

    // Click instant craft button
    fireEvent.click(screen.getByRole('button', { name: /即刻凝丹/ }))
    expect(act).toHaveBeenCalledWith('炼丹 聚气丹')

    // Click background craft button
    fireEvent.click(screen.getByRole('button', { name: /慢火温养/ }))
    expect(act).toHaveBeenCalledWith('洞府生产 聚气丹')
  })

  it('renders spirit field deduction with active crop and allows acceleration', () => {
    const act = vi.fn()
    const facilityItem: FacilityItem = {
      name: '灵田',
      level: 1,
      cost_stones: 150,
      materials: {},
      affordable: true,
      action: '升级洞府 灵田',
    }

    render(
      <CaveDeductionStage
        facilityName="灵田"
        facilityItem={facilityItem}
        cave={mockCave}
        onAction={act}
      />
    )

    expect(screen.getByText('抽叶期')).toBeInTheDocument()
    expect(screen.getByText(/还需 2 个月/)).toBeInTheDocument()

    // Click accelerate crop button
    fireEvent.click(screen.getByRole('button', { name: /切换【灵田轮作】灵蕴催熟/ }))
    expect(act).toHaveBeenCalledWith('洞府方针 灵田轮作')
  })

  it('renders ready crop with harvest button', () => {
    const act = vi.fn()
    const readyCave: CaveSnapshot = {
      ...mockCave,
      crops: [
        {
          name: '灵药',
          due_turn: 12,
          remaining_months: 0,
          ready: true,
          progress: 100,
          stage: '成熟待采',
          harvest_action: '收获 灵药',
          expected_yield: 4,
        },
      ],
    }
    const facilityItem: FacilityItem = {
      name: '灵田',
      level: 1,
      action: '升级洞府 灵田',
    }

    render(
      <CaveDeductionStage
        facilityName="灵田"
        facilityItem={facilityItem}
        cave={readyCave}
        onAction={act}
      />
    )

    expect(screen.getByText('成熟待采')).toBeInTheDocument()
    const harvestBtn = screen.getByRole('button', { name: /开镰采灵/ })
    fireEvent.click(harvestBtn)
    expect(act).toHaveBeenCalledWith('收获 灵药')
  })

  it('renders spirit gathering array with bagua policies', () => {
    const act = vi.fn()
    const facilityItem: FacilityItem = {
      name: '聚灵阵',
      level: 1,
      action: '升级洞府 聚灵阵',
    }

    render(
      <CaveDeductionStage
        facilityName="聚灵阵"
        facilityItem={facilityItem}
        cave={mockCave}
        onAction={act}
      />
    )

    expect(screen.getByText(/九宫八卦聚灵大阵/)).toBeInTheDocument()
    const dispatchBtn = screen.getByRole('button', { name: /百艺轮转/ })
    fireEvent.click(dispatchBtn)
    expect(act).toHaveBeenCalledWith('洞府方针 百艺轮转')
  })

  it('renders meditation chamber with recuperation and talisman crafting', () => {
    const act = vi.fn()
    const facilityItem: FacilityItem = {
      name: '静室',
      level: 1,
      action: '升级洞府 静室',
    }

    render(
      <CaveDeductionStage
        facilityName="静室"
        facilityItem={facilityItem}
        cave={mockCave}
        onAction={act}
      />
    )

    const recuperateBtn = screen.getByRole('button', { name: /调息养元/ })
    fireEvent.click(recuperateBtn)
    expect(act).toHaveBeenCalledWith('洞府调息')

    const instantTalismanBtn = screen.getByRole('button', { name: '即刻制符' })
    fireEvent.click(instantTalismanBtn)
    expect(act).toHaveBeenCalledWith('制符 火球符')
  })
})
