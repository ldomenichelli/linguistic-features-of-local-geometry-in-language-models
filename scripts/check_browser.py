#!/usr/bin/env python3
"""Exercise the explorer in a real Chrome browser via a local DevTools endpoint.

Requires optional package websocket-client. Start `make serve`, then:
  google-chrome --headless --remote-debugging-port=9222 --remote-allow-origins='*' about:blank
  python3 scripts/check_browser.py --url http://127.0.0.1:8765/
Use --screenshots /tmp/project-preview to save desktop/mobile PNG previews.
"""
from __future__ import annotations
import argparse
import base64
import csv
import tempfile
import json
import time
import pandas as pd
import urllib.request
from pathlib import Path

import websocket


def main():
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--url',default='http://127.0.0.1:8765/')
    parser.add_argument('--devtools',default='http://127.0.0.1:9222')
    parser.add_argument('--screenshots',type=Path)
    args=parser.parse_args()
    tabs=json.load(urllib.request.urlopen(args.devtools+'/json'))
    tab=next(t for t in tabs if t['type']=='page')
    ws=websocket.create_connection(tab['webSocketDebuggerUrl'],timeout=15)
    index=0; errors=[]; failures=[]
    def call(method,params=None):
        nonlocal index
        index+=1;ws.send(json.dumps({'id':index,'method':method,'params':params or {}}))
        while True:
            message=json.loads(ws.recv())
            if message.get('method')=='Runtime.exceptionThrown':errors.append(message)
            if message.get('method')=='Network.responseReceived' and message['params']['response']['status']>=400:failures.append(message['params']['response']['url'])
            if message.get('id')==index:
                assert 'error' not in message,message
                return message.get('result',{})
    def js(code):
        result=call('Runtime.evaluate',{'expression':code,'returnByValue':True,'awaitPromise':True})
        assert 'exceptionDetails' not in result,result
        return result.get('result',{}).get('value')
    def wait_for(expression,timeout=15):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            if js(expression):return
            time.sleep(.07)
        raise AssertionError('Timed out: '+expression)
    def navigate(suffix=''):
        call('Page.navigate',{'url':args.url.rstrip('/')+'/'+suffix})
        wait_for("document.querySelectorAll('.feature-row').length===46 && !document.querySelector('#count').textContent.startsWith('Loading')")
    def change(identifier,value):
        js(f"document.getElementById({json.dumps(identifier)}).value={json.dumps(value)};document.getElementById({json.dumps(identifier)}).dispatchEvent(new Event('change',{{bubbles:true}}))")
        wait_for("!document.querySelector('#count').textContent.startsWith('Loading') && !document.querySelector('#detail').hasAttribute('aria-busy')")
    def snapshot(name,offset=None):
        if not args.screenshots:return
        if offset is not None:js(f"window.scrollTo({{top:{offset},behavior:'instant'}})")
        time.sleep(.15)
        shot=call('Page.captureScreenshot',{'format':'png'})
        args.screenshots.mkdir(parents=True,exist_ok=True)
        (args.screenshots/(name+'.png')).write_bytes(base64.b64decode(shot['data']))
    call('Runtime.enable');call('Page.enable');call('Network.enable')
    call('Network.setCacheDisabled',{'cacheDisabled':True})
    call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1050,'deviceScaleFactor':1,'mobile':False})
    navigate()
    assert js("Object.keys(EXPLORER_GEOMETRY).length")==1
    assert js("typeof EXPLORER_NEIGHBOURHOODS==='undefined'")
    assert js("document.querySelectorAll('.plot-point').length")==1994
    assert js("EXPLORER_INDEX.excerpts.length")==2000
    assert js("document.querySelector('#count').textContent.startsWith('2,000 / 2,000')")
    assert js("[...document.querySelectorAll('a[href]')].every(a=>!(/\\.(zip|tex)(?:$|[?#])/i).test(a.getAttribute('href')))")
    assert js("document.querySelectorAll('.table-item').length")==16
    assert js("document.querySelectorAll('.paper-figure').length")==7
    snapshot('desktop-v3',0)
    js("document.querySelector('.population-plot').scrollIntoView({behavior:'instant'})")
    snapshot('explorer-v3')
    js("document.querySelector('#search').value='New York';document.querySelector('#search').dispatchEvent(new Event('input'))")
    time.sleep(.25);wait_for("!document.querySelector('#count').textContent.startsWith('Loading')")
    count=js("document.querySelectorAll('.plot-point').length")
    assert 1<count<1994
    # The available point values must match the unfiltered source population.
    targets=pd.read_parquet(Path(__file__).resolve().parents[1]/'data/derived/main_targets.parquet')
    population=targets.loc[(targets.model_key=='pythia')&(targets.layer==16)].set_index('query_index').pointwise_ess
    expected_percentile=population.rank(method='average',pct=True).loc[1140]*100
    assert abs(float(js("document.querySelector('.measure-table tr[data-estimator=ess] td:last-child').textContent"))-expected_percentile)<.051
    js("document.querySelector('#reset').click()")
    wait_for("document.querySelectorAll('.plot-point').length===1994")
    change('model','qwen')
    assert js("document.querySelector('#depth option:checked').textContent")=='Intermediate · layer 14'
    change('depth','late');change('estimator','mle');change('band','high');change('sort','high')
    displayed=js("[...document.querySelectorAll('.excerpt-bottom strong')].map(e=>parseFloat(e.textContent.split('ID ')[1].replace(',','')))")
    assert displayed==sorted(displayed,reverse=True)
    # Pair the same excerpt across settings and make both axes into percentiles.
    change('plot-mode','compare');change('compare-model','apertus');change('compare-depth','intermediate');change('chart-scale','percentile')
    assert js("!document.querySelector('#compare-controls').hidden && document.querySelector('.plot-diagonal')!==null")
    assert js("document.querySelectorAll('.plot-point').length")>300
    # Selecting a point opens the text. Arrow keys retain a single roving tab stop.
    js("document.querySelector('.plot-point').dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    active=js("document.querySelector('.plot-point.selected').dataset.example")
    assert active in js("document.querySelector('#detail .detail-head').textContent")
    js("document.querySelector('.plot-point.selected').dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}))")
    assert js("document.querySelectorAll('.plot-point[tabindex=\"0\"]').length")==1
    js("document.querySelector('.plot-point.selected').dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}))")
    assert js("document.activeElement.id")=='detail'
    # Missing FCI is never rendered as zero, and its percentile denominator shrinks.
    navigate('?depth=early&estimator=fci&example=q-502')
    assert js("document.querySelector('[data-estimator=fci] td').textContent")=='Unavailable'
    assert js("document.querySelector('#detail').textContent.includes('1,999')")
    assert js("document.querySelectorAll('.plot-point').length")==1993
    # Locality is a verified 498-excerpt subset, with explicit k and shell ranks.
    navigate('?example=q-14&measure=radius_ratio')
    assert js("document.querySelectorAll('.plot-point').length")==498
    assert js("Object.keys(EXPLORER_NEIGHBOURHOODS).length")==1
    js("document.querySelectorAll('#detail > details')[1].open=true")
    wait_for("document.querySelector('.neighbourhood-table')!==null")
    change('neighbour-k','500');change('neighbour-kind','shell')
    assert js("document.querySelector('#detail').textContent.includes('101–500')")
    assert js("document.querySelector('#detail').textContent.includes('400 neighbours')")
    assert js("document.querySelector('#detail').textContent.includes('k = 1,000')")
    original=pd.read_parquet(Path(__file__).resolve().parents[1]/'data/derived/neighbourhood_locality_metrics.parquet')
    actual=original.loc[(original.model=='Pythia-6.9B')&(original.layer==16)&(original.query_position==14)&(original.kind=='shell')&(original.k==500)].iloc[0]
    recorded=js("EXPLORER_NEIGHBOURHOODS['pythia.intermediate'].rows.find(r=>r[0]===14&&r[1]==='shell'&&r[2]===500)")
    assert recorded[7]==actual.radius_ratio
    # Three estimators and raw fraction units survive a real CSV download.
    with tempfile.TemporaryDirectory(prefix='geometry-export-') as directory:
        call('Browser.setDownloadBehavior',{'behavior':'allow','downloadPath':directory})
        js("document.querySelector('#search').value='q-14';document.querySelector('#search').dispatchEvent(new Event('input'))")
        time.sleep(.25);wait_for("document.querySelectorAll('.plot-point').length===1")
        js("document.querySelector('#download-filtered').click()")
        deadline=time.monotonic()+10;exported=[]
        while time.monotonic()<deadline:
            exported=list(Path(directory).glob('*.csv'))
            if exported:break
            time.sleep(.1)
        assert exported,'CSV was not downloaded'
        with exported[0].open(newline='') as stream:rows=list(csv.DictReader(stream))
        assert len(rows)==1
        row=rows[0];assert row['excerpt_key']=='q-14' and row['id_k']=='1000' and row['diagnostic_k']=='500'
        assert float(row['radius_ratio'])==actual.radius_ratio
        full=pd.read_parquet(Path(__file__).resolve().parents[1]/'data/derived/main_targets.parquet')
        query=full.loc[(full.model_key=='pythia')&(full.layer==16)&(full.query_index==14)].iloc[0]
        assert float(row['ess_id'])==query.pointwise_ess
        assert float(row['mle_id'])==query.pointwise_mle
        feature=pd.read_parquet(Path(__file__).resolve().parents[1]/'data/derived/features.parquet').set_index('query_index')
        assert float(row['lexical_density'])==feature.loc[14,'lexical_density']
        call('Browser.setDownloadBehavior',{'behavior':'default'})
    change('plot-feature','lexical_density')
    val=js("document.querySelector('.feature-row.active td').textContent")
    assert abs(float(val.rstrip('%'))-feature.loc[14,'lexical_density']*100)<.051
    js("document.querySelector('#feature-search').value='nominal';document.querySelector('#feature-search').dispatchEvent(new Event('input'))")
    assert 0<js("document.querySelectorAll('.feature-row').length")<46
    # All-model comparison is requested explicitly; all nine chunks then load.
    js("document.querySelectorAll('#detail > details')[0].open=true")
    wait_for("Object.keys(EXPLORER_GEOMETRY).length===9 && document.querySelector('#detail .compare-table tbody tr')!==null")
    assert js("document.querySelectorAll('#detail .compare-table tbody tr').length")==9
    # Every original excerpt is searchable, including the six without profiles.
    for missing_query in [95,321,421,704,1318,1479]:
        navigate(f'?search=q-{missing_query}&example=q-{missing_query}')
        assert js("document.querySelector('#detail').textContent.includes('Linguistic profile unavailable')")
        assert js("[...document.querySelectorAll('.feature-row td')].every(e=>e.textContent==='Unavailable')")
        assert js("document.querySelector('[data-estimator=ess] td').textContent!=='Unavailable'")
        assert js("document.querySelectorAll('.plot-point').length")==0
    navigate('?plotMode=compare')
    assert js("document.querySelectorAll('.plot-point').length")==2000
    # No diagnostics are fabricated for an excerpt outside the locality sample.
    navigate('?example=q-1140&measure=radius')
    js("document.querySelectorAll('#detail > details')[1].open=true")
    wait_for("document.querySelector('#detail').textContent.includes('was not in the 500-query')")
    assert js("document.querySelector('#plot-selection').textContent.includes('no available')")
    js("document.querySelector('.figure-image').click()")
    assert js("document.querySelector('#figure-dialog').open")
    js("document.querySelector('#close-figure').click()")
    assert js("Promise.all([...document.querySelectorAll('a[href]')].filter(a=>a.origin===location.origin&&!a.hash).map(a=>fetch(a.href,{method:'HEAD'}).then(r=>r.ok))).then(a=>a.every(Boolean))")
    for width,height,name in [(390,844,'mobile-v3'),(768,1024,'tablet-v3')]:
        call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':True})
        js("document.querySelectorAll('.table-item').forEach(e=>e.open=true)")
        time.sleep(.2)
        assert js("document.documentElement.scrollWidth<=innerWidth"),f'Page overflow at {width}'
        snapshot(name,0)
        js("document.querySelector('.reading-grid').scrollIntoView({behavior:'instant'})")
        snapshot(name+'-excerpt')
    assert not errors,errors
    assert not failures,failures
    print(json.dumps({'status':'passed','checks':['progressive loading','search','model/layer filters','sorting','paired model/layer graph','point-to-excerpt','keyboard navigation','missing FCI','neighbourhood cohort and shell ranks','source-precision CSV','feature definitions and units','all-model comparison','real downloads','mobile/tablet layout'],'javascript_errors':len(errors),'failed_requests':len(failures)},indent=2))
    ws.close()


if __name__=='__main__':main()
