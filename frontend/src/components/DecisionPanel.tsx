import { motion } from 'motion/react'
import { CircleHelp, LoaderCircle, LockKeyhole, Sparkles } from 'lucide-react'
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
  const choiceMarks = ['壹', '贰', '叁', '肆', '伍', '陆']
  return (
    <section className="decision-panel" data-exclusive={decision.exclusive || undefined} aria-labelledby="decision-title">
      <div className="decision-heading">
        <span><Sparkles size={15} />{decision.eyebrow || '此刻抉择'}</span>
        <h3 id="decision-title">{decision.title}</h3>
        <p>{decision.hint}</p>
      </div>
      <div className="decision-grid">
        {decision.choices.map((choice, index) => {
          const disabled = busy || readOnly || Boolean(choice.disabled)
          const selected = busy && activeAction === choice.action
          const button = (
            <motion.button
              key={choice.action}
              type="button"
              className="decision-choice"
              data-tone={choice.tone || 'primary'}
              data-selected={selected || undefined}
              aria-pressed={selected}
              aria-busy={selected}
              disabled={disabled}
              whileHover={disabled ? undefined : { y: -2 }}
              whileTap={disabled ? undefined : { y: 1, scale: 0.99 }}
              onClick={() => onChoose(choice.action)}
            >
              <span className="choice-seal">{selected ? <LoaderCircle className="animate-spin" size={17} /> : disabled ? <LockKeyhole size={17} /> : choiceMarks[index] || index + 1}</span>
              <span className="choice-copy">
                <strong>{choice.label}{choice.tooltip && <GameTooltip label={choice.tooltip}><span className="choice-help" tabIndex={0} aria-label={`${choice.label}说明`}><CircleHelp size={13} /></span></GameTooltip>}</strong>
                {choice.summary && <small>{choice.summary}</small>}
                <p>{readOnly ? '成果巡览仅供检验，不会修改当前存档' : choice.disabled ? choice.disabled_reason : choice.description}</p>
              </span>
              <i>{selected ? '推演中' : disabled ? '不可选' : '定此念'}</i>
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
