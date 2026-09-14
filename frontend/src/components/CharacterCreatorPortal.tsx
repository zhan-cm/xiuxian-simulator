import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import {
  Sparkles,
  Dice5,
  Check,
  ChevronRight,
  ChevronLeft,
  User,
  Shield,
  Zap,
  Flame,
  Award,
  Compass,
  Feather,
  CheckCircle2,
  AlertCircle,
  Gem,
} from 'lucide-react'

interface CharacterCreatorPortalProps {
  phase: string
  busy: boolean
  draft?: unknown
  onAction: (action: string) => void
}

// 姓氏与名字库
const FIRST_NAMES = ['陆', '叶', '楚', '林', '姜', '萧', '洛', '顾', '墨', '虞', '苏', '裴', '白', '燕', '谢', '宁', '沈', '莫', '唐', '云', '纪', '许', '温']
const GIVEN_NAMES = ['轻舟', '凌霄', '沉渊', '晚照', '问天', '青雪', '长歌', '清涟', '无双', '白', '无咎', '听雨', '随风', '知白', '玉衡', '渡', '惊鸿', '停云', '无暇', '天澜', '惊雷']

// 出身列表（与 character_creation.py 一致）
const BACKGROUNDS = [
  { key: '农家子', label: '农家子', icon: '🌾', bonus: '道心 +2', desc: '寒门薄田，心志坚毅，不易受外魔所惑' },
  { key: '猎户之后', label: '猎户之后', icon: '🏹', bonus: '气血上限 +20', desc: '山野竞走，搏杀猛兽，筋骨极为健硕' },
  { key: '商贾之家', label: '商贾之家', icon: '🪙', bonus: '灵石 +300、仙缘 +1', desc: '家资饶盈，随身资粮充足，善辨利市' },
  { key: '官宦子弟', label: '官宦子弟', icon: '📜', bonus: '声望 +20', desc: '门荫显赫，熟谙世故礼法，扬名九州' },
  { key: '将门之后', label: '将门之后', icon: '⚔️', bonus: '道心 +1、悟性 +1', desc: '兵法家传，沉稳多智，擅统筹攻伐' },
  { key: '没落世家', label: '没落世家', icon: '🏛️', bonus: '获得【先祖残卷】玄阶功法', desc: '虽门庭衰败，箱底尚遗留祖传修真道统' },
  { key: '市井孤儿', label: '市井孤儿', icon: '🏃', bonus: '遁速 +2', desc: '百家饭大，耳听八方，遇危逃遁机敏' },
  { key: '书香门第', label: '书香门第', icon: '📚', bonus: '悟性 +3', desc: '诗书传家，识文通达，参悟道法神速' },
  { key: '方外遗孤', label: '方外遗孤', icon: '🪨', bonus: '资质 +2', desc: '自幼沐天地之精，骨骼清奇暗具仙姿' },
  { key: '妖族后裔', label: '妖族后裔', icon: '🦊', bonus: '身负【半妖之身】异禀', desc: '体内流淌远古异兽真血，肉身潜能无尽' },
]

// 道途列表
const DAO_PATHS = [
  { key: '问道飞升', daoName: '清微', desc: '求索大道终极，以元神跨越仙凡天堑，执着飞升' },
  { key: '逍遥长生', daoName: '长闲', desc: '游弋大荒山海，不争浮名，求天地同寿长存' },
  { key: '快意恩仇', daoName: '照胆', desc: '胸中剑胆琴心，恩必偿仇必报，荡尽世间不平' },
  { key: '守护所爱', daoName: '守一', desc: '心系至亲同道，愿为遮风避雨，以此为道根' },
  { key: '问鼎天下', daoName: '凌霄', desc: '开宗立派统御八荒，俾睨群雄，制霸九州仙界' },
  { key: '随心所欲', daoName: '无拘', desc: '不拘正魔戒律，从心所欲而行，万法皆任我意' },
]

// 相貌等级
const APPEARANCE_LEVELS = [
  { level: '仙姿', template: '谪仙降世，清冷出尘，眸若含星' },
  { level: '超凡', template: '超凡脱俗，神光内蕴，丰神绝朗' },
  { level: '出众', template: '风骨秀异，眉目疏朗，神采奕奕' },
  { level: '清秀', template: '眉目清秀，神情沉静，质朴端方' },
  { level: '凡姿', template: '相貌平平，隐于市井，朴拙无奇' },
]

// 灵根预设
const SPIRITUAL_ROOTS = [
  { group: '天灵根（单一纯质）', items: ['金天灵根', '木天灵根', '水天灵根', '火天灵根', '土天灵根'] },
  { group: '异变灵根（天地异象）', items: ['风灵根', '雷灵根', '冰灵根'] },
  { group: '双灵根（相生互补）', items: ['木火双灵根', '金水双灵根', '水木双灵根', '火土双灵根', '金火双灵根'] },
  { group: '特殊混沌', items: ['五行混元灵根', '真灵根'] },
]

// 体质列表
const CONSTITUTIONS = [
  { name: '先天道体', tag: '修炼极速', effect: '修炼效率永久提升 50%，周天运转如神助' },
  { name: '剑灵体', tag: '剑道通玄', effect: '剑道亲和，研习御使剑法威能大幅跃迁' },
  { name: '九阳圣体', tag: '至阳至烈', effect: '体内真阳流转，所有火系杀伐与功法威力 +30%' },
  { name: '冰魄灵体', tag: '玄冥极寒', effect: '神识清明无垢，所有冰寒术法威力 +30%' },
  { name: '玄阴体', tag: '太阴蕴灵', effect: '天生具有双修奇效，可与同道互通灵性' },
  { name: '纯阳体', tag: '浩气长存', effect: '气机刚正不阿，同道论道与双修皆获丰厚回馈' },
  { name: '混沌体', tag: '万法归宗', effect: '五行皆通，全系术法与法宝皆能融会贯通' },
  { name: '凡体', tag: '厚积薄发', effect: '凡胎肉躯无异象，但道基稳固，大器晚成' },
]

// 六维定义
const ATTRIBUTE_DEFS = [
  { key: 'aptitude', label: '资质', desc: '影响修炼吐纳效率与破境根基' },
  { key: 'comprehension', label: '悟性', desc: '影响研习道法与武艺参悟领悟' },
  { key: 'spirit_sense', label: '神识', desc: '影响施法感知、探查秘境与感知' },
  { key: 'speed', label: '遁速', desc: '影响身法敏捷、先手权与危急脱身' },
  { key: 'dao_heart', label: '道心', desc: '影响抵抗心魔、重伤心防与问心试炼' },
  { key: 'fortune', label: '仙缘', desc: '影响天地机缘、奇遇偶得与天道庇佑' },
]

// 天赋列表
const TALENT_ITEMS = [
  { name: '天资聪颖', cost: 1, desc: '资质 +3，筋骨天成' },
  { name: '过目不忘', cost: 1, desc: '悟性 +3，博闻强识' },
  { name: '身轻如燕', cost: 1, desc: '遁速 +3，步履如风' },
  { name: '天生道心', cost: 1, desc: '道心 +3，心如止水' },
  { name: '气运加身', cost: 1, desc: '仙缘 +3，福泽延绵' },
  { name: '神识过人', cost: 1, desc: '神识 +3，感知敏锐' },
  { name: '百脉俱通', cost: 1, desc: '灵力上限 +50，真元充沛' },
  { name: '钢筋铁骨', cost: 1, desc: '气血上限 +80，生机旺盛' },
  { name: '药理通神', cost: 1, desc: '初始炼丹等级 1，熟通百草' },
  { name: '桃花运', cost: 1, desc: '初始同道好感 +20，人缘出众' },
  { name: '体弱多病', cost: -2, desc: '气血上限 -50，但返还 2 点天赋点数（可额外选 2 个正面天赋）' },
]

export function CharacterCreatorPortal({ phase, busy, draft, onAction }: CharacterCreatorPortalProps) {
  // 当前处于第一面还是第二面
  const isStepOne = phase === 'character_creation_basic' || !phase.includes('traits')

  const draftObj = draft && typeof draft === 'object' ? (draft as Record<string, unknown>) : null

  // 第一面状态（支持自 draft 恢复）
  const [name, setName] = useState(() => (draftObj?.name ? String(draftObj.name) : '林渡'))
  const [gender, setGender] = useState(() => (draftObj?.gender ? String(draftObj.gender) : '女'))
  const [age, setAge] = useState(() => (draftObj?.age ? Number(draftObj.age) : 18))
  const [appearanceLevel, setAppearanceLevel] = useState('出众')
  const [appearanceCustom, setAppearanceCustom] = useState(() => (draftObj?.appearance_description ? String(draftObj.appearance_description) : '清冷出众，眸若星辰'))
  const [background, setBackground] = useState(() => (draftObj?.background ? String(draftObj.background) : '书香门第'))
  const [daoPath, setDaoPath] = useState(() => (draftObj?.dao_path ? String(draftObj.dao_path) : '问道飞升'))

  // 第二面状态
  const [spiritualRoot, setSpiritualRoot] = useState('木火双灵根')
  const [constitution, setConstitution] = useState('凡体')

  // 六维分配（初始 10/10/10/10/10/10，合计 60）
  const [attrs, setAttrs] = useState<Record<string, number>>({
    aptitude: 10,
    comprehension: 10,
    spirit_sense: 10,
    speed: 10,
    dao_heart: 10,
    fortune: 10,
  })

  // 天赋选择（初始 5 项基础各耗 1 点，合计 5 点）
  const [selectedTalents, setSelectedTalents] = useState<string[]>([
    '天资聪颖',
    '过目不忘',
    '身轻如燕',
    '天生道心',
    '气运加身',
  ])

  // 六维总和
  const attrSum = useMemo(() => {
    return Object.values(attrs).reduce((acc, curr) => acc + curr, 0)
  }, [attrs])

  // 天赋消耗总和
  const talentCost = useMemo(() => {
    return selectedTalents.reduce((sum, item) => {
      return sum + (item === '体弱多病' ? -2 : 1)
    }, 0)
  }, [selectedTalents])

  // 随机取名
  const handleRandomName = () => {
    const f = FIRST_NAMES[Math.floor(Math.random() * FIRST_NAMES.length)]
    const g = GIVEN_NAMES[Math.floor(Math.random() * GIVEN_NAMES.length)]
    setName(`${f}${g}`)
  }

  // 随机全部第一面
  const handleRandomStepOne = () => {
    handleRandomName()
    setGender(Math.random() > 0.5 ? '男' : '女')
    setAge(Math.floor(Math.random() * 20) + 16)
    const app = APPEARANCE_LEVELS[Math.floor(Math.random() * APPEARANCE_LEVELS.length)]
    setAppearanceLevel(app.level)
    setAppearanceCustom(app.template)
    const bg = BACKGROUNDS[Math.floor(Math.random() * BACKGROUNDS.length)]
    setBackground(bg.key)
    const dp = DAO_PATHS[Math.floor(Math.random() * DAO_PATHS.length)]
    setDaoPath(dp.key)
  }

  // 六维快捷模版分配
  const applyAttrPreset = (preset: Record<string, number>) => {
    setAttrs({ ...preset })
  }

  // 随机合法六维（合为 60，每项 1~15）
  const handleRandomAttrs = () => {
    let pts = 60
    const keys = ['aptitude', 'comprehension', 'spirit_sense', 'speed', 'dao_heart', 'fortune']
    const result: Record<string, number> = {
      aptitude: 1,
      comprehension: 1,
      spirit_sense: 1,
      speed: 1,
      dao_heart: 1,
      fortune: 1,
    }
    pts -= 6
    while (pts > 0) {
      const idx = Math.floor(Math.random() * keys.length)
      const k = keys[idx]
      if (result[k] < 15) {
        result[k]++
        pts--
      }
    }
    setAttrs(result)
  }

  // 调整六维单项
  const adjustAttr = (key: string, delta: number) => {
    const curr = attrs[key] || 10
    const next = curr + delta
    if (next < 1 || next > 15) return
    if (delta > 0 && attrSum >= 60) return
    setAttrs((prev) => ({ ...prev, [key]: next }))
  }

  // 切换天赋
  const toggleTalent = (talentName: string) => {
    if (selectedTalents.includes(talentName)) {
      setSelectedTalents(selectedTalents.filter((t) => t !== talentName))
    } else {
      setSelectedTalents([...selectedTalents, talentName])
    }
  }

  // 提交第一面
  const submitStepOne = () => {
    const cleanName = name.trim() || '沈砚'
    const cleanDesc = appearanceCustom.includes(appearanceLevel)
      ? appearanceCustom
      : `${appearanceLevel}，${appearanceCustom}`
    const cmd = `姓名=${cleanName}；性别=${gender}；年龄=${age}；相貌=${cleanDesc}；出身=${background}；道途=${daoPath}`
    onAction(cmd)
  }

  // 提交第二面
  const submitStepTwo = () => {
    if (attrSum !== 60 || talentCost !== 5) return
    const attrPairs = [
      `资质=${attrs.aptitude}`,
      `悟性=${attrs.comprehension}`,
      `神识=${attrs.spirit_sense}`,
      `遁速=${attrs.speed}`,
      `道心=${attrs.dao_heart}`,
      `仙缘=${attrs.fortune}`,
    ].join('；')
    const talentsStr = selectedTalents.join('、')
    const cmd = `灵根=${spiritualRoot}；体质=${constitution}；${attrPairs}；天赋=${talentsStr}`
    onAction(cmd)
  }

  // 当前道途对应的道号
  const activeDaoName = DAO_PATHS.find((p) => p.key === daoPath)?.daoName || '清微'
  const activeBg = BACKGROUNDS.find((b) => b.key === background)

  return (
    <div className="character-creator-portal">
      {/* 顶部阶段导航与快速开始 */}
      <header className="creator-header">
        <div className="creator-steps-indicator">
          <div className={`step-badge ${isStepOne ? 'active' : 'passed'}`}>
            <span>壹</span>
            <strong>凡尘命格</strong>
            <small>姓名 · 容止 · 出身 · 初心</small>
          </div>
          <ChevronRight size={18} className="step-arrow" />
          <div className={`step-badge ${!isStepOne ? 'active' : 'pending'}`}>
            <span>贰</span>
            <strong>道骨仙胎</strong>
            <small>灵根 · 体质 · 六维 · 天赋</small>
          </div>
        </div>

        <div className="creator-header-actions">
          {isStepOne && (
            <button
              type="button"
              className="creator-action-btn dice-btn"
              onClick={handleRandomStepOne}
              title="随机掷出一套行世命格"
            >
              <Dice5 size={16} />
              <span>灵机定格</span>
            </button>
          )}
          <button
            type="button"
            className="creator-action-btn default-btn"
            disabled={busy}
            onClick={() => onAction('确认默认创角')}
            title="以沈砚默认配置直接踏入修仙"
          >
            <Sparkles size={16} />
            <span>承袭天命（默认创角）</span>
          </button>
        </div>
      </header>

      {/* 主体两栏布局：左侧交互配置，右侧命盘定契长卷 */}
      <div className="creator-body-layout">
        {/* 左侧配置区 */}
        <main className="creator-config-pane">
          <AnimatePresence mode="wait">
            {isStepOne ? (
              <motion.div
                key="step-one"
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 16 }}
                className="step-content step-one-content"
              >
                {/* 姓名与性别 */}
                <section className="form-group-row">
                  <div className="form-field name-field">
                    <label>
                      <User size={14} />
                      <span>修士尊名</span>
                      <small>（1~12字）</small>
                    </label>
                    <div className="input-with-action">
                      <input
                        type="text"
                        maxLength={12}
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="请输入姓名"
                      />
                      <button
                        type="button"
                        className="field-inline-btn"
                        onClick={handleRandomName}
                        title="随机生成道名"
                      >
                        <Dice5 size={14} />
                        <span>掷名</span>
                      </button>
                    </div>
                  </div>

                  <div className="form-field gender-field">
                    <label>
                      <span>阴阳乾坤</span>
                    </label>
                    <div className="segmented-control">
                      {['男', '女', '自定义'].map((g) => (
                        <button
                          type="button"
                          key={g}
                          className={gender === g ? 'active' : ''}
                          onClick={() => setGender(g)}
                        >
                          {g === '男' ? '乾道 (男)' : g === '女' ? '坤道 (女)' : '自定义'}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="form-field age-field">
                    <label>
                      <span>涉世年岁</span>
                      <strong>{age} 岁</strong>
                    </label>
                    <input
                      type="range"
                      min={16}
                      max={60}
                      value={age}
                      onChange={(e) => setAge(Number(e.target.value))}
                      className="age-slider"
                    />
                    <div className="age-marks">
                      <span>16岁·初悟</span>
                      <span>18岁·风华</span>
                      <span>30岁·立业</span>
                      <span>60岁·老成</span>
                    </div>
                  </div>
                </section>

                {/* 相貌风采 */}
                <section className="form-group appearance-group">
                  <label>
                    <Feather size={14} />
                    <span>风采神韵</span>
                    <small>影响修仙界人物初始印象</small>
                  </label>
                  <div className="appearance-level-chips">
                    {APPEARANCE_LEVELS.map((item) => (
                      <button
                        type="button"
                        key={item.level}
                        className={`appearance-chip ${appearanceLevel === item.level ? 'active' : ''}`}
                        onClick={() => {
                          setAppearanceLevel(item.level)
                          setAppearanceCustom(item.template)
                        }}
                      >
                        <strong>{item.level}</strong>
                      </button>
                    ))}
                  </div>
                  <input
                    type="text"
                    value={appearanceCustom}
                    onChange={(e) => setAppearanceCustom(e.target.value)}
                    placeholder="自定义相貌描述..."
                    className="appearance-input"
                  />
                </section>

                {/* 出身选择（10选1） */}
                <section className="form-group background-group">
                  <label>
                    <Shield size={14} />
                    <span>凡尘出身</span>
                    <small>不同出身赋予本命初始特质与修行资粮</small>
                  </label>
                  <div className="background-cards-grid">
                    {BACKGROUNDS.map((bg) => {
                      const isSelected = background === bg.key
                      return (
                        <div
                          key={bg.key}
                          className={`creator-card bg-card ${isSelected ? 'selected' : ''}`}
                          onClick={() => setBackground(bg.key)}
                        >
                          <div className="card-top">
                            <span className="card-icon">{bg.icon}</span>
                            <strong>{bg.label}</strong>
                            {isSelected && <CheckCircle2 size={15} className="check-icon" />}
                          </div>
                          <span className="card-bonus">{bg.bonus}</span>
                          <p className="card-desc">{bg.desc}</p>
                        </div>
                      )
                    })}
                  </div>
                </section>

                {/* 道途选择（6选1） */}
                <section className="form-group daopath-group">
                  <label>
                    <Compass size={14} />
                    <span>问道初心</span>
                    <small>确立求长生的本心方向，并烙印专属传世道号</small>
                  </label>
                  <div className="daopath-cards-grid">
                    {DAO_PATHS.map((dp) => {
                      const isSelected = daoPath === dp.key
                      return (
                        <div
                          key={dp.key}
                          className={`creator-card dp-card ${isSelected ? 'selected' : ''}`}
                          onClick={() => setDaoPath(dp.key)}
                        >
                          <div className="card-top">
                            <strong>{dp.key}</strong>
                            <span className="dao-name-seal">道号 · {dp.daoName}</span>
                            {isSelected && <CheckCircle2 size={15} className="check-icon" />}
                          </div>
                          <p className="card-desc">{dp.desc}</p>
                        </div>
                      )
                    })}
                  </div>
                </section>

                {/* 第一面底部操作按钮 */}
                <footer className="creator-step-footer">
                  <div className="footer-tip">
                    <span>* 核验基础信息无误后，即可步入灵台测定灵根与道骨</span>
                  </div>
                  <motion.button
                    type="button"
                    className="submit-step-btn"
                    disabled={busy || !name.trim()}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={submitStepOne}
                  >
                    <span>步入灵台 · 测定道骨 ➔</span>
                  </motion.button>
                </footer>
              </motion.div>
            ) : (
              <motion.div
                key="step-two"
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -16 }}
                className="step-content step-two-content"
              >
                {/* 灵根选择 */}
                <section className="form-group root-group">
                  <label>
                    <Flame size={14} />
                    <span>先天灵根</span>
                    <small>决定天地灵气感应亲和与术法修习方向</small>
                  </label>
                  <div className="root-categories">
                    {SPIRITUAL_ROOTS.map((cat) => (
                      <div key={cat.group} className="root-cat-row">
                        <span className="cat-label">{cat.group}</span>
                        <div className="cat-chips">
                          {cat.items.map((item) => (
                            <button
                              type="button"
                              key={item}
                              className={`root-chip ${spiritualRoot === item ? 'active' : ''}`}
                              onClick={() => setSpiritualRoot(item)}
                            >
                              {item}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                {/* 体质选择 */}
                <section className="form-group constitution-group">
                  <label>
                    <Zap size={14} />
                    <span>特殊道体</span>
                    <small>肉身体魄之天道异象</small>
                  </label>
                  <div className="constitution-grid">
                    {CONSTITUTIONS.map((c) => {
                      const isSelected = constitution === c.name
                      return (
                        <div
                          key={c.name}
                          className={`creator-card const-card ${isSelected ? 'selected' : ''}`}
                          onClick={() => setConstitution(c.name)}
                        >
                          <div className="card-top">
                            <strong>{c.name}</strong>
                            <span className="const-tag">{c.tag}</span>
                            {isSelected && <CheckCircle2 size={15} className="check-icon" />}
                          </div>
                          <p className="card-desc">{c.effect}</p>
                        </div>
                      )
                    })}
                  </div>
                </section>

                {/* 六维分配（总计 60 点，单项 1~15） */}
                <section className="form-group attributes-group">
                  <div className="attrs-header">
                    <label>
                      <Award size={14} />
                      <span>六维道基</span>
                      <small>单项上限 15 点，总和必须正好为 60 点</small>
                    </label>
                    <div className="attrs-status-tag" data-valid={attrSum === 60}>
                      {attrSum === 60 ? (
                        <span className="tag-ok"><Check size={14} />点数已平衡（60 / 60）</span>
                      ) : (
                        <span className="tag-warn">
                          <AlertCircle size={14} />
                          {attrSum > 60 ? `超出 ${attrSum - 60} 点` : `剩余 ${60 - attrSum} 点待分配`}（{attrSum} / 60）
                        </span>
                      )}
                    </div>
                  </div>

                  {/* 快捷模版 */}
                  <div className="attr-presets-bar">
                    <span className="preset-label">快捷配点：</span>
                    <button
                      type="button"
                      className="preset-btn"
                      onClick={() => applyAttrPreset({ aptitude: 10, comprehension: 10, spirit_sense: 10, speed: 10, dao_heart: 10, fortune: 10 })}
                    >
                      中庸平正
                    </button>
                    <button
                      type="button"
                      className="preset-btn"
                      onClick={() => applyAttrPreset({ aptitude: 15, comprehension: 12, spirit_sense: 8, speed: 13, dao_heart: 7, fortune: 5 })}
                    >
                      绝代剑胎
                    </button>
                    <button
                      type="button"
                      className="preset-btn"
                      onClick={() => applyAttrPreset({ aptitude: 5, comprehension: 15, spirit_sense: 8, speed: 5, dao_heart: 15, fortune: 12 })}
                    >
                      悟道奇才
                    </button>
                    <button
                      type="button"
                      className="preset-btn"
                      onClick={() => applyAttrPreset({ aptitude: 6, comprehension: 11, spirit_sense: 10, speed: 6, dao_heart: 12, fortune: 15 })}
                    >
                      气运福星
                    </button>
                    <button
                      type="button"
                      className="preset-btn dice-btn"
                      onClick={handleRandomAttrs}
                    >
                      <Dice5 size={12} />
                      <span>随机平衡掷骰</span>
                    </button>
                  </div>

                  {/* 六维调节器列表 */}
                  <div className="attrs-allocator-grid">
                    {ATTRIBUTE_DEFS.map((a) => {
                      const val = attrs[a.key] || 10
                      const percent = (val / 15) * 100
                      return (
                        <div key={a.key} className="attr-alloc-item">
                          <div className="alloc-meta">
                            <strong>{a.label}</strong>
                            <small>{a.desc}</small>
                          </div>

                          <div className="alloc-bar-container">
                            <div className="alloc-bar-fill" style={{ width: `${percent}%` }} />
                          </div>

                          <div className="alloc-controls">
                            <button
                              type="button"
                              className="step-btn"
                              disabled={val <= 1}
                              onClick={() => adjustAttr(a.key, -1)}
                            >
                              -
                            </button>
                            <span className="attr-val-display">{val}</span>
                            <button
                              type="button"
                              className="step-btn"
                              disabled={val >= 15 || attrSum >= 60}
                              onClick={() => adjustAttr(a.key, 1)}
                            >
                              +
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </section>

                {/* 先天天赋（必须消耗正好 5 点） */}
                <section className="form-group talents-group">
                  <div className="talents-header">
                    <label>
                      <Gem size={14} />
                      <span>先天天赋</span>
                      <small>正面天赋各耗 1 点，体弱多病返还 2 点；最终必须正好使用 5 点</small>
                    </label>
                    <div className="talent-cost-tag" data-valid={talentCost === 5}>
                      {talentCost === 5 ? (
                        <span className="tag-ok"><Check size={14} />已耗 5 点天赋</span>
                      ) : (
                        <span className="tag-warn">
                          <AlertCircle size={14} />
                          当前已用 {talentCost} / 5 点（{talentCost > 5 ? `超出 ${talentCost - 5} 点` : `还需选择 ${5 - talentCost} 点`}）
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="talents-grid">
                    {TALENT_ITEMS.map((t) => {
                      const isSelected = selectedTalents.includes(t.name)
                      const isNegative = t.cost < 0
                      return (
                        <div
                          key={t.name}
                          className={`talent-chip-card ${isSelected ? 'selected' : ''} ${isNegative ? 'negative' : ''}`}
                          onClick={() => toggleTalent(t.name)}
                        >
                          <div className="t-head">
                            <strong>{t.name}</strong>
                            <span className="t-cost-badge">
                              {t.cost > 0 ? `消耗 ${t.cost} 点` : `返还 ${Math.abs(t.cost)} 点`}
                            </span>
                            {isSelected && <Check size={14} className="t-check" />}
                          </div>
                          <p className="t-desc">{t.desc}</p>
                        </div>
                      )
                    })}
                  </div>
                </section>

                {/* 第二面底部操作按钮 */}
                <footer className="creator-step-footer">
                  <button
                    type="button"
                    className="back-step-btn"
                    onClick={() => {
                      // 调用返回上一步
                      onAction('返回上一步')
                    }}
                  >
                    <ChevronLeft size={16} />
                    <span>返回修改凡尘资料</span>
                  </button>

                  <motion.button
                    type="button"
                    className="submit-step-btn enter-world-btn"
                    disabled={busy || attrSum !== 60 || talentCost !== 5}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={submitStepTwo}
                  >
                    <Sparkles size={16} />
                    <span>天命已定 · 踏入仙途 ➔</span>
                  </motion.button>
                </footer>
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* 右侧：命盘定契实时长卷预览 */}
        <aside className="creator-preview-scroll">
          <div className="scroll-paper-body">
            <div className="scroll-top-seal">
              <span className="seal-char">道</span>
              <h3>仙命天契</h3>
              <small>九州冥冥 · 命理昭然</small>
            </div>

            <div className="preview-character-header">
              <div className="p-name-row">
                <h2>{name || '无名修士'}</h2>
                <span className="p-dao-name">{activeDaoName}</span>
              </div>
              <p className="p-sub-meta">
                {gender} · {age} 岁 · {appearanceLevel}
              </p>
            </div>

            <div className="preview-divider" />

            <div className="preview-section">
              <h4>【凡尘因果】</h4>
              <div className="preview-badge-row">
                <span className="p-badge">{background}</span>
                <span className="p-badge">{daoPath}</span>
              </div>
              {activeBg && <p className="p-bonus-text">特质：{activeBg.bonus}</p>}
            </div>

            <div className="preview-divider" />

            <div className="preview-section">
              <h4>【道胎骨相】</h4>
              <div className="preview-badge-row">
                <span className="p-badge gold">{spiritualRoot}</span>
                <span className="p-badge jade">{constitution}</span>
              </div>
            </div>

            <div className="preview-divider" />

            <div className="preview-section">
              <h4>【六维基石】</h4>
              <div className="preview-stats-grid">
                <div><span>资质</span><strong>{attrs.aptitude}</strong></div>
                <div><span>悟性</span><strong>{attrs.comprehension}</strong></div>
                <div><span>神识</span><strong>{attrs.spirit_sense}</strong></div>
                <div><span>遁速</span><strong>{attrs.speed}</strong></div>
                <div><span>道心</span><strong>{attrs.dao_heart}</strong></div>
                <div><span>仙缘</span><strong>{attrs.fortune}</strong></div>
              </div>
            </div>

            <div className="preview-divider" />

            <div className="preview-section">
              <h4>【命定先天天赋】</h4>
              <div className="preview-talents-cloud">
                {selectedTalents.map((t) => (
                  <span key={t} className={`t-pill ${t === '体弱多病' ? 'neg' : ''}`}>
                    {t}
                  </span>
                ))}
              </div>
            </div>

            <div className="scroll-bottom-calligraphy">
              <p>“天地玄黄，宇宙洪荒。凡尘有尽，唯道永恒。”</p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
