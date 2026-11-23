import {normalizeAtlasQuestion} from './atlas-question-intents.ts';
type Language='pt'|'en'|'es';
type Topic='where-to-buy'|'singles-or-packs';
const patterns:Record<Language,Record<Topic,RegExp[]>>={
 pt:{
  'where-to-buy':[
   /^a?onde (?:eu )?(?:(?:consigo|posso|devo) )?(?:comprar|compro|encontrar|encontro|achar|acho) (?:cartas?|cards?)(?: (?:raras?|raros?|avulsas?|avulsos?))?(?: (?:de )?pokemon)?(?: (?:raras?|avulsas?))?(?: (?:online|pela internet|no brasil))?$/,
   /^(?:em )?qual (?:site|loja) (?:eu )?(?:posso )?(?:comprar|compro|encontro) cartas(?: raras| avulsas)?(?: de pokemon)?$/,
   /^(?:quais|que) (?:lojas|sites) (?:vendem|tem) cartas(?: (?:raras|avulsas))?(?: de pokemon)?$/,
   /^qual (?:loja|site) (?:vende|tem) cartas(?: (?:raras|avulsas))?(?: de pokemon)?$/,
   /^como (?:comprar|encontrar) cartas (?:raras|avulsas)(?: de pokemon)?$/,
   /^(?:quero|gostaria de) comprar cartas(?: (?:raras|avulsas))?(?: de pokemon)?$/
  ],
  'singles-or-packs':[
   /^(?:(?:e )?melhor|vale mais a pena|devo) comprar (?:cartas avulsas ou boosters|boosters ou cartas avulsas)$/,
   /^qual (?:e )?a diferenca entre (?:cartas avulsas e boosters|boosters e cartas avulsas)$/,
   /^comprar cartas avulsas ou boosters$/
  ]
 },
 en:{
  'where-to-buy':[
   /^where (?:can|should|do) i (?:buy|find) (?:rare |single |individual )?(?:pokemon )?cards(?: (?:online|in brazil))?$/,
   /^where to buy (?:rare |single )?(?:pokemon )?cards$/,
   /^which (?:stores|sites) sell (?:rare |single )?(?:pokemon )?cards$/
  ],
  'singles-or-packs':[/^(?:should i|is it better to) buy (?:singles or booster packs|booster packs or singles)$/,
   /^what is the difference between singles and booster packs$/]
 },
 es:{
  'where-to-buy':[
   /^donde (?:puedo |debo )?(?:comprar|encontrar) cartas(?: (?:raras|sueltas))?(?: de pokemon)?(?: en linea| en brasil)?$/,
   /^que (?:tiendas|sitios) venden cartas(?: raras| sueltas)?(?: de pokemon)?$/
  ],
  'singles-or-packs':[/^(?:es mejor|debo) comprar (?:cartas sueltas o sobres|sobres o cartas sueltas)$/,
   /^cual es la diferencia entre cartas sueltas y sobres$/]
 }
};
const answers:Record<Topic,Record<Language,string>>={
 'where-to-buy':{
  pt:'Para procurar uma carta rara específica, busque cartas avulsas em lojas de TCG e marketplaces. Se for Pokémon no Brasil, a MYP Cards tem uma seção de avulsas; o link abaixo é um ponto de pesquisa, não uma oferta verificada. O localizador oficial Pokémon também ajuda a encontrar lojas, mas não informa se terão a carta desejada.\n\nMinha orientação: compare coleção, número, idioma, acabamento e conservação. Confira fotos do exemplar, histórico do vendedor, frete e condições de devolução. Não consultei estoque nem preços atuais e não certifico anúncios. Para uma busca específica, inclua o jogo, a carta e seu país na pergunta.',
  en:'To look for a particular rare card, search for singles at TCG stores and marketplaces. For Pokémon in Brazil, MYP Cards has a singles section; the link below is a starting point, not a verified offer. The official Pokémon locator also helps find stores, but does not establish whether they have your desired card.\n\nMy guidance: compare set, number, language, finish and condition. Check photos of the actual card, seller history, shipping and return terms. I have not checked current stock or prices and do not certify listings. For a specific search, include the game, card and country in your question.',
  es:'Para buscar una carta rara concreta, consulta cartas sueltas en tiendas de TCG y marketplaces. Para Pokémon en Brasil, MYP Cards tiene una sección de cartas sueltas; el enlace es un punto de búsqueda, no una oferta verificada. El localizador oficial Pokémon también ayuda a encontrar tiendas, pero no confirma que tengan la carta deseada.\n\nMi orientación: compara colección, número, idioma, acabado y estado. Revisa fotos del ejemplar, historial del vendedor, envío y condiciones de devolución. No he consultado existencias ni precios actuales y no certifico anuncios. Para una búsqueda concreta, incluye juego, carta y país en la pregunta.'
 },
 'singles-or-packs':{
  pt:'Depende do objetivo. Para escolher uma carta específica, minha sugestão é comparar anúncios de cartas avulsas. No Pokémon, boosters têm conteúdo aleatório: não garantem a carta que você procura. Abrir pacotes é uma experiência diferente de escolher cada carta. Compare custos atuais antes de decidir; não estou afirmando qual opção sai mais barata.',
  en:'It depends on your goal. To choose a specific card, my suggestion is to compare singles listings. Pokémon boosters have random contents: they do not guarantee the card you want. Opening packs is a different experience from selecting each card. Compare current costs before deciding; I am not claiming which option is cheaper.',
  es:'Depende de tu objetivo. Para elegir una carta concreta, sugiero comparar anuncios de cartas sueltas. Los sobres Pokémon tienen contenido aleatorio: no garantizan la carta que buscas. Abrir sobres es una experiencia distinta de elegir cada carta. Compara los costes actuales antes de decidir; no afirmo qué opción es más barata.'
 }
};
const references={
 'where-to-buy':[
  {title:'MYP Cards — Pokémon: cartas avulsas',url:'https://mypcards.com/pokemon'},
  {title:'Pokémon — Localizador de lojas',url:'https://events.pokemon.com/en-us/locations'},
  {title:'Pokémon Support — Onde comprar',url:'https://support.pokemon.com/hc/en-us/articles/360000634514-How-can-I-find-where-Pok%C3%A9mon-products-are-available-to-buy'}
 ],
 'singles-or-packs':[{title:'Pokémon Support — Tipos de produtos',url:'https://support.pokemon.com/hc/en-us/articles/360001024394-What-types-of-Trading-Card-Game-products-are-available'}]
};
export function lookupBuyingGuide(question:string,options:{hasAttachment?:boolean;cardId?:string}={}){
 if(question.length>240||options.hasAttachment||options.cardId)return null;
 const text=normalizeAtlasQuestion(question);
 for(const language of ['pt','en','es'] as const){
  for(const topicId of ['where-to-buy','singles-or-packs'] as const){
   if(!patterns[language][topicId].some(p=>p.test(text)))continue;
   return {answer:answers[topicId][language],source:'knowledge' as const,language,topicId,
    sourceLabel:{pt:'Orientação editorial do Atlas · sem geração por IA',en:'Atlas editorial guidance · no AI generation',es:'Orientación editorial de Atlas · sin generación por IA'}[language],
    reviewedAt:'2026-11-22',references:references[topicId]};
  }
 }
 return null;
}
