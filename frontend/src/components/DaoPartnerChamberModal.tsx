import { useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import {
  Baby,
  BookHeart,
  Crown,
  Flame,
  Heart,
  HeartHandshake,
  MessageCircle,
  MessageSquare,
  Send,
  Shield,
  Sparkles,
  Swords,
  X,
  Zap,
} from 'lucide-react'
import type { DaoPartnerSystemSnapshot } from '../api/types'
import { NpcAvatar } from './NpcAvatar'

export interface DaoPartnerChamberModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  partnerSystem?: DaoPartnerSystemSnapshot | null
  busy?: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

const PRESET_MESSAGES = [
  '道友近日安好？心印微温，甚是念卿。',
  '九州风云变幻，道友在外历练切记顾全自身。',
  '山间灵茶新采，待此番闭关出关，愿与君共品。',
  '修行路漫漫，幸得卿心常伴，此生道途不孤。',
]

export function DaoPartnerChamberModal({
  open,
  onOpenChange,
  partnerSystem,
  busy = false,
  readOnly = false,
  onAction,
}: DaoPartnerChamberModalProps) {
  const [tab, setTab] = useState<'chamber' | 'transmission' | 'lineage'>('chamber')
  const [selectedPartnerIndex, setSelectedPartnerIndex] = useState(0)
  const [customMessage, setCustomMessage] = useState('')

  const partners = partnerSystem?.partners || []
  const hasPartners = partners.length > 0
  const currentPartner = partners[selectedPartnerIndex] || partners[0]
  const children = partnerSystem?.children || []
  const messages = (partnerSystem?.messages || []).filter(
    (m) => !currentPartner || m.partner === currentPartner.name
  )

  const handleDualCultivate = () => {
    if (!currentPartner || busy || readOnly) return
    onAction(`仙侣同修 ${currentPartner.name}`)
  }

  const handleSendMessage = (textToSend?: string) => {
    if (!currentPartner || busy || readOnly) return
    const msg = textToSend ?? customMessage.trim()
    onAction(`传音 ${currentPartner.name} ${msg}`)
    setCustomMessage('')
  }

  const handleConceive = () => {
    if (!currentPartner || busy || readOnly) return
    onAction(`孕育仙胎 ${currentPartner.name}`)
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay partner-chamber-overlay" />
        <Dialog.Content
          className="dialog-content partner-chamber-content"
          aria-describedby="partner-chamber-desc"
        >
          <header className="partner-chamber-header">
            <div className="partner-header-left">
              <span className="partner-category-badge">
                <HeartHandshake size={14} />
                <span>阴阳合道 · 本命心印</span>
              </span>
              <Dialog.Title className="partner-modal-title">
                仙侣同修阁
              </Dialog.Title>
            </div>
            <Dialog.Close asChild>
              <button type="button" className="close-btn partner-close-btn" aria-label="关闭">
                <X size={18} />
              </button>
            </Dialog.Close>
          </header>

          <p id="partner-chamber-desc" className="sr-only">
            仙侣同修静室，进行阴阳合修、凝结专属合道法印、心印传音与仙家子嗣培育。
          </p>

          {!hasPartners ? (
            <div className="partner-empty-state">
              <BookHeart size={48} className="partner-empty-icon" />
              <h3>红尘孤身 · 尚待知己</h3>
              <p>
                你当前尚未与任何红颜知己或至交好友结下道侣之契。
                <br />
                在【情缘】中赠礼论道，将心仪人物的好感提升至 <strong>80 点</strong> 以上，即可结为道侣共攀长生。
              </p>
              <div className="partner-empty-actions">
                <button
                  type="button"
                  className="action-btn partner-cta-btn"
                  onClick={() => {
                    onAction('情缘')
                    onOpenChange(false)
                  }}
                >
                  <Heart size={15} />
                  <span>寻访红颜知己</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="partner-chamber-body">
              {/* 顶部标签切换与道侣选择器 */}
              <div className="partner-top-bar">
                <div className="partner-tabs">
                  <button
                    type="button"
                    className={`partner-tab-btn ${tab === 'chamber' ? 'active' : ''}`}
                    onClick={() => setTab('chamber')}
                  >
                    <Sparkles size={14} />
                    <span>合修静室</span>
                  </button>
                  <button
                    type="button"
                    className={`partner-tab-btn ${tab === 'transmission' ? 'active' : ''}`}
                    onClick={() => setTab('transmission')}
                  >
                    <MessageCircle size={14} />
                    <span>心印传音</span>
                  </button>
                  <button
                    type="button"
                    className={`partner-tab-btn ${tab === 'lineage' ? 'active' : ''}`}
                    onClick={() => setTab('lineage')}
                  >
                    <Baby size={14} />
                    <span>仙家子嗣 ({children.length})</span>
                  </button>
                </div>

                {partners.length > 1 && (
                  <div className="partner-selector">
                    <span>当前伴侣：</span>
                    {partners.map((p, idx) => (
                      <button
                        key={p.name}
                        type="button"
                        className={`partner-pill-btn ${idx === selectedPartnerIndex ? 'active' : ''}`}
                        onClick={() => setSelectedPartnerIndex(idx)}
                      >
                        {p.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* 选项卡 1：合修静室 */}
              {tab === 'chamber' && currentPartner && (
                <div className="partner-chamber-grid">
                  {/* 左侧：道侣 2D 立绘秀台 */}
                  <div className="partner-portrait-showcase">
                    <div className="partner-avatar-frame">
                      <NpcAvatar
                        item={{
                          name: currentPartner.name,
                          identity: '结契道侣',
                          realm: '同修至交',
                        }}
                        size="vn"
                        className="partner-avatar-img"
                      />
                      <div className="partner-affinity-ribbon">
                        <Heart size={13} className="text-rose-400 fill-rose-400" />
                        <span>羁绊好感 {currentPartner.affinity}</span>
                      </div>
                    </div>
                    <div className="partner-stats-strip">
                      <div className="strip-item">
                        <span className="strip-label">合修周天</span>
                        <strong className="strip-val">{currentPartner.dual_count} 次</strong>
                      </div>
                      <div className="strip-item">
                        <span className="strip-label">本命心印</span>
                        <strong className="strip-val text-emerald-400">已灵通</strong>
                      </div>
                      <div className="strip-item">
                        <span className="strip-label">子嗣造化</span>
                        <strong
                          className={`strip-val ${
                            currentPartner.can_conceive ? 'text-amber-300' : 'text-zinc-400'
                          }`}
                        >
                          {currentPartner.can_conceive ? '机缘已至' : '蓄积中'}
                        </strong>
                      </div>
                    </div>
                  </div>

                  {/* 右侧：法印卡片与合修操作 */}
                  <div className="partner-blessing-dock">
                    <div className="blessing-card">
                      <div className="blessing-card-header">
                        <div className="blessing-title-group">
                          <Crown size={16} className="text-amber-400" />
                          <h4 className="blessing-name">
                            {currentPartner.preset_blessing.name}
                          </h4>
                          <span className="blessing-origin-tag">
                            {currentPartner.name} 专属合道法印
                          </span>
                        </div>
                        {currentPartner.active_blessing ? (
                          <span className="blessing-active-pill">
                            生效中 · 余 {currentPartner.active_blessing.remaining_months} 月
                          </span>
                        ) : (
                          <span className="blessing-inactive-pill">尚未凝结</span>
                        )}
                      </div>

                      <p className="blessing-desc">
                        {currentPartner.preset_blessing.description}
                      </p>

                      <div className="blessing-perks-grid">
                        {currentPartner.preset_blessing.attack_multiplier &&
                          currentPartner.preset_blessing.attack_multiplier > 1.0 && (
                            <div className="blessing-perk-badge perk-attack">
                              <Swords size={13} />
                              <span>
                                全伤提升 +
                                {Math.round(
                                  (currentPartner.preset_blessing.attack_multiplier - 1.0) * 100
                                )}
                                %
                              </span>
                            </div>
                          )}
                        {currentPartner.preset_blessing.defense_bonus &&
                          currentPartner.preset_blessing.defense_bonus > 0 && (
                            <div className="blessing-perk-badge perk-def">
                              <Shield size={13} />
                              <span>
                                受创减免 +{currentPartner.preset_blessing.defense_bonus} 点
                              </span>
                            </div>
                          )}
                        {currentPartner.preset_blessing.lifesteal_percent &&
                          currentPartner.preset_blessing.lifesteal_percent > 0 && (
                            <div className="blessing-perk-badge perk-leech">
                              <Zap size={13} />
                              <span>
                                伤害吸血 +
                                {Math.round(
                                  currentPartner.preset_blessing.lifesteal_percent * 100
                                )}
                                %
                              </span>
                            </div>
                          )}
                        {currentPartner.preset_blessing.stone_multiplier &&
                          currentPartner.preset_blessing.stone_multiplier > 1.0 && (
                            <div className="blessing-perk-badge perk-wealth">
                              <Flame size={13} />
                              <span>
                                探索灵石 +
                                {Math.round(
                                  (currentPartner.preset_blessing.stone_multiplier - 1.0) * 100
                                )}
                                %
                              </span>
                            </div>
                          )}
                      </div>
                    </div>

                    <div className="chamber-action-controls">
                      <button
                        type="button"
                        className="chamber-primary-btn"
                        disabled={busy || readOnly}
                        onClick={handleDualCultivate}
                      >
                        <Sparkles size={16} />
                        <div>
                          <strong>阴阳性命合修一月</strong>
                          <small>气血灵力全复 · 修为激增 · 刷新【{currentPartner.preset_blessing.name}】</small>
                        </div>
                      </button>

                      <div className="chamber-secondary-actions">
                        <button
                          type="button"
                          className="chamber-sub-btn conceive-btn"
                          disabled={!currentPartner.can_conceive || busy || readOnly}
                          onClick={handleConceive}
                          title={
                            currentPartner.can_conceive
                              ? '天降祥瑞，诞育身具双方至强血脉的仙苗'
                              : '需彼此好感达 100 且合修满 3 次方可孕育'
                          }
                        >
                          <Baby size={15} />
                          <span>
                            {currentPartner.can_conceive
                              ? '孕育仙家麟儿'
                              : '孕育条件未足 (好感100 & 合修3次)'}
                          </span>
                        </button>
                        <button
                          type="button"
                          className="chamber-sub-btn trial-btn"
                          disabled={busy || readOnly}
                          onClick={() => onAction('情劫')}
                          title="若尘缘过重引发心魔情劫，可入定斩破心魔"
                        >
                          <Swords size={15} />
                          <span>叩问心魔情劫</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 选项卡 2：心印传音 */}
              {tab === 'transmission' && currentPartner && (
                <div className="partner-transmission-layout">
                  <div className="transmission-chat-history">
                    {messages.length === 0 ? (
                      <div className="transmission-empty">
                        <MessageSquare size={32} className="text-zinc-500" />
                        <p>尚无往来传音，发一道心印传信向道侣问好吧。</p>
                      </div>
                    ) : (
                      messages.map((msg, i) => (
                        <div key={i} className="transmission-exchange">
                          <div className="msg-bubble user-bubble">
                            <span className="msg-sender">你传音道：</span>
                            <p className="msg-text">“{msg.user_text}”</p>
                          </div>
                          <div className="msg-bubble partner-bubble">
                            <span className="msg-sender">{msg.partner} 心印回响：</span>
                            <p className="msg-text">“{msg.reply}”</p>
                            {(msg.gift_item || msg.gift_stones) && (
                              <div className="msg-gift-tag">
                                <span>随信奉赠：</span>
                                {msg.gift_item && (
                                  <strong>
                                    【{msg.gift_item}】×{msg.gift_count || 1}{' '}
                                  </strong>
                                )}
                                {msg.gift_stones ? <strong>灵石 +{msg.gift_stones}</strong> : null}
                              </div>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  <div className="transmission-preset-pills">
                    <span className="preset-label">心念寄语：</span>
                    {PRESET_MESSAGES.map((preset, idx) => (
                      <button
                        key={idx}
                        type="button"
                        className="preset-msg-pill"
                        disabled={busy || readOnly}
                        onClick={() => handleSendMessage(preset)}
                      >
                        {preset}
                      </button>
                    ))}
                  </div>

                  <div className="transmission-input-bar">
                    <input
                      type="text"
                      className="transmission-input"
                      placeholder="亦可在此抒写心印传音之语..."
                      value={customMessage}
                      onChange={(e) => setCustomMessage(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSendMessage()
                      }}
                      disabled={busy || readOnly}
                    />
                    <button
                      type="button"
                      className="transmission-send-btn"
                      disabled={busy || readOnly}
                      onClick={() => handleSendMessage()}
                    >
                      <Send size={15} />
                      <span>发放心印</span>
                    </button>
                  </div>
                </div>
              )}

              {/* 选项卡 3：仙家子嗣 */}
              {tab === 'lineage' && (
                <div className="partner-lineage-layout">
                  {children.length === 0 ? (
                    <div className="lineage-empty-box">
                      <Baby size={40} className="text-zinc-500" />
                      <h4>仙家谱牒 · 暂无子嗣</h4>
                      <p>
                        修仙之人夺天地造化，若与道侣情深意笃（好感达 100 且合修 3 次以上），
                        可在合修静室【孕育仙胎】。
                        <br />
                        子嗣将继承二人的天灵根与稀世体质，随岁月年满十六筑基后，外出历练常会带回天材地宝回报双亲！
                      </p>
                    </div>
                  ) : (
                    <div className="lineage-cards-grid">
                      {children.map((c) => (
                        <div key={c.id} className="lineage-card">
                          <div className="lineage-card-header">
                            <div className="lineage-child-name-row">
                              <h4 className="child-name">{c.name}</h4>
                              <span className="child-gender-tag">{c.gender}</span>
                              <span className="child-partner-tag">双亲：你与【{c.partner}】</span>
                            </div>
                            <span className="child-stage-pill">{c.stage}</span>
                          </div>

                          <div className="lineage-traits-row">
                            <div className="trait-item">
                              <span className="trait-key">寿数年龄</span>
                              <strong className="trait-val">{c.age} 岁</strong>
                            </div>
                            <div className="trait-item">
                              <span className="trait-key">当前修为</span>
                              <strong className="trait-val text-amber-300">{c.realm}</strong>
                            </div>
                            <div className="trait-item">
                              <span className="trait-key">天命灵根</span>
                              <strong className="trait-val text-cyan-300">
                                {c.spiritual_root}
                              </strong>
                            </div>
                            <div className="trait-item">
                              <span className="trait-key">太古体魄</span>
                              <strong className="trait-val text-emerald-300">
                                {c.constitution}
                              </strong>
                            </div>
                          </div>

                          <div className="lineage-foot-note">
                            {c.age >= 16 ? (
                              <span className="text-emerald-400">
                                已达筑基，游历各州寻觅机缘，年节孝奉天材地宝。
                              </span>
                            ) : (
                              <span className="text-zinc-400">
                                尚在吐纳修持，待十六岁筑基可出师历练九州。
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
