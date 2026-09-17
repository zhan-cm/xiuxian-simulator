import { useMemo, useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import {
  BookOpen,
  Gift,
  Heart,
  HeartHandshake,
  HeartPulse,
  MapPin,
  MessageCircleMore,
  ScrollText,
  ShieldCheck,
  Sparkles,
  Swords,
  X,
} from 'lucide-react'
import type { InventorySnapshot, NpcLifeProfile, NpcProfile } from '../api/types'
import { NpcAvatar, deduceNpcAppearance } from './NpcAvatar'

export const CHARACTER_DIALOGUES: Record<
  string,
  {
    greeting: string
    highAffinity: string
    partner: string
    discussDaoSuccess: string
    sparringPrompt: string
  }
> = {
  顾清玄: {
    greeting: '剑有锋芒，道心却不必处处伤人。道友远道而来，何妨与清玄共品一盏灵茶，再论剑意？',
    highAffinity: '自与道友印证剑道，清玄胸中窒碍尽去。他日同登九霄之巅，清玄愿与道友同进共退。',
    partner: '弱水三千，清玄唯愿与道友并肩仗剑，纵使万劫临身，青云剑下绝不负卿。',
    discussDaoSuccess: '道友方才那一言，真如当头棒喝！清玄受教了。',
    sparringPrompt: '点到为止，青云剑出三寸，道友请小心接招。',
  },
  白凝霜: {
    greeting: '北原风雪常年不息，极寒入骨。能踏过万载玄冰与我相逢者，唯道友一人。',
    highAffinity: '你身上……有这片终年冻土未曾见过的暖意。这枚雪髓灵晶，便赠予道友避煞吧。',
    partner: '冰肌玉骨本无情，直至遇见道友……自此之后，万载风雪，凝霜与你共度。',
    discussDaoSuccess: '玄冰亦有向阳之时，道友对阴阳相济的领悟，令我茅塞顿开。',
    sparringPrompt: '雪族玄法以寒制动，若有得罪之处，道友莫怪。',
  },
  云栖: {
    greeting: '哟，贵客临门！天机阁今日新到了不少九州天材地宝，道友随便瞧瞧，价格好商量~',
    highAffinity: '旁人来坊市皆为利往，唯有道友能懂我心中算筹。今晚天机阁后院设宴，可不许推脱！',
    partner: '我算尽了天下奇珍异宝的价码，唯独算不尽对道友的心意。从今往后，天机阁与我，皆归你管。',
    discussDaoSuccess: '商道亦是天道，道友对灵石气数的洞察，实在令云栖叹服！',
    sparringPrompt: '小女子可不擅长打打杀杀，道友可要懂得怜香惜玉才好~',
  },
  谢无咎: {
    greeting: '血海滔滔，仙门伪善。若无逆天改命的狠劲，便休要在本君面前空谈天道长生！',
    highAffinity: '哼，你倒有些胆色与真本事，合本君脾性！日后若有那些道貌岸然之徒找你麻烦，报我谢无咎的名号！',
    partner: '天下人皆视我为魔，唯你敢与我并肩入渊。既然结契，黄泉碧落，谁若伤你，本君灭他满门！',
    discussDaoSuccess: '好霸道的杀伐之道！以杀止杀，正合我血煞宗之意！',
    sparringPrompt: '本君出手从不留情，哪怕切磋，你也要做好见血的准备！',
  },
  墨尘: {
    greeting: '喂！古妖山可不是人修闲逛的花园。要打便痛快些，休要学仙门那些弯弯绕绕！',
    highAffinity: '哈哈哈！好身手！本少主认你这个知己！走，带你去妖祖圣窟掏九阶火凤蛋去！',
    partner: '古妖一族一生唯认定一侣。我墨尘既认定你，纵使十万大山祖灵反对，我也定护你周全！',
    discussDaoSuccess: '以肉身借天地造化之气……妙啊！人修里居然也有你这般通晓自然之辈！',
    sparringPrompt: '小心了！本少主的龙角可不长眼睛！',
  },
  洛浅浅: {
    greeting: '嘻……这位仙长生得好生俊俏，眼角眉梢皆合浅浅心意，莫不是特意来寻浅浅的？',
    highAffinity: '红尘三千丈，合欢铃响动凡心。浅浅阅人无数，却唯独在仙长面前，辨不清真心还是假意了呢~',
    partner: '情蛊入髓，神魂相系。仙长既要了浅浅的心，那生生世世的仙途，便休想甩开我了哦？',
    discussDaoSuccess: '春水生情，情入道骨……仙长一席话，让浅浅的合欢真气都欢跃起来了呢。',
    sparringPrompt: '仙长可要小心浅浅的摄魂彩缎，莫要在对决时丢了心神呢~',
  },
}

export function getAffinityRank(affinity: number, relation?: string): { label: string; tone: string; percent: number } {
  const safe = Math.max(0, Math.min(100, affinity))
  if (relation === '道侣') return { label: '倾心道侣 · 生死契阔', tone: 'partner', percent: safe }
  if (safe >= 80) return { label: '莫逆之交 · 心意相通', tone: 'exceptional', percent: safe }
  if (safe >= 60) return { label: '相知甚深 · 肝胆相照', tone: 'close', percent: safe }
  if (safe >= 40) return { label: '志趣相投 · 意气相合', tone: 'friendly', percent: safe }
  if (safe >= 20) return { label: '泛泛之交 · 萍水相逢', tone: 'acquaintance', percent: safe }
  return { label: '素未谋面 · 缘分初结', tone: 'stranger', percent: safe }
}

export interface VisualNovelDialogProps {
  npc?: NpcProfile | NpcLifeProfile
  inventory?: InventorySnapshot
  open: boolean
  readOnly?: boolean
  busy?: boolean
  onClose: () => void
  onAction: (action: string) => void
}

export function VisualNovelDialog({
  npc,
  inventory,
  open,
  readOnly = false,
  busy = false,
  onClose,
  onAction,
}: VisualNovelDialogProps) {
  const [activeTab, setActiveTab] = useState<'interact' | 'gifts' | 'bio'>('interact')
  const [lastActionFeedback, setLastActionFeedback] = useState('')

  const lifeProfile = npc as NpcLifeProfile | undefined
  const regularProfile = npc as NpcProfile | undefined

  const name = npc?.name || '同道修者'
  const identity = npc?.identity || '散修'
  const realm = npc?.realm || '练气·初期'
  const location = npc?.location || '九州某处'
  const alive = npc?.alive !== false
  const relation = npc?.relation || '缘分未定'
  const affinity = Number(npc?.affinity ?? 0)
  const likes = npc?.likes || []
  const dislikes = regularProfile?.dislikes || []

  const appearance = useMemo(() => deduceNpcAppearance(lifeProfile, npc), [lifeProfile, npc])
  const rank = useMemo(() => getAffinityRank(affinity, relation), [affinity, relation])

  // Contextual speech generation
  const activeDialogue = useMemo(() => {
    const known = CHARACTER_DIALOGUES[name]
    if (known) {
      if (relation === '道侣') return known.partner
      if (affinity >= 70) return known.highAffinity
      return known.greeting
    }
    if (regularProfile?.greeting) return regularProfile.greeting
    if (affinity >= 70) return '与道友相交至今，知君心性纯良高蹈，得友如此，仙途不孤。'
    if (affinity >= 40) return '道友今日神华内敛，气机越发精进，令人艳羡。'
    if (appearance.temperament === 'aloof') return '山路迢迢，仙尘有隔。不知道友叩关拜访，所为何求？'
    if (appearance.temperament === 'fierce') return '天下修者皆趋利，若无真意，休要多费唇舌。'
    return '浮生若梦，能在浩渺九州与道友相逢，自是一段仙缘。'
  }, [name, relation, affinity, regularProfile, appearance])

  // Filter gift items from inventory
  const giftItems = useMemo(() => {
    if (!inventory?.items) return []
    return inventory.items.filter((item) => item.category === '礼物' && item.count > 0)
  }, [inventory])

  if (!npc) return null

  const handleAct = (actionCommand: string, feedbackText?: string) => {
    if (feedbackText) setLastActionFeedback(feedbackText)
    onAction(actionCommand)
  }

  const isPartner = relation === '道侣'
  const canPropose = affinity >= 80 && !isPartner && alive
  const hasGuardRequest = Boolean(lifeProfile?.pending)

  return (
    <Dialog.Root open={open} onOpenChange={(val) => { if (!val) onClose() }}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay vn-dialog-overlay" />
        <Dialog.Content className="character-dialog vn-dialog" aria-describedby={`vn-desc-${name}`}>
          {/* 顶栏关闭与古典视窗装饰 */}
          <div className="vn-window-header">
            <span className="vn-scroll-tag">仙途会道 · 浮生相逢</span>
            <Dialog.Close asChild>
              <button type="button" className="vn-close-btn" aria-label="关闭会面案卷">
                <X size={18} />
              </button>
            </Dialog.Close>
          </div>

          <div className="vn-dialog-body">
            {/* 左侧：2D 动漫立绘舞台 */}
            <aside className="vn-stage" data-path={appearance.path} aria-label={`${name}立绘展示舞台`}>
              <div className="vn-stage-halo" aria-hidden="true" />
              <div className="vn-stage-portrait-wrapper">
                <NpcAvatar
                  profile={lifeProfile}
                  item={npc}
                  size="vn"
                  className="vn-stage-avatar"
                />
              </div>

              {/* 立绘下方气韵与相貌小卷 */}
              <div className="vn-stage-caption">
                <div className="vn-stage-tags">
                  <span className="vn-stage-path-badge">{appearance.archetypeLabel}</span>
                  <span className="vn-stage-temperament-badge">{appearance.temperamentLabel}</span>
                </div>
                <p className="vn-stage-summary">“{appearance.summary}”</p>
              </div>
            </aside>

            {/* 右侧：古典宣纸对谈案卷 */}
            <section className="vn-scroll" id={`vn-desc-${name}`}>
              {/* 1. 人物身份印记与好感机枢 */}
              <header className="vn-profile-header">
                <div className="vn-name-block">
                  <Dialog.Title className="vn-name-title">{name}</Dialog.Title>
                  <span className="vn-realm-badge">{realm}</span>
                  <span className="vn-identity-badge">{identity}</span>
                  <span className="vn-location-badge">
                    <MapPin size={12} />
                    {location}
                  </span>
                </div>

                {/* 所好速览 */}
                <div className="vn-preferences-preview" aria-label="性情所好">
                  <small>性情所好：</small>
                  {likes.length ? (
                    likes.map((like) => <span key={like} className="vn-chip like">{like}</span>)
                  ) : (
                    <span className="vn-chip muted">尚待相知</span>
                  )}
                </div>

                {/* 好感度条 */}
                <div className="vn-affinity-cluster" title={`当前好感度：${affinity}/100`}>
                  <div className="vn-affinity-labels">
                    <span className="vn-affinity-rank">
                      <Heart size={13} className="vn-heart-icon" />
                      {rank.label}
                    </span>
                    <strong className="vn-affinity-num">{affinity} / 100</strong>
                  </div>
                  <div className="vn-affinity-track" aria-hidden="true">
                    <div
                      className="vn-affinity-fill"
                      data-tone={rank.tone}
                      style={{ width: `${Math.max(4, Math.min(100, affinity))}%` }}
                    />
                  </div>
                </div>
              </header>

              {/* 2. 视觉小说水墨台词气泡 */}
              <article className="vn-speech-bubble" aria-label={`${name}的台词`}>
                <div className="vn-speech-knot-left" aria-hidden="true" />
                <span className="vn-speaker-tag">{name}</span>
                <p className="vn-speech-text">“{activeDialogue}”</p>
                <div className="vn-speech-knot-right" aria-hidden="true" />
              </article>

              {/* 3. 标签切换：互动行止 / 仙珍赠礼 / 浮生玉牒 */}
              <nav className="vn-tab-nav" aria-label="对谈交互分类">
                <button
                  type="button"
                  className={`vn-tab-btn ${activeTab === 'interact' ? 'active' : ''}`}
                  onClick={() => setActiveTab('interact')}
                >
                  <MessageCircleMore size={15} />
                  <span>交互行止</span>
                </button>
                <button
                  type="button"
                  className={`vn-tab-btn ${activeTab === 'gifts' ? 'active' : ''}`}
                  onClick={() => setActiveTab('gifts')}
                >
                  <Gift size={15} />
                  <span>奉赠仙珍 ({giftItems.length})</span>
                </button>
                <button
                  type="button"
                  className={`vn-tab-btn ${activeTab === 'bio' ? 'active' : ''}`}
                  onClick={() => setActiveTab('bio')}
                >
                  <ScrollText size={15} />
                  <span>相貌浮生</span>
                </button>
              </nav>

              {/* 4. Tab 1: 交互操作案席 */}
              {activeTab === 'interact' && (
                <div className="vn-actions-deck">
                  <div className="vn-action-grid">
                    <button
                      type="button"
                      className="vn-action-card interact-talk"
                      aria-label="前往交谈"
                      disabled={!alive || readOnly || busy}
                      onClick={() => handleAct(`对话 ${name}`, `与${name}促膝长谈，时光流逝，好感增进。`)}
                    >
                      <div className="vn-action-icon"><MessageCircleMore size={20} /></div>
                      <div className="vn-action-info">
                        <strong>前往交谈</strong>
                        <small>推进一月 · 倾听近况与感悟</small>
                      </div>
                    </button>

                    <button
                      type="button"
                      className="vn-action-card interact-discuss"
                      aria-label="论道印证"
                      disabled={!alive || readOnly || busy}
                      onClick={() => handleAct(`论道 ${name}`, `与${name}印证道法心术。`)}
                    >
                      <div className="vn-action-icon"><Sparkles size={20} /></div>
                      <div className="vn-action-info">
                        <strong>论道印证</strong>
                        <small>心性神识相交 · 获取修为感悟</small>
                      </div>
                    </button>

                    <button
                      type="button"
                      className="vn-action-card interact-spar"
                      aria-label="同道切磋"
                      disabled={!alive || readOnly || busy}
                      onClick={() => handleAct(`切磋 ${name}`, `与${name}展开点到为止的术法切磋。`)}
                    >
                      <div className="vn-action-icon"><Swords size={20} /></div>
                      <div className="vn-action-info">
                        <strong>同道切磋</strong>
                        <small>点到为止 · 检验实战斗法手段</small>
                      </div>
                    </button>

                    <button
                      type="button"
                      className="vn-action-card interact-gift-jump"
                      aria-label="赠礼纳祥"
                      disabled={!alive || readOnly || busy}
                      onClick={() => setActiveTab('gifts')}
                    >
                      <div className="vn-action-icon"><Gift size={20} /></div>
                      <div className="vn-action-info">
                        <strong>赠礼纳祥</strong>
                        <small>{giftItems.length ? `随身备有 ${giftItems.length} 件心意礼物` : '囊中暂无礼物，可去坊市采办'}</small>
                      </div>
                    </button>
                  </div>

                  {/* 结为道侣 / 双修 特殊心动行动 */}
                  {isPartner && (
                    <div className="vn-special-action-box partner-box">
                      <div className="vn-special-info">
                        <HeartHandshake size={18} />
                        <div>
                          <strong>道侣同心 · 合修一月</strong>
                          <small>阴阳共济，气运相生，大幅增进两方修为</small>
                        </div>
                      </div>
                      <button
                        type="button"
                        className="vn-special-btn partner-btn"
                        disabled={!alive || readOnly || busy}
                        onClick={() => handleAct(`双修 ${name}`, `与道侣${name}共参仙经合修一月。`)}
                      >
                        双修合契
                      </button>
                    </div>
                  )}

                  {canPropose && (
                    <div className="vn-special-action-box propose-box">
                      <div className="vn-special-info">
                        <Sparkles size={18} />
                        <div>
                          <strong>心意相通 · 结为道侣</strong>
                          <small>好感已臻至化境，可立下生死与共之天道誓约</small>
                        </div>
                      </div>
                      <button
                        type="button"
                        className="vn-special-btn propose-btn"
                        disabled={readOnly || busy}
                        onClick={() => handleAct(`结为道侣 ${name}`, `向${name}道出心意，结为长生道侣。`)}
                      >
                        誓结长生盟
                      </button>
                    </div>
                  )}

                  {/* 护道急件 */}
                  {hasGuardRequest && lifeProfile && (
                    <div className="vn-special-action-box guard-box">
                      <div className="vn-special-info">
                        <ShieldCheck size={18} />
                        <div>
                          <strong>突破护道急信：{lifeProfile.pending_kind}</strong>
                          <small>余 {lifeProfile.expires_in} 个月内需回应天命抉择</small>
                        </div>
                      </div>
                      <div className="vn-guard-btn-group">
                        <button
                          type="button"
                          className="vn-guard-btn"
                          disabled={readOnly || busy || !lifeProfile.can_gift_pill}
                          onClick={() => handleAct(`护道 ${name} 赠丹`)}
                        >
                          赠送突破丹药
                        </button>
                        <button
                          type="button"
                          className="vn-guard-btn highlight"
                          disabled={readOnly || busy || !lifeProfile.can_guard}
                          onClick={() => handleAct(`护道 ${name} 护持`)}
                        >
                          亲自护法 (耗灵 30)
                        </button>
                      </div>
                    </div>
                  )}

                  {lastActionFeedback && (
                    <div className="vn-feedback-bar" role="status">
                      <ScrollText size={14} />
                      <span>{lastActionFeedback}</span>
                    </div>
                  )}
                </div>
              )}

              {/* 5. Tab 2: 礼物奉赠抽屉 */}
              {activeTab === 'gifts' && (
                <div className="vn-gifts-deck">
                  <div className="vn-preferences-banner">
                    <div className="vn-pref-block likes">
                      <span className="vn-pref-title">
                        <Heart size={12} />
                        心头所好：
                      </span>
                      <div className="vn-pref-chips">
                        {likes.length ? (
                          likes.map((like) => <span key={like} className="vn-chip like">{like}</span>)
                        ) : (
                          <span className="vn-chip muted">尚待相处深交</span>
                        )}
                      </div>
                    </div>
                    {dislikes.length > 0 && (
                      <div className="vn-pref-block dislikes">
                        <span className="vn-pref-title">心生不悦：</span>
                        <div className="vn-pref-chips">
                          {dislikes.map((dislike) => <span key={dislike} className="vn-chip dislike">{dislike}</span>)}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="vn-gifts-list">
                    {giftItems.length === 0 ? (
                      <div className="vn-empty-gifts">
                        <Gift size={32} />
                        <p>乾坤袋中未备有「礼物」类雅致仙珍。</p>
                        <small>可前往九州天机坊市、探索秘境或击败异兽获取灵茶、佩玉与奇珍。</small>
                      </div>
                    ) : (
                      giftItems.map((item) => {
                        const isLiked = likes.includes(item.name)
                        const isDisliked = dislikes.includes(item.name)
                        return (
                          <div key={item.name} className="vn-gift-row" data-liked={isLiked || undefined}>
                            <div className="vn-gift-icon">
                              <Gift size={18} />
                            </div>
                            <div className="vn-gift-meta">
                              <strong>{item.name}</strong>
                              <small>持有 ×{item.count} 份</small>
                            </div>
                            <div className="vn-gift-reaction">
                              {isLiked && <span className="vn-reaction-tag liked">至爱 +好感</span>}
                              {isDisliked && <span className="vn-reaction-tag disliked">不悦</span>}
                              {!isLiked && !isDisliked && <span className="vn-reaction-tag regular">心意礼品</span>}
                            </div>
                            <button
                              type="button"
                              className="vn-send-gift-btn"
                              disabled={!alive || readOnly || busy}
                              onClick={() => handleAct(`送礼 ${name} ${item.name}`, `将【${item.name}】赠予了${name}。`)}
                            >
                              奉赠
                            </button>
                          </div>
                        )
                      })
                    )}
                  </div>
                </div>
              )}

              {/* 6. Tab 3: 相貌风仪与生平档案 */}
              {activeTab === 'bio' && (
                <div className="vn-bio-deck">
                  {/* 相貌描述 */}
                  <article className="vn-bio-card appearance-card">
                    <header>
                      <Sparkles size={16} />
                      <strong>相貌风仪案卷</strong>
                      <small>{appearance.archetypeLabel} · {appearance.temperamentLabel}</small>
                    </header>
                    <p className="vn-bio-desc">{appearance.description}</p>
                  </article>

                  {/* 寿元机杼 */}
                  {lifeProfile && (
                    <article className="vn-bio-card lifespan-card">
                      <header>
                        <HeartPulse size={16} />
                        <strong>岁序荣枯</strong>
                        <small>现年 {lifeProfile.age} 岁 / 天命寿元 {lifeProfile.lifespan} 年</small>
                      </header>
                      <div className="vn-lifespan-track">
                        <div
                          className="vn-lifespan-fill"
                          style={{ width: `${Math.max(4, Math.min(100, (lifeProfile.age / Math.max(1, lifeProfile.lifespan)) * 100))}%` }}
                        />
                      </div>
                      <p className="vn-lifespan-note">
                        {lifeProfile.alive
                          ? `若无大限延寿或境界突破，尚余约 ${lifeProfile.years_remaining} 年寿元。`
                          : `此生已然落幕：${lifeProfile.cause_of_death || '化道归真'}`}
                      </p>
                    </article>
                  )}

                  {/* 近世行迹 */}
                  {lifeProfile?.life_events && lifeProfile.life_events.length > 0 && (
                    <article className="vn-bio-card chronicle-card">
                      <header>
                        <BookOpen size={16} />
                        <strong>近世行迹履历</strong>
                      </header>
                      <ol className="vn-chronicle-list">
                        {lifeProfile.life_events.slice(-5).reverse().map((ev, idx) => (
                          <li key={`${ev}-${idx}`}>
                            <span className="vn-chronicle-index">{idx + 1}</span>
                            <p>{ev}</p>
                          </li>
                        ))}
                      </ol>
                    </article>
                  )}
                </div>
              )}
            </section>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
