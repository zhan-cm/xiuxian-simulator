import * as Dialog from '@radix-ui/react-dialog'
import { BookOpen, ChevronRight, CircleDotDashed, History, Sparkles, X } from 'lucide-react'
import type { DaoSnapshot } from '../api/types'

interface Props { dao: DaoSnapshot; busy: boolean; readOnly?: boolean; onAction: (action: string) => void }

export function DaoTree({ dao, busy, readOnly = false, onAction }: Props) {
  const insightPercent = Math.min(100, Math.round(dao.insight / dao.insight_required * 100))
  return <Dialog.Root>
    <Dialog.Trigger asChild><button className="dao-ribbon" type="button" data-ready={dao.points > 0 || undefined}><span><CircleDotDashed size={17} /></span><div><small>悟道九途</small><strong>{dao.total_levels ? `已点亮 ${dao.total_levels} 层` : '大道初闻'}</strong></div><i><b style={{ width: `${insightPercent}%` }} /></i><p>感悟 {dao.insight}/{dao.insight_required}</p><em>{dao.points} 点可用</em><ChevronRight size={16} /></button></Dialog.Trigger>
    <Dialog.Portal><Dialog.Overlay className="dialog-overlay" /><Dialog.Content className="character-dialog dao-dialog">
      <header><div><p>观万象 · 证己道</p><Dialog.Title>悟道九途</Dialog.Title><Dialog.Description>论道、观想与实战积累感悟；闭关凝成悟道点后，由你亲自决定永久道途。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
      <section className="dao-overview"><span><Sparkles size={17} /></span><div><small>未化感悟</small><strong>{dao.insight}<b> / {dao.insight_required}</b></strong><i><b style={{ width: `${insightPercent}%` }} /></i></div><div><small>悟道点</small><strong>{dao.points}</strong></div><div className="dao-actions"><button type="button" disabled={busy || readOnly || !dao.can_contemplate} title={dao.contemplate_reason || '消耗 10 灵力并推进一个月'} onClick={() => onAction(dao.contemplate_action)}>静坐观想</button><button type="button" disabled={busy || readOnly || !dao.can_digest} title={dao.digest_reason || '闭关一月，最多凝成三点'} onClick={() => onAction(dao.digest_action)}>消化感悟</button></div></section>
      <section className="dao-scroll"><div className="dao-branch-grid">{dao.branches.map((branch) => <article key={branch.id} data-active={branch.level > 0 || undefined} data-complete={branch.level >= branch.max_level || undefined}><header><span>{branch.mark}</span><div><small>{branch.subtitle}</small><h3>{branch.name}</h3></div><em>{branch.level} / {branch.max_level}</em></header><div className="dao-pips">{Array.from({ length: branch.max_level }, (_, index) => <i key={index} data-lit={index < branch.level || undefined} />)}</div><p>{branch.summary}</p><dl><div><dt>当前</dt><dd>{branch.effect}</dd></div><div><dt>下一层</dt><dd>{branch.next_effect}</dd></div></dl><button type="button" disabled={busy || readOnly || !branch.eligible} title={branch.disabled_reason || branch.next_effect} onClick={() => onAction(branch.action)}><BookOpen size={13} />{branch.level >= branch.max_level ? '此道圆满' : `点亮第 ${branch.level + 1} 层`}</button>{!branch.eligible && branch.level < branch.max_level && <small>{branch.disabled_reason}</small>}</article>)}</div>
        <section className="dao-history"><h3><History size={14} />悟道留痕</h3>{dao.history.length ? <ol>{[...dao.history].reverse().map((entry, index) => <li key={`${entry}-${index}`}><span>{dao.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>第一缕感悟尚未落入道心。</p>}</section>
      </section>
    </Dialog.Content></Dialog.Portal>
  </Dialog.Root>
}
