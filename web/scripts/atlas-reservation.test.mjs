import test from 'node:test';
import assert from 'node:assert/strict';
import {withAtlasReservation} from '../lib/atlas-reservation.ts';

function fixture({allowed=true, duplicate=false, settlementErrors=0}={}) {
 const calls=[]; let errors=settlementErrors;
 const db={rpc:async(name,args)=>{
  calls.push({name,args});
  if(name==='reserve_atlas_web_question')return {data:{allowed,duplicate},error:null};
  if(errors-->0)return {data:null,error:new Error('network')};
  return {data:{status:args.p_success?'completed':'refunded',remaining:args.p_success?4:5},error:null};
 }};
 return {db,calls};
}
test('success settles before returning without leaking the capability',async()=>{
 const {db,calls}=fixture(); const result=await withAtlasReservation(db,'request',async()=>({answer:'Pikachu'}));
 assert.deepEqual(result,{value:{answer:'Pikachu'},remaining:4});
 assert.equal(calls[1].args.p_success,true);
 assert.equal(calls[0].args.p_token,calls[1].args.p_token);
 assert.match(calls[0].args.p_token,/^[0-9a-f-]{36}$/);
});
test('provider failure refunds the same reservation',async()=>{
 const {db,calls}=fixture();
 await assert.rejects(withAtlasReservation(db,'request',async()=>{throw new Error('provider secret');}),e=>e.status===503&&e.message.includes('devolvida')&&!e.message.includes('secret'));
 assert.equal(calls[1].args.p_success,false);
 assert.equal(calls[0].args.p_token,calls[1].args.p_token);
});
test('duplicate and exhausted quota never invoke provider',async()=>{
 for(const duplicate of [true,false]){
  const {db,calls}=fixture({allowed:false,duplicate});let invoked=false;
  await assert.rejects(withAtlasReservation(db,'request',async()=>{invoked=true;}),e=>e.status===(duplicate?409:402));
  assert.equal(invoked,false);assert.equal(calls.length,1);
 }
});
test('settlement retries preserve request identity',async()=>{
 const {db,calls}=fixture({settlementErrors:1});
 await withAtlasReservation(db,'request',async()=>'answer');
 assert.deepEqual(calls[1],calls[2]);
});
test('unconfirmed refund does not promise immediate restoration',async()=>{
 const {db}=fixture({settlementErrors:2});
 await assert.rejects(withAtlasReservation(db,'request',async()=>{throw new Error();}),e=>e.message.includes('reconciliada')&&!e.message.includes('devolvida'));
});
test('unconfirmed completion never releases an answer',async()=>{
 const {db}=fixture({settlementErrors:2});
 await assert.rejects(withAtlasReservation(db,'request',async()=>'private answer'),e=>e.status===503);
});
