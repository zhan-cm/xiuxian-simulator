from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from . import __version__
from .choices import DecisionCatalog
from .engine import GameEngine
from .presentation import present_action, welcome_presentation
from .relationships import NPCS
from .npc_lifecycle import NpcLifecycleEngine
from .npc_network import NpcNetworkEngine
from .state import GameState
from .journey import JourneyEngine
from .commissions import CommissionEngine
from .story import StoryEngine
from .new_era import NewEraEngine
from .dao import DaoEngine
from .items import InventoryEngine
from .auctions import AuctionEngine
from .travel import TravelEngine
from .regional import RegionalEngine
from .cave import CaveEngine
from .beasts import SpiritBeastEngine
from .formations import FormationEngine
from .sect_library import SectLibraryEngine
from .artifact_growth import ArtifactGrowthEngine
from .art_mastery import ArtMasteryEngine
from .recovery import RecoveryEngine
from .legacy import LegacyEngine
from .sect_foundation import SectFoundationEngine
from .sect_diplomacy import SectDiplomacyEngine


class WebApplication:
    """Shared application facade used by the single React/FastAPI interface."""

    def __init__(self, engine: GameEngine, project_root: Path, decisions: DecisionCatalog | None = None) -> None:
        self.engine = engine
        self.project_root = project_root.resolve()
        self.decisions = decisions or DecisionCatalog.load(
            self.project_root / "data" / "content" / "decision_choices.json"
        )
        self._lock = threading.Lock()
        self._presentation = welcome_presentation()

    def snapshot(self) -> dict[str, Any]:
        life_state = GameState.from_dict(self.engine.state.to_dict())
        npc_lives = NpcLifecycleEngine.snapshot(life_state)
        npc_network = NpcNetworkEngine.snapshot(life_state)
        life_by_name = {item["name"]: item for item in npc_lives["profiles"]}
        npc_profiles = {
            name: {
                "name": npc.name,
                "gender": npc.gender,
                "identity": npc.identity,
                "age": life_by_name[name]["age"],
                "lifespan": life_by_name[name]["lifespan"],
                "realm": life_by_name[name]["realm"],
                "location": life_by_name[name]["location"],
                "likes": list(npc.likes),
                "dislikes": list(npc.dislikes),
                "greeting": npc.greeting,
                "affinity": int(self.engine.state.npc_relations.get(name, {}).get("affinity", 0)),
                "relation": life_by_name[name]["relation"],
                "alive": life_by_name[name]["alive"],
                "status": life_by_name[name]["status"],
            }
            for name, npc in NPCS.items()
        }
        sect_domain = SectFoundationEngine.snapshot(self.engine.state)
        sect_domain["diplomacy"] = SectDiplomacyEngine.snapshot(self.engine.state)
        return {
            "app_version": __version__,
            "state": self.engine.state.to_dict(),
            "narrator": self.engine.narrator.name,
            "save_names": self.engine.saves.list_names(),
            "save_summaries": self.engine.saves.list_summaries(),
            "presentation": self._presentation,
            "decision": self.decisions.for_state(self.engine.state),
            "npc_profiles": npc_profiles,
            "journey": JourneyEngine.snapshot(self.engine.state),
            "commissions": CommissionEngine.snapshot(self.engine.state),
            "story": StoryEngine.snapshot(self.engine.state),
            "new_era": NewEraEngine.snapshot(self.engine.state),
            "dao": DaoEngine.snapshot(self.engine.state),
            "spirit_beasts": SpiritBeastEngine.snapshot(self.engine.state),
            "formations": FormationEngine.snapshot(self.engine.state),
            "sect_library": SectLibraryEngine.snapshot(self.engine.state),
            "artifacts": ArtifactGrowthEngine.snapshot(self.engine.state),
            "art_mastery": ArtMasteryEngine.snapshot(self.engine.state),
            "recovery": RecoveryEngine.snapshot(self.engine.state),
            "legacy": LegacyEngine.snapshot(self.engine.state),
            "sect_domain": sect_domain,
            "inventory": InventoryEngine.snapshot(self.engine.state),
            "auction": AuctionEngine.snapshot(self.engine.state),
            "travel": TravelEngine.snapshot(self.engine.state),
            "regional": RegionalEngine.snapshot(self.engine.state),
            "cave": CaveEngine.snapshot(self.engine.state),
            "npc_lives": npc_lives,
            "npc_network": npc_network,
        }

    def perform_action(self, action: str) -> dict[str, Any]:
        """Run one validated action and return the shared UI snapshot.

        The FastAPI interface uses this method so action results and snapshots
        always share one rule and presentation path.
        """
        normalized = action.strip()
        with self._lock:
            before = self.engine.state.to_dict()
            output = self.engine.process(normalized)
            after = self.engine.state.to_dict()
            self._presentation = present_action(normalized, output, before, after)
            snapshot = self.snapshot()
        return {"output": output, **snapshot}

    def export_save(self, name: str) -> dict[str, Any]:
        with self._lock:
            return self.engine.saves.export_payload(name)

    def import_save(
        self,
        payload: dict[str, Any],
        *,
        preferred_name: str = "",
        overwrite: bool = False,
    ) -> dict[str, Any]:
        with self._lock:
            result = self.engine.saves.import_payload(
                payload,
                preferred_name=preferred_name,
                overwrite=overwrite,
                expected_rule_sha256=self.engine.rules.sha256,
            )
            result["save_summaries"] = self.engine.saves.list_summaries()
        return result
