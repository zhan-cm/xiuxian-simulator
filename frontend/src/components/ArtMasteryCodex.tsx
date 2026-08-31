import * as Dialog from '@radix-ui/react-dialog'
import { BookOpenText, Brain, Flame, History, LockKeyhole, ScrollText, Sparkles, Swords, X, Zap } from 'lucide-react'
import type { ArtMasteryItem, ArtMasterySnapshot } from '../api/types'

interface Props {
  mastery: ArtMasterySnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

function MasteryCard({ item, busy, readOnly, onAction }: { item: ArtMasteryItem; busy: boolean; readOnly: boolean; onAction: (action: string) => void }) {
  const active = ['主修', '辅修', '已装备'].includes(item.role)
  return (
    <article className="mastery-card" data-active={active || undefined} data-kind={item.kind}>
      <header>
        <span>{item.kind === '功法' ? <BookOpenText size={17} /> : <Flame size={17} />}</span>
        <div><small>{item.grade}{item.element ? ` · ${item.element}行` : ''}</small><h3>{item.name}</h3></div>
        <em>{item.role}</em>
      </header>
      <p>{item.description}</p>
      <div className="mastery-level"><span><Sparkles size={12} />{item.level_label}</span><i><b style={{ width: `${item.progress}%` }} /></i><strong>{item.xp}/{item.next_xp}</strong></div>
      <dl><div><dt>当前领悟</dt><dd>{item.effect}</dd></div><div><dt>下一境界</dt><dd>{item.next_effect}</dd></div></dl>
      <button type="button" disabled={!item.can_study || busy || readOnly} title={readOnly ? '巡览模式不会修改存档' : item.disabled_reason || `消耗 ${12} 灵力并推进一个月`} onClick={() => onAction(item.study_action)}>
        {item.can_study ? <ScrollText size={13} /> : <LockKeyhole size={13} />}{item.disabled_reason || '参研一月'}
      </button>
    </article>
  )
}

export function ArtMasteryCodex({ mastery, busy, readOnly = false, onAction }: Props) {
  if (!mastery.known_count) return null
  const primary = mastery.primary
  const spell = mastery.equipped_spell
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button className="mastery-ribbon" type="button">
          <span><BookOpenText size={17} /></span>
          <div><small>道法谱</small><strong>{primary.name || '未定主修'}</strong></div>
          <p>{primary.level_label || '初窥'} · {primary.effect || '尚待参研'}</p>
          <i><b style={{ width: `${primary.progress || 0}%` }} /></i>
          <em>{spell.name ? `${spell.name} · ${spell.level_label}` : `${mastery.known_count} 门道法`}</em>
          <Sparkles size={14} />
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog mastery-dialog">
          <header><div><p>万法由生至熟 · 由熟入道</p><Dialog.Title>功法境界与道法熟练度</Dialog.Title><Dialog.Description>吐纳、闭关、实战施法与主动参研都会留下真实积累，并改变修炼与战斗结算。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
          <section className="mastery-overview">
            <span><Swords size={22} /></span>
            <div><small>当前构筑</small><strong>{primary.name || '未定主修'} · {primary.level_label || '初窥'}</strong><p>{spell.name ? `配术 ${spell.name} · ${spell.level_label}` : '尚未装备法术'}</p></div>
            <dl><div><dt>已悟道法</dt><dd>{mastery.known_count}</dd></div><div><dt>圆满</dt><dd>{mastery.mastered_count}</dd></div></dl>
          </section>
          <div className="mastery-resources"><span><Zap size={13} /><small>灵力</small><strong>{mastery.spirit}/{mastery.spirit_max}</strong></span><span><Brain size={13} /><small>悟性</small><strong>{mastery.comprehension}</strong></span><span><ScrollText size={13} /><small>参研消耗</small><strong>{mastery.study_cost} 灵力 / 月</strong></span></div>
          <section className="mastery-scroll">
            <div className="mastery-section"><h2><BookOpenText size={15} />功法心诀 <small>{mastery.techniques.length} 门</small></h2><div className="mastery-grid">{mastery.techniques.map((item) => <MasteryCard key={item.name} item={item} busy={busy} readOnly={readOnly} onAction={onAction} />)}</div></div>
            <div className="mastery-section"><h2><Flame size={15} />术法神通 <small>{mastery.spells.length} 门</small></h2><div className="mastery-grid">{mastery.spells.map((item) => <MasteryCard key={item.name} item={item} busy={busy} readOnly={readOnly} onAction={onAction} />)}</div></div>
            <section className="mastery-history"><h3><History size={14} />参研留痕</h3>{mastery.history.length ? <ol>{mastery.history.map((entry, index) => <li key={`${entry}-${index}`}><span>{mastery.history.length - index}</span><p>{entry}</p></li>)}</ol> : <p>尚未留下晋境或参研记录。</p>}</section>
          </section>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
