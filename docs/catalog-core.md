# CardCraft Catalog Core

## Goal

CardCraft Catalog Core is the internal, provenance-aware card database for CardCraftAI.
External databases are **synchronization inputs**, not the runtime source of truth.

The long-term product goal is:

1. search the CardCraft database first;
2. keep rich historical metadata locally;
3. preserve multiple languages, printings and physical variants;
4. know where every field came from;
5. detect source disagreements instead of silently overwriting them;
6. accept community discoveries for cards/variants absent from upstream catalogs;
7. refresh sources in maintenance jobs without making the user experience depend on
   those services being online.

## Canonical model

The database intentionally separates concepts that many catalogs flatten together:

- `catalog_games`: TCG/product families.
- `catalog_sets`: canonical releases/sets.
- `catalog_cards`: a card printing identity within a game/set.
- `catalog_card_localizations`: language-specific name/text/image references.
- `catalog_card_variants`: physical variants such as unlimited, first edition,
  shadowless, stamps, jumbo, reverse/holo subtypes, etc.
- `catalog_aliases`: alternate names and search aliases.
- `catalog_sources`: source registry and licensing posture.
- `catalog_source_records`: immutable-ish raw source evidence + SHA-256.
- `catalog_source_links`: provenance links from evidence to canonical entities.
- `catalog_conflicts`: disagreements that require reconciliation.
- `catalog_sync_runs`: auditable import history.
- `catalog_discovery_submissions`: user discoveries that can become new canonical
  records only after review.

This is the basis for future CardCraft IDs and a field-level Confidence Engine.

## First source: TCGdex

The first build source is the public `tcgdex/cards-database` repository.

Why it is the first source:

- the database itself is MIT-licensed;
- it is multilingual;
- source files include detailed card metadata and many explicit physical variants;
- building from a checked-out repository means the initial snapshot does not depend
  on the live API;
- the exact upstream revision, license, SHA-256 and export statistics are preserved
  in the build artifact.

Card images are **not copied** by the exporter. The snapshot contains deterministic
remote asset references only. Image rights remain separate from the database license.

## Build pipeline

`.github/workflows/catalog-snapshot.yml`:

1. checks out CardCraftAI;
2. checks out `tcgdex/cards-database`;
3. validates the upstream TypeScript database;
4. exports card/set/localization/variant data to JSONL;
5. records source revision, license and SHA-256;
6. uploads the snapshot as a GitHub Actions artifact.

The Streamlit app does not run this process.

## Ingestion

`scripts/ingest_catalog_snapshot.py` validates the snapshot, then upserts it into
Catalog Core using the Supabase service role in a trusted maintenance environment.

The command is resumable/idempotent by canonical/source keys. Service-role keys must
never be committed to GitHub or exposed in the Streamlit client.

Example dry run:

```bash
python scripts/ingest_catalog_snapshot.py artifacts/tcgdex/tcgdex_cards.jsonl --dry-run
```

Real ingest requires `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in the
maintenance environment.

## Organic growth: cards upstream catalogs miss

A database cannot become uniquely complete by mirroring one provider. CardCraft's
own discovery loop is therefore part of the schema:

1. user scans/searches a card;
2. CardCraft cannot find an adequate canonical match;
3. the user can submit name/set/number/language/variant plus evidence;
4. submission enters a review queue;
5. reviewers compare physical evidence and available sources;
6. accepted discoveries become canonical CardCraft records with provenance;
7. later upstream matches are linked as new evidence rather than replacing CardCraft
   identity.

Future additions should include image fingerprinting, duplicate detection,
moderation tooling and reviewer reputation before user-supplied images are accepted
as canonical evidence.

## Source admission policy

Do not ingest a new provider merely because an API exists. Before enabling an
adapter, record:

- allowed commercial/product use;
- redistribution/mirroring terms;
- attribution requirements;
- image/artwork rights separately from metadata rights;
- rate limits;
- whether local persistent storage is allowed;
- update strategy and deletion/correction obligations.

If terms are unclear, keep the provider in `review` status and do not bulk mirror it.

## Runtime migration

The current app still has an external Pokémon catalog path. Catalog Core should
replace it only after the internal database has enough coverage and search quality.

Safe rollout:

1. populate TEST Catalog Core;
2. compare local results vs current catalog for representative cards;
3. local-first / external-fallback in TEST;
4. measure misses and conflicts;
5. make external providers background refresh sources;
6. remove runtime dependency only when coverage is proven.

Prices remain a separate, freshness-sensitive layer. Static card identity belongs in
Catalog Core; market quotes should keep source, currency, observation time and stale
threshold.
