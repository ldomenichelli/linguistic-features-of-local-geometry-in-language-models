#!/usr/bin/env python3
"""Package real manuscript/code/data downloads and a static repository browser."""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'


def write_zip(path, files):
    # Stable timestamps/order make release artifacts deterministic across rebuilds.
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for source in sorted(set(files)):
            if not source.is_file():continue
            info=zipfile.ZipInfo(str(source.relative_to(ROOT)),date_time=(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,source.read_bytes())
    assert path.stat().st_size<25*1024*1024, f'Split large static asset before deployment: {path}'


def build():
    dest=DOCS/'downloads';dest.mkdir(exist_ok=True)
    for original,name in [('paper/manuscript/manuscript.tex','manuscript.tex'),('paper/manuscript/supplied-paper.pdf','supplied-paper.pdf')]:shutil.copy2(ROOT/original,dest/name)
    manifest=json.loads((ROOT/'paper/current/manifest.json').read_text())
    assert hashlib.sha256((ROOT/'paper/manuscript/manuscript.tex').read_bytes()).hexdigest()==manifest['manuscriptSha256']
    for folder,web in [('paper/current/tables','current'),('paper/current/figures','figures'),('paper/tables','archive'),('paper/figures','archive')]:
        target=DOCS/'results'/web;target.mkdir(parents=True,exist_ok=True)
        for source in (ROOT/folder).iterdir():
            if source.suffix in {'.csv','.tex','.png','.pdf'}:shutil.copy2(source,target/source.name)
    (DOCS/'assets/results-data.js').write_text('window.RESULTS_DATA='+json.dumps(manifest,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n')
    data_files=[p for folder in ['data','paper','results/reference'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    write_zip(dest/'measurements.zip',data_files)
    code_files=[p for folder in ['scripts','src','tests','configs','.github'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    code_files += [p for p in ROOT.iterdir() if p.is_file() and (p.suffix in {'.md','.txt','.cff'} or p.name in {'Makefile','.gitignore','.gitattributes'})]
    code_files += [DOCS/'index.html',*[DOCS/'assets'/name for name in ['app.js','style.css','favicon.svg']]]
    write_zip(dest/'project-code.zip',code_files)
    tracked=subprocess.check_output(['git','-C',str(ROOT),'ls-files','--cached','--others','--exclude-standard'],text=True).splitlines()
    files=[]
    for name in sorted(set(tracked)):
        path=ROOT/name
        if not path.is_file():continue
        preview=None
        if path.suffix in {'.py','.md','.html','.css','.js','.yaml','.yml','.cff','.tex','.txt'} or path.name in {'Makefile','.gitignore','.gitattributes'}:
            if path.stat().st_size<160000 and not name.startswith(('docs/assets/geometry/','docs/assets/neighbourhood/')):
                try:preview=path.read_text()
                except UnicodeDecodeError:pass
        files.append({'path':name,'bytes':path.stat().st_size,'preview':preview,'bundle':'code' if path in code_files else 'data'})
    meta={'title':json.loads((ROOT/'configs/site.json').read_text())['title'],'branch':'main','files':files,'readme':(ROOT/'README.md').read_text()}
    repo=DOCS/'repository';repo.mkdir(exist_ok=True)
    # Source views use textContent; no parsed source is executed by the browser.
    (repo/'repository-data.js').write_text('window.REPOSITORY_DATA='+json.dumps(meta,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n')
    report={name:{'sha256':hashlib.sha256((dest/name).read_bytes()).hexdigest(),'bytes':(dest/name).stat().st_size} for name in ['manuscript.tex','supplied-paper.pdf','project-code.zip','measurements.zip']}
    (DOCS/'assets/downloads-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Prepared verified downloads and repository browser:',len(files),'files;', {name:round(v['bytes']/1024/1024,2) for name,v in report.items()})

if __name__=='__main__':build()
