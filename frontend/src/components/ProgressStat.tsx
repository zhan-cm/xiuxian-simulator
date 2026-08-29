import { GameTooltip } from './GameTooltip'

interface ProgressStatProps {
  label: string
  value: number
  max: number
  tone: 'health' | 'spirit' | 'cultivation'
  help: string
}

export function ProgressStat({ label, value, max, tone, help }: ProgressStatProps) {
  const progress = max > 0 ? Math.max(0, Math.min(100, Math.round(value * 100 / max))) : 0
  return (
    <GameTooltip label={help}>
      <div className="progress-stat" tabIndex={0}>
        <div><span>{label}</span><strong>{value} / {max}</strong></div>
        <div className={`progress-track ${tone}`}>
          <i style={{ width: `${progress}%` }} />
          {progress === 0 && <b aria-hidden="true" />}
        </div>
      </div>
    </GameTooltip>
  )
}
