# scbatch

`scbatch` is a scientific Python package for single-cell batch-effect
correction research. It supports the paper workflow that compares established
methods with an anchor-based quantile-quantile correction approach.

The package follows Scanpy-style namespaces and uses `anndata.AnnData` as its
central data structure. It is developed as one published pip package with
separate UV workspace members for focused module development.

## Status

The repository currently provides the package and development framework. Batch
correction methods, graph construction, embeddings, clustering, diagnostic
plots, and bundled datasets are planned module work and must not be treated as
implemented scientific functionality until their public APIs and tests land.

## Package layout

| Namespace | Responsibility |
| --- | --- |
| `scbatch.pp` | Preprocessing and batch-correction methods |
| `scbatch.pl` | Diagnostic and result plotting |
| `scbatch.datasets` | Reproducible and synthetic AnnData datasets |
| `scbatch.tl` | scbatch-specific downstream tools, currently DBSCAN |

The project design is documented in
[`documentation/Python Package Design.pdf`](documentation/Python%20Package%20Design.pdf)
and the current research roadmap is in
[`documentation/roadmap.pdf`](documentation/roadmap.pdf).

## Notebook examples

Jupyter notebook examples are located in the [`examples/`](examples/) directory.

## Develop from a Git checkout

Clone the repository, then choose one package manager. Each option installs
the local checkout in editable mode.

```bash
git clone https://github.com/yishaiar/scbatch.git
cd scbatch
```

### Regular package

Install only the package dependencies.

With UV:

```bash
uv sync --no-dev
```

With pip:

```bash
pip install -e .
```

### Development package

Install the package plus test, lint, type-check, and notebook tools.

With UV:

```bash
uv sync
```

With pip:

```bash
pip install -e ".[dev]"
```

`uv sync --no-dev` and `pip install -e .` are the equivalent regular
installations. `uv sync` and `pip install -e ".[dev]"` are the equivalent
development installations. The UV `dev` dependency group and pip `dev` extra
are intentionally kept aligned.

## Install a released package

If you only want the published package, rather than a Git checkout, install it
from PyPI:

```bash
pip install scbatch
```

For the published package plus the development tools:

```bash
pip install "scbatch[dev]"
```

See [`documentation/development.md`](documentation/development.md) for
workspace-member development, local tests, notebooks, and verification.

## Local development with Git worktrees

Each feature uses an isolated Git worktree. From the main checkout:

```bash
cd <path-to-repo>/scbatch
git worktree add -b <feature-name> ../scbatch-<feature-name>
cd ../scbatch-<feature-name>
UV_PROJECT_ENVIRONMENT=$(pwd)/.venv uv sync --project $(pwd)
```

List worktrees with `git worktree list`. After merging or discarding the
feature branch, run this from the main checkout:

```bash
cd <path-to-repo>/scbatch
git worktree remove --force ../scbatch-<feature-name>
git branch -d <feature-name>
```

Git includes committed `.agents/` and `.codex/` configuration in every
worktree. Until those directories are committed, a new worktree will not
contain them. Git does not create symlinks or copy ignored local state. See
[`documentation/development.md`](documentation/development.md) for the full
worktree, environment-file, agent-hook, and cleanup conventions.

## Data model and conventions

- Public processing and tool functions operate on `anndata.AnnData`.
- Raw and intermediate values are stored in named AnnData layers.
- Method provenance and parameters are recorded in `adata.uns`.
- Embeddings and graph-derived representations use standard AnnData slots.
- Public request, configuration, and result schemas use Pydantic v2.

## Package design

The package is designed as a unified AnnData workflow. Public functions accept
and return the same multi-sample, multi-batch AnnData object, including sparse
or dense matrices. Batch labels and anchor labels are explicit metadata keys.

- `adata.raw` preserves uncorrected input when a workflow needs it.
- Named layers hold intermediate transformations, such as an arcsinh layer and
  a final corrected layer.
- `adata.uns` records method selection and fitted transformation parameters,
  including slopes, intercepts, and quantile-curve data when applicable.
- The correction API will support functional entry points and a
  scikit-learn-style estimator that fits reference batches and transforms query
  samples.
- `scbatch.datasets` will provide lightweight synthetic AnnData examples, and
  `scbatch.pl` will provide diagnostics for extrapolation, distributional
  alignment, and per-marker differences.

These are design contracts, not a claim that the corresponding methods are
implemented yet.

## Pipeline contract

`scbatch.run_pipeline` is the orchestration API. It runs the working matrix
through the following named representations. Every matrix snapshot is an
independent copy, so retaining all layers has a proportional memory cost.

| Stage | Owner | Result |
| --- | --- | --- |
| Input | scbatch pipeline | `adata.layers["input"]` |
| Empty-profile removal | `scanpy.pp.filter_cells(min_counts=1)` | `adata.layers["filtered"]` |
| ArcSinh | `scbatch.pp.arcsinh` | `adata.layers["arcsinh"]` |
| Batch correction | `scbatch.pp.batch_correct` | `adata.layers["batch_corrected"]` |
| Core normalization | `scbatch.pp.normalize_core` | `adata.layers["core_normalized"]` |
| Scaling | `scanpy.pp.scale` | `adata.layers["scaled"]` |
| UMAP, including its required neighbors graph | `scanpy.pp.neighbors`, then `scanpy.tl.umap` | graph in `adata.obsp` and `adata.uns["neighbors"]`; coordinates in `adata.obsm["X_umap"]`; `adata.layers["umap"]` X snapshot |
| Leiden, when `clustering_is_leiden=True` | `scanpy.tl.leiden` | `adata.obs["leiden"]`, `adata.uns["leiden"]`, and `adata.layers["leiden"]` X snapshot |
| DBSCAN, when `clustering_is_leiden=False` | `scbatch.tl.dbscan` | algorithm output and `adata.layers["dbscan"]` X snapshot |

The pipeline mutates the supplied `adata` and works on `adata.X`. Its `input`
layer is an independent snapshot of the matrix before processing. The default
Scanpy QC call removes empty profiles only. It is not a biological or
CyTOF-specific gating threshold; apply domain-specific QC before running the
pipeline. `clustering_is_leiden=True` runs Scanpy Leiden, while `False` runs
scbatch DBSCAN.

`filter_cells`, `scale`, `neighbors`, `umap`, and `leiden` are deliberately
not re-exported by scbatch. Import them directly from Scanpy when you need
individual control. ArcSinh, batch correction, core normalization, and DBSCAN
remain scbatch-owned operations. ArcSinh, core normalization, and QQ batch
correction currently use a temporary ``adata.X + 1`` placeholder. They must
not be interpreted as completed scientific implementations. The other batch
correction methods and DBSCAN remain scaffolds.

## Research direction

The target correction workflow uses shared reference controls, non-parametric
QQ mappings, interpolation within anchor-supported ranges, and chained
cross-batch transforms. The package will expose this method alongside
comparator methods only after reproducible implementations and validation are
available.

## License

MIT License. See [LICENSE](LICENSE).
