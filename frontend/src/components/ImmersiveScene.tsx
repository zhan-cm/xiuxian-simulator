import * as Dialog from '@radix-ui/react-dialog'
import { CalendarDays, CloudSun, Compass, Home, Landmark, Map, Menu, Mountain, ScrollText, Sparkles, UsersRound, X } from 'lucide-react'
import type { RefObject } from 'react'
import type { GameState, PlayerState, Presentation } from '../api/types'

const sceneFrom = (state: GameState, presentation: Presentation) => {
  const action = presentation.action || ''
  if (state.phase.startsWith('combat') || presentation.tone === 'combat') return 'battle'
  if (/坊市|拍卖|交易|买入|卖出/.test(action)) return 'market'
  if (/洞府|修炼|闭关|调息/.test(action)) return 'cave'
  if (/宗|门派|藏经/.test(action)) return 'sect'
  if (/地图|探索|秘境|行旅/.test(action)) return 'wilds'
  const location = state.player.location
  if (/坊市/.test(location)) return 'market'
  if (/宗|门派|藏经/.test(location)) return 'sect'
  if (/山|洲|域/.test(location)) return 'wilds'
  return 'cave'
}

interface ImmersiveSceneProps {
  state: GameState
  presentation: Presentation
  calendarLabel: string
}

export function ImmersiveScene({ state, presentation, calendarLabel }: ImmersiveSceneProps) {
  const { player } = state
  const scene = sceneFrom(state, presentation)
  const summary = presentation.paragraphs?.[0] || state.last_world_event || '天地无言，灵机正在暗处流转。'
  const summaryCharacters = Array.from(summary)
  const shortened = summaryCharacters.length > 120
  const preview = shortened ? `${summaryCharacters.slice(0, 120).join('')}…` : summary
  return (
    <section className="immersive-scene" data-scene={scene} aria-label={`当前场景：${player.location}`}>
      <div className="scene-sky" aria-hidden="true" />
      <div className="scene-sun" aria-hidden="true" />
      <div className="scene-mountain scene-mountain-far" aria-hidden="true" />
      <div className="scene-mountain scene-mountain-near" aria-hidden="true" />
      <div className="scene-mist scene-mist-one" aria-hidden="true" />
      <div className="scene-mist scene-mist-two" aria-hidden="true" />

      <header className="scene-location">
        <span><Compass size={14} />当前所在</span>
        <strong>{player.location}</strong>
        <small><CloudSun size={13} />{state.world_era}</small>
      </header>

      <div className="scene-character" aria-label={`${player.name}，${player.realm}`}>
        <div className="scene-aura" aria-hidden="true" />
        <span className="scene-portrait">{player.name.slice(0, 1)}</span>
        <div><small>{player.sect || '散修'} · {player.condition}</small><strong>{player.name}</strong><em>{player.realm}</em></div>
      </div>

      <article className="scene-narrative">
        <span><CalendarDays size={13} />第 {state.turn} 回合 · {calendarLabel}</span>
        <h2>{presentation.title || '灵气潮汐将至'}</h2>
        <p>{preview}</p>
        {shortened && <Dialog.Root key={summary}>
          <Dialog.Trigger asChild><button type="button" className="scene-read-more"><ScrollText size={14} />读完这段</button></Dialog.Trigger>
          <Dialog.Portal><Dialog.Overlay className="dialog-overlay" /><Dialog.Content className="character-dialog narrative-dialog">
            <header><div><Dialog.Title>{presentation.title || '此刻道途'}</Dialog.Title><Dialog.Description>第 {state.turn} 回合 · {calendarLabel}</Dialog.Description></div><Dialog.Close aria-label="关闭完整叙事"><X size={20} /></Dialog.Close></header>
            <div className="narrative-dialog-copy"><p>{summary}</p></div>
          </Dialog.Content></Dialog.Portal>
        </Dialog.Root>}
        {presentation.changes?.length > 0 && <div>{presentation.changes.slice(0, 3).map((change, index) => <small key={`${change.label}-${index}`}><b>{change.label}</b>{change.value}</small>)}</div>}
      </article>
    </section>
  )
}

interface CultivatorHudProps {
  player: PlayerState
}

export function CultivatorHud({ player }: CultivatorHudProps) {
  const stats = [
    { label: '气血', value: player.health, max: player.health_max, tone: 'health' },
    { label: '灵力', value: player.spirit, max: player.spirit_max, tone: 'spirit' },
    { label: '修为', value: player.cultivation, max: player.cultivation_required, tone: 'cultivation' },
  ]
  return (
    <section className="cultivator-hud" aria-label="修士核心状态">
      <span>{player.name.slice(0, 1)}</span>
      <div className="cultivator-hud-name"><small>{player.dao_name || '道号未定'}</small><strong>{player.name}</strong><em>{player.realm}</em></div>
      <div className="cultivator-hud-stats">
        {stats.map((stat) => {
          const percent = stat.max > 0 ? Math.max(0, Math.min(100, stat.value * 100 / stat.max)) : 0
          return <div key={stat.label} data-tone={stat.tone} title={`${stat.label} ${stat.value} / ${stat.max}`}><small>{stat.label}<b>{stat.value}/{stat.max}</b></small><i><b style={{ width: `${percent}%` }} /></i></div>
        })}
      </div>
    </section>
  )
}

const destinations = [
  { label: '洞府', action: '洞府', icon: Home },
  { label: '九州', action: '地图', icon: Map },
  { label: '坊市', action: '坊市', icon: Landmark },
  { label: '人物', action: '情缘', icon: UsersRound },
  { label: '宗门', action: '宗门', icon: Mountain },
  { label: '修行', action: '功法', icon: Sparkles },
]

interface WorldNavigationProps {
  activeAction: string
  disabled?: boolean
  disabledReason?: string
  codexOpen: boolean
  codexButtonRef?: RefObject<HTMLButtonElement | null>
  hasUpdates?: boolean
  onNavigate: (action: string) => void
  onToggleCodex: () => void
}

export function WorldNavigation({ activeAction, disabled = false, disabledReason, codexOpen, codexButtonRef, hasUpdates, onNavigate, onToggleCodex }: WorldNavigationProps) {
  return (
    <nav className="world-navigation" aria-label="修仙世界导航">
      <span className="world-navigation-mark">问道</span>
      {destinations.map(({ label, action, icon: Icon }) => <button type="button" key={action} disabled={disabled} title={disabled ? disabledReason : `查看${label}`} aria-current={activeAction === action ? 'page' : undefined} data-active={activeAction === action || undefined} onClick={() => onNavigate(action)}><Icon size={18} /><span>{label}</span></button>)}
      <button type="button" ref={codexButtonRef} aria-haspopup="dialog" aria-expanded={codexOpen} data-active={codexOpen || undefined} onClick={onToggleCodex}><Menu size={18} /><span>{codexOpen ? '收起侧记' : '洞天侧记'}</span>{hasUpdates && <i className="nav-update-dot" aria-label="修行百艺有可推进事项" />}</button>
    </nav>
  )
}
