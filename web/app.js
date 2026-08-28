const $ = (id) => document.getElementById(id);
let latestSnapshot = null;
let previousSnapshot = null;
const seenContentKeys = new Set();

const phaseActions = {
  new: ["开始游戏"],
  character_creation_basic: ["确认默认创角"],
  character_creation_traits: [],
  playing: ["面板", "修炼", "闭关3月", "地图", "秘境", "坊市", "宗门", "情缘", "世情", "天下", "干预天下", "存档"],
  combat_ready: ["开战", "离开", "遁走"],
  combat: ["攻击", "防御", "施法 流火术", "蓄势", "绝技", "遁走"],
  combat_loot: ["拾取全部", "离开"],
  adventure_ready: ["确认进入", "离开"],
  adventure: ["谨慎探索", "强行探索", "退出秘境"],
  breakthrough_talent_choice: ["选择 1", "选择 2", "选择 3"],
  sect_defection_ready: ["确认叛宗", "取消"],
  heart_trial_choice: ["情劫 坦诚相告", "情劫 暂避锋芒", "情劫 一心问道"],
  ended: ["开始游戏"],
};

const actionMeta = {
  "修炼": { label: "吐纳修炼", icon: "cultivate" },
  "闭关3月": { label: "闭关三月", icon: "retreat" },
  "地图": { label: "查看地图", icon: "map" },
  "坊市": { label: "前往坊市", icon: "market" },
  "存档": { label: "保存进度", icon: "save" },
  "面板": { label: "角色面板", icon: "foundation" },
  "秘境": { label: "秘境", icon: "explore" },
  "宗门": { label: "宗门", icon: "world" },
  "情缘": { label: "人物情缘", icon: "people" },
  "世情": { label: "人物动态", icon: "history" },
  "天下": { label: "天下局势", icon: "world" },
  "干预天下": { label: "干预天下", icon: "world" },
  "情劫": { label: "面对情劫", icon: "people" },
  "护宗战": { label: "护宗战", icon: "foundation" },
};

const termHelp = [
  ["成功率", "成功率是本次判定通过的概率；仍可能因随机判定成功或失败。"],
  ["历练", "历练反映探索与实战积累，可影响部分成长与事件判断。"],
  ["宗门贡献", "宗门贡献用于晋升身份、兑换资源和参与宗门事务。"],
  ["贡献", "贡献用于宗门晋升、资源兑换与特定事务。"],
  ["声望", "声望反映你在修仙界的名望，会影响人物、宗门与事件判定。"],
  ["好感", "好感范围通常为 -100 至 120；提高后可解锁更深关系与邀约。"],
  ["五行", "五行存在生克关系；克制敌方属性时可提高伤害。"],
  ["威胁", "威胁综合敌方境界、气血与攻击能力，越高越危险。"],
  ["弱点", "使用对应五行或战术攻击弱点，通常能取得更高收益。"],
  ["境界", "境界决定基础实力、寿元、可进入区域与可学习内容。"],
  ["道心", "道心会影响突破、心魔与部分重大选择的判定。"],
  ["冷却", "突破失败后需要休养，冷却结束前不能再次尝试。"],
  ["灵石", "灵石是修仙界通用货币，用于购买丹药、法器与材料。"],
];

const itemGuide = {
  "聚气丹": { kind: "丹药", rarity: "凡品", effect: "辅助炼气期修炼，提高当前修为。", description: "以温和灵药炼制，适合日常吐纳后服用。" },
  "疗伤丹": { kind: "丹药", rarity: "良品", effect: "在战斗或受伤后恢复气血。", description: "药力偏烈，危急时可迅速稳住伤势。" },
  "筑基丹": { kind: "破境丹药", rarity: "上品", effect: "人道筑基所需的关键材料。", description: "凝聚炼气根基，能显著降低筑基时的失控风险。" },
  "灵药": { kind: "材料", rarity: "凡品", effect: "用于炼丹、洞府种植和部分任务。", description: "蕴含温和灵气的通用药材。" },
  "青锋剑": { kind: "法器", rarity: "黄阶", effect: "装备后提高普通攻击伤害，五行为金。", description: "青云一带常见的入门飞剑，锋锐而易于驾驭。" },
  "五行灵珠": { kind: "天材地宝", rarity: "极品", effect: "天道突破与高阶炼制的重要材料。", description: "五行灵机在珠中循环不息，极为罕见。" },
  "道韵": { kind: "悟道材料", rarity: "珍稀", effect: "用于天道突破及高阶悟道。", description: "天地规则留下的一缕痕迹，无法以凡俗价值衡量。" },
};

function helpFor(label) {
  const text = String(label || "");
  return termHelp.find(([term]) => text.includes(term))?.[1] || "";
}

function addTooltip(node, help) {
  if (!help) return node;
  node.classList.add("has-tooltip");
  if (!node.hasAttribute("tabindex")) node.tabIndex = 0;
  node.dataset.tooltip = help;
  node.title = help;
  return node;
}

function svgIcon(name) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  svg.classList.add("ui-icon");
  svg.setAttribute("aria-hidden", "true");
  use.setAttribute("href", `#icon-${name || "explore"}`);
  svg.append(use);
  return svg;
}

function percent(value, max) {
  if (!max) return 0;
  return Math.max(0, Math.min(100, Math.round(value * 100 / max)));
}

function setBar(prefix, value, max) {
  $(`${prefix}Text`).textContent = `${value} / ${max}`;
  const fill = $(`${prefix}Bar`);
  const track = fill.parentElement;
  fill.style.width = `${percent(value, max)}%`;
  track.dataset.kind = prefix;
  track.classList.toggle("is-empty", Number(value) <= 0 && Number(max) > 0);
  track.setAttribute("aria-label", `${prefix === "health" ? "气血" : (prefix === "spirit" ? "灵力" : "修为")} ${value} / ${max}`);
}

function calendarLabel(state) {
  const seasons = ["", "春一月", "春二月", "春三月", "夏四月", "夏五月", "夏六月", "秋七月", "秋八月", "秋九月", "冬十月", "冬十一月", "冬十二月"];
  return `天玄历 ${state.calendar_year} 年 · ${seasons[state.month] || `${state.month} 月`}`;
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function openDetail({ kind = "条目详情", title = "未知道途", subtitle = "", seal = "览", body = "暂无更多说明。", stats = [] }) {
  $("detailKind").textContent = kind;
  $("detailTitle").textContent = title;
  $("detailSubtitle").textContent = subtitle;
  $("detailSeal").textContent = seal;
  $("detailBody").textContent = body;
  $("detailStats").replaceChildren(...stats.filter((entry) => entry?.value !== undefined && entry?.value !== "").map((entry) => {
    const stat = element("span", "detail-stat");
    stat.append(element("small", "", entry.label), element("strong", "", String(entry.value)));
    if (entry.help || helpFor(entry.label)) addTooltip(stat, entry.help || helpFor(entry.label));
    return stat;
  }));
  const dialog = $("detailDialog");
  if (!dialog.open) dialog.showModal();
}

function itemDetail(name, count) {
  const guide = itemGuide[name] || { kind: "修仙资源", rarity: "未鉴定", effect: "可在对应事件、炼制或交易中使用。", description: "此物的具体用途会随道途进展逐步显现。" };
  openDetail({
    kind: "乾坤袋 · 物品详情",
    title: name,
    subtitle: guide.description,
    seal: String(name || "物").slice(0, 1),
    body: guide.effect,
    stats: [{ label: "持有", value: `${count} 件` }, { label: "类别", value: guide.kind }, { label: "品阶", value: guide.rarity }],
  });
}

function personDetail(person) {
  const profile = latestSnapshot?.npc_profiles?.[person.name] || {};
  const affinity = person.affinity ?? profile.affinity ?? "0";
  openDetail({
    kind: "人物牵绊 · 完整档案",
    title: person.name || "未知道友",
    subtitle: person.descriptor || person.identity || profile.identity || "身份未明",
    seal: String(person.name || "人").slice(0, 1),
    body: person.greeting || profile.greeting || "你们尚未留下足够深刻的交谈。",
    stats: [
      { label: "性别", value: person.gender || profile.gender || "未知" },
      { label: "年龄", value: person.age || (profile.age ? `${profile.age}岁` : "未知") },
      { label: "境界", value: person.realm || profile.realm || "未知" },
      { label: "关系", value: person.relation || profile.relation || "缘分未定" },
      { label: "好感", value: affinity },
      { label: "所在地", value: person.location || profile.location || "行踪不明" },
      { label: "偏爱", value: (person.likes || profile.likes || []).join("、") || "尚待了解" },
      { label: "避讳", value: (person.dislikes || profile.dislikes || []).join("、") || "尚待了解" },
    ],
  });
}

function makeDetailEntry(node, details) {
  node.classList.add("interactive-entry");
  node.tabIndex = 0;
  node.setAttribute("role", "button");
  node.dataset.showcaseReadonly = "true";
  const open = () => details.onOpen ? details.onOpen() : openDetail(details);
  node.addEventListener("click", open);
  node.addEventListener("keydown", (event) => {
    if (!["Enter", " "].includes(event.key)) return;
    event.preventDefault();
    open();
  });
  return node;
}

function showToast(message, tone = "success") {
  const toast = element("div", "game-toast", message);
  toast.dataset.tone = tone;
  $("toastRegion").append(toast);
  window.setTimeout(() => toast.classList.add("is-leaving"), 2800);
  window.setTimeout(() => toast.remove(), 3250);
}

function announceResult(payload) {
  const presentation = payload?.presentation || {};
  const changes = presentation.changes || [];
  const resourceChange = changes.find((change) => /灵石|灵药|丹|剑|材料|收获/.test(`${change.label || ""}${change.value || ""}`));
  const relationChange = changes.find((change) => /好感|关系|道侣/.test(`${change.label || ""}${change.value || ""}`));
  if (presentation.tone === "danger") showToast(`危机已结算 · ${presentation.title || "请查看当前状态"}`, "danger");
  else if (resourceChange) showToast(`获得与消耗已更新 · ${resourceChange.label} ${resourceChange.value}`, "treasure");
  else if (relationChange) showToast(`人物牵绊有新进展 · ${relationChange.label} ${relationChange.value}`, "relation");
  else showToast(`推演完成 · ${presentation.title || "道途已更新"}`, "success");
}

function semanticHead(title, meta = "", mark = "") {
  const head = element("header", "semantic-head");
  const identity = element("div", "semantic-identity");
  if (mark) identity.append(element("span", "module-mark", mark));
  identity.append(element("h4", "", title || "相关信息"));
  head.append(identity);
  if (meta) head.append(element("span", "", meta));
  return head;
}

function factItem(item) {
  const node = element("div", "fact-item");
  const labelText = item.label || "信息";
  const label = element("small", "fact-label");
  const iconName = labelText.includes("五行") ? "element" : (labelText.includes("威胁") ? "threat" : (labelText.includes("弱点") ? "weakness" : (labelText.includes("成功率") ? "chance" : "")));
  if (iconName) label.append(svgIcon(iconName));
  label.append(document.createTextNode(labelText));
  addTooltip(label, item.help || helpFor(labelText));
  node.append(label, element("strong", "", item.value || "—"));
  return node;
}

function personItem(person) {
  const row = element("article", "person-summary");
  const main = element("header", "person-main");
  const avatar = element("span", "person-avatar", (person.name || "人").slice(0, 1));
  const copy = element("span", "person-copy");
  copy.append(
    element("strong", "", person.name || "未知道友"),
    element("small", "", person.descriptor || person.identity || "身份未明"),
  );
  const bond = element("span", "person-bond");
  bond.append(element("small", "", person.relation || "缘分未定"));
  main.append(avatar, copy, bond);

  const tags = element("div", "person-tags");
  [person.gender, person.age, person.realm, person.identity, person.location ? `身在 ${person.location}` : ""]
    .filter(Boolean)
    .forEach((value) => tags.append(element("span", "", value)));

  row.append(main, tags);
  if (person.affinity !== "") {
    const value = Math.max(-100, Math.min(100, Number(person.affinity) || 0));
    const affinity = element("div", "person-affinity");
    const track = element("span", "affinity-track");
    const fill = element("i", "");
    fill.style.width = `${Math.max(0, value)}%`;
    track.append(fill);
    affinity.append(addTooltip(element("small", "", "好感"), helpFor("好感")), track, element("strong", "", String(value)));
    row.append(affinity);
  }
  return makeDetailEntry(row, {
    kind: "人物牵绊 · 完整档案",
    title: person.name || "未知道友",
    subtitle: "点击查看完整档案",
    seal: String(person.name || "人").slice(0, 1),
    body: "正在打开人物档案。",
    stats: [],
    onOpen: () => personDetail(person),
  });
}

function locationItem(location) {
  const card = element("article", "location-item");
  card.dataset.tone = location.tone || "normal";
  card.dataset.access = location.accessible === false ? "locked" : "open";
  const head = element("header", "location-head");
  const name = element("div", "location-name");
  name.append(element("strong", "", location.name || "未知之地"));
  if (location.visited) name.append(element("small", "location-visited", "已探访"));
  const danger = element("span", "danger-badge has-tooltip", `${location.danger_label || "未知"} · ${location.danger ?? "—"}`);
  danger.tabIndex = 0;
  danger.dataset.tooltip = location.danger_help || "危险度越高，越容易遭遇强敌与不利事件。";
  danger.title = danger.dataset.tooltip;
  danger.setAttribute("aria-label", `危险度 ${location.danger ?? "未知"}，${location.danger_label || "等级未知"}`);
  head.append(name, danger);
  const meta = element("div", "location-meta");
  meta.append(element("span", "", "准入"), element("strong", "", location.requirement_label || location.requirement || "境界未知"));
  const help = element("p", "location-help", location.help || "请量力而行。 ");
  const footer = element("footer", "location-footer");
  const action = element("button", "location-action has-tooltip");
  action.type = "button";
  action.disabled = location.accessible === false;
  action.dataset.tooltip = action.disabled ? (location.locked_reason || "当前境界不足，无法进入") : "点击后立即前往，并执行一次探索推演";
  action.title = action.dataset.tooltip;
  action.setAttribute("aria-label", action.disabled ? `无法探索 ${location.name}：${action.dataset.tooltip}` : `探索 ${location.name}，点击后立即执行`);
  action.append(svgIcon("explore"), element("span", "", action.disabled ? "境界不足" : "前往探索"));
  action.addEventListener("click", () => sendAction(`探索 ${location.name}`));
  footer.append(action);
  card.append(head, meta, help, footer);
  return card;
}

function overflowDetails(label, nodes) {
  const details = element("details", "semantic-more");
  details.append(element("summary", "", label));
  const body = element("div", "semantic-more-body");
  body.append(...nodes);
  details.append(body);
  return details;
}

function renderSemanticBlock(block, index) {
  const type = block.type || "list";
  const card = element("section", `semantic-block ${type}-block`);
  card.style.setProperty("--block-order", index);
  const items = block.items || [];
  const noticeKey = `${block.title || ""}:${items.map((item) => item.text || item.name || item.value || "").join("|")}`;
  if (/宗门.*任务|任务|委托/.test(block.title || "") && !seenContentKeys.has(noticeKey)) {
    card.classList.add("has-new-content");
    card.addEventListener("click", () => {
      seenContentKeys.add(noticeKey);
      card.classList.remove("has-new-content");
    }, { once: true });
  }

  if (type === "facts") {
    card.append(semanticHead(block.title, `${items.length} 项`, block.mark || "判"));
    const body = element("div", "semantic-data-region");
    if (items.length > 8) body.dataset.overflow = "true";
    const grid = element("div", "fact-grid");
    grid.append(...items.slice(0, 6).map(factItem));
    body.append(grid);
    if (items.length > 6) body.append(overflowDetails(`查看其余 ${items.length - 6} 项`, items.slice(6).map(factItem)));
    card.append(body);
    return card;
  }

  if (type === "people") {
    const preview = Math.max(1, block.preview || 2);
    card.append(semanticHead(block.title, `${items.length} 人`, block.mark || "人"));
    const body = element("div", "semantic-data-region");
    if (items.length > 4) body.dataset.overflow = "true";
    const list = element("div", "person-summaries");
    list.append(...items.slice(0, preview).map(personItem));
    body.append(list);
    if (items.length > preview) body.append(overflowDetails(`查看其余 ${items.length - preview} 位人物`, items.slice(preview).map(personItem)));
    card.append(body);
    return card;
  }

  if (type === "locations") {
    card.append(semanticHead(block.title, `${items.length} 处`, block.mark || "图"));
    const body = element("div", "semantic-data-region");
    if (items.length > 4) body.dataset.overflow = "true";
    const grid = element("div", "location-grid");
    grid.append(...items.map(locationItem));
    body.append(grid);
    if (block.legend) body.append(element("p", "location-legend", block.legend));
    card.append(body);
    return card;
  }

  if (type === "meter") {
    const max = Math.max(1, Number(block.max) || 100);
    const value = Math.max(0, Math.min(max, Number(block.value) || 0));
    const percentValue = Math.round(value * 100 / max);
    card.dataset.level = percentValue >= 70 ? "high" : (percentValue >= 40 ? "medium" : "low");
    card.append(semanticHead(block.title, `${value}/${max}`, block.mark || "势"));
    const meter = element("div", "module-meter");
    const track = element("span", "module-meter-track");
    const fill = element("i", "");
    fill.style.width = `${percentValue}%`;
    track.append(fill);
    meter.append(track, element("strong", "", `${percentValue}%`));
    card.append(meter);
    if (block.summary) card.append(element("p", "module-summary", block.summary));
    return card;
  }

  const preview = block.collapsed ? 0 : Math.max(1, block.preview || 3);
  card.append(semanticHead(block.title, `${items.length} 条`, block.mark || (block.title || "录").slice(0, 1)));
  if (preview) {
    const list = element("ul", "semantic-list");
    list.append(...items.slice(0, preview).map((item) => {
      const line = element("li", "", item.text || "");
      if (/坊市|货架|商铺|宗门|任务|委托|收获/.test(block.title || "")) {
        makeDetailEntry(line, {
          kind: `${block.title || "道途"} · 条目详情`,
          title: (item.text || "相关条目").split(/[｜·：:]/)[0],
          subtitle: block.title || "相关信息",
          seal: (block.mark || block.title || "览").slice(0, 1),
          body: item.text || "暂无更多说明。",
          stats: [],
        });
      }
      return line;
    }));
    card.append(list);
  }
  if (items.length > preview) {
    card.append(overflowDetails(
      preview ? `查看其余 ${items.length - preview} 条` : `展开查看 ${items.length} 条`,
      items.slice(preview).map((item) => {
        const line = element("p", "semantic-detail-line", item.text || "");
        if (/坊市|货架|商铺|宗门|任务|委托|收获/.test(block.title || "")) {
          makeDetailEntry(line, {
            kind: `${block.title || "道途"} · 条目详情`,
            title: (item.text || "相关条目").split(/[｜·：:]/)[0],
            subtitle: block.title || "相关信息",
            seal: (block.mark || block.title || "览").slice(0, 1),
            body: item.text || "暂无更多说明。",
            stats: [],
          });
        }
        return line;
      }),
    ));
  }
  return card;
}

function renderPresentation(presentation) {
  const view = presentation || {
    title: "天道推演",
    eyebrow: "云深不知处",
    seal: "道",
    tone: "story",
    paragraphs: ["等待下一次天道推演。"],
    changes: [],
    sections: [],
    details: "",
    has_details: false,
  };

  $("eventHero").dataset.tone = view.tone || "story";
  $("eventSeal").textContent = view.seal || "道";
  $("eventEyebrow").textContent = view.eyebrow || "天道推演";
  $("eventTitle").textContent = view.title || "天道推演";
  $("eventHero").classList.toggle("is-duplicate-title", (view.title || "").trim() === $("sceneTitle").textContent.trim());
  $("storyOutput").replaceChildren(...(view.paragraphs || []).map((text) => element("p", "", text)));

  $("changeRibbon").replaceChildren(...(view.changes || []).map((change) => {
    const card = element("article", "change-chip");
    card.dataset.tone = change.tone || "story";
    const seal = element("span", "change-seal", change.seal || "变");
    const copy = element("span", "change-copy");
    copy.append(element("small", "", change.label), element("strong", "", change.value));
    card.append(seal, copy);
    return card;
  }));

  const fallbackBlocks = (view.sections || []).map((section) => ({
    type: "list",
    mark: section.title.slice(0, 1),
    title: section.title,
    items: (section.body || "").split("\n").filter(Boolean).map((text) => ({ text })),
    preview: 3,
  }));
  $("eventSections").replaceChildren(...(view.blocks || fallbackBlocks).map(renderSemanticBlock));

  const details = $("eventDetails");
  details.hidden = !view.has_details;
  details.open = false;
  $("eventDetailsText").textContent = view.details || "";
}

function renderLoading() {
  renderPresentation({
    title: "天机流转",
    eyebrow: "正在推演此行",
    seal: "演",
    tone: "loading",
    paragraphs: ["灵台微动，因果正在汇成新的篇章……"],
    changes: [],
    sections: [],
    details: "",
    has_details: false,
  });
}

function renderError(message) {
  renderPresentation({
    title: "推演受阻",
    eyebrow: "天机暂晦",
    seal: "阻",
    tone: "danger",
    paragraphs: [message],
    changes: [],
    sections: [],
    details: "",
    has_details: false,
  });
}

function renderDecision(decision) {
  const panel = $("decisionPanel");
  const choices = decision?.choices || [];
  panel.hidden = choices.length === 0;
  if (!choices.length) {
    $("decisionChoices").replaceChildren();
    return;
  }
  $("decisionEyebrow").textContent = decision.eyebrow || "当前抉择";
  $("decisionTitle").textContent = decision.title || "请选择下一步";
  $("decisionHint").textContent = decision.hint || "点击任一按钮即可提交选择。";
  $("decisionChoices").replaceChildren(...choices.map((choice) => {
    const button = element("button", "decision-choice");
    button.type = "button";
    button.dataset.tone = choice.tone || "primary";
    button.disabled = choice.disabled === true;
    button.setAttribute("aria-pressed", "false");
    button.setAttribute("aria-label", button.disabled ? `${choice.label}，不可用：${choice.disabled_reason || "条件不足"}` : `选择：${choice.label}`);
    addTooltip(button, choice.tooltip || choice.disabled_reason || choice.description || "");
    const seal = element("span", "decision-choice-seal", (choice.label || "选").slice(0, 1));
    const copy = element("span", "decision-choice-copy");
    copy.append(
      element("strong", "", choice.label),
      element("small", "", choice.summary || choice.description || "点击选择此项。"),
    );
    const action = element("span", "decision-choice-action", button.disabled ? "条件不足" : "选择此项");
    button.append(seal, copy, action);
    button.addEventListener("click", () => {
      document.querySelectorAll("#decisionChoices .decision-choice").forEach((entry) => {
        entry.classList.remove("is-selected");
        entry.setAttribute("aria-pressed", "false");
      });
      button.classList.add("is-selected");
      button.setAttribute("aria-pressed", "true");
      action.textContent = "推演中";
      sendAction(choice.action);
    });
    return button;
  }));
}

function renderSaveLibrary(snapshot) {
  const saves = snapshot.save_summaries || [];
  $("saveCount").textContent = `${saves.length} 份`;
  $("saveLibrary").replaceChildren(...(saves.length ? saves.map((save) => {
    const entry = element("article", "save-entry");
    const seal = element("span", "save-entry-seal", (save.dao_name || save.player_name || "卷").slice(0, 1));
    const copy = element("span", "save-entry-copy");
    copy.append(
      element("strong", "", save.name),
      element("small", "", `${save.dao_name || save.player_name} · ${save.realm}`),
      element("small", "", `天玄历 ${save.calendar_year} 年 · ${save.month} 月 · 第 ${save.turn} 回合`),
    );
    const load = element("button", "load-save", "载入");
    load.type = "button";
    load.addEventListener("click", async () => {
      if (!load.classList.contains("confirming")) {
        load.classList.add("confirming");
        load.textContent = "确认载入";
        window.setTimeout(() => { load.classList.remove("confirming"); load.textContent = "载入"; }, 3500);
        return;
      }
      load.disabled = true;
      const payload = await sendAction(`读档 ${save.name}`);
      if (payload) $("archiveDialog").close();
    });
    entry.append(seal, copy, load);
    return entry;
  }) : [element("p", "empty", "尚无可用存档")]));
}

function readPreference(key, fallback) {
  try { return window.localStorage.getItem(key) || fallback; } catch (_) { return fallback; }
}

function writePreference(key, value) {
  try { window.localStorage.setItem(key, value); } catch (_) { /* 浏览器禁用存储时仍可临时使用。 */ }
}

function applyReadingPreferences() {
  const fontSize = readPreference("xiuxian-font-size", "normal");
  const reduceMotion = readPreference("xiuxian-reduce-motion", "false") === "true";
  document.documentElement.dataset.fontSize = fontSize;
  document.documentElement.classList.toggle("reduce-motion", reduceMotion);
  document.querySelectorAll("[data-font-size]").forEach((button) => {
    button.classList.toggle("active", button.dataset.fontSize === fontSize);
  });
  $("motionToggle").checked = reduceMotion;
}

function inventoryEmptyState() {
  const state = element("div", "inventory-empty");
  const slots = element("div", "inventory-slots");
  for (let index = 0; index < 4; index += 1) slots.append(element("i", ""));
  state.append(
    slots,
    element("strong", "inventory-capacity", "容量不限 · 格位按物品自动扩展"),
    element("p", "", "获得丹药、法器或材料后，将自动收纳在这里。"),
  );
  return state;
}

function compactRelationItem(name, relation) {
  const affinityValue = Number(relation.affinity) || 0;
  const item = element("article", "relation-item");
  const head = element("div", "relation-head");
  head.append(element("strong", "", name), element("span", "relation-path", relation.path || "缘分未定"));
  const meter = element("div", "relation-affinity");
  const track = element("span", "relation-affinity-track");
  const fill = element("i", "");
  fill.style.width = `${Math.max(0, Math.min(100, affinityValue))}%`;
  track.append(fill);
  meter.append(addTooltip(element("small", "", "好感"), helpFor("好感")), track, element("strong", "", String(affinityValue)));
  item.append(head, meter);
  return makeDetailEntry(item, {
    onOpen: () => personDetail({ name, relation: relation.path || "缘分未定", affinity: affinityValue }),
  });
}

function historyItem(entry) {
  const parts = String(entry).split("｜").map((part) => part.trim()).filter(Boolean);
  const item = element("li", "history-item");
  const turn = element("span", "history-turn", parts[0] || "往事");
  const copy = element("span", "history-copy");
  copy.append(
    element("strong", "", parts.slice(2).join("｜") || parts[1] || String(entry)),
    element("small", "", parts.length > 2 ? parts[1] : "道途留痕"),
  );
  item.append(turn, copy);
  item.title = String(entry);
  return item;
}

function actionAvailability(action) {
  const player = latestSnapshot?.state?.player;
  if (["修炼", "闭关3月"].includes(action) && player && Number(player.cultivation) >= Number(player.cultivation_required)) {
    return { enabled: false, reason: "修为已圆满，请先尝试突破" };
  }
  return { enabled: true, reason: "" };
}

function actionButton(action, className = "") {
  const meta = actionMeta[action] || { label: action, icon: "explore" };
  const availability = actionAvailability(action);
  const button = element("button", className);
  button.type = "button";
  button.dataset.action = action;
  button.disabled = !availability.enabled;
  button.title = availability.enabled ? `${meta.label}：点击后立即执行` : availability.reason;
  button.setAttribute("aria-label", availability.enabled ? `${meta.label}，点击后立即执行` : `${meta.label}，不可用：${availability.reason}`);
  button.append(svgIcon(meta.icon), element("span", "", meta.label));
  button.addEventListener("click", () => sendAction(action));
  return button;
}

function actionGroup(label, actions) {
  const group = element("div", "action-group");
  group.append(element("small", "", label));
  const buttons = element("div", "action-group-buttons");
  buttons.append(...actions.map((action) => actionButton(action)));
  group.append(buttons);
  return group;
}

function render(snapshot, options = {}) {
  previousSnapshot = latestSnapshot;
  latestSnapshot = snapshot;
  const state = snapshot.state;
  const p = state.player;
  $("timeLabel").textContent = calendarLabel(state);
  $("playerName").textContent = state.phase === "new" ? "尚未入世" : `${p.dao_name} · ${p.name}`;
  $("daoSeal").textContent = (p.dao_name || p.name || "道").slice(0, 1);
  $("playerMeta").textContent = `${p.gender} · ${p.age}岁（寿元 ${p.lifespan}） · ${p.location}`;
  $("realmValue").textContent = p.realm;
  $("sectValue").textContent = p.sect === "散修" ? "散修" : `${p.sect}·${p.sect_rank}`;
  $("stonesValue").textContent = p.spirit_stones;
  $("turnBadgeText").textContent = `第 ${state.turn} 回合｜${calendarLabel(state)}`;
  $("sceneTitle").textContent = state.phase === "ended" ? "此世已终" : (state.main_quest || "长生问道");
  setBar("health", p.health, p.health_max);
  setBar("spirit", p.spirit, p.spirit_max);
  setBar("cultivation", p.cultivation, p.cultivation_required);

  const resources = Object.entries(p.resources || {}).filter(([, count]) => count > 0);
  $("inventoryList").replaceChildren(...(resources.length
    ? resources.slice(0, 18).map(([name, count]) => {
        const tag = element("button", "inventory-item", `${name} × ${count}`);
        tag.type = "button";
        tag.dataset.showcaseReadonly = "true";
        tag.setAttribute("aria-label", `查看 ${name} 详情，当前 ${count} 件`);
        tag.addEventListener("click", () => itemDetail(name, count));
        return tag;
      })
    : [inventoryEmptyState()]));

  const relations = Object.entries(state.npc_relations || {});
  const isKnownRelation = ([, relation]) => (Number(relation.affinity) || 0) !== 0 || !["", "缘分未定", "陌生"].includes(relation.path || "");
  const knownRelations = relations.filter(isKnownRelation).sort((left, right) => (Number(right[1].affinity) || 0) - (Number(left[1].affinity) || 0));
  const unknownRelations = relations.filter((entry) => !isKnownRelation(entry));
  const tension = Math.max(0, Math.min(100, state.relationship_tension || 0));
  $("tensionMeter").hidden = tension <= 0;
  $("tensionValue").textContent = `${tension}/100`;
  $("tensionBar").style.width = `${tension}%`;
  $("tensionHint").textContent = tension >= 60 ? "情劫将至" : (tension >= 30 ? "数段心意正在交汇" : "风波初起");
  $("relationList").replaceChildren(...(knownRelations.length
    ? knownRelations.slice(0, 8).map(([name, relation]) => compactRelationItem(name, relation))
    : [element("p", "empty relation-empty", unknownRelations.length ? "尚未结下牵绊，可从下方人物开始结识。" : "尚未遇见可结识的修士。")]
  ));
  $("unknownRelations").hidden = unknownRelations.length === 0;
  $("unknownRelations").open = false;
  $("unknownRelationCount").textContent = `${unknownRelations.length} 位`;
  $("unknownRelationList").replaceChildren(...unknownRelations.map(([name]) => element("span", "", name)));
  const previousRelations = Object.entries(previousSnapshot?.state?.npc_relations || {}).filter(isKnownRelation);
  $("relationNotice").hidden = options.suppressNotices || !previousSnapshot || knownRelations.length <= previousRelations.length;

  const history = (state.history || []).slice(-12).reverse();
  $("historyList").replaceChildren(...(history.length
    ? history.slice(0, 4).map(historyItem)
    : [element("li", "empty", "等待第一段经历")]));
  const olderHistory = history.slice(4);
  $("historyMore").hidden = olderHistory.length === 0;
  $("historyMore").open = false;
  $("historyMoreLabel").textContent = `查看更早 ${olderHistory.length} 条经历`;
  $("historyMoreList").replaceChildren(...olderHistory.map(historyItem));
  const worldEvent = state.last_world_event || "灵气潮汐尚在暗中酝酿。";
  $("worldEvent").textContent = worldEvent;
  const previousWorldEvent = previousSnapshot?.state?.last_world_event || "灵气潮汐尚在暗中酝酿。";
  $("worldNotice").hidden = options.suppressNotices || !previousSnapshot || worldEvent === previousWorldEvent;
  renderPresentation(snapshot.presentation);
  renderDecision(snapshot.decision);
  renderSaveLibrary(snapshot);

  const actions = snapshot.decision?.exclusive ? [] : [...(phaseActions[state.phase] || ["面板", "帮助"] )];
  if (state.phase === "playing" && tension >= 30 && !actions.includes("情劫")) actions.splice(8, 0, "情劫");
  const war = state.active_sect_war || {};
  if (state.phase === "playing" && [war.attacker, war.defender].includes(p.sect) && !war.player_acted && !actions.includes("护宗战")) {
    actions.splice(8, 0, "护宗战");
  }
  const primaryNames = state.phase === "playing" ? new Set(["修炼", "闭关3月", "地图", "坊市", "存档"]) : new Set(actions);
  const primaryActions = actions.filter((action) => primaryNames.has(action));
  const secondaryActions = actions.filter((action) => !primaryNames.has(action));
  if (state.phase === "playing") {
    const groups = [
      actionGroup("修行", primaryActions.filter((action) => ["修炼", "闭关3月"].includes(action))),
      actionGroup("出行", primaryActions.filter((action) => ["地图", "坊市"].includes(action))),
      actionGroup("记录", primaryActions.filter((action) => action === "存档")),
    ].filter((group) => group.querySelector("button"));
    $("quickActions").replaceChildren(...groups);
  } else {
    $("quickActions").replaceChildren(...primaryActions.map((action) => actionButton(action)));
  }
  $("quickMore").replaceChildren(...secondaryActions.map((action) => actionButton(action)));
  $("moreActionPanel").hidden = secondaryActions.length === 0;
  $("moreActionPanel").open = false;
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "天道推演失败");
  return payload;
}

async function sendAction(action) {
  const trimmed = action.trim();
  if (!trimmed) return;
  document.body.classList.add("is-resolving");
  document.querySelectorAll("#quickActions button, #quickMore button, .action-suggestions button, #submitAction").forEach((button) => {
    button.disabled = true;
    if (button.closest("#quickActions, #quickMore")) button.classList.add("is-pending");
  });
  document.querySelectorAll("#decisionChoices button").forEach((button) => { button.disabled = true; });
  renderLoading();
  try {
    const payload = await requestJson("/api/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: trimmed }),
    });
    $("actionInput").value = "";
    render(payload);
    announceResult(payload);
    return payload;
  } catch (error) {
    renderError(error.message);
    renderDecision(latestSnapshot?.decision);
    showToast(`推演受阻 · ${error.message}`, "danger");
    return null;
  } finally {
    document.body.classList.remove("is-resolving");
    $("submitAction").disabled = false;
    document.querySelectorAll("#quickActions button, #quickMore button").forEach((button) => {
      const availability = actionAvailability(button.dataset.action || "");
      button.disabled = !availability.enabled;
      button.classList.remove("is-pending");
    });
    document.querySelectorAll(".action-suggestions button").forEach((button) => { button.disabled = false; });
    $("actionInput").focus();
  }
}

$("actionForm").addEventListener("submit", (event) => {
  event.preventDefault();
  sendAction($("actionInput").value);
});
document.querySelectorAll("[data-suggestion]").forEach((button) => {
  button.prepend(svgIcon(button.dataset.icon));
  button.addEventListener("click", () => {
    $("actionInput").value = button.dataset.suggestion || "";
    $("actionInput").focus();
  });
});

$("openArchive").addEventListener("click", () => {
  if (latestSnapshot) renderSaveLibrary(latestSnapshot);
  $("archiveDialog").showModal();
});
$("closeArchive").addEventListener("click", () => $("archiveDialog").close());
$("archiveDialog").addEventListener("click", (event) => {
  if (event.target === $("archiveDialog")) $("archiveDialog").close();
});
$("namedSaveForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("saveNameInput");
  const name = input.value.trim();
  if (!name) { input.setCustomValidity("请先填写存档名称"); input.reportValidity(); return; }
  input.setCustomValidity("");
  const payload = await sendAction(`存档 ${name}`);
  if (payload) { input.value = ""; renderSaveLibrary(payload); }
});
$("saveNameInput").addEventListener("input", () => $("saveNameInput").setCustomValidity(""));
document.querySelectorAll("[data-font-size]").forEach((button) => {
  button.addEventListener("click", () => { writePreference("xiuxian-font-size", button.dataset.fontSize); applyReadingPreferences(); });
});
$("motionToggle").addEventListener("change", (event) => {
  writePreference("xiuxian-reduce-motion", String(event.target.checked));
  applyReadingPreferences();
});

function openGuide() {
  if (document.body.classList.contains("showcase-mode")) return;
  $("guideDialog").showModal();
}
function closeGuide(markSeen = false) {
  if (markSeen) writePreference("xiuxian-guide-seen", "true");
  $("guideDialog").close();
}
$("openGuide").addEventListener("click", openGuide);
$("closeGuide").addEventListener("click", () => closeGuide(false));
$("finishGuide").addEventListener("click", () => closeGuide(true));
$("guideDialog").addEventListener("click", (event) => {
  if (event.target === $("guideDialog")) closeGuide(false);
});
$("closeDetail").addEventListener("click", () => $("detailDialog").close());
$("detailDialog").addEventListener("click", (event) => {
  if (event.target === $("detailDialog")) $("detailDialog").close();
});
$("relationNotice").closest("details").addEventListener("toggle", (event) => {
  if (event.currentTarget.open) $("relationNotice").hidden = true;
});
$("worldNotice").closest("section").addEventListener("click", () => { $("worldNotice").hidden = true; });

applyReadingPreferences();
if (readPreference("xiuxian-guide-seen", "false") !== "true") window.setTimeout(openGuide, 180);

window.xiuxianUi = {
  renderSnapshot: render,
  getLatestSnapshot: () => latestSnapshot,
  openGuide,
  notify: showToast,
};

requestJson("/api/state")
  .then((snapshot) => render(snapshot))
  .catch((error) => { renderError(`无法读取游戏状态：${error.message}`); });
