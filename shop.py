"""Public CardCraft Shop discovery page; no local sales or checkout."""
from __future__ import annotations

import json
from urllib.parse import quote_plus, urlparse


PARTNERS = {
    'tcgplayer': ('TCGplayer', 'https://www.tcgplayer.com/search/all/product?q='),
    'amazon_br': ('Amazon Brasil', 'https://www.amazon.com.br/s?k='),
}
ALLOWED_AFFILIATE_HOSTS = {
    'tcgplayer': {'tcgplayer.com', 'www.tcgplayer.com', 'impact.com', 'www.impact.com'},
    'amazon_br': {'amazon.com.br', 'www.amazon.com.br'},
}

ITEMS = [
    ('pokemon-cards', 'Pokémon', 'singles', 'Pokémon TCG cards', '⚡', 'cards'),
    ('magic-cards', 'Magic', 'singles', 'Magic The Gathering cards', '✦', 'cards'),
    ('yugioh-cards', 'Yu-Gi-Oh!', 'singles', 'Yu-Gi-Oh cards', '◈', 'cards'),
    ('onepiece-cards', 'One Piece', 'singles', 'One Piece Card Game cards', '☠', 'cards'),
    ('pokemon-sealed', 'Pokémon', 'boosters', 'Pokemon TCG booster box', '⚡', 'sealed'),
    ('magic-sealed', 'Magic', 'boosters', 'Magic The Gathering booster box', '✦', 'sealed'),
    ('yugioh-sealed', 'Yu-Gi-Oh!', 'boosters', 'Yu-Gi-Oh booster box', '◈', 'sealed'),
    ('onepiece-sealed', 'One Piece', 'boosters', 'One Piece Card Game booster box', '☠', 'sealed'),
    ('sleeves', 'Acessórios', 'sleeves', 'trading card sleeves', '▣', 'accessories'),
    ('binders', 'Acessórios', 'binders', 'trading card binder', '▤', 'accessories'),
    ('deckboxes', 'Acessórios', 'deckboxes', 'trading card deck box', '▥', 'accessories'),
    ('toploaders', 'Acessórios', 'toploaders', 'trading card top loaders', '◇', 'accessories'),
]

COPY = {
    'pt': {'subtitle': 'Encontre. Organize. Escolha onde comprar.', 'intro': 'Um ponto de partida para explorar cards, produtos lacrados e acessórios de TCG.',
           'disclosure': 'Links externos: o CardCraft Shop não vende nem processa pagamentos. Alguns links podem gerar comissão de afiliado, sem custo adicional para você.',
           'search': 'Buscar por jogo, carta ou acessório', 'all': 'Tudo', 'cards': 'Cartas', 'sealed': 'Lacrados', 'accessories': 'Acessórios', 'singles': 'Cartas avulsas', 'boosters': 'Boosters e boxes', 'sleeves': 'Sleeves', 'binders': 'Fichários', 'deckboxes': 'Deck boxes', 'toploaders': 'Toploaders',
           'discover': 'Explorar', 'wishlist': 'Lista de desejos', 'cart': 'Carrinho de links', 'add': 'Adicionar ao carrinho',
           'remove': 'Remover', 'open': 'Ver no parceiro', 'empty': 'Sua lista está vazia.', 'no_results': 'Nenhuma opção encontrada.',
           'note': 'Preços, disponibilidade, envio e condições são definidos pelo parceiro. Confirme os detalhes antes de comprar.',
           'affiliate': 'Link de afiliado', 'standard': 'Link externo', 'back': 'Voltar ao CardCraftAI',
           'cart_note': 'Este carrinho organiza links. A compra é feita separadamente em cada loja.', 'featured': 'Explore seu próximo achado',
           'saved': 'Salvo no seu navegador', 'qty': 'Quantidade', 'product_note': 'Explore opções nos parceiros, sem preço ou estoque prometido.'},
    'en': {'subtitle': 'Discover. Save. Choose where to shop.', 'intro': 'One place to explore TCG cards, sealed products and accessories.',
           'disclosure': 'External links: CardCraft Shop does not sell items or process payments. Some links may earn an affiliate commission at no extra cost to you.',
           'search': 'Search games, cards or accessories', 'all': 'All', 'cards': 'Cards', 'sealed': 'Sealed', 'accessories': 'Accessories', 'singles': 'Single cards', 'boosters': 'Boosters & boxes', 'sleeves': 'Sleeves', 'binders': 'Binders', 'deckboxes': 'Deck boxes', 'toploaders': 'Toploaders',
           'discover': 'Explore', 'wishlist': 'Wishlist', 'cart': 'Link cart', 'add': 'Add to cart',
           'remove': 'Remove', 'open': 'Visit partner', 'empty': 'Your list is empty.', 'no_results': 'No matches found.',
           'note': 'Prices, availability, delivery and terms are set by the partner. Check details before buying.',
           'affiliate': 'Affiliate link', 'standard': 'External link', 'back': 'Back to CardCraftAI',
           'cart_note': 'This cart organizes links. Purchases happen separately at each store.', 'featured': 'Explore your next find',
           'saved': 'Saved in your browser', 'qty': 'Quantity', 'product_note': 'Explore partner options without promised prices or stock.'},
    'es': {'subtitle': 'Descubre. Guarda. Elige dónde comprar.', 'intro': 'Explora cartas TCG, productos sellados y accesorios.',
           'disclosure': 'Enlaces externos: CardCraft Shop no vende ni procesa pagos. Algunos enlaces pueden generar comisión de afiliado sin coste adicional.',
           'search': 'Buscar juegos, cartas o accesorios', 'all': 'Todo', 'cards': 'Cartas', 'sealed': 'Sellados', 'accessories': 'Accesorios', 'singles': 'Cartas sueltas', 'boosters': 'Sobres y cajas', 'sleeves': 'Fundas', 'binders': 'Archivadores', 'deckboxes': 'Cajas de mazo', 'toploaders': 'Protectores rígidos',
           'discover': 'Explorar', 'wishlist': 'Favoritos', 'cart': 'Carrito de enlaces', 'add': 'Añadir al carrito',
           'remove': 'Eliminar', 'open': 'Ver en la tienda', 'empty': 'Tu lista está vacía.', 'no_results': 'Sin resultados.',
           'note': 'El socio determina precios, disponibilidad, envío y condiciones. Comprueba los detalles antes de comprar.',
           'affiliate': 'Enlace de afiliado', 'standard': 'Enlace externo', 'back': 'Volver a CardCraftAI',
           'cart_note': 'Este carrito organiza enlaces. Cada compra se hace en la tienda externa.', 'featured': 'Explora tu próximo hallazgo',
           'saved': 'Guardado en tu navegador', 'qty': 'Cantidad', 'product_note': 'Explora opciones sin promesas de precio o disponibilidad.'},
    'ja': {'subtitle': '見つけて、保存して、購入先を選ぶ。', 'intro': 'TCGカード、未開封商品、アクセサリーを探せます。',
           'disclosure': '外部リンク：CardCraft Shopは販売や決済を行いません。一部のリンクから購入されると紹介料を受け取る場合があります。',
           'search': 'ゲーム・カード・用品を検索', 'all': 'すべて', 'cards': 'カード', 'sealed': '未開封', 'accessories': '用品', 'singles': 'シングルカード', 'boosters': 'パック・ボックス', 'sleeves': 'スリーブ', 'binders': 'バインダー', 'deckboxes': 'デッキケース', 'toploaders': '硬質ケース',
           'discover': '探す', 'wishlist': 'お気に入り', 'cart': 'リンクのカート', 'add': 'カートに追加',
           'remove': '削除', 'open': '販売先を見る', 'empty': 'リストは空です。', 'no_results': '見つかりませんでした。',
           'note': '価格、在庫、配送、条件は販売先が決めます。購入前にご確認ください。',
           'affiliate': '紹介リンク', 'standard': '外部リンク', 'back': 'CardCraftAIに戻る',
           'cart_note': 'このカートはリンク整理用です。購入は各販売先で行います。', 'featured': '次の一枚を探そう',
           'saved': 'ブラウザに保存', 'qty': '数量', 'product_note': '価格や在庫の保証なく販売先を探せます。'},
}


def partner_link(item_id: str, partner: str, query: str, configured=None):
    """Only administrator supplied, HTTPS allowlisted links can be affiliates."""
    configured = configured if isinstance(configured, dict) else {}
    value = configured.get(f'{item_id}:{partner}')
    if isinstance(value, str):
        parsed = urlparse(value)
        if parsed.scheme == 'https' and parsed.hostname in ALLOWED_AFFILIATE_HOSTS[partner] and not parsed.username and not parsed.password:
            return value, True
    return PARTNERS[partner][1] + quote_plus(query), False


def shop_payload(configured=None):
    products = []
    for item_id, game, category, query, icon, group in ITEMS:
        links = []
        for partner, (label, _) in PARTNERS.items():
            url, affiliate = partner_link(item_id, partner, query, configured)
            links.append({'label': label, 'url': url, 'affiliate': affiliate})
        products.append({'id': item_id, 'game': game, 'category': category, 'query': query,
                         'icon': icon, 'group': group, 'links': links})
    return products


def render_shop(st, language='pt', affiliate_links=None):
    language = language if language in COPY else 'pt'
    payload = {'items': shop_payload(affiliate_links), 'copy': COPY[language]}
    safe_json = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    st.html(SHOP_HTML.replace('__SHOP_DATA__', safe_json), unsafe_allow_javascript=True)


SHOP_HTML = r'''<div id="cardcraft-shop">
<style>
#cardcraft-shop{--ink:#edf3ff;--muted:#a9b8cf;--line:#354862;--blue:#59d7fb;--violet:#a98bff;color:var(--ink);font:15px/1.5 Inter,ui-sans-serif,system-ui,sans-serif;max-width:1240px;margin:auto}
#cardcraft-shop *{box-sizing:border-box}#cardcraft-shop button,#cardcraft-shop input{font:inherit}#cardcraft-shop button{cursor:pointer}
#cardcraft-shop .shop-top{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1rem 0 1.8rem;flex-wrap:wrap}
#cardcraft-shop .brand{display:flex;align-items:center;gap:.8rem;text-decoration:none;color:#fff;font-size:1.25rem;font-weight:850;letter-spacing:-.03em}
#cardcraft-shop .brand span:first-child{display:grid;place-items:center;width:52px;height:52px;border-radius:15px;background:linear-gradient(145deg,#8b6cff,#2563eb);font-size:1.85rem;box-shadow:0 10px 30px #33298655}
#cardcraft-shop nav{display:flex;gap:.4rem;flex-wrap:wrap}#cardcraft-shop .navbtn,#cardcraft-shop .chip{border:1px solid var(--line);color:var(--ink);background:#17253c;border-radius:999px;padding:.62rem 1rem}
#cardcraft-shop .navbtn[aria-current="page"],#cardcraft-shop .chip[aria-pressed="true"]{border-color:#a98bff;background:#6e55b244}
#cardcraft-shop .hero{position:relative;overflow:hidden;padding:clamp(1.5rem,4vw,3.2rem);border:1px solid #705ca675;border-radius:28px;background:radial-gradient(circle at 87% 20%,#6351b055,transparent 33%),linear-gradient(125deg,#202b4d,#101d32 66%);box-shadow:0 25px 70px #0005}
#cardcraft-shop .eyebrow{text-transform:uppercase;letter-spacing:.18em;color:#92dff4;font-weight:800;font-size:.76rem}#cardcraft-shop h1{font-size:clamp(2.1rem,5vw,4.5rem);line-height:1.06;letter-spacing:-.05em;margin:.5rem 0 1rem;max-width:720px}
#cardcraft-shop .hero p{max-width:630px;color:#bfd0e6;font-size:1.05rem}#cardcraft-shop .hero-art{position:absolute;right:5%;top:10%;font-size:clamp(5rem,12vw,12rem);opacity:.22;transform:rotate(-18deg);pointer-events:none}
#cardcraft-shop .disclosure,#cardcraft-shop .note{color:#b5c5da;background:#122138;border:1px solid #344964;border-radius:14px;padding:.85rem 1.05rem;margin:1.25rem 0}
#cardcraft-shop .controls{display:flex;gap:1rem;justify-content:space-between;align-items:center;flex-wrap:wrap;margin:2rem 0 1.2rem}#cardcraft-shop h2{font-size:1.55rem;letter-spacing:-.03em;margin:0}
#cardcraft-shop .search{width:min(100%,370px);background:#111d31;color:#fff;border:1px solid #516485;border-radius:13px;padding:.78rem 1rem;outline:none}#cardcraft-shop .search:focus{border-color:var(--blue);box-shadow:0 0 0 3px #59d7fb33}
#cardcraft-shop .chips{display:flex;gap:.55rem;flex-wrap:wrap;margin:0 0 1.2rem}#cardcraft-shop .grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}
#cardcraft-shop .product{border:1px solid #354862;border-radius:20px;background:linear-gradient(145deg,#1b2a45,#111d32);padding:1.15rem;min-width:0;display:flex;flex-direction:column;gap:.65rem}
#cardcraft-shop .product-art{height:128px;display:grid;place-items:center;border-radius:14px;background:radial-gradient(circle at 50% 35%,#7561c368,#243855 68%);font-size:3.6rem;color:#dce6ff}
#cardcraft-shop .product small{color:#9be2f4;font-weight:750;text-transform:uppercase;letter-spacing:.08em}#cardcraft-shop .product h3{margin:0;font-size:1.18rem}#cardcraft-shop .product p{margin:0;color:var(--muted)}
#cardcraft-shop .actions{display:flex;gap:.5rem;margin-top:auto;flex-wrap:wrap}#cardcraft-shop .actions button,#cardcraft-shop .partners a,#cardcraft-shop .row button{border:1px solid #62718a;border-radius:11px;background:#263956;color:#fff;padding:.6rem .75rem;text-decoration:none;font-weight:700}
#cardcraft-shop .actions .primary{background:linear-gradient(100deg,#765ce4,#436bd2);border-color:#806bef}#cardcraft-shop .actions .heart[aria-pressed="true"]{color:#ff9cbf;border-color:#ff9cbf}
#cardcraft-shop .partners{display:flex;gap:.45rem;flex-wrap:wrap}#cardcraft-shop .partners a{font-size:.86rem;padding:.5rem .7rem;background:#13243c}#cardcraft-shop .partners span{font-size:.72rem;opacity:.78;display:block;font-weight:500}
#cardcraft-shop .row{display:flex;align-items:center;gap:1rem;justify-content:space-between;border-bottom:1px solid #354862;padding:1rem 0;flex-wrap:wrap}#cardcraft-shop .row strong{min-width:180px}#cardcraft-shop .row input{width:60px;border:1px solid #586d89;border-radius:8px;background:#122138;color:#fff;padding:.4rem}
#cardcraft-shop .muted{color:var(--muted)}#cardcraft-shop .empty{padding:2rem;border:1px dashed #536580;border-radius:15px;color:#c0ccdf;text-align:center}
@media(max-width:860px){#cardcraft-shop .grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:600px){#cardcraft-shop .grid{grid-template-columns:1fr}#cardcraft-shop .hero-art{opacity:.09}#cardcraft-shop .row{align-items:flex-start}}
</style>
<header class="shop-top"><a class="brand" href="./" aria-label="CardCraftAI"><span aria-hidden="true">🃏</span><span>CardCraft <span style="color:#a98bff">Shop</span></span></a><nav aria-label="Shop"><button class="navbtn" data-view="discover"></button><button class="navbtn" data-view="wishlist"></button><button class="navbtn" data-view="cart"></button></nav></header>
<main><section class="hero"><div class="eyebrow">CardCraftAI · TCG discovery</div><h1 id="shop-subtitle"></h1><p id="shop-intro"></p><div class="hero-art" aria-hidden="true">🃏</div></section><p class="disclosure" id="shop-disclosure"></p><div class="controls"><h2 id="shop-heading"></h2><input class="search" type="search" id="shop-search" maxlength="80"></div><div class="chips" id="shop-filters"></div><div id="shop-content"></div><p class="note" id="shop-note"></p></main>
<script>
(()=>{'use strict';const root=document.getElementById('cardcraft-shop');if(!root)return;
const data=__SHOP_DATA__,items=data.items,c=data.copy,byId=Object.fromEntries(items.map(p=>[p.id,p]));
const storeKey='cardcraft-shop-v1';let saved={wishlist:[],cart:{}};
try{const raw=JSON.parse(localStorage.getItem(storeKey)||'{}');if(Array.isArray(raw.wishlist))saved.wishlist=raw.wishlist.filter(id=>byId[id]).slice(0,100);if(raw.cart&&typeof raw.cart==='object')for(const [id,n] of Object.entries(raw.cart))if(byId[id]&&Number.isInteger(n)&&n>0)saved.cart[id]=Math.min(n,99)}catch(_){}
const state={view:'discover',filter:'all',search:'',...saved};
const persist=()=>{try{localStorage.setItem(storeKey,JSON.stringify({wishlist:state.wishlist,cart:state.cart}))}catch(_){}};
const esc=s=>String(s).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const title=p=>`${p.game} · ${c[p.category]}`;
const links=p=>`<div class="partners">${p.links.map(link=>`<a target="_blank" rel="${link.affiliate?'sponsored ':''}noopener noreferrer" href="${esc(link.url)}">${esc(link.label)}<span>${esc(link.affiliate?c.affiliate:c.standard)} ↗</span></a>`).join('')}</div>`;
function render(){root.querySelector('#shop-subtitle').textContent=c.subtitle;root.querySelector('#shop-intro').textContent=c.intro;root.querySelector('#shop-disclosure').textContent=c.disclosure;root.querySelector('#shop-note').textContent=state.view==='cart'?c.cart_note+' '+c.note:c.note;
root.querySelectorAll('.navbtn').forEach(b=>{b.textContent=state.view===b.dataset.view?({'discover':c.discover,'wishlist':c.wishlist,'cart':c.cart}[b.dataset.view]):({'discover':c.discover,'wishlist':c.wishlist,'cart':c.cart}[b.dataset.view]);if(b.dataset.view==='cart')b.textContent+=` (${Object.keys(state.cart).length})`;if(b.dataset.view==='wishlist')b.textContent+=` (${state.wishlist.length})`;b.setAttribute('aria-current',state.view===b.dataset.view?'page':'false')});
root.querySelector('#shop-heading').textContent=state.view==='discover'?c.featured:state.view==='wishlist'?c.wishlist:c.cart;
root.querySelector('#shop-search').placeholder=c.search;root.querySelector('#shop-search').hidden=state.view!=='discover';
const filters=root.querySelector('#shop-filters');filters.hidden=state.view!=='discover';filters.innerHTML=['all','cards','sealed','accessories'].map(k=>`<button class="chip" data-filter="${k}" aria-pressed="${state.filter===k}">${esc(c[k])}</button>`).join('');
const body=root.querySelector('#shop-content');let list=items;
if(state.view==='wishlist')list=items.filter(p=>state.wishlist.includes(p.id));
else if(state.view==='cart')list=items.filter(p=>state.cart[p.id]);
else list=items.filter(p=>(state.filter==='all'||p.group===state.filter)&&`${p.game} ${p.category} ${c[p.category]} ${p.query}`.toLocaleLowerCase().includes(state.search.toLocaleLowerCase()));
if(!list.length){body.innerHTML=`<div class="empty">${esc(state.view==='discover'?c.no_results:c.empty)}</div>`;return}
if(state.view==='cart'){body.innerHTML=list.map(p=>`<div class="row"><strong>${esc(title(p))}</strong><label>${esc(c.qty)} <input type="number" min="1" max="99" value="${state.cart[p.id]}" data-qty="${p.id}"></label>${links(p)}<button data-remove="${p.id}">${esc(c.remove)}</button></div>`).join('');return}
body.innerHTML=`<div class="grid">${list.map(p=>`<article class="product"><div class="product-art" aria-hidden="true">${esc(p.icon)}</div><small>${esc(p.game)} · ${esc(c[p.group])}</small><h3>${esc(c[p.category])}</h3><p>${esc(c.product_note)}</p><div class="actions"><button class="primary" data-add="${p.id}">${esc(c.add)}</button><button class="heart" data-wish="${p.id}" aria-label="${esc(c.wishlist)}: ${esc(title(p))}" aria-pressed="${state.wishlist.includes(p.id)}">♥</button></div>${links(p)}</article>`).join('')}</div>`}
root.addEventListener('click',e=>{const b=e.target.closest('button');if(!b||!root.contains(b))return;
if(b.dataset.view)state.view=b.dataset.view;
if(b.dataset.filter)state.filter=b.dataset.filter;
if(b.dataset.add)state.cart[b.dataset.add]=Math.min(99,(state.cart[b.dataset.add]||0)+1);
if(b.dataset.wish)state.wishlist=state.wishlist.includes(b.dataset.wish)?state.wishlist.filter(id=>id!==b.dataset.wish):[...state.wishlist,b.dataset.wish];
if(b.dataset.remove)delete state.cart[b.dataset.remove];persist();render()});
root.querySelector('#shop-search').addEventListener('input',e=>{state.search=e.target.value;render();root.querySelector('#shop-search').focus()});
root.addEventListener('change',e=>{if(!e.target.dataset.qty)return;const n=Number.parseInt(e.target.value,10);state.cart[e.target.dataset.qty]=Number.isFinite(n)?Math.max(1,Math.min(n,99)):1;persist();render()});
render()})();
</script></div>'''
