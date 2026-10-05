import test from 'node:test';
import assert from 'node:assert/strict';
import {geminiRequest} from '../lib/gemini-request.ts';

test('provider failures record only categories and status, never secrets or content', async () => {
  const original = console.error;
  const logs = [];
  console.error = (...args) => logs.push(args.join(' '));
  try {
    for (const status of [400,401,403,404,429,500]) {
      await assert.rejects(geminiRequest('https://example.invalid/SECRET', {}, async () => new Response('SECRET provider body', {status})), e => e.status === 503 && !e.message.includes('SECRET'));
    }
    await assert.rejects(geminiRequest('SECRET', {}, async () => {throw new Error('SECRET');}));
    await assert.rejects(geminiRequest('SECRET', {}, async () => {throw new DOMException('SECRET', 'TimeoutError');}));
    assert.equal(logs.length, 8);
    assert.ok(logs.some(l => l.includes('quota_or_rate_limit')));
    assert.ok(logs.some(l => l.includes('timeout')));
    assert.ok(logs.every(l => !l.includes('SECRET')));
  } finally { console.error = original; }
});

test('successful provider response remains readable', async () => {
  const response = await geminiRequest('https://example.invalid', {}, async () => Response.json({answer:'ok'}));
  assert.deepEqual(await response.json(), {answer:'ok'});
});
