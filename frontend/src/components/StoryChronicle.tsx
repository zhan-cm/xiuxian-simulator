import * as Dialog from '@radix-ui/react-dialog'
import { BookOpen, Check, ChevronRight, LockKeyhole, MapPin, ScrollText, Sparkles, X } from 'lucide-react'
import type { StorySnapshot } from '../api/types'

interface Props { story: StorySnapshot; busy: boolean; readOnly?: boolean; onAction: (action: string) => void }

export function StoryChronicle({ story, busy, readOnly = false, onAction }: Props) {
  const next = story.chapters.find((chapter) => !chapter.completed)
  return <Dialog.Root>
    <Dialog.Trigger asChild><button className="story-ribbon" type="button" data-ready={story.available || Boolean(story.pending) || undefined}><span><BookOpen size={17} /></span><div><small>灵潮主线</small><strong>{story.title}</strong></div><p>{story.pending ? '因果等待抉择' : story.available ? '新因果可推进' : story.next_hint}</p><em>{story.completed}/{story.total}</em><ChevronRight size={16} /></button></Dialog.Trigger>
    <Dialog.Portal><Dialog.Overlay className="dialog-overlay" /><Dialog.Content className="character-dialog story-dialog">
      <header><div><p>一念落子 · 九州生变</p><Dialog.Title>灵潮因果录</Dialog.Title><Dialog.Description>主线只在条件成熟时出现；每次选择都会推进时间并永久改变本世。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
      <div className="story-summary"><Sparkles size={16} /><span>篇章进度</span><strong>{story.completed}/{story.total}</strong><small>{story.pending ? `《${story.title}》正在等待你的选择` : story.available ? `当前可推进《${next?.title || story.title}》` : story.next_hint}</small>{story.available && <button type="button" disabled={busy || readOnly} onClick={() => onAction(story.begin_action)}>推进主线</button>}</div>
      <div className="story-chapters">{story.chapters.map((chapter) => <article key={chapter.id} data-complete={chapter.completed || undefined} data-locked={!chapter.unlocked || undefined}><span>{chapter.completed ? <Check size={15} /> : chapter.unlocked ? chapter.chapter : <LockKeyhole size={14} />}</span><div><small>第 {chapter.chapter} 章 · <MapPin size={11} />{chapter.location}</small><h3>{chapter.title}</h3><p>{chapter.summary}</p>{chapter.completed && <em><ScrollText size={12} />因果已定：{chapter.choice}</em>}{!chapter.unlocked && <em>{chapter.locked_hint}</em>}</div></article>)}</div>
      {story.history.length > 0 && <section className="story-history"><h3>因果留痕</h3>{story.history.map((entry) => <p key={entry}>{entry}</p>)}</section>}
    </Dialog.Content></Dialog.Portal>
  </Dialog.Root>
}
