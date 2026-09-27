import { motion } from 'motion/react'
import { Sparkles, Compass, FolderOpen, ScrollText, Play, Feather, ShieldCheck, Flame } from 'lucide-react'
import type { Snapshot } from '../api/types'

interface StartGamePortalProps {
  busy: boolean
  saveSummaries: Snapshot['save_summaries']
  onAction: (action: string) => void
  onOpenArchive: () => void
}

export function StartGamePortal({ busy, saveSummaries, onAction, onOpenArchive }: StartGamePortalProps) {
  const latestSave = saveSummaries.find((save) => !save.corrupt) || null
  const begin = (action: string) => {
    if (saveSummaries.length && !window.confirm('开始新游戏会替换当前自动存档。旧进度会先另存为“开局前”卷宗，可在存档界面读取。确定继续吗？')) return
    onAction(action)
  }

  return (
    <div className="start-game-portal">
      <div className="portal-backdrop-mist" />

      <div className="portal-content-card">
        <header className="portal-header">
          <div className="portal-seal-crest">
            <Flame size={28} className="crest-icon" />
          </div>
          <span className="portal-era-badge">天玄历 387 年 · 灵气潮汐将至</span>
          <h1 className="portal-title">永恒之道</h1>
          <p className="portal-subtitle">高自由修仙文字模拟 · 凡尘一念证长生</p>
        </header>

        <section className="portal-lore-scroll">
          <p>
            浩瀚九州，名山洞天星罗棋布，正邪诸宗暗流涌动。世间凡夫俗子终其一生难越寿元大限，而修仙之士逆天夺造化，自炼气、筑基乃至登仙，万劫不磨。
          </p>
          <p className="lore-accent">
            天地不仁，以万物为刍狗；仙路漫漫，唯道心坚者可履极巅。今日灵机勃发，正是你踏碎凡尘、立命开篇之时。
          </p>
        </section>

        <div className="portal-action-cluster">
          {latestSave && (
            <motion.button
              type="button"
              className="portal-btn primary-start-btn"
              disabled={busy}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onAction(`读档 ${String(latestSave.name)}`)}
            >
              <div className="btn-seal"><FolderOpen size={20} /></div>
              <div className="btn-text">
                <strong>继续上次修行</strong>
                <small>{String(latestSave.player_name || '修士')} · {String(latestSave.realm || '凡人')} · {String(latestSave.name)}</small>
              </div>
              <Play size={18} className="btn-arrow" />
            </motion.button>
          )}
          {/* 主动作 1：自定创角 */}
          <motion.button
            type="button"
            className={`portal-btn ${latestSave ? 'quick-start-btn' : 'primary-start-btn'}`}
            disabled={busy}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => begin('开始游戏')}
          >
            <div className="btn-seal"><Feather size={20} /></div>
            <div className="btn-text">
              <strong>踏入仙途 · 执笔立命</strong>
              <small>自定义姓名、出身、道途、灵根、体质与六维天赋</small>
            </div>
            <Play size={18} className="btn-arrow" />
          </motion.button>

          {/* 主动作 2：快速开局 */}
          <motion.button
            type="button"
            className="portal-btn quick-start-btn"
            disabled={busy}
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => begin('快速开始游戏')}
          >
            <div className="btn-seal"><Sparkles size={20} /></div>
            <div className="btn-text">
              <strong>承袭天命 · 快速启程</strong>
              <small>以推荐道骨「沈砚 · 问道飞升」直接入世，即刻开启修仙</small>
            </div>
            <span className="fast-tag">极速试玩</span>
          </motion.button>

          {/* 主动作 3：读档 */}
          <div className="portal-archive-action">
            <button
              type="button"
              className="portal-archive-btn"
              disabled={busy}
              onClick={onOpenArchive}
            >
              <FolderOpen size={16} />
              <span>查阅洞天卷宗（存档与读档）</span>
              {saveSummaries && saveSummaries.length > 0 && (
                <em>{saveSummaries.length} 份已有存档</em>
              )}
            </button>

            {latestSave && (
              <button className="latest-save-chip" type="button" disabled={busy} onClick={onOpenArchive}>
                <ScrollText size={13} />
                <span>最近卷宗：<strong>{String(latestSave.name || 'autosave')}</strong>（{String(latestSave.player_name || '修士')} · {String(latestSave.realm || '凡人')}）</span>
              </button>
            )}
          </div>
        </div>

        <footer className="portal-footer">
          <div className="footer-feature-item">
            <Compass size={13} />
            <span>自由道途 · 仙魔由心</span>
          </div>
          <div className="footer-feature-item">
            <ShieldCheck size={13} />
            <span>本地卷宗 · 规则自洽</span>
          </div>
          <div className="footer-feature-item">
            <Sparkles size={13} />
            <span>大道十重 · 逆天破境</span>
          </div>
        </footer>
      </div>
    </div>
  )
}
