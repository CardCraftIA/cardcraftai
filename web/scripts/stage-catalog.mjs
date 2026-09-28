import { copyFile, mkdir, readFile } from 'node:fs/promises';
import path from 'node:path';

const source = path.resolve(process.cwd(), '../data/catalog_name_index_tcgdex_en.json');
const target = path.resolve(process.cwd(), 'data/catalog_name_index_tcgdex_en.json');
const parsed = JSON.parse(await readFile(source, 'utf8'));
if (parsed.provider !== 'tcgdex' || parsed.language !== 'en' || !Array.isArray(parsed.entries)) {
  throw new Error('Invalid public catalog index');
}
await mkdir(path.dirname(target), {recursive: true});
await copyFile(source, target);
console.log(`Staged ${parsed.entries.length} public catalog names`);
