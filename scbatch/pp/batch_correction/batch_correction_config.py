"""Method names and default for batch correction."""

from typing import Literal

CorrectionMethod = Literal[
    "boundary_extrapolated_qq",
    "qq",
    "cytonorm",
    "cycombine",
    "mmd_resnet",
    "harmony",
    "fastmnn",
]

SUPPORTED_CORRECTION_METHODS: tuple[CorrectionMethod, ...] = (
    "boundary_extrapolated_qq",
    "qq",
    "cytonorm",
    "cycombine",
    "mmd_resnet",
    "harmony",
    "fastmnn",
)
"""Registered method keys accepted by functional and predictor-style APIs."""

DEFAULT_CORRECTION_METHOD: CorrectionMethod = "boundary_extrapolated_qq"
"""Method used whenever a caller does not select a correction method."""
