// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { GameState, Presentation } from '../api/types'
import { CultivatorHud, ImmersiveScene, WorldNavigation } from './ImmersiveScene'

const state = {
  version: '1.0.0', phase: 'playing', turn: 12, calendar_year: 387, month: 12, world_era: '灵潮前夜', last_world_event: '青岳灵雾渐浓。', relationship_tension: 0, main_quest: '', history: [], npc_relations: {},
  player: { name: '沈砚', dao_name: '听松', gender: '男', age: 18, lifespan: 100, realm: '炼气·初期', sect: '散修', sect_rank: '', spiritual_root: '木灵根', constitution: '清灵体', health: 72, health_max: 100, spirit: 64, spirit_max: 100, cultivation: 20, cultivation_required: 100, spirit_stones: 30, condition: '安好', location: '东洲青岳', inventory: [], resources: {} },
} as GameState

const presentation = { action: '修炼', title: '松间吐纳', eyebrow: '当前道途', seal: '修', tone: 'story', paragraphs: ['晨雾沿着石阶漫入洞府。'], changes: [], blocks: [], details: '', has_details: false } as Presentation

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
    render(<WorldNavigation activeAction="地图" codexOpen={false} onNavigate={navigate} onToggleCodex={toggle} />)
    fireEvent.click(screen.getByRole('button', { name: /坊市/ }))
    fireEvent.click(screen.getByRole('button', { name: /洞天侧记/ }))
    expect(navigate).toHaveBeenCalledWith('坊市')
    expect(toggle).toHaveBeenCalledOnce()
  })
})
