from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .crafting import RECIPES, CraftingEngine, Recipe
from .dao import DaoEngine
from .progression import ProgressionEngine
from .state import GameState


FOCUSES: dict[str, dict[str, Any]] = {
    "蕴养灵脉": {
        "title": "蕴养灵脉",
        "summary": "每月灵蕴产量提高五成",
        "facility": "",
    },
    "潜修养元": {
        "title": "潜修养元",
        "summary": "静室每月消耗灵蕴，缓慢增长修为",
        "facility": "静室",
    },
    "灵田轮作": {
        "title": "灵田轮作",
        "summary": "消耗灵蕴照料作物，加快成熟",
        "facility": "灵田",
    },
    "百艺轮转": {
        "title": "百艺轮转",
        "summary": "后台生产成功率提高 8%",
        "facility": "工坊",
    },
}


@dataclass(frozen=True, slots=True)
class CaveTickResult:
    generated: int
    events: tuple[str, ...]


class CaveEngine:
    @staticmethod
    def energy_cap(state: GameState) -> int:
        gathering = state.cave_facilities.get("聚灵阵", 0)
        ward = state.cave_facilities.get("禁制", 0)
        return 24 + gathering * 18 + ward * 3

    @staticmethod
    def monthly_generation(state: GameState) -> int:
        base = 2 + state.cave_facilities.get("聚灵阵", 0) * 3 + DaoEngine.cave_energy_bonus(state)
        if state.cave_focus == "蕴养灵脉":
            base = (base * 3 + 1) // 2
        return base

    @staticmethod
    def recipe_duration(recipe: Recipe) -> int:
        if recipe.name == "筑基丹":
            return 3
        return {"炼丹": 2, "炼器": 3, "符箓": 1}.get(recipe.craft, 2)

    @staticmethod
    def facility_capacity(state: GameState, facility: str) -> int:
        return max(0, state.cave_facilities.get(facility, 0))

    @classmethod
    def active_for_facility(cls, state: GameState, facility: str) -> int:
        return sum(1 for job in state.cave_workshop_jobs if job.get("facility") == facility)

    @classmethod
    def focus_availability(cls, state: GameState, focus: str) -> tuple[bool, str]:
        if focus not in FOCUSES:
            return False, "未知运转方针"
        required = str(FOCUSES[focus]["facility"])
        if not required:
            return True, ""
        if required == "工坊":
            if state.cave_facilities.get("丹房", 0) or state.cave_facilities.get("器坊", 0):
                return True, ""
            return False, "需要至少建成丹房或器坊"
        if state.cave_facilities.get(required, 0) < 1:
            return False, f"需要至少 1 级{required}"
        return True, ""

    @classmethod
    def set_focus(cls, state: GameState, focus: str) -> None:
        available, reason = cls.focus_availability(state, focus)
        if not available:
            raise ValueError(reason)
        state.cave_focus = focus
        cls._record(state, f"洞府运转方针改为“{focus}”")

    @classmethod
    def queue_recipe(cls, state: GameState, name: str) -> dict[str, Any]:
        if name not in RECIPES:
            raise ValueError("未知洞府生产配方：" + name)
        recipe = RECIPES[name]
        level = state.cave_facilities.get(recipe.facility, 0)
        if level < 1:
            raise ValueError(f"需要至少 1 级{recipe.facility}才能安排{name}。")
        active = cls.active_for_facility(state, recipe.facility)
        if active >= cls.facility_capacity(state, recipe.facility):
            raise ValueError(f"{recipe.facility}的生产位已满；升级设施可增加队列容量。")
        CraftingEngine.consume_ingredients(state, recipe)
        state.cave_job_counter += 1
        duration = cls.recipe_duration(recipe)
        bonus = 8 if state.cave_focus == "百艺轮转" else 0
        job = {
            "id": f"府-{state.cave_job_counter:03d}",
            "recipe": name,
            "craft": recipe.craft,
            "facility": recipe.facility,
            "started_turn": state.turn,
            "due_turn": state.turn + duration,
            "duration": duration,
            "chance": CraftingEngine.success_chance(state, recipe, bonus),
            "output": recipe.output,
            "output_count": recipe.output_count,
            "ingredients": dict(recipe.ingredients),
        }
        state.cave_workshop_jobs.append(job)
        cls._record(state, f"{recipe.facility}开始后台制作{name}，预计 {duration} 个月完成")
        return job

    @classmethod
    def cancel_job(cls, state: GameState, job_id: str) -> dict[str, Any]:
        job = next((item for item in state.cave_workshop_jobs if str(item.get("id")) == job_id), None)
        if job is None:
            raise ValueError(f"找不到进行中的洞府生产：{job_id}")
        state.cave_workshop_jobs.remove(job)
        for name, count in dict(job.get("ingredients", {})).items():
            CraftingEngine.add_resource(state, str(name), int(count))
        cls._record(state, f"取消{job.get('recipe', '未名造物')}的生产，预留材料已全部取回")
        return job

    @classmethod
    def recuperate(cls, state: GameState) -> tuple[int, int, int]:
        level = state.cave_facilities.get("静室", 0)
        if level < 1:
            raise ValueError("需要至少 1 级静室才能洞府调息。")
        cost = 10
        if state.cave_spirit_energy < cost:
            raise ValueError(f"洞府灵蕴不足：需要 {cost}，当前 {state.cave_spirit_energy}。")
        if state.player.health >= state.player.health_max and state.player.spirit >= state.player.spirit_max:
            raise ValueError("气血与灵力均已充盈，无需消耗灵蕴调息。")
        if state.player.health >= state.player.health_max and state.player.spirit >= state.player.spirit_max:
            raise ValueError("气血与灵力均已充盈，无需消耗灵蕴调息。")
        state.cave_spirit_energy -= cost
        health_before = state.player.health
        spirit_before = state.player.spirit
        amount = 28 + level * 7
        state.player.health = min(state.player.health_max, state.player.health + amount)
        state.player.spirit = min(state.player.spirit_max, state.player.spirit + amount)
        return state.player.health - health_before, state.player.spirit - spirit_before, cost

    @classmethod
    def tick(cls, state: GameState) -> CaveTickResult:
        cap = cls.energy_cap(state)
        before = state.cave_spirit_energy
        state.cave_spirit_energy = min(cap, before + cls.monthly_generation(state))
        generated = state.cave_spirit_energy - before
        events: list[str] = []

        if state.cave_focus == "潜修养元" and state.cave_facilities.get("静室", 0) > 0:
            if state.cave_spirit_energy >= 3 and state.player.cultivation < state.player.cultivation_required:
                state.cave_spirit_energy -= 3
                gained = min(1 + state.cave_facilities.get("静室", 0), state.player.cultivation_required - state.player.cultivation)
                state.player.cultivation += gained
                events.append(f"静室潜修消耗灵蕴 3，修为 +{gained}")
        elif state.cave_focus == "灵田轮作" and state.cave_facilities.get("灵田", 0) > 0:
            growing = [(name, due) for name, due in state.spirit_crops.items() if due > state.turn]
            if growing and state.cave_spirit_energy >= 2:
                crop, due = min(growing, key=lambda item: item[1])
                state.cave_spirit_energy -= 2
                state.spirit_crops[crop] = max(state.turn, due - 1)
                events.append(f"灵田轮作消耗灵蕴 2，{crop}成熟提前 1 个月")

        completed = [job for job in state.cave_workshop_jobs if int(job.get("due_turn", 0)) <= state.turn]
        for job in completed:
            state.cave_workshop_jobs.remove(job)
            name = str(job.get("recipe", "未名造物"))
            recipe = RECIPES.get(name)
            if recipe is None:
                events.append(f"{name}生产记录异常，已停止该任务")
                continue
            chance = int(job.get("chance", CraftingEngine.success_chance(state, recipe)))
            roll = ProgressionEngine.deterministic_roll(state, f"cave-job:{job.get('id')}:{name}")
            if roll <= chance:
                leveled = CraftingEngine.record_success(state, recipe)
                rank = f"，{recipe.craft}技艺有所精进" if leveled else ""
                events.append(f"{recipe.facility}完成{name}：成功获得{recipe.output}×{recipe.output_count}{rank}（{roll}/{chance}）")
            else:
                events.append(f"{recipe.facility}完成{name}：炼制失败，预留材料尽毁（{roll}/{chance}）")

        if events:
            for event in events:
                cls._record(state, event)
        return CaveTickResult(generated, tuple(events))

    @staticmethod
    def _record(state: GameState, event: str) -> None:
        state.last_cave_event = event
        state.cave_ledger.append(f"第 {state.turn} 回合｜{event}")
        state.cave_ledger = state.cave_ledger[-30:]

    @classmethod
    def snapshot(cls, state: GameState) -> dict[str, Any]:
        jobs: list[dict[str, Any]] = []
        for job in state.cave_workshop_jobs:
            duration = max(1, int(job.get("duration", 1)))
            remaining = max(0, int(job.get("due_turn", state.turn)) - state.turn)
            jobs.append(
                {
                    **job,
                    "months_left": remaining,
                    "progress": max(0, min(100, round((duration - remaining) / duration * 100))),
                    "cancel_action": f"取消洞府生产 {job.get('id')}",
                }
            )

        blueprints: list[dict[str, Any]] = []
        for recipe in RECIPES.values():
            missing = [
                f"{name}×{count}"
                for name, count in recipe.ingredients.items()
                if state.player.resources.get(name, 0) < count
            ]
            level = state.cave_facilities.get(recipe.facility, 0)
            full = level > 0 and cls.active_for_facility(state, recipe.facility) >= cls.facility_capacity(state, recipe.facility)
            reason = ""
            if level < 1:
                reason = f"需要 1 级{recipe.facility}"
            elif full:
                reason = f"{recipe.facility}生产位已满"
            elif missing:
                reason = "缺少 " + "、".join(missing)
            bonus = 8 if state.cave_focus == "百艺轮转" else 0
            blueprints.append(
                {
                    "name": recipe.name,
                    "craft": recipe.craft,
                    "facility": recipe.facility,
                    "duration": cls.recipe_duration(recipe),
                    "ingredients": dict(recipe.ingredients),
                    "output": recipe.output,
                    "output_count": recipe.output_count,
                    "chance": CraftingEngine.success_chance(state, recipe, bonus),
                    "available": not reason,
                    "disabled_reason": reason,
                    "action": f"洞府生产 {recipe.name}",
                }
            )

        focuses = []
        for name, definition in FOCUSES.items():
            available, reason = cls.focus_availability(state, name)
            focuses.append(
                {
                    "name": name,
                    "summary": definition["summary"],
                    "active": state.cave_focus == name,
                    "available": available,
                    "disabled_reason": reason,
                    "action": f"洞府方针 {name}",
                }
            )

        capacity = sum(cls.facility_capacity(state, facility) for facility in ("静室", "丹房", "器坊"))
        return {
            "name": state.cave_name,
            "aura": state.aura_level,
            "spirit_energy": state.cave_spirit_energy,
            "spirit_energy_cap": cls.energy_cap(state),
            "monthly_generation": cls.monthly_generation(state),
            "focus": state.cave_focus,
            "focuses": focuses,
            "capacity": capacity,
            "active_jobs": len(jobs),
            "jobs": jobs,
            "blueprints": blueprints,
            "last_event": state.last_cave_event,
            "ledger": list(reversed(state.cave_ledger[-8:])),
            "can_recuperate": state.cave_facilities.get("静室", 0) > 0 and state.cave_spirit_energy >= 10,
            "recuperate_reason": (
                "需要 1 级静室"
                if state.cave_facilities.get("静室", 0) < 1
                else (f"需要灵蕴 10，当前 {state.cave_spirit_energy}" if state.cave_spirit_energy < 10 else "")
            ),
        }
