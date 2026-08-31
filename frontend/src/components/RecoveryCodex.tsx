import * as Dialog from '@radix-ui/react-dialog'
import { BedDouble, HeartPulse, History, Pill, ShieldAlert, TimerReset, X, Zap } from 'lucide-react'
import type { RecoverySnapshot } from '../api/types'

interface Props {
  recovery: RecoverySnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

function percentage(value: number, maximum: number) {
  return Math.max(0, Math.min(100, Math.round(value / Math.max(1, maximum) * 100)))
}

function modifier(value: number, inverse = false) {
  const delta = Math.round((value - 1) * 100)
  if (!delta) return '无影响'
  const signed = `${delta > 0 ? '+' : ''}${delta}%`
  return inverse ? signed : `${delta}%`
}

export function RecoveryCodex({ recovery, busy, readOnly = false, onAction }: Props) {
  if (!recovery.active) return null
  const lead = recovery.injuries[0]
  const longest = Math.max(...recovery.injuries.map((injury) => injury.months_left))
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button className="recovery-trigger" type="button" data-severity={lead?.severity || 1}>
          <span><ShieldAlert size={15} /></span>
          <div><small>伤势在身 · 点击查看疗愈方案</small><strong>{recovery.condition}</strong></div>
          <em>最长 {longest} 月</em>
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog recovery-dialog">
          <header><div><p>伤可养 · 道不可躁进</p><Dialog.Title>伤势与疗愈卷宗</Dialog.Title><Dialog.Description>伤势会真实影响吐纳、斗法、受伤与遁速；岁月、丹药和洞府静室均可缩短调养期。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>

          <section className="recovery-overview">
            <span><HeartPulse size={23} /></span>
            <div><small>当前状态</small><strong>{recovery.condition}</strong><p>{recovery.count} 处持续伤势 · 伤愈前不可强行破境</p></div>
            <dl>
              <div><dt>吐纳</dt><dd>{modifier(recovery.penalties.cultivation)}</dd></div>
              <div><dt>攻势</dt><dd>{modifier(recovery.penalties.combat)}</dd></div>
              <div><dt>承伤</dt><dd>{modifier(recovery.penalties.damage_taken, true)}</dd></div>
              <div><dt>遁速</dt><dd>{recovery.penalties.speed ? `-${recovery.penalties.speed}` : '无影响'}</dd></div>
            </dl>
          </section>

          <div className="recovery-vitals">
            <div><span><HeartPulse size={13} />气血 <b>{recovery.health}/{recovery.health_max}</b></span><i><b style={{ width: `${percentage(recovery.health, recovery.health_max)}%` }} /></i></div>
            <div><span><Zap size={13} />灵力 <b>{recovery.spirit}/{recovery.spirit_max}</b></span><i><b style={{ width: `${percentage(recovery.spirit, recovery.spirit_max)}%` }} /></i></div>
          </div>

          <section className="recovery-scroll">
            <div className="recovery-grid">
              {recovery.injuries.map((injury) => (
                <article className="recovery-card" key={injury.id} data-severity={injury.severity}>
                  <header><span>{injury.mark}</span><div><small>{injury.severity_label}伤势</small><h3>{injury.name}</h3></div><em><TimerReset size={11} />尚需 {injury.months_left} 月</em></header>
                  <p>{injury.description}</p>
                  <div className="recovery-effects">{injury.effects.map((effect) => <span key={effect}>{effect}</span>)}</div>
                  <footer><small>伤势缘起</small><strong>{injury.source}</strong></footer>
                </article>
              ))}
            </div>

            <div className="recovery-actions">
              <button type="button" disabled={busy || readOnly || !recovery.can_rest} title={readOnly ? '巡览模式不会修改存档' : recovery.rest_reason || '推进一个月，恢复气血与灵力并缩短伤势调养期'} onClick={() => onAction(recovery.rest_action)}><BedDouble size={15} /><span><strong>闭门静养</strong><small>推进一月 · 稳妥恢复</small></span></button>
              <button type="button" disabled={busy || readOnly || !recovery.has_healing_pill} title={readOnly ? '巡览模式不会修改存档' : recovery.has_healing_pill ? '服药恢复气血，并缩短最严重伤势 3 个月' : '乾坤袋中没有疗伤丹'} onClick={() => onAction(recovery.pill_action)}><Pill size={15} /><span><strong>服用疗伤丹</strong><small>{recovery.has_healing_pill ? '快速处理最重伤势' : '乾坤袋中暂无丹药'}</small></span></button>
            </div>

            <section className="recovery-history"><h3><History size={14} />伤势留痕</h3>{recovery.history.length ? <ol>{recovery.history.map((entry, index) => <li key={`${entry}-${index}`}><span>{recovery.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>尚无疗愈记录。</p>}</section>
          </section>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
