// @vitest-environment jsdom

import * as Dialog from '@radix-ui/react-dialog'
import { useRef, useState } from 'react'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it } from 'vitest'
import { CodexDrawer } from './CodexDrawer'

function CodexExample() {
  const [open, setOpen] = useState(false)
  const trigger = useRef<HTMLButtonElement>(null)
  return <>
    <button ref={trigger} onClick={() => setOpen(true)}>打开侧记</button>
    <CodexDrawer open={open} onClose={() => setOpen(false)} returnFocusRef={trigger} hasUpdates
      character={<p>随身物品</p>} world={<p>众生近况</p>}
      pathways={<Dialog.Root><Dialog.Trigger>查看悟道</Dialog.Trigger><Dialog.Portal>
        <Dialog.Overlay /><Dialog.Content><Dialog.Title>悟道卷册</Dialog.Title><Dialog.Description>修行详情</Dialog.Description><Dialog.Close>返回侧记</Dialog.Close></Dialog.Content>
      </Dialog.Portal></Dialog.Root>}
    />
  </>
}

afterEach(() => cleanup())

describe('codex access', () => {
  it('organizes auxiliary content and returns keyboard focus on Escape', async () => {
    render(<CodexExample />)
    fireEvent.click(screen.getByRole('button', { name: '打开侧记' }))
    const drawer = screen.getByRole('dialog', { name: '洞天侧记' })
    expect(within(drawer).getByText('随身物品')).toBeVisible()
    fireEvent.click(within(drawer).getByRole('button', { name: '尘世见闻' }))
    expect(within(drawer).getByText('众生近况')).toBeVisible()
    expect(within(drawer).queryByText('随身物品')).not.toBeInTheDocument()
    fireEvent.keyDown(document.activeElement || drawer, { key: 'Escape', code: 'Escape' })
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(screen.getByRole('button', { name: '打开侧记' })).toHaveFocus()
  })

  it('opens a system dialog over the drawer and returns without losing the category', async () => {
    render(<CodexExample />)
    fireEvent.click(screen.getByRole('button', { name: '打开侧记' }))
    fireEvent.click(screen.getByRole('button', { name: /修行百艺/ }))
    fireEvent.click(screen.getByRole('button', { name: '查看悟道' }))
    expect(screen.getByRole('dialog', { name: '悟道卷册' })).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: '返回侧记' }))
    await waitFor(() => expect(screen.getByRole('dialog', { name: '洞天侧记' })).toBeVisible())
    expect(screen.getByRole('button', { name: /修行百艺/ })).toHaveAttribute('aria-pressed', 'true')
  })
})
