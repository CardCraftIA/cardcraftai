import {supabaseConfig} from '@/lib/config';
import {Login} from '../components/login';
export const dynamic = 'force-dynamic';
export default function Page(){const c=supabaseConfig();return <main className="page narrow"><span className="eyebrow">SUA CONTA CARDCRAFT</span><h1>Bem-vindo à sua coleção.</h1><p>Entre para conversar com o Atlas e guardar suas descobertas.</p><Login url={c.url} publicKey={c.key}/></main>;}
