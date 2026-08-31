import * as Dialog from '@radix-ui/react-dialog'
import { BookOpenText, ChevronRight, CircleDollarSign, Crown, Handshake, History, Landmark, LockKeyhole, Send, Shield, Sparkles, Swords, UserPlus, UsersRound, X } from 'lucide-react'
import type { SectDiplomacySnapshot, SectDomainSnapshot } from '../api/types'

interface Props {
  domain: SectDomainSnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

export function SectDominion({ domain, busy, readOnly = false, onAction }: Props) {
  if (!domain.visible) return null
  const sect = domain.sect
  return <Dialog.Root>
    <Dialog.Trigger asChild>
      <button className="domain-ribbon" type="button" data-founded={domain.founded || undefined} data-pending={domain.pending || undefined} data-ruined={sect.ruined || undefined}>
        <span>{domain.founded ? <Crown size={17} /> : <Landmark size={17} />}</span>
        <div><small>{domain.founded ? sect.ruined ? '故宗遗脉 · 流亡道统' : sect.level_name : '金丹之后 · 一方之主'}</small><strong>{domain.founded ? sect.name : domain.pending ? '择定开山道统' : '开宗立派'}</strong></div>
        <p>{domain.founded ? sect.ruined ? '山门已经覆灭 · 掌门携残存道统流亡' : `${domain.disciples.length} 名门人 · 月净 ${(sect.monthly_net || 0) >= 0 ? '+' : ''}${sect.monthly_net || 0}` : domain.pending ? `${domain.suggested_name}等待道统` : domain.found_reason || '资粮与声名俱足'}</p>
        <em>{domain.founded ? sect.ruined ? '不可经营' : `${sect.treasury} 库藏` : domain.requirements.filter((item) => item.met).length + '/4'}</em><ChevronRight size={16} />
      </button>
    </Dialog.Trigger>
    <Dialog.Portal>
      <Dialog.Overlay className="dialog-overlay" />
      <Dialog.Content className="character-dialog domain-dialog">
        <header>
          <div><p>{domain.founded ? sect.ruined ? '故宗遗脉 · 道统未绝' : '传道授业 · 山门长青' : '聚众传法 · 自立道统'}</p><Dialog.Title>{domain.founded ? sect.name : '开宗立派'}</Dialog.Title><Dialog.Description>{domain.founded ? sect.ruined ? '山门虽已覆灭，本世留下的门人、战史与道统仍会进入仙途评传。' : '门人、库藏、道统与山门设施会随九州月份真实演化。' : '达到金丹、积累声望与资粮后，可亲立山门并从三种根本道统中择一。'}</Dialog.Description></div>
          <Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close>
        </header>

        {!domain.founded ? <Foundation domain={domain} busy={busy} readOnly={readOnly} onAction={onAction} /> : <Dominion domain={domain} busy={busy} readOnly={readOnly} onAction={onAction} />}
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
}

function Foundation({ domain, busy, readOnly, onAction }: Props) {
  return <div className="domain-scroll">
    <section className="foundation-overview">
      <span><Landmark size={22} /></span><div><small>拟立山门</small><strong>{domain.suggested_name}</strong><p>也可在自由行动中输入“开宗立派 自定义宗门名”。</p></div>
      <em>{domain.pending ? '名号已定' : domain.can_found ? '可以立宗' : '资粮未足'}</em>
    </section>
    <div className="foundation-requirements">{domain.requirements.map((item) => <div key={item.label} data-met={item.met || undefined}><span>{item.met ? <Sparkles size={13} /> : <LockKeyhole size={13} />}{item.label}</span><strong>{item.current}</strong><small>需要 {item.value}</small></div>)}</div>
    <section className="foundation-doctrines"><div className="domain-section-title"><BookOpenText size={16} /><div><small>一宗根本</small><strong>{domain.pending ? '亲自择定道统' : '预览三种道统'}</strong></div></div><div>{domain.doctrines.map((item) => <article key={item.id}><header><span>{item.mark}</span><div><small>根本道统</small><h3>{item.name}</h3></div></header><p>{item.summary}</p><strong>{item.effect}</strong>{domain.pending && <button type="button" disabled={busy || readOnly} title={readOnly ? '巡览模式不会修改存档' : item.effect} onClick={() => onAction(item.action)}>立此道统</button>}</article>)}</div></section>
    <footer className="foundation-footer"><p>{readOnly ? '成果巡览中不会消耗灵石或建立宗门。' : domain.pending ? '确认道统后才会消耗 2000 灵石。' : domain.found_reason || '立宗后会获得两名开山弟子。'}</p>{domain.pending ? <button className="quiet" type="button" disabled={busy || readOnly} onClick={() => onAction('取消立宗')}>暂缓立宗</button> : <button type="button" disabled={busy || readOnly || !domain.can_found} title={domain.found_reason || '使用建议名号进入道统选择'} onClick={() => onAction(domain.begin_action)}><Crown size={15} />筹建立宗</button>}</footer>
  </div>
}

function Dominion({ domain, busy, readOnly = false, onAction }: Props) {
  const sect = domain.sect
  return <div className="domain-scroll">
    <section className="domain-overview">
      <span>{sect.doctrine_mark}</span><div><small>{sect.level_name} · 天玄历 {sect.founded_year} 年开宗</small><strong>{sect.doctrine_name}</strong><p>{sect.doctrine_effect}</p></div>
      <dl><div><dt>宗门实力</dt><dd>{sect.strength}</dd></div><div><dt>山门声望</dt><dd>{sect.renown}</dd></div><div><dt>稳定</dt><dd>{sect.stability}</dd></div><div><dt>库藏</dt><dd>{sect.treasury}</dd></div></dl>
    </section>
    <div className="domain-growth"><span><i><b style={{ width: `${sect.experience_percent || 0}%` }} /></i><small>宗门底蕴 {sect.experience}/{sect.experience_required}</small></span><em>月度收支 {(sect.monthly_net || 0) >= 0 ? '+' : ''}{sect.monthly_net || 0}{sect.war_scars ? ` · 战损 ${sect.war_scars}` : ''}</em></div>
    <section className="domain-actions"><button type="button" disabled={busy || readOnly || !domain.can_recruit} title={domain.recruit_reason || `消耗 ${domain.recruit_cost} 库藏，推进一个月`} onClick={() => onAction(domain.recruit_action || '宗门招徒')}><UserPlus size={16} /><span><strong>开山收徒</strong><small>{domain.recruit_reason || `${domain.recruit_cost} 库藏 · 1 个月`}</small></span></button><button type="button" disabled={busy || readOnly || !domain.can_teach} title={domain.teach_reason || `消耗 ${domain.teach_cost} 库藏，推进一个月`} onClick={() => onAction(domain.teach_action || '宗门传法')}><BookOpenText size={16} /><span><strong>掌门传法</strong><small>{domain.teach_reason || `${domain.teach_cost} 库藏 · 每年一次`}</small></span></button></section>

    <Diplomacy diplomacy={domain.diplomacy} busy={busy} readOnly={readOnly} onAction={onAction} />

    <section className="domain-section"><div className="domain-section-title"><Shield size={16} /><div><small>每年一议</small><strong>宗门方针</strong></div></div><div className="domain-focuses">{domain.focuses.map((focus) => <button key={focus.id} type="button" data-current={focus.current || undefined} disabled={busy || readOnly || !focus.available} title={focus.disabled_reason || focus.effect} onClick={() => onAction(focus.action)}><strong>{focus.name}</strong><small>{focus.effect}</small></button>)}</div></section>

    <section className="domain-section"><div className="domain-section-title"><Landmark size={16} /><div><small>三处基业</small><strong>山门营造</strong></div></div><div className="domain-buildings">{domain.buildings.map((building) => <article key={building.id}><header><span>{building.mark}</span><div><small>{building.level}/{building.max_level} 级</small><h3>{building.name}</h3></div></header><p>{building.summary}</p><i>{Array.from({ length: building.max_level }, (_, index) => <b key={index} data-lit={index < building.level || undefined} />)}</i><button type="button" disabled={busy || readOnly || !building.available} title={building.disabled_reason || `消耗 ${building.cost} 库藏，工期三个月`} onClick={() => onAction(building.action)}>{building.available ? `营造 · ${building.cost}` : building.disabled_reason}</button></article>)}</div></section>

    <section className="domain-section"><div className="domain-section-title"><UsersRound size={16} /><div><small>{domain.disciples.length}/12 人</small><strong>门人名录</strong></div></div><div className="disciple-grid">{domain.disciples.map((disciple) => <article key={disciple.name}><header><span>{disciple.name.slice(0, 1)}</span><div><small>{disciple.role} · 资质 {disciple.aptitude}</small><h3>{disciple.name}</h3></div><em>忠诚 {disciple.loyalty}</em></header><p>{disciple.realm}</p><i><b style={{ width: `${disciple.progress_percent}%` }} /></i><small>修行 {disciple.progress}/{disciple.progress_required}</small></article>)}</div></section>

    <section className="domain-history"><h3><History size={14} />山门纪事</h3>{domain.history.length ? <ol>{domain.history.map((entry, index) => <li key={`${entry}-${index}`}><span>{domain.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>开山钟声初响，尚无更多纪事。</p>}</section>
    <footer className="domain-ledger"><CircleDollarSign size={14} />宗门财政独立于个人灵石；招徒、传法与营造均从库藏结算。</footer>
  </div>
}

function Diplomacy({ diplomacy, busy, readOnly, onAction }: { diplomacy: SectDiplomacySnapshot; busy: boolean; readOnly: boolean; onAction: (action: string) => void }) {
  if (!diplomacy.visible) return null
  return <section className="domain-section diplomacy-section">
    <div className="domain-section-title"><Handshake size={16} /><div><small>一年一议 · 商盟月入 +{diplomacy.income_bonus}</small><strong>九州外务</strong></div><em>{diplomacy.acted_this_year ? '本年已定' : '可主持外务'}</em></div>
    {diplomacy.war.active && <div className="sect-war-alert"><Swords size={18} /><div><small>{diplomacy.war.side} · 已历 {diplomacy.war.months} 月</small><strong>正与{diplomacy.war.target}交战</strong><p>{diplomacy.war.momentum_label} · 战局声势 {(diplomacy.war.momentum || 0) >= 0 ? '+' : ''}{diplomacy.war.momentum}</p></div><em>{diplomacy.war.player_acted ? '掌门已决策' : '可前往护宗战'}</em></div>}
    <div className="diplomacy-grid">{diplomacy.factions.map((faction) => <article key={faction.name} data-war={faction.at_war || undefined} data-fallen={faction.fallen || undefined}>
      <header><span>{faction.mark}</span><div><small>{faction.path} · 实力 {faction.strength}</small><h3>{faction.name}</h3></div><em>{faction.stance}</em></header>
      <div className="relation-meter"><i><b style={{ width: `${faction.relation_percent}%` }} /></i><strong>{faction.relation > 0 ? '+' : ''}{faction.relation}</strong></div>
      <p>{faction.description}</p><div className="treaty-chip"><Handshake size={11} />{faction.treaty_label}</div>
      <footer><button type="button" disabled={busy || readOnly || !faction.primary.available} title={faction.primary.reason || faction.primary.label} onClick={() => faction.primary.action && onAction(faction.primary.action)}><Send size={12} />{faction.primary.label}</button><button type="button" disabled={busy || readOnly || !faction.secondary.available} title={faction.secondary.reason || faction.secondary.label} onClick={() => faction.secondary.action && onAction(faction.secondary.action)}><Swords size={12} />{faction.secondary.label}</button></footer>
    </article>)}</div>
    <details className="diplomacy-history"><summary>外务纪事 · 胜 {diplomacy.victories || 0} / 负 {diplomacy.defeats || 0}</summary>{diplomacy.history.length ? <ol>{diplomacy.history.map((entry, index) => <li key={`${entry}-${index}`}>{entry}</li>)}</ol> : <p>山门初立，尚未遣使九州。</p>}</details>
  </section>
}
