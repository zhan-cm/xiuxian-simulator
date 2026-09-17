// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { TianjiRankModal } from './TianjiRankModal'
import type { TianjiSnapshot } from '../api/types'

afterEach(() => cleanup())

const mockTianji: TianjiSnapshot = {
  player_rank: 8,
  player_power: 1150,
  tokens: 45,
  news: ['天机阁快讯：东洲青岳洗剑池剑气冲霄，顾清玄悟出通天剑意！'],
  prodigies: [
    {
      id: 'prodigy-gu-qingxuan',
      rank: 1,
      name: '顾清玄',
      dao_name: '青云剑子',
      sect: '青云宗',
      province: '东洲',
      realm: '金丹·后期',
      realm_index: 3,
      power: 1480,
      title: '青岳第一剑 · 纯阳通玄',
      specialty: '太乙分光剑阵',
      description: '青云宗关门弟子，温润却剑意逼人。',
      is_npc: true,
      npc_name: '顾清玄',
      personality: '温润守礼',
      is_player: false,
      can_challenge: true,
      challenge_action: '登榜问剑 prodigy-gu-qingxuan',
    },
    {
      id: 'player-self',
      rank: 8,
      name: '沈砚',
      dao_name: '清微',
      sect: '青云宗',
      province: '东洲',
      realm: '金丹·初期',
      realm_index: 2,
      power: 1150,
      title: '潜龙在渊 · 仙道求索',
      specialty: '流火术',
      description: '沈砚，于九州求索长生大道。',
      is_npc: false,
      npc_name: '',
      personality: '道心坚定',
      is_player: true,
      can_challenge: false,
      challenge_action: '',
    },
  ],
  overlords: [
    {
      rank: 1,
      name: '青云子',
      dao_name: '天阳真人',
      sect: '青云宗',
      realm: '化神·圆满',
      power: 9800,
      title: '九州正道之首 · 万剑至尊',
      legend: '一柄青天古剑威震神州八百载。',
    },
  ],
  sects: [
    {
      rank: 1,
      name: '青云宗',
      province: '东洲青岳',
      doctrine: '清正持剑 · 守望正道',
      prestige: 9850,
      trend: '鼎盛',
      leader: '青云子',
    },
  ],
  treasures: [
    {
      id: 'tj-pill',
      name: '太虚蕴灵丹',
      category: '玄品丹药',
      token_cost: 45,
      effect: '服下后即刻增长 150 点修为',
      summary: '天机阁百草药圃凝炼的上乘灵丹。',
      affordable: true,
      action: '天机兑换 tj-pill',
    },
    {
      id: 'tj-box',
      name: '天机万象盒',
      category: '远古遗珍',
      token_cost: 60,
      effect: '开启随机得大量灵石',
      summary: '未知符文锦盒。',
      affordable: false,
      action: '天机兑换 tj-box',
    },
  ],
}

describe('TianjiRankModal Component', () => {
  it('renders modal header, player stats and prodigy ladder', () => {
    const onAction = vi.fn()
    const onOpenNpc = vi.fn()
    render(
      <TianjiRankModal
        open={true}
        onOpenChange={() => {}}
        tianji={mockTianji}
        busy={false}
        onAction={onAction}
        onOpenNpc={onOpenNpc}
      />
    )

    // Verify title and header
    expect(screen.getByText('天机百晓风云谱')).toBeInTheDocument()
    expect(screen.getByText('第 8 位')).toBeInTheDocument()
    expect(screen.getAllByText('1150')[0]).toBeInTheDocument()
    expect(screen.getByText('45 枚')).toBeInTheDocument()

    // Verify prodigy list
    expect(screen.getByText('顾清玄')).toBeInTheDocument()
    expect(screen.getByText('沈砚')).toBeInTheDocument()
    expect(screen.getByText('★ 本人')).toBeInTheDocument()

    // Verify Challenge button
    const challengeBtn = screen.getByRole('button', { name: /登榜问剑/ })
    expect(challengeBtn).toBeInTheDocument()
    fireEvent.click(challengeBtn)
    expect(onAction).toHaveBeenCalledWith('登榜问剑 prodigy-gu-qingxuan')

    // Verify NPC bond button
    const talkBtn = screen.getByRole('button', { name: /同道结缘/ })
    expect(talkBtn).toBeInTheDocument()
    fireEvent.click(talkBtn)
    expect(onOpenNpc).toHaveBeenCalledWith('顾清玄')
  })

  it('switches tabs to overlords and treasures', () => {
    const onAction = vi.fn()
    render(
      <TianjiRankModal
        open={true}
        onOpenChange={() => {}}
        tianji={mockTianji}
        busy={false}
        onAction={onAction}
      />
    )

    // Switch to Overlords
    const overlordsTab = screen.getByRole('button', { name: /九天巨擘榜/ })
    fireEvent.click(overlordsTab)
    expect(screen.getByText('青云子')).toBeInTheDocument()
    expect(screen.getByText('九州正道之首 · 万剑至尊')).toBeInTheDocument()

    // Switch to Treasures
    const treasuresTab = screen.getByRole('button', { name: /天机宝阁/ })
    fireEvent.click(treasuresTab)
    expect(screen.getByText('太虚蕴灵丹')).toBeInTheDocument()
    expect(screen.getByText('天机万象盒')).toBeInTheDocument()

    // Redeem button
    const redeemBtn = screen.getByRole('button', { name: /启封兑换/ })
    fireEvent.click(redeemBtn)
    expect(onAction).toHaveBeenCalledWith('天机兑换 tj-pill')
  })
})
