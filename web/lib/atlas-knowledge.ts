import {lookupCollectorGuide} from './atlas-collector-guides.ts';
import {lookupBeginnerGuide} from './atlas-beginner.ts';
import {lookupBuyingGuide} from './atlas-buying.ts';
import {repairAtlasSpelling} from './atlas-input.ts';
import {matchCollectorIntent,normalizeAtlasQuestion} from './atlas-question-intents.ts';
import {lookupAtlasGlossary} from './atlas-glossary.ts';
// Curated explanations, not per-card catalog records or learned model output.
// Extend only with reviewed sources, translations and negative matching tests.
type Language='pt'|'en'|'es';
type Topic='finish'|'rarity';
const reference={title:'TCGplayer — Pokémon TCG rarities',url:'https://help.tcgplayer.com/hc/en-us/articles/360025636074-What-are-the-rarities-of-Pok%C3%A9mon-TCG-cards'};
const answers:Record<Language,Record<Topic,string>>={
 pt:{
  finish:'No Pokémon TCG, Holo tradicional tem brilho na ilustração; Reverse Holo costuma ter brilho ao redor dela, mantendo a ilustração sem foil. O acabamento exato varia conforme a coleção e a edição: essa regra visual não é universal. Confira a variante no catálogo da coleção. Brilho, sozinho, não determina valor nem comprova autenticidade.',
  rarity:'No Pokémon TCG, os símbolos básicos são: círculo = comum; losango = incomum; estrela = rara. Existem outras categorias e exceções conforme a coleção. Raridade e acabamento são coisas diferentes: uma versão Reverse Holo não transforma automaticamente uma carta comum em rara. Para identificar uma edição, confira também a coleção e o número.'
 },
 en:{
  finish:'In Pokémon TCG, traditional Holo has a foil illustration; Reverse Holo usually has foil around the illustration, leaving the illustration non-foil. The exact finish varies by set and edition, so this visual rule is not universal. Check the variant in the set catalog. Shine alone does not determine value or prove authenticity.',
  rarity:'In Pokémon TCG, the basic symbols are: circle = common; diamond = uncommon; star = rare. Other categories and exceptions depend on the set. Rarity and finish are different: a Reverse Holo version does not automatically make a common card rare. Also check the set and collector number to identify an edition.'
 },
 es:{
  finish:'En Pokémon TCG, Holo tradicional tiene brillo en la ilustración; Reverse Holo suele tener brillo alrededor de ella y deja la ilustración sin foil. El acabado exacto varía según la colección y la edición: esta regla visual no es universal. Consulta la variante en el catálogo de la colección. El brillo por sí solo no determina el valor ni demuestra autenticidad.',
  rarity:'En Pokémon TCG, los símbolos básicos son: círculo = común; rombo = poco común; estrella = rara. Existen otras categorías y excepciones según la colección. Rareza y acabado son diferentes: una versión Reverse Holo no convierte automáticamente una carta común en rara. Comprueba también la colección y el número para identificar una edición.'
 }
};
// Full-question matching is deliberate: never answer only part of a compound request.
const patterns:Record<Language,Record<Topic,RegExp>>={
 pt:{
  finish:/^(?:(?:qual (?:e )?a diferenca entre|explique a diferenca entre) (?:holo|holografica) e (?:reverse holo|holo invertida)|(?:o que (?:e|significa)|explique) (?:uma carta )?(?:holo|reverse holo|holografica|holo invertida))(?: no pokemon(?: tcg)?)?$/,
  rarity:/^(?:quais (?:sao )?os simbolos de raridade|o que significam os simbolos de raridade|como identificar a raridade de uma carta)(?: (?:no|de) pokemon(?: tcg)?)?$/
 },
 en:{
  finish:/^(?:(?:what is the difference between|explain the difference between) holo and reverse holo|(?:what is|explain) (?:a )?(?:holo|reverse holo)(?: card)?)(?: in pokemon(?: tcg)?)?$/,
  rarity:/^(?:what are the rarity symbols|what do the rarity symbols mean|how to identify (?:a card.s )?rarity)(?: in pokemon(?: tcg)?)?$/
 },
 es:{
  finish:/^(?:(?:cual es la diferencia entre|explica la diferencia entre) holo y reverse holo|(?:que (?:es|significa)|explica) (?:una carta )?(?:holo|reverse holo|holografica|holo invertida))(?: en pokemon(?: tcg)?)?$/,
  rarity:/^(?:cuales son los simbolos de rareza|que significan los simbolos de rareza|como identificar la rareza de una carta)(?: (?:en|de) pokemon(?: tcg)?)?$/
 }
};
function lookupExactKnowledge(question:string,options:{hasAttachment?:boolean;cardId?:string}={}){
 if(options.hasAttachment||options.cardId||question.length>240)return null;
 const intent=matchCollectorIntent(question);
 const normalized=normalizeAtlasQuestion(question);
 for(const language of ['pt','en','es'] as const){
  for(const topic of ['finish','rarity'] as const){
   if((intent?.topic===topic&&intent.language===language)||patterns[language][topic].test(normalized))return {
    answer:answers[language][topic],source:'knowledge' as const,language,topicId:topic,
    sourceLabel:{pt:'Base revisada do Atlas · sem geração por IA',en:'Atlas reviewed knowledge · no AI generation',es:'Base revisada de Atlas · sin generación por IA'}[language],
    references:[reference],reviewedAt:'2026-11-19'
   };
  }
 }
 return lookupAtlasGlossary(question,options)??lookupCollectorGuide(question,options)??lookupBeginnerGuide(question,options)??lookupBuyingGuide(question,options);
}
export function lookupAtlasKnowledge(question:string,options:{hasAttachment?:boolean;cardId?:string}={}){
 if(options.hasAttachment||options.cardId||question.length>240)return null;
 // Never let spelling repair replace a question already understood exactly.
 const exact=lookupExactKnowledge(question,options);
 if(exact)return exact;
 const normalized=normalizeAtlasQuestion(question);
 const repaired=repairAtlasSpelling(normalized);
 if(repaired===normalized)return null;
 const spanish=/[¿¡]|\bcómo\b/i.test(question);
 return lookupExactKnowledge((spanish?'¿':'')+repaired,options);
}
