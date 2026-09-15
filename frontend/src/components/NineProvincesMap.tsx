import React from 'react'
import { motion } from 'motion/react'
import {
  Flame,
  Mountain,
  Snowflake,
  Sun,
  Castle,
  MapPin,
  Sparkles,
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

// 对应五域古卷实际山川地理与地貌特征配置
const REGION_CONFIGS: Record<
  string,
  {
    x: number // 百分比
    y: number // 百分比
    badgeChar: string
    terrainTitle: string
    terrainType: string
    icon: React.ComponentType<{ size?: number; className?: string }>
    themeColor: string
    accentColor: string
  }
> = {
  中州: {
    x: 51,
    y: 55,
    badgeChar: '中',
    terrainTitle: '中土天阙 · 仙宫浮云',
    terrainType: '昆仑天柱 · 浮空仙阙',
    icon: Castle,
    themeColor: '#b8860b',
    accentColor: '#fcf6e5',
  },
  东洲: {
    x: 75,
    y: 48,
    badgeChar: '东',
    terrainTitle: '东海青岳 · 碧峰叠翠',
    terrainType: '千峰秀水 · 仙雾流泉',
    icon: Mountain,
    themeColor: '#2e7d32',
    accentColor: '#e9f5ed',
  },
  南疆: {
    x: 51,
    y: 82,
    badgeChar: '南',
    terrainTitle: '南疆赤炎 · 十万大山',
    terrainType: '地火熔脉 · 妖氛凶谷',
    icon: Flame,
    themeColor: '#c62828',
    accentColor: '#faece8',
  },
  西漠: {
    x: 23,
    y: 52,
    badgeChar: '西',
    terrainTitle: '西垂流沙 · 瀚海鸣沙',
    terrainType: '大漠古道 · 佛窟遗迹',
    icon: Sun,
    themeColor: '#b58434',
    accentColor: '#f9f2e3',
  },
  北原: {
    x: 50,
    y: 19,
    badgeChar: '北',
    terrainTitle: '极北寒渊 · 万载玄冰',
    terrainType: '暴雪冰川 · 幽冥极光',
    icon: Snowflake,
    themeColor: '#1565c0',
    accentColor: '#e7f3fa',
  },
}

export function NineProvincesMap({ items, selectedKey, onSelect }: NineProvincesMapProps) {
  return (
    <nav className="region-atlas-map nine-provinces-2d-canvas" aria-label="五域卷轴舆图">
      {/* 1. 真实水墨古卷宣纸地图底图 */}
      <img
        src={mapBg}
        alt="神州五域山川古卷舆图"
        className="map-canvas-background"
        aria-hidden="true"
      />

      {/* 2. 2D 灵脉古道与舆图印签矢量层 */}
      <svg
        className="map-topography-svg"
        viewBox="0 0 1000 800"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
      >
        <defs>
          <filter id="routeGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#8b5a2b" floodOpacity="0.45" />
          </filter>
          <radialGradient id="mapVignette" cx="50%" cy="50%" r="62%">
            <stop offset="60%" stopColor="transparent" />
            <stop offset="100%" stopColor="#2c1f10" stopOpacity="0.32" />
          </radialGradient>
        </defs>

        {/* 古卷边缘暗角 */}
        <rect x="0" y="0" width="1000" height="800" fill="url(#mapVignette)" />

        {/* 跨域灵脉古道路线 (连接五域实际地貌位置) */}
        <g className="travel-routes-layer" filter="url(#routeGlow)">
          {/* 中州至东洲 */}
          <path d="M 510,440 Q 630,395 750,384" fill="none" stroke="#754e22" strokeWidth="2.8" strokeDasharray="6 5" opacity="0.85" />
          {/* 中州至西漠 */}
          <path d="M 510,440 Q 370,430 230,416" fill="none" stroke="#754e22" strokeWidth="2.8" strokeDasharray="6 5" opacity="0.85" />
          {/* 中州至北原 */}
          <path d="M 510,440 Q 490,290 500,152" fill="none" stroke="#754e22" strokeWidth="2.8" strokeDasharray="6 5" opacity="0.85" />
          {/* 中州至南疆 */}
          <path d="M 510,440 Q 525,550 510,656" fill="none" stroke="#754e22" strokeWidth="2.8" strokeDasharray="6 5" opacity="0.85" />
          {/* 东洲至南疆环线 */}
          <path d="M 750,384 Q 680,560 510,656" fill="none" stroke="#754e22" strokeWidth="2" strokeDasharray="4 4" opacity="0.65" />
          {/* 西漠至北原古道 */}
          <path d="M 230,416 Q 330,240 500,152" fill="none" stroke="#754e22" strokeWidth="2" strokeDasharray="4 4" opacity="0.65" />
        </g>

        {/* 四方山海古典题记 */}
        <g className="map-seal-inscriptions" fontFamily="KaiTi, serif" fontSize="13" fontWeight="bold" fill="#4d351c" opacity="0.7">
          <text x="500" y="45" textAnchor="middle" letterSpacing="0.28em">极 北 寒 渊 · 万 载 玄 冰</text>
          <text x="65" y="420" textAnchor="middle" letterSpacing="0.2em" writingMode="vertical-rl">西 垂 流 沙 · 瀚 海 鸣 沙</text>
          <text x="935" y="390" textAnchor="middle" letterSpacing="0.2em" writingMode="vertical-rl">东 海 青 岳 · 碧 峰 叠 翠</text>
          <text x="500" y="770" textAnchor="middle" letterSpacing="0.28em">南 荒 赤 炎 · 十 万 大 山</text>
        </g>
      </svg>

      {/* 3. 司南罗盘印记 */}
      <span className="atlas-compass" aria-hidden="true">
        <i>北</i>
        <b>九州</b>
        <i>南</i>
      </span>

      {/* 4. 五域交互节点（完整保留已有语义与自动化测试属性） */}
      {items.map((item, index) => {
        const current = item.current === true
        const accessible = item.accessible === true
        const visited = item.visited === true
        const key = String(item.key || `地域-${index}`)
        const chosen = selectedKey === key || (selectedKey === '' && current)
        const cfg = REGION_CONFIGS[key] || {
          x: 50,
          y: 50,
          badgeChar: key.slice(0, 1),
          terrainTitle: '未知异域',
          terrainType: '山川未定',
          icon: Mountain,
          themeColor: '#4b6759',
          accentColor: '#f7f7ec',
        }
        const Icon = cfg.icon

        return (
          <button
            type="button"
            className="region-node nine-provinces-2d-node"
            data-region={key}
            data-current={current || undefined}
            data-visited={visited || undefined}
            data-locked={(!accessible && !current) || undefined}
            aria-pressed={chosen}
            aria-label={`查看${String(item.name || key)}地域`}
            onClick={() => onSelect(key)}
            key={key}
            style={
              {
                '--node-x': `${cfg.x}%`,
                '--node-y': `${cfg.y}%`,
              } as React.CSSProperties
            }
          >
            {/* 地貌古印章图徽 */}
            <span className="node-emblem" style={{ borderColor: cfg.themeColor }}>
              <Icon size={14} className="node-terrain-icon" />
              <b className="node-char">{cfg.badgeChar}</b>
            </span>

            <div className="node-text-col">
              <div className="node-name-row">
                <strong>{String(item.name || '无名地域')}</strong>
                {current && (
                  <span className="current-player-pin" title="道友此刻正在此地">
                    <MapPin size={10} />
                    <em>落脚</em>
                  </span>
                )}
              </div>
              <small className="node-terrain-subtitle">
                {current ? (
                  <span className="active-glow-text">修真落脚地</span>
                ) : visited ? (
                  '足迹已至'
                ) : (
                  String(item.danger_label || cfg.terrainType)
                )}
              </small>
            </div>

            {/* 机缘光点 */}
            {item.has_event === true && (
              <i className="node-event-star" aria-label="有地方机缘" title="此地正有仙缘机会">
                <Sparkles size={10} />
              </i>
            )}

            {/* 当前主角所在位置灵光光晕 */}
            {current && (
              <motion.div
                className="taiji-halo-beacon"
                initial={{ scale: 0.9, opacity: 0.6 }}
                animate={{ scale: [0.95, 1.15, 0.95], opacity: [0.7, 0.25, 0.7] }}
                transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut' }}
              />
            )}
          </button>
        )
      })}

      {/* 5. 底部古卷说明与题跋 */}
      <div className="map-canvas-footer">
        <Wind size={12} />
        <span>神州五域山川图 · 凡俗与仙宗共立</span>
      </div>
      <p>山河入卷 · 五域可观</p>
    </nav>
  )
}
