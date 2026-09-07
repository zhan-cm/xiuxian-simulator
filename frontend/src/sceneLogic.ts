import type { NpcProfile, Presentation } from './api/types'

export function findEncounterNpc(profiles: Record<string, NpcProfile> | undefined, presentation: Presentation) {
  if (!profiles || presentation.tone !== 'relation') return undefined
  if (!/^(对话|交谈|送礼|论道|结为道侣|双修|确立关系|回应|护道)/.test(presentation.action.trim())) return undefined
  const source = `${presentation.action} ${presentation.title} ${(presentation.paragraphs || []).join(' ')}`
  return Object.values(profiles).find((profile) => source.includes(profile.name))
}
