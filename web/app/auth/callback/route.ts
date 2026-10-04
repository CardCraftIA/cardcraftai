import {NextResponse} from 'next/server';
import {serverClient} from '@/lib/server';
export async function GET(request:Request){const url=new URL(request.url);const code=url.searchParams.get('code');try{if(code){const db=await serverClient();const {error}=await db.auth.exchangeCodeForSession(code);if(!error)return NextResponse.redirect(new URL(url.searchParams.get('recovery')==='1'?'/login?recovery=1':'/login?connected=1',url.origin));}}catch{}return NextResponse.redirect(new URL('/login?error=callback',url.origin));}
