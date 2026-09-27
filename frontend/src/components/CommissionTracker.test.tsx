// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ActiveCommission, CommissionSnapshot } from '../api/types'
import { CommissionTracker } from './CommissionTracker'

afterEach(cleanup)

const commission = {
  id: 'herb-delivery@0',
  title: '青岳采露',
  location: '东洲·青岳山麓或坊市',
  how_to: '探索青岳山麓可采到灵药，也可在坊市购买。',
  current: 1,
  required: 3,
  turns_left: 4,
  ready: false,
  expired: false,
  next_action: '探索 青岳山麓',
  next_label: '去青岳山麓采药',
  action_hint: '探索耗时 1 个月',
} as ActiveCommission

const snapshot = {
  active: [commission],
  active_count: 1,
  active_limit: 2,
} as CommissionSnapshot

describe('CommissionTracker', () => {
  it('shows location, method, progress and a direct next step', () => {
    const onAction = vi.fn()
    render(<CommissionTracker commissions={snapshot} busy={false} canAct onAction={onAction} onOpenBoard={vi.fn()} />)
    expect(screen.getByText('东洲·青岳山麓或坊市')).toBeInTheDocument()
    expect(screen.getByText('进度 1/3')).toBeInTheDocument()
    expect(screen.getByText(/探索青岳山麓可采到灵药/)).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '去青岳山麓采药' }))
    expect(onAction).toHaveBeenCalledExactlyOnceWith('探索 青岳山麓')
  })

  it('uses the updated delivery action when ready and disables actions while busy', () => {
    const onAction = vi.fn()
    const ready = { ...commission, ready: true, current: 3, next_action: '交付委托 herb-delivery@0', next_label: '交付委托并领取报酬' }
    const { rerender } = render(<CommissionTracker commissions={{ ...snapshot, active: [ready] }} busy={false} canAct onAction={onAction} onOpenBoard={vi.fn()} />)
    fireEvent.click(screen.getByRole('button', { name: '交付委托并领取报酬' }))
    expect(onAction).toHaveBeenCalledExactlyOnceWith('交付委托 herb-delivery@0')
    rerender(<CommissionTracker commissions={snapshot} busy canAct onAction={onAction} onOpenBoard={vi.fn()} />)
    expect(screen.getByRole('button', { name: '去青岳山麓采药' })).toBeDisabled()
  })

  it('does not take space when no commission is active', () => {
    const { container } = render(<CommissionTracker commissions={{ ...snapshot, active: [], active_count: 0 }} busy={false} canAct onAction={vi.fn()} onOpenBoard={vi.fn()} />)
    expect(container).toBeEmptyDOMElement()
  })
})
