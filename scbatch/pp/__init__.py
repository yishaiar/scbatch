"""Scanpy-style preprocessing and batch-correction entrypoints."""

from importlib import import_module
from typing import Any

from .arcsinh import arcsinh
from .gating import gating
from .normalize_core import normalize_core

_DIRECT_EXPORTS = {
    "run_pre_processing": ".pipeline",
}
_BATCH_CORRECTION_EXPORTS = {
    "BatchCorrectionPredictor",
    "BatchCorrector",
    "CorrectionMethod",
    "DEFAULT_CORRECTION_METHOD",
    "SUPPORTED_CORRECTION_METHODS",
    "available_batch_correction_methods",
    "batch_correct",
    "batch_correct_boundary_extrapolated_qq",
    "batch_correct_cycombine",
    "batch_correct_cytonorm",
    "batch_correct_fastmnn",
    "batch_correct_harmony",
    "batch_correct_mmd_resnet",
    "batch_correct_qq",
}

__all__ = [
    "BatchCorrectionPredictor",
    "BatchCorrector",
    "CorrectionMethod",
    "DEFAULT_CORRECTION_METHOD",
    "SUPPORTED_CORRECTION_METHODS",
    "available_batch_correction_methods",
    "arcsinh",
    "gating",
    "batch_correct",
    "batch_correct_boundary_extrapolated_qq",
    "batch_correct_cycombine",
    "batch_correct_cytonorm",
    "batch_correct_fastmnn",
    "batch_correct_harmony",
    "batch_correct_mmd_resnet",
    "batch_correct_qq",
    "normalize_core",
    "run_pre_processing",
]


def __getattr__(name: str) -> Any:
    """Load a public preprocessing entry point only when it is requested."""
    if name in _DIRECT_EXPORTS:
        value = getattr(import_module(_DIRECT_EXPORTS[name], __name__), name)
    elif name in _BATCH_CORRECTION_EXPORTS:
        value = getattr(import_module(".batch_correction", __name__), name)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = value
    return value
