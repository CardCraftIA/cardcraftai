"""Private collection: authenticated Supabase client only; no AI or credit calls."""
from urllib.parse import urlparse
from collection_exports import export_collection

CONDITIONS = ('Not assessed', 'Near Mint', 'Lightly Played', 'Moderately Played', 'Heavily Played', 'Damaged')
CARD_LANGUAGES = ('', 'English', 'Portuguese', 'Spanish', 'Japanese', 'Korean', 'French', 'German', 'Italian', 'Chinese', 'Other')
VARIANTS = ('', 'Regular', 'Holo', 'Reverse Holo', '1st Edition', 'Unlimited', 'Promo', 'Full Art', 'Alternate Art')


def safe_image(value):
    value = str(value or '')
    parsed = urlparse(value)
    return value if parsed.scheme == 'https' and parsed.hostname in {'assets.tcgdex.net', 'images.pokemontcg.io'} else ''


def catalog_record(card, user_id):
    identity, name = str(card.get('id') or '').strip(), str(card.get('name') or '').strip()
    if not identity or not name or len(identity) > 200 or len(name) > 200:
        raise ValueError('Invalid catalog identity')
    return dict(user_id=user_id, catalog_id=identity, card_name=name,
                set_name=str((card.get('set') or {}).get('name') or ''),
                card_number=str(card.get('number') or ''),
                image_url=safe_image((card.get('images') or {}).get('small')))


def validate_edit(quantity, condition, language, variant, notes, wishlist):
    if isinstance(quantity, bool) or not isinstance(quantity, int) or not 0 <= quantity <= 9999:
        raise ValueError('Invalid quantity')
    if condition not in CONDITIONS:
        raise ValueError('Invalid condition')
    values = dict(language=language.strip(), variant=variant.strip(), notes=notes.strip())
    if any(len(values[k]) > limit for k, limit in [('language', 80), ('variant', 120), ('notes', 2000)]):
        raise ValueError('Text too long')
    return dict(quantity=quantity, condition=condition, wishlist=bool(wishlist), **values)


def save_edit(client, user_id, item_id, values):
    # Explicit owner filter is defense in depth; RLS remains authoritative.
    return client.table('collection_items').update(values).eq('user_id', user_id).eq('id', item_id).execute()


def render_collection(st, client, user_id, portuguese=False, translate=None):
    # Keep the collection theme inside its own subtree, including in the real app.
    with st.container(key='collection_v2'):
        _render_collection(st, client, user_id, portuguese, translate)


def _render_collection(st, client, user_id, portuguese=False, translate=None):
    def tr(pt, en):
        return pt if portuguese else en
    def feedback(key):
        if translate is not None:
            return translate(key)
        return {
            'collection_saved': tr('Alterações salvas com sucesso.', 'Changes saved successfully.'),
            'collection_save_error': tr('Não foi possível salvar as alterações. Seus dados foram mantidos. Tente novamente.', 'Could not save your changes. Your entries have been kept. Please try again.'),
            'collection_saving': tr('Salvando…', 'Saving…'),
        }[key]

    def begin_save(key):
        st.session_state[key] = True
    st.markdown('''<style>
    .st-key-collection_v2 {
        background:radial-gradient(ellipse at top right,#193a35 0%,#111d27 40%,#0b131d 100%);
        color:#edf4f9;border:1px solid #2a3d49;border-radius:22px;
        padding:clamp(16px,3vw,32px);box-shadow:0 18px 48px #06101a20;
    }
    .st-key-collection_v2 h2 {color:#edf4f9;font-family:Georgia,serif;font-size:2rem;letter-spacing:-.025em;padding-top:0;}
    .st-key-collection_v2 h3 {color:#edf4f9;font-size:1.12rem;line-height:1.4;overflow-wrap:anywhere;}
    .st-key-collection_v2 [data-testid="stCaptionContainer"],
    .st-key-collection_v2 [data-testid="stCaptionContainer"] p {color:#aebfcb;}
    .st-key-collection_v2 [data-testid="stWidgetLabel"] p,
    .st-key-collection_v2 [data-testid="stRadio"] p,
    .st-key-collection_v2 [data-testid="stCheckbox"] p {color:#dae6ed;font-size:.875rem;}
    .st-key-collection_v2 [data-testid="stMetric"] {
        background:linear-gradient(130deg,#1a2b35,#121f29);border:1px solid #314450;
        border-radius:14px;padding:16px 20px;border-top:2px solid #59cfae;
    }
    .st-key-collection_v2 [data-testid="stMetricLabel"] p {color:#aec1cd;font-size:.8rem;}
    .st-key-collection_v2 [data-testid="stMetricValue"] {color:#edf4f9;font-size:1.8rem;font-weight:650;}
    .st-key-collection_v2 .st-key-collection_toolbar {
        background:#121f2b;border:1px solid #2c414e;border-radius:16px;padding:16px 18px;
    }
    .st-key-collection_v2 [data-testid="stTextInputRootElement"],
    .st-key-collection_v2 [data-testid="stTextAreaRootElement"],
    .st-key-collection_v2 [data-testid="stNumberInputContainer"] {
        background:#172936;border-color:#405766;border-radius:10px;
    }
    .st-key-collection_v2 input,.st-key-collection_v2 textarea {
        color:#edf4f9;background:#172936;caret-color:#59e5bb;
    }
    .st-key-collection_v2 input::placeholder {color:#aebfcb;opacity:1;}
    .st-key-collection_v2 [data-testid="stSelectbox"] [role="combobox"] {
        color:#edf4f9;background:#172936;border-radius:8px;
    }
    .st-key-collection_v2 [data-testid="stSelectbox"] [role="group"],
    .st-key-collection_v2 [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        color:#edf4f9;background:#172936;border-color:#405766;
    }
    .st-key-collection_v2 [data-testid="stSelectbox"] button,
    .st-key-collection_v2 [data-testid="stNumberInput"] button {color:#dbe9ef;background:#1b303a;}
    .st-key-collection_v2 button[kind] {
        background:#1b303a;color:#edf4f9;border:1px solid #45616d;border-radius:10px;
    }
    .st-key-collection_v2 button[kind="primaryFormSubmit"] {
        background:#59e5bb;color:#09251c;border-color:#59e5bb;font-weight:600;
    }
    .st-key-collection_v2 button:disabled {opacity:.55;}
    .st-key-collection_v2 button:focus-visible,
    .st-key-collection_v2 input:focus-visible,.st-key-collection_v2 textarea:focus-visible {
        outline:2px solid #59e5bb;outline-offset:3px;
    }
    .st-key-collection_v2 [data-testid="stExpander"] details {border:1px solid #344b58;border-radius:12px;background:#13232e;}
    .st-key-collection_v2 [data-testid="stExpander"] summary,
    .st-key-collection_v2 [data-testid="stExpander"] details[open] > summary,
    .st-key-collection_v2 [data-testid="stExpander"] summary:hover,
    .st-key-collection_v2 [data-testid="stExpander"] summary:focus-visible {
        color:#edf4f9 !important;background:#1b303a !important;border-radius:10px;
    }
    .st-key-collection_v2 [data-testid="stExpander"] summary p,
    .st-key-collection_v2 [data-testid="stExpander"] summary svg,
    .st-key-collection_v2 [data-testid="stExpander"] summary span {
        color:#edf4f9 !important;background:transparent !important;
    }
    .st-key-collection_v2 [data-testid="stForm"] {
        width:100%;min-width:0;box-sizing:border-box;padding:12px;border-color:#344b58;border-radius:12px;
    }
    .st-key-collection_v2 [class*="st-key-collection_card_"] {
        background:linear-gradient(145deg,#1c2d39,#111d28);border:1px solid #344958;
        border-radius:16px;padding:16px;box-shadow:0 8px 20px #0002;
    }
    .st-key-collection_v2 [data-testid="stImage"] {width:100%;text-align:center;}
    .st-key-collection_v2 [data-testid="stImage"] img {
        width:100%;height:260px;object-fit:contain;border-radius:10px;filter:drop-shadow(0 8px 12px #0005);
    }
    .st-key-collection_v2 .collection-no-image {
        height:260px;border:1px dashed #486170;border-radius:10px;display:grid;place-content:center;
        text-align:center;gap:10px;background:radial-gradient(ellipse at top,#26483f,#142330);color:#adc9c5;
    }
    .st-key-collection_v2 .collection-no-image span {font-size:44px;color:#59cfae;}
    .st-key-collection_v2 .collection-no-image small {font-size:12px;}
    .st-key-collection_v2 .st-key-collection_empty [data-testid="stAlertContainer"] {
        background:#172936;border:1px solid #405766;color:#edf4f9;
    }
    .st-key-collection_v2 .st-key-collection_empty [data-testid="stAlert"] p {
        color:#edf4f9;
    }
    .st-key-collection_v2 [data-testid="stDataFrame"] {border:1px solid #344958;border-radius:12px;overflow:hidden;}
    @media(prefers-reduced-motion:no-preference) {
        .st-key-collection_v2 [data-testid="stImage"] img {transition:transform .18s;}
        .st-key-collection_v2 [data-testid="stImage"] img:hover {transform:translateY(-3px);}
    }
    @media(max-width:700px) {
        .st-key-collection_v2 {padding:14px;border-radius:14px;}
        .st-key-collection_v2 h2 {font-size:1.6rem;}
        .st-key-collection_v2 .st-key-collection_toolbar {padding:12px;}
        .st-key-collection_v2 [data-testid="stMetric"] {padding:12px;}
    }
    </style>''', unsafe_allow_html=True)
    st.header(tr('Minha coleção', 'My collection'))
    st.caption(tr('Seu acervo privado. Organizar cartas não consome créditos.', 'Your private binder. Organizing cards uses no credits.'))
    try:
        # Explicit pagination avoids silently truncating at the Supabase row limit.
        items = []
        while True:
            batch = client.table('collection_items').select('*').eq('user_id', user_id).order('id').range(len(items), len(items) + 499).execute().data or []
            items.extend(batch)
            if len(batch) < 500:
                break
    except Exception:
        st.error(tr('Não foi possível carregar a coleção. Verifique se a migração foi aplicada e tente novamente.', 'Could not load the collection. Check that the migration was applied and try again.'))
        return
    cols = st.columns(3)
    cols[0].metric(tr('Exemplares', 'Copies'), sum(x['quantity'] for x in items))
    cols[1].metric(tr('Cartas diferentes', 'Distinct cards'), len({x['catalog_id'] for x in items if x['quantity'] > 0}))
    cols[2].metric(tr('Lista de desejos', 'Wishlist'), sum(bool(x['wishlist']) for x in items))
    if not items:
        st.info(tr('Busque uma carta no catálogo e use “Adicionar à coleção”.', 'Find a card in the catalog and use “Add to collection”.'))
        return
    with st.container(key='collection_toolbar'):
        search_col, set_col = st.columns([2, 1])
        query = search_col.text_input(tr('Buscar no acervo', 'Search your binder'), placeholder=tr('Nome, coleção ou número…', 'Name, set or number…')).casefold().strip()
        chosen_set = set_col.selectbox(tr('Coleção', 'Set'), [''] + sorted({x['set_name'] for x in items if x['set_name']}), format_func=lambda value: value or tr('Todas as coleções', 'All sets'))
        wishes = st.checkbox(tr('Somente lista de desejos', 'Wishlist only'))
        view_col, export_col = st.columns([1, 2])
        view = view_col.radio(tr('Visualização', 'View'), ['album', 'list'], format_func=lambda value: tr('Álbum', 'Album') if value == 'album' else tr('Lista', 'List'), horizontal=True)
    shown = [x for x in items if (not wishes or x['wishlist']) and (not chosen_set or x['set_name'] == chosen_set) and query in f"{x['card_name']} {x['set_name']} {x['card_number']}".casefold()]
    with export_col.expander(tr('↓ Exportar coleção', '↓ Export collection')):
        st.caption(tr('Exporta todos os registros filtrados. PDF e Word são relatórios textuais nesta etapa.', 'Exports all filtered entries. PDF and Word are text reports at this stage.'))
        include_notes = st.checkbox(tr('Incluir notas privadas no arquivo', 'Include private notes in file'), key='collection_export_notes')
        format_name = st.selectbox(tr('Formato', 'Format'), ['xlsx', 'pdf', 'docx'], format_func=lambda value: {'xlsx':'Excel', 'pdf':'PDF', 'docx':'Word'}[value])
        if st.button(tr('Preparar arquivo', 'Prepare file'), disabled=not shown):
            try:
                data = export_collection(shown, format_name, include_notes)
            except Exception:
                st.error(tr('Não foi possível gerar o arquivo. Tente novamente.', 'Could not generate the file. Please try again.'))
            else:
                st.download_button(tr('Baixar arquivo', 'Download file'), data, file_name='cardcraftai-collection.' + format_name,
                                   mime={'xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','pdf':'application/pdf','docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}[format_name])
    result_col, page_col = st.columns([3, 1])
    result_col.caption(tr(f'{len(shown)} registros encontrados', f'{len(shown)} entries found'))
    if not shown:
        with st.container(key='collection_empty'):
            st.info(tr('Nenhuma carta encontrada. Ajuste os filtros para tentar novamente.', 'No cards found. Try adjusting your filters.'))
        return
    if view == 'list':
        st.dataframe([{tr('Carta', 'Card'): x['card_name'], tr('Coleção', 'Set'): x['set_name'], '#': x['card_number'], tr('Quantidade', 'Quantity'): x['quantity'], tr('Condição', 'Condition'): x['condition']} for x in shown], use_container_width=True, hide_index=True)
        return
    pages = max(1, (len(shown) + 23) // 24)
    page = page_col.selectbox(tr('Página', 'Page'), range(1, pages + 1))
    page_items = shown[(page - 1) * 24:page * 24]
    # Only the image and summary use columns; the editor spans the entire item.
    for item in page_items:
        with st.container(key='collection_card_' + item['id']):
            image_col, summary_col = st.columns([1, 3])
            with image_col:
                image = safe_image(item['image_url'])
                if image:
                    st.image(image, use_container_width=True)
                else:
                    st.markdown('<div class="collection-no-image"><span aria-hidden="true">◇</span><small>' + tr('Imagem indisponível', 'Image unavailable') + '</small></div>', unsafe_allow_html=True)
            with summary_col:
                st.subheader(item['card_name'])
                st.caption(f"{item['set_name']} · #{item['card_number']} · {item['quantity']}×")
            state_key = f"collection_save_{user_id}_{item['id']}"
            result = st.session_state.pop(state_key + '_result', None)
            with st.expander(tr('Editar exemplar', 'Edit entry'), expanded=result is not None):
                # Outside the form so choosing Custom immediately reveals its input.
                variant_options = list(VARIANTS)
                if item['variant'] not in variant_options:
                    variant_options.append(item['variant'])
                variant_options.append(0)  # UI-only sentinel; never stored.
                variant = st.selectbox(
                    tr('Variante', 'Variant'), variant_options,
                    index=variant_options.index(item['variant']),
                    format_func=lambda value: 'Other / Custom' if value == 0 else (value or 'Not specified'),
                    key=f"collection_variant_{user_id}_{item['id']}",
                )
                with st.form('collection_' + item['id']):
                    quantity = st.number_input(tr('Quantidade', 'Quantity'), min_value=0, max_value=9999, value=item['quantity'], step=1)
                    condition = st.selectbox(tr('Condição', 'Condition'), CONDITIONS, index=CONDITIONS.index(item['condition']))
                    language_options = list(CARD_LANGUAGES)
                    if item['language'] not in language_options:
                        language_options.append(item['language'])
                    language = st.selectbox(
                        tr('Idioma da carta', 'Card language'), language_options,
                        index=language_options.index(item['language']),
                        format_func=lambda value: value or 'Not specified',
                    )
                    if variant == 0:
                        variant = st.text_input(
                            tr('Variante personalizada', 'Custom variant'),
                            item['variant'] if item['variant'] not in VARIANTS else '',
                            max_chars=120,
                        )
                    notes = st.text_area(tr('Notas privadas', 'Private notes'), item['notes'], max_chars=2000)
                    wishlist = st.checkbox(tr('Na lista de desejos', 'On wishlist'), value=item['wishlist'])
                    if result == 'success':
                        st.toast(feedback('collection_saved'), icon='✅')
                    elif result == 'error':
                        st.error(feedback('collection_save_error'))
                    saving = st.session_state.get(state_key, False)
                    st.form_submit_button(
                        feedback('collection_saving') if saving else tr('Salvar', 'Save'),
                        key=state_key + '_button', disabled=saving,
                        on_click=begin_save, args=(state_key,),
                    )
                    if saving:
                        try:
                            response = save_edit(client, user_id, item['id'], validate_edit(quantity, condition, language, variant, notes, wishlist))
                            if not response.data:
                                raise ValueError('Update not confirmed')
                        except Exception:
                            st.session_state[state_key + '_result'] = 'error'
                        else:
                            st.session_state[state_key + '_result'] = 'success'
                        finally:
                            st.session_state[state_key] = False
                        st.rerun()
