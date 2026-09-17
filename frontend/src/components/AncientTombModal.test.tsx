// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { AncientTombModal } from './AncientTombModal'
import type { AncientTombSnapshot, TombTileData } from '../api/types'

afterEach(() => cleanup())

const mockThemes = [
  {
    id: 'sword_crypt',
    name: '太古纯阳剑冢',
    description: '传闻上古纯阳剑仙羽化之所',
    recommended_realm: '筑基期',
    unlocked: true,
    special_drop: '古剑残片',
  },
  {
    id: 'ghost_crypt',
    name: '九幽冥帝古宫',
    description: '万劫不入的九幽冥殿沉于地底千丈',
    recommended_realm: '金丹期',
    unlocked: false,
    special_drop: '道韵',
  },
]

const mockGrid: TombTileData[] = []
for (let y = 0; y < 5; y++) {
  for (let x = 0; x < 5; x++) {
    if (x === 0 && y === 0) {
      mockGrid.push({
        x: 0,
        y: 0,
        type: 'entrance',
        name: '古墓甬道入口',
        description: '古墓入口石门',
        revealed: true,
        cleared: true,
      })
    } else if (x === 1 && y === 0) {
      mockGrid.push({
        x: 1,
        y: 0,
        type: 'treasure',
        name: '太古金丝楠玉匣',
        description: '沉睡万古的封印宝匣',
        revealed: true,
        cleared: false,
        reward_stones: 50,
      })
    } else {
      mockGrid.push({
        x,
        y,
        type: 'corridor',
        name: '幽暗石廊',
        description: '青石板铺就的墓道',
        revealed: false,
        cleared: false,
      })
    }
  }
}

describe('AncientTombModal', () => {
  it('renders theme selector and enters tomb when not currently exploring', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    const snapshot: AncientTombSnapshot = {
      active: false,
      current_tomb: null,
      themes: mockThemes,
      history: ['从太古纯阳剑冢安全撤离'],
    }

    render(
      <AncientTombModal
        open={true}
        onOpenChange={handleOpenChange}
        ancientTomb={snapshot}
        onAction={handleAction}
      />
    )

    expect(screen.getByText('太古大能秘境古墓')).toBeInTheDocument()
    expect(screen.getByText('太古纯阳剑冢')).toBeInTheDocument()
    expect(screen.getByText('九幽冥帝古宫')).toBeInTheDocument()
    expect(screen.getByText(/需达 金丹期/)).toBeInTheDocument()

    // Click enter button on sword_crypt
    const enterBtns = screen.getAllByRole('button', { name: /踏入古墓探险/ })
    fireEvent.click(enterBtns[0])
    expect(handleAction).toHaveBeenCalledWith('进入古墓 sword_crypt')
  })

  it('renders 5x5 grid, current tile info, moves and interacts during exploration', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    const snapshot: AncientTombSnapshot = {
      active: true,
      current_tomb: {
        id: 'sword_crypt',
        name: '太古纯阳剑冢',
        depth: 1,
        max_depth: 3,
        player_x: 0,
        player_y: 0,
        miasma: 12,
        loot_stones: 120,
        loot_items: { 灵铁: 2 },
        completed: false,
        grid: mockGrid,
        log: ['踏入太古大能秘境展开探险！'],
      },
      themes: mockThemes,
      history: [],
    }

    render(
      <AncientTombModal
        open={true}
        onOpenChange={handleOpenChange}
        ancientTomb={snapshot}
        onAction={handleAction}
      />
    )

    expect(screen.getByText('第 1 / 3 层')).toBeInTheDocument()
    expect(screen.getByText(/12 \/ 100/)).toBeInTheDocument()
    expect(screen.getByText(/灵石 \+120/)).toBeInTheDocument()
    expect(screen.getByText(/灵铁×2/)).toBeInTheDocument()

    // Current tile is (0, 0)
    expect(screen.getByText('古墓甬道入口')).toBeInTheDocument()

    // Click nav move button (向东 / 右)
    const rightBtn = screen.getByTitle('向东移动')
    fireEvent.click(rightBtn)
    expect(handleAction).toHaveBeenCalledWith('古墓移动 右')

    // Click safe retreat button
    const retreatBtn = screen.getByRole('button', { name: /安全撤离/ })
    fireEvent.click(retreatBtn)
    expect(handleAction).toHaveBeenCalledWith('古墓撤离')
  })

  it('triggers tile interaction when inspecting an uncleared treasure room', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    const snapshot: AncientTombSnapshot = {
      active: true,
      current_tomb: {
        id: 'sword_crypt',
        name: '太古纯阳剑冢',
        depth: 1,
        max_depth: 3,
        player_x: 1,
        player_y: 0,
        miasma: 15,
        loot_stones: 50,
        loot_items: {},
        completed: false,
        grid: mockGrid,
        log: ['移动至石室 (1, 0)'],
      },
      themes: mockThemes,
      history: [],
    }

    render(
      <AncientTombModal
        open={true}
        onOpenChange={handleOpenChange}
        ancientTomb={snapshot}
        onAction={handleAction}
      />
    )

    expect(screen.getByText('太古金丝楠玉匣')).toBeInTheDocument()
    const openChestBtn = screen.getByRole('button', { name: /解封开启宝匣/ })
    fireEvent.click(openChestBtn)
    expect(handleAction).toHaveBeenCalledWith('古墓探索')
  })
})
