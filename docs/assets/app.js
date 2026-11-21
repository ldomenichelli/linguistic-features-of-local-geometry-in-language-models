/* Static, dependency-free browser for measured excerpt-level results. */
(() => {
  'use strict';
  const data = window.EXPLORER_DATA, results = window.RESULTS_DATA;
  const $ = id => document.getElementById(id);
  if (!data || !results) { $('count').textContent = 'Data could not be loaded. Please reload, or download the JSON below.'; return; }
  const byId = new Map(data.excerpts.map(e => [e.id, e]));
  const featureById = new Map(data.features.map((f, i) => [f.id, {...f, index:i}]));
  const defaults = {model:'pythia', depth:'intermediate', estimator:'ess', search:'', source:'all', band:'all', sort:'featured', feature:'n_tokens', example:'q-1140', compare:''};
  const params = new URLSearchParams(location.search);
  const state = {...defaults};
  for (const key of Object.keys(defaults)) if (params.has(key)) state[key] = params.get(key);
  if (!data.models.some(m => m.id === state.model)) state.model = defaults.model;
  if (!['early','intermediate','late'].includes(state.depth)) state.depth = defaults.depth;
  if (!data.estimators.some(e => e.id === state.estimator)) state.estimator = defaults.estimator;
  if (!featureById.has(state.feature)) state.feature = defaults.feature;
  if (!byId.has(state.example)) state.example = data.excerpts[0].id;
  if (!byId.has(state.compare)) state.compare = '';
  if (!['all','low','middle','high'].includes(state.band)) state.band='all';
  if (!['featured','high','low','feature','index'].includes(state.sort)) state.sort='featured';
  const sources = [...new Set(data.excerpts.map(e => e.source))].sort();
  if (!['all', ...sources].includes(state.source)) state.source='all';
  let filtered = [], page = 0;
  const pageSize = 10;
  const el = (tag, cls, text) => {const n=document.createElement(tag); if(cls) n.className=cls; if(text!==undefined) n.textContent=text; return n;};
  const fmt = (n, digits=2) => Number.isFinite(n) ? n.toLocaleString('en-US',{maximumFractionDigits:digits}) : 'Unavailable';
  const featureValue = (f,n) => !Number.isFinite(n) ? 'Unavailable' : f.unit === 'ratio' ? `${fmt(n*100,1)}%` : f.unit === 'percent' ? `${fmt(n,1)}%` : fmt(n, f.unit==='count'?0:2);
  const score = (e, depth=state.depth) => e.scores[state.model][depth][state.estimator];
  const model = () => data.models.find(m=>m.id===state.model);
  const layer = () => model().layers.find(d=>d.id===state.depth);
  const setting = () => `${model().label} · layer ${layer().number} · ${state.estimator.toUpperCase()}`;
  const link = (text,url,cls='text-link') => {const a=el('a',cls,text); a.href=url; return a;};
  const button = (text, callback, cls='quiet') => {const b=el('button',cls,text); b.type='button'; b.addEventListener('click',callback); return b;};
  const persist = () => {const p=new URLSearchParams(); for(const key of Object.keys(defaults)) if(state[key]!==defaults[key] && state[key]!=='') p.set(key,state[key]); history.replaceState(null,'',location.pathname+(p.size?'?'+p.toString():'')+location.hash);};
  const selectExample = id => {state.example=id; persist(); renderList(); renderDetail(); renderComparison(); renderPlot();};
  function applyFilters(resetPage=true) {
    const query=state.search.toLocaleLowerCase().trim(); const fi=featureById.get(state.feature).index;
    filtered=data.excerpts.filter(e=>{
      const p=score(e)[1];
      return (!query || e.text.toLocaleLowerCase().includes(query) || String(e.queryIndex)===query)
        && (state.source==='all'||e.source===state.source)
        && (state.band==='all'||Number.isFinite(p)&&(state.band==='low'?p<=20:state.band==='high'?p>=80:p>20&&p<80));
    });
    const numberSort=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)?b-a:Number.isFinite(a)?-1:Number.isFinite(b)?1:0;
    filtered.sort((a,b)=> {
      let delta=0;
      if(state.sort==='featured') delta=Number(b.paperExample)-Number(a.paperExample);
      if(state.sort==='high') delta=numberSort(score(a)[0],score(b)[0]);
      if(state.sort==='low') delta=numberSort(Number.isFinite(score(a)[0])?-score(a)[0]:null,Number.isFinite(score(b)[0])?-score(b)[0]:null);
      if(state.sort==='feature') delta=numberSort(a.features[fi],b.features[fi]);
      return delta || a.queryIndex-b.queryIndex;
    });
    if(resetPage) page=0;
    if(filtered.length && !filtered.some(e=>e.id===state.example)) state.example=filtered[0].id;
    persist(); render();
  }
  function render() {
    $('model').value=state.model; $('estimator').value=state.estimator; $('search').value=state.search;
    for(const key of ['source','band','sort']) $(key).value=state[key];
    $('plot-feature').value=state.feature;
    for(const b of $('depth-controls').querySelectorAll('button')) {
      b.setAttribute('aria-pressed',String(b.dataset.depth===state.depth));
      b.querySelector('small').textContent=model().layers.find(d=>d.id===b.dataset.depth).number;
    }
    $('count').textContent=`${fmt(filtered.length,0)} of ${fmt(data.meta.population,0)} excerpts · ${setting()}`;
    $('setting-note').textContent='1,000 neighbours · 15,000 reference excerpts';
    renderList(); renderDetail(); renderComparison(); renderPlot();
  }
  function renderList() {
    const list=$('excerpt-list'); list.replaceChildren();
    if(!filtered.length) list.append(el('p','empty','No excerpts match these filters. Try another search or reset the filters.'));
    for(const e of filtered.slice(page*pageSize,(page+1)*pageSize)) {
      const item=el('div'); item.setAttribute('role','listitem');
      const b=button('',()=>selectExample(e.id),'excerpt-item'+(e.id===state.example?' selected':'')); b.setAttribute('aria-pressed',String(e.id===state.example));
      const top=el('span','excerpt-top'); top.append(el('span','',`#${e.queryIndex} · ${e.source}`)); if(e.paperExample) top.append(el('span','tag','Paper example'));
      b.append(top,el('span','excerpt-preview',e.text.length>230?e.text.slice(0,230)+'…':e.text));
      const [id,p]=score(e); const bottom=el('span','excerpt-bottom'); bottom.append(el('strong','',`ID ${fmt(id)}`),el('span','',Number.isFinite(p)?`Percentile ${fmt(p,1)}`:'Estimate unavailable')); b.append(bottom); item.append(b); list.append(item);
    }
    const pages=Math.max(1,Math.ceil(filtered.length/pageSize)); $('page-number').textContent=`${page+1} / ${pages}`;
    $('prev').disabled=page===0; $('next').disabled=page+1>=pages;
  }
  function renderDetail() {
    const panel=$('detail'); panel.replaceChildren();
    if(!filtered.length) {panel.append(el('p','empty','Choose another filter to inspect an excerpt.')); return;}
    const e=byId.get(state.example), [id,p]=score(e);
    const top=el('div','detail-top'); top.append(el('p','eyebrow',`Excerpt #${e.queryIndex}`),el('span','source-label',e.source));
    panel.append(top,el('blockquote','full-excerpt',e.text));
    const strip=el('div','score-strip');
    const value=el('div'); value.append(el('span','small','Measured pointwise ID'),el('strong','',fmt(id)));
    const rank=el('div'); rank.append(el('span','small','Within-setting percentile'),el('strong','',Number.isFinite(p)?fmt(p,1):'Unavailable'));
    strip.append(value,rank); panel.append(strip);
    const track=el('div','percentile-track'); const fill=el('span','percentile-fill'); fill.style.width=`${Number.isFinite(p)?p:0}%`; track.append(fill); panel.append(track);
    const n=data.meta.validPopulation[`${state.model}.${state.depth}.${state.estimator}`];
    panel.append(el('p','detail-note',`${setting()} · Percentile among ${fmt(n,0)} available aligned estimates. ${Number.isFinite(id)?'Higher percentiles indicate larger measured ID in this setting.':'This measurement is missing; no value has been imputed.'}`));
    const depths=el('div','depth-reads'); for(const d of model().layers) {const [v]=score(e,d.id); depths.append(button(`${d.label} · L${d.number}\nID ${fmt(v)}`,()=>{state.depth=d.id; applyFilters(false);},'depth-read'+(d.id===state.depth?' active':'')));} panel.append(depths);
    const actions=el('div','detail-actions'); actions.append(button(state.compare===e.id?'Pinned for comparison':'Pin for comparison',()=>{state.compare=state.compare===e.id?'':e.id; persist(); renderDetail();renderComparison();renderPlot();}),button('Copy link',async event=>{
      const b=event.currentTarget; const url=location.href.split('#')[0]+'#explorer';
      try {await navigator.clipboard.writeText(url); b.textContent='Link copied';} catch {const a=link('Open this excerpt’s permalink',url); actions.append(a); b.disabled=true;}
    })); panel.append(actions);
    const heading=el('div','feature-heading'); heading.append(el('h3','','Linguistic profile'),el('span','small','Select a feature to plot it below')); panel.append(heading);
    const groups=new Map(); data.features.forEach((f,i)=>{if(!groups.has(f.family))groups.set(f.family,[]);groups.get(f.family).push([f,i]);});
    for(const [family,items] of groups) {
      const familyClass=family.includes('frequency')?'frequency':family.includes('Morphosyntactic')?'morph':family.includes('Surface')?'raw':/Clausal|morphology/.test(family)?'verbal':'syntax';
      const details=el('details','feature-family '+familyClass); details.open=family.includes('Surface')||items.some(([f])=>f.id===state.feature);
      const summary=el('summary','',family); summary.append(el('span','',String(items.length))); details.append(summary);
      for(const [f,i] of items) {const row=el('div','feature-row'+(f.id===state.feature?' active':'')); const b=button(f.label,()=>{state.feature=f.id;persist();renderDetail();renderPlot(); if(state.sort==='feature')applyFilters(false);},''); b.title='Plot this feature'; b.append(el('span','feature-code',f.id)); row.append(b,el('strong',Number.isFinite(e.features[i])?'':'unavailable',featureValue(f,e.features[i])),el('p','feature-help',f.definition)); details.append(row);}
      panel.append(details);
    }
  }
  function renderComparison() {
    const panel=$('comparison'); panel.replaceChildren(); panel.hidden=!state.compare;
    if(!state.compare) return;
    const a=byId.get(state.compare), b=byId.get(state.example);
    const head=el('div','detail-top'); head.append(el('h3','','Compare excerpts'),button('Clear',()=>{state.compare='';persist();renderDetail();renderComparison();renderPlot();})); panel.append(head);
    if(a===b) {panel.append(el('p','detail-note',`Excerpt #${a.queryIndex} is pinned. Select another excerpt to compare their measured ID and features.`)); return;}
    const texts=el('div','compare-texts'); for(const e of [a,b]){const item=el('div');item.append(el('strong','',`#${e.queryIndex} · ${e.source}`),el('p','',e.text));texts.append(item);}panel.append(texts);
    const table=el('table','compare-table'); const tr=el('tr');for(const s of ['Feature / measurement',`#${a.queryIndex}`,`#${b.queryIndex}`])tr.append(el('th','',s));const thead=el('thead');thead.append(tr);table.append(thead); const body=el('tbody');
    const addRow=(label,v1,v2)=>{const row=el('tr');const th=el('th','',label);th.scope='row';row.append(th,el('td','',v1),el('td','',v2));body.append(row);};
    addRow(`ID · ${setting()}`,fmt(score(a)[0]),fmt(score(b)[0])); addRow('Percentile',fmt(score(a)[1],1),fmt(score(b)[1],1));
    data.features.forEach((f,i)=>addRow(f.label,featureValue(f,a.features[i]),featureValue(f,b.features[i])));
    table.append(body);const scroll=el('div','table-scroll');scroll.append(table);panel.append(scroll);
  }
  function renderPlot() {
    const svg=$('scatter'), feature=featureById.get(state.feature);svg.replaceChildren();
    const points=filtered.filter(e=>Number.isFinite(e.features[feature.index])&&Number.isFinite(score(e)[0]));
    $('plot-note').textContent=`${fmt(points.length,0)} excerpts · ${setting()}`;
    $('plot-description').textContent=`${feature.definition} Points follow the explorer filters. Percentiles remain relative to the full aligned population.`;
    $('plot-tooltip').hidden=true;
    const ns='http://www.w3.org/2000/svg'; const s=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;};
    if(!points.length){svg.append(s('text',{x:500,y:180,'text-anchor':'middle',class:'axis-label'},'No available measurements for these filters.'));return;}
    let xmin=Math.min(...points.map(e=>e.features[feature.index])), xmax=Math.max(...points.map(e=>e.features[feature.index])),ymin=Math.min(...points.map(e=>score(e)[0])),ymax=Math.max(...points.map(e=>score(e)[0]));
    if(xmin===xmax){xmin-=.5;xmax+=.5;}if(ymin===ymax){ymin-=.5;ymax+=.5;}
    const pad=(ymax-ymin)*.05;ymin-=pad;ymax+=pad;
    const x=v=>78+(v-xmin)/(xmax-xmin)*892, y=v=>305-(v-ymin)/(ymax-ymin)*275;
    for(let i=0;i<=4;i++){const xx=xmin+(xmax-xmin)*i/4,yy=ymin+(ymax-ymin)*i/4;svg.append(s('line',{x1:78,x2:970,y1:y(yy),y2:y(yy),class:'plot-grid'}),s('text',{x:64,y:y(yy)+4,'text-anchor':'end',class:'axis-label'},fmt(yy,1)),s('text',{x:x(xx),y:328,'text-anchor':'middle',class:'axis-label'},featureValue(feature,xx)));}
    svg.append(s('text',{x:524,y:355,'text-anchor':'middle',class:'axis-title'},feature.label),s('text',{transform:'translate(18 170) rotate(-90)','text-anchor':'middle',class:'axis-title'},'Measured pointwise ID'));
    const tooltip=$('plot-tooltip');
    for(const e of [...points.filter(e=>e.id!==state.example&&e.id!==state.compare),...points.filter(e=>e.id===state.compare||e.id===state.example)]) {
      const selected=e.id===state.example,pinned=e.id===state.compare;
      const c=s('circle',{cx:x(e.features[feature.index]),cy:y(score(e)[0]),r:selected?6:pinned?5:3.3,class:'plot-point'+(selected?' selected':'')+(pinned?' pinned':''),'data-example':e.id});
      const label=`Excerpt #${e.queryIndex}: ${feature.label} ${featureValue(feature,e.features[feature.index])}; ID ${fmt(score(e)[0])}. ${e.text}`;c.append(s('title',{},label));
      const show=event=>{tooltip.textContent=`#${e.queryIndex} · ${featureValue(feature,e.features[feature.index])} · ID ${fmt(score(e)[0])}\n${e.text.slice(0,180)}${e.text.length>180?'…':''}`;tooltip.hidden=false;const rect=svg.parentElement.getBoundingClientRect();tooltip.style.left=Math.min(event.clientX-rect.left+12,Math.max(8,rect.width-290))+'px';tooltip.style.top=Math.max(0,event.clientY-rect.top-70)+'px';};
      c.addEventListener('mousemove',show);c.addEventListener('mouseleave',()=>tooltip.hidden=true);c.addEventListener('click',()=>{selectExample(e.id);const i=filtered.findIndex(v=>v.id===e.id);page=Math.floor(i/pageSize);renderList();$('explorer').scrollIntoView({behavior:'smooth'});});svg.append(c);
    }
  }
  function renderResearch() {
    for(const f of results.figures) {
      const card=el('figure','figure-card'),open=button('',()=>{$('large-figure').src=f.png;$('large-figure').alt=f.caption;$('large-caption').textContent=`Figure ${f.number}. ${f.caption}`;$('figure-dialog').showModal();},'figure-image');
      const img=el('img');img.src=f.png;img.alt=`Figure ${f.number}. ${f.caption}`;img.loading='lazy';open.append(img);card.append(open);
      const cap=el('figcaption');cap.append(el('strong','',`Figure ${f.number}`),el('p','',f.caption));const downloads=el('div','figure-links');if(f.pdf)downloads.append(link('PDF ↓',f.pdf));downloads.append(link('PNG ↓',f.png));cap.append(downloads);card.append(cap);$('figure-gallery').append(card);
    }
    for(const t of results.tables) {
      const details=el('details','table-item'),summary=el('summary');summary.append(el('span','',`Table ${t.number}`),el('strong','',t.title));details.append(summary,el('p','table-caption',t.caption));
      const downloads=el('div','table-downloads');downloads.append(link('Download CSV ↓',t.csv),link('Original table TeX ↓',t.tex));details.append(downloads);
      const table=el('table','result-table');table.setAttribute('aria-label',`Table ${t.number}: ${t.title}`);const body=el('tbody');t.rows.forEach((cells,i)=>{const tr=el('tr');cells.forEach((cell,j)=>{const c=el(i===0?'th':'td','',cell);c.colSpan=t.colspans?.[i]?.[j]||1;tr.append(c);});body.append(tr);});table.append(body);const scroll=el('div','table-scroll');scroll.append(table);details.append(scroll);$('tables').append(details);
    }
    $('archive-count').textContent=`(${results.archive.length} files)`;
    for(const a of results.archive)$('archive-files').append(link(a.name,a.url,''));
  }
  function downloadFiltered() {
    const escape=v=>'"'+String(v??'').replaceAll('"','""')+'"';
    const rows=[['query_index','text','source','model','layer','estimator','measured_id','percentile',...data.features.map(f=>f.id)]];
    for(const e of filtered)rows.push([e.queryIndex,e.text,e.source,state.model,layer().number,state.estimator,...score(e),...e.features]);
    const blob=new Blob([rows.map(r=>r.map(escape).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'});const url=URL.createObjectURL(blob);const a=link('',url);a.download=`excerpts-${state.model}-layer${layer().number}-${state.estimator}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  for(const source of sources){const o=el('option','',source);o.value=source;$('source').append(o);}
  const familyOptions=new Map(); for(const f of data.features){if(!familyOptions.has(f.family)){const g=el('optgroup');g.label=f.family;familyOptions.set(f.family,g);$('plot-feature').append(g);}const o=el('option','',f.label);o.value=f.id;familyOptions.get(f.family).append(o);}
  for(const key of ['model','estimator','source','band','sort'])$(key).addEventListener('change',()=>{state[key]=$(key).value;applyFilters();});
  let searchTimer;$('search').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{state.search=$('search').value;applyFilters();},150);});
  $('plot-feature').addEventListener('change',()=>{state.feature=$('plot-feature').value;applyFilters(false);});
  for(const b of $('depth-controls').querySelectorAll('button'))b.addEventListener('click',()=>{state.depth=b.dataset.depth;applyFilters();});
  $('reset').addEventListener('click',()=>{Object.assign(state,defaults);applyFilters();});
  $('prev').addEventListener('click',()=>{page=Math.max(0,page-1);renderList();});$('next').addEventListener('click',()=>{page++;renderList();});
  $('download-filtered').addEventListener('click',downloadFiltered);
  $('close-figure').addEventListener('click',()=>$('figure-dialog').close());$('figure-dialog').addEventListener('click',event=>{if(event.target===$('figure-dialog'))$('figure-dialog').close();});
  const hero=byId.get('q-1140')||data.excerpts.find(e=>e.paperExample);$('hero-text').textContent=hero.text;$('hero-source').textContent=`${hero.source} · excerpt #${hero.queryIndex}`;
  for(const d of data.models[0].layers){const row=el('div','hero-depth');row.append(el('span','',`${d.label} · L${d.number}`));const track=el('span','hero-track'),fill=el('span','hero-fill');const p=hero.scores.pythia[d.id].ess[1];fill.style.width=p+'%';track.append(fill);row.append(track,el('strong','',fmt(p,1)));$('hero-depths').append(row);}
  $('hero-open').addEventListener('click',()=>{Object.assign(state,defaults,{example:hero.id});applyFilters();});
  renderResearch();applyFilters();
})();
