// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { EventPanel } from './EventPanel'
import type { NaturalExplorationSnapshot, Presentation } from '../api/types'

afterEach(() => cleanup())

const mockNaturalExploration: NaturalExplorationSnapshot = {
  current_region: '东洲',
  current_landmark: {
    id: 'dz-sword-pool',
    province: '东洲',
    name: '青岳洗剑池',
    title: '万剑通玄 · 洗剑清池',
    category: '剑仙灵脉',
    scenery: '青岳绝巅，飞泉注玉。池底沉有上古万千名剑剑胚。',
    specialties: ['灵泉玉液', '洗剑古砂', '古剑残片'],
    ferry_name: '青岳灵渡',
    ferry_desc: '东洲最大临海仙港，常驻巨型破浪楼船与御风灵舟。',
  },
  landmarks: [
    {
      id: 'dz-sword-pool',
      province: '东洲',
      name: '青岳洗剑池',
      title: '万剑通玄 · 洗剑清池',
      category: '剑仙灵脉',
      required_realm: 0,
      requirement_label: '炼气可达',
      scenery: '青岳绝巅，飞泉注玉。池底沉有上古万千名剑剑胚。',
      specialties: ['灵泉玉液', '洗剑古砂', '古剑残片'],
      ferry_name: '青岳灵渡',
      ferry_desc: '东洲最大临海仙港，常驻巨型破浪楼船与御风灵舟。',
      is_current: true,
      accessible: true,
      actions: {
        meditate: '胜境悟道 dz-sword-pool',
        harvest: '胜境采灵 dz-sword-pool',
        explore_secret: '胜境探幽 dz-sword-pool',
      },
    },
    {
      id: 'zz-celestial-pillar',
      province: '中州',
      name: '昆仑天柱仙台',
      title: '仙阙浮云 · 天地之脊',
      category: '登仙圣地',
      required_realm: 1,
      requirement_label: '筑基可达',
      scenery: '通天巨峰上接九霄罡风，浮空金阙若隐若现。',
      specialties: ['太虚清气', '九天仙露'],
      ferry_name: '通天帝渡',
      ferry_desc: '九州行旅之核心总枢，日夜有浮空巨舰穿梭五域。',
      is_current: false,
      accessible: true,
      actions: {
        meditate: '胜境悟道 zz-celestial-pillar',
        harvest: '胜境采灵 zz-celestial-pillar',
        explore_secret: '胜境探幽 zz-celestial-pillar',
      },
    },
  ],
  ferry_routes: [
    {
      destination: '中州',
      destination_name: '中州·天阙',
      months: 1,
      cost_stones: 45,
      can_travel: true,
      action: '渡海灵舟 中州',
    },
  ],
  player_realm_index: 1,
  player_stones: 500,
}

const mockPresentation: Presentation = {
  action: '九州舆图',
  title: '九州全景舆图',
  eyebrow: '九宫八卦',
  seal: '州',
  tone: 'neutral',
  paragraphs: [],
  changes: [],
  details: '',
  has_details: false,
  blocks: [
    {
      type: 'regions',
      title: '九州全景舆图',
      items: [
        {
          key: '东洲',
          name: '东洲 · 青岳',
          current: true,
          visited: true,
          accessible: true,
          danger: 12,
          danger_label: '凡人安居',
          months: 0,
          specialties: ['灵药', '聚气丹'],
          demands: ['妖兽材料'],
        },
        {
          key: '中州',
          name: '中州 · 天阙',
          current: false,
          visited: false,
          accessible: true,
          danger: 28,
          danger_label: '金丹历练',
          months: 2,
          specialties: ['奇闻玉简'],
          demands: ['天材地宝'],
          action: '前往 中州',
        },
      ],
    },
  ],
}

describe('NaturalExploration Landmarks & Ferries in EventPanel', () => {
  it('renders landmark details and 3 interaction buttons for current region', () => {
    const onAction = vi.fn()
    render(
      <EventPanel
        presentation={mockPresentation}
        naturalExploration={mockNaturalExploration}
        onAction={onAction}
      />
    )

    // Check landmark name and category badge
    expect(screen.getByText('青岳洗剑池')).toBeInTheDocument()
    expect(screen.getByText('剑仙灵脉')).toBeInTheDocument()
    expect(screen.getByText('青岳灵渡')).toBeInTheDocument()

    // Check 3 interaction buttons
    const meditateBtn = screen.getByRole('button', { name: /悟道/ })
    const harvestBtn = screen.getByRole('button', { name: /采灵/ })
    const secretBtn = screen.getByRole('button', { name: /探幽/ })

    expect(meditateBtn).toBeInTheDocument()
    expect(harvestBtn).toBeInTheDocument()
    expect(secretBtn).toBeInTheDocument()

    // Fire meditate action
    fireEvent.click(meditateBtn)
    expect(onAction).toHaveBeenCalledWith('胜境悟道 dz-sword-pool')

    // Fire harvest action
    fireEvent.click(harvestBtn)
    expect(onAction).toHaveBeenCalledWith('胜境采灵 dz-sword-pool')

    // Fire explore secret action
    fireEvent.click(secretBtn)
    expect(onAction).toHaveBeenCalledWith('胜境探幽 dz-sword-pool')
  })

  it('renders ferry and teleport fast travel buttons when selecting other accessible region', () => {
    const onAction = vi.fn()
    render(
      <EventPanel
        presentation={mockPresentation}
        naturalExploration={mockNaturalExploration}
        onAction={onAction}
      />
    )

    // Click Zhongzhou in the map
    const zhongzhouBtn = screen.getByRole('button', { name: /中州/ })
    fireEvent.click(zhongzhouBtn)

    // Verify Zhongzhou landmark shows up
    expect(screen.getByText('昆仑天柱仙台')).toBeInTheDocument()
    expect(screen.getByText('登仙圣地')).toBeInTheDocument()

    // Verify Ferry & Teleport buttons are rendered
    const ferryBtn = screen.getByRole('button', { name: /渡海灵舟/ })
    const teleportBtn = screen.getByRole('button', { name: /古阵挪移/ })

    expect(ferryBtn).toBeInTheDocument()
    expect(teleportBtn).toBeInTheDocument()

    fireEvent.click(ferryBtn)
    expect(onAction).toHaveBeenCalledWith('渡海灵舟 中州')

    fireEvent.click(teleportBtn)
    expect(onAction).toHaveBeenCalledWith('古阵挪移 中州')
  })
})
