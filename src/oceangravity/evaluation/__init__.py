"""Metrics, uncertainty, holdout evaluation, and experiment reporting."""

from .detection import (
    gaussian_detection_probability,
    gaussian_threshold_for_false_alarm,
    required_snr_for_detection_probability,
)

__all__ = [
    "gaussian_detection_probability",
    "gaussian_threshold_for_false_alarm",
    "required_snr_for_detection_probability",
]

