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
import { SpiritBeastSanctuary } from './SpiritBeastSanctuary'
import { StoryChronicle } from './StoryChronicle'

interface Props { snapshot: Snapshot; busy: boolean; readOnly: boolean; onAction: (action: string) => void }

export function PathwaysCodex({ snapshot, busy, readOnly, onAction }: Props) {
  const { state } = snapshot
  if (['new', 'character_creation_basic', 'character_creation_traits'].includes(state.phase)) {
    return <div className="empty-state"><strong>道途待启</strong><p>完成创角后，主线、委托、百艺与宗门事务将在此展开。</p></div>
  }
  const actions = { busy: busy || state.phase !== 'playing', readOnly, onAction }
  return <div className="pathways-codex">
    {state.phase !== 'playing' && <p className="codex-pending-note">当前尚有抉择待定，可查看卷册；请返回场景完成抉择后再行动。</p>}
    <section><h3>仙途与因果</h3><p>追踪主线，领取历练与委托的报酬。</p>
      <StoryChronicle story={snapshot.story} {...actions} />
      <JourneyTracker journey={snapshot.journey} {...actions} />
      <CommissionBoard commissions={snapshot.commissions} {...actions} />
    </section>
    <section><h3>修行与百艺</h3><p>悟道、养兽、阵法与器物，各循其道。</p>
      <DaoTree dao={snapshot.dao} {...actions} />
      <ArtMasteryCodex mastery={snapshot.art_mastery} {...actions} />
      <SpiritBeastSanctuary beasts={snapshot.spirit_beasts} {...actions} />
      <FormationAtlas formations={snapshot.formations} {...actions} />
      <ArtifactForge artifacts={snapshot.artifacts} {...actions} />
    </section>
    <section><h3>山门事务</h3><p>研读藏经，经营属于你的道统。</p>
      <SectLibrary library={snapshot.sect_library} {...actions} />
      <SectDominion domain={snapshot.sect_domain} {...actions} />
    </section>
    {(snapshot.auction.active || snapshot.auction.pending || snapshot.new_era.active) && <section><h3>九州机缘</h3><p>正在发生的法会与新世余波。</p>
      <AuctionHouse auction={snapshot.auction} stones={state.player.spirit_stones} {...actions} />
      <NewEraChronicle era={snapshot.new_era} {...actions} />
    </section>}
  </div>
}
