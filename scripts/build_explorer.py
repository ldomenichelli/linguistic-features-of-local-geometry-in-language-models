#!/usr/bin/env python3
"""Build the static explorer from released numeric data and verified excerpts."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from explorer_metadata import NEIGHBOURHOOD_METRICS

ROOT = Path(__file__).resolve().parents[1]
MODEL_LAYERS = {"pythia": [2, 16, 31], "qwen": [2, 14, 27], "apertus": [2, 16, 31]}
NAMES = {"pythia": "Pythia-6.9B", "qwen": "Qwen2.5-7B", "apertus": "Apertus-8B"}
TARGETS = {"ess": "pointwise_ess", "mle": "pointwise_mle", "fci": "pointwise_fci_id"}
DEPTHS = ["early", "intermediate", "late"]
LABELS = {
    "n_sentences": "Sentences", "n_tokens": "Word tokens", "tokens_per_sent": "Words per sentence",
    "char_per_tok": "Characters per word", "avg_links_len": "Mean dependency length",
    "max_links_len": "Maximum dependency length", "avg_max_depth": "Mean tree depth",
    "avg_prepositional_chain_len": "Prepositional chain depth", "avg_subordinate_chain_len": "Subordinate chain depth",
    "avg_token_per_clause": "Words per clause", "avg_verb_edges": "Dependencies per verb",
    "subordinate_proposition_dist": "Subordinate clauses", "verbal_root_perc": "Sentences with verbal roots",
    "subj_pre": "Subjects before verbs", "obj_post": "Objects after verbs", "subordinate_post": "Subordinate clauses after heads",
    "lexical_density": "Lexical density", "aux_mood_dist_Ind": "Indicative auxiliaries",
    "aux_num_pers_dist_Sing+3": "Third-person singular auxiliaries", "aux_tense_dist_Pres": "Present-tense auxiliaries",
    "verbs_form_dist_Inf": "Infinitive verbs", "verbs_form_dist_Part": "Participle verbs",
    "verbs_mood_dist_Ind": "Indicative verbs", "verbs_tense_dist_Past": "Past-tense verbs", "verbs_tense_dist_Pres": "Present-tense verbs",
    "median_frequency_class": "Median token frequency class", "max_frequency_class": "Rarest token frequency class",
    "min_frequency_class": "Most frequent token frequency class",
}
POS = {"ADJ": "Adjectives", "ADP": "Adpositions", "ADV": "Adverbs", "AUX": "Auxiliaries", "CCONJ": "Coordinating conjunctions", "DET": "Determiners", "NOUN": "Common nouns", "NUM": "Numerals", "PART": "Particles", "PRON": "Pronouns", "PROPN": "Proper nouns", "PUNCT": "Punctuation", "VERB": "Verbs"}
DEPS = {"compound": "Compound dependencies", "nmod": "Nominal modifiers", "nsubj": "Nominal subjects", "obj": "Core objects", "obl": "Oblique nominals"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value):
    return float(value) if pd.notna(value) and math.isfinite(float(value)) else None


def import_excerpts(source: Path, features: pd.DataFrame) -> None:
    profile = pd.read_csv(source / "outputs/eval_known_feature60_plus_frequency_for_predict.tsv", sep="\t")
    profile = profile.rename(columns={"recovered_row_index": "query_index", "recovered_text": "text"}).set_index("query_index")
    targets = pd.read_parquet(source / "outputs_6.9/seen_unseen_pythia69b_mle_ess_fci_k1000_ref15000_layers2_16_31_sentence_level/eval_known_layer16_k1000_ref15000_sentence_level.parquet").set_index("query_index")
    metadata = pd.read_csv(source / "outputs_6.9/local_seen_unseen_pythia69b_deduped/seen_metadata.csv").set_index("example_index")
    records = []
    for row in features.itertuples(index=False):
        text = str(profile.loc[row.query_index, "text"])
        assert hashlib.sha256(text.encode()).hexdigest() == row.text_sha256, row.query_index
        target = targets.loc[row.query_index]
        assert target["text"] == text
        meta = metadata.loc[target["query_source_index"]]
        assert meta["text"] == text and meta["line_index"] == target["line_index"]
        records.append({"query_index": int(row.query_index), "text": text, "source": str(meta["pile_set_name"]) if pd.notna(meta["pile_set_name"]) else "The Pile", "text_sha256": row.text_sha256})
    output = ROOT / "data/explorer/excerpts.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")) + "\n")



def write_js(path, namespace, key, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded=json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).replace("</", "<\\/")
    if key is None: source=f"window.{namespace}={encoded};\n"
    else: source=f"window.{namespace}=window.{namespace}||{{}};window.{namespace}[{json.dumps(key)}]={encoded};\n"
    path.write_text(source)


def build_progressive(payload, out):
    alignment=json.loads((ROOT/'data/explorer/neighbourhood_alignment.json').read_text())
    locality_path=ROOT/'data/derived/neighbourhood_locality_metrics.parquet'
    assert digest(locality_path)==alignment['locality_sha256']
    locality=pd.read_parquet(locality_path)
    assert sorted(locality.query_position.unique())==alignment['positions']
    assert all(v['aligned_excerpts']==498 for v in alignment['verified_settings'])
    manifest={}; local_manifest={}
    for model in payload['models']:
        for layer in model['layers']:
            key=f"{model['id']}.{layer['id']}"
            records={str(e['queryIndex']):[v for estimator in TARGETS for v in e['scores'][model['id']][layer['id']][estimator]] for e in payload['excerpts']}
            path=out/'geometry'/f"{model['id']}-{layer['id']}.js"
            write_js(path,'EXPLORER_GEOMETRY',key,{'records':records})
            manifest[key]={'path':f'assets/geometry/{path.name}','sha256':digest(path),'bytes':path.stat().st_size}
            group=locality.loc[(locality.model==model['label'])&(locality.layer==layer['number'])]
            rows=[]
            for row in group.sort_values(['query_position','kind','k']).itertuples():
                if row.query_position not in alignment['aligned_positions']: continue
                rows.append([int(row.query_position),row.kind,int(row.k),int(row.rank_start),int(row.n_neighbors),*[number(getattr(row,col[0])) for col in NEIGHBOURHOOD_METRICS]])
            assert len(rows)==4980
            path=out/'neighbourhood'/f"{model['id']}-{layer['id']}.js"
            write_js(path,'EXPLORER_NEIGHBOURHOODS',key,{'columns':['query_index','kind','k','rank_start','n_neighbors',*[m[0] for m in NEIGHBOURHOOD_METRICS]],'rows':rows})
            local_manifest[key]={'path':f'assets/neighbourhood/{path.name}','sha256':digest(path),'bytes':path.stat().st_size,'rows':len(rows)}
    bootstrap={k:v for k,v in payload.items() if k!='excerpts'}
    bootstrap['schemaVersion']=3
    bootstrap['paper']=json.loads((ROOT/'configs/site.json').read_text())
    bootstrap['excerpts']=[{k:v for k,v in e.items() if k!='scores'} for e in payload['excerpts']]
    bootstrap['geometryManifest']=manifest
    bootstrap['neighbourhoodManifest']=local_manifest
    bootstrap['neighbourhoodMetrics']=[{'id':k,'label':label,'unit':unit,'definition':definition,'granularity':'query neighbourhood'} for k,label,unit,definition in NEIGHBOURHOOD_METRICS]
    bootstrap['neighbourhoodCoverage']={'sample':500,'aligned':498,'positions':alignment['aligned_positions'],'k':[100,500,1000,2000,3000],'kinds':['cumulative','shell'],'sha256':digest(locality_path)}
    write_js(out/'explorer-index.js','EXPLORER_INDEX',None,bootstrap)


def build(source: Path | None = None) -> dict:
    feature_path = ROOT / "data/derived/features.parquet"
    target_path = ROOT / "data/derived/main_targets.parquet"
    frame = pd.read_parquet(feature_path).sort_values("query_index")
    targets = pd.read_parquet(target_path)
    if source:
        import_excerpts(source, frame)
    texts_path = ROOT / "data/explorer/excerpts.json"
    texts = {r["query_index"]: r for r in json.loads(texts_path.read_text())}
    assert len(texts) == len(frame) == 1994 and frame.query_index.is_unique
    inventory = pd.read_csv(ROOT / "paper/tables/table_17.csv").to_dict("records")
    columns = [r["feature"] for r in inventory]
    assert len(columns) == 46 and set(columns) == set(frame.columns) - {"query_index", "text_sha256"}
    features = []
    for row in inventory:
        key = row["feature"]
        label = LABELS.get(key, POS.get(key.removeprefix("upos_dist_"), DEPS.get(key.removeprefix("dep_dist_"), key)))
        unit = "percent" if row["definition"].startswith(("Percentage", "Among")) else "number"
        if key == "lexical_density": unit = "ratio"
        if key in {"n_tokens", "n_sentences"}: unit = "count"
        if "frequency_class" in key: unit = "class"
        values = pd.to_numeric(frame[key], errors="raise")
        assert not np.isinf(values).any()
        features.append({"id": key, "label": label, "family": row["family"], "granularity": "excerpt aggregate", "definition": row["definition"], "unit": unit, "min": number(values.min()), "max": number(values.max()), "p05": number(values.quantile(.05)), "p95": number(values.quantile(.95))})
    ids = frame.query_index.to_list()
    scores = {int(q): {} for q in ids}
    revisions = {}
    populations = {}
    for model, layers in MODEL_LAYERS.items():
        for depth, layer in zip(DEPTHS, layers):
            group = targets.loc[(targets.model_key == model) & (targets.layer == layer)].set_index("query_index").reindex(ids)
            assert group.index.is_unique and group.reference_size.eq(15000).all() and group.k.eq(1000).all()
            assert group.model_revision.nunique() == 1
            revisions[model] = group.model_revision.iloc[0]
            populations[f"{model}.{depth}"] = len(group)
            for estimator, column in TARGETS.items():
                values = pd.to_numeric(group[column], errors="raise")
                valid = np.isfinite(values) & values.gt(0)
                if estimator == "ess":
                    assert valid.all()
                values = values.where(valid)
                populations[f"{model}.{depth}.{estimator}"] = int(valid.sum())
                percentiles = values.rank(method="average", pct=True) * 100
                for q in ids:
                    scores[int(q)].setdefault(model, {}).setdefault(depth, {})[estimator] = [number(values.loc[q]), number(percentiles.loc[q])]
    paper_ids = set(pd.read_csv(ROOT / "paper/tables/table_13.csv").query_index)
    excerpts = []
    for _, row in frame.iterrows():
        q = int(row.query_index); text = texts[q]
        assert text["text_sha256"] == row.text_sha256 == hashlib.sha256(text["text"].encode()).hexdigest()
        excerpts.append({"id": f"q-{q}", "queryIndex": q, "text": text["text"], "textSha256": text["text_sha256"], "source": text["source"], "paperExample": q in paper_ids, "features": [number(row[col]) for col in columns], "scores": scores[q]})
    payload = {"schemaVersion": 2, "meta": {"title": "Linguistic Features of Local Geometry in Language Models", "population": len(frame), "geometricPopulation": 2000, "referenceSize": 15000, "k": 1000, "percentilePopulation": "All available finite estimates among the 1,994 evaluation excerpts with an aligned linguistic profile, separately for each model, layer, and estimator. Missing estimates are retained as null and never imputed.", "validPopulation": {k: v for k, v in populations.items() if k.count('.') == 2}, "frequencyControls": "The three frequency controls are the shared Pythia-1.4B-tokenizer proxies in the released profiling table, not independently recomputed per model.", "sources": {"features": digest(feature_path), "targets": digest(target_path), "excerpts": digest(texts_path)}}, "models": [{"id": m, "label": NAMES[m], "revision": revisions[m], "layers": [{"id": d, "number": n, "label": d.title()} for d, n in zip(DEPTHS, layers)]} for m, layers in MODEL_LAYERS.items()], "estimators": [{"id": e, "label": e.upper()} for e in TARGETS], "features": features, "excerpts": excerpts}
    out = ROOT / "docs/assets"; out.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    (out / "explorer.json").write_text(encoded + "\n")
    build_progressive(payload, out)
    legacy = out / "explorer-data.js"
    if legacy.exists(): legacy.unlink()
    report = {"excerpts": len(excerpts), "features": len(features), "model_depth_settings": len(MODEL_LAYERS) * len(DEPTHS), "estimator_settings": len(MODEL_LAYERS) * len(DEPTHS) * len(TARGETS), "verified_text_hashes": len(excerpts), "paper_examples": sum(e["paperExample"] for e in excerpts), "population_by_setting": payload["meta"]["validPopulation"], "locality_aligned_queries": 498, "sources": payload["meta"]["sources"]}
    (out / "explorer-validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="Original experiment directory, only needed to import the verified evaluation excerpts once.")
    build(parser.parse_args().source_root)
