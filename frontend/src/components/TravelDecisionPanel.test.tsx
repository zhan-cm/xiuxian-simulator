// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Decision, TravelSnapshot } from '../api/types'
import { TooltipProvider } from './GameTooltip'
import { TravelDecisionPanel } from './TravelDecisionPanel'

afterEach(() => cleanup())

const decision = {
  eyebrow: '跨域行旅', title: '从东洲前往中州', hint: '远行会一次结算数月岁月。', exclusive: true,
  choices: [
    { label: '随商队同行 · 6 月', action: '行旅选择 caravan', summary: '消耗 180 灵石', description: '路途较慢，但有人照应。', tone: 'safe' },
    { label: '御风独行 · 3 月', action: '行旅选择 swift', summary: '消耗 54 灵力', description: '更快抵达，沿途风险更高。', tone: 'primary', disabled: true, disabled_reason: '需要 54 灵力，当前仅有 20' },
    { label: '暂不启程', action: '行旅选择 cancel', description: '留在当前地域。', tone: 'quiet' },
  ],
} as Decision

const travel = {
  current: '东洲', current_name: '东洲', visited: ['东洲'], pending: { origin: '东洲', destination: '中州', distance: 3 }, trade_profit: 0,
  current_reputation: {}, history: [], regions: [
    { key: '东洲', name: '东洲', minimum_realm: 0, minimum_realm_label: '炼气可达', danger: 12, description: '', specialties: [], demands: [], months: 0, current: true, visited: true, accessible: true, action: '', reputation: 20, rank: '小有声名', buy_discount: 0, sell_bonus: 0, travel_bonus: 0, exploration_bonus: 0 },
    { key: '中州', name: '中州', minimum_realm: 1, minimum_realm_label: '筑基可达', danger: 38, description: '', specialties: [], demands: [], months: 3, current: false, visited: false, accessible: true, action: '前往 中州', reputation: 0, rank: '初来乍到', buy_discount: 0, sell_bonus: 0, travel_bonus: 0, exploration_bonus: 0 },
  ],
} as TravelSnapshot

describe('cross-region journey surface', () => {
  it('shows the route, cost and rule-backed availability before departure', () => {
    const act = vi.fn()
    render(<TooltipProvider><TravelDecisionPanel decision={decision} travel={travel} activeAction="" busy={false} onChoose={act} /></TooltipProvider>)
    expect(screen.getByLabelText('行程路线：东洲前往中州')).toBeInTheDocument()
    expect(screen.getByText('180 灵石')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /御风独行/ })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: /随商队同行/ }))
    expect(act).toHaveBeenCalledExactlyOnceWith('行旅选择 caravan')
  })

  it('keeps every route choice inert in showcase mode', () => {
    const act = vi.fn()
    render(<TooltipProvider><TravelDecisionPanel decision={decision} travel={travel} activeAction="" busy={false} readOnly onChoose={act} /></TooltipProvider>)
    expect(screen.getByRole('button', { name: /随商队同行/ })).toBeDisabled()
    expect(screen.getByRole('button', { name: /巡览中不可更改行程/ })).toBeDisabled()
    expect(act).not.toHaveBeenCalled()
  })
})
