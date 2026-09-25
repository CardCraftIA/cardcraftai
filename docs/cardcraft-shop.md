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
It is isolated from authentication, Gemini, credits and Supabase writes.

Validation: `PYTHONPATH=tests python -m unittest tests.test_shop tests.test_navigation`.
