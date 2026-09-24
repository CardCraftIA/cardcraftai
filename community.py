import re
from collections import Counter
from datetime import datetime, timezone
from html import escape


AVATAR_OPTIONS = ["🃏", "⚡", "🔥", "💎", "🌟", "🎴", "🧠", "🏆"]
POST_TYPE_ORDER = ["showcase", "question", "discussion", "collection"]


LABELS = {
    "English": {
        "nav": "🌐 Community",
        "title": "CardCraft Community",
        "subtitle": "The collector network inside CardCraftAI — show cards, ask for help, follow people and build reputation around the hobby.",
        "discover": "🔥 Discover",
        "following": "👥 Following",
        "create": "✍️ Create",
        "profile": "👤 Profile",
        "pulse": "Community pulse",
        "members": "Members",
        "posts": "Posts",
        "hypes": "Hypes",
        "trending": "Trending now",
        "guidelines": "Community code",
        "guidelines_text": "Be helpful. No spam, harassment, impersonation or personal data. Use Report when something does not belong here.",
        "filter": "Feed filter",
        "all": "All",
        "showcase": "🏆 Showcase",
        "question": "❓ Help / Identification",
        "discussion": "💬 Discussion",
        "collection": "📚 Collection",
        "empty": "No posts yet. Be the first collector to start the feed.",
        "empty_following": "Follow collectors from Discover and their posts will appear here.",
        "follow": "Follow",
        "following_button": "Following",
        "hype": "⚡ Hype",
        "comments": "Comments",
        "comment_placeholder": "Add something useful to the conversation…",
        "comment": "Comment",
        "delete": "Delete post",
        "delete_comment": "Delete",
        "report": "Report",
        "report_reason": "Reason",
        "report_details": "Details (optional)",
        "report_send": "Send report",
        "reported": "Report sent for review.",
        "publish_title": "Create a community post",
        "publish_intro": "Share a pull, ask the community for help, start a discussion or show collection progress.",
        "post_type": "Post type",
        "post_title": "Title",
        "post_body": "What do you want to share?",
        "attach_card": "Attach a card from My Collection",
        "choose_card": "Choose a card",
        "comments_enabled": "Allow comments",
        "publish": "Publish",
        "published": "Published to CardCraft Community.",
        "profile_title": "Your community identity",
        "profile_intro": "Your public community profile never exposes your account email.",
        "display_name": "Display name",
        "handle": "Handle",
        "bio": "Bio",
        "favorite_tcg": "Favorite TCG",
        "avatar": "Avatar",
        "save_profile": "Save profile",
        "profile_saved": "Community profile updated.",
        "handle_help": "3–24 characters: lowercase letters, numbers and underscores.",
        "handle_invalid": "Use 3–24 lowercase letters, numbers or underscores.",
        "handle_taken": "That handle is already in use.",
        "profile_stats": "Your network",
        "followers": "Followers",
        "following_count": "Following",
        "your_posts": "Your posts",
        "shared_card": "Shared card",
        "condition": "Condition",
        "variant": "Variant",
        "language": "Language",
        "set": "Set",
        "number": "Number",
        "no_collection": "Your collection is empty. You can still publish a text post.",
        "load_error": "Community could not be loaded right now.",
        "action_error": "That action could not be completed right now.",
        "own_post": "Your post",
        "reason_spam": "Spam",
        "reason_harassment": "Harassment",
        "reason_unsafe": "Unsafe content",
        "reason_misleading": "Misleading information",
        "reason_other": "Other",
        "just_now": "now",
        "minutes": "{n}m",
        "hours": "{n}h",
        "days": "{n}d",
    },
    "Português (BR)": {
        "nav": "🌐 Comunidade",
        "title": "CardCraft Community",
        "subtitle": "A rede dos colecionadores dentro do CardCraftAI — mostre cartas, peça ajuda, siga pessoas e construa sua presença no hobby.",
        "discover": "🔥 Descobrir",
        "following": "👥 Seguindo",
        "create": "✍️ Publicar",
        "profile": "👤 Perfil",
        "pulse": "Pulso da comunidade",
        "members": "Membros",
        "posts": "Publicações",
        "hypes": "Hypes",
        "trending": "Em alta agora",
        "guidelines": "Código da comunidade",
        "guidelines_text": "Ajude de verdade. Sem spam, assédio, falsidade de identidade ou dados pessoais. Use Denunciar quando algo não pertencer aqui.",
        "filter": "Filtrar feed",
        "all": "Tudo",
        "showcase": "🏆 Showcase",
        "question": "❓ Ajuda / Identificação",
        "discussion": "💬 Discussão",
        "collection": "📚 Coleção",
        "empty": "Ainda não há publicações. Seja o primeiro colecionador a iniciar o feed.",
        "empty_following": "Siga colecionadores em Descobrir e as publicações deles aparecerão aqui.",
        "follow": "Seguir",
        "following_button": "Seguindo",
        "hype": "⚡ Hype",
        "comments": "Comentários",
        "comment_placeholder": "Acrescente algo útil à conversa…",
        "comment": "Comentar",
        "delete": "Excluir publicação",
        "delete_comment": "Excluir",
        "report": "Denunciar",
        "report_reason": "Motivo",
        "report_details": "Detalhes (opcional)",
        "report_send": "Enviar denúncia",
        "reported": "Denúncia enviada para análise.",
        "publish_title": "Criar publicação",
        "publish_intro": "Mostre uma conquista, peça ajuda para identificar uma carta, abra uma discussão ou compartilhe o progresso da sua coleção.",
        "post_type": "Tipo de publicação",
        "post_title": "Título",
        "post_body": "O que você quer compartilhar?",
        "attach_card": "Anexar uma carta da Minha Coleção",
        "choose_card": "Escolha uma carta",
        "comments_enabled": "Permitir comentários",
        "publish": "Publicar",
        "published": "Publicado na CardCraft Community.",
        "profile_title": "Sua identidade na comunidade",
        "profile_intro": "Seu perfil público da comunidade nunca expõe o e-mail da sua conta.",
        "display_name": "Nome de exibição",
        "handle": "Usuário",
        "bio": "Bio",
        "favorite_tcg": "TCG favorito",
        "avatar": "Avatar",
        "save_profile": "Salvar perfil",
        "profile_saved": "Perfil da comunidade atualizado.",
        "handle_help": "3–24 caracteres: letras minúsculas, números e underscore.",
        "handle_invalid": "Use de 3 a 24 letras minúsculas, números ou underscore.",
        "handle_taken": "Esse nome de usuário já está em uso.",
        "profile_stats": "Sua rede",
        "followers": "Seguidores",
        "following_count": "Seguindo",
        "your_posts": "Suas publicações",
        "shared_card": "Carta compartilhada",
        "condition": "Condição",
        "variant": "Variante",
        "language": "Idioma",
        "set": "Coleção",
        "number": "Número",
        "no_collection": "Sua coleção está vazia. Você ainda pode publicar somente texto.",
        "load_error": "Não foi possível carregar a comunidade agora.",
        "action_error": "Não foi possível concluir essa ação agora.",
        "own_post": "Sua publicação",
        "reason_spam": "Spam",
        "reason_harassment": "Assédio",
        "reason_unsafe": "Conteúdo inseguro",
        "reason_misleading": "Informação enganosa",
        "reason_other": "Outro",
        "just_now": "agora",
        "minutes": "{n}min",
        "hours": "{n}h",
        "days": "{n}d",
    },
    "Español": {
        "nav": "🌐 Comunidad",
        "title": "CardCraft Community",
        "subtitle": "La red de coleccionistas dentro de CardCraftAI: muestra cartas, pide ayuda, sigue personas y construye tu presencia en el hobby.",
        "discover": "🔥 Descubrir",
        "following": "👥 Siguiendo",
        "create": "✍️ Publicar",
        "profile": "👤 Perfil",
        "pulse": "Pulso de la comunidad",
        "members": "Miembros",
        "posts": "Publicaciones",
        "hypes": "Hypes",
        "trending": "Tendencias",
        "guidelines": "Código de la comunidad",
        "guidelines_text": "Ayuda de verdad. Sin spam, acoso, suplantación ni datos personales. Usa Reportar cuando algo no corresponda.",
        "filter": "Filtrar feed",
        "all": "Todo",
        "showcase": "🏆 Showcase",
        "question": "❓ Ayuda / Identificación",
        "discussion": "💬 Discusión",
        "collection": "📚 Colección",
        "empty": "Todavía no hay publicaciones. Sé la primera persona en iniciar el feed.",
        "empty_following": "Sigue coleccionistas en Descubrir y sus publicaciones aparecerán aquí.",
        "follow": "Seguir",
        "following_button": "Siguiendo",
        "hype": "⚡ Hype",
        "comments": "Comentarios",
        "comment_placeholder": "Añade algo útil a la conversación…",
        "comment": "Comentar",
        "delete": "Eliminar publicación",
        "delete_comment": "Eliminar",
        "report": "Reportar",
        "report_reason": "Motivo",
        "report_details": "Detalles (opcional)",
        "report_send": "Enviar reporte",
        "reported": "Reporte enviado para revisión.",
        "publish_title": "Crear publicación",
        "publish_intro": "Muestra una carta, pide ayuda, inicia una conversación o comparte el progreso de tu colección.",
        "post_type": "Tipo de publicación",
        "post_title": "Título",
        "post_body": "¿Qué quieres compartir?",
        "attach_card": "Adjuntar una carta de Mi Colección",
        "choose_card": "Elige una carta",
        "comments_enabled": "Permitir comentarios",
        "publish": "Publicar",
        "published": "Publicado en CardCraft Community.",
        "profile_title": "Tu identidad en la comunidad",
        "profile_intro": "Tu perfil público nunca muestra el correo de tu cuenta.",
        "display_name": "Nombre visible",
        "handle": "Usuario",
        "bio": "Bio",
        "favorite_tcg": "TCG favorito",
        "avatar": "Avatar",
        "save_profile": "Guardar perfil",
        "profile_saved": "Perfil actualizado.",
        "handle_help": "3–24 caracteres: minúsculas, números y guion bajo.",
        "handle_invalid": "Usa de 3 a 24 letras minúsculas, números o guion bajo.",
        "handle_taken": "Ese usuario ya está en uso.",
        "profile_stats": "Tu red",
        "followers": "Seguidores",
        "following_count": "Siguiendo",
        "your_posts": "Tus publicaciones",
        "shared_card": "Carta compartida",
        "condition": "Estado",
        "variant": "Variante",
        "language": "Idioma",
        "set": "Colección",
        "number": "Número",
        "no_collection": "Tu colección está vacía. Aun así puedes publicar texto.",
        "load_error": "No se pudo cargar la comunidad.",
        "action_error": "No se pudo completar esa acción.",
        "own_post": "Tu publicación",
        "reason_spam": "Spam",
        "reason_harassment": "Acoso",
        "reason_unsafe": "Contenido inseguro",
        "reason_misleading": "Información engañosa",
        "reason_other": "Otro",
        "just_now": "ahora",
        "minutes": "{n}min",
        "hours": "{n}h",
        "days": "{n}d",
    },
    "日本語": {
        "nav": "🌐 コミュニティ",
        "title": "CardCraft Community",
        "subtitle": "CardCraftAI内のコレクターネットワーク。カードを共有し、質問し、仲間をフォローできます。",
        "discover": "🔥 発見",
        "following": "👥 フォロー中",
        "create": "✍️ 投稿",
        "profile": "👤 プロフィール",
        "pulse": "コミュニティ",
        "members": "メンバー",
        "posts": "投稿",
        "hypes": "Hype",
        "trending": "トレンド",
        "guidelines": "コミュニティルール",
        "guidelines_text": "互いに助け合い、スパム・嫌がらせ・なりすまし・個人情報の投稿は避けてください。",
        "filter": "フィード絞り込み",
        "all": "すべて",
        "showcase": "🏆 ショーケース",
        "question": "❓ 質問 / 識別",
        "discussion": "💬 ディスカッション",
        "collection": "📚 コレクション",
        "empty": "まだ投稿がありません。最初の投稿を作成しましょう。",
        "empty_following": "発見タブでコレクターをフォローすると、ここに投稿が表示されます。",
        "follow": "フォロー",
        "following_button": "フォロー中",
        "hype": "⚡ Hype",
        "comments": "コメント",
        "comment_placeholder": "会話に役立つコメントを追加…",
        "comment": "コメント",
        "delete": "投稿を削除",
        "delete_comment": "削除",
        "report": "報告",
        "report_reason": "理由",
        "report_details": "詳細（任意）",
        "report_send": "報告を送信",
        "reported": "報告を送信しました。",
        "publish_title": "投稿を作成",
        "publish_intro": "カードを見せたり、識別を相談したり、コレクションの進捗を共有できます。",
        "post_type": "投稿タイプ",
        "post_title": "タイトル",
        "post_body": "共有したい内容",
        "attach_card": "マイコレクションのカードを添付",
        "choose_card": "カードを選択",
        "comments_enabled": "コメントを許可",
        "publish": "投稿",
        "published": "CardCraft Community に投稿しました。",
        "profile_title": "コミュニティプロフィール",
        "profile_intro": "公開プロフィールにアカウントのメールアドレスは表示されません。",
        "display_name": "表示名",
        "handle": "ユーザー名",
        "bio": "自己紹介",
        "favorite_tcg": "好きなTCG",
        "avatar": "アバター",
        "save_profile": "プロフィールを保存",
        "profile_saved": "プロフィールを更新しました。",
        "handle_help": "3〜24文字：小文字英数字とアンダースコア。",
        "handle_invalid": "3〜24文字の小文字英数字またはアンダースコアを使用してください。",
        "handle_taken": "そのユーザー名は使用されています。",
        "profile_stats": "あなたのネットワーク",
        "followers": "フォロワー",
        "following_count": "フォロー中",
        "your_posts": "あなたの投稿",
        "shared_card": "共有カード",
        "condition": "状態",
        "variant": "バリアント",
        "language": "言語",
        "set": "セット",
        "number": "番号",
        "no_collection": "コレクションは空ですが、テキスト投稿は作成できます。",
        "load_error": "コミュニティを読み込めませんでした。",
        "action_error": "操作を完了できませんでした。",
        "own_post": "あなたの投稿",
        "reason_spam": "スパム",
        "reason_harassment": "嫌がらせ",
        "reason_unsafe": "危険なコンテンツ",
        "reason_misleading": "誤解を招く情報",
        "reason_other": "その他",
        "just_now": "今",
        "minutes": "{n}分",
        "hours": "{n}時間",
        "days": "{n}日",
    },
}


def community_nav_label(language):
    return LABELS.get(language, LABELS["English"])["nav"]


def _normalize_handle(value):
    value = str(value or "").strip().lower().replace(" ", "_")
    value = re.sub(r"[^a-z0-9_]", "", value)
    return value[:24]


def _valid_handle(value):
    return bool(re.fullmatch(r"[a-z0-9_]{3,24}", str(value or "")))


def _labels(language):
    return LABELS.get(language, LABELS["English"])


def _relative_time(value, labels):
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        seconds = max(0, int((now - dt.astimezone(timezone.utc)).total_seconds()))
    except Exception:
        return ""
    if seconds < 60:
        return labels["just_now"]
    if seconds < 3600:
        return labels["minutes"].format(n=seconds // 60)
    if seconds < 86400:
        return labels["hours"].format(n=seconds // 3600)
    return labels["days"].format(n=seconds // 86400)


def _ensure_profile(supabase, user_id):
    response = (
        supabase.table("community_profiles")
        .select("user_id,handle,display_name,bio,avatar_emoji,favorite_tcg,created_at")
        .eq("user_id", str(user_id))
        .limit(1)
        .execute()
    )
    rows = response.data or []
    if rows:
        return rows[0]

    suffix = str(user_id).replace("-", "")[:10]
    profile = {
        "user_id": str(user_id),
        "handle": f"collector_{suffix}",
        "display_name": "CardCrafter",
        "bio": "",
        "avatar_emoji": "🃏",
        "favorite_tcg": "Pokémon",
    }
    try:
        inserted = (
            supabase.table("community_profiles")
            .insert(profile)
            .execute()
        )
        if inserted.data:
            return inserted.data[0]
    except Exception:
        profile["handle"] = f"crafter_{str(user_id).replace('-', '')[:12]}"
        inserted = supabase.table("community_profiles").insert(profile).execute()
        if inserted.data:
            return inserted.data[0]
    return profile


def _card_snapshot(item):
    if not item:
        return {}
    return {
        "catalog_id": str(item.get("catalog_id") or "")[:200],
        "card_name": str(item.get("card_name") or "")[:200],
        "set_name": str(item.get("set_name") or "")[:200],
        "card_number": str(item.get("card_number") or "")[:80],
        "image_url": str(item.get("image_url") or "")[:1000],
        "condition": str(item.get("condition") or "")[:80],
        "language": str(item.get("language") or "")[:80],
        "variant": str(item.get("variant") or "")[:120],
    }


def _safe_https_url(value):
    value = str(value or "").strip()
    if value.startswith("https://") and len(value) <= 1200:
        return value
    return ""


def _load_community(supabase, user_id):
    posts = (
        supabase.table("community_posts")
        .select("id,user_id,post_type,title,body,card_snapshot,comments_enabled,status,created_at,updated_at")
        .eq("status", "active")
        .order("created_at", desc=True)
        .limit(60)
        .execute()
    ).data or []

    profiles = (
        supabase.table("community_profiles")
        .select("user_id,handle,display_name,bio,avatar_emoji,favorite_tcg")
        .execute()
    ).data or []
    profile_map = {str(row.get("user_id")): row for row in profiles}

    post_ids = [str(row["id"]) for row in posts if row.get("id")]
    if post_ids:
        reactions = (
            supabase.table("community_reactions")
            .select("post_id,user_id,reaction")
            .in_("post_id", post_ids)
            .execute()
        ).data or []
        comments = (
            supabase.table("community_comments")
            .select("id,post_id,user_id,body,status,created_at")
            .in_("post_id", post_ids)
            .eq("status", "active")
            .order("created_at")
            .limit(400)
            .execute()
        ).data or []
    else:
        reactions = []
        comments = []

    follows = (
        supabase.table("community_follows")
        .select("follower_id,following_id")
        .execute()
    ).data or []

    reaction_map = {}
    for row in reactions:
        reaction_map.setdefault(str(row.get("post_id")), set()).add(str(row.get("user_id")))

    comment_map = {}
    for row in comments:
        comment_map.setdefault(str(row.get("post_id")), []).append(row)

    following_ids = {
        str(row.get("following_id"))
        for row in follows
        if str(row.get("follower_id")) == str(user_id)
    }

    return posts, profile_map, reaction_map, comment_map, follows, following_ids


def _toggle_follow(st, supabase, user_id, target_id, following_ids, labels):
    try:
        if str(target_id) in following_ids:
            (
                supabase.table("community_follows")
                .delete()
                .eq("follower_id", str(user_id))
                .eq("following_id", str(target_id))
                .execute()
            )
        else:
            supabase.table("community_follows").insert({
                "follower_id": str(user_id),
                "following_id": str(target_id),
            }).execute()
        st.rerun()
    except Exception:
        st.error(labels["action_error"])


def _toggle_hype(st, supabase, user_id, post_id, current_users, labels):
    try:
        if str(user_id) in current_users:
            (
                supabase.table("community_reactions")
                .delete()
                .eq("post_id", str(post_id))
                .eq("user_id", str(user_id))
                .execute()
            )
        else:
            supabase.table("community_reactions").insert({
                "post_id": str(post_id),
                "user_id": str(user_id),
                "reaction": "hype",
            }).execute()
        st.rerun()
    except Exception:
        st.error(labels["action_error"])


def _render_shared_card(st, snapshot, labels):
    if not isinstance(snapshot, dict) or not snapshot.get("card_name"):
        return

    st.caption(labels["shared_card"])
    left, right = st.columns([0.34, 0.66], gap="medium")
    image_url = _safe_https_url(snapshot.get("image_url"))
    with left:
        if image_url:
            st.image(image_url, use_container_width=True)
        else:
            st.markdown(
                '<div class="cc-community-card-placeholder">🃏</div>',
                unsafe_allow_html=True,
            )
    with right:
        st.markdown(f"### {escape(str(snapshot.get('card_name') or ''))}")
        facts = []
        if snapshot.get("set_name"):
            facts.append(f"**{labels['set']}:** {snapshot['set_name']}")
        if snapshot.get("card_number"):
            facts.append(f"**{labels['number']}:** {snapshot['card_number']}")
        if snapshot.get("condition"):
            facts.append(f"**{labels['condition']}:** {snapshot['condition']}")
        if snapshot.get("language"):
            facts.append(f"**{labels['language']}:** {snapshot['language']}")
        if snapshot.get("variant"):
            facts.append(f"**{labels['variant']}:** {snapshot['variant']}")
        for fact in facts:
            st.markdown(fact)


def _report_post(st, supabase, user_id, post_id, labels):
    reason_labels = {
        "spam": labels["reason_spam"],
        "harassment": labels["reason_harassment"],
        "unsafe": labels["reason_unsafe"],
        "misleading": labels["reason_misleading"],
        "other": labels["reason_other"],
    }
    with st.popover("⋯"):
        st.caption(labels["report"])
        reason = st.selectbox(
            labels["report_reason"],
            list(reason_labels),
            format_func=lambda key: reason_labels[key],
            key=f"community_report_reason_{post_id}",
        )
        details = st.text_area(
            labels["report_details"],
            max_chars=500,
            key=f"community_report_details_{post_id}",
        )
        if st.button(labels["report_send"], key=f"community_report_send_{post_id}"):
            try:
                supabase.table("community_reports").insert({
                    "reporter_id": str(user_id),
                    "post_id": str(post_id),
                    "reason": reason,
                    "details": details.strip(),
                }).execute()
                st.success(labels["reported"])
            except Exception:
                st.error(labels["action_error"])


def _render_post(
    st,
    supabase,
    user_id,
    post,
    profile_map,
    reaction_map,
    comment_map,
    following_ids,
    labels,
):
    post_id = str(post.get("id"))
    author_id = str(post.get("user_id"))
    author = profile_map.get(author_id, {})
    is_owner = author_id == str(user_id)
    reaction_users = reaction_map.get(post_id, set())
    comments = comment_map.get(post_id, [])
    type_label = labels.get(str(post.get("post_type")), labels["discussion"])

    with st.container(border=True):
        head_left, head_mid, head_action = st.columns([0.10, 0.68, 0.22], vertical_alignment="center")
        with head_left:
            st.markdown(
                f'<div class="cc-community-avatar">{escape(str(author.get("avatar_emoji") or "🃏"))}</div>',
                unsafe_allow_html=True,
            )
        with head_mid:
            display = str(author.get("display_name") or "CardCrafter")
            handle = str(author.get("handle") or "collector")
            tcg = str(author.get("favorite_tcg") or "TCG")
            when = _relative_time(post.get("created_at"), labels)
            st.markdown(f"**{display}** · @{handle}")
            st.caption(f"{tcg} · {when} · {type_label}")
        with head_action:
            if is_owner:
                st.caption(labels["own_post"])
            else:
                if st.button(
                    labels["following_button"] if author_id in following_ids else labels["follow"],
                    key=f"community_follow_{post_id}",
                    use_container_width=True,
                ):
                    _toggle_follow(st, supabase, user_id, author_id, following_ids, labels)

        st.markdown(f"### {post.get('title') or ''}")
        st.markdown(str(post.get("body") or ""))

        snapshot = post.get("card_snapshot") or {}
        if snapshot:
            _render_shared_card(st, snapshot, labels)

        action1, action2, action3 = st.columns([0.27, 0.45, 0.28], vertical_alignment="center")
        with action1:
            liked = str(user_id) in reaction_users
            if st.button(
                f"{labels['hype']} · {len(reaction_users)}",
                key=f"community_hype_{post_id}",
                type="primary" if liked else "secondary",
                use_container_width=True,
            ):
                _toggle_hype(st, supabase, user_id, post_id, reaction_users, labels)
        with action2:
            st.caption(f"💬 {len(comments)} {labels['comments']}")
        with action3:
            if is_owner:
                if st.button(labels["delete"], key=f"community_delete_{post_id}", use_container_width=True):
                    try:
                        supabase.table("community_posts").delete().eq("id", post_id).eq("user_id", str(user_id)).execute()
                        st.rerun()
                    except Exception:
                        st.error(labels["action_error"])
            else:
                _report_post(st, supabase, user_id, post_id, labels)

        if post.get("comments_enabled", True):
            with st.expander(f"💬 {labels['comments']} ({len(comments)})"):
                for comment_row in comments:
                    comment_author_id = str(comment_row.get("user_id"))
                    comment_author = profile_map.get(comment_author_id, {})
                    c_display = str(comment_author.get("display_name") or "CardCrafter")
                    c_handle = str(comment_author.get("handle") or "collector")
                    c_avatar = str(comment_author.get("avatar_emoji") or "🃏")
                    c_when = _relative_time(comment_row.get("created_at"), labels)
                    st.markdown(f"{c_avatar} **{c_display}** · @{c_handle} · {c_when}")
                    st.write(str(comment_row.get("body") or ""))
                    if comment_author_id == str(user_id):
                        if st.button(
                            labels["delete_comment"],
                            key=f"community_delete_comment_{comment_row.get('id')}",
                        ):
                            try:
                                (
                                    supabase.table("community_comments")
                                    .delete()
                                    .eq("id", str(comment_row.get("id")))
                                    .eq("user_id", str(user_id))
                                    .execute()
                                )
                                st.rerun()
                            except Exception:
                                st.error(labels["action_error"])
                    st.divider()

                new_comment = st.text_input(
                    labels["comment_placeholder"],
                    max_chars=1000,
                    key=f"community_comment_{post_id}",
                )
                if st.button(labels["comment"], key=f"community_comment_send_{post_id}"):
                    body = new_comment.strip()
                    if body:
                        try:
                            supabase.table("community_comments").insert({
                                "post_id": post_id,
                                "user_id": str(user_id),
                                "body": body,
                            }).execute()
                            st.rerun()
                        except Exception:
                            st.error(labels["action_error"])


def _render_feed(
    st,
    supabase,
    user_id,
    posts,
    profile_map,
    reaction_map,
    comment_map,
    following_ids,
    labels,
    only_following=False,
):
    options = ["all"] + POST_TYPE_ORDER
    selected = st.selectbox(
        labels["filter"],
        options,
        format_func=lambda key: labels[key],
        key="community_feed_filter_following" if only_following else "community_feed_filter",
    )
    filtered = []
    for post in posts:
        if only_following and str(post.get("user_id")) not in following_ids:
            continue
        if selected != "all" and post.get("post_type") != selected:
            continue
        filtered.append(post)

    if not filtered:
        st.info(labels["empty_following"] if only_following else labels["empty"])
        return

    for post in filtered:
        _render_post(
            st,
            supabase,
            user_id,
            post,
            profile_map,
            reaction_map,
            comment_map,
            following_ids,
            labels,
        )


def _render_composer(st, supabase, user_id, labels):
    st.subheader(labels["publish_title"])
    st.caption(labels["publish_intro"])

    if st.session_state.pop("community_clear_composer", False):
        st.session_state["community_post_title"] = ""
        st.session_state["community_post_body"] = ""
        st.session_state["community_attach_card"] = False

    type_key = st.selectbox(
        labels["post_type"],
        POST_TYPE_ORDER,
        format_func=lambda key: labels[key],
        key="community_post_type",
    )
    title = st.text_input(labels["post_title"], max_chars=140, key="community_post_title")
    body = st.text_area(labels["post_body"], max_chars=2200, height=150, key="community_post_body")

    try:
        collection = (
            supabase.table("collection_items")
            .select("id,catalog_id,card_name,set_name,card_number,image_url,quantity,condition,language,variant")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        ).data or []
    except Exception:
        collection = []

    attach = st.checkbox(labels["attach_card"], key="community_attach_card")
    chosen = None
    if attach:
        if collection:
            by_id = {str(row["id"]): row for row in collection}
            chosen_id = st.selectbox(
                labels["choose_card"],
                list(by_id),
                format_func=lambda item_id: (
                    f"{by_id[item_id].get('card_name') or 'Card'}"
                    + (f" · {by_id[item_id].get('set_name')}" if by_id[item_id].get("set_name") else "")
                    + (f" #{by_id[item_id].get('card_number')}" if by_id[item_id].get("card_number") else "")
                ),
                key="community_collection_card",
            )
            chosen = by_id.get(chosen_id)
            _render_shared_card(st, _card_snapshot(chosen), labels)
        else:
            st.info(labels["no_collection"])

    allow_comments = st.checkbox(labels["comments_enabled"], value=True, key="community_comments_enabled")

    if st.button(labels["publish"], type="primary", use_container_width=True, key="community_publish"):
        title_clean = title.strip()
        body_clean = body.strip()
        if not title_clean or not body_clean:
            st.warning(f"{labels['post_title']} / {labels['post_body']}")
            return
        try:
            supabase.table("community_posts").insert({
                "user_id": str(user_id),
                "post_type": type_key,
                "title": title_clean,
                "body": body_clean,
                "collection_item_id": str(chosen.get("id")) if chosen else None,
                "card_snapshot": _card_snapshot(chosen),
                "comments_enabled": bool(allow_comments),
            }).execute()
            st.success(labels["published"])
            st.session_state["community_clear_composer"] = True
            st.rerun()
        except Exception:
            st.error(labels["action_error"])


def _render_profile(st, supabase, user_id, profile, follows, posts, labels):
    st.subheader(labels["profile_title"])
    st.caption(labels["profile_intro"])

    left, right = st.columns([0.28, 0.72], gap="large")
    with left:
        avatar = st.selectbox(
            labels["avatar"],
            AVATAR_OPTIONS,
            index=AVATAR_OPTIONS.index(profile.get("avatar_emoji")) if profile.get("avatar_emoji") in AVATAR_OPTIONS else 0,
            key="community_profile_avatar",
        )
        st.markdown(
            f'<div class="cc-community-avatar cc-community-avatar-xl">{escape(avatar)}</div>',
            unsafe_allow_html=True,
        )
    with right:
        display_name = st.text_input(
            labels["display_name"],
            value=str(profile.get("display_name") or ""),
            max_chars=40,
            key="community_profile_display",
        )
        handle = st.text_input(
            labels["handle"],
            value=str(profile.get("handle") or ""),
            max_chars=24,
            help=labels["handle_help"],
            key="community_profile_handle",
        )
        bio = st.text_area(
            labels["bio"],
            value=str(profile.get("bio") or ""),
            max_chars=240,
            height=100,
            key="community_profile_bio",
        )
        favorite_tcg = st.text_input(
            labels["favorite_tcg"],
            value=str(profile.get("favorite_tcg") or "Pokémon"),
            max_chars=60,
            key="community_profile_tcg",
        )

    if st.button(labels["save_profile"], type="primary", use_container_width=True, key="community_profile_save"):
        normalized = _normalize_handle(handle)
        if not _valid_handle(normalized):
            st.warning(labels["handle_invalid"])
        elif not display_name.strip() or not favorite_tcg.strip():
            st.warning(labels["action_error"])
        else:
            try:
                (
                    supabase.table("community_profiles")
                    .update({
                        "display_name": display_name.strip(),
                        "handle": normalized,
                        "bio": bio.strip(),
                        "favorite_tcg": favorite_tcg.strip(),
                        "avatar_emoji": avatar,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    })
                    .eq("user_id", str(user_id))
                    .execute()
                )
                st.success(labels["profile_saved"])
                st.rerun()
            except Exception as error:
                if "duplicate" in str(error).lower() or "unique" in str(error).lower():
                    st.warning(labels["handle_taken"])
                else:
                    st.error(labels["action_error"])

    followers = sum(1 for row in follows if str(row.get("following_id")) == str(user_id))
    following = sum(1 for row in follows if str(row.get("follower_id")) == str(user_id))
    own_posts = sum(1 for row in posts if str(row.get("user_id")) == str(user_id))
    st.markdown(f"#### {labels['profile_stats']}")
    m1, m2, m3 = st.columns(3)
    m1.metric(labels["followers"], followers)
    m2.metric(labels["following_count"], following)
    m3.metric(labels["your_posts"], own_posts)


def _install_style(st):
    st.markdown(
        """
        <style>
        .cc-community-hero {
            position: relative;
            overflow: hidden;
            padding: 1.5rem 1.6rem;
            border-radius: 22px;
            border: 1px solid rgba(56,189,248,.20);
            background:
                radial-gradient(circle at 95% 10%, rgba(56,189,248,.18), transparent 24rem),
                linear-gradient(135deg, rgba(124,92,252,.17), rgba(17,28,46,.92) 55%, rgba(8,15,28,.92));
            margin-bottom: 1rem;
        }
        .cc-community-hero .eyebrow {
            color:#9f8cff;
            font-weight:800;
            letter-spacing:.16em;
            text-transform:uppercase;
            font-size:.72rem;
            margin-bottom:.45rem;
        }
        .cc-community-hero h2 {
            margin:0;
            color:#f8fafc;
            font-size:clamp(1.8rem,3.5vw,2.65rem);
            letter-spacing:-.045em;
        }
        .cc-community-hero p {
            color:#a9b8cb;
            max-width:850px;
            line-height:1.6;
            margin:.65rem 0 0;
        }
        .cc-community-avatar {
            width:44px;
            height:44px;
            display:grid;
            place-items:center;
            border-radius:14px;
            font-size:1.35rem;
            background:linear-gradient(145deg,rgba(124,92,252,.34),rgba(37,99,235,.22));
            border:1px solid rgba(139,108,255,.28);
            box-shadow:0 10px 24px rgba(0,0,0,.14);
        }
        .cc-community-avatar-xl {
            width:96px;
            height:96px;
            border-radius:28px;
            font-size:2.7rem;
            margin:0 auto 1rem;
        }
        .cc-community-card-placeholder {
            min-height:180px;
            display:grid;
            place-items:center;
            border-radius:16px;
            font-size:3rem;
            background:rgba(124,92,252,.08);
            border:1px dashed rgba(139,108,255,.35);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_community(st, supabase, user_id, language="English"):
    labels = _labels(language)
    _install_style(st)

    st.markdown(
        f"""
        <section class="cc-community-hero">
            <div class="eyebrow">SOCIAL TCG NETWORK</div>
            <h2>{escape(labels["title"])}</h2>
            <p>{escape(labels["subtitle"])}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    try:
        profile = _ensure_profile(supabase, user_id)
        posts, profile_map, reaction_map, comment_map, follows, following_ids = _load_community(supabase, user_id)
        profile_map[str(user_id)] = profile
    except Exception:
        st.error(labels["load_error"])
        return

    main, rail = st.columns([0.74, 0.26], gap="large")
    with main:
        discover_tab, following_tab, create_tab, profile_tab = st.tabs([
            labels["discover"],
            labels["following"],
            labels["create"],
            labels["profile"],
        ])
        with discover_tab:
            _render_feed(
                st, supabase, user_id, posts, profile_map, reaction_map,
                comment_map, following_ids, labels, only_following=False
            )
        with following_tab:
            _render_feed(
                st, supabase, user_id, posts, profile_map, reaction_map,
                comment_map, following_ids, labels, only_following=True
            )
        with create_tab:
            _render_composer(st, supabase, user_id, labels)
        with profile_tab:
            _render_profile(st, supabase, user_id, profile, follows, posts, labels)

    with rail:
        st.markdown(f"#### {labels['pulse']}")
        total_hypes = sum(len(users) for users in reaction_map.values())
        c1, c2 = st.columns(2)
        c1.metric(labels["members"], len(profile_map))
        c2.metric(labels["posts"], len(posts))
        st.metric(labels["hypes"], total_hypes)

        st.markdown(f"#### {labels['trending']}")
        type_counts = Counter(str(row.get("post_type")) for row in posts)
        for key, count in type_counts.most_common():
            if key in labels:
                st.caption(f"{labels[key]} · {count}")

        st.markdown(f"#### {labels['guidelines']}")
        st.info(labels["guidelines_text"])
