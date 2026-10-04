import 'server-only';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
export type IndexCard={display_name:string;normalized_name:string;representative_id:string;representative_image:string};
let index:Promise<IndexCard[]>|undefined;
export function loadIndex(){return index??=readFile(path.resolve(process.cwd(),'data/catalog_name_index_tcgdex_en.json'),'utf8').then(raw=>{const d=JSON.parse(raw);if(d.provider!=='tcgdex'||!Array.isArray(d.entries))throw new Error('catalog');return d.entries as IndexCard[];}).catch(e=>{index=undefined;throw e;});}
export type Detail={id:string;name:string;image?:string;localId?:string;category?:string;hp?:number;types?:string[];rarity?:string;illustrator?:string;set?:{id:string;name:string};attacks?:{name:string;effect?:string;damage?:string|number}[];variants?:Record<string,boolean>};
export async function cardDetail(id:string):Promise<Detail|null>{if(!/^[a-zA-Z0-9.-]{1,80}$/.test(id))return null;const r=await fetch('https://api.tcgdex.net/v2/en/cards/'+encodeURIComponent(id),{next:{revalidate:3600},signal:AbortSignal.timeout(9000)});if(r.status===404)return null;if(!r.ok)throw new Error('catalog');const d=await r.json();if(d.id!==id||typeof d.name!=='string')throw new Error('catalog');return d;}
export function safeImage(url:string|undefined){return url&&/^https:\/\/assets\.tcgdex\.net\/[a-zA-Z0-9/._-]+$/.test(url)?url:'';}
export function marketplace(query:string,partner='tcgplayer'){return partner==='amazon'?'https://www.amazon.com.br/s?k='+encodeURIComponent(query):'https://www.tcgplayer.com/search/all/product?q='+encodeURIComponent(query);}
