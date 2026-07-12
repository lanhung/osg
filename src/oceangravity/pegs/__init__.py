"""Prompt elasto-gravity signal simulation and detection."""

from .scenario import ManilaScenario, TsunamiArrival
from .warning import WarningTimeline
from .energy_baseline import (
    HeldoutEnergyEventResult,
    SingleStationEnergyAudit,
    WindowEnergyScores,
    audit_single_station_energy_baseline,
    windowed_rms_energy_scores,
)
from .template_baseline import (
    NetworkTemplateScores,
    independent_noise_network_template_scores,
)
from .source_inversion import (
    DiscreteSourceInversion,
    SourceHypothesisFit,
    SourceTemplateHypothesis,
    invert_discrete_source_library,
)
from .network import (
    NetworkPerformance,
    coherent_network_stack,
    generate_station_outage_masks,
    pareto_optimal_networks,
)
from .stations import (
    StationEpochReadiness,
    StationReadinessAudit,
    audit_station_readiness,
)

__all__ = [
    "ManilaScenario",
    "TsunamiArrival",
    "WarningTimeline",
    "HeldoutEnergyEventResult",
    "SingleStationEnergyAudit",
    "WindowEnergyScores",
    "audit_single_station_energy_baseline",
    "windowed_rms_energy_scores",
    "NetworkTemplateScores",
    "independent_noise_network_template_scores",
    "DiscreteSourceInversion",
    "SourceHypothesisFit",
    "SourceTemplateHypothesis",
    "invert_discrete_source_library",
    "NetworkPerformance",
    "coherent_network_stack",
    "generate_station_outage_masks",
    "pareto_optimal_networks",
    "StationEpochReadiness",
    "StationReadinessAudit",
    "audit_station_readiness",
]
