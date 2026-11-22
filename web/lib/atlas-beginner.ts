import {normalizeAtlasQuestion} from './atlas-question-intents.ts';
type Language='pt'|'en'|'es';
const patterns:Record<Language,RegExp[]>={
 pt:[
  /^quais cartas (?:voce |vc )?(?:recomendaria|recomenda|indica|indicaria|sugere) (?:para|pra) (?:eu )?(?:iniciar|comecar|montar) (?:a |uma |minha |a minha )?colecao(?: de (?:cartas|pokemon))?$/,
  /^(?:como|por onde) (?:eu )?(?:posso |devo )?(?:comecar|iniciar) (?:a |uma |minha |a minha )?colecao(?: de (?:cartas|pokemon))?$/,
  /^(?:quero|gostaria de) (?:comecar|iniciar|montar) (?:a |uma |minha )?colecao(?: de (?:cartas|pokemon))?$/,
  /^(?:sou iniciante[,.]? )?(?:como|por onde) (?:comecar a colecionar|comeco a colecionar)(?: cartas| pokemon)?$/,
  /^sou iniciante (?:em colecionar cartas|no colecionismo)[,.]? por onde comeco$/,
  /^(?:que|quais) cartas (?:comprar|escolher) (?:para|pra) (?:comecar|iniciar)(?: (?:a |uma |minha )?colecao)?$/,
  /^quero comecar a colecionar(?: cartas| pokemon)?$/
 ],
 en:[
  /^(?:which|what) cards (?:would you recommend|do you recommend|should i (?:buy|choose)) to start (?:my|a) collection$/,
  /^(?:how|where) (?:do i|should i|can i) start (?:my|a) (?:card |pokemon )?collection$/,
  /^(?:how to|i want to) start collecting(?: cards| pokemon cards)?$/
 ],
 es:[
  /^que cartas (?:recomiendas|recomendarias|me recomiendas|deberia comprar) para (?:empezar|iniciar|comenzar) (?:mi|una) coleccion$/,
  /^(?:como|por donde) (?:puedo |debo )?(?:empezar|iniciar|comenzar) (?:mi|una) coleccion(?: de (?:cartas|pokemon))?$/,
  /^quiero (?:empezar|comenzar) a coleccionar(?: cartas| pokemon)?$/
 ]
};
const answers:Record<Language,string>={
 pt:'Minha sugestão é começar com um tema pequeno: personagens de que você gosta ou ilustrações que gostaria de guardar. Se for Pokémon, versões de Pikachu ou Eevee podem ser exemplos, caso você goste deles — não estou indicando uma edição nem um preço específico.\n\nDefina um limite de gasto e uma lista curta de cartas. Para buscar uma carta específica, considere cartas avulsas; boosters têm conteúdo aleatório. Se também quiser jogar Pokémon, um deck pré-construído é uma opção diferente de montar uma coleção por preferência.\n\nPara personalizar a orientação, inclua na próxima pergunta o TCG, seus personagens favoritos e o orçamento. Esta é uma sugestão de hobby, sem promessa de valorização.',
 en:'My suggestion is to start with a small theme: characters you like or artwork you would enjoy keeping. For Pokémon, versions of Pikachu or Eevee are examples if you like them — I am not recommending a particular printing or quoting a price.\n\nSet a spending limit and a short card list. For a specific card, consider singles; booster contents are random. If you also want to play Pokémon, a preconstructed deck is a different option from collecting personal favorites.\n\nFor more tailored guidance, include the TCG, favorite characters and budget in your next question. This is a hobby suggestion, not a promise of appreciation.',
 es:'Mi sugerencia es empezar con un tema pequeño: personajes que te gustan o ilustraciones que quieras conservar. En Pokémon, versiones de Pikachu o Eevee son ejemplos si te gustan — no recomiendo una edición concreta ni indico un precio.\n\nDefine un límite de gasto y una lista corta de cartas. Para una carta específica, considera cartas sueltas; los sobres tienen contenido aleatorio. Si también quieres jugar Pokémon, un mazo preconstruido es una opción distinta de coleccionar por preferencias.\n\nPara personalizar la orientación, incluye el TCG, tus personajes favoritos y el presupuesto en tu próxima pregunta. Es una sugerencia de afición, sin promesa de revalorización.'
};
export function lookupBeginnerGuide(question:string,options:{hasAttachment?:boolean;cardId?:string}={}){
 if(question.length>240||options.hasAttachment||options.cardId)return null;
 const text=normalizeAtlasQuestion(question);
 for(const language of ['pt','en','es'] as const){
  if(!patterns[language].some(p=>p.test(text)))continue;
  return {answer:answers[language],language,topicId:'starting-collection',source:'knowledge' as const,
   sourceLabel:{pt:'Orientação editorial do Atlas · sem geração por IA',en:'Atlas editorial guidance · no AI generation',es:'Orientación editorial de Atlas · sin generación por IA'}[language],
   reviewedAt:'2026-11-22',references:[
    {title:'Pokémon — Collecting and playing',url:'https://parents.pokemon.com/en-us/trading-card-game/'},
    {title:'Pokémon Support — Product types',url:'https://support.pokemon.com/hc/en-us/articles/360001024394-What-types-of-Trading-Card-Game-products-are-available'}
   ]};
 }
 return null;
}
