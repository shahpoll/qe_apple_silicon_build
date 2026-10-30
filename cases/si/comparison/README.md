# Historical silicon comparison archive

The bundled outputs are historical QE 7.4.1-era artifacts. They are retained as evidence, not current-build qualification. Some manual/PWTK spectra disagree and their provenance is incomplete; the old comparison reassurance is not a valid numerical verdict.

Generate fresh results with `qe-apple-silicon-build workflow --qe-bin /absolute/path/bin --out-dir /absolute/path/new-run`. For PWTK add `--engine pwtk --pwtk /absolute/path/pwtk --tclsh /absolute/path/tclsh8.6`. Both engines use canonical identical settings and verified parent datasets.

Use `qe-apple-silicon-build compare --manual /absolute/path/new-manual --pwtk /absolute/path/new-pwtk --out-dir /absolute/path/new-comparison`. Plots and summaries require an explicit fresh run with `dataset.json`; implicit bundled data is refused. See the repository README for curl installation and evidence handling.
