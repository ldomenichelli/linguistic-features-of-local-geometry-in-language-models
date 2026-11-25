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
    bootstrap=read_js(DOCS / 'assets/explorer-index.js', 'EXPLORER_INDEX')
    assert bootstrap['excerpts']==[{k:v for k,v in e.items() if k!='scores'} for e in payload['excerpts']]
    assert bootstrap['features']==payload['features']
    assert bootstrap['meta']==payload['meta']
    features = pd.read_parquet(ROOT / 'data/derived/features.parquet').set_index('query_index').sort_index()
    targets = pd.read_parquet(ROOT / 'data/derived/main_targets.parquet')
    excerpts = payload['excerpts']
    assert len(excerpts) == 2000 and len(features) == 1994
    assert len({e['id'] for e in excerpts}) == len(excerpts)
    assert set(features.index) <= set(e['queryIndex'] for e in excerpts)
    proof=json.loads((ROOT/'data/explorer/excerpt_alignment.json').read_text())
    assert proof['excerpts_sha256']==sha(ROOT/'data/explorer/excerpts.json')
    assert proof['queries']==2000 and len(proof['verified_settings'])==9
    assert proof['missing_profile_queries']==[95,321,421,704,1318,1479]
    columns = [f['id'] for f in payload['features']]
    assert len(columns) == 46 and set(columns) == set(features.columns) - {'text_sha256'}
    for name, rel in [('features','data/derived/features.parquet'), ('targets','data/derived/main_targets.parquet'), ('excerpts','data/explorer/excerpts.json')]:
        assert payload['meta']['sources'][name] == sha(ROOT / rel)
    for e in excerpts:
        q = e['queryIndex']
        assert e['id'] == f'q-{q}' and e['source'] and e['text']
        assert hashlib.sha256(e['text'].encode()).hexdigest() == e['textSha256']
        assert e['featuresAvailable'] == (q in features.index)
        if q in features.index:
            assert e['textSha256'] == features.loc[q, 'text_sha256']
            np.testing.assert_allclose(np.array(e['features'], dtype=float), features.loc[q, columns].to_numpy(dtype=float), rtol=0, atol=0, equal_nan=True)
        else:
            assert q in proof['missing_profile_queries'] and e['features']==[None]*46
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
        assert 'tex' not in t and t['label'].startswith('tab:')
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



def read_chunk(path, namespace, key):
    source=path.read_text();prefix=f'window.{namespace}[{json.dumps(key)}]='
    assert prefix in source and source.endswith(';\n'),path
    return json.loads(source.split(prefix,1)[1][:-2])


def check_progressive():
    bootstrap=read_js(DOCS/'assets/explorer-index.js','EXPLORER_INDEX')
    full=json.loads((DOCS/'assets/explorer.json').read_text())
    assert len(bootstrap['geometryManifest'])==9 and len(bootstrap['neighbourhoodManifest'])==9
    local=pd.read_parquet(ROOT/'data/derived/neighbourhood_locality_metrics.parquet')
    aligned=bootstrap['neighbourhoodCoverage']['positions']
    proof=json.loads((ROOT/'data/explorer/neighbourhood_alignment.json').read_text())
    assert aligned==proof['aligned_positions'] and len(aligned)==500
    assert proof['locality_sha256']==sha(ROOT/'data/derived/neighbourhood_locality_metrics.parquet')
    assert bootstrap['neighbourhoodCoverage']['sha256']==proof['locality_sha256']
    count=0
    for m in bootstrap['models']:
        for l in m['layers']:
            key=f"{m['id']}.{l['id']}"
            entry=bootstrap['geometryManifest'][key];path=safe_download(entry['path']);assert sha(path)==entry['sha256']
            chunk=read_chunk(path,'EXPLORER_GEOMETRY',key)
            assert len(chunk['records'])==2000
            for e in full['excerpts']:
                expected=[v for est in ['ess','mle','fci'] for v in e['scores'][m['id']][l['id']][est]]
                assert chunk['records'][str(e['queryIndex'])]==expected
            entry=bootstrap['neighbourhoodManifest'][key];path=safe_download(entry['path']);assert sha(path)==entry['sha256']
            chunk=read_chunk(path,'EXPLORER_NEIGHBOURHOODS',key)
            frame=pd.DataFrame(chunk['rows'],columns=chunk['columns']).rename(columns={'query_index':'query_position'})
            expected=local.loc[(local.model==m['label'])&(local.layer==l['number'])&local.query_position.isin(aligned),frame.columns].sort_values(['query_position','kind','k']).reset_index(drop=True)
            pd.testing.assert_frame_equal(frame,expected,check_dtype=False,check_exact=True)
            count+=len(frame)
    assert count==45000
    return {'progressive_geometry_files':9,'progressive_locality_files':9,'verified_locality_rows':count}


def check_downloads():
    manifest=json.loads((DOCS/'assets/downloads-manifest.json').read_text())
    assert set(manifest)=={'supplied-paper.pdf'}
    for name,metadata in manifest.items():
        path=safe_download('downloads/'+name)
        assert sha(path)==metadata['sha256'] and path.stat().st_size==metadata['bytes']
    assert not [p for p in DOCS.rglob('*') if p.is_file() and p.suffix in {'.zip','.tex'}]
    paper=json.loads((ROOT/'configs/site.json').read_text())
    results=json.loads((ROOT/'paper/current/manifest.json').read_text())
    assert paper['manuscriptSha256']==results['manuscriptSha256']
    assert re.fullmatch(r'[0-9a-f]{64}', paper['manuscriptSha256'])
    assert not [p for p in (ROOT/'paper').rglob('*') if p.suffix.lower() in {'.tex','.bib','.sty','.cls'}]
    assert paper['paperPdfSha256']==sha(DOCS/'downloads/supplied-paper.pdf')


def main():
    report={**check_data(), **check_results(), **check_progressive()};check_links();check_downloads()
    print(json.dumps({'status':'passed',**report},indent=2))


if __name__=='__main__':main()
