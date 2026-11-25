/* Buildless browser for recorded excerpt profiles and representation geometry. */
(() => {
'use strict';
const D=window.EXPLORER_INDEX, R=window.RESULTS_DATA, $=id=>document.getElementById(id);
if(!D||!R){$('count').textContent='The data index could not be loaded. Reload this page or use the data downloads.';return;}
const byId=new Map(D.excerpts.map(e=>[e.id,e])), features=new Map(D.features.map((f,i)=>[f.id,{...f,index:i}]));
const metrics=new Map(D.neighbourhoodMetrics.map((m,i)=>[m.id,{...m,index:i+5}]));
const localityIds=new Set(D.neighbourhoodCoverage.positions), searchIndex=new Map(D.excerpts.map(e=>[e.id,e.text.normalize('NFKC').toLocaleLowerCase()]));
const defaults={model:'pythia',depth:'intermediate',estimator:'ess',search:'',source:'all',band:'all',sort:'featured',feature:'n_tokens',example:'q-1140',compare:'',plotMode:'feature',measure:'id',scale:'raw',compareModel:'pythia',compareDepth:'late',neighbourK:'1000',neighbourKind:'cumulative',min:'',max:'',localityOnly:'false'};
const state={...defaults}, params=new URLSearchParams(location.search);
for(const k of Object.keys(defaults))if(params.has(k))state[k]=params.get(k);
const valid=(key,values)=>{if(!values.includes(state[key]))state[key]=defaults[key];};
const models=D.models.map(m=>m.id), depths=['early','intermediate','late'];
valid('model',models);valid('compareModel',models);valid('depth',depths);valid('compareDepth',depths);valid('estimator',['ess','mle','fci']);valid('band',['all','low','middle','high']);valid('sort',['featured','high','low','feature','index']);valid('feature',[...features.keys()]);valid('example',[...byId.keys()]);valid('compare',['',...byId.keys()]);valid('plotMode',['feature','compare']);valid('measure',['id',...metrics.keys()]);valid('scale',['raw','percentile']);valid('neighbourK',['100','500','1000','2000','3000']);valid('neighbourKind',['cumulative','shell']);valid('localityOnly',['true','false']);
for(const k of ['min','max'])if(state[k]!==''&&!Number.isFinite(Number(state[k])))state[k]='';
const sources=[...new Set(D.excerpts.map(e=>e.source))].sort();valid('source',['all',...sources]);
let filtered=[], page=0, epoch=0, ready=false, featureQuery='', featureOpen=new Set(['Surface and lexical composition']), neighbourhoodOpen=false, modelComparisonOpen=false;
const pageSize=8, requests=new Map(), neighbourhoodMaps=new Map();
const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
const button=(label,fn,cls='')=>{const b=el('button',cls,label);b.type='button';b.addEventListener('click',fn);return b;};
const link=(label,path)=>{const a=el('a','',label);a.href=path;return a;};
const fmt=(n,digits=2)=>Number.isFinite(n)?n.toLocaleString('en-US',{maximumFractionDigits:digits}):'Unavailable';
const featureValue=(f,n)=>!Number.isFinite(n)?'Unavailable':f.unit==='ratio'?`${fmt(n*100,1)}%`:f.unit==='percent'?`${fmt(n,1)}%`:fmt(n,f.unit==='count'?0:2);
const metricValue=(m,n)=>!Number.isFinite(n)?'Unavailable':m.unit==='ratio'?`${fmt(n*100,2)}${m.id==='same_source_gain'?' pp':'%'}`:fmt(n,m.unit==='count'?0:3);
const model=id=>D.models.find(m=>m.id===(id||state.model));
const layer=(m=state.model,d=state.depth)=>model(m).layers.find(l=>l.id===d);
const setting=(m=state.model,d=state.depth)=>`${model(m).label}, layer ${layer(m,d).number}`;
const key=(m=state.model,d=state.depth)=>`${m}.${d}`;
const estimatorIndex={ess:0,mle:2,fci:4};
const score=(e,m=state.model,d=state.depth,est=state.estimator)=>{const values=window.EXPLORER_GEOMETRY?.[key(m,d)]?.records[e.queryIndex];return values?values.slice(estimatorIndex[est],estimatorIndex[est]+2):[null,null];};
const currentMetric=()=>state.plotMode==='compare'||state.measure==='id'?null:metrics.get(state.measure);
const localRow=e=>neighbourhoodMaps.get(key())?.get(`${e.queryIndex}.${state.neighbourKind}.${state.neighbourK}`);
const valueOf=e=>{const m=currentMetric();return m?localRow(e)?.[m.index]??null:score(e)[state.scale==='percentile'?1:0];};
const persist=()=>{const p=new URLSearchParams();for(const k of Object.keys(defaults))if(state[k]!==defaults[k]&&state[k]!=='')p.set(k,state[k]);try{history.replaceState(null,'',location.pathname+(p.size?'?'+p.toString():'')+location.hash);}catch{/* Local file previews can still be read without URL rewriting. */}};
function loadChunk(kind,k){
 const namespace=kind==='geometry'?'EXPLORER_GEOMETRY':'EXPLORER_NEIGHBOURHOODS';
 const manifest=kind==='geometry'?D.geometryManifest:D.neighbourhoodManifest;
 if(window[namespace]?.[k])return Promise.resolve(window[namespace][k]);
 const requestKey=kind+':'+k;if(requests.has(requestKey))return requests.get(requestKey);
 const promise=new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=manifest[k].path;script.async=true;script.dataset.chunk=requestKey;script.onload=()=>{const payload=window[namespace]?.[k];if(payload)resolve(payload);else reject(new Error('The data file was empty.'));};script.onerror=()=>{requests.delete(requestKey);script.remove();reject(new Error(`Could not load ${kind} measurements for ${k}.`));};document.head.append(script);});
 requests.set(requestKey,promise);return promise;
}
async function loadLocality(k=key()){
 const chunk=await loadChunk('neighbourhood',k);
 if(!neighbourhoodMaps.has(k))neighbourhoodMaps.set(k,new Map(chunk.rows.map(r=>[`${r[0]}.${r[1]}.${r[2]}`,r])));
 return chunk;
}
function showError(error){const box=$('load-error');box.hidden=false;box.replaceChildren(el('span','',error.message+' Your filters are retained.'),button('Retry',()=>update(false)));$('count').textContent='Some measurements are unavailable because a data file failed to load.';}
function syncControls(){
 for(const id of ['model','depth','estimator','source','band','sort'])$(id).value=state[id];
 for(const [id,k]of [['plot-mode','plotMode'],['plot-feature','feature'],['plot-measure','measure'],['chart-scale','scale'],['compare-model','compareModel'],['compare-depth','compareDepth'],['neighbour-k','neighbourK'],['neighbour-kind','neighbourKind'],['feature-min','min'],['feature-max','max']])$(id).value=state[k];
 $('search').value=state.search;$('locality-only').checked=state.localityOnly==='true';
 for(const [id,m]of [['depth',state.model],['compare-depth',state.compareModel]])for(const option of $(id).options){const l=layer(m,option.value);option.textContent=`${l.label} · layer ${l.number}`;}
 $('compare-controls').hidden=state.plotMode!=='compare';$('measure-control').hidden=state.plotMode==='compare';
 $('neighbour-controls').hidden=!currentMetric()&&!neighbourhoodOpen;
 $('chart-scale').disabled=!!currentMetric();
}
async function update(resetPage=true){
 const turn=++epoch;syncControls();$('load-error').hidden=true;$('count').textContent=`Loading ${setting()}…`;$('scatter').classList.add('plot-busy');$('detail').setAttribute('aria-busy','true');
 try{await loadChunk('geometry',key());
  if(state.plotMode==='compare')await loadChunk('geometry',key(state.compareModel,state.compareDepth));
  if(currentMetric()||neighbourhoodOpen)await loadLocality();
  if(modelComparisonOpen)await Promise.all(D.models.flatMap(m=>m.layers.map(l=>loadChunk('geometry',key(m.id,l.id)))));
  if(turn!==epoch)return;
  applyFilters(resetPage);ready=true;persist();render();
 }catch(error){if(turn===epoch)showError(error);}
 finally{if(turn===epoch){$('scatter').classList.remove('plot-busy');$('detail').removeAttribute('aria-busy');}}
}
function applyFilters(resetPage){
 const q=state.search.normalize('NFKC').toLocaleLowerCase().trim(),f=features.get(state.feature),lo=state.min===''?null:Number(state.min),hi=state.max===''?null:Number(state.max);
 filtered=D.excerpts.filter(e=>{const p=score(e)[1],v=e.features[f.index];return(!q||searchIndex.get(e.id).includes(q)||e.id===q||String(e.queryIndex)===q)&&(state.source==='all'||e.source===state.source)&&(state.band==='all'||Number.isFinite(p)&&(state.band==='low'?p<=20:state.band==='high'?p>=80:p>20&&p<80))&&(state.localityOnly!=='true'||localityIds.has(e.queryIndex))&&(lo===null||Number.isFinite(v)&&v>=lo)&&(hi===null||Number.isFinite(v)&&v<=hi);});
 const descending=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)?b-a:Number.isFinite(a)?-1:Number.isFinite(b)?1:0;
 filtered.sort((a,b)=>{let order=0;if(state.sort==='featured')order=Number(b.paperExample)-Number(a.paperExample);if(state.sort==='high')order=descending(valueOf(a),valueOf(b));if(state.sort==='low'){const av=valueOf(a),bv=valueOf(b);order=descending(Number.isFinite(av)?-av:null,Number.isFinite(bv)?-bv:null);}if(state.sort==='feature')order=descending(a.features[f.index],b.features[f.index]);return order||a.queryIndex-b.queryIndex;});
 if(resetPage)page=0;page=Math.min(page,Math.max(0,Math.ceil(filtered.length/pageSize)-1));
 if(filtered.length&&!filtered.some(e=>e.id===state.example))state.example=filtered[0].id;
}
function render(){syncControls();$('count').textContent=`${fmt(filtered.length,0)} / ${fmt(D.meta.population,0)} excerpts · ${setting()} · ${state.estimator.toUpperCase()}`;renderList();renderDetail();renderPinned();renderPlot();}
function select(id,focusDetail=false){if(!byId.has(id))return;state.example=id;const index=filtered.findIndex(e=>e.id===id);if(index>=0)page=Math.floor(index/pageSize);persist();renderList();renderDetail();renderPinned();renderPlot();if(focusDetail){$('detail').focus({preventScroll:true});$('detail').scrollIntoView({behavior:'instant',block:'start'});}}
function renderList(){
 const list=$('excerpt-list');list.replaceChildren();
 if(!filtered.length)list.append(el('p','empty','No excerpts match these filters. Change a filter or reset them.'));
 for(const e of filtered.slice(page*pageSize,(page+1)*pageSize)){
  const wrapper=el('div');wrapper.setAttribute('role','listitem');const b=button('',()=>select(e.id),'excerpt-item'+(e.id===state.example?' selected':''));b.setAttribute('aria-pressed',String(e.id===state.example));
  const top=el('span','excerpt-top');top.append(el('span','',e.id),el('span','',e.source));b.append(top,el('span','excerpt-preview',e.text));
  const [v,p]=score(e),bottom=el('span','excerpt-bottom'),metric=currentMetric();bottom.append(el('strong','',`${state.estimator.toUpperCase()} ID ${fmt(v)}`),el('span','',metric?`${metric.label}: ${metricValue(metric,valueOf(e))}`:Number.isFinite(p)?`${fmt(p,1)}th pct.`:'Unavailable'));b.append(bottom);wrapper.append(b);list.append(wrapper);
 }
 const pages=Math.max(1,Math.ceil(filtered.length/pageSize));$('prev').disabled=page===0;$('next').disabled=page+1>=pages;$('page-number').textContent=`${page+1} / ${pages}`;
}
function addTableRow(body,label,values,cls=''){const tr=el('tr',cls),th=el('th','',label);th.scope='row';tr.append(th,...values.map(v=>el('td',v==='Unavailable'?'unavailable':'',v)));body.append(tr);return tr;}
function estimatorTable(e){
 const table=el('table','measure-table'),head=el('thead'),h=el('tr');for(const label of ['Intrinsic-dimension estimator','Estimate','Percentile'])h.append(el('th','',label));head.append(h);table.append(head);const body=el('tbody');
 for(const estimator of D.estimators){const [v,p]=score(e,state.model,state.depth,estimator.id);const name=estimator.id==='fci'?'Local FCI':estimator.label;const row=addTableRow(body,name,[fmt(v),fmt(p,1)],estimator.id===state.estimator?'current':'');row.dataset.estimator=estimator.id;row.title=`${name}: query-neighbourhood estimate, k=1,000, 15,000 references`;}
 table.append(body);return table;
}
function renderDetail(){
 const panel=$('detail');panel.replaceChildren();if(!filtered.length){panel.append(el('p','empty','No excerpt is selected.'));return;}
 const e=byId.get(state.example),head=el('div','detail-head');head.append(el('strong','',`Excerpt key: ${e.id}`),el('span','',e.source));panel.append(head,el('blockquote','full-excerpt',e.text));
 const sentences=e.features[features.get('n_sentences').index],profileContext=e.featuresAvailable?`${fmt(sentences,0)} parser-detected sentence${sentences===1?'':'s'}`:'Linguistic profile unavailable';panel.append(el('p','excerpt-context',`${setting()} · last non-padding token representation · ${profileContext}`),estimatorTable(e));
 if(!e.featuresAvailable)panel.append(el('p','small muted','No linguistic profile was released for this excerpt. Its text and recorded geometry are available; feature values remain unavailable.'));
 const n=D.meta.validPopulation[`${key()}.${state.estimator}`];panel.append(el('p','measure-caption',`ID estimates use k = 1,000 and 15,000 disjoint references. ${state.estimator.toUpperCase()} percentile denominator: ${fmt(n,0)} available estimates. Missing values are not imputed.`));
 const actions=el('div','detail-actions');actions.append(button('Locate on plot',()=>{const node=$('scatter').querySelector(`[data-example="${e.id}"]`);if(node){node.focus();node.scrollIntoView({behavior:'instant',block:'center'});}else{$('plot-selection').textContent=`${e.id} has no available value for the current plot. Its text and other measurements remain available below.`;}}),button(state.compare===e.id?'Unpin excerpt':'Pin for text comparison',()=>{state.compare=state.compare===e.id?'':e.id;persist();renderDetail();renderPinned();renderPlot();}),button('Copy excerpt link',async event=>{const target=event.currentTarget;try{await navigator.clipboard.writeText(location.href.split('#')[0]+'#explorer');target.textContent='Link copied';}catch{const a=link('Excerpt permalink',location.href.split('#')[0]+'#explorer');actions.append(a);target.disabled=true;}}));panel.append(actions);
 const modelsSection=el('details','detail-section');modelsSection.open=modelComparisonOpen;modelsSection.append(el('summary','','Compare this excerpt across models and layers'));const modelContent=el('div');modelsSection.append(modelContent);panel.append(modelsSection);
 if(modelComparisonOpen)renderModelComparison(e,modelContent);
 modelsSection.addEventListener('toggle',()=>{if(modelsSection.open===modelComparisonOpen)return;modelComparisonOpen=modelsSection.open;if(modelComparisonOpen){modelContent.textContent='Loading the recorded model/layer estimates…';update(false);}});
 const neighbourhood=el('details','detail-section');neighbourhood.open=neighbourhoodOpen;neighbourhood.append(el('summary','','Neighbourhood distances and composition'));const localContent=el('div');neighbourhood.append(localContent);panel.append(neighbourhood);if(neighbourhoodOpen)renderNeighbourhood(e,localContent);
 neighbourhood.addEventListener('toggle',()=>{if(neighbourhood.open===neighbourhoodOpen)return;neighbourhoodOpen=neighbourhood.open;if(neighbourhoodOpen){localContent.textContent='Loading locality diagnostics…';update(false);}else syncControls();});
 const heading=el('div','feature-heading');heading.append(el('h3','','Linguistic features'));const search=el('label','feature-search','Find a feature');const input=el('input');input.type='search';input.value=featureQuery;input.id='feature-search';input.placeholder='Name or definition';search.append(input);heading.append(search);panel.append(heading);
 const profile=el('div');profile.id='feature-profile';panel.append(profile);renderFeatures(e,profile);
 input.addEventListener('input',()=>{featureQuery=input.value;renderFeatures(e,profile);});
}
function renderFeatures(e,container){
 container.replaceChildren();const query=featureQuery.toLocaleLowerCase().trim(),groups=new Map();D.features.forEach((f,i)=>{if(query&&!`${f.label} ${f.id} ${f.definition}`.toLocaleLowerCase().includes(query))return;if(!groups.has(f.family))groups.set(f.family,[]);groups.get(f.family).push([f,i]);});
 if(!groups.size)container.append(el('p','empty','No feature matches this search.'));
 for(const [family,items]of groups){
  const cls=family.includes('Surface')?'raw':family.includes('Morphosyntactic')?'morph':/Clausal|morphology/.test(family)?'verbal':family.includes('frequency')?'frequency':'syntax';const section=el('details','feature-family '+cls);section.open=!!query||featureOpen.has(family)||items.some(([f])=>f.id===state.feature);
  const summary=el('summary','',family);summary.append(el('span','',String(items.length)));section.append(summary);const table=el('table','feature-table'),body=el('tbody');table.setAttribute('aria-label',family);
  for(const [f,i]of items){const row=el('tr','feature-row'+(f.id===state.feature?' active':''));row.dataset.feature=f.id;const name=el('th');name.scope='row';const b=button(f.label,()=>{state.feature=f.id;state.plotMode='feature';featureOpen.add(f.family);persist();update(false).then(()=>{$('detail').querySelector(`[data-feature="${f.id}"] button`)?.focus({preventScroll:true});});});name.append(b,el('code','feature-code',f.id),el('span','feature-help',f.definition));const value=featureValue(f,e.features[i]);row.append(name,el('td',value==='Unavailable'?'unavailable':'',value));body.append(row);}table.append(body);section.append(table);container.append(section);
  section.addEventListener('toggle',()=>{if(section.open)featureOpen.add(family);else featureOpen.delete(family);});
 }
}
function renderModelComparison(e,container){
 const table=el('table','compare-table'),head=el('thead'),row=el('tr');for(const name of ['Model / layer','ESS ID','MLE ID','Local FCI ID',`${state.estimator.toUpperCase()} percentile`])row.append(el('th','',name));head.append(row);table.append(head);const body=el('tbody');
 for(const m of D.models)for(const l of m.layers){const values=['ess','mle','fci'].map(est=>fmt(score(e,m.id,l.id,est)[0]));values.push(fmt(score(e,m.id,l.id)[1],1));addTableRow(body,`${m.label} · ${l.number}`,values,m.id===state.model&&l.id===state.depth?'current':'');}table.append(body);const scroll=el('div','table-scroll');scroll.append(table);container.append(scroll,el('p','small muted','The text and linguistic profile are shared. Every geometry value is measured separately in the named model/layer setting. Percentiles use each setting’s own distribution; raw scales need not match.'));
}
function renderNeighbourhood(e,container){
 if(!localityIds.has(e.queryIndex)){container.append(el('p','small muted','This excerpt was not in the 500-query locality audit. No neighbourhood diagnostics are available for it. Its intrinsic-dimension estimates remain available above.'));return;}
 const row=localRow(e);if(!row){container.append(el('p','small muted','The locality data file has not loaded.'));return;}
 container.append(el('p','small',`${setting()} · neighbour ranks ${row[3]}–${row[2]} · ${fmt(row[4],0)} neighbours · ${state.neighbourKind} interval. Change the diagnostic neighbourhood in the plot controls.`));
 const table=el('table','measure-table neighbourhood-table'),body=el('tbody');
 for(const m of D.neighbourhoodMetrics){const tr=el('tr'),th=el('th');th.scope='row';th.append(el('span','',m.label),el('span','neighbour-definition',m.definition));tr.append(th,el('td','',metricValue(m,row[metrics.get(m.id).index])));body.append(tr);}table.append(body);container.append(table,el('p','small muted','These values come from the recorded locality audit over unnormalised Euclidean representations. They describe a query’s neighbourhood and its corpus/lexical composition, not token-level geometry.'));
}
function renderPinned(){
 const panel=$('comparison');panel.replaceChildren();panel.hidden=!state.compare||!filtered.length;if(panel.hidden)return;panel.className='comparison';const a=byId.get(state.compare),b=byId.get(state.example),head=el('div','detail-head');head.append(el('h3','','Text comparison'),button('Clear pinned excerpt',()=>{state.compare='';persist();renderDetail();renderPinned();renderPlot();}));panel.append(head);
 if(a.id===b.id){panel.append(el('p','small',`${a.id} is pinned. Select another excerpt to compare its ID and linguistic profile.`));return;}
 const texts=el('div','compare-texts');for(const e of [a,b]){const col=el('div');col.append(el('strong','',`${e.id} · ${e.source}`),el('p','',e.text));texts.append(col);}panel.append(texts);const table=el('table','compare-table'),thead=el('thead'),h=el('tr');for(const name of ['Measurement / feature',a.id,b.id])h.append(el('th','',name));thead.append(h);table.append(thead);const body=el('tbody');addTableRow(body,`${state.estimator.toUpperCase()} ID`,[fmt(score(a)[0]),fmt(score(b)[0])]);addTableRow(body,'Within-setting percentile',[fmt(score(a)[1],1),fmt(score(b)[1],1)]);D.features.forEach((f,i)=>addTableRow(body,f.label,[featureValue(f,a.features[i]),featureValue(f,b.features[i])]));table.append(body);const scroll=el('div','table-scroll');scroll.append(table);panel.append(scroll);
}
function plotData(){
 const f=features.get(state.feature),compare=state.plotMode==='compare',metric=currentMetric();return filtered.map(e=>{const x=compare?score(e)[state.scale==='percentile'?1:0]:e.features[f.index];const y=compare?score(e,state.compareModel,state.compareDepth)[state.scale==='percentile'?1:0]:valueOf(e);return{e,x,y};}).filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y));
}
function renderPlot(){
 const svg=$('scatter'),width=Math.min(1080,Math.max(420,svg.parentElement.clientWidth));svg.setAttribute('viewBox',`0 0 ${width} 330`);svg.replaceChildren();$('plot-tooltip').hidden=true;const points=plotData(),f=features.get(state.feature),compare=state.plotMode==='compare',metric=currentMetric();
 const xLabel=compare?`${model().label} L${layer().number} · ${state.scale==='percentile'?'percentile':'ID'}`:f.label;
 const yLabel=compare?`${model(state.compareModel).label} L${layer(state.compareModel,state.compareDepth).number} · ${state.scale==='percentile'?'percentile':'ID'}`:metric?metric.label:`${state.estimator.toUpperCase()} intrinsic dimension${state.scale==='percentile'?' · percentile':''}`;
 $('plot-note').textContent=`${fmt(points.length,0)} plotted excerpts · ${compare?'paired measurements':setting()}${metric?` · ${state.neighbourKind}, k = ${state.neighbourK}`:''}`;
 $('plot-description').textContent=compare?'Paired observations of the same excerpts; changing settings does not change the text.':metric?`${metric.definition} Locality coverage: 500 excerpts from the recorded audit. ID estimates retain k = 1,000.`:f.definition+' Each plotted ID value is a measured neighbourhood estimate. Missing feature/geometry pairs are omitted.';
 const ns='http://www.w3.org/2000/svg',s=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text!==undefined)n.textContent=text;return n;};
 const selected=points.find(p=>p.e.id===state.example);
 const xFormat=v=>compare?fmt(v,2):featureValue(f,v),yFormat=v=>metric?metricValue(metric,v):fmt(v,2);
 $('plot-selection').textContent=selected?`${selected.e.id}: ${xLabel} = ${xFormat(selected.x)}; ${yLabel} = ${yFormat(selected.y)}.`:filtered.length?`${state.example} has no available pair of values for this plot. Its other measurements remain visible below.`:'No excerpts match the current filters.';
 if(!points.length){svg.append(s('text',{x:width/2,y:150,'text-anchor':'middle',class:'axis-label'},'No available measurements for these filters.'));return;}
 let xmin=Math.min(...points.map(p=>p.x)),xmax=Math.max(...points.map(p=>p.x)),ymin=Math.min(...points.map(p=>p.y)),ymax=Math.max(...points.map(p=>p.y));if(xmin===xmax){xmin-=.5;xmax+=.5;}if(ymin===ymax){ymin-=.5;ymax+=.5;}
 if(compare&&state.scale==='percentile'){xmin=ymin=0;xmax=ymax=100;}else{const xp=(xmax-xmin)*.035,yp=(ymax-ymin)*.06;xmin-=xp;xmax+=xp;ymin-=yp;ymax+=yp;}
 const x=v=>90+(v-xmin)/(xmax-xmin)*(width-115),y=v=>265-(v-ymin)/(ymax-ymin)*240;
 for(let i=0;i<=4;i++){const xx=xmin+(xmax-xmin)*i/4,yy=ymin+(ymax-ymin)*i/4;svg.append(s('line',{x1:90,x2:width-25,y1:y(yy),y2:y(yy),class:'plot-grid','aria-hidden':'true'}),s('text',{x:78,y:y(yy)+5,'text-anchor':'end',class:'axis-label','aria-hidden':'true'},metric?metricValue(metric,yy):fmt(yy,1)),s('text',{x:x(xx),y:288,'text-anchor':'middle',class:'axis-label','aria-hidden':'true'},compare?fmt(xx,1):featureValue(f,xx)));}
 if(compare&&state.scale==='percentile')svg.append(s('line',{x1:x(0),x2:x(100),y1:y(0),y2:y(100),class:'plot-diagonal','aria-hidden':'true'}));
 svg.append(s('text',{x:(width+65)/2,y:321,'text-anchor':'middle',class:'axis-title','aria-hidden':'true'},xLabel),s('text',{transform:'translate(19 145) rotate(-90)','text-anchor':'middle',class:'axis-title','aria-hidden':'true'},yLabel));
 const sorted=[...points].sort((a,b)=>a.x-b.x||a.e.queryIndex-b.e.queryIndex),keyboardId=selected?.e.id||points[0].e.id;
 const ordered=[...points.filter(p=>p.e.id!==state.example&&p.e.id!==state.compare),...points.filter(p=>p.e.id===state.compare||p.e.id===state.example)];
 for(const p of ordered){const e=p.e,active=e.id===state.example,pinned=e.id===state.compare,c=s('circle',{cx:x(p.x),cy:y(p.y),r:active?6:pinned?5.5:3.5,class:'plot-point'+(active?' selected':'')+(pinned?' pinned':''),'data-example':e.id,tabindex:e.id===keyboardId?'0':'-1',role:'button','aria-pressed':String(active),'aria-label':`${e.id}: ${xLabel} ${xFormat(p.x)}; ${yLabel} ${yFormat(p.y)}. ${e.text.slice(0,160)}`});
  c.append(s('title',{},`${e.id} · ${xFormat(p.x)} · ${yFormat(p.y)}\n${e.text}`));
  c.addEventListener('click',()=>select(e.id,true));c.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select(e.id,true);}else if(['ArrowRight','ArrowLeft','Home','End'].includes(event.key)){event.preventDefault();const index=sorted.findIndex(q=>q.e.id===e.id),next=event.key==='Home'?0:event.key==='End'?sorted.length-1:Math.max(0,Math.min(sorted.length-1,index+(event.key==='ArrowRight'?1:-1)));select(sorted[next].e.id);queueMicrotask(()=>$('scatter').querySelector(`[data-example="${sorted[next].e.id}"]`)?.focus({preventScroll:true}));}});
  c.addEventListener('mousemove',event=>{const t=$('plot-tooltip'),rect=svg.parentElement.getBoundingClientRect();t.textContent=`${e.id} · ${yLabel}: ${yFormat(p.y)}\n${e.text.slice(0,190)}${e.text.length>190?'…':''}`;t.hidden=false;t.style.left=Math.max(2,Math.min(event.clientX-rect.left+10,rect.width-300))+'px';t.style.top=Math.max(0,event.clientY-rect.top-85)+'px';});c.addEventListener('mouseleave',()=>$('plot-tooltip').hidden=true);svg.append(c);
 }
}
function renderResearch(){
 $('abstract-text').textContent=D.paper.abstract;
 if(D.paper.codeUrl)$('paper-links').append(link('GitHub',D.paper.codeUrl));
 for(const f of R.figures){const figure=el('figure','paper-figure'),open=button('',()=>{$('large-figure').src=f.png;$('large-figure').alt=f.caption;$('large-caption').textContent=`Figure ${f.number}. ${f.caption}`;$('figure-dialog').showModal();},'figure-image');open.setAttribute('aria-label',`Enlarge figure ${f.number}`);const img=el('img');img.src=f.png;img.alt=f.caption;img.loading='lazy';open.append(img);figure.append(open);const caption=el('figcaption');caption.append(el('p','',f.caption));const links=el('div','figure-links');if(f.pdf)links.append(link('PDF',f.pdf));links.append(link('PNG',f.png));caption.append(links);figure.append(caption);([2,7].includes(f.number)?$('principal-figures'):$('other-figures')).append(figure);}
 for(const t of R.tables){const details=el('details','table-item'),summary=el('summary');summary.append(el('span','',`Table ${t.number}`),el('strong','',t.title));details.append(summary,el('p','table-caption',t.caption));const links=el('div','table-downloads');links.append(link('CSV',t.csv));details.append(links);const table=el('table','result-table');table.setAttribute('aria-label',t.title);const body=el('tbody');t.rows.forEach((cells,i)=>{const tr=el('tr');cells.forEach((value,j)=>{const c=el(i===0?'th':'td','',value);c.colSpan=t.colspans?.[i]?.[j]||1;tr.append(c);});body.append(tr);});table.append(body);const scroll=el('div','table-scroll');scroll.tabIndex=0;scroll.setAttribute('aria-label',`Scrollable table ${t.number}`);scroll.append(table);details.append(scroll);$('tables').append(details);}
 $('archive-count').textContent=`(${R.archive.length} files)`;for(const a of R.archive)$('archive-files').append(link(a.name,a.url));
}
async function downloadFiltered(event){
 const b=event.currentTarget;b.disabled=true;b.textContent='Preparing CSV…';
 try{await loadLocality();const fcols=D.features.map(f=>f.id),mcols=D.neighbourhoodMetrics.map(m=>m.id);const header=['query_index','excerpt_key','text','source','text_sha256','model','layer','reference_size','id_k','selected_estimator','ess_id','ess_percentile','mle_id','mle_percentile','local_fci_id','local_fci_percentile','diagnostic_k','diagnostic_kind',...mcols,...fcols];
 if(state.plotMode==='compare')header.push('comparison_model','comparison_layer','comparison_id','comparison_percentile');const rows=[header];
 for(const e of filtered){const local=localRow(e),line=[e.queryIndex,e.id,e.text,e.source,e.textSha256,state.model,layer().number,15000,1000,state.estimator,...['ess','mle','fci'].flatMap(est=>score(e,state.model,state.depth,est)),Number(state.neighbourK),state.neighbourKind,...D.neighbourhoodMetrics.map(m=>local?.[metrics.get(m.id).index]??null),...e.features];if(state.plotMode==='compare')line.push(state.compareModel,layer(state.compareModel,state.compareDepth).number,...score(e,state.compareModel,state.compareDepth));rows.push(line);}
 const cell=v=>'"'+String(v??'').replaceAll('"','""')+'"';const blob=new Blob([rows.map(r=>r.map(cell).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),a=link('',url);a.download=`excerpts-${state.model}-layer${layer().number}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 }catch(error){showError(error);}finally{b.disabled=false;b.textContent='Download filtered CSV';}
}
for(const source of sources){const option=el('option','',source);option.value=source;$('source').append(option);}
const groups=new Map();for(const f of D.features){if(!groups.has(f.family)){const group=el('optgroup');group.label=f.family;groups.set(f.family,group);$('plot-feature').append(group);}const o=el('option','',f.label);o.value=f.id;groups.get(f.family).append(o);}
for(const m of D.neighbourhoodMetrics){const o=el('option','',m.label);o.value=m.id;$('plot-measure').append(o);}
for(const id of ['model','depth','estimator','source','band','sort'])$(id).addEventListener('change',()=>{state[id]=$(id).value;update();});
for(const [id,k]of [['plot-mode','plotMode'],['plot-feature','feature'],['plot-measure','measure'],['chart-scale','scale'],['compare-model','compareModel'],['compare-depth','compareDepth'],['neighbour-k','neighbourK'],['neighbour-kind','neighbourKind'],['feature-min','min'],['feature-max','max']])$(id).addEventListener('change',()=>{state[k]=$(id).value;update();});
$('locality-only').addEventListener('change',()=>{state.localityOnly=String($('locality-only').checked);update();});
let searchTimer;$('search').addEventListener('input',()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{state.search=$('search').value;update();},140);});
$('reset').addEventListener('click',()=>{Object.assign(state,defaults);featureQuery='';update();});
$('prev').addEventListener('click',()=>{page=Math.max(0,page-1);renderList();});$('next').addEventListener('click',()=>{page++;renderList();});
$('download-filtered').addEventListener('click',downloadFiltered);$('close-figure').addEventListener('click',()=>$('figure-dialog').close());$('figure-dialog').addEventListener('click',event=>{if(event.target===$('figure-dialog'))$('figure-dialog').close();});
let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(ready)renderPlot();},100);});
renderResearch();syncControls();update();
})();
