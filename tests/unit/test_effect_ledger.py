"""Environmental effect ownership and CMEMS/ERA5 collision tests."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from oceangravity.loading import EffectDeclaration, audit_effect_ledger  # noqa: E402

SPEC = importlib.util.spec_from_file_location(
    "audit_effect_composition", ROOT / "scripts/audit_effect_composition.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _row(source, effect, status):
    return EffectDeclaration(source, effect, status, "unit-test evidence")


class TestEffectLedger(unittest.TestCase):
    def test_one_owner_and_explicit_exclusion_close_effect(self) -> None:
        audit = audit_effect_ledger(
            (_row("A", "effect", "included"), _row("B", "effect", "excluded")),
            required_effect_ids=("effect",),
        )
        self.assertTrue(audit.closure_ready)
        self.assertEqual(audit.effects[0].status, "closed")

    def test_duplicate_unknown_and_missing_owners_are_distinct(self) -> None:
        audit = audit_effect_ledger(
            (
                _row("A", "duplicate", "included"),
                _row("B", "duplicate", "included"),
                _row("A", "ambiguous", "included"),
                _row("B", "ambiguous", "unknown"),
                _row("A", "missing", "excluded"),
            ),
            required_effect_ids=("duplicate", "ambiguous", "missing", "undeclared"),
        )
        statuses = {row.effect_id: row.status for row in audit.effects}
        self.assertEqual(statuses["duplicate"], "duplicate_owner")
        self.assertEqual(statuses["ambiguous"], "ambiguous_possible_overlap")
        self.assertEqual(statuses["missing"], "missing_owner")
        self.assertEqual(statuses["undeclared"], "missing_owner")
        self.assertFalse(audit.closure_ready)

    def test_repository_p2_e001_snapshot_preserves_open_gate(self) -> None:
        document = json.loads((ROOT / "configs/paper2/effect_composition.json").read_text())
        result = MODULE.audit_document(document)
        self.assertFalse(result["closure_ready"])
        ib = next(
            row
            for row in result["effects"]
            if row["effect_id"] == "ocean_inverse_barometer_response"
        )
        self.assertEqual(ib["status"], "ambiguous_possible_overlap")
        self.assertEqual(ib["included_sources"], ("era5_inverse_barometer_model",))
        self.assertEqual(ib["unknown_sources"], ("cmems_ntol_forward_model",))

    def test_p2_e002_cmems_ib_status_closes_without_double_counting(self) -> None:
        document = json.loads((ROOT / "configs/paper2/effect_composition_closed.json").read_text())
        result = MODULE.audit_document(document)
        self.assertTrue(result["closure_ready"])
        ib = next(
            row
            for row in result["effects"]
            if row["effect_id"] == "ocean_inverse_barometer_response"
        )
        self.assertEqual(ib["status"], "closed")
        self.assertEqual(ib["included_sources"], ("era5_inverse_barometer_model",))
        self.assertEqual(ib["excluded_sources"], ("cmems_ntol_forward_model",))
        self.assertEqual(ib["unknown_sources"], ())


if __name__ == "__main__":
    unittest.main()
