"""Predictor-style interface for a selected batch-correction method.

The functional API is ``scbatch.pp.batch_correct(adata, method=...)``. Use
``BatchCorrectionPredictor`` when one reference AnnData object will later be
applied to multiple query AnnData objects. The current scaffold stores a method
choice but does not yet fit or apply a scientific correction.
"""

from typing import Self

from anndata import AnnData

from .batch_correction_config import (
    DEFAULT_CORRECTION_METHOD,
    SUPPORTED_CORRECTION_METHODS,
    CorrectionMethod,
)


class BatchCorrectionPredictor:
    """Configure a batch-correction predictor before fitting reference anchors.

    ``method`` defaults to ``DEFAULT_CORRECTION_METHOD`` when omitted. A future
    predictor implementation will make ``fit`` learn from reference anchors,
    then allow ``transform`` to apply those learned parameters to query AnnData
    objects.
    """

    def __init__(
        self,
        method: CorrectionMethod = DEFAULT_CORRECTION_METHOD,
    ) -> None:
        """Store a validated method selection.

        Args:
            method: Registered correction key, defaulting when omitted.
        """
        self.method = method

    @staticmethod
    def available_batch_correction_methods() -> tuple[CorrectionMethod, ...]:
        """Return every method key accepted by this predictor.

        The list identifies registered choices, not completed scientific
        implementations.
        """
        return SUPPORTED_CORRECTION_METHODS

    def fit(self, ref_adata: AnnData) -> Self:
        """Fit the predictor using anchors in a reference AnnData object."""
        _ = ref_adata
        raise NotImplementedError("scbatch.pp.BatchCorrectionPredictor.fit is not implemented yet.")

    def transform(
        self,
        adata: AnnData,
    ) -> AnnData:
        """Use a fitted predictor to correct a query AnnData object."""
        _ = adata
        raise NotImplementedError(
            "scbatch.pp.BatchCorrectionPredictor.transform is not implemented yet."
        )

    def fit_transform(
        self,
        adata: AnnData,
    ) -> AnnData:
        """Fit the predictor and correct one AnnData object in a single call."""
        _ = adata
        raise NotImplementedError(
            "scbatch.pp.BatchCorrectionPredictor.fit_transform is not implemented yet."
        )


BatchCorrector = BatchCorrectionPredictor
"""Compatibility alias for :class:`BatchCorrectionPredictor`."""


def _print_usage_example() -> None:
    """Print the intended predictor workflow without executing unsupported methods."""
    print(
        "Usage example:\n"
        "from scbatch.pp import BatchCorrectionPredictor\n\n"
        "print(BatchCorrectionPredictor.available_batch_correction_methods())\n"
        "predictor = BatchCorrectionPredictor(method='qq')\n"
        "predictor.fit(reference_adata)\n"
        "corrected_adata = predictor.transform(query_adata)\n\n"
        "fit, transform, and fit_transform are currently unsupported and raise "
        "NotImplementedError when called."
    )


if __name__ == "__main__":
    from ...datasets.demo import load_demo

    adata = load_demo()
    predictor = BatchCorrectionPredictor()
    adata = predictor.fit_transform(adata)
    print(adata)
