// @vitest-environment jsdom

import { cleanup, render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { afterEach, describe, expect, it } from 'vitest'
import { NpcAvatar, NPC_PORTRAIT_IMAGES, deduceNpcAppearance } from './NpcAvatar'

afterEach(() => cleanup())

describe('NpcAvatar dual-mode portrait engine', () => {
  it('registers high-res 2D anime artworks for core characters', () => {
    expect(NPC_PORTRAIT_IMAGES['顾清玄']).toBeDefined()
    expect(NPC_PORTRAIT_IMAGES['白凝霜']).toBeDefined()
    expect(NPC_PORTRAIT_IMAGES['云栖']).toBeDefined()
    expect(NPC_PORTRAIT_IMAGES['谢无咎']).toBeDefined()
    expect(NPC_PORTRAIT_IMAGES['墨尘']).toBeDefined()
    expect(NPC_PORTRAIT_IMAGES['洛浅浅']).toBeDefined()
  })

  it('renders high-res anime artwork image for registered core characters', () => {
    const { rerender } = render(<NpcAvatar item={{ name: '白凝霜' }} size="large" />)
    const img = screen.getByRole('img', { name: '白凝霜立绘' })
    expect(img).toBeInTheDocument()
    expect(img).toHaveAttribute('src', NPC_PORTRAIT_IMAGES['白凝霜'])

    rerender(<NpcAvatar item={{ name: '云栖' }} size="large" />)
    const yunqiImg = screen.getByRole('img', { name: '云栖立绘' })
    expect(yunqiImg).toBeInTheDocument()
    expect(yunqiImg).toHaveAttribute('src', NPC_PORTRAIT_IMAGES['云栖'])

    rerender(<NpcAvatar item={{ name: '顾清玄' }} size="large" />)
    const guImg = screen.getByRole('img', { name: '顾清玄立绘' })
    expect(guImg).toBeInTheDocument()
    expect(guImg).toHaveAttribute('src', NPC_PORTRAIT_IMAGES['顾清玄'])

    rerender(<NpcAvatar item={{ name: '谢无咎' }} size="large" />)
    const xieImg = screen.getByRole('img', { name: '谢无咎立绘' })
    expect(xieImg).toBeInTheDocument()
    expect(xieImg).toHaveAttribute('src', NPC_PORTRAIT_IMAGES['谢无咎'])

    rerender(<NpcAvatar item={{ name: '墨尘' }} size="large" />)
    const moImg = screen.getByRole('img', { name: '墨尘立绘' })
    expect(moImg).toBeInTheDocument()
    expect(moImg).toHaveAttribute('src', NPC_PORTRAIT_IMAGES['墨尘'])

    rerender(<NpcAvatar item={{ name: '洛浅浅' }} size="large" />)
    const luoImg = screen.getByRole('img', { name: '洛浅浅立绘' })
    expect(luoImg).toBeInTheDocument()
    expect(luoImg).toHaveAttribute('src', NPC_PORTRAIT_IMAGES['洛浅浅'])
  })

  it('renders bespoke SVG vector portrait for characters without raster artwork', () => {
    render(<NpcAvatar item={{ name: '青云知客' }} size="medium" />)
    expect(screen.queryByRole('img', { name: '青云知客立绘' })).not.toBeInTheDocument()
    expect(screen.getByLabelText('青云知客肖像')).toBeInTheDocument()
  })

  it('deduces correct known profiles and lore descriptions', () => {
    const bai = deduceNpcAppearance({ name: '白凝霜' })
    expect(bai.archetypeLabel).toBe('雪岭玄女')
    expect(bai.path).toBe('snow_saint')
    expect(bai.summary).toContain('银发如霜')

    const yun = deduceNpcAppearance({ name: '云栖' })
    expect(yun.archetypeLabel).toBe('天机灵贾')
    expect(yun.path).toBe('merchant')
    expect(yun.summary).toContain('金钗步摇')
  })
})
