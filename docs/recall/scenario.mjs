import {Engine} from './engine.mjs';
const $=id=>document.getElementById(id),esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const e=new Engine(await fetch('./fitness.json').then(r=>r.json()),localStorage);
function render(){
 const c=e.state.consent,granted=c.state!=='not_granted',withdrawn=c.state==='withdrawn',deleted=granted&&!e.state.stores.documents.D1;
 $('step-consent').className='scenario-step '+(granted?'complete':'active');
 $('step-delete').className='scenario-step '+(deleted?'complete':granted?'active':'');
 $('step-withdraw').className='scenario-step '+(e.state.request?.status==='complete'?'complete':deleted?'active':'');
 $('consent-node').innerHTML=`<strong>Club Portal · original permission</strong><p>${!granted?'No sharing permission yet.':withdrawn?'Permission withdrawn. Further sharing blocked.':`Consent ${esc(c.id)} · recommendations and invitations permitted.`}</p>`;
 for(const [service,id,name]of [['search','booking-node','Class Booking'],['personalization','offers-node','Member Offers']]){
  const delegation=e.state.delegations.find(d=>d.to===service);
  const online=!(e.state.fault?.mode==='offline'&&e.state.fault.service===service);
  const present=Object.values(e.state.stores[service]).filter(r=>r.consent_root==='D1').length;
  $(id).className='share-node '+(delegation?'received':'');
  $(id).innerHTML=`<strong>${name} · ${delegation?'received shared interests':'waiting for consent'}</strong><p>${!delegation?'Nothing shared before your approval.':!online?'App unavailable · removal unverified.':withdrawn?`${present} consent-linked records remain. ${present?'Withdrawal still in progress.':'Personalization removed.'}`:`${present} linked records · shared by Club Portal under consent ${esc(delegation.consentId)}.`}</p>`;
 }
 $('sharing-events').innerHTML=e.state.sharingEvents.map(ev=>`<li>${new Date(ev.time).toLocaleTimeString()} · ${esc(({documents:'Club Portal',search:'Class Booking',personalization:'Member Offers'})[ev.service])} — ${esc(ev.event)}</li>`).join('')||'<li>No sharing has occurred.</li>';
}
$('reset-scenario').onclick=async()=>{if(!confirm('Reset all synthetic customer apps and withdrawal history?'))return;const run=()=>{e.reset();render();location.reload();};if(navigator.locks)await navigator.locks.request('recall-demo-operation',run);else run();};
window.addEventListener('storage',event=>{if(event.key===e.key){e.load();render();}});render();
