#!/usr/bin/env python3
"""Prepare the paper PDF, numeric results, and static repository browser."""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'


def build():
    dest=DOCS/'downloads';dest.mkdir(exist_ok=True)
    # Remove previously generated download formats as well as their links.
    for folder in [dest, DOCS/'results']:
        for path in folder.rglob('*'):
            if path.is_file() and path.suffix in {'.zip', '.tex'}: path.unlink()
    shutil.copy2(ROOT/'paper/manuscript/supplied-paper.pdf',dest/'supplied-paper.pdf')
    manifest=json.loads((ROOT/'paper/current/manifest.json').read_text())
    assert hashlib.sha256((ROOT/'paper/manuscript/manuscript.tex').read_bytes()).hexdigest()==manifest['manuscriptSha256']
    for folder,web in [('paper/current/tables','current'),('paper/current/figures','figures'),('paper/tables','archive'),('paper/figures','archive')]:
        target=DOCS/'results'/web;target.mkdir(parents=True,exist_ok=True)
        for source in (ROOT/folder).iterdir():
            if source.suffix in {'.csv','.png','.pdf'}:shutil.copy2(source,target/source.name)
    web_manifest={**manifest,'tables':[{k:v for k,v in table.items() if k!='tex'} for table in manifest['tables']]}
    (DOCS/'assets/results-data.js').write_text('window.RESULTS_DATA='+json.dumps(web_manifest,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n')
    tracked=subprocess.check_output(['git','-C',str(ROOT),'ls-files','--cached','--others','--exclude-standard'],text=True).splitlines()
    files=[]
    for name in sorted(set(tracked)):
        path=ROOT/name
        if not path.is_file() or path.suffix in {'.tex','.zip'}:continue
        preview=None
        if path.suffix in {'.py','.md','.html','.css','.js','.yaml','.yml','.cff','.tex','.txt'} or path.name in {'Makefile','.gitignore','.gitattributes'}:
            if path.stat().st_size<160000 and not name.startswith(('docs/assets/geometry/','docs/assets/neighbourhood/')):
                try:preview=path.read_text()
                except UnicodeDecodeError:pass
        files.append({'path':name,'bytes':path.stat().st_size,'preview':preview})
    meta={'title':json.loads((ROOT/'configs/site.json').read_text())['title'],'branch':'main','files':files,'readme':(ROOT/'README.md').read_text()}
    repo=DOCS/'repository';repo.mkdir(exist_ok=True)
    # Source views use textContent; no parsed source is executed by the browser.
    (repo/'repository-data.js').write_text('window.REPOSITORY_DATA='+json.dumps(meta,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n')
    report={name:{'sha256':hashlib.sha256((dest/name).read_bytes()).hexdigest(),'bytes':(dest/name).stat().st_size} for name in ['supplied-paper.pdf']}
    (DOCS/'assets/downloads-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Prepared verified downloads and repository browser:',len(files),'files;', {name:round(v['bytes']/1024/1024,2) for name,v in report.items()})

if __name__=='__main__':build()
