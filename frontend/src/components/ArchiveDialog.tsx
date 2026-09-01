import * as Dialog from '@radix-ui/react-dialog'
import { CalendarDays, FileDown, FolderOpen, Save, ScrollText, Upload, X } from 'lucide-react'
import { useRef, useState } from 'react'
import { fetchSaveExport, importSave } from '../api/client'
import type { Snapshot } from '../api/types'

interface ArchiveDialogProps {
  saves: Snapshot['save_summaries']
  busy: boolean
  onAction: (action: string) => void
  onChanged: () => Promise<unknown> | void
  onNotice: (message: string) => void
}

const value = (item: Record<string, unknown>, key: string, fallback = '—') => String(item[key] ?? fallback)

const MAX_IMPORT_BYTES = 2 * 1024 * 1024

export function ArchiveDialog({ saves, busy, onAction, onChanged, onNotice }: ArchiveDialogProps) {
  const [name, setName] = useState('autosave')
  const [confirming, setConfirming] = useState('')
  const [transferring, setTransferring] = useState('')
  const [transferStatus, setTransferStatus] = useState<{ tone: 'success' | 'error'; text: string } | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)
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
  const download = async (saveName: string) => {
    setTransferring(`export:${saveName}`)
    setTransferStatus(null)
    try {
      const blob = await fetchSaveExport(saveName)
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `${saveName}-问道长生存档.json`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      URL.revokeObjectURL(url)
      const message = `“${saveName}”已导出，可复制到新版目录或其他电脑。`
      setTransferStatus({ tone: 'success', text: message })
      onNotice(message)
    } catch (reason) {
      setTransferStatus({ tone: 'error', text: reason instanceof Error ? reason.message : '导出失败。' })
    } finally {
      setTransferring('')
    }
  }
  const upload = async (file: File | undefined) => {
    if (!file) return
    setTransferring('import')
    setTransferStatus(null)
    try {
      if (file.size > MAX_IMPORT_BYTES) throw new Error('存档超过 2 MB 安全上限。')
      const parsed = JSON.parse(await file.text()) as unknown
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error('存档必须是 JSON 对象。')
      const data = parsed as Record<string, unknown>
      const fileName = file.name.replace(/\.json$/i, '').replace(/-问道长生存档$/, '')
      const preferred = data.format === 'wendao-changsheng-save' ? '' : fileName
      const result = await importSave(data, preferred)
      await onChanged()
      const message = result.renamed
        ? `同名卷宗已存在，安全导入为“${result.name}”。`
        : `已导入“${result.name}”，可在下方确认读取。`
      setTransferStatus({ tone: 'success', text: message })
      onNotice(message)
    } catch (reason) {
      setTransferStatus({ tone: 'error', text: reason instanceof Error ? reason.message : '导入失败。' })
    } finally {
      setTransferring('')
      if (fileInput.current) fileInput.current.value = ''
    }
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
          <section className="save-transfer">
            <div><span><Upload size={16} /></span><div><h3>迁移卷宗</h3><p>支持便携卷宗和旧版原始 JSON；同名默认另存，不会静默覆盖。</p></div><button type="button" disabled={busy || Boolean(transferring)} onClick={() => fileInput.current?.click()}><Upload size={14} />{transferring === 'import' ? '正在校验…' : '导入存档文件'}</button></div>
            <input ref={fileInput} type="file" accept=".json,application/json" onChange={(event) => void upload(event.target.files?.[0])} />
            {transferStatus && <p className="save-transfer-status" data-tone={transferStatus.tone}>{transferStatus.text}</p>}
          </section>
          <section className="save-list"><h3><ScrollText size={15} />已有卷宗 <small>{saves.length} 份</small></h3>
            {saves.length ? <div>{saves.map((item) => {
              const saveName = value(item, 'name')
              const selected = confirming === saveName
              const exporting = transferring === `export:${saveName}`
              return <article key={saveName}><span>{value(item, 'player_name', '无名修士').slice(0, 1)}</span><div><strong>{saveName}</strong><p>{value(item, 'player_name', '无名修士')} · {value(item, 'realm', '凡人')}</p><small><CalendarDays size={11} />天玄历 {value(item, 'calendar_year', '387')} 年 {value(item, 'month', '1')} 月 · 第 {value(item, 'turn', '0')} 回合</small></div><div className="save-entry-actions"><button type="button" title="导出为带校验值的便携卷宗" disabled={busy || Boolean(transferring)} onClick={() => void download(saveName)}><FileDown size={14} />{exporting ? '导出中…' : '导出'}</button><button type="button" data-confirm={selected || undefined} disabled={busy || Boolean(transferring)} onClick={() => load(saveName)}><FolderOpen size={14} />{selected ? '再次点击确认' : '读取'}</button></div></article>
            })}</div> : <div className="empty-save"><ScrollText size={25} /><p>还没有已保存的卷宗。</p></div>}
          </section>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
