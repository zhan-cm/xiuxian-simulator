import { motion } from 'motion/react'
import { Check, LockKeyhole, Sparkles } from 'lucide-react'
import type { Decision } from '../api/types'
import { GameTooltip } from './GameTooltip'

interface DecisionPanelProps {
  decision: Decision
  activeAction: string
  busy: boolean
  readOnly?: boolean
  onChoose: (action: string) => void
}

export function DecisionPanel({ decision, activeAction, busy, readOnly = false, onChoose }: DecisionPanelProps) {
  if (!decision?.choices?.length) return null
  return (
    <section className="decision-panel" aria-labelledby="decision-title">
      <div className="decision-heading">
        <span><Sparkles size={15} />{decision.eyebrow || '此刻抉择'}</span>
        <h3 id="decision-title">{decision.title}</h3>
        <p>{decision.hint}</p>
      </div>
      <div className="decision-grid">
        {decision.choices.map((choice) => {
          const disabled = busy || readOnly || Boolean(choice.disabled)
          const selected = busy && activeAction === choice.action
          const button = (
            <motion.button
              key={choice.action}
              type="button"
              className="decision-choice"
              data-tone={choice.tone || 'primary'}
              data-selected={selected || undefined}
              disabled={disabled}
              whileHover={disabled ? undefined : { y: -2 }}
              whileTap={disabled ? undefined : { y: 1, scale: 0.99 }}
              onClick={() => onChoose(choice.action)}
            >
              <span className="choice-seal">{disabled ? <LockKeyhole size={17} /> : <Check size={17} />}</span>
              <span className="choice-copy">
                <strong>{choice.label}</strong>
                {choice.summary && <small>{choice.summary}</small>}
                <p>{readOnly ? '成果巡览仅供检验，不会修改当前存档' : choice.disabled ? choice.disabled_reason : choice.description}</p>
              </span>
              <i>{selected ? '推演中' : '选择'}</i>
            </motion.button>
          )
          const disabledReason = readOnly ? '成果巡览模式仅供检验界面' : choice.disabled_reason
          return disabled && disabledReason
            ? <GameTooltip key={choice.action} label={disabledReason}>{button}</GameTooltip>
            : button
        })}
      </div>
    </section>
  )
}
