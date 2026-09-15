// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { NineProvincesMap } from './NineProvincesMap'
import type { RegionAtlasItem } from './NineProvincesMap'

afterEach(() => cleanup())

const mockFiveRegions: RegionAtlasItem[] = [
  { key: '东洲', name: '东洲 · 青岳', current: true, visited: true, accessible: true, danger: 12, danger_label: '凡人安居', months: 0 },
  { key: '中州', name: '中州 · 天阙', current: false, visited: false, accessible: true, danger: 38, danger_label: '金丹历练', months: 3 },
  { key: '西漠', name: '西漠 · 流沙', current: false, visited: false, accessible: false, danger: 45, danger_label: '元婴历练', months: 4 },
  { key: '南疆', name: '南疆 · 赤炎', current: false, visited: false, accessible: false, danger: 50, danger_label: '元婴绝地', months: 4 },
  { key: '北原', name: '北原 · 寒渊', current: false, visited: false, accessible: false, danger: 65, danger_label: '化神冰渊', months: 5 },
]

describe('NineProvincesMap 2D Atlas', () => {
  it('renders all nine provinces in Nine Palaces Bagua geography', () => {
    const onSelect = vi.fn()
    render(
      <NineProvincesMap
        items={mockFiveRegions}
        selectedKey="东洲"
        onSelect={onSelect}
      />
    )

    // Verify all 9 provinces are rendered as interactive sectors
    const allNine = ['东洲', '中州', '西漠', '南疆', '北原', '雷州', '幽州', '云州', '瀛洲']
    for (const province of allNine) {
      expect(screen.getByRole('button', { name: new RegExp(`查看.*${province}.*地域`) })).toBeInTheDocument()
    }

    // Verify the vermilion seals for all 9
    const allChars = ['东', '中', '西', '南', '北', '雷', '幽', '云', '瀛']
    for (const char of allChars) {
      expect(screen.getAllByText(char)[0]).toBeInTheDocument()
    }

    // Verify outer sealed realms show "太古禁域"
    const sealedBadges = screen.getAllByText('太古禁域')
    expect(sealedBadges.length).toBeGreaterThanOrEqual(4)
  })

  it('selects province on click and supports keyboard navigation', () => {
    const onSelect = vi.fn()
    render(
      <NineProvincesMap
        items={mockFiveRegions}
        selectedKey="东洲"
        onSelect={onSelect}
      />
    )

    // Click an outer sealed territory (雷州)
    const leizhou = screen.getByRole('button', { name: /查看雷州/ })
    fireEvent.click(leizhou)
    expect(onSelect).toHaveBeenCalledWith('雷州')

    // Press Enter on another territory (幽州)
    const youzhou = screen.getByRole('button', { name: /查看幽州/ })
    fireEvent.keyDown(youzhou, { key: 'Enter' })
    expect(onSelect).toHaveBeenCalledWith('幽州')
  })

  it('toggles panoramic expansion mode', () => {
    const onSelect = vi.fn()
    const onTogglePanoramic = vi.fn()
    render(
      <NineProvincesMap
        items={mockFiveRegions}
        selectedKey="东洲"
        onSelect={onSelect}
        panoramic={false}
        onTogglePanoramic={onTogglePanoramic}
      />
    )

    const toggleBtn = screen.getByRole('button', { name: '展开全景' })
    expect(toggleBtn).toBeInTheDocument()
    fireEvent.click(toggleBtn)
    expect(onTogglePanoramic).toHaveBeenCalledTimes(1)
  })
})
