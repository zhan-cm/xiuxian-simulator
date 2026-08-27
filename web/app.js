const $ = (id) => document.getElementById(id);

const phaseActions = {
  new: ["开始游戏"],
  character_creation_basic: ["确认默认创角"],
  character_creation_traits: [],
  playing: ["面板", "修炼", "闭关3月", "地图", "秘境", "坊市", "宗门", "情缘", "世情", "天下", "存档"],
  combat_ready: ["开战", "离开", "遁走"],
  combat: ["攻击", "防御", "施法 流火术", "蓄势", "绝技", "遁走"],
  combat_loot: ["拾取全部", "离开"],
  adventure_ready: ["确认进入", "离开"],
  adventure: ["谨慎探索", "强行探索", "退出秘境"],
  breakthrough_talent_choice: ["选择 1", "选择 2", "选择 3"],
  sect_defection_ready: ["确认叛宗", "取消"],
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

function render(snapshot) {
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

  const actions = phaseActions[state.phase] || ["面板", "帮助"];
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
  $("storyOutput").textContent = "天机流转，正在推演……";
  try {
    const payload = await requestJson("/api/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: trimmed }),
    });
    $("storyOutput").textContent = payload.output;
    $("actionInput").value = "";
    render(payload);
  } catch (error) {
    $("storyOutput").textContent = `推演受阻：${error.message}`;
  } finally {
    $("submitAction").disabled = false;
    $("actionInput").focus();
  }
}

$("actionForm").addEventListener("submit", (event) => {
  event.preventDefault();
  sendAction($("actionInput").value);
});

requestJson("/api/state")
  .then((snapshot) => render(snapshot))
  .catch((error) => { $("storyOutput").textContent = `无法读取游戏状态：${error.message}`; });
