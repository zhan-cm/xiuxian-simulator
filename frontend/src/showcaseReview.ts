import type { ShowcasePage } from './api/types'

export const SHOWCASE_REVIEW_STORAGE_KEY = 'xiuxian-showcase-review-v1'
export const SHOWCASE_REVIEW_SCHEMA = 1
export const SHOWCASE_NOTE_LIMIT = 600

type ReviewPage = Pick<ShowcasePage, 'id' | 'title'>

export interface ShowcaseReview {
  schemaVersion: number
  appVersion: string
  currentId: string
  completedIds: string[]
  notes: Record<string, string>
}

export function createShowcaseReview(pages: ReviewPage[], appVersion: string): ShowcaseReview {
  return {
    schemaVersion: SHOWCASE_REVIEW_SCHEMA,
    appVersion,
    currentId: pages[0]?.id || '',
    completedIds: [],
    notes: {},
  }
}

export function parseShowcaseReview(raw: string | null, pages: ReviewPage[], appVersion: string): ShowcaseReview {
  const empty = createShowcaseReview(pages, appVersion)
  if (!raw) return empty
  try {
    const value = JSON.parse(raw) as Partial<ShowcaseReview>
    if (value.schemaVersion !== SHOWCASE_REVIEW_SCHEMA || value.appVersion !== appVersion) return empty
    const pageIds = new Set(pages.map((page) => page.id))
    const completedIds = pages
      .map((page) => page.id)
      .filter((id) => Array.isArray(value.completedIds) && value.completedIds.includes(id))
    const sourceNotes = value.notes && typeof value.notes === 'object' ? value.notes : {}
    const notes = Object.fromEntries(
      Object.entries(sourceNotes)
        .filter(([id, note]) => pageIds.has(id) && typeof note === 'string' && note.trim())
        .map(([id, note]) => [id, note.slice(0, SHOWCASE_NOTE_LIMIT)]),
    )
    return {
      schemaVersion: SHOWCASE_REVIEW_SCHEMA,
      appVersion,
      currentId: typeof value.currentId === 'string' && pageIds.has(value.currentId) ? value.currentId : empty.currentId,
      completedIds,
      notes,
    }
  } catch {
    return empty
  }
}

export function loadShowcaseReview(pages: ReviewPage[], appVersion: string): ShowcaseReview {
  try {
    return parseShowcaseReview(window.localStorage.getItem(SHOWCASE_REVIEW_STORAGE_KEY), pages, appVersion)
  } catch {
    return createShowcaseReview(pages, appVersion)
  }
}

export function storeShowcaseReview(review: ShowcaseReview): void {
  try {
    window.localStorage.setItem(SHOWCASE_REVIEW_STORAGE_KEY, JSON.stringify(review))
  } catch {
    // Browsers may disable local storage. The current review still works in memory.
  }
}

export function buildShowcaseReviewSummary(
  pages: ReviewPage[],
  review: ShowcaseReview,
): string {
  const completed = new Set(review.completedIds)
  const lines = [
    `《问道长生》V${review.appVersion} 玩家验收摘要`,
    `成果巡览：${pages.length} 页｜已检查 ${review.completedIds.length} 页｜待检查 ${Math.max(0, pages.length - review.completedIds.length)} 页`,
    '',
    '页面状态：',
    ...pages.map((page, index) => `${completed.has(page.id) ? '[已检查]' : '[待检查]'} ${String(index + 1).padStart(2, '0')} · ${page.title}`),
  ]
  const notedPages = pages.filter((page) => review.notes[page.id]?.trim())
  if (notedPages.length) {
    lines.push('', '玩家备注：')
    for (const page of notedPages) {
      lines.push(`- ${page.title}：${review.notes[page.id].trim().replace(/\s+/g, ' ')}`)
    }
  }
  lines.push('', '隐私说明：此摘要只包含巡览勾选状态和手写备注，不包含角色、存档、密钥或本机路径。')
  return lines.join('\n')
}
