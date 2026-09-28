import * as Dialog from '@radix-ui/react-dialog'
import { CalendarDays, FileDown, FolderOpen, RotateCcw, Save, ScrollText, Trash2, Upload, X } from 'lucide-react'
import { useRef, useState } from 'react'
import { deleteSave, fetchSaveExport, importSave } from '../api/client'
import type { Snapshot } from '../api/types'

interface ArchiveDialogProps {
  saves: Snapshot['save_summaries']
  busy: boolean
  canSave: boolean
  onAction: (action: string) => void
  onChanged: () => Promise<unknown> | void
  onNotice: (message: string) => void
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

const value = (item: Record<string, unknown>, key: string, fallback = '—') => String(item[key] ?? fallback)

const MAX_IMPORT_BYTES = 2 * 1024 * 1024

export function ArchiveDialog({ saves, busy, canSave, onAction, onChanged, onNotice, open, onOpenChange }: ArchiveDialogProps) {
  const [name, setName] = useState('手动存档')
  const [confirming, setConfirming] = useState('')
  const [transferring, setTransferring] = useState('')
  const [transferStatus, setTransferStatus] = useState<{ tone: 'success' | 'error'; text: string } | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)
  const submitSave = () => {
    const normalized = name.trim() || '手动存档'
    if (saves.some((item) => item.name === normalized) && !window.confirm(`“${normalized}”已存在。确定覆盖这份卷宗吗？`)) return
    onAction(`存档 ${normalized}`)
  }
  const load = (saveName: string) => {
    if (confirming !== saveName) {
      setConfirming(saveName)
      return
    }
    setConfirming('')
    onAction(`读档 ${saveName}`)
    onOpenChange?.(false)
  }
  const remove = async (saveName: string) => {
    if (!window.confirm(`删除“${saveName}”及其备份？文件会移入本地回收目录，不会重置当前角色；继续行动可能重新生成自动存档。`)) return
    setTransferring(`delete:${saveName}`)
    setTransferStatus(null)
    try {
      const result = await deleteSave(saveName)
      setConfirming('')
      await onChanged()
      const message = `“${saveName}”已删除，不会重置当前角色。可恢复文件位于：${result.recovery_directory}`
      setTransferStatus({ tone: 'success', text: message })
      onNotice(message)
    } catch (reason) {
      setTransferStatus({ tone: 'error', text: reason instanceof Error ? reason.message : '删除失败。' })
    } finally {
      setTransferring('')
    }
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
    <Dialog.Root
      open={open}
      onOpenChange={(next) => {
        setConfirming('')
        onOpenChange?.(next)
      }}
    >
      <Dialog.Trigger asChild><button className="archive-trigger" type="button"><Save size={16} />洞天卷宗</button></Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog archive-dialog">
          <header><div><p>本地卷宗</p><Dialog.Title>存档与读档</Dialog.Title><Dialog.Description>存档保存在你的电脑中；覆盖旧档前会自动留存备份。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
          <section className="save-create">
            <label htmlFor="save-name">卷宗名称</label>
            <div><input id="save-name" value={name} maxLength={48} onChange={(event) => setName(event.target.value)} placeholder="例如：筑基之前" /><button type="button" disabled={busy || !canSave} onClick={submitSave}><Save size={15} />保存当前进度</button></div>
            {!canSave && <small>开始游戏后才能保存当前进度。</small>}
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
              return (
                <article key={saveName}>
                  <span>{value(item, 'player_name', '无名修士').slice(0, 1)}</span>
                  <div>
                    <strong>{saveName}</strong>
                    <p>{item.corrupt ? '存档损坏，无法读取；原文件仍保留在本地' : `${value(item, 'player_name', '无名修士')} · ${value(item, 'realm', '凡人')}`}</p>
                    {!item.corrupt && <small><CalendarDays size={11} />天玄历 {value(item, 'calendar_year', '387')} 年 {value(item, 'month', '1')} 月 · 第 {value(item, 'turn', '0')} 回合</small>}
                  </div>
                  <div className="save-entry-actions">
                    {Boolean(item.has_backup) && <button type="button" title="将上一个版本另存为新卷宗" disabled={busy || Boolean(transferring)} onClick={() => onAction(`恢复备份 ${saveName}`)}><RotateCcw size={14} />恢复备份</button>}
                    <button type="button" title="导出为带校验值的便携卷宗" disabled={busy || Boolean(transferring) || Boolean(item.corrupt)} onClick={() => void download(saveName)}><FileDown size={14} />{exporting ? '导出中…' : '导出'}</button>
                    <button type="button" data-confirm={selected || undefined} disabled={busy || Boolean(transferring) || Boolean(item.corrupt)} onClick={() => load(saveName)}><FolderOpen size={14} />{selected ? '再次点击确认' : '读取'}</button>
                    <button type="button" className="save-delete-button" aria-label={`删除 ${saveName}`} title="确认后移入本地回收目录，不重置角色" disabled={busy || Boolean(transferring)} onClick={() => void remove(saveName)}><Trash2 size={14} />{transferring === `delete:${saveName}` ? '删除中…' : '删除'}</button>
                  </div>
                </article>
              )
            })}</div> : <div className="empty-save"><ScrollText size={25} /><p>还没有已保存的卷宗。</p></div>}
          </section>
          <section className="save-restart-area">
            <div className="save-restart-row">
              <div className="restart-info-col">
                <span className="restart-icon-wrap"><RotateCcw size={18} /></span>
                <div className="restart-text-col">
                  <h3>再入轮回 · 重开新局</h3>
                  <p>舍去此世肉身命盘，重新经历凡尘定格与灵根道骨测定。</p>
                </div>
              </div>
              <button
                type="button"
                className="restart-game-btn"
                disabled={busy}
                onClick={() => {
                  if (window.confirm('确定要放弃当前进度，重开新局并重新创角吗？建议先在上方保存当前进度。')) {
                    onAction('重开新局')
                    onOpenChange?.(false)
                  }
                }}
              >
                <RotateCcw size={14} />
                <span>重开新局</span>
              </button>
            </div>
          </section>
          <div className="dialog-bottom-spacer" aria-hidden="true" />
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
