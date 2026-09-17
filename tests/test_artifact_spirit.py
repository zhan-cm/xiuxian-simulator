from pathlib import Path
import pytest

from xiuxian_simulator.artifact_spirit import (
    SPIRIT_ARCHETYPES,
    ArtifactSpiritEngine,
)
from xiuxian_simulator.combat import CombatEngine
from xiuxian_simulator.engine import GameEngine
from xiuxian_simulator.narrator import LocalNarrator
from xiuxian_simulator.rules import RuleBook
from xiuxian_simulator.save_manager import SaveManager
from xiuxian_simulator.state import GameState, PlayerState
from xiuxian_simulator.webapp import WebApplication


def test_archetypes_integrity():
    assert len(SPIRIT_ARCHETYPES) == 4
    for key in ("sword_fairy", "thunder_child", "mirror_maiden", "cauldron_spirit"):
        assert key in SPIRIT_ARCHETYPES
        arch = SPIRIT_ARCHETYPES[key]
        assert arch.name
        assert arch.title
        assert arch.description
        assert arch.personality
        assert arch.default_name
        assert arch.combat_skill_name
        assert arch.combat_skill_desc
        assert arch.skill_value > 0
        assert len(arch.quotes) >= 3


def test_can_manifest():
    state = GameState()
    # 1. No bonded artifact
    can, reason = ArtifactSpiritEngine.can_manifest(state)
    assert not can
    assert "尚未祭炼【本命法宝】" in reason

    # 2. Bonded but resonance < 30
    state.bonded_artifact = "青竹蜂云剑"
    state.artifact_refinements["青竹蜂云剑"] = {"resonance": 20}
    can, reason = ArtifactSpiritEngine.can_manifest(state)
    assert not can
    assert "器心契合度不足" in reason

    # 3. Resonance >= 30
    state.artifact_refinements["青竹蜂云剑"]["resonance"] = 45
    can, reason = ArtifactSpiritEngine.can_manifest(state)
    assert can
    assert reason == ""


def test_manifest_and_talk():
    state = GameState()
    state.bonded_artifact = "青竹蜂云剑"
    state.artifact_refinements["青竹蜂云剑"] = {"resonance": 50}

    # Manifest with default name
    res = ArtifactSpiritEngine.manifest(state, "sword_fairy")
    assert res["spirit"]["name"] == "青霜"
    assert res["spirit"]["archetype_id"] == "sword_fairy"
    assert res["spirit"]["level"] == 1
    assert res["spirit"]["intimacy"] == 60
    assert res["spirit"]["is_active"] is True
    assert state.artifact_spirit["name"] == "青霜"
    assert len(state.artifact_spirit_history) == 1

    # Talk
    talk_res = ArtifactSpiritEngine.talk(state, "青霜，可愿陪我同登仙道？")
    assert talk_res["intimacy"] == 62
    assert state.artifact_spirit["intimacy"] == 62
    assert len(state.artifact_spirit["dialogue_history"]) >= 2
    assert "青霜" in talk_res["msg"]


def test_manifest_with_custom_name():
    state = GameState()
    state.bonded_artifact = "紫霄雷印"
    state.artifact_refinements["紫霄雷印"] = {"resonance": 60}

    res = ArtifactSpiritEngine.manifest(state, "thunder_child", "小雷霆")
    assert res["spirit"]["name"] == "小雷霆"
    assert res["spirit"]["archetype_id"] == "thunder_child"
    assert state.artifact_spirit["name"] == "小雷霆"


def test_feed_and_level_up():
    state = GameState()
    state.bonded_artifact = "八卦紫金鼎"
    state.artifact_refinements["八卦紫金鼎"] = {"resonance": 80}
    ArtifactSpiritEngine.manifest(state, "cauldron_spirit", "赤火")

    # Feed with insufficient stones
    state.player.spirit_stones = 10
    with pytest.raises(ValueError, match="灵石不足"):
        ArtifactSpiritEngine.feed(state, "灵石")

    # Feed with stones
    state.player.spirit_stones = 100
    feed_res = ArtifactSpiritEngine.feed(state, "灵石")
    assert state.player.spirit_stones == 50
    assert feed_res["exp_gain"] == 50
    assert state.artifact_spirit["exp"] == 50
    assert state.artifact_spirit["intimacy"] == 65
    assert not feed_res["leveled_up"]

    # Feed with 聚气丹 and level up
    state.player.resources["聚气丹"] = 3
    feed_res2 = ArtifactSpiritEngine.feed(state, "聚气丹")
    assert feed_res2["exp_gain"] == 20
    assert state.artifact_spirit["exp"] == 70

    # Feed with 筑基丹 (exp +60 => 130 => level up!)
    state.player.resources["筑基丹"] = 1
    feed_res3 = ArtifactSpiritEngine.feed(state, "筑基丹")
    assert feed_res3["leveled_up"] is True
    assert state.artifact_spirit["level"] == 2
    assert state.artifact_spirit["exp"] == 30  # 130 - 100
    assert state.artifact_spirit["skill_value"] == 55  # 45 + 10


def test_toggle_active():
    state = GameState()
    state.bonded_artifact = "玄阴宝镜"
    state.artifact_refinements["玄阴宝镜"] = {"resonance": 40}
    ArtifactSpiritEngine.manifest(state, "mirror_maiden")

    assert state.artifact_spirit["is_active"] is True
    res = ArtifactSpiritEngine.toggle_active(state)
    assert res["is_active"] is False
    assert state.artifact_spirit["is_active"] is False

    res2 = ArtifactSpiritEngine.toggle_active(state)
    assert res2["is_active"] is True
    assert state.artifact_spirit["is_active"] is True


def test_combat_assist_and_combat_engine():
    state = GameState()
    state.bonded_artifact = "青竹蜂云剑"
    state.artifact_refinements["青竹蜂云剑"] = {"resonance": 50}
    ArtifactSpiritEngine.manifest(state, "sword_fairy", "青霜")

    CombatEngine.prepare(state, "噬灵獾", mode="切磋")
    CombatEngine.start(state)

    # Initial enemy health
    initial_enemy_hp = state.combat["enemy_health"]
    # Act attack on round 0 (even round => spirit assist triggers!)
    round_res = CombatEngine.act(state, "攻击")
    # Spirit assist text should be present
    assert "青霜" in round_res.player_text or "青莲断空斩" in round_res.player_text
    # Enemy health should have dropped by attack damage + spirit assist damage (50)
    assert state.combat["enemy_health"] < initial_enemy_hp


def test_engine_commands(tmp_path):
    rules = RuleBook(Path("dummy"), "test", "dummy_sha")
    saves = SaveManager(tmp_path)
    engine = GameEngine(rules, saves, LocalNarrator(), autosave_name="test_save")
    engine.state.phase = "playing"
    engine.state.player = PlayerState(name="林逸", dao_name="纯阳", realm_index=2, health=100)

    # Before bonded artifact
    out = engine.process("器灵")
    assert "尚未祭炼【本命法宝】" in out

    # Give player a bonded artifact and resonance
    engine.state.bonded_artifact = "青云剑"
    engine.state.artifact_refinements["青云剑"] = {"resonance": 40}

    out2 = engine.process("器灵")
    assert "已可举行化形大典" in out2

    # Manifest via command
    out_manifest = engine.process("器灵化形 剑仙 青霜仙子")
    assert "青霜仙子" in out_manifest
    assert engine.state.artifact_spirit["name"] == "青霜仙子"

    # Talk via command
    out_talk = engine.process("器灵交谈 今日剑道大进")
    assert "器灵心声" in out_talk

    # Feed via command
    engine.state.player.resources["聚气丹"] = 2
    out_feed = engine.process("器灵喂养 聚气丹")
    assert "喂养器灵【青霜仙子】" in out_feed

    # Toggle active
    out_toggle = engine.process("召回器灵")
    assert "化为原形归位" in out_toggle or "静养" in out_toggle

    # Webapp snapshot
    root = Path(__file__).resolve().parent.parent
    app = WebApplication(engine, root)
    snap = app.snapshot()
    assert "artifact_spirit" in snap
    assert snap["artifact_spirit"]["spirit"]["name"] == "青霜仙子"
