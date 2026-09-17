from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from .progression import ProgressionEngine
from .state import GameState


@dataclass(frozen=True, slots=True)
class TombTheme:
    id: str
    name: str
    description: str
    recommended_realm: str
    min_realm_index: int
    boss_name: str
    boss_power: int
    boss_health: int
    guardian_types: list[str]
    trap_types: list[str]
    special_drop: str


TOMB_THEMES: dict[str, TombTheme] = {
    "sword_crypt": TombTheme(
        id="sword_crypt",
        name="太古纯阳剑冢",
        description="传闻上古纯阳剑仙羽化之所，万柄残剑插满石壁，庚金剑罡森然流转。",
        recommended_realm="筑基期",
        min_realm_index=1,
        boss_name="纯阳剑仙不灭剑骨",
        boss_power=75,
        boss_health=450,
        guardian_types=["守陵剑傀", "庚金石兽", "断剑残魂"],
        trap_types=["万剑归宗阵", "庚金破体雷", "地煞剑气壑"],
        special_drop="古剑残片",
    ),
    "alchemy_crypt": TombTheme(
        id="alchemy_crypt",
        name="太虚丹尊玄陵",
        description="远古药王宗丹尊埋骨之地，地火九幽长明，鼎炉灵药经万载岁月已通化成灵。",
        recommended_realm="筑基·中期",
        min_realm_index=1,
        boss_name="九天玄火丹尊法相",
        boss_power=88,
        boss_health=520,
        guardian_types=["地火守炉傀", "药王毒藤灵", "吞炎古蟒"],
        trap_types=["九幽迷魂瘴", "地火三昧喷涌", "逆转阴阳五行锁"],
        special_drop="结丹灵药",
    ),
    "ghost_crypt": TombTheme(
        id="ghost_crypt",
        name="九幽冥帝古宫",
        description="万劫不入的九幽冥殿沉于地底千丈，黄泉阴风呼啸，沉睡着远古鬼帝法身。",
        recommended_realm="金丹期",
        min_realm_index=2,
        boss_name="九幽冥帝残魄分身",
        boss_power=115,
        boss_health=680,
        guardian_types=["幽冥铁骑尸王", "黄泉引魂鸦", "万魂血煞怨灵"],
        trap_types=["蚀骨销魂阴风", "幽魂问心阵", "黄泉绝生锁链"],
        special_drop="道韵",
    ),
}


class AncientTombEngine:
    GRID_WIDTH = 5
    GRID_HEIGHT = 5

    @classmethod
    def get_available_themes(cls, state: GameState) -> list[dict[str, Any]]:
        themes = []
        for theme in TOMB_THEMES.values():
            unlocked = state.player.realm_index >= theme.min_realm_index
            themes.append({
                "id": theme.id,
                "name": theme.name,
                "description": theme.description,
                "recommended_realm": theme.recommended_realm,
                "unlocked": unlocked,
                "special_drop": theme.special_drop,
            })
        return themes

    @classmethod
    def generate_floor(cls, theme: TombTheme, depth: int, seed: int) -> list[dict[str, Any]]:
        rng = random.Random(seed)
        grid: list[dict[str, Any]] = []

        # 25 tiles
        coords = [(x, y) for y in range(cls.GRID_HEIGHT) for x in range(cls.GRID_WIDTH)]
        # Entrance at (0, 0)
        coords.remove((0, 0))
        # Boss / Stairs at (4, 4)
        coords.remove((4, 4))

        rng.shuffle(coords)

        # Distribute types:
        # 5 treasures, 5 traps, 6 monsters, 3 altars, 4 corridors
        type_distribution = (
            ["treasure"] * 5
            + ["trap"] * 5
            + ["monster"] * 6
            + ["altar"] * 3
            + ["corridor"] * 4
        )

        tile_map: dict[tuple[int, int], dict[str, Any]] = {}

        # Entrance
        tile_map[(0, 0)] = {
            "x": 0,
            "y": 0,
            "type": "entrance",
            "name": "古墓甬道入口",
            "description": "古墓入口石门，微弱的灵光在此维系，可由此安全撤出古墓。",
            "revealed": True,
            "cleared": True,
            "reward_stones": 0,
            "reward_items": {},
        }

        # Boss at (4, 4)
        is_final_boss = depth >= 3
        boss_title = theme.boss_name if is_final_boss else f"第{depth}层守陵统领·{theme.boss_name.split('·')[-1]}"
        tile_map[(4, 4)] = {
            "x": 4,
            "y": 4,
            "type": "boss",
            "name": boss_title,
            "description": "主墓大殿中央的重关之门，恐怖的威压从棺木中涌出，唯有击破方能深入！",
            "revealed": False,
            "cleared": False,
            "enemy_power": theme.boss_power + (depth - 1) * 15,
            "enemy_health": theme.boss_health + (depth - 1) * 80,
            "reward_stones": 200 * depth,
            "reward_items": {theme.special_drop: 1, "天材地宝": depth},
        }

        # Place regular tiles
        for (x, y), tile_type in zip(coords, type_distribution):
            tile_data: dict[str, Any] = {
                "x": x,
                "y": y,
                "type": tile_type,
                "revealed": False,
                "cleared": False,
                "reward_stones": 0,
                "reward_items": {},
            }

            if tile_type == "treasure":
                t_names = ["太古金丝楠玉匣", "青铜古修士遗龛", "大能藏经石壁", "古仙储灵玉葫"]
                tile_data["name"] = rng.choice(t_names)
                tile_data["description"] = "沉睡万古的封印宝匣，其上铭刻着太古禁制，隐隐散发灵光。"
                tile_data["reward_stones"] = rng.randint(40, 100) * depth
                if rng.random() > 0.4:
                    tile_data["reward_items"] = {rng.choice(["聚气丹", "灵铁", "符箓材料", "妖兽材料"]): rng.randint(1, 2)}

            elif tile_type == "trap":
                trap_name = rng.choice(theme.trap_types)
                tile_data["name"] = trap_name
                tile_data["description"] = f"古墓中的杀伐古阵【{trap_name}】，地火剑气与重力玄磁环绕，需以神识推演阵眼方能破除。"
                tile_data["trap_dc"] = 12 + depth * 3
                tile_data["reward_stones"] = 30 * depth

            elif tile_type == "monster":
                monster_name = rng.choice(theme.guardian_types)
                tile_data["name"] = monster_name
                tile_data["description"] = f"驻守此地的死寂古物【{monster_name}】，双目闪烁幽火，扼守必经之路！"
                tile_data["enemy_power"] = 35 + depth * 15
                tile_data["enemy_health"] = 160 + depth * 60
                tile_data["reward_stones"] = rng.randint(30, 70) * depth
                tile_data["reward_items"] = {"妖兽材料": 1}

            elif tile_type == "altar":
                tile_data["name"] = "太古清宁灵池"
                tile_data["description"] = "由地脉灵乳汇聚的古泉，蕴含精纯灵气，可拂去身心疲惫并驱散墓煞。"
                tile_data["cleared"] = False

            else:  # corridor
                tile_data["name"] = "幽暗石廊"
                tile_data["description"] = "青石板铺就的墓道，两壁雕刻着太古仙魔征战的斑驳壁画。"
                tile_data["cleared"] = True
                if rng.random() > 0.6:
                    tile_data["reward_stones"] = rng.randint(10, 30)

            tile_map[(x, y)] = tile_data

        # Build list sorted by y, then x
        for y in range(cls.GRID_HEIGHT):
            for x in range(cls.GRID_WIDTH):
                grid.append(tile_map[(x, y)])

        return grid

    @classmethod
    def reveal_neighbors(cls, tomb: dict[str, Any], cx: int, cy: int) -> None:
        """Reveal current tile and all orthogonal neighbors in the grid."""
        grid = tomb["grid"]
        for tile in grid:
            tx, ty = tile["x"], tile["y"]
            if abs(tx - cx) + abs(ty - cy) <= 1:
                tile["revealed"] = True

    @classmethod
    def enter_tomb(cls, state: GameState, theme_id: str = "sword_crypt") -> dict[str, Any]:
        """Enter or start an ancient tomb dungeon exploration."""
        if state.active_tomb:
            return {
                "tomb": state.active_tomb,
                "msg": f"你尚在【{state.active_tomb['name']}】第 {state.active_tomb['depth']} 层探险中，可继续行动。",
            }

        theme = TOMB_THEMES.get(theme_id, TOMB_THEMES["sword_crypt"])
        if state.player.realm_index < theme.min_realm_index:
            raise ValueError(f"【境界不足】{theme.name}极度凶险，需至少达{theme.recommended_realm}方可踏足。")

        seed = state.turn * 1000 + state.calendar_year * 10 + 1
        grid = cls.generate_floor(theme, depth=1, seed=seed)

        tomb_data: dict[str, Any] = {
            "id": theme.id,
            "name": theme.name,
            "depth": 1,
            "max_depth": 3,
            "player_x": 0,
            "player_y": 0,
            "miasma": 0,
            "loot_items": {},
            "loot_stones": 0,
            "completed": False,
            "grid": grid,
            "log": [f"点燃引魂古灯，踏入【{theme.name}】第一层。地底幽暗森冷，需步步为营。"],
        }

        # Initial reveal around start (0, 0)
        cls.reveal_neighbors(tomb_data, 0, 0)

        state.active_tomb = tomb_data
        event = f"踏入太古大能秘境【{theme.name}】展开探险！"
        state.remember(event)

        return {
            "tomb": tomb_data,
            "msg": f"【太古古墓开启】踏入【{theme.name}】第一层。输入【古墓移动 上/下/左/右】探索石室迷雾！",
        }

    @classmethod
    def move(cls, state: GameState, direction: str) -> dict[str, Any]:
        """Move player in grid (上/下/左/右)."""
        tomb = state.active_tomb
        if not tomb:
            raise ValueError("当前尚未进入任何古墓秘境。可输入【古墓探险】选择大能古冢。")

        dir_map = {
            "上": (0, -1),
            "下": (0, 1),
            "左": (-1, 0),
            "右": (1, 0),
            "w": (0, -1),
            "s": (0, 1),
            "a": (-1, 0),
            "d": (1, 0),
        }
        direction = direction.strip().lower()
        delta = dir_map.get(direction)
        if not delta:
            raise ValueError("移动方向无效。可选：上、下、左、右。")

        nx = tomb["player_x"] + delta[0]
        ny = tomb["player_y"] + delta[1]

        if not (0 <= nx < cls.GRID_WIDTH and 0 <= ny < cls.GRID_HEIGHT):
            raise ValueError("石壁森严，前方已是古墓断崖绝壁，无法通行。")

        tomb["player_x"] = nx
        tomb["player_y"] = ny

        # Increment miasma slightly
        tomb["miasma"] = min(100, tomb.get("miasma", 0) + 3)

        # Reveal adjacent tiles
        cls.reveal_neighbors(tomb, nx, ny)

        # Locate current tile
        cur_tile = next((t for t in tomb["grid"] if t["x"] == nx and t["y"] == ny), None)
        tile_event = f"移动至石室 ({nx}, {ny})：【{cur_tile['name']}】。"

        # If corridor has small stones, auto collect
        if cur_tile and cur_tile["type"] == "corridor" and cur_tile.get("reward_stones", 0) > 0:
            found = cur_tile.pop("reward_stones")
            tomb["loot_stones"] += found
            tile_event += f" 在散落碎石中拾得灵石 +{found}！"

        tomb["log"].append(tile_event)
        tomb["log"] = tomb["log"][-20:]

        return {
            "tomb": tomb,
            "tile": cur_tile,
            "msg": tile_event,
        }

    @classmethod
    def interact(cls, state: GameState, action: str = "") -> dict[str, Any]:
        """Interact with current tile (开箱 / 破阵 / 斩杀 / 调息 / 进下层 / 撤离)."""
        tomb = state.active_tomb
        if not tomb:
            raise ValueError("当前不在古墓探险中。")

        cx, cy = tomb["player_x"], tomb["player_y"]
        cur_tile = next((t for t in tomb["grid"] if t["x"] == cx and t["y"] == cy), None)
        if not cur_tile:
            raise ValueError("当前位置异常。")

        action = action.strip()

        # Handle retreat
        if action in {"撤离", "离开", "返航"}:
            return cls.retreat(state)

        # Handle descend to next floor
        if action in {"进入下层", "下层", "深入"}:
            if cur_tile["type"] != "boss" or not cur_tile["cleared"]:
                raise ValueError("唯有诛灭本层主墓大能古灵，方可开启进入下层的虚空古阵。")
            return cls.descend(state)

        if cur_tile["cleared"]:
            return {
                "tomb": tomb,
                "msg": f"此石室【{cur_tile['name']}】已探明，灵蕴尽数收纳。",
            }

        tile_type = cur_tile["type"]

        # 1. Treasure
        if tile_type == "treasure":
            stones = cur_tile.get("reward_stones", 0)
            items = cur_tile.get("reward_items", {})
            tomb["loot_stones"] += stones
            for item, count in items.items():
                tomb["loot_items"][item] = tomb["loot_items"].get(item, 0) + count

            cur_tile["cleared"] = True
            loot_str = []
            if stones:
                loot_str.append(f"灵石 +{stones}")
            for k, v in items.items():
                loot_str.append(f"【{k}】×{v}")

            msg = f"开启【{cur_tile['name']}】！收获宝藏：" + "、".join(loot_str)
            tomb["log"].append(msg)
            return {"tomb": tomb, "msg": msg}

        # 2. Trap
        elif tile_type == "trap":
            # Check player comprehension & spirit_sense
            stat = state.player.comprehension + state.player.spirit_sense
            roll = ProgressionEngine.deterministic_roll(state, f"tomb-trap:{tomb['depth']}:{cx}:{cy}")
            dc = cur_tile.get("trap_dc", 20)
            if roll + stat // 3 >= dc:
                # Success
                cur_tile["cleared"] = True
                stones = cur_tile.get("reward_stones", 30)
                tomb["loot_stones"] += stones
                state.player.dao_insight += 2
                msg = f"神识通透识破【{cur_tile['name']}】阵眼！机关化解，感悟 +2，拾获阵枢灵石 +{stones}。"
            else:
                # Fail: take damage and increase miasma
                dmg = 20 + tomb["depth"] * 10
                state.player.health = max(1, state.player.health - dmg)
                tomb["miasma"] = min(100, tomb["miasma"] + 15)
                cur_tile["cleared"] = True
                msg = f"触动机关反噬！受到毒火剑气创伤气血 -{dmg}，墓煞侵蚀 +15 点！"

            tomb["log"].append(msg)
            return {"tomb": tomb, "msg": msg}

        # 3. Altar
        elif tile_type == "altar":
            heal = 80 + tomb["depth"] * 30
            state.player.health = min(state.player.health_max, state.player.health + heal)
            state.player.spirit = state.player.spirit_max
            tomb["miasma"] = max(0, tomb["miasma"] - 35)
            cur_tile["cleared"] = True
            msg = f"在【{cur_tile['name']}】吐纳调息：气血回复 +{heal}，灵力回满，驱散墓煞 -35 点！"
            tomb["log"].append(msg)
            return {"tomb": tomb, "msg": msg}

        # 4. Monster & Boss
        elif tile_type in {"monster", "boss"}:
            enemy_pwr = int(cur_tile.get("enemy_power", 50))
            enemy_hp = int(cur_tile.get("enemy_health", 200))

            player_pwr = 20 + state.player.realm_index * 25 + state.player.stage_index * 6 + state.player.aptitude

            # Roll battle outcome
            roll = ProgressionEngine.deterministic_roll(state, f"tomb-battle:{tomb['depth']}:{cx}:{cy}")
            win = (player_pwr + roll // 2) >= enemy_pwr

            if win:
                cur_tile["cleared"] = True
                stones = cur_tile.get("reward_stones", 50)
                items = cur_tile.get("reward_items", {})
                tomb["loot_stones"] += stones
                for item, count in items.items():
                    tomb["loot_items"][item] = tomb["loot_items"].get(item, 0) + count

                loot_str = [f"灵石 +{stones}"]
                for k, v in items.items():
                    loot_str.append(f"【{k}】×{v}")

                is_boss = tile_type == "boss"
                if is_boss:
                    if tomb["depth"] >= tomb["max_depth"]:
                        tomb["completed"] = True
                        msg = f"天威浩荡！斩灭主墓终极道主【{cur_tile['name']}】！古墓彻底勘破！获胜战利品：" + "、".join(loot_str)
                    else:
                        msg = f"斩灭守陵统领【{cur_tile['name']}】！开启通往下层的传送虚空阵！战利品：" + "、".join(loot_str)
                else:
                    msg = f"施展神通斩灭【{cur_tile['name']}】！战利品：" + "、".join(loot_str)

            else:
                dmg = 35 + tomb["depth"] * 15
                state.player.health = max(1, state.player.health - dmg)
                tomb["miasma"] = min(100, tomb["miasma"] + 10)
                msg = f"与【{cur_tile['name']}】交锋受挫！受创气血 -{dmg}，阴煞缠身。"

            tomb["log"].append(msg)
            return {"tomb": tomb, "msg": msg}

        return {"tomb": tomb, "msg": f"探索了石室【{cur_tile['name']}】。"}

    @classmethod
    def descend(cls, state: GameState) -> dict[str, Any]:
        """Descend to next deeper floor of the tomb."""
        tomb = state.active_tomb
        if not tomb:
            raise ValueError("当前不在古墓中。")

        if tomb["depth"] >= tomb["max_depth"]:
            raise ValueError("当前已至古墓最深层。")

        new_depth = tomb["depth"] + 1
        theme = TOMB_THEMES.get(tomb["id"], TOMB_THEMES["sword_crypt"])
        seed = state.turn * 1000 + new_depth * 77 + 9

        grid = cls.generate_floor(theme, depth=new_depth, seed=seed)
        tomb["depth"] = new_depth
        tomb["player_x"] = 0
        tomb["player_y"] = 0
        tomb["grid"] = grid
        cls.reveal_neighbors(tomb, 0, 0)

        msg = f"踏入太古古墓第 {new_depth} 层！阴煞更加浓郁，大能神识威压愈发强烈！"
        tomb["log"].append(msg)
        state.remember(f"深入太古古墓【{theme.name}】至第 {new_depth} 层。")

        return {"tomb": tomb, "msg": msg}

    @classmethod
    def retreat(cls, state: GameState) -> dict[str, Any]:
        """Safely leave tomb with all collected treasures."""
        tomb = state.active_tomb
        if not tomb:
            raise ValueError("当前不在古墓中。")

        stones = tomb.get("loot_stones", 0)
        items = tomb.get("loot_items", {})

        # Transfer loot to player
        state.player.spirit_stones += stones
        for item, count in items.items():
            state.player.resources[item] = state.player.resources.get(item, 0) + count

        summary_parts = []
        if stones:
            summary_parts.append(f"灵石 +{stones}")
        for k, v in items.items():
            summary_parts.append(f"【{k}】×{v}")

        summary = "、".join(summary_parts) if summary_parts else "两手空空"

        completed = tomb.get("completed", False)
        depth = tomb.get("depth", 1)
        name = tomb.get("name", "太古古墓")

        ev = f"从【{name}】（第 {depth} 层）安全撤离返航！带出秘宝：{summary}。"
        state.remember(ev)
        state.tomb_history.append(ev)
        state.tomb_history = state.tomb_history[-20:]

        state.active_tomb = {}

        return {
            "stones": stones,
            "items": items,
            "completed": completed,
            "msg": f"【古墓撤离】安全脱离古墓秘境！带出宝物：{summary}！",
        }

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        """Snapshot for UI rendering."""
        return {
            "active": bool(state.active_tomb),
            "current_tomb": state.active_tomb or None,
            "themes": cls.get_available_themes(state),
            "history": list(state.tomb_history[-10:]),
        }
