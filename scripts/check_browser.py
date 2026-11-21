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
import json
import time
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
    def navigate(suffix=''):
        call('Page.navigate',{'url':args.url.rstrip('/')+'/'+suffix})
        deadline=time.monotonic()+15
        while time.monotonic()<deadline:
            if js("document.querySelectorAll('.feature-row').length===46"):return
            time.sleep(.1)
        raise AssertionError('Explorer did not load')
    def change(identifier,value):
        js(f"document.getElementById({json.dumps(identifier)}).value={json.dumps(value)};document.getElementById({json.dumps(identifier)}).dispatchEvent(new Event('change',{{bubbles:true}}))")
    def snapshot(name,offset=None):
        if not args.screenshots:return
        if offset is not None:js(f"window.scrollTo({{top:{offset},behavior:'instant'}})")
        time.sleep(.15)
        shot=call('Page.captureScreenshot',{'format':'png'})
        args.screenshots.mkdir(parents=True,exist_ok=True)
        (args.screenshots/(name+'.png')).write_bytes(base64.b64decode(shot['data']))
    call('Runtime.enable');call('Page.enable');call('Network.enable')
    call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1050,'deviceScaleFactor':1,'mobile':False})
    navigate()
    assert js("document.querySelectorAll('.plot-point').length") == 1994
    assert js("document.querySelectorAll('.table-item').length") == 16
    assert js("document.querySelectorAll('.figure-card').length") == 7
    snapshot('desktop',0)
    js("document.querySelector('#explorer').scrollIntoView({behavior:'instant'})")
    snapshot('explorer')
    # Search must preserve percentiles from the full reference population.
    js("document.querySelector('#search').value='New York';document.querySelector('#search').dispatchEvent(new Event('input'))")
    time.sleep(.3)
    assert js("document.querySelectorAll('.plot-point').length") > 1
    assert js("document.querySelector('#count').textContent.includes('1,994 of')") is False
    js("document.querySelector('#reset').click()")
    change('model','qwen')
    assert js("document.querySelector('[data-depth=intermediate] small').textContent") == '14'
    assert js("document.querySelector('#count').textContent.includes('Qwen2.5-7B')")
    js("document.querySelector('[data-depth=late]').click()")
    change('estimator','mle')
    assert js("document.querySelector('#detail').textContent.includes('layer 27 · MLE')")
    change('band','high')
    assert js("[...document.querySelectorAll('.excerpt-bottom span')].every(e=>parseFloat(e.textContent.replace('Percentile ',''))>=80)")
    change('sort','high')
    displayed=js("[...document.querySelectorAll('.excerpt-bottom strong')].map(e=>parseFloat(e.textContent.replace('ID ','').replace(',','')))")
    assert displayed==sorted(displayed,reverse=True)
    js("document.querySelector('#detail .detail-actions button').click();document.querySelectorAll('.excerpt-item')[1].click()")
    assert js("!document.querySelector('#comparison').hidden && document.querySelectorAll('.compare-table tbody tr').length===48")
    change('plot-feature','lexical_density')
    assert js("document.querySelector('.feature-row.active strong').textContent.endsWith('%')")
    js("document.querySelector('.figure-image').click()")
    assert js("document.querySelector('#figure-dialog').open")
    js("document.querySelector('#close-figure').click();document.querySelector('.table-item').open=true")
    assert js("document.querySelectorAll('.table-item .result-table tr').length")>100
    # Direct links preserve missing measurements and must not display null as zero.
    navigate('?depth=early&estimator=fci&example=q-502')
    assert js("document.querySelector('#detail .score-strip strong').textContent")=='Unavailable'
    assert js("document.querySelector('#detail').textContent.includes('1,993')")
    assert js("document.querySelectorAll('.plot-point').length")==1993
    navigate('?model=apertus&depth=late&estimator=mle&example=q-723&feature=upos_dist_NOUN')
    assert js("document.querySelector('#detail .eyebrow').textContent")=='Excerpt #723'
    assert js("document.querySelector('#model').value")=='apertus'
    assert js("document.querySelector('#plot-feature').value")=='upos_dist_NOUN'
    # The actual display should retain the lexical-density fraction convention.
    expected=js("(()=>{const e=EXPLORER_DATA.excerpts.find(x=>x.id==='q-723');return e.features[EXPLORER_DATA.features.findIndex(x=>x.id==='lexical_density')]*100})()")
    change('plot-feature','lexical_density')
    actual=js("parseFloat(document.querySelector('.feature-row.active strong').textContent)")
    assert abs(expected-actual)<.051,(expected,actual)
    # All download links must resolve under a repository subpath or root.
    assert js("Promise.all([...document.querySelectorAll('#tables a,.figure-links a,#archive-files a')].map(a=>fetch(a.href).then(r=>r.ok))).then(a=>a.every(Boolean))")
    for width,height,name in [(390,844,'mobile'),(768,1024,'tablet')]:
        call('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':True})
        js("document.querySelector('#comparison').hidden=true;document.querySelectorAll('.table-item').forEach(e=>e.open=true)")
        assert js("document.documentElement.scrollWidth <= innerWidth"),f'Horizontal overflow at {width}'
        snapshot(name,0)
        js("document.querySelector('#explorer').scrollIntoView({behavior:'instant'})")
        snapshot(name+'-explorer')
    assert not errors,errors
    assert not failures,failures
    print(json.dumps({'status':'passed','browser':'Chrome DevTools','checks':['filters','sort','model-specific layers','comparison','missing estimate','deep links','feature units','downloads','mobile/tablet layout'],'javascript_errors':len(errors),'failed_requests':len(failures)},indent=2))
    ws.close()


if __name__=='__main__':main()
