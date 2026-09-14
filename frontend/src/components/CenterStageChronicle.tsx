import { CloudSun, Flame, MapPin, ScrollText, Sparkles, TrendingUp } from 'lucide-react'
import type { Snapshot } from '../api/types'
import { CultivationGuideCard } from './CultivationGuide'

const REALM_NAMES = ['炼气', '筑基', '结晶', '金丹', '具灵', '元婴', '化神', '悟道', '羽化', '登仙']
const STAGE_NAMES = ['初期', '中期', '后期', '圆满']

interface CenterStageChronicleProps {
  snapshot: Snapshot
  busy: boolean
  readOnly: boolean
  onAction: (action: string) => void
  onOpenBreakthrough: () => void
  onOpenGuide: () => void
}

export function CenterStageChronicle({
  snapshot,
  busy,
  readOnly,
  onAction,
  onOpenBreakthrough,
  onOpenGuide,
}: CenterStageChronicleProps) {
  const { state } = snapshot
  const { player } = state

  const [baseRealm = '炼气', stageName = '初期'] = (player.realm || '').split('·')
  const realmIndex = Math.max(0, REALM_NAMES.indexOf(baseRealm))
  const stageIndex = Math.max(0, STAGE_NAMES.indexOf(stageName))
  const isPinnacle = stageIndex >= 3
  const isCultivationMax = player.cultivation >= player.cultivation_required

  const nextMilestone = isPinnacle
    ? `大境界天关 · ${REALM_NAMES[realmIndex + 1] || '真仙'}境`
    : `${REALM_NAMES[realmIndex]}·${STAGE_NAMES[stageIndex + 1] || '圆满'}`

  const percent = player.cultivation_required > 0
    ? Math.min(100, Math.max(0, (player.cultivation / player.cultivation_required) * 100))
    : 0

  const recentHistory = [...(state.history || [])].reverse().slice(0, 3)
  const localStanding = snapshot.regional?.standings?.find((item) => item.key === snapshot.regional?.current)
  const regionName = snapshot.travel?.current_name || localStanding?.key || player.location

  return (
    <div className="center-chronicle-container">
      {/* 1. 道途境界阶梯与瓶颈推演 (Dao Ladder) */}
      <section className="chronicle-card dao-ladder-card">
        <header className="dao-ladder-header">
          <div className="ladder-stage-current">
            <small>当前道境</small>
            <strong>{player.realm}</strong>
          </div>

          <div className="ladder-progress-info">
            <div className="ladder-labels">
              <span><TrendingUp size={13} />道行圆满度：{percent.toFixed(1)}%</span>
              <strong>{player.cultivation} / {player.cultivation_required}</strong>
            </div>
            <div className="ladder-bar">
              <div className="ladder-fill" style={{ width: `${percent}%` }} />
            </div>
          </div>

          <div className="ladder-stage-next">
            <small>前路所向</small>
            <strong>{nextMilestone}</strong>
          </div>
        </header>

        <div className="dao-ladder-footer">
          <span className="speed-tag">
            <Sparkles size={13} />
            {isCultivationMax
              ? '✨ 丹田灵力大圆满，随时可引动天地灵机破关！'
              : `吐纳炼气以充盈丹田，尚需 ${player.cultivation_required - player.cultivation} 点修为即可叩关。`}
          </span>
          <div className="breakthrough-ready-cta">
            <button
              type="button"
              disabled={busy || readOnly}
              onClick={onOpenBreakthrough}
            >
              <Flame size={13} />
              <span>{isCultivationMax ? '叩问境界突破' : '查看天关破境要求'}</span>
            </button>
          </div>
        </div>
      </section>

      {/* 2. 仙途指津 · 行止向导 (如果想要……你可以去哪里干什么) */}
      <CultivationGuideCard
        snapshot={snapshot}
        onNavigate={onAction}
        onOpenFullGuide={onOpenGuide}
      />

      {/* 3. 九州风云与天地大势 (World Panorama) */}
      <section className="chronicle-card world-panorama-card">
        <div className="panorama-header">
          <h3>
            <CloudSun size={16} />
            <span>九州世象全景</span>
          </h3>
          <span>天玄历 {state.calendar_year} 年</span>
        </div>

        <div className="panorama-grid">
          <div className="panorama-item">
            <small><CloudSun size={13} />当今天地气象</small>
            <strong>{state.world_era || '灵气潮汐运转'}</strong>
            <p>{state.last_world_event || '山海静寂，天地灵机暗中流转。'}</p>
          </div>

          {localStanding && (
            <div className="panorama-item">
              <small><MapPin size={13} />所在地域与机缘</small>
              <strong>{regionName} · 声望 {localStanding.reputation}</strong>
              <p>
                {localStanding.encounter_completed
                  ? '此间机缘已被探明'
                  : localStanding.encounter_title || '山川灵秀，机缘未探'}
              </p>
              {!localStanding.encounter_completed && localStanding.encounter_title && (
                <button
                  type="button"
                  style={{
                    marginTop: 6,
                    padding: '3px 8px',
                    borderRadius: 6,
                    border: '1px solid rgba(186, 148, 75, 0.4)',
                    background: '#fff',
                    color: '#8c6020',
                    fontSize: 11,
                    cursor: 'pointer',
                    width: 'fit-content'
                  }}
                  disabled={busy || readOnly}
                  onClick={() => onAction('地方机缘')}
                >
                  探查机缘
                </button>
              )}
            </div>
          )}
        </div>
      </section>

      {/* 3. 仙途履迹 · 岁月留痕 (Recent Turn Footprints) */}
      {recentHistory.length > 0 && (
        <section className="chronicle-card footprints-card">
          <div className="footprints-header">
            <h3>
              <ScrollText size={15} />
              <span>仙途履迹 · 岁月留痕</span>
            </h3>
            <small>近几月修行记事</small>
          </div>
          <div className="footprints-list">
            {recentHistory.map((entry, index) => (
              <div key={`${entry}-${index}`} className="footprint-entry">
                <span className="footprint-badge">往事</span>
                <span>{entry}</span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

