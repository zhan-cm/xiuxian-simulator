from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .progression import ProgressionEngine, REALMS
from .state import GameState
from .travel import TravelEngine


@dataclass(frozen=True, slots=True)
class EncounterCharacter:
    name: str
    identity: str
    realm: str
    temperament: str  # aloof, gentle, fierce, cunning, valiant, charm
    avatar_type: str  # preset or procedural
    quote: str


@dataclass(frozen=True, slots=True)
class EncounterChoice:
    id: str
    label: str
    dao_stance: str
    tone: str  # primary, safe, danger, quiet
    requirements: dict[str, Any]
    summary: str
    description: str
    effects: dict[str, Any]
    outcome_text: str


@dataclass(frozen=True, slots=True)
class EncounterDefinition:
    id: str
    title: str
    category: str  # ancient_secret, mortal_dust, spirit_creature, npc_destiny
    region_affinity: str  # empty means any region
    required_realm: int
    character: EncounterCharacter
    scene: str
    choices: tuple[EncounterChoice, ...]
    unique: bool = False


ENCOUNTERS_CATALOG: dict[str, EncounterDefinition] = {
    "ancient_remains": EncounterDefinition(
        id="ancient_remains",
        title="古修士遗蜕与残魂传道",
        category="ancient_secret",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="太古剑尊残魂",
            identity="古修残灵",
            realm="化神·圆满",
            temperament="aloof",
            avatar_type="procedural",
            quote="后辈修士，能破吾三千禁制踏足此地，也算有机缘。吾这一生剑骨与道典，你欲如何承接？",
        ),
        scene="踏入万年古修封印石室，一尊不朽金身端坐蒲团之上，周身剑气如虹，残魂自虚空中浮现，双眸神光流转俯瞰来者。",
        choices=(
            EncounterChoice(
                id="worship",
                label="躬身叩拜，求承衣钵",
                dao_stance="慈悲仁善",
                tone="safe",
                requirements={},
                summary="功德 +3 · 道法感悟 +25 · 悟道点 +1 · 声望 +5",
                description="执弟子之礼向古尊行三跪九叩大礼，心怀敬畏承继衣钵。",
                effects={"merit": 3, "dao_insight": 25, "dao_points": 1, "reputation": 5, "resources": {"古剑残片": 1}},
                outcome_text="太古剑尊抚须长笑，化作一道浩瀚青芒没入你眉心。你获得古尊完整剑道真意，心中剑理豁然洞开！",
            ),
            EncounterChoice(
                id="plunder",
                label="强破残魂，搜刮遗珍",
                dao_stance="杀人夺宝",
                tone="danger",
                requirements={"realm_index": 1},
                summary="业障 +4 · 灵石 +300 · 天材地宝 +1 · 气血 -20",
                description="趁残魂虚弱强行以术法轰杀残灵，搜刮金身储物古戒。",
                effects={"karma": 4, "stones": 300, "resources": {"天材地宝": 1}, "health_loss": 20, "condition": "剑气侵体"},
                outcome_text="你悍然祭出杀招绞碎残魂，石室崩塌间夺得古戒！但残魂溃灭前的剑煞怨气反噬入骨，令你气血大损。",
            ),
            EncounterChoice(
                id="purify",
                label="诵经超度，助其往生",
                dao_stance="守中无为",
                tone="primary",
                requirements={"spirit": 20},
                summary="消耗 20 灵力 · 功德 +6 · 道韵 +1 · 寿元 +2",
                description="不贪图遗蜕宝物，盘坐诵念道家度人经文，助其执念消解遁入轮回。",
                effects={"spirit_cost": 20, "merit": 6, "resources": {"道韵": 1}, "lifespan": 2},
                outcome_text="清圣梵音响彻石室，残魂脸上戾气尽褪，化作点点功德金雨落入你道躯，天道感应降下长生造化！",
            ),
        ),
    ),
    "celestial_chess": EncounterDefinition(
        id="celestial_chess",
        title="仙人绝巅残局对弈",
        category="ancient_secret",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="无相弈仙",
            identity="九天仙影",
            realm="悟道·大能",
            temperament="gentle",
            avatar_type="procedural",
            quote="黑子势如天劫覆地，白子困守孤岛生机。道友，可敢落下一子？",
        ),
        scene="云海万仞孤峰之巅，两尊白玉古石凳间摆放着万古未决的星辰残局。黑白二子皆引动天地法则雷鸣，白袍仙影执子微吟。",
        choices=(
            EncounterChoice(
                id="solve_board",
                label="沉心推演，顺天破局",
                dao_stance="逍遥求道",
                tone="primary",
                requirements={"spirit": 25},
                summary="消耗 25 灵力 · 悟道点 +2 · 修为 +40 · 声望 +8",
                description="神识如丝探入万千星宿阵列，以毕生道法推演，落子天元开辟生机。",
                effects={"spirit_cost": 25, "dao_points": 2, "cultivation": 40, "dao_insight": 30, "reputation": 8},
                outcome_text="落子刹那，整座棋盘星宿倒转、紫气东来三万里！弈仙抚掌赞叹，浩瀚道意灌注你天灵盖！",
            ),
            EncounterChoice(
                id="flip_board",
                label="挥袖掀局，逆反天地",
                dao_stance="狂放霸道",
                tone="danger",
                requirements={},
                summary="业障 +2 · 声望 +12 · 阵法残卷 +1 · 气血 -10",
                description="冷笑一声挥袖掀翻棋盘：“天地万灵皆自由，何须困于他人之棋规！”",
                effects={"karma": 2, "reputation": 12, "resources": {"道韵": 1}, "health_loss": 10},
                outcome_text="棋盘轰然碎裂，虚空雷云震荡！弈仙虚影先是一怔，旋即仰天长笑：“好一个跳出三界外之狂徒！”留下星辰道韵消散。",
            ),
            EncounterChoice(
                id="observe_quiet",
                label="默坐观棋，不着一子",
                dao_stance="守中无为",
                tone="safe",
                requirements={},
                summary="修为 +20 · 灵力回满 · 气血恢复",
                description="静坐观照黑白起伏，不染胜负机心，体悟万法生灭自然之道。",
                effects={"cultivation": 20, "spirit_restore": 999, "health_restore": 30},
                outcome_text="山风拂过，落叶归根。你心台明镜无尘，周天灵气欢跃奔涌，体魄与灵识在一呼一吸间达到浑圆饱满！",
            ),
        ),
    ),
    "ancient_tree": EncounterDefinition(
        id="ancient_tree",
        title="太古神木涅槃圣果",
        category="ancient_secret",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="木灵玄女",
            identity="神木树灵",
            realm="通灵·巅峰",
            temperament="gentle",
            avatar_type="procedural",
            quote="神木十万年一涅槃，若愿以精血灵机相助，木灵一族必永生铭记君之恩德。",
        ),
        scene="地底灵泉喷涌之处，一株太古青乙神木正逢十万年涅槃，树冠青华璀璨，正凝结一颗引动九天异象的生机圣果。",
        choices=(
            EncounterChoice(
                id="feed_essence",
                label="舍血相助，浇灌涅槃",
                dao_stance="慈悲仁善",
                tone="safe",
                requirements={"health": 30},
                summary="气血 -25 · 功德 +5 · 寿元 +5 · 灵果 +3",
                description="割破掌心，引自身纯阳本命精血注入神木根须，助其破茧重生。",
                effects={"health_loss": 25, "merit": 5, "lifespan": 5, "resources": {"灵果": 3}},
                outcome_text="神木吸纳真血，刹那间万枝绽放青莲神华！树灵少女感动落泪，将伴生灵果双手捧赠，天道赐福增益你的寿元！",
            ),
            EncounterChoice(
                id="sever_branch",
                label="斩断主干，掠取灵根",
                dao_stance="利欲熏心",
                tone="danger",
                requirements={},
                summary="业障 +5 · 天材地宝 +2 · 地方声望 -10 · 气血 -25",
                description="贪念顿生，趁神木涅槃衰弱之际挥动法宝强斩主干，剥离树心生机。",
                effects={"karma": 5, "resources": {"天材地宝": 2}, "regional_reputation": -10, "health_loss": 25},
                outcome_text="主干断裂，神木发出凄厉悲鸣！古木溃灭化作滚滚枯败煞气反震入体，你夺得神木灵物，却也背负了深重业障。",
            ),
            EncounterChoice(
                id="protect_tree",
                label="结印布阵，护道御灾",
                dao_stance="守中无为",
                tone="primary",
                requirements={"spirit": 30},
                summary="消耗 30 灵力 · 功德 +3 · 道韵 +1 · 灵药 +2",
                description="布设敛息防御大阵，隔绝外界凶兽窥探，护其安然渡过涅槃虚弱期。",
                effects={"spirit_cost": 30, "merit": 3, "resources": {"道韵": 1, "灵药": 2}},
                outcome_text="大阵光幕流转，挡下数批地底凶煞侵扰。涅槃圆满之际，天降甘霖，你收取了纯净道韵与天产灵药！",
            ),
        ),
    ),
    "sword_graveyard": EncounterDefinition(
        id="sword_graveyard",
        title="古剑冢万剑齐鸣",
        category="ancient_secret",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="万劫剑魄",
            identity="剑冢器灵",
            realm="金丹·极境",
            temperament="valiant",
            avatar_type="procedural",
            quote="万载沉沦，折戟沉沙！若无斩断因果之决意，休要在万剑冢前妄动狂言！",
        ),
        scene="荒谷天坑之内，插着上万柄折断的太古神剑，凶煞剑气与冲天剑意交织如网。核心处一柄通体漆黑的无上凶剑剧烈震颤。",
        choices=(
            EncounterChoice(
                id="take_sword",
                label="以身试剑，强拔凶煞",
                dao_stance="杀伐霸道",
                tone="danger",
                requirements={"health": 40},
                summary="气血 -35 · 业障 +2 · 极品灵铁 +2 · 声望 +15",
                description="踏过万剑锋芒，任由剑气割裂法袍道躯，徒手握住凶剑剑柄强行拔起！",
                effects={"health_loss": 35, "karma": 2, "resources": {"灵铁": 2}, "reputation": 15},
                outcome_text="黑煞剑芒撕裂苍穹！狂暴剑魄怒吼挣扎，最终被你霸道无匹的意志强行镇压，万剑齐鸣俯首称臣！",
            ),
            EncounterChoice(
                id="resonate_dao",
                label="引动剑道，清鸣和弦",
                dao_stance="温润悟道",
                tone="primary",
                requirements={"spirit": 25},
                summary="消耗 25 灵力 · 悟道点 +1 · 道法感悟 +35 · 声望 +6",
                description="不争不抢，盘膝抚剑，以自身大道清音与万剑残魂共鸣共感。",
                effects={"spirit_cost": 25, "dao_points": 1, "dao_insight": 35, "reputation": 6, "resources": {"古剑残片": 2}},
                outcome_text="剑冢之内万剑和鸣，化作悠扬仙乐。一柄柄古剑向你垂首致敬，赠予你无上剑道传承与古剑残片！",
            ),
            EncounterChoice(
                id="bury_swords",
                label="立碑敛冢，安息英灵",
                dao_stance="慈悲仁善",
                tone="safe",
                requirements={"stones": 50},
                summary="消耗 50 灵石 · 功德 +4 · 气血回满 · 道心通明",
                description="搬动巨岩为万千战死名剑立冢，燃灵石为祭，告慰古修英魂。",
                effects={"stones_cost": 50, "merit": 4, "health_restore": 999, "condition": "道心通明"},
                outcome_text="石碑立定，剑冢肃杀之气尽化浩然清风。万剑灵辉如流萤环绕你周身，洗涤你身心尘垢，道心一片通透！",
            ),
        ),
    ),
    "righteous_demonic": EncounterDefinition(
        id="righteous_demonic",
        title="正魔暗通仙门机密",
        category="mortal_dust",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="玄阴密使",
            identity="魔门探子",
            realm="筑基·巅峰",
            temperament="cunning",
            avatar_type="procedural",
            quote="既然被你撞破，是识相分一杯羹封口，还是要本座送你神魂俱灭？",
        ),
        scene="荒野古刹夜雨连绵，你偶遇仙门执事与魔宗玄阴密使私会，桌上摆放着仙门防务阵图与大量血玉灵石。",
        choices=(
            EncounterChoice(
                id="report_sect",
                label="悍然出手，缴械呈报",
                dao_stance="行侠仗义",
                tone="primary",
                requirements={"health": 25},
                summary="气血 -15 · 功德 +4 · 声望 +20 · 灵石 +150",
                description="厉声喝止奸逆，雷霆出手击毙密使夺取密图，回山呈交宗门大殿。",
                effects={"health_loss": 15, "merit": 4, "reputation": 20, "stones": 150},
                outcome_text="你以迅雷不及掩耳之势破入古刹，重创恶徒夺下防务图！宗门上下震动，对你重重犒赏，名扬仙门！",
            ),
            EncounterChoice(
                id="blackmail",
                label="敲山震虎，坐地分赃",
                dao_stance="利欲熏心",
                tone="danger",
                requirements={},
                summary="业障 +3 · 灵石 +350 · 血玉 +2 · 声望 -5",
                description="冷眼抱臂走出阴影，亮出道法威压，逼迫两人奉上封口重礼。",
                effects={"karma": 3, "stones": 350, "resources": {"血玉": 2}, "reputation": -5},
                outcome_text="二人面如土色，战战兢兢将厚重灵石与血玉奉上。你收下重宝飘然离去，虽获暴利，心台却隐现业力红线。",
            ),
            EncounterChoice(
                id="join_conspiracy",
                label="暗拓阵图，静观风云",
                dao_stance="城府深沉",
                tone="quiet",
                requirements={"spirit": 15},
                summary="消耗 15 灵力 · 悟道点 +1 · 道法感悟 +20",
                description="隐匿气息，祭出留影玉简将阵图悄然拓印一份，悄无声息退入夜雨之中。",
                effects={"spirit_cost": 15, "dao_points": 1, "dao_insight": 20},
                outcome_text="夜雨遮蔽了你的足迹。你手握仙门阵理玄机，借此印证阵道虚实，于暗影中掌控九州因果棋局。",
            ),
        ),
    ),
    "mortal_drought": EncounterDefinition(
        id="mortal_drought",
        title="凡朝旱荒帝王叩求",
        category="mortal_dust",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="凡世人皇",
            identity="古国帝王",
            realm="凡胎·天子",
            temperament="gentle",
            avatar_type="procedural",
            quote="大旱三年赤地千里……求仙长发慈悲救我万民，国库三百年灵藏任凭仙师取用！",
        ),
        scene="凡尘古国大旱三年，烈日灼焦大地。老迈帝王素服赤足，率文武百官徒步三千里登山叩求仙家，额头鲜血淋漓。",
        choices=(
            EncounterChoice(
                id="rain_blessing",
                label="倾力施法，普降甘霖",
                dao_stance="慈悲济世",
                tone="safe",
                requirements={"spirit": 35},
                summary="消耗 35 灵力 · 功德 +10 · 声望 +25 · 悟道点 +1",
                description="不忍生灵涂炭，登坛踏斗焚香祝祷，倾尽周身灵力引动天地甘霖洗涤八荒。",
                effects={"spirit_cost": 35, "merit": 10, "reputation": 25, "dao_points": 1},
                outcome_text="万丈乌云自九天汇聚，暴雨倾盆而下，旱涸大地生机重焕！千万人皇百姓齐齐伏拜，海量功德金光将你层层环绕！",
            ),
            EncounterChoice(
                id="demand_dragon_vein",
                label="索取灵藏，互利交换",
                dao_stance="利益交换",
                tone="primary",
                requirements={},
                summary="业障 +1 · 灵石 +400 · 天材地宝 +1 · 地方声望 +5",
                description="答应施法解厄，但明确要求交割国库封存的上古天材地宝与灵玉。",
                effects={"karma": 1, "stones": 400, "resources": {"天材地宝": 1}, "regional_reputation": 5},
                outcome_text="一场法雨解去燃眉之急，你如约带走国库最珍贵的天材地宝。凡人奉你为护国国师，利市大发。",
            ),
            EncounterChoice(
                id="ignore_mortal",
                label="仙凡有别，拂袖绝尘",
                dao_stance="冷眼旁观",
                tone="quiet",
                requirements={},
                summary="道心无波，不染红尘",
                description="天道循环自有定数，仙路漫漫不沾因果，拂袖乘风化光而去。",
                effects={},
                outcome_text="你踏云而去，身后哭号声渐行渐远。天地不仁以万物为刍狗，你深吸一口气，继续踏向孤独的长生路。",
            ),
        ),
    ),
    "black_market_orphan": EncounterDefinition(
        id="black_market_orphan",
        title="黑市夺宝与散修遗孤",
        category="mortal_dust",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="落魄孤女",
            identity="落魄散修",
            realm="练气·一层",
            temperament="gentle",
            avatar_type="procedural",
            quote="你们害死我爹娘，休想抢走我家传的破境道书！我纵然粉身碎骨也不给你们！",
        ),
        scene="阴暗黑市窄巷，数名穷凶极恶的劫道煞修将一名衣衫褴褛的少女死死围住，少女嘴角溢血，死抱包裹不放。",
        choices=(
            EncounterChoice(
                id="save_and_adopt",
                label="拔剑诛凶，护佑孤女",
                dao_stance="行侠仗义",
                tone="primary",
                requirements={"health": 20},
                summary="气血 -10 · 功德 +5 · 声望 +10 · 筑基丹 +1",
                description="眼中容不得恃强凌弱，剑气出鞘如惊雷乍起，将劫道恶修立毙当场！",
                effects={"health_loss": 10, "merit": 5, "reputation": 10, "resources": {"筑基丹": 1}},
                outcome_text="剑光落定，恶修伏诛！少女涕零跪谢，将家传珍藏已久的筑基丹赠予恩公，发誓他日必报大恩！",
            ),
            EncounterChoice(
                id="loot_together",
                label="同流合污，落井下石",
                dao_stance="利欲熏心",
                tone="danger",
                requirements={},
                summary="业障 +6 · 灵石 +200 · 灵药 +3 · 声望 -15",
                description="冷笑着加入掠夺阵营，强行掰开少女手指取走遗物，灭口离去。",
                effects={"karma": 6, "stones": 200, "resources": {"灵药": 3}, "reputation": -15},
                outcome_text="你将宝物收入囊中，少女绝望的目光如烙印刻在神魂深处。贪欲得逞，但道心深处已蒙上一层阴翳。",
            ),
            EncounterChoice(
                id="buy_peace",
                label="灵石买断，好聚好散",
                dao_stance="善财免灾",
                tone="safe",
                requirements={"stones": 100},
                summary="消耗 100 灵石 · 功德 +3 · 声望 +6 · 聚气丹 +2",
                description="掷出一袋灵石打发走恶修，买下少女与包裹，保全其性命。",
                effects={"stones_cost": 100, "merit": 3, "reputation": 6, "resources": {"聚气丹": 2}},
                outcome_text="恶修见灵石丰厚骂咧离去。少女感念仙长大德，赠上随身聚气丹，安心踏上凡俗归乡之途。",
            ),
        ),
    ),
    "fox_spirit": EncounterDefinition(
        id="fox_spirit",
        title="灵狐负伤受困托孤",
        category="spirit_creature",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="九尾雪狐",
            identity="青丘灵狐",
            realm="金丹·初期",
            temperament="gentle",
            avatar_type="procedural",
            quote="仙长留步……妾身重伤难返，小儿尚在灵卵之中，求仙长发慈悲救护骨肉，妾身愿献出千年狐珠……",
        ),
        scene="落叶堆积的山谷深处，一只通体如雪的三尾灵狐腹部受重创倒在血泊中，怀里死死捂着一枚散发温润白光的幼狐灵卵。",
        choices=(
            EncounterChoice(
                id="adopt_egg",
                label="赠药疗伤，立契护孤",
                dao_stance="慈悲道缘",
                tone="safe",
                requirements={},
                summary="功德 +6 · 悟道点 +1 · 获得灵宠至宝 · 灵药 +2",
                description="取出身边灵药为雪狐止血，诚心许诺必定悉心照拂幼狐长大成人。",
                effects={"merit": 6, "dao_points": 1, "resources": {"灵药": 2, "道韵": 1}},
                outcome_text="灵狐含泪化去最后灵力，将本命灵光凝结为一枚道韵玄珠赠予你，灵卵亲昵地蹭了蹭你的手背。",
            ),
            EncounterChoice(
                id="kill_for_fur",
                label="剥皮取丹，尽数掠尽",
                dao_stance="杀戮掠夺",
                tone="danger",
                requirements={},
                summary="业障 +5 · 妖兽材料 +4 · 灵石 +180 · 心魔暗生",
                description="眼中只有灵兽皮毛与金丹内丹，毫不留情辣手摧花。",
                effects={"karma": 5, "resources": {"妖兽材料": 4}, "stones": 180, "condition": "心魔暗生"},
                outcome_text="血光四溅，你收割了价值连城的灵狐毛皮与内丹，但灵狐临终前凄厉的诅咒让你眉心隐隐刺痛，心魔暗生。",
            ),
            EncounterChoice(
                id="take_egg_only",
                label="取走灵卵，不问生死",
                dao_stance="适者生存",
                tone="quiet",
                requirements={},
                summary="业障 +1 · 获得异兽机缘",
                description="俯身抱起灵卵放入灵兽袋，对垂死的雪狐不施以援手，转身离去。",
                effects={"karma": 1, "resources": {"妖兽材料": 1}},
                outcome_text="你带走了灵卵，留下了苟延残喘的雪狐。修仙界弱肉强食，谁也无法苛责你的冷漠，但也谈不上光彩。",
            ),
        ),
    ),
    "gu_qingxuan_encounter": EncounterDefinition(
        id="gu_qingxuan_encounter",
        title="青云断剑·顾清玄",
        category="npc_destiny",
        region_affinity="东洲",
        required_realm=0,
        character=EncounterCharacter(
            name="顾清玄",
            identity="青云剑宗真传",
            realm="筑基·中期",
            temperament="gentle",
            avatar_type="preset",
            quote="道友来得正好……此番斩魔，佩剑虽折，心中窒碍却一扫而空。不知在道友眼中，剑修之锋芒，当在手中抑或在心？",
        ),
        scene="青岳绝壁断崖之上，顾清玄独立风中，手中青云佩剑断成两截，身前倒着数头暴毙的三阶魔狼。青年剑修长发微拂，温润眸光望向你。",
        choices=(
            EncounterChoice(
                id="discuss_sword",
                label="席地坐谈，印证心剑",
                dao_stance="知己论道",
                tone="primary",
                requirements={"spirit": 20},
                summary="顾清玄好感 +20 · 道法感悟 +40 · 悟道点 +1 · 声望 +10",
                description="席地盘膝而坐，与这位青云天骄畅论“无剑胜有剑”之心剑境界。",
                effects={"spirit_cost": 20, "npc_affinity": {"顾清玄": 20}, "dao_insight": 40, "dao_points": 1, "reputation": 10},
                outcome_text="顾清玄眼中神采奕奕，抚掌大笑：“妙哉！得友如道友，何愁剑道不通！”二人神识交汇，心意相通，道心大进！",
            ),
            EncounterChoice(
                id="offer_steel",
                label="赠予灵铁，相助铸剑",
                dao_stance="同道互助",
                tone="safe",
                requirements={"resources": {"灵铁": 1}},
                summary="消耗 灵铁×1 · 顾清玄好感 +25 · 功德 +3 · 灵石 +100",
                description="从乾坤袋中取出上佳灵铁递过：“好剑当配君子，清玄兄何妨以此铁再造青云？”",
                effects={"resources_cost": {"灵铁": 1}, "npc_affinity": {"顾清玄": 25}, "merit": 3, "stones": 100},
                outcome_text="顾清玄郑重接下灵铁，深深一揖：“道友厚谊，清玄铭记于心！来日登临九霄，定与君共饮长生酒！”",
            ),
            EncounterChoice(
                id="spar_broken",
                label="邀其切磋，试探断剑",
                dao_stance="以武会友",
                tone="danger",
                requirements={"health": 25},
                summary="气血 -15 · 顾清玄好感 +15 · 修为 +35 · 声望 +12",
                description="长笑拔剑：“既然剑折道存，清玄兄可敢以残剑与我切磋三十招？”",
                effects={"health_loss": 15, "npc_affinity": {"顾清玄": 15}, "cultivation": 35, "reputation": 12},
                outcome_text="断剑出鞘，剑芒撕裂长空！数招对轰畅快淋漓，二人虽各负微伤，却惺惺相惜，战意沸腾！",
            ),
        ),
    ),
    "bai_ningshuang_encounter": EncounterDefinition(
        id="bai_ningshuang_encounter",
        title="极北寒潭·白凝霜",
        category="npc_destiny",
        region_affinity="北原",
        required_realm=0,
        character=EncounterCharacter(
            name="白凝霜",
            identity="雪族圣女",
            realm="结晶·初期",
            temperament="aloof",
            avatar_type="preset",
            quote="潭底有万载玄冰蛟蛰伏，凭我一人难以取莲。道友若愿并肩，极北寒髓与我……皆不相负。",
        ),
        scene="极北风雪呼啸的万载玄冰裂隙中，白凝霜素衣白裙独立寒风，冰肌玉骨上凝着几缕暗红血煞。深潭中央一株九品玄冥冰莲散发沁骨芳香。",
        choices=(
            EncounterChoice(
                id="dual_cultivate_warmth",
                label="真火护体，共斩冰蛟",
                dao_stance="同心协力",
                tone="primary",
                requirements={"spirit": 30},
                summary="消耗 30 灵力 · 白凝霜好感 +25 · 冰莲 +1 · 功德 +3 · 悟道点 +1",
                description="催动纯阳真气替她驱散体内寒毒，并肩跃入寒潭力战万载冰蛟！",
                effects={"spirit_cost": 30, "npc_affinity": {"白凝霜": 25}, "resources": {"冰莲": 1}, "merit": 3, "dao_points": 1},
                outcome_text="纯阳炽焰与冰魄玄光交相辉映，恶蛟哀鸣伏诛！白凝霜苍白的脸庞泛起一抹微红，将采下的冰莲亲手赠予你。",
            ),
            EncounterChoice(
                id="seize_lotus",
                label="趁危夺莲，夺宝遁走",
                dao_stance="唯利是图",
                tone="danger",
                requirements={},
                summary="白凝霜好感 -45 · 业障 +4 · 冰莲 +2 · 气血 -30",
                description="趁其受寒毒反噬无力还击，疾速采下双生冰莲转身御风遁走！",
                effects={"npc_affinity": {"白凝霜": -45}, "karma": 4, "resources": {"冰莲": 2}, "health_loss": 30},
                outcome_text="白凝霜眼中闪过一抹难以置信与森寒杀意，拼力一击冰魄神光轰在你背心！你吐血重伤遁逃，彻底结下死仇。",
            ),
            EncounterChoice(
                id="stand_guard",
                label="岸边护法，君子之交",
                dao_stance="君子有道",
                tone="safe",
                requirements={},
                summary="白凝霜好感 +18 · 雪晶 +3 · 声望 +8",
                description="手按剑柄伫立岸边警惕四周雪兽，不染半分贪念，守护她自行调息取莲。",
                effects={"npc_affinity": {"白凝霜": 18}, "resources": {"雪晶": 3}, "reputation": 8},
                outcome_text="白凝霜安然取莲而归，清冷双眸中多了一分少见的柔和，赠予你数枚雪族至宝雪晶以示谢意。",
            ),
        ),
    ),
    "yun_qi_encounter": EncounterDefinition(
        id="yun_qi_encounter",
        title="流沙遇伏·云栖",
        category="npc_destiny",
        region_affinity="西漠",
        required_realm=0,
        character=EncounterCharacter(
            name="云栖",
            identity="天机灵贾",
            realm="筑基·初期",
            temperament="cunning",
            avatar_type="preset",
            quote="哎呀！贵客道友救命！只要击退这帮流沙匪徒，天机阁此趟商队三成收益都是你的！绝不反悔！",
        ),
        scene="西漠万顷狂暴沙暴中，天机阁商队被十数名蒙面沙盗死死围困。云栖金雀步摇微散，金算盘灵光激荡，眼波流转中如见救星。",
        choices=(
            EncounterChoice(
                id="charge_rescue",
                label="破浪拔刀，横扫沙盗",
                dao_stance="行侠仗义",
                tone="primary",
                requirements={"health": 25},
                summary="气血 -15 · 云栖好感 +25 · 灵石 +350 · 灵石匣 +1 · 声望 +15",
                description="身化长虹杀入沙盗群中，雷霆手段将劫匪头目斩于刀下！",
                effects={"health_loss": 15, "npc_affinity": {"云栖": 25}, "stones": 350, "resources": {"灵石匣": 1}, "reputation": 15},
                outcome_text="沙匪作鸟兽散！云栖拍了拍胸口巧笑嫣然，不仅如约奉上沉甸甸的灵石，更悄悄将精致灵石匣塞入你怀中。",
            ),
            EncounterChoice(
                id="negotiate_ransom",
                label="金舌巧辩，威慑群寇",
                dao_stance="智谋化解",
                tone="safe",
                requirements={"reputation": 15},
                summary="云栖好感 +20 · 灵石 +200 · 声望 +10",
                description="气度从容走上前台，摆出大宗门威仪与天下声威，言辞诛心逼退沙匪。",
                effects={"npc_affinity": {"云栖": 20}, "stones": 200, "reputation": 10},
                outcome_text="沙匪首领面带忌惮，权衡利弊后抱拳退走。云栖明眸善睐惊叹道：“道友真乃神人也，一言退万寇！”",
            ),
            EncounterChoice(
                id="split_loot",
                label="暗通款曲，反戈洗劫",
                dao_stance="黑吃黑",
                tone="danger",
                requirements={},
                summary="云栖好感 -50 · 业障 +5 · 灵石 +600 · 声望 -20",
                description="冷眼旁观后与沙匪对视一眼，悍然联手将天机阁商队掠劫一空！",
                effects={"npc_affinity": {"云栖": -50}, "karma": 5, "stones": 600, "reputation": -20},
                outcome_text="云栖在护卫死战掩护下遁逃，望向你的目光充满厌恶与仇恨。你分得巨量灵石，天机阁的通缉令却已暗中布下。",
            ),
        ),
    ),
    "luo_qianqian_encounter": EncounterDefinition(
        id="luo_qianqian_encounter",
        title="月下情丝·洛浅浅",
        category="npc_destiny",
        region_affinity="",
        required_realm=0,
        character=EncounterCharacter(
            name="洛浅浅",
            identity="合欢宗嫡传",
            realm="结丹·初期",
            temperament="charm",
            avatar_type="preset",
            quote="长夜漫漫，仙长何必苦苦执着枯燥长生？不如与浅浅在此共度春宵，印证欢喜禅法，岂不快活胜神仙？",
        ),
        scene="幽篁竹林月色迷离，粉红轻雾中弥漫着摄人心魄的合欢异香。洛浅浅斜倚青石，罗衣半解，眼波流转若春水，纤指轻绕情丝。",
        choices=(
            EncounterChoice(
                id="dao_heart_iron",
                label="道心若磐，法剑斩情",
                dao_stance="道心通明",
                tone="primary",
                requirements={},
                summary="洛浅浅好感 +15 · 悟道点 +1 · 道法感悟 +30 · 祛除心魔",
                description="默运清心太虚诀，双眸澄澈如寒水，指尖微动一道纯阳剑气斩断粉红情丝！",
                effects={"npc_affinity": {"洛浅浅": 15}, "dao_points": 1, "dao_insight": 30, "condition": "无"},
                outcome_text="情丝寸断，粉雾退散！洛浅浅不仅未恼，反倒收敛了魅惑，美眸异彩涟涟：“这红尘世间，竟真有坐怀不乱的真君子……”",
            ),
            EncounterChoice(
                id="surrender_passion",
                label="将计就计，琴瑟和鸣",
                dao_stance="红尘逍遥",
                tone="safe",
                requirements={"spirit": 20},
                summary="消耗 20 灵力 · 洛浅浅好感 +25 · 修为 +50 · 气血回满 · 业障 +1",
                description="微微一笑顺水推舟，与妖女于月下竹影间参悟阴阳互济之道。",
                effects={"spirit_cost": 20, "npc_affinity": {"洛浅浅": 25}, "cultivation": 50, "health_restore": 999, "karma": 1},
                outcome_text="春水生情，云雨方歇。在合欢秘术互哺下你修为暴涨周身气血充盈，洛浅浅依偎在你怀中，悄然将一缕心神系于你身。",
            ),
            EncounterChoice(
                id="slay_enchantress",
                label="怒斥魔妖，雷霆轰杀",
                dao_stance="铁血无情",
                tone="danger",
                requirements={"health": 25},
                summary="气血 -10 · 洛浅浅好感 -30 · 灵石 +120 · 声望 +10",
                description="眼中杀机毕露，冷叱一声魔门妖孽，催动绝杀法术直取其要害！",
                effects={"health_loss": 10, "npc_affinity": {"洛浅浅": -30}, "stones": 120, "reputation": 10},
                outcome_text="轰鸣巨响中洛浅浅化作彩蝶残影负伤遁走，恨恨留下一句娇斥。你拾起掉落的零散灵石，杀意凛然。",
            ),
        ),
    ),
}


class RedDustEncounterEngine:
    @classmethod
    def get_candidate_ids(cls, state: GameState, region_key: str = "") -> list[str]:
        current_region = region_key or TravelEngine.current_region(state)
        candidates = []
        for enc_id, enc in ENCOUNTERS_CATALOG.items():
            if enc.unique and enc_id in state.completed_encounters:
                continue
            if state.player.realm_index < enc.required_realm:
                continue
            if enc.region_affinity and enc.region_affinity != current_region:
                continue
            candidates.append(enc_id)
        return candidates or list(ENCOUNTERS_CATALOG.keys())

    @classmethod
    def trigger_encounter(
        cls,
        state: GameState,
        context: str = "travel",
        forced_id: str = "",
    ) -> dict[str, Any] | None:
        """Trigger an encounter, updating state.phase to 'encounter_choice'."""
        if forced_id and forced_id in ENCOUNTERS_CATALOG:
            target_id = forced_id
        else:
            region_key = TravelEngine.current_region(state)
            candidates = cls.get_candidate_ids(state, region_key)
            if not candidates:
                return None
            roll = ProgressionEngine.deterministic_roll(
                state, f"encounter:{state.turn}:{context}:{region_key}"
            )
            # Pick deterministically from candidates
            target_id = candidates[roll % len(candidates)]

        enc = ENCOUNTERS_CATALOG[target_id]
        state.pending_encounter = {
            "id": enc.id,
            "title": enc.title,
            "category": enc.category,
            "character": {
                "name": enc.character.name,
                "identity": enc.character.identity,
                "realm": enc.character.realm,
                "temperament": enc.character.temperament,
                "avatar_type": enc.character.avatar_type,
                "quote": enc.character.quote,
            },
            "scene": enc.scene,
            "context": context,
            "turn": state.turn,
        }
        state.phase = "encounter_choice"
        return state.pending_encounter

    @classmethod
    def check_requirements(cls, state: GameState, reqs: dict[str, Any]) -> list[str]:
        missing = []
        player = state.player
        if "realm_index" in reqs and player.realm_index < reqs["realm_index"]:
            required = REALMS[min(reqs["realm_index"], len(REALMS) - 1)]
            missing.append(f"境界需达{required}")
        if "spirit" in reqs and player.spirit < reqs["spirit"]:
            missing.append(f"灵力需 {reqs['spirit']} 点（当前 {player.spirit}）")
        if "health" in reqs and player.health < reqs["health"]:
            missing.append(f"气血需 {reqs['health']} 点（当前 {player.health}）")
        if "stones" in reqs and player.spirit_stones < reqs["stones"]:
            missing.append(f"灵石需 {reqs['stones']} 枚（当前 {player.spirit_stones}）")
        if "reputation" in reqs and player.reputation < reqs["reputation"]:
            missing.append(f"声望需达 {reqs['reputation']}")
        if "resources" in reqs:
            for item, count in reqs["resources"].items():
                have = player.resources.get(item, 0)
                if have < count:
                    missing.append(f"{item}×{count}（当前拥有 {have}）")
        return missing

    @classmethod
    def resolve(cls, state: GameState, choice_id: str) -> dict[str, Any]:
        """Resolve the player's choice in the pending encounter."""
        pending = state.pending_encounter
        if not pending or state.phase != "encounter_choice":
            raise ValueError("当前没有等待决断的红尘奇遇。")

        enc_id = pending["id"]
        if enc_id not in ENCOUNTERS_CATALOG:
            state.phase = "playing"
            state.pending_encounter = {}
            raise ValueError("奇遇数据异常，已自动归位。")

        enc = ENCOUNTERS_CATALOG[enc_id]
        choice_obj = next((c for c in enc.choices if c.id == choice_id), None)
        if choice_obj is None:
            # try fuzzy matching by label
            choice_obj = next((c for c in enc.choices if choice_id in (c.label, c.id)), None)
        if choice_obj is None:
            options = "、".join(f"{c.id}({c.label})" for c in enc.choices)
            raise ValueError(f"未知抉择选项。可选：{options}")

        # Check requirements
        missing = cls.check_requirements(state, choice_obj.requirements)
        if missing:
            raise ValueError(f"条件不满足：{'、'.join(missing)}")

        player = state.player
        effects = choice_obj.effects
        applied_logs: list[str] = []

        # Deduct costs
        if "spirit_cost" in effects:
            cost = effects["spirit_cost"]
            player.spirit = max(0, player.spirit - cost)
            applied_logs.append(f"灵力 -{cost}")
        if "health_loss" in effects:
            loss = effects["health_loss"]
            player.health = max(1, player.health - loss)
            applied_logs.append(f"气血 -{loss}")
        if "stones_cost" in effects:
            cost = effects["stones_cost"]
            player.spirit_stones = max(0, player.spirit_stones - cost)
            applied_logs.append(f"灵石 -{cost}")
        if "resources_cost" in effects:
            for item, count in effects["resources_cost"].items():
                player.resources[item] = max(0, player.resources.get(item, 0) - count)
                applied_logs.append(f"消耗 {item}×{count}")

        # Grant rewards / effects
        if "merit" in effects:
            val = effects["merit"]
            player.merit += val
            applied_logs.append(f"功德 {val:+d}")
        if "karma" in effects:
            val = effects["karma"]
            player.karma += val
            applied_logs.append(f"业障 {val:+d}")
        if "reputation" in effects:
            val = effects["reputation"]
            player.reputation += val
            applied_logs.append(f"声望 {val:+d}")
        if "regional_reputation" in effects:
            val = effects["regional_reputation"]
            from .regional import RegionalEngine
            current_reg = RegionalEngine.current_region(state)
            RegionalEngine.adjust(state, current_reg, val)
            applied_logs.append(f"{current_reg}声望 {val:+d}")
        if "dao_points" in effects:
            val = effects["dao_points"]
            player.dao_points += val
            applied_logs.append(f"悟道点 +{val}")
        if "dao_insight" in effects:
            val = effects["dao_insight"]
            player.dao_insight += val
            applied_logs.append(f"感悟 +{val}")
        if "cultivation" in effects:
            val = effects["cultivation"]
            player.cultivation = min(player.cultivation_required, player.cultivation + val)
            applied_logs.append(f"修为 +{val}")
        if "health_restore" in effects:
            restore = effects["health_restore"]
            before = player.health
            player.health = min(player.health_max, player.health + restore)
            applied_logs.append(f"气血恢复 +{player.health - before}")
        if "spirit_restore" in effects:
            restore = effects["spirit_restore"]
            before = player.spirit
            player.spirit = min(player.spirit_max, player.spirit + restore)
            applied_logs.append(f"灵力恢复 +{player.spirit - before}")
        if "lifespan" in effects:
            val = effects["lifespan"]
            player.lifespan += val
            applied_logs.append(f"寿元 +{val} 年")
        if "stones" in effects:
            val = effects["stones"]
            player.spirit_stones += val
            applied_logs.append(f"灵石 +{val}")
        if "resources" in effects:
            for item, count in effects["resources"].items():
                player.resources[item] = player.resources.get(item, 0) + count
                applied_logs.append(f"{item} +{count}")
        if "condition" in effects:
            cond = effects["condition"]
            player.condition = cond
            applied_logs.append(f"状态变为【{cond}】")

        # Handle NPC affinity
        if "npc_affinity" in effects:
            from .relationships import RelationshipEngine
            for npc_name, aff_change in effects["npc_affinity"].items():
                try:
                    RelationshipEngine.adjust(state, npc_name, aff_change, reason=f"红尘奇遇《{enc.title}》")
                    applied_logs.append(f"{npc_name}好感 {aff_change:+d}")
                except Exception:
                    # fallback if RelationshipEngine not active for this name
                    rel = state.npc_relations.setdefault(npc_name, {"affinity": 0, "path": "相识"})
                    rel["affinity"] = max(0, min(100, int(rel.get("affinity", 0)) + aff_change))
                    applied_logs.append(f"{npc_name}好感 {aff_change:+d}")

        # Update completed records
        state.completed_encounters.append(enc.id)
        log_entry = f"经历《{enc.title}》选择【{choice_obj.label}】（{choice_obj.dao_stance}）：{'、'.join(applied_logs)}"
        state.encounter_history.append(log_entry)
        state.encounter_history = state.encounter_history[-30:]
        state.remember(log_entry)

        # Clear pending
        state.pending_encounter = {}
        state.phase = "playing"

        return {
            "encounter_id": enc.id,
            "title": enc.title,
            "character_name": enc.character.name,
            "choice_id": choice_obj.id,
            "choice_label": choice_obj.label,
            "dao_stance": choice_obj.dao_stance,
            "outcome_text": choice_obj.outcome_text,
            "applied_effects": applied_logs,
        }

    @classmethod
    def decision(cls, state: GameState) -> dict[str, Any]:
        """Produce choices dictionary for DecisionCatalog."""
        pending = state.pending_encounter
        if not pending or state.phase != "encounter_choice":
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}

        enc_id = pending["id"]
        if enc_id not in ENCOUNTERS_CATALOG:
            return {"eyebrow": "", "title": "", "hint": "", "exclusive": False, "choices": []}

        enc = ENCOUNTERS_CATALOG[enc_id]
        choices = []
        for choice in enc.choices:
            missing = cls.check_requirements(state, choice.requirements)
            choices.append({
                "label": choice.label,
                "action": f"奇遇选择 {choice.id}",
                "summary": choice.summary,
                "description": f"【{choice.dao_stance}】{choice.description}",
                "tooltip": f"道心立场：{choice.dao_stance} · {choice.summary}",
                "tone": choice.tone,
                "disabled": bool(missing),
                "disabled_reason": "缺少 " + "、".join(missing) if missing else "",
            })

        return {
            "eyebrow": f"红尘奇遇 · {enc.category}",
            "title": f"《{enc.title}》· 抉择本心",
            "hint": f"{enc.character.name}（{enc.character.identity}）正注视着你。道心一念，善恶因果皆将深植于命格之中。",
            "exclusive": True,
            "choices": choices,
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        """Return encounter snapshot for frontend serialization."""
        pending_raw = state.pending_encounter
        pending_view = None
        if pending_raw and pending_raw.get("id") in ENCOUNTERS_CATALOG:
            enc = ENCOUNTERS_CATALOG[pending_raw["id"]]
            choices_view = []
            for c in enc.choices:
                missing = cls.check_requirements(state, c.requirements)
                choices_view.append({
                    "id": c.id,
                    "label": c.label,
                    "dao_stance": c.dao_stance,
                    "tone": c.tone,
                    "summary": c.summary,
                    "description": c.description,
                    "disabled": bool(missing),
                    "disabled_reason": "、".join(missing) if missing else "",
                })
            pending_view = {
                "id": enc.id,
                "title": enc.title,
                "category": enc.category,
                "character": {
                    "name": enc.character.name,
                    "identity": enc.character.identity,
                    "realm": enc.character.realm,
                    "temperament": enc.character.temperament,
                    "avatar_type": enc.character.avatar_type,
                    "quote": enc.character.quote,
                },
                "scene": enc.scene,
                "choices": choices_view,
            }

        return {
            "active": state.phase == "encounter_choice",
            "pending": pending_view,
            "completed_count": len(state.completed_encounters),
            "completed_ids": list(state.completed_encounters),
            "history": list(state.encounter_history[-10:]),
        }

    @classmethod
    def text_panel(cls, state: GameState) -> str:
        """Textual display for CLI console."""
        pending = state.pending_encounter
        if not pending or state.phase != "encounter_choice":
            return "【九州红尘奇遇】\n天下浩渺，红尘万丈。当前暂无等待抉择之机缘。可输入“寻觅机缘”主动寻访游历。"

        enc_id = pending["id"]
        enc = ENCOUNTERS_CATALOG[enc_id]
        lines = [
            f"╔════════════════════════════════════════════════════════════════╗",
            f"  【红尘奇遇 · {enc.title}】（{enc.character.identity} · {enc.character.name}）",
            f"╚════════════════════════════════════════════════════════════════╝",
            f"\n场景风貌：\n{enc.scene}\n",
            f"人物言谈（{enc.character.name} · {enc.character.realm}）：\n“{enc.character.quote}”\n",
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"可供抉择之本心分支：",
        ]
        for idx, c in enumerate(enc.choices, 1):
            missing = cls.check_requirements(state, c.requirements)
            status_tag = f"【暂不可选：{'、'.join(missing)}】" if missing else "【可行】"
            lines.append(f"{idx}. 【{c.dao_stance}】{c.label} ({c.id}) {status_tag}")
            lines.append(f"   说明：{c.description}")
            lines.append(f"   因果预知：{c.summary}")
        lines.append(f"\n指令格式：奇遇选择 <选项ID> （例如：奇遇选择 {enc.choices[0].id}）")
        return "\n".join(lines)
