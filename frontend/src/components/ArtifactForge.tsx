import * as Dialog from '@radix-ui/react-dialog'
import { Anvil, CircleGauge, Coins, Gem, History, LockKeyhole, Shield, Sparkles, Swords, X, Zap } from 'lucide-react'
import type { ArtifactGrowthSnapshot } from '../api/types'

interface ArtifactForgeProps {
  artifacts: ArtifactGrowthSnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

export function ArtifactForge({ artifacts, busy, readOnly = false, onAction }: ArtifactForgeProps) {
  if (!artifacts.count) return null
  const bonded = artifacts.bonded
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button className="artifact-ribbon" type="button" data-bonded={Boolean(artifacts.bonded_name) || undefined}>
          <span><Gem size={17} /></span>
          <div><small>{artifacts.bonded_name ? '器心已契' : '器心待定'}</small><strong>本命法宝</strong></div>
          <p>{artifacts.bonded_name ? `${artifacts.bonded_name} · ${bonded.level_label}` : `${artifacts.count} 件法宝可认主`}</p>
          <i><b style={{ width: `${bonded.resonance || 0}%` }} /></i>
          <em>{artifacts.bonded_name ? `契合 ${bonded.resonance}/100` : '尚未认主'}</em>
          <Sparkles size={14} />
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog artifact-dialog">
          <header><div><p>器成有灵 · 神魂相契</p><Dialog.Title>本命法宝</Dialog.Title><Dialog.Description>装备只是起点。认主、淬炼和实战共鸣会让同一件法宝走出不同成长轨迹。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
          <section className="artifact-overview">
            <span>{artifacts.bonded_name ? <Sparkles size={22} /> : <Gem size={22} />}</span>
            <div><small>当前本命</small><strong>{artifacts.bonded_name || '器心未定'}</strong><p>{artifacts.bonded_name ? `${bonded.grade} · ${bonded.slot} · ${bonded.effect}` : '先装备一件法宝，再以灵力祭炼认主'}</p></div>
            <dl><div><dt>淬炼上限</dt><dd>{artifacts.level_cap_label}</dd></div><div><dt>持有法宝</dt><dd>{artifacts.count} 件</dd></div></dl>
          </section>
          <div className="artifact-resources" aria-label="淬炼资源">
            <span><Coins size={13} /><small>灵石</small><strong>{artifacts.materials.spirit_stones}</strong></span>
            <span><Zap size={13} /><small>灵力</small><strong>{artifacts.materials.spirit}/{artifacts.materials.spirit_max}</strong></span>
            <span><Anvil size={13} /><small>灵铁</small><strong>{artifacts.materials.spirit_iron}</strong></span>
            <span><Gem size={13} /><small>妖兽材料</small><strong>{artifacts.materials.beast_materials}</strong></span>
          </div>
          <section className="artifact-scroll">
            <div className="artifact-grid">
              {artifacts.artifacts.map((item) => (
                <article key={item.name} data-bonded={item.bonded || undefined} data-equipped={item.equipped || undefined}>
                  <header><span>{item.slot === '武器' ? <Swords size={17} /> : <Shield size={17} />}</span><div><small>{item.grade} · {item.slot}{item.element ? ` · ${item.element}行` : ''}</small><h3>{item.name}</h3></div><em>{item.bonded ? '本命' : item.equipped ? '已装备' : '袋中'}</em></header>
                  <div className="artifact-growth"><div><span>{item.level_label}</span><small>境界上限 {item.level_cap} 炼</small></div><div><span>{item.effect}</span><small>历战 {item.victories} 场</small></div></div>
                  <div className="artifact-resonance"><span><Sparkles size={12} />器心契合</span><i><b style={{ width: `${item.resonance}%` }} /></i><strong>{item.resonance}/100</strong></div>
                  <div className="artifact-refine"><span><CircleGauge size={13} />下次淬炼 {item.refine_chance}%</span><small>{item.refine_cost}</small></div>
                  <footer>
                    <button className="quiet" type="button" disabled={!item.can_bind || busy || readOnly} title={readOnly ? '巡览模式不会修改存档' : item.bind_reason || '消耗灵力，将此物祭为本命'} onClick={() => onAction(item.bind_action)}>{item.bonded ? <Sparkles size={13} /> : item.can_bind ? <Gem size={13} /> : <LockKeyhole size={13} />}{item.bonded ? '已认主' : item.bind_reason || '祭炼认主'}</button>
                    <button type="button" disabled={!item.can_refine || busy || readOnly} title={readOnly ? '巡览模式不会修改存档' : item.refine_reason || item.refine_cost} onClick={() => onAction(item.refine_action)}>{item.can_refine ? <Anvil size={13} /> : <LockKeyhole size={13} />}{item.refine_reason || '开炉淬炼'}</button>
                    <button className="warm" type="button" disabled={!item.can_nourish || busy || readOnly} title={readOnly ? '巡览模式不会修改存档' : item.nourish_reason || '消耗灵力并推进一个月'} onClick={() => onAction(item.nourish_action)}>{item.can_nourish ? <Sparkles size={13} /> : <LockKeyhole size={13} />}{item.nourish_reason || '温养器心'}</button>
                  </footer>
                </article>
              ))}
            </div>
            <section className="artifact-history"><h3><History size={14} />器火留痕</h3>{artifacts.history.length ? <ol>{artifacts.history.map((entry, index) => <li key={`${entry}-${index}`}><span>{artifacts.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>尚未留下认主、淬炼或温养记录。</p>}</section>
          </section>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
