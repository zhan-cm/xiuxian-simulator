
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
 * 行一（北向）：雷州(西北乾) 北原(正北坎) 幽州(东北艮)
 * 行二（中向）：西漠(正西兑) 中州(中宫天阙) 东洲(正东震)
 * 行三（南向）：云州(西南坤) 南疆(正南离) 瀛洲(东南巽)
 */
const PROVINCE_GEOMETRIES: Record<string, ProvinceGeom> = {
  北原: {
    key: '北原',
    path: 'M 350,60 C 400,30 450,15 500,15 C 550,15 600,30 650,60 C 655,120 655,190 645,260 C 600,270 550,275 500,275 C 450,275 400,270 355,260 C 345,190 345,120 350,60 Z',
    sealX: 486,
    sealY: 75,
    labelX: 500,
    labelY: 128,
    badgeChar: '北',
    terrainTitle: '极北寒渊 · 万载玄冰',
    terrainType: '暴雪冰川 · 幽冥极光',
    icon: Snowflake,
    themeColor: '#1565c0',
  },
  雷州: {
    key: '雷州',
    path: 'M 25,60 C 60,30 140,20 220,20 C 270,20 320,35 350,60 C 345,120 345,190 355,260 C 280,265 200,260 130,250 C 70,240 30,190 20,130 C 18,100 20,80 25,60 Z',
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
    path: 'M 650,60 C 680,35 730,20 780,20 C 860,20 940,30 975,60 C 980,80 982,100 980,130 C 970,190 930,240 870,250 C 800,260 720,265 645,260 C 655,190 655,120 650,60 Z',
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
    path: 'M 25,270 C 70,260 140,260 210,265 C 280,270 330,275 355,285 C 365,355 365,435 355,515 C 325,525 270,530 200,535 C 130,540 60,535 25,515 C 15,445 15,350 25,270 Z',
    sealX: 166,
    sealY: 340,
    labelX: 180,
    labelY: 395,
    badgeChar: '西',
    terrainTitle: '西垂流沙 · 瀚海鸣沙',
    terrainType: '大漠古道 · 佛窟遗迹',
    icon: Sun,
    themeColor: '#b58434',
  },
  中州: {
    key: '中州',
    path: 'M 355,285 C 400,275 450,270 500,270 C 550,270 600,275 645,285 C 655,355 655,435 645,515 C 600,525 550,530 500,530 C 450,530 400,525 355,515 C 345,435 345,355 355,285 Z',
    sealX: 486,
    sealY: 340,
    labelX: 500,
    labelY: 395,
    badgeChar: '中',
    terrainTitle: '中土天阙 · 仙宫浮云',
    terrainType: '昆仑天柱 · 浮空金阙',
    icon: Castle,
    themeColor: '#b8860b',
  },
  东洲: {
    key: '东洲',
    path: 'M 645,285 C 670,275 720,270 790,265 C 860,260 930,260 975,270 C 985,350 985,445 975,515 C 940,535 870,540 800,535 C 730,530 675,525 645,515 C 655,435 655,355 645,285 Z',
    sealX: 806,
    sealY: 340,
    labelX: 820,
    labelY: 395,
    badgeChar: '东',
    terrainTitle: '东海青岳 · 碧峰叠翠',
    terrainType: '千峰秀水 · 仙雾流泉',
    icon: Mountain,
    themeColor: '#2e7d32',
  },
  云州: {
    key: '云州',
    path: 'M 25,535 C 70,545 140,550 210,545 C 280,540 330,535 355,540 C 355,610 350,680 340,745 C 280,765 210,775 140,775 C 80,775 40,755 25,720 C 15,670 15,600 25,535 Z',
    sealX: 166,
    sealY: 605,
    labelX: 180,
    labelY: 660,
    badgeChar: '云',
    terrainTitle: '云梦古泽 · 迷障幻蜃',
    terrainType: '太虚蜃气 · 浮生幻境',
    icon: Wind,
    themeColor: '#00838f',
  },
  南疆: {
    key: '南疆',
    path: 'M 355,540 C 400,535 450,530 500,530 C 550,530 600,535 645,540 C 645,610 640,680 635,745 C 590,765 550,775 500,775 C 450,775 410,765 340,745 C 350,680 355,610 355,540 Z',
    sealX: 486,
    sealY: 605,
    labelX: 500,
    labelY: 660,
    badgeChar: '南',
    terrainTitle: '南荒赤炎 · 十万大山',
    terrainType: '地火熔脉 · 妖氛凶谷',
    icon: Flame,
    themeColor: '#c62828',
  },
  瀛洲: {
    key: '瀛洲',
    path: 'M 645,540 C 670,535 720,540 790,545 C 860,550 930,545 975,535 C 985,600 985,670 975,720 C 960,755 920,775 860,775 C 790,775 720,765 660,745 C 640,680 645,610 645,540 Z',
    sealX: 806,
    sealY: 605,
    labelX: 820,
    labelY: 660,
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

        {/* 跨域灵脉古道 (连通神州九宫) */}
        <g className="travel-routes-layer" opacity="0.65" pointerEvents="none">
          {/* 核心五域灵脉古道 */}
          <path d="M 500,400 Q 660,390 820,400" fill="none" stroke="#754e22" strokeWidth="2.5" strokeDasharray="6 5" />
          <path d="M 500,400 Q 340,390 180,400" fill="none" stroke="#754e22" strokeWidth="2.5" strokeDasharray="6 5" />
          <path d="M 500,400 Q 490,260 500,140" fill="none" stroke="#754e22" strokeWidth="2.5" strokeDasharray="6 5" />
          <path d="M 500,400 Q 510,540 500,660" fill="none" stroke="#754e22" strokeWidth="2.5" strokeDasharray="6 5" />
          <path d="M 820,400 Q 720,570 500,660" fill="none" stroke="#754e22" strokeWidth="2" strokeDasharray="4 4" opacity="0.6" />
          <path d="M 180,400 Q 280,230 500,140" fill="none" stroke="#754e22" strokeWidth="2" strokeDasharray="4 4" opacity="0.6" />

          {/* 四极太古禁断古道 (虚线阵法连线) */}
          <path d="M 180,140 Q 340,110 500,140" fill="none" stroke="#8c6a38" strokeWidth="1.8" strokeDasharray="3 4" opacity="0.45" />
          <path d="M 180,140 L 180,400" fill="none" stroke="#8c6a38" strokeWidth="1.8" strokeDasharray="3 4" opacity="0.45" />
          <path d="M 820,140 Q 660,110 500,140" fill="none" stroke="#8c6a38" strokeWidth="1.8" strokeDasharray="3 4" opacity="0.45" />
          <path d="M 820,140 L 820,400" fill="none" stroke="#8c6a38" strokeWidth="1.8" strokeDasharray="3 4" opacity="0.45" />
          <path d="M 180,660 L 180,400" fill="none" stroke="#8c6a38" strokeWidth="1.8" strokeDasharray="3 4" opacity="0.45" />
          <path d="M 180,660 Q 340,690 500,660" fill="none" stroke="#8c6a38" strokeWidth="1.8" strokeDasharray="3 4" opacity="0.45" />
          <path d="M 820,660 L 820,400" fill="none" stroke="#8c6a38" strokeWidth="1.8" strokeDasharray="3 4" opacity="0.45" />
          <path d="M 820,660 Q 660,690 500,660" fill="none" stroke="#8c6a38" strokeWidth="1.8" strokeDasharray="3 4" opacity="0.45" />
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

