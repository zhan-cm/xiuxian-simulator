import { ArrowUpRight, Compass, Landmark, Map, MoonStar, Save, Sparkles } from 'lucide-react'
import { useUiStore } from '../store/ui'

const quickActions = [
  { action: '修炼', label: '吐纳修炼', icon: Sparkles },
  { action: '闭关3月', label: '闭关三月', icon: MoonStar },
  { action: '地图', label: '查看地图', icon: Map },
  { action: '坊市', label: '前往坊市', icon: Landmark },
  { action: '存档', label: '保存进度', icon: Save },
]

const drafts = ['去坊市打听最近的秘境传闻', '谨慎探索青岳山麓', '拜访一位相识修士并询问近况']

interface ActionDockProps {
  busy: boolean
  canQuickAct: boolean
  canDraft: boolean
  onAction: (action: string) => void
}

export function ActionDock({ busy, canQuickAct, canDraft, onAction }: ActionDockProps) {
  const { draft, setDraft, clearDraft } = useUiStore()
  const submit = () => {
    if (!draft.trim() || busy) return
    onAction(draft.trim())
    clearDraft()
  }
  return (
    <section className="action-dock">
      <div className="quick-action-row" aria-label="一键行动">
        <span>一键行动</span>
        {quickActions.map(({ action, label, icon: Icon }) => (
          <button type="button" key={action} disabled={!canQuickAct || busy} onClick={() => onAction(action)} title={canQuickAct ? `立即执行：${label}` : '请先完成当前抉择'}>
            <Icon size={16} />{label}
          </button>
        ))}
      </div>
      <div className="draft-row">
        <span><Compass size={14} />行动草稿</span>
        {drafts.map((item) => <button type="button" key={item} disabled={!canDraft || busy} onClick={() => setDraft(item)}>{item.replace('最近的', '').replace('一位', '')}</button>)}
        <small>点击后仍可修改，推演此行才会生效</small>
      </div>
      <div className="action-input-row">
        <textarea disabled={!canDraft || busy} value={draft} onChange={(event) => setDraft(event.target.value)} maxLength={2000} rows={2} placeholder={canDraft ? '描述你想做的事，也可以点击上方行动草稿' : '请先完成上方抉择'} />
        <button type="button" disabled={!canDraft || !draft.trim() || busy} onClick={submit}>{busy ? '推演中…' : '推演此行'}<ArrowUpRight size={17} /></button>
      </div>
    </section>
  )
}
