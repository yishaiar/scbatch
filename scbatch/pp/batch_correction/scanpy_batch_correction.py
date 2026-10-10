"""Scanpy-style functional batch-correction API.

Call ``batch_correct(adata, method=...)`` to choose one registered correction
method for an AnnData object. This module finds the selected method function and
forwards the AnnData object to it. The ``qq`` method currently applies a
temporary ``adata.X + 1``
operation; the remaining method implementations are pass-through scaffolds.
"""

from collections.abc import Callable

from anndata import AnnData

from .batch_correction_config import (
    DEFAULT_CORRECTION_METHOD,
    SUPPORTED_CORRECTION_METHODS,
    CorrectionMethod,
)
from .boundary_extrapolated_qq import batch_correct_boundary_extrapolated_qq
from .cycombine import batch_correct_cycombine
from .cytonorm import batch_correct_cytonorm
from .fastmnn import batch_correct_fastmnn
from .harmony import batch_correct_harmony
from .mmd_resnet import batch_correct_mmd_resnet
from .qq import batch_correct_qq

# Every method accepts one AnnData object.
BatchCorrectionFunction = Callable[..., AnnData]

# Method strings are public choices. The mapping keeps selection in
# one Scanpy-style entrypoint while each method remains independently importable.
_METHOD_FUNCTIONS: dict[str, BatchCorrectionFunction] = {
    "boundary_extrapolated_qq": batch_correct_boundary_extrapolated_qq,
    "qq": batch_correct_qq,
    "cytonorm": batch_correct_cytonorm,
    "cycombine": batch_correct_cycombine,
    "mmd_resnet": batch_correct_mmd_resnet,
    "harmony": batch_correct_harmony,
    "fastmnn": batch_correct_fastmnn,
}


def available_batch_correction_methods() -> tuple[CorrectionMethod, ...]:
    """Return the method keys selectable through ``batch_correct``.

    The returned keys are registered API choices. They do not imply that every
    method has a completed scientific implementation.
    """
    return SUPPORTED_CORRECTION_METHODS


def batch_correct(
    adata: AnnData,
    method: str = DEFAULT_CORRECTION_METHOD,
) -> AnnData:
    """Run one selected correction method using a Scanpy-style function call.

    Args:
        adata: AnnData object supplied to, and currently returned by, the method.
        method: Registered correction key. Omit it to use the configured default.
    Returns:
        The selected method's AnnData result. Only ``qq`` currently transforms
        ``adata.X``, using the temporary ``X + 1`` placeholder.

    ``run_pipeline`` owns the ``layers['batch_corrected']`` snapshot after
    this stage. The scientific correction implementation remains pending.
    """
    try:
        correction_function = _METHOD_FUNCTIONS[method]
    except KeyError as error:
        raise ValueError(f"Unknown batch-correction method: {method!r}.") from error
    correction_function(adata)
    return adata


def _print_usage_example() -> None:
    """Print the functional API workflow and current implementation status."""
    print(
        "Usage example:\n"
        "from scbatch.pp import available_batch_correction_methods, batch_correct\n\n"
        "print(available_batch_correction_methods())\n"
        "corrected_adata = batch_correct(adata, method='qq')\n\n"
        "The qq method temporarily adds one to adata.X. Other registered methods "
        "remain unsupported-operation scaffolds."
    )


if __name__ == "__main__":
    from ...datasets.demo import load_demo

    adata = load_demo()
    adata = batch_correct(adata)
    print(adata)
