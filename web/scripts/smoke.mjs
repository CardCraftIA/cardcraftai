import {spawn} from 'node:child_process';
import assert from 'node:assert/strict';

const port = 3219;
const server = spawn(process.execPath, ['node_modules/next/dist/bin/next', 'start', '-p', String(port), '-H', '127.0.0.1'],
  {stdio: 'pipe'});
let output = '';
server.stderr.on('data', chunk => {output += String(chunk).slice(0, 2000);});

try {
  let response;
  for (let attempt = 0; attempt < 30; attempt++) {
    try {
      response = await fetch(`http://127.0.0.1:${port}/api/catalog?q=Pikachu`);
      break;
    } catch {
      if (server.exitCode !== null) throw new Error(`Server exited: ${output}`);
      await new Promise(resolve => setTimeout(resolve, 250));
    }
  }
  assert.ok(response, `Server did not start: ${output}`);
  assert.equal(response.status, 200);
  const result = await response.json();
  assert.ok(result.cards.some(card => card.name === 'Pikachu'));
  const home = await fetch(`http://127.0.0.1:${port}/`);
  assert.equal(home.status, 200);
  assert.match(await home.text(), /CardCraftAI/);
  console.log('Public web home and catalog route are ready');
} finally {
  server.kill('SIGTERM');
}
