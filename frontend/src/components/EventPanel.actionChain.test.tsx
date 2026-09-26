// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CommissionSnapshot, InventorySnapshot, PlayerState, Presentation, RecoverySnapshot } from '../api/types'
import { EventPanel } from './EventPanel'

afterEach(() => cleanup())

const basePresentation: Presentation = {
  action: '探索 荒野',
  title: '荒野深处',
  eyebrow: '历练',
  seal: '游',
  tone: 'adventure',
  paragraphs: [
    '你在荒野深处探寻，拨开荆棘，偶得前人遗存。',
    '指令：闭关、吐纳、前往坊市',
    '可进行行动：\n- 胜境采灵 huashan：采集灵草奇珍\n- 胜境探幽 huashan：洞窟探秘',
  ],
  changes: [
    { label: '修为', value: '+120' },
    { label: '灵石', value: '+50' },
  ],
  details: '',
  has_details: false,
  blocks: [],
}

const mockPlayer: PlayerState = {
  name: '韩立',
  dao_name: '厉飞雨',
  gender: '男',
  age: 20,
  lifespan: 120,
  realm: '炼气期·九层',
  sect: '黄枫谷',
  sect_rank: '外门弟子',
  spiritual_root: '四灵根',
  constitution: '凡体',
  health: 30, // low health: max is 100
  health_max: 100,
  spirit: 80,
  spirit_max: 100,
  cultivation: 1000,
  cultivation_required: 1000, // maxed!
  spirit_stones: 300,
  condition: '受轻伤',
  location: '太岳山脉',
  inventory: [],
  resources: {},
}

const mockInventory: InventorySnapshot = {
  total_types: 2,
  total_count: 3,
  equipped: { weapon: '', armor: '' },
  categories: ['丹药', '法宝'],
  items: [
    {
      name: '聚气丹',
      count: 2,
      category: '丹药',
      rarity: '黄阶',
      description: '益气培元之丹',
      usage: '服用以助修为',
      equipped: false,
      slot: '',
      action: '使用 聚气丹',
      action_label: '服用',
      actionable: true,
      disabled_reason: '',
    },
    {
      name: '青云剑',
      count: 1,
      category: '法宝',
      rarity: '玄阶',
      description: '青钢淬灵之剑',
      usage: '一柄锋锐飞剑',
      equipped: false,
      slot: 'weapon',
      action: '装备 青云剑',
      action_label: '装备',
      actionable: true,
      disabled_reason: '',
    },
  ],
}

const mockCommissions: CommissionSnapshot = {
  title: '悬赏榜',
  cycle: 1,
  rotation_label: '轮换',
  active_limit: 3,
  active_count: 1,
  renown: 20,
  completed_count: 5,
  offers: [],
  history: [],
  active: [
    {
      id: 'comm-1',
      template_id: 't-1',
      title: '剿除黑风盗',
      issuer: '青岳城',
      kind: 'combat',
      kind_label: '斩妖除祟',
      summary: '剿除贼寇',
      requirement: '击败黑风盗',
      duration: 3,
      reward: '灵石 +200',
      accepted: true,
      completed: false,
      eligible: true,
      disabled_reason: '',
      accept_action: '',
      current: 1,
      required: 1,
      progress: 100,
      ready: true,
      expired: false,
      turns_left: 2,
      deadline_turn: 10,
      deliver_action: '交付悬赏 comm-1',
      abandon_action: '放弃悬赏 comm-1',
    },
  ],
}

const mockRecovery: RecoverySnapshot = {
  active: true,
  count: 1,
  condition: '轻伤',
  health: 30,
  health_max: 100,
  spirit: 80,
  spirit_max: 100,
  injuries: [
    {
      id: 'inj-1',
      name: '经脉震荡',
      mark: '伤',
      severity: 1,
      severity_label: '轻创',
      months_left: 2,
      source: '荒野恶战',
      description: '受反震力道所激',
      effects: [],
    },
  ],
  penalties: { cultivation: 0, combat: 0, damage_taken: 0, speed: 0 },
  can_rest: true,
  rest_reason: '',
  rest_action: '运功疗伤',
  has_healing_pill: true,
  pill_action: '使用 疗伤丹',
  history: [],
}

describe('EventActionChain and Interactive Ribbons in EventPanel', () => {
  it('renders command capsule buttons for text containing 指令 and bullet actions', () => {
    const onAction = vi.fn()

    render(
      <EventPanel
        presentation={basePresentation}
        player={mockPlayer}
        readOnly={false}
        onAction={onAction}
      />
    )

    // Check 指令 capsule buttons
    const biguanBtn = screen.getByRole('button', { name: '闭关' })
    const tunaBtn = screen.getByRole('button', { name: '吐纳' })
    const fangshiBtn = screen.getByRole('button', { name: '前往坊市' })

    expect(biguanBtn).toBeInTheDocument()
    expect(tunaBtn).toBeInTheDocument()
    expect(fangshiBtn).toBeInTheDocument()

    fireEvent.click(biguanBtn)
    expect(onAction).toHaveBeenCalledWith('闭关')

    // Check rich bullet action buttons
    const cailingBtn = screen.getByRole('button', { name: /胜境采灵 huashan/ })
    expect(cailingBtn).toBeInTheDocument()
    fireEvent.click(cailingBtn)
    expect(onAction).toHaveBeenCalledWith('胜境采灵 huashan')
  })

  it('renders breakthrough climax card when cultivation is maxed', () => {
    const onAction = vi.fn()
    const onOpenBreakthrough = vi.fn()

    render(
      <EventPanel
        presentation={basePresentation}
        player={mockPlayer}
        readOnly={false}
        onAction={onAction}
        onOpenBreakthrough={onOpenBreakthrough}
      />
    )

    const breakthroughBtn = screen.getByRole('button', { name: /叩问天关 · 立即突破/ })
    expect(breakthroughBtn).toBeInTheDocument()

    fireEvent.click(breakthroughBtn)
    expect(onOpenBreakthrough).toHaveBeenCalledTimes(1)
  })

  it('renders bounty claim card and delivers on click', () => {
    const onAction = vi.fn()

    render(
      <EventPanel
        presentation={basePresentation}
        player={mockPlayer}
        commissions={mockCommissions}
        readOnly={false}
        onAction={onAction}
      />
    )

    const claimBtn = screen.getByRole('button', { name: /一键揭榜领赏/ })
    expect(claimBtn).toBeInTheDocument()

    fireEvent.click(claimBtn)
    expect(onAction).toHaveBeenCalledWith('交付悬赏 comm-1')
  })

  it('renders triage and emergency healing buttons on low health/injuries', () => {
    const onAction = vi.fn()

    render(
      <EventPanel
        presentation={basePresentation}
        player={mockPlayer}
        recovery={mockRecovery}
        readOnly={false}
        onAction={onAction}
      />
    )

    const healBtn = screen.getByRole('button', { name: /运功疗伤/ })
    expect(healBtn).toBeInTheDocument()
    fireEvent.click(healBtn)
    expect(onAction).toHaveBeenCalledWith('运功疗伤')

    const pillBtn = screen.getByRole('button', { name: /吞服疗伤圣药/ })
    expect(pillBtn).toBeInTheDocument()
    fireEvent.click(pillBtn)
    expect(onAction).toHaveBeenCalledWith('使用 疗伤丹')
  })

  it('renders instant usable loot buttons and contextual actions', () => {
    const onAction = vi.fn()

    render(
      <EventPanel
        presentation={basePresentation}
        player={mockPlayer}
        inventory={mockInventory}
        readOnly={false}
        onAction={onAction}
      />
    )

    const pillLootBtn = screen.getByRole('button', { name: /立即服用【聚气丹】/ })
    expect(pillLootBtn).toBeInTheDocument()
    fireEvent.click(pillLootBtn)
    expect(onAction).toHaveBeenCalledWith('使用 聚气丹')

    const swordLootBtn = screen.getByRole('button', { name: /一键装备【青云剑】/ })
    expect(swordLootBtn).toBeInTheDocument()
    fireEvent.click(swordLootBtn)
    expect(onAction).toHaveBeenCalledWith('装备 青云剑')

    // Contextual next-steps for exploration
    const continueBtn = screen.getByRole('button', { name: /继续深入探寻/ })
    expect(continueBtn).toBeInTheDocument()
    fireEvent.click(continueBtn)
    expect(onAction).toHaveBeenCalledWith('探索 荒野')
  })
})
