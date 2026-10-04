import {AtlasChat} from '../components/atlas-chat';
export default async function Page({searchParams}:{searchParams:Promise<{card?:string}>}){const {card}=await searchParams;return <main className="page chat-page"><AtlasChat initialCard={typeof card==='string'?card.slice(0,80):''}/></main>;}
