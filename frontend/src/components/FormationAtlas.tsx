import * as Dialog from '@radix-ui/react-dialog'
import { ChevronRight, CircleGauge, Hammer, History, Orbit, Shield, Sparkles, Wrench, X } from 'lucide-react'
import type { FormationSnapshot } from '../api/types'

interface Props {
  formations: FormationSnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

export function FormationAtlas({ formations, busy, readOnly = false, onAction }: Props) {
  const active = formations.arrays.find((item) => item.active)
  return <Dialog.Root>
    <Dialog.Trigger asChild>
      <button className="formation-ribbon" type="button" data-active={Boolean(active) || undefined}>
        <span><Orbit size={17} /></span>
        <div><small>五行阵图</small><strong>{active ? `${active.name}运转` : '阵枢未定'}</strong></div>
        {active ? <><i><b style={{ width: `${active.integrity}%` }} /></i><p>阵基 {active.integrity}/{active.integrity_max}</p></> : <p>尚未装配阵盘</p>}
        <em>{formations.count} 卷</em><ChevronRight size={16} />
      </button>
    </Dialog.Trigger>
    <Dialog.Portal>
      <Dialog.Overlay className="dialog-overlay" />
      <Dialog.Content className="character-dialog formation-dialog">
        <header>
          <div><p>结界 · 困敌 · 聚灵 · 杀伐</p><Dialog.Title>五行阵图</Dialog.Title><Dialog.Description>研习阵图、炼成阵盘并装配于身。阵基会在战斗中损耗，阵道修为可降低催动代价。</Dialog.Description></div>
          <Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close>
        </header>
        <section className="formation-overview">
          <span><Orbit size={21} /></span>
          <div><small>当前阵枢</small><strong>{active?.name || '尚未装配'}</strong><p>{active ? `${active.element === '五行' ? active.element : `${active.element}行`} · ${active.role} · 阵基 ${active.integrity}%` : '炼成第一卷阵图后会自动装配'}</p></div>
          <dl><div><dt>阵图</dt><dd>{formations.count}</dd></div><div><dt>阵法</dt><dd>{formations.skill_level} 级</dd></div><div><dt>阵道</dt><dd>{formations.dao_level} 层</dd></div></dl>
        </section>
        <section className="formation-scroll">
          <div className="formation-grid">{formations.arrays.map((formation) => <article key={formation.id} data-active={formation.active || undefined} data-role={formation.role}>
            <header><span>{formation.mark}</span><div><small>{formation.element === '五行' ? formation.element : `${formation.element}行`} · {formation.role}</small><h3>{formation.name}</h3></div><em>{formation.owned ? '已炼成' : `准入 ${formation.minimum_realm}`}</em></header>
            <p>{formation.summary}</p>
            <div className="formation-effect"><Sparkles size={13} /><span>{formation.effect}</span></div>
            <dl><div><dt>阵材</dt><dd>{formation.ingredients}</dd></div><div><dt>成功率</dt><dd>{formation.chance}%</dd></div></dl>
            {formation.owned && <div className="formation-integrity"><span><Shield size={12} />阵基完整度 <b>{formation.integrity}/{formation.integrity_max}</b></span><i><b style={{ width: `${formation.integrity}%` }} /></i></div>}
            <div className="formation-actions">
              {!formation.owned ? <button type="button" disabled={busy || readOnly || !formation.can_build} title={formation.build_reason || '消耗阵材并推进一个月'} onClick={() => onAction(formation.build_action)}><Hammer size={13} />炼制阵盘</button> : <>
                <button type="button" data-active={formation.active || undefined} disabled={busy || readOnly || formation.active || !formation.can_deploy} title={formation.deploy_reason || (formation.active ? '当前装配阵盘' : '更换阵盘不推进时间')} onClick={() => onAction(formation.deploy_action)}><CircleGauge size={13} />{formation.active ? '阵枢运转中' : '装配阵盘'}</button>
                <button type="button" disabled={busy || readOnly || !formation.can_repair} title={formation.repair_reason || '消耗灵铁×1并推进一个月'} onClick={() => onAction(formation.repair_action)}><Wrench size={13} />修复阵基</button>
              </>}
            </div>
            {(!formation.owned && formation.build_reason) && <small>{formation.build_reason}</small>}
          </article>)}</div>
          <section className="formation-history"><h3><History size={14} />阵纹留痕</h3>{formations.history.length ? <ol>{formations.history.map((entry, index) => <li key={`${entry}-${index}`}><span>{formations.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>尚未留下炼阵记录。</p>}</section>
        </section>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
}
