# Project Memory

## Package topology

- `scbatch` is the only published pip distribution.
- UV workspace members `scbatch/pp`, `scbatch/pl`, `scbatch/datasets`, and
  `scbatch/tl` are internal development boundaries and use `package = false`.
- The root project owns the union of runtime dependencies. Member TOMLs record
  the dependencies owned by each scientific namespace.

## Scientific conventions

- Public computational APIs use `anndata.AnnData` and Scanpy-style module
  namespaces.
- Preserve sparse matrices and AnnData axis alignment unless a documented
  operation requires otherwise.
- Store method parameters and provenance in `adata.uns`; use layers for
  intermediate matrices and standard AnnData slots for derived data.
- Pydantic v2 models remain mandatory at public API boundaries.

## Tests and quality

- Tests live with their owning component at `scbatch/<module>/tests/` and use
  `unittest.TestCase` unless asynchronous behavior requires
  `unittest.IsolatedAsyncioTestCase`.
- The root development group provides Ruff, BasedPyright, pytest, Jupyter, and
  notebook tooling.

## Documentation

- The PDFs and notebooks under `documentation/` are research and design
  sources. Do not claim a planned method is implemented until its public API
  and local tests exist.
