// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { ShowcasePage } from '../api/types'
import { SHOWCASE_REVIEW_STORAGE_KEY } from '../showcaseReview'
import { ShowcaseNavigator } from './ShowcaseNavigator'

const pages: ShowcasePage[] = [
  { id: 'home', title: '洞府主界面', description: '检查主界面。', checklist: ['数值清楚'], snapshot: {} as ShowcasePage['snapshot'] },
  { id: 'battle', title: '临阵抉择', description: '检查战斗。', checklist: ['敌情清楚'], snapshot: {} as ShowcasePage['snapshot'] },
]

beforeEach(() => window.localStorage.clear())
afterEach(() => cleanup())

describe('ShowcaseNavigator', () => {
  it('persists checked pages and page notes', () => {
    render(<ShowcaseNavigator pages={pages} index={0} appVersion="1.0.0" onIndex={() => undefined} onExit={() => undefined} />)
    fireEvent.click(screen.getByRole('button', { name: '标记本页已检查' }))
    fireEvent.click(screen.getByText('记录本页问题或建议'))
    fireEvent.change(screen.getByPlaceholderText(/手机宽度/), { target: { value: '主界面在窄屏正常' } })

    expect(screen.getByText('已验收 1 / 2')).toBeTruthy()
    const saved = JSON.parse(window.localStorage.getItem(SHOWCASE_REVIEW_STORAGE_KEY) || '{}') as { completedIds?: string[]; notes?: Record<string, string> }
    expect(saved.completedIds).toEqual(['home'])
    expect(saved.notes?.home).toBe('主界面在窄屏正常')
  })

  it('copies a privacy-safe acceptance summary', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } })
    render(<ShowcaseNavigator pages={pages} index={0} appVersion="1.0.0" onIndex={() => undefined} onExit={() => undefined} />)

    fireEvent.click(screen.getByRole('button', { name: /复制摘要/ }))
    await waitFor(() => expect(writeText).toHaveBeenCalledOnce())
    expect(writeText.mock.calls[0][0]).toContain('《问道长生》V1.0.0 玩家验收摘要')
    expect(writeText.mock.calls[0][0]).toContain('不包含角色、存档、密钥或本机路径')
    expect(screen.getByRole('status').textContent).toContain('已复制')
  })
})
