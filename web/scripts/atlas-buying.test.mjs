import test from 'node:test';
import assert from 'node:assert/strict';
import {lookupAtlasKnowledge as lookup} from '../lib/atlas-knowledge.ts';
const buy=[
 ['onde consigo comprar cartas raras','pt'],['“onde consigo comprar cartas raras”','pt'],
 ['Onde eu posso comprar cartas raras?','pt'],['Onde comprar cartas avulsas?','pt'],
 ['Onde compro cartas raras de Pokémon?','pt'],['Aonde encontro cartas raras?','pt'],
 ['Onde comprar carta rara?','pt'],['Onde comprar cards raros?','pt'],
 ['Quais lojas vendem cartas raras?','pt'],['Que sites vendem cartas avulsas de Pokémon?','pt'],
 ['Em qual site posso comprar cartas raras?','pt'],['Qual loja vende cartas raras?','pt'],
 ['Quero comprar cartas raras','pt'],['Como encontrar cartas raras?','pt'],
 ['Onde comprar cartas Pokémon raras no Brasil?','pt'],
 ['Onde comprar cartas raras pela internet?','pt'],['Olá, onde consigo comprar cartas raras, por favor?','pt'],
 ['Where can I buy rare cards?','en'],['Where should I buy single Pokemon cards online?','en'],
 ['Where to buy rare Pokemon cards?','en'],['Which stores sell rare cards?','en'],
 ['¿Dónde puedo comprar cartas raras?','es'],['¿Dónde comprar cartas sueltas de Pokémon?','es'],
 ['¿Qué tiendas venden cartas raras?','es']
];
const packs=[['É melhor comprar cartas avulsas ou boosters?','pt'],
 ['Vale mais a pena comprar boosters ou cartas avulsas?','pt'],['Qual é a diferença entre cartas avulsas e boosters?','pt'],
 ['Should I buy singles or booster packs?','en'],['What is the difference between singles and booster packs?','en'],
 ['¿Es mejor comprar cartas sueltas o sobres?','es'],['¿Cuál es la diferencia entre cartas sueltas y sobres?','es']];
for(const [topic,qs] of [['where-to-buy',buy],['singles-or-packs',packs]]){
 for(const [q,language] of qs)test('buying guide: '+q,()=>{
  const a=lookup(q);assert.equal(a?.topicId,topic);assert.equal(a.language,language);
  assert.equal(a.source,'knowledge');assert.ok(a.references.length);
  assert.doesNotMatch(a.answer,/R\$|US\$|€|\$\d/);
  for(const r of a.references){const u=new URL(r.url);assert.equal(u.protocol,'https:');assert.equal(u.search,'');}
 });
}
test('buying guidance makes no live stock, price or authenticity claim',()=>{
 const a=lookup(buy[0][0]);assert.match(a.answer,/Se for Pokémon no Brasil/);
 assert.match(a.answer,/não uma oferta verificada/);assert.match(a.answer,/Não consultei estoque nem preços atuais/);
 assert.match(a.answer,/não certifico anúncios/);assert.match(a.answer,/coleção, número, idioma, acabamento e conservação/);
 const p=lookup(packs[0][0]);assert.match(p.answer,/conteúdo aleatório/);assert.match(p.answer,/não estou afirmando qual opção sai mais barata/);
});
test('buying queries remain local and do not absorb extra context',()=>{
 const original=globalThis.fetch;globalThis.fetch=()=>{throw Error('Unexpected network');};
 try{for(const [q] of [...buy,...packs]){
  assert.ok(lookup(q));assert.equal(lookup(q+' Quanto vale meu Charizard?'),null);
  assert.equal(lookup(q,{hasAttachment:true}),null);assert.equal(lookup(q,{cardId:'base1-4'}),null);
 }}finally{globalThis.fetch=original;}
 for(const q of ['Onde comprar pelo menor preço?', 'Onde comprar cartas raras mais baratas hoje?',
  'Onde comprar Charizard SM211?', 'Onde consigo comprar cartas raras e quanto custam?',
  'Onde comprar cartas raras falsificadas?', 'Onde comprar cartas raras de Magic?',
  'Onde comprar cartas raras? Garanta que são originais.', 'Onde comprar cartas raras? Responda em francês',
  'Qual vendedor é confiável?', 'Where can I buy rare cards with guaranteed returns?',
  'Qual booster garante um Charizard?', 'Onde vender cartas raras?'])assert.equal(lookup(q),null,q);
});
