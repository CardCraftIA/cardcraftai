"""Private shop analytics. Counts outbound intent, never revenue or buyers."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit, urlunsplit

from shop import ITEMS, PARTNERS, tracked_path


def admin_ids(value):
    if isinstance(value, str):
        return {part.strip() for part in value.split(',') if part.strip()}
    if isinstance(value, (list, tuple)):
        return {str(part).strip() for part in value if str(part).strip()}
    return set()


def read_events(client, days=30):
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    result = (client.table('shop_outbound_events')
              .select('occurred_at,item_id,partner,campaign,is_affiliate')
              .gte('occurred_at', since).order('occurred_at', desc=True)
              .limit(5000).execute())
    return result.data or []


def summarize(events):
    daily, items, partners, campaigns = Counter(), Counter(), Counter(), Counter()
    for event in events:
        day = str(event.get('occurred_at', ''))[:10]
        if len(day) != 10:
            continue
        daily[day] += 1
        items[str(event.get('item_id'))] += 1
        partners[str(event.get('partner'))] += 1
        campaigns[str(event.get('campaign'))] += 1
    return daily, items, partners, campaigns


def commercial_insights(daily, items, partners, today):
    recent = sum(n for day, n in daily.items() if 0 <= (today - datetime.fromisoformat(day).date()).days < 7)
    prior = sum(n for day, n in daily.items() if 7 <= (today - datetime.fromisoformat(day).date()).days < 14)
    change = None if prior == 0 else round((recent - prior) / prior * 100)
    top_item = items.most_common(1)[0] if items else None
    top_partner = partners.most_common(1)[0] if partners else None
    return recent, prior, change, top_item, top_partner


def render_commercial(st, service_client, signing_secret, affiliate_links=None):
    import pandas as pd

    st.header('📊 Inteligência comercial · CardCraft Shop')
    st.caption('Painel interno: cliques de saída para marketplaces. Sem dados de venda, comissão ou faturamento.')
    try:
        events = read_events(service_client)
    except Exception:
        st.error('Não foi possível carregar os dados comerciais agora.')
        return
    daily, items, partners, campaigns = summarize(events)
    today = datetime.now(timezone.utc).date()
    seven_days, prior_week, change, top_item, top_partner = commercial_insights(daily, items, partners, today)
    columns = st.columns(3)
    columns[0].metric('Saídas · 30 dias', sum(daily.values()))
    columns[1].metric('Saídas · 7 dias', seven_days)
    columns[2].metric('Receita atribuída', 'Indisponível')
    st.caption('Um clique é uma intenção de visita, não uma pessoa única nem uma compra. Eventos podem incluir repetição ou automação.')
    if daily:
        st.subheader('Leitura comercial')
        if change is None:
            st.write(f'Últimos 7 dias: {seven_days} saídas. Ainda não há base na semana anterior para medir tendência.')
        else:
            st.write(f'Últimos 7 dias: {seven_days} saídas, {change:+d}% frente às {prior_week} da semana anterior.')
        st.write(f'Maior interesse: {top_item[0]} ({top_item[1]} saídas). Parceiro mais acessado: {PARTNERS[top_partner[0]][0]} ({top_partner[1]} saídas).')
        st.caption('Use esses sinais para priorizar categorias e campanhas; confirme vendas nos relatórios oficiais dos parceiros.')
    if daily:
        days = pd.date_range(today - timedelta(days=29), today)
        chart = pd.DataFrame({'Saídas': [daily.get(day.date().isoformat(), 0) for day in days]}, index=days)
        st.subheader('Saídas por dia · UTC')
        st.bar_chart(chart)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader('Marketplaces')
            st.bar_chart(pd.DataFrame({'Saídas': dict(partners.most_common())}))
        with c2:
            st.subheader('Interesses por categoria')
            st.bar_chart(pd.DataFrame({'Saídas': dict(items.most_common(10))}))
        st.subheader('Campanhas')
        st.dataframe(pd.DataFrame(campaigns.most_common(), columns=['Campanha', 'Saídas']), hide_index=True)
        if len(events) >= 5000:
            st.warning('O relatório atingiu 5.000 eventos. Use exportação agregada antes de tirar conclusões sobre o mês inteiro.')
    else:
        st.info('Os primeiros dados aparecerão quando visitantes abrirem links rastreados do Shop.')
    st.divider()
    st.subheader('Gerador de links rastreáveis')
    names = {item[0]: f'{item[1]} · {item[2]}' for item in ITEMS}
    item_id = st.selectbox('Categoria', list(names), format_func=lambda value: names[value], key='shop_link_item')
    partner = st.selectbox('Marketplace', list(PARTNERS), format_func=lambda value: PARTNERS[value][0], key='shop_link_partner')
    campaign = st.text_input('Campanha (letras minúsculas, números, _ ou -)', value='shop', max_chars=32, key='shop_link_campaign')
    query = st.text_input('Busca específica no marketplace (opcional)', max_chars=100, key='shop_link_query')
    try:
        path = tracked_path(item_id, partner, campaign, query, signing_secret)
        browser_url = st.context.url
        if isinstance(browser_url, bytes):
            browser_url = browser_url.decode('utf-8', errors='ignore')
        current = urlsplit(str(browser_url or ''))
        if current.scheme in ('http', 'https') and current.netloc:
            base = urlunsplit((current.scheme, current.netloc, current.path, '', ''))
            st.code(base + path, language=None)
            st.caption('Compartilhe este endereço. Ele contabiliza a saída e então abre a busca no marketplace selecionado. Não contém preço nem ID de usuário.')
        else:
            st.info('Abra o painel no endereço publicado do app para copiar um link completo.')
    except ValueError:
        st.warning('Confira a campanha e a busca antes de gerar o link.')
