#!/usr/bin/env python3
"""Verify locality query positions against original excerpt/source joins once."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 'Pythia-6.9B':'outputs_6.9/seen_unseen_pythia69b_mle_ess_fci_k1000_ref15000_layers2_16_31_sentence_level',
 'Qwen2.5-7B':'qwen_results/outputs/local_seen_unseen_qwen2p5_7b_mle_ess_pyfci_ref15000_k1000_layers2_14_27_sentence_level',
 'Apertus-8B':'apertus_results/outputs/apertus8b_2509_l2_l16_l31/local_seen_unseen_apertus8b_2509_l2_l16_l31_mle_ess_pyfci_ref15000_k1000_sentence_level',
}
def main(source):
 path=source/'outputs/neighborhood_locality_quick_20260916/per_query_metrics.parquet'
 original=pd.read_parquet(path)
 released=pd.read_parquet(ROOT/'data/derived/neighbourhood_locality_metrics.parquet')
 pd.testing.assert_frame_equal(original[released.columns],released)
 texts={r['query_index']:r for r in json.loads((ROOT/'data/explorer/excerpts.json').read_text())}
 hashes={};verified=[]
 for (model,layer),group in original.groupby(['model','layer']):
  target_path=source/SOURCES[model]/f'eval_known_layer{layer}_k1000_ref15000_sentence_level.parquet'
  targets=pd.read_parquet(target_path).set_index('query_index')
  hashes[f'{model}.layer-{layer}']=hashlib.sha256(target_path.read_bytes()).hexdigest()
  rows=group[['query_position','query_source_index','query_source']].drop_duplicates()
  assert len(rows)==500
  for row in rows.itertuples():
   target=targets.loc[row.query_position]
   assert target.query_source_index==row.query_source_index
   if row.query_position in texts:
    t=texts[row.query_position]
    assert target.text==t['text'] and row.query_source==t['source']
    assert hashlib.sha256(target.text.encode()).hexdigest()==t['text_sha256']
  verified.append({'model':model,'layer':int(layer),'query_positions':len(rows),'aligned_excerpts':sum(int(q) in texts for q in rows.query_position)})
 positions=sorted(int(q) for q in released.query_position.unique())
 report={'mapping':'query_position equals main evaluation query_index; verified against original query_source_index and exact text SHA-256 for every available profile, separately in all nine model/layer settings','locality_sha256':hashlib.sha256((ROOT/'data/derived/neighbourhood_locality_metrics.parquet').read_bytes()).hexdigest(),'original_locality_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'target_source_hashes':hashes,'verified_settings':verified,'positions':positions,'aligned_positions':[q for q in positions if q in texts]}
 (ROOT/'data/explorer/neighbourhood_alignment.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Verified locality alignment:',len(report['aligned_positions']),'of',len(positions),'queries across',len(verified),'settings')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',type=Path,required=True);main(p.parse_args().source_root)
