import type {Metadata} from 'next';
import Link from 'next/link';
import {Navigation} from './components/navigation';
import './style.css';
export const metadata:Metadata={title:{default:'CardCraftAI · Descubra o universo TCG',template:'%s · CardCraftAI'},description:'Explore cartas TCG, converse com Atlas e organize sua coleção.'};
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>){return <html lang="pt-BR"><body><a className="skip" href="#conteudo">Pular para conteúdo</a><Navigation/><div id="conteudo">{children}</div><footer><Link href="/">✦ CardCraftAI</Link><span>Descubra. Colecione. Compartilhe.</span><div><Link href="/planos">Planos</Link> · <Link href="/legal">Termos e privacidade</Link></div></footer></body></html>;}
