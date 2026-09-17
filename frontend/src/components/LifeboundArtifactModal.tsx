import * as Dialog from '@radix-ui/react-dialog'
import {
  Anvil,
  Coins,
  Compass,
  Flame,
  Gem,
  MessageSquare,
  Shield,
  Sparkles,
  Swords,
  X,
  Zap,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import type { ArtifactGrowthSnapshot } from '../api/types'

export interface LifeboundArtifactModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  artifacts?: ArtifactGrowthSnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

export function LifeboundArtifactModal({
  open,
  onOpenChange,
  artifacts,
  busy,
  readOnly = false,
  onAction,
}: LifeboundArtifactModalProps) {
  const [activeTab, setActiveTab] = useState<'inscriptions' | 'infusion' | 'spirit' | 'all'>('inscriptions')

  const bonded = useMemo(() => {
    if (!artifacts) return null
    return (artifacts.artifacts || []).find((a) => a.bonded) || null
  }, [artifacts])

  const allArtifacts = useMemo(() => artifacts?.artifacts || [], [artifacts])
  const allInscriptions = useMemo(() => artifacts?.all_inscriptions || [], [artifacts])
  const infusableMaterials = useMemo(() => artifacts?.infusable_materials || [], [artifacts])
  const materials = useMemo(
    () => artifacts?.materials || { spirit_stones: 0, spirit: 0, spirit_max: 0, spirit_iron: 0, beast_materials: 0 },
    [artifacts]
  )

  const bondedInscriptions = bonded?.inscriptions || []
  const maxSlots = bonded?.max_slots || 2
  const resonance = bonded?.resonance || 0

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-backdrop" />
        <Dialog.Content
          className="lifebound-modal dialog-content"
          aria-label="本命灵宝阁"
        >
          <div className="lifebound-wrapper">
            {/* 顶栏卷轴抬头 */}
            <header className="lifebound-header">
              <div className="lifebound-seal">
                <span className="ink-seal">本命</span>
              </div>
              <div className="lifebound-titles">
                <div className="lifebound-badge">
                  <Sparkles size={13} />
                  <span>丹田气海 · 灵枢温养</span>
                </div>
                <h2>本命灵宝阁 · 九重器纹</h2>
                <p>性命交修，以神魂精血化育无上法宝；铭太古九重器纹，御剑破空显圣护道</p>
              </div>
              <button
                type="button"
                className="lifebound-close-btn"
                onClick={() => onOpenChange(false)}
                aria-label="收回神识"
                title="收回神识"
              >
                <X size={18} />
              </button>
            </header>

            {/* 灵宝总览指示条 */}
            <section className="lifebound-banner" aria-label="本命法宝总览">
              <div className="banner-stat bonded-stat">
                <div className="stat-icon">
                  {bonded?.slot === '武器' ? <Swords size={16} /> : <Shield size={16} />}
                </div>
                <div>
                  <small>当前本命</small>
                  <strong>{bonded ? `${bonded.name}（${bonded.level_label}）` : '器心待定'}</strong>
                </div>
              </div>

              <div className="banner-stat resonance-stat">
                <div className="stat-icon">
                  <Sparkles size={16} />
                </div>
                <div>
                  <small>器心契合</small>
                  <strong>{resonance} / 100</strong>
                </div>
              </div>

              <div className="banner-stat slot-stat">
                <div className="stat-icon">
                  <Gem size={16} />
                </div>
                <div>
                  <small>器纹槽位</small>
                  <strong>{bondedInscriptions.length} / {maxSlots} 孔</strong>
                </div>
              </div>

              <div className="banner-resources">
                <span><Coins size={12} /> {materials.spirit_stones} 灵石</span>
                <span><Zap size={12} /> {materials.spirit}/{materials.spirit_max} 灵力</span>
                <span><Anvil size={12} /> 灵铁 {materials.spirit_iron}</span>
              </div>
            </section>

            {/* 分类标签 */}
            <nav className="lifebound-nav" aria-label="灵宝功能分类">
              <button
                type="button"
                className={`lifebound-tab ${activeTab === 'inscriptions' ? 'active' : ''}`}
                onClick={() => setActiveTab('inscriptions')}
              >
                <Gem size={14} />
                <span>九重器纹</span>
              </button>
              <button
                type="button"
                className={`lifebound-tab ${activeTab === 'infusion' ? 'active' : ''}`}
                onClick={() => setActiveTab('infusion')}
              >
                <Flame size={14} />
                <span>神料熔铸</span>
              </button>
              <button
                type="button"
                className={`lifebound-tab ${activeTab === 'spirit' ? 'active' : ''}`}
                onClick={() => setActiveTab('spirit')}
              >
                <MessageSquare size={14} />
                <span>器灵通微</span>
              </button>
              <button
                type="button"
                className={`lifebound-tab ${activeTab === 'all' ? 'active' : ''}`}
                onClick={() => setActiveTab('all')}
              >
                <Anvil size={14} />
                <span>法宝囊匣 ({allArtifacts.length})</span>
              </button>
            </nav>

            {/* 主舞台内容 */}
            <main className="lifebound-body">
              {/* 1. 器纹铭刻 */}
              {activeTab === 'inscriptions' && (
                <div className="tab-inscriptions">
                  {bonded ? (
                    <div className="inscriptions-layout">
                      {/* 左侧：法宝中央灵阵与槽位 */}
                      <section className="inscriptions-stage">
                        <div className="stage-card">
                          <div className="artifact-core">
                            <div className="core-avatar">
                              {bonded.slot === '武器' ? <Swords size={32} /> : <Shield size={32} />}
                            </div>
                            <h3>{bonded.name}</h3>
                            <span className="grade-badge">{bonded.grade} · {bonded.slot}</span>
                            <p className="effect-label">{bonded.effect}</p>
                          </div>

                          {/* 槽位展示 */}
                          <div className="slots-grid" aria-label="器纹槽位">
                            {Array.from({ length: maxSlots }).map((_, idx) => {
                              const inscrName = bondedInscriptions[idx]
                              const inscr = allInscriptions.find((i) => i.id === inscrName)
                              return (
                                <div
                                  key={idx}
                                  className={`slot-box ${inscrName ? 'filled' : 'empty'}`}
                                >
                                  <span className="slot-idx">#{idx + 1}</span>
                                  {inscr ? (
                                    <div className="slot-content">
                                      <strong>{inscr.name}</strong>
                                      <small>{inscr.effect_text}</small>
                                      {!readOnly && (
                                        <button
                                          type="button"
                                          className="wash-btn"
                                          disabled={busy}
                                          title={`消耗 50 灵石洗练洗去【${inscr.name}】`}
                                          onClick={() => onAction(`洗练器纹 ${bonded.name} ${inscr.id}`)}
                                        >
                                          洗练
                                        </button>
                                      )}
                                    </div>
                                  ) : (
                                    <div className="slot-empty">
                                      <span>虚位待刻</span>
                                    </div>
                                  )}
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      </section>

                      {/* 右侧：太古九重器纹图鉴与铭刻行动 */}
                      <section className="inscriptions-catalog">
                        <h3>太古九重器纹谱系</h3>
                        <div className="inscriptions-list" role="list">
                          {(bonded.available_inscriptions || []).map((item) => (
                            <article key={item.id} className={`inscr-card ${item.inscribed ? 'is-inscribed' : ''}`} role="listitem">
                              <div className="inscr-head">
                                <div className="inscr-name-wrap">
                                <h4>{item.name}</h4>
                                <span className="inscr-type">{item.slot_type}</span>
                                <span className="inscr-req">需{item.req_grade}</span>
                                </div>
                                <span className="inscr-effect">{item.effect_text}</span>
                              </div>
                              <p className="inscr-desc">{item.desc}</p>
                              <div className="inscr-foot">
                                <span className="inscr-cost">
                                  灵石 {item.cost_stones}
                                  {Object.entries(item.cost_materials).map(([m, c]) => ` · ${m}×${c}`)}
                                </span>
                                {item.inscribed ? (
                                  <span className="inscribed-tag">★ 已铭刻</span>
                                ) : (
                                  <button
                                    type="button"
                                    className="inscribe-btn"
                                    disabled={busy || readOnly || !item.can_inscribe}
                                    title={readOnly ? '巡览只读' : item.inscribe_reason || `铭刻【${item.name}】`}
                                    onClick={() => onAction(item.inscribe_action)}
                                  >
                                    <Gem size={12} />
                                    <span>{item.can_inscribe ? '铭刻器纹' : item.inscribe_reason || '条件未满'}</span>
                                  </button>
                                )}
                              </div>
                            </article>
                          ))}
                        </div>
                      </section>
                    </div>
                  ) : (
                    <div className="no-bonded-notice">
                      <Compass size={28} />
                      <p>尚未认主本命法宝。请前往【法宝囊匣】挑选一件已装备的法宝祭炼认主！</p>
                    </div>
                  )}
                </div>
              )}

              {/* 2. 神料熔铸 */}
              {activeTab === 'infusion' && (
                <div className="tab-infusion">
                  <div className="infusion-header">
                    <Flame size={18} />
                    <p>将采自名山大川的天地元晶、神铁玄料熔入本命法宝，激发法宝通玄潜能与器心共鸣。</p>
                  </div>
                  <div className="infusion-grid" role="list">
                    {infusableMaterials.map((mat) => (
                      <article key={mat.name} className="infuse-card" role="listitem">
                        <div className="mat-head">
                          <h4>{mat.name}</h4>
                          <span className="mat-count">持有：{mat.count}</span>
                        </div>
                        <p className="mat-desc">{mat.desc}</p>
                        <div className="mat-bonus">
                          <span>神威：{mat.bonus_text}</span>
                          <small>器心契合 +{mat.resonance_gain}</small>
                        </div>
                        <button
                          type="button"
                          className="infuse-action-btn"
                          disabled={busy || readOnly || !mat.can_infuse}
                          title={
                            readOnly
                              ? '巡览只读'
                              : !bonded
                              ? '请先认主本命法宝'
                              : mat.count <= 0
                              ? '囊中缺少此灵料'
                              : `消耗 1 个【${mat.name}】与 30 灵石熔铸入本命`
                          }
                          onClick={() => onAction(mat.infuse_action)}
                        >
                          <Flame size={13} />
                          <span>{mat.can_infuse ? '熔铸入胚' : mat.count <= 0 ? '灵料不足' : '不可熔铸'}</span>
                        </button>
                      </article>
                    ))}
                  </div>
                </div>
              )}

              {/* 3. 器灵通微 */}
              {activeTab === 'spirit' && (
                <div className="tab-spirit">
                  {bonded ? (
                    <div className="spirit-panel">
                      <div className="spirit-avatar-box">
                        <div className="spirit-icon-halo">
                          <Sparkles size={40} />
                        </div>
                        <h3>器灵法相 · {bonded.spirit_stage_label || '器心沉眠'}</h3>
                        <p className="spirit-dialogue-bubble">
                          “{bonded.spirit_dialogue || '法宝静默悬浮，静候真元温润...'}”
                        </p>
                      </div>

                      <div className="spirit-stages">
                        <h4>器灵蜕变四重境界</h4>
                        <div className="stages-list">
                          <div className={`stage-step ${(bonded.spirit_stage || 0) >= 1 ? 'achieved' : ''}`}>
                            <strong>第一重 · 初露灵光 (30)</strong>
                            <small>诞生微弱灵识，可感应器灵并恢复灵力</small>
                          </div>
                          <div className={`stage-step ${(bonded.spirit_stage || 0) >= 2 ? 'achieved' : ''}`}>
                            <strong>第二重 · 形意相依 (60)</strong>
                            <small>灵影化形，温养法宝灵力消耗减半</small>
                          </div>
                          <div className={`stage-step ${(bonded.spirit_stage || 0) >= 3 ? 'achieved' : ''}`}>
                            <strong>第三重 · 人器合一 (90)</strong>
                            <small>心意相通，攻势与防御神威倍增</small>
                          </div>
                          <div className={`stage-step ${(bonded.spirit_stage || 0) >= 4 ? 'achieved' : ''}`}>
                            <strong>第四重 · 真灵显圣 (100)</strong>
                            <small>真灵圆满化形，九州演武具象化护道</small>
                          </div>
                        </div>
                      </div>

                      <div className="spirit-actions">
                        <button
                          type="button"
                          className="spirit-commune-btn"
                          disabled={busy || readOnly}
                          onClick={() => onAction(bonded.spirit_commune_action || `器灵感应 ${bonded.name}`)}
                        >
                          <MessageSquare size={14} />
                          <span>器灵神识感应</span>
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="no-bonded-notice">
                      <Compass size={28} />
                      <p>尚未认主本命法宝，无法唤醒器灵。</p>
                    </div>
                  )}
                </div>
              )}

              {/* 4. 法宝总览 */}
              {activeTab === 'all' && (
                <div className="tab-all-artifacts">
                  <div className="artifacts-grid" role="list">
                    {allArtifacts.map((item) => (
                      <article key={item.name} className={`artifact-card ${item.bonded ? 'is-bonded' : ''}`} role="listitem">
                        <header className="art-header">
                          <span className="art-icon">{item.slot === '武器' ? <Swords size={16} /> : <Shield size={16} />}</span>
                          <div>
                            <h4>{item.name}</h4>
                            <small>{item.grade} · {item.slot} · {item.level_label}</small>
                          </div>
                          <span className={`bond-status ${item.bonded ? 'bonded' : item.equipped ? 'equipped' : 'stored'}`}>
                            {item.bonded ? '★ 本命' : item.equipped ? '已装备' : '袋中'}
                          </span>
                        </header>

                        <p className="art-effect">{item.effect}</p>
                        <div className="art-meta">
                          <span>器心契合：{item.resonance}/100</span>
                          <span>器纹：{(item.inscriptions || []).length}/{item.max_slots || 2} 孔</span>
                        </div>

                        <footer className="art-actions">
                          {!item.bonded && (
                            <button
                              type="button"
                              className="bind-btn"
                              disabled={busy || readOnly || !item.can_bind}
                              title={readOnly ? '巡览只读' : item.bind_reason || `将【${item.name}】祭为本命`}
                              onClick={() => onAction(item.bind_action)}
                            >
                              <Gem size={12} />
                              <span>{item.can_bind ? '祭为本命' : item.bind_reason || '不可认主'}</span>
                            </button>
                          )}
                          <button
                            type="button"
                            className="refine-btn"
                            disabled={busy || readOnly || !item.can_refine}
                            title={readOnly ? '巡览只读' : item.refine_reason || `淬炼【${item.name}】`}
                            onClick={() => onAction(item.refine_action)}
                          >
                            <Anvil size={12} />
                            <span>{item.can_refine ? '开炉淬炼' : item.refine_reason || '淬炼上限'}</span>
                          </button>
                          {item.bonded && (
                            <button
                              type="button"
                              className="nourish-btn"
                              disabled={busy || readOnly || !item.can_nourish}
                              title={readOnly ? '巡览只读' : item.nourish_reason || `温养【${item.name}】`}
                              onClick={() => onAction(item.nourish_action)}
                            >
                              <Sparkles size={12} />
                              <span>{item.can_nourish ? '温养器心' : item.nourish_reason || '器心已满'}</span>
                            </button>
                          )}
                        </footer>
                      </article>
                    ))}
                  </div>
                </div>
              )}
            </main>

            {/* 底栏说明 */}
            <footer className="lifebound-footer">
              <p>
                <Compass size={13} />
                本命法宝与修士性命相依。认主后随修士战历与温养逐步觉醒器灵；铭刻九重器纹将在实战与登榜演武中大放异彩。
              </p>
            </footer>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
