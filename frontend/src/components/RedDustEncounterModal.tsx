import * as Dialog from '@radix-ui/react-dialog'
import {
  Compass,
  Flame,
  HeartHandshake,
  MessageSquareQuote,
  ScrollText,
  ShieldAlert,
  Sparkles,
  Swords,
  X,
} from 'lucide-react'
import type { PendingEncounterData } from '../api/types'
import { NpcAvatar } from './NpcAvatar'

export interface RedDustEncounterModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  encounter?: PendingEncounterData | null
  busy?: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

export function RedDustEncounterModal({
  open,
  onOpenChange,
  encounter,
  busy = false,
  readOnly = false,
  onAction,
}: RedDustEncounterModalProps) {
  if (!encounter) return null

  const { character, choices, scene, title, category } = encounter

  const getStanceIcon = (stance: string) => {
    if (stance.includes('善') || stance.includes('慈') || stance.includes('仁')) {
      return <HeartHandshake size={15} className="text-emerald-400" />
    }
    if (stance.includes('杀') || stance.includes('魔') || stance.includes('掠') || stance.includes('夺')) {
      return <Swords size={15} className="text-rose-400" />
    }
    if (stance.includes('道') || stance.includes('悟') || stance.includes('逍遥')) {
      return <Sparkles size={15} className="text-amber-400" />
    }
    if (stance.includes('利') || stance.includes('商') || stance.includes('换')) {
      return <Flame size={15} className="text-orange-400" />
    }
    return <Compass size={15} className="text-cyan-400" />
  }

  const categoryLabel =
    category === 'ancient_secret'
      ? '太古秘境机缘'
      : category === 'npc_destiny'
        ? '故人红尘奇遇'
        : category === 'spirit_creature'
          ? '灵宠异兽道缘'
          : '九州红尘善恶'

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay encounter-dialog-overlay" />
        <Dialog.Content
          className="dialog-content encounter-modal-content"
          aria-describedby="encounter-scene-desc"
        >
          <header className="encounter-modal-header">
            <div className="encounter-header-left">
              <span className="encounter-category-badge">
                <Sparkles size={13} />
                <span>{categoryLabel}</span>
              </span>
              <Dialog.Title className="encounter-modal-title">《{title}》</Dialog.Title>
            </div>
            <Dialog.Close asChild>
              <button type="button" className="close-btn encounter-close-btn" aria-label="暂且静观">
                <X size={18} />
              </button>
            </Dialog.Close>
          </header>

          <main className="encounter-stage-layout">
            {/* 左侧：出场人物立绘与名帖 */}
            <aside className="encounter-actor-stage">
              <div className="encounter-avatar-wrapper">
                <NpcAvatar
                  item={{
                    name: character.name,
                    identity: character.identity,
                    realm: character.realm,
                  }}
                  size="vn"
                  className="encounter-actor-avatar"
                />
              </div>
              <div className="encounter-actor-card">
                <h3 className="encounter-actor-name">{character.name}</h3>
                <div className="encounter-actor-meta">
                  <span className="actor-identity-tag">{character.identity}</span>
                  <span className="actor-realm-tag">{character.realm}</span>
                </div>
              </div>
            </aside>

            {/* 右侧：经典对白、场景叙事与道心分支 */}
            <section className="encounter-narrative-stage">
              {/* 人物台词气泡 */}
              <div className="encounter-speech-bubble">
                <div className="speech-speaker-label">
                  <MessageSquareQuote size={15} />
                  <span>{character.name}</span>
                </div>
                <blockquote className="speech-text">“{character.quote}”</blockquote>
              </div>

              {/* 场景氛围长卷 */}
              <div className="encounter-scene-box" id="encounter-scene-desc">
                <div className="scene-box-header">
                  <ScrollText size={14} />
                  <span>天道因果画卷</span>
                </div>
                <p className="scene-box-text">{scene}</p>
              </div>

              {/* 道心分支卡片组 */}
              <div className="encounter-choices-container">
                <h4 className="choices-heading">
                  <span>遵从本心 · 抉择因果</span>
                  <small>一念动天心，善恶皆留痕</small>
                </h4>
                <div className="encounter-choice-list">
                  {choices.map((choice) => {
                    const isDisabled = busy || readOnly || choice.disabled
                    return (
                      <button
                        key={choice.id}
                        type="button"
                        className={`encounter-choice-card tone-${choice.tone || 'primary'}`}
                        disabled={isDisabled}
                        onClick={() => {
                          onAction(`奇遇选择 ${choice.id}`)
                        }}
                      >
                        <div className="choice-card-top">
                          <div className="choice-stance-badge">
                            {getStanceIcon(choice.dao_stance)}
                            <span>【{choice.dao_stance}】</span>
                          </div>
                          <strong className="choice-card-label">{choice.label}</strong>
                          {choice.disabled && choice.disabled_reason && (
                            <span className="choice-disabled-tip" title={choice.disabled_reason}>
                              <ShieldAlert size={12} />
                              <span>{choice.disabled_reason}</span>
                            </span>
                          )}
                        </div>
                        <p className="choice-card-desc">{choice.description}</p>
                        <div className="choice-card-summary">
                          <span>因果回响：</span>
                          <em>{choice.summary}</em>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
            </section>
          </main>

          <footer className="encounter-modal-footer">
            <Compass size={14} />
            <span>红尘百态，皆为磨砺；凡尘一念，善恶因果皆将深植于命格之中。</span>
          </footer>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
