import * as Dialog from '@radix-ui/react-dialog'
import { CalendarDays, Download, Save, ScrollText, X } from 'lucide-react'
import { useState } from 'react'
import type { Snapshot } from '../api/types'

interface ArchiveDialogProps {
  saves: Snapshot['save_summaries']
  busy: boolean
  onAction: (action: string) => void
}

const value = (item: Record<string, unknown>, key: string, fallback = '—') => String(item[key] ?? fallback)

export function ArchiveDialog({ saves, busy, onAction }: ArchiveDialogProps) {
  const [name, setName] = useState('autosave')
  const [confirming, setConfirming] = useState('')
  const submitSave = () => {
    const normalized = name.trim() || 'autosave'
    onAction(`存档 ${normalized}`)
  }
  const load = (saveName: string) => {
    if (confirming !== saveName) {
      setConfirming(saveName)
      return
    }
    setConfirming('')
    onAction(`读档 ${saveName}`)
  }
  return (
    <Dialog.Root onOpenChange={() => setConfirming('')}>
      <Dialog.Trigger asChild><button className="archive-trigger" type="button"><Save size={16} />洞天卷宗</button></Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog archive-dialog">
          <header><div><p>本地卷宗</p><Dialog.Title>存档与读档</Dialog.Title><Dialog.Description>存档保存在你的电脑中；覆盖旧档前会自动留存备份。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
          <section className="save-create">
            <label htmlFor="save-name">卷宗名称</label>
            <div><input id="save-name" value={name} maxLength={48} onChange={(event) => setName(event.target.value)} placeholder="例如：筑基之前" /><button type="button" disabled={busy} onClick={submitSave}><Save size={15} />保存当前进度</button></div>
            <small>同名卷宗会被新进度覆盖，但上一个版本仍会保留为备份。</small>
          </section>
          <section className="save-list"><h3><ScrollText size={15} />已有卷宗 <small>{saves.length} 份</small></h3>
            {saves.length ? <div>{saves.map((item) => {
              const saveName = value(item, 'name')
              const selected = confirming === saveName
              return <article key={saveName}><span>{value(item, 'player_name', '无名修士').slice(0, 1)}</span><div><strong>{saveName}</strong><p>{value(item, 'player_name', '无名修士')} · {value(item, 'realm', '凡人')}</p><small><CalendarDays size={11} />天玄历 {value(item, 'calendar_year', '387')} 年 {value(item, 'month', '1')} 月 · 第 {value(item, 'turn', '0')} 回合</small></div><button type="button" data-confirm={selected || undefined} disabled={busy} onClick={() => load(saveName)}><Download size={14} />{selected ? '再次点击确认' : '读取'}</button></article>
            })}</div> : <div className="empty-save"><ScrollText size={25} /><p>还没有已保存的卷宗。</p></div>}
          </section>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
