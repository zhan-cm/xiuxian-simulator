
import React, { useState } from 'react'
import {
  Flame,
  Mountain,
  Snowflake,
  Sun,
  Castle,
  Wind,
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
  [key: string]: unknown
}

interface NineProvincesMapProps {
  items: RegionAtlasItem[]
  selectedKey: string
  onSelect: (key: string) => void
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

const PROVINCE_GEOMETRIES: Record<string, ProvinceGeom> = {
  北原: {
    key: '北原',
    path: 'M 160,100 C 280,20 400,15 500,15 C 600,15 720,20 840,100 C 880,160 870,220 820,270 C 700,290 600,285 500,280 C 400,285 300,290 180,270 C 130,220 120,160 160,100 Z',
    sealX: 486,
    sealY: 78,
    labelX: 500,
    labelY: 130,
    badgeChar: '北',
    terrainTitle: '极北寒渊 · 万载玄冰',
    terrainType: '暴雪冰川 · 幽冥极光',
    icon: Snowflake,
    themeColor: '#1565c0',
  },
  西漠: {
    key: '西漠',
    path: 'M 180,270 C 260,285 330,300 370,320 C 390,410 385,490 370,570 C 300,595 240,615 170,630 C 80,590 25,520 20,430 C 20,340 70,280 180,270 Z',
    sealX: 196,
    sealY: 375,
    labelX: 210,
    labelY: 428,
    badgeChar: '西',
    terrainTitle: '西垂流沙 · 瀚海鸣沙',
    terrainType: '大漠古道 · 佛窟遗迹',
    icon: Sun,
    themeColor: '#b58434',
  },
  中州: {
    key: '中州',
    path: 'M 500,280 C 580,285 620,300 650,320 C 670,410 665,490 650,570 C 600,590 550,600 500,600 C 450,600 400,590 370,570 C 385,490 390,410 370,320 C 400,300 440,285 500,280 Z',
    sealX: 486,
    sealY: 375,
    labelX: 500,
    labelY: 428,
    badgeChar: '中',
    terrainTitle: '中土天阙 · 仙宫浮云',
    terrainType: '昆仑天柱 · 浮空金阙',
    icon: Castle,
    themeColor: '#b8860b',
  },
  东洲: {
    key: '东洲',
    path: 'M 650,320 C 700,300 760,285 820,270 C 910,280 970,340 980,430 C 975,520 920,590 830,630 C 760,615 700,595 650,570 C 665,490 670,410 650,320 Z',
    sealX: 786,
    sealY: 375,
    labelX: 800,
    labelY: 428,
    badgeChar: '东',
    terrainTitle: '东海青岳 · 碧峰叠翠',
    terrainType: '千峰秀水 · 仙雾流泉',
    icon: Mountain,
    themeColor: '#2e7d32',
  },
  南疆: {
    key: '南疆',
    path: 'M 170,630 C 240,615 300,595 370,570 C 410,590 460,600 500,600 C 540,600 590,590 650,570 C 720,595 760,615 830,630 C 860,690 820,750 760,780 C 660,795 500,800 500,800 C 500,800 340,795 240,780 C 180,750 140,690 170,630 Z',
    sealX: 486,
    sealY: 625,
    labelX: 500,
    labelY: 678,
    badgeChar: '南',
    terrainTitle: '南荒赤炎 · 十万大山',
    terrainType: '地火熔脉 · 妖氛凶谷',
    icon: Flame,
    themeColor: '#c62828',
  },
}

export function NineProvincesMap({ items, selectedKey, onSelect }: NineProvincesMapProps) {
  const [hoveredKey, setHoveredKey] = useState<string | null>(null)

  // 排序：让当前悬浮或选中的地域绘制在最上层，确保浮动阴影与边缘不被邻域遮挡
  const sortedItems = [...items].sort((a, b) => {
    const aKey = String(a.key)
    const bKey = String(b.key)
    const aActive = aKey === hoveredKey || (selectedKey === aKey)
    const bActive = bKey === hoveredKey || (selectedKey === bKey)
    if (aActive && !bActive) return 1
    if (!aActive && bActive) return -1
    return 0
  })

  return (
    <nav className="region-atlas-map nine-provinces-2d-canvas" aria-label="五域卷轴舆图">
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

        {/* 跨域灵脉古道 (连通五域) */}
        <g className="travel-routes-layer" opacity="0.6" pointerEvents="none">
          <path d="M 500,430 Q 640,395 800,430" fill="none" stroke="#754e22" strokeWidth="2.5" strokeDasharray="6 5" />
          <path d="M 500,430 Q 360,420 210,430" fill="none" stroke="#754e22" strokeWidth="2.5" strokeDasharray="6 5" />
          <path d="M 500,430 Q 490,280 500,140" fill="none" stroke="#754e22" strokeWidth="2.5" strokeDasharray="6 5" />
          <path d="M 500,430 Q 520,550 500,670" fill="none" stroke="#754e22" strokeWidth="2.5" strokeDasharray="6 5" />
          <path d="M 800,430 Q 700,580 500,670" fill="none" stroke="#754e22" strokeWidth="2" strokeDasharray="4 4" opacity="0.6" />
          <path d="M 210,430 Q 330,240 500,140" fill="none" stroke="#754e22" strokeWidth="2" strokeDasharray="4 4" opacity="0.6" />
        </g>

        {/* 2. 五大州独立实体板块（可单独悬浮、整体隆起、带真实水墨古意） */}
        {sortedItems.map((item, index) => {
          const current = item.current === true
          const accessible = item.accessible === true
          const key = String(item.key || `地域-${index}`)
          const chosen = selectedKey === key || (selectedKey === '' && current)
          const geom = PROVINCE_GEOMETRIES[key] || PROVINCE_GEOMETRIES['中州']
          const isHovered = hoveredKey === key

          return (
            <g
              key={key}
              className={`province-sector ${isHovered ? 'hovered' : ''} ${chosen ? 'selected' : ''}`}
              data-region={key}
              data-current={current || undefined}
              data-locked={(!accessible && !current) || undefined}
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
              filter={isHovered ? 'url(#inkShadow) url(#goldGlow)' : chosen ? 'url(#inkShadow) url(#activeGlow)' : undefined}
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
                  filter={isHovered ? 'brightness(1.08) contrast(1.06)' : chosen ? 'brightness(1.05) contrast(1.04)' : undefined}
                />
              </g>

              {/* 板块金光金线外沿轮廓 */}
              <path
                d={geom.path}
                className="province-contour-stroke"
                fill={isHovered ? 'rgba(255, 235, 175, 0.12)' : chosen ? 'rgba(255, 225, 150, 0.15)' : 'none'}
                stroke={chosen ? '#ba8d3c' : isHovered ? '#dfb055' : 'rgba(110, 78, 38, 0.38)'}
                strokeWidth={chosen ? 3.5 : isHovered ? 3 : 1.5}
                strokeDasharray={chosen ? undefined : isHovered ? '8 4' : undefined}
                pointerEvents="none"
              />

              {/* 3. 浑然一体的古风题字与朱砂印鉴（彻底移除矩形UI边框！） */}
              {/* 朱砂印鉴 */}
              <g transform={`translate(${geom.sealX}, ${geom.sealY})`} pointerEvents="none">
                <rect
                  width="28"
                  height="28"
                  rx="5"
                  fill={chosen ? '#a62419' : isHovered ? '#ba2d20' : '#8a2016'}
                  stroke="#edd8b4"
                  strokeWidth="1.2"
                  opacity="0.95"
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
                fill={chosen ? '#2c1a0e' : isHovered ? '#3a2212' : '#452b18'}
                className="province-title-text"
                pointerEvents="none"
              >
                {String(item.name || key)}
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
        <g className="map-seal-inscriptions" fontFamily="KaiTi, serif" fontSize="13" fontWeight="bold" fill="#4d351c" opacity="0.6" pointerEvents="none">
          <text x="500" y="38" textAnchor="middle" letterSpacing="0.3em">极 北 寒 渊 · 万 载 玄 冰</text>
          <text x="50" y="420" textAnchor="middle" letterSpacing="0.22em" writingMode="vertical-rl">西 垂 流 沙 · 瀚 海 鸣 沙</text>
          <text x="950" y="390" textAnchor="middle" letterSpacing="0.22em" writingMode="vertical-rl">东 海 青 岳 · 碧 峰 叠 翠</text>
          <text x="500" y="775" textAnchor="middle" letterSpacing="0.3em">南 荒 赤 炎 · 十 万 大 山</text>
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
        <span>神州五域山川图 · 凡俗与仙宗共立</span>
      </div>
      <p>山河入卷 · 五域可观</p>
    </nav>
  )
}

