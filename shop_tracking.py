"""Allowlisted outbound redirects and anonymous commercial event capture."""
from __future__ import annotations

import json

from shop import resolve_tracked


def process_outbound(st, params, secret, supabase_url, service_key, create_client, affiliates=None):
    resolved = resolve_tracked(params, secret, affiliates)
    if not resolved:
        st.error('Link do Shop inválido ou expirado.')
        return False
    destination, event = resolved
    if supabase_url and service_key:
        try:
            create_client(supabase_url, service_key).table('shop_outbound_events').insert(event).execute()
        except Exception:
            # An analytics outage must never trap a visitor on the redirect.
            pass
    safe_url = json.dumps(destination).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    st.html(f'<script>window.location.replace({safe_url})</script>', unsafe_allow_javascript=True)
    st.link_button('Abrir marketplace ↗', destination)
    st.caption('Você está saindo do CardCraftAI. Preços e compras pertencem à loja externa.')
    return True
