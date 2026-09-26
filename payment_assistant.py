"""Checkout guidance using server-owned facts; never handles payment details."""

from chatbot import question_language


def reply(question, language='Português (BR)', paypal_ready=False):
    language = question_language(question, language)
    q = question.casefold()
    if any(term in q for term in ('paypal', 'internacional', 'international', 'dólar', 'dollar')):
        key = 'paypal' if 'paypal' in q else 'international'
    elif any(term in q for term in ('cartão', 'card', 'segurança', 'secure', 'seguro')):
        key = 'security'
    elif any(term in q for term in ('crédito', 'credit', 'saldo', 'balance', 'aprov', 'confirm', 'pending', 'pendente')):
        key = 'credits'
    elif any(term in q for term in ('atlas', 'pergunta', 'question', 'upgrade', 'plano', 'plan', 'assinatura')):
        key = 'atlas'
    else:
        key = 'general'
    copy = {
        'Português (BR)': {
            'paypal': 'PayPal ainda não está habilitado. Quando a conta e a confirmação de pagamento estiverem integradas, esta página mostrará a opção disponível.',
            'international': 'O checkout atual está disponível somente em BRL. Os valores em outras moedas são informativos.',
            'security': 'O pagamento é concluído no provedor. Não envie número de cartão, senha ou códigos nesta conversa.',
            'credits': 'Créditos são liberados após confirmação do servidor pelo provedor. Se o saldo não atualizar, recarregue a página e consulte o histórico de compras.',
            'atlas': 'Atlas inclui cinco perguntas gratuitas. Depois disso, a continuação com IA dependerá de um plano ativo; os planos de assinatura ainda aguardam a integração da cobrança recorrente.',
            'general': 'Posso explicar créditos, planos, segurança, PayPal e confirmação de pagamento. Qual é a sua dúvida?',
        },
        'English': {
            'paypal': 'PayPal is not enabled yet. Once the account and payment verification are connected, the available option will appear here.',
            'international': 'Checkout currently supports BRL only. Other currencies are for display.',
            'security': 'Payment happens with the provider. Do not share card numbers, passwords or codes in this chat.',
            'credits': 'Credits are released after the provider confirms payment to the server. Refresh and check purchase history if the balance has not changed.',
            'atlas': 'Atlas includes five free questions. Further AI chat requires an active plan; recurring subscription checkout is still being connected.',
            'general': 'I can explain credits, plans, security, PayPal and payment confirmation. What would you like to know?',
        },
        'Español': {
            'paypal': 'PayPal aún no está habilitado. La opción aparecerá cuando conectemos la cuenta y la verificación de pagos.',
            'international': 'El checkout actual solo admite BRL. Los valores en otras monedas son informativos.',
            'security': 'El pago se realiza con el proveedor. No compartas números de tarjeta, contraseñas ni códigos en este chat.',
            'credits': 'Los créditos se liberan tras la confirmación del pago en el servidor. Actualiza la página y revisa el historial de compras.',
            'atlas': 'Atlas incluye cinco preguntas gratuitas. Para seguir usando IA necesitarás un plan activo; la suscripción recurrente aún está en preparación.',
            'general': 'Puedo explicar créditos, planes, seguridad, PayPal y confirmación de pagos. ¿Cuál es tu duda?',
        },
        '日本語': {
            'paypal': 'PayPalはまだ利用できません。アカウントと支払い確認の連携後に選択肢を表示します。',
            'international': '現在の決済はBRLのみ対応しています。他の通貨の表示は参考価格です。',
            'security': '支払いは決済事業者で行います。このチャットにカード番号、パスワード、認証コードを入力しないでください。',
            'credits': 'サーバーが決済を確認した後にクレジットを付与します。残高が変わらない場合は更新して購入履歴をご確認ください。',
            'atlas': 'Atlasの無料質問は5回です。以降のAI会話には有効なプランが必要です。定期課金は準備中です。',
            'general': 'クレジット、プラン、セキュリティ、PayPal、決済確認についてご案内できます。',
        },
    }
    return copy.get(language, copy['English'])[key]


def render_payment_assistant(st, language):
    heading = '💬 Ajuda com planos e pagamentos' if language == 'Português (BR)' else '💬 Plans and payment help'
    st.subheader(heading)
    history = st.session_state.setdefault('payment_help_history', [])
    for entry in history[-8:]:
        with st.chat_message(entry['role']):
            st.write(entry['text'])
    prompt = 'Pergunte sobre pagamento ou planos' if language == 'Português (BR)' else 'Ask about payments or plans'
    if question := st.chat_input(prompt, key='payment_help_input', max_chars=300):
        history.extend(({'role': 'user', 'text': question}, {'role': 'assistant', 'text': reply(question, language)}))
        st.session_state.payment_help_history = history[-8:]
        st.rerun()
