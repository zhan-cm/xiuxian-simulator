import * as Dialog from '@radix-ui/react-dialog'
import {
  ArrowRight,
  BookOpen,
  Coins,
  Compass,
  Flame,
  HeartHandshake,
  HelpCircle,
  Home,
  Landmark,
  Map,
  Mountain,
  Search,
  Sparkles,
  Swords,
  UsersRound,
  X,
} from 'lucide-react'
import { useMemo, useState } from 'react'
import type { GameState, PlayerState, Snapshot } from '../api/types'

export type GuideCategory = '全部' | '破境修为' | '资粮生财' | '功法神兵' | '人脉因缘' | '伤病寿元' | '洞天修行'

export interface GuideEntry {
  id: string
  category: Exclude<GuideCategory, '全部'>
  want: string
  location: string
  action: string
  targetAction: string
  buttonLabel: string
  iconName: 'breakthrough' | 'cultivate' | 'coins' | 'market' | 'travel' | 'sect' | 'art' | 'social' | 'heal' | 'cave'
  priority?: (player: PlayerState, state: GameState) => number
}

export const GUIDE_ENTRIES: GuideEntry[] = [
  // 1. 破境修为
  {
    id: 'breakthrough-major',
    category: '破境修为',
    want: '突破大境界（如炼气升筑基、筑基升结晶）',
    location: '【突破圣台】或【坊市·百宝阁】',
    action: '当修为达标后，在突破圣台选择人道、地道或天道路线破关；若缺少筑基丹等破关丹药或五行灵宝，可先前往坊市购买或洞府炼制。',
    targetAction: '突破',
    buttonLabel: '叩问突破',
    iconName: 'breakthrough',
    priority: (player) => (player.cultivation >= player.cultivation_required ? 100 : 20),
  },
  {
    id: 'cultivate-gather',
    category: '破境修为',
    want: '快速积蓄修为提升当前境界',
    location: '【洞府·清修静室】',
    action: '在洞府进行每月吐纳修炼，或使用「闭关三月」沉淀道行；亦可服用聚气丹等增进灵元丹药加速气海盈满。',
    targetAction: '洞府',
    buttonLabel: '前往洞府',
    iconName: 'cultivate',
    priority: (player) => (player.cultivation < player.cultivation_required ? 50 : 10),
  },
  {
    id: 'find-spirit-vein',
    category: '破境修为',
    want: '寻觅高阶灵脉加速吐纳效率',
    location: '【九州·名山福地】或【仙宗灵脉】',
    action: '前往九州名山大川或仙家宗门修炼灵脉，灵气浓郁之地吐纳获得的月度修为远高于外界荒野。',
    targetAction: '地图',
    buttonLabel: '游历名山',
    iconName: 'travel',
  },

  // 2. 资粮生财
  {
    id: 'earn-spirit-stones',
    category: '资粮生财',
    want: '赚取大笔灵石以备修行花销',
    location: '【坊市·百宝阁】或【九州·悬赏榜】',
    action: '将降妖获得的妖丹兽皮、采集的灵草矿石或闲置法宝在坊市出售；也可前往九州各地悬榜接取斩妖护送委托赚取赏金。',
    targetAction: '坊市',
    buttonLabel: '前往坊市',
    iconName: 'coins',
    priority: (player) => (player.spirit_stones < 50 ? 85 : 30),
  },
  {
    id: 'buy-pills-treasures',
    category: '资粮生财',
    want: '购买高阶丹药、护身法器与稀罕灵珍',
    location: '【坊市·百宝阁/拍卖会】',
    action: '在百宝阁选购破境灵丹、法器防具与炼丹药引；留意每年一度的仙家拍卖会，携带充足灵石与各方修士竞夺绝世异宝。',
    targetAction: '坊市',
    buttonLabel: '逛百宝阁',
    iconName: 'market',
  },
  {
    id: 'trade-across-regions',
    category: '资粮生财',
    want: '低买高卖行商赚取巨额差价',
    location: '【九州·行旅各地】',
    action: '在特产灵草产地低价收购，前往匮乏物资的大荒州郡高价倒卖；打听各域供需行情，行商四海富甲一方。',
    targetAction: '地图',
    buttonLabel: '游历行商',
    iconName: 'travel',
  },

  // 3. 功法神兵
  {
    id: 'learn-techniques',
    category: '功法神兵',
    want: '学习强力功法心法与杀伐神通',
    location: '【仙宗·藏经阁】或【九州·古仙遗迹】',
    action: '加入宗门后积攒宗门贡献，前往藏经阁换取本门镇派玄法；或者在九州探险中破解上古仙府禁制获取失传神通秘籍。',
    targetAction: '宗门',
    buttonLabel: '前往宗门',
    iconName: 'sect',
  },
  {
    id: 'nourish-artifacts',
    category: '功法神兵',
    want: '温养祭炼打造本命法宝',
    location: '【洞府·百炼器室】',
    action: '投入玄铁精金与妖兽精核祭炼法宝，提升法宝共鸣度与杀伤力，亦可打造强力飞剑与护身宝甲。',
    targetAction: '洞府',
    buttonLabel: '温养法宝',
    iconName: 'art',
  },
  {
    id: 'craft-pills',
    category: '功法神兵',
    want: '开炉亲手炼制保命与增功灵丹',
    location: '【洞府·九鼎丹房】',
    action: '配齐主药与辅药药材，根据丹方掌舵火候，亲手炼制聚气丹、筑基丹、回春丹，自给自足无需受坊市奸商盘剥。',
    targetAction: '洞府',
    buttonLabel: '开炉炼丹',
    iconName: 'cave',
  },

  // 4. 人脉因缘
  {
    id: 'seek-dao-companion',
    category: '人脉因缘',
    want: '结交生死知己或寻觅同道结为道侣',
    location: '【人物·因缘谱】',
    action: '拜访同道修士，投其所好赠送灵茶异宝，促膝交谈增进了解；好感达到80以上即可缔结道侣同修合道，共参长生。',
    targetAction: '情缘',
    buttonLabel: '查看人物',
    iconName: 'social',
  },
  {
    id: 'debate-dao',
    category: '人脉因缘',
    want: '与高人坐而论道获取天地感悟',
    location: '【人物·修士交互】',
    action: '与高境界前辈或同辈天骄坐而论道，通过心性思辨胜出可直接获得丰厚道悟与修为增长。',
    targetAction: '情缘',
    buttonLabel: '寻道友论道',
    iconName: 'social',
  },
  {
    id: 'mediate-disputes',
    category: '人脉因缘',
    want: '调解宗门恩怨或拉拢修士盟友',
    location: '【人物·众生缘网】',
    action: '介入修仙界各方势力的爱恨纠葛，通过调解、偏袒或威慑维护自身人脉网，获取长辈庇护与好友援助。',
    targetAction: '情缘',
    buttonLabel: '查看人脉网',
    iconName: 'social',
  },

  // 5. 伤病寿元
  {
    id: 'heal-wounds',
    category: '伤病寿元',
    want: '治疗重伤反噬与调养亏空气血',
    location: '【洞府·调息静室】或【乾坤袋】',
    action: '在洞府中使用「静养调息」恢复气血灵力，或随时在随身乾坤袋中服用回春丹，防止伤势恶化动摇道基。',
    targetAction: '洞府',
    buttonLabel: '静养调息',
    iconName: 'heal',
    priority: (player) => (player.health < player.health_max * 0.6 ? 95 : 10),
  },
  {
    id: 'extend-lifespan',
    category: '伤病寿元',
    want: '抵抗大限将至、逆天延年益寿',
    location: '【突破圣台】或【九州·神药秘境】',
    action: '大境界每突破一层（如炼气突破至筑基），天道赐寿直接翻倍；也可在九州禁地寻得长生仙草服下强延大限。',
    targetAction: '突破',
    buttonLabel: '叩问突破',
    iconName: 'breakthrough',
    priority: (player) => (player.age > player.lifespan * 0.75 ? 90 : 15),
  },

  // 6. 洞天修行
  {
    id: 'join-sect',
    category: '洞天修行',
    want: '拜入仙家名门求取师尊庇护',
    location: '【九州·仙山大派】',
    action: '前往仙门驻地参与收徒大典，凭借灵根悟性考核拜入宗门，每月领受宗门俸禄，享藏经阁与历练资源。',
    targetAction: '宗门',
    buttonLabel: '前往宗门',
    iconName: 'sect',
    priority: (player) => (!player.sect || player.sect === '散修' ? 70 : 10),
  },
  {
    id: 'explore-wilderness',
    category: '洞天修行',
    want: '外出游历寻访天地古修机缘',
    location: '【九州·大荒舆图】',
    action: '踏遍五域九州山川河流，探秘未知洞天，偶遇大能残魂传道或天降机缘奇遇。',
    targetAction: '地图',
    buttonLabel: '探索九州',
    iconName: 'travel',
  },
]

export function getSmartRecommendations(player: PlayerState, state: GameState): GuideEntry[] {
  return [...GUIDE_ENTRIES]
    .sort((a, b) => {
      const pA = a.priority ? a.priority(player, state) : 0
      const pB = b.priority ? b.priority(player, state) : 0
      return pB - pA
    })
    .slice(0, 3)
}

function getIcon(name: GuideEntry['iconName']) {
  switch (name) {
    case 'breakthrough':
      return <Flame size={18} />
    case 'cultivate':
      return <Sparkles size={18} />
    case 'coins':
      return <Coins size={18} />
    case 'market':
      return <Landmark size={18} />
    case 'travel':
      return <Map size={18} />
    case 'sect':
      return <Mountain size={18} />
    case 'art':
      return <Swords size={18} />
    case 'social':
      return <UsersRound size={18} />
    case 'heal':
      return <HeartHandshake size={18} />
    case 'cave':
      return <Home size={18} />
  }
}

interface CultivationGuideDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onNavigate: (action: string) => void
  player: PlayerState
  state: GameState
}

export function CultivationGuideDialog({
  open,
  onOpenChange,
  onNavigate,
  player,
  state,
}: CultivationGuideDialogProps) {
  const [selectedCategory, setSelectedCategory] = useState<GuideCategory>('全部')
  const [keyword, setKeyword] = useState('')

  const categories: GuideCategory[] = ['全部', '破境修为', '资粮生财', '功法神兵', '人脉因缘', '伤病寿元', '洞天修行']

  const filteredEntries = useMemo(() => {
    return GUIDE_ENTRIES.filter((entry) => {
      const matchCategory = selectedCategory === '全部' || entry.category === selectedCategory
      const query = keyword.trim().toLowerCase()
      const matchKeyword =
        !query ||
        entry.want.toLowerCase().includes(query) ||
        entry.location.toLowerCase().includes(query) ||
        entry.action.toLowerCase().includes(query)
      return matchCategory && matchKeyword
    })
  }, [selectedCategory, keyword])

  const recommendations = useMemo(() => getSmartRecommendations(player, state), [player, state])

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog cultivation-guide-dialog">
          <header className="guide-dialog-header">
            <div>
              <p>修仙指津 · 行止向导</p>
              <Dialog.Title>如果想要……你可以去哪里干什么？</Dialog.Title>
              <Dialog.Description>
                凡尘入道，百废待兴。天地万物皆有其法，查阅下表速解仙途疑难困惑。
              </Dialog.Description>
            </div>
            <Dialog.Close aria-label="关闭指南">
              <X size={20} />
            </Dialog.Close>
          </header>

          {/* 当下智能指引条 */}
          {recommendations.length > 0 && (
            <div className="guide-smart-alert">
              <div className="alert-heading">
                <Compass size={15} />
                <span>天机推演 · 当前急务指引</span>
              </div>
              <div className="smart-chips-grid">
                {recommendations.map((rec) => (
                  <button
                    key={rec.id}
                    type="button"
                    className="smart-chip"
                    onClick={() => {
                      onOpenChange(false)
                      onNavigate(rec.targetAction)
                    }}
                  >
                    <span>若想{rec.want.slice(0, 10)}…</span>
                    <strong>去{rec.location.replace(/[【】]/g, '')}</strong>
                    <ArrowRight size={13} />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 分类标签与搜索框 */}
          <div className="guide-controls">
            <div className="guide-categories-bar">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  className="guide-cat-btn"
                  data-active={selectedCategory === cat || undefined}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="guide-search-box">
              <Search size={15} />
              <input
                type="text"
                placeholder="搜索你想做的事情（如：灵石、突破、筑基、功法、道侣、疗伤）..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
              />
              {keyword && (
                <button type="button" onClick={() => setKeyword('')} aria-label="清空">
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          {/* 指南卡片列表 */}
          <div className="guide-cards-scroll">
            {filteredEntries.length === 0 ? (
              <div className="guide-empty">
                <HelpCircle size={32} />
                <p>未能寻得与“{keyword}”匹配的天机指引，可更换关键词或切换上方类别查阅。</p>
              </div>
            ) : (
              <div className="guide-cards-grid">
                {filteredEntries.map((entry) => (
                  <article key={entry.id} className="guide-card" data-cat={entry.category}>
                    <div className="guide-card-icon">{getIcon(entry.iconName)}</div>
                    <div className="guide-card-main">
                      <div className="guide-row-want">
                        <span className="guide-badge want-badge">如果想要</span>
                        <strong>{entry.want}</strong>
                      </div>

                      <div className="guide-row-loc">
                        <span className="guide-badge loc-badge">你可以去</span>
                        <strong>{entry.location}</strong>
                      </div>

                      <div className="guide-row-act">
                        <span className="guide-badge act-badge">干什么</span>
                        <p>{entry.action}</p>
                      </div>
                    </div>

                    <div className="guide-card-action">
                      <button
                        type="button"
                        className="guide-jump-btn"
                        onClick={() => {
                          onOpenChange(false)
                          onNavigate(entry.targetAction)
                        }}
                      >
                        <span>{entry.buttonLabel}</span>
                        <ArrowRight size={13} />
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

interface CultivationGuideCardProps {
  snapshot: Snapshot
  onNavigate: (action: string) => void
  onOpenFullGuide: () => void
}

export function CultivationGuideCard({ snapshot, onNavigate, onOpenFullGuide }: CultivationGuideCardProps) {
  const { state } = snapshot
  const { player } = state
  const recommendations = useMemo(() => getSmartRecommendations(player, state), [player, state])

  return (
    <section className="chronicle-card cultivation-guide-card" aria-label="仙途指津">
      <header className="guide-card-header">
        <div className="guide-card-title">
          <Compass size={17} />
          <strong>仙途指津 · 行止向导</strong>
          <small>如果想要怎么，你可以去哪里干什么</small>
        </div>
        <button type="button" className="open-full-guide-btn" onClick={onOpenFullGuide}>
          <BookOpen size={13} />
          <span>查阅天机全书</span>
        </button>
      </header>

      <div className="guide-card-items">
        {recommendations.map((rec) => (
          <div key={rec.id} className="guide-compact-item">
            <div className="guide-item-body">
              <div className="compact-title-row">
                <span className="badge-want">若想</span>
                <strong>{rec.want}</strong>
              </div>
              <p>
                <span>可前往 </span>
                <em>{rec.location}</em>
                <span>：{rec.action}</span>
              </p>
            </div>
            <button
              type="button"
              className="compact-jump-btn"
              onClick={() => onNavigate(rec.targetAction)}
            >
              <span>{rec.buttonLabel}</span>
              <ArrowRight size={12} />
            </button>
          </div>
        ))}
      </div>
    </section>
  )
}
