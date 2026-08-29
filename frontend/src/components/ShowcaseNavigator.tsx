import { CheckCircle2, ChevronLeft, ChevronRight, Eye, X } from 'lucide-react'
import type { ShowcasePage } from '../api/types'

interface ShowcaseNavigatorProps {
  pages: ShowcasePage[]
  index: number
  onIndex: (index: number) => void
  onExit: () => void
}

export function ShowcaseNavigator({ pages, index, onIndex, onExit }: ShowcaseNavigatorProps) {
  const page = pages[index]
  if (!page) return null
  const progress = Math.round(((index + 1) / pages.length) * 100)
  return (
    <aside className="showcase-navigator" aria-label="成果巡览控制器">
      <header><div><span><Eye size={14} />只读巡览</span><h2>新版成果验收</h2></div><button type="button" onClick={onExit} aria-label="退出成果巡览"><X size={17} /></button></header>
      <div className="showcase-progress"><span>{String(index + 1).padStart(2, '0')} / {String(pages.length).padStart(2, '0')}</span><i><b style={{ width: `${progress}%` }} /></i></div>
      <label>当前展示页面<select value={index} onChange={(event) => onIndex(Number(event.target.value))}>{pages.map((item, itemIndex) => <option value={itemIndex} key={item.id}>{item.title}</option>)}</select></label>
      <section><h3>{page.title}</h3><p>{page.description}</p><ul>{page.checklist.map((item) => <li key={item}><CheckCircle2 size={13} />{item}</li>)}</ul></section>
      <footer><button type="button" disabled={index === 0} onClick={() => onIndex(index - 1)}><ChevronLeft size={15} />上一页</button><button type="button" onClick={index === pages.length - 1 ? onExit : () => onIndex(index + 1)}>{index === pages.length - 1 ? '完成巡览' : '下一页'}{index < pages.length - 1 && <ChevronRight size={15} />}</button></footer>
    </aside>
  )
}
