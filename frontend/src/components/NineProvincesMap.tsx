
import React, { useState, useMemo } from 'react'
import {
  Flame,
  Mountain,
  Snowflake,
  Sun,
  Castle,
  Wind,
  Zap,
  Waves,
  Maximize2,
  Minimize2,
} from 'lucide-react'
import mapBg from '../assets/jiuzhou_ancient_map.jpg'

export interface RegionAtlasItem {
  key: string
  name: string
  current?: boolean
  visited?: boolean
  accessible?: boolean
  danger?: number
  danger_label?: string
  requirement_label?: string
  description?: string
  months?: number
  specialties?: string[]
  demands?: string[]
  rank?: string
  reputation?: number
  locked_reason?: string
  action?: string
  has_event?: boolean
  event_title?: string
  event_pending?: boolean
  tone?: string
  sealed?: boolean
  [key: string]: unknown
}

interface NineProvincesMapProps {
  items: RegionAtlasItem[]
  selectedKey: string
  onSelect: (key: string) => void
  panoramic?: boolean
  onTogglePanoramic?: () => void
}

interface ProvinceGeom {
  key: string
  path: string
  sealX: number
  sealY: number
  labelX: number
  labelY: number
  badgeChar: string
  terrainTitle: string
  terrainType: string
  icon: React.ComponentType<{ size?: number; className?: string }>
  themeColor: string
}

/**
 * 太古四大禁绝封印外域（补齐神州九宫九域格局）
 */
export const OUTER_SEALED_PROVINCES: Record<string, RegionAtlasItem> = {
  雷州: {
    key: '雷州',
    name: '雷州 · 雷泽',
    current: false,
    visited: false,
    accessible: false,
    danger: 85,
    danger_label: '化神禁域',
    requirement_label: '化神境',
    description: '上古九霄雷泽所在，漫天紫霄神雷终年不绝。相传太古雷鹏在此涅槃，雷灵晶矿遍布深渊，非化神道躯不可硬抗罡风神雷。',
    months: 6,
    specialties: ['紫霄雷竹', '九天雷劫木', '辟邪神雷晶'],
    demands: ['避雷神符', '避劫古丹', '定风珠'],
    rank: '太古封印',
    reputation: 0,
    locked_reason: '太古雷劫大禁封印 · 需至化神境方可破禁横渡',
    tone: 'peril',
    sealed: true,
  },
  幽州: {
    key: '幽州',
    name: '幽州 · 九幽',
    current: false,
    visited: false,
    accessible: false,
    danger: 92,
    danger_label: '九幽极凶',
    requirement_label: '化神境',
    description: '连通冥河忘川之幽渊绝地，终年被太阴冥煞笼罩。古来唯有修习生死轮回大道的古能曾在此筑下幽冥道宫，寻常修士触之魂飞魄散。',
    months: 7,
    specialties: ['忘川彼岸花', '玄冥重水', '黄泉幽魄石'],
    demands: ['纯阳仙丹', '九转还魂草', '离火神符'],
    rank: '冥海天堑',
    reputation: 0,
    locked_reason: '幽冥黄泉大阵未破 · 需修至化神以上领悟生死法则',
    tone: 'peril',
    sealed: true,
  },
  云州: {
    key: '云州',
    name: '云州 · 云梦',
    current: false,
    visited: false,
    accessible: false,
    danger: 75,
    danger_label: '幻泽秘境',
    requirement_label: '元婴境',
    description: '八百里云梦大泽，蜃气横生，虚实莫辨。内藏上古真灵浮生古境，稍有不慎便会陷入百世轮回幻象之中，道心不固者终身难出。',
    months: 5,
    specialties: ['太虚梦蝶卵', '千幻云蜃珠', '雾隐仙萝'],
    demands: ['破妄清目丹', '定魂神香', '太清法剑'],
    rank: '幻障难通',
    reputation: 0,
    locked_reason: '太虚蜃气封天锁地 · 需至元婴破妄或持定海令入内',
    tone: 'warning',
    sealed: true,
  },
  瀛洲: {
    key: '瀛洲',
    name: '瀛洲 · 蓬莱',
    current: false,
    visited: false,
    accessible: false,
    danger: 80,
    danger_label: '海外仙墟',
    requirement_label: '化神境',
    description: '极东无尽汪洋之中的海上仙山，与蓬莱、方丈齐名。仙雾飘渺，神兽翱翔，古仙人曾于此留存不死药与飞升法门，非有仙缘大机缘者难寻其踪。',
    months: 8,
    specialties: ['不死仙芝', '九品碧海珊瑚', '乘鸾仙羽'],
    demands: ['跨海仙舟', '万载灵乳', '避水玄珠'],
    rank: '仙迹渺茫',
    reputation: 0,
    locked_reason: '天海无尽迷仙阵阻隔 · 需至化神境御风凌虚方见其形',
    tone: 'primary',
    sealed: true,
  },
}

/**
 * 神州九宫九域 2D 几何版图定义 (1000 x 800 viewBox)
 * 遵循天然山川水系（通天古江、天脊山脉、流沙古界、云梦大泽、沧海群岛）天然地界划分，
 * 彻底消除「＃」字井字正交网格，实现犬牙交错的大陆板块与名山大川格局。
 */
const PROVINCE_GEOMETRIES: Record<string, ProvinceGeom> = {
  北原: {
    key: '北原',
    path: 'M 310,60 C 375,25 440,15 500,15 C 560,15 625,25 690,60 C 720,110 710,180 670,235 C 600,255 530,240 470,250 C 410,245 350,255 330,235 C 290,180 280,110 310,60 Z',
    sealX: 486,
    sealY: 70,
    labelX: 500,
    labelY: 125,
    badgeChar: '北',
    terrainTitle: '极北寒渊 · 万载玄冰',
    terrainType: '暴雪冰川 · 幽冥极光',
    icon: Snowflake,
    themeColor: '#1565c0',
  },
  雷州: {
    key: '雷州',
    path: 'M 25,60 C 70,25 150,20 230,20 C 275,25 295,45 310,60 C 280,110 290,180 330,235 C 270,245 200,240 140,245 C 80,245 35,190 20,130 C 15,100 20,80 25,60 Z',
    sealX: 166,
    sealY: 75,
    labelX: 180,
    labelY: 128,
    badgeChar: '雷',
    terrainTitle: '九天雷泽 · 罡风神雷',
    terrainType: '紫霄雷池 · 太古禁绝',
    icon: Zap,
    themeColor: '#7b1fa2',
  },
  幽州: {
    key: '幽州',
    path: 'M 690,60 C 705,45 725,25 770,20 C 850,20 930,25 975,60 C 985,100 970,170 940,225 C 870,245 800,240 740,245 C 700,245 680,240 670,235 C 710,180 720,110 690,60 Z',
    sealX: 806,
    sealY: 75,
    labelX: 820,
    labelY: 128,
    badgeChar: '幽',
    terrainTitle: '幽冥极境 · 忘川黄泉',
    terrainType: '九幽冥煞 · 轮回天堑',
    icon: Castle,
    themeColor: '#37474f',
  },
  西漠: {
    key: '西漠',
    path: 'M 25,265 C 75,255 140,255 210,260 C 270,265 315,255 335,265 C 365,335 375,415 355,495 C 315,505 270,515 200,520 C 130,520 60,515 20,490 C 15,420 15,340 25,265 Z',
    sealX: 166,
    sealY: 335,
    labelX: 180,
    labelY: 390,
    badgeChar: '西',
    terrainTitle: '西垂流沙 · 瀚海鸣沙',
    terrainType: '大漠古道 · 佛窟遗迹',
    icon: Sun,
    themeColor: '#b58434',
  },
  中州: {
    key: '中州',
    path: 'M 335,265 C 375,255 425,250 500,255 C 575,250 625,255 665,265 C 685,335 675,415 655,495 C 615,510 565,515 500,510 C 435,515 385,510 355,495 C 375,415 365,335 335,265 Z',
    sealX: 486,
    sealY: 335,
    labelX: 500,
    labelY: 390,
    badgeChar: '中',
    terrainTitle: '中土天阙 · 仙宫浮云',
    terrainType: '昆仑天柱 · 浮空金阙',
    icon: Castle,
    themeColor: '#b8860b',
  },
  东洲: {
    key: '东洲',
    path: 'M 665,265 C 705,255 775,255 835,260 C 895,265 940,255 975,265 C 985,340 985,425 975,490 C 935,515 865,520 800,520 C 730,515 685,505 655,495 C 675,415 685,335 665,265 Z',
    sealX: 806,
    sealY: 335,
    labelX: 820,
    labelY: 390,
    badgeChar: '东',
    terrainTitle: '东海青岳 · 碧峰叠翠',
    terrainType: '千峰秀水 · 仙雾流泉',
    icon: Mountain,
    themeColor: '#2e7d32',
  },
  云州: {
    key: '云州',
    path: 'M 20,515 C 65,525 130,525 200,525 C 270,520 320,510 350,520 C 355,595 345,670 330,735 C 270,760 200,775 140,775 C 80,775 40,750 25,715 C 15,660 15,590 20,515 Z',
    sealX: 166,
    sealY: 595,
    labelX: 180,
    labelY: 650,
    badgeChar: '云',
    terrainTitle: '云梦古泽 · 迷障幻蜃',
    terrainType: '太虚蜃气 · 浮生幻境',
    icon: Wind,
    themeColor: '#00838f',
  },
  南疆: {
    key: '南疆',
    path: 'M 350,520 C 385,510 435,515 500,510 C 565,515 615,510 650,520 C 655,595 645,670 635,735 C 585,760 545,775 500,775 C 455,775 415,760 365,735 C 345,670 355,595 350,520 Z',
    sealX: 486,
    sealY: 595,
    labelX: 500,
    labelY: 650,
    badgeChar: '南',
    terrainTitle: '南荒赤炎 · 十万大山',
    terrainType: '地火熔脉 · 妖氛凶谷',
    icon: Flame,
    themeColor: '#c62828',
  },
  瀛洲: {
    key: '瀛洲',
    path: 'M 650,520 C 685,510 735,520 800,525 C 870,525 935,525 980,515 C 985,590 985,660 975,715 C 960,750 920,775 860,775 C 800,775 730,760 670,735 C 645,670 655,595 650,520 Z',
    sealX: 806,
    sealY: 595,
    labelX: 820,
    labelY: 650,
    badgeChar: '瀛',
    terrainTitle: '沧海瀛洲 · 蓬莱仙阁',
    terrainType: '东海仙山 · 乘鸾踏浪',
    icon: Waves,
    themeColor: '#00695c',
  },
}

export function NineProvincesMap({
  items,
  selectedKey,
  onSelect,
  panoramic = false,
  onTogglePanoramic,
}: NineProvincesMapProps) {
  const [hoveredKey, setHoveredKey] = useState<string | null>(null)

  // 补齐神州九域：如传入的项目少于九域，自动合入外域封印四方
  const allItems = useMemo(() => {
    const merged = [...items]
    const existingKeys = new Set(items.map((it) => it.key))
    for (const [key, outerItem] of Object.entries(OUTER_SEALED_PROVINCES)) {
      if (!existingKeys.has(key)) {
        merged.push(outerItem)
      }
    }
    return merged
  }, [items])

  // 排序：让当前悬浮或选中的地域绘制在最上层，确保浮动阴影与边缘不被邻域遮挡
  const sortedItems = useMemo(() => {
    return [...allItems].sort((a, b) => {
      const aKey = String(a.key)
      const bKey = String(b.key)
      const aActive = aKey === hoveredKey || selectedKey === aKey
      const bActive = bKey === hoveredKey || selectedKey === bKey
      if (aActive && !bActive) return 1
      if (!aActive && bActive) return -1
      return 0
    })
  }, [allItems, hoveredKey, selectedKey])

  return (
    <nav
      className="region-atlas-map nine-provinces-2d-canvas"
      aria-label="五域卷轴舆图"
      data-panoramic={panoramic || undefined}
    >
      {/* 展开全景 / 收拢全景切换按钮 */}
      {onTogglePanoramic && (
        <button
          type="button"
          className="map-panoramic-btn"
          onClick={onTogglePanoramic}
          aria-label={panoramic ? '收拢舆图' : '展开全景'}
          title={panoramic ? '收拢舆图' : '全景宏图'}
        >
          {panoramic ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
          <span>{panoramic ? '收拢舆图' : '全景宏图'}</span>
        </button>
      )}

      {/* 1. 2D 水墨全景交互 SVG 画卷 */}
      <svg
        className="map-topography-svg"
        viewBox="0 0 1000 800"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          {/* 金光灵气滤镜 */}
          <filter id="goldGlow" x="-25%" y="-25%" width="150%" height="150%">
            <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="#d4a34b" floodOpacity="0.75" />
          </filter>
          <filter id="activeGlow" x="-25%" y="-25%" width="150%" height="150%">
            <feDropShadow dx="0" dy="0" stdDeviation="8" floodColor="#ba8d3c" floodOpacity="0.9" />
          </filter>
          <filter id="inkShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="12" stdDeviation="10" floodColor="#2c1d10" floodOpacity="0.38" />
          </filter>
          <radialGradient id="mapVignette" cx="50%" cy="50%" r="62%">
            <stop offset="60%" stopColor="transparent" />
            <stop offset="100%" stopColor="#2c1f10" stopOpacity="0.4" />
          </radialGradient>

          {/* 各州领地 ClipPath 遮罩 */}
          {Object.entries(PROVINCE_GEOMETRIES).map(([k, geom]) => (
            <clipPath id={`clip-${k}`} key={`clip-${k}`}>
              <path d={geom.path} />
            </clipPath>
          ))}
        </defs>

        {/* 底层卷轴素雅暗纹底图（静止不动，当上方州板块浮起时衬托深度） */}
        <image
          href={mapBg}
          x="0"
          y="0"
          width="1000"
          height="800"
          preserveAspectRatio="xMidYMid slice"
          opacity="0.55"
          filter="contrast(0.9) brightness(0.95)"
        />

        {/* 古卷边缘暗角 */}
        <rect x="0" y="0" width="1000" height="800" fill="url(#mapVignette)" pointerEvents="none" />

        {/* 天然山川大水系与地界脉络（彻底消除 ＃ 字井字网格，以大江与龙脉为天然地界） */}
        <g className="natural-boundaries-layer" pointerEvents="none">
          {/* 通天古江大水系（天水自然界）：自西北雪岭曲折绕昆仑入东海 */}
          <path
            d="M 310,60 C 330,130 310,190 335,265 C 380,250 440,245 500,255 C 570,245 630,250 665,265 C 685,340 670,420 655,495 C 680,515 760,515 800,520 C 870,525 930,515 980,510"
            fill="none"
            stroke="rgba(38, 92, 110, 0.42)"
            strokeWidth="16"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M 310,60 C 330,130 310,190 335,265 C 380,250 440,245 500,255 C 570,245 630,250 665,265 C 685,340 670,420 655,495 C 680,515 760,515 800,520 C 870,525 930,515 980,510"
            fill="none"
            stroke="rgba(72, 148, 172, 0.65)"
            strokeWidth="9"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M 310,60 C 330,130 310,190 335,265 C 380,250 440,245 500,255 C 570,245 630,250 665,265 C 685,340 670,420 655,495 C 680,515 760,515 800,520 C 870,525 930,515 980,510"
            fill="none"
            stroke="#daf1f6"
            strokeWidth="1.8"
            strokeDasharray="14 10"
            strokeLinecap="round"
            opacity="0.85"
          />

          {/* 南向沧溟水系分支（汇入云梦与南海） */}
          <path
            d="M 655,495 C 640,560 650,630 650,735"
            fill="none"
            stroke="rgba(38, 92, 110, 0.38)"
            strokeWidth="12"
            strokeLinecap="round"
          />
          <path
            d="M 655,495 C 640,560 650,630 650,735"
            fill="none"
            stroke="rgba(72, 148, 172, 0.58)"
            strokeWidth="6"
            strokeLinecap="round"
          />

          {/* 天脊祖龙山脉褶皱（北原南界 & 西南群山） */}
          <path
            d="M 60,255 C 160,245 250,250 335,265"
            fill="none"
            stroke="rgba(105, 75, 42, 0.4)"
            strokeWidth="4"
            strokeDasharray="4 6"
          />
          <path
            d="M 665,265 C 750,250 850,245 950,255"
            fill="none"
            stroke="rgba(105, 75, 42, 0.4)"
            strokeWidth="4"
            strokeDasharray="4 6"
          />
          <path
            d="M 335,265 C 360,340 375,410 350,520"
            fill="none"
            stroke="rgba(145, 110, 55, 0.4)"
            strokeWidth="3.5"
            strokeDasharray="6 4"
          />
          <path
            d="M 350,520 C 430,510 570,510 655,495"
            fill="none"
            stroke="rgba(130, 60, 40, 0.4)"
            strokeWidth="4"
            strokeDasharray="5 5"
          />

          {/* 天然地界铭刻题字（水系名与天险名） */}
          <g fontFamily="KaiTi, STKaiti, serif" fontSize="10" fill="#6d5334" opacity="0.75">
            <text x="500" y="248" textAnchor="middle" letterSpacing="0.25em">≈ 通 天 大 江 ≈</text>
            <text x="670" y="420" textAnchor="middle" letterSpacing="0.2em" writingMode="vertical-rl">≈ 沧 溟 龙 峡 ≈</text>
            <text x="345" y="415" textAnchor="middle" letterSpacing="0.2em" writingMode="vertical-rl">▲ 昆 仑 西 岭 ▲</text>
            <text x="500" y="525" textAnchor="middle" letterSpacing="0.25em">▲ 十 万 祖 山 ▲</text>
            <text x="660" y="650" textAnchor="middle" letterSpacing="0.2em" writingMode="vertical-rl">≈ 蓬 莱 灵 堑 ≈</text>
          </g>
        </g>

        {/* 跨域灵脉古道 (沿山势水系蜿蜒流转，绝无任何 ＃ 井字死板直线) */}
        <g className="travel-routes-layer" opacity="0.68" pointerEvents="none">
          {/* 中州核心四方蜿蜒灵脉 */}
          <path d="M 500,390 C 580,355 720,360 820,390" fill="none" stroke="#8b5e28" strokeWidth="2.2" strokeDasharray="5 5" />
          <path d="M 500,390 C 420,355 280,360 180,390" fill="none" stroke="#8b5e28" strokeWidth="2.2" strokeDasharray="5 5" />
          <path d="M 500,390 C 465,300 535,215 500,125" fill="none" stroke="#8b5e28" strokeWidth="2.2" strokeDasharray="5 5" />
          <path d="M 500,390 C 535,480 465,565 500,650" fill="none" stroke="#8b5e28" strokeWidth="2.2" strokeDasharray="5 5" />

          {/* 外域山关斜贯古道 */}
          <path d="M 180,128 C 240,195 320,310 180,390" fill="none" stroke="#966d3b" strokeWidth="1.6" strokeDasharray="4 4" opacity="0.5" />
          <path d="M 820,128 C 760,195 680,310 820,390" fill="none" stroke="#966d3b" strokeWidth="1.6" strokeDasharray="4 4" opacity="0.5" />
          <path d="M 180,390 C 240,470 320,580 180,650" fill="none" stroke="#966d3b" strokeWidth="1.6" strokeDasharray="4 4" opacity="0.5" />
          <path d="M 820,390 C 760,470 680,580 820,650" fill="none" stroke="#966d3b" strokeWidth="1.6" strokeDasharray="4 4" opacity="0.5" />
          <path d="M 180,128 C 300,90 410,105 500,125" fill="none" stroke="#966d3b" strokeWidth="1.6" strokeDasharray="4 4" opacity="0.5" />
          <path d="M 820,128 C 700,90 590,105 500,125" fill="none" stroke="#966d3b" strokeWidth="1.6" strokeDasharray="4 4" opacity="0.5" />
          <path d="M 180,650 C 300,685 410,670 500,650" fill="none" stroke="#966d3b" strokeWidth="1.6" strokeDasharray="4 4" opacity="0.5" />
          <path d="M 820,650 C 700,685 590,670 500,650" fill="none" stroke="#966d3b" strokeWidth="1.6" strokeDasharray="4 4" opacity="0.5" />
        </g>

        {/* 2. 九大州独立实体板块（可单独悬浮、整体隆起、带真实水墨古意） */}
        {sortedItems.map((item, index) => {
          const current = item.current === true
          const accessible = item.accessible === true
          const key = String(item.key || `地域-${index}`)
          const chosen = selectedKey === key || (selectedKey === '' && current)
          const geom = PROVINCE_GEOMETRIES[key] || PROVINCE_GEOMETRIES['中州']
          const isHovered = hoveredKey === key
          const isSealed = item.sealed === true

          return (
            <g
              key={key}
              className={`province-sector ${isHovered ? 'hovered' : ''} ${chosen ? 'selected' : ''}`}
              data-region={key}
              data-current={current || undefined}
              data-locked={(!accessible && !current) || undefined}
              data-sealed={isSealed || undefined}
              role="button"
              tabIndex={0}
              aria-pressed={chosen}
              aria-label={`查看${String(item.name || key)}地域`}
              onClick={() => onSelect(key)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  onSelect(key)
                }
              }}
              onMouseEnter={() => setHoveredKey(key)}
              onMouseLeave={() => setHoveredKey(null)}
              filter={
                isHovered
                  ? 'url(#inkShadow) url(#goldGlow)'
                  : chosen
                    ? 'url(#inkShadow) url(#activeGlow)'
                    : undefined
              }
            >
              {/* 板块底色填充与事件响应拾取区域 */}
              <path
                d={geom.path}
                className="province-hitbox"
                fill="#f4ecd8"
                fillOpacity="0.01"
                pointerEvents="all"
              />

              {/* 板块独立地图切片（悬浮时随此州整体隆起浮动） */}
              <g clipPath={`url(#clip-${key})`} pointerEvents="none">
                <image
                  href={mapBg}
                  x="0"
                  y="0"
                  width="1000"
                  height="800"
                  preserveAspectRatio="xMidYMid slice"
                  className="province-land-texture"
                  filter={
                    isHovered
                      ? 'brightness(1.08) contrast(1.06)'
                      : chosen
                        ? 'brightness(1.05) contrast(1.04)'
                        : undefined
                  }
                />
              </g>

              {/* 板块金光金线外沿轮廓 */}
              <path
                d={geom.path}
                className="province-contour-stroke"
                fill={
                  isHovered
                    ? 'rgba(255, 235, 175, 0.12)'
                    : chosen
                      ? 'rgba(255, 225, 150, 0.15)'
                      : isSealed
                        ? 'rgba(80, 50, 30, 0.04)'
                        : 'none'
                }
                stroke={
                  chosen
                    ? '#ba8d3c'
                    : isHovered
                      ? '#dfb055'
                      : isSealed
                        ? 'rgba(100, 70, 40, 0.28)'
                        : 'rgba(110, 78, 38, 0.38)'
                }
                strokeWidth={chosen ? 3.5 : isHovered ? 3 : 1.5}
                strokeDasharray={chosen ? undefined : isHovered ? '8 4' : isSealed ? '5 3' : undefined}
                pointerEvents="none"
              />

              {/* 3. 浑然一体的古风题字与朱砂印鉴 */}
              {/* 朱砂印鉴 */}
              <g transform={`translate(${geom.sealX}, ${geom.sealY})`} pointerEvents="none">
                <rect
                  width="28"
                  height="28"
                  rx="5"
                  fill={
                    isSealed
                      ? chosen
                        ? '#6d1d18'
                        : '#541c17'
                      : chosen
                        ? '#a62419'
                        : isHovered
                          ? '#ba2d20'
                          : '#8a2016'
                  }
                  stroke={isSealed ? '#d0b58e' : '#edd8b4'}
                  strokeWidth="1.2"
                  opacity={isSealed && !isHovered && !chosen ? 0.75 : 0.95}
                />
                <text
                  x="14"
                  y="19"
                  textAnchor="middle"
                  fontFamily="KaiTi, serif"
                  fontSize="15"
                  fontWeight="bold"
                  fill="#fff4e0"
                >
                  {geom.badgeChar}
                </text>
              </g>

              {/* 水墨榜书大字 */}
              <text
                x={geom.labelX}
                y={geom.labelY}
                textAnchor="middle"
                fontFamily="KaiTi, STKaiti, serif"
                fontSize={isHovered || chosen ? '19' : '17'}
                fontWeight="bold"
                fill={
                  chosen
                    ? '#2c1a0e'
                    : isHovered
                      ? '#3a2212'
                      : isSealed
                        ? '#503825'
                        : '#452b18'
                }
                className="province-title-text"
                pointerEvents="none"
              >
                {String(item.name || key).split('·')[0].trim()}
              </text>

              {/* 地貌意境题跋小字 */}
              <text
                x={geom.labelX}
                y={geom.labelY + 22}
                textAnchor="middle"
                fontFamily="KaiTi, serif"
                fontSize="11"
                fill={isHovered || chosen ? '#6e4c25' : '#886d4b'}
                className="province-subtitle-text"
                pointerEvents="none"
              >
                {geom.terrainTitle}
              </text>

              {/* 太古禁域标识 */}
              {isSealed && !current && (
                <g transform={`translate(${geom.labelX - 32}, ${geom.labelY + 32})`} pointerEvents="none">
                  <rect width="64" height="16" rx="8" fill="#5c3826" fillOpacity="0.85" stroke="#dfc299" strokeWidth="0.8" />
                  <text x="32" y="11.5" textAnchor="middle" fontFamily="KaiTi, serif" fontSize="9" fill="#fcf6ec">
                    太古禁域
                  </text>
                </g>
              )}

              {/* 当前道友落脚标记 */}
              {current && (
                <g transform={`translate(${geom.labelX - 44}, ${geom.labelY + 32})`} pointerEvents="none">
                  <rect width="88" height="18" rx="9" fill="#2b6351" fillOpacity="0.9" stroke="#cfe3d6" strokeWidth="0.8" />
                  <text x="44" y="13" textAnchor="middle" fontFamily="KaiTi, serif" fontSize="10" fill="#ffffff">
                    道友在此落脚
                  </text>
                </g>
              )}

              {/* 机缘神采星芒 */}
              {item.has_event === true && (
                <g
                  className="province-event-marker"
                  transform={`translate(${geom.sealX + 34}, ${geom.sealY})`}
                  aria-label="有地方机缘"
                  pointerEvents="none"
                >
                  <circle cx="10" cy="10" r="10" fill="#ba8d3c" />
                  <path d="M 10,4 L 11.5,8.5 L 16,10 L 11.5,11.5 L 10,16 L 8.5,11.5 L 4,10 L 8.5,8.5 Z" fill="#ffffff" />
                </g>
              )}
            </g>
          )
        })}

        {/* 古卷四方印签文案 */}
        <g className="map-seal-inscriptions" fontFamily="KaiTi, serif" fontSize="13" fontWeight="bold" fill="#4d351c" opacity="0.65" pointerEvents="none">
          <text x="500" y="38" textAnchor="middle" letterSpacing="0.32em">极 北 寒 渊 · 万 载 玄 冰</text>
          <text x="45" y="400" textAnchor="middle" letterSpacing="0.25em" writingMode="vertical-rl">西 垂 流 沙 · 瀚 海 鸣 沙</text>
          <text x="955" y="400" textAnchor="middle" letterSpacing="0.25em" writingMode="vertical-rl">东 海 青 岳 · 碧 峰 叠 翠</text>
          <text x="500" y="785" textAnchor="middle" letterSpacing="0.32em">南 荒 赤 炎 · 十 万 大 山</text>
        </g>
      </svg>

      {/* 司南罗盘 */}
      <span className="atlas-compass" aria-hidden="true">
        <i>北</i>
        <b>九州</b>
        <i>南</i>
      </span>

      {/* 底部卷轴说明文案 */}
      <div className="map-canvas-footer">
        <Wind size={12} />
        <span>神州九域全图 · 九宫八卦之局</span>
      </div>
      <p>山河入卷 · 九州可观</p>
    </nav>
  )
}

