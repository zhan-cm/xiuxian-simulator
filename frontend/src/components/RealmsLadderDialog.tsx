import * as Dialog from '@radix-ui/react-dialog'
import {
  CheckCircle2,
  Clock,
  Compass,
  Flame,
  Lock,
  Mountain,
  ShieldAlert,
  Sparkles,
  X,
} from 'lucide-react'
import { useEffect, useMemo, useRef } from 'react'
import type { PlayerState } from '../api/types'

export interface RealmMeta {
  index: number
  name: string
  numeral: string
  title: string
  lifespan: number
  quote: string
  essence: string
  features: string[]
  breakthroughPill: string
  tribulation: string
  colorTone: string
}

export const ALL_REALMS: RealmMeta[] = [
  {
    index: 0,
    name: '炼气',
    numeral: '壹',
    title: '凡躯初省 · 引气入体',
    lifespan: 100,
    quote: '凡尘一念断俗缘，初引清气洗丹田。',
    essence: '引天地游离灵气淬炼肉身，开辟丹田气海。此时灵气呈气态流动，身轻体健，延年百载，始脱凡人范畴。',
    features: [
      '肉身轻灵，百病不生，五感较凡人敏锐数倍',
      '灵气呈白雾游离状，初通低阶法术与御风行步',
      '寿元天限为百岁，未脱凡夫生老病死大关',
    ],
    breakthroughPill: '筑基丹',
    tribulation: '筑基三大天关：人道平稳、地道纳灵、天道极道',
    colorTone: 'cyan',
  },
  {
    index: 1,
    name: '筑基',
    numeral: '贰',
    title: '铸就仙基 · 灵液成池',
    lifespan: 200,
    quote: '灵池玉液铸仙基，从此长生第一阶。',
    essence: '周天气态灵雾化作液态灵池，丹田拓宽十倍。肉身洗髓伐毛，道骨天成，正式脱离肉眼凡胎，可御器飞行。',
    features: [
      '气态转液态，体内诞生第一汪清莹灵池',
      '真气自成循环，可御剑凌空，神识可外放探物',
      '寿元天限增至二百载，享两世凡人生死光阴',
    ],
    breakthroughPill: '凝晶丹',
    tribulation: '凝液化晶之关，需稳固道基心神',
    colorTone: 'jade',
  },
  {
    index: 2,
    name: '结晶',
    numeral: '叁',
    title: '凝水成晶 · 道体纯阳',
    lifespan: 300,
    quote: '九转灵液凝玉晶，神游千仞气自清。',
    essence: '灵池真液进一步凝结固化，凝结成璀璨灵晶。法力强度与坚韧度暴涨数倍，经脉如玉石晶莹，威压初显。',
    features: [
      '灵液凝为实质棱晶，法力精纯密度达凡阶顶峰',
      '道体抗性大幅增长，能抵御寻常法术刀兵之伤',
      '寿元天限达三百载，一方仙门中坚柱石',
    ],
    breakthroughPill: '结丹灵药',
    tribulation: '熔晶抱丹之劫，心魔幻境初生考验',
    colorTone: 'crystal',
  },
  {
    index: 3,
    name: '金丹',
    numeral: '肆',
    title: '无瑕金丹 · 我命由我',
    lifespan: 500,
    quote: '一粒金丹吞入腹，始知我命由我不由天。',
    essence: '熔铸本命浑圆无瑕金丹，诞生纯阳三昧真火。法力生生不息，一举一动皆蕴大道法则威能，被尊称为一方宗师、得道真人。',
    features: [
      '丹田孕育浑圆金丹，诞生本命真火，焚尽妖邪',
      '神识暴涨十倍，可隔空御敌斩杀千里外首级',
      '寿元大限达五百岁，可称老祖真人，开辟仙家世家',
    ],
    breakthroughPill: '具灵丹',
    tribulation: '风火雷三灾初劫，天道考验命格坚贞',
    colorTone: 'gold',
  },
  {
    index: 4,
    name: '具灵',
    numeral: '伍',
    title: '金丹具灵 · 真如显相',
    lifespan: 800,
    quote: '丹生玄相通幽冥，万化归真性自灵。',
    essence: '金丹内部孕育真灵玄相，道心灵台通明。法宝与本体彻底通灵相合，神识化丝入微，可窥测天地气机走向。',
    features: [
      '金丹内部孕育真灵，自身法相雏形初显',
      '可洞察他人灵根因果，法术威能兼备灵性',
      '寿元天限达八百岁，俯瞰凡俗数朝兴衰鼎革',
    ],
    breakthroughPill: '结婴丹',
    tribulation: '破丹化婴之大天劫，生死只在雷光一念',
    colorTone: 'amber',
  },
  {
    index: 5,
    name: '元婴',
    numeral: '陆',
    title: '破丹成婴 · 元神不灭',
    lifespan: 1200,
    quote: '碎丹出婴乘风去，肉身虽陨神永存。',
    essence: '破碎金丹孕化第二本命元婴！修士从此拥有双重本命，肉身若毁，元婴亦可瞬移夺舍重生。挥手翻江倒海，镇压一域气运。',
    features: [
      '第二元神元婴独立成型，肉身陨而真魂不灭',
      '瞬移撕裂虚空，举手投足移山填海、号令风雷',
      '寿元天限跨入千载（一千二百岁），名震大千世界',
    ],
    breakthroughPill: '化神丹',
    tribulation: '九九天劫与六道心魔劫，元神出窍试炼',
    colorTone: 'purple',
  },
  {
    index: 6,
    name: '化神',
    numeral: '柒',
    title: '返虚化神 · 领域初辟',
    lifespan: 2000,
    quote: '神念通天同造化，万象皆由一念生。',
    essence: '元婴与肉身彻底熔炼归一，化作天地神念法象。自身神识拓为领域空间，踏入化神者如神明临尘，一念之间裁决众生。',
    features: [
      '元神化为领域法身，自身所立之处即为绝对法则领域',
      '调动方圆千里天地元气，凡尘修士望之如睹神明',
      '寿元天限突破两千载，坐镇万古圣地为太上至尊',
    ],
    breakthroughPill: '悟道丹',
    tribulation: '天人五衰之首衰，道心与天道秩序叩问',
    colorTone: 'crimson',
  },
  {
    index: 7,
    name: '悟道',
    numeral: '捌',
    title: '参悟三千 · 言出法随',
    lifespan: 5000,
    quote: '道参造化乾坤外，法在阴阳造化间。',
    essence: '脱离天地灵气粗浅运用，直接执掌一条大道真意（如剑道、阴阳、生死、时空）。言出法随，改写天地物理规则。',
    features: [
      '领悟自身专属本源道则，一言一行即是修仙界天律',
      '掌控空间生灭，甚至可推演预卜未来因果命数',
      '寿元天限达五千载，横跨上古与当世，寿与山齐',
    ],
    breakthroughPill: '羽化丹',
    tribulation: '纯阳金雷大天劫，褪换凡尘血肉骨骼',
    colorTone: 'dao',
  },
  {
    index: 8,
    name: '羽化',
    numeral: '玖',
    title: '褪壳登真 · 半步天仙',
    lifespan: 10000,
    quote: '万劫不磨纯阳体，羽化登天只待风。',
    essence: '肉身骨血全部羽化为纯阳无垢仙体，不染半点凡尘因果。已半步踏入仙界大门，只需经受最后九天飞升紫霄雷劫。',
    features: [
      '肉身转化为仙躯玉骨，凡间一切浊物不可近身',
      '引动仙界接引仙光，仙家气象笼罩万里长空',
      '寿元大限达万载光阴（一万岁），人间活神仙',
    ],
    breakthroughPill: '登仙丹',
    tribulation: '九九紫霄天劫与天道升仙封神金榜',
    colorTone: 'celestial',
  },
  {
    index: 9,
    name: '登仙',
    numeral: '拾',
    title: '证道真仙 · 与天同寿',
    lifespan: 50000,
    quote: '踏碎虚空登仙阙，跳出三界五行中。',
    essence: '渡尽万劫，肉身元神尽皆成仙，证得大罗无极真仙果位！跳出三界外，不在五行中，与天地日月同寿同庚，享无上逍遥大自在。',
    features: [
      '证得不朽仙格，跳出六道轮回生死薄',
      '独辟大千仙界洞天，掌开天辟地造化伟力',
      '寿元天限达五万载直至与天同寿，永恒之道终得圆满',
    ],
    breakthroughPill: '万古道果·大道本源',
    tribulation: '无上大道圆满，再无凡俗雷劫加身',
    colorTone: 'immortal',
  },
]

interface RealmsLadderDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  player: PlayerState
  onGoBreakthrough?: () => void
}

export function RealmsLadderDialog({
  open,
  onOpenChange,
  player,
  onGoBreakthrough,
}: RealmsLadderDialogProps) {
  const currentRef = useRef<HTMLDivElement>(null)

  const [baseRealm = '炼气'] = (player.realm || '').split('·')
  const currentRealmIndex = useMemo(() => {
    const found = ALL_REALMS.findIndex((r) => r.name === baseRealm)
    return found >= 0 ? found : 0
  }, [baseRealm])

  // 排序：高的境界在上面（登仙在最顶），低的境界在下面（炼气在最底）
  const ascendingLadder = useMemo(() => {
    return [...ALL_REALMS].reverse()
  }, [])

  // 打开时自动平滑滚动到当前所处的境界位置
  useEffect(() => {
    if (open) {
      const timer = window.setTimeout(() => {
        currentRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 150)
      return () => window.clearTimeout(timer)
    }
  }, [open])

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="dialog-overlay" />
        <Dialog.Content className="character-dialog realms-ladder-dialog">
          <header className="ladder-dialog-header">
            <div className="ladder-header-title">
              <span className="ladder-crest"><Mountain size={20} /></span>
              <div>
                <p>玄黄大千 · 登仙宝鉴</p>
                <Dialog.Title>仙道十重天 · 境界通天图</Dialog.Title>
                <Dialog.Description>
                  自凡尘引气，至登仙证道。拾级而上，每跨一天堑，寿元翻倍，神通大成。
                </Dialog.Description>
              </div>
            </div>
            <div className="ladder-header-actions">
              <button
                type="button"
                className="locate-current-btn"
                onClick={() => currentRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })}
                title="快速定位到我的境界"
              >
                <Compass size={14} />
                <span>定位道阶</span>
              </button>
              <Dialog.Close aria-label="关闭">
                <X size={20} />
              </Dialog.Close>
            </div>
          </header>

          {/* 通天仙梯主画布：高境界在上，低境界在下 */}
          <div className="ladder-scroll-viewport">
            <div className="ladder-sky-aura-top">
              <Sparkles size={16} />
              <span>南天仙阙 · 证道之巅</span>
            </div>

            <div className="ladder-spine-container">
              {/* 贯穿始终的通天灵脉中轴线 */}
              <div className="celestial-meridian" aria-hidden="true" />

              {ascendingLadder.map((realm) => {
                const isCurrent = realm.index === currentRealmIndex
                const isPassed = realm.index < currentRealmIndex

                return (
                  <div
                    key={realm.name}
                    ref={isCurrent ? currentRef : undefined}
                    className="realm-step-card"
                    data-status={isCurrent ? 'current' : isPassed ? 'passed' : 'future'}
                    data-tone={realm.colorTone}
                  >
                    {/* 左侧道阶数字印章与状态光环 */}
                    <div className="step-node-col">
                      <div className="step-seal">
                        <span className="step-numeral">{realm.numeral}</span>
                        <strong className="step-realm-name">{realm.name}</strong>
                      </div>
                      <div className="step-indicator-tag">
                        {isCurrent ? (
                          <span className="tag-current">
                            <Sparkles size={11} />
                            <b>今止于此</b>
                          </span>
                        ) : isPassed ? (
                          <span className="tag-passed">
                            <CheckCircle2 size={11} />
                            <b>道基已固</b>
                          </span>
                        ) : (
                          <span className="tag-future">
                            <Lock size={10} />
                            <b>前路天关</b>
                          </span>
                        )}
                      </div>
                    </div>

                    {/* 右侧境界详述卷轴 */}
                    <div className="step-content-card">
                      <header className="step-header">
                        <div className="step-header-left">
                          <h3 className="step-title">
                            <span>{realm.name}境</span>
                            <small>· {realm.title}</small>
                          </h3>
                          <p className="step-quote">“{realm.quote}”</p>
                        </div>
                        <div className="step-lifespan-badge">
                          <Clock size={13} />
                          <span>天年寿元 <strong>{realm.lifespan.toLocaleString()}</strong> 载</span>
                        </div>
                      </header>

                      <div className="step-body">
                        {/* 质变核心要义 */}
                        <div className="step-essence">
                          <span className="essence-label">【质变要义】</span>
                          <p>{realm.essence}</p>
                        </div>

                        {/* 三大关键特征点 */}
                        <div className="step-features-grid">
                          {realm.features.map((feat, idx) => (
                            <div key={idx} className="feat-chip">
                              <span className="feat-dot" />
                              <span>{feat}</span>
                            </div>
                          ))}
                        </div>

                        {/* 破关丹药与天劫考量 */}
                        <footer className="step-footer">
                          <div className="step-requirement">
                            <Flame size={13} />
                            <span>破境通关丹药：<strong>{realm.breakthroughPill}</strong></span>
                          </div>
                          <div className="step-tribulation">
                            <ShieldAlert size={13} />
                            <span>劫数考量：<small>{realm.tribulation}</small></span>
                          </div>
                        </footer>

                        {/* 如果是当前境界，展示温馨指引和一键叩关 */}
                        {isCurrent && (
                          <div className="current-realm-action-bar">
                            <div className="current-status-copy">
                              <Sparkles size={14} />
                              <span>
                                你当前正驻足于【<strong>{player.realm}</strong>】，气海修为{' '}
                                <b>{player.cultivation}</b> / {player.cultivation_required}
                              </span>
                            </div>
                            {onGoBreakthrough && (
                              <button
                                type="button"
                                className="ladder-breakthrough-btn"
                                onClick={() => {
                                  onOpenChange(false)
                                  onGoBreakthrough()
                                }}
                              >
                                <Flame size={14} />
                                <span>叩问大境界突破</span>
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="ladder-sky-aura-bottom">
              <Mountain size={16} />
              <span>凡尘俗世 · 万道肇始</span>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
