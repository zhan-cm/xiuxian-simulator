import { useState } from 'react'
import {
  ArrowUpRight,
  Award,
  BedDouble,
  BookOpenCheck,
  Castle,
  ChevronDown,
  Coins,
  Compass,
  Flame,
  Globe,
  Hammer,
  Heart,
  Landmark,
  Layers,
  Map,
  MoonStar,
  MountainSnow,
  Package,
  Save,
  ScrollText,
  Shield,
  Sparkles,
  Store,
  Sun,
  Users,
  Waves,
  type LucideIcon,
} from 'lucide-react'
import type { PendingEncounterData, RecoverySnapshot } from '../api/types'
import { useUiStore } from '../store/ui'

export interface ContextAction {
  action: string
  label: string
  description: string
  tone: 'breakthrough' | 'story' | 'commission' | 'world'
}

const contextIcons: Record<ContextAction['tone'], LucideIcon> = {
  breakthrough: MountainSnow,
  story: BookOpenCheck,
  commission: ScrollText,
  world: Waves,
}

const drafts = ['去坊市打听最近的秘境传闻', '谨慎探索青岳山麓', '拜访一位相识修士并询问近况']

export type ActionCategory = 'cultivation' | 'adventure' | 'economy' | 'social'

export interface SelectableActionItem {
  action: string
  label: string
  desc: string
  icon: LucideIcon
}

export const CATEGORIES: { id: ActionCategory; name: string; icon: LucideIcon }[] = [
  { id: 'cultivation', name: '潜修', icon: Sparkles },
  { id: 'adventure', name: '历练', icon: Compass },
  { id: 'economy', name: '生财', icon: Coins },
  { id: 'social', name: '红尘', icon: Users },
]

export const CATEGORY_ACTIONS: Record<ActionCategory, SelectableActionItem[]> = {
  cultivation: [
    { action: '修炼', label: '吐纳修炼', desc: '纳天地灵气，增进当前修为', icon: Sparkles },
    { action: '闭关3月', label: '闭关三月', desc: '避世清修，加速道行破关', icon: MoonStar },
    { action: '观想', label: '观想天地', desc: '静思参悟，凝练大道感悟', icon: Sun },
    { action: '消化感悟', label: '消化感悟', desc: '转化感悟心得，研习道法', icon: BookOpenCheck },
    { action: '道法', label: '研习道法', desc: '参阅门派心法与攻伐道术', icon: Flame },
    { action: '法宝', label: '器阁温养', desc: '温养本命法宝，淬炼灵威', icon: Shield },
  ],
  adventure: [
    { action: '探索 青岳山麓', label: '探索山麓', desc: '巡游近郊灵山，搜寻药草灵物', icon: MountainSnow },
    { action: '秘境', label: '探查秘境', desc: '寻访古仙洞府与天机秘境', icon: Compass },
    { action: '地方机缘', label: '寻访机缘', desc: '探访所在地域，触发风土奇遇', icon: Sparkles },
    { action: '探寻灵兽', label: '巡山觅兽', desc: '深入山林，寻觅通灵异兽', icon: Sun },
    { action: '地图', label: '九州舆图', desc: '纵览神州五域，筹备跨州游历', icon: Map },
    { action: '推进主线', label: '探寻命数', desc: '叩问宿命因果，推进主线机缘', icon: ScrollText },
  ],
  economy: [
    { action: '坊市', label: '前往坊市', desc: '步入修士坊市，买卖丹药法宝', icon: Store },
    { action: '委托', label: '悬赏榜单', desc: '揭阅东洲悬榜，承接任务赚取灵石', icon: ScrollText },
    { action: '拍卖会', label: '天机竞价', desc: '赴天机阁拍卖盛会，竞购珍宝', icon: Landmark },
    { action: '背包', label: '清点乾坤', desc: '盘点储物袋中的灵石丹药与法宝', icon: Package },
    { action: '技艺', label: '百工造诣', desc: '开炉炼丹或锻制法器', icon: Hammer },
    { action: '存档', label: '保存进度', desc: '将当前修仙命盘存入洞天卷宗', icon: Save },
  ],
  social: [
    { action: '宗门', label: '仙门重地', desc: '拜谒宗门长辈，承接内务或晋升', icon: Castle },
    { action: '情缘', label: '同道知己', desc: '拜访红颜知己，结伴修行论道', icon: Heart },
    { action: '人脉', label: '天下人脉', desc: '纵览四海交游缘网，打听同道近况', icon: Users },
    { action: '道途', label: '道途章程', desc: '查验大道修行目标与里程碑奖励', icon: Award },
    { action: '天下', label: '神州大事', desc: '洞悉仙门风云与灵潮劫波动态', icon: Globe },
    { action: '宗门外交', label: '宗门外务', desc: '遣使结盟或宣战，运筹修真界', icon: Shield },
  ],
}

export const CORE_FOCUS_ACTIONS: SelectableActionItem[] = [
  { action: '修炼', label: '吐纳修炼', desc: '纳天地灵气，增进当前修为', icon: Sparkles },
  { action: '闭关3月', label: '闭关三月', desc: '避世清修悟道，加速道行破关', icon: MoonStar },
  { action: '探索 青岳山麓', label: '巡游历练', desc: '巡游近郊灵山，搜寻药草灵物', icon: MountainSnow },
  { action: '委托', label: '悬赏榜单', desc: '揭阅东洲悬榜，接单除祟赚取灵石', icon: ScrollText },
  { action: '坊市', label: '前往坊市', desc: '步入修士坊市，买卖丹药法宝', icon: Store },
]

interface ActionDockProps {
  busy: boolean
  canQuickAct: boolean
  canDraft: boolean
  readOnly?: boolean
  recovery?: RecoverySnapshot
  contextActions?: ContextAction[]
  pendingEncounter?: PendingEncounterData | null
  initialMode?: 'focus' | 'all'
  onOpenEncounterModal?: () => void
  onOpenCommissionBoard?: () => void
  onAction: (action: string) => void
}

export function ActionDock({
  busy,
  canQuickAct,
  canDraft,
  readOnly = false,
  recovery,
  contextActions = [],
  pendingEncounter,
  initialMode = 'all',
  onOpenEncounterModal,
  onOpenCommissionBoard,
  onAction,
}: ActionDockProps) {
  const [activeCategory, setActiveCategory] = useState<ActionCategory>('cultivation')
  const [viewMode, setViewMode] = useState<'focus' | 'all'>(initialMode)
  const [customDraftOpen, setCustomDraftOpen] = useState(false)
  const { draft, setDraft, clearDraft } = useUiStore()

  const submit = () => {
    if (!draft.trim() || busy || readOnly || !canDraft) return
    onAction(draft.trim())
    clearDraft()
  }

  const currentActions = CATEGORY_ACTIONS[activeCategory] || []

  return (
    <section className="action-dock" aria-label="心念决策台">
      {/* 红尘奇遇未决提示条 */}
      {pendingEncounter && (
        <div className="dock-encounter-pending-banner" role="status">
          <ScrollText size={18} />
          <div>
            <strong>【红尘机缘待定】</strong>
            <p>需定夺当前奇遇道心因果，方可重续日常吐纳与历练。</p>
          </div>
          {onOpenEncounterModal && (
            <button
              type="button"
              className="dock-encounter-reopen-btn"
              onClick={onOpenEncounterModal}
              title="重新唤出红尘机缘画卷"
            >
              展开画卷
            </button>
          )}
        </div>
      )}

      {/* 临机要务：突破机缘与伤势静养 */}
      {(recovery?.active || contextActions.length > 0) && (
        <div className="dock-priority-banner" aria-label="临机要务">
          {recovery?.active && (
            <button
              type="button"
              className="dock-recovery-btn"
              aria-label="静养疗伤"
              disabled={!canQuickAct || busy || readOnly || !recovery.can_rest}
              title={
                readOnly
                  ? '成果巡览仅供查看'
                  : !canQuickAct
                    ? '请先完成当前抉择'
                    : recovery.can_rest
                      ? '静养一个月，恢复伤势'
                      : recovery.rest_reason
              }
              onClick={() => onAction(recovery.rest_action)}
            >
              <BedDouble size={16} />
              <span>
                <strong>静养疗伤</strong>
                <small>{recovery.can_rest ? '避战潜修静养以平复经络' : recovery.rest_reason}</small>
              </span>
            </button>
          )}
          {contextActions.slice(0, 1).map((item) => {
            const Icon = contextIcons[item.tone]
            return (
              <button
                className="context-action dock-breakthrough-btn"
                type="button"
                data-tone={item.tone}
                key={item.action}
                disabled={!canQuickAct || busy || readOnly}
                onClick={() => onAction(item.action)}
                title={readOnly ? '成果巡览仅供查看' : item.description}
              >
                <Icon size={16} />
                <span>
                  <strong>{item.label}</strong>
                  <small>{item.description}</small>
                </span>
              </button>
            )
          })}
        </div>
      )}

      {/* 意境导引标题与模式切换 */}
      <div className="dock-header">
        <span className="dock-title">
          <Sparkles size={14} />
          <strong>{viewMode === 'focus' ? '日常潜修' : '万象罗盘'}</strong>
        </span>
        <button
          type="button"
          className="dock-viewmode-toggle-btn"
          onClick={() => setViewMode((prev) => (prev === 'focus' ? 'all' : 'focus'))}
          title={viewMode === 'focus' ? '展开全量24门心念罗盘' : '收起为极简日常潜修模式'}
        >
          <Layers size={13} />
          <span>{viewMode === 'focus' ? '展开万象' : '极简修行'}</span>
        </button>
      </div>

      {/* 分类心念选项卡（仅在万象模式下展示） */}
      {viewMode === 'all' && (
        <div className="dock-category-bar" role="tablist" aria-label="行动分类选项">
          {CATEGORIES.map((cat) => {
            const CatIcon = cat.icon
            const isActive = activeCategory === cat.id
            return (
              <button
                type="button"
                role="tab"
                aria-selected={isActive}
                key={cat.id}
                className={`dock-category-tab ${isActive ? 'active' : ''}`}
                onClick={() => setActiveCategory(cat.id)}
              >
                <CatIcon size={13} />
                <span>{cat.name}</span>
              </button>
            )
          })}
        </div>
      )}

      {/* 可选心念卡片网格 */}
      <div
        className={`dock-action-grid ${viewMode === 'focus' ? 'mode-focus' : 'mode-all'}`}
        role="tabpanel"
        aria-label={viewMode === 'focus' ? '日常潜修心念' : `${CATEGORIES.find((c) => c.id === activeCategory)?.name}心念`}
      >
        {(viewMode === 'focus' ? CORE_FOCUS_ACTIONS : currentActions).map((item) => {
          const ActionIcon = item.icon
          return (
            <button
              type="button"
              key={item.action}
              className="dock-action-card"
              aria-label={item.label}
              disabled={!canQuickAct || busy || readOnly}
              onClick={() => {
                if (item.action === '委托' && onOpenCommissionBoard) {
                  onOpenCommissionBoard()
                } else {
                  onAction(item.action)
                }
              }}
              title={
                readOnly
                  ? '成果巡览仅供查看'
                  : !canQuickAct
                    ? '请先完成当前抉择'
                    : `立即执行：${item.label} (${item.desc})`
              }
            >
              <span className="action-card-icon-wrap">
                <ActionIcon size={15} />
              </span>
              <span className="action-card-text">
                <strong className="action-card-label">{item.label}</strong>
                <small className="action-card-desc">{item.desc}</small>
              </span>
            </button>
          )
        })}
      </div>

      {/* 自定心念折叠区（为高阶自定推演提供输入框，兼容原有测试与自定义需要） */}
      <div className="custom-draft-container">
        <button
          type="button"
          className="custom-draft-toggle"
          onClick={() => setCustomDraftOpen(!customDraftOpen)}
          aria-expanded={customDraftOpen}
        >
          <span className="toggle-left">
            <Compass size={13} />
            <strong>自定义心念草稿</strong>
            <small>（新手无需使用，点选上方卡片即可）</small>
          </span>
          <ChevronDown size={14} className={`toggle-chevron ${customDraftOpen ? 'open' : ''}`} />
        </button>

        <div className={`custom-draft-body ${customDraftOpen ? 'open' : ''}`}>
          <div className="draft-row">
            <span>草稿预填</span>
            {drafts.map((item) => (
              <button
                type="button"
                key={item}
                disabled={!canDraft || busy || readOnly}
                onClick={() => {
                  setDraft(item)
                  setCustomDraftOpen(true)
                }}
              >
                {item.replace('最近的', '').replace('一位', '')}
              </button>
            ))}
          </div>
          <div className="action-input-row">
            <textarea
              aria-label="行动草稿"
              disabled={!canDraft || busy || readOnly}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              maxLength={2000}
              rows={2}
              placeholder={
                readOnly
                  ? '成果巡览中不会执行行动'
                  : canDraft
                    ? '若有独门奇思妙想，可在此书写后推演…'
                    : '请先完成上方抉择'
              }
            />
            <button
              type="button"
              disabled={!canDraft || !draft.trim() || busy || readOnly}
              onClick={submit}
            >
              {busy ? '推演中…' : '推演此行'}
              <ArrowUpRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}
