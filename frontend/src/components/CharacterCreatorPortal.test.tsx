// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { StartGamePortal } from './StartGamePortal'
import { CharacterCreatorPortal } from './CharacterCreatorPortal'

afterEach(() => {
  cleanup()
})

describe('StartGamePortal', () => {
  it('triggers "开始游戏" on clicking step into cultivation', () => {
    const act = vi.fn()
    const openArchive = vi.fn()
    render(<StartGamePortal busy={false} saveSummaries={[]} onAction={act} onOpenArchive={openArchive} />)

    fireEvent.click(screen.getByRole('button', { name: /踏入仙途/ }))
    expect(act).toHaveBeenCalledWith('开始游戏')

    fireEvent.click(screen.getByRole('button', { name: /查阅洞天卷宗/ }))
    expect(openArchive).toHaveBeenCalled()
  })
})

describe('CharacterCreatorPortal', () => {
  it('formats and submits valid step 1 character basic creation command', () => {
    const act = vi.fn()
    render(<CharacterCreatorPortal phase="character_creation_basic" busy={false} onAction={act} />)

    // Change name
    const nameInput = screen.getByPlaceholderText('请输入姓名')
    fireEvent.change(nameInput, { target: { value: '楚凌霄' } })

    // Submit step one
    const submitBtn = screen.getByRole('button', { name: /步入灵台 · 测定道骨/ })
    fireEvent.click(submitBtn)

    expect(act).toHaveBeenCalled()
    const callArg = act.mock.calls[0][0] as string
    expect(callArg).toContain('姓名=楚凌霄')
    expect(callArg).toContain('性别=')
    expect(callArg).toContain('年龄=')
    expect(callArg).toContain('相貌=')
    expect(callArg).toContain('出身=')
    expect(callArg).toContain('道途=')
  })

  it('submits valid step 2 traits command when points are 60 and talents are 5', () => {
    const act = vi.fn()
    render(<CharacterCreatorPortal phase="character_creation_traits" busy={false} onAction={act} />)

    // Default setup is 60 attribute points and 5 talent points
    const submitBtn = screen.getByRole('button', { name: /天命已定 · 踏入仙途/ })
    expect(submitBtn).not.toBeDisabled()

    fireEvent.click(submitBtn)
    expect(act).toHaveBeenCalled()
    const callArg = act.mock.calls[0][0] as string
    expect(callArg).toContain('灵根=')
    expect(callArg).toContain('体质=')
    expect(callArg).toContain('资质=10')
    expect(callArg).toContain('悟性=10')
    expect(callArg).toContain('神识=10')
    expect(callArg).toContain('遁速=10')
    expect(callArg).toContain('道心=10')
    expect(callArg).toContain('仙缘=10')
    expect(callArg).toContain('天赋=')
  })

  it('allows returning to step one from step two', () => {
    const act = vi.fn()
    render(<CharacterCreatorPortal phase="character_creation_traits" busy={false} onAction={act} />)

    const backBtn = screen.getByRole('button', { name: /返回修改凡尘资料/ })
    fireEvent.click(backBtn)
    expect(act).toHaveBeenCalledWith('返回上一步')
  })
})
