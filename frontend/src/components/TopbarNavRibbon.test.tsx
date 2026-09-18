// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { TopbarNavRibbon } from './TopbarNavRibbon'

afterEach(() => cleanup())

describe('TopbarNavRibbon', () => {
  it('toggles sanctuary popovers and triggers corresponding callbacks', () => {
    const onOpenRealmsLadder = vi.fn()
    const onOpenGuide = vi.fn()
    const onOpenSectGate = vi.fn()
    const onOpenTianji = vi.fn()
    const onOpenLifebound = vi.fn()
    const onOpenArtifactSpirit = vi.fn()
    const onOpenEncounter = vi.fn()
    const onOpenPartnerChamber = vi.fn()
    const onOpenAncientTomb = vi.fn()
    const onToggleCodex = vi.fn()

    render(
      <TopbarNavRibbon
        hasPendingEncounter={true}
        onOpenRealmsLadder={onOpenRealmsLadder}
        onOpenGuide={onOpenGuide}
        onOpenSectGate={onOpenSectGate}
        onOpenTianji={onOpenTianji}
        onOpenLifebound={onOpenLifebound}
        onOpenArtifactSpirit={onOpenArtifactSpirit}
        onOpenEncounter={onOpenEncounter}
        onOpenPartnerChamber={onOpenPartnerChamber}
        onOpenAncientTomb={onOpenAncientTomb}
        onToggleCodex={onToggleCodex}
      />
    )

    // 1. 道途本纪
    const chronicleBtn = screen.getByRole('button', { name: /道途本纪/ })
    fireEvent.click(chronicleBtn)
    expect(screen.getByText('道途修行 · 指津本纪')).toBeInTheDocument()
    expect(screen.getByText('通天仙阶')).toBeInTheDocument()
    expect(screen.getByText('仙途指津')).toBeInTheDocument()
    expect(screen.getByText('洞天卷宗')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /通天仙阶/ }))
    expect(onOpenRealmsLadder).toHaveBeenCalledTimes(1)
    expect(screen.queryByText('道途修行 · 指津本纪')).not.toBeInTheDocument()

    // 2. 九州风云
    const worldBtn = screen.getByRole('button', { name: /九州风云/ })
    fireEvent.click(worldBtn)
    expect(screen.getByText('九州仙门 · 风云机缘')).toBeInTheDocument()
    expect(screen.getByText('拜山请益')).toBeInTheDocument()
    expect(screen.getByText('天机风云谱')).toBeInTheDocument()
    expect(screen.getByText('红尘奇遇')).toBeInTheDocument()
    expect(screen.getByText('机缘待决')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /拜山请益/ }))
    expect(onOpenSectGate).toHaveBeenCalledTimes(1)
    expect(screen.queryByText('九州仙门 · 风云机缘')).not.toBeInTheDocument()

    // 3. 洞天造化
    const mysteriesBtn = screen.getByRole('button', { name: /洞天造化/ })
    fireEvent.click(mysteriesBtn)
    expect(screen.getByText('本命造化 · 秘境同修')).toBeInTheDocument()
    expect(screen.getByText('本命灵宝')).toBeInTheDocument()
    expect(screen.getByText('器灵化形')).toBeInTheDocument()
    expect(screen.getByText('仙侣同修阁')).toBeInTheDocument()
    expect(screen.getByText('太古古墓秘境')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /本命灵宝/ }))
    expect(onOpenLifebound).toHaveBeenCalledTimes(1)
    expect(screen.queryByText('本命造化 · 秘境同修')).not.toBeInTheDocument()
  })
})
