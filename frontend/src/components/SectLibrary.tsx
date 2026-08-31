import * as Dialog from '@radix-ui/react-dialog'
import { Award, BookOpen, ChevronRight, History, Landmark, LockKeyhole, ScrollText, Sparkles, X } from 'lucide-react'
import type { SectLibrarySnapshot } from '../api/types'

interface Props {
  library: SectLibrarySnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

const ranks = ['外门弟子', '内门弟子', '真传弟子', '长老', '掌门']

export function SectLibrary({ library, busy, readOnly = false, onAction }: Props) {
  if (!library.member) return null
  const rankIndex = Math.max(0, ranks.indexOf(library.rank))
  const available = library.offerings.filter((item) => item.available).length
  return <Dialog.Root>
    <Dialog.Trigger asChild>
      <button className="library-ribbon" type="button" data-ready={available > 0 || undefined}>
        <span><BookOpen size={17} /></span>
        <div><small>{library.sect}</small><strong>宗门藏经阁</strong></div>
        <p>{available ? `${available} 项传承可领取` : `${library.rank}权限 · 静候积功`}</p>
        <em>{library.contribution} 贡献</em><ChevronRight size={16} />
      </button>
    </Dialog.Trigger>
    <Dialog.Portal>
      <Dialog.Overlay className="dialog-overlay" />
      <Dialog.Content className="character-dialog library-dialog">
        <header>
          <div><p>积功入阁 · 传法有序</p><Dialog.Title>{library.sect}藏经阁</Dialog.Title><Dialog.Description>宗门贡献不再只是晋升门槛：可兑换一次性传承，也可在每年接受一次长老讲法。</Dialog.Description></div>
          <Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close>
        </header>
        <section className="library-overview">
          <span><Landmark size={21} /></span>
          <div><small>当前身份</small><strong>{library.rank}</strong><p>{library.sect} · 已领取 {library.claimed_count} 项传承</p></div>
          <dl><div><dt>宗门贡献</dt><dd>{library.contribution}</dd></div><div><dt>可领取</dt><dd>{available}</dd></div></dl>
        </section>
        <div className="library-ranks" aria-label="藏经阁权限阶序">{ranks.map((rank, index) => <span key={rank} data-current={index === rankIndex || undefined} data-unlocked={index <= rankIndex || undefined}><i>{index <= rankIndex ? <Award size={12} /> : <LockKeyhole size={11} />}</i><small>{rank.replace('弟子', '')}</small></span>)}</div>
        <section className="library-scroll">
          <article className="guidance-card" data-ready={library.can_receive_guidance || undefined}>
            <span><Sparkles size={20} /></span><div><small>年度长老讲法</small><strong>宗门传功</strong><p>消耗 {library.guidance_cost} 贡献，推进一个月；身份越高，所得感悟与修为越多。</p></div>
            <button type="button" disabled={busy || readOnly || !library.can_receive_guidance} title={library.guidance_reason || '每个自然年限一次'} onClick={() => onAction(library.guidance_action)}>{library.can_receive_guidance ? '入殿听讲' : library.guidance_reason}</button>
          </article>
          <div className="library-grid">{library.offerings.map((offering) => <article key={offering.id} data-claimed={offering.claimed || undefined}>
            <header><span>{offering.mark}</span><div><small>{offering.category} · {offering.minimum_rank}</small><h3>{offering.name}</h3></div>{offering.claimed ? <em>已领取</em> : <em>{offering.cost} 贡献</em>}</header>
            <p>{offering.summary}</p>
            <div className="library-reward"><ScrollText size={13} /><span>{offering.rewards}</span></div>
            <button type="button" disabled={busy || readOnly || !offering.available} title={offering.disabled_reason || `消耗 ${offering.cost} 宗门贡献`} onClick={() => onAction(offering.action)}>{offering.claimed ? '本世已领' : offering.available ? '领取传承' : offering.disabled_reason}</button>
          </article>)}</div>
          <section className="library-history"><h3><History size={14} />阁中留录</h3>{library.history.length ? <ol>{library.history.map((entry, index) => <li key={`${entry}-${index}`}><span>{library.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>尚未在藏经阁留下领取或传功记录。</p>}</section>
        </section>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
}
