// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ActionDock } from './ActionDock'
import { useUiStore } from '../store/ui'
import type { RecoverySnapshot } from '../api/types'

afterEach(() => { cleanup(); useUiStore.getState().clearDraft() })

describe('action drafts', () => {
  it('requires explicit execution after inserting and editing a draft', () => {
    const act = vi.fn()
    render(<ActionDock busy={false} canQuickAct canDraft onAction={act} />)
    fireEvent.click(screen.getByRole('button', { name: '谨慎探索青岳山麓' }))
    expect(act).not.toHaveBeenCalled()
    fireEvent.change(screen.getByRole('textbox', { name: '行动草稿' }), { target: { value: '探索 青岳山麓' } })
    fireEvent.click(screen.getByRole('button', { name: '推演此行' }))
    expect(act).toHaveBeenCalledExactlyOnceWith('探索 青岳山麓')
  })

  it('does not consume the real draft in showcase mode', () => {
    useUiStore.getState().setDraft('我的未完成计划')
    const act = vi.fn()
    render(<ActionDock busy={false} canQuickAct canDraft readOnly onAction={act} />)
    fireEvent.click(screen.getByRole('button', { name: '推演此行' }))
    fireEvent.click(screen.getByRole('button', { name: '吐纳修炼' }))
    expect(screen.getByRole('textbox')).toBeDisabled()
    expect(act).not.toHaveBeenCalled()
    expect(useUiStore.getState().draft).toBe('我的未完成计划')
  })

  it('offers injury recovery using the rule engine action and availability', () => {
    const act = vi.fn()
    const recovery = { active: true, can_rest: false, rest_reason: '当前伤势不能通过静养恢复', rest_action: '静养' } as RecoverySnapshot
    const { rerender } = render(<ActionDock busy={false} canQuickAct canDraft recovery={recovery} onAction={act} />)
    expect(screen.getByRole('button', { name: '静养疗伤' })).toBeDisabled()
    rerender(<ActionDock busy={false} canQuickAct canDraft recovery={{ ...recovery, can_rest: true }} onAction={act} />)
    fireEvent.click(screen.getByRole('button', { name: '静养疗伤' }))
    expect(act).toHaveBeenCalledExactlyOnceWith('静养')
  })

  it('surfaces the highest-priority rule-backed contextual action', () => {
    const act = vi.fn()
    render(<ActionDock busy={false} canQuickAct canDraft contextActions={[{ action: '突破', label: '叩问突破', description: '炼气·圆满修为已圆满', tone: 'breakthrough' }]} onAction={act} />)
    const breakthrough = screen.getByRole('button', { name: /叩问突破/ })
    expect(breakthrough).toHaveAttribute('title', '炼气·圆满修为已圆满')
    fireEvent.click(breakthrough)
    expect(act).toHaveBeenCalledExactlyOnceWith('突破')
  })

  it('allows one-click execution of selectable actions across categories without manual typing', () => {
    const act = vi.fn()
    render(<ActionDock busy={false} canQuickAct canDraft onAction={act} />)

    // Default category is 潜修 (cultivation)
    fireEvent.click(screen.getByRole('button', { name: '闭关三月' }))
    expect(act).toHaveBeenCalledWith('闭关3月')

    // Switch to 历练 (adventure)
    fireEvent.click(screen.getByRole('tab', { name: '历练' }))
    fireEvent.click(screen.getByRole('button', { name: '探索山麓' }))
    expect(act).toHaveBeenCalledWith('探索 青岳山麓')

    // Switch to 生财 (economy)
    fireEvent.click(screen.getByRole('tab', { name: '生财' }))
    fireEvent.click(screen.getByRole('button', { name: '前往坊市' }))
    expect(act).toHaveBeenCalledWith('坊市')

    // Switch to 红尘 (social)
    fireEvent.click(screen.getByRole('tab', { name: '红尘' }))
    fireEvent.click(screen.getByRole('button', { name: '仙门重地' }))
    expect(act).toHaveBeenCalledWith('宗门')

    expect(act).toHaveBeenCalledTimes(4)
  })

  it('disables selectable action cards when quick action is not permitted', () => {
    const act = vi.fn()
    render(<ActionDock busy={false} canQuickAct={false} canDraft onAction={act} />)
    const cultivateBtn = screen.getByRole('button', { name: '吐纳修炼' })
    expect(cultivateBtn).toBeDisabled()
    fireEvent.click(cultivateBtn)
    expect(act).not.toHaveBeenCalled()
  })
})

