# Workflow

Use the repository README's checksum-pinned curl manager installation. A reviewed remote release must exist before its URL can be used; the current implementation has not been published.

Build a new inactive QE suite with `install --backend openblas --blas-library /absolute/path/libopenblas.dylib`. Select its exact printed `bin` directory for `check` and `workflow --engine manual` or `workflow --engine pwtk`. Use a new external `--out-dir` for every attempt.

The canonical order is SCF, bands and band postprocessing, uniform NSCF, DOS/PDOS, with explicit parents and artifact hashes. Analysis takes the fresh dataset manifest. Requested-rank PW/PH and one-managed-rank postprocessing define the current core layout. Never use historical bundled data to imply a new run passed.
