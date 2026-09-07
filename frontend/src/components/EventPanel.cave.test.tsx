// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { CaveSnapshot, Presentation } from '../api/types'
import { EventPanel } from './EventPanel'

afterEach(() => cleanup())

const presentation = {
  action: '洞府', title: '青岳石屋', eyebrow: '洞府', seal: '府', tone: 'cultivation', paragraphs: ['洞府灵机安稳流转。'], changes: [], details: '', has_details: false,
  blocks: [{
    type: 'facilities', title: '青岳石屋', aura: '浓郁', crops: '灵药幼苗', items: [
      { name: '静室', level: 1, cost_stones: 200, materials: {}, affordable: true, disabled_reason: '', action: '升级洞府 静室' },
      { name: '丹房', level: 0, cost_stones: 300, materials: { 灵木: 2 }, affordable: false, disabled_reason: '缺少 灵木×2', action: '升级洞府 丹房' },
    ],
  }],
} as Presentation

const cave = {
  name: '青岳石屋', aura: '浓郁', spirit_energy: 12, spirit_energy_cap: 30, monthly_generation: 4, focus: '蕴养灵脉', focuses: [], capacity: 1, active_jobs: 0, jobs: [], blueprints: [], last_event: '', ledger: [], can_recuperate: true, recuperate_reason: '',
} as CaveSnapshot

describe('cave scene hotspots', () => {
  it('selects a facility on the landscape without advancing the game', () => {
    const act = vi.fn()
    render(<EventPanel presentation={presentation} cave={cave} immersive onAction={act} />)
    expect(screen.getByLabelText('洞府设施分布')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /丹房/ }))
    expect(screen.getByRole('heading', { name: '丹房' })).toBeInTheDocument()
    screen.getAllByRole('button', { name: '缺少 灵木×2' }).forEach((button) => expect(button).toBeDisabled())
    expect(act).not.toHaveBeenCalled()
  })
})
