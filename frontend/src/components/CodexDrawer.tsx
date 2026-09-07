import * as Dialog from '@radix-ui/react-dialog'
import { BookOpen, HeartHandshake, UserRound, X } from 'lucide-react'
import { useState, type ReactNode, type RefObject } from 'react'

interface Props {
  open: boolean
  onClose: () => void
  returnFocusRef: RefObject<HTMLButtonElement | null>
  character: ReactNode
  pathways: ReactNode
  world: ReactNode
  hasUpdates: boolean
}

export function CodexDrawer({ open, onClose, returnFocusRef, character, pathways, world, hasUpdates }: Props) {
  const [section, setSection] = useState<'character' | 'pathways' | 'world'>('character')
  const sections = [
    { id: 'character' as const, label: '修士与行囊', icon: UserRound, content: character },
    { id: 'pathways' as const, label: '修行百艺', icon: BookOpen, content: pathways },
    { id: 'world' as const, label: '尘世见闻', icon: HeartHandshake, content: world },
  ]
  const active = sections.find((item) => item.id === section)!
  return (
    <Dialog.Root open={open} onOpenChange={(nextOpen) => { if (!nextOpen) onClose() }}>
      <Dialog.Portal>
        <Dialog.Overlay className="codex-overlay" />
        <Dialog.Content className="immersive-codex" onCloseAutoFocus={(event) => {
          if (returnFocusRef.current?.isConnected) {
            event.preventDefault()
            returnFocusRef.current.focus()
          }
        }}>
          <header><div><span>随身卷册</span><Dialog.Title>洞天侧记</Dialog.Title></div><Dialog.Close aria-label="关闭洞天侧记"><X size={19} /></Dialog.Close></header>
          <Dialog.Description className="codex-description">查看随身藏品、修行诸事与尘世见闻。</Dialog.Description>
          <div className="codex-sections" role="group" aria-label="侧记分类">
            {sections.map(({ id, label, icon: Icon }) => <button type="button" key={id} aria-pressed={section === id} onClick={() => setSection(id)}><Icon size={16} />{label}{id === 'pathways' && hasUpdates && <i aria-label="有可推进事项" />}</button>)}
          </div>
          <div className="codex-content" key={section} role="region" aria-label={active.label}>{active.content}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
