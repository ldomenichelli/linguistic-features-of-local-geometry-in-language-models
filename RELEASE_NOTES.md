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

Replaced the presentation-led page with a compact paper page: real abstract and authors, central figures, compact tables, actual manuscript/code/data downloads, and a source browser. The supplied PDF is identified as an earlier version; the current TeX snapshot is separately provided. No unverified GitHub, DOI, or arXiv link is displayed.

The explorer now loads geometry progressively by model/layer and locality diagnostics on request. It supports paired model/layer plots, a nine-setting per-excerpt measurement table, feature-value filtering, feature-definition search, full-precision multi-estimator CSV export, and keyboard-operable plot points.

Verified the original locality query/source joins and text digests across nine settings: 498 aligned excerpts, five neighbourhood sizes, cumulative/shell intervals, and all 16 retained diagnostics. All 44,820 exported locality rows match the canonical Parquet data exactly. `make check` passes 17 tests plus artifact, provenance, percentile, download, and progressive-chunk checks. Real-browser checks pass with no JavaScript exceptions or failed requests, including source-precision CSV values, missing FCI handling, model/layer comparison, native keyboard navigation, retry after a blocked data file, and mobile/tablet layout.

See [SITE.md](SITE.md) for measure granularity, source units, missing observations, progressive loading, accessibility, and update instructions.
