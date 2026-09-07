import { motion } from 'motion/react'
import { Clock3, Coins, Feather, LoaderCircle, LockKeyhole, MapPin, Route, ShieldCheck, Sparkles, Wind } from 'lucide-react'
import type { Decision, DecisionChoice, TravelSnapshot } from '../api/types'
import { GameTooltip } from './GameTooltip'

interface TravelDecisionPanelProps {
  decision: Decision
  travel: TravelSnapshot
  activeAction: string
  busy: boolean
  readOnly?: boolean
  onChoose: (action: string) => void
}

const pendingText = (travel: TravelSnapshot, key: string) => {
  const value = travel.pending?.[key]
  return typeof value === 'string' || typeof value === 'number' ? String(value) : ''
}

const methodFor = (choice: DecisionChoice) => choice.action.endsWith('caravan') ? 'caravan' : choice.action.endsWith('swift') ? 'swift' : 'cancel'
const monthsFor = (choice: DecisionChoice) => Number(choice.label.match(/(\d+)\s*月/)?.[1] || 0)
const costFor = (choice: DecisionChoice) => {
  const value = choice.summary?.match(/(\d+)\s*(灵石|灵力)/)
  return value ? { amount: value[1], unit: value[2] } : { amount: '—', unit: '无需消耗' }
}

export function TravelDecisionPanel({ decision, travel, activeAction, busy, readOnly = false, onChoose }: TravelDecisionPanelProps) {
  if (!decision?.choices?.length || !travel.pending || !Object.keys(travel.pending).length) return null
  const originKey = pendingText(travel, 'origin')
  const destinationKey = pendingText(travel, 'destination')
  const origin = travel.regions.find((region) => region.key === originKey)
  const destination = travel.regions.find((region) => region.key === destinationKey)
  const methods = decision.choices.filter((choice) => methodFor(choice) !== 'cancel')
  const cancel = decision.choices.find((choice) => methodFor(choice) === 'cancel')
  const distance = pendingText(travel, 'distance') || '远'

  return (
    <section className="travel-decision" aria-labelledby="travel-decision-title">
      <header className="travel-decision-heading">
        <span aria-hidden="true">行</span>
        <div><small><Route size={14} />跨域行旅 · 路书已成</small><h3 id="travel-decision-title">{origin?.name || originKey}至{destination?.name || destinationKey}</h3><p>{decision.hint}</p></div>
        <em><Sparkles size={13} />相隔 {distance} 程</em>
      </header>

      <div className="travel-route-stage" aria-label={`行程路线：${origin?.name || originKey}前往${destination?.name || destinationKey}`}>
        <div className="travel-terminal" data-position="origin"><span>{(origin?.name || originKey).slice(0, 1)}</span><div><small>此刻落脚</small><strong>{origin?.name || originKey}</strong><em>{origin?.rank || '声名未定'}</em></div></div>
        <div className="travel-route-line" aria-hidden="true"><i /><b><Feather size={16} /></b><i /></div>
        <div className="travel-terminal" data-position="destination"><span>{(destination?.name || destinationKey).slice(0, 1)}</span><div><small>此行所向</small><strong>{destination?.name || destinationKey}</strong><em>危险度 {destination?.danger ?? '—'} · {destination?.minimum_realm_label || '准入未明'}</em></div></div>
      </div>

      <div className="travel-method-grid">
        {methods.map((choice) => {
          const method = methodFor(choice)
          const selected = busy && activeAction === choice.action
          const disabled = busy || readOnly || Boolean(choice.disabled)
          const cost = costFor(choice)
          const Icon = method === 'caravan' ? ShieldCheck : Wind
          const button = (
            <motion.button
              type="button"
              className="travel-method"
              data-method={method}
              data-selected={selected || undefined}
              disabled={disabled}
              aria-pressed={selected}
              aria-busy={selected}
              whileHover={disabled ? undefined : { y: -2 }}
              whileTap={disabled ? undefined : { y: 1, scale: .99 }}
              onClick={() => onChoose(choice.action)}
            >
              <span className="travel-method-mark">{selected ? <LoaderCircle className="animate-spin" size={20} /> : choice.disabled ? <LockKeyhole size={20} /> : <Icon size={20} />}</span>
              <div className="travel-method-copy"><small>{method === 'caravan' ? '稳妥之选' : '独行之选'}</small><strong>{choice.label.replace(/\s*·.*$/, '')}</strong><p>{choice.description}</p></div>
              <dl><div><dt><Clock3 size={12} />耗时</dt><dd>{monthsFor(choice)} 个月</dd></div><div><dt>{cost.unit === '灵石' ? <Coins size={12} /> : <Sparkles size={12} />}消耗</dt><dd>{cost.amount} {cost.unit}</dd></div></dl>
              <i>{selected ? '正在启程' : choice.disabled ? '资粮不足' : readOnly ? '巡览只读' : '选择此路'}</i>
            </motion.button>
          )
          const reason = readOnly ? '成果巡览仅供检验，不会修改当前存档' : choice.disabled_reason
          return disabled && reason ? <GameTooltip key={choice.action} label={reason}>{button}</GameTooltip> : <span key={choice.action}>{button}</span>
        })}
      </div>
      <footer><p><MapPin size={13} />启程后会同步推进寿元、委托期限与九州局势。</p>{cancel && <button type="button" disabled={busy || readOnly} onClick={() => onChoose(cancel.action)}>{readOnly ? '巡览中不可更改行程' : '暂缓此行'}</button>}</footer>
    </section>
  )
}
