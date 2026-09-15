import { useMemo } from 'react'
import type { NpcLifeProfile } from '../api/types'

export interface NpcAppearanceData {
  name: string
  gender: '男' | '女'
  ageGroup: 'youth' | 'prime' | 'mature' | 'elder'
  path: 'sword' | 'alchemy' | 'demonic' | 'snow_saint' | 'merchant' | 'beast' | 'charm' | 'orthodox' | 'rogue'
  temperament: 'aloof' | 'gentle' | 'fierce' | 'cunning' | 'valiant' | 'charm'
  archetypeLabel: string
  temperamentLabel: string
  featureLabel: string
  description: string
  summary: string
  theme: {
    bgGradient: string
    robeColor: string
    robeTrim: string
    auraColor: string
    hairColor: string
    skinColor: string
    eyeColor: string
    sealColor: string
  }
  hasBattleScar: boolean
  hasThunderMark: boolean
  hasDaoSeal: boolean
  isGhost: boolean
  isWounded: boolean
}

const KNOWN_PROFILES: Record<string, Partial<NpcAppearanceData>> = {
  顾清玄: {
    gender: '男',
    path: 'sword',
    temperament: 'gentle',
    archetypeLabel: '温润剑修',
    temperamentLabel: '剑意内敛 · 眸澄若水',
    featureLabel: '青云玉簪 · 素白剑袍',
    summary: '白衣胜雪，剑气温润如玉',
    description: '头戴青云玉簪，剑眉星目，面庞俊朗清逸；一袭素白剑袍迎风微拂，眸光温润澄澈，虽负绝世锋芒却不带半分盛气凌人之意。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #2a5242, #142a22)',
      robeColor: '#eef6f2',
      robeTrim: '#3e765f',
      auraColor: '#68b896',
      hairColor: '#1a221f',
      skinColor: '#fcf6ed',
      eyeColor: '#274b3c',
      sealColor: '#4f9e78',
    },
  },
  云栖: {
    gender: '女',
    path: 'merchant',
    temperament: 'cunning',
    archetypeLabel: '天机灵贾',
    temperamentLabel: '明眸善睐 · 蕙质兰心',
    featureLabel: '金凤流苏 · 绯红云锦',
    summary: '金钗步摇，眼波流转若秋水',
    description: '梳着流云飞天髻，斜插金雀步摇，明眸如一泓秋水般顾盼生辉；身披绯红流金轻罗羽衣，嘴角噙着一抹若有若无的聪慧浅笑。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #66382b, #2c1915)',
      robeColor: '#9e3d2d',
      robeTrim: '#d6a836',
      auraColor: '#e2a33c',
      hairColor: '#1d191a',
      skinColor: '#fff5eb',
      eyeColor: '#702d1a',
      sealColor: '#d6a836',
    },
  },
  谢无咎: {
    gender: '男',
    path: 'demonic',
    temperament: 'fierce',
    archetypeLabel: '血煞魔君',
    temperamentLabel: '剑眉煞眸 · 桀骜狂狷',
    featureLabel: '玄黑战铠 · 幽血魔印',
    summary: '玄袍狂发，眉宇暗蕴血色煞芒',
    description: '乌发如夜披散肩头，剑眉斜飞入鬓，眼神孤鸷而凌厉；眉心隐现一缕淡淡赤血魔纹，一袭玄黑织金战袍暗蕴凶戾煞气，令人不敢逼视。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #471b21, #1e0b0e)',
      robeColor: '#261b21',
      robeTrim: '#b82e2e',
      auraColor: '#d83437',
      hairColor: '#130e13',
      skinColor: '#f4e9e3',
      eyeColor: '#8a1f23',
      sealColor: '#d82e2e',
    },
  },
  白凝霜: {
    gender: '女',
    path: 'snow_saint',
    temperament: 'aloof',
    archetypeLabel: '雪岭玄女',
    temperamentLabel: '冰肌玉骨 · 孤绝高蹈',
    featureLabel: '极北雪晶 · 霜白羽裳',
    summary: '银发如霜，眸若万载极寒玄冰',
    description: '银发如三千瀑雪倾泻，肤如凝脂、神若秋水；眉心凝结着一瓣六角极寒冰晶，一袭素白雪绡羽裳纤尘不染，周身散发着拒人于千里之外的冷艳与清辉。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #2a4754, #12222b)',
      robeColor: '#edf6fa',
      robeTrim: '#68a0b5',
      auraColor: '#93d4e8',
      hairColor: '#d7eaf2',
      skinColor: '#f9fcff',
      eyeColor: '#34667a',
      sealColor: '#7bc8e2',
    },
  },
  墨尘: {
    gender: '男',
    path: 'beast',
    temperament: 'valiant',
    archetypeLabel: '古妖少君',
    temperamentLabel: '金瞳桀骜 · 野性不羁',
    featureLabel: '兽牙金环 · 墨绿皮甲',
    summary: '金眸兽牙，英气勃发的桀骜少年',
    description: '短发凌乱而野性，额侧暗藏一缕妖族金鳞灵纹，一双金珀般的兽瞳灼灼生辉；身着兽皮护肩短褐，嘴角微撇挂着傲娇不屑，少年英气逼人。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #424622, #1c1d0e)',
      robeColor: '#303a29',
      robeTrim: '#c09836',
      auraColor: '#a8b638',
      hairColor: '#1d1b18',
      skinColor: '#eddccb',
      eyeColor: '#ba8e23',
      sealColor: '#c09836',
    },
  },
  洛浅浅: {
    gender: '女',
    path: 'charm',
    temperament: 'charm',
    archetypeLabel: '合欢仙姝',
    temperamentLabel: '桃花含露 · 娇媚多情',
    featureLabel: '粉蝶流苏 · 银铃红绦',
    summary: '桃腮带笑，腕间银铃清脆作响',
    description: '梳着娇俏的垂鬟分髾髻，鬓边点缀着粉嫩桃花珠钗；双眸水波盈盈、含情脉脉，粉白纱裙随风轻曳，腕间银铃清脆作响，嫣然一笑尽展万种风情。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #592e44, #27141e)',
      robeColor: '#f8e4ed',
      robeTrim: '#c45887',
      auraColor: '#f090b8',
      hairColor: '#20181c',
      skinColor: '#fff2f2',
      eyeColor: '#8a3c60',
      sealColor: '#d65886',
    },
  },
}

export function deduceNpcAppearance(
  profile?: Partial<NpcLifeProfile>,
  item?: { name?: string; identity?: string; descriptor?: string; realm?: string; affinity?: number }
): NpcAppearanceData {
  const name = String(profile?.name || item?.name || '无名道友')
  const gender = (profile?.gender === '女' || (item?.identity && item.identity.includes('女')) || name.includes('仙子') || name.includes('圣女')) ? '女' : '男'
  const identity = String(profile?.identity || item?.identity || item?.descriptor || '')
  const realm = String(profile?.realm || item?.realm || '练气')
  const age = Number(profile?.age || 26)
  const isWounded = Boolean(profile?.wounded || profile?.status?.includes('受创') || profile?.status?.includes('重伤'))
  const isGhost = Boolean(profile?.alive === false || profile?.status?.includes('已故') || profile?.status?.includes('坐化'))
  const likes = Array.isArray(profile?.likes) ? profile.likes.join('、') : ''
  const events = Array.isArray(profile?.life_events) ? profile.life_events.join('；') : ''

  // 1. Check known core NPC profiles
  const known = KNOWN_PROFILES[name]
  if (known) {
    const isOld = age > 180
    const theme = { ...known.theme! }
    if (isGhost) {
      theme.bgGradient = 'radial-gradient(circle at 50% 25%, #3a4240, #181d1c)'
      theme.robeColor = '#e2e7e5'
      theme.auraColor = '#8c9e99'
      theme.hairColor = '#808b88'
    } else if (isOld) {
      theme.hairColor = '#dce3e0'
    }
    return {
      name,
      gender: known.gender || gender,
      ageGroup: isOld ? 'elder' : age > 70 ? 'mature' : age > 26 ? 'prime' : 'youth',
      path: known.path || 'sword',
      temperament: known.temperament || 'gentle',
      archetypeLabel: known.archetypeLabel || '仙道高足',
      temperamentLabel: known.temperamentLabel || '风姿绰约',
      featureLabel: known.featureLabel || '仙姿佚貌',
      summary: known.summary || '风采斐然',
      description: known.description || `${name}姿容端正，气度沉稳，周身有淡淡灵机流转。`,
      theme,
      hasBattleScar: isWounded,
      hasThunderMark: events.includes('雷') || events.includes('劫'),
      hasDaoSeal: realm.includes('金丹') || realm.includes('元婴') || realm.includes('化神'),
      isGhost,
      isWounded,
    }
  }

  // 2. Dynamic archetype & path deduction from identity, likes, and life events
  const textPool = `${identity} ${likes} ${events} ${realm}`
  let path: NpcAppearanceData['path'] = 'orthodox'
  let archetypeLabel = gender === '女' ? '玄门女修' : '仙门真传'
  let temperament: NpcAppearanceData['temperament'] = 'gentle'
  let temperamentLabel = '温润端雅 · 气息绵长'
  let featureLabel = '青衫云带 · 灵簪束发'

  if (textPool.includes('剑') || textPool.includes('斩') || textPool.includes('锋') || textPool.includes('绝影')) {
    path = 'sword'
    archetypeLabel = gender === '女' ? '凌波剑仙' : '青峰剑修'
    temperament = 'aloof'
    temperamentLabel = '剑眉星目 · 孤傲如雪'
    featureLabel = '素白剑冠 · 负剑青锋'
  } else if (textPool.includes('魔') || textPool.includes('煞') || textPool.includes('血') || textPool.includes('阴') || textPool.includes('邪')) {
    path = 'demonic'
    archetypeLabel = gender === '女' ? '幽冥魔女' : '血煞魔修'
    temperament = 'fierce'
    temperamentLabel = '桀骜森冷 · 煞气流转'
    featureLabel = '玄黑战袍 · 暗红灵纹'
  } else if (textPool.includes('丹') || textPool.includes('药') || textPool.includes('医') || textPool.includes('草')) {
    path = 'alchemy'
    archetypeLabel = gender === '女' ? '百草灵医' : '妙手丹师'
    temperament = 'gentle'
    temperamentLabel = '春风化雨 · 仁心济世'
    featureLabel = '青玉药鼎 · 翠罗挂囊'
  } else if (textPool.includes('商') || textPool.includes('阁') || textPool.includes('宝') || textPool.includes('石') || textPool.includes('市')) {
    path = 'merchant'
    archetypeLabel = gender === '女' ? '金鳞商娘' : '天机掌柜'
    temperament = 'cunning'
    temperamentLabel = '精明敏达 · 谈笑自若'
    featureLabel = '锦缎华袍 · 灵玉扳指'
  } else if (textPool.includes('雪') || textPool.includes('冰') || textPool.includes('霜') || textPool.includes('寒')) {
    path = 'snow_saint'
    archetypeLabel = gender === '女' ? '极寒玄女' : '冰渊隐士'
    temperament = 'aloof'
    temperamentLabel = '清冷如月 · 纤尘不染'
    featureLabel = '冰丝羽衣 · 霜雪华簪'
  } else if (textPool.includes('妖') || textPool.includes('兽') || textPool.includes('荒') || textPool.includes('山')) {
    path = 'beast'
    archetypeLabel = gender === '女' ? '灵妖妙姝' : '狂野妖修'
    temperament = 'valiant'
    temperamentLabel = '野性桀骜 · 战意如炽'
    featureLabel = '兽牙挂坠 · 劲装护臂'
  } else if (textPool.includes('合欢') || textPool.includes('情') || textPool.includes('魅') || textPool.includes('红尘')) {
    path = 'charm'
    archetypeLabel = gender === '女' ? '红尘仙子' : '多情游侠'
    temperament = 'charm'
    temperamentLabel = '明眸如水 · 顾盼生姿'
    featureLabel = '粉罗羽裙 · 银铃流苏'
  } else if (textPool.includes('散') || textPool.includes('浪') || textPool.includes('酒') || textPool.includes('游')) {
    path = 'rogue'
    archetypeLabel = gender === '女' ? '四海侠女' : '落拓散修'
    temperament = 'valiant'
    temperamentLabel = '洒脱不羁 · 浪迹天涯'
    featureLabel = '青竹斗笠 · 腰悬酒葫'
  }

  const isOld = age > 180
  const ageGroup: NpcAppearanceData['ageGroup'] = isOld ? 'elder' : age > 70 ? 'mature' : age > 26 ? 'prime' : 'youth'
  if (isOld) {
    archetypeLabel = gender === '女' ? '世外道姑' : '玄门道翁'
    temperamentLabel = '鹤发童颜 · 仙风道骨'
    featureLabel = '素雪苍髯 · 紫金道袍'
  }

  // Generate appearance summary & detailed poetic description
  let summary = ''
  let description = ''
  if (isGhost) {
    summary = '魂光幽幽，此生已入轮回'
    description = `周身泛着淡淡水墨余韵，神情安详平和，唯留生前的一袭${featureLabel.split('·')[1]?.trim() || '道袍'}在记忆中依稀可辨。`
  } else if (isOld) {
    summary = '皓首长髯，深谙世事沧桑'
    description = `鹤发如霜雪般整饬束起，面容清癯却神光内敛；一袭宽大道袍飘飘若仙，目光如寒潭映月，透着看透红尘兴衰的通透与从容。`
  } else if (gender === '女') {
    summary = `${temperamentLabel.split('·')[0]?.trim()}，风采照人`
    description = `面容白皙若凝脂，眉如远山微黛，眼波流转含光；着一袭裁制精巧的${featureLabel.split('·')[1]?.trim() || '轻罗羽裳'}，神态${temperamentLabel.split('·')[0]?.trim() || '端庄'}，举止从容脱俗。`
  } else {
    summary = `${temperamentLabel.split('·')[0]?.trim()}，神气清朗`
    description = `身姿挺拔修长，颌下线条分明，目光深邃而有神采；身着${featureLabel.split('·')[1]?.trim() || '齐整道袍'}，周身隐隐散发着${archetypeLabel}特有的从容气度。`
  }

  if (isWounded) {
    description += ' 眉宇间隐带几分苍白虚弱之色，显是近期经历了一场凶险历练。'
  }

  // Theme palettes based on path
  const themes: Record<NpcAppearanceData['path'], NpcAppearanceData['theme']> = {
    sword: { bgGradient: 'radial-gradient(circle at 50% 25%, #24463a, #12241d)', robeColor: '#edf6f2', robeTrim: '#3e765f', auraColor: '#68b896', hairColor: '#1a221f', skinColor: '#fbf5eb', eyeColor: '#274b3c', sealColor: '#4f9e78' },
    demonic: { bgGradient: 'radial-gradient(circle at 50% 25%, #471b21, #1e0b0e)', robeColor: '#261b21', robeTrim: '#b82e2e', auraColor: '#d83437', hairColor: '#130e13', skinColor: '#f4e9e3', eyeColor: '#8a1f23', sealColor: '#d82e2e' },
    alchemy: { bgGradient: 'radial-gradient(circle at 50% 25%, #2d4c38, #15271d)', robeColor: '#e7f3ea', robeTrim: '#4a825e', auraColor: '#75be8c', hairColor: '#20221e', skinColor: '#faf6ee', eyeColor: '#305c41', sealColor: '#4cb072' },
    merchant: { bgGradient: 'radial-gradient(circle at 50% 25%, #593f24, #271a0e)', robeColor: '#9c4c28', robeTrim: '#d6a836', auraColor: '#e2a33c', hairColor: '#1c1815', skinColor: '#fff5ea', eyeColor: '#703c1b', sealColor: '#d6a836' },
    snow_saint: { bgGradient: 'radial-gradient(circle at 50% 25%, #264350, #101e24)', robeColor: '#edf6fa', robeTrim: '#68a0b5', auraColor: '#93d4e8', hairColor: isOld ? '#f0f5f7' : '#22282d', skinColor: '#f9fcff', eyeColor: '#34667a', sealColor: '#7bc8e2' },
    beast: { bgGradient: 'radial-gradient(circle at 50% 25%, #3c4422, #181c0d)', robeColor: '#323c28', robeTrim: '#c09836', auraColor: '#a8b638', hairColor: '#1d1b18', skinColor: '#eddccb', eyeColor: '#ba8e23', sealColor: '#c09836' },
    charm: { bgGradient: 'radial-gradient(circle at 50% 25%, #542c42, #24131c)', robeColor: '#f8e4ed', robeTrim: '#c45887', auraColor: '#f090b8', hairColor: '#20181c', skinColor: '#fff2f2', eyeColor: '#8a3c60', sealColor: '#d65886' },
    orthodox: { bgGradient: 'radial-gradient(circle at 50% 25%, #34483d, #17241d)', robeColor: '#f0ede4', robeTrim: '#705e3f', auraColor: '#c9a85b', hairColor: '#1e211e', skinColor: '#fcf6ee', eyeColor: '#455047', sealColor: '#b89445' },
    rogue: { bgGradient: 'radial-gradient(circle at 50% 25%, #403828, #1c1810)', robeColor: '#453c30', robeTrim: '#947a50', auraColor: '#b59765', hairColor: '#1e1c19', skinColor: '#ebdccb', eyeColor: '#5c4832', sealColor: '#9e7b44' },
  }

  const theme = { ...themes[path] }
  if (isOld) theme.hairColor = '#dce3e0'
  if (isGhost) {
    theme.bgGradient = 'radial-gradient(circle at 50% 25%, #38423f, #191e1d)'
    theme.robeColor = '#e2e7e5'
    theme.auraColor = '#8c9e99'
  }

  return {
    name,
    gender,
    ageGroup,
    path,
    temperament,
    archetypeLabel,
    temperamentLabel,
    featureLabel,
    summary,
    description,
    theme,
    hasBattleScar: isWounded,
    hasThunderMark: events.includes('雷') || events.includes('劫'),
    hasDaoSeal: realm.includes('金丹') || realm.includes('元婴') || realm.includes('化神'),
    isGhost,
    isWounded,
  }
}

export function NpcAvatar({
  profile,
  item,
  size = 'medium',
  className = '',
}: {
  profile?: Partial<NpcLifeProfile>
  item?: { name?: string; identity?: string; descriptor?: string; realm?: string; affinity?: number }
  size?: 'small' | 'medium' | 'large'
  className?: string
}) {
  const data = useMemo(() => deduceNpcAppearance(profile, item), [profile, item])
  const { gender, ageGroup, path, theme, hasBattleScar, hasDaoSeal, isGhost, isWounded, name } = data

  const isFemale = gender === '女'
  const isElder = ageGroup === 'elder'
  const isYouth = ageGroup === 'youth'

  return (
    <div
      className={`npc-avatar-box size-${size} ${className}`}
      data-path={path}
      data-alive={!isGhost}
      data-wounded={isWounded || undefined}
      title={`${name} · ${data.archetypeLabel} (${data.temperamentLabel})`}
      style={{
        background: theme.bgGradient,
      }}
    >
      <svg
        className="npc-avatar-svg"
        viewBox="0 0 100 125"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        {/* 1. 后景：道途祥云灵光光环 */}
        <circle cx="50" cy="46" r="36" fill={theme.auraColor} fillOpacity="0.18" />
        <circle cx="50" cy="46" r="42" stroke={theme.auraColor} strokeWidth="1" strokeDasharray="3 4" opacity="0.35" />

        {/* 剑修特殊悬剑虚影 */}
        {path === 'sword' && (
          <path d="M78 8L74 44L72 43L76 7Z" fill="#cce8db" fillOpacity="0.75" />
        )}
        {/* 雪族冰晶雪花 */}
        {path === 'snow_saint' && (
          <path d="M22 24L26 28M26 24L22 28M24 22V30M20 26H28" stroke="#a6e3f7" strokeWidth="1" opacity="0.65" />
        )}
        {/* 妖族灵耳轮廓 */}
        {path === 'beast' && (
          <g fill={theme.hairColor} opacity="0.9">
            <polygon points="34,22 28,8 39,17" />
            <polygon points="66,22 72,8 61,17" />
          </g>
        )}

        {/* 2. 背景长发 */}
        {isFemale ? (
          <path
            d="M32 36C28 48 24 72 26 95C34 98 42 96 46 95 M68 36C72 48 76 72 74 95C66 98 58 96 54 95"
            fill={theme.hairColor}
            stroke={theme.hairColor}
            strokeWidth="2"
            strokeLinejoin="round"
          />
        ) : (
          <path
            d="M35 38C30 52 28 72 32 88 M65 38C70 52 72 72 68 88"
            fill={theme.hairColor}
            stroke={theme.hairColor}
            strokeWidth="3"
            strokeLinecap="round"
          />
        )}

        {/* 3. 衣袍躯干与道袍领口 */}
        <path
          d="M12 125C14 102 24 88 38 84L50 94L62 84C76 88 86 102 88 125Z"
          fill={theme.robeColor}
          stroke={theme.robeTrim}
          strokeWidth="1.5"
        />
        {/* 交领右衽（传统汉服道服前襟） */}
        <path d="M38 84L52 108L62 84" fill="none" stroke={theme.robeTrim} strokeWidth="3" />
        <path d="M43 89L50 98L57 89" fill="none" stroke="#eed8a1" strokeWidth="1.4" opacity="0.75" />
        <path d="M50 98V125" stroke={theme.robeTrim} strokeWidth="1.8" />

        {/* 4. 颈项 */}
        <path d="M43 66V88H57V66Z" fill={theme.skinColor} />

        {/* 5. 颌下须髯（长者/老道专属） */}
        {isElder && (
          <path
            d="M42 66C40 82 46 106 50 114C54 106 60 82 58 66Z"
            fill="#dbe3e0"
            stroke="#b8c6c2"
            strokeWidth="1"
          />
        )}

        {/* 6. 面庞轮廓 */}
        <path
          d={
            isFemale
              ? 'M35 44C35 60 41 73 50 73C59 73 65 60 65 44C65 32 59 27 50 27C41 27 35 32 35 44Z'
              : isYouth
              ? 'M34 43C34 60 40 73 50 73C60 73 66 60 66 43C66 31 60 26 50 26C40 26 34 31 34 43Z'
              : 'M33 42C33 60 41 75 50 75C59 75 67 60 67 42C67 30 60 25 50 25C40 25 33 30 33 42Z'
          }
          fill={theme.skinColor}
          stroke={isGhost ? '#8a9c97' : '#cbb29b'}
          strokeWidth="1.2"
        />

        {/* 双耳 */}
        <path d="M33 46C31 46 31 54 34 56 M67 46C69 46 69 54 66 56" stroke="#cbb29b" strokeWidth="1.2" />

        {/* 女修耳坠步摇 */}
        {isFemale && (
          <g fill={theme.sealColor}>
            <circle cx="32" cy="58" r="1.5" />
            <path d="M32 59V64" stroke={theme.sealColor} strokeWidth="1" />
            <circle cx="68" cy="58" r="1.5" />
            <path d="M68 59V64" stroke={theme.sealColor} strokeWidth="1" />
          </g>
        )}

        {/* 7. 眉目神态 */}
        {/* 眉毛 */}
        {path === 'sword' || path === 'demonic' ? (
          <g stroke={isElder ? '#c2cec9' : '#1e1c18'} strokeWidth="2" strokeLinecap="round">
            <path d="M38 43L46 41" />
            <path d="M62 43L54 41" />
          </g>
        ) : isFemale ? (
          <g stroke={isElder ? '#c2cec9' : '#2a201c'} strokeWidth="1.4" strokeLinecap="round">
            <path d="M38 43C41 41 45 42 47 43" />
            <path d="M62 43C59 41 55 42 53 43" />
          </g>
        ) : (
          <g stroke={isElder ? '#c2cec9' : '#22201d'} strokeWidth="1.8" strokeLinecap="round">
            <path d="M38 43H47" />
            <path d="M62 43H53" />
          </g>
        )}

        {/* 眼睛 */}
        <g fill={theme.eyeColor}>
          <ellipse cx="42.5" cy="48" rx="3.2" ry="2.2" />
          <circle cx="43.5" cy="47.2" r="0.8" fill="#ffffff" />
          <ellipse cx="57.5" cy="48" rx="3.2" ry="2.2" />
          <circle cx="58.5" cy="47.2" r="0.8" fill="#ffffff" />
        </g>
        <path d="M38.5 47C41 45.5 45 46 46.5 47 M61.5 47C59 45.5 55 46 53.5 47" stroke="#3d352e" strokeWidth="1" fill="none" />

        {/* 鼻梁 */}
        <path d="M50 49V56L48.5 57" stroke="#caa78d" strokeWidth="1.1" strokeLinecap="round" />

        {/* 嘴唇 */}
        <path
          d="M46 63C48 64.5 52 64.5 54 63"
          stroke={isFemale ? '#c4586d' : '#ab7d6f'}
          strokeWidth={isFemale ? '1.8' : '1.3'}
          strokeLinecap="round"
          fill="none"
        />

        {/* 8. 经历印记：眉心灵印 / 战痕劫印 */}
        {hasDaoSeal && (
          <path d="M50 33L51.5 36.5L50 38L48.5 36.5Z" fill={theme.sealColor} />
        )}
        {hasBattleScar && (
          <path d="M43 38L47 43" stroke="#b33838" strokeWidth="1.2" strokeLinecap="round" opacity="0.85" />
        )}

        {/* 9. 前发与道冠发髻 */}
        {isFemale ? (
          <g fill={theme.hairColor}>
            <path d="M40 28C40 16 60 16 60 28Z" />
            <path d="M34 33C42 27 58 27 66 33C64 38 60 41 58 40C52 35 48 35 42 40C40 41 36 38 34 33Z" />
            <path d="M36 21H64" stroke="#e8c258" strokeWidth="1.8" strokeLinecap="round" />
            <circle cx="64" cy="21" r="2.2" fill="#e8c258" />
          </g>
        ) : (
          <g fill={theme.hairColor}>
            <path d="M43 27C43 18 57 18 57 27Z" />
            <path d="M39 23H61" stroke={path === 'sword' ? '#92c2af' : '#caa758'} strokeWidth="1.8" strokeLinecap="round" />
            <path d="M33 34C40 28 48 30 50 34C52 30 60 28 67 34C64 39 60 38 56 36C52 35 48 35 44 36C40 38 36 39 33 34Z" />
          </g>
        )}

        {/* 故人（坐化）幽水墨薄纱覆层 */}
        {isGhost && (
          <rect x="0" y="0" width="100" height="125" fill="#1b2923" fillOpacity="0.3" />
        )}
      </svg>

      {/* 底部名讳小印 (朱砂古印，既美观又一目了然) */}
      <span className="npc-avatar-seal" aria-hidden="true">
        {name.slice(0, 1)}
      </span>
    </div>
  )
}
