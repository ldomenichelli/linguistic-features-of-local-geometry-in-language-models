#!/usr/bin/env python3
"""Import displayed results from a supplied manuscript without rerunning experiments.

CSV grids preserve the displayed table structure. Manuscript sources stay outside
the repository. Higher-precision historical CSVs remain in paper/.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIGURES = {
    "fig:pipeline": "poster/figures/pointwise_excerpt_pipeline.pdf",
    "fig:ess_profile": "outputs/three_model_k1000_median_pointwise_id_across_layers/three_model_k1000_ess_mean_sd_pointwise_id_across_layers.pdf",
    "fig:reference_plateau": "outputs/reference_size_plateau_ess/ess_reference_size_plateau_eval_seen_k50_100_500_1000_layers12_no_title.png",
    "fig:ess_reference_stability": "outputs_6.9/essential_experiments/pythia69b_ess_reference_resampling_l16_k1000_curve/corrected_figure3_ess_reference_stability.pdf",
    "fig:estimators": "gaussian_cloud_calibration_no_title.pdf",
    "fig:scores_on_layers": "pointwise_id_layers_ess_fci_mle.pdf",
    "fig:ess-checkpoints": "outputs_6.9_checkpoints/pythia_checkpoint_k1000_selected_layers/ess_model_comparison/pythia_apertus_checkpoint_ess_layers2_16_31_mean_sd.pdf",
}


def sha(path: Path): return hashlib.sha256(path.read_bytes()).hexdigest()


def argument(s: str, start: int):
    start = s.index("{", start); depth = 1; i = start + 1
    while depth:
        slash = 0; j = i - 1
        while j >= 0 and s[j] == "\\": slash += 1; j -= 1
        if not slash % 2:
            if s[i] == "{": depth += 1
            elif s[i] == "}": depth -= 1
        i += 1
    return s[start + 1:i - 1], i


def plain(s: str):
    s = re.sub(r"(?<!\\)%[^\n]*", "", s)
    s = s.replace(r"\{", "__LITERAL_OPEN_BRACE__").replace(r"\}", "__LITERAL_CLOSE_BRACE__")
    # Keep the text argument of spanning cells and colour keys.
    for command, count, keep in [("multicolumn", 3, 2), ("multirow", 3, 2), ("familykey", 2, 1)]:
        pattern = re.compile(r"\\" + command + r"(?:\[[^\]]*\])?\s*\{")
        while (match := pattern.search(s)):
            pos = match.end() - 1; args = []
            for _ in range(count):
                value, pos = argument(s, pos); args.append(value)
            s = s[:match.start()] + args[keep] + s[pos:]
    s = re.sub(r"\\(?:rowcolor|cellcolor|hspace|vspace)\s*\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:toprule|midrule|bottomrule|addlinespace|cmidrule)(?:\([^)]*\))?(?:\[[^\]]*\])?(?:\{[\d-]+\})?", " ", s)
    s = re.sub(r"\\(?:smallskip|medskip|noindent)\b", " ", s)
    for old, new in [(r"\_", "_"), (r"\%", "%"), (r"\&", "&"), (r"\pm", "±"), (r"\Delta", "Δ"), (r"\sigma", "σ"), (r"\rho", "ρ"), (r"\uparrow", "↑"), (r"\downarrow", "↓"), (r"\rightarrow", "→"), (r"\geq", "≥"), (r"\leq", "≤"), (r"\times", "×")]: s = s.replace(old, new)
    s = s.replace(r"\(", "").replace(r"\)", "").replace("$", "")
    for _ in range(12):
        out = re.sub(r"\\[A-Za-z]+\*?\s*\{([^{}]*)\}", r"\1", s)
        if out == s: break
        s = out
    s = re.sub(r"\\(?:newline|linebreak)\b|\\\\(?:\[[^\]]*\])?", " ", s)
    s = re.sub(r"\\[A-Za-z]+\*?", " ", s)
    s = re.sub(r"\\[,;! ]", " ", s)
    s = s.replace("{", "").replace("}", "").replace("``", '“').replace("''", '”').replace("---", "—").replace("--", "–")
    s = s.replace("__LITERAL_OPEN_BRACE__", "{").replace("__LITERAL_CLOSE_BRACE__", "}")
    s = s.replace("R^2", "R²")
    return re.sub(r"\s+", " ", s).strip()


def split_top(s: str, rows: bool):
    values = []; start = 0; depth = 0; i = 0
    while i < len(s):
        if s[i] == "\\":
            if rows and depth == 0 and s[i:i + 2] == "\\\\":
                values.append(s[start:i]); i += 2
                if i < len(s) and s[i] == "[": i = s.index("]", i) + 1
                start = i; continue
            i += 2; continue
        if s[i] == "{": depth += 1
        elif s[i] == "}": depth -= 1
        elif not rows and s[i] == "&" and depth == 0:
            values.append(s[start:i]); start = i + 1
        i += 1
    values.append(s[start:])
    return values


def table_rows(block: str, kind: str):
    pos = block.index("}") + 1
    for _ in range(2 if kind in {"tabularx", "tabular*"} else 1): _, pos = argument(block, pos)
    body = block[pos:block.rindex(r"\end{")]
    body = re.sub(r"\\featgroup\{([^}]+)\}\{([^}]+)\}", lambda m: m[1] + " (" + m[2] + " predictors) \\\\ ", body)
    rows = []; spans = []; pending = {}
    for raw in split_top(body, True):
        cells = split_top(raw, False)
        if not any(plain(cell) for cell in cells): continue
        row = []; sizes = []; column = 0; new_pending = {}
        for cell in cells:
            width_match = re.search(r"\\multicolumn\{(\d+)\}", cell)
            width = int(width_match[1]) if width_match else 1
            value = plain(cell)
            if not value and column in pending: value = pending[column][1]
            height_match = re.search(r"\\multirow\{(\d+)\}", cell)
            if height_match: new_pending[column] = (int(height_match[1]) - 1, value)
            row.append(value); sizes.append(width); column += width
        pending = {col: (count - 1, value) for col, (count, value) in pending.items() if count > 1}
        pending.update(new_pending)
        rows.append(row); spans.append(sizes)
    return rows, spans



def import_results(manuscript: Path, source_root: Path):
    text = manuscript.read_text(); dest = ROOT / "paper/current"
    (dest / "tables").mkdir(parents=True, exist_ok=True); (dest / "figures").mkdir(exist_ok=True)
    (ROOT / "docs/results/current").mkdir(parents=True, exist_ok=True)
    tables = []; figures = []
    for match in re.finditer(r"\\begin\{(tabularx|tabular\*?)\}.*?\\end\{\1\}", text, re.S):
        tail = text[match.end():]
        cap = re.search(r"\\caption(?:of\{table\})?\s*\{", tail)
        assert cap
        caption, end = argument(tail, cap.end() - 1)
        label = re.search(r"\\label\{([^}]+)\}", tail[end:])[1]
        assert label.startswith("tab:")
        slug = label[4:].replace("_", "-")
        rows, spans = table_rows(match[0], match[1]); width = max(map(sum, spans))
        csv_path = dest / "tables" / (slug + ".csv")
        with csv_path.open("w", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n"); writer.writerow(["cell_" + str(i + 1) for i in range(width)])
            for row, sizes in zip(rows, spans):
                expanded = [value for cell, size in zip(row, sizes) for value in [cell] + [""] * (size - 1)]
                writer.writerow(expanded + [""] * (width - len(expanded)))
        shutil.copy2(csv_path, ROOT / "docs/results/current" / csv_path.name)
        tables.append({"number": len(tables) + 1, "label": label, "title": plain(caption).split(". ")[0] + ".", "caption": plain(caption), "rows": rows, "colspans": spans, "csv": "results/current/" + csv_path.name, "sha256": sha(csv_path)})
    for match in re.finditer(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", text, re.S):
        label = re.search(r"\\label\{([^}]+)\}", match[0])[1]
        cap = re.search(r"\\caption\s*\{", match[0]); caption, _ = argument(match[0], cap.end() - 1)
        original = source_root / FIGURES[label]; assert original.is_file()
        slug = label[4:].replace("_", "-"); paths = {}
        for suffix in [".png", ".pdf"]:
            source = original.with_suffix(suffix)
            if not source.is_file(): continue
            target = dest / "figures" / (slug + suffix); shutil.copy2(source, target)
            web = ROOT / "docs/results/figures" / target.name; web.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(target, web)
            paths[suffix[1:]] = "results/figures/" + target.name
        assert "png" in paths
        figures.append({"number": len(figures) + 1, "label": label, "caption": plain(caption), "source": FIGURES[label], "sourceSha256": sha(original), **paths})
    assert len(tables) == 16 and len(figures) == 7
    archive = []
    for folder in [ROOT / "paper/tables", ROOT / "paper/figures"]:
        for source in sorted(folder.iterdir()):
            if source.suffix not in {".csv", ".png", ".pdf"}: continue
            web = ROOT / "docs/results/archive" / source.name; web.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, web)
            archive.append({"name": source.name, "url": "results/archive/" + source.name, "type": source.suffix[1:], "sha256": sha(source)})
    payload = {"schemaVersion": 1, "manuscriptSha256": sha(manuscript), "tables": tables, "figures": figures, "archive": archive, "tableFormat": "CSV cell grids transcribed from the current manuscript. Manuscript sources are not included. Earlier full-precision tidy tables and additional analyses are separately retained in the archive."}
    (dest / "manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "docs/assets/results-data.js").write_text("window.RESULTS_DATA=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";\n")
    index = ["# Current manuscript results", "", "Figures and tables from the current paper. [Earlier results and supporting analyses](../TABLES.md) are available separately.", "", "## Tables", ""]
    for t in tables: index += [f"- **Table {t['number']}** — {t['title']} [CSV](tables/{t['csv'].split('/')[-1]})"]
    index += ["", "## Figures", ""]
    for f in figures: index += [f"- **Figure {f['number']}** — {f['caption']} [PNG](figures/{f['png'].split('/')[-1]})" + (f" · [PDF](figures/{f['pdf'].split('/')[-1]})" if f.get("pdf") else "")]
    (dest / "README.md").write_text("\n".join(index) + "\n")
    print(f"Imported {len(tables)} current tables, {len(figures)} current figures and {len(archive)} archived artifacts.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--manuscript", type=Path, required=True); p.add_argument("--source-root", type=Path, required=True)
    args = p.parse_args(); import_results(args.manuscript, args.source_root)
