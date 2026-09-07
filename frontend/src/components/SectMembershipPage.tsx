import { Award, BookOpenText, ChevronRight, Crown, History, Landmark, LockKeyhole, ScrollText, Shield, Swords } from 'lucide-react'
import type { SectMembershipSnapshot, SectTaskView } from '../api/types'

interface Props {
  membership: SectMembershipSnapshot
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

const ranks = ['外门弟子', '内门弟子', '真传弟子', '长老', '掌门']
const taskDescriptions: Record<string, string> = {
  采药: '入山辨灵植，以福缘寻得宗门所需药材。',
  巡逻: '巡视山门与灵脉，以神识察觉潜伏异动。',
  猎妖: '清剿侵入宗门辖地的妖兽，失败可能负伤。',
  护送: '护持宗门物资远行，以道心应对沿途变数。',
  镇守: '坐镇要地抵御强敌，回报丰厚而风险最高。',
}

const rewardText = (task: SectTaskView) => {
  const extras = Object.entries(task.rewards).map(([name, count]) => `${name}×${count}`)
  return [`灵石 +${task.stones}`, `贡献 +${task.contribution}`, ...extras].join(' · ')
}

export function SectMembershipEntry({ membership, busy, readOnly = false, onAction }: Props) {
  if (!membership.member) return null
  const ready = Boolean(membership.promotion.available || membership.tournament.available)
  return <button className="sect-membership-ribbon" type="button" disabled={busy || readOnly} data-ready={ready || undefined} onClick={() => onAction('宗门')}>
    <span><Landmark size={17} />{ready && <i aria-label="有可办理宗门事务" />}</span>
    <div><small>{membership.sect}</small><strong>本宗事务</strong></div>
    <p>{membership.rank} · {membership.tasks.length} 类宗门任务</p>
    <em>{membership.contribution} 贡献</em><ChevronRight size={16} />
  </button>
}

export function SectMembershipPage({ membership, busy, readOnly = false, onAction }: Props) {
  if (!membership.member) return null
  const rankIndex = Math.max(0, ranks.indexOf(membership.rank))
  const promotion = membership.promotion
  const tournament = membership.tournament
  return <section className="sect-membership-page" aria-labelledby="sect-membership-title">
    <header className="sect-membership-hero">
      <span aria-hidden="true">宗</span>
      <div><small>山门有序 · 各司其职</small><h3 id="sect-membership-title">{membership.sect}</h3><p>领取宗门差事，积累贡献，沿门中阶序争取更高传承。</p></div>
      <dl><div><dt>当前身份</dt><dd>{membership.rank}</dd></div><div><dt>宗门贡献</dt><dd>{membership.contribution}</dd></div></dl>
    </header>

    <div className="sect-rank-path" aria-label="宗门职位阶序">
      {ranks.map((rank, index) => <span key={rank} data-current={index === rankIndex || undefined} data-reached={index <= rankIndex || undefined}><i>{index <= rankIndex ? <Award size={13} /> : <LockKeyhole size={12} />}</i><small>{rank}</small></span>)}
    </div>

    <div className="sect-advancement-grid">
      <article data-ready={promotion.available || undefined}>
        <span><Crown size={18} /></span><div><small>职位晋升</small><strong>{promotion.target ? `申请${promotion.target}` : '已至门中极位'}</strong><p>{promotion.reason}</p></div>
        <dl>{promotion.target && <><div><dt>贡献门槛</dt><dd data-met={promotion.contribution_met || undefined}>{membership.contribution} / {promotion.contribution_required}</dd></div><div><dt>境界门槛</dt><dd data-met={promotion.realm_met || undefined}>{promotion.minimum_realm_label}</dd></div><div><dt>试炼胜算</dt><dd>{promotion.chance}%</dd></div></>}</dl>
        <button type="button" disabled={busy || readOnly || !promotion.available} title={readOnly ? '成果巡览仅供查看' : promotion.reason} onClick={() => promotion.action && onAction(promotion.action)}>{promotion.available ? '申请晋升试炼' : promotion.reason}</button>
      </article>
      <article data-ready={tournament.available || undefined}>
        <span><Swords size={18} /></span><div><small>十年盛会</small><strong>宗门大比</strong><p>{tournament.reason}</p></div>
        <dl><div><dt>届次状态</dt><dd>{tournament.participated ? tournament.result : tournament.available ? '正在举行' : '尚未开启'}</dd></div><div><dt>下次年份</dt><dd>天玄历 {tournament.next_year}</dd></div></dl>
        <button type="button" disabled={busy || readOnly || !tournament.available} title={readOnly ? '成果巡览仅供查看' : tournament.reason} onClick={() => tournament.action && onAction(tournament.action)}>{tournament.available ? '参加本届大比' : tournament.reason}</button>
      </article>
    </div>

    <section className="sect-task-board">
      <header><ScrollText size={16} /><div><small>一事一结 · 真实判定</small><strong>宗门差事</strong></div><em>{membership.tasks.length} 类可领</em></header>
      <div>{membership.tasks.map((task) => <article key={task.name} data-tone={task.tone}>
        <span>{task.mark}</span><div><small>{task.attribute} {task.attribute_value} · 胜算 {task.chance}%</small><strong>{task.name}</strong><p>{taskDescriptions[task.name]}</p></div>
        <em>{rewardText(task)}</em>
        <button type="button" disabled={busy || readOnly} title={readOnly ? '成果巡览仅供查看' : `${task.name}会推进一个月，并进行真实成功判定`} onClick={() => onAction(task.action)}>领取差事</button>
      </article>)}</div>
    </section>

    <footer className="sect-membership-footer">
      <div><Shield size={15} /><span><small>门中权限</small><strong>{membership.privileges.length ? membership.privileges.join(' · ') : '尚无额外权限'}</strong></span></div>
      <details><summary><History size={13} />离宗相关</summary><p>叛宗会清空宗门贡献、降低声望并增加业力，仍需在下一步亲自确认。</p><button type="button" disabled={busy || readOnly} onClick={() => onAction('叛宗')}>查看叛宗后果</button></details>
      <p><BookOpenText size={13} />传承兑换与年度讲法请前往“宗门藏经阁”。</p>
    </footer>
  </section>
}
