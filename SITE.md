# Website: data model, updates, and publication

The project website is buildless HTML, CSS, and JavaScript in `docs/`. GitHub Pages can serve it directly. The static files also support a private hosted review. The site never calls a language model, fits a predictor, or computes missing scientific measurements in the browser.

## What is an observation?

| Field / measure | Granularity | Coverage and interpretation |
|---|---|---|
| `query_index`, excerpt key `q-N` | Evaluation excerpt identifier | Join keys, never intrinsic-dimension values or predictors. |
| Excerpt text and source | Excerpt | An excerpt can contain multiple parser-detected sentences. |
| 46 linguistic features | Aggregated excerpt profile | 43 Profiling-UD descriptors and three shared Pythia-tokenizer frequency proxies. Definitions specify denominators. |
| ESS, MLE, local FCI | Query representation and its reference neighbourhood | One last-non-padding-token representation per excerpt/model/layer; main ID uses k=1,000 and 15,000 disjoint references. These are not per-token scores. |
| Percentiles | Distribution of available evaluation query estimates | Average rank / available population × 100, separately by model, layer, and estimator; calculated before filtering. |
| Radius and mean distance | Selected query neighbourhood | Unnormalised Euclidean representation distances; magnitude depends on model and layer. |
| Relative radius | Selected query neighbourhood | Radius / median query-to-reference distance. |
| Source fractions, entropy, lexical cosine | Composition of a query neighbourhood | Fractions, normalised entropy, or TF-IDF similarity; not direct word-level or semantic labels. |
| Paper figure means / standard deviations | Dataset or checkpoint summary | Some summaries cover all 2,000 queries; do not assign them to an individual excerpt. |

The geometric targets and text browser contain all 2,000 original queries. Six have no released linguistic profile, and their 46 feature values remain null. A locality audit sampled 500 queries; all 500 texts and their recorded diagnostics are included. `data/explorer/neighbourhood_alignment.json` records verification of original source indices and exact text digests in every model/layer setting. No proximity or source-name heuristic was used to join these rows.

The locality controls select one of five k values and either a cumulative neighbourhood or a shell. Shells are ranks 1–100, 101–500, 501–1,000, 1,001–2,000, and 2,001–3,000. Their sizes are 100, 400, 500, 1,000, and 1,000, respectively. They do not change the main ID estimates’ k=1,000.

## Missing data and reconstruction boundaries

- Six geometric evaluation queries have no aligned linguistic profile. Their original texts and geometry are included in the browser; the feature panel explains the missing profile.
- Local FCI for Pythia, early layer 2, query 502 is missing. Its percentile denominator is 1,999; other main settings have 2,000 available measurements.
- Locality diagnostics are absent outside the recorded 500-query audit. The browser does not approximate or impute them.
- Linguistic missing values remain missing in the browser. Fold-local median imputation belongs to prediction experiments only.
- Token-level geometric scores and word-aligned annotations are not supplied. Neighbour texts, hidden states, and raw reference arrays are not packaged.
- Checkpoint measurements are available in the repository and paper results. The interactive per-excerpt comparison currently covers the nine main model/layer settings.
- No DOI or arXiv URL was provided. The supplied PDF predates the current TeX snapshot; the site identifies that version difference. The website provides the PDF; manuscript sources remain in the repository.
- The GitHub repository URL is verified and recorded in `configs/site.json`. Website downloads use PDF, CSV, and JSON. ZIP archives and TeX files are neither generated nor served by the site.

## Progressive loading

`build_explorer.py` verifies UTF-8 SHA-256 text joins and builds:

1. `explorer-index.js`: texts, source labels, feature vectors, definitions, and data-file manifests. Search normalises text once and uses a debounced local index.
2. Nine geometry files, loaded by model/layer. The initial view requests one; paired plots request two; the expanded all-model table requests the remaining settings.
3. Nine locality files, loaded on demand when plotting a locality measure, opening its definitions/values, or exporting a CSV.
4. `explorer.json`: the portable, full-precision main excerpt/feature/ID download. Full locality and checkpoint data remain in the repository’s numeric tables.

There is no all-layer or locality-data fetch at first paint. Loaded files are cached in the page. Load failures produce a retry control without fabricated values. Static script chunks also work from extracted local files.

## Display and export

The interface rounds for reading. Full-precision CSV exports include text hashes, explicit model/layer, all three raw ID estimators and percentiles, diagnostic k and interval, available locality measures, and all raw feature values. A paired plot adds the comparison setting and measurements. Missing values export as empty cells and stay null in JSON.

Lexical density is the one feature stored as a 0–1 fraction; it is displayed as a percentage. Other percentage features are stored on a 0–100 scale. Same-source and zero-distance fractions are displayed as percentages; same-source excess is shown in percentage points. Downloads retain original stored units.

## Rebuild after changing data

```bash
make PYTHON=.venv/bin/python site
make PYTHON=.venv/bin/python check
```

`make site` needs only released files inside this repository. `build_site_assets.py` prepares the supplied paper PDF, figure/result downloads, and a static source browser. It removes legacy ZIP and TeX assets from the website output. The source browser omits ZIP and TeX entries; the complete canonical sources remain in the repository.

When importing a new manuscript snapshot, put its figures in the original source tree, update `FIGURES` in `scripts/import_current_paper.py` if labels change, and run:

```bash
python3 scripts/import_current_paper.py \
  --manuscript /path/to/manuscript.tex \
  --source-root /path/to/experiment-project
```

Copy that same TeX snapshot to `paper/manuscript/manuscript.tex` and update the title, abstract, author list, hashes, and version note in `configs/site.json`. Replace the supplied PDF only when a suitable new PDF exists. Update `codeUrl` only with a real, verified repository URL; leave it null otherwise.

For changed numeric results, update the released Parquet files, their original manifests, and their provenance before rebuilding. A new text cohort must be imported and hash-verified using `build_explorer.py --source-root`. If locality cohorts change, rerun `import_neighbourhood_alignment.py --source-root` against the original query/source mappings. Query counts, settings, and missingness are deliberately asserted for this release; update these documented assertions when changing the experiment design.

Before committing:

```bash
make site
make check
# Optional: real Chrome DevTools endpoint and websocket-client required.
python3 scripts/check_browser.py --screenshots /tmp/local-geometry-preview
```

Commit the changed source, manifests, paper snapshot, and generated JS/JSON data chunks. Public Pages publication is paused. The workflow does not run on push, and its manual public opt-in requires a public repository. The private preview uses owner-only Sites permissions. See [PUBLISHING.md](PUBLISHING.md) for access and future publication.

## Accessibility and visual conventions

The layout follows a compact academic page with readable text, a limited blue palette from the paper figures, and no promotional hero or decorative card grid. Orange marks the selected excerpt; purple marks a pinned comparison. Excerpt keys, labels, and text readouts supplement colour. Feature-family accents follow the manuscript’s four family colours.

Every plot has an equivalent excerpt list. The selected SVG point is the only point in the Tab sequence; Left/Right and Home/End move through points, and Enter opens the corresponding text. A text selection updates the plot; “Locate on plot” moves focus to its point. Tables scroll inside their own regions on mobile. Reduced-motion preferences are respected, and no repeated animations are used.
