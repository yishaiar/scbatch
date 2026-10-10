# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

> **Always read `.agents/memory/MEMORY.md` at the start of every session**. It contains persistent project knowledge and gotchas.

## Overview

`scbatch` is a scientific Python monorepo for the batch-effect comparison paper and its package implementation. It has one published distribution, `scbatch`; `scbatch/pp`, `scbatch/pl`, `scbatch/datasets`, and `scbatch/tl` are internal UV workspace ownership boundaries, not separately installable applications.

## Commands

### Installation

```bash
uv sync
```

### Testing

```bash
# One package component
uv run pytest scbatch/<module>/tests

# All package tests
uv run pytest

# A specific test file
uv run pytest scbatch/<module>/tests/test_<component>.py
```

### Linting and formatting

```bash
uv run ruff format .
uv run ruff format --check .
uv run ruff check .
uv run basedpyright
```

### Environment

The project is platform-neutral and supports macOS, Linux, and Windows. Do not add platform-specific dependency pins unless a documented upstream incompatibility requires one. Never commit local environments, cache directories, generated coverage artifacts, or `uv.lock`.

## Code standards

- **Pydantic for all API schemas**. Use Pydantic v2 models for request, configuration, and result validation. No raw dictionaries at public API boundaries.
- **No bare `except`**. Always catch specific exceptions.
- **Type hints required**. All public function signatures must have type hints.
- **Ruff must pass**. Run `uv run ruff check .` before any PR. Ruff is the primary linter.
- **AnnData contracts are explicit**. Preserve sparse data and axis alignment. Store provenance and method parameters in `adata.uns`, intermediate data in named layers, and embeddings or graphs in standard AnnData slots.

### Engineering principles

- Favor modular, reusable scientific interfaces so a new correction method or benchmark needs minimal changes to existing modules.
- Self-check new code for repeated multi-line logic before presenting it as done, then extract a helper where that improves clarity. This does not apply to intentionally parallel sibling functions.
- Keep parallel scientific entities, such as correction-method adapters, benchmark metrics, and plot helpers, structurally consistent even when that costs some duplication.
- Prioritize readability, explicit contracts, and reproducibility over clever or condensed abstractions.
- Write tests for new code and update the corresponding tests whenever existing behavior changes. The save hook runs `uv run pytest` automatically for `test_*.py` saves.

## Skills

Skills are defined in `.agents/skills/<skill-name>/SKILL.md`. Automatically invoke the relevant skill based on the current context. Do not wait for the user to explicitly call it.

Skills below cover structured processes. The per-file execution-validation loop is separately driven by `.agents/hooks/`, wired in `.codex/hooks.json`.

| Event | Script | Purpose |
| --- | --- | --- |
| `PreToolUse` (Bash) | `secret-scan-on-commit.sh` | No-op unless the command is `git commit`; blocks the commit if the staged diff looks like a hardcoded credential |
| `PostToolUse` (Edit\|Write) | `format-on-save.sh` | Auto-formats saved Python files and Jupyter notebook code cells with Ruff |
| `PostToolUse` (Edit\|Write) | `lint-on-save.sh` | Lints saved Python files, Markdown code fences, and Jupyter notebook code cells with Ruff |
| `PostToolUse` (Edit\|Write) | `pyright-on-save.sh` | Type-checks the saved Python file with BasedPyright |
| `PostToolUse` (Edit\|Write) | `debug-artifact-on-save.sh` | Flags leftover `pdb` and `breakpoint()` calls |
| `PostToolUse` (Edit\|Write) | `test-on-spec-save.sh` | Runs `uv run pytest` whenever a `test_*.py` file is saved |
| `Stop` | `notify-on-stop.sh` | Sends a notification naming the repository, worktree, and branch when a session ends |
| `UserPromptSubmit` | `cold-eye-reminder.sh` | Re-injects the `cold-eye` objectivity reminder into every prompt |
| `UserPromptSubmit` | `plan-mode-enforce-skill.sh` | When `permission_mode` is `plan`, nudges Codex to load `plan-new-feature` instead of following native Plan Mode generically |

| Trigger | Skill |
| --- | --- |
| *(always active, reinforced every turn via the `UserPromptSubmit` hook)* | `/cold-eye` |
| User reports a bug, error, or something is not working | `/debugger` |
| User asks to implement, create, add, or build a new feature | `/plan-new-feature` |
| User says start implementing or execute the plan, once a plan is approved | `/execute-new-feature` |
| User asks to refactor, clean up, simplify, or improve code | `/refactor` |
| User asks to review, check, or audit code, or is preparing a PR | `/code-reviewer` |
| User asks to write or format a commit message, or is ready to commit | `/commit-workflow` |
| User asks to create a planned notebook or add or change its code cells | `/execute-new-notebook-code` |
| User asks to run or validate a Jupyter notebook | `/start-jupyter-server`, then `/validate-notebook` |
| User says rebase, fix conflicts, or my branch is behind | `/rebase-and-resolve` |
| User asks to add tests or increase coverage | `/write-tests` |
| User asks to create, open, or draft a PR | `/create-pr` |
| User asks what code does or wants to understand it before changing it | `/explain-code` |
| After resolving a bug, learning a pattern, or making an architectural decision | `/update-memory` |
| User wants to log or track a feature, fix, or improvement for a release | `/track-release-feature` |
| User says run tests, fix tests, make tests green, or after code changes | `/babysit-tests` |
| User shares or pastes a skill file, asks if it is safe, or wants to audit one | `/skill-scanner` |
| User finishes or pauses complex feature work and wants to save context | `/save-feature-context` |
| User asks to start Jupyter, check its connection, or verify that a live Jupyter kernel connection is available | `/start-jupyter-server` |

### New-feature flow

For implementing a new feature end-to-end, skills chain in this order. These are three separate pipelines. Clear the conversation between each step for fresh context; every step reads persisted state rather than conversation history.

1. `/plan-new-feature` plans in Plan Mode. On approval, it saves the plan to `.agents/memory/CURRENT_PLAN.md`, a gitignored local scratch file, and suggests switching permission mode for the execution phase.

   Clear the conversation here.

2. `/execute-new-feature` loads the approved plan from `.agents/memory/CURRENT_PLAN.md`, then implements it phase by phase: types, logic, error handling, tests, and documentation. It invokes `/write-tests`, then `/babysit-tests` to verify the result.

   Clear the conversation here.

3. `/create-pr` invokes `/commit-workflow` if needed, invokes `/rebase-and-resolve` when the branch is behind, runs `/code-reviewer` against the resulting diff, drafts the PR description, and invokes `/track-release-feature` after a successful merge.

Push and opening a PR always require explicit user go-ahead. That gate is not skill-controlled.

### New-notebook flow

For a new Jupyter notebook or new code in an existing notebook, use this
sequence. Each stage uses persisted plan state where applicable instead of
relying solely on conversation history.

1. `/plan-new-feature` defines the new notebook or notebook-code goal,
   intended inputs, files, and validation target. After approval, save the plan to
   `.agents/memory/CURRENT_PLAN.md`.

2. `/execute-new-notebook-code` creates the notebook or adds the approved new code
   to an existing notebook. It adds a runtime-provenance cell that asserts
   imports come from the intended checkout, verifies structure only, and hands
   off to validation. It must not claim that the notebook runs.

3. Invoke `/start-jupyter-server` immediately before validation and confirm that
   a live Jupyter kernel connection is available.

4. Invoke `/validate-notebook` deliberately after notebook work is ready, not
   after every edit. Validation must open the notebook, restart the kernel, run
   all cells, wait for the kernel to become idle, inspect fresh outputs and
   provenance, then save the notebook. Source inspection, `nbformat`, shell
   imports, and Jupyter server health checks are supplementary only, never
   proof that the notebook ran.

5. If validation reports an error, invoke `/debugger` with the failing cell and
   full notebook output, repair the responsible layer, then repeat step 4. Do
   not describe the notebook as working before step 4 passes.

### Rebase conflict patterns

- **`pyproject.toml`**. Merge dependency-group, tool, and workspace-member changes entry by entry. `uv.lock` is ignored, so regenerate it locally with `uv sync` rather than merging it.
- **`scbatch/<module>/__init__.py`**. Preserve exports from both branches, then verify every export belongs to its owning scientific namespace.
- **`scbatch/<module>/pyproject.toml`**. Keep the member's ownership boundaries and dependency declarations from both branches. Do not turn members into independently published distributions.
- **Scientific API modules**. Do not resolve competing AnnData mutation contracts syntactically. If both branches change representation keys, layers, or `adata.uns` provenance semantics, surface the decision to the user.
- **Documentation and README**. Keep both source-installation and research-workflow changes, but ensure commands consistently name `scbatch`, use UV or pip accurately, and do not claim unimplemented methods exist.

### Future skills, not yet built

- **`/generate-release-notes`**. Expand raw bullets accumulated by `/track-release-feature` into polished release notes at release-cut time.
- **`/personal:update-work-log`**. Personal tooling from the source conventions, not part of this repository's agent framework. Add a repository-level equivalent only if requested later.

## Architecture

### Scientific package architecture

This repository is a Scanpy-style scientific package, not an application monorepo. Its UV workspace members are ownership boundaries for scientific code.

```text
AnnData input
    |
    +-- scbatch.datasets  reproducible inputs and fixtures
    +-- scbatch.pp        validation, transformations, correction
    +-- scbatch.tl        graph, embedding, clustering, downstream analysis
    +-- scbatch.pl        diagnostics and publication-ready plots
```

`pp` may write documented corrected or intermediate layers and method provenance to `adata.uns`. `tl` consumes documented representations and writes graphs or embeddings to standard AnnData slots. `pl` reads results without mutation unless its public API explicitly states otherwise. `datasets` supplies deterministic, documented test and example inputs.

Use `AnnData` for data-bearing APIs and Pydantic v2 for public request, configuration, and result schemas. Validate metadata keys, shapes, and axis alignment before mutation.

### Package structure

```text
scbatch/
├── pp/        # preprocessing and batch correction
├── pl/        # diagnostics and result plotting
├── datasets/  # reproducible and synthetic AnnData datasets
└── tl/        # graph, embedding, clustering, and downstream tools
```

When creating a new scientific capability, first define the public schema and AnnData mutation contract. Then implement it in the owning member, add local tests for normal, invalid, empty, sparse, and dense inputs as applicable, and export only stable public functions through the corresponding namespace.

The generic staged-pipeline blueprint is preserved in `.agents/memory/architecture_layered_pipeline.md` for future repositories that actually have applications. Do not force that application architecture onto `scbatch`.

## Tests

Tests live beside the owning component at `scbatch/<module>/tests/test_<component>.py`. Keep setup local to the test class, use `unittest.TestCase` for synchronous code and `unittest.IsolatedAsyncioTestCase` for asynchronous code, and use `unittest.mock` for external services. Test normal behavior, invalid metadata, empty inputs, sparse and dense inputs where supported, and Pydantic validation when a public schema is introduced.

Jupyter is optional support for notebooks and exploratory verification. The `start-jupyter-server` skill checks connectivity only and must not substitute for package tests.
