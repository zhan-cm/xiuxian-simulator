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

export interface JourneyTask {
  id: string
  title: string
  description: string
  hint: string
  complete: boolean
  claimed: boolean
  reward: string
  claim_action: string
}

export interface JourneyChapter {
  id: string
  number: number
  title: string
  summary: string
  unlocked: boolean
  claimed: boolean
  complete: boolean
  completed_tasks: number
  total_tasks: number
  reward_ready: boolean
  reward: string
  claim_action: string
  tasks: JourneyTask[]
}

export interface JourneySnapshot {
  points: number
  active_chapter_id: string
  active: JourneyChapter
  chapters: JourneyChapter[]
}

export interface CommissionOffer {
  id: string
  template_id: string
  title: string
  issuer: string
  kind: string
  kind_label: string
  summary: string
  requirement: string
  duration: number
  reward: string
  accepted: boolean
  completed: boolean
  eligible: boolean
  disabled_reason: string
  accept_action: string
}

export interface ActiveCommission extends CommissionOffer {
  current: number
  required: number
  progress: number
  ready: boolean
  expired: boolean
  turns_left: number
  deadline_turn: number
  deliver_action: string
  abandon_action: string
}

export interface CommissionSnapshot {
  title: string
  cycle: number
  rotation_label: string
  active_limit: number
  active_count: number
  renown: number
  completed_count: number
  offers: CommissionOffer[]
  active: ActiveCommission[]
  history: string[]
}

export interface StoryChapter {
  id: string; chapter: number; title: string; summary: string; location: string
  completed: boolean; choice: string; unlocked: boolean; locked_hint: string
}

export interface StorySnapshot {
  title: string; completed: number; total: number; available: boolean
  begin_action: string; next_hint: string; pending: string
  chapters: StoryChapter[]; history: string[]
}

export interface InventoryItem {
  name: string; count: number; category: string; rarity: string
  description: string; usage: string; equipped: boolean; slot: string
  action: string; action_label: string; actionable: boolean; disabled_reason: string
}

export interface InventorySnapshot {
  items: InventoryItem[]; categories: string[]; total_types: number; total_count: number
  equipped: { weapon: string; armor: string }
}

export interface AuctionLot {
  id: string; name: string; summary: string; reserve: number; increment: number
  rewards: Record<string, number>; minimum_realm: number; minimum_realm_label: string
  status: 'available' | 'won' | 'lost' | 'expired'; price: number; winner: string
  eligible: boolean; affordable: boolean; begin_action: string
}

export interface AuctionSnapshot {
  active: boolean; title: string; closes_in: number; competitor: string; competitor_style: string
  pending: string; lots: AuctionLot[]; history: string[]
}

export interface TravelRegion {
  key: string; name: string; minimum_realm: number; minimum_realm_label: string
  danger: number; description: string; specialties: string[]; demands: string[]
  months: number; current: boolean; visited: boolean; accessible: boolean; action: string
  reputation: number; rank: string; buy_discount: number; sell_bonus: number
  travel_bonus: number; exploration_bonus: number
}

export interface TravelSnapshot {
  current: string; current_name: string; visited: string[]; pending: Record<string, unknown>
  trade_profit: number; current_reputation: Record<string, unknown>; regions: TravelRegion[]; history: string[]
}

export interface RegionalStanding {
  key: string; reputation: number; rank: string; buy_discount: number; sell_bonus: number
  travel_bonus: number; exploration_bonus: number; trade_volume: number; explorations: number
  encounter_title: string; encounter_completed: boolean
}

export interface RegionalSnapshot {
  current: string; current_rank: string; pending: Record<string, unknown>
  standings: RegionalStanding[]; history: string[]
}

export interface CaveFocus {
  name: string; summary: string; active: boolean; available: boolean
  disabled_reason: string; action: string
}

export interface CaveJob {
  id: string; recipe: string; craft: string; facility: string; duration: number
  months_left: number; progress: number; chance: number; output: string
  output_count: number; ingredients: Record<string, number>; cancel_action: string
}

export interface CaveBlueprint {
  name: string; craft: string; facility: string; duration: number
  ingredients: Record<string, number>; output: string; output_count: number
  chance: number; available: boolean; disabled_reason: string; action: string
}

export interface CaveSnapshot {
  name: string; aura: string; spirit_energy: number; spirit_energy_cap: number
  monthly_generation: number; focus: string; focuses: CaveFocus[]
  capacity: number; active_jobs: number; jobs: CaveJob[]; blueprints: CaveBlueprint[]
  last_event: string; ledger: string[]; can_recuperate: boolean; recuperate_reason: string
}

export interface Snapshot {
  state: GameState
  narrator: string
  save_names: string[]
  save_summaries: Array<Record<string, unknown>>
  presentation: Presentation
  decision: Decision
  npc_profiles: Record<string, NpcProfile>
  journey: JourneySnapshot
  commissions: CommissionSnapshot
  story: StorySnapshot
  inventory: InventorySnapshot
  auction: AuctionSnapshot
  travel: TravelSnapshot
  regional: RegionalSnapshot
  cave: CaveSnapshot
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
