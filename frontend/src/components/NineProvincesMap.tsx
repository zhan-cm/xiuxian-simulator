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

// 对应五域地理与地貌特征配置
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
    x: 50,
    y: 50,
    badgeChar: '中',
    terrainTitle: '中土天阙 · 仙宫浮云',
    terrainType: '昆仑天柱 · 浮空仙阙',
    icon: Castle,
    themeColor: '#c29b38',
    accentColor: '#fcf6e5',
  },
  东洲: {
    x: 82,
    y: 47,
    badgeChar: '东',
    terrainTitle: '东荒青岳 · 碧峰叠翠',
    terrainType: '千峰秀水 · 仙雾流泉',
    icon: Mountain,
    themeColor: '#3d7a5a',
    accentColor: '#e9f5ed',
  },
  南疆: {
    x: 50,
    y: 84,
    badgeChar: '南',
    terrainTitle: '南荒赤炎 · 十万大山',
    terrainType: '地火熔脉 · 妖氛凶谷',
    icon: Flame,
    themeColor: '#b84e36',
    accentColor: '#faece8',
  },
  西漠: {
    x: 18,
    y: 49,
    badgeChar: '西',
    terrainTitle: '西垂流沙 · 瀚海鸣沙',
    terrainType: '大漠古道 · 佛窟遗迹',
    icon: Sun,
    themeColor: '#b58434',
    accentColor: '#f9f2e3',
  },
  北原: {
    x: 50,
    y: 15,
    badgeChar: '北',
    terrainTitle: '极北寒渊 · 万载玄冰',
    terrainType: '暴雪冰川 · 幽冥极光',
    icon: Snowflake,
    themeColor: '#3a7694',
    accentColor: '#e7f3fa',
  },
}

export function NineProvincesMap({ items, selectedKey, onSelect }: NineProvincesMapProps) {
  return (
    <nav className="region-atlas-map nine-provinces-2d-canvas" aria-label="五域卷轴舆图">
      {/* 2D 水墨矢量山川地貌底图 */}
      <svg
        className="map-topography-svg"
        viewBox="0 0 1000 800"
        preserveAspectRatio="xMidYMid meet"
        aria-hidden="true"
      >
        <defs>
          {/* 宣纸水墨底纹与暗影滤镜 */}
          <filter id="inkBlur" x="-10%" y="-10%" width="120%" height="120%">
            <feGaussianBlur stdDeviation="2" />
          </filter>
          <filter id="glowGold" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#ba8d3c" floodOpacity="0.4" />
          </filter>
          <filter id="glowRed" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#d9534f" floodOpacity="0.35" />
          </filter>

          {/* 北原：冰雪极地渐变 */}
          <linearGradient id="snowGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
            <stop offset="60%" stopColor="#d5e8f5" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#9fc1d9" stopOpacity="0.75" />
          </linearGradient>
          <linearGradient id="snowGrad2" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#ffffff" />
            <stop offset="100%" stopColor="#b2d4eb" />
          </linearGradient>
          <radialGradient id="auroraGlow" cx="50%" cy="10%" r="50%">
            <stop offset="0%" stopColor="#55b5b0" stopOpacity="0.22" />
            <stop offset="60%" stopColor="#3a6085" stopOpacity="0.08" />
            <stop offset="100%" stopColor="#000000" stopOpacity="0" />
          </radialGradient>

          {/* 西漠：大漠沙丘与残阳渐变 */}
          <linearGradient id="desertGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fae7b5" stopOpacity="0.9" />
            <stop offset="60%" stopColor="#e3be74" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#c79d4b" stopOpacity="0.75" />
          </linearGradient>
          <linearGradient id="desertGrad2" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#d4a34b" />
            <stop offset="100%" stopColor="#f5dd9d" />
          </linearGradient>

          {/* 东洲：青翠仙山与碧水渐变 */}
          <linearGradient id="mountainGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#679b7b" stopOpacity="0.92" />
            <stop offset="70%" stopColor="#3d6b51" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#254a36" stopOpacity="0.8" />
          </linearGradient>
          <linearGradient id="mountainGrad2" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stopColor="#82b395" />
            <stop offset="100%" stopColor="#437256" />
          </linearGradient>
          <linearGradient id="riverGrad" x1="0%" y1="0%" x2="100%" y2="50%">
            <stop offset="0%" stopColor="#4a8ba8" stopOpacity="0.55" />
            <stop offset="100%" stopColor="#265a73" stopOpacity="0.7" />
          </linearGradient>

          {/* 南疆：地火熔岩与险山渐变 */}
          <linearGradient id="volcanoGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#7a4236" stopOpacity="0.9" />
            <stop offset="60%" stopColor="#4d241c" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#260f0a" stopOpacity="0.9" />
          </linearGradient>
          <linearGradient id="lavaGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#ff4d2e" />
            <stop offset="50%" stopColor="#ff8a3d" />
            <stop offset="100%" stopColor="#d12e17" />
          </linearGradient>

          {/* 中州：昆仑天柱与祥云天阙 */}
          <linearGradient id="kunlunGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#e4d29e" stopOpacity="0.95" />
            <stop offset="50%" stopColor="#9c8751" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#57492c" stopOpacity="0.85" />
          </linearGradient>
          <radialGradient id="celestialHalo" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#f5e4ab" stopOpacity="0.3" />
            <stop offset="50%" stopColor="#caa048" stopOpacity="0.12" />
            <stop offset="100%" stopColor="#ba8d3c" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* 1. 天地八荒背景光韵 */}
        <rect x="0" y="0" width="1000" height="800" fill="#f6f2e4" opacity="0.4" />
        <circle cx="500" cy="110" r="400" fill="url(#auroraGlow)" />
        <circle cx="500" cy="400" r="320" fill="url(#celestialHalo)" />

        {/* 2. 九州山水脉络与河流水系 */}
        {/* 沧浪长河：自西向东汇入东海 */}
        <path
          d="M 120,410 C 260,370 320,440 450,420 C 580,400 680,450 860,420 C 920,410 960,430 1000,420"
          fill="none"
          stroke="url(#riverGrad)"
          strokeWidth="6"
          strokeLinecap="round"
          opacity="0.65"
        />
        <path
          d="M 500,180 C 470,260 520,330 460,420 C 420,480 480,560 490,660"
          fill="none"
          stroke="url(#riverGrad)"
          strokeWidth="4"
          strokeLinecap="round"
          opacity="0.45"
          strokeDasharray="8 4"
        />

        {/* 3. 跨域灵舟古道路线 (连接五域) */}
        <g className="travel-routes-layer" opacity="0.65">
          {/* 中州至东洲 */}
          <path d="M 500,400 Q 650,370 820,380" fill="none" stroke="#947a46" strokeWidth="2.5" strokeDasharray="5 5" />
          {/* 中州至西漠 */}
          <path d="M 500,400 Q 340,390 180,390" fill="none" stroke="#947a46" strokeWidth="2.5" strokeDasharray="5 5" />
          {/* 中州至北原 */}
          <path d="M 500,400 Q 480,240 500,120" fill="none" stroke="#947a46" strokeWidth="2.5" strokeDasharray="5 5" />
          {/* 中州至南疆 */}
          <path d="M 500,400 Q 520,540 500,670" fill="none" stroke="#947a46" strokeWidth="2.5" strokeDasharray="5 5" />
          {/* 东洲至南疆环路 */}
          <path d="M 820,380 Q 720,580 500,670" fill="none" stroke="#947a46" strokeWidth="1.8" strokeDasharray="4 4" opacity="0.5" />
          {/* 西漠至北原古道 */}
          <path d="M 180,390 Q 280,210 500,120" fill="none" stroke="#947a46" strokeWidth="1.8" strokeDasharray="4 4" opacity="0.5" />
        </g>

        {/* ==================== 4. 五域山川地貌矢量实体绘制 ==================== */}

        {/* 【北原·寒渊】：万仞冰川雪峰群与玄冰深谷 */}
        <g className="topography-north" filter="url(#inkBlur)">
          {/* 远景雪山 */}
          <polygon points="500,30 420,130 580,130" fill="url(#snowGrad1)" opacity="0.85" />
          <polygon points="410,50 340,140 480,140" fill="url(#snowGrad2)" opacity="0.75" />
          <polygon points="590,55 520,145 660,145" fill="url(#snowGrad2)" opacity="0.75" />
          <polygon points="330,70 270,150 390,150" fill="url(#snowGrad1)" opacity="0.65" />
          <polygon points="670,75 610,155 730,155" fill="url(#snowGrad1)" opacity="0.65" />
          {/* 冰川裂隙阴影 */}
          <path d="M 495,45 L 500,130 M 415,65 L 420,140 M 585,70 L 580,145" stroke="#487896" strokeWidth="2" opacity="0.7" />
          {/* 霜雪浮纹 */}
          <path d="M 370,110 Q 500,90 630,110" fill="none" stroke="#ffffff" strokeWidth="3" opacity="0.8" />
        </g>

        {/* 【西漠·流沙】：层叠金色瀚海沙丘与雅丹石林 */}
        <g className="topography-west">
          {/* 残阳 */}
          <circle cx="90" cy="300" r="32" fill="#d9743c" opacity="0.4" />
          <circle cx="90" cy="300" r="22" fill="#e88941" opacity="0.7" />
          {/* 沙丘起伏 */}
          <path
            d="M 30,440 Q 110,340 210,410 Q 280,360 340,430 L 340,470 L 30,470 Z"
            fill="url(#desertGrad1)"
            opacity="0.88"
          />
          <path
            d="M 60,450 Q 150,380 240,435 Q 290,400 330,460 L 330,490 L 60,490 Z"
            fill="url(#desertGrad2)"
            opacity="0.78"
          />
          {/* 古佛石窟塔影 */}
          <polygon points="120,370 115,400 125,400" fill="#7a5525" opacity="0.7" />
          <rect x="117" y="380" width="6" height="22" fill="#7a5525" opacity="0.6" />
        </g>

        {/* 【东洲·青岳】：翠绿灵山千峰与东海仙波 */}
        <g className="topography-east">
          {/* 青翠群峰 */}
          <polygon points="820,310 750,440 890,440" fill="url(#mountainGrad1)" opacity="0.9" />
          <polygon points="890,340 830,450 950,450" fill="url(#mountainGrad2)" opacity="0.8" />
          <polygon points="750,350 690,455 810,455" fill="url(#mountainGrad2)" opacity="0.85" />
          <polygon points="700,380 650,465 750,465" fill="url(#mountainGrad1)" opacity="0.75" />
          <polygon points="940,370 880,470 1000,470" fill="url(#mountainGrad1)" opacity="0.7" />
          {/* 灵泉飞瀑 */}
          <path d="M 818,330 C 825,370 812,410 822,440" fill="none" stroke="#79c5e3" strokeWidth="2" opacity="0.85" />
          {/* 山间仙雾云气 */}
          <path d="M 720,400 C 760,390 810,405 850,395" fill="none" stroke="#ffffff" strokeWidth="4" strokeLinecap="round" opacity="0.6" />
        </g>

        {/* 【南疆·赤炎】：十万大山黑石火脉与地脉熔岩 */}
        <g className="topography-south">
          {/* 火山险峰 */}
          <polygon points="500,560 410,730 590,730" fill="url(#volcanoGrad1)" opacity="0.95" />
          <polygon points="410,600 330,750 490,750" fill="url(#volcanoGrad1)" opacity="0.85" />
          <polygon points="590,610 510,755 670,755" fill="url(#volcanoGrad1)" opacity="0.85" />
          {/* 熔岩火脉裂痕 */}
          <path
            d="M 500,580 L 495,640 L 480,680 L 505,730 M 495,640 L 525,690 L 515,730"
            fill="none"
            stroke="url(#lavaGrad)"
            strokeWidth="3.5"
            strokeLinecap="round"
            filter="url(#glowRed)"
          />
          {/* 妖山火气 */}
          <ellipse cx="500" cy="565" rx="35" ry="12" fill="#ff6b42" opacity="0.45" filter="url(#glowRed)" />
        </g>

        {/* 【中州·天阙】：中央昆仑天柱与九重浮空金阙 */}
        <g className="topography-center">
          {/* 昆仑天柱主峰 */}
          <polygon points="500,260 410,470 590,470" fill="url(#kunlunGrad)" opacity="0.9" />
          <polygon points="440,310 380,480 500,480" fill="#756238" opacity="0.75" />
          <polygon points="560,320 500,485 620,485" fill="#5c4d2c" opacity="0.8" />
          {/* 天柱石棱金光 */}
          <line x1="500" y1="260" x2="500" y2="470" stroke="#fce6a7" strokeWidth="2.5" opacity="0.8" />

          {/* 悬空仙阁金阙 (天阙主殿剪影) */}
          <g transform="translate(470, 310) scale(0.65)" filter="url(#glowGold)">
            <path d="M 45,0 L 5,20 L 85,20 Z" fill="#e8c258" />
            <rect x="18" y="20" width="54" height="24" fill="#a87f28" />
            <path d="M 50,-18 L 15,2 L 80,2 Z" fill="#f5db76" />
            <rect x="26" y="2" width="38" height="18" fill="#c49733" />
          </g>

          {/* 环山祥云 */}
          <path d="M 420,380 C 460,365 540,365 580,380" fill="none" stroke="#fff9e6" strokeWidth="6" strokeLinecap="round" opacity="0.75" />
          <path d="M 440,430 C 470,420 530,420 560,430" fill="none" stroke="#ffffff" strokeWidth="4" strokeLinecap="round" opacity="0.65" />
        </g>

        {/* 舆图四方古雅文字雕版印刻 */}
        <g className="map-seal-inscriptions" opacity="0.45" fontFamily="KaiTi, serif" fontSize="13" fill="#695632">
          <text x="500" y="32" textAnchor="middle" letterSpacing="0.2em">极北寒渊 · 绝境裂隙</text>
          <text x="80" y="470" textAnchor="middle" letterSpacing="0.15em">西垂流沙 · 瀚海佛土</text>
          <text x="910" y="470" textAnchor="middle" letterSpacing="0.15em">东海青岳 · 碧海群仙</text>
          <text x="500" y="785" textAnchor="middle" letterSpacing="0.2em">南蛮赤炎 · 巫蛊火脉</text>
        </g>
      </svg>

      {/* 5. 罗盘司南 */}
      <span className="atlas-compass" aria-hidden="true">
        <i>北</i>
        <b>九州</b>
        <i>南</i>
      </span>

      {/* 6. 五域交互节点按键（完全保留已有语义与测试标签） */}
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
            {/* 地貌微缩印章图徽 */}
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

            {/* 当前主角所在灵光光环 */}
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

      {/* 底部卷轴说明文案 */}
      <div className="map-canvas-footer">
        <Wind size={12} />
        <span>神州五域山川图 · 凡俗与仙宗共立</span>
      </div>
      <p>山河入卷 · 五域可观</p>
    </nav>
  )
}
