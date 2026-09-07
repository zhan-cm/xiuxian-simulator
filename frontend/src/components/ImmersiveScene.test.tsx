// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { GameState, InventorySnapshot, NpcLifeSnapshot, NpcProfile, Presentation } from '../api/types'
import { EventPanel } from './EventPanel'
import { CultivatorHud, ImmersiveScene, SocialActionBar, WorldNavigation } from './ImmersiveScene'

const state = {
  version: '1.0.0', phase: 'playing', turn: 12, calendar_year: 387, month: 12, world_era: '灵潮前夜', last_world_event: '青岳灵雾渐浓。', relationship_tension: 0, main_quest: '', history: [], npc_relations: {},
  player: { name: '沈砚', dao_name: '听松', gender: '男', age: 18, lifespan: 100, realm: '炼气·初期', sect: '散修', sect_rank: '', spiritual_root: '木灵根', constitution: '清灵体', health: 72, health_max: 100, spirit: 64, spirit_max: 100, cultivation: 20, cultivation_required: 100, spirit_stones: 30, condition: '安好', location: '东洲青岳', inventory: [], resources: {} },
} as GameState

const presentation = { action: '修炼', title: '松间吐纳', eyebrow: '当前道途', seal: '修', tone: 'story', paragraphs: ['晨雾沿着石阶漫入洞府。'], changes: [], blocks: [], details: '', has_details: false } as Presentation
const npc = { name: '顾清玄', gender: '男', identity: '青云宗真传·温润剑修', age: 24, lifespan: 180, realm: '筑基·后期', location: '青云宗', greeting: '剑有锋芒，道心却不必处处伤人。', likes: ['剑穗', '清茶'], dislikes: ['情蛊'], affinity: 66, relation: '知己', alive: true, status: '静修' } as NpcProfile

afterEach(() => cleanup())

describe('immersive game shell', () => {
  it('presents the current place and event as the visual focus', () => {
    render(<><CultivatorHud player={state.player} /><ImmersiveScene state={state} presentation={presentation} calendarLabel="天玄历 387 年 · 冬十二月" /></>)
    expect(screen.getByRole('region', { name: '当前场景：东洲青岳' })).toBeTruthy()
    expect(screen.getByText('松间吐纳')).toBeTruthy()
    expect(screen.getByText('晨雾沿着石阶漫入洞府。')).toBeTruthy()
    expect(screen.getByTitle('气血 72 / 100')).toBeTruthy()
  })

  it('keeps world navigation explicit and separates the codex tray', () => {
    const navigate = vi.fn()
    const toggle = vi.fn()
    render(<WorldNavigation activeAction="地图" codexOpen={false} hasUpdates onNavigate={navigate} onToggleCodex={toggle} />)
    fireEvent.click(screen.getByRole('button', { name: /坊市/ }))
    fireEvent.click(screen.getByRole('button', { name: /洞天侧记/ }))
    expect(navigate).toHaveBeenCalledWith('坊市')
    expect(toggle).toHaveBeenCalledOnce()
    expect(screen.getByLabelText('世界与修行有可推进事项')).toBeVisible()
  })

  it('hands the first paragraph to the scene without repeating the event heading', () => {
    const detailed = { ...presentation, paragraphs: ['场景中的首段。', '仅在下方展开的补充段落。'] }
    render(<EventPanel presentation={detailed} immersive readOnly onAction={() => undefined} />)
    expect(screen.queryByText('松间吐纳')).toBeNull()
    expect(screen.queryByText('场景中的首段。')).toBeNull()
    expect(screen.getByText('仅在下方展开的补充段落。')).toBeTruthy()
  })

  it('lets readers open every character of a long narrative without needing a debug record', () => {
    const full = '山雨初歇，道旁古松间传来一声清越的剑鸣。'.repeat(14) + '来人终于道出了秘境的真正入口。'
    render(<ImmersiveScene state={state} presentation={{ ...presentation, paragraphs: [full] }} calendarLabel="冬十二月" />)
    expect(screen.queryByText(full)).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: '读完这段' }))
    const dialog = screen.getByRole('dialog', { name: '松间吐纳' })
    expect(within(dialog).getByText(full)).toBeInTheDocument()
    fireEvent.click(within(dialog).getByRole('button', { name: '关闭完整叙事' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('keeps every settlement change visible exactly once across the scene and event', () => {
    const settled = { ...presentation, changes: [
      { label: '气血', value: '-12' }, { label: '灵力', value: '-8' },
      { label: '灵石', value: '+50' }, { label: '寿元', value: '+10' },
    ] }
    render(<><ImmersiveScene state={state} presentation={settled} calendarLabel="冬十二月" /><EventPanel presentation={settled} immersive onAction={() => undefined} /></>)
    for (const change of settled.changes) expect(screen.getAllByText(change.value)).toHaveLength(1)
  })

  it('keeps the codex accessible while an exclusive decision locks travel', () => {
    const navigate = vi.fn()
    const toggle = vi.fn()
    render(<WorldNavigation activeAction="" disabled disabledReason="请先完成当前抉择" codexOpen={false} onNavigate={navigate} onToggleCodex={toggle} />)
    fireEvent.click(screen.getByRole('button', { name: '坊市' }))
    expect(screen.getByRole('button', { name: '坊市' })).toBeDisabled()
    expect(navigate).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: '洞天侧记' }))
    expect(toggle).toHaveBeenCalledOnce()
  })

  it('cannot explore or buy through event cards in preview mode', () => {
    const act = vi.fn()
    const map = { ...presentation, blocks: [{ type: 'locations', items: [{ name: '青岳山麓', accessible: true, action: '探索 青岳山麓' }] }] }
    render(<EventPanel presentation={map} readOnly immersive onAction={act} />)
    const explore = screen.getByRole('button', { name: '前往探索' })
    expect(explore).toBeDisabled()
    fireEvent.click(explore)
    expect(act).not.toHaveBeenCalled()
  })

  it('presents exploration as a themed system surface with legible danger and locked routes', () => {
    const map = { ...presentation, blocks: [{ type: 'locations', title: '东洲探索地图', legend: '危险越高，历练与危机越多。', items: [
      { name: '青岳山麓', danger: 12, danger_label: '低危', requirement_label: '炼气境', description: '林风清润，适合初入道途者试炼。', accessible: true, visited: false, action: '探索 青岳山麓', tone: 'safe' },
      { name: '古战场外围', danger: 38, danger_label: '绝境', requirement_label: '筑基境', description: '残阵与煞气终年不散。', accessible: false, locked_reason: '需要达到筑基境才可进入', tone: 'danger' },
    ] }] } as Presentation
    render(<EventPanel presentation={map} immersive onAction={() => undefined} />)
    expect(screen.getByText('东洲探索地图').closest('.event-panel')).toHaveAttribute('data-surface', 'locations')
    expect(screen.getByText('山河可赴')).toBeVisible()
    expect(screen.getByText('机缘未探')).toBeVisible()
    expect(screen.getByLabelText('危险等级 4 / 4')).toBeVisible()
    expect(screen.getByRole('button', { name: /需要达到筑基境才可进入/ })).toBeDisabled()
  })

  it('turns five regions into a selectable atlas with one focused route detail', () => {
    const act = vi.fn()
    const atlas = { ...presentation, blocks: [{ type: 'regions', title: '九州舆图', items: [
      { key: '东洲', name: '东洲·青岳', current: true, visited: true, accessible: false, danger: 12, danger_label: '低危', requirement_label: '炼气境', description: '散修汇聚之地。', months: 0, specialties: ['灵药'], demands: ['妖兽材料'], rank: '略有薄名', reputation: 12, locked_reason: '当前所在', action: '前往 东洲', has_event: true, event_title: '青岳灵雾' },
      { key: '南疆', name: '南疆·赤炎', current: false, visited: false, accessible: true, danger: 34, danger_label: '高危', requirement_label: '筑基境', description: '火脉与妖兽并存。', months: 3, specialties: ['烈酒'], demands: ['灵药'], rank: '初来乍到', reputation: 0, action: '前往 南疆' },
      { key: '北原', name: '北原·寒渊', current: false, visited: false, accessible: false, danger: 72, danger_label: '绝境', requirement_label: '元婴境', description: '长夜雪暴笼罩寒渊。', months: 4, specialties: ['冰莲'], demands: ['疗伤丹'], rank: '初来乍到', reputation: 0, locked_reason: '需要达到元婴境才可前往', action: '前往 北原' },
    ] }] } as Presentation
    render(<EventPanel presentation={atlas} immersive onAction={act} />)
    expect(screen.getByRole('navigation', { name: '五域卷轴舆图' })).toBeVisible()
    expect(screen.getByRole('complementary', { name: '东洲·青岳地域详情' })).toBeVisible()
    expect(screen.getByLabelText('有地方机缘')).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: '查看南疆·赤炎地域' }))
    expect(screen.getByRole('complementary', { name: '南疆·赤炎地域详情' })).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: '规划前往南疆' }))
    expect(act).toHaveBeenCalledExactlyOnceWith('前往 南疆')
    fireEvent.click(screen.getByRole('button', { name: '查看北原·寒渊地域' }))
    expect(screen.getByRole('button', { name: '需要达到元婴境才可前往' })).toBeDisabled()
  })

  it('turns the market into a filterable shelf with explicit buy and sell states', () => {
    const act = vi.fn()
    const market = { ...presentation, blocks: [{ type: 'market', title: '青岳坊市', currency: 20, items: [
      { name: '聚气丹', category: '丹药', rarity: '凡品', description: '温养经脉、凝聚灵气的入门丹药。', usage: '服用后增加当前大境界修为。', owned: 0, affordable: true, buy: 12, sell: 6, buy_action: '购买 聚气丹', sell_action: '出售 聚气丹' },
      { name: '青灵草', category: '材料', owned: 2, affordable: false, buy: 30, sell: 9, buy_action: '购买 青灵草', sell_action: '出售 青灵草' },
    ] }] } as Presentation
    render(<EventPanel presentation={market} immersive onAction={act} />)
    fireEvent.click(screen.getByRole('button', { name: '丹药' }))
    expect(screen.getAllByText('聚气丹')).toHaveLength(2)
    expect(screen.queryByText('青灵草')).not.toBeInTheDocument()
    expect(screen.getByText('温养经脉、凝聚灵气的入门丹药。')).toBeVisible()
    expect(screen.getByText('服用后增加当前大境界修为。')).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: /买入.*12/ }))
    expect(act).toHaveBeenCalledWith('购买 聚气丹')
    expect(screen.getByRole('button', { name: /卖出.*6/ })).toBeDisabled()
  })

  it('keeps browsing available but mutations disabled in showcase mode', () => {
    const act = vi.fn()
    const market = { ...presentation, blocks: [{ type: 'market', title: '青岳坊市', currency: 20, items: [
      { name: '聚气丹', category: '丹药', owned: 0, affordable: true, buy: 12, sell: 6, buy_action: '购买 聚气丹', sell_action: '出售 聚气丹' },
      { name: '青灵草', category: '材料', owned: 2, affordable: true, buy: 8, sell: 4, buy_action: '购买 青灵草', sell_action: '出售 青灵草' },
    ] }] } as Presentation
    render(<EventPanel presentation={market} readOnly immersive onAction={act} />)
    fireEvent.click(screen.getByRole('button', { name: '材料' }))
    expect(screen.getByRole('complementary', { name: '青灵草详情' })).toBeVisible()
    expect(screen.getByRole('button', { name: /买入.*8/ })).toBeDisabled()
    expect(screen.getByRole('button', { name: /卖出.*4/ })).toBeDisabled()
    expect(act).not.toHaveBeenCalled()
  })

  it('opens a complete character dossier without allowing showcase actions', () => {
    const act = vi.fn()
    const lives = { living_count: 1, pending_count: 0, memorials: [], history: [], last_event: '', profiles: [{
      name: '顾清玄', gender: '男', identity: '青云宗真传·温润剑修', realm: '筑基·后期', age: 24, lifespan: 180,
      years_remaining: 156, life_percent: 13, location: '青云宗', activity: '山门静修', status: '安好', alive: true,
      wounded: false, affinity: 66, relation: '知己', likes: ['清茶', '剑穗'], pending: false, pending_kind: '', expires_in: 0,
      pill: '', can_gift_pill: false, can_guard: false, life_events: ['第 8 回合｜青岳论剑'], cause_of_death: '',
    }] } as NpcLifeSnapshot
    const people = { ...presentation, action: '情缘', blocks: [{ type: 'people', title: '浮生故人', items: [{ name: '顾清玄' }] }] } as Presentation
    render(<EventPanel presentation={people} npcLives={lives} readOnly immersive onAction={act} />)
    fireEvent.click(screen.getByRole('button', { name: '查看档案' }))
    const dialog = screen.getByRole('dialog', { name: '顾清玄' })
    expect(within(dialog).getByText('青云宗真传·温润剑修')).toBeVisible()
    expect(within(dialog).getByText('清茶')).toBeVisible()
    expect(within(dialog).getByRole('button', { name: '前往交谈' })).toBeDisabled()
    expect(act).not.toHaveBeenCalled()
  })

  it('matches cultivation to the cave even when the current location contains a region name', () => {
    render(<ImmersiveScene state={state} presentation={presentation} calendarLabel="冬十二月" />)
    expect(screen.getByRole('region', { name: '当前场景：东洲青岳' })).toHaveAttribute('data-scene', 'cave')
    expect(screen.getByText(/第 12 回合/)).toBeInTheDocument()
  })

  it('stages a named relationship action as a two-character encounter', () => {
    const meeting = { ...presentation, action: '对话 顾清玄', title: '顾清玄', tone: 'relation', paragraphs: ['“剑有锋芒，道心却不必处处伤人。”'] }
    render(<ImmersiveScene state={state} presentation={meeting} npcProfiles={{ 顾清玄: npc }} calendarLabel="冬十二月" />)
    const scene = screen.getByRole('region', { name: '当前场景：东洲青岳' })
    expect(scene).toHaveAttribute('data-scene', 'relation')
    expect(scene).toHaveAttribute('data-conversation', 'true')
    expect(screen.getByLabelText('正在与顾清玄会面')).toBeVisible()
    expect(screen.getByText('青云宗真传·温润剑修')).toBeVisible()
    expect(screen.getByText('心意相知 · 静修')).toBeVisible()
  })

  it('keeps the full relationship roster neutral until a person is chosen', () => {
    const roster = { ...presentation, action: '情缘', title: '人物与情缘', tone: 'relation', paragraphs: ['六位故人的近况已经汇入卷册。'] }
    render(<ImmersiveScene state={state} presentation={roster} npcProfiles={{ 顾清玄: npc }} calendarLabel="冬十二月" />)
    expect(screen.queryByLabelText('正在与顾清玄会面')).not.toBeInTheDocument()
    expect(screen.getByRole('region', { name: '当前场景：东洲青岳' })).not.toHaveAttribute('data-conversation')
  })

  it('offers concrete follow-up actions and only submits the selected gift', () => {
    const act = vi.fn()
    const inventory = { items: [
      { name: '清茶', count: 2, category: '礼物' },
      { name: '剑穗', count: 1, category: '礼物' },
      { name: '疗伤丹', count: 2, category: '丹药' },
    ], categories: ['全部', '礼物', '丹药'], total_types: 3, total_count: 5, equipped: { weapon: '', armor: '' } } as InventorySnapshot
    render(<SocialActionBar npc={npc} inventory={inventory} onAction={act} />)
    fireEvent.click(screen.getByRole('button', { name: /继续交谈/ }))
    expect(act).toHaveBeenLastCalledWith('对话 顾清玄')
    fireEvent.change(screen.getByRole('combobox', { name: /赠一份心意/ }), { target: { value: '剑穗' } })
    fireEvent.click(screen.getByRole('button', { name: '送出' }))
    expect(act).toHaveBeenLastCalledWith('送礼 顾清玄 剑穗')
    expect(screen.queryByRole('option', { name: /疗伤丹/ })).not.toBeInTheDocument()
  })
})
