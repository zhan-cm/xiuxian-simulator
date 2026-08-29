import * as Dialog from '@radix-ui/react-dialog'
import { Coins, Gavel, LockKeyhole, Timer, UserRound, X } from 'lucide-react'
import { useState } from 'react'
import type { AuctionSnapshot } from '../api/types'

interface AuctionHouseProps {
  auction: AuctionSnapshot
  stones: number
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

const rewardLabel = (rewards: Record<string, number>) => Object.entries(rewards).map(([name, count]) => `${name}×${count}`).join('、')

export function AuctionHouse({ auction, stones, busy, readOnly = false, onAction }: AuctionHouseProps) {
  const [open, setOpen] = useState(false)
  if (!auction.active && !auction.pending) return null
  const available = auction.lots.filter((lot) => lot.status === 'available').length
  const begin = (action: string) => {
    setOpen(false)
    onAction(action)
  }
  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger asChild><button className="auction-ribbon" type="button" data-pending={Boolean(auction.pending) || undefined}><span><Gavel size={17} /></span><div><small>天机坊临时法会</small><strong>{auction.pending ? '一锤正在待定' : '天机拍卖会'}</strong></div><p>{auction.pending ? '请先完成当前竞价' : `${auction.competitor}已入场`}</p><em><Timer size={12} />余 {auction.closes_in} 月</em><b>{available} 件</b></button></Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog auction-dialog">
          <header><div><p>奇珍无主 · 价高者得</p><Dialog.Title>天机拍卖会</Dialog.Title><Dialog.Description>竞价胜负由仙缘、声望、对手压力与出价策略共同决定；落败不会扣除灵石。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
          <div className="auction-summary"><span><Coins size={15} />持有灵石</span><strong>{stones}</strong><span><Timer size={15} />剩余时间</span><strong>{auction.closes_in} 月</strong></div>
          <section className="auction-competitor"><UserRound size={18} /><div><small>主要竞价对手</small><strong>{auction.competitor}</strong><p>{auction.competitor_style}</p></div></section>
          <div className="auction-lots">{auction.lots.map((lot, index) => {
            const availableLot = lot.status === 'available'
            const enabled = availableLot && lot.eligible && lot.affordable && !auction.pending && !readOnly && !busy
            return <article data-status={lot.status} key={lot.id}>
              <header><span>{String(index + 1).padStart(2, '0')}</span><div><small>{lot.minimum_realm_label}席 · 每次加价 {lot.increment}</small><h3>{lot.name}</h3></div><em>{lot.status === 'won' ? '已拍得' : lot.status === 'lost' ? '旁落' : lot.status === 'expired' ? '已散场' : '待落槌'}</em></header>
              <p>{lot.summary}</p>
              <div className="lot-reward">所得 <strong>{rewardLabel(lot.rewards)}</strong></div>
              <footer><div><small>起拍价</small><strong>{lot.reserve} <i>灵石</i></strong></div>{availableLot ? <button type="button" disabled={!enabled} title={readOnly ? '巡览模式不会修改存档' : auction.pending ? '请先完成当前竞价' : !lot.eligible ? `至少需要${lot.minimum_realm_label}境` : !lot.affordable ? '灵石不足以完成首次举牌' : '进入竞价抉择'} onClick={() => begin(lot.begin_action)}>{!lot.eligible ? <><LockKeyhole size={13} />境界不足</> : !lot.affordable ? '灵石不足' : '参与竞拍'}</button> : <span>{lot.winner} · {lot.price} 灵石</span>}</footer>
            </article>
          })}</div>
          {auction.history.length > 0 && <details className="auction-history"><summary>查看最近落槌记录</summary>{auction.history.map((entry) => <p key={entry}>{entry}</p>)}</details>}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
