import {createServerClient} from '@supabase/ssr';
import {NextRequest,NextResponse} from 'next/server';
import {supabaseConfig} from './lib/config';
export async function proxy(request:NextRequest){let response=NextResponse.next({request});const {url,key,configured}=supabaseConfig();if(!configured)return response;const db=createServerClient(url,key,{cookies:{getAll:()=>request.cookies.getAll(),setAll:values=>{values.forEach(({name,value})=>request.cookies.set(name,value));response=NextResponse.next({request});values.forEach(({name,value,options})=>response.cookies.set(name,value,options));}}});try{await db.auth.getUser();}catch{}response.headers.set('Cache-Control','private, no-store');return response;}
export const config={matcher:['/login','/auth/:path*','/api/me','/api/auth/:path*','/api/collection','/api/community','/api/atlas']};
