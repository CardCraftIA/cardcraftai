import 'server-only';
import {HttpError,readLimited} from './limits';
export {HttpError} from './limits';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';
import { supabaseConfig, LEGAL_VERSION } from './config';
export async function serverClient() {
  const {url,key,configured}=supabaseConfig();
  if (!configured) throw new HttpError(503,'Autenticação ainda não configurada neste ambiente.');
  const jar=await cookies();
  return createServerClient(url,key,{cookies:{getAll:()=>jar.getAll(),setAll:values=>{values.forEach(({name,value,options})=>jar.set(name,value,options));}}});
}

export function fail(error:unknown){return NextResponse.json({error:error instanceof HttpError ? error.message : 'Não foi possível concluir. Tente novamente mais tarde.'},{status:error instanceof HttpError ? error.status : 503,headers:{'Cache-Control':'private, no-store'}});}
export function json(value:unknown,status=200){return NextResponse.json(value,{status,headers:{'Cache-Control':'private, no-store'}});}
export function sameOrigin(request:Request){if(request.headers.get('origin')!==new URL(request.url).origin)throw new HttpError(403,'Origem da solicitação inválida.');}
export async function account(requireLegal=true){
  const db=await serverClient();
  const {data,error}=await db.auth.getUser();
  if(error||!data.user)throw new HttpError(401,'Entre na sua conta para continuar.');
  if(!data.user.email_confirmed_at)throw new HttpError(403,'Confirme seu e-mail antes de continuar.');
  if(requireLegal){const legal=await db.from('legal_acceptances').select('id').eq('user_id',data.user.id).eq('terms_version',LEGAL_VERSION).eq('privacy_version',LEGAL_VERSION).limit(1);if(legal.error)throw new HttpError(503,'Não foi possível verificar seu aceite.');if(!legal.data?.length)throw new HttpError(403,'Leia e aceite os termos na página Entrar.');}
  return {db,user:data.user};
}
export async function body(request:Request,max=20000){const text=new TextDecoder().decode(await readLimited(request,max));try{return JSON.parse(text);}catch{throw new HttpError(400,'Dados inválidos.');}}
