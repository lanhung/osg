"""Observable and provenance constraints for environmental Newtonian-noise models."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestNewtonianNoiseManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[2]
        cls.document = json.loads(
            (root / "data/manifests/newtonian_noise_models.json").read_text()
        )

    def test_models_are_separate_from_instrument_curves(self) -> None:
        self.assertEqual(self.document["schema_version"], 1)
        self.assertEqual(len(self.document["models"]), 2)
        for model in self.document["models"]:
            self.assertTrue(model["not_an_instrument_noise_curve"])
            self.assertEqual(
                model["output_observable"],
                "equivalent_gravitational_wave_strain_noise",
            )
            self.assertTrue(model["source"].startswith("https://doi.org/"))

    def test_cosmic_explorer_input_unit_conversions(self) -> None:
        model = next(
            item
            for item in self.document["models"]
            if item["model_id"] == "cosmic_explorer_local_gravity_fluctuation_budget"
        )
        inputs = model["reported_design_inputs"]
        self.assertEqual(inputs["rayleigh_wave_ambient_acceleration_asd_m_s2_hz_minus_half"], 1e-6)
        self.assertEqual(inputs["body_wave_ambient_acceleration_asd_m_s2_hz_minus_half"], 3e-7)
        self.assertEqual(inputs["infrasound_pressure_asd_pa_hz_minus_half"], 1e-3)
        self.assertGreater(
            inputs["rayleigh_wave_required_mitigation_db"],
            inputs["body_wave_required_mitigation_db"],
        )

    def test_unimplemented_models_cannot_be_mistaken_for_completed_curves(self) -> None:
        self.assertTrue(
            all("not yet" in item["implementation_status"] for item in self.document["models"])
        )


if __name__ == "__main__":
    unittest.main()

