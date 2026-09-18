import { useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import {
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  Box,
  Coins,
  Compass,
  Crown,
  DoorOpen,
  Droplets,
  EyeOff,
  Flame,
  Footprints,
  History,
  Lock,
  Mountain,
  PackageCheck,
  Shield,
  ShieldAlert,
  Skull,
  Sparkles,
  Store,
  Swords,
  X,
} from 'lucide-react'
import type { ActiveTombData, AncientTombSnapshot, TombThemeData, TombTileData } from '../api/types'

export interface AncientTombModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  ancientTomb?: AncientTombSnapshot | null
  busy?: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

function TombThemesView({
  themes,
  history,
  busy,
  readOnly,
  onAction,
}: {
  themes: TombThemeData[]
  history: string[]
  busy: boolean
  readOnly: boolean
  onAction: (action: string) => void
}) {
  const [selectedThemeId, setSelectedThemeId] = useState<string>('sword_crypt')

  const handleEnter = (themeId: string) => {
    if (busy || readOnly) return
    onAction(`进入古墓 ${themeId}`)
  }

  return (
    <div className="tomb-themes-view">
      <div className="tomb-view-intro">
        <h3>大能秘境 · 沉眠古冢</h3>
        <p>
          九州古脉之下沉睡着数万载以前破碎虚空的太古大能与远古道尊真身。
          墓中机关星罗棋布，妖尸幽魂扼守险关；亦封存着通天古经、造化神物与无上仙兵。
        </p>
      </div>

      {themes.every((t) => !t.unlocked) && (
        <div
          className="tomb-prep-banner"
          style={{
            padding: '14px 18px',
            marginBottom: '18px',
            borderRadius: '8px',
            background: 'rgba(239, 68, 68, 0.08)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            textAlign: 'left',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#f87171', marginBottom: '6px' }}>
            <ShieldAlert size={16} />
            <strong style={{ fontSize: '14px' }}>太古禁制封印 · 勘阵备战指南</strong>
          </div>
          <p style={{ color: '#cbd5e1', fontSize: '13px', lineHeight: 1.6, margin: '0 0 12px' }}>
            大能古冢设有万载上古锁灵仙阵，需修士神识达到【筑基期】方能窥破阵眼破禁而入。当前修为尚在炼气期，建议先行突破筑基天堑，并备足回春灵丹与护身法宝以御死局！
          </p>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              type="button"
              disabled={busy || readOnly}
              onClick={() => onAction('突破')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '6px 14px',
                borderRadius: '5px',
                background: 'linear-gradient(135deg, #e11d48, #9f1239)',
                color: '#fff',
                border: 'none',
                fontSize: '12px',
                fontWeight: 600,
                cursor: busy || readOnly ? 'not-allowed' : 'pointer',
              }}
            >
              <Mountain size={13} />
              <span>凝气冲击筑基</span>
            </button>
            <button
              type="button"
              disabled={busy || readOnly}
              onClick={() => onAction('坊市')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '6px 14px',
                borderRadius: '5px',
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                color: '#cbd5e1',
                fontSize: '12px',
                cursor: busy || readOnly ? 'not-allowed' : 'pointer',
              }}
            >
              <Store size={13} />
              <span>坊市备足灵药</span>
            </button>
            <button
              type="button"
              disabled={busy || readOnly}
              onClick={() => onAction('委托')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                padding: '6px 14px',
                borderRadius: '5px',
                background: 'rgba(245, 158, 11, 0.12)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                color: '#fbbf24',
                fontSize: '12px',
                cursor: busy || readOnly ? 'not-allowed' : 'pointer',
              }}
            >
              <Coins size={13} />
              <span>接取悬榜生财</span>
            </button>
          </div>
        </div>
      )}

      <div className="tomb-cards-grid">
        {themes.map((theme) => {
          const isSelected = selectedThemeId === theme.id
          return (
            <div
              key={theme.id}
              className={`tomb-theme-card ${isSelected ? 'selected' : ''} ${
                !theme.unlocked ? 'locked' : ''
              }`}
              onClick={() => setSelectedThemeId(theme.id)}
            >
              <div className="theme-card-head">
                <h4 className="theme-name">{theme.name}</h4>
                {theme.unlocked ? (
                  <span className="theme-badge-unlocked">
                    准入 · {theme.recommended_realm}
                  </span>
                ) : (
                  <span className="theme-badge-locked">
                    <Lock size={12} />
                    需达 {theme.recommended_realm}
                  </span>
                )}
              </div>
              <p className="theme-desc">{theme.description}</p>
              <div className="theme-loot-preview">
                <span>镇墓异宝：</span>
                <strong className="text-amber-300">{theme.special_drop}</strong>
              </div>
              <button
                type="button"
                className="theme-enter-btn"
                disabled={!theme.unlocked || busy || readOnly}
                title={
                  readOnly
                    ? '巡览只读'
                    : !theme.unlocked
                    ? `上古禁制封印，需达【${theme.recommended_realm}】破禁`
                    : `踏入【${theme.name}】探险`
                }
                onClick={(e) => {
                  e.stopPropagation()
                  handleEnter(theme.id)
                }}
              >
                {theme.unlocked ? <Sparkles size={14} /> : <Lock size={14} />}
                <span>{theme.unlocked ? '踏入古墓探险' : '禁制封印 · 境界不足'}</span>
              </button>
            </div>
          )
        })}
      </div>

      {history && history.length > 0 && (
        <div className="tomb-history-ledger">
          <div className="ledger-header">
            <History size={14} />
            <span>近期古墓探秘手记</span>
          </div>
          <ul className="ledger-list">
            {history.map((h, idx) => (
              <li key={idx}>{h}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function TombExplorerView({
  tomb,
  busy,
  readOnly,
  onAction,
}: {
  tomb: ActiveTombData
  busy: boolean
  readOnly: boolean
  onAction: (action: string) => void
}) {
  const handleMove = (direction: '上' | '下' | '左' | '右') => {
    if (busy || readOnly) return
    onAction(`古墓移动 ${direction}`)
  }

  const handleInteract = (extra: string = '') => {
    if (busy || readOnly) return
    onAction(`古墓探索 ${extra}`.trim())
  }

  const handleRetreat = () => {
    if (busy || readOnly) return
    onAction('古墓撤离')
  }

  const currentTile: TombTileData | undefined = tomb.grid.find(
    (t) => t.x === tomb.player_x && t.y === tomb.player_y
  )

  const canStepTo = (tx: number, ty: number) => {
    const dx = Math.abs(tx - tomb.player_x)
    const dy = Math.abs(ty - tomb.player_y)
    return dx + dy === 1
  }

  const handleTileClick = (tile: TombTileData) => {
    if (busy || readOnly) return
    if (!canStepTo(tile.x, tile.y)) return

    if (tile.x > tomb.player_x) handleMove('右')
    else if (tile.x < tomb.player_x) handleMove('左')
    else if (tile.y > tomb.player_y) handleMove('下')
    else if (tile.y < tomb.player_y) handleMove('上')
  }

  const getTileIcon = (tile: TombTileData, isCurrent: boolean) => {
    if (!tile.revealed) {
      return <EyeOff size={16} className="text-zinc-600 opacity-60" />
    }
    if (isCurrent) {
      return <Footprints size={18} className="text-emerald-400 animate-pulse" />
    }
    if (tile.type === 'entrance') {
      return <DoorOpen size={16} className="text-cyan-400" />
    }
    if (tile.type === 'boss') {
      return tile.cleared ? (
        <Crown size={16} className="text-amber-500" />
      ) : (
        <Skull size={18} className="text-rose-400 animate-bounce" />
      )
    }
    if (tile.type === 'treasure') {
      return <PackageCheck size={16} className={tile.cleared ? 'text-zinc-500' : 'text-amber-400'} />
    }
    if (tile.type === 'trap') {
      return <ShieldAlert size={16} className={tile.cleared ? 'text-zinc-500' : 'text-orange-400'} />
    }
    if (tile.type === 'monster') {
      return <Swords size={16} className={tile.cleared ? 'text-zinc-500' : 'text-red-400'} />
    }
    if (tile.type === 'altar') {
      return <Droplets size={16} className={tile.cleared ? 'text-zinc-500' : 'text-emerald-300'} />
    }
    return <span className="text-xs text-zinc-500">·</span>
  }

  return (
    <div className="tomb-explorer-view">
      {/* 顶部探险状态栏 */}
      <div className="tomb-status-bar">
        <div className="status-item depth-badge">
          <span>墓室深度</span>
          <strong>第 {tomb.depth} / {tomb.max_depth} 层</strong>
        </div>

        {/* 墓煞计量槽 */}
        <div className="status-item miasma-item">
          <div className="miasma-label-row">
            <span>
              <Flame size={12} className="text-purple-400" />
              墓煞侵蚀
            </span>
            <strong>{tomb.miasma} / 100</strong>
          </div>
          <div className="miasma-bar-track">
            <div
              className={`miasma-bar-fill ${
                tomb.miasma >= 70 ? 'danger' : tomb.miasma >= 40 ? 'warning' : 'safe'
              }`}
              style={{ width: `${Math.min(100, tomb.miasma)}%` }}
            />
          </div>
        </div>

        {/* 已拾得宝物 */}
        <div className="status-item loot-bag">
          <span>累积收获</span>
          <div className="loot-tags">
            <span className="loot-pill">灵石 +{tomb.loot_stones}</span>
            {Object.entries(tomb.loot_items || {}).map(([name, count]) => (
              <span key={name} className="loot-pill item">
                {name}×{count}
              </span>
            ))}
          </div>
        </div>

        <button
          type="button"
          className="tomb-retreat-btn"
          disabled={busy || readOnly}
          onClick={handleRetreat}
          title="携已得宝物安全脱离古墓，回到九州现世"
        >
          <DoorOpen size={15} />
          <span>安全撤离</span>
        </button>
      </div>

      {/* 中央网格与交互控制面板 */}
      <div className="tomb-main-stage">
        {/* 左侧：5x5 地宫灵图 */}
        <div className="tomb-grid-container">
          <div className="tomb-grid-board">
            {tomb.grid.map((tile) => {
              const isCurrent = tile.x === tomb.player_x && tile.y === tomb.player_y
              const isAdjacent = canStepTo(tile.x, tile.y)
              return (
                <button
                  key={`${tile.x}-${tile.y}`}
                  type="button"
                  className={`tomb-tile ${tile.type} ${
                    tile.revealed ? 'revealed' : 'fog'
                  } ${isCurrent ? 'current' : ''} ${
                    tile.cleared ? 'cleared' : ''
                  } ${isAdjacent ? 'adjacent' : ''}`}
                  onClick={() => handleTileClick(tile)}
                  disabled={!isAdjacent || busy || readOnly}
                  title={
                    tile.revealed
                      ? `${tile.name} (${tile.cleared ? '已勘破' : '未探明'})`
                      : '幽暗迷雾：需移步至相邻石室方可勘明'
                  }
                >
                  <div className="tile-icon">{getTileIcon(tile, isCurrent)}</div>
                  {isCurrent && <span className="current-marker">你</span>}
                  {tile.revealed && !tile.cleared && tile.type === 'boss' && (
                    <span className="boss-tag">镇殿</span>
                  )}
                </button>
              )
            })}
          </div>

          <div className="tomb-grid-legend">
            <span>图例：</span>
            <span><Footprints size={12} className="text-emerald-400" /> 当前位置</span>
            <span><PackageCheck size={12} className="text-amber-400" /> 宝匣</span>
            <span><ShieldAlert size={12} className="text-orange-400" /> 机关</span>
            <span><Swords size={12} className="text-red-400" /> 凶灵</span>
            <span><Droplets size={12} className="text-cyan-400" /> 灵泉</span>
            <span><Crown size={12} className="text-purple-400" /> 主墓</span>
          </div>
        </div>

        {/* 右侧：当前石室详情与动作指令台 */}
        <div className="tomb-inspector-panel">
          {currentTile ? (
            <div className="chamber-card">
              <div className="chamber-header">
                <div className="chamber-title-row">
                  <h4 className="chamber-name">{currentTile.name}</h4>
                  <span className="chamber-coords">
                    坐标 ({currentTile.x}, {currentTile.y})
                  </span>
                </div>
                <span
                  className={`chamber-status-badge ${
                    currentTile.cleared ? 'cleared' : 'uncleared'
                  }`}
                >
                  {currentTile.cleared ? '已勘破' : '未探明'}
                </span>
              </div>

              <p className="chamber-desc">{currentTile.description}</p>

              {/* 交互主要按钮 */}
              <div className="chamber-action-dock">
                {!currentTile.cleared && currentTile.type === 'treasure' && (
                  <button
                    type="button"
                    className="tomb-action-btn treasure-btn"
                    disabled={busy || readOnly}
                    onClick={() => handleInteract()}
                  >
                    <Box size={16} />
                    <span>解封开启宝匣</span>
                  </button>
                )}

                {!currentTile.cleared && currentTile.type === 'trap' && (
                  <button
                    type="button"
                    className="tomb-action-btn trap-btn"
                    disabled={busy || readOnly}
                    onClick={() => handleInteract()}
                  >
                    <Shield size={16} />
                    <span>神识推演破除古阵</span>
                  </button>
                )}

                {!currentTile.cleared && currentTile.type === 'monster' && (
                  <button
                    type="button"
                    className="tomb-action-btn battle-btn"
                    disabled={busy || readOnly}
                    onClick={() => handleInteract()}
                  >
                    <Swords size={16} />
                    <span>施展神通诛杀守陵凶兽</span>
                  </button>
                )}

                {!currentTile.cleared && currentTile.type === 'altar' && (
                  <button
                    type="button"
                    className="tomb-action-btn altar-btn"
                    disabled={busy || readOnly}
                    onClick={() => handleInteract()}
                  >
                    <Droplets size={16} />
                    <span>灵池调息（回复气血并驱散墓煞）</span>
                  </button>
                )}

                {!currentTile.cleared && currentTile.type === 'boss' && (
                  <button
                    type="button"
                    className="tomb-action-btn boss-btn"
                    disabled={busy || readOnly}
                    onClick={() => handleInteract()}
                  >
                    <Skull size={16} />
                    <span>决战主墓道尊法相</span>
                  </button>
                )}

                {currentTile.cleared &&
                  currentTile.type === 'boss' &&
                  tomb.depth < tomb.max_depth && (
                    <button
                      type="button"
                      className="tomb-action-btn descend-btn"
                      disabled={busy || readOnly}
                      onClick={() => handleInteract('下层')}
                    >
                      <ArrowDown size={16} />
                      <span>踏入虚空阵通往第 {tomb.depth + 1} 层</span>
                    </button>
                  )}
              </div>
            </div>
          ) : (
            <div className="chamber-empty">正在探寻石室灵机...</div>
          )}

          {/* 罗盘方向控制舵 */}
          <div className="tomb-nav-control">
            <span className="nav-title">移动探索：</span>
            <div className="nav-pad">
              <button
                type="button"
                className="nav-btn up"
                disabled={tomb.player_y <= 0 || busy || readOnly}
                onClick={() => handleMove('上')}
                title="向北移动"
              >
                <ArrowUp size={16} />
              </button>
              <div className="nav-row-middle">
                <button
                  type="button"
                  className="nav-btn left"
                  disabled={tomb.player_x <= 0 || busy || readOnly}
                  onClick={() => handleMove('左')}
                  title="向西移动"
                >
                  <ArrowLeft size={16} />
                </button>
                <span className="nav-center-dot">·</span>
                <button
                  type="button"
                  className="nav-btn right"
                  disabled={tomb.player_x >= 4 || busy || readOnly}
                  onClick={() => handleMove('右')}
                  title="向东移动"
                >
                  <ArrowRight size={16} />
                </button>
              </div>
              <button
                type="button"
                className="nav-btn down"
                disabled={tomb.player_y >= 4 || busy || readOnly}
                onClick={() => handleMove('下')}
                title="向南移动"
              >
                <ArrowDown size={16} />
              </button>
            </div>
          </div>

          {/* 实时地宫纪事 */}
          <div className="tomb-log-stream">
            <span className="log-title">地宫实时感应：</span>
            <div className="log-content">
              {(tomb.log || []).slice(-4).map((entry, idx) => (
                <p key={idx}>{entry}</p>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export function AncientTombModal({
  open,
  onOpenChange,
  ancientTomb,
  busy = false,
  readOnly = false,
  onAction,
}: AncientTombModalProps) {
  const tomb = ancientTomb?.current_tomb
  const themes = ancientTomb?.themes || []
  const history = ancientTomb?.history || []
  const isExploring = Boolean(tomb && tomb.grid && tomb.grid.length > 0)

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay tomb-dialog-overlay" />
        <Dialog.Content
          className="dialog-content tomb-modal-content"
          aria-describedby="tomb-modal-desc"
        >
          <header className="tomb-modal-header">
            <div className="tomb-header-left">
              <span className="tomb-category-badge">
                <Compass size={14} />
                <span>太古遗冢 · 迷雾地宫</span>
              </span>
              <Dialog.Title className="tomb-modal-title">
                {isExploring && tomb ? tomb.name : '太古大能秘境古墓'}
              </Dialog.Title>
            </div>
            <Dialog.Close asChild>
              <button type="button" className="close-btn tomb-close-btn" aria-label="关闭">
                <X size={18} />
              </button>
            </Dialog.Close>
          </header>

          <p id="tomb-modal-desc" className="sr-only">
            太古大能秘境古墓探索：走格子探索迷雾石室、破解太古机关、击溃守陵凶灵并争夺至宝。
          </p>

          {!isExploring || !tomb ? (
            <TombThemesView
              themes={themes}
              history={history}
              busy={busy}
              readOnly={readOnly}
              onAction={onAction}
            />
          ) : (
            <TombExplorerView
              tomb={tomb}
              busy={busy}
              readOnly={readOnly}
              onAction={onAction}
            />
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
