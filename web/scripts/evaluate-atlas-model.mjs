import {cases} from './fixtures/atlas-comprehension.mjs';
import {atlasModelConfig,askAtlasModel} from '../lib/atlas-model.ts';
import {parseAtlasHistory} from '../lib/atlas-conversation.ts';

// Listing is offline. --live makes real calls to the configured, owned endpoint.
// No keys in arguments, files or logs. Set server-only credentials in the environment.
const selectedId=process.argv.find(a=>a.startsWith('--case='))?.slice(7);
const selected=selectedId?cases.filter(c=>c.id===selectedId):cases;
if(!selected.length)throw new Error('Unknown evaluation case');
if(!process.argv.includes('--live')){
 console.log(JSON.stringify({status:'not_run',cases:selected},null,2));
}else{
 const config=atlasModelConfig(process.env);
 for(const item of selected){
  const start=Date.now();
  try{
   const result=await askAtlasModel(config,item.question,parseAtlasHistory(JSON.stringify(item.history||[])),null);
   console.log(JSON.stringify({id:item.id,question:item.question,history:item.history||[],expect:item.expect,result,elapsedMs:Date.now()-start,verdict:'needs_human_review'}));
  }catch{console.log(JSON.stringify({id:item.id,status:'provider_failed',elapsedMs:Date.now()-start}));}
 }
}
