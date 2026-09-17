import pytest
from pathlib import Path

from xiuxian_simulator.encounters import (
    ENCOUNTERS_CATALOG,
    RedDustEncounterEngine,
    EncounterDefinition,
)
from xiuxian_simulator.state import GameState, PlayerState
from xiuxian_simulator.choices import DecisionCatalog
from xiuxian_simulator.engine import GameEngine
from xiuxian_simulator.narrator import LocalNarrator
from xiuxian_simulator.rules import RuleBook
from xiuxian_simulator.save_manager import SaveManager


def test_encounters_catalog_integrity():
    assert len(ENCOUNTERS_CATALOG) >= 12
    for enc_id, enc in ENCOUNTERS_CATALOG.items():
        assert enc.id == enc_id
        assert enc.title
        assert enc.scene
        assert enc.character.name
        assert enc.character.identity
        assert enc.character.quote
        assert len(enc.choices) >= 2
        for choice in enc.choices:
            assert choice.id
            assert choice.label
            assert choice.dao_stance
            assert choice.outcome_text
            assert choice.summary


def test_trigger_encounter_and_snapshot():
    state = GameState()
    state.phase = "playing"
    state.player.realm_index = 1
    state.player.location = "东洲·青岳"

    # Forced trigger
    enc_data = RedDustEncounterEngine.trigger_encounter(state, forced_id="ancient_remains")
    assert enc_data is not None
    assert state.phase == "encounter_choice"
    assert state.pending_encounter["id"] == "ancient_remains"

    snapshot = RedDustEncounterEngine.snapshot(state)
    assert snapshot["active"] is True
    assert snapshot["pending"]["id"] == "ancient_remains"
    assert snapshot["pending"]["character"]["name"] == "太古剑尊残魂"
    assert len(snapshot["pending"]["choices"]) >= 3

    text = RedDustEncounterEngine.text_panel(state)
    assert "古修士遗蜕与残魂传道" in text
    assert "太古剑尊残魂" in text


def test_resolve_encounter_with_effects():
    state = GameState()
    state.phase = "playing"
    state.player.spirit = 50
    state.player.health = 100
    state.player.merit = 0
    state.player.karma = 0
    state.player.dao_points = 0
    state.player.dao_insight = 0

    RedDustEncounterEngine.trigger_encounter(state, forced_id="ancient_remains")

    # Choose worship
    res = RedDustEncounterEngine.resolve(state, "worship")
    assert res["choice_id"] == "worship"
    assert res["dao_stance"] == "慈悲仁善"
    assert state.phase == "playing"
    assert state.pending_encounter == {}
    assert state.player.merit == 3
    assert state.player.dao_points == 1
    assert state.player.dao_insight == 25
    assert state.player.resources.get("古剑残片") == 1
    assert "ancient_remains" in state.completed_encounters
    assert len(state.encounter_history) == 1


def test_resolve_requirement_check():
    state = GameState()
    state.phase = "playing"
    state.player.spirit = 5  # Needs 20 for purify

    RedDustEncounterEngine.trigger_encounter(state, forced_id="ancient_remains")
    with pytest.raises(ValueError, match="条件不满足"):
        RedDustEncounterEngine.resolve(state, "purify")


def test_npc_affinity_encounter():
    state = GameState()
    state.phase = "playing"
    state.player.spirit = 40

    # Trigger Gu Qingxuan encounter
    RedDustEncounterEngine.trigger_encounter(state, forced_id="gu_qingxuan_encounter")
    initial_aff = state.npc_relations.get("顾清玄", {}).get("affinity", 0)

    res = RedDustEncounterEngine.resolve(state, "discuss_sword")
    assert res["choice_id"] == "discuss_sword"
    new_aff = state.npc_relations.get("顾清玄", {}).get("affinity", 0)
    assert new_aff >= initial_aff + 20
    assert state.player.spirit == 20  # 40 - 20


def test_engine_seek_and_choice_flow(tmp_path: Path):
    rules = RuleBook(Path("dummy"), "test", "dummy_sha")
    saves = SaveManager(tmp_path)
    narrator = LocalNarrator()
    engine = GameEngine(rules, saves, narrator)

    engine.state.phase = "playing"
    engine.state.player = PlayerState(name="陆沉", dao_name="沉玄", spirit=50, health=100)
    assert engine.state.phase == "playing"

    # Command: 寻觅机缘
    out = engine.process("寻觅机缘")
    assert engine.state.phase == "encounter_choice"
    assert "红尘奇遇" in out

    # Test DecisionCatalog produces encounter choices
    decisions = DecisionCatalog({})
    decision = decisions.for_state(engine.state)
    assert decision["exclusive"] is True
    assert len(decision["choices"]) >= 2
    first_action = decision["choices"][0]["action"]
    assert first_action.startswith("奇遇选择 ")

    # Process choice action
    choice_out = engine.process(first_action)
    assert engine.state.phase == "playing"
    assert "因果回响" in choice_out
    assert len(engine.state.completed_encounters) >= 1
