# Release candidate readiness

Work branch: `codex/cardcraftai-integration`. No production operations, Secrets
changes, main merge, or deletion of original branches/stashes are part of this RC.
Final technical pass began at `1c1d1b5daf46688e39e78cccc24438ba0114062b`,
with a clean tree and `0 / 0` divergence after `git fetch origin`.

## AUTOMATICALLY VERIFIED

- Full offline suite: **128 passing, no skipped tests**. Command:
  `python -B scripts/run_tests.py`. HTTP and external sockets are blocked;
  loopback IPC remains available for Streamlit/asyncio on Windows.
- Clean installation from `requirements-dev.txt` on Python 3.14; `pip check`
  passes. Resolved versions include Streamlit 1.64, Pillow 12.3, Supabase 2.31
  and google-genai 2.25. Requirements were not broadly upgraded or rewritten.
- Isolated Streamlit health endpoint returns HTTP 200 without configured Secrets;
  an AppTest confirms the app stops with a safe configuration message. This is
  startup validation, not evidence that external services are configured.
- Python compilation and import paths exercised by the offline suite; static
  inspection found no undefined names. Existing unused exception variables are
  not release blockers. Git whitespace checks pass.
- CI installs dependencies, checks consistency, compiles Python, runs the full
  offline suite and checks the diff on Python 3.12/3.14. Triggers: pushes to
  `codex/**`, PRs targeting `main` or `codex/**`. Pinned actions, read-only token,
  no deployment/migration job or real service credentials.
- Local snapshot remains 4,425 names, approximately 897 KB; no complete remote
  index is downloaded by suggestions. Five-run medians in the clean environment:
  cold read/validation 120 ms, warm read 5 ms; Picachu 70 ms, Pikacu 62 ms,
  Pikatchu 76 ms. Pikachu ranks first for each; Picachu also suggests Pichu.
  A synthetic 5,000-row collection search took 148 ms. These are local timings,
  not promises about full external catalog requests.
- Final technical audit: all seven existing authenticated routes render in four
  languages with explicit fake clients; actual sidebar callbacks preserve the
  fixture credit balance. These checks do not establish live authentication/RLS.
  Login was inspected at 1440px and 390px with no document horizontal overflow. There is
  no separate Home route; the authenticated landing page is Photo Analysis.
- This pass additionally clears prior photo/history evidence on identity change,
  distinguishes purchase-history outages from empty results, translates the
  collection sidebar entry in Spanish/Japanese, and removes a remaining
  post-analysis diagnostic from the visible warning. Regression tests cover each.
- Collection grid/editor, filters, metrics, legacy values, exports, both search
  flows, exact-name suppression, offline snapshot failures and free searches
  remain covered. Confidence Engine criteria and stored schema are unchanged.

Twelve groups of corrections in this RC:

1. Fail-closed authentication: complete token pair and Supabase-confirmed email;
   phone confirmation alone does not authorize access. Expired, unconfirmed and
   failed sessions have distinct states.
2. Private session cleanup on logout/owner change; same-owner refresh preserves
   current work. Recovery tokens are removed from URL parameters after handling.
3. Paid-analysis re-entry guard and request identity before reservation, with
   failure-path tests for audit, completion and refunds. Business rules unchanged.
4. Checkout package-code, BRL currency and provider HTTPS URL validation;
   browser return parameters cannot grant credits. Only package code is submitted.
5. Bounded upload bytes/pixels, actual format/MIME checks, corrupt/multiframe
   rejection and EXIF cleanup before the paid analysis path.
6. Diagnostic token/password redaction and removal of raw errors from critical
   UI paths; failed SDK initialization presents a safe message.
7. Catalog refresh now reaches inner cache layers; public caches are bounded.
8. Catalog partial detail failures retain valid cards, detail work is capped at
   48 requests, and valid empty results differ from provider failure.
9. Collection pagination handles server-side caps and rejects repeated pages,
   partial failures and unexpected owners instead of returning misleading data.
10. Optimistic collection edits compare saved baseline fields; conflicts preserve
    entered values and do not report success or overwrite concurrent edits.
11. Malformed/untrusted public image URLs fail safely; snapshot normalization
    consistency is validated on load.
12. Critical auth/legal/profile messages and collection labels use the existing
    four-language translation system, including Spanish and Japanese coverage.

Limitations documented rather than hidden: dependency ranges are not a lockfile;
future releases require CI validation. Existing Streamlit width deprecations are
nonblocking. Full catalog detail calls remain sequential and can still be slow
under repeated timeouts; provider result limits mean this is not an exhaustive
catalog export. No claim of complete provider pagination is made.

## REQUIRES TEST ENVIRONMENT

These are production-readiness gates, not proven by mocks. They require TEST
service access and can be automated once a dedicated environment is available.

**2026-09-23 actual-service results:** approved TEST URL matched; Auth health and
Auth settings with the public key returned HTTP 200. A randomly named nonexistent
account was rejected with HTTP 400 / `invalid_credentials`, without a session.
REST schema requests returned HTTP 401, including the standard Authorization
header; the administrative key specifically received `Invalid API key`. The
public key works with Auth and must not be described as globally invalid.
Signup/email confirmation, two-user authenticated flows, effective RLS and credit
RPC verification are **BLOCKED**: no controlled TEST inbox/account credentials
were supplied and administrative provisioning is unavailable. The anonymous
collection request also returned 401; this alone does not prove owner isolation.
No credentials were modified, accounts created or stored rows changed.
TCGdex returned HTTP 200 and the expected Pikachu for `base1-58`. Gemini model
metadata was accessible, including both configured primary/fallback models;
no generation or end-to-end charged analysis was run.
The latter remains **BLOCKED** by unavailable TEST Auth/credit/audit integration.

- Supabase signup/email confirmation, login, expiration/refresh, recovery and
  logout against actual Auth configuration. Verify profile creation, initial
  credits and legal acceptance with two independent accounts.
- Effective RLS/grants for `profiles`, `analysis_runs`, `purchases`,
  `legal_acceptances`, `credit_packages`, `credit_package_prices` and
  `collection_items`. Collection migration is present and unchanged; verify the
  deployed owner policies and CRUD-only grants. Offline owner filters do not
  prove deployed RLS. Verify service-role keys remain server-only.
- SQL RPC implementations are absent from this repository: `reserve_credit`,
  `refund_credit`, `complete_credit_usage`, `start_analysis_run`,
  `complete_analysis_run`, `fail_analysis_run`, `update_analysis_catalog`,
  `record_legal_acceptance`. Confirm transactional ownership, idempotency by
  request ID, cross-session concurrency, network-ambiguous outcomes and exactly
  one charge/refund. A session guard is not a substitute for atomic SQL.
- `mercadopago-create-preference` and payment webhook implementation are absent.
  Verify server-owned package price/currency/credits, authenticated owner,
  webhook signature and provider-side payment lookup, pending/approved/rejected,
  duplicate/reordered delivery and exactly-once credit fulfillment. Use TEST
  buyers only. Confirm returned checkout URL matches the Brazilian allowlist.
  `payment_webhook.py` now supplies tested signature verification and an
  authenticated fixed-host provider lookup, but is not wired to an endpoint.
  It cannot grant credits or prove fulfillment. Payments are **NOT READY TO SELL**.
  See [payment audit](payment-audit.md) for the missing transactional contract.
- Real Gemini analysis and audit/completion/refund across failures, and TCGdex
  timeout/availability behavior. No paid analysis or payment was performed here.
- Deployment service configuration, required Secrets, package runtime and
  account/dashboard-triggered integrations cannot be established from this
  repository alone. No production deployment was performed.

## REQUIRES HUMAN VALIDATION

- Review the actually received confirmation/recovery email for clarity, branding
  and usable links on the intended mail clients.
- Judge responsive layout, contrast, card thumbnails and editor ergonomics on
  desktop/mobile with a real collection, including loading and error states.
- Native-language review of English, Portuguese, Spanish and Japanese critical
  messages and legal wording; automated presence checks do not establish quality.
- Judge real analysis usefulness and card-identification quality on representative
  photos without changing approved Confidence Engine criteria.
