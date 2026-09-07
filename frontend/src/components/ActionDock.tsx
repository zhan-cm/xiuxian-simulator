import { ArrowUpRight, BedDouble, BookOpenCheck, Compass, MoonStar, MountainSnow, Save, ScrollText, Sparkles, Waves } from 'lucide-react'
import type { RecoverySnapshot } from '../api/types'
import { useUiStore } from '../store/ui'

const quickActions = [
  { action: '修炼', label: '吐纳修炼', icon: Sparkles },
  { action: '闭关3月', label: '闭关三月', icon: MoonStar },
  { action: '存档', label: '保存进度', icon: Save },
]

const drafts = ['去坊市打听最近的秘境传闻', '谨慎探索青岳山麓', '拜访一位相识修士并询问近况']

export interface ContextAction {
  action: string
  label: string
  description: string
  tone: 'breakthrough' | 'story' | 'commission' | 'world'
}

const contextIcons = { breakthrough: MountainSnow, story: BookOpenCheck, commission: ScrollText, world: Waves }

interface ActionDockProps {
  busy: boolean
  canQuickAct: boolean
  canDraft: boolean
  readOnly?: boolean
  recovery?: RecoverySnapshot
  contextActions?: ContextAction[]
  onAction: (action: string) => void
}

export function ActionDock({ busy, canQuickAct, canDraft, readOnly = false, recovery, contextActions = [], onAction }: ActionDockProps) {
  const { draft, setDraft, clearDraft } = useUiStore()
  const submit = () => {
    if (!draft.trim() || busy || readOnly || !canDraft) return
    onAction(draft.trim())
    clearDraft()
  }
  return (
    <section className="action-dock">
      <div className="quick-action-row" aria-label="一键行动">
        <span>一键行动</span>
        {recovery?.active && <button type="button" disabled={!canQuickAct || busy || readOnly || !recovery.can_rest} title={readOnly ? '成果巡览仅供查看' : !canQuickAct ? '请先完成当前抉择' : recovery.can_rest ? '静养一个月，恢复伤势' : recovery.rest_reason} onClick={() => onAction(recovery.rest_action)}><BedDouble size={16} />静养疗伤</button>}
        {contextActions.slice(0, 1).map((item) => { const Icon = contextIcons[item.tone]; return <button className="context-action" type="button" data-tone={item.tone} key={item.action} disabled={!canQuickAct || busy || readOnly} onClick={() => onAction(item.action)} title={readOnly ? '成果巡览仅供查看' : item.description}><Icon size={16} /><span><strong>{item.label}</strong><small>{item.description}</small></span></button> })}
        {quickActions.map(({ action, label, icon: Icon }) => (
          <button type="button" key={action} disabled={!canQuickAct || busy || readOnly} onClick={() => onAction(action)} title={readOnly ? '成果巡览仅供查看' : canQuickAct ? `立即执行：${label}` : '请先完成当前抉择'}>
            <Icon size={16} />{label}
          </button>
        ))}
      </div>
      <div className="draft-row">
        <span><Compass size={14} />行动草稿</span>
        {drafts.map((item) => <button type="button" key={item} disabled={!canDraft || busy || readOnly} onClick={() => setDraft(item)}>{item.replace('最近的', '').replace('一位', '')}</button>)}
        <small>点击后仍可修改，推演此行才会生效</small>
      </div>
      <div className="action-input-row">
        <textarea aria-label="行动草稿" disabled={!canDraft || busy || readOnly} value={draft} onChange={(event) => setDraft(event.target.value)} maxLength={2000} rows={2} placeholder={readOnly ? '成果巡览中不会执行行动' : canDraft ? '描述你想做的事，也可以点击上方行动草稿' : '请先完成上方抉择'} />
        <button type="button" disabled={!canDraft || !draft.trim() || busy || readOnly} onClick={submit}>{busy ? '推演中…' : '推演此行'}<ArrowUpRight size={17} /></button>
      </div>
    </section>
  )
}
