import * as Dialog from '@radix-ui/react-dialog'
import { Backpack, Gem, Shield, Sparkles, Swords, X } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { InventoryItem, InventorySnapshot } from '../api/types'
import { Panel } from './Panel'

interface InventoryDialogProps {
  inventory: InventorySnapshot
  busy: boolean
  canAct: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

const rarityGlyph: Record<string, string> = { 仙品: '仙', 灵品: '灵', 珍品: '珍', 良品: '良', 玄阶: '玄', 黄阶: '黄', 凡品: '凡' }

export function InventoryDialog({ inventory, busy, canAct, readOnly = false, onAction }: InventoryDialogProps) {
  const [open, setOpen] = useState(false)
  const [category, setCategory] = useState('全部')
  const [selectedName, setSelectedName] = useState('')
  const selected = inventory.items.find((item) => item.name === selectedName) || inventory.items[0]
  const shown = useMemo(
    () => category === '全部' ? inventory.items : inventory.items.filter((item) => item.category === category),
    [category, inventory.items],
  )
  const openItem = (item: InventoryItem) => {
    setSelectedName(item.name)
    setOpen(true)
  }
  const act = () => {
    if (selected?.action) onAction(selected.action)
  }
  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Panel title="乾坤袋" icon={<Backpack size={18} />} meta={inventory.total_types ? `${inventory.total_types} 类` : '空'}>
        {inventory.items.length ? <>
          <div className="inventory-grid">{inventory.items.slice(0, 4).map((item) => <button type="button" data-rarity={item.rarity} data-equipped={item.equipped || undefined} onClick={() => openItem(item)} key={item.name}><span>{item.name.slice(0, 1)}</span><strong>{item.name}</strong><small>×{item.count}</small>{item.equipped && <em>已装备</em>}</button>)}</div>
          <button className="inventory-open" type="button" onClick={() => setOpen(true)}>整理乾坤袋 <span>{inventory.total_count} 件藏品</span></button>
        </> : <div className="empty-inventory"><div><Gem size={20} /><span /><span /><span /></div><p>获取丹药、法器或材料后，将陈列于此。</p><small>探索、交易与委托均可获得物品</small></div>}
      </Panel>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog inventory-dialog">
          <header><div><p>一袋藏万象</p><Dialog.Title>乾坤袋</Dialog.Title><Dialog.Description>物品用途、持有数量和装备状态均来自同一套规则引擎。</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
          <div className="equipment-slots">
            <div><Swords size={16} /><span><small>武器</small><strong>{inventory.equipped.weapon || '尚未装备'}</strong></span></div>
            <div><Shield size={16} /><span><small>护甲</small><strong>{inventory.equipped.armor || '尚未装备'}</strong></span></div>
            <em>{inventory.total_types} 类 · {inventory.total_count} 件</em>
          </div>
          {inventory.items.length ? <div className="inventory-layout">
            <section className="inventory-collection">
              <nav aria-label="物品分类">{inventory.categories.map((name) => <button type="button" data-active={category === name || undefined} onClick={() => setCategory(name)} key={name}>{name}</button>)}</nav>
              <div className="inventory-list">{shown.map((item) => <button type="button" data-active={selected?.name === item.name || undefined} data-rarity={item.rarity} onClick={() => setSelectedName(item.name)} key={item.name}><span>{rarityGlyph[item.rarity] || item.name.slice(0, 1)}</span><div><strong>{item.name}</strong><small>{item.category} · {item.rarity}</small></div><em>×{item.count}</em>{item.equipped && <i>已装备</i>}</button>)}</div>
            </section>
            {selected && <section className="item-inspector" data-rarity={selected.rarity}>
              <div className="item-emblem"><Sparkles size={17} /><span>{selected.name.slice(0, 1)}</span></div>
              <small>{selected.category} · {selected.rarity}{selected.slot ? ` · ${selected.slot}` : ''}</small>
              <h3>{selected.name}</h3>
              <p>{selected.description}</p>
              <dl><div><dt>持有</dt><dd>{selected.count} 件</dd></div><div><dt>状态</dt><dd>{selected.equipped ? '当前装备' : '收入袋中'}</dd></div></dl>
              <div className="item-usage"><strong>实际用途</strong><p>{selected.usage}</p></div>
              {selected.actionable ? <button type="button" disabled={busy || readOnly || !canAct || Boolean(selected.disabled_reason)} title={readOnly ? '巡览模式不会修改存档' : !canAct ? '请先完成当前抉择或行动' : selected.disabled_reason} onClick={act}>{busy ? '正在结算…' : selected.disabled_reason || selected.action_label}</button> : <span className="item-passive">此物无需直接操作</span>}
            </section>}
          </div> : <div className="inventory-dialog-empty"><Gem size={30} /><strong>袋中尚无藏品</strong><p>先去坊市、东洲探索或领取委托报酬。</p></div>}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
