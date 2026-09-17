// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { BreakthroughAltar } from './BreakthroughAltar'
import type { Snapshot } from '../api/types'

afterEach(() => cleanup())

const mockSnapshot = {
  app_version: '1.0.0',
  state: {
    version: '1.0.0',
    phase: 'playing',
    turn: 12,
    calendar_year: 388,
    month: 3,
    main_quest: '凝丹化境',
    history: [],
    world_era: '灵潮前夜',
    last_world_event: '',
    relationship_tension: 0,
    npc_relations: {},
    player: {
      name: '顾清玄',
      dao_name: '长生',
      gender: '乾',
      age: 28,
      lifespan: 100,
      realm: '炼气·圆满',
      sect: '青云宗',
      sect_rank: '真传弟子',
      spiritual_root: '天灵根',
      constitution: '纯阳剑体',
      health: 120,
      health_max: 120,
      spirit: 100,
      spirit_max: 100,
      cultivation: 100,
      cultivation_required: 100,
      spirit_stones: 500,
      condition: '健康',
      location: '东洲·青岳',
      inventory: [],
      resources: {
        筑基丹: 1,
        天材地宝: 1,
        五行灵珠: 1,
        道韵: 1,
      },
    },
  },
  narrator: '通晓古今',
  save_names: [],
  save_summaries: [],
  presentation: {
    action: '突破',
    title: '叩问天关',
    blocks: [],
  },
  decision: {
    eyebrow: '破境路线',
    title: '选择此番道基',
    hint: '定夺未来仙途',
    exclusive: true,
    choices: [],
  },
  npc_profiles: {},
  journey: { chapters: [], active_chapter: 0, total_points: 0, rewards_claimed: [] },
  commissions: { active: [], completed: [], total_renown: 0 },
  story: { current_node: 'start', history: [] },
  new_era: { era_name: '灵潮初现', countdown: 10, choices: [] },
  dao: { paths: [] },
  spirit_beasts: { beasts: [], active_id: '' },
  formations: { arrays: [], active_id: '' },
  sect_library: { books: [], read_ids: [] },
  sect_membership: { contribution: 100, rank: '真传', privileges: [] },
  artifacts: { count: 0, bonded_name: '', level_cap: 3, level_cap_label: '', artifacts: [] },
  art_mastery: { techniques: [], spells: [] },
  recovery: { active_injuries: [], history: [] },
  legacy: { generation: 1, past_lives: [] },
  sect_domain: { buildings: [], disciples: [], territories: [] },
  inventory: { items: [], capacity: 50 },
  auction: { items: [], active: false },
  travel: { current_region: '东洲', destinations: [] },
  regional: { regions: [] },
  cave: { facilities: [], focus: '' },
  npc_lives: { profiles: [], active_events: [] },
  npc_network: { network_events: [], logs: [] },
  tribulation: {
    current_realm: '炼气·圆满',
    target_realm: '筑基',
    target_realm_index: 1,
    tier_info: {
      tier: 1,
      name: '一九玄霄雷劫',
      title: '玄霄涤凡',
      description: '天地灵气初凝，降下三波玄霄紫雷涤荡肉胎凡骨。',
      waves_count: 3,
      base_power: 120,
      wave_names: ['第一重 · 青木引雷', '第二重 · 庚金疾雷', '第三重 · 玄霄落顶'],
      element: '紫霄玄雷',
      threat_level: '凡凡相蜕',
    },
    protection: {
      has_artifact: true,
      artifact_name: '太玄青锋剑',
      artifact_tier: '玄阶',
      affinity: 70,
      inscriptions: ['雷罡', '护命'],
      has_thunder_seal: true,
      has_life_seal: true,
      has_solid_seal: false,
      has_chaos_seal: false,
      spirit_stage: '形意',
      spirit_stage_index: 2,
      formation_shield: 160,
      has_ward_talisman: true,
      has_protect_pill: false,
      has_breakthrough_pill: true,
      thunder_mitigation_rate: 45.5,
      protection_tags: ['雷罡·引雷淬体', '护命·绝境免死', '洞府阵幕(160点)', '天机·避劫符'],
      defense_score: 110,
      readiness_label: '万全通天',
    },
  },
} as unknown as Snapshot

describe('BreakthroughAltar component', () => {
  it('正确渲染天劫雷罚威仪与护道底牌大阵面板', () => {
    render(
      <BreakthroughAltar
        snapshot={mockSnapshot}
        busy={false}
        readOnly={false}
        onAction={vi.fn()}
      />
    )

    // 验证天劫威仪卡片
    expect(screen.getByText('一九玄霄雷劫')).toBeInTheDocument()
    expect(screen.getByText(/三波玄霄紫雷涤荡肉胎凡骨/)).toBeInTheDocument()
    expect(screen.getByText('凡凡相蜕')).toBeInTheDocument()

    // 验证护道底牌大阵
    expect(screen.getByText('护道底牌大阵')).toBeInTheDocument()
    expect(screen.getByText('万全通天')).toBeInTheDocument()
    expect(screen.getByText('+45.5%')).toBeInTheDocument()
    expect(screen.getByText('160点')).toBeInTheDocument()
    expect(screen.getByText('已就绪')).toBeInTheDocument()
    expect(screen.getByText(/本命【太玄青锋剑】· 形意/)).toBeInTheDocument()
    expect(screen.getByText(/雷罡·引雷淬体/)).toBeInTheDocument()
    expect(screen.getByText(/护命·绝境免死/)).toBeInTheDocument()
  })

  it('点击人道叩关按钮触发 onAction', () => {
    const onAction = vi.fn()
    render(
      <BreakthroughAltar
        snapshot={mockSnapshot}
        busy={false}
        readOnly={false}
        onAction={onAction}
      />
    )

    const humanBtn = screen.getByRole('button', { name: /叩定人道/ })
    expect(humanBtn).toBeInTheDocument()
    fireEvent.click(humanBtn)
    expect(onAction).toHaveBeenCalledWith('突破 人道')
  })

  it('渡劫战报输出时正确展示渡劫回响卡片', () => {
    const snapshotWithOutput = {
      ...mockSnapshot,
      output: '【一九玄霄雷劫】· 人道叩关渡劫战报\n天劫雷罚：共降下 3/3 重九霄神雷，总承雷威 280 点。',
    }

    render(
      <BreakthroughAltar
        snapshot={snapshotWithOutput}
        busy={false}
        readOnly={false}
        onAction={vi.fn()}
      />
    )

    expect(screen.getByRole('region', { name: '渡劫回响战报' })).toBeInTheDocument()
    expect(screen.getByText(/共降下 3\/3 重九霄神雷/)).toBeInTheDocument()
  })
})
