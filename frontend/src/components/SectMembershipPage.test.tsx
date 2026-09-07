// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { SectMembershipSnapshot } from '../api/types'
import { SectMembershipEntry, SectMembershipPage } from './SectMembershipPage'

afterEach(() => cleanup())

const membership = {
  member: true, sect: '青云宗', rank: '外门弟子', contribution: 120, privileges: ['青云宗外门权限'],
  tasks: [
    { name: '采药', mark: '采', attribute: '福缘', attribute_value: 16, chance: 90, stones: 30, contribution: 8, rewards: { 灵药: 2 }, tone: 'safe', action: '宗门任务 采药' },
    { name: '猎妖', mark: '猎', attribute: '遁速', attribute_value: 12, chance: 82, stones: 60, contribution: 12, rewards: { 妖兽材料: 1 }, tone: 'danger', action: '宗门任务 猎妖' },
  ],
  promotion: { target: '内门弟子', contribution_required: 100, contribution_met: true, minimum_realm: 0, minimum_realm_label: '炼气', realm_met: true, chance: 76, available: true, reason: '资历已足，可以申请晋升试炼', action: '申请晋升' },
  tournament: { available: false, participated: false, result: '', next_year: 390, reason: '下一届：天玄历 390 年', action: '宗门大比' },
} as SectMembershipSnapshot

describe('ordinary sect membership surface', () => {
  it('turns tasks, promotion and tournament into rule-backed controls', () => {
    const act = vi.fn()
    render(<SectMembershipPage membership={membership} busy={false} onAction={act} />)
    expect(screen.getByRole('heading', { name: '青云宗' })).toBeInTheDocument()
    expect(screen.getByText('灵石 +30 · 贡献 +8 · 灵药×2')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: '下一届：天玄历 390 年' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: '申请晋升试炼' }))
    fireEvent.click(screen.getAllByRole('button', { name: '领取差事' })[0])
    expect(act).toHaveBeenNthCalledWith(1, '申请晋升')
    expect(act).toHaveBeenNthCalledWith(2, '宗门任务 采药')
  })

  it('offers the same sect page from the system hub without executing in read-only mode', () => {
    const act = vi.fn()
    const { rerender } = render(<SectMembershipEntry membership={membership} busy={false} readOnly onAction={act} />)
    expect(screen.getByRole('button', { name: /本宗事务/ })).toBeDisabled()
    rerender(<SectMembershipEntry membership={membership} busy={false} onAction={act} />)
    fireEvent.click(screen.getByRole('button', { name: /本宗事务/ }))
    expect(act).toHaveBeenCalledExactlyOnceWith('宗门')
  })
})
