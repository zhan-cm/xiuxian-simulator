import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'motion/react'
import { CalendarDays, CheckCircle2, CircleAlert, CloudSun, Eye, HeartHandshake, History, Leaf, LoaderCircle, RotateCcw, ScrollText, Shield, Sparkles, UserRound, Waypoints, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { fetchShowcase, fetchSnapshot, performAction } from './api/client'
import type { Snapshot } from './api/types'
import { ActionDock } from './components/ActionDock'
import { ArchiveDialog } from './components/ArchiveDialog'
import { CharacterSheet } from './components/CharacterSheet'
import { CodexDrawer } from './components/CodexDrawer'
import { DecisionPanel } from './components/DecisionPanel'
import { EventPanel } from './components/EventPanel'
import { GameTooltip, TooltipProvider } from './components/GameTooltip'
import { InventoryDialog } from './components/InventoryDialog'
import { Panel } from './components/Panel'
import { ProgressStat } from './components/ProgressStat'
import { ShowcaseNavigator } from './components/ShowcaseNavigator'
import { loadShowcaseReview } from './showcaseReview'
import { PathwaysCodex } from './components/PathwaysCodex'
import { RecoveryCodex } from './components/RecoveryCodex'
import { LegacyChronicle } from './components/LegacyChronicle'
import { CultivatorHud, ImmersiveScene, SocialActionBar, WorldNavigation } from './components/ImmersiveScene'
import { findEncounterNpc } from './sceneLogic'
import { useUiStore } from './store/ui'

const monthNames = ['春一月', '春二月', '春三月', '夏四月', '夏五月', '夏六月', '秋七月', '秋八月', '秋九月', '冬十月', '冬十一月', '冬十二月']

function LoadingScreen() {
  return <main className="loading-screen"><LoaderCircle className="animate-spin" /><h1>正在观照此方天地</h1><p>规则引擎与卷宗正在汇合……</p></main>
}

function ErrorScreen({ message }: { message: string }) {
  return <main className="loading-screen error"><CircleAlert /><h1>暂时未能连通本地世界</h1><p>{message}</p><button type="button" onClick={() => window.location.reload()}>重新尝试</button></main>
}

function Relations({ snapshot, disabled, onAction }: { snapshot: Snapshot; disabled: boolean; onAction: (action: string) => void }) {
  const known = Object.entries(snapshot.state.npc_relations || {}).filter(([, relation]) => Number(relation.affinity || 0) !== 0 || relation.path)
  const lifePending = snapshot.npc_lives?.pending_count || 0
  const networkPending = snapshot.npc_network?.pending?.id ? 1 : 0
  const pendingMeta = [lifePending ? `${lifePending} 封护道书` : '', networkPending ? '1 桩人情待决' : ''].filter(Boolean).join(' · ')
  return (
    <Panel title="人物牵绊" icon={<HeartHandshake size={18} />} meta={pendingMeta || (known.length ? `${known.length} 位` : '缘分未定')} className="balanced-panel">
      {known.length ? <div className="relation-stack">{known.slice(0, 4).map(([name, relation]) => {
        const profile = snapshot.npc_profiles[name]
        return <button type="button" disabled={disabled} onClick={() => onAction('情缘')} title={disabled ? '请在正常游玩且无待决抉择时查看' : '打开完整人物生平'} key={name} data-alive={profile?.alive !== false || undefined}>
          <span>{name.slice(0, 1)}</span>
          <div><strong>{name}</strong><small>{profile?.realm || '境界未明'} · {profile?.age ?? '?'}岁 · {profile?.status || '近况未明'}</small><i><b style={{ width: `${Math.max(0, Math.min(100, Number(relation.affinity || 0)))}%` }} /></i></div>
          <em>{relation.path || '相识'}<small>好感 {relation.affinity || 0}</small></em>
        </button>
      })}</div> : <div className="empty-state"><UserRound size={24} /><strong>尘缘尚未落笔</strong><p>结识人物后，这里会显示关系、好感与最近变化。</p></div>}
      <button className="network-shortcut" type="button" disabled={disabled} onClick={() => onAction('人脉')}><Waypoints size={13} /><span>查看众生缘网</span>{networkPending ? <em>有新纷争</em> : <small>{snapshot.npc_network?.bond_count || 0} 段因缘</small>}</button>
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
  showcase: boolean
  showcaseLoading: boolean
  onShowcase: () => void
  onExitShowcase: () => void
  notice: string
  onArchiveChanged: () => Promise<unknown> | void
  onNotice: (message: string) => void
}

function Game({ snapshot, busy, activeAction, error, onAction, showcase, showcaseLoading, onShowcase, onExitShowcase, notice, onArchiveChanged, onNotice }: GameProps) {
  const { state, presentation, decision } = snapshot
  const { player } = state
  const { codexOpen, toggleCodex, closeCodex } = useUiStore()
  const codexTrigger = useRef<HTMLButtonElement>(null)
  // 人情纷争也带 exclusive 标记，但规则允许暂缓；只有实际游戏阶段锁定行动。
  const canUseQuickActions = state.phase === 'playing'
  const canDraft = canUseQuickActions || ['character_creation_basic', 'character_creation_traits'].includes(state.phase)
  const hasUpdates = snapshot.story.available || snapshot.new_era.available || snapshot.commissions.active.some((item) => item.ready)
  const encounterNpc = findEncounterNpc(snapshot.npc_profiles, presentation)
  const onCodexAction = (value: string) => {
    if (busy || showcase || !canUseQuickActions) return
    closeCodex()
    onAction(value)
  }
  const networkSurface = ['人脉', '缘网', '众生缘网'].includes(presentation.action) || presentation.action.startsWith('介入人情')
  const legacySurface = state.phase === 'ended'
  const activeLegacy = snapshot.legacy.active_legacy
  return (
    <TooltipProvider>
      <div className="game-shell" data-showcase={showcase || undefined} data-ended={legacySurface || undefined}>
        <header className="topbar immersive-topbar">
          <div className="brand"><span>高自由修仙文字模拟</span><h1>问道长生</h1><p>凡尘一念，万法由心</p></div>
          {!legacySurface && <CultivatorHud player={player} />}
          <div className="topbar-actions">
            <div className="time-badge"><CalendarDays size={16} /><span>第 {state.turn} 回合</span><b /><strong>天玄历 {state.calendar_year} 年 · {monthNames[state.month - 1] || `${state.month}月`}</strong></div>
            <button className="showcase-trigger" type="button" disabled={showcaseLoading} onClick={showcase ? onExitShowcase : onShowcase}>{showcase ? <X size={16} /> : <Eye size={16} />}{showcase ? '退出巡览' : showcaseLoading ? '准备巡览…' : '成果巡览'}</button>
            {!showcase && <ArchiveDialog saves={snapshot.save_summaries} busy={busy} onAction={onAction} onChanged={onArchiveChanged} onNotice={onNotice} />}
            <CharacterSheet player={player} />
          </div>
        </header>

        <main className="game-grid immersive-grid">
          <section className="main-stage">
            {!legacySurface && <ImmersiveScene state={state} presentation={presentation} npcProfiles={snapshot.npc_profiles} calendarLabel={`天玄历 ${state.calendar_year} 年 · ${monthNames[state.month - 1] || `${state.month}月`}`} />}
            {legacySurface && <div className="stage-heading"><div><span>本世已终</span><h2>{player.name} · 仙途评传</h2></div></div>}
            {!legacySurface && <>
              <AnimatePresence mode="wait">
                <motion.div key={`${state.turn}-${presentation.title}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.24 }}>
                  <EventPanel presentation={presentation} cave={snapshot.cave} npcLives={snapshot.npc_lives} npcNetwork={snapshot.npc_network} readOnly={showcase || busy} immersive onAction={onAction} />
                </motion.div>
              </AnimatePresence>
              <SocialActionBar npc={encounterNpc} inventory={snapshot.inventory} disabled={busy || showcase || !canUseQuickActions} onAction={onAction} />
              {!networkSurface && <DecisionPanel decision={decision} activeAction={activeAction} busy={busy} readOnly={showcase} onChoose={onAction} />}
            </>}
            {legacySurface && <LegacyChronicle legacy={snapshot.legacy} busy={busy} readOnly={showcase} onAction={onAction} />}
            {error && <p className="action-error"><CircleAlert size={16} />{error}</p>}
            {!legacySurface && <ActionDock busy={busy} canQuickAct={canUseQuickActions} canDraft={canDraft} readOnly={showcase} recovery={snapshot.recovery} onAction={onAction} />}
          </section>
            {!legacySurface && <CodexDrawer open={codexOpen} onClose={closeCodex} returnFocusRef={codexTrigger} hasUpdates={Boolean(hasUpdates)}
              character={
                <section className="codex-column">
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
                    <div className="root-row"><span><Leaf size={14} />{player.spiritual_root}</span><span><Sparkles size={14} />{player.constitution}</span>{activeLegacy.name && <GameTooltip label={activeLegacy.effect || '来自上一世的轮回传承。'}><span tabIndex={0}><RotateCcw size={14} />{activeLegacy.name}</span></GameTooltip>}</div>
                    <RecoveryCodex recovery={snapshot.recovery} busy={busy || !canUseQuickActions} readOnly={showcase} onAction={onCodexAction} />
                  </Panel>
                  <InventoryDialog inventory={snapshot.inventory} busy={busy} canAct={canUseQuickActions} readOnly={showcase} onAction={onCodexAction} />
                </section>
              }
              pathways={<PathwaysCodex snapshot={snapshot} busy={busy || !canUseQuickActions} readOnly={showcase} onAction={onCodexAction} />}
              world={
                <section className="codex-column">
                  <Relations snapshot={snapshot} disabled={busy || showcase || !canUseQuickActions} onAction={onCodexAction} />
                  <HistoryPanel snapshot={snapshot} />
                  <Panel title="九州风声" icon={<CloudSun size={18} />} meta={state.world_era} className="balanced-panel world-panel">
                    <div><span aria-hidden="true">闻</span><p>{state.last_world_event || '灵气潮汐尚在暗中酝酿，九州表面仍显平静。'}</p></div>
                  </Panel>
                </section>
              }
            />}
        </main>
        {!legacySurface && <WorldNavigation activeAction={presentation.action} disabled={busy || showcase || !canUseQuickActions} disabledReason={showcase ? '成果巡览仅供查看' : busy ? '正在推演，请稍候' : '请先完成当前抉择'} codexOpen={codexOpen} codexButtonRef={codexTrigger} hasUpdates={Boolean(hasUpdates)} onNavigate={onAction} onToggleCodex={toggleCodex} />}
        <footer className="game-footer">问道长生 · 本地运行 · 进度保存在你的电脑中</footer>
        <AnimatePresence>{notice && <motion.div className="action-toast" initial={{ opacity: 0, y: 14, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 8 }}><CheckCircle2 size={17} /><div><strong>推演完成</strong><p>{notice}</p></div></motion.div>}</AnimatePresence>
      </div>
    </TooltipProvider>
  )
}

export default function App() {
  const queryClient = useQueryClient()
  const [activeAction, setActiveAction] = useState('')
  const [actionError, setActionError] = useState('')
  const [notice, setNotice] = useState('')
  const [showcaseIndex, setShowcaseIndex] = useState<number | null>(null)
  const snapshot = useQuery({ queryKey: ['snapshot'], queryFn: fetchSnapshot, staleTime: 15_000, retry: 1 })
  const showcase = useQuery({ queryKey: ['showcase'], queryFn: fetchShowcase, enabled: false, staleTime: Infinity })
  const action = useMutation({
    mutationFn: performAction,
    onMutate: (value) => { setActiveAction(value); setActionError(''); setNotice('') },
    onSuccess: (data, value) => {
      queryClient.setQueryData(['snapshot'], data)
      setNotice(data.presentation?.title || `已完成：${value}`)
      window.scrollTo({ top: 0, behavior: 'instant' })
    },
    onError: (reason: Error) => setActionError(reason.message),
    onSettled: () => setActiveAction(''),
  })
  useEffect(() => {
    if (!notice) return
    const timer = window.setTimeout(() => setNotice(''), 3200)
    return () => window.clearTimeout(timer)
  }, [notice])

  if (snapshot.isPending) return <LoadingScreen />
  if (snapshot.isError) return <ErrorScreen message={snapshot.error.message} />
  const pages = showcase.data?.pages || []
  const inShowcase = showcaseIndex !== null && Boolean(pages[showcaseIndex])
  const displayed = inShowcase ? pages[showcaseIndex].snapshot : snapshot.data
  const openShowcase = async () => {
    const result = await showcase.refetch()
    if (result.data?.pages.length) {
      const review = loadShowcaseReview(result.data.pages, snapshot.data.app_version)
      const resumedIndex = result.data.pages.findIndex((page) => page.id === review.currentId)
      setShowcaseIndex(resumedIndex >= 0 ? resumedIndex : 0)
    }
  }
  return (
    <>
      <Game
        snapshot={displayed}
        busy={inShowcase ? false : action.isPending}
        activeAction={inShowcase ? '' : activeAction}
        error={inShowcase ? '' : actionError}
        onAction={inShowcase ? () => undefined : (value) => action.mutate(value)}
        showcase={inShowcase}
        showcaseLoading={showcase.isFetching}
        onShowcase={openShowcase}
        onExitShowcase={() => setShowcaseIndex(null)}
        notice={inShowcase ? '' : notice}
        onArchiveChanged={async () => { await snapshot.refetch() }}
        onNotice={(message) => { setActionError(''); setNotice(message) }}
      />
      {inShowcase && <ShowcaseNavigator pages={pages} index={showcaseIndex} appVersion={snapshot.data.app_version} onIndex={setShowcaseIndex} onExit={() => setShowcaseIndex(null)} />}
    </>
  )
}
