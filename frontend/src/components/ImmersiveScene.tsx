import * as Dialog from '@radix-ui/react-dialog'
import { CalendarDays, CloudSun, Compass, Gift, Home, Landmark, Map, Menu, MessageCircleMore, Mountain, ScrollText, Sparkles, Swords, UsersRound, X } from 'lucide-react'
import { useMemo, useState, type RefObject } from 'react'
import type { GameState, InventorySnapshot, NpcProfile, PlayerState, Presentation } from '../api/types'
import { findEncounterNpc } from '../sceneLogic'

const sceneFrom = (state: GameState, presentation: Presentation) => {
  const action = presentation.action || ''
  if (state.phase.startsWith('combat') || presentation.tone === 'combat') return 'battle'
  if (presentation.tone === 'relation') return 'relation'
  if (/坊市|拍卖|交易|买入|卖出/.test(action)) return 'market'
  if (/洞府|修炼|闭关|调息/.test(action)) return 'cave'
  if (/宗|门派|藏经/.test(action)) return 'sect'
  if (/行旅|前往\s/.test(action)) return 'travel'
  if (/地图|探索|秘境/.test(action)) return 'wilds'
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
  npcProfiles?: Record<string, NpcProfile>
}

const encounterMood = (npc: NpcProfile, action: string) => {
  if (!npc.alive) return { key: 'memory', label: '故人旧影' }
  if (/伤|危|虚弱/.test(npc.status)) return { key: 'wounded', label: '气息不稳' }
  if (action.startsWith('论道')) return { key: 'focused', label: '凝神论道' }
  if (action.startsWith('送礼')) return { key: 'warm', label: npc.affinity >= 40 ? '欣然相受' : '礼数相交' }
  if (npc.affinity >= 60) return { key: 'warm', label: '心意相知' }
  if (npc.affinity < 0) return { key: 'guarded', label: '心有戒备' }
  return { key: 'calm', label: '从容相叙' }
}

export function ImmersiveScene({ state, presentation, calendarLabel, npcProfiles }: ImmersiveSceneProps) {
  const { player } = state
  const scene = sceneFrom(state, presentation)
  const npc = findEncounterNpc(npcProfiles, presentation)
  const mood = npc ? encounterMood(npc, presentation.action) : undefined
  const summary = presentation.paragraphs?.[0] || state.last_world_event || '天地无言，灵机正在暗处流转。'
  const summaryCharacters = Array.from(summary)
  const shortened = summaryCharacters.length > 120
  const preview = shortened ? `${summaryCharacters.slice(0, 120).join('')}…` : summary
  return (
    <section className="immersive-scene" data-scene={scene} data-conversation={npc ? 'true' : undefined} aria-label={`当前场景：${player.location}`}>
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

      <div className="scene-character" data-side="player" aria-label={`${player.name}，${player.realm}`}>
        <div className="scene-aura" aria-hidden="true" />
        <span className="scene-portrait">{player.name.slice(0, 1)}</span>
        <div><small>{player.sect || '散修'} · {player.condition}</small><strong>{player.name}</strong><em>{player.realm}</em></div>
      </div>

      {npc && <div className="scene-npc" data-mood={mood?.key} aria-label={`正在与${npc.name}会面`}>
        <div className="scene-npc-copy"><small>{mood?.label} · {npc.status}</small><strong>{npc.name}</strong><em>{npc.identity}</em><div title={`好感 ${npc.affinity}，关系：${npc.relation}`}><span>{npc.relation || '缘分未定'}</span><i><b style={{ width: `${Math.max(3, Math.min(100, npc.affinity))}%` }} /></i><span>好感 {npc.affinity}</span></div></div>
        <span className="scene-npc-portrait">{npc.name.slice(0, 1)}</span>
      </div>}

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

interface SocialActionBarProps {
  npc?: NpcProfile
  inventory: InventorySnapshot
  disabled?: boolean
  onAction: (action: string) => void
}

export function SocialActionBar({ npc, inventory, disabled = false, onAction }: SocialActionBarProps) {
  const gifts = useMemo(() => inventory.items.filter((item) => item.category === '礼物' && item.count > 0), [inventory.items])
  const [selectedGift, setSelectedGift] = useState('')
  const gift = gifts.some((item) => item.name === selectedGift) ? selectedGift : gifts[0]?.name || ''
  if (!npc) return null
  const unavailable = disabled || !npc.alive
  const relationAction = npc.relation === '道侣'
    ? { label: '合修一月', action: `双修 ${npc.name}` }
    : npc.affinity >= 80
      ? { label: '结道侣契', action: `结为道侣 ${npc.name}` }
      : null
  return <section className="social-action-bar" aria-label={`与${npc.name}互动`}>
    <header><span>{npc.name.slice(0, 1)}</span><div><small>此刻相逢</small><strong>接下来想与{npc.name}做什么？</strong></div></header>
    <div className="social-primary-actions">
      <button type="button" disabled={unavailable} onClick={() => onAction(`对话 ${npc.name}`)}><MessageCircleMore size={16} /><span><strong>继续交谈</strong><small>推进一月 · 增进了解</small></span></button>
      <button type="button" disabled={unavailable} onClick={() => onAction(`论道 ${npc.name}`)}><Swords size={16} /><span><strong>论道印证</strong><small>真实判定 · 获得感悟</small></span></button>
      {relationAction && <button type="button" disabled={unavailable} onClick={() => onAction(relationAction.action)}><Sparkles size={16} /><span><strong>{relationAction.label}</strong><small>{npc.relation === '道侣' ? '共同修行 · 增长修为' : '需要好感达到 80'}</small></span></button>}
    </div>
    <div className="social-gift-action">
      <label htmlFor="encounter-gift"><Gift size={15} /><span><strong>赠一份心意</strong><small>{gifts.length ? `袋中有 ${gifts.length} 种礼物` : '乾坤袋中暂无礼物'}</small></span></label>
      <select id="encounter-gift" value={gift} disabled={unavailable || !gifts.length} onChange={(event) => setSelectedGift(event.target.value)}>{gifts.map((item) => <option key={item.name} value={item.name}>{item.name} ×{item.count}</option>)}</select>
      <button type="button" disabled={unavailable || !gift} title={gift ? `${npc.name}喜欢：${npc.likes.join('、') || '尚待了解'}` : '先从探索或坊市获得礼物'} onClick={() => onAction(`送礼 ${npc.name} ${gift}`)}>送出</button>
    </div>
  </section>
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
      <button type="button" ref={codexButtonRef} aria-haspopup="dialog" aria-expanded={codexOpen} data-active={codexOpen || undefined} onClick={onToggleCodex}><Menu size={18} /><span>{codexOpen ? '收起侧记' : '洞天侧记'}</span>{hasUpdates && <i className="nav-update-dot" aria-label="世界与修行有可推进事项" />}</button>
    </nav>
  )
}
