PYTHON ?= python3
DATA_DIR ?= data/derived
PAPER_DATA_DIR ?= data/paper
OUTPUT_DIR ?= results/generated
PAPER_OUTPUT_DIR ?= results/paper
REFERENCE_DIR ?= results/reference

.PHONY: help paper check-paper check-experiments analysis analysis-extended verify test anonymity check site check-site serve browser-test site-assets

help:
	@echo "Available targets:"
	@echo "  paper              Rebuild numbered paper and geometry/control artifacts"
	@echo "  check-paper        Check the rebuilt paper artifact set and table values"
	@echo "  check-experiments  Check archived geometry/control results and artifacts"
	@echo "  analysis           Refit the main ESS and checkpoint models"
	@echo "  analysis-extended  Add MLE, FCI, and every retained feature ablation"
	@echo "  verify             Compare downstream outputs with reference results"
	@echo "  test               Run the lightweight test suite"
	@echo "  anonymity          Scan files and Git metadata for identity leaks"
	@echo "  check              Run artifact checks, tests, and site checks"
	@echo "  site               Rebuild and validate interactive explorer data"
	@echo "  serve              Preview committed site on http://localhost:8765"
	@echo ""
	@echo "Overrides: PYTHON, DATA_DIR, PAPER_DATA_DIR, OUTPUT_DIR, PAPER_OUTPUT_DIR, REFERENCE_DIR"

paper:
	$(PYTHON) scripts/build_paper_artifacts.py \
		--derived-dir $(DATA_DIR) \
		--paper-data-dir $(PAPER_DATA_DIR) \
		--output-dir $(PAPER_OUTPUT_DIR)

check-paper:
	$(PYTHON) scripts/check_paper_artifacts.py \
		--committed-dir paper \
		--generated-dir $(PAPER_OUTPUT_DIR) \
		--derived-dir $(DATA_DIR)

analysis:
	$(PYTHON) scripts/reproduce_analysis.py \
		--data-dir $(DATA_DIR) \
		--output-dir $(OUTPUT_DIR)

analysis-extended:
	$(PYTHON) scripts/reproduce_analysis.py \
		--data-dir $(DATA_DIR) \
		--output-dir $(OUTPUT_DIR) \
		--extended

verify:
	$(PYTHON) scripts/verify_reproduction.py \
		--generated-dir $(OUTPUT_DIR) \
		--reference-dir $(REFERENCE_DIR)

test:
	$(PYTHON) -m unittest discover -s tests -v

anonymity:
	$(PYTHON) scripts/check_anonymity.py

check-experiments:
	$(PYTHON) scripts/check_experiment_results.py

check: paper check-paper check-experiments test check-site

# The current manuscript snapshot is immutable; this regenerates browser data.
site:
	$(PYTHON) scripts/build_explorer.py
	$(PYTHON) scripts/build_site_assets.py
	$(PYTHON) scripts/check_site.py

check-site: site-assets
	$(PYTHON) scripts/check_site.py

serve:
	$(PYTHON) -m http.server 8765 --directory docs

# Start make serve and a Chrome DevTools endpoint before running this optional check.
browser-test:
	$(PYTHON) scripts/check_browser.py --url http://127.0.0.1:8765/

site-assets:
	$(PYTHON) scripts/build_site_assets.py
