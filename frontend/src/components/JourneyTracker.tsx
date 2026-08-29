import * as Dialog from '@radix-ui/react-dialog'
import { Check, ChevronRight, Circle, Gift, LockKeyhole, MapPinned, Sparkles, X } from 'lucide-react'
import type { JourneySnapshot } from '../api/types'

interface JourneyTrackerProps {
  journey: JourneySnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

export function JourneyTracker({ journey, busy, readOnly = false, onAction }: JourneyTrackerProps) {
  const active = journey.active
  const progress = active.total_tasks ? Math.round(active.completed_tasks * 100 / active.total_tasks) : 0
  const next = active.tasks.find((task) => !task.complete) || active.tasks.find((task) => !task.claimed)
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild>
        <button className="journey-ribbon" type="button">
          <span><MapPinned size={17} /></span>
          <div><small>第 {active.number} 章 · 道途章程</small><strong>{active.title}</strong></div>
          <i><b style={{ width: `${progress}%` }} /></i>
          <em>{active.completed_tasks}/{active.total_tasks}</em>
          <p>{next ? `下一步：${next.title}` : active.reward_ready ? '本章奖励可以领取' : '本章历练已经完成'}</p>
          <ChevronRight size={17} />
        </button>
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog journey-dialog">
          <header><div><p>四卷长生路</p><Dialog.Title>道途章程</Dialog.Title><Dialog.Description>历练不会替你做决定，只把真实完成的修行足迹汇成长期目标。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
          <div className="journey-score"><Sparkles size={16} /><span>累计历练</span><strong>{journey.points}</strong><small>{readOnly ? '巡览模式仅供查看' : '完成目标后可领取真实资源'}</small></div>
          <div className="journey-chapters">
            {journey.chapters.map((chapter) => (
              <section className="journey-chapter" data-locked={!chapter.unlocked || undefined} data-complete={chapter.claimed || undefined} key={chapter.id}>
                <header><span>{chapter.claimed ? <Check size={16} /> : chapter.unlocked ? chapter.number : <LockKeyhole size={15} />}</span><div><small>第 {chapter.number} 章</small><h3>{chapter.title}</h3><p>{chapter.summary}</p></div><em>{chapter.completed_tasks}/{chapter.total_tasks}</em></header>
                {chapter.unlocked && <div className="journey-task-list">{chapter.tasks.map((task) => (
                  <article data-complete={task.complete || undefined} data-claimed={task.claimed || undefined} key={task.id}>
                    <span>{task.claimed ? <Check size={14} /> : task.complete ? <Gift size={14} /> : <Circle size={11} />}</span>
                    <div><strong>{task.title}</strong><p>{task.description}</p><small title={task.hint}>{task.complete ? task.reward : task.hint}</small></div>
                    {task.complete && !task.claimed ? <button type="button" disabled={busy || readOnly} title={readOnly ? '巡览模式不会修改存档' : `领取：${task.reward}`} onClick={() => onAction(task.claim_action)}>领取</button> : <em>{task.claimed ? '已领取' : '进行中'}</em>}
                  </article>
                ))}</div>}
                {chapter.unlocked && <footer><div><Gift size={15} /><span>章成奖励</span><strong>{chapter.reward}</strong></div>{chapter.claimed ? <em><Check size={13} />已领取</em> : <button type="button" disabled={!chapter.reward_ready || busy || readOnly} title={chapter.reward_ready ? '领取本章最终奖励' : '完成并领取全部小目标后解锁'} onClick={() => onAction(chapter.claim_action)}>领取章成奖励</button>}</footer>}
              </section>
            ))}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
