// @vitest-environment jsdom

import { cleanup, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Decision } from '../api/types'
import { DecisionPanel } from './DecisionPanel'
import { TooltipProvider } from './GameTooltip'

afterEach(() => cleanup())

const decision = {
  eyebrow: '破境路线', title: '选择此番道基', hint: '一次选择会改变此后的仙途。', exclusive: true,
  choices: [
    { label: '人道筑基', action: '突破 人道', summary: '心魔 90%', description: '稳守根基。', tone: 'safe', tooltip: '风险最低，成长较稳。' },
    { label: '天道筑基', action: '突破 天道', summary: '心魔 54%', description: '逆天一搏。', tone: 'danger', disabled: true, disabled_reason: '缺少天道筑基丹' },
  ],
} as Decision

describe('decision presentation', () => {
  it('exposes selected, risk explanation and disabled states consistently', () => {
    render(<TooltipProvider><DecisionPanel decision={decision} activeAction="突破 人道" busy onChoose={vi.fn()} /></TooltipProvider>)
    expect(screen.getByRole('button', { name: /人道筑基/ })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: /人道筑基/ })).toHaveAttribute('aria-busy', 'true')
    expect(screen.getByLabelText('人道筑基说明')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /天道筑基/ })).toBeDisabled()
  })
})
