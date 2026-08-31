import * as Dialog from '@radix-ui/react-dialog'
import { Bone, ChevronRight, Heart, History, PawPrint, ShieldCheck, Sparkles, Swords, X, Zap } from 'lucide-react'
import type { SpiritBeastSnapshot } from '../api/types'

interface Props {
  beasts: SpiritBeastSnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

export function SpiritBeastSanctuary({ beasts, busy, readOnly = false, onAction }: Props) {
  const active = beasts.beasts.find((item) => item.active)
  return <Dialog.Root>
    <Dialog.Trigger asChild>
      <button className="beast-ribbon" type="button" data-active={Boolean(active) || undefined}>
        <span><PawPrint size={17} /></span>
        <div><small>万灵兽苑</small><strong>{active ? `${active.name}随行` : '静待灵缘'}</strong></div>
        {active ? <><i><b style={{ width: `${active.vigor}%` }} /></i><p>{active.level}级 · 羁绊 {active.bond}</p></> : <p>尚无战宠</p>}
        <em>{beasts.count} 只</em><ChevronRight size={16} />
      </button>
    </Dialog.Trigger>
    <Dialog.Portal>
      <Dialog.Overlay className="dialog-overlay" />
      <Dialog.Content className="character-dialog beast-dialog">
        <header>
          <div><p>万灵有性 · 契行九州</p><Dialog.Title>万灵兽苑</Dialog.Title><Dialog.Description>在不同地域追索兽踪，以神识结契；战宠会随历练成长，也需要精力与羁绊。</Dialog.Description></div>
          <Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close>
        </header>
        <section className="beast-overview">
          <span><PawPrint size={20} /></span>
          <div><small>当前随行</small><strong>{active?.name || '尚未结契'}</strong><p>{active ? `${active.role} · ${active.element}行 · ${active.level}级` : '先在当前地域探寻灵兽'}</p></div>
          <dl><div><dt>兽苑</dt><dd>{beasts.count}</dd></div><div><dt>灵材</dt><dd>{beasts.materials}</dd></div><div><dt>召唤</dt><dd>{beasts.summon_cost} 灵力</dd></div></dl>
          <button type="button" disabled={busy || readOnly || !beasts.can_search} title={beasts.search_reason || '消耗 10 灵力并推进一个月'} onClick={() => onAction(beasts.search_action)}><Sparkles size={14} />探寻兽踪</button>
        </section>
        <section className="beast-scroll">
          {beasts.beasts.length ? <div className="beast-grid">{beasts.beasts.map((beast) => {
            const experiencePercent = beast.experience_required ? Math.min(100, beast.experience / beast.experience_required * 100) : 100
            return <article key={beast.id} data-active={beast.active || undefined}>
              <header><span>{beast.mark}</span><div><small>{beast.element}行 · {beast.role}</small><h3>{beast.name}</h3></div><em>{beast.level} / {beast.max_level}级</em></header>
              <p>{beast.summary}</p><div className="beast-talent"><Zap size={13} /><span>{beast.talent}</span></div>
              <div className="beast-meters">
                <label><span><Heart size={12} />羁绊 <b>{beast.bond}</b></span><i><b style={{ width: `${beast.bond}%` }} /></i></label>
                <label><span><ShieldCheck size={12} />精力 <b>{beast.vigor}/{beast.vigor_max}</b></span><i><b style={{ width: `${beast.vigor / beast.vigor_max * 100}%` }} /></i></label>
                <label><span><Swords size={12} />历练 <b>{beast.experience_required ? `${beast.experience}/${beast.experience_required}` : '圆满'}</b></span><i><b style={{ width: `${experiencePercent}%` }} /></i></label>
              </div>
              <div className="beast-actions"><button type="button" data-active={beast.active || undefined} disabled={busy || readOnly || beast.active || !beast.can_deploy} title={beast.deploy_reason || (beast.active ? '当前随行战宠' : '切换随行战宠不推进时间')} onClick={() => onAction(beast.deploy_action)}><Swords size={13} />{beast.active ? '正在随行' : '设为战宠'}</button><button type="button" disabled={busy || readOnly || !beast.can_feed} title={beast.feed_reason || '消耗妖兽材料×1并推进一个月'} onClick={() => onAction(beast.feed_action)}><Bone size={13} />喂养</button></div>
            </article>
          })}</div> : <div className="beast-empty"><PawPrint size={34} /><strong>兽苑尚静</strong><p>东洲可以遇见青风狐与玄甲灵龟；游历五域后，还会出现各具天赋的灵兽。</p><button type="button" disabled={busy || readOnly || !beasts.can_search} title={beasts.search_reason} onClick={() => onAction(beasts.search_action)}>探寻第一道兽踪</button></div>}
          <section className="beast-history"><h3><History size={14} />万灵留痕</h3>{beasts.history.length ? <ol>{beasts.history.map((entry, index) => <li key={`${entry}-${index}`}><span>{beasts.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>尚未与灵兽结下因果。</p>}</section>
        </section>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
}
