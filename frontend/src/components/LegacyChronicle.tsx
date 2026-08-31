import { BookOpenText, Compass, Crown, Flame, HeartHandshake, MapPinned, RotateCcw, ScrollText, Sparkles, Waypoints } from 'lucide-react'
import type { LegacySnapshot } from '../api/types'

interface Props {
  legacy: LegacySnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

const metrics = [
  ['regions', '踏访地域', MapPinned],
  ['story', '主线篇章', BookOpenText],
  ['relations', '尘缘人物', HeartHandshake],
  ['commissions', '完成委托', ScrollText],
  ['dao_levels', '悟道层数', Sparkles],
  ['beasts', '灵兽同伴', Waypoints],
] as const

export function LegacyChronicle({ legacy, busy, readOnly = false, onAction }: Props) {
  if (!legacy.ended || !legacy.latest.life) return null
  const life = legacy.latest
  return (
    <section className="legacy-ending">
      <header className="legacy-heading">
        <span><RotateCcw size={22} /></span>
        <div><small>第 {life.life} 世 · 道途已终</small><h2>仙途评传</h2><p>{life.name} · 道号 {life.dao_name}｜{life.sect}｜{life.realm}</p></div>
        <div className="legacy-rank"><small>{life.rank}</small><strong>{life.score}</strong><em>道途评分</em></div>
      </header>

      <div className="legacy-epilogue">
        <span>{String(life.dao_name || life.name).slice(0, 1)}</span>
        <div><small>天玄历 {life.year} 年 · 享年 {life.age}</small><h3>{life.cause}</h3><p>{life.epilogue}</p></div>
      </div>

      <div className="legacy-metrics">
        {metrics.map(([key, label, Icon]) => <div key={key}><Icon size={14} /><span><small>{label}</small><strong>{life.metrics?.[key] || 0}</strong></span></div>)}
      </div>

      <section className="legacy-highlights"><h3><Crown size={15} />本世留痕</h3><div>{life.highlights?.map((item) => <span key={item}>{item}</span>)}</div></section>

      <section className="legacy-choice-area">
        <header><div><small>一世只留一道 · 不抹去失败代价</small><h3>择一道痕，赠予来世</h3></div><em>{legacy.selected ? '轮回已定，仍可在启封前改选' : '等待亲自选择'}</em></header>
        <div className="legacy-options">
          {legacy.options.map((option) => (
            <article key={option.id} data-selected={option.selected || undefined}>
              <span>{option.mark}</span>
              <div><small>{option.selected ? '已铭入神魂' : '轮回余痕'}</small><h4>{option.name}</h4></div>
              <p>{option.summary}</p>
              <strong><Flame size={12} />{option.effect}</strong>
              <button type="button" disabled={busy || readOnly || option.selected} title={readOnly ? '巡览模式不会修改存档' : option.selected ? '当前已经选择此道传承' : option.effect} onClick={() => onAction(option.action)}>{option.selected ? '此痕已铭刻' : '铭刻此痕'}</button>
            </article>
          ))}
        </div>
      </section>

      <footer className="legacy-footer">
        <div><Compass size={16} /><span><small>历世卷宗</small><strong>已记录 {legacy.completed_lives} 世</strong></span></div>
        <button type="button" disabled={busy || readOnly || !legacy.can_begin_next} title={readOnly ? '巡览模式不会修改存档' : legacy.can_begin_next ? '保留评传并进入下一世创角' : '请先选择一道轮回传承'} onClick={() => onAction(legacy.begin_action)}><RotateCcw size={15} />{legacy.can_begin_next ? '启封下一世' : '先择一道传承'}</button>
      </footer>
    </section>
  )
}
