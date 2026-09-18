// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { TianjiFocusCard } from './TianjiFocusCard'
import type { GameState, PlayerState, Snapshot } from '../api/types'

afterEach(() => { cleanup() })

const basePlayer: PlayerState = {
  name: '韩立',
  dao_name: '厉飞雨',
  gender: '男',
  age: 20,
  lifespan: 100,
  realm: '炼气·前期',
  sect: '黄枫谷',
  sect_rank: '外门弟子',
  spiritual_root: '伪灵根',
  constitution: '凡躯',
  health: 100,
  health_max: 100,
  spirit: 50,
  spirit_max: 50,
  cultivation: 20,
  cultivation_required: 100,
  spirit_stones: 100,
  condition: '健康',
  location: '洞府',
  inventory: ['聚气丹'],
  resources: {},
}

const baseState = {
  version: '1.0.0',
  phase: 'playing',
  turn: 1,
  calendar_year: 1,
  month: 1,
  main_quest: '求道长生',
  history: [],
  world_era: '天玄初历',
  last_world_event: '灵气平静',
} as unknown as GameState

const baseSnapshot = {
  player: basePlayer,
  state: baseState,
  presentation: { action: '修炼', title: '潜修' },
} as unknown as Snapshot

describe('TianjiFocusCard', () => {
  it('recommends cultivation/retreat under normal conditions', () => {
    const handleAction = vi.fn()
    render(
      <TianjiFocusCard
        player={basePlayer}
        state={baseState}
        snapshot={baseSnapshot}
        canQuickAct={true}
        onAction={handleAction}
      />
    )

    expect(screen.getByText(/天机司南/)).toBeInTheDocument()
    expect(screen.getByText(/闭关三月/)).toBeInTheDocument()
    fireEvent.click(screen.getByText(/闭关三月/))
    expect(handleAction).toHaveBeenCalledWith('闭关3月')
  })

  it('recommends breakthrough when cultivation is full', () => {
    const handleAction = vi.fn()
    const fullPlayer = { ...basePlayer, cultivation: 100, cultivation_required: 100 }
    render(
      <TianjiFocusCard
        player={fullPlayer}
        state={baseState}
        snapshot={baseSnapshot}
        canQuickAct={true}
        onAction={handleAction}
      />
    )

    expect(screen.getByText(/气海翻涌引动天劫/)).toBeInTheDocument()
    expect(screen.getByText(/引动雷劫破境/)).toBeInTheDocument()
    fireEvent.click(screen.getByText(/引动雷劫破境/))
    expect(handleAction).toHaveBeenCalledWith('突破')
  })

  it('recommends rest when player is critically wounded', () => {
    const handleAction = vi.fn()
    const woundedPlayer = { ...basePlayer, health: 20, health_max: 100, condition: '经络重伤' }
    render(
      <TianjiFocusCard
        player={woundedPlayer}
        state={baseState}
        snapshot={baseSnapshot}
        canQuickAct={true}
        onAction={handleAction}
      />
    )

    expect(screen.getByText(/宜入洞府静养/)).toBeInTheDocument()
    expect(screen.getByText(/洞府闭门静养/)).toBeInTheDocument()
    fireEvent.click(screen.getByText(/洞府闭门静养/))
    expect(handleAction).toHaveBeenCalled()
  })

  it('prioritizes pending encounter decisions', () => {
    const handleOpenEncounter = vi.fn()
    const mockEncounter = {
      id: 'enc-1',
      title: '太古神木涅槃',
      category: 'ancient_secret',
      character: { name: '木灵玄女', identity: '树灵', realm: '元婴', temperament: '温婉', avatar_type: 'wood_spirit', quote: '' },
      scene: '神木逢春',
      choices: [],
    }

    render(
      <TianjiFocusCard
        player={basePlayer}
        state={{ ...baseState, phase: 'encounter_choice' }}
        snapshot={baseSnapshot}
        pendingEncounter={mockEncounter}
        canQuickAct={false}
        onAction={vi.fn()}
        onOpenEncounter={handleOpenEncounter}
      />
    )

    expect(screen.getByText(/太古神木涅槃/)).toBeInTheDocument()
    const btn = screen.getByText('定夺机缘因果')
    fireEvent.click(btn)
    expect(handleOpenEncounter).toHaveBeenCalled()
  })
})
