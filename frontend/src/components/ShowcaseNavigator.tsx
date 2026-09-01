import { Check, CheckCircle2, ChevronLeft, ChevronRight, ClipboardCopy, Eye, X } from 'lucide-react'
import { useState } from 'react'
import type { ShowcasePage } from '../api/types'
import {
  buildShowcaseReviewSummary,
  loadShowcaseReview,
  SHOWCASE_NOTE_LIMIT,
  storeShowcaseReview,
  type ShowcaseReview,
} from '../showcaseReview'

interface ShowcaseNavigatorProps {
  pages: ShowcasePage[]
  index: number
  appVersion: string
  onIndex: (index: number) => void
  onExit: () => void
}

async function copyText(text: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }
  const field = document.createElement('textarea')
  field.value = text
  field.style.position = 'fixed'
  field.style.opacity = '0'
  document.body.appendChild(field)
  field.select()
  const copied = document.execCommand('copy')
  field.remove()
  if (!copied) throw new Error('浏览器未允许复制。')
}

export function ShowcaseNavigator({ pages, index, appVersion, onIndex, onExit }: ShowcaseNavigatorProps) {
  const [review, setReview] = useState<ShowcaseReview>(() => loadShowcaseReview(pages, appVersion))
  const [copyStatus, setCopyStatus] = useState('')
  const page = pages[index]
  if (!page) return null
  const browseProgress = Math.round(((index + 1) / pages.length) * 100)
  const reviewProgress = pages.length ? Math.round((review.completedIds.length / pages.length) * 100) : 0
  const pageComplete = review.completedIds.includes(page.id)
  const updateReview = (next: ShowcaseReview) => {
    setReview(next)
    storeShowcaseReview(next)
    setCopyStatus('')
  }
  const navigate = (nextIndex: number) => {
    const nextPage = pages[nextIndex]
    if (!nextPage) return
    updateReview({ ...review, currentId: nextPage.id })
    onIndex(nextIndex)
  }
  const toggleComplete = () => {
    const selected = new Set(review.completedIds)
    if (selected.has(page.id)) selected.delete(page.id)
    else selected.add(page.id)
    updateReview({
      ...review,
      completedIds: pages.map((item) => item.id).filter((id) => selected.has(id)),
    })
  }
  const updateNote = (note: string) => {
    const notes = { ...review.notes }
    if (note.trim()) notes[page.id] = note.slice(0, SHOWCASE_NOTE_LIMIT)
    else delete notes[page.id]
    updateReview({ ...review, notes })
  }
  const copySummary = async () => {
    try {
      await copyText(buildShowcaseReviewSummary(pages, review))
      setCopyStatus('验收摘要已复制，可直接粘贴反馈。')
    } catch (reason) {
      setCopyStatus(reason instanceof Error ? reason.message : '复制失败，请稍后重试。')
    }
  }
  return (
    <aside className="showcase-navigator" aria-label="成果巡览控制器">
      <header><div><span><Eye size={14} />只读巡览</span><h2>新版成果验收</h2></div><button type="button" onClick={onExit} aria-label="退出成果巡览"><X size={17} /></button></header>
      <div className="showcase-progress"><span>浏览 {String(index + 1).padStart(2, '0')} / {String(pages.length).padStart(2, '0')}</span><i><b style={{ width: `${browseProgress}%` }} /></i></div>
      <div className="showcase-review-progress"><span>已验收 {review.completedIds.length} / {pages.length}</span><i><b style={{ width: `${reviewProgress}%` }} /></i></div>
      <label>当前展示页面<select value={index} onChange={(event) => navigate(Number(event.target.value))}>{pages.map((item, itemIndex) => <option value={itemIndex} key={item.id}>{review.completedIds.includes(item.id) ? '✓ ' : ''}{item.title}</option>)}</select></label>
      <section data-complete={pageComplete || undefined}><div className="showcase-page-title"><h3>{page.title}</h3>{pageComplete && <span><Check size={12} />已检查</span>}</div><p>{page.description}</p><ul>{page.checklist.map((item) => <li key={item}><CheckCircle2 size={13} />{item}</li>)}</ul><button className="showcase-check-button" data-complete={pageComplete || undefined} type="button" onClick={toggleComplete}><Check size={14} />{pageComplete ? '取消本页已检查' : '标记本页已检查'}</button><details className="showcase-notes"><summary>记录本页问题或建议</summary><textarea value={review.notes[page.id] || ''} maxLength={SHOWCASE_NOTE_LIMIT} onChange={(event) => updateNote(event.target.value)} placeholder="例如：手机宽度下按钮被遮挡；只保存在当前浏览器中。" /><small>{(review.notes[page.id] || '').length} / {SHOWCASE_NOTE_LIMIT}</small></details></section>
      {copyStatus && <p className="showcase-copy-status" role="status">{copyStatus}</p>}
      <footer><button type="button" disabled={index === 0} onClick={() => navigate(index - 1)}><ChevronLeft size={15} />上一页</button><button type="button" onClick={() => void copySummary()}><ClipboardCopy size={14} />复制摘要</button><button type="button" onClick={index === pages.length - 1 ? onExit : () => navigate(index + 1)}>{index === pages.length - 1 ? review.completedIds.length === pages.length ? '完成并退出' : '暂时退出' : '下一页'}{index < pages.length - 1 && <ChevronRight size={15} />}</button></footer>
    </aside>
  )
}
