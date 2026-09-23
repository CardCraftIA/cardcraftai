"""Release-safety messages and collection labels for the existing t() tables."""
LANGUAGES = ('English', 'Português (BR)', 'Español', '日本語')
MESSAGES = {
    'collection_save_conflict': ('Update could not be confirmed. Your entries were kept. Reopen the editor to review the current version before saving.', 'Não foi possível confirmar a atualização. Seus dados foram mantidos. Reabra o editor para revisar a versão atual antes de salvar.', 'No se pudo confirmar la actualización. Tus cambios se conservaron. Vuelve a abrir el editor para revisar la versión actual antes de guardar.', '更新を確認できませんでした。入力内容は保持されています。編集画面を開き直し、現在の内容を確認してから保存してください。'),
    'auth_expired': ('Your session expired. Please sign in again.', 'Sua sessão expirou. Entre novamente.', 'Tu sesión ha caducado. Inicia sesión de nuevo.', 'セッションの有効期限が切れました。再度ログインしてください。'),
    'auth_error': ('Authentication could not be verified. Please try signing in again.', 'Não foi possível verificar a autenticação. Tente entrar novamente.', 'No se pudo verificar la autenticación. Intenta iniciar sesión de nuevo.', '認証を確認できませんでした。再度ログインしてください。'),
    'auth_email_unconfirmed': ('Confirm your email before signing in.', 'Confirme seu e-mail antes de entrar.', 'Confirma tu correo antes de iniciar sesión.', 'ログインする前にメールアドレスを確認してください。'),
    'analysis_busy': ('An analysis is already in progress. Please wait.', 'Uma análise já está em andamento. Aguarde.', 'Ya hay un análisis en curso. Espera.', '分析を実行中です。お待ちください。'),
    'legal_check_failed': ('Could not verify your legal acceptance. Access remains blocked; please try again.', 'Não foi possível verificar seu aceite legal. O acesso permanece bloqueado; tente novamente.', 'No se pudo verificar tu aceptación legal. El acceso permanece bloqueado; inténtalo de nuevo.', '規約への同意を確認できません。アクセスは制限されています。再度お試しください。'),
    'legal_save_failed': ('Could not save your acceptance. Please try again.', 'Não foi possível registrar seu aceite. Tente novamente.', 'No se pudo guardar tu aceptación. Inténtalo de nuevo.', '同意を保存できませんでした。再度お試しください。'),
    'profile_unavailable': ('Your account profile is temporarily unavailable. Please sign in again or contact support.', 'O perfil da sua conta está indisponível. Entre novamente ou contate o suporte.', 'El perfil de tu cuenta no está disponible. Inicia sesión de nuevo o contacta con soporte.', 'アカウント情報を取得できません。再度ログインするかサポートにお問い合わせください。'),
}

# English keys are presentation-only; saved condition/language/variant values are unchanged.
COLLECTION = {
    'My collection': ('Mi colección', 'マイコレクション'),
    'Your private binder. Organizing cards uses no credits.': ('Tu colección privada. Organizar cartas no consume créditos.', '自分だけのコレクションです。整理にはクレジットを消費しません。'),
    'Copies': ('Ejemplares', '枚数'), 'Distinct cards': ('Cartas distintas', 'カード種類'),
    'Wishlist': ('Lista de deseos', 'ウィッシュリスト'), 'Sets': ('Expansiones', 'セット'),
    'Duplicates': ('Copias adicionales', '重複枚数'), 'Page': ('Página', 'ページ'),
    'Search my collection': ('Buscar en mi colección', 'コレクションを検索'),
    'Name, set, number, condition, language or variant…': ('Nombre, expansión, número, estado, idioma o variante…', '名前、セット、番号、状態、言語、バリエーション…'),
    'Set': ('Expansión', 'セット'), 'All sets': ('Todas las expansiones', 'すべてのセット'),
    'Wishlist only': ('Solo lista de deseos', 'ウィッシュリストのみ'),
    'View': ('Vista', '表示'), 'Album': ('Álbum', 'アルバム'), 'List': ('Lista', 'リスト'),
    'Did you mean?': ('¿Quisiste decir?', 'もしかして？'),
    '↓ Export collection': ('↓ Exportar colección', '↓ コレクションをエクスポート'),
    'Exports all filtered entries. PDF and Word are text reports at this stage.': ('Exporta todos los registros filtrados. PDF y Word son informes de texto.', '絞り込んだ全項目を出力します。PDFとWordはテキスト形式です。'),
    'Include private notes in file': ('Incluir notas privadas en el archivo', 'ファイルに非公開メモを含める'),
    'Format': ('Formato', '形式'), 'Prepare file': ('Preparar archivo', 'ファイルを作成'),
    'Download file': ('Descargar archivo', 'ダウンロード'),
    'Could not generate the file. Please try again.': ('No se pudo generar el archivo. Inténtalo de nuevo.', 'ファイルを作成できませんでした。再度お試しください。'),
    'No cards found. Try adjusting your filters.': ('No se encontraron cartas. Ajusta los filtros.', 'カードが見つかりません。フィルターを変更してください。'),
    '{count} entries found': ('{count} registros encontrados', '{count}件見つかりました'),
    'Card': ('Carta', 'カード'), 'Quantity': ('Cantidad', '数量'),
    'Condition': ('Estado', '状態'), 'Image unavailable': ('Imagen no disponible', '画像なし'),
    'Edit': ('Editar', '編集'), 'Edit entry': ('Editar registro', '項目を編集'),
    'Variant': ('Variante', 'バリエーション'), 'Card language': ('Idioma de la carta', 'カードの言語'),
    'Custom variant': ('Variante personalizada', 'カスタムバリエーション'),
    'Private notes': ('Notas privadas', '非公開メモ'), 'On wishlist': ('En lista de deseos', 'ウィッシュリストに追加'),
    'Save': ('Guardar', '保存'), 'Not specified': ('Sin especificar', '指定なし'),
    'Other / Custom': ('Otra / Personalizada', 'その他 / カスタム'),
    'Find a card in the catalog and use “Add to collection”.': ('Busca una carta en el catálogo y usa “Añadir a la colección”.', 'カタログからカードを検索し、コレクションに追加してください。'),
    'Could not load the collection. Check that the migration was applied and try again.': ('No se pudo cargar la colección. Inténtalo de nuevo o contacta con soporte.', 'コレクションを読み込めません。再度お試しいただくかサポートにお問い合わせください。'),
}


def install_messages(tables):
    for key, values in MESSAGES.items():
        for language, value in zip(LANGUAGES, values):
            tables[language][key] = value
    for english, (spanish, japanese) in COLLECTION.items():
        tables['English']['collection_ui:' + english] = english
        tables['Español']['collection_ui:' + english] = spanish
        tables['日本語']['collection_ui:' + english] = japanese
