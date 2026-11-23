import {lookupAtlasKnowledge} from './atlas-knowledge.ts';

// Reuse the reviewed answers rather than copying knowledge into a second database.
// This small corpus is sent in full: no keyword filter can hide a relevant topic.
const seeds=[
 ['finish','Qual a diferença entre Holo e Reverse Holo?'],
 ['rarity','Quais são os símbolos de raridade?'],
 ['condition','O que é Near Mint?'],
 ['mana','O que é mana no Magic?'],
 ['energy','O que é energia no Pokémon?'],
 ['deck','O que é um deck no Pokémon?'],
 ['storage','Como proteger minhas cartas?'],
 ['sleeves','Qual a diferença entre sleeve e toploader?'],
 ['cleaning','Como limpar minhas cartas?'],
 ['grading','O que é grading?'],
 ['grading-condition','Near Mint é a mesma coisa que PSA 10?'],
 ['identify-set','Como descobrir a coleção da minha carta?'],
 ['collector-number','O que significa o número 123/100?'],
 ['promo','O que é uma carta promo?'],
 ['edition','Qual a diferença entre primeira edição e reimpressão?'],
 ['starting-collection','Como começar uma coleção?'],
 ['where-to-buy','Onde consigo comprar cartas raras?'],
 ['singles-or-packs','Devo comprar cartas avulsas ou boosters?'],
] as const;

export type AtlasEvidence={id:string;question:string;text:string;reviewedAt:string;references:{title:string;url:string}[]};
export function atlasEvidence():AtlasEvidence[]{
 return seeds.map(([id,question])=>{
  const answer=lookupAtlasKnowledge(question);
  if(!answer||answer.topicId!==id)throw new Error('Atlas evidence registry is incomplete');
  return {id,question,text:answer.answer,reviewedAt:answer.reviewedAt,references:[...answer.references]};
 });
}
