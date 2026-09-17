import { motion } from 'motion/react'
import { Activity, AlertCircle, CheckCircle2, Crown, Flame, Info, Shield, Sparkles, Swords, X, Zap } from 'lucide-react'
import type { Snapshot } from '../api/types'

const REALM_NAMES = ['炼气', '筑基', '结晶', '金丹', '具灵', '元婴', '化神', '悟道', '羽化', '登仙']
const STAGE_NAMES = ['初期', '中期', '后期', '圆满']
const PILL_NAMES = ['筑基丹', '凝晶丹', '结丹灵药', '结婴丹', '具灵丹', '化神丹', '悟道丹', '羽化丹', '登仙丹']
const TARGET_LIFESPANS = [100, 200, 300, 500, 800, 1200, 2000, 5000, 10000, 50000]

interface BreakthroughAltarProps {
  snapshot: Snapshot
  busy: boolean
  readOnly: boolean
  onAction: (action: string) => void
  onClose?: () => void
}

export function BreakthroughAltar({ snapshot, busy, readOnly, onAction, onClose }: BreakthroughAltarProps) {
  const { state, decision } = snapshot
  const { player } = state

  const [baseRealm = '炼气', stageName = '初期'] = (player.realm || '').split('·')
  const currentRealmIndex = Math.max(0, REALM_NAMES.indexOf(baseRealm))
  const currentStageIndex = Math.max(0, STAGE_NAMES.indexOf(stageName))
  const isPinnacleStage = currentStageIndex >= 3 // 圆满
  const isCultivationMax = player.cultivation >= player.cultivation_required

  const nextRealmName = REALM_NAMES[currentRealmIndex + 1] || '真仙'
  const nextLifespan = TARGET_LIFESPANS[currentRealmIndex + 1] || player.lifespan + 200
  const pillRequired = PILL_NAMES[currentRealmIndex] || '破境丹'

  // 检查乾坤袋及资源中的丹药与材料
  const hasHumanPill = Boolean(
    (player.resources?.[pillRequired] && player.resources[pillRequired] > 0) ||
    snapshot.inventory?.items?.some((item) => item.name === pillRequired && item.count > 0)
  )
  const hasEarthTreasure = Boolean(
    (player.resources?.['天材地宝'] && player.resources['天材地宝'] > 0) ||
    snapshot.inventory?.items?.some((item) => item.name === '天材地宝' && item.count > 0)
  )
  const hasSpiritOrb = Boolean(
    (player.resources?.['五行灵珠'] && player.resources['五行灵珠'] > 0) ||
    snapshot.inventory?.items?.some((item) => item.name === '五行灵珠' && item.count > 0)
  )
  const hasDaoRhyme = Boolean(
    (player.resources?.['道韵'] && player.resources['道韵'] > 0) ||
    snapshot.inventory?.items?.some((item) => item.name === '道韵' && item.count > 0)
  )
  const hasHeavenTreasure = hasEarthTreasure && hasSpiritOrb && hasDaoRhyme

  const tribulation = snapshot.tribulation
  const tierInfo = tribulation?.tier_info
  const protection = tribulation?.protection
  const outputText = snapshot.output || ''
  const hasTribulationOutput = outputText.includes('渡劫战报') || outputText.includes('天劫雷罚')

  const isDestinyPhase = state.phase === 'destiny_choice' || decision?.eyebrow === '逆天改命' || (decision?.title || '').includes('逆天改命')
  const isMajorDecisionPhase = state.phase === 'major_breakthrough_choice' || decision?.eyebrow === '破境路线'
  const isMajorDecision = isPinnacleStage || isMajorDecisionPhase

  // 1. 如果处于【逆天改命】先天气运刻印时刻
  if (isDestinyPhase) {
    const destinyCards = decision?.choices?.length
      ? decision.choices.map((c, i) => ({
          title: c.label,
          desc: c.description,
          action: c.action,
          index: i,
        }))
      : (Array.isArray(state.pending_choices) ? (state.pending_choices as string[]) : ['紫气东来', '剑灵胚胎', '天道眷顾']).map((trait, i) => ({
          title: String(trait),
          desc: `将【${String(trait)}】永久写入本世命盘，受大道气运庇佑，终生受益。`,
          action: `选择 ${i + 1}`,
          index: i,
        }))

    return (
      <section className="breakthrough-altar destiny-altar" aria-label="逆天改命圣殿">
        <header className="altar-hero destiny-hero">
          <span className="altar-crown-seal"><Crown size={28} /></span>
          <div className="altar-hero-text">
            <small>天道交感 · 功德圆满</small>
            <h2>逆天改命 · 命格刻印</h2>
            <p>破开天道锁链，大道降下先天气运，请选择其一融入本命道基：</p>
          </div>
          {onClose && (
            <button type="button" className="altar-close-btn" onClick={onClose} aria-label="关闭">
              <X size={18} />
            </button>
          )}
        </header>

        <div className="destiny-cards-grid">
          {destinyCards.map((card) => (
            <motion.div
              key={card.action}
              className="destiny-card"
              whileHover={busy || readOnly ? undefined : { y: -3 }}
            >
              <div className="destiny-card-top">
                <span className="destiny-order-badge">天命 0{card.index + 1}</span>
                <Sparkles size={16} color="#ba8d3c" />
              </div>
              <h3>{card.title}</h3>
              <p>{card.desc}</p>
              <button
                type="button"
                className="destiny-select-btn"
                disabled={busy || readOnly}
                onClick={() => onAction(card.action)}
              >
                <span>烙入此命</span>
              </button>
            </motion.div>
          ))}
        </div>
      </section>
    )
  }

  // 2. 常规或大境界准备阶段
  return (
    <section className="breakthrough-altar" aria-label="大境界突破圣台">
      {/* 顶部天关封印横额 */}
      <header className="altar-hero">
        <div className="altar-crown-seal"><Flame size={24} /></div>
        <div className="altar-hero-text">
          <small>{isMajorDecision ? '大境界天关叩关' : '小境界蓄力推演'}</small>
          <h2>{isMajorDecision ? `${player.realm} · 叩问天门` : `${player.realm} · 潜心蓄力`}</h2>
          <p>
            {isMajorDecision
              ? `已至${baseRealm}大圆满。欲登临【${nextRealmName}】之境，需定夺破境道基，历经劫数洗礼。`
              : `当前道行尚未抵达圆满天关，可先行体悟人、地、天三道之奥秘与资粮要求。`}
          </p>
        </div>
        {onClose && (
          <button type="button" className="altar-close-btn" onClick={onClose} aria-label="返回仙途">
            <X size={18} />
          </button>
        )}
      </header>

      {/* 境界晋升天梯桥 */}
      <div className="altar-realm-transition">
        <div className="realm-node current">
          <span className="realm-node-badge">当前道阶</span>
          <strong>{player.realm}</strong>
          <small>修为 {player.cultivation}/{player.cultivation_required}</small>
        </div>

        <div className="realm-bridge">
          <span className="bridge-line">
            <Sparkles size={14} />
            <span>叩问天道</span>
          </span>
          <small>寿元天限 +{nextLifespan - player.lifespan} 载</small>
        </div>

        <div className="realm-node target">
          <span className="realm-node-badge">问鼎前路</span>
          <strong>{nextRealmName}·初期</strong>
          <small>天年大限达 {nextLifespan} 岁</small>
        </div>
      </div>

      {/* 准备状态提示 */}
      <div className="altar-status-banner">
        <div>
          {isCultivationMax ? <CheckCircle2 size={18} color="#2b6351" /> : <AlertCircle size={18} color="#ba8d3c" />}
          <span>
            {isCultivationMax
              ? '气海灵元大圆满！请择定人道、地道或天道其一叩问天关。'
              : `气海尚需积蓄 ${player.cultivation_required - player.cultivation} 点修为，方可引发天地天象。`}
          </span>
        </div>
      </div>

      {/* 渡劫实况回响（若刚经历渡劫） */}
      {hasTribulationOutput && (
        <div className="tribulation-chronicle-box" role="region" aria-label="渡劫回响战报">
          <div className="chronicle-header">
            <Zap size={16} color="#ba8d3c" />
            <strong>九天雷劫 · 渡劫回响</strong>
          </div>
          <p className="chronicle-body">{outputText.split('【逆天改命')[0].trim()}</p>
        </div>
      )}

      {/* 天劫雷罚威仪与护道底蕴面板 */}
      {tierInfo && (
        <section className="tribulation-overview-card" aria-label="九天雷劫与护道底蕴">
          <div className="tribulation-hero-grid">
            {/* 左侧：天劫威仪 */}
            <div className="tribulation-danger-block">
              <div className="tribulation-title-row">
                <span className="tribulation-pill-tag">大境界雷罚</span>
                <span className="tribulation-threat-badge">{tierInfo.threat_level}</span>
              </div>
              <h3 className="tribulation-name">
                <Zap size={20} className="thunder-icon" />
                <span>{tierInfo.name}</span>
              </h3>
              <p className="tribulation-desc">{tierInfo.description}</p>
              <div className="tribulation-waves-meta">
                <span className="wave-badge">
                  <Activity size={13} /> 共 <strong>{tierInfo.waves_count}</strong> 重神雷轰顶
                </span>
                <span className="wave-badge">
                  <Flame size={13} /> 异象：{tierInfo.element}
                </span>
              </div>
            </div>

            {/* 右侧：护道底蕴检视 */}
            <div className="dao-protection-block">
              <div className="protection-title-row">
                <div className="protection-title-left">
                  <Shield size={16} color="#ba8d3c" />
                  <strong>护道底牌大阵</strong>
                </div>
                <span className={`readiness-seal readiness-${protection?.readiness_label || '单薄'}`}>
                  {protection?.readiness_label || '单薄涉险'}
                </span>
              </div>

              <div className="protection-grid-specs">
                <div className="prot-spec-item">
                  <small>抗雷削减</small>
                  <strong>+{protection?.thunder_mitigation_rate || 0}%</strong>
                </div>
                <div className="prot-spec-item">
                  <small>阵法灵幕</small>
                  <strong>{protection?.formation_shield ? `${protection.formation_shield}点` : '无阵法'}</strong>
                </div>
                <div className="prot-spec-item">
                  <small>避劫神符</small>
                  <strong style={{ color: protection?.has_ward_talisman ? '#2b6351' : '#888' }}>
                    {protection?.has_ward_talisman ? '已就绪' : '未佩戴'}
                  </strong>
                </div>
              </div>

              {/* 核心法宝神威标签 */}
              <div className="protection-tags-list">
                {protection?.has_artifact ? (
                  <div className="artifact-status-pill">
                    <Swords size={12} />
                    <span>本命【{protection.artifact_name}】· {protection.spirit_stage}</span>
                  </div>
                ) : (
                  <span className="no-artifact-hint">暂未认主本命灵宝，以肉身直面天雷</span>
                )}
                {protection?.protection_tags?.map((tag) => (
                  <span key={tag} className="dao-seal-tag">
                    {tag.includes('免死') || tag.includes('避劫') ? '🔥 ' : tag.includes('引雷') ? '⚡ ' : '✨ '}
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* 三大破境道基路线对比 (人道 / 地道 / 天道) */}
      <div className="altar-routes-container">
        <div className="routes-header">
          <h3>三大道基路线比较</h3>
          <span>选择合适道基，定鼎未来仙途</span>
        </div>

        <div className="routes-grid">
          {/* 人道破关 */}
          <article className="route-card human-route">
            <div className="route-card-header">
              <div className="route-card-title-row">
                <strong>人道破关</strong>
                <span className="route-badge">凡俗守真</span>
              </div>
              <em>稳妥自保 · 不历凶险</em>
            </div>

            <div className="route-specs">
              <div className="spec-row">
                <span>心魔通过率</span>
                <strong>95%</strong>
              </div>
              <div className="spec-row">
                <span>雷劫抗性</span>
                <strong>95%</strong>
              </div>
            </div>

            <div className="route-requirements">
              <span className="req-item" data-fulfilled={hasHumanPill}>
                {hasHumanPill ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                <span>所需丹药：{pillRequired} ×1 ({hasHumanPill ? '已备齐' : '缺少'})</span>
              </span>
            </div>

            <div className="route-perks">
              <span>· 气血与灵力平稳提升</span>
              <span>· 极低走火入魔风险</span>
            </div>

            <button
              type="button"
              className="route-action-btn"
              disabled={busy || readOnly || !isCultivationMax || !hasHumanPill}
              onClick={() => onAction('突破 人道')}
              title={
                !isCultivationMax
                  ? `修为未满（还需 ${player.cultivation_required - player.cultivation} 点修为）`
                  : !hasHumanPill
                    ? `缺少所需丹药【${pillRequired}×1】，可在坊市百宝阁购买或洞府炼制`
                    : '以人道根基叩问天关'
              }
            >
              <span>
                {!isCultivationMax ? '修为未圆满' : !hasHumanPill ? `缺少${pillRequired}` : '叩定人道'}
              </span>
            </button>
          </article>

          {/* 地道破关 */}
          <article className="route-card earth-route">
            <div className="route-card-header">
              <div className="route-card-title-row">
                <strong>地道破关</strong>
                <span className="route-badge">坤灵厚土</span>
              </div>
              <em>纳地脉地宝 · 根骨雄浑</em>
            </div>

            <div className="route-specs">
              <div className="spec-row">
                <span>心魔通过率</span>
                <strong>85%</strong>
              </div>
              <div className="spec-row">
                <span>雷劫抗性</span>
                <strong>85%</strong>
              </div>
            </div>

            <div className="route-requirements">
              <span className="req-item" data-fulfilled={hasEarthTreasure}>
                {hasEarthTreasure ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                <span>所需灵材：天材地宝 ×1 ({hasEarthTreasure ? '已备齐' : '缺少'})</span>
              </span>
            </div>

            <div className="route-perks">
              <span>· 六维底蕴大幅增幅</span>
              <span>· 额外寿元与灵海拓宽</span>
            </div>

            <button
              type="button"
              className="route-action-btn"
              disabled={busy || readOnly || !isCultivationMax || !hasEarthTreasure}
              onClick={() => onAction('突破 地道')}
              title={
                !isCultivationMax
                  ? `修为未满（还需 ${player.cultivation_required - player.cultivation} 点修为）`
                  : !hasEarthTreasure
                    ? '缺少所需灵物【天材地宝×1】，可在地方机缘、拍卖会或大荒探索中寻觅'
                    : '以厚土地脉叩问天关'
              }
            >
              <span>
                {!isCultivationMax ? '修为未圆满' : !hasEarthTreasure ? '缺少天材地宝' : '叩定地道'}
              </span>
            </button>
          </article>

          {/* 天道破关 */}
          <article className="route-card heaven-route">
            <div className="route-card-header">
              <div className="route-card-title-row">
                <strong>天道破关</strong>
                <span className="route-badge">极道夺造化</span>
              </div>
              <em>逆天改命 · 解锁无上天资</em>
            </div>

            <div className="route-specs">
              <div className="spec-row">
                <span>心魔通过率</span>
                <strong>70%</strong>
              </div>
              <div className="spec-row">
                <span>雷劫抗性</span>
                <strong>70%</strong>
              </div>
            </div>

            <div className="route-requirements">
              <span className="req-item" data-fulfilled={hasEarthTreasure}>
                {hasEarthTreasure ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                <span>天材地宝 ×1</span>
              </span>
              <span className="req-item" data-fulfilled={hasSpiritOrb}>
                {hasSpiritOrb ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                <span>五行灵珠 ×1</span>
              </span>
              <span className="req-item" data-fulfilled={hasDaoRhyme}>
                {hasDaoRhyme ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                <span>道韵 ×1</span>
              </span>
            </div>

            <div className="route-perks">
              <span>✨ 极道道基：解锁【逆天改命】</span>
              <span>· 寿元与六维属性极限飞跃</span>
            </div>

            <button
              type="button"
              className="route-action-btn"
              disabled={busy || readOnly || !isCultivationMax || !hasHeavenTreasure}
              onClick={() => onAction('突破 天道')}
              title={
                !isCultivationMax
                  ? `修为未满（还需 ${player.cultivation_required - player.cultivation} 点修为）`
                  : !hasHeavenTreasure
                    ? `缺少极道资粮：${[!hasEarthTreasure && '天材地宝', !hasSpiritOrb && '五行灵珠', !hasDaoRhyme && '道韵'].filter(Boolean).join('、')}，逆天改命需极道资粮`
                    : '夺天地造化，叩定极道天关'
              }
            >
              <span>
                {!isCultivationMax ? '修为未圆满' : !hasHeavenTreasure ? '极道资粮不足' : '叩定天道'}
              </span>
            </button>
          </article>
        </div>
      </div>

      <footer className="altar-status-banner altar-footer-banner">
        <div>
          <Info size={16} />
          <span>若材料不足，可在【坊市】寻访百宝阁，或在【洞府】静室中炼丹制器。</span>
        </div>
        {onClose && (
          <button
            type="button"
            className="altar-cancel-action-btn"
            disabled={busy || readOnly}
            onClick={onClose}
          >
            <X size={14} />
            <span>暂缓突破 · 收拢灵力</span>
          </button>
        )}
      </footer>
    </section>
  )
}

