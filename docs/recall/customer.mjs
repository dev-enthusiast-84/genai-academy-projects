import {Engine,USER,STORAGE_KEY} from './engine.mjs';
const $=id=>document.getElementById(id),esc=v=>String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const service=document.body.dataset.app;
const fixture=await fetch('./fitness.json').then(r=>r.json());
const engine=new Engine(fixture,localStorage);
const embedded=new URLSearchParams(location.search).has('embed');
if(embedded)document.body.classList.add('compact');
let busy=false;
const active=id=>Boolean(engine.state.stores[service][id]);
function render(){
  const consent=engine.state.consent;
  let content='';
  if(engine.state.fault?.service===service&&engine.state.fault.mode==='offline')content='<div class="offline"><strong>This app is unavailable.</strong>Recall will keep this app’s removal status unresolved until it can verify the result.</div>';
  else if(service==='documents'){
    content='<div class="eyebrow">MEMBERSHIP / AVERY EXAMPLE</div><h1>Your club.<br>Your choices.</h1><p>Choose how your fitness interests are used.</p><div class="member-card"><small>ACTIVE MEMBERSHIP</small><strong>Avery Example</strong><span>Member since 2024 · Club access included</span></div>';
    if(consent.state==='not_granted')content+='<section class="card"><h2>Find your next favorite class.</h2><div class="interest">Evening yoga · After 6 pm</div><label class="consent-check"><input id="agree" type="checkbox">I agree to share my fitness interests with Class Booking for recommendations and Member Offers for personalized invitations.</label><button id="grant" class="primary" disabled>Agree & share my interests →</button></section>';
    else if(consent.state==='active')content+=`<section class="card"><h2>${active('D1')?'Your fitness interests':'Your questionnaire is deleted.'}</h2><p>${active('D1')?'Evening yoga · After 6 pm':'Your copies in the other apps still exist.'}</p><span class="status warn">SHARING CONSENT ACTIVE</span>${active('D1')?'<button id="delete-source" class="outline">Delete only my questionnaire</button>':'<p style="font-size:11px;margin-top:12px">Deleting this form did not withdraw your permission to share.</p>'}</section><a class="recall-link" href="./index.html#request" target="${embedded?'_top':'_blank'}">Withdraw across all apps with Recall ↗</a>`;
    else content='<div class="eyebrow">MEMBERSHIP / AVERY EXAMPLE</div><h1>Your choices.<br>Respected.</h1><div class="member-card"><small>ACTIVE MEMBERSHIP</small><strong>Avery Example</strong><span>Your membership stays unchanged.</span></div><section class="card"><h2>Sharing consent withdrawn.</h2><p>Sharing permission is off. Recall verifies removal of the questionnaire and its copies; your membership stays active.</p><span class="status good">PERSONALIZATION OFF</span></section>';
  }else if(service==='search'){
    content='<div class="eyebrow">YOUR WEEK IN MOTION</div><h1>Make time<br>to move.</h1><p>A little space in your day. A lot of good.</p><div class="day-strip"><span>MON<strong>14</strong></span><span>TUE<strong>15</strong></span><span>WED<strong>16</strong></span><span>THU<strong>17</strong></span><span>FRI<strong>18</strong></span><span class="selected">SAT<strong>19</strong></span></div>';
    if(active('B1'))content+='<div class="booking-ticket"><div class="booking-time">10<small>AM · SAT</small></div><div><h2>Strength & balance</h2><p>Your Saturday class</p><span class="status good">PAID · CONFIRMED</span></div></div>';
    content+='<div class="section-label">RECOMMENDED FOR YOU</div>';
    content+=active('V2')?'<div class="recommendation"><h2>Evening yoga</h2><p>Wednesday · 7 pm<br>A match for your shared fitness interests.</p><span>PERSONALIZED VIA CLUB PORTAL</span></div>':`<div class="empty">${consent.state==='withdrawn'?'Personalized recommendations removed. Your paid booking is still here.':'No personalized suggestions yet. Share your interests in Club Portal to see a match.'}</div>`;
  }else{
    content='<div class="eyebrow">A LITTLE SOMETHING FOR YOU</div><h1>Your next<br>good thing.</h1><p>Invitations inspired by what you love.</p><div class="offer-art" aria-hidden="true"><span>✳</span></div>';
    content+=active('Q1')?'<div class="invitation"><span class="tag">JUST FOR AVERY</span><h2>Your evening<br>yoga invitation.</h2><p>A complimentary taster this Thursday.<br>Because you enjoy evening yoga.</p><div class="coupon">QUEUED INVITATION · NOT SENT</div></div>':`<div class="empty"><h2>${consent.state==='withdrawn'?'Your choice comes first.':'Good things take a moment.'}</h2><p>${consent.state==='withdrawn'?'Your audience profile and queued invitation have been removed.':'No personalized invitation yet. We use interests only after you agree in Club Portal.'}</p></div>`;
  }
  $('content').innerHTML=content+'<p id="message" role="status"></p><footer>SYNTHETIC CUSTOMER APP · OWN SERVICE RECORDS</footer>';
  if($('agree'))$('agree').onchange=()=>$('grant').disabled=!$('agree').checked||busy;
  if($('grant'))$('grant').onclick=()=>mutate(async()=>{if(!$('agree').checked)return;await engine.grantConsent(true,render);});
  if($('delete-source'))$('delete-source').disabled=busy;
  if($('delete-source'))$('delete-source').onclick=()=>{if(confirm('Delete only the questionnaire in Club Portal? Sharing consent and copies in the other apps will remain.'))mutate(async()=>engine.deleteSourceOnly());};
}
async function mutate(fn){
  if(busy)return;busy=true;
  try{const run=async()=>{engine.load();await fn();};if(navigator.locks)await navigator.locks.request('recall-demo-operation',run);else await run();}
  catch(error){$('message').textContent=error.message;busy=false;return;}
  busy=false;render();
}
window.addEventListener('storage',e=>{if(e.key===engine.key&&!busy){engine.load();render();}});
render();
