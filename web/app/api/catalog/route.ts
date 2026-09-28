import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
type Card = {display_name: string; normalized_name: string; representative_id: string; representative_image: string};
let snapshot: Promise<Card[]> | undefined;

function loadIndex(): Promise<Card[]> {
  snapshot ??= readFile(path.resolve(process.cwd(), 'data/catalog_name_index_tcgdex_en.json'), 'utf8')
    .then(raw => {
      const parsed = JSON.parse(raw);
      if (parsed.provider !== 'tcgdex' || parsed.language !== 'en' || !Array.isArray(parsed.entries)) {
        throw new Error('Invalid catalog snapshot');
      }
      return parsed.entries as Card[];
    }).catch(error => { snapshot = undefined; throw error; });
  return snapshot;
}

export async function GET(request: NextRequest) {
  const query = (request.nextUrl.searchParams.get('q') || '').trim().toLocaleLowerCase('en').slice(0, 80);
  if (query.length < 2) return NextResponse.json({cards: []});
  try {
    const entries = await loadIndex();
    const matches = entries.filter(card => card.normalized_name.includes(query))
      .sort((a, b) => Number(b.normalized_name === query) - Number(a.normalized_name === query)
        || Number(b.normalized_name.startsWith(query)) - Number(a.normalized_name.startsWith(query))
        || a.normalized_name.localeCompare(b.normalized_name)).slice(0, 24);
    return NextResponse.json({cards: matches.map(({display_name, representative_id, representative_image}) =>
      ({name: display_name, id: representative_id, image: representative_image}))},
      {headers: {'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=3600'}});
  } catch {
    return NextResponse.json({error: 'Catálogo temporariamente indisponível'}, {status: 503});
  }
}
