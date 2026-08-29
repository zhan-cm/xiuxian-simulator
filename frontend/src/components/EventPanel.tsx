import { Coins, Compass, FlaskConical, Hammer, Landmark, MapPin, ScrollText, ShoppingBag, Sprout, UserRound } from 'lucide-react'
import { useMemo, useState } from 'react'
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

function MarketBlock({ block, onAction }: { block: PresentationBlock; onAction: (action: string) => void }) {
  const items = useMemo(() => block.items || [], [block.items])
  const categories = useMemo(() => ['全部', ...new Set(items.map((item) => text(item.category, '其他')))], [items])
  const [category, setCategory] = useState('全部')
  const shown = useMemo(() => category === '全部' ? items : items.filter((item) => item.category === category), [category, items])
  return (
    <section className="semantic-block market-block">
      <header><ShoppingBag size={16} /><strong>{block.title || '坊市货架'}</strong><small><Coins size={13} />持有 {text(block.currency, '0')} 灵石</small></header>
      <nav className="market-tabs" aria-label="货架分类">
        {categories.map((name) => <button type="button" data-active={category === name || undefined} onClick={() => setCategory(name)} key={name}>{name}</button>)}
      </nav>
      <div className="market-grid">
        {shown.map((item) => {
          const owned = Number(item.owned || 0)
          const affordable = item.affordable !== false
          return (
            <article className="market-item" key={text(item.name)}>
              <span className="item-glyph">{text(item.name, '物').slice(0, 1)}</span>
              <div className="market-copy"><strong>{text(item.name, '未鉴定物品')}</strong><small>{text(item.category, '修仙杂物')} · 持有 {owned}</small></div>
              <div className="market-prices"><button type="button" disabled={!affordable} title={affordable ? '买入一件' : '灵石不足'} onClick={() => onAction(text(item.buy_action))}>买 <b>{text(item.buy)}</b></button><button type="button" disabled={owned <= 0} title={owned > 0 ? '卖出一件' : '当前未持有'} onClick={() => onAction(text(item.sell_action))}>卖 <b>{text(item.sell)}</b></button></div>
            </article>
          )
        })}
      </div>
    </section>
  )
}

function FacilitiesBlock({ block, onAction }: { block: PresentationBlock; onAction: (action: string) => void }) {
  return (
    <section className="semantic-block facility-block">
      <header><Landmark size={16} /><strong>{block.title || '洞府设施'}</strong><small>灵气 {text(block.aura, '普通')} · 灵田 {text(block.crops, '无作物')}</small></header>
      <div className="facility-grid">
        {(block.items || []).map((item) => {
          const level = Number(item.level || 0)
          const materials = item.materials && typeof item.materials === 'object' ? Object.entries(item.materials as Record<string, unknown>).map(([name, count]) => `${name}×${count}`).join('、') : ''
          const available = item.affordable === true
          return (
            <article className="facility-card" key={text(item.name)}>
              <header><span><Hammer size={15} /></span><div><strong>{text(item.name)}</strong><small>{level ? `${level} 级设施` : '尚未营造'}</small></div><div className="level-pips">{[1, 2, 3].map((value) => <i data-filled={value <= level || undefined} key={value} />)}</div></header>
              <p>灵石 {text(item.cost_stones)}{materials ? ` · ${materials}` : ''}</p>
              <button type="button" disabled={!available} title={available ? '升级会推进一个月' : text(item.disabled_reason)} onClick={() => onAction(text(item.action))}>{level >= 3 ? '已达上限' : available ? `升至 ${level + 1} 级` : text(item.disabled_reason, '材料不足')}</button>
            </article>
          )
        })}
      </div>
      <div className="crop-actions"><button type="button" onClick={() => onAction('种植 灵药')}><Sprout size={14} />种植灵药</button><button type="button" onClick={() => onAction('收获 灵药')}><FlaskConical size={14} />收获灵药</button></div>
    </section>
  )
}

function RecipesBlock({ block, onAction }: { block: PresentationBlock; onAction: (action: string) => void }) {
  return (
    <section className="semantic-block recipe-block">
      <header><FlaskConical size={16} /><strong>{block.title || '已知配方'}</strong><small>投入材料后将真实判定成败</small></header>
      <div className="recipe-grid">
        {(block.items || []).map((item) => {
          const available = item.available === true
          const ingredients = item.ingredients && typeof item.ingredients === 'object' ? Object.entries(item.ingredients as Record<string, unknown>).map(([name, count]) => `${name}×${count}`).join('、') : ''
          return <article className="recipe-card" key={text(item.name)}><span>{text(item.craft, '技')}</span><div><strong>{text(item.name)}</strong><small>{ingredients} → {text(item.result)}</small><em>基础成功率 {text(item.chance)}%</em></div><button type="button" disabled={!available} title={available ? '立即制作并推进一个月' : text(item.disabled_reason)} onClick={() => onAction(text(item.action))}>{available ? '开炉制作' : '材料不足'}</button></article>
        })}
      </div>
    </section>
  )
}

function SectsBlock({ block, onAction }: { block: PresentationBlock; onAction: (action: string) => void }) {
  const mottos: Record<string, string> = { 青云宗: '清正持剑，守望东洲', 丹霞谷: '丹火养生，济世求真', 玄剑门: '以战磨剑，锋芒证道' }
  return (
    <section className="semantic-block sect-block">
      <header><Landmark size={16} /><strong>{block.title || '可选宗门'}</strong><small>入门试炼会推进一个月，也可能失败</small></header>
      <div className="sect-grid">
        {(block.items || []).map((item, index) => <article className="sect-card" key={text(item.name)} data-index={index}><span>{text(item.name, '宗').slice(0, 1)}</span><div><strong>{text(item.name)}</strong><small>{mottos[text(item.name)] || text(item.description)}</small><p>{text(item.description)}</p></div><button type="button" onClick={() => onAction(text(item.action))}>申请试炼</button></article>)}
      </div>
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
  if (block.type === 'market') return <MarketBlock block={block} onAction={onAction} />
  if (block.type === 'facilities') return <FacilitiesBlock block={block} onAction={onAction} />
  if (block.type === 'recipes') return <RecipesBlock block={block} onAction={onAction} />
  if (block.type === 'sects') return <SectsBlock block={block} onAction={onAction} />
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
