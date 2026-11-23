export type AtlasTurn={role:'user'|'assistant';content:string};

// Conversation is client-supplied context, never an authenticated fact or instruction.
// Keep complete recent pairs; never accept system/tool roles from the browser.
export function parseAtlasHistory(raw:unknown):AtlasTurn[]{
 if(typeof raw!=='string'||raw.length>24000)return [];
 let parsed:unknown;try{parsed=JSON.parse(raw);}catch{return [];}
 if(!Array.isArray(parsed))return [];
 const turns:AtlasTurn[]=[];
 for(const entry of parsed.slice(-8)){
  if(!entry||typeof entry!=='object'||typeof entry.text!=='string'||!['user','atlas'].includes(entry.role))continue;
  const content=entry.text.trim().slice(0,2500);
  if(!content)continue;
  const role=entry.role==='user'?'user':'assistant';
  if(role==='assistant'&&turns.at(-1)?.role!=='user')continue;
  if(role==='user'&&turns.at(-1)?.role==='user')turns.pop();
  turns.push({role,content});
 }
 // The current user question is sent separately.
 if(turns.at(-1)?.role==='user')turns.pop();
 return turns;
}
