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
    [data-testid="stMain"] {background:radial-gradient(ellipse at top right, #163c35 0%, #101923 48%, #0b1119 100%);color:#eaf4f1;}
    [data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3 {color:#eaf4f1;}
    [data-testid="stMain"] label,[data-testid="stMain"] [data-testid="stMetricValue"],
    [data-testid="stMain"] [data-testid="stMetricLabel"],
    [data-testid="stMain"] [data-testid="stWidgetLabel"],
    [data-testid="stMain"] [data-testid="stRadio"] p {color:#eaf4f1;}
    [data-testid="stMain"] [data-testid="stTextArea"] textarea {color:#14212b;background:#f0f2f6;caret-color:#14212b;}
    [data-testid="stMain"] [data-testid="stAlert"] p {color:#d8edff;}
    [data-testid="stMain"] button[kind="secondary"], [data-testid="stMain"] button[kind="primary"] {background:#1c4138;color:#eaf4f1;border:1px solid #527c70;}
    [data-testid="stMain"] [data-testid="stCaptionContainer"] {color:#b5c8c2;}
    [data-testid="stMain"] [data-testid="stMetric"] {background:#18282f;border:1px solid #38524e;border-radius:16px;}
    [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {border-radius:16px;}
    [data-testid="stMain"] [data-testid="stImage"] img {border-radius:12px;filter:drop-shadow(0 8px 12px #0005);transition:transform .2s;}
    @media(prefers-reduced-motion:no-preference){[data-testid="stMain"] [data-testid="stImage"] img:hover {transform:translateY(-4px) rotate(-1deg);}}
    </style>''', unsafe_allow_html=True)
    st.header(tr('🃏 Minha coleção', '🃏 My collection'))
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
    query = st.text_input(tr('Buscar no acervo', 'Search your binder')).casefold().strip()
    chosen_set = st.selectbox(tr('Coleção', 'Set'), [''] + sorted({x['set_name'] for x in items if x['set_name']}), format_func=lambda value: value or tr('Todas as coleções', 'All sets'))
    wishes = st.checkbox(tr('Somente lista de desejos', 'Wishlist only'))
    shown = [x for x in items if (not wishes or x['wishlist']) and (not chosen_set or x['set_name'] == chosen_set) and query in f"{x['card_name']} {x['set_name']} {x['card_number']}".casefold()]
    with st.expander(tr('↓ Exportar coleção', '↓ Export collection')):
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
    view = st.radio(tr('Visualização', 'View'), ['album', 'list'], format_func=lambda value: tr('Álbum', 'Album') if value == 'album' else tr('Lista', 'List'), horizontal=True)
    if view == 'list':
        st.dataframe([{tr('Carta', 'Card'): x['card_name'], tr('Coleção', 'Set'): x['set_name'], '#': x['card_number'], tr('Quantidade', 'Quantity'): x['quantity'], tr('Condição', 'Condition'): x['condition']} for x in shown], use_container_width=True, hide_index=True)
        return
    if not shown:
        st.info(tr('Nenhuma carta corresponde aos filtros.', 'No cards match these filters.'))
    pages = max(1, (len(shown) + 23) // 24)
    page = st.selectbox(tr('Página', 'Page'), range(1, pages + 1))
    page_items = shown[(page - 1) * 24:page * 24]
    for offset in range(0, len(page_items), 3):
        for col, item in zip(st.columns(3), page_items[offset:offset + 3]):
            with col, st.container(border=True):
                image = safe_image(item['image_url'])
                if image:
                    st.image(image, width=200)
                else:
                    st.markdown('<div style="height:210px;border:1px solid #38524e;border-radius:14px;display:grid;place-items:center;background:linear-gradient(145deg,#24443e,#15202c);color:#9bdcca;font-size:56px" aria-label="Sem imagem">◇</div>', unsafe_allow_html=True)
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
