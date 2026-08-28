(() => {
  const ui = window.xiuxianUi;
  if (!ui) return;

  const byId = (id) => document.getElementById(id);
  const clone = (value) => JSON.parse(JSON.stringify(value));
  const emptyDecision = () => ({ eyebrow: "", title: "", hint: "", exclusive: false, choices: [] });
  let liveSnapshot = null;
  let currentIndex = 0;

  function demoBase(source) {
    const snapshot = clone(source);
    const state = snapshot.state;
    const player = state.player;
    state.phase = "playing";
    state.turn = 12;
    state.calendar_year = 387;
    state.month = 12;
    state.main_quest = "灵气潮汐将至";
    state.last_world_event = "东洲灵脉异动，各宗门正在暗中探查。";
    state.history = [
      "第 12 回合｜天玄历 387 年 · 冬十二月｜青岳山麓发现灵脉异动",
      "第 11 回合｜天玄历 387 年 · 冬十一月｜与顾清玄论道一夜",
      "第 10 回合｜天玄历 387 年 · 冬十月｜完成青云宗巡山任务",
      "第 9 回合｜天玄历 387 年 · 秋九月｜坊市购得聚气丹",
      "第 8 回合｜天玄历 387 年 · 秋八月｜初次探索百草谷",
    ];
    state.npc_relations = {};
    state.relationship_tension = 0;
    state.active_sect_war = {};
    Object.assign(player, {
      name: "沈砚", dao_name: "清微", gender: "男", age: 19, lifespan: 100,
      realm: "炼气·后期", realm_index: 0, stage_index: 2, sect: "青云宗", sect_rank: "内门弟子",
      location: "东洲·青岳", spirit_stones: 286, health: 84, health_max: 100,
      spirit: 72, spirit_max: 100, cultivation: 76, cultivation_required: 100,
      resources: { "聚气丹": 3, "疗伤丹": 1, "灵药": 8, "青锋剑": 1 },
    });
    snapshot.presentation = {
      title: "洞府清晨", eyebrow: "仙途日常", seal: "居", tone: "story",
      paragraphs: ["晨雾沿着青岳山腰散去，洞府外传来灵鹤清鸣。", "今日无强制事件，你可以自由安排修炼、出行或人际往来。"],
      changes: [], blocks: [], details: "成果巡览展示数据，不参与真实结算。", has_details: true,
    };
    snapshot.decision = emptyDecision();
    snapshot.save_summaries = [
      { name: "筑基之前", dao_name: "清微", player_name: "沈砚", realm: "炼气·后期", calendar_year: 387, month: 12, turn: 12 },
      { name: "初入青云", dao_name: "清微", player_name: "沈砚", realm: "炼气·中期", calendar_year: 387, month: 7, turn: 7 },
    ];
    return snapshot;
  }

  const presentation = (options) => ({
    title: options.title,
    eyebrow: options.eyebrow || "成果巡览",
    seal: options.seal || "验",
    tone: options.tone || "story",
    paragraphs: options.paragraphs || [],
    changes: options.changes || [],
    blocks: options.blocks || [],
    details: options.details || "此页使用真实组件与展示数据生成，不会写入存档。",
    has_details: options.hasDetails !== false,
  });

  const scenes = [
    {
      label: "01 · 初始入世",
      description: "检查欢迎叙事、第一项重大选择与空状态。",
      checks: ["主剧情视觉重心", "抉择按钮是否明确", "左右空状态是否友好"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.phase = "new";
        snapshot.state.turn = 0;
        snapshot.state.player.resources = {};
        snapshot.state.history = [];
        snapshot.presentation = presentation({ title: "灵气潮汐将至", eyebrow: "天道初启", seal: "道", paragraphs: ["九州云海未定，你的长生路尚待落笔。", "点击抉择，踏入这方修真世界。"], hasDetails: false });
        snapshot.decision = { eyebrow: "轮回之始", title: "是否踏入仙途？", hint: "这会开启一段新的修仙人生。", exclusive: true, choices: [{ label: "踏入仙途", action: "开始游戏", description: "开启世界并进入创角。", tone: "primary" }] };
        return snapshot;
      },
    },
    {
      label: "02 · 角色创建",
      description: "检查创角说明、默认角色选择和自由输入区域。",
      checks: ["创角信息是否易扫读", "默认角色入口是否突出", "输入区是否仍然清楚"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.phase = "character_creation_basic";
        snapshot.state.turn = 1;
        snapshot.presentation = presentation({ title: "创角大面板", eyebrow: "仙途初启", seal: "创", tone: "system", paragraphs: ["灵气潮汐将至，你尚是芸芸众生之一。", "可以使用默认角色快速试玩，也可以在下方输入完整资料。"], blocks: [{ type: "list", mark: "资", title: "创角资料", items: [{ text: "灵根、体质、六维 60 点与天赋 5 点" }, { text: "姓名、性别、年龄、相貌、出身与道途均可自定义" }, { text: "完成后所有加成写入结构化状态" }], preview: 3 }] });
        snapshot.decision = { eyebrow: "创角选择", title: "快速试玩或自行落笔", hint: "默认角色可立即开始；自定义资料可在下方输入。", exclusive: true, choices: [{ label: "使用默认角色", action: "确认默认创角", description: "以沈砚·清微的默认配置进入九州。", tone: "safe" }] };
        return snapshot;
      },
    },
    {
      label: "03 · 洞府主界面",
      description: "检查常规游玩时的属性、背包、行动和经历布局。",
      checks: ["三栏主次是否清楚", "状态条数值是否醒目", "一键行动与草稿是否易区分"],
      build: demoBase,
    },
    {
      label: "04 · 探索地图",
      description: "检查地点风险、境界锁定、响应式网格和探索按钮。",
      checks: ["难度颜色与 Tooltip", "锁定地点是否明确", "标题固定、数据区独立滚动"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.presentation = presentation({ title: "东洲探索地图", eyebrow: "山河游历", seal: "图", tone: "adventure", paragraphs: ["东洲山河已展开，请根据境界与当前状态选择去处。"], blocks: [{ type: "locations", mark: "图", title: "东洲探索地图", legend: "危险度表示遭遇强敌与不利事件的风险，不是奖励点数；境界不足的地点会自动锁定。", items: [
          { name: "青岳山麓", requirement_label: "炼气境", accessible: true, visited: true, danger: 12, danger_label: "低危", tone: "safe", help: "适合初次探索，仍可能遭遇意外。", danger_help: "危险度 12：风险较低，但并非绝对安全。" },
          { name: "百草谷", requirement_label: "炼气境", accessible: true, visited: true, danger: 18, danger_label: "寻常", tone: "normal", help: "灵药繁盛，也常有妖兽出没。", danger_help: "危险度 18：存在明确风险与收益。" },
          { name: "迷雾山谷", requirement_label: "筑基境", accessible: false, locked_reason: "需要达到筑基境才可进入", danger: 28, danger_label: "高危", tone: "warning", help: "雾中神识受阻，容易遭遇强敌。", danger_help: "危险度 28：高风险区域，建议筑基后进入。" },
          { name: "古战场外围", requirement_label: "结晶境", accessible: false, locked_reason: "需要达到结晶境才可进入", danger: 38, danger_label: "绝境", tone: "danger", help: "阴煞汇聚，准备不足可能丧命。", danger_help: "危险度 38：可能触发致命事件。" },
          { name: "丹霞古道", requirement_label: "炼气境", accessible: true, danger: 22, danger_label: "寻常", tone: "normal", help: "商旅与散修往来频繁，也有劫修窥伺。", danger_help: "危险度 22：收益有所提高，也更容易遭遇争斗。" },
          { name: "断魂崖", requirement_label: "金丹境", accessible: false, locked_reason: "需要达到金丹境才可进入", danger: 46, danger_label: "绝境", tone: "danger", help: "罡风终年不息，低阶修士难以立足。", danger_help: "危险度 46：远超当前承受范围。" },
        ] }] });
        return snapshot;
      },
    },
    {
      label: "05 · 坊市交易",
      description: "检查货币、价格、物品信息和交易结果的结构化展示。",
      checks: ["灵石变化是否直观", "商品价格是否易比较", "物品详情与获得提示是否可见"],
      toast: { message: "宝物已入袋 · 聚气丹 +1", tone: "treasure" },
      build(source) {
        const snapshot = demoBase(source);
        snapshot.presentation = presentation({ title: "青岳坊市", eyebrow: "坊市往来", seal: "市", tone: "trade", paragraphs: ["檐下铜铃轻响，各家摊位已经开张。", "买卖会由规则引擎核对灵石与持有数量。"], changes: [{ label: "灵石", seal: "石", value: "-20", tone: "wealth" }, { label: "聚气丹", seal: "物", value: "+1", tone: "item" }], blocks: [{ type: "facts", mark: "易", title: "本次成交", items: [{ label: "物品", value: "聚气丹 ×1" }, { label: "单价", value: "20 灵石" }, { label: "成交后", value: "266 灵石" }] }, { type: "list", mark: "货", title: "坊市货架", items: [{ text: "聚气丹｜买 20／卖 12 灵石" }, { text: "疗伤丹｜买 60／卖 36 灵石" }, { text: "青锋剑｜买 180／卖 108 灵石" }, { text: "护身法袍｜买 220／卖 132 灵石" }], preview: 3 }] });
        return snapshot;
      },
    },
    {
      label: "06 · 宗门事务",
      description: "检查身份、贡献、任务和宗门动态组件。",
      checks: ["身份与贡献是否明确", "任务信息是否紧凑", "宗门事件是否有层级"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.player.sect_contribution = 148;
        snapshot.presentation = presentation({ title: "青云宗山门", eyebrow: "宗门因果", seal: "宗", tone: "sect", paragraphs: ["晨钟响彻群峰，执事堂新放出一批宗门任务。"], blocks: [{ type: "facts", mark: "令", title: "弟子名录", items: [{ label: "身份", value: "内门弟子" }, { label: "贡献", value: "148" }, { label: "声望", value: "22" }, { label: "权限", value: "藏经阁二层" }] }, { type: "list", mark: "务", title: "可接任务", items: [{ text: "巡山｜稳妥｜贡献 +10" }, { text: "猎妖｜有风险｜贡献 +12" }, { text: "护送｜需道心判定｜贡献 +14" }], preview: 3 }] });
        return snapshot;
      },
    },
    {
      label: "07 · 人物情缘",
      description: "检查人物小组件、好感进度和右侧牵绊面板。",
      checks: ["人物信息是否避免长串", "好感关系是否直观", "右侧面板是否平衡"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.relationship_tension = 46;
        snapshot.state.npc_relations = { "顾清玄": { affinity: 74, path: "道侣" }, "云栖": { affinity: 38, path: "知己" }, "陆沉舟": { affinity: 12, path: "同门" } };
        snapshot.presentation = presentation({ title: "故人来访", eyebrow: "红尘一念", seal: "缘", tone: "relation", paragraphs: ["顾清玄踏着晨雾来到洞府前，手中提着一壶新茶。"], changes: [{ label: "顾清玄好感", seal: "缘", value: "+4", tone: "relation" }], blocks: [{ type: "people", mark: "人", title: "相关人物", preview: 2, items: [
          { name: "顾清玄", gender: "男", age: "24岁", identity: "青云宗真传", descriptor: "温润剑修", realm: "筑基·后期", relation: "道侣", affinity: 74, location: "青云宗" },
          { name: "云栖", gender: "女", age: "25岁", identity: "天机坊市老板娘", descriptor: "聪慧狡黠", realm: "筑基·中期", relation: "知己", affinity: 38, location: "天机坊市" },
          { name: "陆沉舟", gender: "男", age: "22岁", identity: "青云宗内门", descriptor: "寡言刀修", realm: "炼气·圆满", relation: "同门", affinity: 12, location: "青岳" },
        ] }, { type: "meter", mark: "情", title: "尘缘波澜", value: 46, max: 100, summary: "数段心意正在交汇，未来可能触发情劫。" }] });
        return snapshot;
      },
    },
    {
      label: "08 · 战斗抉择",
      description: "检查敌我情报、危险提示与战斗行动按钮。",
      checks: ["敌我差距是否醒目", "危险选择是否有语义色", "战斗按钮是否便于操作"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.phase = "combat_ready";
        snapshot.presentation = presentation({ title: "雾隐妖蟒拦路", eyebrow: "斗法交锋", seal: "战", tone: "combat", paragraphs: ["山雾中鳞光一闪，雾隐妖蟒封住了退路。", "对方境界略高，正面交锋可能受伤。"], blocks: [{ type: "facts", mark: "敌", title: "敌方情报", items: [{ label: "境界", value: "筑基·初期" }, { label: "五行", value: "水" }, { label: "威胁", value: "高" }, { label: "弱点", value: "雷、火" }] }] });
        snapshot.decision = { eyebrow: "战前抉择", title: "如何应对雾隐妖蟒？", hint: "展示模式不会真正进入战斗。", exclusive: true, choices: [{ label: "拔剑迎战", action: "开战", description: "进入真实回合制战斗。", tone: "danger" }, { label: "施展遁术", action: "遁走", description: "尝试脱离此地，失败可能遭受追击。", tone: "quiet" }] };
        return snapshot;
      },
    },
    {
      label: "09 · 秘境探索",
      description: "检查秘境阶段、成功率、临时收获与退出选择。",
      checks: ["阶段进度是否明确", "风险和收益是否分开", "退出秘境是否容易找到"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.phase = "adventure";
        snapshot.presentation = presentation({ title: "通灵秘境 · 阵法核心", eyebrow: "山河游历", seal: "秘", tone: "adventure", paragraphs: ["青色阵纹在石壁间次第亮起，前方灵雾比外围更加浓郁。"], blocks: [{ type: "meter", mark: "进", title: "秘境进度", value: 2, max: 3, summary: "已通过秘境外围，正在探索阵法核心。" }, { type: "facts", mark: "获", title: "临时收获", items: [{ label: "灵药", value: "×4" }, { label: "灵石", value: "36" }, { label: "成功率", value: "82%" }] }] });
        return snapshot;
      },
    },
    {
      label: "10 · 突破路线",
      description: "检查人道、地道、天道三路线的重大选择。",
      checks: ["路线差异是否清楚", "材料需求是否可读", "重大选择是否足够突出"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.phase = "major_breakthrough_choice";
        snapshot.state.player.realm = "炼气·圆满";
        snapshot.state.player.cultivation = 100;
        snapshot.state.player.resources["筑基丹"] = 1;
        snapshot.presentation = presentation({ title: "筑基之门", eyebrow: "破境问道", seal: "破", tone: "breakthrough", paragraphs: ["周天灵力已经圆满，道基将由你此刻的选择定形。"], blocks: [{ type: "facts", mark: "基", title: "突破准备", items: [{ label: "当前境界", value: "炼气·圆满" }, { label: "修为", value: "100 / 100" }, { label: "道心", value: "14" }, { label: "冷却", value: "无" }] }] });
        snapshot.decision = { eyebrow: "破境路线", title: "选择此番道基", hint: "路线越高，风险与未来潜力越大。", exclusive: true, choices: [
          { label: "人道筑基", action: "突破 人道", summary: "筑基丹×1 · 心魔 97% / 雷劫 97%", description: "成功率最高，道基潜力平稳。", tooltip: "风险最低，成功后气血与灵力小幅增长。", tone: "safe" },
          { label: "地道筑基", action: "突破 地道", summary: "天材地宝×1 · 当前材料不足", description: "风险与潜力均衡。", disabled: true, disabled_reason: "缺少天材地宝×1", tone: "primary" },
          { label: "天道筑基", action: "突破 天道", summary: "三类天材 · 当前材料不足", description: "风险最高，潜力也最强。", disabled: true, disabled_reason: "缺少天材地宝×1、五行灵珠×1、道韵×1", tone: "danger" },
          { label: "暂缓突破", action: "取消突破", description: "保留当前状态，稍后再作决定。", tone: "quiet" },
        ] };
        return snapshot;
      },
    },
    {
      label: "11 · 天下局势",
      description: "检查宗门盛衰、地域民生与世界事件展示。",
      checks: ["世界信息是否易扫读", "数值卡片是否不过载", "九州风声是否与主事件分工"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.last_world_event = "南疆两宗争夺新生灵脉，东洲商路随之涨价。";
        snapshot.presentation = presentation({ title: "九州风云录", eyebrow: "九州大势", seal: "世", tone: "story", paragraphs: ["灵气潮汐渐近，各域势力都在重新衡量彼此。"], blocks: [{ type: "facts", mark: "势", title: "势力盛衰", items: [{ label: "青云宗", value: "72" }, { label: "血魔宗", value: "41" }, { label: "天机阁", value: "65" }, { label: "丹霞谷", value: "58" }] }, { type: "meter", mark: "潮", title: "灵气潮汐", value: 63, max: 100, summary: "潮汐正在加速，秘境和灵脉事件出现得更加频繁。" }, { type: "list", mark: "闻", title: "近期大事记", items: [{ text: "东洲灵脉复苏" }, { text: "南疆宗门交战" }, { text: "西漠商路重开" }, { text: "北原遭遇雪灾" }], preview: 3 }] });
        return snapshot;
      },
    },
    {
      label: "12 · 道途终章",
      description: "检查陨落或寿尽后的结局信息与重新开始入口。",
      checks: ["结局是否庄重而明确", "关键经历是否保留", "重新开始入口是否清楚"],
      build(source) {
        const snapshot = demoBase(source);
        snapshot.state.phase = "ended";
        snapshot.state.player.age = 103;
        snapshot.state.player.condition = "寿元耗尽";
        snapshot.presentation = presentation({ title: "百年道途，一朝归尘", eyebrow: "道途生变", seal: "终", tone: "danger", paragraphs: ["天玄历四百七十四年，你在青岳洞府中安然坐化。", "旧友为你立下无字碑，山风仍会经过曾经修行的石阶。"], blocks: [{ type: "facts", mark: "录", title: "此生留痕", items: [{ label: "享年", value: "103 岁" }, { label: "最高境界", value: "筑基·中期" }, { label: "道侣", value: "顾清玄" }, { label: "声望", value: "68" }] }, { type: "list", mark: "事", title: "一生大事", items: [{ text: "拜入青云宗，晋升内门弟子" }, { text: "通灵秘境取得上古传承" }, { text: "与顾清玄结为道侣" }], preview: 3 }] });
        snapshot.decision = { eyebrow: "轮回再启", title: "是否再问一世长生？", hint: "新游戏会重新创建角色。", exclusive: true, choices: [{ label: "再入轮回", action: "开始游戏", description: "结束此世，开启新的修仙人生。", tone: "primary" }] };
        return snapshot;
      },
    },
    {
      label: "13 · 洞天卷宗",
      description: "检查命名存档、存档列表和阅读设置弹窗。",
      checks: ["存档入口是否显眼", "存档摘要是否易识别", "阅读设置是否清楚"],
      dialog: "archive",
      build: demoBase,
    },
    {
      label: "14 · 游玩指引",
      description: "检查首次游玩三步指引与关闭入口。",
      checks: ["三步说明是否足够简短", "按钮选择和自由行动是否讲清", "关闭入口是否容易找到"],
      dialog: "guide",
      build: demoBase,
    },
  ];

  function closePreviewDialogs() {
    [byId("archiveDialog"), byId("guideDialog"), byId("detailDialog")].forEach((dialog) => {
      if (dialog.open) dialog.close();
      dialog.classList.remove("showcase-preview");
    });
  }

  function lockGameControls() {
    document.querySelectorAll(".layout button:not([data-showcase-readonly]), .action-card textarea, .top-status button:not(#openShowcase), dialog:not(#detailDialog) button, dialog:not(#detailDialog) input").forEach((control) => {
      control.dataset.showcaseLocked = "true";
      control.setAttribute("aria-disabled", "true");
    });
  }

  function unlockStaticControls() {
    document.querySelectorAll("[data-showcase-locked]").forEach((control) => {
      delete control.dataset.showcaseLocked;
      control.removeAttribute("aria-disabled");
    });
  }

  function updateController(scene) {
    byId("showcaseSelect").value = String(currentIndex);
    byId("showcaseIndex").textContent = `${String(currentIndex + 1).padStart(2, "0")} / ${scenes.length}`;
    byId("showcaseProgressBar").style.width = `${Math.round((currentIndex + 1) * 100 / scenes.length)}%`;
    byId("showcasePageTitle").textContent = scene.label.replace(/^\d+\s*·\s*/, "");
    byId("showcaseDescription").textContent = scene.description;
    byId("showcaseChecklist").replaceChildren(...scene.checks.map((check) => {
      const item = document.createElement("li");
      item.textContent = check;
      return item;
    }));
    byId("showcasePrevious").disabled = currentIndex === 0;
    byId("showcaseNext").textContent = currentIndex === scenes.length - 1 ? "完成巡览" : "下一页";
  }

  function showScene(index) {
    currentIndex = Math.max(0, Math.min(scenes.length - 1, index));
    const scene = scenes[currentIndex];
    closePreviewDialogs();
    ui.renderSnapshot(scene.build(liveSnapshot), { suppressNotices: true });
    document.body.classList.add("showcase-mode");
    lockGameControls();
    if (scene.dialog) {
      const dialog = byId(scene.dialog === "archive" ? "archiveDialog" : "guideDialog");
      dialog.classList.add("showcase-preview");
      dialog.show();
    }
    updateController(scene);
    if (scene.toast) ui.notify(scene.toast.message, scene.toast.tone);
    document.querySelector(".story-column")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function enterShowcase() {
    const latest = ui.getLatestSnapshot();
    if (!latest) return;
    liveSnapshot = clone(latest);
    byId("showcasePanel").hidden = false;
    byId("openShowcase").setAttribute("aria-pressed", "true");
    showScene(0);
  }

  function exitShowcase() {
    if (!liveSnapshot) return;
    closePreviewDialogs();
    document.body.classList.remove("showcase-mode");
    byId("showcasePanel").hidden = true;
    byId("openShowcase").setAttribute("aria-pressed", "false");
    ui.renderSnapshot(liveSnapshot, { suppressNotices: true });
    unlockStaticControls();
    liveSnapshot = null;
  }

  scenes.forEach((scene, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = scene.label;
    byId("showcaseSelect").append(option);
  });

  byId("openShowcase").addEventListener("click", () => {
    if (document.body.classList.contains("showcase-mode")) exitShowcase();
    else enterShowcase();
  });
  byId("exitShowcase").addEventListener("click", exitShowcase);
  byId("showcasePrevious").addEventListener("click", () => showScene(currentIndex - 1));
  byId("showcaseNext").addEventListener("click", () => {
    if (currentIndex === scenes.length - 1) exitShowcase();
    else showScene(currentIndex + 1);
  });
  byId("showcaseSelect").addEventListener("change", (event) => showScene(Number(event.target.value)));
  document.addEventListener("keydown", (event) => {
    if (!document.body.classList.contains("showcase-mode") || ["INPUT", "TEXTAREA", "SELECT"].includes(event.target.tagName)) return;
    if (event.key === "ArrowRight") showScene(currentIndex + 1);
    if (event.key === "ArrowLeft") showScene(currentIndex - 1);
    if (event.key === "Escape") exitShowcase();
  });
  document.addEventListener("click", (event) => {
    if (!document.body.classList.contains("showcase-mode")) return;
    const target = event.target.closest(".layout button, .action-card textarea, .top-status button:not(#openShowcase), dialog button, dialog input");
    if (!target) return;
    if (target.dataset.showcaseReadonly === "true" || target.closest("#detailDialog")) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    if (target.classList.contains("decision-choice") && !target.disabled) {
      document.querySelectorAll("#decisionChoices .decision-choice").forEach((choice) => {
        choice.classList.remove("is-selected");
        choice.setAttribute("aria-pressed", "false");
        const label = choice.querySelector(".decision-choice-action");
        if (label) label.textContent = choice.disabled ? "条件不足" : "选择此项";
      });
      target.classList.add("is-selected");
      target.setAttribute("aria-pressed", "true");
      const label = target.querySelector(".decision-choice-action");
      if (label) label.textContent = "已选择预览";
    }
  }, true);
  document.addEventListener("submit", (event) => {
    if (!document.body.classList.contains("showcase-mode")) return;
    event.preventDefault();
    event.stopImmediatePropagation();
  }, true);

  const readiness = window.setInterval(() => {
    if (!ui.getLatestSnapshot()) return;
    byId("openShowcase").disabled = false;
    window.clearInterval(readiness);
  }, 60);
})();
