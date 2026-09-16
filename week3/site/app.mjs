import {Engine,investigate,providerRequest,USER,STORAGE_KEY} from './engine.mjs';
const $=id=>document.getElementById(id);
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fixture=await fetch('./fitness.json').then(r=>{if(!r.ok)throw new Error('Cannot load sample data.');return r.json();});
let engine;
try {engine=new Engine(fixture,localStorage);}catch(error){$('notice').hidden=false;$('notice').textContent=error.message;throw error;}
let config={provider:'openrouter',base:'https://openrouter.ai/api/v1',key:'',model:''};
let busy=false,needsClarification=false,history=[],liveTrace=[],selection=null;
const ready=()=>Boolean(config.model&&(config.key||config.provider==='litellm'));
const notice=(message,type='')=>{const box=$('notice');box.textContent=message;box.className=`notice ${type}`;box.hidden=!message;};
async function action(fn){
  if(busy)return;busy=true;document.body.classList.add('busy');renderControls();
  try {
    const run=async()=>{engine.load();await fn();};
    if(navigator.locks)await navigator.locks.request('recall-demo-operation',run);else await run();
  }catch(error){notice(error.message,'error');}
  finally{busy=false;document.body.classList.remove('busy');render();}
}
function renderControls(){
  $('investigate').disabled=busy;
  $('investigate').innerHTML=busy?'Working…':'Trace my data <span aria-hidden="true">→</span>';
  $('rehearse').disabled=busy;$('reset').disabled=busy;
  document.querySelectorAll('#approval-controls button').forEach(b=>b.disabled=busy||b.id==='approve'&&!$('consent')?.checked);
}
function renderMap(){
  const req=engine.state.request;
  const graph=req?{records:req.targets,edges:req.edges,roots:req.roots}:{...engine.trace('D1'),roots:['D1']};
  const records=graph.records,positions={};
  const services=['documents','search','personalization'];
  for(const [column,service] of services.entries()) {
    const group=records.filter(r=>r.service===service).sort((a,b)=>{
      const order=['D1','T1','V1','V2','P1','C1','Q1'];return order.indexOf(a.id)-order.indexOf(b.id);
    });
    group.forEach((r,i)=>positions[r.id]={x:22+column*287,y:group.length===1?150:25+i*(260/Math.max(1,group.length-1))});
  }
  let svg='<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#b8a797"/></marker></defs>';
  for(const edge of graph.edges){
    const a=positions[edge.source],b=positions[edge.target];if(!a||!b)continue;
    const gone=engine.inspect(edge.target).state==='absent';
    const path=a.x===b.x?`M ${a.x+116} ${a.y+87} C ${a.x+116} ${a.y+112},${b.x+116} ${b.y-25},${b.x+116} ${b.y}`:`M ${a.x+232} ${a.y+43} C ${a.x+265} ${a.y+43},${b.x-35} ${b.y+43},${b.x} ${b.y+43}`;
    svg+=`<path class="edge ${gone?'gone':''}" d="${path}" marker-end="url(#arrow)"><title>${escape(edge.evidence_id)}: ${escape(edge.source)} → ${escape(edge.target)}</title></path>`;
  }
  for(const r of records){
    const p=positions[r.id],state=engine.inspect(r.id).state;
    const label=engine.state.consent.state==='not_granted'&&r.consent_root?'NOT SHARED YET':{present:'PRESENT',absent:'VERIFIED ABSENT',unknown:'UNABLE TO VERIFY'}[state];
    const icon=state==='absent'?'✓':state==='unknown'?'?':graph.roots.includes(r.id)?'↳':'◇';
    const title=r.title.length>27?r.title.slice(0,26)+'…':r.title;
    svg+=`<g class="node ${state}" data-record="${escape(r.id)}" tabindex="0" role="button" aria-label="Inspect ${escape(r.title)}, ${label}" transform="translate(${p.x},${p.y})"><rect class="card" width="232" height="87" rx="11"/><rect class="icon-bg" x="13" y="14" width="25" height="25" rx="7"/><text class="icon" x="25.5" y="31" text-anchor="middle">${icon}</text><text class="id" x="49" y="25">${escape(r.id)} · ${escape(({documents:'CLUB PORTAL',search:'CLASS BOOKING',personalization:'MEMBER OFFERS'})[r.service])}</text><text class="name" x="13" y="54">${escape(title)}</text><text class="status" x="13" y="73">${label}</text></g>`;
  }
  $('data-map').innerHTML=svg;$('map-count').textContent=`${records.length} linked records`;
  if(selection){
    const r=engine.meta(selection),incoming=graph.edges.filter(e=>e.target===selection);
    $('record-detail').hidden=false;
    $('record-detail').innerHTML=`<strong>${escape(r.title)}</strong> · ${escape(r.id)} · version ${engine.inspect(selection).version}<br>${incoming.length?incoming.map(e=>`Source ${escape(e.source)} · evidence ${escape(e.evidence_id)}`).join('<br>'):'Source record; no upstream dependency in this request.'}`;
  }
}
function renderReceipt(){
  const r=engine.state.request;
  if(!r){
    $('receipt').innerHTML='<div class="empty-seal">↩</div><h3>Nothing changes<br>until you approve.</h3><p>First, we trace the source and its copies. Then you review exactly what will be removed.</p>';
    $('approval-controls').innerHTML='<p class="fineprint">Reads are autonomous.<br>Every deletion waits for your approval.</p>';return;
  }
  const count=r.targets.filter(t=>t.verification==='absent').length;
  const status={awaiting_approval:'REVIEW REQUIRED',approved:'APPROVED',executing:'WITHDRAWING',partial:'PARTIAL WITHDRAWAL',complete:'WITHDRAWAL VERIFIED',interrupted:'READY TO RESUME',needs_new_plan:'SCOPE CHANGED',revoked:'APPROVAL REVOKED'}[r.status]||r.status;
  $('receipt').innerHTML=`<div class="status-tag ${r.status==='complete'?'complete':''}">${escape(status)}</div><div class="tally">${count}<small> / ${r.targets.length}</small></div><p>records independently verified absent</p>${r.origin!=='live_agent'?'<span class="status-tag rehearsal">SCRIPTED REHEARSAL</span>':''}`;
  let controls='';
  if(r.status==='awaiting_approval'){
    controls=`<div class="target-list">${r.targets.map(t=>`<div class="target-row"><strong>${escape(t.id)} · v${t.version}</strong><span>${escape(t.service)}</span></div>`).join('')}</div><p class="fineprint">Withdraw sharing consent, delete these records, and block re-ingestion. Up to two retries. Deletion cannot be undone.</p><label class="consent"><input id="consent" type="checkbox">I approve these removals and ingestion blocks.</label><button id="approve" class="primary full" disabled>Approve & withdraw →</button>`;
    if(needsClarification)controls='<p class="fineprint">Resolve your latest question before approving. This is an earlier preview.</p>';
  }else if(['partial','interrupted','approved','executing'].includes(r.status)){
    const exhausted=r.targets.some(t=>t.attempts>=3&&t.verification!=='absent');
    controls=`<p class="fineprint">${exhausted?'Retry allowance exhausted. Investigate and approve a new plan.':'Progress is saved. Restore the simulated service and continue where you left off.'}</p>${exhausted?'':'<button id="resume" class="primary full">Restore & resume →</button>'}<button id="revoke" class="receipt-download">Revoke further attempts</button>`;
  }else if(r.status==='complete')controls='<p class="fineprint">Every approved target is absent from these connected stores.</p><button id="verify" class="secondary full">Verify again <span>✓</span></button>';
  else controls='<p class="fineprint">Start a fresh investigation to review and approve a new plan.</p>';
  controls+='<button id="download" class="receipt-download">Download receipt ↓</button>';
  $('approval-controls').innerHTML=controls;
}
function renderProof(){
  const hits=engine.search($('search').value);
  $('search-count').textContent=`${hits.length} matches`;
  const offline=engine.state.fault?.mode==='offline';
  $('search-results').innerHTML=(offline?'<span>Offline service excluded. Check the receipt for unknowns.</span>':'')+(hits.length?`<details><summary>Inspect matching records</summary><ul>${hits.map(r=>`<li><strong>${escape(r.id)}</strong> · ${escape(r.content)}</li>`).join('')}</ul></details>`:'<span>No accessible matching records.</span>');
  $('replay').disabled=busy||engine.state.request?.status!=='complete';
  $('preserved').innerHTML=['B1','D2'].map(id=>{const r=engine.inspect(id);return `<div class="preserved-row"><span>${escape(r.title)}</span><span>${r.state==='present'?'UNCHANGED':escape(r.state.toUpperCase())}</span></div>`;}).join('');
}
function renderEvidence(){
  const r=engine.state.request,trace=liveTrace.length?liveTrace:r?.investigation||[];
  $('agent-events').innerHTML=trace.length?trace.map(e=>`<div class="log-event"><small>READ TOOL</small><strong>${escape(e.tool)}</strong> · ${escape(Object.values(e.arguments||{}).join(', '))}<details><summary>Evidence</summary><pre>${escape(JSON.stringify(e.result,null,2))}</pre></details></div>`).join(''):'<p class="fineprint">No live model investigation yet.</p>';
  $('execution-events').innerHTML=r?.events.map(e=>`<div class="log-event"><small>${new Date(e.time).toLocaleTimeString()} · ${escape(e.record_id||'request')}</small>${escape(e.message)}</div>`).join('')||'<p class="fineprint">No changes have been made.</p>';
  $('event-count').textContent=r?` · ${r.events.length} events`:'';
}
function render(){
  renderMap();renderReceipt();renderProof();renderEvidence();renderControls();
  $('connection-label').textContent=ready()?'Model connected':'Connect a model';
  document.querySelector('.connection-dot').classList.toggle('ready',ready());
  $('consent-summary').textContent=({not_granted:'No sharing consent yet · start in Club Portal',active:'Sharing consent active · copies can outlive the form',withdrawn:'Sharing consent withdrawn · check each app’s verification'})[engine.state.consent.state];
  $('mode-label').textContent=ready()?`Live agent · ${config.model}`:'Live agent · connect a model to begin';
}
$('settings-open').onclick=()=>$('settings-dialog').showModal();
$('about-open').onclick=()=>$('about-dialog').showModal();
$('scenario-open').onclick=()=>$('scenario-dialog').showModal();
$('save-scenario').onclick=()=>{$('scenario-dialog').close();notice($('scenario').value==='healthy'?'Healthy services selected.':`Test scenario selected: ${$('scenario').selectedOptions[0].text}.`);};
$('provider').onchange=()=>{$('base-url').value=$('provider').value==='openrouter'?'https://openrouter.ai/api/v1':'http://localhost:4000/v1';$('api-key').value='';$('model').value='';$('models').replaceChildren();};
const formConfig=()=>({provider:$('provider').value,base:$('base-url').value.trim(),key:$('api-key').value.trim(),model:$('model').value.trim()});
$('load-models').onclick=async()=>{
  const button=$('load-models');button.disabled=true;$('settings-status').textContent='Loading models…';
  try{const result=await providerRequest(formConfig(),'/models');$('models').replaceChildren();let count=0;
    for(const m of result.data||[])if(!m.supported_parameters||m.supported_parameters.includes('tools')){const o=document.createElement('option');o.value=m.id;$('models').append(o);count++;}
    $('settings-status').textContent=`${count} models loaded. Choose one in the model field.`;
  }catch(error){$('settings-status').textContent=error.message;}finally{button.disabled=false;}
};
$('save-settings').onclick=()=>{config=formConfig();if(!ready()){$('settings-status').textContent='Enter a model ID and the required key.';return;}$('settings-dialog').close();render();notice('Model connection selected. Start an investigation when ready.');};
$('investigate').onclick=()=>{
  if(engine.state.consent.state==='not_granted'){notice('Start in Club Portal: give consent and watch the connected apps personalize.','error');return;}
  if(!ready()){$('settings-dialog').showModal();return;}
  if(!$('request').value.trim()){notice('Describe the source you want withdrawn.','error');return;}
  action(async()=>{liveTrace=[];notice('The agent is tracing your data…');
    const request=$('request').value;
    const result=await investigate(engine,config,request,history,entry=>{liveTrace.push(entry);renderEvidence();notice(`Investigating · ${entry.tool.replaceAll('_',' ')}`);});
    needsClarification=result.action==='clarify';history.push({role:'user',content:request},{role:'assistant',content:result.message});
    notice(result.message);selection=null;
  });
};
$('rehearse').onclick=()=>action(async()=>{engine.plan(['D1'],null,'scripted_rehearsal');liveTrace=[];needsClarification=false;selection=null;notice('Scripted rehearsal: seven consent-linked records found. Review the plan before anything changes.');$('replay-result').textContent='';});
$('approval-controls').addEventListener('change',e=>{if(e.target.id==='consent')$('approve').disabled=!e.target.checked||busy;});
$('approval-controls').addEventListener('click',e=>{
  const id=e.target.closest('button')?.id;
  if(id==='download'){
    const blob=new Blob([JSON.stringify(engine.state.request,null,2)],{type:'application/json'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`recall-${engine.state.request.id}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);return;
  }
  if(id==='approve'&&$('consent')?.checked&&!needsClarification)action(async()=>{await engine.approve();const mode=$('scenario').value;engine.fault(mode==='restart'?'healthy':mode);await engine.execute(()=>{renderMap();renderProof();},mode==='restart'?1:0);notice(engine.state.request.status==='complete'?'Withdrawal verified. Every approved target is absent.':'Some work is unfinished. Your progress is saved.',engine.state.request.status==='complete'?'success':'');});
  if(id==='resume')action(async()=>{engine.fault('healthy');await engine.execute(()=>{renderMap();renderProof();});notice(engine.state.request.status==='complete'?'Withdrawal verified. Remaining work completed.':'Some records still need attention.',engine.state.request.status==='complete'?'success':'');});
  if(id==='revoke')action(async()=>{engine.revoke();notice('Further attempts revoked. Completed deletions cannot be reversed.');});
  if(id==='verify')action(async()=>{engine.verify();notice(engine.state.request.status==='complete'?'Verified again: every approved target is absent.':'Verification is incomplete.',engine.state.request.status==='complete'?'success':'');});
});
$('search').oninput=renderProof;
$('replay').onclick=()=>action(async()=>{const result=engine.replay();$('replay-result').textContent=result==='blocked'?'✓ Blocked. The withdrawn search record stays absent.':'This record was outside the withdrawal scope and was inserted.';});
$('reset').onclick=()=>{if(confirm('Reset the synthetic data and all saved withdrawal history?'))action(async()=>{engine.reset();history=[];liveTrace=[];selection=null;needsClarification=false;$('record-detail').hidden=true;$('replay-result').textContent='';notice('Demo reset. All synthetic records restored.');});};
$('data-map').addEventListener('click',e=>{const node=e.target.closest('[data-record]');if(node){selection=node.dataset.record;renderMap();}});
$('data-map').addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();e.target.closest('[data-record]')?.dispatchEvent(new MouseEvent('click',{bubbles:true}));}});
window.addEventListener('storage',e=>{if(e.key===engine.key&&!busy){engine.load();render();}});
render();
