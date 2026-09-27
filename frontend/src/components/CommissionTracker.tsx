import { ArrowRight, CheckCircle2, Clock3, MapPin, ScrollText } from 'lucide-react'
import type { CommissionSnapshot } from '../api/types'

interface CommissionTrackerProps {
  commissions: CommissionSnapshot
  busy: boolean
  canAct: boolean
  readOnly?: boolean
  onAction: (action: string) => void
  onOpenBoard: () => void
}

export function CommissionTracker({ commissions, busy, canAct, readOnly = false, onAction, onOpenBoard }: CommissionTrackerProps) {
  if (!commissions.active.length) return null

  return (
    <section className="commission-tracker" aria-label="正在进行的委托">
      <header>
        <div><ScrollText size={18} /><h3>正在进行的委托</h3><span>{commissions.active_count}/{commissions.active_limit}</span></div>
        <button type="button" onClick={onOpenBoard}>查看悬榜</button>
      </header>
      <div className="commission-tracker-list">
        {commissions.active.map((item) => (
          <article key={item.id} data-ready={item.ready || undefined}>
            <div className="commission-tracker-heading">
              <strong>{item.title}</strong>
              <span>{item.ready ? <><CheckCircle2 size={14} />可交付</> : <><Clock3 size={14} />余 {item.turns_left} 月</>}</span>
            </div>
            <p className="commission-tracker-location"><MapPin size={14} />{item.location}</p>
            <p className="commission-tracker-instruction">{item.how_to}</p>
            <div className="commission-tracker-bottom">
              <div className="commission-tracker-progress">
                <span>进度 {item.current}/{item.required}</span>
                <progress value={item.current} max={item.required} aria-label={`${item.title}进度`} />
              </div>
              <button type="button" disabled={busy || readOnly || !canAct || item.expired} onClick={() => onAction(item.next_action)}>
                {item.next_label}<ArrowRight size={15} />
              </button>
            </div>
            <small>{item.action_hint}</small>
          </article>
        ))}
      </div>
    </section>
  )
}
