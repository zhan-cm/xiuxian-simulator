import { Compass, MapPin, ScrollText, UserRound } from 'lucide-react'
import type { Presentation, PresentationBlock } from '../api/types'

const text = (value: unknown, fallback = '') => typeof value === 'string' || typeof value === 'number' ? String(value) : fallback

function FactsBlock({ block }: { block: PresentationBlock }) {
  return (
    <section className="semantic-block">
      <header><ScrollText size={16} /><strong>{block.title || '本次结算'}</strong></header>
      <div className="fact-grid">
        {(block.items || []).map((item, index) => (
          <div className="fact-chip" key={`${text(item.label)}-${index}`}>
            <span>{text(item.label, '信息')}</span><strong>{text(item.value, '—')}</strong>
          </div>
        ))}
      </div>
    </section>
  )
}

function PeopleBlock({ block }: { block: PresentationBlock }) {
  return (
    <section className="semantic-block">
      <header><UserRound size={16} /><strong>{block.title || '人物牵绊'}</strong></header>
      <div className="person-grid">
        {(block.items || []).map((item, index) => (
          <article className="person-card" key={`${text(item.name)}-${index}`}>
            <span className="person-avatar">{text(item.name, '人').slice(0, 1)}</span>
            <div><strong>{text(item.name, '未知道友')}</strong><small>{text(item.identity || item.descriptor, '身份未明')}</small></div>
            <div className="person-tags"><span>{text(item.realm, '境界未明')}</span><span>好感 {text(item.affinity, '0')}</span></div>
          </article>
        ))}
      </div>
    </section>
  )
}

function LocationsBlock({ block, onAction }: { block: PresentationBlock; onAction: (action: string) => void }) {
  return (
    <section className="semantic-block location-block">
      <header><Compass size={16} /><strong>{block.title || '探索地图'}</strong><small>{block.legend}</small></header>
      <div className="location-grid">
        {(block.items || []).map((item, index) => {
          const accessible = item.accessible !== false
          const action = text(item.action, `探索 ${text(item.name)}`)
          return (
            <article className="location-card" data-tone={text(item.tone, 'safe')} key={`${text(item.name)}-${index}`}>
              <header><div><MapPin size={16} /><strong>{text(item.name, '未名之地')}</strong></div><span>{text(item.danger_label, '未知')} · {text(item.danger, '?')}</span></header>
              <small>准入：{text(item.requirement_label || item.requirement, '炼气境')}</small>
              <p>{text(item.description || item.help, '前路未明，需亲自踏勘。')}</p>
              <button type="button" disabled={!accessible} title={accessible ? '立即前往探索' : text(item.locked_reason, '当前无法进入')} onClick={() => onAction(action)}>
                {accessible ? '前往探索' : text(item.locked_reason, '尚未解锁')}
              </button>
            </article>
          )
        })}
      </div>
    </section>
  )
}

function MeterBlock({ block }: { block: PresentationBlock }) {
  const value = Number(block.value || 0)
  const max = Number(block.max || 100)
  return (
    <section className="semantic-block meter-block">
      <header><strong>{block.title || '局势变化'}</strong><span>{value} / {max}</span></header>
      <div><i style={{ width: `${Math.max(0, Math.min(100, value * 100 / max))}%` }} /></div>
    </section>
  )
}

function GenericBlock({ block }: { block: PresentationBlock }) {
  return (
    <section className="semantic-block">
      <header><ScrollText size={16} /><strong>{block.title || '相关信息'}</strong></header>
      <div className="generic-list">
        {(block.items || []).map((item, index) => (
          <div key={index}><strong>{text(item.name || item.label || item.title, `记录 ${index + 1}`)}</strong><span>{text(item.value || item.description || item.summary)}</span></div>
        ))}
      </div>
    </section>
  )
}

function Block({ block, onAction }: { block: PresentationBlock; onAction: (action: string) => void }) {
  if (block.type === 'facts') return <FactsBlock block={block} />
  if (block.type === 'people') return <PeopleBlock block={block} />
  if (block.type === 'locations') return <LocationsBlock block={block} onAction={onAction} />
  if (block.type === 'meter') return <MeterBlock block={block} />
  return <GenericBlock block={block} />
}

export function EventPanel({ presentation, onAction }: { presentation: Presentation; onAction: (action: string) => void }) {
  return (
    <article className="event-panel" data-tone={presentation.tone || 'story'}>
      <div className="event-ornament" aria-hidden="true" />
      <header className="event-heading">
        <span className="event-seal">{presentation.seal || '道'}</span>
        <div><p>{presentation.eyebrow || '当前道途'}</p><h2>{presentation.title || '灵气潮汐将至'}</h2></div>
      </header>
      <div className="event-copy">
        {(presentation.paragraphs || []).map((paragraph, index) => <p key={index}>{paragraph}</p>)}
      </div>
      {presentation.changes?.length > 0 && (
        <div className="change-row">
          {presentation.changes.map((change, index) => <span key={`${change.label}-${index}`}><small>{change.label}</small><strong>{change.value}</strong></span>)}
        </div>
      )}
      <div className="event-blocks">
        {(presentation.blocks || []).map((block, index) => <Block block={block} onAction={onAction} key={`${block.type}-${index}`} />)}
      </div>
      {presentation.has_details && (
        <details className="full-record"><summary>查看完整推演记录</summary><pre>{presentation.details}</pre></details>
      )}
    </article>
  )
}
