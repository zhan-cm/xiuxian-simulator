import * as Dialog from '@radix-ui/react-dialog'
import { Ban, Check, ClipboardList, Clock3, Coins, Gift, LockKeyhole, ScrollText, ShieldCheck, X } from 'lucide-react'
import type { CommissionSnapshot } from '../api/types'

interface CommissionBoardProps {
  commissions: CommissionSnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

export function CommissionBoard({ commissions, busy, readOnly = false, onAction }: CommissionBoardProps) {
  const ready = commissions.active.filter((item) => item.ready).length
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button className="commission-ribbon" type="button" data-ready={ready > 0 || undefined}>
          <span><ClipboardList size={17} /></span>
          <div><small>东洲悬榜</small><strong>{commissions.active_count ? `${commissions.active_count} 份委托在途` : '寻一桩合意差事'}</strong></div>
          <p>{ready ? `${ready} 份报酬待领取` : commissions.rotation_label}</p>
          <em>{commissions.active_count}/{commissions.active_limit}</em>
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog commission-dialog">
          <header>
            <div><p>四方来帖 · 因果有偿</p><Dialog.Title>东洲悬榜</Dialog.Title><Dialog.Description>接取委托后亲自完成对应历练，逾期会自动撤榜；同时最多追踪两份。</Dialog.Description></div>
            <Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close>
          </header>
          <div className="commission-summary">
            <span><ShieldCheck size={16} />委托信誉<strong>{commissions.renown}</strong></span>
            <span><Check size={16} />累计完成<strong>{commissions.completed_count}</strong></span>
            <span><Clock3 size={16} />{commissions.rotation_label}</span>
            <small>{readOnly ? '成果巡览中不会修改存档' : '报酬由规则引擎真实结算'}</small>
          </div>

          <div className="commission-scroll">
          <section className="commission-section">
            <div className="commission-section-title"><div><ScrollText size={17} /><span><small>正在追踪</small><strong>在途委托</strong></span></div><em>{commissions.active_count}/{commissions.active_limit}</em></div>
            {commissions.active.length ? <div className="active-commission-list">{commissions.active.map((item) => (
              <article key={item.id} data-ready={item.ready || undefined} data-expired={item.expired || undefined}>
                <header><div><small>{item.issuer}</small><h3>{item.title}</h3></div><span><Clock3 size={13} />{item.expired ? '已经逾期' : `余 ${item.turns_left} 月`}</span></header>
                <p>{item.summary}</p>
                <div className="commission-progress"><i><b style={{ width: `${item.progress}%` }} /></i><strong>{item.current}/{item.required}</strong></div>
                <footer><small><Gift size={13} />{item.reward}</small><div><button className="quiet" type="button" disabled={busy || readOnly} onClick={() => onAction(item.abandon_action)}><Ban size={13} />放弃</button><button type="button" disabled={!item.ready || busy || readOnly} title={!item.ready ? '完成要求后才可交付' : `领取 ${item.reward}`} onClick={() => onAction(item.deliver_action)}>{item.ready ? <Gift size={14} /> : <LockKeyhole size={14} />}{item.ready ? '交付领取' : '尚未完成'}</button></div></footer>
              </article>
            ))}</div> : <div className="commission-empty"><ClipboardList size={25} /><div><strong>尚无在途委托</strong><p>从下方悬榜挑选差事，探索、斗法与百艺都会记录真实进度。</p></div></div>}
          </section>

          <section className="commission-section board-section">
            <div className="commission-section-title"><div><Coins size={17} /><span><small>本期四帖</small><strong>可接悬榜</strong></span></div><em>{commissions.rotation_label}</em></div>
            <div className="commission-offer-grid">{commissions.offers.map((item) => (
              <article key={item.id} data-disabled={!item.eligible || undefined} data-complete={item.completed || undefined}>
                <header><span>{item.kind_label}</span><small>{item.issuer}</small></header>
                <h3>{item.title}</h3><p>{item.summary}</p>
                <dl><div><dt>要求</dt><dd>{item.requirement}</dd></div><div><dt>限期</dt><dd>{item.duration} 个月</dd></div><div><dt>报酬</dt><dd>{item.reward}</dd></div></dl>
                <button type="button" disabled={!item.eligible || busy || readOnly} title={readOnly ? '巡览模式仅供查看' : item.disabled_reason || `接取《${item.title}》`} onClick={() => onAction(item.accept_action)}>{item.completed ? <Check size={14} /> : item.eligible ? <ScrollText size={14} /> : <LockKeyhole size={14} />}{item.completed ? '本期已完成' : item.accepted ? '已经接取' : item.eligible ? '接取委托' : item.disabled_reason}</button>
              </article>
            ))}</div>
          </section>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
