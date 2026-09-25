# CardCraft Shop (staging)

The Shop is a public discovery tab opened from the signed-in app with
`?shop=1&lang=pt`. It offers 12 TCG shopping paths, text search, category
filters, a wishlist, and a **link cart**. The lists are stored in the visitor's
browser with `localStorage`; they are not synchronized between devices or
added to the private CardCraft collection. The shop does not show prices,
stock, delivery promises or a CardCraft checkout. Visitors complete purchases
directly with an external partner.

Current outgoing links are ordinary searches at TCGplayer and Amazon Brasil.
They are not represented as affiliate links or endorsements. TCGplayer's
published affiliate program uses Impact, and its partner guidelines govern
usage. Only approved, account-specific URLs should be inserted after the
CardCraftAI publisher account is enrolled. Configure full links in Streamlit
secrets, for example:

```toml
[SHOP_AFFILIATE_LINKS]
"pokemon-cards:tcgplayer" = "https://www.tcgplayer.com/search/all/product?q=Pokemon&ref=YOUR_APPROVED_LINK"
```

The example is illustrative and must not be deployed as a real affiliate
link. Every configured link is required to use HTTPS and a partner allowlist;
an invalid URL falls back to the ordinary search. The UI labels approved
links as affiliate links and displays a visible commission disclosure.
Review each program's landing page and link rules before activation. No
affiliate credentials, user identifiers or private collection data are placed
in URLs. Amazon links require an approved local program account and its
specified disclosure before monetization.

The storefront uses trusted, repository-owned HTML and JavaScript with
`st.html(..., unsafe_allow_javascript=True)` for local browser persistence.
Never inject user text, LLM output or untrusted remote HTML into that template.
Product descriptions and partner URLs are rendered as escaped text/attributes.
It is isolated from authentication, Gemini and credits. Only the redirect
handler writes anonymous outbound events to Supabase TEST.

## Commercial intelligence (TEST)

When the server has a service key, all shop destinations are signed CardCraft
links. The public redirect validates item, marketplace, campaign and optional
search term before building a destination from the approved partner list. It
records **one outbound click event** and forwards the visitor. A failed
analytics write does not block navigation. The event contains only time,
category ID, partner, campaign and affiliate flag; no visitor ID, IP address,
account, cookie or collection details are saved in the analytics table.
Automated traffic and repeated clicks can inflate this directional metric.

`shop_outbound_events` is private with RLS enabled and no public grants. A
verified signed-in user sees **Shop Intelligence** only when their Auth user ID
is listed in the server secret `SHOP_ADMIN_USER_IDS` (comma-separated string or
array). The panel aggregates 30 days of outbound clicks into daily,
marketplace, item and campaign views. It also signs shareable category or
card-search links for TCGplayer/Amazon. If you want a dedicated signing key,
set `SHOP_LINK_SIGNING_KEY` in server secrets; otherwise the existing server
service key signs links. Rotating the signing key invalidates old links.

Clicks and outbound intents are **not** qualified unique visitors, sales,
commissions, conversion rates or revenue. Those measures require partner
conversion reports or an approved API integration with matching campaign IDs.
Do not infer revenue from click counts or estimated marketplace prices. The
dashboard intentionally displays revenue as unavailable. Only staging and
Supabase TEST are in scope until separately promoted.

Validation: `PYTHONPATH=tests python -m unittest tests.test_shop tests.test_shop_intelligence tests.test_navigation`.
