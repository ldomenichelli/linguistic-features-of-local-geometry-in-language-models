> This directory preserves the earlier reproduction bundle and its numbering. For the current manuscript’s 7 figures and 16 tables, use [the current result index](current/README.md).

# Paper artifacts

This directory collects every numbered result in *Linguistic Features of Local Geometry in Language Models*.

- [`FIGURES.md`](FIGURES.md) shows Figures 1–6 and links to both PNG and PDF files.
- [`TABLES.md`](TABLES.md) renders Tables 1–17 and links to the corresponding CSV files.
- [`ARTIFACTS.md`](ARTIFACTS.md) explains where each result comes from and how far it can be regenerated from the public data.
- [`artifacts.csv`](artifacts.csv) provides the same mapping in machine-readable form.

Run `make paper` from the repository root to rebuild all six plots and all seventeen table CSVs in `results/paper/`. Figures 1–3 and 6 retain the manuscript exports. Figures 4 and 5 are clean vector rerenders from the archived paper values because the exact final export commands were not retained. Regenerated plots may differ slightly in font metrics or spacing across Matplotlib versions.

Table 13 contains seven short excerpts from The Pile. They are included because they appear in the paper and are needed to interpret that table. They remain third-party material.
