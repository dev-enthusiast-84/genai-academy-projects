import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {Engine,investigate,providerRequest,STORAGE_KEY} from '../site/engine.mjs';
const golden=JSON.parse(readFileSync(new URL('../data/golden/fixtures.json',import.meta.url)));
const cases=JSON.parse(readFileSync(new URL('../data/golden/cases.json',import.meta.url))).cases;
const fixture=JSON.parse(readFileSync(new URL('../site/demo.json',import.meta.url)));
class Memory {constructor(){this.map=new Map();}getItem(k){return this.map.get(k)||null;}setItem(k,v){this.map.set(k,v);}}
const present=e=>Object.values(e.state.stores).flatMap(s=>Object.keys(s)).sort();
for(const c of cases)test(`Pages ${c.id}: ${c.title}`,async()=>{
  const storage=new Memory();let e=new Engine(golden,storage);
  for(const id of c.initial_state.absent_record_ids)delete e.state.stores[e.meta(id).service][id];e.save();
  if(c.id==='G09'){assert.equal(e.state.request,null);assert.deepEqual(present(e),c.expected.actually_present_record_ids);return;}
  e.plan(['J1'],null,'test_fixture');
  if(c.human_approval)await e.approve();else await assert.rejects(()=>e.execute(),/approval/);
  for(const f of c.faults){e.state.fault={service:f.service,mode:({fail_before_commit:'temporary',commit_then_timeout:'lost_response',unavailable_after_approval:'offline'})[f.mode],remaining:f.count==='persistent'?-1:f.count};e.save();}
  if(c.id==='G05'){e.state.stores.personalization.P1.version=2;e.save();}
  if(c.human_approval)await e.execute(()=>{},c.id==='G04'?1:0);
  if(c.id==='G04'){assert.equal(e.state.request.status,'interrupted');e=new Engine(golden,storage);await e.execute();}
  const r=e.state.request;
  assert.equal(r.status==='needs_new_plan'?'awaiting_approval':r.status,c.expected.status);
  assert.deepEqual(present(e),c.expected.actually_present_record_ids);
  if(c.id==='G03')assert.equal(r.targets.find(t=>t.id==='C1').verification,'unknown');
  const writes=r.events.filter(x=>x.kind==='delete_attempt').map(x=>x.record_id);
  assert.ok(writes.every(id=>c.expected.allowed_new_deletion_ids.includes(id)));
  if(['G04','G07'].includes(c.id))assert.equal(writes.filter(id=>id==='C1').length,1);
  if(c.id==='G08')assert.ok(!writes.includes('C1'));
  assert.throws(()=>e.inspect('J3'),/scope/);
});
test('Pages re-ingestion remains blocked after refresh',async()=>{
  const storage=new Memory();let e=new Engine(fixture,storage);
  e.plan(['D1']);await e.approve();await e.execute();
  e=new Engine(fixture,storage);assert.equal(e.replay(),'blocked');assert.equal(e.inspect('V1').state,'absent');
  assert.equal(e.search('quiet rooms').length,0);assert.equal(e.inspect('D2').state,'present');
});
test('Pages shared-source and new lineage require review',async()=>{
  const e=new Engine(fixture,new Memory());e.plan(['D1']);await e.approve();
  e.state.edges.push({source:'D2',target:'P1',evidence_id:'shared'});e.save();
  assert.equal((await e.execute()).status,'needs_new_plan');assert.equal(e.inspect('D1').state,'present');
  assert.throws(()=>e.plan(['D1']),/another source/);
});
test('Pages approval tampering and revocation cannot delete',async()=>{
  const e=new Engine(fixture,new Memory());e.plan(['D1']);await e.approve();
  e.state.request.targets[0].version=5;
  await assert.rejects(()=>e.execute(),/approval/);assert.equal(e.inspect('D1').state,'present');
  e.plan(['D1']);await e.approve();e.revoke();await assert.rejects(()=>e.execute(),/approval/);
});
test('Pages retry limit survives refresh',async()=>{
  const storage=new Memory();let e=new Engine(fixture,storage);e.plan(['D1']);await e.approve();
  e.state.fault={service:'search',mode:'temporary',remaining:-1};await e.execute();
  e=new Engine(fixture,storage);await e.execute();
  assert.ok(e.state.request.targets.filter(t=>t.service==='search').every(t=>t.attempts===3));
});
test('Pages request retention preserves suppression',async()=>{
  const storage=new Memory();const e=new Engine(fixture,storage);e.plan(['D1']);await e.approve();await e.execute();
  e.state.request.created=Date.now()-86400001;e.save();const restored=new Engine(fixture,storage);
  assert.equal(restored.state.request,null);assert.ok(restored.state.suppression.D1);
});
const call=(name,args)=>({choices:[{message:{role:'assistant',content:null,tool_calls:[{id:crypto.randomUUID(),type:'function',function:{name,arguments:JSON.stringify(args)}}]}}]});
const final=out=>({choices:[{message:{content:JSON.stringify(out)}}]});
test('Pages live investigation code requires read evidence, never writes',async()=>{
  const e=new Engine(fixture,new Memory());
  const sequence=[call('discover_records',{query:'onboarding'}),call('trace_lineage',{root_id:'D1'}),call('inspect_service',{record_id:'V1'}),final({action:'propose',roots:['D1'],targets:['D1','T1','V1','V2','P1','C1'],message:'Review six records.'})];
  const result=await investigate(e,{},'Withdraw D1',[],()=>{},async()=>sequence.shift());
  assert.equal(result.plan.status,'awaiting_approval');assert.equal(result.trace.length,3);assert.equal(e.inspect('D1').state,'present');assert.deepEqual(e.state.suppression,{});
});
test('Pages ambiguous intent produces a clarification',async()=>{
  const e=new Engine(fixture,new Memory());const sequence=[call('discover_records',{query:''}),final({action:'clarify',message:'Which notes?'})];
  const r=await investigate(e,{},'Remove notes',[],()=>{},async()=>sequence.shift());assert.equal(r.action,'clarify');assert.equal(e.state.request,null);
});
test('Pages provider secrets are not exposed in error or storage',async()=>{
  const e=new Engine(fixture,new Memory());
  await assert.rejects(()=>providerRequest({base:'https://example.com/v1',key:'secret'},'/models',null,async()=>({ok:false,status:401,text:async()=>'secret'})),/HTTP 401/);
  assert.ok(!e.storage.getItem(STORAGE_KEY).includes('secret'));
});

const fitness=JSON.parse(readFileSync(new URL('../site/fitness.json',import.meta.url)));
test('Fitness starts without shared personalization and requires explicit consent',async()=>{
 const e=new Engine(fitness,new Memory());
 assert.equal(e.inspect('D1').state,'absent');assert.equal(e.inspect('V2').state,'absent');assert.equal(e.inspect('Q1').state,'absent');assert.equal(e.inspect('B1').state,'present');
 await assert.rejects(()=>e.grantConsent(false),/consent/);assert.throws(()=>e.plan(['D1']),/recorded consent/);
});
test('Fitness one consent automatically populates all three apps with common provenance',async()=>{
 const e=new Engine(fitness,new Memory());await e.grantConsent(true);
 assert.equal(e.inspect('D1').state,'present');assert.equal(e.inspect('V2').state,'present');assert.equal(e.inspect('Q1').state,'present');
 assert.equal(e.state.delegations.length,2);assert.ok(e.state.delegations.every(d=>d.consentId===e.state.consent.id));assert.equal(e.trace('D1').records.length,7);
});
test('Fitness source-only deletion exposes surviving recommendations and offers',async()=>{
 const e=new Engine(fitness,new Memory());await e.grantConsent(true);e.deleteSourceOnly();
 assert.equal(e.inspect('D1').state,'absent');assert.equal(e.inspect('V2').state,'present');assert.equal(e.inspect('Q1').state,'present');assert.equal(e.state.consent.state,'active');
 assert.equal(e.trace('D1').records.length,7);
});
test('Fitness withdrawal survives outage and removes behavior while protecting paid booking',async()=>{
 const storage=new Memory();let e=new Engine(fitness,storage);await e.grantConsent(true);e.deleteSourceOnly();e.plan(['D1']);await e.approve();e.fault('offers_offline');
 await e.execute();assert.equal(e.state.request.status,'partial');assert.equal(e.state.consent.state,'withdrawn');assert.equal(e.state.request.targets.filter(t=>t.verification==='unknown').length,3);
 e=new Engine(fitness,storage);e.fault('healthy');await e.execute();assert.equal(e.state.request.status,'complete');assert.equal(e.inspect('Q1').state,'absent');assert.equal(e.inspect('V2').state,'absent');assert.equal(e.inspect('B1').state,'present');assert.equal(e.replay('D1'),'blocked');assert.equal(e.replay('Q1'),'blocked');
 await assert.rejects(()=>e.grantConsent(true),/withdrawn/);
});
test('Fitness protected booking cannot become a withdrawal target',async()=>{
 const e=new Engine(fitness,new Memory());await e.grantConsent(true);assert.throws(()=>e.plan(['B1']),/source questionnaire/);assert.equal(e.inspect('B1').state,'present');
});
