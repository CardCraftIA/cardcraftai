# Smart Search integration and release audit

## Isolated checkpoints

- Integration base: `d18c9f4180eeb4375aef784afb11791486d8b821`.
- Public catalog: `3a32b74138f5ff0b24bf5098aa72e4914dde7c93`.
- Private collection: `aefabc55936101841dd29e2e7e79034624b4391a`.
- Original branches and both collection-search stashes are preserved.
- No production database, migration, Secrets or deployment changes were made.

## Shared search and automated validation

`search_utils.py` shares Unicode normalization, Latin accent folding and fuzzy
similarity. Public ranking retains its edition-token penalty and compact snapshot;
collection matching retains its six fields, exact-before-substring ordering,
number denominators, and suggestions limited to the owner's Set/Wishlist results.
Private notes are excluded. No private data enters the public cache.

Run the entire suite with `python -B scripts/run_tests.py` after installing
`requirements-dev.txt`. The runner blocks real HTTP and socket connections and
fails if any test is skipped. No credentials are supplied or loaded. Catalog
UI tests extract the real page with fake clients; collection UI tests use the
in-memory preview. Operational tests extract real functions without executing
the app's credential-loading or authentication code.

Coverage includes exact and fuzzy catalog names, offline/missing/corrupt snapshot,
unavailable external catalog, collection fields and legacy values, Set/Wishlist,
Album/List/grid/editor, suggestion clicks, exports, metrics, no-network searches,
unchanged free-search credit balances, and paid-analysis failure orchestration.

GitHub Actions runs on pushes and pull requests **targeting `codex/**` branches**,
on Python 3.12 and 3.14. It installs dev requirements, runs `pip check`, the full
offline suite, and a whitespace diff check. New-branch pushes check the tip commit;
later pushes check all changes since the previous remote tip, and PRs compare
against the base SHA. Actions are SHA-pinned; token permissions are read-only,
checkout credentials are not persisted, and no deploy or migration job exists.

## Technical audit and limited fixes

- All tracked Python files were parsed and checked for undefined names/imports.
  Runtime imports are also exercised without initializing the live app.
- The selected-card identity transformation failure had nested refund handlers:
  it could call the refund RPC twice and claim success before confirmation. It now
  reaches one existing outer failure handler, preserving reservation/charge rules.
  Tests protect successful charging, failed transformation, failed refund and
  failed completion. No RPC or monetary rule changed.
- Technical-error redaction now includes session access/refresh tokens. No real
  token is used in tests.
- Package-loading failures no longer interpolate backend exceptions into the UI;
  checkout errors no longer display raw exception details below the safe message.
- Collection reads and writes retain explicit owner filters. The existing SQL
  still enables RLS and owner-scoped policies with CRUD-only grants. Inspection
  cannot substitute for querying an actual deployment's effective policies.
- Existing prototypes are used by UI tests; they are not dead files. No cosmetic
  cleanup, unrelated dependency removal, Confidence Engine change or new feature
  was performed.

## Relevant follow-up before production

- SQL implementations of credit/audit RPCs and payment Edge Functions are not in
  this repository. Cross-session atomicity/idempotency and deployed RLS cannot be
  proven by these offline tests. Validate them in TEST before a production rollout.
- Full catalog searches still perform sequential detail requests and may fall
  back to the legacy provider. They can be slower than local suggestions; changing
  their retry/cache/ranking architecture remains outside this consolidation.
- Requirements use lower bounds rather than a complete lockfile. CI validates a
  clean installation, but future dependency releases can change compatibility.
- Streamlit reports deprecation warnings for existing `use_container_width`
  calls. Current tests pass; migrate these separately before removing compatibility.
- Authenticated end-to-end flows and payment webhooks remain TEST-environment
  checks. CI intentionally does not contact Supabase, Gemini or payment services.
