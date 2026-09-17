import { Check, Flame, FlaskConical, Hammer, Leaf, Shield, Sparkles, Sprout, Wind, Zap } from 'lucide-react'
import type { CaveSnapshot } from '../api/types'

export interface FacilityItem {
  name?: string
  level?: number | string
  cost_stones?: number | string
  materials?: Record<string, unknown>
  affordable?: boolean
  disabled_reason?: string
  action?: string
  description?: string
}

interface CaveDeductionStageProps {
  facilityName: string
  facilityItem: FacilityItem
  cave?: CaveSnapshot
  cropsString?: string
  readOnly?: boolean
  onAction: (action: string) => void
}

export function CaveDeductionStage({
  facilityName,
  facilityItem,
  cave,
  readOnly = false,
  onAction,
}: CaveDeductionStageProps) {
  const level = Number(facilityItem.level || 0)
  const isConstructed = level > 0

  // Relevant blueprints for this facility
  const relevantBlueprints = (cave?.blueprints || []).filter(
    (bp) => bp.facility === facilityName
  )

  // Matching crops if facility is 灵田
  const currentCrops = cave?.crops || []
  const hasActiveCrops = currentCrops.length > 0
  const activeCrop = currentCrops[0]

  // Craft skill matching
  const skillMap: Record<string, string> = {
    丹房: '炼丹',
    器坊: '炼器',
    静室: '符箓',
    灵田: '灵植',
    聚灵阵: '阵法',
  }
  const skillName = skillMap[facilityName]
  const skillRank = skillName && cave?.skills ? cave.skills[skillName] : undefined

  return (
    <aside className="cave-hotspot-inspector cave-deduction-stage" data-facility={facilityName}>
      <header className="cave-inspector-header">
        <span className="cave-inspector-emblem" aria-hidden="true">
          {facilityName === '丹房' && <Flame size={22} />}
          {facilityName === '灵田' && <Sprout size={22} />}
          {facilityName === '器坊' && <Hammer size={22} />}
          {facilityName === '聚灵阵' && <Wind size={22} />}
          {facilityName === '静室' && <Sparkles size={22} />}
          {facilityName === '禁制' && <Shield size={22} />}
        </span>
        <div className="cave-inspector-title-area">
          <small>当前设施</small>
          <h3>{facilityName}</h3>
          {skillRank && (
            <span className="skill-rank-tag">
              {skillName} · <strong>{skillRank}</strong>
            </span>
          )}
        </div>
        <em className="facility-level-label">{isConstructed ? `${level} 级` : '尚未营造'}</em>
      </header>

      {/* 动态推演玄机展台 */}
      <div className="cave-deduction-workbench">
        {/* 丹房：玄火宝鼎与凝丹推演 */}
        {facilityName === '丹房' && (
          <div className="workbench-section workbench-alchemy">
            <div className="workbench-visual-card alchemy-orb-card">
              <div className="alchemy-flame-indicator" aria-hidden="true">
                <Flame size={26} className="flame-flicker" />
                <div className="alchemy-mist-ring" />
              </div>
              <div className="workbench-visual-info">
                <strong>
                  {level === 3 ? '九转乾坤神鼎' : level === 2 ? '赤炎八卦宝鼎' : level === 1 ? '青铜玄火鼎' : '凡品粗陶鼎'}
                </strong>
                <p>
                  {isConstructed
                    ? '地脉玄火引动，鼎内丹气氤氲。可即刻开炉凝丹，亦可慢火温养排产。'
                    : '尚未筑成丹房，无法引真火凝丹。升至 1 级后可开炉。'}
                </p>
              </div>
            </div>

            <div className="workbench-recipe-list" aria-label="丹房配方">
              {relevantBlueprints.length > 0 ? (
                relevantBlueprints.map((bp) => {
                  const ingredientsText = Object.entries(bp.ingredients)
                    .map(([k, v]) => `${k}×${v}`)
                    .join('、')
                  return (
                    <article className="workbench-recipe-item" key={bp.name}>
                      <div className="recipe-headline">
                        <strong>{bp.name}</strong>
                        <span className="recipe-chance">成丹率 {bp.chance}%</span>
                        <span className="recipe-yield">产出 {bp.output}×{bp.output_count}</span>
                      </div>
                      <p className="recipe-reqs">需耗：{ingredientsText}</p>
                      <div className="recipe-btn-group">
                        <button
                          type="button"
                          className="btn-instant-craft"
                          disabled={readOnly || !bp.instant_available}
                          title={
                            readOnly
                              ? '成果巡览仅供查看'
                              : bp.instant_available
                                ? '即刻开炉凝丹并推进一个月'
                                : bp.instant_disabled_reason || '材料不足'
                          }
                          onClick={() => bp.instant_action && onAction(bp.instant_action)}
                        >
                          <Flame size={12} />
                          即刻凝丹
                        </button>
                        <button
                          type="button"
                          className="btn-queue-craft"
                          disabled={readOnly || !bp.available}
                          title={
                            readOnly
                              ? '成果巡览仅供查看'
                              : bp.available
                                ? `安排后台慢火温养，耗时 ${bp.duration} 个月，不推进当前时间`
                                : bp.disabled_reason
                          }
                          onClick={() => onAction(bp.action)}
                        >
                          <FlaskConical size={12} />
                          慢火温养
                        </button>
                      </div>
                    </article>
                  )
                })
              ) : (
                <p className="workbench-empty-hint">暂无已知丹方，升级丹房或获取灵药后可推演。</p>
              )}
            </div>
          </div>
        )}

        {/* 灵田：青玉生机与催熟推演 */}
        {facilityName === '灵田' && (
          <div className="workbench-section workbench-field">
            <div className="workbench-visual-card field-soil-card">
              <div className="field-sprout-indicator" aria-hidden="true">
                <Sprout size={26} className="sprout-sway" />
              </div>
              <div className="workbench-visual-info">
                <strong>
                  {level === 3 ? '九天息壤玉田' : level === 2 ? '二品灵秀沃土' : level === 1 ? '一品初辟灵田' : '山田荒瘠'}
                </strong>
                <p>
                  {isConstructed
                    ? `灵气深润，当前灵田为 ${level} 级，每次采收可获 ${3 + level} 株上品灵药。`
                    : '灵田尚未垦辟，修葺后方可播撒种苗。'}
                </p>
              </div>
            </div>

            <div className="workbench-crop-display">
              {hasActiveCrops && activeCrop ? (
                <div className="crop-live-card">
                  <div className="crop-header-row">
                    <strong>{activeCrop.name}</strong>
                    <span className="crop-stage-badge" data-ready={activeCrop.ready || undefined}>
                      {activeCrop.stage}
                    </span>
                    <span className="crop-due-text">
                      {activeCrop.ready ? '金芒内敛·已成熟' : `还需 ${activeCrop.remaining_months} 个月`}
                    </span>
                  </div>

                  <div className="crop-progress-track" role="progressbar" aria-valuenow={activeCrop.progress} aria-valuemin={0} aria-valuemax={100}>
                    <div className="crop-progress-fill" style={{ width: `${activeCrop.progress}%` }} />
                  </div>

                  <div className="crop-growth-ticks">
                    <span className={activeCrop.progress >= 25 ? 'reached' : ''}>萌芽</span>
                    <span className={activeCrop.progress >= 50 ? 'reached' : ''}>抽叶</span>
                    <span className={activeCrop.progress >= 75 ? 'reached' : ''}>孕灵</span>
                    <span className={activeCrop.ready ? 'reached' : ''}>大熟</span>
                  </div>

                  <div className="crop-interaction-row">
                    {activeCrop.ready ? (
                      <button
                        type="button"
                        className="btn-harvest-action"
                        disabled={readOnly}
                        onClick={() => onAction(activeCrop.harvest_action)}
                      >
                        <Leaf size={14} />
                        开镰采灵（收获 {activeCrop.expected_yield} 株）
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="btn-accelerate-action"
                        disabled={readOnly || cave?.focus === '灵田轮作'}
                        title={cave?.focus === '灵田轮作' ? '当前已采用灵田轮作方针' : '消耗灵蕴催熟作物，加快成熟'}
                        onClick={() => onAction('洞府方针 灵田轮作')}
                      >
                        <Zap size={13} />
                        {cave?.focus === '灵田轮作' ? '灵蕴轮作催熟中' : '切换【灵田轮作】灵蕴催熟'}
                      </button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="crop-empty-card">
                  <p>灵垄空润待耕，下种后可静待灵药随日月吐纳成熟。</p>
                  <button
                    type="button"
                    className="btn-plant-action"
                    disabled={readOnly || !isConstructed}
                    title={!isConstructed ? '需先营造灵田' : '播撒灵药幼苗'}
                    onClick={() => onAction('种植 灵药')}
                  >
                    <Sprout size={13} />
                    播种灵药
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 器坊：玄铁重砧与淬砺推演 */}
        {facilityName === '器坊' && (
          <div className="workbench-section workbench-forge">
            <div className="workbench-visual-card forge-anvil-card">
              <div className="forge-hammer-indicator" aria-hidden="true">
                <Hammer size={26} className="hammer-strike" />
              </div>
              <div className="workbench-visual-info">
                <strong>
                  {level === 3 ? '太乙玄金重砧' : level === 2 ? '陨铁精金砧' : level === 1 ? '精铸青钢砧' : '凡铁锻砧'}
                </strong>
                <p>
                  {isConstructed
                    ? '地火通明，千锤百炼。可引地脉真火淬淬法宝出鞘，亦可精工慢铸。'
                    : '器坊未成，地火未引，尚无法锻淬飞剑法宝。'}
                </p>
              </div>
            </div>

            <div className="workbench-recipe-list" aria-label="器坊图谱">
              {relevantBlueprints.length > 0 ? (
                relevantBlueprints.map((bp) => {
                  const ingredientsText = Object.entries(bp.ingredients)
                    .map(([k, v]) => `${k}×${v}`)
                    .join('、')
                  return (
                    <article className="workbench-recipe-item" key={bp.name}>
                      <div className="recipe-headline">
                        <strong>{bp.name}</strong>
                        <span className="recipe-chance">铸成率 {bp.chance}%</span>
                        <span className="recipe-yield">产出 {bp.output}×{bp.output_count}</span>
                      </div>
                      <p className="recipe-reqs">材料：{ingredientsText}</p>
                      <div className="recipe-btn-group">
                        <button
                          type="button"
                          className="btn-instant-craft"
                          disabled={readOnly || !bp.instant_available}
                          title={
                            readOnly
                              ? '成果巡览仅供查看'
                              : bp.instant_available
                                ? '即刻开炉锻淬出鞘并推进一个月'
                                : bp.instant_disabled_reason || '材料不足'
                          }
                          onClick={() => bp.instant_action && onAction(bp.instant_action)}
                        >
                          <Flame size={12} />
                          即刻锻淬
                        </button>
                        <button
                          type="button"
                          className="btn-queue-craft"
                          disabled={readOnly || !bp.available}
                          title={
                            readOnly
                              ? '成果巡览仅供查看'
                              : bp.available
                                ? `安排后台精心慢铸，工期 ${bp.duration} 个月`
                                : bp.disabled_reason
                          }
                          onClick={() => onAction(bp.action)}
                        >
                          <Hammer size={12} />
                          后台精铸
                        </button>
                      </div>
                    </article>
                  )
                })
              ) : (
                <p className="workbench-empty-hint">暂无器坊图谱，营造设施后可在此推演打造。</p>
              )}
            </div>
          </div>
        )}

        {/* 聚灵阵：八卦周天与灵脉调度 */}
        {facilityName === '聚灵阵' && (
          <div className="workbench-section workbench-gathering">
            <div className="workbench-visual-card gathering-bagua-card">
              <div className="gathering-bagua-indicator" aria-hidden="true">
                <Wind size={26} className="bagua-rotate-ring" />
              </div>
              <div className="workbench-visual-info">
                <strong>九宫八卦聚灵大阵 · {cave?.aura || '普通'}品阶</strong>
                <p>
                  八方灵气潮汐吞吐，灵蕴储量 {cave?.spirit_energy || 0} / {cave?.spirit_energy_cap || 24}（每月生成 +{cave?.monthly_generation || 2} 点）。
                </p>
              </div>
            </div>

            <div className="gathering-dispatch-grid">
              <button
                type="button"
                className={`btn-policy-dispatch ${cave?.focus === '蕴养灵脉' ? 'selected-active' : ''}`}
                disabled={readOnly || cave?.focus === '蕴养灵脉'}
                onClick={() => onAction('洞府方针 蕴养灵脉')}
              >
                <div>
                  <strong>蕴养灵脉</strong>
                  {cave?.focus === '蕴养灵脉' && <Check size={13} />}
                </div>
                <small>每月灵蕴产量提升 50%</small>
              </button>

              <button
                type="button"
                className={`btn-policy-dispatch ${cave?.focus === '百艺轮转' ? 'selected-active' : ''}`}
                disabled={readOnly || cave?.focus === '百艺轮转'}
                onClick={() => onAction('洞府方针 百艺轮转')}
              >
                <div>
                  <strong>百艺轮转</strong>
                  {cave?.focus === '百艺轮转' && <Check size={13} />}
                </div>
                <small>后台生产成功率提升 8%</small>
              </button>
            </div>
          </div>
        )}

        {/* 静室：云崖悟道与神识抚伤 */}
        {facilityName === '静室' && (
          <div className="workbench-section workbench-chamber">
            <div className="workbench-visual-card chamber-incense-card">
              <div className="chamber-incense-indicator" aria-hidden="true">
                <Sparkles size={26} className="incense-smoke" />
              </div>
              <div className="workbench-visual-info">
                <strong>云崖悟道静室 · 吐纳养元</strong>
                <p>
                  静息凝神，澄澈心境。可消耗灵蕴调息抚平道伤，亦可潜心闭关稳增修为。
                </p>
              </div>
            </div>

            <div className="chamber-actions-grid">
              <button
                type="button"
                className="btn-recuperate-action"
                disabled={readOnly || !cave?.can_recuperate}
                title={
                  readOnly
                    ? '成果巡览仅供查看'
                    : cave?.can_recuperate
                      ? '消耗 10 灵蕴，恢复气血与灵力并疗愈内伤'
                      : cave?.recuperate_reason || '条件不足'
                }
                onClick={() => onAction('洞府调息')}
              >
                <Sparkles size={13} />
                调息养元（耗 10 灵蕴）
              </button>

              <button
                type="button"
                className={`btn-focus-cultivate-action ${cave?.focus === '潜修养元' ? 'selected-active' : ''}`}
                disabled={readOnly || cave?.focus === '潜修养元'}
                onClick={() => onAction('洞府方针 潜修养元')}
              >
                <Check size={13} />
                {cave?.focus === '潜修养元' ? '潜修养元进行中' : '方针：潜修养元'}
              </button>
            </div>

            {relevantBlueprints.length > 0 && (
              <div className="workbench-recipe-list talisman-sublist" aria-label="符箓推演">
                {relevantBlueprints.map((bp) => (
                  <article className="workbench-recipe-item" key={bp.name}>
                    <div className="recipe-headline">
                      <strong>{bp.name}</strong>
                      <span className="recipe-chance">绘制率 {bp.chance}%</span>
                      <span className="recipe-yield">产出 {bp.output}×{bp.output_count}</span>
                    </div>
                    <div className="recipe-btn-group">
                      <button
                        type="button"
                        className="btn-instant-craft"
                        disabled={readOnly || !bp.instant_available}
                        onClick={() => bp.instant_action && onAction(bp.instant_action)}
                      >
                        即刻制符
                      </button>
                      <button
                        type="button"
                        className="btn-queue-craft"
                        disabled={readOnly || !bp.available}
                        onClick={() => onAction(bp.action)}
                      >
                        后台绘制
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 禁制：九峰神篆护山屏障 */}
        {facilityName === '禁制' && (
          <div className="workbench-section workbench-ward">
            <div className="workbench-visual-card ward-shield-card">
              <div className="ward-shield-indicator" aria-hidden="true">
                <Shield size={26} className="shield-glimmer" />
              </div>
              <div className="workbench-visual-info">
                <strong>九峰镇山神篆 · 辟邪护山</strong>
                <p>
                  神篆锁脉，坚固山门。提升灵蕴容量上限 +{level * 3}，抵御妖兽侵袭。
                </p>
              </div>
            </div>

            <div className="ward-stats-row">
              <div className="ward-stat-pill">
                <small>灵障屏障</small>
                <strong>{isConstructed ? `${level * 33 + 1}%` : '未开启'}</strong>
              </div>
              <div className="ward-stat-pill">
                <small>灵蕴扩容</small>
                <strong>+{level * 3} 点</strong>
              </div>
              <div className="ward-stat-pill">
                <small>神篆威能</small>
                <strong>{isConstructed ? '威压庇佑' : '待建'}</strong>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 设施营建修葺栏 */}
      <footer className="cave-facility-construction">
        <dl className="construction-meta">
          <div>
            <dt>当前层级</dt>
            <dd>{level} / 3</dd>
          </div>
          <div>
            <dt>升级灵石</dt>
            <dd>{facilityItem.cost_stones ? `${facilityItem.cost_stones}` : '—'}</dd>
          </div>
          <div>
            <dt>所需材料</dt>
            <dd>
              {facilityItem.materials && typeof facilityItem.materials === 'object'
                ? Object.entries(facilityItem.materials as Record<string, unknown>)
                    .map(([name, count]) => `${name}×${count}`)
                    .join('、') || '无需材料'
                : '无需材料'}
            </dd>
          </div>
        </dl>

        <button
          type="button"
          className="btn-upgrade-facility-action"
          disabled={readOnly || facilityItem.affordable !== true || level >= 3}
          title={
            readOnly
              ? '成果巡览仅供查看'
              : level >= 3
                ? '已达最高层级'
                : facilityItem.affordable === true
                  ? '升级会推进一个月'
                  : facilityItem.disabled_reason || '资粮不足'
          }
          onClick={() => facilityItem.action && onAction(facilityItem.action)}
        >
          {level >= 3
            ? '已达最高层级'
            : facilityItem.affordable === true
              ? `营造至 ${level + 1} 级`
              : facilityItem.disabled_reason || '资粮不足'}
        </button>
      </footer>
    </aside>
  )
}
