import { Compass, Mountain, ScrollText, Sparkles } from 'lucide-react'
import { useState } from 'react'
import type { Snapshot } from '../api/types'
import { ArtMasteryCodex } from './ArtMasteryCodex'
import { ArtifactForge } from './ArtifactForge'
import { AuctionHouse } from './AuctionHouse'
import { CommissionBoard } from './CommissionBoard'
import { DaoTree } from './DaoTree'
import { FormationAtlas } from './FormationAtlas'
import { JourneyTracker } from './JourneyTracker'
import { NewEraChronicle } from './NewEraChronicle'
import { SectDominion } from './SectDominion'
import { SectLibrary } from './SectLibrary'
import { SectMembershipEntry } from './SectMembershipPage'
import { SpiritBeastSanctuary } from './SpiritBeastSanctuary'
import { StoryChronicle } from './StoryChronicle'

interface Props { snapshot: Snapshot; busy: boolean; readOnly: boolean; onAction: (action: string) => void }

export function PathwaysCodex({ snapshot, busy, readOnly, onAction }: Props) {
  const { state } = snapshot
  const [section, setSection] = useState<'causality' | 'cultivation' | 'sect' | 'opportunity'>('causality')
  if (['new', 'character_creation_basic', 'character_creation_traits'].includes(state.phase)) {
    return <div className="empty-state"><strong>道途待启</strong><p>完成创角后，主线、委托、百艺与宗门事务将在此展开。</p></div>
  }
  const actions = { busy: busy || state.phase !== 'playing', readOnly, onAction }
  const opportunityAvailable = Boolean(snapshot.auction.active || snapshot.auction.pending || snapshot.new_era.active)
  const sections = [
    { id: 'causality' as const, label: '仙途因果', hint: '主线 · 章程 · 委托', icon: ScrollText, updated: snapshot.story.available || snapshot.commissions.active.some((item) => item.ready) },
    { id: 'cultivation' as const, label: '修行百艺', hint: '悟道 · 万法 · 灵兽 · 阵法 · 法宝', icon: Sparkles, updated: false },
    { id: 'sect' as const, label: '山门事务', hint: '藏经 · 宗门经营', icon: Mountain, updated: false },
    ...(opportunityAvailable ? [{ id: 'opportunity' as const, label: '九州机缘', hint: '拍卖 · 新世余波', icon: Compass, updated: snapshot.new_era.available }] : []),
  ]
  const current = sections.find((item) => item.id === section) || sections[0]
  return <div className="pathways-codex">
    {state.phase !== 'playing' && <p className="codex-pending-note">当前尚有抉择待定，可查看卷册；请返回场景完成抉择后再行动。</p>}
    <nav className="pathways-hub" aria-label="修行卷册分类">
      {sections.map(({ id, label, hint, icon: Icon, updated }) => <button type="button" key={id} aria-pressed={current.id === id} data-active={current.id === id || undefined} onClick={() => setSection(id)}><span><Icon size={16} />{updated && <i aria-label="有可推进事项" />}</span><strong>{label}</strong><small>{hint}</small></button>)}
    </nav>
    {current.id === 'causality' && <section className="pathways-surface" aria-labelledby="pathways-causality"><header><span>因</span><div><small>命数有迹</small><h3 id="pathways-causality">仙途与因果</h3><p>追踪主线，领取历练与委托的报酬。</p></div></header>
      <StoryChronicle story={snapshot.story} {...actions} />
      <JourneyTracker journey={snapshot.journey} {...actions} />
      <CommissionBoard commissions={snapshot.commissions} {...actions} />
    </section>}
    {current.id === 'cultivation' && <section className="pathways-surface" aria-labelledby="pathways-cultivation"><header><span>修</span><div><small>万法归途</small><h3 id="pathways-cultivation">修行与百艺</h3><p>悟道、养兽、阵法与器物，各循其道。</p></div></header>
      <DaoTree dao={snapshot.dao} {...actions} />
      <ArtMasteryCodex mastery={snapshot.art_mastery} {...actions} />
      <SpiritBeastSanctuary beasts={snapshot.spirit_beasts} {...actions} />
      <FormationAtlas formations={snapshot.formations} {...actions} />
      <ArtifactForge artifacts={snapshot.artifacts} {...actions} />
    </section>}
    {current.id === 'sect' && <section className="pathways-surface" aria-labelledby="pathways-sect"><header><span>宗</span><div><small>山门有序</small><h3 id="pathways-sect">山门事务</h3><p>研读藏经，经营属于你的道统。</p></div></header>
      <SectMembershipEntry membership={snapshot.sect_membership} {...actions} />
      <SectLibrary library={snapshot.sect_library} {...actions} />
      <SectDominion domain={snapshot.sect_domain} {...actions} />
    </section>}
    {current.id === 'opportunity' && opportunityAvailable && <section className="pathways-surface" aria-labelledby="pathways-opportunity"><header><span>缘</span><div><small>风云际会</small><h3 id="pathways-opportunity">九州机缘</h3><p>正在发生的法会与新世余波。</p></div></header>
      <AuctionHouse auction={snapshot.auction} stones={state.player.spirit_stones} {...actions} />
      <NewEraChronicle era={snapshot.new_era} {...actions} />
    </section>}
  </div>
}
