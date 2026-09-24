# CardCraft Assistant (TEST)

The assistant is available in Home, the sidebar, and from a selected catalog
card. Its decision order is:

The assistant detects the language of each question independently of the
interface language. Deterministic replies and Gemini prompts use that language.
When a short query contains no language signal (for example a card name alone),
it continues in the last detected conversation language, then falls back to
the interface language. Catalog names and source-specific variant values remain
as recorded by the source.

1. The signed-in user's private `collection_items`, only for collection and
   ownership questions. Queries retain an explicit `user_id` filter and RLS.
2. `search_catalog_core` on the CardCraft catalog, requiring an exact name
   match and an unambiguous edition. The user may supply set and number.
3. The app's existing external catalog search if the local catalog misses.
4. Gemini only for unresolved general card questions. The question is sent to
   the existing model; private collection rows, notes and account details are
   never sent. Gemini is marked as unverified and is forbidden to claim live
   prices, catalog confirmation, authenticity or specific card identity.

Purchase/price questions never call Gemini. The interface provides direct
marketplace searches. It can show a dated TCGdex market reference supplied by
an already selected external card if the date is within seven days. Such a
reference is not a live listing, best offer, guaranteed price or appraisal.
Collection value is unavailable until per-card observations include source,
currency, condition, variant and timestamp; the collection table currently has
no price observations.

AI usage is capped at three attempts per Streamlit session and does not debit
analysis credits. This cap is a prototype cost guard, not an account-wide quota:
a persistent backend quota or credit policy is required before a broad public
rollout. Chat history is session-only, bounded to 32 messages and deleted on
sign-out. The local catalog's current TEST pilot is four cards, so external
catalog fallback will be common until coverage expands.

Validation: `python -m unittest tests.test_chatbot tests.test_navigation`.
Manual TEST checks: select a card from search, open the assistant, ask about
its characteristics and price, test an unknown general question, and confirm
that the Gemini request is only made for the unanswered question. Repeat with
another account to check collection isolation. No production changes.
