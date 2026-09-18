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
  const [showMilestones, setShowMilestones] = useState(true)

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

    // 优先级 4：修为圆满瓶颈（破境契机）
    if (player.cultivation >= player.cultivation_required) {
      return {
        tone: 'breakthrough',
        badge: '破境契机',
        eyebrow: '【道基圆满】瓶颈已现',
        title: `${player.realm}圆满 · 气海翻涌引动天劫`,
        description: '经络灵力澎湃充盈，已至此境极限。天地雷劫呼之欲出，速速破关登仙！',
        actionLabel: '引动雷劫破境',
        action: '突破',
        icon: Mountain,
      }
    }

    // 优先级 5：悬赏有成（在途委托已达标，前往领赏）
    const readyCommissions = snapshot.commissions?.active?.filter((item) => item.ready) || []
    if (readyCommissions.length > 0) {
      const firstReady = readyCommissions[0]
      return {
        tone: 'gain',
        badge: '悬榜有成',
        eyebrow: '【因果有偿】委托已达标',
        title: `《${firstReady.title}》已成 · 前往东洲悬榜领赏`,
        description: `历练圆满达成所托，可领取 ${firstReady.reward} 等丰厚报酬。`,
        actionLabel: '领取悬榜赏金',
        action: 'open_commission',
        isModalAction: Boolean(onOpenCommissionBoard),
        icon: ScrollText,
      }
    }

    // 优先级 6：囊中羞涩（灵石不足 40 且未达突破，急需生财）
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

    // 优先级 7：日常潜修纳气（日常主推）
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
  }, [player, state.phase, snapshot.recovery, snapshot.commissions, pendingEncounter, onOpenCommissionBoard])

  // 2. 当前道阶里程碑清单（Milestone Checklist）
  const milestones = useMemo(() => {
    const isCultivationFull = player.cultivation >= player.cultivation_required
    const hasSpellsOrArts = Boolean(
      snapshot.art_mastery?.equipped_spell?.name ||
      (snapshot.art_mastery?.spells && snapshot.art_mastery.spells.length > 0) ||
      (player.inventory || []).some((i) => /术|诀|法|经/.test(i))
    )
    const hasPillOrWealth =
      player.spirit_stones >= 150 ||
      (player.inventory || []).some((i) => /丹/.test(i))

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
        label: '筹备破关聚气灵丹与资粮',
        done: hasPillOrWealth,
        hint: hasPillOrWealth ? '资粮充足' : '备好破境灵丹或攒足灵石以御反噬',
      },
    ]
  }, [player, snapshot.art_mastery])

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
