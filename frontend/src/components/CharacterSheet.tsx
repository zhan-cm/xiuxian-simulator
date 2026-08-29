import * as Dialog from '@radix-ui/react-dialog'
import { ScrollText, X } from 'lucide-react'
import type { PlayerState } from '../api/types'

const attributes: Array<[keyof PlayerState, string]> = [
  ['aptitude', '资质'], ['comprehension', '悟性'], ['spirit_sense', '神识'],
  ['speed', '遁速'], ['dao_heart', '道心'], ['fortune', '仙缘'],
]

export function CharacterSheet({ player }: { player: PlayerState }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger asChild><button className="archive-trigger" type="button"><ScrollText size={16} />道途详览</button></Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog">
          <header><div><p>修士名帖</p><Dialog.Title>{player.name} · {player.dao_name}</Dialog.Title><Dialog.Description>{String(player.background || '凡尘')}出身，行于{player.location}</Dialog.Description></div><Dialog.Close aria-label="关闭"><X size={20} /></Dialog.Close></header>
          <div className="dialog-identity"><span>{player.realm}</span><span>{player.spiritual_root}</span><span>{player.constitution}</span><span>{player.age}岁 / 寿元{player.lifespan}</span></div>
          <div className="attribute-grid">
            {attributes.map(([key, label]) => <div key={key}><small>{label}</small><strong>{String(player[key] ?? '—')}</strong></div>)}
          </div>
          <section><h3>当前修行</h3><dl><div><dt>主修功法</dt><dd>{String(player.primary_technique || '尚未选择')}</dd></div><div><dt>当前法术</dt><dd>{String(player.equipped_spell || '尚未装备')}</dd></div><div><dt>宗门身份</dt><dd>{player.sect} · {player.sect_rank}</dd></div><div><dt>身体状态</dt><dd>{player.condition}</dd></div></dl></section>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
