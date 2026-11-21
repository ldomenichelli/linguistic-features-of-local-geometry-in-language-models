#!/usr/bin/env python3
"""Validate every released browser join, percentile, and downloadable artifact."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_js(path, name):
    source = path.read_text()
    prefix = f'window.{name}='
    assert source.startswith(prefix) and source.endswith(';\n'), path
    return json.loads(source[len(prefix):-2])


def check_data():
    payload = json.loads((DOCS / 'assets/explorer.json').read_text())
    assert payload == read_js(DOCS / 'assets/explorer-data.js', 'EXPLORER_DATA')
    features = pd.read_parquet(ROOT / 'data/derived/features.parquet').set_index('query_index').sort_index()
    targets = pd.read_parquet(ROOT / 'data/derived/main_targets.parquet')
    excerpts = payload['excerpts']
    assert len(excerpts) == len(features) == 1994
    assert len({e['id'] for e in excerpts}) == len(excerpts)
    assert set(e['queryIndex'] for e in excerpts) == set(features.index)
    columns = [f['id'] for f in payload['features']]
    assert len(columns) == 46 and set(columns) == set(features.columns) - {'text_sha256'}
    for name, rel in [('features','data/derived/features.parquet'), ('targets','data/derived/main_targets.parquet'), ('excerpts','data/explorer/excerpts.json')]:
        assert payload['meta']['sources'][name] == sha(ROOT / rel)
    for e in excerpts:
        q = e['queryIndex']
        assert e['id'] == f'q-{q}' and e['source'] and e['text']
        assert hashlib.sha256(e['text'].encode()).hexdigest() == features.loc[q, 'text_sha256']
        np.testing.assert_allclose(np.array(e['features'], dtype=float), features.loc[q, columns].to_numpy(dtype=float), rtol=0, atol=0, equal_nan=True)
    ids = [e['queryIndex'] for e in excerpts]
    missing = []
    for model in payload['models']:
        for layer in model['layers']:
            rows = targets.loc[(targets.model_key == model['id']) & (targets.layer == layer['number'])].set_index('query_index').reindex(ids)
            for estimator, column in [('ess','pointwise_ess'),('mle','pointwise_mle'),('fci','pointwise_fci_id')]:
                raw = rows[column].to_numpy(dtype=float)
                valid = np.isfinite(raw) & (raw > 0)
                scores = np.array([e['scores'][model['id']][layer['id']][estimator] for e in excerpts], dtype=float)
                assert payload['meta']['validPopulation'][f"{model['id']}.{layer['id']}.{estimator}"] == int(valid.sum())
                np.testing.assert_allclose(scores[valid,0], raw[valid], rtol=0, atol=0)
                # Independent rank implementation catches accidental subset rankings or tie errors.
                expected = rankdata(raw[valid], method='average') / valid.sum() * 100
                np.testing.assert_allclose(scores[valid,1], expected, rtol=0, atol=1e-12)
                assert np.isnan(scores[~valid]).all()
                missing.extend((model['id'],layer['id'],estimator,ids[i]) for i in np.where(~valid)[0])
    assert missing == [('pythia','early','fci',502)], missing
    assert sum(e['paperExample'] for e in excerpts) == 7
    units = {f['id']: f['unit'] for f in payload['features']}
    assert units['lexical_density'] == 'ratio' and units['upos_dist_NOUN'] == 'percent'
    return {'excerpts':len(excerpts), 'features':len(columns), 'settings':27, 'missing_measurements':len(missing)}


def safe_download(relative):
    path = (DOCS / relative).resolve()
    assert path.is_relative_to(DOCS.resolve()) and path.is_file() and path.stat().st_size, relative
    return path


def check_results():
    manifest = json.loads((ROOT / 'paper/current/manifest.json').read_text())
    assert manifest == read_js(DOCS / 'assets/results-data.js', 'RESULTS_DATA')
    assert len(manifest['tables']) == 16 and len(manifest['figures']) == 7
    for t in manifest['tables']:
        path = safe_download(t['csv']); assert sha(path) == t['sha256']
        assert path.read_bytes() == (ROOT/'paper/current/tables'/path.name).read_bytes()
        with path.open(newline='') as stream:
            grid = list(csv.reader(stream))
        width = len(grid[0]); assert len(grid) == len(t['rows']) + 1
        for actual, cells, sizes in zip(grid[1:], t['rows'], t['colspans']):
            expanded = [value for cell, size in zip(cells, sizes) for value in [cell] + ['']*(size-1)]
            assert actual == expanded + [''] * (width - len(expanded))
        tex = safe_download(t['tex'])
        assert tex.read_bytes() == (ROOT/'paper/current/tables'/tex.name).read_bytes()
        assert f"\\label{{{t['label']}}}" in tex.read_text()
        assert not any('@ c' in cell or '\\textbf' in cell for row in t['rows'] for cell in row)
    for f in manifest['figures']:
        for extension in ['png','pdf']:
            if extension not in f: continue
            path = safe_download(f[extension])
            assert path.read_bytes() == (ROOT/'paper/current/figures'/path.name).read_bytes()
            assert path.read_bytes().startswith(b'%PDF-' if extension=='pdf' else b'\x89PNG\r\n\x1a\n')
        original_extension = Path(f['source']).suffix[1:]
        assert sha(safe_download(f[original_extension])) == f['sourceSha256']
    for a in manifest['archive']:
        path = safe_download(a['url']); assert sha(path) == a['sha256']
        original = ROOT/'paper'/('tables' if a['type']=='csv' else 'figures')/a['name']
        assert path.read_bytes() == original.read_bytes()
    return {'current_tables':len(manifest['tables']), 'current_figures':len(manifest['figures']), 'archive_files':len(manifest['archive'])}


class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.paths=[]; self.ids=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        for name in ['href','src']:
            if name in attrs:self.paths.append(attrs[name])


def check_links():
    parser=Links(); parser.feed((DOCS/'index.html').read_text())
    assert len(parser.ids)==len(set(parser.ids))
    for url in parser.paths:
        parsed=urlsplit(url)
        if parsed.scheme or parsed.netloc:continue
        if parsed.path: safe_download(unquote(parsed.path))
        elif parsed.fragment: assert parsed.fragment in parser.ids, url
    css=(DOCS/'assets/style.css').read_text()
    for path in re.findall(r'url\([\"\']?([^\)\"\']+)',css):
        if not urlsplit(path).scheme: assert (DOCS/'assets'/path).is_file()


def main():
    report={**check_data(), **check_results()};check_links()
    print(json.dumps({'status':'passed',**report},indent=2))


if __name__=='__main__':main()
