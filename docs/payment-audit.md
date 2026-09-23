# Payment release gate — NOT READY TO SELL

Audit date: 2026-09-23. Integration branch only; nothing deployed or migrated.

| Requirement | Evidence / status |
| --- | --- |
| Server-created preference | App calls `mercadopago-create-preference`; its source is absent. BLOCKED. |
| Server price, currency, credits | App sends only a validated package code and user bearer token. Authoritative backend validation is absent/unverified. BLOCKED. |
| Purchase owner authentication | User token is forwarded; endpoint validation and binding to a database owner cannot be inspected. BLOCKED. |
| Webhook endpoint | No endpoint implementation/deployment in this repository. BLOCKED. |
| Signature verification | New isolated Python component verifies HMAC, rejects malformed/tampered IDs and timestamps, and uses constant-time comparison. Offline tests pass. Not connected to a live webhook. |
| Provider lookup | Component fetches `/v1/payments/{numeric_id}` only after signature validation, with timeout, no redirects, matching response ID and safe errors. Mock-tested, not verified with a TEST seller. |
| Idempotency / duplicate / reordered delivery | No durable ledger or atomic fulfillment SQL is available. BLOCKED. A timestamp window is not idempotency. |
| Exactly-once credit | No implementation can be proven. BLOCKED. Browser return parameters never credit an account. |
| Approved/pending/rejected/cancelled | UI has labels; authoritative state transitions and settlement are absent. BLOCKED. |

## Implemented without credentials

`payment_webhook.py` is a server-side building block, deliberately unused by the
Streamlit app. It validates a signed notification and fetches the authoritative
payment. It does not listen for webhooks, create preferences, persist state or
alter balances. Never treat a returned payment dictionary as authorization to
grant credits. Tests use synthetic signatures and mocked HTTP only.

Signature and lookup follow the provider's
[official schema](https://github.com/mercadopago/openapi/blob/main/schemas/webhooks.yaml).
The adapter must use URL `data.id`, support payment notifications only, keep the
webhook secret server-side, and respond/retry according to the
[provider webhook documentation](https://www.mercadopago.com.br/developers/en/docs/checkout-pro-preferences/additional-content/notifications/webhooks).

## Why the remaining backend was not guessed

Only the collection migration is versioned. Definitions/constraints/triggers for
`purchases`, `profiles`, package pricing and the credit ledger are missing.
TEST schema inspection returned 401 with both local credentials. Creating a new
ledger against guessed schemas could conflict with an existing webhook and
double-credit accounts. No migration, deployed endpoint or monetary rule was
invented. Existing refund/subscription behavior also needs its authoritative
business contract before a replacement can safely be wired.

## Required before sales

1. Export/version the existing TEST schema, credit RPCs and Edge Functions;
   reconcile their ownership and transaction contracts before implementation.
2. Preference endpoint authenticates the user and reads an active server-owned
   package/price. Persist purchase owner, currency, amount, credits and a stable
   idempotency key before calling the provider; retries must recover that purchase.
3. Webhook adapter validates the signature, looks up the payment and matches
   environment, seller, external reference, currency and exact amount against the
   stored purchase. Never trust the notification's status/amount or browser data.
4. A single database transaction locks the purchase, deduplicates provider payment
   and purchase IDs, validates transitions and grants credits exactly once. Handle
   duplicate, concurrent and reordered notifications without balance regression.
   Refund/chargeback/subscription policy must match existing approved rules.
5. Verify sandbox preference, approved/pending/rejected/cancelled payments,
   signature failures, provider outages and duplicate/reordered deliveries with
   Mercado Pago TEST seller/buyer configuration. No real payment is authorized.

Until those checks pass, both payment readiness and production publication remain
blocked. An HTTP 200 from Streamlit or a mock test is not payment certification.
