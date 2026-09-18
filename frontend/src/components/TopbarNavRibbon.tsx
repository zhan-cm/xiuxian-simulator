import {
  BookOpen,
  ChevronDown,
  ClipboardList,
  Compass,
  HeartHandshake,
  Landmark,
  Mountain,
  ScrollText,
  Sparkles,
  Trophy,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

export interface TopbarNavRibbonProps {
  hasPendingEncounter?: boolean
  hasReadyCommission?: boolean
  onOpenRealmsLadder: () => void
  onOpenGuide: () => void
  onOpenSectGate: (sectName?: string) => void
  onOpenCommissionBoard?: () => void
  onOpenTianji: () => void
  onOpenLifebound: () => void
  onOpenArtifactSpirit: () => void
  onOpenEncounter: () => void
  onOpenPartnerChamber: () => void
  onOpenAncientTomb: () => void
  onToggleCodex?: () => void
}

type SanctuaryId = 'chronicle' | 'world' | 'mysteries' | null

export function TopbarNavRibbon({
  hasPendingEncounter = false,
  hasReadyCommission = false,
  onOpenRealmsLadder,
  onOpenGuide,
  onOpenSectGate,
  onOpenCommissionBoard,
  onOpenTianji,
  onOpenLifebound,
  onOpenArtifactSpirit,
  onOpenEncounter,
  onOpenPartnerChamber,
  onOpenAncientTomb,
  onToggleCodex,
}: TopbarNavRibbonProps) {
  const [activeSanctuary, setActiveSanctuary] = useState<SanctuaryId>(null)
  const ribbonRef = useRef<HTMLDivElement>(null)

  // 点击外部自动收起气泡菜单
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (ribbonRef.current && !ribbonRef.current.contains(e.target as Node)) {
        setActiveSanctuary(null)
      }
    }
    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  const toggle = (id: SanctuaryId) => {
    setActiveSanctuary((prev) => (prev === id ? null : id))
  }

  const handleSelect = (callback: () => void) => {
    setActiveSanctuary(null)
    callback()
  }

  return (
    <nav
      className="xianxia-sanctuary-nav"
      ref={ribbonRef}
      aria-label="九州修真核心系统大类"
    >
      {/* 1. 道途本纪 */}
      <div
        className={`sanctuary-capsule-wrap ${activeSanctuary === 'chronicle' ? 'open' : ''}`}
      >
        <button
          type="button"
          className="sanctuary-capsule-trigger"
          onClick={() => toggle('chronicle')}
          aria-expanded={activeSanctuary === 'chronicle'}
        >
          <Mountain size={15} className="capsule-icon" />
          <span className="capsule-title">道途本纪</span>
          <ChevronDown size={13} className="capsule-arrow" />
        </button>

        {activeSanctuary === 'chronicle' && (
          <div className="sanctuary-popover" role="menu">
            <div className="popover-header">
              <Mountain size={14} />
              <span>道途修行 · 指津本纪</span>
            </div>
            <button
              type="button"
              className="popover-item"
              onClick={() => handleSelect(onOpenRealmsLadder)}
            >
              <div className="popover-item-icon">
                <Mountain size={16} />
              </div>
              <div className="popover-item-text">
                <strong>通天仙阶</strong>
                <small>仙道十重天境界图谱，直观俯瞰登仙道梯</small>
              </div>
            </button>
            <button
              type="button"
              className="popover-item"
              onClick={() => handleSelect(onOpenGuide)}
            >
              <div className="popover-item-icon">
                <Compass size={16} />
              </div>
              <div className="popover-item-text">
                <strong>仙途指津</strong>
                <small>“如果想要什么，你可以去哪里干什么”行止向导</small>
              </div>
            </button>
            {onToggleCodex && (
              <button
                type="button"
                className="popover-item"
                onClick={() => handleSelect(onToggleCodex)}
              >
                <div className="popover-item-icon">
                  <BookOpen size={16} />
                </div>
                <div className="popover-item-text">
                  <strong>洞天卷宗</strong>
                  <small>名帖属性、储物行囊、四海人脉与九州风声</small>
                </div>
              </button>
            )}
          </div>
        )}
      </div>

      {/* 2. 九州风云 */}
      <div
        className={`sanctuary-capsule-wrap ${activeSanctuary === 'world' ? 'open' : ''}`}
      >
        <button
          type="button"
          className={`sanctuary-capsule-trigger ${hasPendingEncounter ? 'pulse-urgent' : ''}`}
          onClick={() => toggle('world')}
          aria-expanded={activeSanctuary === 'world'}
        >
          <Landmark size={15} className="capsule-icon" />
          <span className="capsule-title">九州风云</span>
          {hasPendingEncounter && <span className="capsule-urgent-dot" />}
          <ChevronDown size={13} className="capsule-arrow" />
        </button>

        {activeSanctuary === 'world' && (
          <div className="sanctuary-popover" role="menu">
            <div className="popover-header">
              <Landmark size={14} />
              <span>九州仙门 · 风云机缘</span>
            </div>
            <button
              type="button"
              className="popover-item"
              onClick={() => handleSelect(() => onOpenSectGate())}
            >
              <div className="popover-item-icon">
                <Landmark size={16} />
              </div>
              <div className="popover-item-text">
                <strong>拜山请益</strong>
                <small>走访各大名山宗门，求丹借宝、演武与承接悬赏</small>
              </div>
            </button>
            <button
              type="button"
              className="popover-item"
              onClick={() => handleSelect(onOpenTianji)}
            >
              <div className="popover-item-icon">
                <Trophy size={16} />
              </div>
              <div className="popover-item-text">
                <strong>天机风云谱</strong>
                <small>青云潜龙榜、九天巨擘榜、宗门势力榜与天机阁</small>
              </div>
            </button>
            <button
              type="button"
              className={`popover-item ${hasPendingEncounter ? 'highlight-item' : ''}`}
              onClick={() => handleSelect(onOpenEncounter)}
            >
              <div className="popover-item-icon">
                <ScrollText size={16} />
              </div>
              <div className="popover-item-text">
                <div className="item-title-row">
                  <strong>红尘奇遇</strong>
                  {hasPendingEncounter && (
                    <span className="urgent-badge">机缘待决</span>
                  )}
                </div>
                <small>太古秘境古仙遗蜕、故人因果与灵宠奇遇画卷</small>
              </div>
            </button>
            {onOpenCommissionBoard && (
              <button
                type="button"
                className={`popover-item ${hasReadyCommission ? 'highlight-item' : ''}`}
                onClick={() => handleSelect(onOpenCommissionBoard)}
              >
                <div className="popover-item-icon">
                  <ClipboardList size={16} />
                </div>
                <div className="popover-item-text">
                  <div className="item-title-row">
                    <strong>东洲悬榜</strong>
                    {hasReadyCommission && (
                      <span className="urgent-badge">有酬待领</span>
                    )}
                  </div>
                  <small>揭阅四方悬赏生财，接取采药除祟差事赚取丰厚灵石</small>
                </div>
              </button>
            )}
          </div>
        )}
      </div>

      {/* 3. 洞天造化 */}
      <div
        className={`sanctuary-capsule-wrap ${activeSanctuary === 'mysteries' ? 'open' : ''}`}
      >
        <button
          type="button"
          className="sanctuary-capsule-trigger"
          onClick={() => toggle('mysteries')}
          aria-expanded={activeSanctuary === 'mysteries'}
        >
          <Sparkles size={15} className="capsule-icon" />
          <span className="capsule-title">洞天造化</span>
          <ChevronDown size={13} className="capsule-arrow" />
        </button>

        {activeSanctuary === 'mysteries' && (
          <div className="sanctuary-popover" role="menu">
            <div className="popover-header">
              <Sparkles size={14} />
              <span>本命造化 · 秘境同修</span>
            </div>
            <button
              type="button"
              className="popover-item"
              onClick={() => handleSelect(onOpenLifebound)}
            >
              <div className="popover-item-icon">
                <Sparkles size={16} />
              </div>
              <div className="popover-item-text">
                <strong>本命灵宝</strong>
                <small>九重太古器纹铭刻、神料熔铸与本命温养</small>
              </div>
            </button>
            <button
              type="button"
              className="popover-item"
              onClick={() => handleSelect(onOpenArtifactSpirit)}
            >
              <div className="popover-item-icon">
                <Sparkles size={16} />
              </div>
              <div className="popover-item-text">
                <strong>器灵化形</strong>
                <small>本命真灵觉醒、独立人形侍从伙伴与护道神通</small>
              </div>
            </button>
            <button
              type="button"
              className="popover-item"
              onClick={() => handleSelect(onOpenPartnerChamber)}
            >
              <div className="popover-item-icon">
                <HeartHandshake size={16} />
              </div>
              <div className="popover-item-text">
                <strong>仙侣同修阁</strong>
                <small>道侣合道法印、本命心印传音、情魔渡劫与仙嗣</small>
              </div>
            </button>
            <button
              type="button"
              className="popover-item"
              onClick={() => handleSelect(onOpenAncientTomb)}
            >
              <div className="popover-item-icon">
                <Compass size={16} />
              </div>
              <div className="popover-item-text">
                <strong>太古古墓秘境</strong>
                <small>迷雾格子探险 Roguelike，破阵开匣与大能遗宝</small>
              </div>
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
