// Conservative, whole-question intent recognition. No network or model calls.
// Do not turn a keyword mention inside a longer request into a complete answer.
import {expandAtlasShorthand} from './atlas-input.ts';
type Language='pt'|'en'|'es';
type Topic='condition'|'finish'|'rarity'|'deck'|'energy'|'mana';
function unwrapQuestion(question:string){
 let text=question.trim();
 const quotes:Record<string,string>={'"':'"',"'":"'",'“':'”','‘':'’','«':'»','„':'“'};
 // Only remove enclosing pairs, never quotes or extra requests within a question.
 for(;;){
  const previous=text;
  text=text.replace(/[?!.]+$/,'').trim();
  if(text.length>=2&&quotes[text[0]]===text.at(-1))text=text.slice(1,-1).trim();
  if(text===previous)return text;
 }
}
export function normalizeAtlasQuestion(question:string){
 const normalized=unwrapQuestion(question).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()
  .replace(/near[-‐‑]mint/g,'near mint').trim().replace(/^[¿¡]/,'')
  .replace(/^(?:oi|ola|hello|hi|hola|atlas)[,!]?\s+/,'')
  .replace(/[?!.]+$/,'').trim()
  .replace(/,?\s+(?:por favor|please)$/,'').trim().replace(/\s+/g,' ');
 return expandAtlasShorthand(normalized);
}
const rules:Record<Language,Record<Topic,RegExp[]>>={
 pt:{
  condition:[
   /^(?:qual (?:e )?a diferenca entre|como diferenciar) (?:nm|near mint|lp|mp|dmg) (?:e|de) (?:nm|near mint|lp|mp|dmg)$/,
   /^(?:uma carta )?(?:nm|near mint) e (?:uma carta rara|uma raridade|raridade)$/,
   /^o que (?:quer dizer|significa) (?:nm|near mint|lp|mp|dmg) (?:numa|em uma|na) carta$/,
   /^(?:pode me explicar|me explica|explique) (?:o )?estado de conservacao (?:das cartas|de uma carta)$/
  ],
  finish:[
   /^como (?:diferenciar|distinguir) (?:holo|holografica) de (?:reverse holo|holo invertida)$/,
   /^onde (?:fica|esta) o brilho (?:da|de uma carta) (?:reverse holo|holo invertida)$/,
   /^holo e reverse holo sao a mesma coisa$/,
   /^(?:me explica|me explique|pode explicar) o que e (?:uma carta )?(?:holo|holografica|reverse holo|holo invertida)$/
  ],
  rarity:[
   /^o que (?:significa|quer dizer) (?:o circulo|o losango|a estrela preta) (?:na|numa|em uma) carta (?:de )?pokemon$/
  ],
  deck:[/^quantas cartas (?:tem|ha em) um (?:deck|baralho) de pokemon(?: tcg)?$/],
  energy:[/^para que serve (?:a )?energia no pokemon(?: tcg)?$/],
  mana:[/^para que serve (?:a )?mana (?:no|em) (?:magic|mtg)(?: the gathering)?$/]
 },
 en:{
  condition:[
   /^what (?:does|do) (?:nm|near mint|lp|mp|dmg) mean on a card$/,
   /^what is the difference between (?:nm|near mint|lp|mp|dmg) and (?:nm|near mint|lp|mp|dmg)$/,
   /^is (?:nm|near mint) a rarity$/,
   /^(?:can you explain|explain) card condition$/
  ],
  finish:[
   /^how (?:can i tell|to distinguish) holo from reverse holo$/,
   /^where is the foil on a reverse holo card$/,
   /^are holo and reverse holo the same$/
  ],
  rarity:[/^what does the (?:black star|circle|diamond) on a pokemon card mean$/],
  deck:[/^how many cards are in a pokemon(?: tcg)? deck$/],
  energy:[/^what is energy (?:used )?for in pokemon(?: tcg)?$/],
  mana:[/^what is mana (?:used )?for in (?:magic|mtg)(?: the gathering)?$/]
 },
 es:{
  condition:[
   /^que significa (?:nm|near mint|lp|mp|dmg) en una carta$/,
   /^cual es la diferencia entre (?:nm|near mint|lp|mp|dmg) y (?:nm|near mint|lp|mp|dmg)$/,
   /^(?:nm|near mint) es una rareza$/,
   /^(?:puedes explicar|explica) el estado de conservacion de las cartas$/
  ],
  finish:[
   /^como (?:diferenciar|distinguir) holo de reverse holo$/,
   /^donde esta el brillo de una carta reverse holo$/,
   /^holo y reverse holo son lo mismo$/
  ],
  rarity:[/^que significa (?:el rombo|el circulo|la estrella negra) en una carta pokemon$/],
  deck:[/^cuantas cartas tiene un mazo de pokemon(?: tcg)?$/],
  energy:[/^para que sirve (?:la )?energia en pokemon(?: tcg)?$/],
  mana:[/^para que sirve (?:el )?mana en (?:magic|mtg)(?: the gathering)?$/]
 }
};
export function matchCollectorIntent(question:string):{topic:Topic;language:Language}|null{
 const text=normalizeAtlasQuestion(question);
 // Preserve Spanish evidence before accent folding (cómo and Portuguese como collide).
 const languages:Language[]=/[¿¡]|\bcómo\b/i.test(question)?['es','pt','en']:['pt','en','es'];
 for(const language of languages){
  for(const topic of ['condition','finish','rarity','deck','energy','mana'] as const){
   if(rules[language][topic].some(pattern=>pattern.test(text)))return {topic,language};
  }
 }
 return null;
}
