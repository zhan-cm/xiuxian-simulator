// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Presentation } from '../api/types'
import { EventPanel } from './EventPanel'

afterEach(() => cleanup())

const presentationWithSects = {
  action: '寻仙访道',
  title: '九州名山大川',
  eyebrow: '宗门',
  seal: '宗',
  tone: 'world',
  paragraphs: ['九州大地，仙门耸峙。'],
  changes: [],
  details: '',
  has_details: false,
  blocks: [
    {
      type: 'sects',
      title: '九州仙门',
      items: [
        {
          name: '天剑宗',
          description: '以剑证道，直指上清。',
          action: '申请试炼 天剑宗',
        },
      ],
    },
  ],
} as unknown as Presentation

describe('SectsBlock in EventPanel', () => {
  it('renders harmonized action buttons and triggers callbacks', () => {
    const onAction = vi.fn()
    const onOpenSectGate = vi.fn()

    render(
      <EventPanel
        presentation={presentationWithSects}
        readOnly={false}
        onAction={onAction}
        onOpenSectGate={onOpenSectGate}
      />
    )

    const visitBtn = screen.getByRole('button', { name: /登门拜山/ })
    expect(visitBtn).toBeInTheDocument()
    expect(visitBtn).toHaveClass('sect-action-btn')
    expect(visitBtn).toHaveClass('sect-visit-btn')

    const trialBtn = screen.getByRole('button', { name: /申请试炼/ })
    expect(trialBtn).toBeInTheDocument()
    expect(trialBtn).toHaveClass('sect-action-btn')
    expect(trialBtn).toHaveClass('sect-trial-btn')

    // Click visit
    fireEvent.click(visitBtn)
    expect(onOpenSectGate).toHaveBeenCalledWith('天剑宗')

    // Click trial
    fireEvent.click(trialBtn)
    expect(onAction).toHaveBeenCalledWith('申请试炼 天剑宗')
  })
})
