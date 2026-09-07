// @vitest-environment jsdom

import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Snapshot } from '../api/types'
import { PathwaysCodex } from './PathwaysCodex'

vi.mock('./StoryChronicle', () => ({ StoryChronicle: () => <button>灵潮因果卷</button> }))
vi.mock('./JourneyTracker', () => ({ JourneyTracker: () => <button>道途章程卷</button> }))
vi.mock('./CommissionBoard', () => ({ CommissionBoard: () => <button>东洲悬榜卷</button> }))
vi.mock('./DaoTree', () => ({ DaoTree: () => <button>悟道九途卷</button> }))
vi.mock('./ArtMasteryCodex', () => ({ ArtMasteryCodex: () => <button>万法参研卷</button> }))
vi.mock('./SpiritBeastSanctuary', () => ({ SpiritBeastSanctuary: () => <button>万灵兽苑卷</button> }))
vi.mock('./FormationAtlas', () => ({ FormationAtlas: () => <button>五行阵图卷</button> }))
vi.mock('./ArtifactForge', () => ({ ArtifactForge: () => <button>本命法宝卷</button> }))
vi.mock('./SectLibrary', () => ({ SectLibrary: () => <button>藏经阁卷</button> }))
vi.mock('./SectMembershipPage', () => ({ SectMembershipEntry: () => <button>本宗事务卷</button> }))
vi.mock('./SectDominion', () => ({ SectDominion: () => <button>宗门经营卷</button> }))
vi.mock('./AuctionHouse', () => ({ AuctionHouse: () => <button>天机竞价卷</button> }))
vi.mock('./NewEraChronicle', () => ({ NewEraChronicle: () => <button>新世余波卷</button> }))

afterEach(() => cleanup())

const snapshot = {
  state: { phase: 'playing', player: { spirit_stones: 500 } },
  story: { available: true }, commissions: { active: [{ ready: true }] },
  auction: { active: true, pending: '' }, new_era: { active: true, available: true },
} as unknown as Snapshot

describe('pathways system hub', () => {
  it('shows one system family at a time and preserves every existing destination', () => {
    render(<PathwaysCodex snapshot={snapshot} busy={false} readOnly onAction={vi.fn()} />)
    expect(screen.getByText('灵潮因果卷')).toBeInTheDocument()
    expect(screen.queryByText('万法参研卷')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /修行百艺/ }))
    expect(screen.getByText('万法参研卷')).toBeInTheDocument()
    expect(screen.getByText('本命法宝卷')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /山门事务/ }))
    expect(screen.getByText('藏经阁卷')).toBeInTheDocument()
    expect(screen.getByText('本宗事务卷')).toBeInTheDocument()
    expect(screen.getByText('宗门经营卷')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /九州机缘/ }))
    expect(screen.getByText('天机竞价卷')).toBeInTheDocument()
    expect(screen.getByText('新世余波卷')).toBeInTheDocument()
  })
})
