// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { SectVisitSnapshot } from '../api/types'
import { SectGateModal } from './SectGateModal'

afterEach(() => cleanup())

const mockSectVisit: SectVisitSnapshot = {
  gift_cost: 50,
  player_sect: '青云宗',
  player_stones: 500,
  player_reputation: 50,
  gates: [
    {
      name: '青云宗',
      province: '东洲青岳',
      mark: '云',
      doctrine: '正道名门 · 剑道通玄',
      motto: '清正持剑，守望东洲',
      description: '雄踞东洲青岳群峰之巅，云蒸霞蔚，剑阁高耸。',
      welcome_gift: '青云剑穗',
      welcome_gift_count: 1,
      can_visit: true,
      visit_action: '拜山 青云宗',
      spar_chance: 65,
      spar_action: '山门演武 青云宗',
      treasures: [
        {
          id: 'qy-pill',
          name: '聚气丹',
          cost_stones: 180,
          category: '丹药',
          reputation_req: 10,
          count: 3,
          summary: '青云灵药圃秘炼聚气丹。',
          available: true,
          disabled_reason: '',
          action: '求丹借宝 青云宗 qy-pill',
        },
        {
          id: 'qy-sword',
          name: '青锋剑',
          cost_stones: 350,
          category: '法宝',
          reputation_req: 30,
          count: 1,
          summary: '青云洗剑池淬砺上品法剑。',
          available: true,
          disabled_reason: '',
          action: '求丹借宝 青云宗 qy-sword',
        },
        {
          id: 'qy-pendant',
          name: '青云佩',
          cost_stones: 600,
          category: '奇珍',
          reputation_req: 60,
          count: 1,
          summary: '聚青岳千年浩气。',
          available: false,
          disabled_reason: '灵石不足（需 600）',
          action: '求丹借宝 青云宗 qy-pendant',
        },
      ],
      bounties: [
        {
          id: 'qy-bounty-1',
          title: '清剿青岳外围妖狼',
          risk: '普通',
          chance: 75,
          reward_stones: 200,
          reward_reputation: 10,
          reward_items: { 妖兽材料: 2 },
          summary: '扫荡潜入青岳灵脉边缘的嗜血妖狼群。',
          action: '山门历练 青云宗 qy-bounty-1',
        },
      ],
    },
    {
      name: '丹霞谷',
      province: '南荒丹霞',
      mark: '丹',
      doctrine: '万火归元 · 济世丹道',
      motto: '丹火养生，济世求真',
      description: '深藏南荒十万群山之中。',
      welcome_gift: '回春灵泉',
      welcome_gift_count: 2,
      can_visit: true,
      visit_action: '拜山 丹霞谷',
      spar_chance: 60,
      spar_action: '山门演武 丹霞谷',
      treasures: [],
      bounties: [],
    },
  ],
}

describe('SectGateModal', () => {
  it('renders modal with player status and all sect selectors', () => {
    render(
      <SectGateModal
        open={true}
        onOpenChange={vi.fn()}
        sectVisit={mockSectVisit}
        busy={false}
        onAction={vi.fn()}
      />
    )

    expect(screen.getByText('九州各大宗门拜山案席')).toBeInTheDocument()
    expect(screen.getAllByText('青云宗').length).toBeGreaterThan(0)
    expect(screen.getByText('丹霞谷')).toBeInTheDocument()
    expect(screen.getByText('500')).toBeInTheDocument()
    expect(screen.getByText('50 灵石')).toBeInTheDocument()
  })

  it('allows switching between sects', () => {
    render(
      <SectGateModal
        open={true}
        onOpenChange={vi.fn()}
        sectVisit={mockSectVisit}
        busy={false}
        onAction={vi.fn()}
      />
    )

    const dxBtn = screen.getByRole('button', { name: /丹霞谷/i })
    fireEvent.click(dxBtn)

    expect(screen.getAllByText('南荒丹霞').length).toBeGreaterThan(0)
    expect(screen.getByText('“丹火养生，济世求真”')).toBeInTheDocument()
  })

  it('triggers visit action on 递帖拜山 button click', () => {
    const onAction = vi.fn()
    render(
      <SectGateModal
        open={true}
        onOpenChange={vi.fn()}
        sectVisit={mockSectVisit}
        busy={false}
        onAction={onAction}
      />
    )

    const visitBtn = screen.getByRole('button', { name: /递帖拜谒 青云宗/i })
    fireEvent.click(visitBtn)

    expect(onAction).toHaveBeenCalledWith('拜山 青云宗')
  })

  it('switches to treasures tab and acquires treasure', () => {
    const onAction = vi.fn()
    render(
      <SectGateModal
        open={true}
        onOpenChange={vi.fn()}
        sectVisit={mockSectVisit}
        busy={false}
        onAction={onAction}
      />
    )

    const tab = screen.getByRole('tab', { name: /求丹借宝/i })
    fireEvent.click(tab)

    expect(screen.getByText('青云宗 藏宝案席')).toBeInTheDocument()
    expect(screen.getByText('聚气丹')).toBeInTheDocument()

    const acquireBtns = screen.getAllByRole('button', { name: /求取仙珍/i })
    fireEvent.click(acquireBtns[0])

    expect(onAction).toHaveBeenCalledWith('求丹借宝 青云宗 qy-pill')
  })

  it('switches to spar tab and initiates arena sparring', () => {
    const onAction = vi.fn()
    render(
      <SectGateModal
        open={true}
        onOpenChange={vi.fn()}
        sectVisit={mockSectVisit}
        busy={false}
        onAction={onAction}
      />
    )

    const tab = screen.getByRole('tab', { name: /擂台演武/i })
    fireEvent.click(tab)

    expect(screen.getByText('青云宗 演武道台')).toBeInTheDocument()
    expect(screen.getByText('65%')).toBeInTheDocument()

    const sparBtn = screen.getByRole('button', { name: /登台切磋试剑/i })
    fireEvent.click(sparBtn)

    expect(onAction).toHaveBeenCalledWith('山门演武 青云宗')
  })

  it('switches to bounties tab and accepts sect bounty quest', () => {
    const onAction = vi.fn()
    render(
      <SectGateModal
        open={true}
        onOpenChange={vi.fn()}
        sectVisit={mockSectVisit}
        busy={false}
        onAction={onAction}
      />
    )

    const tab = screen.getByRole('tab', { name: /外务悬赏/i })
    fireEvent.click(tab)

    expect(screen.getByText('青云宗 山门悬赏黄绢令')).toBeInTheDocument()
    expect(screen.getByText('清剿青岳外围妖狼')).toBeInTheDocument()

    const bountyBtn = screen.getByRole('button', { name: /揭榜领受历练/i })
    fireEvent.click(bountyBtn)

    expect(onAction).toHaveBeenCalledWith('山门历练 青云宗 qy-bounty-1')
  })

  it('disables visit button when player has insufficient spirit stones', () => {
    const poorSectVisit: SectVisitSnapshot = {
      ...mockSectVisit,
      player_stones: 20, // less than 50
    }

    render(
      <SectGateModal
        open={true}
        onOpenChange={vi.fn()}
        sectVisit={poorSectVisit}
        busy={false}
        onAction={vi.fn()}
      />
    )

    const visitBtn = screen.getByRole('button', { name: /递帖拜谒 青云宗/i })
    expect(visitBtn).toBeDisabled()
    expect(screen.getByText(/灵石不足：拜山递帖需备好 50 灵石/i)).toBeInTheDocument()
  })
})
