# Revisão semanal do Atlas — 2026-09-28

## Escopo e referências

- Repositório de destino: `CardCraftIA/cardcraftai`, branch `staging` (HEAD observado: `a61a64b09fe30fbfa86cb672fa896fa44419e9a9` antes deste relatório).
- Ambiente consultado: Supabase `CardCraftAI-TEST` (`hwsaxufycqgmzrxjxsfb`). Nenhuma escrita no banco foi feita.
- Fonte principal: [TCGdex cards-database](https://github.com/tcgdex/cards-database), licença [MIT](https://github.com/tcgdex/cards-database/blob/master/LICENSE) para a base. Direitos sobre imagens são separados.
- Referência do snapshot atual: `feced2e7b99bcf2e2ab76f0309e16ce2c15b6a9a` (documentada em [catalog-core.md](catalog-core.md)).
- Revisão nova inspecionada: `309aab7060b165925fee48573e730275dfbd737c` (commit de 2026-09-27 13:54 UTC). [Comparação integral](https://github.com/tcgdex/cards-database/compare/feced2e7b99bcf2e2ab76f0309e16ce2c15b6a9a...309aab7060b165925fee48573e730275dfbd737c).

## Mudanças verificadas na fonte

A comparação contém três commits e 27 arquivos alterados:

1. [Correção #2393](https://github.com/tcgdex/cards-database/commit/b274094794ded22fe32017ee70a95b6b6f964c72), 2026-09-25: nomes e efeitos de habilidades em inglês adicionados para Articuno ex, Moltres ex e Zapdos ex, arquivos `EX/FireRed & LeafGreen/114-116.ts`.
2. [Adição #2392](https://github.com/tcgdex/cards-database/commit/a9bf1ef787f862971b088c4bd713fb7da812171b), 2026-09-25: 22 arquivos de carta, numerados 089–110, na coleção `MEP Black Star Promos`. Os 22 arquivos trazem texto de carta em inglês; não há localização portuguesa nesses arquivos. Cada arquivo declara ao menos uma variante holo; alguns declaram mais de uma variante holo com detalhes distintos. Os números 107 e 109 têm o mesmo nome `Pikachu ex`, mas são registros separados pela numeração.
3. Commit de 2026-09-27: documentação/patrocínio, sem alteração de carta.

Nenhum dos quatro source keys já hidratados no TEST (`base1-58`, `base1-4`, `sv01-081`, `asia:miscp-001`) aparece nos arquivos alterados. Não foi observado conflito com esses registros. Isto não substitui uma reconciliação após exportação da nova revisão.

## Cobertura e validação do TEST

Consultas de leitura em 2026-09-28: 4 cartas, 15 localizações, 18 variantes, 4 registros de origem, 0 conflitos registrados e 0 source keys duplicados. Tamanho do banco: 14.126.227 bytes (~13,5 MiB). A última sincronização registrada é o piloto `hydrate` de quatro cartas na revisão `feced2e...`; não existe sincronização da revisão `309aab7...`.

A capacidade contratada e o espaço livre do projeto não foram comprovados. O snapshot anterior tinha aproximadamente 133 MB em JSONL antes de índices e demais custos do Postgres. Não há validação de quota suficiente para carga integral. Também não há snapshot exportado, hash e dry run da nova revisão disponíveis nesta revisão. Por esses motivos, nenhum registro confirmado foi criado ou alterado no TEST.

## Proveniência, idiomas, variantes e fontes complementares

A fonte continua rastreável por revisão e licença. A comparação identifica os 22 arquivos novos e três correções, mas a ingestão segura depende do artefato completo com `SHA256SUMS`, validação do exporter e reconciliação. Não traduzir o inglês para português por IA e registrar a tradução como confirmada. Manter variantes múltiplas como entidades separadas conforme o modelo do catálogo. Não foram importadas imagens, preços ou links de venda; a licença MIT da base não concede por si só direitos de imagem. Nenhuma fonte complementar foi integrada sem revisão dos termos de uso e da correspondência de identidade/variantes.

## Próximos passos

1. Gerar snapshot na revisão `309aab7...` usando o workflow existente, verificar integridade, licença, contagens e hashes.
2. Executar as validações do exporter e `ingest_catalog_snapshot.py --dry-run` no artefato completo.
3. Confirmar limite e espaço livre do Supabase TEST antes de ampliar a carga; começar por uma seleção pequena e revisada dos novos números MEP.
4. Comparar localizações e variantes com fontes oficiais compatíveis e documentar divergências sem sobrescrever registros revisados.
5. Aplicar mudanças de dados apenas em `staging` e TEST após esses gates; manter `main` e produção intocados.
