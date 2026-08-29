import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'motion/react'
import { Backpack, CalendarDays, CircleAlert, CloudSun, Gem, HeartHandshake, History, Leaf, LoaderCircle, ScrollText, Shield, Sparkles, UserRound } from 'lucide-react'
import { useState } from 'react'
import { fetchSnapshot, performAction } from './api/client'
import type { Snapshot } from './api/types'
import { ActionDock } from './components/ActionDock'
import { CharacterSheet } from './components/CharacterSheet'
import { DecisionPanel } from './components/DecisionPanel'
import { EventPanel } from './components/EventPanel'
import { GameTooltip, TooltipProvider } from './components/GameTooltip'
import { Panel } from './components/Panel'
import { ProgressStat } from './components/ProgressStat'
import { useUiStore } from './store/ui'

const monthNames = ['春一月', '春二月', '春三月', '夏四月', '夏五月', '夏六月', '秋七月', '秋八月', '秋九月', '冬十月', '冬十一月', '冬十二月']

function LoadingScreen() {
  return <main className="loading-screen"><LoaderCircle className="animate-spin" /><h1>正在观照此方天地</h1><p>规则引擎与卷宗正在汇合……</p></main>
}

function ErrorScreen({ message }: { message: string }) {
  return <main className="loading-screen error"><CircleAlert /><h1>暂时未能连通本地世界</h1><p>{message}</p><button type="button" onClick={() => window.location.reload()}>重新尝试</button></main>
}

function Inventory({ snapshot }: { snapshot: Snapshot }) {
  const resources = Object.entries(snapshot.state.player.resources || {})
  const inventory = snapshot.state.player.inventory || []
  const items: Array<[string, number]> = [...inventory.map((name) => [name, 1] as [string, number]), ...resources]
  return (
    <Panel title="乾坤袋" icon={<Backpack size={18} />} meta={items.length ? `${items.length} 类` : '空'}>
      {items.length ? <div className="inventory-grid">{items.slice(0, 8).map(([name, count]) => <button type="button" key={name}><span>{name.slice(0, 1)}</span><strong>{name}</strong><small>×{count}</small></button>)}</div> : <div className="empty-inventory"><div><Gem size={20} /><span /><span /><span /></div><p>获取丹药、法器或材料后，将陈列于此。</p><small>当前容量 0 / 20</small></div>}
    </Panel>
  )
}

function Relations({ snapshot }: { snapshot: Snapshot }) {
  const known = Object.entries(snapshot.state.npc_relations || {}).filter(([, relation]) => Number(relation.affinity || 0) !== 0 || relation.path)
  return (
    <Panel title="人物牵绊" icon={<HeartHandshake size={18} />} meta={known.length ? `${known.length} 位` : '缘分未定'} className="balanced-panel">
      {known.length ? <div className="relation-stack">{known.slice(0, 4).map(([name, relation]) => { const profile = snapshot.npc_profiles[name]; return <button type="button" key={name}><span>{name.slice(0, 1)}</span><div><strong>{name}</strong><small>{profile?.identity || '身份未明'}</small><i><b style={{ width: `${Math.max(0, Number(relation.affinity || 0))}%` }} /></i></div><em>{relation.path || '相识'}<small>好感 {relation.affinity || 0}</small></em></button>})}</div> : <div className="empty-state"><UserRound size={24} /><strong>尘缘尚未落笔</strong><p>结识人物后，这里会显示关系、好感与最近变化。</p></div>}
    </Panel>
  )
}

function HistoryPanel({ snapshot }: { snapshot: Snapshot }) {
  const { historyExpanded, toggleHistory } = useUiStore()
  const history = [...(snapshot.state.history || [])].reverse()
  const shown = historyExpanded ? history : history.slice(0, 4)
  return (
    <Panel title="最近经历" icon={<History size={18} />} meta={`最近 ${Math.min(4, history.length)} 条`} className="history-panel">
      {shown.length ? <ol className="history-list">{shown.map((entry, index) => <li key={`${entry}-${index}`} title={entry}><span>{history.length - index}</span><p>{entry}</p></li>)}</ol> : <div className="empty-state compact"><ScrollText size={22} /><p>等待第一段经历。</p></div>}
      {history.length > 4 && <button className="quiet-link" type="button" onClick={toggleHistory}>{historyExpanded ? '收起旧事' : `查看全部 ${history.length} 条`}</button>}
    </Panel>
  )
}

interface GameProps {
  snapshot: Snapshot
  busy: boolean
  activeAction: string
  error: string
  onAction: (action: string) => void
}

function Game({ snapshot, busy, activeAction, error, onAction }: GameProps) {
  const { state, presentation, decision } = snapshot
  const { player } = state
  const canUseQuickActions = state.phase === 'playing'
  const canDraft = ['playing', 'character_creation_basic', 'character_creation_traits'].includes(state.phase)
  return (
    <TooltipProvider>
      <div className="game-shell">
        <header className="topbar">
          <div className="brand"><span>高自由修仙文字模拟</span><h1>问道长生</h1><p>凡尘一念，万法由心</p></div>
          <div className="topbar-actions">
            <div className="time-badge"><CalendarDays size={16} /><span>第 {state.turn} 回合</span><b /><strong>天玄历 {state.calendar_year} 年 · {monthNames[state.month - 1] || `${state.month}月`}</strong></div>
            <CharacterSheet player={player} />
          </div>
        </header>

        <main className="game-grid">
          <aside className="left-rail">
            <Panel title="修士名帖" icon={<UserRound size={18} />} meta={player.location}>
              <div className="name-card"><span>{player.name.slice(0, 1)}</span><div><h3>{player.name}</h3><p>道号 · {player.dao_name}</p></div></div>
              <div className="identity-tags"><span><small>境界</small>{player.realm}</span><span><small>宗门</small>{player.sect}</span><GameTooltip label="灵石是修仙界通行货币，可在坊市购买丹药、法器与材料。"><span tabIndex={0}><small>灵石</small>{player.spirit_stones}</span></GameTooltip></div>
              <p className="life-label">{player.gender} · {player.age}岁（寿元 {player.lifespan}）</p>
            </Panel>
            <Panel title="道途根基" icon={<Shield size={18} />} meta={player.condition}>
              <div className="progress-stack">
                <ProgressStat label="气血" value={player.health} max={player.health_max} tone="health" help="气血归零会重伤或陨落，可通过丹药与休养恢复。" />
                <ProgressStat label="灵力" value={player.spirit} max={player.spirit_max} tone="spirit" help="施展法术会消耗灵力，修炼和休息可以恢复。" />
                <ProgressStat label="修为" value={player.cultivation} max={player.cultivation_required} tone="cultivation" help="修为达到当前上限后，可以尝试突破境界。" />
              </div>
              <div className="root-row"><span><Leaf size={14} />{player.spiritual_root}</span><span><Sparkles size={14} />{player.constitution}</span></div>
            </Panel>
            <Inventory snapshot={snapshot} />
          </aside>

          <section className="main-stage">
            <div className="stage-heading"><div><span>当前所在</span><h2>{player.location}</h2></div><span className="era-badge"><CloudSun size={15} />{state.world_era}</span></div>
            <AnimatePresence mode="wait">
              <motion.div key={`${state.turn}-${presentation.title}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.24 }}>
                <EventPanel presentation={presentation} onAction={onAction} />
              </motion.div>
            </AnimatePresence>
            <DecisionPanel decision={decision} activeAction={activeAction} busy={busy} onChoose={onAction} />
            {error && <p className="action-error"><CircleAlert size={16} />{error}</p>}
            <ActionDock busy={busy} canQuickAct={canUseQuickActions} canDraft={canDraft} onAction={onAction} />
          </section>

          <aside className="right-rail">
            <Relations snapshot={snapshot} />
            <HistoryPanel snapshot={snapshot} />
            <Panel title="九州风声" icon={<CloudSun size={18} />} meta={state.world_era} className="balanced-panel world-panel">
              <div><span aria-hidden="true">闻</span><p>{state.last_world_event || '灵气潮汐尚在暗中酝酿，九州表面仍显平静。'}</p></div>
            </Panel>
          </aside>
        </main>
        <footer className="game-footer">本地运行 · 存档保存在你的电脑中 · 数值由规则引擎真实结算 · V0.31 React 技术预览</footer>
      </div>
    </TooltipProvider>
  )
}

export default function App() {
  const queryClient = useQueryClient()
  const [activeAction, setActiveAction] = useState('')
  const [actionError, setActionError] = useState('')
  const snapshot = useQuery({ queryKey: ['snapshot'], queryFn: fetchSnapshot, staleTime: 15_000, retry: 1 })
  const action = useMutation({
    mutationFn: performAction,
    onMutate: (value) => { setActiveAction(value); setActionError('') },
    onSuccess: (data) => { queryClient.setQueryData(['snapshot'], data) },
    onError: (reason: Error) => setActionError(reason.message),
    onSettled: () => setActiveAction(''),
  })

  if (snapshot.isPending) return <LoadingScreen />
  if (snapshot.isError) return <ErrorScreen message={snapshot.error.message} />
  return <Game snapshot={snapshot.data} busy={action.isPending} activeAction={activeAction} error={actionError} onAction={(value) => action.mutate(value)} />
}
