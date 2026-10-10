"""Scanpy-style preprocessing and batch-correction entrypoints."""

from .arcsinh import arcsinh
from .gating import gating
from .batch_correction import (
    BatchCorrectionPredictor,
    BatchCorrector,
    CorrectionMethod,
    DEFAULT_CORRECTION_METHOD,
    SUPPORTED_CORRECTION_METHODS,
    available_batch_correction_methods,
    batch_correct,
    batch_correct_boundary_extrapolated_qq,
    batch_correct_cycombine,
    batch_correct_cytonorm,
    batch_correct_fastmnn,
    batch_correct_harmony,
    batch_correct_mmd_resnet,
    batch_correct_qq,
)
from .normalize_core import normalize_core

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
]
