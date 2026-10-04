import {serverClient,sameOrigin,json,fail} from '@/lib/server';
export async function POST(r:Request){try{sameOrigin(r);const db=await serverClient();const result=await db.auth.signOut();if(result.error)throw new Error();return json({ok:true});}catch(e){return fail(e);}}
