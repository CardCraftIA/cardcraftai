import {normalizeAtlasQuestion} from './atlas-question-intents.ts';
type Language='pt'|'en'|'es';
const prompts={
 price:{
  pt:'Qual carta você quer avaliar? Envie o nome, a coleção e o número, além do idioma, acabamento e estado de conservação. Isso ajuda a distinguir as edições; não tenho um preço atual confirmado só com essa pergunta.',
  en:'Which card would you like to value? Send its name, set and number, plus language, finish and condition. These help distinguish editions; this question alone does not establish a current price.',
  es:'¿Qué carta quieres valorar? Indica nombre, colección y número, además de idioma, acabado y estado. Estos datos ayudan a distinguir ediciones; esta pregunta no permite confirmar un precio actual.'
 },
 choice:{
  pt:'Melhor para qual objetivo: jogar, colecionar ou proteger as cartas? Inclua o jogo e o que deseja comparar na próxima pergunta.',
  en:'Best for what purpose: playing, collecting or protecting cards? Include the game and what you want to compare in your next question.',
  es:'¿Mejor para jugar, coleccionar o proteger las cartas? Incluye el juego y lo que quieres comparar en tu próxima pregunta.'
 },
 vague:{
  pt:'Pode completar a pergunta? Diga o nome da carta ou o assunto e o que quer saber. Por exemplo: “O que significa uma carta NM?” ou “Como proteger minhas cartas?”.',
  en:'Could you complete the question? Include the card name or topic and what you want to know. For example: “What is card condition?” or “How should I store my cards?”.',
  es:'¿Puedes completar la pregunta? Indica el nombre de la carta o el tema y qué quieres saber. Por ejemplo: “¿Qué significa NM?” o “¿Cómo proteger mis cartas?”.'
 },
 hp:{
  pt:'Você quer saber sobre HP como pontos de vida no jogo ou como estado de conservação (Heavily Played)? Inclua esse contexto na pergunta.',
  en:'Do you mean HP as hit points in a game or as card condition (Heavily Played)? Include that context in the question.',
  es:'¿Te refieres a HP como puntos de vida del juego o como estado de conservación (Heavily Played)? Incluye ese contexto en la pregunta.'
 }
};
const rules:{language:Language;topic:keyof typeof prompts;pattern:RegExp}[]=[
 {language:'pt',topic:'price',pattern:/^(?:quanto vale(?: essa carta| esta carta| isso)?|(?:qual (?:e )?o )?preco(?: dessa carta)?|valor da carta)$/},
 {language:'en',topic:'price',pattern:/^(?:how much is it worth|what is it worth|what is the price|card price)$/},
 {language:'es',topic:'price',pattern:/^(?:cuanto vale(?: esta carta)?|cual es el precio|precio de la carta)$/},
 {language:'pt',topic:'choice',pattern:/^qual (?:e )?(?:o|a) melhor$/},
 {language:'en',topic:'choice',pattern:/^(?:which|what) is (?:the )?best$/},
 {language:'es',topic:'choice',pattern:/^cual es (?:el|la) mejor$/},
 {language:'pt',topic:'hp',pattern:/^(?:hp|o que e hp)$/},
 {language:'en',topic:'hp',pattern:/^what is hp$/},
 {language:'es',topic:'hp',pattern:/^que es hp$/},
 {language:'pt',topic:'vague',pattern:/^(?:e essa|e essa carta|e agora|me ajuda|ajuda|nao entendi|como assim|isso|nm|holo)$/},
 {language:'en',topic:'vague',pattern:/^(?:what about this|help me|i don't understand|what do you mean)$/},
 {language:'es',topic:'vague',pattern:/^(?:y esta|ayudame|no entendi|no entiendo)$/}
];
export function lookupAtlasClarification(question:string,options:{hasAttachment?:boolean;cardId?:string}={}){
 if(options.hasAttachment||options.cardId||question.length>240)return null;
 const text=normalizeAtlasQuestion(question);
 const rule=rules.find(r=>r.pattern.test(text));
 if(!rule)return null;
 return {answer:prompts[rule.topic][rule.language],source:'clarification' as const,language:rule.language,
  sourceLabel:{pt:'Atlas · preciso de mais detalhes · sem consumo de pergunta',en:'Atlas · more details needed · no question charged',es:'Atlas · necesito más detalles · sin consumir pregunta'}[rule.language]};
}
