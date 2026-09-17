import * as Dialog from '@radix-ui/react-dialog'
import {
  Award,
  Castle,
  Compass,
  Crown,
  Gift,
  MessageCircle,
  ScrollText,
  Sparkles,
  Swords,
  Trophy,
  X,
  Zap,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import type { TianjiSnapshot } from '../api/types'

export interface TianjiRankModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tianji?: TianjiSnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
  onOpenNpc?: (npcName: string) => void
}

export function TianjiRankModal({
  open,
  onOpenChange,
  tianji,
  busy,
  readOnly = false,
  onAction,
  onOpenNpc,
}: TianjiRankModalProps) {
  const [activeTab, setActiveTab] = useState<'prodigies' | 'overlords' | 'sects' | 'treasures'>('prodigies')

  const prodigies = useMemo(() => tianji?.prodigies || [], [tianji])
  const overlords = useMemo(() => tianji?.overlords || [], [tianji])
  const sects = useMemo(() => tianji?.sects || [], [tianji])
  const treasures = useMemo(() => tianji?.treasures || [], [tianji])
  const news = useMemo(() => tianji?.news || [], [tianji])

  const playerRank = tianji?.player_rank ?? '—'
  const playerPower = tianji?.player_power ?? '—'
  const tokens = tianji?.tokens ?? 0

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-backdrop" />
        <Dialog.Content
          className="tianji-rank-modal dialog-content"
          aria-label="天机阁百晓风云谱"
        >
          {/* 水墨宣纸质感暗纹与朱砂印鉴 */}
          <div className="tianji-modal-wrapper">
            {/* 顶栏卷轴抬头 */}
            <header className="tianji-modal-header">
              <div className="tianji-header-seal">
                <span className="ink-seal">天机</span>
              </div>
              <div className="tianji-header-titles">
                <div className="tianji-header-badge">
                  <ScrollText size={13} />
                  <span>天机通天鉴 · 九州三千界</span>
                </div>
                <h2>天机百晓风云谱</h2>
                <p>监察天下气运造化，勘定九州天骄巨擘座次，录尽风云变幻</p>
              </div>
              <button
                type="button"
                className="tianji-close-btn"
                onClick={() => onOpenChange(false)}
                aria-label="闭合卷轴"
                title="闭合卷轴"
              >
                <X size={18} />
              </button>
            </header>

            {/* 玩家当前排位高光指示台 */}
            <section className="tianji-player-banner" aria-label="玩家排位总览">
              <div className="banner-item rank-item">
                <div className="banner-icon">
                  <Crown size={16} />
                </div>
                <div>
                  <small>潜龙榜座次</small>
                  <strong>第 {playerRank} 位</strong>
                </div>
              </div>
              <div className="banner-item power-item">
                <div className="banner-icon">
                  <Zap size={16} />
                </div>
                <div>
                  <small>综合战力指数</small>
                  <strong>{playerPower}</strong>
                </div>
              </div>
              <div className="banner-item token-item">
                <div className="banner-icon">
                  <Award size={16} />
                </div>
                <div>
                  <small>持有天机令</small>
                  <strong>{tokens} 枚</strong>
                </div>
              </div>
              {news.length > 0 && (
                <div className="tianji-news-ticker" title={news[0]}>
                  <Sparkles size={13} />
                  <span>{news[0]}</span>
                </div>
              )}
            </section>

            {/* 榜单导航切换卡 */}
            <nav className="tianji-tab-nav" aria-label="榜单分类">
              <button
                type="button"
                className={`tianji-tab-btn ${activeTab === 'prodigies' ? 'active' : ''}`}
                onClick={() => setActiveTab('prodigies')}
              >
                <Trophy size={14} />
                <span>青云潜龙榜</span>
                <small>年轻天骄</small>
              </button>
              <button
                type="button"
                className={`tianji-tab-btn ${activeTab === 'overlords' ? 'active' : ''}`}
                onClick={() => setActiveTab('overlords')}
              >
                <Crown size={14} />
                <span>九天巨擘榜</span>
                <small>大能通天</small>
              </button>
              <button
                type="button"
                className={`tianji-tab-btn ${activeTab === 'sects' ? 'active' : ''}`}
                onClick={() => setActiveTab('sects')}
              >
                <Castle size={14} />
                <span>九州宗门榜</span>
                <small>名门气运</small>
              </button>
              <button
                type="button"
                className={`tianji-tab-btn ${activeTab === 'treasures' ? 'active' : ''}`}
                onClick={() => setActiveTab('treasures')}
              >
                <Gift size={14} />
                <span>天机宝阁</span>
                <small>令牌兑换</small>
              </button>
            </nav>

            {/* 榜单内容主舞台 */}
            <main className="tianji-modal-body">
              {/* 1. 青云潜龙榜 */}
              {activeTab === 'prodigies' && (
                <div className="tianji-prodigy-list" role="list">
                  {prodigies.map((p) => {
                    const isTop1 = p.rank === 1
                    const isTop2 = p.rank === 2
                    const isTop3 = p.rank === 3
                    const rankClass = isTop1 ? 'gold' : isTop2 ? 'silver' : isTop3 ? 'bronze' : 'normal'
                    return (
                      <article
                        key={p.id}
                        className={`prodigy-card ${p.is_player ? 'is-player' : ''} rank-${rankClass}`}
                        role="listitem"
                      >
                        {/* 名次标识 */}
                        <div className={`prodigy-rank-badge ${rankClass}`}>
                          {isTop1 ? (
                            <span>魁首</span>
                          ) : isTop2 ? (
                            <span>榜眼</span>
                          ) : isTop3 ? (
                            <span>探花</span>
                          ) : (
                            <span>#{p.rank}</span>
                          )}
                        </div>

                        {/* 天骄主体信息 */}
                        <div className="prodigy-main-info">
                          <div className="prodigy-name-row">
                            <h3 className="prodigy-name">
                              {p.name}
                              {p.is_player && <span className="player-tag">★ 本人</span>}
                            </h3>
                            <span className="prodigy-dao">【{p.dao_name}】</span>
                            <span className="prodigy-realm-tag">{p.realm}</span>
                            <span className="prodigy-sect-tag">{p.sect} · {p.province}</span>
                          </div>

                          <div className="prodigy-title-row">
                            <strong>{p.title}</strong>
                            <em>绝学：{p.specialty}</em>
                          </div>

                          <p className="prodigy-desc">{p.description}</p>
                        </div>

                        {/* 战力指数与行动交互 */}
                        <div className="prodigy-action-side">
                          <div className="prodigy-power-stat">
                            <small>战力估测</small>
                            <strong>{p.power}</strong>
                          </div>

                          <div className="prodigy-btns">
                            {/* 如果是已知 NPC 且提供结交回调 */}
                            {p.is_npc && onOpenNpc && (
                              <button
                                type="button"
                                className="tianji-btn talk-btn"
                                title={`与【${p.name}】促膝长谈`}
                                onClick={() => {
                                  onOpenChange(false)
                                  onOpenNpc(p.npc_name)
                                }}
                              >
                                <MessageCircle size={12} />
                                <span>同道结缘</span>
                              </button>
                            )}

                            {/* 问剑挑战按钮 */}
                            {!p.is_player && (
                              <button
                                type="button"
                                className="tianji-btn challenge-btn"
                                disabled={busy || readOnly || !p.can_challenge}
                                title={
                                  readOnly
                                    ? '巡览只读'
                                    : !p.can_challenge
                                    ? '仅可向相近座次天骄发起问剑'
                                    : `向【${p.name}】发起登榜问剑`
                                }
                                onClick={() => onAction(p.challenge_action)}
                              >
                                <Swords size={12} />
                                <span>登榜问剑</span>
                              </button>
                            )}
                          </div>
                        </div>
                      </article>
                    )
                  })}
                </div>
              )}

              {/* 2. 九天巨擘榜 */}
              {activeTab === 'overlords' && (
                <div className="tianji-overlord-list" role="list">
                  {overlords.map((o) => (
                    <article key={o.rank} className="overlord-card" role="listitem">
                      <div className="overlord-rank-box">
                        <Crown size={18} />
                        <span>#{o.rank}</span>
                      </div>
                      <div className="overlord-info">
                        <div className="overlord-head">
                          <h3>{o.name}</h3>
                          <span className="overlord-dao">道号【{o.dao_name}】</span>
                          <span className="overlord-realm">{o.realm}</span>
                          <span className="overlord-sect">{o.sect}</span>
                        </div>
                        <h4 className="overlord-title">{o.title}</h4>
                        <p className="overlord-legend">{o.legend}</p>
                      </div>
                      <div className="overlord-power">
                        <small>大能灵压</small>
                        <strong>{o.power}</strong>
                      </div>
                    </article>
                  ))}
                </div>
              )}

              {/* 3. 九州宗门榜 */}
              {activeTab === 'sects' && (
                <div className="tianji-sect-list" role="list">
                  {sects.map((s) => (
                    <article key={s.rank} className="tianji-sect-card" role="listitem">
                      <div className="sect-rank-marker">
                        <Castle size={16} />
                        <span>#{s.rank}</span>
                      </div>
                      <div className="sect-info">
                        <div className="sect-title-bar">
                          <h3>{s.name}</h3>
                          <span className="sect-loc">{s.province}</span>
                          <span className={`sect-trend trend-${s.trend}`}>{s.trend}</span>
                        </div>
                        <p className="sect-doctrine">{s.doctrine}</p>
                        <small className="sect-leader">掌门教主：{s.leader}</small>
                      </div>
                      <div className="sect-prestige-box">
                        <small>宗门气运威望</small>
                        <strong>{s.prestige}</strong>
                      </div>
                    </article>
                  ))}
                </div>
              )}

              {/* 4. 天机宝阁 */}
              {activeTab === 'treasures' && (
                <div className="tianji-treasure-grid" role="list">
                  {treasures.map((t) => (
                    <article key={t.id} className="treasure-card" role="listitem">
                      <div className="treasure-head">
                        <span className="treasure-badge">{t.category}</span>
                        <h3>{t.name}</h3>
                        <span className="token-cost">
                          <Award size={13} />
                          <strong>{t.token_cost}</strong> 令
                        </span>
                      </div>
                      <p className="treasure-effect">{t.effect}</p>
                      <small className="treasure-summary">{t.summary}</small>
                      <button
                        type="button"
                        className="redeem-btn"
                        disabled={busy || readOnly || !t.affordable}
                        title={
                          readOnly
                            ? '巡览只读'
                            : !t.affordable
                            ? '天机令不足'
                            : `消耗 ${t.token_cost} 枚天机令兑换【${t.name}】`
                        }
                        onClick={() => onAction(t.action)}
                      >
                        <Gift size={13} />
                        <span>{t.affordable ? '启封兑换' : '令符不足'}</span>
                      </button>
                    </article>
                  ))}
                </div>
              )}
            </main>

            {/* 卷轴底栏通告 */}
            <footer className="tianji-modal-footer">
              <p>
                <Compass size={13} />
                天机风云谱每月由天机阁阴阳鉴动态勘定，挑战名次即刻名动神州，斩获天机令可启封万象秘宝。
              </p>
            </footer>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
