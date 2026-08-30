import { ArrowRight, Check, Clock3, Coins, Compass, FlaskConical, Gauge, Hammer, HeartPulse, Landmark, LockKeyhole, MapPin, Route, ScrollText, ShieldCheck, ShoppingBag, Sparkles, Sprout, UserRound, Wind, X } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { CaveSnapshot, NpcLifeSnapshot, Presentation, PresentationBlock } from '../api/types'

const text = (value: unknown, fallback = '') => typeof value === 'string' || typeof value === 'number' ? String(value) : fallback
const words = (value: unknown) => Array.isArray(value) ? value.map((item) => text(item)).filter(Boolean) : []

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

function PeopleBlock({ block, lives, readOnly, onAction }: { block: PresentationBlock; lives?: NpcLifeSnapshot; readOnly: boolean; onAction: (action: string) => void }) {
  const lifeByName = useMemo(() => new Map((lives?.profiles || []).map((profile) => [profile.name, profile])), [lives])
  return (
    <section className="semantic-block people-block">
      <header><UserRound size={16} /><strong>{block.title || '人物牵绊'}</strong><small>{lives ? `${lives.living_count} 位尚在世 · ${lives.pending_count} 封护道书` : '众生各循其道'}</small></header>
      <div className="person-grid">
        {(block.items || []).map((item, index) => {
          const name = text(item.name, '未知道友')
          const profile = lifeByName.get(name)
          const alive = profile?.alive !== false
          return (
            <article className="person-card life-card" data-alive={alive || undefined} data-pending={profile?.pending || undefined} key={`${name}-${index}`}>
              <span className="person-avatar">{name.slice(0, 1)}</span>
              <div className="person-heading"><strong>{name}</strong><small>{profile?.identity || text(item.identity || item.descriptor, '身份未明')}</small></div>
              <div className="person-tags"><span>{profile?.realm || text(item.realm, '境界未明')}</span><span>{profile?.relation || text(item.relation, '缘分未定')} · 好感 {profile?.affinity ?? text(item.affinity, '0')}</span></div>
              {profile && <>
                <div className="life-meter" title={`年龄 ${profile.age} 岁，寿元上限 ${profile.lifespan} 岁`}><span><HeartPulse size={11} />{alive ? `${profile.age}岁 · 尚余 ${profile.years_remaining} 年` : `${profile.age}岁 · 已故`}</span><i><b style={{ width: `${Math.max(3, 100 - profile.life_percent)}%` }} /></i></div>
                <div className="life-status"><span>{profile.location}</span><em>{profile.activity}</em><b data-danger={profile.wounded || !alive || undefined}>{profile.status}</b></div>
                {profile.pending && <div className="guard-request"><header><ShieldCheck size={14} /><span><strong>{profile.pending_kind}</strong><small>{profile.expires_in} 个月内回应</small></span></header><p>可赠 {profile.pill} 提高胜算，或亲自消耗灵力护持。</p><div><button type="button" disabled={readOnly || !profile.can_gift_pill} title={profile.can_gift_pill ? `消耗 ${profile.pill}×1` : `乾坤袋中没有${profile.pill}`} onClick={() => onAction(`护道 ${name} 赠丹`)}>赠丹</button><button type="button" disabled={readOnly || !profile.can_guard} title={profile.can_guard ? '消耗灵力 30，失败时可能受反噬' : '灵力不足 30'} onClick={() => onAction(`护道 ${name} 护持`)}>亲自护持</button><button type="button" disabled={readOnly} onClick={() => onAction(`护道 ${name} 守候`)}>静候天命</button></div></div>}
                {!alive && profile.cause_of_death && <p className="memorial-line">{profile.cause_of_death}</p>}
                {profile.life_events.length > 0 && <details className="life-events"><summary>查看生平近事</summary><ol>{profile.life_events.map((entry) => <li key={entry}>{entry}</li>)}</ol></details>}
              </>}
            </article>
          )
        })}
      </div>
      {lives?.memorials.length ? <details className="memorial-book"><summary>故人名录 · {lives.memorials.length}</summary><ol>{lives.memorials.map((entry) => <li key={`${entry.name}-${entry.year}`}><span>{entry.name}</span><strong>{entry.realm} · 享年 {entry.age}</strong><small>{entry.cause}</small></li>)}</ol></details> : null}
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

function RegionsBlock({ block, onAction }: { block: PresentationBlock; onAction: (action: string) => void }) {
  return (
    <section className="semantic-block region-block">
      <header><Route size={16} /><strong>{block.title || '九州舆图'}</strong><small>{block.legend}</small></header>
      <div className="region-grid">
        {(block.items || []).map((item, index) => {
          const current = item.current === true
          const accessible = item.accessible === true
          const visited = item.visited === true
          return (
            <article className="region-card" data-tone={text(item.tone, 'safe')} data-current={current || undefined} key={`${text(item.key)}-${index}`}>
              <header>
                <span>{text(item.key, '州').slice(0, 1)}</span>
                <div><small>{visited ? <><Check size={10} />已踏访</> : '未踏访'}</small><strong>{text(item.name, '无名地域')}</strong></div>
                <em>{current ? '当前落脚' : `${text(item.danger_label)} · ${text(item.danger)}`}</em>
              </header>
              <p>{text(item.description)}</p>
              <div className="route-facts"><span><Wind size={12} />{text(item.months)} 月</span><span>{text(item.requirement_label)}</span></div>
              <div className="region-standing" title="地方声望会影响坊市价格、探索判定与行旅安全">
                <Landmark size={12} /><strong>{text(item.rank, '初来乍到')}</strong><span>{Number(item.reputation || 0) >= 0 ? '+' : ''}{text(item.reputation, '0')}</span>
              </div>
              <dl>
                <div><dt>本地特产</dt><dd>{words(item.specialties).join(' · ')}</dd></div>
                <div><dt>热门求购</dt><dd>{words(item.demands).join(' · ')}</dd></div>
              </dl>
              <button type="button" disabled={!accessible} title={accessible ? '规划跨域行程' : text(item.locked_reason)} onClick={() => onAction(text(item.action))}>
                {current ? <><MapPin size={13} />当前所在</> : accessible ? <><ArrowRight size={13} />规划行程</> : <><LockKeyhole size={13} />{text(item.locked_reason, '尚未解锁')}</>}
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
      <div className="market-context"><span><small>本地特产</small>{text(block.specialties, '行情平稳')}</span><span><small>热门求购</small>{text(block.demands, '暂无异动')}</span><span><small>地方声望</small>{text(block.standing, '初来乍到 · +0')}</span><span data-profit={Number(block.trade_profit || 0) >= 0 ? 'gain' : 'loss'}><small>商路累计</small>{Number(block.trade_profit || 0) >= 0 ? '+' : ''}{text(block.trade_profit, '0')} 灵石</span></div>
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

function FacilitiesBlock({ block, cave, onAction }: { block: PresentationBlock; cave?: CaveSnapshot; onAction: (action: string) => void }) {
  const energyPercent = cave ? Math.max(0, Math.min(100, Math.round(cave.spirit_energy / Math.max(1, cave.spirit_energy_cap) * 100))) : 0
  return (
    <section className="semantic-block facility-block">
      <header><Landmark size={16} /><strong>{cave?.name || block.title || '洞府设施'}</strong><small>灵气 {cave?.aura || text(block.aura, '普通')} · 灵田 {text(block.crops, '无作物')}</small></header>
      {cave && <>
        <div className="cave-overview">
          <article className="cave-energy"><span><Sparkles size={17} /></span><div><small>洞府灵蕴</small><strong>{cave.spirit_energy} <i>/ {cave.spirit_energy_cap}</i></strong><div><b style={{ width: `${energyPercent}%` }} /></div></div><em>每月 +{cave.monthly_generation}</em></article>
          <article className="cave-operation"><Gauge size={17} /><div><small>当前方针</small><strong>{cave.focus}</strong><p>{cave.last_event || '洞府正在安稳运转'}</p></div><button type="button" disabled={!cave.can_recuperate} title={cave.can_recuperate ? '消耗 10 灵蕴并推进一个月' : cave.recuperate_reason} onClick={() => onAction('洞府调息')}>调息养元</button></article>
        </div>
        <div className="cave-focus-grid" aria-label="洞府运转方针">
          {cave.focuses.map((focus) => <button type="button" data-active={focus.active || undefined} disabled={focus.active || !focus.available} title={!focus.available ? focus.disabled_reason : focus.summary} onClick={() => onAction(focus.action)} key={focus.name}><span>{focus.active ? <Check size={13} /> : <Wind size={13} />}</span><strong>{focus.name}</strong><small>{focus.summary}</small></button>)}
        </div>
        <section className="cave-workshop">
          <header><Clock3 size={15} /><div><strong>后台工坊</strong><small>{cave.active_jobs}/{cave.capacity} 个生产位运转中</small></div></header>
          {cave.jobs.length ? <div className="cave-job-grid">{cave.jobs.map((job) => <article key={job.id}><span>{job.recipe.slice(0, 1)}</span><div><strong>{job.recipe}<small>{job.facility} · 成功率 {job.chance}%</small></strong><div><b style={{ width: `${job.progress}%` }} /></div><p>{job.months_left ? `还需 ${job.months_left} 个月` : '本月结算'} · {job.output}×{job.output_count}</p></div><button type="button" title="取消后取回全部预留材料" onClick={() => onAction(job.cancel_action)}><X size={13} />取消</button></article>)}</div> : <div className="cave-empty-job"><Clock3 size={18} /><span><strong>尚无后台生产</strong><small>先建成对应设施，再从下方配方安排任务。</small></span></div>}
        </section>
      </>}
      <details className="cave-fold" open>
        <summary><span>洞府设施</span><small>升级设施会推进一个月，并提升对应能力</small></summary>
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
      </details>
      {cave && <details className="cave-fold">
        <summary><span>生产配方</span><small>{cave.blueprints.length} 种 · 材料在安排时预留</small></summary>
        <div className="cave-blueprints">{cave.blueprints.map((item) => { const ingredients = Object.entries(item.ingredients).map(([name, count]) => `${name}×${count}`).join('、'); return <article key={item.name}><span>{item.craft.slice(0, 1)}</span><div><strong>{item.name}<small>{item.facility} · {item.duration} 个月 · {item.chance}%</small></strong><p>{ingredients} → {item.output}×{item.output_count}</p></div><button type="button" disabled={!item.available} title={item.available ? '安排后台生产，不立即推进时间' : item.disabled_reason} onClick={() => onAction(item.action)}>{item.available ? '安排生产' : item.disabled_reason}</button></article> })}</div>
      </details>}
      <div className="crop-actions"><button type="button" onClick={() => onAction('种植 灵药')}><Sprout size={14} />种植灵药</button><button type="button" onClick={() => onAction('收获 灵药')}><FlaskConical size={14} />收获灵药</button></div>
      {cave?.ledger.length ? <details className="cave-ledger"><summary>查看最近洞府月报</summary><ol>{cave.ledger.map((entry, index) => <li key={`${entry}-${index}`}>{entry}</li>)}</ol></details> : null}
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

function Block({ block, cave, lives, readOnly, onAction }: { block: PresentationBlock; cave?: CaveSnapshot; lives?: NpcLifeSnapshot; readOnly: boolean; onAction: (action: string) => void }) {
  if (block.type === 'facts') return <FactsBlock block={block} />
  if (block.type === 'people') return <PeopleBlock block={block} lives={lives} readOnly={readOnly} onAction={onAction} />
  if (block.type === 'regions') return <RegionsBlock block={block} onAction={onAction} />
  if (block.type === 'locations') return <LocationsBlock block={block} onAction={onAction} />
  if (block.type === 'meter') return <MeterBlock block={block} />
  if (block.type === 'market') return <MarketBlock block={block} onAction={onAction} />
  if (block.type === 'facilities') return <FacilitiesBlock block={block} cave={cave} onAction={onAction} />
  if (block.type === 'recipes') return <RecipesBlock block={block} onAction={onAction} />
  if (block.type === 'sects') return <SectsBlock block={block} onAction={onAction} />
  return <GenericBlock block={block} />
}

export function EventPanel({ presentation, cave, npcLives, readOnly = false, onAction }: { presentation: Presentation; cave?: CaveSnapshot; npcLives?: NpcLifeSnapshot; readOnly?: boolean; onAction: (action: string) => void }) {
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
        {(presentation.blocks || []).map((block, index) => <Block block={block} cave={cave} lives={npcLives} readOnly={readOnly} onAction={onAction} key={`${block.type}-${index}`} />)}
      </div>
      {presentation.has_details && (
        <details className="full-record"><summary>查看完整推演记录</summary><pre>{presentation.details}</pre></details>
      )}
    </article>
  )
}
