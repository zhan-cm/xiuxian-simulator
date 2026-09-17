// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ArtifactSpiritModal } from './ArtifactSpiritModal'
import type { ArtifactSpiritSnapshot } from '../api/types'

afterEach(() => cleanup())

const mockArchetypes = [
  {
    id: 'sword_fairy',
    name: '素衣剑仙子',
    title: '太古纯阳剑灵',
    description: '一袭素白剑衣迎风飘拂，明眸如霜。',
    personality: '清冷高绝 · 剑心护主',
    default_name: '青霜',
    combat_skill_name: '青莲断空斩',
    combat_skill_desc: '每隔一轮引动天地剑煞斩击敌方！',
    attack_multiplier: 1.15,
    defense_bonus: 0,
    max_health_bonus: 0,
  },
  {
    id: 'thunder_child',
    name: '紫霄雷灵童',
    title: '紫霄雷煞正灵',
    description: '银发紫眸的小道童，身披紫电道袍。',
    personality: '傲娇好胜 · 雷厉风行',
    default_name: '雷霄',
    combat_skill_name: '紫霄诛魔雷',
    combat_skill_desc: '雷芒贯顶轰杀对手！',
    attack_multiplier: 1.18,
    defense_bonus: 10,
    max_health_bonus: 0,
  },
]

describe('ArtifactSpiritModal', () => {
  it('renders manifestation view when spirit is not yet manifested', () => {
    const handleAction = vi.fn()
    const handleOpenChange = vi.fn()

    const snapshot: ArtifactSpiritSnapshot = {
      bonded_artifact: '青竹蜂云剑',
      resonance: 45,
      can_manifest: true,
      manifest_reason: '',
      spirit: null,
      archetypes: mockArchetypes,
      history: ['祭炼本命青竹蜂云剑大成'],
    }

    render(
      <ArtifactSpiritModal
        open={true}
        onOpenChange={handleOpenChange}
        artifactSpirit={snapshot}
        onAction={handleAction}
      />
    )

    expect(screen.getByText('本命法宝 · 器灵化形阁')).toBeInTheDocument()
    expect(screen.getByText('【青竹蜂云剑】')).toBeInTheDocument()
    expect(screen.getByText(/器心契合：45\/100/)).toBeInTheDocument()
    expect(screen.getByText('素衣剑仙子')).toBeInTheDocument()
    expect(screen.getByText('紫霄雷灵童')).toBeInTheDocument()

    // Select thunder_child
    fireEvent.click(screen.getByText('紫霄雷灵童'))

    // Custom name input
    const input = screen.getByPlaceholderText('雷霄')
    fireEvent.change(input, { target: { value: '霄儿' } })

    // Click manifest
    const manifestBtn = screen.getByRole('button', { name: /唤醒化形大典/ })
    fireEvent.click(manifestBtn)
    expect(handleAction).toHaveBeenCalledWith('器灵化形 thunder_child 霄儿')
  })

  it('disables ceremony button when cannot manifest', () => {
    const handleAction = vi.fn()
    const snapshot: ArtifactSpiritSnapshot = {
      bonded_artifact: '青竹蜂云剑',
      resonance: 15,
      can_manifest: false,
      manifest_reason: '器心契合度不足（当前 15/100，需达 30）',
      spirit: null,
      archetypes: mockArchetypes,
      history: [],
    }

    render(
      <ArtifactSpiritModal
        open={true}
        onOpenChange={vi.fn()}
        artifactSpirit={snapshot}
        onAction={handleAction}
      />
    )

    const btn = screen.getByRole('button', { name: /唤醒化形大典/ })
    expect(btn).toBeDisabled()
    expect(
      screen.getByText('器心契合度不足（当前 15/100，需达 30）')
    ).toBeInTheDocument()
  })

  it('renders active spirit view with stats, feeds, and interactions', () => {
    const handleAction = vi.fn()
    const snapshot: ArtifactSpiritSnapshot = {
      bonded_artifact: '青竹蜂云剑',
      resonance: 60,
      can_manifest: true,
      manifest_reason: '',
      spirit: {
        name: '青霜',
        artifact_name: '青竹蜂云剑',
        archetype_id: 'sword_fairy',
        archetype_name: '素衣剑仙子',
        title: '太古纯阳剑灵',
        description: '一袭素白剑衣迎风飘拂',
        personality: '清冷高绝 · 剑心护主',
        level: 2,
        intimacy: 72,
        exp: 40,
        is_active: true,
        combat_skill_name: '青莲断空斩',
        combat_skill_desc: '每隔一轮引动天地剑煞斩击敌方！',
        skill_value: 60,
        attack_multiplier: 1.15,
        defense_bonus: 10,
        max_health_bonus: 0,
        dialogue_history: ['青霜：“主人剑锋所指，青霜长剑所向。”'],
      },
      archetypes: mockArchetypes,
      history: ['真灵化形大成！诞生侍从【青霜】'],
    }

    render(
      <ArtifactSpiritModal
        open={true}
        onOpenChange={vi.fn()}
        artifactSpirit={snapshot}
        onAction={handleAction}
      />
    )

    // Check spirit details
    expect(screen.getByText('青霜')).toBeInTheDocument()
    expect(screen.getByText('2 阶器灵')).toBeInTheDocument()
    expect(screen.getByText(/40 \/ 200 EXP/)).toBeInTheDocument()
    expect(screen.getByText('72 / 100')).toBeInTheDocument()
    expect(screen.getByText('《青莲断空斩》')).toBeInTheDocument()
    expect(screen.getByText('青霜：“主人剑锋所指，青霜长剑所向。”')).toBeInTheDocument()

    // Recall spirit
    const recallBtn = screen.getByRole('button', { name: /召回器灵/ })
    fireEvent.click(recallBtn)
    expect(handleAction).toHaveBeenCalledWith('召回器灵')

    // Feed spirit
    const feedStonesBtn = screen.getByRole('button', { name: /灵石 \(50枚\)/ })
    fireEvent.click(feedStonesBtn)
    expect(handleAction).toHaveBeenCalledWith('器灵喂养 灵石')

    const feedPillBtn = screen.getByRole('button', { name: /聚气丹/ })
    fireEvent.click(feedPillBtn)
    expect(handleAction).toHaveBeenCalledWith('器灵喂养 聚气丹')

    // Quick topic talk
    const topicBtn = screen.getByRole('button', { name: '温养如何？' })
    fireEvent.click(topicBtn)
    expect(handleAction).toHaveBeenCalledWith('器灵交谈 器灵近来温养可觉通畅？')

    // Custom talk input
    const talkInput = screen.getByPlaceholderText('对【青霜】说些什么……')
    fireEvent.change(talkInput, { target: { value: '今天练剑可有心得？' } })
    const sendBtn = screen.getByRole('button', { name: /传言/ })
    fireEvent.click(sendBtn)
    expect(handleAction).toHaveBeenCalledWith('器灵交谈 今天练剑可有心得？')
  })
})
