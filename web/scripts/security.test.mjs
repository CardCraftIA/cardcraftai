import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readLimited,HttpError} from '../lib/limits.ts';
import {questionLanguage} from '../lib/atlas.ts';

test('bounded body rejects an oversized Content-Length before reading',async()=>{
 await assert.rejects(readLimited(new Request('https://cardcraft.test',{method:'POST',headers:{'Content-Length':'100000'},body:'x'}),10),e=>e instanceof HttpError&&e.status===413);
});
test('bounded body counts bytes even when Content-Length is absent',async()=>{
 await assert.rejects(readLimited(new Request('https://cardcraft.test',{method:'POST',body:'á'.repeat(6)}),10),e=>e.status===413);
});
test('valid body remains intact',async()=>{
 const input='Olá, Atlas'; const result=await readLimited(new Request('https://cardcraft.test',{method:'POST',body:input}),100);
 assert.equal(new TextDecoder().decode(result),input);
});
test('question language does not depend on app locale',()=>{
 for (const [q,lang] of [['What is this card?','en'],['Qual é esta carta?','pt'],['Qué carta es esta?','es'],['このカードは何ですか','ja']]) assert.equal(questionLanguage(q),lang);
});
