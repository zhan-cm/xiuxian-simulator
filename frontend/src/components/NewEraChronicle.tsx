import * as Dialog from '@radix-ui/react-dialog'
import { ChevronRight, CircleDotDashed, History, Landmark, MapPin, Waves, X } from 'lucide-react'
import type { NewEraSnapshot } from '../api/types'

interface Props { era: NewEraSnapshot; busy: boolean; readOnly?: boolean; onAction: (action: string) => void }

export function NewEraChronicle({ era, busy, readOnly = false, onAction }: Props) {
  if (!era.active) return null
  const status = era.pending
    ? `《${era.event.title}》等待抉择`
    : era.available
      ? `《${era.event.title}》已经显现`
      : `${era.next_in} 个月后再起余波`
  return <Dialog.Root>
    <Dialog.Trigger asChild><button className="new-era-ribbon" type="button" data-ready={era.available || Boolean(era.pending) || undefined}><span><Waves size={17} /></span><div><small>新世演化</small><strong>{era.stage}</strong></div><p>{status}</p><em>第 {era.completed} 轮</em><ChevronRight size={16} /></button></Dialog.Trigger>
    <Dialog.Portal><Dialog.Overlay className="dialog-overlay" /><Dialog.Content className="character-dialog new-era-dialog">
      <header><div><p>终局之后 · 山河仍行</p><Dialog.Title>新世卷宗</Dialog.Title><Dialog.Description>每次余波都由终局路线生成，并永久改变山河、天机与九州盟约。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
      <section className="new-era-overview"><Waves size={17} /><div><small>{era.title}</small><strong>{era.stage}</strong></div><span><small>已处置</small><b>{era.completed} 轮</b></span><em>{era.pending ? '因果待决' : era.available ? '新局已至' : `余 ${era.next_in} 月`}</em></section>
      <section className="new-era-scores"><header><span>新世三衡</span><small>任何一项长期失衡，都会改变后来事件的代价</small></header><div>{era.scores.map((score) => <article key={score.id} data-dominant={score.dominant || undefined} title={score.help} tabIndex={0}><span>{score.mark}</span><div><strong>{score.label}</strong><i><b style={{ width: `${Math.max(0, Math.min(100, score.value))}%` }} /></i></div><em>{score.value}</em></article>)}</div></section>
      {era.event.id && <article className="new-era-event" data-ready={era.available || Boolean(era.pending) || undefined}><header><span><CircleDotDashed size={16} /></span><div><small>{era.pending ? '正在处置' : era.available ? '当世余波' : '下一轮预兆'}</small><h3>{era.event.title}</h3></div><em><MapPin size={11} />{era.event.location}</em></header><p>{era.event.summary}</p>{era.available && <button type="button" disabled={busy || readOnly} onClick={() => onAction(era.begin_action)}><Landmark size={14} />处置此轮余波</button>}{era.pending && <small>请在主界面的三项新世抉择中亲自决定。</small>}</article>}
      <section className="new-era-history"><h3><History size={14} />近世留痕</h3>{era.history.length ? <ol>{[...era.history].reverse().map((entry, index) => <li key={`${entry}-${index}`}><span>{era.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>终局余韵尚未化作新的历史。</p>}</section>
    </Dialog.Content></Dialog.Portal>
  </Dialog.Root>
}
