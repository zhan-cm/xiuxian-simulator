import {
  BedDouble,
  CheckCircle2,
  Circle,
  Coins,
  Compass,
  Hourglass,
  Mountain,
  ScrollText,
  Sparkles,
  Zap,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import type { GameState, PendingEncounterData, PlayerState, Snapshot } from '../api/types'

export interface TianjiFocusCardProps {
  player: PlayerState
  state: GameState
  snapshot: Snapshot
  pendingEncounter?: PendingEncounterData | null
  busy?: boolean
  readOnly?: boolean
  canQuickAct: boolean
  onAction: (action: string) => void
  onOpenGuide?: () => void
  onOpenRealmsLadder?: () => void
  onOpenEncounter?: () => void
  onOpenCommissionBoard?: () => void
}

interface FocusActionRecommendation {
  tone: 'encounter' | 'danger' | 'warning' | 'breakthrough' | 'cultivation' | 'trade' | 'gain'
  eyebrow: string
  title: string
  description: string
  actionLabel: string
  action: string
  isModalAction?: boolean
  icon: typeof Sparkles
  badge: string
}

const MAJOR_PILLS = ['筑基丹', '凝晶丹', '结丹灵药', '结婴丹', '具灵丹', '化神丹', '悟道丹', '羽化丹', '登仙丹']

function ownsItem(player: PlayerState, inventory: Snapshot['inventory'] | undefined, name: string) {
  return Boolean(
    player.resources?.[name] > 0 || player.inventory?.includes(name) ||
    inventory?.items?.some((item) => item.name === name && item.count > 0)
  )
}

export function TianjiFocusCard({
  player,
  state,
  snapshot,
  pendingEncounter,
  busy = false,
  readOnly = false,
  canQuickAct,
  onAction,
  onOpenGuide,
  onOpenRealmsLadder,
  onOpenEncounter,
  onOpenCommissionBoard,
}: TianjiFocusCardProps) {
  const [showMilestones, setShowMilestones] = useState(false)

  // 1. 动态推演「当务之急」焦点行动（Next Best Action）
  const recommendation = useMemo<FocusActionRecommendation>(() => {
    // 优先级 1：红尘奇遇待决
    if (pendingEncounter || state.phase === 'encounter_choice') {
      return {
        tone: 'encounter',
        badge: '因果待决',
        eyebrow: '【红尘机缘】天道因果',
        title: pendingEncounter ? `机缘待决 · ${pendingEncounter.title}` : '红尘机缘 · 因果待定',
        description: '天地因果已至，当遵从本心道念定夺抉择，方可继续参悟天道。',
        actionLabel: '定夺机缘因果',
        action: 'open_encounter',
        isModalAction: true,
        icon: ScrollText,
      }
    }

    // 优先级 2：气血垂危 / 身负重伤
    const isWounded =
      player.health < player.health_max * 0.35 ||
      /伤|虚弱|濒死/.test(player.condition)
    if (isWounded) {
      const restAct = snapshot.recovery?.rest_action || '修炼'
      return {
        tone: 'danger',
        badge: '经络受损',
        eyebrow: '【身染伤损】气血亏虚',
        title: '气脉紊乱 · 宜入洞府静养',
        description: '当前气血亏损严重，切忌强行涉险历练，宜闭关静养以平复经络伤势。',
        actionLabel: '洞府闭门静养',
        action: restAct,
        icon: BedDouble,
      }
    }

    // 优先级 3：天人五衰大限倒悬（剩余寿元不足3年）
    const remainingYears = player.lifespan - player.age
    if (remainingYears <= 3) {
      return {
        tone: 'warning',
        badge: '大限将至',
        eyebrow: '【寿元大限】五衰逼近',
        title: `寿元仅余 ${remainingYears} 年 · 急寻生机`,
        description: '天道寿限迫在眉睫，当竭尽全力冲击破关以延益天命，或赴坊市寻访延寿灵药。',
        actionLabel: '引动破境机缘',
        action: '突破',
        icon: Hourglass,
      }
    }

    const needsFoundationPill = player.realm === '炼气·圆满' &&
      !ownsItem(player, snapshot.inventory, '筑基丹') && !ownsItem(player, snapshot.inventory, '天材地宝')
    if (needsFoundationPill) {
      const canShop = player.spirit_stones >= 300
      return {
        tone: 'trade',
        badge: '筑基准备',
        eyebrow: '【破境资粮】先备丹药',
        title: canShop ? '先去坊市寻找筑基丹' : '筑基丹尚未备齐 · 先赚灵石',
        description: `人道筑基需要筑基丹×1；坊市参考价约 300 灵石，你现有 ${player.spirit_stones} 灵石。可做悬榜委托，或收集灵药与妖兽材料自行炼丹；地道也可使用天材地宝。`,
        actionLabel: canShop ? '前往坊市备丹' : '查看可做的悬榜',
        action: canShop ? '坊市' : 'open_commission',
        isModalAction: !canShop && Boolean(onOpenCommissionBoard),
        icon: Coins,
      }
    }

    // 优先级 4：修为圆满瓶颈（破境契机）
    if (player.cultivation >= player.cultivation_required) {
      const isMajor = player.realm.endsWith('圆满')
      return {
        tone: 'breakthrough',
        badge: '破境契机',
        eyebrow: '【道基圆满】瓶颈已现',
        title: `${player.realm} · 修为已满`,
        description: isMajor ? '修为已经圆满，资粮备齐后可选择突破路线。' : '修为已满，可以尝试突破当前小境界；无需筑基丹或渡雷劫。',
        actionLabel: isMajor ? '选择突破路线' : '尝试小境界突破',
        action: '突破',
        icon: Mountain,
      }
    }

    // 委托统一交给常驻追踪卡，避免与当务之急重复显示。
    // 优先级 5：囊中羞涩（灵石不足 40 且未达突破，急需生财）
    if (player.spirit_stones < 40) {
      return {
        tone: 'trade',
        badge: '生财有道',
        eyebrow: '【囊中羞涩】资粮告急',
        title: '灵石见底 · 宜赴悬榜或山麓历练生财',
        description: '仙道贵在资粮，眼下灵石空乏难以为继。当速去东洲悬榜承接差事，或巡游山麓采集妖材灵草在坊市变现。',
        actionLabel: '揭阅悬赏生财',
        action: 'open_commission',
        isModalAction: Boolean(onOpenCommissionBoard),
        icon: Coins,
      }
    }

    // 优先级 6：日常潜修纳气（日常主推）
    const needCultivation = Math.max(0, player.cultivation_required - player.cultivation)
    const canRetreat = player.spirit >= 20
    return {
      tone: 'cultivation',
      badge: '道途潜修',
      eyebrow: '【玄黄潜修】周天运化',
      title: canRetreat ? '纳气闭关 · 运转大小周天' : '吐纳炼气 · 吞纳天地灵机',
      description: `身处${player.location}，当前境界${player.realm}，距破境尚缺 ${needCultivation} 点修为，宜凝心聚气。`,
      actionLabel: canRetreat ? '闭关三月（加速修道）' : '吐纳修炼（积蓄灵力）',
      action: canRetreat ? '闭关3月' : '修炼',
      icon: Sparkles,
    }
  }, [player, state.phase, snapshot.recovery, snapshot.inventory, pendingEncounter, onOpenCommissionBoard])

  // 2. 当前道阶里程碑清单（Milestone Checklist）
  const milestones = useMemo(() => {
    const isCultivationFull = player.cultivation >= player.cultivation_required
    const hasSpellsOrArts = Boolean(
      snapshot.art_mastery?.equipped_spell?.name ||
      (snapshot.art_mastery?.spells && snapshot.art_mastery.spells.length > 0) ||
      (player.inventory || []).some((i) => /术|诀|法|经/.test(i))
    )
    const [realmName, stageName] = player.realm.split('·')
    const realmIndex = ['炼气', '筑基', '结晶', '金丹', '具灵', '元婴', '化神', '悟道', '羽化'].indexOf(realmName)
    const requiredPill = MAJOR_PILLS[realmIndex]
    const majorReady = Boolean(
      (requiredPill && ownsItem(player, snapshot.inventory, requiredPill)) || ownsItem(player, snapshot.inventory, '天材地宝')
    )
    const needsMajorResources = stageName === '圆满' && Boolean(requiredPill)

    return [
      {
        id: 'realm_solid',
        label: `稳固${player.realm}道基`,
        done: true,
        hint: '已破入此境界',
      },
      {
        id: 'cultivation_fill',
        label: `气海周天圆满 (${player.cultivation}/${player.cultivation_required})`,
        done: isCultivationFull,
        hint: isCultivationFull ? '道行已臻至瓶颈' : '需通过吐纳或闭关蓄足灵力',
      },
      {
        id: 'arts_mastery',
        label: '研习护道心法攻伐法术',
        done: hasSpellsOrArts,
        hint: hasSpellsOrArts ? '已有道法在身' : '可前往宗门或坊市研习法术',
      },
      {
        id: 'breakthrough_prep',
        label: needsMajorResources ? `备齐${requiredPill}或天材地宝` : '小境界无需破境材料',
        done: !needsMajorResources || majorReady,
        hint: !needsMajorResources ? '修为满值即可尝试' : majorReady ? '已持有可用的破境材料' : '灵石本身不能突破；先到坊市购丹、炼丹或寻找天材地宝',
      },
    ]
  }, [player, snapshot.art_mastery, snapshot.inventory])

  const RecIcon = recommendation.icon

  const handleExecutePrimary = () => {
    if (busy || readOnly) return
    if (recommendation.isModalAction) {
      if (recommendation.action === 'open_encounter') {
        onOpenEncounter?.()
      } else if (recommendation.action === 'open_commission') {
        onOpenCommissionBoard?.()
      }
      return
    }
    if (!canQuickAct) return
    onAction(recommendation.action)
  }

  const isPrimaryDisabled =
    busy || readOnly || (!recommendation.isModalAction && !canQuickAct)

  return (
    <section
      className={`tianji-focus-card tone-${recommendation.tone}`}
      aria-label="天机司南与当下心念导引"
    >
      <div className="tianji-focus-inner">
        {/* 左侧灵机核心 */}
        <div className="tianji-compass-crest">
          <div className="tianji-crest-glow" aria-hidden="true" />
          <RecIcon size={24} className="tianji-crest-icon" />
          <span className="tianji-badge-tag">{recommendation.badge}</span>
        </div>

        {/* 中部导引文辞 */}
        <div className="tianji-focus-content">
          <div className="tianji-focus-eyebrow">
            <Compass size={13} />
            <span>天机司南 · {recommendation.eyebrow}</span>
          </div>
          <h3 className="tianji-focus-title">{recommendation.title}</h3>
          <p className="tianji-focus-desc">{recommendation.description}</p>
        </div>

        {/* 右侧主行动机枢 */}
        <div className="tianji-focus-actions">
          <button
            type="button"
            className="tianji-primary-action-btn"
            disabled={isPrimaryDisabled}
            onClick={handleExecutePrimary}
            title={
              readOnly
                ? '成果巡览仅供查看'
                : isPrimaryDisabled
                  ? '请先完成前置抉择'
                  : `一键执行：${recommendation.actionLabel}`
            }
          >
            <Zap size={16} />
            <span>{recommendation.actionLabel}</span>
          </button>
          <div className="tianji-sub-actions">
            {onOpenRealmsLadder && (
              <button
                type="button"
                className="tianji-sub-action-btn"
                onClick={onOpenRealmsLadder}
                title="查看境界仙阶十重天"
              >
                <Mountain size={13} />
                <span>道阶通天</span>
              </button>
            )}
            {onOpenGuide && (
              <button
                type="button"
                className="tianji-sub-action-btn"
                onClick={onOpenGuide}
                title="打开修仙行止向导攻略"
              >
                <Compass size={13} />
                <span>仙途指津</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 底部：当前道阶里程碑清单 */}
      <div className="tianji-milestones-bar">
        <button
          type="button"
          className="tianji-milestone-toggle"
          onClick={() => setShowMilestones((prev) => !prev)}
          aria-expanded={showMilestones}
        >
          <span>🎯 {player.realm} · 证道里程碑</span>
          <small>{showMilestones ? '收起目标' : '展开目标'}</small>
        </button>

        {showMilestones && (
          <ul className="tianji-milestone-list">
            {milestones.map((m) => (
              <li
                key={m.id}
                className={`tianji-milestone-item ${m.done ? 'completed' : 'pending'}`}
                title={m.hint}
              >
                {m.done ? (
                  <CheckCircle2 size={13} className="text-emerald-600" />
                ) : (
                  <Circle size={13} className="text-amber-500/70" />
                )}
                <span>{m.label}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
