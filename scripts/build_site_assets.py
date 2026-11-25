#!/usr/bin/env python3
"""Prepare result downloads and the static repository browser."""
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'


def build():
    (DOCS/'downloads/supplied-paper.pdf').unlink(missing_ok=True)
    (DOCS/'assets/downloads-manifest.json').unlink(missing_ok=True)
    for folder in [DOCS/'downloads', DOCS/'results']:
        for path in folder.rglob('*'):
            if path.is_file() and path.suffix in {'.zip', '.tex'}: path.unlink()
    manifest=json.loads((ROOT/'paper/current/manifest.json').read_text())
    # The manuscript is kept outside the public repository. Its recorded digest
    # identifies the snapshot used to transcribe the released CSV tables.
    config=json.loads((ROOT/'configs/site.json').read_text())
    assert config['manuscriptSha256']==manifest['manuscriptSha256']
    for folder,web in [('paper/current/tables','current'),('paper/current/figures','figures'),('paper/tables','archive'),('paper/figures','archive')]:
        target=DOCS/'results'/web;target.mkdir(parents=True,exist_ok=True)
        for source in (ROOT/folder).iterdir():
            if source.suffix in {'.csv','.png','.pdf'}:shutil.copy2(source,target/source.name)
    (DOCS/'assets/results-data.js').write_text('window.RESULTS_DATA='+json.dumps(manifest,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n')
    tracked=subprocess.check_output(['git','-C',str(ROOT),'ls-files','--cached','--others','--exclude-standard'],text=True).splitlines()
    files=[]
    for name in sorted(set(tracked)):
        path=ROOT/name
        if not path.is_file() or path.suffix in {'.tex','.zip'}:continue
        preview=None
        if path.suffix in {'.py','.md','.html','.css','.js','.yaml','.yml','.cff','.txt'} or path.name in {'Makefile','.gitignore','.gitattributes'}:
            if path.stat().st_size<160000 and not name.startswith(('docs/assets/geometry/','docs/assets/neighbourhood/')):
                try:preview=path.read_text()
                except UnicodeDecodeError:pass
        files.append({'path':name,'bytes':path.stat().st_size,'preview':preview})
    meta={'title':json.loads((ROOT/'configs/site.json').read_text())['title'],'branch':'main','files':files,'readme':(ROOT/'README.md').read_text()}
    repo=DOCS/'repository';repo.mkdir(exist_ok=True)
    # Source views use textContent; no parsed source is executed by the browser.
    (repo/'repository-data.js').write_text('window.REPOSITORY_DATA='+json.dumps(meta,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n')
    print('Prepared result downloads and repository browser:',len(files),'files')

if __name__=='__main__':build()
