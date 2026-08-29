export interface PlayerState {
  name: string
  dao_name: string
  gender: string
  age: number
  lifespan: number
  realm: string
  sect: string
  sect_rank: string
  spiritual_root: string
  constitution: string
  health: number
  health_max: number
  spirit: number
  spirit_max: number
  cultivation: number
  cultivation_required: number
  spirit_stones: number
  condition: string
  location: string
  inventory: string[]
  resources: Record<string, number>
  [key: string]: unknown
}

export interface GameState {
  version: string
  phase: string
  turn: number
  calendar_year: number
  month: number
  main_quest: string
  history: string[]
  world_era: string
  last_world_event: string
  relationship_tension: number
  npc_relations: Record<string, { affinity?: number; path?: string }>
  player: PlayerState
  [key: string]: unknown
}

export interface PresentationBlock {
  type: string
  title?: string
  meta?: string
  legend?: string
  value?: number
  max?: number
  items?: Array<Record<string, unknown>>
  [key: string]: unknown
}

export interface Presentation {
  action: string
  title: string
  eyebrow: string
  seal: string
  tone: string
  paragraphs: string[]
  changes: Array<{ label: string; value: string }>
  blocks: PresentationBlock[]
  details: string
  has_details: boolean
}

export interface DecisionChoice {
  label: string
  action: string
  description: string
  summary?: string
  tone?: 'primary' | 'danger' | 'safe' | 'quiet'
  disabled?: boolean
  disabled_reason?: string
}

export interface Decision {
  eyebrow: string
  title: string
  hint: string
  exclusive: boolean
  choices: DecisionChoice[]
}

export interface NpcProfile {
  name: string
  gender: string
  identity: string
  age: number
  realm: string
  location: string
  greeting: string
  affinity: number
  relation: string
}

export interface Snapshot {
  state: GameState
  narrator: string
  save_names: string[]
  save_summaries: Array<Record<string, unknown>>
  presentation: Presentation
  decision: Decision
  npc_profiles: Record<string, NpcProfile>
  output?: string
}

export interface ShowcasePage {
  id: string
  title: string
  description: string
  checklist: string[]
  snapshot: Snapshot
}

export interface ShowcaseResponse {
  pages: ShowcasePage[]
}
