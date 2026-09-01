import { describe, expect, it } from 'vitest'
import {
  buildShowcaseReviewSummary,
  createShowcaseReview,
  parseShowcaseReview,
} from './showcaseReview'

const pages = [
  { id: 'home', title: '洞府主界面' },
  { id: 'battle', title: '临阵抉择' },
  { id: 'ending', title: '仙途评传' },
]

describe('showcase review', () => {
  it('resets malformed and older-version progress', () => {
    expect(parseShowcaseReview('{broken', pages, '0.60.0')).toEqual(createShowcaseReview(pages, '0.60.0'))
    expect(parseShowcaseReview(JSON.stringify({ schemaVersion: 1, appVersion: '0.59.0', completedIds: ['home'] }), pages, '0.60.0')).toEqual(createShowcaseReview(pages, '0.60.0'))
  })

  it('keeps only known pages and bounded notes', () => {
    const review = parseShowcaseReview(JSON.stringify({
      schemaVersion: 1,
      appVersion: '0.60.0',
      currentId: 'battle',
      completedIds: ['unknown', 'battle', 'home', 'battle'],
      notes: { battle: '按钮在窄屏被遮挡', unknown: '不应保留', ending: 'x'.repeat(800) },
    }), pages, '0.60.0')
    expect(review.currentId).toBe('battle')
    expect(review.completedIds).toEqual(['home', 'battle'])
    expect(review.notes.unknown).toBeUndefined()
    expect(review.notes.ending).toHaveLength(600)
  })

  it('builds a shareable summary without game-state fields', () => {
    const review = {
      ...createShowcaseReview(pages, '0.60.0'),
      completedIds: ['home'],
      notes: { battle: '  敌方情报需要更醒目\n一些  ' },
    }
    const summary = buildShowcaseReviewSummary(pages, review)
    expect(summary).toContain('已检查 1 页')
    expect(summary).toContain('[已检查] 01 · 洞府主界面')
    expect(summary).toContain('[待检查] 02 · 临阵抉择')
    expect(summary).toContain('临阵抉择：敌方情报需要更醒目 一些')
    expect(summary).toContain('不包含角色、存档、密钥或本机路径')
  })
})
