'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

type Card = {name: string; id: string; image: string};

export function CatalogSearch() {
  const [query, setQuery] = useState('');
  const [cards, setCards] = useState<Card[]>([]);
  const [status, setStatus] = useState('Digite ao menos duas letras para explorar o catálogo.');

  useEffect(() => {
    if (query.trim().length < 2) { setCards([]); setStatus('Digite ao menos duas letras para explorar o catálogo.'); return; }
    const controller = new AbortController();
    const timer = setTimeout(async () => {
      try {
        const response = await fetch('/api/catalog?q=' + encodeURIComponent(query), {signal: controller.signal});
        if (!response.ok) throw new Error('unavailable');
        const result = await response.json() as {cards: Card[]};
        setCards(result.cards);
        setStatus(result.cards.length ? `${result.cards.length} nomes encontrados · índice público em inglês` : 'Nenhum nome encontrado.');
      } catch {
        if (!controller.signal.aborted) { setCards([]); setStatus('Catálogo temporariamente indisponível.'); }
      }
    }, 250);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [query]);

  return <section className="catalog" id="catalogo" aria-labelledby="catalog-title">
    <div className="section-heading"><span className="eyebrow">EXPLORE O CATÁLOGO</span><h2 id="catalog-title">Sua próxima descoberta começa aqui.</h2>
      <p>Busque nomes de cartas Pokémon no índice público. A edição exata requer número e coleção.</p></div>
    <label htmlFor="card-search">Nome da carta</label>
    <input id="card-search" type="search" value={query} onChange={event => setQuery(event.target.value)}
      placeholder="Experimente Pikachu, Charizard, Mew..." maxLength={80} autoComplete="off" />
    <p className="search-status" role="status">{status}</p>
    <div className="card-grid">{cards.map(card => <Link className="card-result" key={card.id} href={`/catalogo/${encodeURIComponent(card.id)}`}>
      {card.image && <Image width={150} height={175} unoptimized src={card.image} alt={`Imagem representativa de ${card.name}`} loading="lazy" />}
      <strong>{card.name}</strong><small>Exemplo: {card.id}</small>
    <span className="card-cta">Ver edição →</span></Link>)}</div>
    <p className="source-note">Fonte: índice TCGdex. Imagens e nomes são referências externas; nenhum preço ou autenticidade é inferido.</p>
  </section>;
}
