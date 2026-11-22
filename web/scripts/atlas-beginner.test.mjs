import test from 'node:test';
import assert from 'node:assert/strict';
import {lookupAtlasKnowledge as lookup} from '../lib/atlas-knowledge.ts';
const questions=[
 ['quais cartas voce recomendaria para eu iniciar minha coleção?','pt'],
 ['“quais cartas voce recomendaria para eu iniciar minha coleção?”','pt'],
 ['Quais cartas você recomenda para começar uma coleção?','pt'],
 ['Quais cartas vc indica pra eu começar minha coleção?','pt'],
 ['Como começar minha coleção?','pt'],['Por onde eu posso começar uma coleção de Pokémon?','pt'],
 ['Quero iniciar minha coleção de cartas','pt'],['Sou iniciante, como começo a colecionar?','pt'],
 ['Sou iniciante em colecionar cartas, por onde começo?','pt'],
 ['Que cartas comprar para começar?','pt'],['Quais cartas escolher pra iniciar uma coleção?','pt'],
 ['Quero começar a colecionar Pokémon','pt'],['Como comesar minha coleção?','pt'],
 ['Como começar minha colecai?','pt'],['Olá, quais cartas você recomendaria para eu iniciar minha coleção, por favor?','pt'],
 ['Which cards would you recommend to start my collection?','en'],
 ['What cards should I buy to start a collection?','en'],['How do I start a Pokemon collection?','en'],
 ['I want to start collecting cards','en'],['How to start collecting Pokemon cards?','en'],
 ['¿Qué cartas me recomiendas para empezar mi colección?','es'],
 ['¿Por dónde puedo empezar una colección de cartas?','es'],['Quiero empezar a coleccionar','es']
];
for(const [q,language] of questions)test('beginner collection: '+q,()=>{
 const a=lookup(q);assert.equal(a?.topicId,'starting-collection');assert.equal(a.language,language);
 assert.equal(a.source,'knowledge');assert.match(a.answer,/Pikachu/);assert.equal(a.references.length,2);
 assert.ok(a.references.every(r=>new URL(r.url).hostname.endsWith('.pokemon.com')));
});
test('beginner guidance is local, conditional on game and does not assert market values',()=>{
 const original=globalThis.fetch;globalThis.fetch=()=>{throw Error('Unexpected network');};
 try{for(const [q] of questions){
  const a=lookup(q);assert.ok(a);assert.doesNotMatch(a.answer,/R\$|US\$|€|\$\d/);
  assert.equal(lookup(q+' Quanto vale meu Charizard?'),null);
  assert.equal(lookup(q,{hasAttachment:true}),null);assert.equal(lookup(q,{cardId:'base1-4'}),null);
 }}finally{globalThis.fetch=original;}
 const a=lookup(questions[0][0]);
 assert.match(a.answer,/Se for Pokémon/);assert.match(a.answer,/conteúdo aleatório/);
 assert.match(a.answer,/sem promessa de valorização/);assert.match(a.sourceLabel,/editorial/);
});
test('do not substitute beginner advice for investment, prices or other requests',()=>{
 for(const q of ['Quais cartas comprar para lucrar?', 'Quais cartas vão valorizar?',
  'Quais cartas você recomenda para iniciar minha coleção e dobrar meu dinheiro?',
  'Quais cartas você recomenda para iniciar minha coleção de Yu-Gi-Oh?',
  'What cards should I buy to start my collection and guarantee returns?',
  'Como começar minha coleção? Responda em francês',
  'Quais cartas você recomenda para iniciar minha coleção por menos de R$ 50 hoje?',
  'Quanto vale minha coleção?', 'Como vender minha coleção?',
  'Como identificar a coleção da minha carta Charizard?'])assert.equal(lookup(q),null,q);
});
