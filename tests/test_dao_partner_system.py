import pytest
from pathlib import Path
from xiuxian_simulator.partner_system import (
    PARTNER_BLESSINGS_PRESETS,
    PARTNER_MESSAGES_PRESETS,
    CHILD_NAMES,
    DaoPartnerEngine,
)
from xiuxian_simulator.state import GameState, PlayerState
from xiuxian_simulator.relationships import RelationshipEngine
from xiuxian_simulator.combat import CombatEngine
from xiuxian_simulator.engine import GameEngine
from xiuxian_simulator.narrator import LocalNarrator
from xiuxian_simulator.rules import RuleBook
from xiuxian_simulator.save_manager import SaveManager


def test_presets_integrity():
    protagonists = ["顾清玄", "白凝霜", "云栖", "谢无咎", "墨尘", "洛浅浅"]
    for p in protagonists:
        assert p in PARTNER_BLESSINGS_PRESETS
        bless = PARTNER_BLESSINGS_PRESETS[p]
        assert bless.name
        assert bless.partner_name == p
        assert bless.duration_months >= 6
        assert p in PARTNER_MESSAGES_PRESETS
        assert len(PARTNER_MESSAGES_PRESETS[p]) >= 2
        assert p in CHILD_NAMES
        assert len(CHILD_NAMES[p]) == 4


def test_dual_cultivate_blessing_and_epiphany():
    state = GameState()
    state.phase = "playing"
    state.player.realm_index = 1
    state.player.health = 50
    state.player.health_max = 100
    state.player.spirit = 20
    state.player.spirit_max = 80

    # Not partner yet
    with pytest.raises(ValueError, match="尚未结契"):
        DaoPartnerEngine.dual_cultivate(state, "白凝霜")

    # Add partner
    state.dao_partners.append("白凝霜")
    RelationshipEngine.add_affinity(state, "白凝霜", 85)

    res = DaoPartnerEngine.dual_cultivate(state, "白凝霜")
    assert res["partner"] == "白凝霜"
    assert res["blessing"] == "玄冥冰魄印"
    assert "白凝霜" in state.active_partner_blessings
    bless_data = state.active_partner_blessings["白凝霜"]
    assert bless_data["remaining_months"] == 6
    assert bless_data["defense_bonus"] == 25
    assert state.partner_dual_counts["白凝霜"] == 1
    # Health and spirit restored
    assert state.player.health >= 100
    assert state.player.spirit == 80


def test_send_message_and_gifts():
    state = GameState()
    state.player.spirit_stones = 100

    # Not partner
    with pytest.raises(ValueError, match="心印未通"):
        DaoPartnerEngine.send_message(state, "云栖", "你好呀")

    state.dao_partners.append("云栖")
    res = DaoPartnerEngine.send_message(state, "云栖", "云姑娘，近日安好？")
    assert res["partner"] == "云栖"
    assert res["reply"]
    assert len(state.partner_message_history) == 1
    assert state.player.spirit_stones > 100  # Received stones gift


def test_conceive_and_grow_child():
    state = GameState()
    state.calendar_year = 387
    state.turn = 10
    state.player.name = "林渡"
    state.dao_partners.append("顾清玄")
    RelationshipEngine.add_affinity(state, "顾清玄", 90)

    # Affinity not 100 yet
    with pytest.raises(ValueError, match="心意未达"):
        DaoPartnerEngine.conceive_child(state, "顾清玄")

    RelationshipEngine.add_affinity(state, "顾清玄", 20)  # affinity reaches 100+
    # Dual count not 3 yet
    with pytest.raises(ValueError, match="阴阳合道不足"):
        DaoPartnerEngine.conceive_child(state, "顾清玄")

    state.partner_dual_counts["顾清玄"] = 3
    res = DaoPartnerEngine.conceive_child(state, "顾清玄")
    assert res["child"]["name"] == "顾慕玄"
    assert res["child"]["spiritual_root"] == "纯阳天灵根"
    assert len(state.partner_children) == 1

    # Second child
    res2 = DaoPartnerEngine.conceive_child(state, "顾清玄")
    assert res2["child"]["name"] == "顾素心"

    # Max 2 children per partner
    with pytest.raises(ValueError, match="已有圆满"):
        DaoPartnerEngine.conceive_child(state, "顾清玄")

    # Advance child growth
    state.calendar_year = 397  # 10 years later
    DaoPartnerEngine.grow_children(state, 12)
    assert state.partner_children[0]["age"] == 10
    assert state.partner_children[0]["stage"] == "凡胎·童蒙"

    # Advance to 16 years
    state.calendar_year = 403  # 16 years later
    events = DaoPartnerEngine.grow_children(state, 12)
    assert state.partner_children[0]["stage"] == "筑基成道"
    assert any("筑基大成" in e for e in events)
    assert state.player.resources.get("天材地宝", 0) >= 1


def test_combat_blessing_integration():
    state = GameState()
    state.phase = "combat"
    state.player.realm_index = 2
    state.player.stage_index = 0
    state.player.aptitude = 20
    state.player.fortune = 10
    state.player.health = 50
    state.player.health_max = 200

    # Add Xie Wujiu blessing: 25% attack boost, 15% lifesteal
    state.active_partner_blessings["谢无咎"] = {
        "name": "修罗杀生印",
        "attack_multiplier": 1.25,
        "defense_bonus": 0,
        "lifesteal_percent": 0.15,
    }

    CombatEngine.prepare(state, "青云宗外门弟子")
    state.phase = "combat"
    state.combat["round"] = 1

    initial_hp = state.player.health
    strike = CombatEngine._player_strike(state, 1.0, "attack")
    if strike.hit and strike.damage > 0:
        # Lifesteal triggered
        assert state.player.health >= initial_hp


def test_engine_partner_commands(tmp_path: Path):
    rules = RuleBook(Path("dummy"), "test", "dummy_sha")
    saves = SaveManager(tmp_path)
    narrator = LocalNarrator()
    engine = GameEngine(rules, saves, narrator)
    engine.state.phase = "playing"
    engine.state.player = PlayerState(name="陆沉", dao_name="沉玄", spirit=50, health=100)

    # Check partner chamber when empty
    out = engine.process("同修阁")
    assert "尚未与任何红颜知己或挚友结下道侣之契" in out

    # Add partner
    engine.state.dao_partners.append("洛浅浅")
    RelationshipEngine.add_affinity(engine.state, "洛浅浅", 95)

    out = engine.process("同修阁")
    assert "【洛浅浅】" in out
    assert "素女妙真印" in out

    # Dual cultivate via engine command
    out_dual = engine.process("仙侣同修 洛浅浅")
    assert "合修静室阴阳互济" in out_dual
    assert "素女妙真印" in out_dual

    # Soul transmission
    out_msg = engine.process("传音 洛浅浅 浅浅，为兄甚念卿")
    assert "本命心印千里传音" in out_msg
    assert "洛浅浅心印传音回响" in out_msg

    # Children panel empty
    out_kids = engine.process("仙家子嗣")
    assert "宗族尚无子嗣生息" in out_kids
