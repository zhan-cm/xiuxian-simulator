import { useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import {
  Sparkles,
  Zap,
  Shield,
  Heart,
  Swords,
  Send,
  Power,
  X,
  Gem,
  MessageCircle,
  Flame,
  Award,
  Scroll,
} from 'lucide-react'
import type {
  ArtifactSpiritData,
  ArtifactSpiritSnapshot,
} from '../api/types'

export interface ArtifactSpiritModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  artifactSpirit?: ArtifactSpiritSnapshot | null
  busy?: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

function ManifestationView({
  snapshot,
  busy,
  readOnly,
  onAction,
}: {
  snapshot: ArtifactSpiritSnapshot
  busy: boolean
  readOnly: boolean
  onAction: (action: string) => void
}) {
  const [selectedId, setSelectedId] = useState<string>('sword_fairy')
  const [customName, setCustomName] = useState<string>('')

  const selectedArch =
    snapshot.archetypes.find((a) => a.id === selectedId) || snapshot.archetypes[0]

  const handleManifest = () => {
    if (busy || readOnly || !snapshot.can_manifest) return
    const cmd = customName.trim()
      ? `器灵化形 ${selectedId} ${customName.trim()}`
      : `器灵化形 ${selectedId}`
    onAction(cmd)
  }

  return (
    <div className="spirit-manifest-view">
      <div className="spirit-bonded-banner">
        <div className="banner-left">
          <span className="banner-label">本命所依</span>
          <h3 className="bonded-title">
            【{snapshot.bonded_artifact || '未认主本命法宝'}】
          </h3>
          <div className="resonance-bar-wrapper">
            <span className="resonance-text">
              器心契合：{snapshot.resonance}/100（化形门槛：30）
            </span>
            <div className="resonance-track">
              <div
                className="resonance-fill"
                style={{ width: `${Math.min(100, snapshot.resonance)}%` }}
              />
            </div>
          </div>
        </div>

        <div className="banner-right">
          {snapshot.can_manifest ? (
            <div className="manifest-status ready">
              <Sparkles size={18} />
              <span>器心通透 · 随时可唤醒化形</span>
            </div>
          ) : (
            <div className="manifest-status locked">
              <span>{snapshot.manifest_reason || '契合度不足'}</span>
            </div>
          )}
        </div>
      </div>

      <div className="spirit-intro-card">
        <h4>本命化形 · 太古灵识</h4>
        <p>
          本命法宝经千锤百炼、日夜心神温养，其器心自生灵性。
          举行化形大典后，器灵将幻化为独立人形侍从常驻身旁，斗法时可释放专属本命神通并增强修士护体罡气！
        </p>
      </div>

      <h4 className="archetypes-title">选择器灵化形原型</h4>
      <div className="archetype-cards-grid">
        {snapshot.archetypes.map((arch) => {
          const isSelected = arch.id === selectedId
          return (
            <div
              key={arch.id}
              className={`archetype-card ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedId(arch.id)}
            >
              <div className="arch-card-header">
                <div className="arch-identity">
                  <h5>{arch.name}</h5>
                  <span className="arch-title">{arch.title}</span>
                </div>
                <span className="arch-personality-tag">{arch.personality}</span>
              </div>
              <p className="arch-desc">{arch.description}</p>
              <div className="arch-skill-box">
                <span className="skill-tag">神通</span>
                <span className="skill-name">《{arch.combat_skill_name}》</span>
                <p className="skill-desc">{arch.combat_skill_desc}</p>
              </div>
              <div className="arch-stat-pills">
                {arch.attack_multiplier > 1.0 && (
                  <span className="stat-pill atk">
                    攻击加成 +{Math.round((arch.attack_multiplier - 1.0) * 100)}%
                  </span>
                )}
                {arch.defense_bonus > 0 && (
                  <span className="stat-pill def">防御 +{arch.defense_bonus}</span>
                )}
                {arch.max_health_bonus > 0 && (
                  <span className="stat-pill hp">气血 +{arch.max_health_bonus}</span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="manifest-action-bar">
        <div className="custom-name-field">
          <label>器灵姓名（留空默认【{selectedArch?.default_name}】）：</label>
          <input
            type="text"
            className="spirit-name-input"
            placeholder={selectedArch?.default_name || '输入器灵姓名'}
            value={customName}
            onChange={(e) => setCustomName(e.target.value)}
            maxLength={8}
          />
        </div>
        <button
          type="button"
          className="btn-manifest-ceremony"
          disabled={!snapshot.can_manifest || busy || readOnly}
          onClick={handleManifest}
        >
          <Sparkles size={18} />
          <span>唤醒化形大典</span>
        </button>
      </div>
    </div>
  )
}

function ActiveSpiritView({
  spirit,
  busy,
  readOnly,
  onAction,
}: {
  spirit: ArtifactSpiritData
  busy: boolean
  readOnly: boolean
  onAction: (action: string) => void
}) {
  const [talkInput, setTalkInput] = useState('')

  const handleToggle = () => {
    if (busy || readOnly) return
    onAction(spirit.is_active ? '召回器灵' : '器灵出战')
  }

  const handleFeed = (item: string) => {
    if (busy || readOnly) return
    onAction(`器灵喂养 ${item}`)
  }

  const handleTalk = (msg?: string) => {
    if (busy || readOnly) return
    const text = msg !== undefined ? msg : talkInput.trim()
    onAction(text ? `器灵交谈 ${text}` : '器灵交谈')
    setTalkInput('')
  }

  return (
    <div className="active-spirit-view">
      {/* Left Column: Spirit Avatar & Status Card */}
      <div className="spirit-profile-col">
        <div className="spirit-avatar-showcase">
          <div className="avatar-orb">
            <Sparkles size={48} className="sparkle-orbit" />
          </div>
          <div className="spirit-hero-meta">
            <div className="hero-name-row">
              <h3>{spirit.name}</h3>
              <span className="hero-stage-badge">{spirit.level} 阶器灵</span>
            </div>
            <span className="hero-archetype">
              {spirit.archetype_name} · {spirit.title}
            </span>
            <span className="hero-personality">{spirit.personality}</span>
          </div>

          <div className="active-switch-row">
            <span className={`status-pill ${spirit.is_active ? 'active' : 'idle'}`}>
              {spirit.is_active ? '随身出战护主' : '识海归位温养'}
            </span>
            <button
              type="button"
              className={`btn-toggle-active ${spirit.is_active ? 'recall' : 'deploy'}`}
              disabled={busy || readOnly}
              onClick={handleToggle}
            >
              <Power size={14} />
              <span>{spirit.is_active ? '召回器灵' : '出战护主'}</span>
            </button>
          </div>
        </div>

        <div className="spirit-stats-card">
          <div className="stat-progress-group">
            <div className="progress-header">
              <span>
                <Award size={14} /> 灵性修为
              </span>
              <span>
                {spirit.exp} / {spirit.level * 100} EXP
              </span>
            </div>
            <div className="progress-bar-track">
              <div
                className="progress-bar-fill exp"
                style={{
                  width: `${Math.min(
                    100,
                    (spirit.exp / (spirit.level * 100)) * 100
                  )}%`,
                }}
              />
            </div>
          </div>

          <div className="stat-progress-group">
            <div className="progress-header">
              <span>
                <Heart size={14} /> 灵犀默契
              </span>
              <span>{spirit.intimacy} / 100</span>
            </div>
            <div className="progress-bar-track">
              <div
                className="progress-bar-fill intimacy"
                style={{ width: `${Math.min(100, spirit.intimacy)}%` }}
              />
            </div>
          </div>

          <div className="spirit-combat-specs">
            <h5>
              <Swords size={14} /> 神通威能加成
            </h5>
            <div className="specs-grid">
              <div className="spec-item">
                <span className="spec-label">攻击增幅</span>
                <span className="spec-value">
                  +{Math.round((spirit.attack_multiplier - 1.0) * 100)}%
                </span>
              </div>
              <div className="spec-item">
                <span className="spec-label">护体防御</span>
                <span className="spec-value">+{spirit.defense_bonus}</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">气血上限</span>
                <span className="spec-value">+{spirit.max_health_bonus}</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">神通威力</span>
                <span className="spec-value">{spirit.skill_value} 点</span>
              </div>
            </div>

            <div className="spirit-active-skill">
              <div className="active-skill-head">
                <Zap size={14} className="skill-icon" />
                <span className="skill-title">《{spirit.combat_skill_name}》</span>
              </div>
              <p className="skill-detail">{spirit.combat_skill_desc}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column: Interaction & Feed Panel */}
      <div className="spirit-interaction-col">
        {/* Feed module */}
        <div className="interaction-section feed-section">
          <h4>
            <Flame size={16} /> 灵丹法宝喂养升级
          </h4>
          <p className="section-tip">
            以灵石丹药温养器灵神魂，可提升灵犀亲密与修为位阶，增强护道神通威能：
          </p>
          <div className="feed-buttons-wrap">
            <button
              type="button"
              className="feed-btn"
              disabled={busy || readOnly}
              onClick={() => handleFeed('灵石')}
            >
              <Gem size={14} />
              <span>灵石 (50枚)</span>
              <span className="feed-reward">+50 EXP / +5 灵犀</span>
            </button>
            <button
              type="button"
              className="feed-btn"
              disabled={busy || readOnly}
              onClick={() => handleFeed('聚气丹')}
            >
              <Sparkles size={14} />
              <span>聚气丹</span>
              <span className="feed-reward">+20 EXP / +5 灵犀</span>
            </button>
            <button
              type="button"
              className="feed-btn"
              disabled={busy || readOnly}
              onClick={() => handleFeed('筑基丹')}
            >
              <Shield size={14} />
              <span>筑基丹</span>
              <span className="feed-reward">+60 EXP / +10 灵犀</span>
            </button>
            <button
              type="button"
              className="feed-btn"
              disabled={busy || readOnly}
              onClick={() => handleFeed('天材地宝')}
            >
              <Award size={14} />
              <span>天材地宝</span>
              <span className="feed-reward">+100 EXP / +20 灵犀</span>
            </button>
            <button
              type="button"
              className="feed-btn"
              disabled={busy || readOnly}
              onClick={() => handleFeed('灵铁')}
            >
              <Swords size={14} />
              <span>灵铁</span>
              <span className="feed-reward">+15 EXP / +3 灵犀</span>
            </button>
          </div>
        </div>

        {/* Talk & Intimacy module */}
        <div className="interaction-section talk-section">
          <h4>
            <MessageCircle size={16} /> 心印交谈与心声互动
          </h4>
          <div className="dialogue-chat-box">
            {spirit.dialogue_history && spirit.dialogue_history.length > 0 ? (
              spirit.dialogue_history.map((log, idx) => (
                <div key={idx} className="chat-bubble-row">
                  <div className="chat-bubble">
                    <pre className="chat-content">{log}</pre>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-dialogue">
                器灵初醒，心神澄澈，正静待主人发话。
              </div>
            )}
          </div>

          <div className="quick-topics-row">
            <button
              type="button"
              className="topic-pill"
              disabled={busy || readOnly}
              onClick={() => handleTalk('器灵近来温养可觉通畅？')}
            >
              温养如何？
            </button>
            <button
              type="button"
              className="topic-pill"
              disabled={busy || readOnly}
              onClick={() => handleTalk('待会随我出战，定斩妖魔！')}
            >
              出战迎敌
            </button>
            <button
              type="button"
              className="topic-pill"
              disabled={busy || readOnly}
              onClick={() => handleTalk('为我护法，我要闭关破境！')}
            >
              护法清心
            </button>
          </div>

          <div className="talk-input-row">
            <input
              type="text"
              className="talk-text-input"
              placeholder={`对【${spirit.name}】说些什么……`}
              value={talkInput}
              onChange={(e) => setTalkInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleTalk()
              }}
            />
            <button
              type="button"
              className="btn-send-talk"
              disabled={busy || readOnly}
              onClick={() => handleTalk()}
            >
              <Send size={15} />
              <span>传言</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const DEFAULT_SPIRIT_SNAPSHOT: ArtifactSpiritSnapshot = {
  bonded_artifact: '',
  resonance: 0,
  can_manifest: false,
  manifest_reason: '尚未佩戴本命灵宝或法宝灵性不足，无法化形',
  spirit: null,
  archetypes: [
    {
      id: 'sword_fairy',
      name: '剑仙子',
      title: '太虚剑魄 · 霜刃凝灵',
      personality: '冷冽清傲 · 攻伐无双',
      description: '法宝真灵化作清冷绝尘之剑仙，出剑势如青霜贯日，诛魔荡邪。',
      default_name: '青霜仙子',
      combat_skill_name: '万剑归墟',
      combat_skill_desc: '护战时激发剑意飞芒，大幅提升主人破甲伤害。',
      attack_multiplier: 1.35,
      defense_bonus: 20,
      max_health_bonus: 50,
    },
    {
      id: 'bell_spirit',
      name: '钟灵儿',
      title: '东皇古钟 · 梵音明心',
      personality: '活泼玲珑 · 固若金汤',
      description: '法宝真灵化作娇憨灵动的少女，身负古朴金钟，护道安宁。',
      default_name: '小叮当',
      combat_skill_name: '镇岳玄罡',
      combat_skill_desc: '护战时敲响荡魔金钟，为主人生成抵御重伤的护体金光。',
      attack_multiplier: 1.05,
      defense_bonus: 60,
      max_health_bonus: 180,
    },
    {
      id: 'flame_qilin',
      name: '赤炎童子',
      title: '九霄神火 · 灵兽化形',
      personality: '纯真好斗 · 焚天烈焰',
      description: '火系神兵真灵幻化之麒麟童子，吞吐纯阳三昧真火，灼尽邪魔。',
      default_name: '火宝',
      combat_skill_name: '纯阳烈焰击',
      combat_skill_desc: '护战时降下连环劫火爆破，焚毁强敌护体罡气。',
      attack_multiplier: 1.25,
      defense_bonus: 30,
      max_health_bonus: 90,
    },
  ],
  history: [],
}

export function ArtifactSpiritModal({
  open,
  onOpenChange,
  artifactSpirit,
  busy = false,
  readOnly = false,
  onAction,
}: ArtifactSpiritModalProps) {
  const currentSnapshot = artifactSpirit || DEFAULT_SPIRIT_SNAPSHOT
  const hasSpirit = Boolean(currentSnapshot.spirit && currentSnapshot.spirit.name)

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay dialog-backdrop" />
        <Dialog.Content className="dialog-content artifact-spirit-modal-content">
          <div className="spirit-modal-header">
            <div className="header-title-wrap">
              <div className="title-icon-badge">
                <Sparkles size={20} />
              </div>
              <div>
                <Dialog.Title className="modal-title">
                  本命法宝 · 器灵化形阁
                </Dialog.Title>
                <Dialog.Description className="modal-subtitle">
                  太古法宝孕真灵 · 独立化形伴仙途 · 神通护法破万法
                </Dialog.Description>
              </div>
            </div>
            <Dialog.Close asChild>
              <button
                type="button"
                className="btn-close-modal"
                aria-label="关闭器灵化形阁"
              >
                <X size={18} />
              </button>
            </Dialog.Close>
          </div>

          <div className="spirit-modal-body">
            {hasSpirit && currentSnapshot.spirit ? (
              <ActiveSpiritView
                spirit={currentSnapshot.spirit}
                busy={busy}
                readOnly={readOnly}
                onAction={onAction}
              />
            ) : (
              <ManifestationView
                snapshot={currentSnapshot}
                busy={busy}
                readOnly={readOnly}
                onAction={onAction}
              />
            )}
          </div>

          {currentSnapshot.history && currentSnapshot.history.length > 0 && (
            <div className="spirit-history-footer">
              <span className="history-label">
                <Scroll size={13} /> 器灵纪事：
              </span>
              <span className="history-text">
                {currentSnapshot.history[currentSnapshot.history.length - 1]}
              </span>
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
