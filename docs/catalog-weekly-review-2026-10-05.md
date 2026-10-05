# Revisão semanal do Atlas — 2026-10-05

## Escopo e controles

- Destino: `CardCraftIA/cardcraftai`, exclusivamente branch `staging` (HEAD inicial `1d2b5a384fba9a27e1f1a7ed75a3441fce40450d`).
- Banco consultado: Supabase `CardCraftAI-TEST` (`hwsaxufycqgmzrxjxsfb`), somente leitura nesta revisão.
- Marco anterior analisado: TCGdex `309aab7060b165925fee48573e730275dfbd737c`.
- Revisão TCGdex observada em 2026-10-05: `c5c0a8a63fe81746d05b9c95e8f51ed6931f7e78`, último commit em 2026-09-30 08:41 UTC.
- Comparação: https://github.com/tcgdex/cards-database/compare/309aab7060b165925fee48573e730275dfbd737c...c5c0a8a63fe81746d05b9c95e8f51ed6931f7e78
- A base continua sob licença MIT: https://github.com/tcgdex/cards-database/blob/master/LICENSE. A licença da base não deve ser interpretada como licença de imagens ou marcas.

`main`, produção e o Supabase de produção não foram consultados para escrita nem alterados.

## Novidades verificadas

A comparação contém 23 commits entre 28 e 30 de setembro. A API do GitHub expôs 300 arquivos na comparação (2 adicionados e 298 modificados), atingindo o teto de listagem; portanto, 300 é cobertura observada, não prova de total integral.

Principais grupos:

1. **Português — 30th Celebration.** O commit `27a6fb5...` adiciona texto português ausente, com 1.186 adições e 587 remoções. A mensagem informa assistência por Codex; por isso a alteração não deve ser promovida como verdade apenas por origem de IA. Requer conferência com material impresso/oficial e o snapshot completo.
2. **Traduções MEP.** O commit `a506fa1...` restringe traduções às impressões francesas conhecidas: remove traduções indevidas (inclusive `pt`) de itens sem impressão correspondente, mantém francês em 089–091 e 094–110 e corrige textos. Isto é uma correção de proveniência importante e impede completar idiomas automaticamente.
3. **Variantes e marketplaces SVP.** O commit `8cb320c...` altera 25 arquivos: adiciona/corrige IDs Cardmarket/TCGplayer e variantes plain holo/jumbo, mas também remove variantes incorretas em SVP 028/029 e o split cosmos de SVP 042. Não se deve fazer merge aditivo cego; é necessária reconciliação que aceite remoções/correções.
4. **Mega Evolution.** O commit `00da102...` adiciona descrições francesas e normaliza o sufixo `EX` para `ex`; a listagem do commit também atinge 300 arquivos, exigindo snapshot integral.
5. **IDs de aparição/cameo.** Vários commits acrescentam `dexIds` em gerações Base até Scarlet & Violet. O commit final `c5c0a8a...` adiciona ainda o conjunto asiático WCS23 e a carta Yokohama Pikachu ex, além de IDs em 15 conjuntos Scarlet & Violet.
6. **Correções pontuais.** Incluem texto/ID Cardmarket de Unown em Neo Discovery e IDs de grupo TCGplayer para MEP/SVP.

Não foram encontrados commits posteriores a 2026-09-30 no `master` do TCGdex até esta consulta.

## Estado do Supabase TEST

Leitura em 2026-10-05:

- 4 cartas;
- 15 localizações;
- 18 variantes;
- 4 links de origem e 4 registros de origem;
- 0 conflitos;
- 0 registros de origem duplicados pela chave composta `(source_id, source_key, language, entity_type)`;
- banco com 14.331.027 bytes (~13,67 MiB);
- última sincronização: `hydrate` concluído de 4 registros na revisão `feced2e7b99bcf2e2ab76f0309e16ce2c15b6a9a`, sem erros ou conflitos.

O crescimento desde 28/09 é pequeno e não comprova quota disponível para o snapshot integral. O limite contratado/espaço livre continua não verificável pelas consultas disponíveis.

## Validações e segurança

- O workflow **Tests** da `staging` em `1d2b5a3...` concluiu com sucesso em 2026-10-05: https://github.com/CardCraftIA/cardcraftai/actions/runs/37263272761
- As consultas de integridade do piloto passaram: sem conflitos e sem duplicação de origem.
- O advisor do TEST continua apontando avisos preexistentes fora desta carga, incluindo `search_path` mutável, `pg_trgm` no schema `public` e funções `SECURITY DEFINER` executáveis por `anon`. Referência: https://supabase.com/docs/guides/database/database-linter
- Tabelas internas do catálogo com RLS e sem política aparecem como INFO; no modelo atual isso mantém acesso negado pela Data API. Qualquer abertura futura exige política e autorização explícitas.
- O changelog recente do Supabase foi revisado; a novidade OrioleDB em beta não afeta este projeto PostgreSQL existente nem esta revisão somente leitura.

## Decisão de ingestão

**Nenhum dado foi escrito no Supabase TEST.** Também não foram importados preços, imagens ou links comerciais.

Bloqueios objetivos:

1. comparação com listagem truncada em 300 arquivos;
2. ausência de snapshot integral fixado em `c5c0a8a...` com `SHA256SUMS`;
3. ausência de execução do exporter e de `ingest_catalog_snapshot.py --dry-run` sobre esse artefato;
4. capacidade/quota disponível do TEST não confirmada;
5. mudanças incluem remoções de traduções/variantes e correções de IDs, que exigem reconciliação, não simples inserção;
6. textos portugueses assistidos por IA ainda precisam de fonte confirmatória antes de virarem registros confirmados.

## Próximos passos seguros

1. Gerar o snapshot completo exatamente em `c5c0a8a63fe81746d05b9c95e8f51ed6931f7e78`, com manifesto de licença e hashes.
2. Executar validações do exporter, contagens e `ingest_catalog_snapshot.py --dry-run`.
3. Conferir por amostra as traduções portuguesas de 30th Celebration contra material oficial/impresso; manter status não confirmado quando a evidência não existir.
4. Validar remoções e alterações de variantes SVP e IDs de marketplace sem inventar preço nem disponibilidade.
5. Confirmar quota e espaço livre do TEST; só então aplicar um lote pequeno, transacional e reversível.
