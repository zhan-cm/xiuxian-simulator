from pathlib import Path
import pytest

from xiuxian_simulator.ancient_tomb import (
    TOMB_THEMES,
    AncientTombEngine,
)
from xiuxian_simulator.state import GameState, PlayerState
from xiuxian_simulator.engine import GameEngine
from xiuxian_simulator.narrator import LocalNarrator
from xiuxian_simulator.rules import RuleBook
from xiuxian_simulator.save_manager import SaveManager


def test_tomb_themes_integrity():
    assert len(TOMB_THEMES) >= 3
    for tid, theme in TOMB_THEMES.items():
        assert theme.id == tid
        assert theme.name
        assert theme.boss_name
        assert theme.min_realm_index >= 1
        assert len(theme.guardian_types) >= 3
        assert len(theme.trap_types) >= 3
        assert theme.special_drop


def test_enter_tomb_and_realm_requirement():
    state = GameState()
    state.player.realm_index = 0  # 练气期

    # Realm index too low for sword_crypt (requires realm_index >= 1)
    with pytest.raises(ValueError, match="境界不足"):
        AncientTombEngine.enter_tomb(state, "sword_crypt")

    state.player.realm_index = 1  # 筑基期
    res = AncientTombEngine.enter_tomb(state, "sword_crypt")
    assert res["tomb"]["id"] == "sword_crypt"
    assert res["tomb"]["depth"] == 1
    assert res["tomb"]["player_x"] == 0
    assert res["tomb"]["player_y"] == 0
    assert len(res["tomb"]["grid"]) == 25

    # Check entrance tile
    entrance = next(t for t in res["tomb"]["grid"] if t["x"] == 0 and t["y"] == 0)
    assert entrance["type"] == "entrance"
    assert entrance["revealed"] is True

    # Boss tile at (4, 4)
    boss = next(t for t in res["tomb"]["grid"] if t["x"] == 4 and t["y"] == 4)
    assert boss["type"] == "boss"


def test_tomb_movement_and_fog_reveal():
    state = GameState()
    state.player.realm_index = 1
    AncientTombEngine.enter_tomb(state, "sword_crypt")

    # Boundary check: cannot move Up or Left from (0, 0)
    with pytest.raises(ValueError, match="无法通行"):
        AncientTombEngine.move(state, "上")

    with pytest.raises(ValueError, match="无法通行"):
        AncientTombEngine.move(state, "左")

    # Move right to (1, 0)
    res = AncientTombEngine.move(state, "右")
    tomb = res["tomb"]
    assert tomb["player_x"] == 1
    assert tomb["player_y"] == 0
    assert tomb["miasma"] > 0

    # (2, 0) and (1, 1) should now be revealed
    t20 = next(t for t in tomb["grid"] if t["x"] == 2 and t["y"] == 0)
    t11 = next(t for t in tomb["grid"] if t["x"] == 1 and t["y"] == 1)
    assert t20["revealed"] is True
    assert t11["revealed"] is True


def test_tomb_interactions_and_retreat():
    state = GameState()
    state.player.realm_index = 2
    state.player.health = 50
    state.player.health_max = 200
    state.player.comprehension = 20
    state.player.spirit_sense = 20

    AncientTombEngine.enter_tomb(state, "sword_crypt")
    tomb = state.active_tomb

    # Mock current tile as altar
    cur_tile = next(t for t in tomb["grid"] if t["x"] == 0 and t["y"] == 0)
    cur_tile["type"] = "altar"
    cur_tile["cleared"] = False

    tomb["miasma"] = 40
    res_altar = AncientTombEngine.interact(state)
    assert state.player.health > 50
    assert tomb["miasma"] < 40
    assert cur_tile["cleared"] is True

    # Mock treasure tile
    cur_tile["type"] = "treasure"
    cur_tile["cleared"] = False
    cur_tile["reward_stones"] = 80
    cur_tile["reward_items"] = {"古剑残片": 1}

    res_box = AncientTombEngine.interact(state)
    assert tomb["loot_stones"] == 80
    assert tomb["loot_items"]["古剑残片"] == 1
    assert cur_tile["cleared"] is True

    # Retreat
    init_stones = state.player.spirit_stones
    res_retreat = AncientTombEngine.retreat(state)
    assert state.active_tomb == {}
    assert state.player.spirit_stones == init_stones + 80
    assert state.player.resources["古剑残片"] >= 1
    assert len(state.tomb_history) == 1


def test_engine_tomb_commands(tmp_path: Path):
    rules = RuleBook(Path("dummy"), "test", "dummy_sha")
    saves = SaveManager(tmp_path)
    narrator = LocalNarrator()
    engine = GameEngine(rules, saves, narrator)
    engine.state.phase = "playing"
    engine.state.player = PlayerState(name="陆沉", dao_name="沉玄", realm_index=2, health=100)

    # Panel shows available tombs
    out = engine.process("古墓探险")
    assert "太古大能秘境古墓" in out
    assert "太古纯阳剑冢" in out

    # Enter tomb
    out_enter = engine.process("进入古墓 1")
    assert "太古古墓开启" in out_enter
    assert "迷雾灵图" in out_enter
    assert engine.state.active_tomb

    # Move command
    out_move = engine.process("古墓移动 右")
    assert "移动至石室" in out_move

    # Interact command
    out_explore = engine.process("古墓探索")
    assert out_explore

    # Retreat command
    out_retreat = engine.process("古墓撤离")
    assert "【古墓撤离】" in out_retreat
    assert engine.state.active_tomb == {}
