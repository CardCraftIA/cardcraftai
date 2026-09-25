# Atlas · CardCraftAI (TEST)

The assistant is available in Home, the sidebar, and from a selected catalog
card. Its decision order is:

The chat input accepts typed or pasted text, attached/pasted JPG, PNG or WEBP
images, and PDF files. Streamlit 1.64 or later is required for clipboard file
pasting. The application validates the actual file content; images are limited
to 15 MB and 25 megapixels, then reduced to at most 1600 pixels per side. PDFs
are limited to 8 MB and five pages; encrypted documents are rejected. When a
user specifically asks for the text of a searchable PDF, the text is extracted
locally without Gemini. Visual interpretation of a photo or PDF uses one of the
session's three Gemini attempts and is labeled as unverified. Attachment bytes
are neither written to Supabase nor kept in chat history; only the filename is
shown after the request.

The conversation is the only card entry field: users may type a card name or
include a name, set and number in the message (for example, "carta Pikachu do
set Base Set #58"). A previously selected catalog card remains available as
context. Ambiguous editions are listed for clarification.

For a photo in chat, one Gemini vision call extracts only visible name, set,
collector number, rarity, HP, language and physical features as structured
observations. Atlas then reads Catalog Core and, if absent, the external
catalog during that request. It compares an edition only when both set and
number are visible and exactly match one catalog record. Multiple editions,
unreadable fields and disagreements remain explicit. The result displays the
source and UTC query time. Catalog data can lag its upstream source; this is
not a live market feed. Matching a catalog entry does not prove the physical
card is genuine. The image bytes are not stored in chat history or the DB.

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

Validation: `python -m unittest tests.test_chatbot tests.test_chatbot_attachments tests.test_navigation`.
Manual TEST checks: select a card from search, open the assistant, ask about
its characteristics and price, test an unknown general question, and confirm
that the Gemini request is only made for the unanswered question. Repeat with
another account to check collection isolation. No production changes.

## Atualização semanal do conhecimento

Atlas consulta primeiro o catálogo canônico e a coleção do próprio usuário. A
rotina semanal compara fontes TCG públicas com licença compatível, registra
revisão, hash, data e divergências e só incorpora registros verificados no
ambiente TEST. Informações geradas pela IA não são fatos do catálogo. A
expansão para outros jogos exige identificar fontes, licença e esquema de
variantes antes da importação. Cotações e anúncios precisam de fonte e data
próprias; a revisão do catálogo não torna preços em tempo real.

A rotina recorrente é operacional, fora do processo Streamlit. A importação
completa do snapshot TCGdex não deve ser feita sem avaliar tamanho da base,
limites de armazenamento e conflitos. Produção exige promoção separada.
