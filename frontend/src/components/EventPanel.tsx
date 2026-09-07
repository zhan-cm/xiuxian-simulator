import * as Dialog from '@radix-ui/react-dialog'
import { ArrowRight, Check, Clock3, Coins, Compass, FlaskConical, Gauge, Hammer, HeartPulse, Landmark, LockKeyhole, MapPin, Route, Scale, ScrollText, ShieldCheck, ShoppingBag, Sparkles, Sprout, Swords, UserRound, Waypoints, Wind, X } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { CaveSnapshot, NpcLifeProfile, NpcLifeSnapshot, NpcNetworkSnapshot, Presentation, PresentationBlock, SectMembershipSnapshot } from '../api/types'
import { SectMembershipPage } from './SectMembershipPage'

const text = (value: unknown, fallback = '') => typeof value === 'string' || typeof value === 'number' ? String(value) : fallback
const words = (value: unknown) => Array.isArray(value) ? value.map((item) => text(item)).filter(Boolean) : []

function SystemBlockHeader({ mark, eyebrow, title, description, meta, icon }: { mark: string; eyebrow: string; title: string; description?: unknown; meta?: string; icon: ReactNode }) {
  return (
    <header className="system-block-header">
      <span className="system-block-mark" aria-hidden="true">{mark}</span>
      <div className="system-block-copy"><small>{eyebrow}</small><strong>{title}</strong>{text(description) && <p>{text(description)}</p>}</div>
      {meta && <em>{meta}</em>}
      <i aria-hidden="true">{icon}</i>
    </header>
  )
}

function PersonProfileDialog({ profile, readOnly, onClose, onAction }: { profile?: NpcLifeProfile; readOnly: boolean; onClose: () => void; onAction: (action: string) => void }) {
  if (!profile) return null
  const remaining = Math.max(0, 100 - profile.life_percent)
  const act = (action: string) => { onClose(); onAction(action) }
  return (
    <Dialog.Root open onOpenChange={(open) => { if (!open) onClose() }}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog npc-profile-dialog" aria-describedby={`npc-profile-${profile.name}`}>
          <header><div><p>浮生一页 · 众生有迹</p><Dialog.Title>{profile.name}</Dialog.Title><Dialog.Description id={`npc-profile-${profile.name}`}>{profile.identity}</Dialog.Description></div><Dialog.Close aria-label="关闭人物档案"><X size={20} /></Dialog.Close></header>
          <div className="npc-profile-hero" data-alive={profile.alive || undefined}>
            <span aria-hidden="true">{profile.name.slice(0, 1)}</span>
            <div><small>{profile.gender}修 · {profile.relation}</small><strong>{profile.realm}</strong><p><MapPin size={13} />{profile.location} · {profile.activity}</p></div>
            <em data-danger={profile.wounded || !profile.alive || undefined}>{profile.status}</em>
          </div>
          <div className="npc-profile-facts">
            <span><small>年岁</small><strong>{profile.age} 岁</strong></span>
            <span><small>寿元</small><strong>{profile.lifespan} 年</strong></span>
            <span><small>好感</small><strong>{profile.affinity}</strong></span>
            <span><small>缘分</small><strong>{profile.relation}</strong></span>
          </div>
          <section className="npc-profile-life"><header><HeartPulse size={15} /><div><strong>{profile.alive ? `尚余约 ${profile.years_remaining} 年` : '此生已落幕'}</strong><small>{profile.cause_of_death || '岁月会随每一次跨年真实流逝'}</small></div><em>{remaining}%</em></header><i><b style={{ width: `${Math.max(3, remaining)}%` }} /></i></section>
          <section className="npc-profile-preferences"><strong>性情所好</strong><div>{profile.likes.length ? profile.likes.map((like) => <span key={like}>{like}</span>) : <span>尚待相知</span>}</div></section>
          <section className="npc-profile-chronicle"><header><ScrollText size={15} /><strong>近世行迹</strong></header>{profile.life_events.length ? <ol>{profile.life_events.slice(-5).reverse().map((entry, index) => <li key={`${entry}-${index}`}><span>{index + 1}</span><p>{entry}</p></li>)}</ol> : <p>此人的故事尚未留下更多笔墨。</p>}</section>
          <footer><Dialog.Close>返回人物卷</Dialog.Close>{profile.alive && <><button type="button" disabled={readOnly} onClick={() => act(`对话 ${profile.name}`)}>前往交谈</button><button type="button" disabled={readOnly} onClick={() => act(`论道 ${profile.name}`)}>论道印证</button></>}</footer>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

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
  const [selectedName, setSelectedName] = useState('')
  const selectedProfile = lifeByName.get(selectedName)
  return (
    <><section className="semantic-block people-block">
      <SystemBlockHeader mark="人" eyebrow="浮生万象" title={block.title || '人物牵绊'} description="故人各有行迹与寿数；先观近况，再决定是否叩门相见。" meta={lives ? `${lives.living_count} 位尚在世 · ${lives.pending_count} 封护道书` : '众生各循其道'} icon={<UserRound size={21} />} />
      <div className="person-gallery">
        {(block.items || []).map((item, index) => {
          const name = text(item.name, '未知道友')
          const profile = lifeByName.get(name)
          const alive = profile?.alive !== false
          return (
            <article className="person-gallery-card" data-alive={alive || undefined} data-pending={profile?.pending || undefined} key={`${name}-${index}`}>
              <div className="person-gallery-portrait"><span>{name.slice(0, 1)}</span><em data-danger={profile?.wounded || !alive || undefined}>{profile?.status || (alive ? '近况未明' : '已故')}</em></div>
              <header><small>{profile ? `${profile.gender}修 · ${profile.location}` : '来处未明'}</small><strong>{name}</strong><p>{profile?.identity || text(item.identity || item.descriptor, '身份未明')}</p></header>
              <div className="person-gallery-vitals"><span><small>境界</small><strong>{profile?.realm || text(item.realm, '境界未明')}</strong></span><span><small>年岁</small><strong>{profile ? `${profile.age} / ${profile.lifespan}` : '未载'}</strong></span></div>
              <div className="person-gallery-affinity"><span><small>{profile?.relation || text(item.relation, '缘分未定')}</small><strong>好感 {profile?.affinity ?? text(item.affinity, '0')}</strong></span><i title={`好感 ${profile?.affinity ?? text(item.affinity, '0')}`}><b style={{ width: `${Math.max(0, Math.min(100, Number(profile?.affinity ?? item.affinity ?? 0)))}%` }} /></i></div>
              {profile && <>
                {profile.pending && <div className="guard-request"><header><ShieldCheck size={14} /><span><strong>{profile.pending_kind}</strong><small>{profile.expires_in} 个月内回应</small></span></header><p>可赠 {profile.pill} 提高胜算，或亲自消耗灵力护持。</p><div><button type="button" disabled={readOnly || !profile.can_gift_pill} title={profile.can_gift_pill ? `消耗 ${profile.pill}×1` : `乾坤袋中没有${profile.pill}`} onClick={() => onAction(`护道 ${name} 赠丹`)}>赠丹</button><button type="button" disabled={readOnly || !profile.can_guard} title={profile.can_guard ? '消耗灵力 30，失败时可能受反噬' : '灵力不足 30'} onClick={() => onAction(`护道 ${name} 护持`)}>亲自护持</button><button type="button" disabled={readOnly} onClick={() => onAction(`护道 ${name} 守候`)}>静候天命</button></div></div>}
                {!alive && profile.cause_of_death && <p className="memorial-line">{profile.cause_of_death}</p>}
              </>}
              <div className="person-actions"><button className="profile-action" type="button" onClick={() => setSelectedName(name)}>查看档案</button>{alive && <><button type="button" disabled={readOnly} onClick={() => onAction(`对话 ${name}`)}>与其交谈</button><button type="button" disabled={readOnly} onClick={() => onAction(`论道 ${name}`)}>论道印证</button></>}</div>
            </article>
          )
        })}
      </div>
      {lives?.memorials.length ? <details className="memorial-book"><summary>故人名录 · {lives.memorials.length}</summary><ol>{lives.memorials.map((entry) => <li key={`${entry.name}-${entry.year}`}><span>{entry.name}</span><strong>{entry.realm} · 享年 {entry.age}</strong><small>{entry.cause}</small></li>)}</ol></details> : null}
    </section><PersonProfileDialog profile={selectedProfile} readOnly={readOnly} onClose={() => setSelectedName('')} onAction={onAction} /></>
  )
}

function NpcNetworkBlock({ network, readOnly, onAction }: { network: NpcNetworkSnapshot; readOnly: boolean; onAction: (action: string) => void }) {
  const pending = network.pending?.id ? network.pending : null
  return (
    <section className="semantic-block npc-network-block">
      <header><Waypoints size={16} /><strong>众生因缘网</strong><small>{network.connected_count} 人相连 · {network.bond_count} 段因缘</small></header>
      <div className="network-summary">
        <span><strong>{network.allied_count}</strong><small>深交同盟</small></span>
        <span><strong>{network.rival_count}</strong><small>嫌隙宿敌</small></span>
        <span><strong>{network.history.length}</strong><small>近世传闻</small></span>
      </div>
      {pending && <article className="network-dispute">
        <header><Scale size={16} /><div><small>四个月内可介入</small><strong>{pending.left} · {pending.cause} · {pending.right}</strong></div><em>余 {pending.expires_in} 月</em></header>
        <p>你可以居中调停、公开偏袒一方，或把结果交还给二人自己决定。</p>
        <div>
          <button type="button" disabled={readOnly || !pending.can_mediate} title={pending.can_mediate ? `成功率 ${pending.mediate_chance}%，消耗灵力 20` : pending.mediate_reason} onClick={() => onAction('介入人情 调停')}><Scale size={12} />调停 {pending.mediate_chance || '—'}%</button>
          <button type="button" disabled={readOnly || !pending.can_favor_left} title={pending.can_favor_left ? `偏袒${pending.left}会加深双方嫌隙` : `与${pending.left}好感需达到 10`} onClick={() => onAction(`介入人情 偏袒 ${pending.left}`)}>偏袒 {pending.left}</button>
          <button type="button" disabled={readOnly || !pending.can_favor_right} title={pending.can_favor_right ? `偏袒${pending.right}会加深双方嫌隙` : `与${pending.right}好感需达到 10`} onClick={() => onAction(`介入人情 偏袒 ${pending.right}`)}>偏袒 {pending.right}</button>
          <button type="button" disabled={readOnly} title="不消耗资源，结果由二人自行决定" onClick={() => onAction('介入人情 旁观')}>静观其变</button>
        </div>
      </article>}
      <div className="network-bond-grid">
        {network.bonds.map((bond) => {
          const position = Math.max(0, Math.min(100, (bond.score + 100) / 2))
          return <article className="network-bond" data-tone={bond.tone} key={bond.id}>
            <header><span>{bond.left.slice(0, 1)}</span><div><strong>{bond.left}</strong><i><b style={{ width: `${position}%` }} /></i><small>{bond.score > 0 ? '相契' : bond.score < 0 ? '相左' : '未定'} {Math.abs(bond.score)}</small></div><span>{bond.right.slice(0, 1)}</span></header>
            <div><strong>{bond.label}</strong><small>{bond.encounters ? `${bond.encounters} 次交集` : '旧缘底色'}</small></div>
            <p>{bond.last_event}</p>
            {bond.events.length > 1 && <details><summary>查看往来</summary><ol>{bond.events.map((entry, index) => <li key={`${entry}-${index}`}>{entry}</li>)}</ol></details>}
          </article>
        })}
      </div>
      {network.history.length > 0 && <details className="network-rumors"><summary><Swords size={12} />展开最近九州人情传闻</summary><ol>{[...network.history].reverse().map((entry, index) => <li key={`${entry}-${index}`}>{entry}</li>)}</ol></details>}
    </section>
  )
}

function LocationsBlock({ block, readOnly, onAction }: { block: PresentationBlock; readOnly: boolean; onAction: (action: string) => void }) {
  const count = block.items?.length || 0
  return (
    <section className="semantic-block location-block">
      <SystemBlockHeader mark="游" eyebrow="山河可赴" title={block.title || '探索地图'} description={block.legend || '择一处地标动身，风险与机缘皆由规则真实结算。'} meta={`${count} 处地标`} icon={<Compass size={21} />} />
      <div className="location-grid">
        {(block.items || []).map((item, index) => {
          const accessible = item.accessible !== false
          const visited = item.visited === true
          const action = text(item.action, `探索 ${text(item.name)}`)
          const danger = Number(item.danger || 0)
          const dangerLevel = danger <= 15 ? 1 : danger <= 25 ? 2 : danger <= 35 ? 3 : 4
          return (
            <article className="location-card" data-tone={text(item.tone, 'safe')} key={`${text(item.name)}-${index}`}>
              <header><div><MapPin size={17} /><strong>{text(item.name, '未名之地')}</strong></div><div className="location-danger" title={`危险度 ${text(item.danger, '未知')}：数值越高，遭遇强敌与危机的可能越大`}><span>{text(item.danger_label, '未知')} · {text(item.danger, '?')}</span><i aria-label={`危险等级 ${dangerLevel} / 4`}>{[1, 2, 3, 4].map((level) => <b data-filled={level <= dangerLevel || undefined} key={level} />)}</i></div></header>
              <div className="location-card-meta"><small>准入：{text(item.requirement_label || item.requirement, '炼气境')}</small><span data-state={visited ? 'visited' : accessible ? 'available' : 'locked'}>{visited ? <><Check size={11} />已探访</> : accessible ? <><Sparkles size={11} />机缘未探</> : <><LockKeyhole size={11} />境界未至</>}</span></div>
              <p>{text(item.description || item.help, '前路未明，需亲自踏勘。')}</p>
              <button type="button" disabled={readOnly || !accessible} title={readOnly ? '成果巡览仅供查看' : accessible ? '立即前往探索' : text(item.locked_reason, '当前无法进入')} onClick={() => onAction(action)}>
                <span>{accessible ? '前往探索' : text(item.locked_reason, '尚未解锁')}</span>{accessible ? <ArrowRight size={14} /> : <LockKeyhole size={14} />}
              </button>
            </article>
          )
        })}
      </div>
    </section>
  )
}

function RegionsBlock({ block, readOnly, onAction }: { block: PresentationBlock; readOnly: boolean; onAction: (action: string) => void }) {
  const items = useMemo(() => block.items || [], [block.items])
  const [selectedKey, setSelectedKey] = useState('')
  const selected = items.find((item) => text(item.key) === selectedKey) || items.find((item) => item.current === true) || items[0]
  const count = items.length
  return (
    <section className="semantic-block region-block">
      <SystemBlockHeader mark="州" eyebrow="云路万里" title={block.title || '九州舆图'} description={block.legend || '各域物产、声望与行程不同，启程前请细察路途。'} meta={`${count} 方地域`} icon={<Route size={21} />} />
      <div className="region-atlas">
        <nav className="region-atlas-map" aria-label="五域卷轴舆图">
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><path d="M50 13 C42 25 52 35 50 50 C44 65 55 78 50 88" /><path d="M15 50 C30 42 38 53 50 50 C64 45 73 55 86 48" /></svg>
          <span className="atlas-compass" aria-hidden="true"><i>北</i><b>九州</b><i>南</i></span>
          {items.map((item, index) => {
            const current = item.current === true
            const accessible = item.accessible === true
            const visited = item.visited === true
            const key = text(item.key, `地域-${index}`)
            const chosen = selected === item
            return <button type="button" className="region-node" data-region={key} data-current={current || undefined} data-visited={visited || undefined} data-locked={!accessible && !current || undefined} aria-pressed={chosen} aria-label={`查看${text(item.name, key)}地域`} onClick={() => setSelectedKey(key)} key={key}>
              <span>{key.slice(0, 1)}</span><strong>{text(item.name, '无名地域')}</strong><small>{current ? '当前落脚' : visited ? '已经踏访' : text(item.danger_label, '路途未明')}</small>
              {item.has_event === true && <i aria-label="有地方机缘" />}
            </button>
          })}
          <p>山河入卷 · 五域可观</p>
        </nav>
        {selected && (() => {
          const current = selected.current === true
          const accessible = selected.accessible === true
          const visited = selected.visited === true
          return <aside className="region-atlas-detail" data-tone={text(selected.tone, 'safe')} aria-label={`${text(selected.name)}地域详情`}>
            <header><span>{text(selected.key, '州').slice(0, 1)}</span><div><small>{visited ? '足迹已至' : '山河未访'}</small><h3>{text(selected.name, '无名地域')}</h3></div><em>{current ? '当前落脚' : `${text(selected.danger_label)} · ${text(selected.danger)}`}</em></header>
            <p>{text(selected.description)}</p>
            {selected.has_event === true && <div className="region-event-badge" data-pending={selected.event_pending === true || undefined} title={text(selected.event_title, '地方机缘')}><Sparkles size={12} /><strong>{selected.event_pending === true ? '机缘待决' : '有地方机缘'}</strong><small>{text(selected.event_title)}</small></div>}
            <div className="region-atlas-stats"><span><Wind size={12} /><small>行程</small><strong>{text(selected.months)} 月</strong></span><span><ShieldCheck size={12} /><small>准入</small><strong>{text(selected.requirement_label)}</strong></span><span><Landmark size={12} /><small>声望</small><strong>{text(selected.rank, '初来乍到')} · {Number(selected.reputation || 0) >= 0 ? '+' : ''}{text(selected.reputation, '0')}</strong></span></div>
            <dl><div><dt>本地特产</dt><dd>{words(selected.specialties).join(' · ') || '尚待寻访'}</dd></div><div><dt>热门求购</dt><dd>{words(selected.demands).join(' · ') || '行情平稳'}</dd></div></dl>
            <button type="button" disabled={readOnly || !accessible} title={readOnly ? '成果巡览仅供查看' : accessible ? '规划跨域行程' : text(selected.locked_reason)} onClick={() => onAction(text(selected.action))}>
              {current ? <><MapPin size={13} />当前所在</> : accessible ? <><ArrowRight size={13} />规划前往{text(selected.key)}</> : <><LockKeyhole size={13} />{text(selected.locked_reason, '尚未解锁')}</>}
            </button>
          </aside>
        })()}
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

function MarketBlock({ block, readOnly, onAction }: { block: PresentationBlock; readOnly: boolean; onAction: (action: string) => void }) {
  const items = useMemo(() => block.items || [], [block.items])
  const categories = useMemo(() => ['全部', ...new Set(items.map((item) => text(item.category, '其他')))], [items])
  const [category, setCategory] = useState('全部')
  const [selectedName, setSelectedName] = useState('')
  const shown = useMemo(() => category === '全部' ? items : items.filter((item) => item.category === category), [category, items])
  const selected = shown.find((item) => text(item.name) === selectedName) || shown[0]
  return (
    <section className="semantic-block market-block">
      <SystemBlockHeader mark="市" eyebrow="青岳商路" title={block.title || '坊市货架'} description="辨行情、择灵物，每一次买卖都会真实计入行囊与商路账目。" meta={`持有 ${text(block.currency, '0')} 灵石`} icon={<ShoppingBag size={21} />} />
      <div className="market-context"><span><small>本地特产</small>{text(block.specialties, '行情平稳')}</span><span><small>热门求购</small>{text(block.demands, '暂无异动')}</span><span><small>地方声望</small>{text(block.standing, '初来乍到 · +0')}</span><span data-profit={Number(block.trade_profit || 0) >= 0 ? 'gain' : 'loss'}><small>商路累计</small>{Number(block.trade_profit || 0) >= 0 ? '+' : ''}{text(block.trade_profit, '0')} 灵石</span></div>
      <nav className="market-tabs" aria-label="货架分类">
        {categories.map((name) => <button type="button" data-active={category === name || undefined} onClick={() => setCategory(name)} key={name}>{name}</button>)}
      </nav>
      <div className="market-layout"><div className="market-grid">
        {shown.map((item) => <article className="market-item" data-category={text(item.category, '其他')} data-selected={selected === item || undefined} key={text(item.name)}><button className="market-item-select" type="button" aria-pressed={selected === item} onClick={() => setSelectedName(text(item.name))}><span className="item-glyph">{text(item.name, '物').slice(0, 1)}</span><div className="market-copy"><strong>{text(item.name, '未鉴定物品')}</strong><small>{text(item.rarity, '凡品')} · 持有 {text(item.owned, '0')}</small></div><span className="market-quote"><small>买 / 卖</small><strong>{text(item.buy)} <i /> {text(item.sell)}</strong></span><ArrowRight size={14} /></button></article>)}
      </div>{selected && <aside className="market-inspector" data-rarity={text(selected.rarity, '凡品')} aria-label={`${text(selected.name)}详情`}>
        <div className="market-inspector-emblem"><Sparkles size={17} /><span>{text(selected.name, '物').slice(0, 1)}</span></div>
        <small>{text(selected.category, '修仙杂物')} · {text(selected.rarity, '凡品')}</small><h3>{text(selected.name, '未鉴定物品')}</h3>
        <p>{text(selected.description, '尚未鉴定来历的修行物品。')}</p>
        <div className="market-usage"><strong>实际用途</strong><p>{text(selected.usage, '可在坊市交易。')}</p></div>
        <dl><div><dt>当前持有</dt><dd>{text(selected.owned, '0')} 件</dd></div><div><dt>坊市行情</dt><dd>买 {text(selected.buy)} · 卖 {text(selected.sell)}</dd></div></dl>
        <div className="market-inspector-actions"><button type="button" disabled={readOnly || selected.affordable === false} title={readOnly ? '成果巡览仅供查看' : selected.affordable === false ? '灵石不足' : '买入一件'} onClick={() => onAction(text(selected.buy_action))}><small>买入一件</small><b><Coins size={12} />{text(selected.buy)} 灵石</b></button><button type="button" disabled={readOnly || Number(selected.owned || 0) <= 0} title={readOnly ? '成果巡览仅供查看' : Number(selected.owned || 0) > 0 ? '卖出一件' : '当前未持有'} onClick={() => onAction(text(selected.sell_action))}><small>卖出一件</small><b><Coins size={12} />{text(selected.sell)} 灵石</b></button></div>
      </aside>}</div>
    </section>
  )
}

const facilityDescriptions: Record<string, string> = {
  静室: '隔绝尘扰，供闭关吐纳与疗愈伤势；层级越高，静修越安稳。',
  丹房: '引地火、布药炉，可安排丹药在后台炼制并随月份完成。',
  器坊: '淬炼灵铁与妖材，用于打造兵刃、法袍及后续器物。',
  灵田: '培育灵药的洞府沃土；种下灵植后，需等待真实月份成熟。',
  聚灵阵: '汇聚四周灵机，提高洞府灵蕴上限与每月自然生成。',
  禁制: '护住洞府门户与工坊资粮，为高阶经营预留安稳根基。',
}

function FacilitiesBlock({ block, cave, readOnly, onAction }: { block: PresentationBlock; cave?: CaveSnapshot; readOnly: boolean; onAction: (action: string) => void }) {
  const energyPercent = cave ? Math.max(0, Math.min(100, Math.round(cave.spirit_energy / Math.max(1, cave.spirit_energy_cap) * 100))) : 0
  const facilities = useMemo(() => block.items || [], [block.items])
  const [selectedFacilityName, setSelectedFacilityName] = useState('')
  const selectedFacility = facilities.find((item) => text(item.name) === selectedFacilityName) || facilities[0]
  return (
    <section className="semantic-block facility-block">
      <SystemBlockHeader mark="府" eyebrow="一方洞天" title={cave?.name || block.title || '洞府设施'} description={`灵气 ${cave?.aura || text(block.aura, '普通')} · 灵田 ${text(block.crops, '无作物')}`} meta={cave ? `${cave.active_jobs} / ${cave.capacity} 工坊运转` : '洞府营造'} icon={<Landmark size={21} />} />
      {selectedFacility && <div className="cave-scene-stage">
        <div className="cave-landscape" aria-label="洞府设施分布">
          <div className="cave-landscape-mist" aria-hidden="true" /><div className="cave-landscape-ridge" aria-hidden="true" />
          {facilities.map((item, index) => { const name = text(item.name); const level = Number(item.level || 0); return <button type="button" data-spot={name} data-index={index} data-selected={selectedFacility === item || undefined} aria-pressed={selectedFacility === item} onClick={() => setSelectedFacilityName(name)} key={name}><span>{name.slice(0, 1)}</span><strong>{name}</strong><small>{level ? `${level} 级` : '待营造'}</small></button> })}
          <p>点击洞府热点查看设施详情</p>
        </div>
        <aside className="cave-hotspot-inspector">
          <header><span>{text(selectedFacility.name, '府').slice(0, 1)}</span><div><small>当前设施</small><h3>{text(selectedFacility.name)}</h3></div><em>{Number(selectedFacility.level || 0) ? `${text(selectedFacility.level)} 级` : '尚未营造'}</em></header>
          <p>{text(selectedFacility.description, facilityDescriptions[text(selectedFacility.name)] || `${text(selectedFacility.name)}承载着洞府的一项核心能力。`)}</p>
          <dl><div><dt>当前层级</dt><dd>{text(selectedFacility.level, '0')} / 3</dd></div><div><dt>升级灵石</dt><dd>{text(selectedFacility.cost_stones, '—')}</dd></div><div><dt>所需材料</dt><dd>{selectedFacility.materials && typeof selectedFacility.materials === 'object' ? Object.entries(selectedFacility.materials as Record<string, unknown>).map(([name, count]) => `${name}×${count}`).join('、') || '无需材料' : '无需材料'}</dd></div></dl>
          <button type="button" disabled={readOnly || selectedFacility.affordable !== true} title={readOnly ? '成果巡览仅供查看' : selectedFacility.affordable === true ? '升级会推进一个月' : text(selectedFacility.disabled_reason)} onClick={() => onAction(text(selectedFacility.action))}>{Number(selectedFacility.level || 0) >= 3 ? '已达最高层级' : selectedFacility.affordable === true ? `营造至 ${Number(selectedFacility.level || 0) + 1} 级` : text(selectedFacility.disabled_reason, '资粮不足')}</button>
        </aside>
      </div>}
      {cave && <>
        <div className="cave-overview">
          <article className="cave-energy"><span><Sparkles size={17} /></span><div><small>洞府灵蕴</small><strong>{cave.spirit_energy} <i>/ {cave.spirit_energy_cap}</i></strong><div><b style={{ width: `${energyPercent}%` }} /></div></div><em>每月 +{cave.monthly_generation}</em></article>
          <article className="cave-operation"><Gauge size={17} /><div><small>当前方针</small><strong>{cave.focus}</strong><p>{cave.last_event || '洞府正在安稳运转'}</p></div><button type="button" disabled={readOnly || !cave.can_recuperate} title={readOnly ? '成果巡览仅供查看' : cave.can_recuperate ? '消耗 10 灵蕴并推进一个月' : cave.recuperate_reason} onClick={() => onAction('洞府调息')}>调息养元</button></article>
        </div>
        <div className="cave-focus-grid" aria-label="洞府运转方针">
          {cave.focuses.map((focus) => <button type="button" data-active={focus.active || undefined} disabled={readOnly || focus.active || !focus.available} title={readOnly ? '成果巡览仅供查看' : !focus.available ? focus.disabled_reason : focus.summary} onClick={() => onAction(focus.action)} key={focus.name}><span>{focus.active ? <Check size={13} /> : <Wind size={13} />}</span><strong>{focus.name}</strong><small>{focus.summary}</small></button>)}
        </div>
        <section className="cave-workshop">
          <header><Clock3 size={15} /><div><strong>后台工坊</strong><small>{cave.active_jobs}/{cave.capacity} 个生产位运转中</small></div></header>
          {cave.jobs.length ? <div className="cave-job-grid">{cave.jobs.map((job) => <article key={job.id}><span>{job.recipe.slice(0, 1)}</span><div><strong>{job.recipe}<small>{job.facility} · 成功率 {job.chance}%</small></strong><div><b style={{ width: `${job.progress}%` }} /></div><p>{job.months_left ? `还需 ${job.months_left} 个月` : '本月结算'} · {job.output}×{job.output_count}</p></div><button type="button" disabled={readOnly} title={readOnly ? '成果巡览仅供查看' : '取消后取回全部预留材料'} onClick={() => onAction(job.cancel_action)}><X size={13} />取消</button></article>)}</div> : <div className="cave-empty-job"><Clock3 size={18} /><span><strong>尚无后台生产</strong><small>先建成对应设施，再从下方配方安排任务。</small></span></div>}
        </section>
      </>}
      <details className="cave-fold">
        <summary><span>洞府设施</span><small>升级设施会推进一个月，并提升对应能力</small></summary>
        <div className="facility-grid">
          {facilities.map((item) => {
            const level = Number(item.level || 0)
            const materials = item.materials && typeof item.materials === 'object' ? Object.entries(item.materials as Record<string, unknown>).map(([name, count]) => `${name}×${count}`).join('、') : ''
            const available = item.affordable === true
            return (
              <article className="facility-card" data-selected={selectedFacility === item || undefined} key={text(item.name)}>
                <header><span><Hammer size={15} /></span><div><strong>{text(item.name)}</strong><small>{level ? `${level} 级设施` : '尚未营造'}</small></div><div className="level-pips">{[1, 2, 3].map((value) => <i data-filled={value <= level || undefined} key={value} />)}</div></header>
                <p>灵石 {text(item.cost_stones)}{materials ? ` · ${materials}` : ''}</p>
                <button type="button" disabled={readOnly || !available} title={readOnly ? '成果巡览仅供查看' : available ? '升级会推进一个月' : text(item.disabled_reason)} onClick={() => onAction(text(item.action))}>{level >= 3 ? '已达上限' : available ? `升至 ${level + 1} 级` : text(item.disabled_reason, '材料不足')}</button>
              </article>
            )
          })}
        </div>
      </details>
      {cave && <details className="cave-fold">
        <summary><span>生产配方</span><small>{cave.blueprints.length} 种 · 材料在安排时预留</small></summary>
        <div className="cave-blueprints">{cave.blueprints.map((item) => { const ingredients = Object.entries(item.ingredients).map(([name, count]) => `${name}×${count}`).join('、'); return <article key={item.name}><span>{item.craft.slice(0, 1)}</span><div><strong>{item.name}<small>{item.facility} · {item.duration} 个月 · {item.chance}%</small></strong><p>{ingredients} → {item.output}×{item.output_count}</p></div><button type="button" disabled={readOnly || !item.available} title={readOnly ? '成果巡览仅供查看' : item.available ? '安排后台生产，不立即推进时间' : item.disabled_reason} onClick={() => onAction(item.action)}>{item.available ? '安排生产' : item.disabled_reason}</button></article> })}</div>
      </details>}
      <div className="crop-actions"><button type="button" disabled={readOnly} onClick={() => onAction('种植 灵药')}><Sprout size={14} />种植灵药</button><button type="button" disabled={readOnly} onClick={() => onAction('收获 灵药')}><FlaskConical size={14} />收获灵药</button></div>
      {cave?.ledger.length ? <details className="cave-ledger"><summary>查看最近洞府月报</summary><ol>{cave.ledger.map((entry, index) => <li key={`${entry}-${index}`}>{entry}</li>)}</ol></details> : null}
    </section>
  )
}

function RecipesBlock({ block, readOnly, onAction }: { block: PresentationBlock; readOnly: boolean; onAction: (action: string) => void }) {
  return (
    <section className="semantic-block recipe-block">
      <SystemBlockHeader mark="艺" eyebrow="炉火百炼" title={block.title || '已知配方'} description="材料、成功率与产物均由规则引擎结算，开炉前可先查验资粮。" meta={`${block.items?.length || 0} 道配方`} icon={<FlaskConical size={21} />} />
      <div className="recipe-grid">
        {(block.items || []).map((item) => {
          const available = item.available === true
          const ingredients = item.ingredients && typeof item.ingredients === 'object' ? Object.entries(item.ingredients as Record<string, unknown>).map(([name, count]) => `${name}×${count}`).join('、') : ''
          return <article className="recipe-card" key={text(item.name)}><span>{text(item.craft, '技')}</span><div><strong>{text(item.name)}</strong><small>{ingredients} → {text(item.result)}</small><em>基础成功率 {text(item.chance)}%</em></div><button type="button" disabled={readOnly || !available} title={readOnly ? '成果巡览仅供查看' : available ? '立即制作并推进一个月' : text(item.disabled_reason)} onClick={() => onAction(text(item.action))}>{available ? '开炉制作' : '材料不足'}</button></article>
        })}
      </div>
    </section>
  )
}

function SectsBlock({ block, readOnly, onAction }: { block: PresentationBlock; readOnly: boolean; onAction: (action: string) => void }) {
  const mottos: Record<string, string> = { 青云宗: '清正持剑，守望东洲', 丹霞谷: '丹火养生，济世求真', 玄剑门: '以战磨剑，锋芒证道' }
  return (
    <section className="semantic-block sect-block">
      <SystemBlockHeader mark="宗" eyebrow="山门择路" title={block.title || '可选宗门'} description="道统各异，门规不同；入门试炼会推进一个月，也可能失败。" meta={`${block.items?.length || 0} 座山门`} icon={<Landmark size={21} />} />
      <div className="sect-grid">
        {(block.items || []).map((item, index) => <article className="sect-card" key={text(item.name)} data-index={index}><span>{text(item.name, '宗').slice(0, 1)}</span><div><strong>{text(item.name)}</strong><small>{mottos[text(item.name)] || text(item.description)}</small><p>{text(item.description)}</p></div><button type="button" disabled={readOnly} title={readOnly ? '成果巡览仅供查看' : '申请入门试炼'} onClick={() => onAction(text(item.action))}><span>申请试炼</span><ArrowRight size={14} /></button></article>)}
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
  if (block.type === 'regions') return <RegionsBlock block={block} readOnly={readOnly} onAction={onAction} />
  if (block.type === 'locations') return <LocationsBlock block={block} readOnly={readOnly} onAction={onAction} />
  if (block.type === 'meter') return <MeterBlock block={block} />
  if (block.type === 'market') return <MarketBlock block={block} readOnly={readOnly} onAction={onAction} />
  if (block.type === 'facilities') return <FacilitiesBlock block={block} cave={cave} readOnly={readOnly} onAction={onAction} />
  if (block.type === 'recipes') return <RecipesBlock block={block} readOnly={readOnly} onAction={onAction} />
  if (block.type === 'sects') return <SectsBlock block={block} readOnly={readOnly} onAction={onAction} />
  return <GenericBlock block={block} />
}

export function EventPanel({ presentation, cave, npcLives, npcNetwork, sectMembership, readOnly = false, immersive = false, onAction }: { presentation: Presentation; cave?: CaveSnapshot; npcLives?: NpcLifeSnapshot; npcNetwork?: NpcNetworkSnapshot; sectMembership?: SectMembershipSnapshot; readOnly?: boolean; immersive?: boolean; onAction: (action: string) => void }) {
  const showNetwork = Boolean(npcNetwork && (['人脉', '缘网', '众生缘网'].includes(presentation.action) || presentation.action.startsWith('介入人情')))
  const showNetworkOutcome = showNetwork && presentation.action.startsWith('介入人情')
  const showSectMembership = Boolean(sectMembership?.member && (['宗门', '申请晋升', '宗门大比'].includes(presentation.action) || presentation.action.startsWith('宗门任务')))
  const paragraphs = presentation.paragraphs || []
  const visibleParagraphs = immersive ? paragraphs.slice(1) : paragraphs
  const changes = immersive ? (presentation.changes || []).slice(3) : presentation.changes || []
  const hasSecondaryContent = visibleParagraphs.length > 0 || changes.length > 0 || presentation.blocks?.length > 0 || showNetwork || showSectMembership || presentation.has_details
  const surfaceType = (presentation.blocks || []).find((block) => ['people', 'locations', 'regions', 'market', 'facilities', 'sects', 'recipes'].includes(block.type))?.type
  const act = (action: string) => { if (!readOnly) onAction(action) }
  if (immersive && !hasSecondaryContent) return null
  return (
    <article className="event-panel" data-tone={presentation.tone || 'story'} data-immersive={immersive || undefined} data-surface={surfaceType}>
      <div className="event-ornament" aria-hidden="true" />
      {!immersive && <header className="event-heading">
        <span className="event-seal">{presentation.seal || '道'}</span>
        <div><p>{presentation.eyebrow || '当前道途'}</p><h2>{presentation.title || '灵气潮汐将至'}</h2></div>
      </header>}
      {visibleParagraphs.length > 0 && (!showNetwork || showNetworkOutcome) && <div className="event-copy scene-continuation">
        {visibleParagraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
      </div>}
      {changes.length > 0 && (
        <div className="change-row">
          {changes.map((change, index) => <span key={`${change.label}-${index}`}><small>{change.label}</small><strong>{change.value}</strong></span>)}
        </div>
      )}
      <div className="event-blocks" aria-label="本次推演数据">
        {!showNetwork && !showSectMembership && (presentation.blocks || []).map((block, index) => <Block block={block} cave={cave} lives={npcLives} readOnly={readOnly} onAction={act} key={`${block.type}-${index}`} />)}
        {showNetwork && npcNetwork && <NpcNetworkBlock network={npcNetwork} readOnly={readOnly} onAction={act} />}
        {showSectMembership && sectMembership && <SectMembershipPage membership={sectMembership} busy={readOnly} readOnly={readOnly} onAction={act} />}
      </div>
      {presentation.has_details && (
        <details className="full-record"><summary>查看完整推演记录</summary><pre>{presentation.details}</pre></details>
      )}
    </article>
  )
}
