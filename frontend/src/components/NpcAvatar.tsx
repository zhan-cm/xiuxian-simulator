import { useMemo } from 'react'
import type { NpcLifeProfile } from '../api/types'
import guQingxuanImg from '../assets/avatars/gu_qingxuan.jpg'
import baiNingshuangImg from '../assets/avatars/bai_ningshuang.jpg'
import yunQiImg from '../assets/avatars/yun_qi.jpg'
import xieWujiuImg from '../assets/avatars/xie_wujiu.jpg'

export const NPC_PORTRAIT_IMAGES: Record<string, string> = {
  顾清玄: guQingxuanImg,
  白凝霜: baiNingshuangImg,
  云栖: yunQiImg,
  谢无咎: xieWujiuImg,
}

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
    robeInner: string
    robeTrim: string
    auraColor: string
    hairColor: string
    hairHighlight: string
    skinColor: string
    eyeColorTop: string
    eyeColorMid: string
    eyeColorBottom: string
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
      bgGradient: 'radial-gradient(circle at 50% 25%, #244b3c, #11261e)',
      robeColor: '#edf7f3',
      robeInner: '#ffffff',
      robeTrim: '#3e7c65',
      auraColor: '#68c49e',
      hairColor: '#17221e',
      hairHighlight: '#9ce0c4',
      skinColor: '#fdf7ef',
      eyeColorTop: '#142b22',
      eyeColorMid: '#24624b',
      eyeColorBottom: '#52b788',
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
      bgGradient: 'radial-gradient(circle at 50% 25%, #5e3328, #2b1612)',
      robeColor: '#96392b',
      robeInner: '#fff7eb',
      robeTrim: '#e0ab34',
      auraColor: '#f0b348',
      hairColor: '#1a1617',
      hairHighlight: '#f5c364',
      skinColor: '#fff5ec',
      eyeColorTop: '#2b140b',
      eyeColorMid: '#823e19',
      eyeColorBottom: '#e69022',
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
      bgGradient: 'radial-gradient(circle at 50% 25%, #4a1920, #1d090d)',
      robeColor: '#241a20',
      robeInner: '#45161b',
      robeTrim: '#c72e2e',
      auraColor: '#e0383b',
      hairColor: '#120d12',
      hairHighlight: '#993339',
      skinColor: '#f7ebe5',
      eyeColorTop: '#290b0d',
      eyeColorMid: '#8f1c21',
      eyeColorBottom: '#e8383e',
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
    description: '三千银丝整饬如瀑，眸中浮动着剔透冰蓝色微光；身着轻若蝉翼的霜白羽裳，周身常年有凝而不散的极寒雪花轻轻旋落，清冷脱俗。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #254759, #101f27)',
      robeColor: '#f0f8fc',
      robeInner: '#ffffff',
      robeTrim: '#6eb5d1',
      auraColor: '#9ce0f5',
      hairColor: '#e7f3f7',
      hairHighlight: '#ffffff',
      skinColor: '#f9fcff',
      eyeColorTop: '#102733',
      eyeColorMid: '#246b8c',
      eyeColorBottom: '#5ecbf0',
      sealColor: '#63bcdb',
    },
  },
  墨尘: {
    gender: '男',
    path: 'beast',
    temperament: 'valiant',
    archetypeLabel: '古妖少主',
    temperamentLabel: '狂野桀骜 · 少年锐气',
    featureLabel: '墨玉兽角 · 玄骨链坠',
    summary: '墨发微卷，双眸闪烁兽性金瞳',
    description: '发间隐现两支精致微翘的墨玉龙角，眼瞳闪烁着琥珀般的璀璨金芒；衣襟微敞，露出雕琢妖兽图腾的骨链挂坠，满是少年妖修的骄横不羁。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #3c4420, #191c0c)',
      robeColor: '#2b3323',
      robeInner: '#e8deb8',
      robeTrim: '#bfa036',
      auraColor: '#a8ba32',
      hairColor: '#171614',
      hairHighlight: '#68603c',
      skinColor: '#f2e2d0',
      eyeColorTop: '#2b2609',
      eyeColorMid: '#876918',
      eyeColorBottom: '#e6ba22',
      sealColor: '#c09836',
    },
  },
  洛浅浅: {
    gender: '女',
    path: 'charm',
    temperament: 'charm',
    archetypeLabel: '合欢妙姝',
    temperamentLabel: '桃腮带笑 · 娇媚入骨',
    featureLabel: '银铃流苏 · 绯粉罗裙',
    summary: '粉罗挽臂，笑意盈盈乱人道心',
    description: '青丝以合欢彩缎松松绾就，步履间银铃脆响；眼尾勾着一抹浅浅胭脂，一颦一笑皆有摄人心魄的灵动魅意，令人望之忘俗。',
    theme: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #592942, #26111d)',
      robeColor: '#fbeef4',
      robeInner: '#ffffff',
      robeTrim: '#d1588c',
      auraColor: '#f598c0',
      hairColor: '#22161e',
      hairHighlight: '#e08ba7',
      skinColor: '#fff2f2',
      eyeColorTop: '#2d0f1f',
      eyeColorMid: '#912b5f',
      eyeColorBottom: '#ed589e',
      sealColor: '#d65886',
    },
  },
}

export function deduceNpcAppearance(
  profile?: Partial<NpcLifeProfile>,
  item?: { name?: string; identity?: string; descriptor?: string; realm?: string; affinity?: number }
): NpcAppearanceData {
  const name = profile?.name || item?.name || '同道修者'
  const identity = profile?.identity || item?.identity || item?.descriptor || ''
  const gender = (profile?.gender || (identity.includes('女') ? '女' : '男')) as '男' | '女'
  const realm = profile?.realm || item?.realm || '练气'
  const age = profile?.age || 28
  const likes = (profile?.likes || []).join(' ')
  const events = (profile?.life_events || []).join(' ')
  const isGhost = profile?.alive === false
  const isWounded = Boolean(profile?.wounded || profile?.status?.includes('伤') || profile?.status?.includes('危'))

  // 1. Check known core NPCs
  if (KNOWN_PROFILES[name]) {
    const known = KNOWN_PROFILES[name]
    const theme = {
      bgGradient: known.theme?.bgGradient || 'radial-gradient(circle at 50% 25%, #2a5242, #142a22)',
      robeColor: known.theme?.robeColor || '#eef6f2',
      robeInner: known.theme?.robeInner || '#ffffff',
      robeTrim: known.theme?.robeTrim || '#3e765f',
      auraColor: known.theme?.auraColor || '#68b896',
      hairColor: known.theme?.hairColor || '#1a221f',
      hairHighlight: known.theme?.hairHighlight || '#80c2a5',
      skinColor: known.theme?.skinColor || '#fcf6ed',
      eyeColorTop: known.theme?.eyeColorTop || '#142b22',
      eyeColorMid: known.theme?.eyeColorMid || '#24624b',
      eyeColorBottom: known.theme?.eyeColorBottom || '#52b788',
      sealColor: known.theme?.sealColor || '#4f9e78',
    }

    return {
      name,
      gender: known.gender || gender,
      ageGroup: 'prime',
      path: known.path || 'orthodox',
      temperament: known.temperament || 'gentle',
      archetypeLabel: known.archetypeLabel || '名门翘楚',
      temperamentLabel: known.temperamentLabel || '风华绝代 · 神韵超然',
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

  // 2. Dynamic archetype & path deduction
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

  const themes: Record<NpcAppearanceData['path'], NpcAppearanceData['theme']> = {
    sword: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #244b3c, #11261e)',
      robeColor: '#edf7f3',
      robeInner: '#ffffff',
      robeTrim: '#3e7c65',
      auraColor: '#68c49e',
      hairColor: '#17221e',
      hairHighlight: '#9ce0c4',
      skinColor: '#fdf7ef',
      eyeColorTop: '#142b22',
      eyeColorMid: '#24624b',
      eyeColorBottom: '#52b788',
      sealColor: '#4f9e78',
    },
    demonic: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #4a1920, #1d090d)',
      robeColor: '#241a20',
      robeInner: '#45161b',
      robeTrim: '#c72e2e',
      auraColor: '#e0383b',
      hairColor: '#120d12',
      hairHighlight: '#993339',
      skinColor: '#f7ebe5',
      eyeColorTop: '#290b0d',
      eyeColorMid: '#8f1c21',
      eyeColorBottom: '#e8383e',
      sealColor: '#d82e2e',
    },
    alchemy: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #264a35, #12241a)',
      robeColor: '#e7f5ec',
      robeInner: '#ffffff',
      robeTrim: '#43805c',
      auraColor: '#70c78e',
      hairColor: '#1b211c',
      hairHighlight: '#82cca0',
      skinColor: '#fbf7ee',
      eyeColorTop: '#173022',
      eyeColorMid: '#2e6b46',
      eyeColorBottom: '#60c986',
      sealColor: '#4cb072',
    },
    merchant: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #593922, #26160b)',
      robeColor: '#964828',
      robeInner: '#fff6e8',
      robeTrim: '#dbab3b',
      auraColor: '#e8af46',
      hairColor: '#1a1613',
      hairHighlight: '#f2bd5a',
      skinColor: '#fff5ec',
      eyeColorTop: '#2b170a',
      eyeColorMid: '#824218',
      eyeColorBottom: '#e89423',
      sealColor: '#d6a836',
    },
    snow_saint: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #234557, #0e1d24)',
      robeColor: '#edf7fc',
      robeInner: '#ffffff',
      robeTrim: '#68aebd',
      auraColor: '#93dbf0',
      hairColor: isOld ? '#f0f5f7' : '#22282d',
      hairHighlight: '#ffffff',
      skinColor: '#f9fcff',
      eyeColorTop: '#102733',
      eyeColorMid: '#246b8c',
      eyeColorBottom: '#5ecbf0',
      sealColor: '#7bc8e2',
    },
    beast: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #3c4420, #191c0c)',
      robeColor: '#2b3323',
      robeInner: '#e8deb8',
      robeTrim: '#bfa036',
      auraColor: '#a8ba32',
      hairColor: '#171614',
      hairHighlight: '#68603c',
      skinColor: '#f2e2d0',
      eyeColorTop: '#2b2609',
      eyeColorMid: '#876918',
      eyeColorBottom: '#e6ba22',
      sealColor: '#c09836',
    },
    charm: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #592942, #26111d)',
      robeColor: '#fbeef4',
      robeInner: '#ffffff',
      robeTrim: '#d1588c',
      auraColor: '#f598c0',
      hairColor: '#22161e',
      hairHighlight: '#e08ba7',
      skinColor: '#fff2f2',
      eyeColorTop: '#2d0f1f',
      eyeColorMid: '#912b5f',
      eyeColorBottom: '#ed589e',
      sealColor: '#d65886',
    },
    orthodox: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #30473a, #14211a)',
      robeColor: '#eff2ec',
      robeInner: '#ffffff',
      robeTrim: '#6e6044',
      auraColor: '#c9a85b',
      hairColor: '#1c211d',
      hairHighlight: '#9eb5a5',
      skinColor: '#fdf7ef',
      eyeColorTop: '#17241c',
      eyeColorMid: '#395442',
      eyeColorBottom: '#77a886',
      sealColor: '#b89445',
    },
    rogue: {
      bgGradient: 'radial-gradient(circle at 50% 25%, #3d3424, #1a150c)',
      robeColor: '#42372c',
      robeInner: '#f0e6d5',
      robeTrim: '#967a4e',
      auraColor: '#baa06b',
      hairColor: '#1c1a17',
      hairHighlight: '#8a7962',
      skinColor: '#f0e0d0',
      eyeColorTop: '#241a0e',
      eyeColorMid: '#634b2c',
      eyeColorBottom: '#b58e57',
      sealColor: '#9e7b44',
    },
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
    theme: themes[path],
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
  const imageSrc = NPC_PORTRAIT_IMAGES[name]

  // If high-resolution 2D anime visual novel artwork is registered for this character
  if (imageSrc) {
    return (
      <div
        className={`npc-avatar-box anime-photo-box size-${size} ${className}`}
        data-size={size}
        data-path={path}
        data-alive={!isGhost}
        data-wounded={isWounded || undefined}
        title={`${name} · ${data.archetypeLabel} (${data.temperamentLabel})`}
        aria-label={`${name}肖像`}
      >
        <img
          src={imageSrc}
          alt={`${name}立绘`}
          className="npc-avatar-img"
          loading="lazy"
        />
        <div className="npc-avatar-lighting-overlay" aria-hidden="true" />
        {isGhost && <div className="npc-avatar-ghost-veil" aria-hidden="true" />}
        <span className="npc-avatar-seal" aria-hidden="true">
          {name.slice(0, 1)}
        </span>
      </div>
    )
  }

  // Otherwise, render our bespoke high-fidelity 2D Anime Vector Portrait
  return (
    <div
      className={`npc-avatar-box anime-vector-box size-${size} ${className}`}
      data-size={size}
      data-path={path}
      data-alive={!isGhost}
      data-wounded={isWounded || undefined}
      title={`${name} · ${data.archetypeLabel} (${data.temperamentLabel})`}
      style={{
        background: theme.bgGradient,
      }}
      aria-label={`${name}肖像`}
    >
      <svg
        className="npc-avatar-svg"
        viewBox="0 0 160 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <defs>
          {/* 动漫眼眸绚丽多层渐变 */}
          <linearGradient id={`eyeGrad-${name}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={theme.eyeColorTop} />
            <stop offset="42%" stopColor={theme.eyeColorMid} />
            <stop offset="100%" stopColor={theme.eyeColorBottom} />
          </linearGradient>

          {/* 动漫发丝丝光渐变 */}
          <linearGradient id={`hairGrad-${name}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={theme.hairColor} />
            <stop offset="28%" stopColor={theme.hairHighlight} />
            <stop offset="55%" stopColor={theme.hairColor} />
            <stop offset="100%" stopColor="#0d100e" />
          </linearGradient>

          {/* 肤色柔光渐变 */}
          <radialGradient id={`skinGrad-${name}`} cx="50%" cy="38%" r="62%">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.3" />
            <stop offset="55%" stopColor={theme.skinColor} />
            <stop offset="100%" stopColor="#edd8c4" />
          </radialGradient>

          {/* 少女粉嫩腮红 */}
          <radialGradient id={`blushGrad-${name}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#ff708a" stopOpacity="0.42" />
            <stop offset="100%" stopColor="#ff708a" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* 1. 后景：灵光光环与五行气象粒子 */}
        <circle cx="80" cy="74" r="58" fill={theme.auraColor} fillOpacity="0.16" />
        <circle cx="80" cy="74" r="66" stroke={theme.auraColor} strokeWidth="1" strokeDasharray="3 4" opacity="0.32" />

        {/* 剑修：悬浮灵剑青芒 */}
        {path === 'sword' && (
          <g opacity="0.75">
            <path d="M125 18L121 82L119 81L123 17Z" fill="#a7f3d0" />
            <circle cx="122" cy="50" r="1.5" fill="#ffffff" />
          </g>
        )}
        {/* 雪族：冰晶飞雪 */}
        {path === 'snow_saint' && (
          <g stroke="#9ce0f5" strokeWidth="1.2" opacity="0.8">
            <path d="M30 35L36 41M36 35L30 41M33 32V44M27 38H39" />
            <circle cx="130" cy="30" r="1.5" fill="#ffffff" />
            <circle cx="120" cy="55" r="1.2" fill="#9ce0f5" />
          </g>
        )}
        {/* 妖族 / 墨尘：发间微翘墨玉龙角 */}
        {(path === 'beast' || name === '墨尘') && (
          <g>
            <path d="M48 38 C40 26 34 16 37 10 C41 8 46 16 52 28 Z" fill="#181d16" stroke="#4a5a3a" strokeWidth="1.2" />
            <path d="M112 38 C120 26 126 16 123 10 C119 8 114 16 108 28 Z" fill="#181d16" stroke="#4a5a3a" strokeWidth="1.2" />
            <line x1="42" y1="20" x2="47" y2="24" stroke="#a8ba32" strokeWidth="1" opacity="0.7" />
            <line x1="118" y1="20" x2="113" y2="24" stroke="#a8ba32" strokeWidth="1" opacity="0.7" />
          </g>
        )}
        {/* 合欢 / 洛浅浅：飘落桃花与摄魄魅影灵光 */}
        {(path === 'charm' || name === '洛浅浅') && (
          <g opacity="0.75">
            <path d="M28 42 Q33 37 36 42 Q38 47 33 49 Q28 47 28 42 Z" fill="#fb7185" />
            <path d="M132 50 Q137 45 140 50 Q142 55 137 57 Q132 55 132 50 Z" fill="#fb7185" />
            <circle cx="124" cy="28" r="2.2" fill="#f472b6" />
            <circle cx="34" cy="74" r="1.8" fill="#fda4af" />
          </g>
        )}

        {/* 2. 背景长发 */}
        {isFemale ? (
          <g fill={theme.hairColor}>
            <path d="M48 58 C38 88 32 128 36 170 C52 174 64 170 70 166 C60 128 58 88 56 58 Z" />
            <path d="M112 58 C122 88 128 128 124 170 C108 174 96 170 90 166 C100 128 102 88 104 58 Z" />
          </g>
        ) : (
          <g fill={theme.hairColor}>
            <path d="M52 60 C42 85 40 125 44 160 C54 162 62 160 66 156 C58 125 58 88 56 60 Z" />
            <path d="M108 60 C118 85 120 125 116 160 C106 162 98 160 94 156 C102 125 102 88 104 60 Z" />
          </g>
        )}

        {/* 3. 颈项与锁骨阴影 */}
        <path d="M68 108 L68 142 L92 142 L92 108 Z" fill={theme.skinColor} />
        {/* 下巴在颈部的精妙动漫投影 */}
        <polygon points="72,118 80,132 88,118" fill="#dfc0aa" opacity="0.65" />

        {/* 4. 躯干道袍与交领右衽 (古典汉家道服层次) */}
        <path
          d="M20 200 C22 162 38 140 60 134 L80 148 L100 134 C122 140 138 162 140 200 Z"
          fill={theme.robeColor}
        />
        {/* 内衬雪白交领 */}
        <polygon points="66,136 80,154 94,136 98,142 80,162 62,142" fill={theme.robeInner} />
        {/* 右衽前襟主襟边（镶嵌金丝或云纹） */}
        <path d="M60 134 L83 166 L100 134" stroke={theme.robeTrim} strokeWidth="3.5" strokeLinecap="round" fill="none" />
        <path d="M62 135 L82 163" stroke="#e8c76b" strokeWidth="1.2" opacity="0.75" />
        <path d="M80 166 V200" stroke={theme.robeTrim} strokeWidth="2.2" />

        {/* 胸前佩玉吊坠 / 墨尘玄骨链坠 */}
        {name === '墨尘' ? (
          <g>
            <path d="M72 166 L80 178 L88 166" stroke="#4a3b2c" strokeWidth="1.2" fill="none" />
            <polygon points="77,176 80,188 83,176" fill="#fdfbf7" stroke="#bda682" strokeWidth="1" />
          </g>
        ) : (
          <>
            <circle cx="80" cy="172" r="3.5" fill={theme.sealColor} />
            <path d="M80 175 V184" stroke={theme.sealColor} strokeWidth="1.2" />
          </>
        )}

        {/* 5. 动漫精致 V 脸下颌与面部基底 */}
        <path
          d="M50 70 C50 102 62 124 80 130 C98 124 110 102 110 70 C110 44 50 44 50 70 Z"
          fill={`url(#skinGrad-${name})`}
          stroke="#d2b39e"
          strokeWidth="1.2"
        />

        {/* 长者胡须 */}
        {isElder && (
          <path
            d="M66 112 C64 135 74 165 80 176 C86 165 96 135 94 112 Z"
            fill="#e2ece8"
            stroke="#c4d5d0"
            strokeWidth="1.2"
          />
        )}

        {/* 精致耳廓与耳饰 */}
        <path d="M49 74 C46 74 45 84 50 88 M111 74 C114 74 115 84 110 88" stroke="#cca78f" strokeWidth="1.2" fill={theme.skinColor} />
        {isFemale && (
          <g fill={name === '洛浅浅' ? '#e2e8f0' : theme.sealColor}>
            <circle cx="47" cy="90" r="1.8" />
            <path d="M47 91 L47 96" stroke={name === '洛浅浅' ? '#f43f5e' : theme.sealColor} strokeWidth="0.9" />
            {name === '洛浅浅' && <circle cx="47" cy="97" r="2.2" fill="#f8fafc" stroke="#cbd5e1" strokeWidth="0.6" />}
            <circle cx="113" cy="90" r="1.8" />
            <path d="M113 91 L113 96" stroke={name === '洛浅浅' ? '#f43f5e' : theme.sealColor} strokeWidth="0.9" />
            {name === '洛浅浅' && <circle cx="113" cy="97" r="2.2" fill="#f8fafc" stroke="#cbd5e1" strokeWidth="0.6" />}
          </g>
        )}

        {/* 少女粉嫩腮红与漫画小羞线 */}
        {isFemale && (
          <g>
            <ellipse cx="61" cy="96" rx="9" ry="4.5" fill={`url(#blushGrad-${name})`} />
            <ellipse cx="99" cy="96" rx="9" ry="4.5" fill={`url(#blushGrad-${name})`} />
            <path d="M58 95L60 98 M62 95L64 98" stroke="#f43f5e" strokeWidth="0.8" strokeLinecap="round" opacity="0.6" />
            <path d="M96 95L98 98 M100 95L102 98" stroke="#f43f5e" strokeWidth="0.8" strokeLinecap="round" opacity="0.6" />
          </g>
        )}

        {/* 6. 2D 动漫迷人眼睛 (左眼与右眼，大眼灵眸、渐变虹膜、多层高光) */}
        {/* 左眼 */}
        <g>
          {/* 眼白 */}
          <ellipse cx="66" cy="86" rx="8" ry="9.5" fill="#fcfdff" />
          {/* 渐变虹膜 */}
          <ellipse cx="66.5" cy="86.5" rx="6.5" ry="8.5" fill={`url(#eyeGrad-${name})`} />
          {/* 深邃黑瞳孔 */}
          <ellipse cx="66.5" cy="86" rx="3.2" ry="4.5" fill="#14181f" />
          {/* 底部月牙返光 */}
          <path d="M62 89 C64.5 93, 68.5 93, 71 89" stroke="#ffffff" strokeWidth="1.2" fill="none" opacity="0.55" />
          {/* 主高光（大亮光斑） */}
          <ellipse cx="64" cy="82.5" rx="2.4" ry="3.2" fill="#ffffff" />
          {/* 副高光（次光斑） */}
          <circle cx="69" cy="89" r="1.4" fill="#ffffff" opacity="0.9" />
          {/* 上眼睫毛与眼线（赛璐珞风酷黑翘尾） */}
          <path d="M56 83 C61 77 71 77 76 81 L77 79" stroke="#1c201d" strokeWidth="2.4" strokeLinecap="round" fill="none" />
          {/* 双眼皮褶皱 */}
          <path d="M59 75 C64 72 70 72 74 75" stroke="#786c62" strokeWidth="0.9" strokeLinecap="round" fill="none" opacity="0.65" />
          {/* 下眼线 */}
          <path d="M61 93.5 C64 94.5 68 94.5 71 93" stroke="#4a3e35" strokeWidth="1" strokeLinecap="round" fill="none" />
        </g>

        {/* 右眼 */}
        <g>
          {/* 眼白 */}
          <ellipse cx="94" cy="86" rx="8" ry="9.5" fill="#fcfdff" />
          {/* 渐变虹膜 */}
          <ellipse cx="93.5" cy="86.5" rx="6.5" ry="8.5" fill={`url(#eyeGrad-${name})`} />
          {/* 深邃黑瞳孔 */}
          <ellipse cx="93.5" cy="86" rx="3.2" ry="4.5" fill="#14181f" />
          {/* 底部月牙返光 */}
          <path d="M89 89 C91.5 93, 95.5 93, 98 89" stroke="#ffffff" strokeWidth="1.2" fill="none" opacity="0.55" />
          {/* 主高光 */}
          <ellipse cx="91.5" cy="82.5" rx="2.4" ry="3.2" fill="#ffffff" />
          {/* 副高光 */}
          <circle cx="96" cy="89" r="1.4" fill="#ffffff" opacity="0.9" />
          {/* 上眼睫毛与眼线 */}
          <path d="M104 83 C99 77 89 77 84 81 L83 79" stroke="#1c201d" strokeWidth="2.4" strokeLinecap="round" fill="none" />
          {/* 双眼皮褶皱 */}
          <path d="M101 75 C96 72 90 72 86 75" stroke="#786c62" strokeWidth="0.9" strokeLinecap="round" fill="none" opacity="0.65" />
          {/* 下眼线 */}
          <path d="M99 93.5 C96 94.5 92 94.5 89 93" stroke="#4a3e35" strokeWidth="1" strokeLinecap="round" fill="none" />
        </g>

        {/* 7. 优雅眉形 */}
        <g stroke={isElder ? '#a8b6b2' : theme.hairColor} strokeWidth={isFemale ? '1.4' : '2'} strokeLinecap="round" fill="none">
          <path d="M57 73 C62 68 70 69 75 72" />
          <path d="M103 73 C98 68 90 69 85 72" />
        </g>

        {/* 8. 精巧动漫微鼻 */}
        <path d="M80 93 L78.5 97" stroke="#cca187" strokeWidth="1.3" strokeLinecap="round" />

        {/* 9. 灵动微唇 */}
        <path
          d={isFemale ? 'M75 106 C78 108 82 108 85 106' : 'M74 106 C78 107.5 82 107.5 86 106'}
          stroke={isFemale ? '#e0586e' : '#a86558'}
          strokeWidth={isFemale ? '1.8' : '1.4'}
          strokeLinecap="round"
          fill="none"
        />
        {isFemale && <ellipse cx="80" cy="108" rx="2" ry="0.8" fill="#ffffff" opacity="0.5" />}

        {/* 10. 特殊印记（道印/战痕/天劫） */}
        {hasDaoSeal && (
          <path d="M80 62 L82.5 67 L80 69 L77.5 67 Z" fill={theme.sealColor} />
        )}
        {hasBattleScar && (
          <path d="M68 68 L73 75" stroke="#be2e2e" strokeWidth="1.4" strokeLinecap="round" opacity="0.85" />
        )}

        {/* 11. 前发、刘海与发饰 (修仙 2D 动漫标志性碎发与发髻) */}
        {isFemale ? (
          <g fill={theme.hairColor}>
            {/* 发髻 */}
            <ellipse cx="80" cy="38" rx="26" ry="18" />
            {/* 金钗步摇/发簪 */}
            <path d="M54 36 H106" stroke="#e8c258" strokeWidth="2.2" strokeLinecap="round" />
            <circle cx="106" cy="36" r="3.2" fill="#e8c258" />
            <path d="M106 38 L106 46" stroke="#e8c258" strokeWidth="1" />
            <circle cx="106" cy="47" r="1.8" fill={theme.sealColor} />

            {/* 前额 M 型修颜刘海与碎发 */}
            <path d="M46 54 C48 76 56 94 56 108 C58 94 62 76 66 64 C70 82 76 96 80 102 C84 96 90 82 94 64 C98 76 102 94 104 108 C104 94 112 76 114 54 C110 44 50 44 46 54 Z" />
            {/* 左右护颊姬发式长碎发 */}
            <path d="M46 62 C44 94 48 126 52 144 C54 126 56 94 56 62 Z" />
            <path d="M114 62 C116 94 112 126 108 144 C106 126 104 94 104 62 Z" />
          </g>
        ) : (
          <g fill={theme.hairColor}>
            {/* 道冠玉簪发髻 */}
            <path d="M68 38 C68 24 92 24 92 38 Z" />
            <path d="M62 33 H98" stroke={path === 'sword' ? '#86efac' : '#d4af37'} strokeWidth="2.2" strokeLinecap="round" />
            <circle cx="98" cy="33" r="2.5" fill={path === 'sword' ? '#86efac' : '#d4af37'} />

            {/* 男主帅气分层碎发 */}
            <path d="M46 56 C48 74 54 88 58 98 C62 88 64 74 68 62 C72 78 78 92 80 96 C82 92 88 78 92 62 C96 74 98 88 102 98 C106 88 112 74 114 56 C108 46 52 46 46 56 Z" />
            {/* 鬓角剑眉修饰发束 */}
            <path d="M48 64 C46 92 50 120 54 136 C56 120 58 92 58 64 Z" />
            <path d="M112 64 C114 92 110 120 106 136 C104 120 102 92 102 64 Z" />
          </g>
        )}

        {/* 动漫发丝高光光环（天使光圈 Angel Ring） */}
        <path
          d="M58 55 Q80 46 102 55"
          stroke="#ffffff"
          strokeWidth="2.2"
          strokeDasharray="2 3"
          strokeLinecap="round"
          opacity="0.5"
        />

        {/* 故人坐化水墨幽冥覆层 */}
        {isGhost && (
          <rect x="0" y="0" width="160" height="200" fill="#0f1f18" fillOpacity="0.38" />
        )}
      </svg>

      {/* 右下角朱砂小印 */}
      <span className="npc-avatar-seal" aria-hidden="true">
        {name.slice(0, 1)}
      </span>
    </div>
  )
}
