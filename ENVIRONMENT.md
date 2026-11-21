# Environment notes

## Recorded interpreter and packages

The experiment environment used CPython 3.10.12. The two requirements files
serve different purposes:

- `requirements-analysis.txt` is the smaller CPU environment for paper
  artifacts and downstream analysis;
- `requirements-full.txt` adds model extraction, parsing, visualization, and
  FCI dependencies recorded in the working environment.

Versions are exact records, not promises that every wheel remains available on
every platform. On systems without a compatible prebuilt PyTorch wheel, follow
PyTorch's platform-specific installation guidance and then install the
remaining pins. Record any deviation before comparing results.

## Threading

Numerical libraries may use many CPU threads. For a conservative and more
repeatable CPU run:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  make PYTHON=.venv/bin/python analysis
```

The Random Forest implementation records `random_state=42`; its worker count
may be configured by the analysis script without changing the intended
statistical design.

## GPU execution

The full representation workflow expects a CUDA-capable PyTorch environment
for the large models. CUDA toolkit, driver, GPU model, and original extraction
hardware were not preserved as a complete manifest. Do not infer bitwise GPU
reproducibility from the Python pins alone.

Use explicit model commits and save a fresh environment/hardware manifest for
any new extraction run. The sanitized extractor refuses an omitted revision;
that protects new runs from silently depending on a mutable default.

## Platform-neutral paths

Commands in this repository use paths relative to the repository root. Keep
large local inputs in ignored locations such as `data/raw/`, `data/interim/`,
`artifacts/`, or a separately mounted directory supplied on the command line.
