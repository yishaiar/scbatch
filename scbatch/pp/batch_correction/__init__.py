"""Batch-correction method choices and entrypoints."""

from .boundary_extrapolated_qq import batch_correct_boundary_extrapolated_qq
from .batch_correction_config import (
    DEFAULT_CORRECTION_METHOD,
    SUPPORTED_CORRECTION_METHODS,
    CorrectionMethod,
)
from .cycombine import batch_correct_cycombine
from .cytonorm import batch_correct_cytonorm
from .scanpy_batch_correction import available_batch_correction_methods, batch_correct
from .batch_correction_predictor import BatchCorrectionPredictor, BatchCorrector
from .fastmnn import batch_correct_fastmnn
from .harmony import batch_correct_harmony
from .mmd_resnet import batch_correct_mmd_resnet
from .qq import batch_correct_qq

__all__ = [
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
]
