# Prepared project release

This repository combines a current-manuscript result snapshot with the existing reproduction archive. The two original working directories were not changed.

- Imported all 133 tracked files from `local-geometry-reproduction` before updating the public documentation, citation metadata, and build targets. Numeric inputs, scripts, archived results, configurations, and existing tests remain intact.
- Imported all 16 tables and 7 figures from the supplied current manuscript. Displayed numeric precision, captions, labels, exact table TeX, source artifact paths, and SHA-256 hashes are retained. Earlier table/figure numbering remains separate.
- Added 1,994 verified evaluation excerpts joined to the released numeric profiles and 27 measured model/depth/estimator settings. Preserved the one unavailable FCI measurement and raw feature missingness.
- Added the static interactive site, downloadable result files, reproducible browser-data exporter, site integrity checks, browser interaction checks, and GitHub Pages workflow.
- Added no code license and no link to the manuscript.

## Validation performed

`make check` passed: archived artifact regeneration and value comparisons; 28 experiment imports; 18 source/TF-IDF out-of-fold comparisons; 90 locality settings; 24 layers; 16 unit/integration tests; and complete explorer/result integrity checks.

`python3 scripts/check_browser.py` passed in headless Chrome: filtering, sorting, model-specific layers, estimator changes, pinned comparison, missing values, excerpt deep links, feature units, all download links, the contents and original numeric units of a filtered CSV export, and responsive layout at mobile/tablet widths. No JavaScript exceptions or failed HTTP requests were observed. Desktop and mobile screenshots were inspected.

The expensive full downstream refit and fresh language-model inference were not rerun for this packaging task. Current tables are transcriptions of the supplied manuscript, not new experiment estimates. The static browser uses the saved measurements.

Online publication requires creation of the named GitHub repository and a successful Pages deployment. See [PUBLISHING.md](PUBLISHING.md).

## Academic site revision

Replaced the presentation-led page with a compact paper page: real abstract and authors, central figures, compact tables, actual manuscript/code/data downloads, and a source browser. The supplied PDF is identified as an earlier version; current results are provided as CSV tables and figures. No unverified GitHub, DOI, or arXiv link is displayed.

The explorer now loads geometry progressively by model/layer and locality diagnostics on request. It supports paired model/layer plots, a nine-setting per-excerpt measurement table, feature-value filtering, feature-definition search, full-precision multi-estimator CSV export, and keyboard-operable plot points.

Verified the original locality query/source joins and text digests across nine settings: 498 aligned excerpts, five neighbourhood sizes, cumulative/shell intervals, and all 16 retained diagnostics. All 44,820 exported locality rows match the canonical Parquet data exactly. `make check` passes 17 tests plus artifact, provenance, percentile, download, and progressive-chunk checks. Real-browser checks pass with no JavaScript exceptions or failed requests, including source-precision CSV values, missing FCI handling, model/layer comparison, native keyboard navigation, retry after a blocked data file, and mobile/tablet layout.

See [SITE.md](SITE.md) for measure granularity, source units, missing observations, progressive loading, accessibility, and update instructions.


## Private review revision

Recovered the six remaining original texts and verified exact text/source alignment across all nine model/layer outputs. The explorer now contains all 2,000 evaluation excerpts. Missing linguistic profiles remain null, and recorded geometric measurements are unchanged. Browser percentiles now use the full available evaluation population, with denominator 2,000 (1,999 for the one unavailable early-layer Pythia FCI measurement). The paper’s recorded results and original feature table are unchanged.

All 500 locality-audit texts are included, with 45,000 exact diagnostic rows across nine settings. Feature-based plots omit unavailable feature pairs; geometry-only paired plots include all available estimates.

Removed ZIP and TeX download links and generated assets from the website. PDF, CSV, and JSON remain available. Public Pages publication no longer runs on push and requires an explicit manual opt-in in a public repository. The existing owner-only Sites preview is retained.

## Public release preparation — 25 November 2026

Removed the manuscript TeX and all 16 table TeX snippets. The importer now reads an external manuscript and writes only CSV tables, figures, and metadata. Builds check the released artifact hashes and consistent manuscript provenance without requiring the private source. TeX and related LaTeX source formats are ignored to prevent accidental reintroduction.

The owner authorized removing TeX files from Git history before changing repository visibility. A private local backup preserves the original history; it is not part of the public repository or website. Public Pages deployment remains an explicit manual operation.
