const $ = (id) => document.getElementById(id);
let latestSnapshot = null;

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

function percent(value, max) {
  if (!max) return 0;
  return Math.max(0, Math.min(100, Math.round(value * 100 / max)));
}

function setBar(prefix, value, max) {
  $(`${prefix}Text`).textContent = `${value} / ${max}`;
  $(`${prefix}Bar`).style.width = `${percent(value, max)}%`;
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
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
  node.append(element("small", "", item.label || "信息"), element("strong", "", item.value || "—"));
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
    affinity.append(element("small", "", "好感"), track, element("strong", "", String(value)));
    row.append(affinity);
  }
  return row;
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

  if (type === "facts") {
    card.append(semanticHead(block.title, `${items.length} 项`, block.mark || "判"));
    const grid = element("div", "fact-grid");
    grid.append(...items.slice(0, 6).map(factItem));
    card.append(grid);
    if (items.length > 6) card.append(overflowDetails(`查看其余 ${items.length - 6} 项`, items.slice(6).map(factItem)));
    return card;
  }

  if (type === "people") {
    const preview = Math.max(1, block.preview || 2);
    card.append(semanticHead(block.title, `${items.length} 人`, block.mark || "人"));
    const list = element("div", "person-summaries");
    list.append(...items.slice(0, preview).map(personItem));
    card.append(list);
    if (items.length > preview) card.append(overflowDetails(`查看其余 ${items.length - preview} 位人物`, items.slice(preview).map(personItem)));
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
    list.append(...items.slice(0, preview).map((item) => element("li", "", item.text || "")));
    card.append(list);
  }
  if (items.length > preview) {
    card.append(overflowDetails(
      preview ? `查看其余 ${items.length - preview} 条` : `展开查看 ${items.length} 条`,
      items.slice(preview).map((item) => element("p", "semantic-detail-line", item.text || "")),
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
    button.setAttribute("aria-label", `选择：${choice.label}`);
    const seal = element("span", "decision-choice-seal", (choice.label || "选").slice(0, 1));
    const copy = element("span", "decision-choice-copy");
    copy.append(
      element("strong", "", choice.label),
      element("small", "", choice.description || "点击选择此项。"),
    );
    button.append(seal, copy, element("span", "decision-choice-action", "选择此项"));
    button.addEventListener("click", () => sendAction(choice.action));
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

function render(snapshot) {
  latestSnapshot = snapshot;
  const state = snapshot.state;
  const p = state.player;
  $("timeLabel").textContent = `天玄历 ${state.calendar_year} 年 · ${state.month} 月`;
  $("narratorLabel").textContent = snapshot.narrator || "本地叙事器";
  $("playerName").textContent = state.phase === "new" ? "尚未入世" : `${p.dao_name} · ${p.name}`;
  $("daoSeal").textContent = (p.dao_name || p.name || "道").slice(0, 1);
  $("playerMeta").textContent = `${p.gender} · ${p.age}/${p.lifespan}岁 · ${p.location}`;
  $("realmValue").textContent = p.realm;
  $("sectValue").textContent = p.sect === "散修" ? "散修" : `${p.sect}·${p.sect_rank}`;
  $("stonesValue").textContent = p.spirit_stones;
  $("turnBadge").textContent = `第 ${state.turn} 回合`;
  $("sceneTitle").textContent = state.phase === "ended" ? "此世已终" : (state.main_quest || "长生问道");
  setBar("health", p.health, p.health_max);
  setBar("spirit", p.spirit, p.spirit_max);
  setBar("cultivation", p.cultivation, p.cultivation_required);

  const resources = Object.entries(p.resources || {}).filter(([, count]) => count > 0);
  $("inventoryList").replaceChildren(...(resources.length
    ? resources.slice(0, 18).map(([name, count]) => {
        const tag = document.createElement("span"); tag.textContent = `${name} × ${count}`; return tag;
      })
    : [Object.assign(document.createElement("span"), { className: "empty", textContent: "空空如也" })]));

  const relations = Object.entries(state.npc_relations || {});
  const tension = Math.max(0, Math.min(100, state.relationship_tension || 0));
  $("tensionMeter").hidden = tension <= 0;
  $("tensionValue").textContent = `${tension}/100`;
  $("tensionBar").style.width = `${tension}%`;
  $("tensionHint").textContent = tension >= 60 ? "情劫将至" : (tension >= 30 ? "数段心意正在交汇" : "风波初起");
  $("relationList").replaceChildren(...(relations.length
    ? relations.slice(0, 8).map(([name, relation]) => {
        const item = document.createElement("div"); item.className = "relation-item";
        const line = document.createElement("div");
        const who = document.createElement("strong"); who.textContent = name;
        const affinity = document.createElement("span"); affinity.textContent = `好感 ${relation.affinity || 0}`;
        line.append(who, affinity);
        const path = document.createElement("small"); path.textContent = relation.path || "缘分未定";
        item.append(line, path); return item;
      })
    : [Object.assign(document.createElement("p"), { className: "empty", textContent: "尚未结识修士" })]));

  const history = (state.history || []).slice(-7).reverse();
  $("historyList").replaceChildren(...(history.length
    ? history.map((entry) => { const li = document.createElement("li"); li.textContent = entry; return li; })
    : [Object.assign(document.createElement("li"), { className: "empty", textContent: "等待第一段经历" })]));
  $("worldEvent").textContent = state.last_world_event || "灵气潮汐尚在暗中酝酿。";
  renderPresentation(snapshot.presentation);
  renderDecision(snapshot.decision);
  renderSaveLibrary(snapshot);

  const actions = snapshot.decision?.exclusive ? [] : [...(phaseActions[state.phase] || ["面板", "帮助"] )];
  if (state.phase === "playing" && tension >= 30 && !actions.includes("情劫")) actions.splice(8, 0, "情劫");
  const war = state.active_sect_war || {};
  if (state.phase === "playing" && [war.attacker, war.defender].includes(p.sect) && !war.player_acted && !actions.includes("护宗战")) {
    actions.splice(8, 0, "护宗战");
  }
  $("quickActions").replaceChildren(...actions.map((action) => {
    const button = document.createElement("button");
    button.type = "button"; button.textContent = action; button.addEventListener("click", () => sendAction(action));
    return button;
  }));
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
  $("submitAction").disabled = true;
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
    return payload;
  } catch (error) {
    renderError(error.message);
    renderDecision(latestSnapshot?.decision);
    return null;
  } finally {
    $("submitAction").disabled = false;
    $("actionInput").focus();
  }
}

$("actionForm").addEventListener("submit", (event) => {
  event.preventDefault();
  sendAction($("actionInput").value);
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

function openGuide() { $("guideDialog").showModal(); }
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

applyReadingPreferences();
if (readPreference("xiuxian-guide-seen", "false") !== "true") window.setTimeout(openGuide, 180);

requestJson("/api/state")
  .then((snapshot) => render(snapshot))
  .catch((error) => { renderError(`无法读取游戏状态：${error.message}`); });
