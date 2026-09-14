import { BedDouble, Calendar, ChevronRight, Coins, Leaf, MapPin, Mountain, Package, RotateCcw, Shield, Sparkles, UserRound } from 'lucide-react'
import type { Snapshot } from '../api/types'
import { CharacterSheet } from './CharacterSheet'
import { CultivatorHud } from './ImmersiveScene'
import { GameTooltip } from './GameTooltip'
import { InventoryDialog } from './InventoryDialog'

interface CultivatorRailProps {
  snapshot: Snapshot
  busy: boolean
  readOnly: boolean
  canQuickAct: boolean
  onAction: (action: string) => void
  onOpenCodex: () => void
  onOpenBreakthrough?: () => void
  onOpenRealmsLadder?: () => void
}

export function CultivatorRail({
  snapshot,
  busy,
  readOnly,
  canQuickAct,
  onAction,
  onOpenCodex,
  onOpenBreakthrough,
  onOpenRealmsLadder,
}: CultivatorRailProps) {
  const { state } = snapshot
  const { player } = state
  const activeLegacy = snapshot.legacy.active_legacy
  const isCultivationMax = player.cultivation >= player.cultivation_required
  const lifeRemaining = Math.max(0, player.lifespan - player.age)
  const lifePercent = player.lifespan > 0 ? Math.min(100, Math.max(0, (player.age / player.lifespan) * 100)) : 0
  const inventoryTypes = snapshot.inventory?.total_types || 0
  const inventoryCount = snapshot.inventory?.total_count || 0

  return (
    <div className="cultivator-rail-container">
      {/* 命台封印顶标 */}
      <div className="rail-section-header">
        <span className="rail-seal-mark" aria-hidden="true">命</span>
        <div>
          <h4>修士命台</h4>
          <small>道身法相 · 天道因果</small>
        </div>
      </div>

      {/* 核心道身与三大道基 */}
      <div className="rail-card rail-hud-card">
        <CultivatorHud player={player} />
      </div>

      {/* 境界通天图直达入口 */}
      {onOpenRealmsLadder && (
        <button
          type="button"
          className="rail-ladder-trigger"
          onClick={onOpenRealmsLadder}
          title="查看仙道十重天通天境界图（低境界在下，高境界在上）"
        >
          <span><Mountain size={13} />境界通天仙阶</span>
          <ChevronRight size={13} />
        </button>
      )}

      {/* 寿元天年与仙途岁月 */}
      <div className="rail-card rail-lifespan-card">
        <div className="rail-card-row">
          <span><Calendar size={13} />天年寿元</span>
          <strong>{player.age} 岁 <small>/ {player.lifespan} 载</small></strong>
        </div>
        <div className="rail-progress-bar" title={`已度过 ${player.age} 年，尚余 ${lifeRemaining} 年寿元`}>
          <div className="rail-progress-fill lifespan-fill" style={{ width: `${lifePercent}%` }} />
        </div>
        <div className="rail-card-meta">
          <small>尘世已历 {lifePercent.toFixed(0)}%</small>
          <em>尚余约 {lifeRemaining} 年</em>
        </div>
      </div>

      {/* 突破机缘提示 (当修为满时高亮显示) */}
      {isCultivationMax && (
        <div className="rail-card rail-breakthrough-banner">
          <div className="banner-glow" aria-hidden="true" />
          <header>
            <Sparkles size={16} />
            <strong>修为已至大圆满</strong>
          </header>
          <p>{player.realm} 瓶颈松动，天地灵气共鸣！</p>
          <button
            type="button"
            className="rail-breakthrough-btn"
            disabled={!canQuickAct || busy || readOnly}
            onClick={() => {
              onOpenBreakthrough?.()
              onAction('突破')
            }}
          >
            叩问突破境界
          </button>
        </div>
      )}

      {/* 灵根、体质与宿世遗泽 */}
      <div className="rail-card rail-traits-card">
        <div className="trait-tag root-tag">
          <Leaf size={14} />
          <div>
            <small>天生灵根</small>
            <strong>{player.spiritual_root || '凡骨无相'}</strong>
          </div>
        </div>
        <div className="trait-tag constitution-tag">
          <Sparkles size={14} />
          <div>
            <small>先天道体</small>
            <strong>{player.constitution || '凡人体质'}</strong>
          </div>
        </div>
        {activeLegacy?.name && (
          <GameTooltip label={activeLegacy.effect || '来自宿世轮回的先祖馈赠。'}>
            <div className="trait-tag legacy-tag" tabIndex={0}>
              <RotateCcw size={14} />
              <div>
                <small>宿世遗泽</small>
                <strong>{activeLegacy.name}</strong>
              </div>
            </div>
          </GameTooltip>
        )}
      </div>

      {/* 随身资粮与乾坤袋速览 */}
      <div className="rail-card rail-wealth-card">
        <div className="wealth-row">
          <GameTooltip label="修仙界流通货币，可在各大坊市百宝阁换取灵药法宝。">
            <div className="wealth-badge" tabIndex={0}>
              <Coins size={15} />
              <div>
                <small>灵石储蓄</small>
                <strong>{player.spirit_stones} <small>颗</small></strong>
              </div>
            </div>
          </GameTooltip>
          <div className="wealth-badge">
            <Package size={15} />
            <div>
              <small>乾坤法宝</small>
              <strong>{inventoryTypes} <small>种 / {inventoryCount} 件</small></strong>
            </div>
          </div>
        </div>

        {/* 随身物品与道身明细快捷弹窗 */}
        <div className="rail-quick-actions">
          <InventoryDialog
            inventory={snapshot.inventory}
            busy={busy}
            canAct={canQuickAct}
            readOnly={readOnly}
            onAction={onAction}
          />
          <CharacterSheet player={player} />
        </div>
      </div>

      {/* 所在洞府与伤势调养状态 */}
      <div className="rail-card rail-status-card">
        <div className="status-row">
          <span><MapPin size={13} />驻足之地</span>
          <strong>{player.location}</strong>
        </div>
        <div className="status-row">
          <span><Shield size={13} />肉身状态</span>
          <em data-status={player.condition}>{player.condition || '安好'}</em>
        </div>
        {snapshot.recovery?.active && (
          <div className="recovery-alert">
            <BedDouble size={14} />
            <span>肉身负伤，需静养调息</span>
            <button
              type="button"
              disabled={!canQuickAct || busy || readOnly || !snapshot.recovery.can_rest}
              onClick={() => onAction(snapshot.recovery.rest_action)}
            >
              静养
            </button>
          </div>
        )}
      </div>

      {/* 快速展开深入卷宗 */}
      <button
        type="button"
        className="rail-codex-shortcut"
        onClick={onOpenCodex}
      >
        <span><UserRound size={15} />深入洞天卷宗 (百艺/人脉/历练)</span>
        <ChevronRight size={14} />
      </button>
    </div>
  )
}
