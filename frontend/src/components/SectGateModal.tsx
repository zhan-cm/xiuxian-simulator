import * as Dialog from '@radix-ui/react-dialog'
import {
  Award,
  Coins,
  Compass,
  Gift,
  Handshake,
  MapPin,
  Mountain,
  ScrollText,
  ShieldAlert,
  Sparkles,
  Swords,
  X,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import type { SectGateData, SectVisitSnapshot } from '../api/types'

export interface SectGateModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  sectVisit?: SectVisitSnapshot
  initialSect?: string
  busy: boolean
  readOnly?: boolean
  onAction: (action: string) => void
}

const FALLBACK_GATES: SectGateData[] = [
  {
    name: '青云宗',
    province: '东洲青岳',
    mark: '云',
    doctrine: '正道名门 · 剑道通玄',
    motto: '清正持剑，守望东洲',
    description: '雄踞东洲青岳群峰之巅，云蒸霞蔚，剑阁高耸。门风端严，历代护持凡尘安宁。',
    welcome_gift: '青云剑穗',
    welcome_gift_count: 1,
    can_visit: true,
    visit_action: '拜山 青云宗',
    spar_chance: 65,
    spar_action: '山门演武 青云宗',
    treasures: [
      {
        id: 'qy-pill',
        name: '聚气丹',
        cost_stones: 180,
        category: '丹药',
        reputation_req: 10,
        count: 3,
        summary: '青云灵药圃秘炼聚气丹，温润纯和。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 青云宗 qy-pill',
      },
      {
        id: 'qy-sword',
        name: '青锋剑',
        cost_stones: 350,
        category: '法宝',
        reputation_req: 30,
        count: 1,
        summary: '青云洗剑池淬砺上品法剑，锋锐不折。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 青云宗 qy-sword',
      },
      {
        id: 'qy-pendant',
        name: '青云佩',
        cost_stones: 600,
        category: '奇珍',
        reputation_req: 60,
        count: 1,
        summary: '聚青岳千年浩气，可宁心避劫。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 青云宗 qy-pendant',
      },
    ],
    bounties: [
      {
        id: 'qy-bounty-1',
        title: '清剿青岳外围妖狼',
        risk: '普通',
        chance: 75,
        reward_stones: 200,
        reward_reputation: 10,
        reward_items: { 妖兽材料: 2 },
        summary: '扫荡潜入青岳灵脉边缘的嗜血妖狼群。',
        action: '山门历练 青云宗 qy-bounty-1',
      },
      {
        id: 'qy-bounty-2',
        title: '诛灭东洲魔道逆徒',
        risk: '凶险',
        chance: 62,
        reward_stones: 450,
        reward_reputation: 25,
        reward_items: { 魔道余烬: 1, 灵石: 100 },
        summary: '斩杀残害乡里的魔修逆徒，取回被掠宗门法册。',
        action: '山门历练 青云宗 qy-bounty-2',
      },
    ],
  },
  {
    name: '丹霞谷',
    province: '南荒丹霞',
    mark: '丹',
    doctrine: '万火归元 · 济世丹道',
    motto: '丹火养生，济世求真',
    description: '深藏南荒十万群山之中，地肺真火万载不绝。百草芬芳，天下灵药多出其门。',
    welcome_gift: '回春灵泉',
    welcome_gift_count: 2,
    can_visit: true,
    visit_action: '拜山 丹霞谷',
    spar_chance: 60,
    spar_action: '山门演武 丹霞谷',
    treasures: [
      {
        id: 'dx-herb',
        name: '灵药',
        cost_stones: 120,
        category: '材料',
        reputation_req: 10,
        count: 4,
        summary: '丹霞药圃肥土灌溉的高品灵草。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 丹霞谷 dx-herb',
      },
      {
        id: 'dx-healing',
        name: '疗伤丹',
        cost_stones: 220,
        category: '丹药',
        reputation_req: 20,
        count: 2,
        summary: '深谙药理之长老亲手开炉炼制，回春奇效。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 丹霞谷 dx-healing',
      },
      {
        id: 'dx-purify',
        name: '洗髓丹',
        cost_stones: 800,
        category: '丹药',
        reputation_req: 70,
        count: 1,
        summary: '伐毛洗髓脱胎换骨之无上圣丹。',
        available: false,
        disabled_reason: '声望不足（需 70）',
        action: '求丹借宝 丹霞谷 dx-purify',
      },
    ],
    bounties: [
      {
        id: 'dx-bounty-1',
        title: '采撷绝壁龙血芝',
        risk: '稳健',
        chance: 80,
        reward_stones: 220,
        reward_reputation: 12,
        reward_items: { 灵药: 3 },
        summary: '前往赤霞万丈绝壁采摘悬生灵芝。',
        action: '山门历练 丹霞谷 dx-bounty-1',
      },
      {
        id: 'dx-bounty-2',
        title: '护送百草灵舟',
        risk: '凶险',
        chance: 65,
        reward_stones: 500,
        reward_reputation: 25,
        reward_items: { 灵药: 5, 疗伤丹: 1 },
        summary: '护卫载满各洲紧缺丹药的飞舟穿过毒雾瘴林。',
        action: '山门历练 丹霞谷 dx-bounty-2',
      },
    ],
  },
  {
    name: '玄剑门',
    province: '西漠千峰',
    mark: '剑',
    doctrine: '唯剑极道 · 生死试锋',
    motto: '以战磨剑，锋芒证道',
    description: '屹立西漠千仞绝壁，终年剑罡呼啸。门人崇尚极意杀伐，门下弟子皆以剑为命。',
    welcome_gift: '淬剑灵砂',
    welcome_gift_count: 2,
    can_visit: true,
    visit_action: '拜山 玄剑门',
    spar_chance: 55,
    spar_action: '山门演武 玄剑门',
    treasures: [
      {
        id: 'xj-iron',
        name: '灵铁',
        cost_stones: 160,
        category: '材料',
        reputation_req: 10,
        count: 5,
        summary: '地火万锻玄铁，坚固异凡。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 玄剑门 xj-iron',
      },
      {
        id: 'xj-blade',
        name: '玄铁剑',
        cost_stones: 400,
        category: '法宝',
        reputation_req: 35,
        count: 1,
        summary: '玄剑门真传弟子制式重刃，煞气凝重。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 玄剑门 xj-blade',
      },
      {
        id: 'xj-stone',
        name: '太玄剑石',
        cost_stones: 750,
        category: '奇珍',
        reputation_req: 75,
        count: 1,
        summary: '上古剑修留痕的顽石，暗蕴通天剑意。',
        available: false,
        disabled_reason: '声望不足（需 75）',
        action: '求丹借宝 玄剑门 xj-stone',
      },
    ],
    bounties: [
      {
        id: 'xj-bounty-1',
        title: '斩杀荒漠赤尾蝎王',
        risk: '普通',
        chance: 70,
        reward_stones: 260,
        reward_reputation: 15,
        reward_items: { 妖兽材料: 3 },
        summary: '斩杀荒漠中肆虐商路的毒蝎巨妖。',
        action: '山门历练 玄剑门 xj-bounty-1',
      },
      {
        id: 'xj-bounty-2',
        title: '夺取天外陨铁石',
        risk: '凶险',
        chance: 60,
        reward_stones: 550,
        reward_reputation: 30,
        reward_items: { 灵铁: 6 },
        summary: '深入西漠绝境古裂谷，击退争夺者夺取陨铁。',
        action: '山门历练 玄剑门 xj-bounty-2',
      },
    ],
  },
  {
    name: '合欢宗',
    province: '中州万象',
    mark: '欢',
    doctrine: '阴阳和合 · 极乐心印',
    motto: '天地同情，落英飞花',
    description: '中州桃源秘境之中，桃花纷坠，丝竹悦耳。门人修习阴阳和合妙术，眼波流转勾魂摄魄。',
    welcome_gift: '合欢香囊',
    welcome_gift_count: 1,
    can_visit: true,
    visit_action: '拜山 合欢宗',
    spar_chance: 68,
    spar_action: '山门演武 合欢宗',
    treasures: [
      {
        id: 'hh-wine',
        name: '桃花醉',
        cost_stones: 150,
        category: '灵物',
        reputation_req: 10,
        count: 2,
        summary: '百年灵桃古树花蕊酿制，解百愁增好感。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 合欢宗 hh-wine',
      },
      {
        id: 'hh-robe',
        name: '护身法袍',
        cost_stones: 380,
        category: '法宝',
        reputation_req: 30,
        count: 1,
        summary: '天蚕冰丝与七彩云霞所织，轻盈无匹。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 合欢宗 hh-robe',
      },
      {
        id: 'hh-pendant',
        name: '相思引',
        cost_stones: 680,
        category: '奇珍',
        reputation_req: 65,
        count: 1,
        summary: '情丝千缠百转之宝，佩之可护神魂不坠。',
        available: false,
        disabled_reason: '声望不足（需 65）',
        action: '求丹借宝 合欢宗 hh-pendant',
      },
    ],
    bounties: [
      {
        id: 'hh-bounty-1',
        title: '搜集千年落英凝露',
        risk: '稳健',
        chance: 82,
        reward_stones: 200,
        reward_reputation: 12,
        reward_items: { 灵药: 2 },
        summary: '清晨在仙谷采摘带有灵气的桃花朝露。',
        action: '山门历练 合欢宗 hh-bounty-1',
      },
      {
        id: 'hh-bounty-2',
        title: '抚平中州情海孽缘',
        risk: '凶险',
        chance: 66,
        reward_stones: 480,
        reward_reputation: 24,
        reward_items: { 灵石: 200 },
        summary: '化解名门弟子与魔道修士的生死死仇纠葛。',
        action: '山门历练 合欢宗 hh-bounty-2',
      },
    ],
  },
  {
    name: '古妖山',
    province: '十万祖山',
    mark: '妖',
    doctrine: '蛮荒血脉 · 龙骨通天',
    motto: '百兽为宗，万妖独尊',
    description: '隐于崇山密林尽头，万峰盘虬，群妖啸月。妖修天生肉身强横，崇尚强者为尊之蛮荒法则。',
    welcome_gift: '蛮荒兽骨',
    welcome_gift_count: 2,
    can_visit: true,
    visit_action: '拜山 古妖山',
    spar_chance: 58,
    spar_action: '山门演武 古妖山',
    treasures: [
      {
        id: 'gy-bone',
        name: '妖兽材料',
        cost_stones: 150,
        category: '材料',
        reputation_req: 10,
        count: 4,
        summary: '大荒蛮兽坚韧骨牙，为炼器上选。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 古妖山 gy-bone',
      },
      {
        id: 'gy-blood',
        name: '万妖真血',
        cost_stones: 450,
        category: '奇珍',
        reputation_req: 40,
        count: 1,
        summary: '淬炼肉身皮膜之无上灵液，力能拔山。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 古妖山 gy-blood',
      },
      {
        id: 'gy-scale',
        name: '苍龙逆鳞',
        cost_stones: 850,
        category: '法宝',
        reputation_req: 80,
        count: 1,
        summary: '相传上古龙族遗留之厚重鳞片，刀枪不入。',
        available: false,
        disabled_reason: '声望不足（需 80）',
        action: '求丹借宝 古妖山 gy-scale',
      },
    ],
    bounties: [
      {
        id: 'gy-bounty-1',
        title: '平息莽荒暴动幼兽',
        risk: '稳健',
        chance: 78,
        reward_stones: 240,
        reward_reputation: 14,
        reward_items: { 妖兽材料: 2 },
        summary: '安抚因灵气躁动而狂怒的大荒灵兽幼崽。',
        action: '山门历练 古妖山 gy-bounty-1',
      },
      {
        id: 'gy-bounty-2',
        title: '猎杀千丈深谷虺龙',
        risk: '凶险',
        chance: 58,
        reward_stones: 600,
        reward_reputation: 35,
        reward_items: { 妖兽材料: 5, 灵铁: 4 },
        summary: '深入祖山毒瘴深渊，击杀为祸一方的恶蛟。',
        action: '山门历练 古妖山 gy-bounty-2',
      },
    ],
  },
  {
    name: '血魔宗',
    province: '北原雪岭',
    mark: '煞',
    doctrine: '血煞九幽 · 杀伐无量',
    motto: '顺我者生，逆我者戮',
    description: '坐落北原极寒深渊绝壁，血海翻浪，魔雾横空。信奉杀伐掠夺，门人冷酷绝情、嗜血如狂。',
    welcome_gift: '血煞幽晶',
    welcome_gift_count: 1,
    can_visit: true,
    visit_action: '拜山 血魔宗',
    spar_chance: 52,
    spar_action: '山门演武 血魔宗',
    treasures: [
      {
        id: 'xm-shard',
        name: '煞气结晶',
        cost_stones: 180,
        category: '材料',
        reputation_req: 10,
        count: 3,
        summary: '万载血池凝结之阴煞奇石。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 血魔宗 xm-shard',
      },
      {
        id: 'xm-pill',
        name: '化血丹',
        cost_stones: 380,
        category: '丹药',
        reputation_req: 35,
        count: 1,
        summary: '燃血爆发暴击之霸道魔丹，短时实力暴涨。',
        available: true,
        disabled_reason: '',
        action: '求丹借宝 血魔宗 xm-pill',
      },
      {
        id: 'xm-orb',
        name: '九幽嗜血珠',
        cost_stones: 780,
        category: '法宝',
        reputation_req: 75,
        count: 1,
        summary: '吸食天地煞气凝聚而成的杀伐重宝。',
        available: false,
        disabled_reason: '声望不足（需 75）',
        action: '求丹借宝 血魔宗 xm-orb',
      },
    ],
    bounties: [
      {
        id: 'xm-bounty-1',
        title: '清剿雪原白骨魔窟',
        risk: '普通',
        chance: 72,
        reward_stones: 280,
        reward_reputation: 16,
        reward_items: { 煞气结晶: 2 },
        summary: '扫清潜伏在雪山暗穴中的失控骨魔。',
        action: '山门历练 血魔宗 xm-bounty-1',
      },
      {
        id: 'xm-bounty-2',
        title: '截杀魔门叛逃使者',
        risk: '凶险',
        chance: 60,
        reward_stones: 520,
        reward_reputation: 30,
        reward_items: { 化血丹: 1, 灵石: 150 },
        summary: '追猎携带门派血经逃亡的叛徒执事。',
        action: '山门历练 血魔宗 xm-bounty-2',
      },
    ],
  },
]

type SectModalTab = 'visit' | 'treasures' | 'spar' | 'bounties'

export function SectGateModal({
  open,
  onOpenChange,
  sectVisit,
  initialSect,
  busy,
  readOnly = false,
  onAction,
}: SectGateModalProps) {
  const gates = useMemo(() => {
    if (sectVisit?.gates && sectVisit.gates.length > 0) {
      return sectVisit.gates
    }
    return FALLBACK_GATES
  }, [sectVisit])

  const [selectedSectName, setSelectedSectName] = useState<string>(
    initialSect || gates[0]?.name || '青云宗'
  )
  const [activeTab, setActiveTab] = useState<SectModalTab>('visit')

  useEffect(() => {
    if (initialSect) {
      setSelectedSectName(initialSect)
    }
  }, [initialSect])

  const activeGate = useMemo(() => {
    return gates.find((g) => g.name === selectedSectName) || gates[0] || FALLBACK_GATES[0]
  }, [gates, selectedSectName])

  const playerSect = sectVisit?.player_sect || '山野散修'
  const playerStones = sectVisit?.player_stones ?? 100
  const playerReputation = sectVisit?.player_reputation ?? 10
  const giftCost = sectVisit?.gift_cost ?? 50
  const isOwnSect = Boolean(playerSect && playerSect === activeGate.name)
  const canAffordVisit = playerStones >= giftCost

  const handleAction = (act: string) => {
    if (busy || readOnly) return
    onAction(act)
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content
          className="character-dialog sect-gate-dialog"
          aria-describedby="sect-gate-desc"
        >
          {/* Header */}
          <header className="sect-gate-header">
            <div className="sect-gate-title-box">
              <span className="sect-gate-seal" aria-hidden="true">
                宗
              </span>
              <div>
                <small>仙门请益 · 外务巡礼</small>
                <Dialog.Title className="sect-gate-title">九州各大宗门拜山案席</Dialog.Title>
                <Dialog.Description id="sect-gate-desc" className="sect-gate-desc">
                  叩拜各大名门知客台论道交游、求取镇派宝物、登擂演武或承接宗门外务悬赏。
                </Dialog.Description>
              </div>
            </div>
            <Dialog.Close aria-label="关闭山门案席" className="sect-gate-close">
              <X size={20} />
            </Dialog.Close>
          </header>

          {/* Cultivator Status Bar */}
          <div className="sect-gate-status-bar">
            <div className="status-item">
              <Compass size={14} />
              <span>
                当前道途：<strong>{playerSect}</strong>
              </span>
            </div>
            <div className="status-item">
              <Coins size={14} />
              <span>
                灵石：<strong>{playerStones}</strong>
              </span>
            </div>
            <div className="status-item">
              <Award size={14} />
              <span>
                修仙声望：<strong>{playerReputation}</strong>
              </span>
            </div>
            <div className="status-item gift-cost-item">
              <Gift size={14} />
              <span>
                拜山礼金：<strong>{giftCost} 灵石</strong>
              </span>
            </div>
          </div>

          {/* 6 Sects Selector Grid / Tabs */}
          <nav className="sect-gate-selector-nav" aria-label="选择九州宗门">
            {gates.map((g) => {
              const isSelected = g.name === activeGate.name
              const isPlayerBelong = Boolean(playerSect && playerSect === g.name)
              return (
                <button
                  key={g.name}
                  type="button"
                  className={`sect-pill-btn ${isSelected ? 'active' : ''}`}
                  onClick={() => setSelectedSectName(g.name)}
                  aria-pressed={isSelected}
                >
                  <span className="sect-mark-badge">{g.mark}</span>
                  <div className="sect-pill-info">
                    <strong>{g.name}</strong>
                    <small>{g.province}</small>
                  </div>
                  {isPlayerBelong && <span className="own-sect-tag">同门</span>}
                </button>
              )
            })}
          </nav>

          {/* Selected Sect Profile Banner */}
          <section className="sect-gate-hero-card">
            <div className="hero-left">
              <div className="hero-mark-badge">{activeGate.mark}</div>
              <div className="hero-titles">
                <div className="hero-header-row">
                  <h3>{activeGate.name}</h3>
                  <span className="province-tag">
                    <MapPin size={12} />
                    {activeGate.province}
                  </span>
                  {isOwnSect && <span className="own-sect-banner">本宗洞天</span>}
                </div>
                <div className="hero-doctrine-row">
                  <span className="doctrine-pill">{activeGate.doctrine}</span>
                  <em className="motto-text">“{activeGate.motto}”</em>
                </div>
                <p className="hero-desc">{activeGate.description}</p>
              </div>
            </div>

            <div className="hero-right">
              <div className="welcome-gift-card">
                <div className="gift-head">
                  <Gift size={14} />
                  <span>宗门知客回礼</span>
                </div>
                <strong>
                  {activeGate.welcome_gift} × {activeGate.welcome_gift_count}
                </strong>
                <small>正式拜山论道获接见后由知客长老奉送</small>
              </div>
            </div>
          </section>

          {/* Sub Navigation Tabs */}
          <div className="sect-sub-tabs" role="tablist" aria-label="山门事务分类">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'visit'}
              className={`sub-tab-btn ${activeTab === 'visit' ? 'active' : ''}`}
              onClick={() => setActiveTab('visit')}
            >
              <Handshake size={15} />
              <span>山门请益</span>
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'treasures'}
              className={`sub-tab-btn ${activeTab === 'treasures' ? 'active' : ''}`}
              onClick={() => setActiveTab('treasures')}
            >
              <Sparkles size={15} />
              <span>求丹借宝</span>
              <small className="tab-count">{activeGate.treasures.length}</small>
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'spar'}
              className={`sub-tab-btn ${activeTab === 'spar' ? 'active' : ''}`}
              onClick={() => setActiveTab('spar')}
            >
              <Swords size={15} />
              <span>擂台演武</span>
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === 'bounties'}
              className={`sub-tab-btn ${activeTab === 'bounties' ? 'active' : ''}`}
              onClick={() => setActiveTab('bounties')}
            >
              <ScrollText size={15} />
              <span>外务悬赏</span>
              <small className="tab-count">{activeGate.bounties.length}</small>
            </button>
          </div>

          {/* Tab 1: 山门请益 */}
          {activeTab === 'visit' && (
            <div className="sect-gate-tab-panel sect-visit-panel">
              <div className="visit-intro-card">
                <div className="intro-badge">
                  <Mountain size={20} />
                </div>
                <div className="intro-text">
                  <h4>叩谒【{activeGate.name}】山门知客关</h4>
                  <p>
                    递交拜山玉帖与礼敬灵石（消耗 {giftCost}{' '}
                    灵石），请求入山拜会护法长老，坐而论道、印证法门。
                  </p>
                </div>
              </div>

              <div className="visit-outcomes-grid">
                <div className="outcome-card success-outcome">
                  <div className="outcome-header">
                    <Sparkles size={16} />
                    <strong>知客接见 · 坐而论道</strong>
                  </div>
                  <ul>
                    <li>
                      获得修仙界声望 <strong>+8</strong> 点
                    </li>
                    <li>根据当前道境增长对应修为（推进一个月）</li>
                    <li>
                      获奉宗门专属见面礼：
                      <strong>
                        {activeGate.welcome_gift} × {activeGate.welcome_gift_count}
                      </strong>
                    </li>
                  </ul>
                  <small>依修士悟性、神识与修仙声望综合判定知客迎宾之礼遇。</small>
                </div>

                <div className="outcome-card regular-outcome">
                  <div className="outcome-header">
                    <Handshake size={16} />
                    <strong>守山奉还 · 礼貌辞行</strong>
                  </div>
                  <ul>
                    <li>
                      获得修仙界声望 <strong>+2</strong> 点
                    </li>
                    <li>知客弟子点拨指引，修为 <strong>+1</strong> 点</li>
                    <li>礼帖已纳，不退还礼金，但结下一面之缘</li>
                  </ul>
                  <small>虽未得高层长老接见，亦广结仙缘，增广见闻。</small>
                </div>
              </div>

              <div className="visit-action-row">
                {!canAffordVisit && (
                  <p className="visit-warning-text">
                    灵石不足：拜山递帖需备好 {giftCost} 灵石，当前仅有 {playerStones} 灵石。
                  </p>
                )}
                <button
                  type="button"
                  className="btn-primary-visit"
                  disabled={busy || readOnly || !canAffordVisit}
                  onClick={() => handleAction(activeGate.visit_action)}
                  title={
                    !canAffordVisit
                      ? `灵石不足（需 ${giftCost}）`
                      : `向${activeGate.name}递帖拜山（消耗 ${giftCost} 灵石）`
                  }
                >
                  <Handshake size={16} />
                  <span>
                    递帖拜谒 {activeGate.name}（消耗 {giftCost} 灵石）
                  </span>
                </button>
              </div>
            </div>
          )}

          {/* Tab 2: 求丹借宝 */}
          {activeTab === 'treasures' && (
            <div className="sect-gate-tab-panel sect-treasures-panel">
              <div className="panel-sub-header">
                <Sparkles size={16} />
                <div>
                  <h4>{activeGate.name} 藏宝案席</h4>
                  <p>凭修仙界声望与足额灵石，向山门求取本派秘藏丹药、灵材与镇派法宝。</p>
                </div>
              </div>

              <div className="treasures-grid">
                {activeGate.treasures.map((t) => {
                  const affordable =
                    playerStones >= t.cost_stones && playerReputation >= t.reputation_req
                  const canBuy = t.available && affordable
                  const reason =
                    t.disabled_reason ||
                    (playerStones < t.cost_stones
                      ? `灵石不足（需 ${t.cost_stones}）`
                      : playerReputation < t.reputation_req
                        ? `声望不足（需 ${t.reputation_req}）`
                        : '')

                  return (
                    <article key={t.id} className="treasure-card" data-available={canBuy}>
                      <header className="treasure-card-header">
                        <span className="category-tag">{t.category}</span>
                        <h5>
                          {t.name} <small>×{t.count}</small>
                        </h5>
                      </header>
                      <p className="treasure-summary">{t.summary}</p>
                      <div className="treasure-cost-row">
                        <span className="cost-stone">
                          <Coins size={13} />
                          {t.cost_stones} 灵石
                        </span>
                        <span className="req-rep">
                          <Award size={13} />
                          需声望 {t.reputation_req}
                        </span>
                      </div>
                      <button
                        type="button"
                        className="btn-acquire-treasure"
                        disabled={busy || readOnly || !canBuy}
                        title={canBuy ? `消耗 ${t.cost_stones} 灵石求取` : reason}
                        onClick={() => handleAction(t.action)}
                      >
                        {canBuy ? (
                          <>
                            <Sparkles size={14} />
                            <span>求取仙珍</span>
                          </>
                        ) : (
                          <span>{reason || '暂不可求'}</span>
                        )}
                      </button>
                    </article>
                  )
                })}
              </div>
            </div>
          )}

          {/* Tab 3: 擂台演武 */}
          {activeTab === 'spar' && (
            <div className="sect-gate-tab-panel sect-spar-panel">
              <div className="spar-hero-box">
                <div className="spar-icon-badge">
                  <Swords size={22} />
                </div>
                <div className="spar-text">
                  <h4>{activeGate.name} 演武道台</h4>
                  <p>
                    登临云海演武坪，与该门派入室同辈或亲传弟子点到为止切磋试剑。
                    胜者不仅能扬名四方，更可获得该门派奉上的丰厚灵石奖赏！
                  </p>
                </div>
              </div>

              <div className="spar-stats-grid">
                <div className="spar-metric-card">
                  <small>切磋胜算预估</small>
                  <strong className="chance-val">{activeGate.spar_chance}%</strong>
                  <span>根据自身大境界、小阶序、身法遁速与悟性综合推演</span>
                </div>
                <div className="spar-metric-card">
                  <small>胜者优渥犒赏</small>
                  <strong className="reward-val">灵石 150+ / 声望 +6</strong>
                  <span>根据自身境界浮动加成，境界愈高获赐愈丰</span>
                </div>
                <div className="spar-metric-card">
                  <small>惜败点拨馈赠</small>
                  <strong className="consolation-val">灵石 30 / 声望 +1</strong>
                  <span>同道切磋点到为止，不伤根本，亦获赠盘缠茶水</span>
                </div>
              </div>

              <div className="spar-action-row">
                <button
                  type="button"
                  className="btn-primary-spar"
                  disabled={busy || readOnly}
                  onClick={() => handleAction(activeGate.spar_action)}
                  title={`登临${activeGate.name}演武场进行同道切磋`}
                >
                  <Swords size={16} />
                  <span>登台切磋试剑（胜算 {activeGate.spar_chance}%）</span>
                </button>
              </div>
            </div>
          )}

          {/* Tab 4: 外务悬赏 */}
          {activeTab === 'bounties' && (
            <div className="sect-gate-tab-panel sect-bounties-panel">
              <div className="panel-sub-header">
                <ScrollText size={16} />
                <div>
                  <h4>{activeGate.name} 山门悬赏黄绢令</h4>
                  <p>
                    宗门长老面向九州同道发布的案卷委托，接取后即刻下山历练推进。任务越凶险，所获灵材与灵石愈加丰饶！
                  </p>
                </div>
              </div>

              <div className="bounties-grid">
                {activeGate.bounties.map((b) => {
                  const isDangerous = b.risk === '凶险'
                  const rewardItemsText = Object.entries(b.reward_items)
                    .map(([name, count]) => `${name}×${count}`)
                    .join('、')

                  return (
                    <article key={b.id} className="bounty-card" data-risk={b.risk}>
                      <header className="bounty-card-header">
                        <div className="bounty-title-col">
                          <span className={`risk-badge risk-${b.risk}`}>{b.risk}</span>
                          <h5>{b.title}</h5>
                        </div>
                        <div className="bounty-chance-badge">胜算 {b.chance}%</div>
                      </header>

                      <p className="bounty-summary">{b.summary}</p>

                      <div className="bounty-rewards-block">
                        <div className="reward-line">
                          <Coins size={13} />
                          <span>灵石 +{b.reward_stones}</span>
                          <span className="dot-sep">·</span>
                          <Award size={13} />
                          <span>声望 +{b.reward_reputation}</span>
                        </div>
                        {rewardItemsText && (
                          <div className="reward-items-line">
                            <Gift size={13} />
                            <span>战利丰厚：{rewardItemsText}</span>
                          </div>
                        )}
                      </div>

                      {isDangerous && (
                        <div className="bounty-danger-warning">
                          <ShieldAlert size={12} />
                          <span>凶险历练：若失手受挫可能轻微损伤气血与声望。</span>
                        </div>
                      )}

                      <button
                        type="button"
                        className="btn-take-bounty"
                        disabled={busy || readOnly}
                        onClick={() => handleAction(b.action)}
                        title={`接取${activeGate.name}委托【${b.title}】`}
                      >
                        <ScrollText size={14} />
                        <span>揭榜领受历练</span>
                      </button>
                    </article>
                  )
                })}
              </div>
            </div>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
