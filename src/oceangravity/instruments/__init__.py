"""Instrument response and noise models."""

from .noise_curve import NoiseCurve, load_noise_curves

__all__ = ["NoiseCurve", "load_noise_curves"]

