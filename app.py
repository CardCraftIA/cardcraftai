# CARDCRAFTAI RELIABILITY 2.6.21
# Resiliencia operacional + recuperacao de falhas + historico rastreavel 2.5.0

import base64
import json
import time
import unicodedata
import uuid
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from html import escape
from io import BytesIO
from urllib.parse import quote_plus

import requests
import streamlit as st
from google import genai
from google.genai import errors, types
from PIL import Image
from supabase import create_client


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="CardCraftAI - TCG Intelligence",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# ESTILO
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px;
        padding-top: 3.25rem;
        padding-bottom: 2rem;
    }

    /* Reliability 2.6.16: evita recorte vertical de rótulos no topo. */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stTextInput"] label,
    div[data-testid="stFileUploader"] label,
    div[data-testid="stCameraInput"] label,
    div[data-testid="stCheckbox"] label {
        overflow: visible !important;
        line-height: 1.4 !important;
        min-height: 1.45rem;
    }

    div[data-testid="stSelectbox"] label p,
    div[data-testid="stTextInput"] label p,
    div[data-testid="stFileUploader"] label p,
    div[data-testid="stCameraInput"] label p,
    div[data-testid="stCheckbox"] label p {
        overflow: visible !important;
        line-height: 1.4 !important;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(120, 120, 120, 0.25);
        padding: 16px;
        border-radius: 12px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SECRETS
# ============================================================

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    # Esta variavel guarda a nova Secret key (sb_secret_...) do Supabase.
    # O nome foi mantido para compatibilidade com a configuracao do Streamlit.
    SUPABASE_SERVICE_ROLE_KEY = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

except Exception:
    st.error(
        "⚠️ Faltam configurações nos Secrets do Streamlit.\n\n"
        "Verifique:\n"
        "- GEMINI_API_KEY\n"
        "- SUPABASE_URL\n"
        "- SUPABASE_KEY\n"
        "- SUPABASE_SERVICE_ROLE_KEY"
    )
    st.stop()

APP_VERSION = "2.6.21"
AI_MODEL = "gemini-3.6-flash"
AI_FALLBACK_MODEL = "gemini-3-flash-preview"
GEMINI_TIMEOUT_MS = 90_000
ANALYSIS_STALE_MINUTES = 15


# ============================================================
# RELIABILITY 2.6.20 - MATCHING EXATO DO CATALOGO + UI LOCALIZADA
# ============================================================

LANGUAGE_OPTIONS = [
    "English",
    "Português (BR)",
    "Español",
    "日本語",
]

LANGUAGE_LOCALES = {
    "English": "en",
    "Português (BR)": "pt-BR",
    "Español": "es",
    "日本語": "ja",
}

PRICING_CURRENCIES = ["BRL", "USD", "EUR"]

CURRENCY_LABELS = {
    "BRL": "BRL — R$",
    "USD": "USD — US$",
    "EUR": "EUR — €",
}

UI_TEXT = {
    "English": {
        "language": "🌐 Language / Idioma",
        "tagline_login": "Artificial intelligence for TCG card identification and evaluation",
        "access_account": "🔐 Access your account",
        "password_reset_success": "Password reset successfully. ✅ You can now sign in with your new password.",
        "tab_login": "🔑 Sign in",
        "tab_signup": "✨ Create Account",
        "login_intro": "Sign in with your email and password.",
        "email_confirm_hint": "New accounts must confirm their email before the first sign-in.",
        "email": "Email",
        "password": "Password",
        "email_placeholder": "you@example.com",
        "sign_in": "🔑 Sign in",
        "fill_email_password": "Enter your email and password.",
        "login_success": "Signed in successfully.",
        "session_failed": "Could not start the session.",
        "login_failed": "Could not sign in.",
        "check_credentials": "Check your email, password and whether the account has been confirmed.",
        "forgot_password": "🔁 Forgot my password",
        "recover_access": "Recover access",
        "recover_caption": "Enter your account email. If an account exists, we will send a link to create a new password.",
        "recovery_email": "Recovery email",
        "send_recovery": "📧 Send recovery link",
        "enter_email": "Enter your email.",
        "recovery_sent": "If an account exists with this email, CardCraftAI will send a password reset link. ✅",
        "check_spam": "Also check Spam, Junk and Promotions.",
        "recovery_request_failed": "Could not request password recovery right now.",
        "try_again_later": "Wait a moment and try again.",
        "signup_intro": "Create your CardCraftAI account.",
        "free_credits": "🎁 New accounts receive 5 free credits.",
        "your_email": "Your email",
        "create_password": "Create a password",
        "confirm_password": "Confirm your password",
        "password_policy": "Use at least 8 characters, including a lowercase letter, uppercase letter, number and symbol.",
        "accept_legal": "I have read and accept the Terms of Use and Privacy Policy.",
        "legal_available": "You can review the documents below before signing up. Current version: {version}.",
        "create_account": "✨ Create my account",
        "password_min": "The password must have at least {n} characters.",
        "password_lower": "The password must contain at least one lowercase letter.",
        "password_upper": "The password must contain at least one uppercase letter.",
        "password_digit": "The password must contain at least one number.",
        "password_symbol": "The password must contain at least one symbol.",
        "password_mismatch": "The two passwords do not match.",
        "must_accept_legal": "To create the account, you must accept the Terms of Use and Privacy Policy.",
        "signup_success": "Account created! ✅",
        "confirmation_sent": "📧 We sent a confirmation email to {email}. Open the CardCraftAI message and click ‘Confirm my email’.",
        "confirmation_required": "🔒 Your account can only sign in to CardCraftAI after the email is confirmed.",
        "signup_failed": "Could not create the account.",
        "legal_beta": "Beta legal documents",
        "terms": "📜 Terms of Use",
        "privacy": "🔒 Privacy Policy",
        "new_password_title": "🔐 Create a new password",
        "new_password_intro": "Set the new password for your account.",
        "new_password": "New password",
        "confirm_new_password": "Confirm the new password",
        "save_new_password": "✅ Save new password",
        "change_password_failed": "Could not change the password.",
        "cancel_login": "← Cancel and return to sign in",
        "recovery_invalid": "The recovery link is invalid, expired or has already been used. Request a new link using ‘Forgot my password’.",
        "panel": "⚙️ Control Panel",
        "account": "👤 Account",
        "credits": "💎 Credits",
        "current_plan": "Current plan: {plan}",
        "plan_label": "Current plan",
        "plan_free": "Free",
        "email_label": "Email",
        "email_not_confirmed": "Your email address is not confirmed yet.",
        "credits_label": "Credits",
        "no_credits": "You have no credits available.",
        "navigation": "Navigation",
        "nav_photo": "📸 Photo Analysis",
        "nav_search": "🔍 Search Card by Name",
        "nav_plans": "💳 Plans & Credits",
        "nav_account": "👤 My Account",
        "nav_terms": "📜 Terms of Use",
        "nav_privacy": "🔒 Privacy Policy",
        "sign_out": "🚪 Sign out",
        "tagline_app": "Artificial intelligence for TCG card identification, analysis and visual cataloging.",
        "result": "📊 Analysis Result",
        "web_disabled": "🧪 Web search is temporarily disabled in this version.",
        "analysis_used_credit": "💎 The completed analysis used 1 credit.",
        "photo_title": "📸 Photo Analysis",
        "photo_intro": "Upload or take a photo of your card.",
        "analysis_cost": "💎 Each completed analysis uses 1 credit.",
        "upload_file": "📁 Upload File",
        "use_camera": "📷 Use Camera",
        "choose_image": "Choose an image",
        "take_photo": "Take a photo of the card",
        "selected_card": "Selected card",
        "analyze_card": "🚀 Analyze Card — 1 credit",
        "analyzing_card": "🤖 Analyzing the card...",
        "send_photo_start": "👈 Upload or take a photo to begin.",
        "analysis_complete": "✅ Analysis complete.",
        "search_title": "🔍 Search Card by Name",
        "catalog_free": "🖼️ Searching and comparing images in the Pokémon catalog is free. Specialized analysis uses 1 credit.",
        "card_name": "Card name",
        "set_name": "Collection / Set",
        "search_catalog": "🖼️ Search catalog — free",
        "enter_card_name": "Enter the card name to search the catalog.",
        "searching_catalog": "📚 Searching the Pokémon catalog...",
        "catalog_error": "Could not query the Pokémon catalog right now.",
        "catalog_results": "🖼️ Visual catalog results",
        "no_catalog_results": "No matching card was found.",
        "specialized_analysis": "🤖 Specialized analysis",
        "analyze_one_credit": "🤖 Analyze — 1 credit",
        "my_account": "👤 My Account",
        "account_caption": "View your account data, balance, security and history.",
        "confirmed_email": "Confirmed email",
        "yes": "Yes ✅",
        "no": "No",
        "available_credits": "Available credits",
        "account_data": "📧 Account data",
        "email_confirmed_ok": "Your email address is confirmed.",
        "security": "🔐 Security",
        "security_reset_text": "To change your password, send a secure reset link to your account email.",
        "send_password_reset": "📨 Send password reset link",
        "purchase_history": "🧾 Purchase history",
        "no_purchases": "No purchases have been recorded for this account yet.",
        "session": "🚪 Session",
        "sign_out_account": "Sign out of my account",
        "plans_title": "💳 Plans & Credits",
        "balance": "💎 Your current balance",
        "credits_word": "credits",
        "packages_from_db": "The packages below are loaded directly from Supabase.",
        "no_packages": "No active package is available right now.",
        "credit_packages": "🎒 Credit Packages",
        "price": "Price",
        "buy": "Buy {name}",
        "checkout_pending": "💳 Checkout is not connected yet.",
        "checkout_creating": "Creating secure checkout...",
        "checkout_ready": "Secure checkout created. Continue to Mercado Pago to complete your purchase.",
        "checkout_open": "🔐 Continue to Mercado Pago",
        "checkout_error": "Could not start the checkout.",
        "secure_checkout_note": "Payments are processed securely by Mercado Pago. CardCraftAI does not receive or store your card details.",
        "currency_label": "Display currency",
        "currency_caption": "Currency is independent of the interface language. Prices are loaded from CardCraftAI's pricing table.",
        "international_checkout_pending": "International prices are available for display, but checkout in {currency} is not enabled yet. Purchases are currently processed only in BRL.",
        "currency_price_missing": "Price unavailable in {currency}.",
        "subscription_brl_only": "The Store Plan is currently priced and billed only in BRL.",
        "payment_success_return": "✅ Mercado Pago returned the payment as approved. Credits are released only after server confirmation. If the balance has not updated yet, wait a few seconds and refresh.",
        "payment_pending_return": "⏳ The payment is still pending. Credits will be released automatically after Mercado Pago confirms approval.",
        "payment_failure_return": "❌ The payment was not completed. No credits were added.",
        "refresh_balance": "🔄 Refresh balance",
        "subscriptions": "🏢 Subscriptions",
        "per_cycle": "{n} credits per cycle",
        "monthly_fee": "Monthly fee",
        "subscribe": "Subscribe to {name}",
        "subscription_pending": "💳 Recurring subscription checkout is not enabled yet. This plan cannot be purchased until recurring billing is connected.",
        "beta_legal_note": "Beta document. Before commercial launch, we will publish the official support/privacy contact and complete the final legal review.",
    },
    "Português (BR)": {
        "language": "🌐 Idioma / Language",
        "tagline_login": "Inteligência artificial para identificação e avaliação de cartas TCG",
        "access_account": "🔐 Acesse sua conta",
        "password_reset_success": "Senha redefinida com sucesso. ✅ Agora você já pode entrar com a nova senha.",
        "tab_login": "🔑 Entrar", "tab_signup": "✨ Criar Conta", "login_intro": "Entre com seu e-mail e senha.",
        "email_confirm_hint": "Novos cadastros precisam confirmar o e-mail antes do primeiro acesso.",
        "email": "E-mail", "password": "Senha", "email_placeholder": "seuemail@exemplo.com", "sign_in": "🔑 Entrar",
        "fill_email_password": "Preencha o e-mail e a senha.", "login_success": "Login realizado com sucesso.",
        "session_failed": "Não foi possível iniciar a sessão.", "login_failed": "Não foi possível entrar.",
        "check_credentials": "Verifique o e-mail, a senha e se a conta já foi confirmada.", "forgot_password": "🔁 Esqueci minha senha",
        "recover_access": "Recuperar acesso", "recover_caption": "Informe o e-mail da sua conta. Se houver uma conta associada, enviaremos um link para criar uma nova senha.",
        "recovery_email": "E-mail para recuperação", "send_recovery": "📧 Enviar link de recuperação", "enter_email": "Informe seu e-mail.",
        "recovery_sent": "Se existir uma conta com esse e-mail, o CardCraftAI enviará uma mensagem com o link para redefinir a senha. ✅",
        "check_spam": "Verifique também Spam, Lixo eletrônico e Promoções.", "recovery_request_failed": "Não foi possível solicitar a recuperação agora.",
        "try_again_later": "Aguarde alguns instantes e tente novamente.", "signup_intro": "Crie sua conta CardCraftAI.",
        "free_credits": "🎁 Novas contas recebem 5 créditos gratuitos.", "your_email": "Seu e-mail", "create_password": "Crie uma senha",
        "confirm_password": "Confirme sua senha", "password_policy": "Use pelo menos 8 caracteres, incluindo letra minúscula, letra maiúscula, número e símbolo.",
        "accept_legal": "Li e aceito os Termos de Uso e a Política de Privacidade.", "legal_available": "Os documentos podem ser consultados abaixo antes do cadastro. Versão vigente: {version}.",
        "create_account": "✨ Criar minha conta", "password_min": "A senha precisa ter pelo menos {n} caracteres.",
        "password_lower": "A senha precisa ter pelo menos uma letra minúscula.", "password_upper": "A senha precisa ter pelo menos uma letra maiúscula.",
        "password_digit": "A senha precisa ter pelo menos um número.", "password_symbol": "A senha precisa ter pelo menos um símbolo.",
        "password_mismatch": "As duas senhas não são iguais.", "must_accept_legal": "Para criar a conta, você precisa aceitar os Termos de Uso e a Política de Privacidade.",
        "signup_success": "Cadastro realizado! ✅", "confirmation_sent": "📧 Enviamos um e-mail de confirmação para {email}. Abra a mensagem do CardCraftAI e clique em ‘Confirmar meu e-mail’.",
        "confirmation_required": "🔒 Sua conta só poderá entrar no CardCraftAI depois que o e-mail for confirmado.", "signup_failed": "Não foi possível criar a conta.",
        "legal_beta": "Documentos legais da versão beta", "terms": "📜 Termos de Uso", "privacy": "🔒 Política de Privacidade",
        "new_password_title": "🔐 Crie uma nova senha", "new_password_intro": "Defina a nova senha da sua conta.", "new_password": "Nova senha",
        "confirm_new_password": "Confirme a nova senha", "save_new_password": "✅ Salvar nova senha", "change_password_failed": "Não foi possível alterar a senha.",
        "cancel_login": "← Cancelar e voltar ao login", "recovery_invalid": "O link de recuperação é inválido, expirou ou já foi usado. Solicite um novo link em ‘Esqueci minha senha’.",
        "panel": "⚙️ Painel de Controle", "account": "👤 Conta", "credits": "💎 Créditos", "current_plan": "Plano atual: {plan}",
        "plan_label": "Plano atual", "plan_free": "Gratuito", "email_label": "E-mail", "email_not_confirmed": "Seu endereço de e-mail ainda não está confirmado.", "credits_label": "Créditos",
        "no_credits": "Você não possui créditos disponíveis.", "navigation": "Navegação", "nav_photo": "📸 Análise por Foto", "nav_search": "🔍 Buscar Carta por Nome",
        "nav_plans": "💳 Planos e Créditos", "nav_account": "👤 Minha Conta", "nav_terms": "📜 Termos de Uso", "nav_privacy": "🔒 Política de Privacidade",
        "sign_out": "🚪 Sair da conta", "tagline_app": "Inteligência artificial para identificação, análise e catálogo visual de cartas TCG.", "result": "📊 Resultado da Análise",
        "web_disabled": "🧪 A pesquisa web está temporariamente desativada nesta versão.", "analysis_used_credit": "💎 A análise concluída consumiu 1 crédito.",
        "photo_title": "📸 Análise por Foto", "photo_intro": "Envie ou tire uma foto da sua carta.", "analysis_cost": "💎 Cada análise concluída consome 1 crédito.",
        "upload_file": "📁 Enviar Arquivo", "use_camera": "📷 Usar Câmera", "choose_image": "Escolha uma imagem", "take_photo": "Tire uma foto da carta",
        "selected_card": "Carta selecionada", "analyze_card": "🚀 Analisar Carta — 1 crédito", "analyzing_card": "🤖 Analisando a carta...",
        "send_photo_start": "👈 Envie ou tire uma foto para começar.", "analysis_complete": "✅ Análise concluída.", "search_title": "🔍 Buscar Carta por Nome",
        "catalog_free": "🖼️ Buscar e comparar imagens no catálogo Pokémon é grátis. A análise especializada consome 1 crédito.", "card_name": "Nome da carta",
        "set_name": "Coleção / Conjunto", "search_catalog": "🖼️ Buscar no catálogo — grátis", "enter_card_name": "Digite o nome da carta para pesquisar no catálogo.",
        "searching_catalog": "📚 Procurando cartas no catálogo Pokémon...", "catalog_error": "Não foi possível consultar o catálogo Pokémon agora.",
        "catalog_results": "🖼️ Resultados visuais do catálogo", "no_catalog_results": "Nenhuma carta correspondente foi encontrada.", "specialized_analysis": "🤖 Análise especializada",
        "analyze_one_credit": "🤖 Analisar — 1 crédito", "my_account": "👤 Minha Conta", "account_caption": "Consulte seus dados, saldo, segurança e histórico da conta.",
        "confirmed_email": "E-mail confirmado", "yes": "Sim ✅", "no": "Não", "available_credits": "Créditos disponíveis", "account_data": "📧 Dados da conta",
        "email_confirmed_ok": "Seu endereço de e-mail está confirmado.", "security": "🔐 Segurança", "security_reset_text": "Se quiser trocar sua senha, envie um link seguro de redefinição para o e-mail da sua conta.",
        "send_password_reset": "📨 Enviar link para redefinir senha", "purchase_history": "🧾 Histórico de compras", "no_purchases": "Nenhuma compra registrada nesta conta até o momento.",
        "session": "🚪 Sessão", "sign_out_account": "Sair da minha conta", "plans_title": "💳 Planos e Créditos", "balance": "💎 Seu saldo atual", "credits_word": "créditos",
        "packages_from_db": "Os pacotes abaixo são carregados diretamente do Supabase.", "no_packages": "Nenhum pacote ativo está disponível no momento.", "credit_packages": "🎒 Pacotes de Créditos",
        "price": "Preço", "buy": "Comprar {name}", "checkout_pending": "💳 O checkout ainda não está conectado.",
        "checkout_creating": "Criando checkout seguro...", "checkout_ready": "Checkout seguro criado. Continue no Mercado Pago para concluir a compra.",
        "checkout_open": "🔐 Continuar para o Mercado Pago", "checkout_error": "Não foi possível iniciar o checkout.",
        "secure_checkout_note": "O pagamento é processado com segurança pelo Mercado Pago. O CardCraftAI não recebe nem armazena os dados do seu cartão.",
        "currency_label": "Moeda de exibição",
        "currency_caption": "A moeda é independente do idioma da interface. Os preços são carregados da tabela de preços do CardCraftAI.",
        "international_checkout_pending": "Os preços internacionais já estão disponíveis para exibição, mas o checkout em {currency} ainda não está habilitado. As compras são processadas atualmente apenas em BRL.",
        "currency_price_missing": "Preço indisponível em {currency}.",
        "subscription_brl_only": "O Plano Lojista está atualmente precificado e cobrado somente em BRL.",
        "payment_success_return": "✅ O Mercado Pago retornou o pagamento como aprovado. Os créditos só são liberados após a confirmação do servidor. Se o saldo ainda não atualizou, aguarde alguns segundos e atualize.",
        "payment_pending_return": "⏳ O pagamento ainda está pendente. Os créditos serão liberados automaticamente quando o Mercado Pago confirmar a aprovação.",
        "payment_failure_return": "❌ O pagamento não foi concluído. Nenhum crédito foi adicionado.",
        "refresh_balance": "🔄 Atualizar saldo",
        "subscriptions": "🏢 Assinaturas", "per_cycle": "{n} créditos por ciclo", "monthly_fee": "Mensalidade", "subscribe": "Assinar {name}",
        "subscription_pending": "💳 O checkout recorrente da assinatura ainda não está habilitado. Este plano não pode ser comprado até integrarmos a cobrança recorrente.",
        "beta_legal_note": "Documento beta. Antes do lançamento comercial, vamos publicar o canal oficial de suporte/privacidade e concluir a revisão jurídica final.",
    },
    "Español": {
        "language": "🌐 Idioma / Language", "tagline_login": "Inteligencia artificial para identificación y evaluación de cartas TCG", "access_account": "🔐 Accede a tu cuenta",
        "password_reset_success": "Contraseña restablecida correctamente. ✅ Ya puedes iniciar sesión con la nueva contraseña.", "tab_login": "🔑 Entrar", "tab_signup": "✨ Crear cuenta",
        "login_intro": "Inicia sesión con tu correo y contraseña.", "email_confirm_hint": "Las cuentas nuevas deben confirmar el correo antes del primer acceso.", "email": "Correo electrónico",
        "password": "Contraseña", "email_placeholder": "tuemail@ejemplo.com", "sign_in": "🔑 Entrar", "fill_email_password": "Introduce el correo y la contraseña.", "login_success": "Sesión iniciada correctamente.",
        "session_failed": "No se pudo iniciar la sesión.", "login_failed": "No fue posible entrar.", "check_credentials": "Verifica el correo, la contraseña y si la cuenta ya fue confirmada.",
        "forgot_password": "🔁 Olvidé mi contraseña", "recover_access": "Recuperar acceso", "recover_caption": "Introduce el correo de tu cuenta. Si existe una cuenta asociada, enviaremos un enlace para crear una nueva contraseña.",
        "recovery_email": "Correo de recuperación", "send_recovery": "📧 Enviar enlace de recuperación", "enter_email": "Introduce tu correo.",
        "recovery_sent": "Si existe una cuenta con este correo, CardCraftAI enviará un enlace para restablecer la contraseña. ✅", "check_spam": "Revisa también Spam, Correo no deseado y Promociones.",
        "recovery_request_failed": "No se pudo solicitar la recuperación ahora.", "try_again_later": "Espera unos instantes e inténtalo de nuevo.", "signup_intro": "Crea tu cuenta CardCraftAI.",
        "free_credits": "🎁 Las cuentas nuevas reciben 5 créditos gratuitos.", "your_email": "Tu correo", "create_password": "Crea una contraseña", "confirm_password": "Confirma tu contraseña",
        "password_policy": "Usa al menos 8 caracteres, incluyendo una minúscula, una mayúscula, un número y un símbolo.", "accept_legal": "He leído y acepto los Términos de Uso y la Política de Privacidad.",
        "legal_available": "Puedes consultar los documentos antes del registro. Versión vigente: {version}.", "create_account": "✨ Crear mi cuenta", "password_min": "La contraseña debe tener al menos {n} caracteres.",
        "password_lower": "La contraseña debe contener al menos una letra minúscula.", "password_upper": "La contraseña debe contener al menos una letra mayúscula.", "password_digit": "La contraseña debe contener al menos un número.",
        "password_symbol": "La contraseña debe contener al menos un símbolo.", "password_mismatch": "Las dos contraseñas no coinciden.", "must_accept_legal": "Para crear la cuenta, debes aceptar los Términos de Uso y la Política de Privacidad.",
        "signup_success": "¡Cuenta creada! ✅", "confirmation_sent": "📧 Enviamos un correo de confirmación a {email}. Abre el mensaje de CardCraftAI y pulsa ‘Confirmar mi correo’.",
        "confirmation_required": "🔒 Tu cuenta solo podrá entrar en CardCraftAI después de confirmar el correo.", "signup_failed": "No se pudo crear la cuenta.", "legal_beta": "Documentos legales de la versión beta",
        "terms": "📜 Términos de Uso", "privacy": "🔒 Política de Privacidad", "new_password_title": "🔐 Crea una nueva contraseña", "new_password_intro": "Define la nueva contraseña de tu cuenta.",
        "new_password": "Nueva contraseña", "confirm_new_password": "Confirma la nueva contraseña", "save_new_password": "✅ Guardar nueva contraseña", "change_password_failed": "No se pudo cambiar la contraseña.",
        "cancel_login": "← Cancelar y volver al acceso", "recovery_invalid": "El enlace de recuperación no es válido, ha caducado o ya fue usado. Solicita uno nuevo en ‘Olvidé mi contraseña’.",
        "panel": "⚙️ Panel de Control", "account": "👤 Cuenta", "credits": "💎 Créditos", "current_plan": "Plan actual: {plan}",
        "plan_label": "Plan actual", "plan_free": "Gratis", "email_label": "Correo electrónico", "email_not_confirmed": "Tu correo electrónico todavía no está confirmado.", "credits_label": "Créditos", "no_credits": "No tienes créditos disponibles.",
        "navigation": "Navegación", "nav_photo": "📸 Análisis por Foto", "nav_search": "🔍 Buscar Carta por Nombre", "nav_plans": "💳 Planes y Créditos", "nav_account": "👤 Mi Cuenta",
        "nav_terms": "📜 Términos de Uso", "nav_privacy": "🔒 Política de Privacidad", "sign_out": "🚪 Cerrar sesión", "tagline_app": "Inteligencia artificial para identificación, análisis y catálogo visual de cartas TCG.",
        "result": "📊 Resultado del Análisis", "web_disabled": "🧪 La búsqueda web está temporalmente desactivada en esta versión.", "analysis_used_credit": "💎 El análisis completado consumió 1 crédito.",
        "photo_title": "📸 Análisis por Foto", "photo_intro": "Sube o toma una foto de tu carta.", "analysis_cost": "💎 Cada análisis completado consume 1 crédito.", "upload_file": "📁 Subir Archivo",
        "use_camera": "📷 Usar Cámara", "choose_image": "Elige una imagen", "take_photo": "Toma una foto de la carta", "selected_card": "Carta seleccionada", "analyze_card": "🚀 Analizar Carta — 1 crédito",
        "analyzing_card": "🤖 Analizando la carta...", "send_photo_start": "👈 Sube o toma una foto para comenzar.", "analysis_complete": "✅ Análisis completado.", "search_title": "🔍 Buscar Carta por Nombre",
        "catalog_free": "🖼️ Buscar y comparar imágenes en el catálogo Pokémon es gratis. El análisis especializado consume 1 crédito.", "card_name": "Nombre de la carta", "set_name": "Colección / Conjunto",
        "search_catalog": "🖼️ Buscar en el catálogo — gratis", "enter_card_name": "Escribe el nombre de la carta para buscar en el catálogo.", "searching_catalog": "📚 Buscando cartas en el catálogo Pokémon...",
        "catalog_error": "No se pudo consultar el catálogo Pokémon ahora.", "catalog_results": "🖼️ Resultados visuales del catálogo", "no_catalog_results": "No se encontró ninguna carta correspondiente.",
        "specialized_analysis": "🤖 Análisis especializado", "analyze_one_credit": "🤖 Analizar — 1 crédito", "my_account": "👤 Mi Cuenta", "account_caption": "Consulta tus datos, saldo, seguridad e historial de la cuenta.",
        "confirmed_email": "Correo confirmado", "yes": "Sí ✅", "no": "No", "available_credits": "Créditos disponibles", "account_data": "📧 Datos de la cuenta", "email_confirmed_ok": "Tu correo electrónico está confirmado.",
        "security": "🔐 Seguridad", "security_reset_text": "Para cambiar tu contraseña, envía un enlace seguro de restablecimiento al correo de tu cuenta.", "send_password_reset": "📨 Enviar enlace para restablecer contraseña",
        "purchase_history": "🧾 Historial de compras", "no_purchases": "Todavía no hay compras registradas en esta cuenta.", "session": "🚪 Sesión", "sign_out_account": "Cerrar mi sesión", "plans_title": "💳 Planes y Créditos",
        "balance": "💎 Tu saldo actual", "credits_word": "créditos", "packages_from_db": "Los paquetes siguientes se cargan directamente desde Supabase.", "no_packages": "No hay paquetes activos disponibles en este momento.",
        "credit_packages": "🎒 Paquetes de Créditos", "price": "Precio", "buy": "Comprar {name}", "checkout_pending": "💳 El checkout aún no está conectado.",
        "checkout_creating": "Creando checkout seguro...", "checkout_ready": "Checkout seguro creado. Continúa en Mercado Pago para completar la compra.",
        "checkout_open": "🔐 Continuar a Mercado Pago", "checkout_error": "No se pudo iniciar el checkout.",
        "secure_checkout_note": "El pago se procesa de forma segura por Mercado Pago. CardCraftAI no recibe ni almacena los datos de tu tarjeta.",
        "currency_label": "Moneda de visualización",
        "currency_caption": "La moneda es independiente del idioma de la interfaz. Los precios se cargan desde la tabla de precios de CardCraftAI.",
        "international_checkout_pending": "Los precios internacionales ya están disponibles para visualización, pero el checkout en {currency} todavía no está habilitado. Actualmente las compras se procesan solo en BRL.",
        "currency_price_missing": "Precio no disponible en {currency}.",
        "subscription_brl_only": "El Plan Tienda actualmente tiene precio y cobro únicamente en BRL.",
        "payment_success_return": "✅ Mercado Pago devolvió el pago como aprobado. Los créditos solo se liberan después de la confirmación del servidor. Si el saldo aún no se actualizó, espera unos segundos y actualiza.",
        "payment_pending_return": "⏳ El pago todavía está pendiente. Los créditos se liberarán automáticamente cuando Mercado Pago confirme la aprobación.",
        "payment_failure_return": "❌ El pago no se completó. No se añadieron créditos.",
        "refresh_balance": "🔄 Actualizar saldo",
        "subscriptions": "🏢 Suscripciones", "per_cycle": "{n} créditos por ciclo", "monthly_fee": "Mensualidad", "subscribe": "Suscribirse a {name}", "subscription_pending": "💳 El checkout recurrente de la suscripción aún no está habilitado. Este plan no puede comprarse hasta conectar la facturación recurrente.",
        "beta_legal_note": "Documento beta. Antes del lanzamiento comercial, publicaremos el contacto oficial de soporte/privacidad y completaremos la revisión jurídica final.",
    },
    "日本語": {
        "language": "🌐 Language / 言語", "tagline_login": "TCGカードの識別・評価を支援するAI", "access_account": "🔐 アカウントにログイン",
        "password_reset_success": "パスワードを再設定しました。✅ 新しいパスワードでログインできます。", "tab_login": "🔑 ログイン", "tab_signup": "✨ アカウント作成",
        "login_intro": "メールアドレスとパスワードでログインしてください。", "email_confirm_hint": "新規アカウントは初回ログイン前にメール確認が必要です。", "email": "メールアドレス",
        "password": "パスワード", "email_placeholder": "you@example.com", "sign_in": "🔑 ログイン", "fill_email_password": "メールアドレスとパスワードを入力してください。",
        "login_success": "ログインしました。", "session_failed": "セッションを開始できませんでした。", "login_failed": "ログインできませんでした。", "check_credentials": "メール、パスワード、アカウント確認済みかを確認してください。",
        "forgot_password": "🔁 パスワードを忘れた", "recover_access": "アクセスを復旧", "recover_caption": "アカウントのメールアドレスを入力してください。該当アカウントが存在する場合、新しいパスワードを作成するリンクを送信します。",
        "recovery_email": "復旧用メール", "send_recovery": "📧 復旧リンクを送信", "enter_email": "メールアドレスを入力してください。", "recovery_sent": "このメールのアカウントが存在する場合、CardCraftAI がパスワード再設定リンクを送信します。✅",
        "check_spam": "迷惑メールやプロモーションフォルダも確認してください。", "recovery_request_failed": "現在パスワード復旧をリクエストできません。", "try_again_later": "少し待ってから再度お試しください。",
        "signup_intro": "CardCraftAI アカウントを作成します。", "free_credits": "🎁 新規アカウントには5クレジットが無料で付与されます。", "your_email": "メールアドレス",
        "create_password": "パスワードを作成", "confirm_password": "パスワードを確認", "password_policy": "8文字以上で、小文字・大文字・数字・記号をそれぞれ1つ以上含めてください。",
        "accept_legal": "利用規約とプライバシーポリシーを読み、同意します。", "legal_available": "登録前に以下の文書を確認できます。現行版: {version}。", "create_account": "✨ アカウントを作成",
        "password_min": "パスワードは{n}文字以上必要です。", "password_lower": "小文字を1文字以上含めてください。", "password_upper": "大文字を1文字以上含めてください。", "password_digit": "数字を1文字以上含めてください。",
        "password_symbol": "記号を1文字以上含めてください。", "password_mismatch": "2つのパスワードが一致しません。", "must_accept_legal": "アカウントを作成するには利用規約とプライバシーポリシーへの同意が必要です。",
        "signup_success": "アカウントを作成しました！✅", "confirmation_sent": "📧 {email} に確認メールを送信しました。CardCraftAI のメールを開き、「メールを確認」をクリックしてください。",
        "confirmation_required": "🔒 メール確認が完了するまで CardCraftAI にログインできません。", "signup_failed": "アカウントを作成できませんでした。", "legal_beta": "ベータ版の法的文書",
        "terms": "📜 利用規約", "privacy": "🔒 プライバシーポリシー", "new_password_title": "🔐 新しいパスワードを作成", "new_password_intro": "アカウントの新しいパスワードを設定します。",
        "new_password": "新しいパスワード", "confirm_new_password": "新しいパスワードを確認", "save_new_password": "✅ 新しいパスワードを保存", "change_password_failed": "パスワードを変更できませんでした。",
        "cancel_login": "← キャンセルしてログインへ戻る", "recovery_invalid": "復旧リンクは無効、期限切れ、または既に使用されています。「パスワードを忘れた」から新しいリンクを取得してください。",
        "panel": "⚙️ コントロールパネル", "account": "👤 アカウント", "credits": "💎 クレジット", "current_plan": "現在のプラン: {plan}",
        "plan_label": "現在のプラン", "plan_free": "無料", "email_label": "メールアドレス", "email_not_confirmed": "メールアドレスはまだ確認されていません。", "credits_label": "クレジット", "no_credits": "利用可能なクレジットがありません。",
        "navigation": "ナビゲーション", "nav_photo": "📸 写真で分析", "nav_search": "🔍 カード名で検索", "nav_plans": "💳 プランとクレジット", "nav_account": "👤 マイアカウント",
        "nav_terms": "📜 利用規約", "nav_privacy": "🔒 プライバシーポリシー", "sign_out": "🚪 ログアウト", "tagline_app": "TCGカードの識別・分析・ビジュアルカタログを支援するAI。",
        "result": "📊 分析結果", "web_disabled": "🧪 このバージョンではWeb検索を一時的に無効化しています。", "analysis_used_credit": "💎 完了した分析で1クレジットを使用しました。",
        "photo_title": "📸 写真で分析", "photo_intro": "カードの写真をアップロードするか撮影してください。", "analysis_cost": "💎 完了した分析ごとに1クレジットを使用します。", "upload_file": "📁 ファイルをアップロード",
        "use_camera": "📷 カメラを使う", "choose_image": "画像を選択", "take_photo": "カードを撮影", "selected_card": "選択したカード", "analyze_card": "🚀 カードを分析 — 1クレジット",
        "analyzing_card": "🤖 カードを分析しています...", "send_photo_start": "👈 写真をアップロードまたは撮影して開始してください。", "analysis_complete": "✅ 分析が完了しました。", "search_title": "🔍 カード名で検索",
        "catalog_free": "🖼️ Pokémonカタログの画像検索・比較は無料です。専門分析は1クレジットを使用します。", "card_name": "カード名", "set_name": "コレクション / セット",
        "search_catalog": "🖼️ カタログを検索 — 無料", "enter_card_name": "検索するカード名を入力してください。", "searching_catalog": "📚 Pokémonカタログを検索しています...", "catalog_error": "現在Pokémonカタログを検索できません。",
        "catalog_results": "🖼️ カタログの画像結果", "no_catalog_results": "一致するカードが見つかりませんでした。", "specialized_analysis": "🤖 専門分析", "analyze_one_credit": "🤖 分析 — 1クレジット",
        "my_account": "👤 マイアカウント", "account_caption": "アカウント情報、残高、セキュリティ、履歴を確認します。", "confirmed_email": "確認済みメール", "yes": "はい ✅", "no": "いいえ",
        "available_credits": "利用可能クレジット", "account_data": "📧 アカウント情報", "email_confirmed_ok": "メールアドレスは確認済みです。", "security": "🔐 セキュリティ",
        "security_reset_text": "パスワードを変更するには、アカウントのメールに安全な再設定リンクを送信してください。", "send_password_reset": "📨 パスワード再設定リンクを送信", "purchase_history": "🧾 購入履歴",
        "no_purchases": "このアカウントにはまだ購入履歴がありません。", "session": "🚪 セッション", "sign_out_account": "アカウントからログアウト", "plans_title": "💳 プランとクレジット",
        "balance": "💎 現在の残高", "credits_word": "クレジット", "packages_from_db": "以下のパッケージはSupabaseから直接読み込まれます。", "no_packages": "現在利用可能なパッケージはありません。",
        "credit_packages": "🎒 クレジットパッケージ", "price": "価格", "buy": "{name} を購入", "checkout_pending": "💳 チェックアウトはまだ接続されていません。",
        "checkout_creating": "安全なチェックアウトを作成しています...", "checkout_ready": "安全なチェックアウトを作成しました。Mercado Pago で購入を完了してください。",
        "checkout_open": "🔐 Mercado Pago に進む", "checkout_error": "チェックアウトを開始できませんでした。",
        "secure_checkout_note": "支払いは Mercado Pago が安全に処理します。CardCraftAI はカード情報を受信・保存しません。",
        "currency_label": "表示通貨",
        "currency_caption": "表示通貨はインターフェース言語とは独立しています。価格は CardCraftAI の価格テーブルから読み込まれます。",
        "international_checkout_pending": "国際価格は表示できますが、{currency} でのチェックアウトはまだ有効化されていません。現在、購入処理は BRL のみ対応しています。",
        "currency_price_missing": "{currency} の価格は利用できません。",
        "subscription_brl_only": "ストアプランは現在 BRL のみで価格設定・請求されます。",
        "payment_success_return": "✅ Mercado Pago では支払いが承認済みとして戻りました。クレジットはサーバー確認後にのみ付与されます。残高がまだ更新されていない場合は、数秒待って更新してください。",
        "payment_pending_return": "⏳ 支払いはまだ保留中です。Mercado Pago が承認を確認すると、クレジットは自動的に付与されます。",
        "payment_failure_return": "❌ 支払いは完了しませんでした。クレジットは追加されていません。",
        "refresh_balance": "🔄 残高を更新",
        "subscriptions": "🏢 サブスクリプション", "per_cycle": "1サイクルあたり{n}クレジット", "monthly_fee": "月額", "subscribe": "{name} に登録", "subscription_pending": "💳 定期課金のチェックアウトはまだ有効化されていません。定期請求の接続が完了するまで、このプランは購入できません。",
        "beta_legal_note": "ベータ版文書です。商用公開前に公式サポート／プライバシー窓口を公開し、最終的な法務レビューを完了します。",
    },
}


# ============================================================
# RELIABILITY 2.6.20 - TEXTOS LOCALIZADOS DO CATALOGO/VALIDACAO
# ============================================================

UI_TEXT["English"].update({
    "not_confirmed": "Not confirmed",
    "catalog_no_data_title": "Could not validate against the catalog",
    "catalog_no_data_message": "The AI did not identify a card name confidently enough to query the catalog.",
    "catalog_no_result_title": "Not validated by the catalog",
    "catalog_no_result_message": "The catalog did not return a usable match for the photo identification.",
    "catalog_validated_title": "✅ Identification validated by the catalog",
    "catalog_validated_message": "The exact number was found, and the normalized name and set match a real Pokémon TCG catalog card.",
    "catalog_probable_title": "🟡 Identification is probably correct",
    "catalog_probable_image_message": "The catalog found a strong match, but the image quality prevents automatic confirmation.",
    "catalog_probable_missing_message": "The catalog found a strong match, but at least one important identifier still needs confirmation.",
    "catalog_inconclusive_title": "⚠️ Identification not confirmed yet",
    "catalog_inconclusive_number_message": "The AI provided a card number, but no exact match with that number was confirmed. Cards with different numbers are shown only for comparison and are not treated as the same card.",
    "catalog_inconclusive_message": "The catalog found similar versions, but the photo data is still insufficient to confirm the exact card.",
    "confidence_divergence_label": "⚠️ Mismatch detected",
    "confidence_divergence_message": "The card number read from the image differs from the catalog candidate. CardCraftAI blocked promotion to confirmed or high-confidence status.",
    "confidence_ai_number": "Number read by AI: #{number}",
    "confidence_catalog_number": "Catalog candidate number: #{number}",
    "confidence_number_priority": "A number mismatch takes priority over name or set similarity.",
    "confidence_confirmed_label": "✅ Confirmed by catalog",
    "confidence_confirmed_message": "The card's main identity was externally confirmed by exact number, name and set.",
    "confidence_exact_number": "Exact card number found in the Pokémon TCG catalog.",
    "confidence_name_match": "Name matches the catalog result.",
    "confidence_set_match": "Set matches the catalog result.",
    "confidence_partial_label": "🟡 Partially confirmed",
    "confidence_partial_message": "The catalog confirms relevant parts of the identification, but a decisive identifier is still missing for exact-card confirmation.",
    "confidence_exact_candidate": "Exact number matches a catalog candidate.",
    "confidence_name_strong": "Name strongly matches the catalog.",
    "confidence_set_strong": "Set strongly matches the catalog.",
    "confidence_number_missing": "The card number was not read with enough confidence.",
    "confidence_number_not_exact": "The card number still has no exact confirmation.",
    "confidence_set_missing": "The set was not read with enough confidence.",
    "confidence_catalog_no_match": "The catalog was queried but did not confirm a usable match.",
    "confidence_candidates_insufficient": "Catalog candidates exist, but the match is still insufficient.",
    "confidence_no_external_evidence": "There is not enough external evidence to confirm the identity.",
    "confidence_not_confirmed_label": "⚪ Not confirmed",
    "confidence_not_confirmed_message": "The available evidence is not yet sufficient for a safe identity confirmation.",
    "confidence_high_visual_label": "🟢 High visual confidence",
    "confidence_high_visual_message": "The visual reading is strong and contains name, set and number, but there is no external catalog confirmation for this run yet.",
    "confidence_fields_extracted": "Name, set and number were extracted from the image.",
    "confidence_visual_strong": "The AI's preliminary visual reading was classified as strong.",
    "confidence_image_quality_ok": "The image quality was classified as good or acceptable.",
    "confidence_not_catalog_confirmation": "This level is not equivalent to catalog confirmation.",
    "confidence_no_external": "No external confirmation is available for this classification.",
    "confidence_missing_identifiers": "Missing or uncertain identifiers: {fields}.",
    "confidence_image_quality_low": "The image quality does not support high visual confidence.",
    "confidence_visual_not_strong": "The preliminary AI reading did not reach the strong visual level.",
    "confidence_no_external_high_message": "Without external confirmation, the available visual evidence is still insufficient to classify the identity with high confidence.",
    "field_name_short": "name",
    "field_set_short": "set",
    "field_number_short": "number",
    "confidence_title": "### 🧭 CardCraftAI confidence level",
    "confidence_why": "🧩 Why was this level assigned?",
    "confidence_engine_note": "Confidence Engine 2.4.0 uses deterministic rules over existing evidence. It does not ask Gemini for a confidence percentage and does not invent statistical precision.",
    "indicator_not_informed": "⚪ Not provided by the AI",
    "indicator_compatible": "✅ Compatible",
    "indicator_divergent": "⚠️ Mismatch",
    "label_name": "Name",
    "label_set": "Collection / Set",
    "label_number": "Number",
    "validation_explainer": "🔎 How CardCraftAI validated this identification",
    "ai_identified": "**AI identified:** {name} • {set_name} • #{number}",
    "catalog_best_match": "**Best catalog match:** {name} • {set_name} • #{number}",
    "set_not_confirmed": "set not confirmed",
    "number_not_confirmed": "number not confirmed",
    "not_available": "not available",
    "set_not_available": "set not available",
    "number_not_available": "number not available",
    "validation_disclaimer": "Validation compares structured data. It does not physically authenticate the card and does not replace professional verification.",
    "data_origin_title": "### 🧾 Data origin and reliability",
    "confirmed_by_catalog": "✅ Confirmed by the Pokémon TCG catalog",
    "label_rarity": "Rarity",
    "label_artist": "Artist",
    "label_set_release": "Set release",
    "set_release_note": "The date above belongs to the set in the catalog. By itself, it does not confirm this card's specific release date.",
    "ai_visual_assessment": "🤖 AI visual assessment",
    "label_visible_year": "Visible / estimated year on the card",
    "label_variant": "Suggested variant",
    "label_apparent_language": "Apparent language",
    "ai_estimates_note": "Visible year, variant, apparent language, condition and visual authenticity remain AI estimates. The set release date does not confirm the specific year of this card.",
    "physical_assessment_note": "Condition and authenticity require physical evaluation when professional precision is needed.",
    "catalog_image_unavailable": "Image unavailable in the catalog.",
    "catalog_default_card_name": "Pokémon card",
    "catalog_gallery_no_match": "No visual match was found in the Pokémon catalog.",
    "catalog_gallery_instruction": "Click an image to open it larger. Use ‘Select this card’ to identify the correct match.",
    "select_this_card": "✅ Select this card",
    "selected_catalog_title": "✅ Card selected from the catalog",
    "click_image_larger": "Click the image to open a larger version.",
    "catalog_data_source": "Source of the data below: Pokémon TCG catalog.",
    "label_catalog_id": "Catalog ID",
    "tcgplayer_live_caption": "Direct external search on TCGplayer for listings available now. Offer prices may differ from the catalog market references.",
    "tcgplayer_live_button": "🛒 View current TCGplayer offers",
    "validation_only_pokemon": "Automatic catalog validation in this phase is available for Pokémon TCG cards.",
    "validation_name_missing": "⚪ The catalog could not be queried because the card name was not identified with enough confidence.",
    "validation_title": "🛡️ Catalog identification validation",
    "validation_caption": "CardCraftAI compares the photo identification with real Pokémon catalog cards. This validation and retry attempts are free.",
    "validation_saved_retry": "The AI identification remains saved. The button below queries only the catalog and does not run Gemini again.",
    "retry_validation_free": "🔄 Try catalog validation again — free",
    "validation_spinner": "Querying the Pokémon catalog to validate the identification...",
    "validation_preserved": "The AI identification was preserved. You can retry only the catalog validation whenever you want.",
    "validation_unusable": "⚪ Catalog validation does not yet have a usable result.",
    "user_selected_match_title": "✅ Match selected by the user for this analysis",
    "best_match_title": "🎯 Best match found in the catalog",
    "other_matches_title": "🖼️ Other matches for comparison",
    "catalog_temp_unavailable": "The Pokémon catalog is temporarily unavailable. The photo analysis was preserved and no new credit will be required to retry validation.",
    "catalog_http_caption": "The external service returned HTTP {status}. This does not change the identification already produced by the AI.",
    "catalog_rate_limited": "The Pokémon catalog temporarily limited new queries. The photo analysis remains saved and can be validated again without consuming another credit.",
    "catalog_generic_failure": "The analysis completed, but the visual catalog could not be queried right now. The AI identification remains available, but it has not yet been externally validated.",
    "search_performed_by": "Search performed for: {query}",
    "selected_for_analysis_title": "✅ Card selected for this analysis",
    "selection_registered": "The selection was saved. You can keep comparing other versions or use this card in the specialized analysis.",
    "analysis_uses_selected": "The analysis will use the catalog entry you selected.",
    "analysis_uses_typed": "Without a selected card, the analysis will use only the name and set you entered.",
})

UI_TEXT["Português (BR)"].update({
    "not_confirmed": "Não confirmado",
    "catalog_no_data_title": "Não foi possível validar no catálogo",
    "catalog_no_data_message": "A IA não conseguiu identificar um nome de carta com segurança suficiente para consultar o catálogo.",
    "catalog_no_result_title": "Não validado no catálogo",
    "catalog_no_result_message": "O catálogo não retornou uma correspondência utilizável para a identificação da foto.",
    "catalog_validated_title": "✅ Identificação validada pelo catálogo",
    "catalog_validated_message": "O número exato foi localizado e o nome e a coleção normalizados correspondem a uma carta real do catálogo Pokémon TCG.",
    "catalog_probable_title": "🟡 Identificação provavelmente correta",
    "catalog_probable_image_message": "O catálogo encontrou uma correspondência forte, mas a qualidade da imagem impede uma confirmação automática.",
    "catalog_probable_missing_message": "O catálogo encontrou uma correspondência forte, mas ainda falta confirmar pelo menos um identificador importante.",
    "catalog_inconclusive_title": "⚠️ Identificação ainda não confirmada",
    "catalog_inconclusive_number_message": "A IA informou um número de carta, mas nenhuma correspondência com esse número exato foi confirmada. Versões com número diferente são mostradas apenas para comparação e não são tratadas como a mesma carta.",
    "catalog_inconclusive_message": "O catálogo encontrou versões semelhantes, mas os dados extraídos da foto ainda não são suficientes para confirmar a carta exata.",
    "confidence_divergence_label": "⚠️ Divergência detectada",
    "confidence_divergence_message": "O número lido na carta diverge do candidato do catálogo. O CardCraftAI bloqueou qualquer promoção para confirmação ou alta confiança.",
    "confidence_ai_number": "Número lido pela IA: #{number}",
    "confidence_catalog_number": "Número do candidato do catálogo: #{number}",
    "confidence_number_priority": "Divergência de número tem prioridade sobre semelhanças de nome ou coleção.",
    "confidence_confirmed_label": "✅ Confirmado pelo catálogo",
    "confidence_confirmed_message": "A identidade principal da carta foi confirmada externamente por número exato, nome e coleção.",
    "confidence_exact_number": "Número exato localizado no catálogo Pokémon TCG.",
    "confidence_name_match": "Nome compatível com a correspondência do catálogo.",
    "confidence_set_match": "Coleção / set compatível com a correspondência do catálogo.",
    "confidence_partial_label": "🟡 Parcialmente confirmado",
    "confidence_partial_message": "O catálogo confirma parte relevante da identificação, mas ainda falta um identificador decisivo para confirmar a carta exata.",
    "confidence_exact_candidate": "Número exato compatível com um candidato do catálogo.",
    "confidence_name_strong": "Nome fortemente compatível com o catálogo.",
    "confidence_set_strong": "Coleção / set fortemente compatível com o catálogo.",
    "confidence_number_missing": "O número da carta não foi lido com segurança.",
    "confidence_number_not_exact": "O número ainda não possui confirmação exata.",
    "confidence_set_missing": "A coleção / set não foi lida com segurança.",
    "confidence_catalog_no_match": "O catálogo foi consultado, mas não confirmou uma correspondência utilizável.",
    "confidence_candidates_insufficient": "Há candidatos no catálogo, porém a correspondência ainda é insuficiente.",
    "confidence_no_external_evidence": "Não há evidência externa suficiente para confirmar a identidade.",
    "confidence_not_confirmed_label": "⚪ Não confirmado",
    "confidence_not_confirmed_message": "As evidências disponíveis ainda não sustentam uma confirmação segura da identidade da carta.",
    "confidence_high_visual_label": "🟢 Alta confiança visual",
    "confidence_high_visual_message": "A leitura visual é forte e contém nome, coleção e número, mas ainda não existe confirmação externa do catálogo para esta execução.",
    "confidence_fields_extracted": "Nome, coleção / set e número foram extraídos da imagem.",
    "confidence_visual_strong": "A leitura visual preliminar da IA foi classificada como forte.",
    "confidence_image_quality_ok": "A qualidade da imagem foi classificada como boa ou aceitável.",
    "confidence_not_catalog_confirmation": "Este nível não equivale a confirmação pelo catálogo.",
    "confidence_no_external": "Não há confirmação externa disponível para esta classificação.",
    "confidence_missing_identifiers": "Identificadores ausentes ou inseguros: {fields}.",
    "confidence_image_quality_low": "A qualidade da imagem não sustenta alta confiança visual.",
    "confidence_visual_not_strong": "A leitura preliminar da IA não atingiu o nível visual forte.",
    "confidence_no_external_high_message": "Sem confirmação externa, a evidência visual disponível ainda não é suficiente para classificar a identidade com alta confiança.",
    "field_name_short": "nome",
    "field_set_short": "coleção / set",
    "field_number_short": "número",
    "confidence_title": "### 🧭 Nível de confiança CardCraftAI",
    "confidence_why": "🧩 Por que este nível foi atribuído?",
    "confidence_engine_note": "O Confidence Engine 2.4.0 usa regras determinísticas sobre evidências existentes. Ele não pede ao Gemini uma porcentagem de confiança e não inventa precisão estatística.",
    "indicator_not_informed": "⚪ Não informado pela IA",
    "indicator_compatible": "✅ Compatível",
    "indicator_divergent": "⚠️ Divergente",
    "label_name": "Nome",
    "label_set": "Coleção / Set",
    "label_number": "Número",
    "validation_explainer": "🔎 Como o CardCraftAI validou esta identificação",
    "ai_identified": "**IA identificou:** {name} • {set_name} • #{number}",
    "catalog_best_match": "**Melhor correspondência do catálogo:** {name} • {set_name} • #{number}",
    "set_not_confirmed": "coleção não confirmada",
    "number_not_confirmed": "número não confirmado",
    "not_available": "não disponível",
    "set_not_available": "set não disponível",
    "number_not_available": "número não disponível",
    "validation_disclaimer": "A validação compara dados estruturados. Ela não autentica fisicamente a carta e não substitui verificação profissional.",
    "data_origin_title": "### 🧾 Origem e confiabilidade dos dados",
    "confirmed_by_catalog": "✅ Confirmado pelo catálogo Pokémon TCG",
    "label_rarity": "Raridade",
    "label_artist": "Artista",
    "label_set_release": "Lançamento do set",
    "set_release_note": "A data acima pertence ao set no catálogo. Ela não é, por si só, a data específica de lançamento desta carta.",
    "ai_visual_assessment": "🤖 Avaliação visual da IA",
    "label_visible_year": "Ano visível / estimado na carta",
    "label_variant": "Variante sugerida",
    "label_apparent_language": "Idioma aparente",
    "ai_estimates_note": "Ano visual, variante, idioma aparente, condição e autenticidade visual continuam sendo estimativas da IA. A data de lançamento do set não confirma o ano específico desta carta.",
    "physical_assessment_note": "Condição e autenticidade exigem avaliação física quando precisão profissional for necessária.",
    "catalog_image_unavailable": "Imagem não disponível no catálogo.",
    "catalog_default_card_name": "Carta Pokémon",
    "catalog_gallery_no_match": "Nenhuma correspondência visual foi encontrada no catálogo Pokémon.",
    "catalog_gallery_instruction": "Clique em uma imagem para ampliá-la. Use ‘Selecionar esta carta’ para indicar a correspondência correta.",
    "select_this_card": "✅ Selecionar esta carta",
    "selected_catalog_title": "✅ Carta selecionada no catálogo",
    "click_image_larger": "Clique na imagem para abrir a versão maior.",
    "catalog_data_source": "Fonte dos dados abaixo: catálogo Pokémon TCG.",
    "label_catalog_id": "ID do catálogo",
    "tcgplayer_live_caption": "Busca externa direta no TCGplayer para consultar anúncios disponíveis agora. Os valores dessas ofertas podem diferir das referências de mercado do catálogo.",
    "tcgplayer_live_button": "🛒 Ver ofertas atuais no TCGplayer",
    "validation_only_pokemon": "A validação automática por catálogo desta fase está disponível para cartas Pokémon TCG.",
    "validation_name_missing": "⚪ Não foi possível consultar o catálogo porque o nome da carta não foi identificado com segurança.",
    "validation_title": "🛡️ Validação da identificação por catálogo",
    "validation_caption": "O CardCraftAI compara a identificação da foto com cartas reais do catálogo Pokémon. Esta validação e as novas tentativas são gratuitas.",
    "validation_saved_retry": "A identificação feita pela IA continua salva. O botão abaixo consulta somente o catálogo e não executa o Gemini novamente.",
    "retry_validation_free": "🔄 Tentar validar novamente — grátis",
    "validation_spinner": "Consultando o catálogo Pokémon para validar a identificação...",
    "validation_preserved": "A identificação feita pela IA foi mantida. Você pode tentar somente a validação do catálogo novamente quando quiser.",
    "validation_unusable": "⚪ A validação do catálogo ainda não possui um resultado utilizável.",
    "user_selected_match_title": "✅ Correspondência escolhida pelo usuário para esta análise",
    "best_match_title": "🎯 Melhor correspondência encontrada no catálogo",
    "other_matches_title": "🖼️ Outras correspondências para comparação",
    "catalog_temp_unavailable": "O catálogo Pokémon está temporariamente indisponível. A análise da foto foi preservada e nenhum novo crédito será necessário para tentar a validação novamente.",
    "catalog_http_caption": "Serviço externo respondeu com HTTP {status}. Isso não altera a identificação já produzida pela IA.",
    "catalog_rate_limited": "O catálogo Pokémon limitou temporariamente novas consultas. A análise da foto continua salva e pode ser validada novamente sem consumir outro crédito.",
    "catalog_generic_failure": "A análise foi concluída, mas o catálogo visual não pôde ser consultado agora. A identificação da IA continua disponível, mas ainda não foi validada externamente.",
    "search_performed_by": "Busca realizada por: {query}",
    "selected_for_analysis_title": "✅ Carta escolhida para esta análise",
    "selection_registered": "A seleção foi registrada. Você pode continuar comparando outras versões ou usar esta carta na análise especializada.",
    "analysis_uses_selected": "A análise usará a entrada que você selecionou no catálogo.",
    "analysis_uses_typed": "Sem uma carta selecionada, a análise usará somente o nome e a coleção digitados.",
})

UI_TEXT["Español"].update({
    "not_confirmed": "No confirmado",
    "catalog_no_data_title": "No fue posible validar con el catálogo",
    "catalog_no_data_message": "La IA no identificó un nombre de carta con suficiente seguridad para consultar el catálogo.",
    "catalog_no_result_title": "No validado por el catálogo",
    "catalog_no_result_message": "El catálogo no devolvió una coincidencia utilizable para la identificación de la foto.",
    "catalog_validated_title": "✅ Identificación validada por el catálogo",
    "catalog_validated_message": "Se encontró el número exacto y el nombre y la colección normalizados coinciden con una carta real del catálogo Pokémon TCG.",
    "catalog_probable_title": "🟡 Identificación probablemente correcta",
    "catalog_probable_image_message": "El catálogo encontró una coincidencia fuerte, pero la calidad de la imagen impide la confirmación automática.",
    "catalog_probable_missing_message": "El catálogo encontró una coincidencia fuerte, pero todavía falta confirmar al menos un identificador importante.",
    "catalog_inconclusive_title": "⚠️ Identificación aún no confirmada",
    "catalog_inconclusive_number_message": "La IA indicó un número de carta, pero no se confirmó una coincidencia exacta con ese número. Las cartas con otros números se muestran solo para comparación.",
    "catalog_inconclusive_message": "El catálogo encontró versiones similares, pero los datos de la foto todavía no bastan para confirmar la carta exacta.",
    "confidence_divergence_label": "⚠️ Se detectó una divergencia",
    "confidence_divergence_message": "El número leído en la carta difiere del candidato del catálogo. CardCraftAI bloqueó la promoción a confirmada o alta confianza.",
    "confidence_ai_number": "Número leído por la IA: #{number}",
    "confidence_catalog_number": "Número del candidato del catálogo: #{number}",
    "confidence_number_priority": "Una divergencia de número tiene prioridad sobre la similitud de nombre o colección.",
    "confidence_confirmed_label": "✅ Confirmado por el catálogo",
    "confidence_confirmed_message": "La identidad principal de la carta fue confirmada externamente por número exacto, nombre y colección.",
    "confidence_exact_number": "Número exacto localizado en el catálogo Pokémon TCG.",
    "confidence_name_match": "El nombre coincide con el resultado del catálogo.",
    "confidence_set_match": "La colección coincide con el resultado del catálogo.",
    "confidence_partial_label": "🟡 Confirmado parcialmente",
    "confidence_partial_message": "El catálogo confirma una parte relevante de la identificación, pero aún falta un identificador decisivo para confirmar la carta exacta.",
    "confidence_exact_candidate": "El número exacto coincide con un candidato del catálogo.",
    "confidence_name_strong": "El nombre coincide fuertemente con el catálogo.",
    "confidence_set_strong": "La colección coincide fuertemente con el catálogo.",
    "confidence_number_missing": "El número de carta no se leyó con suficiente seguridad.",
    "confidence_number_not_exact": "El número aún no tiene confirmación exacta.",
    "confidence_set_missing": "La colección no se leyó con suficiente seguridad.",
    "confidence_catalog_no_match": "Se consultó el catálogo, pero no confirmó una coincidencia utilizable.",
    "confidence_candidates_insufficient": "Hay candidatos en el catálogo, pero la coincidencia sigue siendo insuficiente.",
    "confidence_no_external_evidence": "No hay evidencia externa suficiente para confirmar la identidad.",
    "confidence_not_confirmed_label": "⚪ No confirmado",
    "confidence_not_confirmed_message": "La evidencia disponible todavía no permite una confirmación segura de la identidad.",
    "confidence_high_visual_label": "🟢 Alta confianza visual",
    "confidence_high_visual_message": "La lectura visual es fuerte e incluye nombre, colección y número, pero todavía no hay confirmación externa del catálogo.",
    "confidence_fields_extracted": "Nombre, colección y número fueron extraídos de la imagen.",
    "confidence_visual_strong": "La lectura visual preliminar de la IA fue clasificada como fuerte.",
    "confidence_image_quality_ok": "La calidad de la imagen fue clasificada como buena o aceptable.",
    "confidence_not_catalog_confirmation": "Este nivel no equivale a una confirmación del catálogo.",
    "confidence_no_external": "No hay confirmación externa disponible para esta clasificación.",
    "confidence_missing_identifiers": "Identificadores ausentes o inseguros: {fields}.",
    "confidence_image_quality_low": "La calidad de la imagen no permite alta confianza visual.",
    "confidence_visual_not_strong": "La lectura preliminar de la IA no alcanzó el nivel visual fuerte.",
    "confidence_no_external_high_message": "Sin confirmación externa, la evidencia visual disponible todavía no basta para clasificar la identidad con alta confianza.",
    "field_name_short": "nombre",
    "field_set_short": "colección / set",
    "field_number_short": "número",
    "confidence_title": "### 🧭 Nivel de confianza CardCraftAI",
    "confidence_why": "🧩 ¿Por qué se asignó este nivel?",
    "confidence_engine_note": "Confidence Engine 2.4.0 usa reglas deterministas sobre la evidencia existente. No pide a Gemini un porcentaje de confianza ni inventa precisión estadística.",
    "indicator_not_informed": "⚪ No informado por la IA",
    "indicator_compatible": "✅ Compatible",
    "indicator_divergent": "⚠️ Divergente",
    "label_name": "Nombre",
    "label_set": "Colección / Set",
    "label_number": "Número",
    "validation_explainer": "🔎 Cómo validó CardCraftAI esta identificación",
    "ai_identified": "**La IA identificó:** {name} • {set_name} • #{number}",
    "catalog_best_match": "**Mejor coincidencia del catálogo:** {name} • {set_name} • #{number}",
    "set_not_confirmed": "colección no confirmada",
    "number_not_confirmed": "número no confirmado",
    "not_available": "no disponible",
    "set_not_available": "set no disponible",
    "number_not_available": "número no disponible",
    "validation_disclaimer": "La validación compara datos estructurados. No autentica físicamente la carta ni sustituye una verificación profesional.",
    "data_origin_title": "### 🧾 Origen y fiabilidad de los datos",
    "confirmed_by_catalog": "✅ Confirmado por el catálogo Pokémon TCG",
    "label_rarity": "Rareza",
    "label_artist": "Artista",
    "label_set_release": "Lanzamiento del set",
    "set_release_note": "La fecha anterior pertenece al set del catálogo y no confirma por sí sola la fecha específica de lanzamiento de esta carta.",
    "ai_visual_assessment": "🤖 Evaluación visual de la IA",
    "label_visible_year": "Año visible / estimado en la carta",
    "label_variant": "Variante sugerida",
    "label_apparent_language": "Idioma aparente",
    "ai_estimates_note": "El año visible, la variante, el idioma aparente, la condición y la autenticidad visual siguen siendo estimaciones de la IA.",
    "physical_assessment_note": "La condición y la autenticidad requieren evaluación física cuando se necesita precisión profesional.",
    "catalog_image_unavailable": "Imagen no disponible en el catálogo.",
    "catalog_default_card_name": "Carta Pokémon",
    "catalog_gallery_no_match": "No se encontró ninguna coincidencia visual en el catálogo Pokémon.",
    "catalog_gallery_instruction": "Haz clic en una imagen para ampliarla. Usa ‘Seleccionar esta carta’ para indicar la coincidencia correcta.",
    "select_this_card": "✅ Seleccionar esta carta",
    "selected_catalog_title": "✅ Carta seleccionada del catálogo",
    "click_image_larger": "Haz clic en la imagen para abrir una versión más grande.",
    "catalog_data_source": "Fuente de los datos siguientes: catálogo Pokémon TCG.",
    "label_catalog_id": "ID del catálogo",
    "tcgplayer_live_caption": "Búsqueda externa directa en TCGplayer para consultar anuncios disponibles ahora. Los precios pueden diferir de las referencias del catálogo.",
    "tcgplayer_live_button": "🛒 Ver ofertas actuales en TCGplayer",
    "validation_only_pokemon": "La validación automática por catálogo de esta fase está disponible para cartas Pokémon TCG.",
    "validation_name_missing": "⚪ No fue posible consultar el catálogo porque el nombre de la carta no se identificó con suficiente seguridad.",
    "validation_title": "🛡️ Validación de identificación por catálogo",
    "validation_caption": "CardCraftAI compara la identificación de la foto con cartas reales del catálogo Pokémon. Esta validación y los reintentos son gratuitos.",
    "validation_saved_retry": "La identificación de la IA permanece guardada. El botón siguiente consulta solo el catálogo y no ejecuta Gemini otra vez.",
    "retry_validation_free": "🔄 Intentar validar de nuevo — gratis",
    "validation_spinner": "Consultando el catálogo Pokémon para validar la identificación...",
    "validation_preserved": "La identificación de la IA fue preservada. Puedes volver a intentar únicamente la validación del catálogo cuando quieras.",
    "validation_unusable": "⚪ La validación del catálogo todavía no tiene un resultado utilizable.",
    "user_selected_match_title": "✅ Coincidencia elegida por el usuario para este análisis",
    "best_match_title": "🎯 Mejor coincidencia encontrada en el catálogo",
    "other_matches_title": "🖼️ Otras coincidencias para comparar",
    "catalog_temp_unavailable": "El catálogo Pokémon está temporalmente no disponible. El análisis de la foto se preservó y no se requerirá otro crédito para reintentar la validación.",
    "catalog_http_caption": "El servicio externo respondió con HTTP {status}. Esto no cambia la identificación ya producida por la IA.",
    "catalog_rate_limited": "El catálogo Pokémon limitó temporalmente nuevas consultas. El análisis de la foto permanece guardado y puede validarse de nuevo sin consumir otro crédito.",
    "catalog_generic_failure": "El análisis se completó, pero el catálogo visual no pudo consultarse ahora. La identificación de la IA sigue disponible, pero todavía no fue validada externamente.",
    "search_performed_by": "Búsqueda realizada por: {query}",
    "selected_for_analysis_title": "✅ Carta elegida para este análisis",
    "selection_registered": "La selección se guardó. Puedes seguir comparando otras versiones o usar esta carta en el análisis especializado.",
    "analysis_uses_selected": "El análisis usará la entrada del catálogo que seleccionaste.",
    "analysis_uses_typed": "Sin una carta seleccionada, el análisis usará solo el nombre y la colección introducidos.",
})

UI_TEXT["日本語"].update({
    "not_confirmed": "未確認",
    "catalog_no_data_title": "カタログで検証できませんでした",
    "catalog_no_data_message": "AI がカタログ検索に十分な確度でカード名を特定できませんでした。",
    "catalog_no_result_title": "カタログ未検証",
    "catalog_no_result_message": "写真の識別結果に対して、カタログから利用可能な一致候補が返されませんでした。",
    "catalog_validated_title": "✅ カタログで識別を確認しました",
    "catalog_validated_message": "正確な番号が見つかり、正規化された名前とセットが Pokémon TCG カタログの実在カードと一致しました。",
    "catalog_probable_title": "🟡 識別はおそらく正しいです",
    "catalog_probable_image_message": "カタログで強い一致が見つかりましたが、画像品質のため自動確認できません。",
    "catalog_probable_missing_message": "カタログで強い一致が見つかりましたが、重要な識別子が少なくとも1つ未確認です。",
    "catalog_inconclusive_title": "⚠️ 識別はまだ確認されていません",
    "catalog_inconclusive_number_message": "AI はカード番号を読み取りましたが、その番号との完全一致は確認できませんでした。番号が異なるカードは比較用にのみ表示されます。",
    "catalog_inconclusive_message": "類似カードは見つかりましたが、写真の情報だけでは正確なカードを確認できません。",
    "confidence_divergence_label": "⚠️ 不一致を検出しました",
    "confidence_divergence_message": "画像から読み取った番号とカタログ候補の番号が一致しないため、CardCraftAI は確認済み／高信頼への昇格を停止しました。",
    "confidence_ai_number": "AI が読み取った番号: #{number}",
    "confidence_catalog_number": "カタログ候補の番号: #{number}",
    "confidence_number_priority": "番号の不一致は、名前やセットの類似より優先されます。",
    "confidence_confirmed_label": "✅ カタログ確認済み",
    "confidence_confirmed_message": "カードの主要な識別情報は、正確な番号・名前・セットによって外部確認されました。",
    "confidence_exact_number": "Pokémon TCG カタログで正確な番号が見つかりました。",
    "confidence_name_match": "名前がカタログ結果と一致します。",
    "confidence_set_match": "セットがカタログ結果と一致します。",
    "confidence_partial_label": "🟡 一部確認済み",
    "confidence_partial_message": "カタログは識別情報の重要な部分を確認しましたが、正確なカード確認には決定的な識別子がまだ不足しています。",
    "confidence_exact_candidate": "正確な番号がカタログ候補と一致します。",
    "confidence_name_strong": "名前がカタログと強く一致します。",
    "confidence_set_strong": "セットがカタログと強く一致します。",
    "confidence_number_missing": "カード番号を十分な確度で読み取れませんでした。",
    "confidence_number_not_exact": "カード番号はまだ完全一致で確認されていません。",
    "confidence_set_missing": "セットを十分な確度で読み取れませんでした。",
    "confidence_catalog_no_match": "カタログを照会しましたが、利用可能な一致は確認できませんでした。",
    "confidence_candidates_insufficient": "カタログ候補はありますが、一致度がまだ不十分です。",
    "confidence_no_external_evidence": "識別を確認するための外部証拠が不足しています。",
    "confidence_not_confirmed_label": "⚪ 未確認",
    "confidence_not_confirmed_message": "利用可能な証拠だけでは、安全に識別を確認するにはまだ不十分です。",
    "confidence_high_visual_label": "🟢 高い視覚的信頼度",
    "confidence_high_visual_message": "視覚的な読み取りは強く、名前・セット・番号がありますが、この実行ではまだカタログによる外部確認がありません。",
    "confidence_fields_extracted": "画像から名前、セット、番号を抽出しました。",
    "confidence_visual_strong": "AI の予備的な視覚読み取りは強いと分類されました。",
    "confidence_image_quality_ok": "画像品質は良好または許容範囲と分類されました。",
    "confidence_not_catalog_confirmation": "このレベルはカタログ確認と同等ではありません。",
    "confidence_no_external": "この分類には外部確認がありません。",
    "confidence_missing_identifiers": "不足または不確かな識別子: {fields}。",
    "confidence_image_quality_low": "画像品質は高い視覚的信頼度を支えるには不十分です。",
    "confidence_visual_not_strong": "AI の予備的な読み取りは強い視覚レベルに達していません。",
    "confidence_no_external_high_message": "外部確認がないため、利用可能な視覚証拠だけでは高信頼で識別するには不十分です。",
    "field_name_short": "名前",
    "field_set_short": "セット",
    "field_number_short": "番号",
    "confidence_title": "### 🧭 CardCraftAI 信頼レベル",
    "confidence_why": "🧩 このレベルになった理由",
    "confidence_engine_note": "Confidence Engine 2.4.0 は既存の証拠に対する決定論的ルールを使用します。Gemini に信頼度の割合を求めず、統計的精度を作りません。",
    "indicator_not_informed": "⚪ AI 未入力",
    "indicator_compatible": "✅ 一致",
    "indicator_divergent": "⚠️ 不一致",
    "label_name": "名前",
    "label_set": "コレクション / セット",
    "label_number": "番号",
    "validation_explainer": "🔎 CardCraftAI の検証方法",
    "ai_identified": "**AI の識別:** {name} • {set_name} • #{number}",
    "catalog_best_match": "**カタログの最良一致:** {name} • {set_name} • #{number}",
    "set_not_confirmed": "セット未確認",
    "number_not_confirmed": "番号未確認",
    "not_available": "利用不可",
    "set_not_available": "セット利用不可",
    "number_not_available": "番号利用不可",
    "validation_disclaimer": "この検証は構造化データを比較するもので、カードを物理的に鑑定するものではなく、専門家の確認に代わるものではありません。",
    "data_origin_title": "### 🧾 データの出所と信頼性",
    "confirmed_by_catalog": "✅ Pokémon TCG カタログで確認済み",
    "label_rarity": "レアリティ",
    "label_artist": "イラストレーター",
    "label_set_release": "セット発売日",
    "set_release_note": "上の日付はカタログ上のセット発売日で、このカード固有の発売日を単独で確認するものではありません。",
    "ai_visual_assessment": "🤖 AI 視覚評価",
    "label_visible_year": "カードに見える／推定年",
    "label_variant": "推定バリエーション",
    "label_apparent_language": "見た目の言語",
    "ai_estimates_note": "見える年、バリエーション、言語、状態、視覚的真正性は引き続き AI の推定です。",
    "physical_assessment_note": "専門的な精度が必要な場合、状態と真正性は実物評価が必要です。",
    "catalog_image_unavailable": "カタログ画像を利用できません。",
    "catalog_default_card_name": "Pokémon カード",
    "catalog_gallery_no_match": "Pokémon カタログで視覚的な一致が見つかりませんでした。",
    "catalog_gallery_instruction": "画像をクリックすると拡大できます。正しい候補を指定するには「このカードを選択」を使用してください。",
    "select_this_card": "✅ このカードを選択",
    "selected_catalog_title": "✅ カタログからカードを選択しました",
    "click_image_larger": "画像をクリックすると大きい画像を開きます。",
    "catalog_data_source": "以下のデータの出典: Pokémon TCG カタログ。",
    "label_catalog_id": "カタログ ID",
    "tcgplayer_live_caption": "現在出品中の商品を確認するため TCGplayer を直接検索します。出品価格はカタログの市場参考値と異なる場合があります。",
    "tcgplayer_live_button": "🛒 TCGplayer の現在の出品を見る",
    "validation_only_pokemon": "この段階の自動カタログ検証は Pokémon TCG カードで利用できます。",
    "validation_name_missing": "⚪ カード名を十分な確度で特定できなかったため、カタログを照会できませんでした。",
    "validation_title": "🛡️ カタログによる識別検証",
    "validation_caption": "CardCraftAI は写真の識別結果を Pokémon カタログの実在カードと比較します。この検証と再試行は無料です。",
    "validation_saved_retry": "AI の識別結果は保存されています。下のボタンはカタログだけを照会し、Gemini を再実行しません。",
    "retry_validation_free": "🔄 カタログ検証を再試行 — 無料",
    "validation_spinner": "識別を検証するため Pokémon カタログを照会しています...",
    "validation_preserved": "AI の識別結果は保持されています。いつでもカタログ検証だけを再試行できます。",
    "validation_unusable": "⚪ カタログ検証にはまだ利用可能な結果がありません。",
    "user_selected_match_title": "✅ この分析用にユーザーが選択した一致候補",
    "best_match_title": "🎯 カタログで見つかった最良一致",
    "other_matches_title": "🖼️ 比較用のその他の候補",
    "catalog_temp_unavailable": "Pokémon カタログは一時的に利用できません。写真分析は保持されており、検証の再試行に追加クレジットは不要です。",
    "catalog_http_caption": "外部サービスが HTTP {status} を返しました。AI が既に生成した識別結果には影響しません。",
    "catalog_rate_limited": "Pokémon カタログが一時的に新規照会を制限しました。写真分析は保存され、追加クレジットなしで再検証できます。",
    "catalog_generic_failure": "分析は完了しましたが、現在ビジュアルカタログを照会できません。AI の識別結果は利用できますが、外部検証はまだ完了していません。",
    "search_performed_by": "検索条件: {query}",
    "selected_for_analysis_title": "✅ この分析用にカードを選択しました",
    "selection_registered": "選択を保存しました。他の版を比較するか、このカードを専門分析に使用できます。",
    "analysis_uses_selected": "分析では、選択したカタログ項目を使用します。",
    "analysis_uses_typed": "カードを選択しない場合、入力した名前とセットだけを分析に使用します。",
})


def idioma_interface_atual():
    if "idioma_interface" not in st.session_state:
        st.session_state.idioma_interface = "English"
    if st.session_state.idioma_interface not in LANGUAGE_OPTIONS:
        st.session_state.idioma_interface = "English"
    return st.session_state.idioma_interface


def t(chave, idioma=None, **kwargs):
    idioma = idioma or idioma_interface_atual()
    tabela = UI_TEXT.get(idioma, UI_TEXT["English"])
    texto = tabela.get(chave, UI_TEXT["English"].get(chave, chave))
    if kwargs:
        try:
            return texto.format(**kwargs)
        except Exception:
            return texto
    return texto


# Widgets usam chaves próprias; idioma_interface é o estado persistente.
# Isso evita que o idioma se perca ao trocar login <-> app autenticado.
LANGUAGE_WIDGET_KEYS = (
    "idioma_login_widget",
    "idioma_sidebar_widget",
    "idioma_recovery_widget",
    "idioma_legal_widget",
)

NAVIGATION_OPTIONS = [
    "photo",
    "search",
    "plans",
    "account",
    "terms",
    "privacy",
]


def _sincronizar_idioma_widget(widget_key):
    selecionado = st.session_state.get(widget_key)
    if selecionado not in LANGUAGE_OPTIONS:
        return

    st.session_state.idioma_interface = selecionado

    # Mantém os seletores das outras telas prontos com a mesma escolha.
    for outra_chave in LANGUAGE_WIDGET_KEYS:
        if outra_chave != widget_key:
            st.session_state[outra_chave] = selecionado


def renderizar_seletor_idioma(container, widget_key):
    idioma_atual = idioma_interface_atual()

    # Antes de criar o widget, sincroniza sua chave com o estado persistente.
    if st.session_state.get(widget_key) != idioma_atual:
        st.session_state[widget_key] = idioma_atual

    container.selectbox(
        t("language", idioma_atual),
        LANGUAGE_OPTIONS,
        key=widget_key,
        on_change=_sincronizar_idioma_widget,
        args=(widget_key,),
    )

    return idioma_interface_atual()


def pagina_interface_atual():
    pagina = st.session_state.get("pagina_interface", "photo")
    if pagina not in NAVIGATION_OPTIONS:
        pagina = "photo"
        st.session_state.pagina_interface = pagina
    return pagina


def _sincronizar_pagina_widget():
    pagina = st.session_state.get("pagina_navegacao_widget")
    if pagina in NAVIGATION_OPTIONS:
        st.session_state.pagina_interface = pagina


def traduzir_plano_ui(plano, idioma=None):
    idioma = idioma or idioma_interface_atual()
    valor = str(plano or "free").strip()
    if valor.lower() == "free":
        return t("plan_free", idioma)
    return valor

# O catálogo visual é um recurso adicional. Se a chave estiver ausente,
# login, créditos e análise por IA continuam funcionando.
POKEMON_TCG_API_KEY = st.secrets.get(
    "POKEMON_TCG_API_KEY",
    "",
)
POKEMON_TCG_API_URL = "https://api.pokemontcg.io/v2/cards"


# ============================================================
# RELIABILITY 1.0 - CONTRATO ESTRUTURADO DA IA
# ============================================================

ANALISE_CARTA_SCHEMA = {
    "type": "object",
    "properties": {
        "status_identificacao": {
            "type": "string",
            "enum": ["confirmada", "provavel", "incerta"],
            "description": (
                "Grau preliminar de identificacao segundo o modelo. "
                "Nao representa validacao por catalogo externo."
            ),
        },
        "jogo": {"type": ["string", "null"]},
        "nome_carta": {"type": ["string", "null"]},
        "colecao_set": {"type": ["string", "null"]},
        "numero_carta": {"type": ["string", "null"]},
        "raridade": {"type": ["string", "null"]},
        "variante": {"type": ["string", "null"]},
        "idioma_carta": {"type": ["string", "null"]},
        "ano": {"type": ["integer", "null"]},
        "qualidade_imagem": {
            "type": "string",
            "enum": ["boa", "aceitavel", "ruim", "nao_aplicavel"],
        },
        "motivo_qualidade_imagem": {"type": ["string", "null"]},
        "evidencias_visuais": {
            "type": "array",
            "items": {"type": "string"},
        },
        "campos_incertos": {
            "type": "array",
            "items": {"type": "string"},
        },
        "informacoes_gerais": {
            "type": "array",
            "items": {"type": "string"},
        },
        "condicao_aparente": {
            "type": "object",
            "properties": {
                "estimativa": {
                    "type": "string",
                    "enum": [
                        "Near Mint",
                        "Lightly Played",
                        "Moderately Played",
                        "Heavily Played",
                        "indeterminada",
                        "nao_aplicavel",
                    ],
                },
                "observacoes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["estimativa", "observacoes"],
        },
        "autenticidade_visual": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": [
                        "sem_sinais_obvios",
                        "requer_verificacao",
                        "indeterminada",
                        "nao_aplicavel",
                    ],
                },
                "observacoes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["status", "observacoes"],
        },
        "conservacao": {
            "type": "array",
            "items": {"type": "string"},
        },
        "anuncio_venda": {"type": ["string", "null"]},
        "mercado": {
            "type": "object",
            "properties": {
                "dados_atualizados_disponiveis": {"type": "boolean"},
                "observacao": {"type": "string"},
            },
            "required": ["dados_atualizados_disponiveis", "observacao"],
        },
    },
    "required": [
        "status_identificacao",
        "jogo",
        "nome_carta",
        "colecao_set",
        "numero_carta",
        "raridade",
        "variante",
        "idioma_carta",
        "ano",
        "qualidade_imagem",
        "motivo_qualidade_imagem",
        "evidencias_visuais",
        "campos_incertos",
        "informacoes_gerais",
        "condicao_aparente",
        "autenticidade_visual",
        "conservacao",
        "anuncio_venda",
        "mercado",
    ],
}


def validar_analise_estruturada(dados):
    if not isinstance(dados, dict):
        raise RuntimeError("A IA nao retornou um objeto JSON valido.")

    obrigatorios = ANALISE_CARTA_SCHEMA["required"]
    ausentes = [campo for campo in obrigatorios if campo not in dados]
    if ausentes:
        raise RuntimeError(
            "A resposta estruturada veio incompleta. "
            f"Campos ausentes: {', '.join(ausentes)}"
        )

    status_validos = {"confirmada", "provavel", "incerta"}
    if dados.get("status_identificacao") not in status_validos:
        raise RuntimeError("Status de identificacao invalido.")

    qualidade_valida = {"boa", "aceitavel", "ruim", "nao_aplicavel"}
    if dados.get("qualidade_imagem") not in qualidade_valida:
        raise RuntimeError("Classificacao de qualidade da imagem invalida.")

    for campo_lista in [
        "evidencias_visuais",
        "campos_incertos",
        "informacoes_gerais",
        "conservacao",
    ]:
        if not isinstance(dados.get(campo_lista), list):
            raise RuntimeError(f"Campo {campo_lista} deveria ser uma lista.")

    for bloco in ["condicao_aparente", "autenticidade_visual", "mercado"]:
        if not isinstance(dados.get(bloco), dict):
            raise RuntimeError(f"Bloco {bloco} veio em formato invalido.")

    # Nesta versao a pesquisa de mercado permanece desativada.
    dados["mercado"]["dados_atualizados_disponiveis"] = False

    return dados


def texto_ou_nao_confirmado(valor, idioma=None):
    if valor is None:
        return t("not_confirmed", idioma)
    texto = str(valor).strip()
    return texto if texto else t("not_confirmed", idioma)

def formatar_resultado_estruturado(dados, tipo_resultado=None):
    status = dados.get("status_identificacao", "incerta")
    analise_por_nome = str(tipo_resultado or "").strip().lower() == "nome"
    rotulos_status = {
        "confirmada": "🟢 Identificacao preliminar forte",
        "provavel": "🟡 Identificacao provavel",
        "incerta": "🔴 Identificacao incerta",
    }

    qualidade = dados.get("qualidade_imagem", "nao_aplicavel")
    rotulos_qualidade = {
        "boa": "Boa",
        "aceitavel": "Aceitavel",
        "ruim": "Ruim",
        "nao_aplicavel": "Nao aplicavel",
    }

    if analise_por_nome:
        linhas = [
            "## 🃏 Identificacao estruturada da IA",
            f"**Status da analise:** {rotulos_status.get(status, '🔴 Identificacao incerta')}",
            "",
            (
                "Os dados abaixo foram processados pela IA a partir da entrada textual "
                "e, quando uma carta foi selecionada, dos dados do catalogo Pokemon TCG. "
                "Nao houve analise de imagem neste fluxo."
            ),
            "",
            f"- **Jogo:** {texto_ou_nao_confirmado(dados.get('jogo'))}",
            f"- **Nome analisado:** {texto_ou_nao_confirmado(dados.get('nome_carta'))}",
            f"- **Colecao / Set analisada:** {texto_ou_nao_confirmado(dados.get('colecao_set'))}",
            f"- **Numero analisado:** {texto_ou_nao_confirmado(dados.get('numero_carta'))}",
            "",
            "### 🤖 Dados ainda dependentes de interpretacao da IA",
            f"- **Raridade sugerida:** {texto_ou_nao_confirmado(dados.get('raridade'))}",
            f"- **Variante sugerida:** {texto_ou_nao_confirmado(dados.get('variante'))}",
            f"- **Idioma aparente:** {texto_ou_nao_confirmado(dados.get('idioma_carta'))}",
            f"- **Ano lido / estimado:** {texto_ou_nao_confirmado(dados.get('ano'))}",
            "",
            "### 🧾 Qualidade da entrada",
            "**Entrada:** Dados textuais / catalogo",
        ]
    else:
        linhas = [
            "## 🃏 Identificacao preliminar da IA",
            f"**Status da leitura visual:** {rotulos_status.get(status, '🔴 Identificacao incerta')}",
            "",
            (
                "Os dados abaixo foram extraidos da imagem pela IA. "
                "Nome, colecao e numero serao comparados com o catalogo "
                "Pokemon quando ele estiver disponivel."
            ),
            "",
            f"- **Jogo:** {texto_ou_nao_confirmado(dados.get('jogo'))}",
            f"- **Nome lido:** {texto_ou_nao_confirmado(dados.get('nome_carta'))}",
            f"- **Colecao / Set lido:** {texto_ou_nao_confirmado(dados.get('colecao_set'))}",
            f"- **Numero lido:** {texto_ou_nao_confirmado(dados.get('numero_carta'))}",
            "",
            "### 🤖 Dados ainda dependentes de interpretacao da IA",
            f"- **Raridade sugerida:** {texto_ou_nao_confirmado(dados.get('raridade'))}",
            f"- **Variante sugerida:** {texto_ou_nao_confirmado(dados.get('variante'))}",
            f"- **Idioma aparente:** {texto_ou_nao_confirmado(dados.get('idioma_carta'))}",
            f"- **Ano lido / estimado:** {texto_ou_nao_confirmado(dados.get('ano'))}",
            "",
            "### 📸 Qualidade da entrada",
            f"**Imagem:** {rotulos_qualidade.get(qualidade, 'Nao aplicavel')}",
        ]

    motivo = dados.get("motivo_qualidade_imagem")
    if motivo:
        linhas.append(f"\n{motivo}")

    evidencias = dados.get("evidencias_visuais") or []
    if evidencias:
        linhas.extend(["", "### 🔎 Evidencias usadas"])
        linhas.extend([f"- {item}" for item in evidencias])

    incertos = dados.get("campos_incertos") or []
    if incertos:
        linhas.extend(["", "### ⚠️ Dados que precisam de confirmacao"])
        linhas.extend([f"- {item}" for item in incertos])

    gerais = dados.get("informacoes_gerais") or []
    if gerais:
        linhas.extend(["", "## 📊 Informacoes gerais"])
        linhas.extend([f"- {item}" for item in gerais])

    condicao = dados.get("condicao_aparente") or {}
    if analise_por_nome:
        linhas.extend([
            "",
            "## 🔎 Condicao aparente — nao avaliada sem foto",
            f"**Estimativa:** {condicao.get('estimativa', 'nao_aplicavel')}",
        ])
    else:
        linhas.extend([
            "",
            "## 🔎 Condicao aparente — estimativa visual da IA",
            f"**Estimativa visual:** {condicao.get('estimativa', 'indeterminada')}",
        ])
    for item in condicao.get("observacoes") or []:
        linhas.append(f"- {item}")

    autenticidade = dados.get("autenticidade_visual") or {}
    rotulos_autenticidade = {
        "sem_sinais_obvios": "Sem sinais obvios na imagem, mas nao certificada",
        "requer_verificacao": "Ha sinais que merecem verificacao adicional",
        "indeterminada": "Nao foi possivel avaliar pela imagem",
        "nao_aplicavel": "Nao aplicavel",
    }
    if analise_por_nome:
        linhas.extend([
            "",
            "## ⚠️ Autenticidade visual — nao avaliada sem foto",
            f"**Status:** {rotulos_autenticidade.get(autenticidade.get('status'), 'Nao aplicavel')}",
        ])
    else:
        linhas.extend([
            "",
            "## ⚠️ Autenticidade visual — triagem da IA",
            f"**Status:** {rotulos_autenticidade.get(autenticidade.get('status'), 'Indeterminada')}",
        ])
    for item in autenticidade.get("observacoes") or []:
        linhas.append(f"- {item}")
    linhas.append(
        "\nEsta avaliacao visual nao substitui autenticacao profissional presencial."
    )

    linhas.extend([
        "",
        "## 💰 Mercado",
        "A IA nao inventa valores de mercado. Quando o catalogo Pokemon estiver disponivel, "
        "as referencias de mercado e a atualidade da fonte aparecem na validacao abaixo.",
    ])

    conservacao = dados.get("conservacao") or []
    if conservacao:
        linhas.extend(["", "## 🛡️ Conservacao"])
        linhas.extend([f"- {item}" for item in conservacao])

    anuncio = dados.get("anuncio_venda")
    if anuncio:
        linhas.extend(["", "## 📝 Base para anuncio", anuncio])

    linhas.extend([
        "",
        "---",
        "*A leitura da IA e preliminar. Quando o catalogo Pokemon estiver disponivel, "
        "a validacao externa aparece logo abaixo sem consumir outro credito. "
        "Somente os campos explicitamente marcados como confirmados pelo catalogo "
        "devem ser tratados como validados externamente.*",
    ])

    return "\n".join(linhas)



# ============================================================
# RELIABILITY 2.1 - CATALOGO VISUAL POKEMON
# ============================================================

def _normalizar_texto_catalogo(valor):
    if valor is None:
        return ""

    texto = unicodedata.normalize(
        "NFKD",
        str(valor),
    )
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    texto = texto.lower().strip()

    return " ".join(
        parte
        for parte in texto.replace("-", " ").split()
        if parte
    )


def _normalizar_colecao_catalogo(valor):
    """Normaliza nomes equivalentes de coleções sem esconder divergências reais."""
    texto = _normalizar_texto_catalogo(valor)
    texto = texto.replace("&", " and " )
    texto = " ".join(texto.split())

    aliases = {
        "sun and moon black star promos": "sm black star promos",
        "sun moon black star promos": "sm black star promos",
        "sword and shield black star promos": "swsh black star promos",
        "sword shield black star promos": "swsh black star promos",
        "scarlet and violet black star promos": "sv black star promos",
        "scarlet violet black star promos": "sv black star promos",
    }

    return aliases.get(texto, texto)


def _normalizar_numero_catalogo(valor):
    """Normaliza o identificador impresso da carta para comparação."""
    texto = str(valor or "").strip().lower()
    texto = texto.lstrip("#").strip()
    return "".join(
        caractere
        for caractere in texto
        if caractere.isalnum() or caractere == "/"
    )


def _numero_principal_catalogo(valor):
    """
    Retorna a parte principal do número impresso.

    Ex.: "#SM211" -> "sm211" e "SM211/248" -> "sm211".
    O denominador só é ignorado quando um dos lados não o fornece.
    """
    normalizado = _normalizar_numero_catalogo(valor)
    if not normalizado:
        return ""
    return normalizado.split("/", 1)[0]


def _numeros_catalogo_equivalentes(a, b):
    """Compara números sem transformar denominadores conflitantes em iguais."""
    a_norm = _normalizar_numero_catalogo(a)
    b_norm = _normalizar_numero_catalogo(b)

    if not a_norm or not b_norm:
        return False

    if a_norm == b_norm:
        return True

    a_tem_denominador = "/" in a_norm
    b_tem_denominador = "/" in b_norm

    # A API frequentemente guarda apenas o número principal, enquanto uma
    # leitura visual pode incluir o denominador impresso. Nesse caso, aceitamos
    # a parte principal. Se ambos trazem denominador e eles divergem, não aceitamos.
    if a_tem_denominador != b_tem_denominador:
        return (
            _numero_principal_catalogo(a_norm)
            == _numero_principal_catalogo(b_norm)
        )

    return False

def _similaridade_catalogo(a, b):
    a_norm = _normalizar_texto_catalogo(a)
    b_norm = _normalizar_texto_catalogo(b)

    if not a_norm or not b_norm:
        return 0.0

    if a_norm == b_norm:
        return 1.0

    if a_norm in b_norm or b_norm in a_norm:
        return 0.92

    return SequenceMatcher(
        None,
        a_norm,
        b_norm,
    ).ratio()


def _similaridade_colecao_catalogo(a, b):
    a_norm = _normalizar_colecao_catalogo(a)
    b_norm = _normalizar_colecao_catalogo(b)

    if not a_norm or not b_norm:
        return 0.0

    if a_norm == b_norm:
        return 1.0

    if a_norm in b_norm or b_norm in a_norm:
        return 0.92

    return SequenceMatcher(
        None,
        a_norm,
        b_norm,
    ).ratio()


def _frase_lucene_segura(valor):
    texto = str(valor or "").strip()
    texto = texto.replace("\\", "\\\\")
    texto = texto.replace('"', '\\"')
    return texto


def _token_fallback_catalogo(nome):
    partes = [
        parte
        for parte in _normalizar_texto_catalogo(nome).split()
        if len(parte) >= 3
    ]

    if not partes:
        return ""

    # Preferimos a palavra mais informativa do nome.
    return max(
        partes,
        key=len,
    )


def _executar_requisicao_catalogo(
    params,
    tentativas=2,
):
    """
    Executa uma consulta curta e tolerante a falhas transitórias.

    - 401: chave inválida / recusada.
    - 429: limite temporário.
    - 500/502/503/504: tenta novamente com pequeno backoff.
    - outros erros HTTP: retorna erro controlado.
    """

    codigos_transitorios = {
        500,
        502,
        503,
        504,
    }

    ultimo_status = None
    ultimo_erro = None

    for tentativa in range(
        1,
        tentativas + 1,
    ):
        try:
            resposta = requests.get(
                POKEMON_TCG_API_URL,
                headers={
                    "X-Api-Key": POKEMON_TCG_API_KEY,
                    "Accept": "application/json",
                },
                params=params,
                timeout=12,
            )

        except requests.RequestException as erro:
            ultimo_erro = erro

            if tentativa < tentativas:
                time.sleep(
                    0.8 * tentativa
                )
                continue

            raise RuntimeError(
                "Não foi possível conectar ao catálogo "
                "Pokémon TCG após novas tentativas."
            ) from erro

        ultimo_status = resposta.status_code

        if resposta.status_code == 401:
            raise RuntimeError(
                "A Pokémon TCG API recusou a chave configurada. "
                "Verifique POKEMON_TCG_API_KEY nos Secrets."
            )

        if resposta.status_code == 429:
            raise RuntimeError(
                "O catálogo Pokémon TCG atingiu temporariamente "
                "o limite de consultas. Tente novamente em alguns minutos."
            )

        if resposta.status_code in codigos_transitorios:
            if tentativa < tentativas:
                time.sleep(
                    0.8 * tentativa
                )
                continue

            return {
                "ok": False,
                "status": resposta.status_code,
                "transitorio": True,
                "data": [],
            }

        try:
            resposta.raise_for_status()
        except requests.RequestException as erro:
            raise RuntimeError(
                "O catálogo Pokémon TCG respondeu com erro "
                f"HTTP {resposta.status_code}."
            ) from erro

        try:
            payload = resposta.json()
        except ValueError as erro:
            raise RuntimeError(
                "O catálogo Pokémon TCG respondeu em formato inválido."
            ) from erro

        cartas = payload.get(
            "data",
            [],
        )

        if not isinstance(
            cartas,
            list,
        ):
            raise RuntimeError(
                "O catálogo Pokémon TCG retornou "
                "uma estrutura inesperada."
            )

        return {
            "ok": True,
            "status": resposta.status_code,
            "transitorio": False,
            "data": cartas,
        }

    return {
        "ok": False,
        "status": ultimo_status,
        "transitorio": bool(
            ultimo_status
            in {
                500,
                502,
                503,
                504,
            }
        ),
        "data": [],
        "erro": str(
            ultimo_erro or ""
        ),
    }


@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def consultar_catalogo_pokemon(
    nome_carta,
    cache_buster=0,
):
    """
    Reliability 2.1.1

    Estratégia:
    1. procura pela frase completa do nome;
    2. em falha transitória ou ausência de resultados,
       tenta uma consulta mais simples;
    3. limita o volume retornado porque o ranking final
       é feito localmente pelo CardCraftAI.
    """

    # cache_buster participa apenas da chave do st.cache_data.
    # Em uma nova tentativa manual, ele muda e força uma consulta fresca
    # sem limpar o cache global de outros usuários/consultas.
    _ = cache_buster

    nome = str(
        nome_carta or ""
    ).strip()

    if not nome:
        return []

    if not POKEMON_TCG_API_KEY:
        raise RuntimeError(
            "A chave POKEMON_TCG_API_KEY ainda não está "
            "configurada nos Secrets do Streamlit."
        )

    nome_seguro = _frase_lucene_segura(
        nome
    )

    # Estratégia principal: frase completa.
    consulta_principal = (
        f'name:"{nome_seguro}"'
    )

    resultado_principal = (
        _executar_requisicao_catalogo(
            params={
                "q": consulta_principal,
                "page": 1,
                "pageSize": 50,
            },
            tentativas=2,
        )
    )

    if (
        resultado_principal.get("ok")
        and
        resultado_principal.get("data")
    ):
        return resultado_principal[
            "data"
        ]

    # Fallback: uma palavra representativa do nome
    # com wildcard, sintaxe suportada pelo catálogo.
    token = _token_fallback_catalogo(
        nome
    )

    if token:
        consulta_fallback = (
            f"name:{token}*"
        )

        resultado_fallback = (
            _executar_requisicao_catalogo(
                params={
                    "q": consulta_fallback,
                    "page": 1,
                    "pageSize": 50,
                },
                tentativas=2,
            )
        )

        if resultado_fallback.get(
            "ok"
        ):
            return resultado_fallback.get(
                "data",
                [],
            )

        status_fallback = (
            resultado_fallback.get(
                "status"
            )
        )

    else:
        resultado_fallback = None
        status_fallback = None

    status_principal = (
        resultado_principal.get(
            "status"
        )
    )

    status_final = (
        status_fallback
        or
        status_principal
    )

    if status_final in {
        500,
        502,
        503,
        504,
    }:
        raise RuntimeError(
            "O catálogo Pokémon TCG está temporariamente "
            f"indisponível (HTTP {status_final}). "
            "O CardCraftAI tentou novamente e também usou "
            "uma busca simplificada. Nenhum crédito foi consumido."
        )

    # Se a API respondeu normalmente mas não encontrou cartas,
    # retornamos lista vazia em vez de tratar como erro.
    return []


@st.cache_data(
    ttl=3600,
    show_spinner=False,
)
def _set_id_catalogo_por_colecao(colecao):
    """Retorna o ID do set quando a coleção possui um alias determinístico conhecido."""
    colecao_norm = _normalizar_colecao_catalogo(colecao)

    mapa = {
        "sm black star promos": "smp",
        "swsh black star promos": "swshp",
        "xy black star promos": "xyp",
        "bw black star promos": "bwp",
        "sv black star promos": "svp",
    }

    return mapa.get(colecao_norm)


def _set_id_catalogo_por_numero(numero_carta):
    """
    Infere alguns sets promocionais pelo prefixo impresso do número.

    É apenas um fallback para quando a coleção veio com um rótulo inesperado;
    não substitui a validação posterior de nome + coleção + número.
    """
    numero = _numero_principal_catalogo(numero_carta).upper()

    prefixos = (
        ("SWSH", "swshp"),
        ("SM", "smp"),
        ("XY", "xyp"),
        ("BW", "bwp"),
    )

    for prefixo, set_id in prefixos:
        if numero.startswith(prefixo) and numero[len(prefixo):].isdigit():
            return set_id

    return None


def _consultar_catalogo_por_id_composto(colecao, numero_carta):
    """
    Reliability 2.6.20

    Para coleções cujo ID é conhecido (ou números promocionais cujo prefixo
    permite inferir o set), consulta diretamente /cards/<id>.
    Isso evita que uma busca ampla por nome substitua uma carta de número exato.
    """
    set_id = (
        _set_id_catalogo_por_colecao(colecao)
        or _set_id_catalogo_por_numero(numero_carta)
    )
    numero_api = _numero_principal_catalogo(numero_carta).upper()

    if not set_id or not numero_api:
        return []

    card_id = f"{set_id}-{numero_api}"
    codigos_transitorios = {500, 502, 503, 504}

    for tentativa in range(1, 3):
        try:
            resposta = requests.get(
                f"{POKEMON_TCG_API_URL}/{card_id}",
                headers={
                    "X-Api-Key": POKEMON_TCG_API_KEY,
                    "Accept": "application/json",
                },
                timeout=12,
            )
        except requests.RequestException as erro:
            if tentativa < 2:
                time.sleep(0.8 * tentativa)
                continue
            raise RuntimeError(
                "Não foi possível conectar ao catálogo Pokémon TCG "
                "durante a consulta exata da carta."
            ) from erro

        if resposta.status_code == 404:
            return []

        if resposta.status_code == 401:
            raise RuntimeError(
                "A Pokémon TCG API recusou a chave configurada. "
                "Verifique POKEMON_TCG_API_KEY nos Secrets."
            )

        if resposta.status_code == 429:
            raise RuntimeError(
                "O catálogo Pokémon TCG atingiu temporariamente "
                "o limite de consultas. Tente novamente em alguns minutos."
            )

        if resposta.status_code in codigos_transitorios:
            if tentativa < 2:
                time.sleep(0.8 * tentativa)
                continue
            raise RuntimeError(
                "O catálogo Pokémon TCG está temporariamente "
                f"indisponível (HTTP {resposta.status_code}) durante a consulta exata."
            )

        try:
            resposta.raise_for_status()
        except requests.RequestException as erro:
            raise RuntimeError(
                "O catálogo Pokémon TCG respondeu com erro "
                f"HTTP {resposta.status_code}."
            ) from erro

        try:
            payload = resposta.json()
        except ValueError as erro:
            raise RuntimeError(
                "O catálogo Pokémon TCG respondeu em formato inválido."
            ) from erro

        carta = payload.get("data")
        if not isinstance(carta, dict):
            return []

        return [carta]

    return []

def consultar_catalogo_pokemon_por_numero(
    numero_carta,
    colecao="",
    cache_buster=0,
):
    """
    Reliability 2.6.20

    Ordem de resolução do identificador:
    1. ID direto quando coleção/prefixo + número permitem derivá-lo;
    2. busca Lucene exata restringida ao set quando ele é conhecido;
    3. busca Lucene exata global;
    4. busca normal por number com filtro local estritamente equivalente.

    Uma falha transitória na rota de ID direto não encerra a busca: tentamos
    também o endpoint de pesquisa. Se nenhuma consulta exata responder de forma
    utilizável, o erro é propagado para impedir um falso "melhor candidato" por nome.
    """
    _ = cache_buster

    numero = str(numero_carta or "").strip()
    numero_norm = _normalizar_numero_catalogo(numero)
    numero_principal = _numero_principal_catalogo(numero).upper()

    if not numero_norm or not numero_principal:
        return []

    if not POKEMON_TCG_API_KEY:
        raise RuntimeError(
            "A chave POKEMON_TCG_API_KEY ainda não está "
            "configurada nos Secrets do Streamlit."
        )

    erro_id = None
    try:
        cartas_id = _consultar_catalogo_por_id_composto(
            colecao,
            numero,
        )
    except RuntimeError as erro:
        erro_id = erro
        cartas_id = []

    cartas_id = [
        carta
        for carta in cartas_id
        if _numeros_catalogo_equivalentes(
            carta.get("number"),
            numero,
        )
    ]
    if cartas_id:
        return cartas_id

    numero_seguro = _frase_lucene_segura(numero_principal)
    set_id = (
        _set_id_catalogo_por_colecao(colecao)
        or _set_id_catalogo_por_numero(numero)
    )

    consultas = []
    if set_id:
        consultas.extend([
            f"!number:{numero_seguro} set.id:{set_id}",
            f"number:{numero_seguro} set.id:{set_id}",
        ])

    consultas.extend([
        f"!number:{numero_seguro}",
        f"number:{numero_seguro}",
    ])

    # Remove duplicatas preservando a ordem.
    consultas = list(dict.fromkeys(consultas))

    ultimo_status = None
    alguma_consulta_exata_respondeu = False

    for consulta in consultas:
        resultado = _executar_requisicao_catalogo(
            params={
                "q": consulta,
                "page": 1,
                "pageSize": 100,
            },
            tentativas=2,
        )

        if not resultado.get("ok"):
            ultimo_status = resultado.get("status")
            continue

        alguma_consulta_exata_respondeu = True
        cartas = resultado.get("data", []) or []
        exatas = [
            carta
            for carta in cartas
            if isinstance(carta, dict)
            and _numeros_catalogo_equivalentes(
                carta.get("number"),
                numero,
            )
        ]

        if set_id:
            exatas_mesmo_set = [
                carta
                for carta in exatas
                if str(((carta.get("set") or {}).get("id")) or "").strip().lower()
                == str(set_id).strip().lower()
            ]
            if exatas_mesmo_set:
                return exatas_mesmo_set

        if exatas:
            return exatas

    if not alguma_consulta_exata_respondeu:
        if erro_id is not None:
            raise erro_id

        if ultimo_status in {500, 502, 503, 504}:
            raise RuntimeError(
                "O catálogo Pokémon TCG está temporariamente "
                f"indisponível (HTTP {ultimo_status}) durante a busca pelo número."
            )

    return []

def ranquear_cartas_catalogo(
    cartas,
    nome="",
    colecao="",
    numero="",
    limite=12,
):
    nome = str(nome or "").strip()
    colecao = str(colecao or "").strip()
    numero = str(numero or "").strip()

    pontuadas = []

    for carta in cartas or []:
        if not isinstance(carta, dict):
            continue

        score = 0.0

        nome_carta = carta.get("name", "")
        set_nome = (
            (carta.get("set") or {})
            .get("name", "")
        )
        numero_carta = carta.get("number", "")

        if nome:
            score += (
                _similaridade_catalogo(
                    nome,
                    nome_carta,
                )
                * 60
            )

        if colecao:
            score += (
                _similaridade_colecao_catalogo(
                    colecao,
                    set_nome,
                )
                * 30
            )

        numero_exato = False
        if numero:
            numero_exato = _numeros_catalogo_equivalentes(
                numero,
                numero_carta,
            )

            if numero_exato:
                score += 60
            else:
                score += (
                    _similaridade_catalogo(
                        numero,
                        numero_carta,
                    )
                    * 15
                )

        pontuadas.append(
            (
                1 if (numero and numero_exato) else 0,
                score,
                carta,
            )
        )

    pontuadas.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    return [
        carta
        for _, _, carta in pontuadas[:limite]
    ]

def buscar_cartas_catalogo_pokemon(
    nome,
    colecao="",
    numero="",
    limite=12,
    cache_buster=0,
):
    """
    Reliability 2.2.4

    Ordem de resolução:
    1. número exato, quando disponível;
    2. nome da carta;
    3. ranking local por número, nome e coleção normalizada.

    O resultado exato por número nunca é descartado pela busca ampla por nome.
    """
    cartas_numero = []
    erro_numero = None

    if str(numero or "").strip():
        try:
            cartas_numero = consultar_catalogo_pokemon_por_numero(
                numero,
                colecao=colecao,
                cache_buster=cache_buster,
            )
        except RuntimeError as erro:
            erro_numero = erro

    cartas_nome = []
    try:
        cartas_nome = consultar_catalogo_pokemon(
            nome,
            cache_buster=cache_buster,
        )
    except RuntimeError:
        if cartas_numero:
            cartas_nome = []
        else:
            raise

    combinadas = []
    ids_vistos = set()

    for carta in [*(cartas_numero or []), *(cartas_nome or [])]:
        if not isinstance(carta, dict):
            continue

        chave = str(carta.get("id") or "").strip()
        if not chave:
            set_dados = carta.get("set") or {}
            chave = "|".join([
                str(carta.get("name") or ""),
                str(set_dados.get("name") or ""),
                str(carta.get("number") or ""),
            ])

        if chave in ids_vistos:
            continue

        ids_vistos.add(chave)
        combinadas.append(carta)

    if erro_numero is not None and str(numero or "").strip():
        # Se a consulta exata por número falhou tecnicamente, não usamos uma
        # busca ampla por nome para inventar um "melhor candidato". Isso evita
        # falsos conflitos como SM211 -> SM60 durante falhas parciais da API.
        raise erro_numero

    return ranquear_cartas_catalogo(
        combinadas,
        nome=nome,
        colecao=colecao,
        numero=numero,
        limite=limite,
    )


# ============================================================
# RELIABILITY 2.2 - VALIDACAO DA IDENTIFICACAO POR FOTO
# ============================================================

def _extrair_identificacao_foto(resultado):
    """Extrai os campos da IA usados na validação com o catálogo."""
    if not isinstance(resultado, dict):
        return {
            "nome": "",
            "colecao": "",
            "numero": "",
            "ano_visual_ia": None,
            "variante_ia": "",
            "idioma_ia": "",
            "qualidade_imagem": "",
            "status_modelo": "",
        }

    return {
        "nome": str(resultado.get("nome_carta") or "").strip(),
        "colecao": str(resultado.get("colecao_set") or "").strip(),
        "numero": str(resultado.get("numero_carta") or "").strip(),
        "ano_visual_ia": resultado.get("ano"),
        "variante_ia": str(resultado.get("variante") or "").strip(),
        "idioma_ia": str(resultado.get("idioma_carta") or "").strip(),
        "qualidade_imagem": str(resultado.get("qualidade_imagem") or "").strip(),
        "status_modelo": str(resultado.get("status_identificacao") or "").strip(),
    }


def _comparar_identificacao_com_carta(identificacao, carta):
    """Compara nome, coleção e número da IA com uma carta real do catálogo."""
    if not isinstance(carta, dict):
        return None

    set_dados = carta.get("set") or {}

    nome_ia = identificacao.get("nome", "")
    colecao_ia = identificacao.get("colecao", "")
    numero_ia = identificacao.get("numero", "")

    nome_catalogo = carta.get("name", "")
    colecao_catalogo = set_dados.get("name", "")
    numero_catalogo = carta.get("number", "")

    similaridade_nome = _similaridade_catalogo(nome_ia, nome_catalogo)
    similaridade_colecao = _similaridade_colecao_catalogo(colecao_ia, colecao_catalogo)

    numero_exato = _numeros_catalogo_equivalentes(
        numero_ia,
        numero_catalogo,
    )

    similaridade_numero = _similaridade_catalogo(numero_ia, numero_catalogo)

    score = similaridade_nome * 50

    if colecao_ia:
        score += similaridade_colecao * 25

    if numero_ia:
        score += 40 if numero_exato else similaridade_numero * 10

    return {
        "carta": carta,
        "score": score,
        "similaridade_nome": similaridade_nome,
        "similaridade_colecao": similaridade_colecao,
        "similaridade_numero": similaridade_numero,
        "numero_exato": numero_exato,
        "nome_catalogo": nome_catalogo,
        "colecao_catalogo": colecao_catalogo,
        "numero_catalogo": numero_catalogo,
    }


def validar_identificacao_foto_catalogo(resultado, cartas):
    """
    Valida a identificação preliminar da IA contra o catálogo Pokémon.

    Regra deliberadamente conservadora:
    confirmação automática exige nome + coleção + número, além de imagem
    que não tenha sido classificada como ruim.
    """
    identificacao = _extrair_identificacao_foto(resultado)

    if not identificacao["nome"]:
        return {
            "status": "sem_dados",
            "titulo": t("catalog_no_data_title"),
            "mensagem": t("catalog_no_data_message"),
            "melhor": None,
            "candidatos": [],
            "identificacao": identificacao,
        }

    comparacoes = []
    for carta in cartas or []:
        comparacao = _comparar_identificacao_com_carta(identificacao, carta)
        if comparacao:
            comparacoes.append(comparacao)

    comparacoes.sort(
        key=lambda item: (
            1 if item.get("numero_exato") else 0,
            item.get("score", 0),
        ),
        reverse=True,
    )

    if not comparacoes:
        return {
            "status": "sem_resultado",
            "titulo": t("catalog_no_result_title"),
            "mensagem": t("catalog_no_result_message"),
            "melhor": None,
            "candidatos": [],
            "identificacao": identificacao,
        }

    melhor = comparacoes[0]

    nome_forte = melhor["similaridade_nome"] >= 0.90
    colecao_forte = melhor["similaridade_colecao"] >= 0.85
    numero_exato = melhor["numero_exato"]

    tem_colecao = bool(identificacao["colecao"])
    tem_numero = bool(identificacao["numero"])
    imagem_ruim = _normalizar_texto_catalogo(
        identificacao["qualidade_imagem"]
    ) == "ruim"

    if (
        nome_forte
        and tem_colecao
        and colecao_forte
        and tem_numero
        and numero_exato
        and not imagem_ruim
    ):
        status = "confirmado"
        titulo = t("catalog_validated_title")
        mensagem = t("catalog_validated_message")

    elif (
        nome_forte
        and (
            (tem_numero and numero_exato)
            or (
                not tem_numero
                and tem_colecao
                and colecao_forte
            )
        )
    ):
        status = "provavel"
        titulo = t("catalog_probable_title")
        mensagem = (
            t("catalog_probable_image_message")
            if imagem_ruim
            else t("catalog_probable_missing_message")
        )

    else:
        status = "inconclusivo"
        titulo = t("catalog_inconclusive_title")
        mensagem = (
            t("catalog_inconclusive_number_message")
            if tem_numero and not numero_exato
            else t("catalog_inconclusive_message")
        )

    return {
        "status": status,
        "titulo": titulo,
        "mensagem": mensagem,
        "melhor": melhor,
        "candidatos": comparacoes[:8],
        "identificacao": identificacao,
    }

# ============================================================
# RELIABILITY 2.4 - CONFIDENCE ENGINE
# ============================================================

def _identificacao_para_confianca(dados):
    """
    Aceita tanto o resultado estruturado bruto da IA quanto o dicionário
    já extraído por _extrair_identificacao_foto().
    """
    if not isinstance(dados, dict):
        return _extrair_identificacao_foto({})

    if any(
        chave in dados
        for chave in (
            "nome_carta",
            "colecao_set",
            "numero_carta",
            "status_identificacao",
        )
    ):
        return _extrair_identificacao_foto(dados)

    base = _extrair_identificacao_foto({})
    for chave in base:
        if chave in dados:
            base[chave] = dados.get(chave)

    return base


def classificar_confianca_cardcraft(
    dados_identificacao,
    validacao=None,
    catalogo_disponivel=True,
):
    """Reliability 2.4.0: confiança determinística, sem porcentagem inventada."""
    identificacao = _identificacao_para_confianca(
        dados_identificacao
    )

    nome = str(identificacao.get("nome") or "").strip()
    colecao = str(identificacao.get("colecao") or "").strip()
    numero = str(identificacao.get("numero") or "").strip()

    qualidade = _normalizar_texto_catalogo(
        identificacao.get("qualidade_imagem")
    )
    status_modelo = _normalizar_texto_catalogo(
        identificacao.get("status_modelo")
    )

    validacao = validacao if isinstance(validacao, dict) else {}
    status_catalogo = str(validacao.get("status") or "").strip().lower()
    melhor = validacao.get("melhor")
    melhor = melhor if isinstance(melhor, dict) else {}

    nome_forte = bool(
        melhor
        and float(melhor.get("similaridade_nome") or 0) >= 0.90
    )
    colecao_forte = bool(
        melhor
        and float(melhor.get("similaridade_colecao") or 0) >= 0.85
    )
    numero_exato = bool(
        melhor
        and melhor.get("numero_exato")
    )

    numero_catalogo = str(
        melhor.get("numero_catalogo") or ""
    ).strip()

    if (
        catalogo_disponivel
        and melhor
        and numero
        and numero_catalogo
        and not numero_exato
    ):
        return {
            "codigo": "divergencia",
            "rotulo": t("confidence_divergence_label"),
            "mensagem": t("confidence_divergence_message"),
            "evidencias": [
                t("confidence_ai_number", number=numero),
                t("confidence_catalog_number", number=numero_catalogo),
                t("confidence_number_priority"),
            ],
            "confirmacao_externa": False,
            "bloqueio_divergencia": True,
        }

    if catalogo_disponivel and status_catalogo == "confirmado":
        return {
            "codigo": "confirmado_catalogo",
            "rotulo": t("confidence_confirmed_label"),
            "mensagem": t("confidence_confirmed_message"),
            "evidencias": [
                t("confidence_exact_number"),
                t("confidence_name_match"),
                t("confidence_set_match"),
            ],
            "confirmacao_externa": True,
            "bloqueio_divergencia": False,
        }

    if catalogo_disponivel:
        evidencias_parciais = []

        if numero_exato:
            evidencias_parciais.append(t("confidence_exact_candidate"))
        if nome_forte:
            evidencias_parciais.append(t("confidence_name_strong"))
        if colecao_forte:
            evidencias_parciais.append(t("confidence_set_strong"))

        parcial = (
            status_catalogo == "provavel"
            or (
                status_catalogo == "inconclusivo"
                and (
                    numero_exato
                    or (nome_forte and colecao_forte)
                )
            )
        )

        if parcial:
            if not numero:
                evidencias_parciais.append(t("confidence_number_missing"))
            elif not numero_exato:
                evidencias_parciais.append(t("confidence_number_not_exact"))

            if not colecao:
                evidencias_parciais.append(t("confidence_set_missing"))

            return {
                "codigo": "parcial",
                "rotulo": t("confidence_partial_label"),
                "mensagem": t("confidence_partial_message"),
                "evidencias": evidencias_parciais,
                "confirmacao_externa": False,
                "bloqueio_divergencia": False,
            }

        if status_catalogo in {"sem_resultado", "sem_dados"}:
            evidencias = [t("confidence_catalog_no_match")]
        elif melhor:
            evidencias = [t("confidence_candidates_insufficient")]
        else:
            evidencias = [t("confidence_no_external_evidence")]

        return {
            "codigo": "nao_confirmado",
            "rotulo": t("confidence_not_confirmed_label"),
            "mensagem": t("confidence_not_confirmed_message"),
            "evidencias": evidencias,
            "confirmacao_externa": False,
            "bloqueio_divergencia": False,
        }

    campos_completos = bool(nome and colecao and numero)
    imagem_utilizavel = qualidade in {"boa", "aceitavel"}
    leitura_visual_forte = status_modelo == "confirmada"

    if campos_completos and imagem_utilizavel and leitura_visual_forte:
        return {
            "codigo": "alta_visual",
            "rotulo": t("confidence_high_visual_label"),
            "mensagem": t("confidence_high_visual_message"),
            "evidencias": [
                t("confidence_fields_extracted"),
                t("confidence_visual_strong"),
                t("confidence_image_quality_ok"),
                t("confidence_not_catalog_confirmation"),
            ],
            "confirmacao_externa": False,
            "bloqueio_divergencia": False,
        }

    faltantes = []
    if not nome:
        faltantes.append(t("field_name_short"))
    if not colecao:
        faltantes.append(t("field_set_short"))
    if not numero:
        faltantes.append(t("field_number_short"))

    evidencias = [t("confidence_no_external")]

    if faltantes:
        evidencias.append(
            t(
                "confidence_missing_identifiers",
                fields=", ".join(faltantes),
            )
        )

    if not imagem_utilizavel:
        evidencias.append(t("confidence_image_quality_low"))

    if not leitura_visual_forte:
        evidencias.append(t("confidence_visual_not_strong"))

    return {
        "codigo": "nao_confirmado",
        "rotulo": t("confidence_not_confirmed_label"),
        "mensagem": t("confidence_no_external_high_message"),
        "evidencias": evidencias,
        "confirmacao_externa": False,
        "bloqueio_divergencia": False,
    }

def mostrar_nivel_confianca_cardcraft(confianca):
    """Apresenta o nível sem transformar incerteza em porcentagem artificial."""
    if not isinstance(confianca, dict):
        return

    codigo = confianca.get("codigo", "nao_confirmado")
    rotulo = confianca.get("rotulo", t("confidence_not_confirmed_label"))
    mensagem = confianca.get("mensagem", "")

    st.markdown(t("confidence_title"))

    if codigo == "confirmado_catalogo":
        st.success(rotulo)
    elif codigo == "divergencia":
        st.error(rotulo)
    elif codigo == "parcial":
        st.warning(rotulo)
    else:
        st.info(rotulo)

    if mensagem:
        st.write(mensagem)

    with st.expander(t("confidence_why")):
        for item in (confianca.get("evidencias") or []):
            st.write(f"- {item}")

        st.caption(t("confidence_engine_note"))

def _indicador_correspondencia(
    valor_ia,
    valor_catalogo,
    limite=0.85,
    numero=False,
    colecao=False,
):
    """Texto curto para explicar ao usuário o que coincidiu."""
    if not valor_ia:
        return t("indicator_not_informed")

    if numero:
        iguais = _numeros_catalogo_equivalentes(
            valor_ia,
            valor_catalogo,
        )
    elif colecao:
        iguais = (
            _similaridade_colecao_catalogo(
                valor_ia,
                valor_catalogo,
            )
            >= limite
        )
    else:
        iguais = _similaridade_catalogo(valor_ia, valor_catalogo) >= limite

    return t("indicator_compatible") if iguais else t("indicator_divergent")

def mostrar_validacao_foto_catalogo(validacao):
    """Renderiza o resultado da validação sem consumir outro crédito."""
    status = validacao.get("status")
    titulo = validacao.get("titulo", t("catalog_no_result_title"))
    mensagem = validacao.get("mensagem", "")

    if status == "confirmado":
        st.success(titulo)
    elif status in {"provavel", "inconclusivo"}:
        st.warning(titulo)
    else:
        st.info(titulo)

    if mensagem:
        st.caption(mensagem)

    identificacao = validacao.get("identificacao") or {}
    confianca = classificar_confianca_cardcraft(
        identificacao,
        validacao=validacao,
        catalogo_disponivel=True,
    )
    mostrar_nivel_confianca_cardcraft(confianca)

    melhor = validacao.get("melhor")
    if not melhor:
        return

    col_nome, col_set, col_numero = st.columns(3)

    with col_nome:
        st.caption(t("label_name"))
        st.write(
            _indicador_correspondencia(
                identificacao.get("nome"),
                melhor.get("nome_catalogo"),
                limite=0.90,
            )
        )

    with col_set:
        st.caption(t("label_set"))
        st.write(
            _indicador_correspondencia(
                identificacao.get("colecao"),
                melhor.get("colecao_catalogo"),
                limite=0.85,
                colecao=True,
            )
        )

    with col_numero:
        st.caption(t("label_number"))
        st.write(
            _indicador_correspondencia(
                identificacao.get("numero"),
                melhor.get("numero_catalogo"),
                numero=True,
            )
        )

    with st.expander(t("validation_explainer")):
        st.write(
            t(
                "ai_identified",
                name=identificacao.get("nome") or t("not_confirmed"),
                set_name=identificacao.get("colecao") or t("set_not_confirmed"),
                number=identificacao.get("numero") or t("number_not_confirmed"),
            )
        )
        st.write(
            t(
                "catalog_best_match",
                name=melhor.get("nome_catalogo") or t("not_available"),
                set_name=melhor.get("colecao_catalogo") or t("set_not_available"),
                number=melhor.get("numero_catalogo") or t("number_not_available"),
            )
        )
        st.caption(t("validation_disclaimer"))

    if status == "confirmado":
        carta_confirmada = melhor.get("carta") or {}
        resumo_confirmado = _resumo_carta_catalogo(carta_confirmada)

        st.markdown(t("data_origin_title"))
        col_confirmado, col_estimado = st.columns(2, gap="large")

        with col_confirmado:
            st.success(t("confirmed_by_catalog"))
            st.write(f"**{t('label_name')}:** " + texto_ou_nao_confirmado(resumo_confirmado.get("nome")))
            st.write(f"**{t('label_set')}:** " + texto_ou_nao_confirmado(resumo_confirmado.get("set")))
            st.write(f"**{t('label_number')}:** " + texto_ou_nao_confirmado(resumo_confirmado.get("numero")))
            st.write(f"**{t('label_rarity')}:** " + texto_ou_nao_confirmado(resumo_confirmado.get("raridade")))
            st.write(f"**{t('label_artist')}:** " + texto_ou_nao_confirmado(resumo_confirmado.get("artista")))
            st.write(f"**{t('label_set_release')}:** " + texto_ou_nao_confirmado(resumo_confirmado.get("data_lancamento_set")))
            st.caption(t("set_release_note"))

        with col_estimado:
            st.info(t("ai_visual_assessment"))
            st.write(f"**{t('label_visible_year')}:** " + texto_ou_nao_confirmado(identificacao.get("ano_visual_ia")))
            st.write(f"**{t('label_variant')}:** " + texto_ou_nao_confirmado(identificacao.get("variante_ia")))
            st.write(f"**{t('label_apparent_language')}:** " + texto_ou_nao_confirmado(identificacao.get("idioma_ia")))
            st.write(t("ai_estimates_note"))
            st.caption(t("physical_assessment_note"))

def _url_imagem_carta(
    carta,
    tamanho="large",
):
    imagens = carta.get("images") or {}

    return (
        imagens.get(tamanho)
        or
        imagens.get("large")
        or
        imagens.get("small")
        or
        ""
    )


def _renderizar_imagem_clicavel(
    carta,
):
    url_grande = _url_imagem_carta(
        carta,
        "large",
    )
    url_pequena = _url_imagem_carta(
        carta,
        "small",
    )

    if not url_pequena:
        st.info(
            "Imagem não disponível no catálogo."
        )
        return

    destino = url_grande or url_pequena
    nome = carta.get(
        "name",
        "Carta Pokémon",
    )

    st.markdown(
        (
            '<a href="'
            + escape(
                destino,
                quote=True,
            )
            + '" target="_blank" rel="noopener noreferrer">'
            + '<img src="'
            + escape(
                url_pequena,
                quote=True,
            )
            + '" alt="'
            + escape(
                nome,
                quote=True,
            )
            + '" style="width:100%;'
              'max-width:260px;'
              'border-radius:10px;'
              'display:block;'
              'margin:0 auto 8px auto;" />'
            + "</a>"
        ),
        unsafe_allow_html=True,
    )


def _resumo_carta_catalogo(
    carta,
):
    set_dados = carta.get("set") or {}

    data_lancamento_set = str(
        set_dados.get(
            "releaseDate",
            "",
        )
        or ""
    ).strip()

    return {
        "id": carta.get("id"),
        "nome": carta.get("name"),
        "set": set_dados.get("name"),
        "numero": carta.get("number"),
        "raridade": carta.get("rarity"),
        "artista": carta.get("artist"),
        # releaseDate pertence ao objeto SET da Pokemon TCG API.
        # Nao deve ser apresentado como data especifica de lancamento da carta.
        "data_lancamento_set": data_lancamento_set or None,
        "ano_set": data_lancamento_set[:4] or None,
        # Compatibilidade interna com trechos antigos enquanto migramos a UI.
        "ano": data_lancamento_set[:4] or None,
    }




FRESCOR_MERCADO_ATUAL_DIAS = 7
FRESCOR_MERCADO_ATENCAO_DIAS = 30


def _parse_data_catalogo(
    valor,
):
    """
    Converte datas vindas do catálogo para date.

    O catálogo costuma usar YYYY/MM/DD, mas aceitamos
    algumas variações para evitar quebrar a interface
    se o formato mudar.
    """
    if not valor:
        return None

    texto = str(valor).strip()

    formatos = [
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]

    for formato in formatos:
        try:
            return datetime.strptime(
                texto,
                formato,
            ).date()
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(
            texto.replace(
                "Z",
                "+00:00",
            )
        ).date()
    except ValueError:
        return None


def _avaliar_frescor_catalogo(
    atualizado,
):
    """
    Classifica a idade da fonte de preço.

    - até 7 dias: atualizado
    - 8 a 30 dias: atenção
    - acima de 30 dias: desatualizado
    """
    data_fonte = _parse_data_catalogo(
        atualizado
    )

    if data_fonte is None:
        return {
            "nivel": "desconhecido",
            "emoji": "⚪",
            "rotulo": "Data não disponível",
            "dias": None,
            "data": None,
        }

    hoje = datetime.now(
        timezone.utc
    ).date()

    dias = (
        hoje - data_fonte
    ).days

    if dias < 0:
        return {
            "nivel": "desconhecido",
            "emoji": "⚪",
            "rotulo": "Data futura a verificar",
            "dias": dias,
            "data": data_fonte,
        }

    if dias <= FRESCOR_MERCADO_ATUAL_DIAS:
        nivel = "atualizado"
        emoji = "🟢"
        rotulo = "Atualizado"
    elif dias <= FRESCOR_MERCADO_ATENCAO_DIAS:
        nivel = "atencao"
        emoji = "🟡"
        rotulo = "Atenção"
    else:
        nivel = "desatualizado"
        emoji = "🔴"
        rotulo = "Desatualizado"

    return {
        "nivel": nivel,
        "emoji": emoji,
        "rotulo": rotulo,
        "dias": dias,
        "data": data_fonte,
    }


def _texto_idade_fonte(
    dias,
):
    if dias is None:
        return "idade desconhecida"

    if dias < 0:
        return "data futura informada pela fonte"

    if dias == 0:
        return "atualizado hoje"

    if dias == 1:
        return "atualizado há 1 dia"

    return f"atualizado há {dias} dias"


def _mostrar_frescor_fonte(
    nome_fonte,
    atualizado,
):
    frescor = _avaliar_frescor_catalogo(
        atualizado
    )

    texto = (
        f"{frescor['emoji']} "
        f"{frescor['rotulo']} — "
        f"{_texto_idade_fonte(frescor['dias'])}"
    )

    if atualizado:
        texto += (
            " • data informada: "
            + str(atualizado)
        )

    if frescor["nivel"] == "atualizado":
        st.success(texto)
    elif frescor["nivel"] == "atencao":
        st.warning(
            texto
            + ". Confirme nas ofertas atuais antes de negociar."
        )
    elif frescor["nivel"] == "desatualizado":
        st.error(
            texto
            + ". Trate estes valores apenas como referência histórica."
        )
    else:
        st.info(
            texto
            + ". Não é possível medir a atualidade desta fonte."
        )

    return frescor


def _formatar_valor_moeda_catalogo(
    valor,
    simbolo,
):
    try:
        numero = float(valor)
    except (
        TypeError,
        ValueError,
    ):
        return None

    texto = (
        f"{numero:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    # O Streamlit interpreta "$" como delimitador matemático
    # quando a string passa pelo Markdown. Escapamos somente
    # para exibição, sem alterar o valor ou a moeda.
    simbolo_exibicao = str(
        simbolo or ""
    ).replace(
        "$",
        r"\$",
    )

    return (
        f"{simbolo_exibicao} "
        f"{texto}"
    )


def _url_busca_tcgplayer(
    carta,
):
    """
    Gera uma busca direta no domínio do TCGplayer.

    Evita depender do redirecionador prices.pokemontcg.io,
    que pode ficar indisponível mesmo quando o marketplace
    principal continua funcionando.
    """
    nome = str(
        carta.get("name") or ""
    ).strip()
    numero = str(
        carta.get("number") or ""
    ).strip()
    set_nome = str(
        ((carta.get("set") or {}).get("name"))
        or ""
    ).strip()

    partes = [
        valor
        for valor in (
            nome,
            numero,
            set_nome,
        )
        if valor
    ]

    if not partes:
        return None

    consulta = quote_plus(
        " ".join(partes)
    )

    return (
        "https://www.tcgplayer.com/"
        "search/pokemon/product"
        f"?q={consulta}"
    )


def _mostrar_precos_referencia_catalogo(
    carta,
):
    """
    Mostra preços recebidos do catálogo com uma classificação
    explícita de atualidade.

    O CardCraftAI diferencia:
    - preço de mercado calculado;
    - menor preço catalogado;
    - ofertas atuais abertas no marketplace.

    Assim, uma referência antiga não é apresentada como se
    fosse um preço atual de compra ou venda.
    """
    tcgplayer = carta.get(
        "tcgplayer"
    ) or {}
    cardmarket = carta.get(
        "cardmarket"
    ) or {}

    tcg_prices = tcgplayer.get(
        "prices"
    ) or {}
    cm_prices = cardmarket.get(
        "prices"
    ) or {}

    if (
        not tcg_prices
        and
        not cm_prices
    ):
        return

    with st.expander(
        "💰 Mercado e atualidade das fontes",
        expanded=False,
    ):
        st.caption(
            "Os valores abaixo são referências fornecidas pelo "
            "catálogo Pokémon TCG. Eles não garantem estoque, "
            "condição, idioma, frete ou preço final."
        )

        st.info(
            "Preço de mercado e menor anúncio são métricas diferentes. "
            "Para saber o que está realmente disponível agora, use "
            "o botão de ofertas atuais do marketplace."
        )

        if tcg_prices:
            st.markdown(
                "#### TCGplayer — USD"
            )

            atualizado = tcgplayer.get(
                "updatedAt"
            )

            frescor_tcg = _mostrar_frescor_fonte(
                "TCGplayer",
                atualizado,
            )

            if frescor_tcg["nivel"] == "desatualizado":
                st.caption(
                    "Os números abaixo ficam visíveis para contexto "
                    "histórico, mas não devem ser tratados como preço "
                    "atual da carta."
                )

            prioridade = [
                "holofoil",
                "normal",
                "reverseHolofoil",
                "1stEditionHolofoil",
                "1stEditionNormal",
            ]

            rotulos = {
                "holofoil": "Holofoil",
                "normal": "Normal",
                "reverseHolofoil": "Reverse Holofoil",
                "1stEditionHolofoil": "1st Edition Holofoil",
                "1stEditionNormal": "1st Edition Normal",
            }

            mostrou_tcg = False

            for tipo in prioridade:
                valores = tcg_prices.get(
                    tipo
                ) or {}

                if not valores:
                    continue

                mercado = _formatar_valor_moeda_catalogo(
                    valores.get("market"),
                    "US$",
                )
                minimo = _formatar_valor_moeda_catalogo(
                    valores.get("low"),
                    "US$",
                )

                partes = []

                if mercado:
                    partes.append(
                        f"preço de mercado {mercado}"
                    )

                if minimo:
                    partes.append(
                        f"menor referência {minimo}"
                    )

                if partes:
                    st.write(
                        "**"
                        + rotulos.get(
                            tipo,
                            tipo,
                        )
                        + ":** "
                        + " • ".join(
                            partes
                        )
                    )
                    mostrou_tcg = True

            if not mostrou_tcg:
                st.caption(
                    "O catálogo não trouxe valores TCGplayer "
                    "utilizáveis para esta carta."
                )

        if cm_prices:
            st.divider()

            st.markdown(
                "#### Cardmarket — EUR"
            )

            atualizado = cardmarket.get(
                "updatedAt"
            )

            frescor_cm = _mostrar_frescor_fonte(
                "Cardmarket",
                atualizado,
            )

            if frescor_cm["nivel"] == "desatualizado":
                st.caption(
                    "Esta fonte está antiga demais para ser usada como "
                    "referência principal. Os valores abaixo são exibidos "
                    "somente como contexto histórico."
                )

            campos = [
                (
                    "Menor preço",
                    "lowPrice",
                ),
                (
                    "Tendência",
                    "trendPrice",
                ),
                (
                    "Média 7 dias",
                    "avg7",
                ),
                (
                    "Média 30 dias",
                    "avg30",
                ),
            ]

            mostrou_cm = False

            for rotulo, campo in campos:
                valor = _formatar_valor_moeda_catalogo(
                    cm_prices.get(
                        campo
                    ),
                    "€",
                )

                if valor:
                    st.write(
                        f"**{rotulo}:** {valor}"
                    )
                    mostrou_cm = True

            if not mostrou_cm:
                st.caption(
                    "O catálogo não trouxe valores Cardmarket "
                    "utilizáveis para esta carta."
                )


def mostrar_carta_catalogo_selecionada(
    carta,
    titulo=None,
):
    if not carta:
        return

    if titulo is None:
        titulo = t("selected_catalog_title")

    resumo = _resumo_carta_catalogo(carta)

    st.success(titulo)

    col_img, col_info = st.columns([1, 2], gap="large")

    with col_img:
        _renderizar_imagem_clicavel(carta)
        st.caption(t("click_image_larger"))

    with col_info:
        st.caption(t("catalog_data_source"))
        st.markdown(f"### {texto_ou_nao_confirmado(resumo.get('nome'))}")
        st.write(f"**{t('label_set')}:** " + texto_ou_nao_confirmado(resumo.get("set")))
        st.write(f"**{t('label_number')}:** " + texto_ou_nao_confirmado(resumo.get("numero")))
        st.write(f"**{t('label_rarity')}:** " + texto_ou_nao_confirmado(resumo.get("raridade")))
        st.write(f"**{t('label_artist')}:** " + texto_ou_nao_confirmado(resumo.get("artista")))
        st.write(f"**{t('label_set_release')}:** " + texto_ou_nao_confirmado(resumo.get("data_lancamento_set")))
        st.caption(t("set_release_note"))
        st.write(f"**{t('label_catalog_id')}:** " + texto_ou_nao_confirmado(resumo.get("id")))

        url_tcgplayer = _url_busca_tcgplayer(carta)

        if url_tcgplayer:
            st.caption(t("tcgplayer_live_caption"))
            st.link_button(
                t("tcgplayer_live_button"),
                url_tcgplayer,
                use_container_width=True,
            )

        _mostrar_precos_referencia_catalogo(carta)

def selecionar_carta_catalogo(
    contexto,
    carta,
):
    """
    Callback executado antes do rerun do Streamlit.

    Mantém a carta escolhida no session_state sem depender
    de um st.rerun() manual dentro da grade de resultados.
    """
    st.session_state[
        f"catalogo_selecionada_{contexto}"
    ] = carta


def mostrar_galeria_catalogo(
    cartas,
    contexto,
):
    if not cartas:
        st.warning(t("catalog_gallery_no_match"))
        return

    st.caption(t("catalog_gallery_instruction"))

    colunas_por_linha = 4

    for inicio in range(0, len(cartas), colunas_por_linha):
        bloco = cartas[inicio:inicio + colunas_por_linha]
        colunas = st.columns(colunas_por_linha, gap="medium")

        for coluna, carta in zip(colunas, bloco):
            with coluna:
                _renderizar_imagem_clicavel(carta)

                set_nome = (carta.get("set") or {}).get("name")
                numero = carta.get("number")
                raridade = carta.get("rarity")

                st.markdown(
                    "**"
                    + escape(str(carta.get("name", t("catalog_default_card_name"))))
                    + "**"
                )

                st.caption(
                    texto_ou_nao_confirmado(set_nome)
                    + " • #"
                    + texto_ou_nao_confirmado(numero)
                )

                if raridade:
                    st.caption(str(raridade))

                carta_id = str(carta.get("id", inicio))

                st.button(
                    t("select_this_card"),
                    key=f"catalogo_selecionar_{contexto}_{carta_id}",
                    use_container_width=True,
                    on_click=selecionar_carta_catalogo,
                    args=(contexto, carta),
                )

def info_catalogo_para_analise(
    carta,
):
    if not carta:
        return ""

    resumo = _resumo_carta_catalogo(
        carta
    )

    return (
        "Fonte: entrada selecionada pelo usuário "
        "no catálogo Pokémon TCG API.\n"
        f"ID do catálogo: {resumo.get('id')}\n"
        f"Nome: {resumo.get('nome')}\n"
        f"Coleção/Set: {resumo.get('set')}\n"
        f"Número: {resumo.get('numero')}\n"
        f"Raridade: {resumo.get('raridade')}\n"
        f"Artista: {resumo.get('artista')}\n"
        f"Data de lançamento do set: {resumo.get('data_lancamento_set')}"
    )


def validar_carta_selecionada_catalogo(
    resultado,
    carta,
):
    """
    Reliability 2.6.3

    Registra a identidade de uma carta que o proprio usuario selecionou
    diretamente no catalogo Pokemon TCG. Nao faz nova requisicao de rede:
    reaproveita a carta ja retornada pelo catalogo gratuito.

    A identidade principal pode ser confirmada pelo catalogo porque a entrada
    da analise e a propria carta selecionada. Ainda assim, a comparacao com a
    resposta da IA e preservada para que uma divergencia objetiva de numero
    continue bloqueando o nivel de confianca no Confidence Engine.
    """
    if not isinstance(carta, dict) or not carta:
        return {
            "status": "sem_dados",
            "titulo": "Carta de catalogo nao disponivel",
            "mensagem": (
                "Nao havia uma carta selecionada do catalogo para registrar "
                "como evidencia externa desta analise."
            ),
            "melhor": None,
            "candidatos": [],
            "identificacao": _extrair_identificacao_foto(resultado),
        }

    identificacao = _extrair_identificacao_foto(resultado)
    comparacao = _comparar_identificacao_com_carta(
        identificacao,
        carta,
    )

    resumo = _resumo_carta_catalogo(carta)

    return {
        "status": "confirmado",
        "titulo": "✅ Identidade confirmada pela carta selecionada no catalogo",
        "mensagem": (
            "A analise partiu de uma carta selecionada diretamente no catalogo "
            "Pokemon TCG. O ID, nome, colecao e numero dessa entrada ficam "
            "persistidos como evidencia externa rastreavel."
        ),
        "melhor": comparacao or {
            "carta": carta,
            "score": None,
            "similaridade_nome": None,
            "similaridade_colecao": None,
            "similaridade_numero": None,
            "numero_exato": False,
            "nome_catalogo": resumo.get("nome"),
            "colecao_catalogo": resumo.get("set"),
            "numero_catalogo": resumo.get("numero"),
        },
        "candidatos": [comparacao] if comparacao else [],
        "identificacao": identificacao,
        "origem": "catalogo_selecionado_usuario",
    }


def _chave_validacao_foto_catalogo(resultado):
    """Cria uma chave estável para reutilizar a validação da mesma análise."""
    identificacao = _extrair_identificacao_foto(
        resultado
    )

    partes = [
        _normalizar_texto_catalogo(
            identificacao.get("nome")
        ),
        _normalizar_texto_catalogo(
            identificacao.get("colecao")
        ),
        _normalizar_texto_catalogo(
            identificacao.get("numero")
        ),
    ]

    return "|".join(partes)


def _preparar_estado_validacao_foto(resultado):
    """
    Mantém a validação do catálogo separada da chamada ao Gemini.

    Isso permite tentar o catálogo novamente sem repetir a análise da foto
    e sem reservar/consumir um novo crédito.
    """
    chave = _chave_validacao_foto_catalogo(
        resultado
    )

    chave_anterior = st.session_state.get(
        "catalogo_validacao_foto_chave"
    )

    if chave != chave_anterior:
        st.session_state.catalogo_validacao_foto_chave = chave
        st.session_state.catalogo_validacao_foto_estado = "novo"
        st.session_state.catalogo_validacao_foto_cartas = []
        st.session_state.catalogo_validacao_foto_resultado = None
        st.session_state.catalogo_validacao_foto_erro = None
        st.session_state.catalogo_validacao_foto_retry = 0
        st.session_state.catalogo_selecionada_foto = None

    return chave


def _status_http_catalogo_erro(erro):
    """Extrai códigos HTTP transitórios conhecidos da mensagem de erro."""
    texto = str(
        erro or ""
    )

    for status in (
        500,
        502,
        503,
        504,
        429,
    ):
        if f"HTTP {status}" in texto:
            return status

    return None


def _mostrar_falha_validacao_catalogo_foto(erro):
    """Explica a falha externa sem invalidar a análise da IA."""
    status = _status_http_catalogo_erro(erro)

    if status in {500, 502, 503, 504}:
        st.warning(t("catalog_temp_unavailable"))
        st.caption(t("catalog_http_caption", status=status))
    elif status == 429:
        st.warning(t("catalog_rate_limited"))
    else:
        st.warning(t("catalog_generic_failure"))
        if erro:
            st.caption(str(erro))

def mostrar_catalogo_para_analise_foto(
    resultado,
):
    if not isinstance(
        resultado,
        dict,
    ):
        return

    jogo = _normalizar_texto_catalogo(
        resultado.get(
            "jogo",
            "",
        )
    )

    if (
        jogo
        and
        "pokemon" not in jogo
    ):
        st.divider()
        st.info(t("validation_only_pokemon"))
        return

    nome = resultado.get(
        "nome_carta"
    )

    if not nome:
        st.divider()
        st.info(t("validation_name_missing"))
        mostrar_nivel_confianca_cardcraft(
            classificar_confianca_cardcraft(
                resultado,
                validacao=None,
                catalogo_disponivel=False,
            )
        )
        return

    st.divider()
    st.subheader(t("validation_title"))
    st.caption(t("validation_caption"))

    _preparar_estado_validacao_foto(
        resultado
    )

    estado = st.session_state.get(
        "catalogo_validacao_foto_estado",
        "novo",
    )

    tentar_novamente = False

    if estado == "erro":
        _mostrar_falha_validacao_catalogo_foto(
            st.session_state.get(
                "catalogo_validacao_foto_erro"
            )
        )

        mostrar_nivel_confianca_cardcraft(
            classificar_confianca_cardcraft(
                resultado,
                validacao=None,
                catalogo_disponivel=False,
            )
        )

        st.info(t("validation_saved_retry"))

        tentar_novamente = st.button(
            t("retry_validation_free"),
            key="retry_validacao_catalogo_foto",
            use_container_width=True,
        )

        if not tentar_novamente:
            return

        st.session_state.catalogo_validacao_foto_retry = (
            int(
                st.session_state.get(
                    "catalogo_validacao_foto_retry",
                    0,
                )
            )
            + 1
        )
        estado = "novo"

    if estado == "sucesso":
        cartas = st.session_state.get(
            "catalogo_validacao_foto_cartas",
            [],
        )
        validacao = st.session_state.get(
            "catalogo_validacao_foto_resultado"
        )
    else:
        inicio_catalogo = time.perf_counter()

        try:
            with st.spinner(t("validation_spinner")):
                cartas = buscar_cartas_catalogo_pokemon(
                    nome=nome,
                    colecao=(
                        resultado.get(
                            "colecao_set"
                        )
                        or ""
                    ),
                    numero=(
                        resultado.get(
                            "numero_carta"
                        )
                        or ""
                    ),
                    limite=8,
                    cache_buster=st.session_state.get(
                        "catalogo_validacao_foto_retry",
                        0,
                    ),
                )

            catalogo_latency_ms = int(
                (time.perf_counter() - inicio_catalogo)
                * 1000
            )

        except Exception as erro:
            catalogo_latency_ms = int(
                (time.perf_counter() - inicio_catalogo)
                * 1000
            )

            st.session_state.catalogo_validacao_foto_estado = "erro"
            st.session_state.catalogo_validacao_foto_erro = str(
                erro
            )
            st.session_state.catalogo_validacao_foto_cartas = []
            st.session_state.catalogo_validacao_foto_resultado = None

            atualizar_registro_catalogo(
                resultado,
                erro=erro,
                catalogo_latency_ms=catalogo_latency_ms,
            )

            _mostrar_falha_validacao_catalogo_foto(
                erro
            )

            mostrar_nivel_confianca_cardcraft(
                classificar_confianca_cardcraft(
                    resultado,
                    validacao=None,
                    catalogo_disponivel=False,
                )
            )

            st.info(t("validation_preserved"))

            st.button(
                t("retry_validation_free"),
                key="retry_validacao_catalogo_foto",
                use_container_width=True,
            )
            return

        validacao = validar_identificacao_foto_catalogo(
            resultado,
            cartas,
        )

        atualizar_registro_catalogo(
            resultado,
            validacao=validacao,
            cartas=cartas,
            catalogo_latency_ms=catalogo_latency_ms,
        )

        st.session_state.catalogo_validacao_foto_estado = "sucesso"
        st.session_state.catalogo_validacao_foto_erro = None
        st.session_state.catalogo_validacao_foto_cartas = cartas
        st.session_state.catalogo_validacao_foto_resultado = validacao

    if not isinstance(
        validacao,
        dict,
    ):
        st.info(t("validation_unusable"))
        return

    mostrar_validacao_foto_catalogo(
        validacao
    )

    selecionada = st.session_state.get(
        "catalogo_selecionada_foto"
    )

    if selecionada:
        mostrar_carta_catalogo_selecionada(
            selecionada,
            titulo=t("user_selected_match_title"),
        )
    else:
        melhor = validacao.get("melhor")
        if (
            melhor
            and
            validacao.get("status") in {
                "confirmado",
                "provavel",
            }
        ):
            mostrar_carta_catalogo_selecionada(
                melhor.get("carta"),
                titulo=t("best_match_title"),
            )

    if cartas:
        st.subheader(t("other_matches_title"))
        mostrar_galeria_catalogo(
            cartas,
            contexto="foto",
        )


# ============================================================
# GEMINI
# ============================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        timeout=GEMINI_TIMEOUT_MS,
    ),
)


# ============================================================
# SESSION STATE
# ============================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "email_confirmado" not in st.session_state:
    st.session_state.email_confirmado = False

if "resultado_analise" not in st.session_state:
    st.session_state.resultado_analise = None

if "resultado_tipo" not in st.session_state:
    st.session_state.resultado_tipo = None

if "resultado_novo" not in st.session_state:
    st.session_state.resultado_novo = False

if "aviso_credito" not in st.session_state:
    st.session_state.aviso_credito = None

if "catalogo_resultados_nome" not in st.session_state:
    st.session_state.catalogo_resultados_nome = []

if "catalogo_consulta_nome" not in st.session_state:
    st.session_state.catalogo_consulta_nome = None

if "catalogo_selecionada_nome" not in st.session_state:
    st.session_state.catalogo_selecionada_nome = None

if "catalogo_selecionada_foto" not in st.session_state:
    st.session_state.catalogo_selecionada_foto = None

if "catalogo_validacao_foto_chave" not in st.session_state:
    st.session_state.catalogo_validacao_foto_chave = None

if "catalogo_validacao_foto_estado" not in st.session_state:
    st.session_state.catalogo_validacao_foto_estado = "novo"

if "catalogo_validacao_foto_cartas" not in st.session_state:
    st.session_state.catalogo_validacao_foto_cartas = []

if "catalogo_validacao_foto_resultado" not in st.session_state:
    st.session_state.catalogo_validacao_foto_resultado = None

if "catalogo_validacao_foto_erro" not in st.session_state:
    st.session_state.catalogo_validacao_foto_erro = None

if "catalogo_validacao_foto_retry" not in st.session_state:
    st.session_state.catalogo_validacao_foto_retry = 0

if "analysis_run_id_atual" not in st.session_state:
    st.session_state.analysis_run_id_atual = None

if "analysis_request_id_atual" not in st.session_state:
    st.session_state.analysis_request_id_atual = None

if "analysis_tipo_atual" not in st.session_state:
    st.session_state.analysis_tipo_atual = None

if "aviso_auditoria" not in st.session_state:
    st.session_state.aviso_auditoria = None

if "aviso_recuperacao" not in st.session_state:
    st.session_state.aviso_recuperacao = None

if "ultima_recuperacao_runs" not in st.session_state:
    st.session_state.ultima_recuperacao_runs = None

if "mostrar_recuperacao_senha" not in st.session_state:
    st.session_state.mostrar_recuperacao_senha = False

if "modo_recuperacao_senha" not in st.session_state:
    st.session_state.modo_recuperacao_senha = False

if "recovery_link_processed" not in st.session_state:
    st.session_state.recovery_link_processed = None

if "erro_recuperacao_senha" not in st.session_state:
    st.session_state.erro_recuperacao_senha = None

if "senha_redefinida_sucesso" not in st.session_state:
    st.session_state.senha_redefinida_sucesso = False

if "checkout_preference" not in st.session_state:
    st.session_state.checkout_preference = None

if "payment_return_status" not in st.session_state:
    st.session_state.payment_return_status = None

if "pricing_currency" not in st.session_state:
    st.session_state.pricing_currency = "BRL"

if st.session_state.pricing_currency not in PRICING_CURRENCIES:
    st.session_state.pricing_currency = "BRL"


# ============================================================
# AUTENTICAÇÃO - CONFIRMAÇÃO DE E-MAIL
# ============================================================

def _email_confirmado_no_usuario(usuario):
    """Retorna True somente quando o Supabase marca o e-mail como confirmado."""
    if not usuario:
        return False

    return bool(
        getattr(usuario, "email_confirmed_at", None)
        or getattr(usuario, "confirmed_at", None)
    )


# ============================================================
# SUPABASE
# ============================================================

def criar_cliente_supabase():

    cliente = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
    )

    access_token = st.session_state.get(
        "access_token"
    )

    refresh_token = st.session_state.get(
        "refresh_token"
    )

    if access_token and refresh_token:

        try:
            resposta = cliente.auth.set_session(
                access_token,
                refresh_token,
            )

            if resposta.session:

                st.session_state.access_token = (
                    resposta.session.access_token
                )

                st.session_state.refresh_token = (
                    resposta.session.refresh_token
                )

            if resposta.user:

                if _email_confirmado_no_usuario(
                    resposta.user
                ):

                    st.session_state.user_id = (
                        resposta.user.id
                    )

                    st.session_state.user_email = (
                        resposta.user.email
                    )

                    st.session_state.email_confirmado = True

                else:

                    st.session_state.access_token = None
                    st.session_state.refresh_token = None
                    st.session_state.user_id = None
                    st.session_state.user_email = None
                    st.session_state.email_confirmado = False

        except Exception:

            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.session_state.email_confirmado = False

    return cliente


supabase = criar_cliente_supabase()


def criar_cliente_supabase_service():
    """Cliente privilegiado exclusivo do processo servidor do Streamlit."""
    return create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )


supabase_service = criar_cliente_supabase_service()


# ============================================================
# AUTENTICAÇÃO
# ============================================================

def salvar_sessao(resposta):

    if not resposta:
        return False

    if not resposta.session:
        return False

    if not resposta.user:
        return False

    if not _email_confirmado_no_usuario(
        resposta.user
    ):
        return False

    st.session_state.access_token = (
        resposta.session.access_token
    )

    st.session_state.refresh_token = (
        resposta.session.refresh_token
    )

    st.session_state.user_id = (
        resposta.user.id
    )

    st.session_state.user_email = (
        resposta.user.email
    )

    st.session_state.email_confirmado = True

    return True


def limpar_sessao():

    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.email_confirmado = False

    st.session_state.resultado_analise = None
    st.session_state.resultado_tipo = None
    st.session_state.resultado_novo = False
    st.session_state.aviso_credito = None

    st.session_state.catalogo_resultados_nome = []
    st.session_state.catalogo_consulta_nome = None
    st.session_state.catalogo_selecionada_nome = None
    st.session_state.catalogo_selecionada_foto = None

    st.session_state.analysis_run_id_atual = None
    st.session_state.analysis_request_id_atual = None
    st.session_state.analysis_tipo_atual = None
    st.session_state.aviso_auditoria = None
    st.session_state.aviso_recuperacao = None
    st.session_state.ultima_recuperacao_runs = None

    st.session_state.checkout_preference = None
    st.session_state.payment_return_status = None

    st.session_state.modo_recuperacao_senha = False

    # Ao encerrar a sessão, a próxima entrada começa na página principal.
    # O idioma é preservado propositalmente. Não alteramos diretamente a
    # chave do widget de navegação aqui porque, no logout, esse widget já
    # foi instanciado nesta execução do Streamlit. A sincronização ocorrerá
    # antes de o widget ser criado na próxima sessão autenticada.
    st.session_state.pagina_interface = "photo"


def usuario_logado():

    return (
        st.session_state.user_id is not None
        and
        st.session_state.access_token is not None
        and
        st.session_state.email_confirmado is True
    )


PASSWORD_MIN_LENGTH = 8
PASSWORD_POLICY_MESSAGE = "Use at least 8 characters with lowercase, uppercase, number and symbol."


def validar_senha_forte(senha, idioma_atual=None):
    """Valida a política de senha usada no cadastro e na recuperação."""
    senha = senha or ""
    idioma_atual = idioma_atual or idioma_interface_atual()

    if len(senha) < PASSWORD_MIN_LENGTH:
        return False, t("password_min", idioma_atual, n=PASSWORD_MIN_LENGTH)

    if not any(caractere.islower() for caractere in senha):
        return False, t("password_lower", idioma_atual)

    if not any(caractere.isupper() for caractere in senha):
        return False, t("password_upper", idioma_atual)

    if not any(caractere.isdigit() for caractere in senha):
        return False, t("password_digit", idioma_atual)

    if not any(
        (not caractere.isalnum()) and (not caractere.isspace())
        for caractere in senha
    ):
        return False, t("password_symbol", idioma_atual)

    return True, None


def processar_link_recuperacao_senha():
    """
    Converte o token_hash do e-mail de recuperação em uma sessão autenticada.

    O template de Reset password aponta para:
    ?token_hash=...&type=recovery

    Isso evita depender do fragmento #access_token=... no navegador, que não
    chega ao servidor Streamlit.
    """

    token_hash = str(
        st.query_params.get(
            "token_hash",
            "",
        )
        or ""
    ).strip()

    tipo = str(
        st.query_params.get(
            "type",
            "",
        )
        or ""
    ).strip().lower()

    if (
        not token_hash
        or
        tipo != "recovery"
    ):
        return

    assinatura = (
        f"recovery:{token_hash}"
    )

    if (
        st.session_state.recovery_link_processed
        ==
        assinatura
        and
        st.session_state.modo_recuperacao_senha
    ):
        return

    st.session_state.recovery_link_processed = (
        assinatura
    )

    try:

        resposta = (
            supabase
            .auth
            .verify_otp(
                {
                    "token_hash": token_hash,
                    "type": "recovery",
                }
            )
        )

        if not salvar_sessao(
            resposta
        ):
            raise RuntimeError(
                "A sessão de recuperação não pôde ser iniciada."
            )

        st.session_state.modo_recuperacao_senha = True
        st.session_state.erro_recuperacao_senha = None

    except Exception:

        limpar_sessao()

        st.session_state.recovery_link_processed = None

        st.session_state.erro_recuperacao_senha = t("recovery_invalid")


def tela_redefinir_senha():
    idioma = renderizar_seletor_idioma(
        st,
        "idioma_recovery_widget",
    )

    st.title("🃏 CardCraftAI")
    st.header(t("new_password_title", idioma))
    st.write(t("new_password_intro", idioma))
    st.info(t("password_policy", idioma))

    nova_senha = st.text_input(
        t("new_password", idioma),
        type="password",
        key="nova_senha_recuperacao",
    )
    confirmar_nova_senha = st.text_input(
        t("confirm_new_password", idioma),
        type="password",
        key="confirmar_nova_senha_recuperacao",
    )

    if st.button(
        t("save_new_password", idioma),
        use_container_width=True,
        key="btn_salvar_nova_senha",
    ):
        senha_valida, erro_senha = validar_senha_forte(nova_senha, idioma)

        if not senha_valida:
            st.warning(erro_senha)
        elif nova_senha != confirmar_nova_senha:
            st.warning(t("password_mismatch", idioma))
        else:
            try:
                supabase.auth.update_user({"password": nova_senha})
                try:
                    supabase.auth.sign_out()
                except Exception:
                    pass
                limpar_sessao()
                st.session_state.recovery_link_processed = None
                st.session_state.erro_recuperacao_senha = None
                st.session_state.senha_redefinida_sucesso = True
                st.query_params.clear()
                st.rerun()
            except Exception:
                st.error(t("change_password_failed", idioma))

    if st.button(
        t("cancel_login", idioma),
        use_container_width=True,
        key="btn_cancelar_recuperacao_senha",
    ):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        limpar_sessao()
        st.session_state.recovery_link_processed = None
        st.query_params.clear()
        st.rerun()


# ============================================================
# PERFIL E CRÉDITOS
# ============================================================

def buscar_perfil():

    if not usuario_logado():
        return None

    try:

        resposta = (
            supabase
            .table("profiles")
            .select(
                "id,email,credits,plan"
            )
            .eq(
                "id",
                st.session_state.user_id
            )
            .single()
            .execute()
        )

        return resposta.data

    except Exception:

        return None


def buscar_compras_usuario(
    limite=20,
):
    """Retorna as compras mais recentes do usuário autenticado."""

    if not usuario_logado():
        return []

    try:

        resposta = (
            supabase
            .table("purchases")
            .select(
                "id,provider,amount_cents,currency,"
                "credits_purchased,status,created_at,approved_at"
            )
            .eq(
                "user_id",
                st.session_state.user_id,
            )
            .order(
                "created_at",
                desc=True,
            )
            .limit(
                limite
            )
            .execute()
        )

        return resposta.data or []

    except Exception:

        return []


def formatar_data_conta(valor):
    """Formata timestamps do Supabase para exibição simples no painel."""

    if not valor:
        return "—"

    try:
        texto = str(valor).replace("Z", "+00:00")
        data = datetime.fromisoformat(texto)
        return data.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(valor)


def rotulo_status_compra(status):
    status = str(status or "").strip().lower()

    mapa = {
        "pending": "Pendente",
        "approved": "Aprovada",
        "completed": "Concluída",
        "refunded": "Reembolsada",
        "cancelled": "Cancelada",
        "canceled": "Cancelada",
        "rejected": "Recusada",
    }

    return mapa.get(
        status,
        status.capitalize() if status else "—",
    )


def buscar_creditos():

    perfil = buscar_perfil()

    if not perfil:
        return 0

    return int(
        perfil.get(
            "credits",
            0
        )
    )


def buscar_pacotes_ativos(currency="BRL"):

    moeda = str(currency or "BRL").strip().upper()
    if moeda not in PRICING_CURRENCIES:
        moeda = "BRL"

    try:

        resposta = (
            supabase
            .table("credit_packages")
            .select(
                "id,code,name,description,credits,"
                "price_cents,currency,package_type,active"
            )
            .eq(
                "active",
                True
            )
            .order(
                "price_cents"
            )
            .execute()
        )

        pacotes = resposta.data or []

        precos_resposta = (
            supabase
            .table("credit_package_prices")
            .select(
                "package_id,currency,price_cents,active"
            )
            .eq(
                "currency",
                moeda
            )
            .eq(
                "active",
                True
            )
            .execute()
        )

        precos_por_pacote = {
            str(item.get("package_id")): item
            for item in (precos_resposta.data or [])
            if item.get("package_id") is not None
        }

        resultado = []

        for pacote_original in pacotes:
            pacote = dict(pacote_original)
            preco_moeda = precos_por_pacote.get(
                str(pacote.get("id"))
            )

            pacote["display_currency"] = moeda
            pacote["display_price_available"] = bool(preco_moeda)
            pacote["display_price_cents"] = (
                int(preco_moeda.get("price_cents") or 0)
                if preco_moeda
                else None
            )

            resultado.append(pacote)

        return resultado

    except Exception as erro:

        raise RuntimeError(
            "Não foi possível carregar os planos e preços por moeda.\n\n"
            f"Detalhes: {erro}"
        )


def formatar_preco(
    price_cents,
    currency="BRL",
):

    if price_cents is None:
        return "—"

    moeda = str(currency or "BRL").strip().upper()
    valor = int(price_cents or 0) / 100

    if moeda == "USD":
        return f"US$ {valor:,.2f}"

    texto = (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    if moeda == "EUR":
        return f"€ {texto}"

    return f"R$ {texto}"


def formatar_preco_brl(price_cents):
    """Compatibilidade com trechos antigos que ainda esperam preço em BRL."""
    return formatar_preco(price_cents, "BRL")


# ============================================================
# RELIABILITY 2.6.19 - CHECKOUT MERCADO PAGO
# ============================================================

def criar_preferencia_mercadopago(package_code):
    """Cria uma preferência de Checkout Pro usando a Edge Function autenticada.

    O navegador nunca envia preço, quantidade de créditos ou user_id. O app
    manda somente o código do pacote e o backend valida todo o restante.
    """

    if not usuario_logado():
        raise RuntimeError(
            "Sua sessão não está autenticada. Entre novamente na conta."
        )

    access_token = str(
        st.session_state.get("access_token")
        or ""
    ).strip()

    codigo = str(
        package_code
        or ""
    ).strip().upper()

    if not access_token:
        raise RuntimeError(
            "A sessão autenticada não possui um token de acesso válido."
        )

    if not codigo:
        raise RuntimeError(
            "O pacote selecionado é inválido."
        )

    endpoint = (
        SUPABASE_URL.rstrip("/")
        + "/functions/v1/mercadopago-create-preference"
    )

    try:
        resposta = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "package_code": codigo,
            },
            timeout=20,
        )

    except requests.RequestException as erro:
        raise RuntimeError(
            "Não foi possível conectar ao serviço seguro de pagamento."
        ) from erro

    try:
        payload = resposta.json()
    except ValueError:
        payload = {}

    if resposta.status_code in {401, 403}:
        raise RuntimeError(
            "Sua sessão não foi aceita pelo serviço de pagamento. "
            "Saia da conta, entre novamente e tente outra vez."
        )

    if not resposta.ok:
        detalhe = (
            payload.get("error")
            if isinstance(payload, dict)
            else None
        )

        if detalhe:
            raise RuntimeError(str(detalhe))

        raise RuntimeError(
            f"O serviço de pagamento respondeu com HTTP {resposta.status_code}."
        )

    if not isinstance(payload, dict) or not payload.get("ok"):
        raise RuntimeError(
            "O serviço de pagamento retornou uma resposta inválida."
        )

    checkout_url = str(
        payload.get("checkout_url")
        or ""
    ).strip()

    preference_id = str(
        payload.get("preference_id")
        or ""
    ).strip()

    pacote_retorno = payload.get("package")
    if not isinstance(pacote_retorno, dict):
        pacote_retorno = {}

    codigo_retorno = str(
        pacote_retorno.get("code")
        or ""
    ).strip().upper()

    if codigo_retorno and codigo_retorno != codigo:
        raise RuntimeError(
            "O checkout retornou um pacote diferente do solicitado."
        )

    if not preference_id:
        raise RuntimeError(
            "O checkout foi criado sem identificador de preferência."
        )

    if not checkout_url.startswith("https://"):
        raise RuntimeError(
            "O serviço de pagamento não retornou uma URL HTTPS válida."
        )

    return {
        "package_code": codigo,
        "preference_id": preference_id,
        "checkout_url": checkout_url,
    }


def processar_retorno_mercadopago():
    """Registra o retorno visual do Checkout Pro sem conceder créditos.

    A query string serve apenas para UX. O saldo continua sendo alterado
    exclusivamente pelo webhook/backend após validação do pagamento.
    """

    status = str(
        st.query_params.get("payment", "")
        or ""
    ).strip().lower()

    if status not in {
        "success",
        "pending",
        "failure",
    }:
        return

    st.session_state.payment_return_status = status
    st.session_state.checkout_preference = None
    st.session_state.pagina_interface = "plans"
    st.session_state.pagina_navegacao_widget = "plans"

    # Remove parâmetros devolvidos pelo checkout para que a mensagem não seja
    # reprocessada indefinidamente em cada rerun do Streamlit.
    st.query_params.clear()


# ============================================================
# NOVO SISTEMA ATÔMICO DE CRÉDITOS
# ============================================================

def reservar_credito(
    acao,
    request_id,
):

    try:

        resposta = (
            supabase
            .rpc(
                "reserve_credit",
                {
                    "p_action": acao,
                    "p_request_id": str(request_id),
                }
            )
            .execute()
        )

        return resposta.data

    except Exception as erro:

        texto_erro = str(erro)

        if (
            "Créditos insuficientes" in texto_erro
            or
            "creditos insuficientes" in texto_erro.lower()
        ):
            raise RuntimeError(
                "💎 Você não possui créditos suficientes."
            )

        raise RuntimeError(
            "Não foi possível reservar o crédito.\n\n"
            f"Detalhes: {erro}"
        )


def concluir_uso_credito(
    request_id,
):

    try:

        resposta = (
            supabase
            .rpc(
                "complete_credit_usage",
                {
                    "p_request_id": str(request_id),
                }
            )
            .execute()
        )

        return resposta.data

    except Exception as erro:

        raise RuntimeError(
            "Não foi possível finalizar o registro "
            f"do crédito: {erro}"
        )


def devolver_credito(
    request_id,
):

    try:

        resposta = (
            supabase
            .rpc(
                "refund_credit",
                {
                    "p_request_id": str(request_id),
                }
            )
            .execute()
        )

        return resposta.data

    except Exception as erro:

        raise RuntimeError(
            "Não foi possível devolver automaticamente "
            f"o crédito: {erro}"
        )


# ============================================================
# RELIABILITY 2.5 - HISTÓRICO E RASTREABILIDADE
# ============================================================

def _rpc_scalar(valor):
    """Normaliza retornos escalares do PostgREST/Supabase RPC."""
    if isinstance(valor, list):
        if not valor:
            return None
        return valor[0]
    return valor


def _tipo_analise_auditoria(tipo_acao):
    mapa = {
        "analise_foto": "photo",
        "analise_nome": "name",
    }
    tipo = mapa.get(tipo_acao)
    if not tipo:
        raise RuntimeError(
            f"Tipo de análise não suportado pela auditoria: {tipo_acao}"
        )
    return tipo


def _nivel_confianca_banco(confianca):
    """Converte o código visual 2.4 para os níveis persistidos na 2.5."""
    codigo = str(
        (confianca or {}).get("codigo")
        or ""
    ).strip()

    mapa = {
        "confirmado_catalogo": "confirmado",
        "parcial": "parcial",
        "divergencia": "divergente",
        "nao_confirmado": "nao_confirmado",
        # Alta confiança visual continua sem confirmação externa.
        "alta_visual": "nao_confirmado",
    }

    return mapa.get(
        codigo,
        "nao_confirmado",
    )


def _motivo_confianca_auditoria(confianca):
    confianca = (
        confianca
        if isinstance(confianca, dict)
        else {}
    )

    return {
        "engine": "2.4.0",
        "codigo_original": confianca.get("codigo"),
        "rotulo": confianca.get("rotulo"),
        "mensagem": confianca.get("mensagem"),
        "evidencias": confianca.get("evidencias") or [],
        "confirmacao_externa": bool(
            confianca.get("confirmacao_externa")
        ),
        "bloqueio_divergencia": bool(
            confianca.get("bloqueio_divergencia")
        ),
    }


def _resumo_comparacao_auditoria(comparacao):
    if not isinstance(comparacao, dict):
        return None

    carta = comparacao.get("carta")
    resumo_carta = (
        _resumo_carta_catalogo(carta)
        if isinstance(carta, dict)
        else None
    )

    return {
        "score": comparacao.get("score"),
        "similaridade_nome": comparacao.get("similaridade_nome"),
        "similaridade_colecao": comparacao.get("similaridade_colecao"),
        "similaridade_numero": comparacao.get("similaridade_numero"),
        "numero_exato": bool(comparacao.get("numero_exato")),
        "nome_catalogo": comparacao.get("nome_catalogo"),
        "colecao_catalogo": comparacao.get("colecao_catalogo"),
        "numero_catalogo": comparacao.get("numero_catalogo"),
        "carta": resumo_carta,
    }


def _payload_catalogo_auditoria(validacao, cartas=None):
    validacao = (
        validacao
        if isinstance(validacao, dict)
        else {}
    )

    candidatos = []
    for item in validacao.get("candidatos") or []:
        resumo = _resumo_comparacao_auditoria(item)
        if resumo:
            candidatos.append(resumo)

    if not candidatos and cartas:
        for carta in (cartas or [])[:8]:
            if isinstance(carta, dict):
                candidatos.append({
                    "carta": _resumo_carta_catalogo(carta),
                })

    return {
        "status": validacao.get("status"),
        "titulo": validacao.get("titulo"),
        "mensagem": validacao.get("mensagem"),
        "identificacao": validacao.get("identificacao") or {},
        "melhor": _resumo_comparacao_auditoria(
            validacao.get("melhor")
        ),
        "candidatos": candidatos[:8],
    }


def iniciar_registro_analise(
    request_id,
    tipo_acao,
):
    user_id = st.session_state.get("user_id")
    if not user_id:
        raise RuntimeError(
            "Usuário não identificado para iniciar o histórico técnico."
        )

    tipo_analise = _tipo_analise_auditoria(
        tipo_acao
    )

    try:
        resposta = (
            supabase_service
            .rpc(
                "start_analysis_run",
                {
                    "p_user_id": str(user_id),
                    "p_usage_request_id": str(request_id),
                    "p_analysis_type": tipo_analise,
                    "p_app_version": APP_VERSION,
                    "p_ai_model": AI_MODEL,
                },
            )
            .execute()
        )

        run_id = _rpc_scalar(
            resposta.data
        )

        if not run_id:
            raise RuntimeError(
                "O servidor não retornou o identificador da análise."
            )

        st.session_state.analysis_run_id_atual = str(run_id)
        st.session_state.analysis_request_id_atual = str(request_id)
        st.session_state.analysis_tipo_atual = tipo_analise

        return str(run_id)

    except Exception as erro:
        raise RuntimeError(
            "Não foi possível iniciar o histórico técnico da análise. "
            f"Detalhes: {erro}"
        )


def atualizar_modelo_registro_analise(
    run_id,
    ai_model,
):
    """Atualiza o modelo que efetivamente produziu a resposta da análise."""
    if not run_id or not ai_model:
        return False

    user_id = st.session_state.get("user_id")
    if not user_id:
        return False

    try:
        resposta = (
            supabase_service
            .table("analysis_runs")
            .update({
                "ai_model": str(ai_model),
            })
            .eq("id", str(run_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        return bool(resposta.data)
    except Exception as erro:
        raise RuntimeError(
            "Não foi possível registrar o modelo de IA efetivamente usado. "
            f"Detalhes: {erro}"
        )


def concluir_registro_analise(
    run_id,
    resultado,
    ai_latency_ms=None,
):
    if not run_id:
        return False

    dados = resultado if isinstance(resultado, dict) else {}

    payload = {
        "ai_status": dados.get("status_identificacao"),
        "ai_name": dados.get("nome_carta"),
        "ai_set": dados.get("colecao_set"),
        "ai_number": dados.get("numero_carta"),
        "ai_language": dados.get("idioma_carta"),
        "ai_year": dados.get("ano"),
        "ai_variant": dados.get("variante"),
        "input_quality": dados.get("qualidade_imagem"),
        "input_quality_details": dados.get("motivo_qualidade_imagem"),
        "catalog_status": "pending",
        "confidence_reason": {
            "stage": "ai_completed_catalog_pending",
            "note": (
                "A leitura da IA foi persistida antes da validação externa "
                "do catálogo."
            ),
        },
        "ai_payload": dados,
        "ai_latency_ms": ai_latency_ms,
    }

    try:
        resposta = (
            supabase_service
            .rpc(
                "complete_analysis_run",
                {
                    "p_user_id": str(st.session_state.user_id),
                    "p_run_id": str(run_id),
                    "p_data": payload,
                },
            )
            .execute()
        )
        return bool(
            _rpc_scalar(resposta.data)
        )
    except Exception as erro:
        raise RuntimeError(
            "Não foi possível concluir o histórico técnico da análise. "
            f"Detalhes: {erro}"
        )


def falhar_registro_analise(
    run_id,
    codigo,
    mensagem,
):
    if not run_id:
        return False

    try:
        resposta = (
            supabase_service
            .rpc(
                "fail_analysis_run",
                {
                    "p_user_id": str(st.session_state.user_id),
                    "p_run_id": str(run_id),
                    "p_error_code": str(codigo or "analysis_error"),
                    "p_error_message": str(mensagem or "")[:4000],
                },
            )
            .execute()
        )
        return bool(
            _rpc_scalar(resposta.data)
        )
    except Exception:
        # A falha principal continua sendo tratada pelo fluxo da análise.
        return False


def atualizar_registro_catalogo(
    resultado,
    validacao=None,
    cartas=None,
    erro=None,
    catalogo_latency_ms=None,
):
    run_id = st.session_state.get(
        "analysis_run_id_atual"
    )

    if not run_id:
        return False

    validacao_dict = (
        validacao
        if isinstance(validacao, dict)
        else None
    )

    if erro is not None:
        http_status = _status_http_catalogo_erro(
            erro
        )
        confianca = classificar_confianca_cardcraft(
            resultado,
            validacao=None,
            catalogo_disponivel=False,
        )

        payload = {
            "catalog_status": "error",
            "catalog_http_status": http_status,
            "catalog_payload": {
                "error": str(erro)[:4000],
            },
            "catalog_latency_ms": catalogo_latency_ms,
            "confidence_level": _nivel_confianca_banco(confianca),
            "confidence_reason": _motivo_confianca_auditoria(confianca),
        }

    else:
        melhor = (
            (validacao_dict or {}).get("melhor")
            or {}
        )
        carta = melhor.get("carta") or {}
        set_dados = (
            carta.get("set")
            if isinstance(carta, dict)
            else {}
        ) or {}

        confianca = classificar_confianca_cardcraft(
            resultado,
            validacao=validacao_dict,
            catalogo_disponivel=True,
        )

        payload = {
            "catalog_status": (
                (validacao_dict or {}).get("status")
                or "sem_resultado"
            ),
            "catalog_http_status": 200,
            "catalog_card_id": (
                carta.get("id")
                if isinstance(carta, dict)
                else None
            ),
            "catalog_name": (
                carta.get("name")
                if isinstance(carta, dict)
                else None
            ),
            "catalog_set": (
                set_dados.get("name")
                if isinstance(set_dados, dict)
                else None
            ),
            "catalog_number": (
                carta.get("number")
                if isinstance(carta, dict)
                else None
            ),
            "catalog_payload": _payload_catalogo_auditoria(
                validacao_dict,
                cartas=cartas,
            ),
            "catalog_latency_ms": catalogo_latency_ms,
            "confidence_level": _nivel_confianca_banco(confianca),
            "confidence_reason": _motivo_confianca_auditoria(confianca),
        }

    try:
        resposta = (
            supabase_service
            .rpc(
                "update_analysis_catalog",
                {
                    "p_user_id": str(st.session_state.user_id),
                    "p_run_id": str(run_id),
                    "p_data": payload,
                },
            )
            .execute()
        )
        return bool(
            _rpc_scalar(resposta.data)
        )
    except Exception as erro_auditoria:
        st.session_state.aviso_auditoria = (
            "A análise foi preservada, mas o histórico técnico do catálogo "
            "não pôde ser atualizado nesta execução. "
            f"Detalhe técnico: {_sanitizar_detalhe_tecnico(erro_auditoria, 600)}"
        )
        return False


# ============================================================
# RELIABILITY 2.6 - RESILIÊNCIA OPERACIONAL E FALHAS CONTROLADAS
# ============================================================

class CardCraftOperationalError(RuntimeError):
    """Erro operacional com mensagem pública separada do detalhe técnico."""

    def __init__(
        self,
        code,
        public_message,
        technical_message="",
        retryable=False,
    ):
        super().__init__(public_message)
        self.code = str(code or "operational_error")
        self.public_message = str(public_message or "Falha operacional.")
        self.technical_message = str(technical_message or "")
        self.retryable = bool(retryable)


def _sanitizar_detalhe_tecnico(valor, limite=4000):
    """Remove segredos conhecidos antes de persistir detalhes técnicos."""
    texto = str(valor or "")

    segredos = [
        GEMINI_API_KEY,
        SUPABASE_KEY,
        SUPABASE_SERVICE_ROLE_KEY,
        POKEMON_TCG_API_KEY,
    ]

    for segredo in segredos:
        segredo = str(segredo or "")
        if segredo and len(segredo) >= 8:
            texto = texto.replace(segredo, "[REDACTED]")

    return texto[:limite]


def _classificar_erro_gemini(erro):
    """Converte falhas do SDK em códigos estáveis e mensagens seguras."""
    if isinstance(erro, CardCraftOperationalError):
        return erro

    codigo_http = getattr(erro, "code", None)
    detalhe = _sanitizar_detalhe_tecnico(erro)
    texto = detalhe.lower()

    if codigo_http == 429 or "429" in texto or "rate limit" in texto or "resource exhausted" in texto:
        return CardCraftOperationalError(
            "gemini_rate_limit",
            "O serviço de IA atingiu um limite temporário. Seu crédito será devolvido; tente novamente mais tarde.",
            detalhe,
            retryable=True,
        )

    if codigo_http in {500, 502, 503, 504} or any(
        termo in texto
        for termo in (
            "service unavailable",
            "temporarily unavailable",
            "internal server error",
            "bad gateway",
            "gateway timeout",
        )
    ):
        return CardCraftOperationalError(
            "gemini_unavailable",
            "O serviço de IA está temporariamente indisponível. Seu crédito será devolvido; tente novamente mais tarde.",
            detalhe,
            retryable=True,
        )

    if codigo_http in {401, 403} or "permission denied" in texto or "unauthorized" in texto:
        return CardCraftOperationalError(
            "gemini_auth_error",
            "A análise está temporariamente indisponível por uma configuração do serviço. Nenhum crédito será consumido.",
            detalhe,
            retryable=False,
        )

    if (
        "timeout" in texto
        or "timed out" in texto
        or "deadline exceeded" in texto
    ):
        return CardCraftOperationalError(
            "gemini_timeout",
            "A IA demorou mais do que o limite seguro para responder. Seu crédito será devolvido; tente novamente.",
            detalhe,
            retryable=True,
        )

    if codigo_http == 400:
        return CardCraftOperationalError(
            "gemini_request_error",
            "A solicitação não pôde ser processada pela IA. Nenhum crédito será consumido.",
            detalhe,
            retryable=False,
        )

    return CardCraftOperationalError(
        "gemini_error",
        "A análise não pôde ser concluída pela IA. Seu crédito será devolvido automaticamente.",
        detalhe,
        retryable=True,
    )


def _mensagem_falha_credito_pos_analise():
    return (
        "A análise foi concluída, mas houve uma inconsistência ao finalizar "
        "o registro do crédito. Não repita a análise agora. O evento ficou "
        "registrado para conferência técnica."
    )


def recuperar_analises_interrompidas_usuario():
    """
    Recupera execuções que ficaram presas em 'processing'.

    Como o Gemini possui timeout explícito de 90 s, uma execução ainda em
    processing após 15 min é tratada como interrompida. O crédito pendente é
    devolvido de forma idempotente antes de o run ser marcado como failed.
    """
    user_id = st.session_state.get("user_id")
    if not user_id:
        return 0

    limite = datetime.now(timezone.utc) - timedelta(
        minutes=ANALYSIS_STALE_MINUTES
    )

    try:
        resposta = (
            supabase_service
            .table("analysis_runs")
            .select("id,usage_request_id,created_at,status")
            .eq("user_id", str(user_id))
            .eq("status", "processing")
            .lt("created_at", limite.isoformat())
            .limit(10)
            .execute()
        )
        registros = resposta.data or []
    except Exception:
        return 0

    recuperados = 0

    for registro in registros:
        run_id = registro.get("id")
        request_id = registro.get("usage_request_id")

        if not run_id:
            continue

        # Primeiro devolvemos o crédito. A RPC de refund já é idempotente.
        if request_id:
            try:
                devolver_credito(request_id)
            except Exception:
                # Não marcamos o run como recuperado se o crédito não pôde ser
                # devolvido; assim a inconsistência permanece visível.
                continue

        falhou = falhar_registro_analise(
            run_id,
            "stale_processing_recovered",
            (
                "Execução permaneceu em processing por mais de "
                f"{ANALYSIS_STALE_MINUTES} minutos e foi recuperada "
                "automaticamente pela Reliability 2.6.2."
            ),
        )

        if falhou:
            recuperados += 1

    if recuperados:
        st.session_state.aviso_recuperacao = (
            f"♻️ O CardCraftAI recuperou {recuperados} análise(s) "
            "interrompida(s) e devolveu o crédito pendente automaticamente."
        )

    return recuperados


def talvez_recuperar_analises_interrompidas():
    """Executa a varredura no máximo uma vez por minuto por sessão."""
    agora = datetime.now(timezone.utc)
    ultima = st.session_state.get("ultima_recuperacao_runs")

    if isinstance(ultima, datetime):
        if (agora - ultima).total_seconds() < 60:
            return 0

    st.session_state.ultima_recuperacao_runs = agora
    return recuperar_analises_interrompidas_usuario()


# ============================================================
# IMAGEM
# ============================================================

def imagem_para_base64(
    imagem_pil
):

    imagem_convertida = (
        imagem_pil.convert("RGB")
    )

    buffer = BytesIO()

    imagem_convertida.save(
        buffer,
        format="JPEG",
        quality=90,
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


# ============================================================
# GEMINI
# ============================================================

def _executar_modelo_gemini(
    modelo,
    entrada,
):
    """Executa uma única tentativa estruturada em um modelo Gemini."""
    try:
        interaction = gemini_client.interactions.create(
            model=modelo,
            input=entrada,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": ANALISE_CARTA_SCHEMA,
            },
        )

        texto_json = interaction.output_text
        if not texto_json:
            raise CardCraftOperationalError(
                "gemini_empty_response",
                "A IA respondeu sem conteúdo utilizável. Seu crédito será devolvido automaticamente.",
                f"{modelo} respondeu sem output_text.",
                retryable=True,
            )

        try:
            dados = json.loads(texto_json)
        except json.JSONDecodeError as erro_json:
            raise CardCraftOperationalError(
                "gemini_invalid_json",
                "A IA respondeu em um formato inválido. Seu crédito será devolvido automaticamente.",
                (
                    f"Modelo: {modelo}. "
                    f"Erro JSON: {_sanitizar_detalhe_tecnico(erro_json)}"
                ),
                retryable=True,
            ) from erro_json

        try:
            return validar_analise_estruturada(dados)
        except Exception as erro_validacao:
            raise CardCraftOperationalError(
                "gemini_schema_validation_error",
                "A resposta da IA não passou pela validação de segurança do CardCraftAI. Seu crédito será devolvido automaticamente.",
                (
                    f"Modelo: {modelo}. "
                    f"Validação: {_sanitizar_detalhe_tecnico(erro_validacao)}"
                ),
                retryable=True,
            ) from erro_validacao

    except CardCraftOperationalError:
        raise
    except errors.APIError as erro_api:
        raise _classificar_erro_gemini(erro_api) from erro_api
    except Exception as erro:
        raise _classificar_erro_gemini(erro) from erro


def analisar_carta(
    idioma,
    imagem_pil=None,
    nome_carta_info=None,
):

    prompt_base = f"""
Voce atua como especialista em Trading Card Games (TCG), mas deve priorizar
precisao e incerteza explicita acima de completar campos.

Responda em {idioma} nos campos descritivos.

REGRAS OBRIGATORIAS:
- Retorne somente dados compativeis com o schema solicitado.
- Quando um dado nao puder ser confirmado, use null e inclua o nome do campo
  em campos_incertos.
- Nao invente colecao, numero, raridade, variante, idioma ou ano.
- Em analise por foto, o campo ano deve representar somente um ano realmente
  visivel na carta (por exemplo copyright) ou uma estimativa explicitamente
  sustentada pela imagem; nao use a data de lancamento do set como se fosse o
  ano especifico da carta.
- Quando receber dados de catalogo, releaseDate pertence ao set e deve ser
  tratada apenas como data de lancamento do set.
- Nao invente precos, vendas recentes, anuncios ou consultas a sites.
- A pesquisa web esta desativada nesta versao.
- status_identificacao e apenas a avaliacao preliminar do modelo; nao significa
  validacao contra catalogo externo.
- Use status "confirmada" somente se nome e varios identificadores relevantes
  estiverem claramente legiveis ou explicitamente fornecidos.
- Se houver fotografia, avalie a qualidade da imagem e cite evidencias visuais.
- Se a imagem estiver ruim, prefira status "incerta" e explique o motivo.
- Condicao e apenas estimativa visual; nunca atribua nota PSA, BGS ou CGC.
- Nunca declare autenticidade definitiva apenas por fotografia.
- Em autenticidade_visual, "sem_sinais_obvios" significa apenas que nada
  evidente foi observado na imagem, nao que a carta seja autentica.
- mercado.dados_atualizados_disponiveis deve ser false.
- O anuncio de venda deve evitar qualquer caracteristica nao confirmada.
"""

    if nome_carta_info:
        prompt_final = f"""
Analise a carta a partir das informacoes textuais abaixo.

Elas podem ter sido digitadas pelo usuario ou podem vir de uma entrada
explicitamente selecionada por ele no catalogo Pokemon TCG API.

{nome_carta_info}

Quando o texto identificar claramente que um campo veio do catalogo,
trate esse campo como referencia estruturada do catalogo, e nao como
uma inferencia do modelo. Nao invente campos ausentes.

{prompt_base}
"""
    else:
        prompt_final = f"""
Identifique cuidadosamente a carta presente na imagem.
Leia, quando realmente visiveis, nome, numero, set, idioma e outros marcadores.

{prompt_base}
"""

    if imagem_pil is not None:
        imagem_base64 = imagem_para_base64(imagem_pil)
        entrada = [
            {
                "type": "text",
                "text": prompt_final,
            },
            {
                "type": "image",
                "data": imagem_base64,
                "mime_type": "image/jpeg",
            },
        ]
    else:
        entrada = prompt_final

    # Reliability 2.6.2:
    # 1) tenta o modelo principal normalmente;
    # 2) somente se ele retornar limite/quota (429 / RESOURCE_EXHAUSTED),
    #    faz UMA tentativa no modelo gratuito de contingência;
    # 3) timeout, credencial, schema inválido e demais falhas não disparam
    #    o fallback para evitar duplicar latência ou mascarar erros reais.
    try:
        resultado = _executar_modelo_gemini(
            AI_MODEL,
            entrada,
        )
        return resultado, AI_MODEL

    except Exception as erro_principal:
        erro_principal_operacional = _classificar_erro_gemini(
            erro_principal
        )

        if erro_principal_operacional.code != "gemini_rate_limit":
            raise erro_principal_operacional from erro_principal

        try:
            resultado = _executar_modelo_gemini(
                AI_FALLBACK_MODEL,
                entrada,
            )
            return resultado, AI_FALLBACK_MODEL

        except Exception as erro_fallback:
            erro_fallback_operacional = _classificar_erro_gemini(
                erro_fallback
            )

            detalhe = _sanitizar_detalhe_tecnico(
                "Modelo principal: "
                f"{AI_MODEL}; erro: "
                f"{erro_principal_operacional.technical_message or erro_principal}. "
                "Modelo de contingência: "
                f"{AI_FALLBACK_MODEL}; erro: "
                f"{erro_fallback_operacional.technical_message or erro_fallback}."
            )

            if erro_fallback_operacional.code == "gemini_rate_limit":
                raise CardCraftOperationalError(
                    "gemini_all_models_rate_limited",
                    "Os modelos de IA disponíveis atingiram o limite temporário. Seu crédito será devolvido; tente novamente mais tarde.",
                    detalhe,
                    retryable=True,
                ) from erro_fallback

            raise CardCraftOperationalError(
                "gemini_fallback_failed",
                "O modelo principal atingiu o limite e o modelo de contingência também não conseguiu concluir a análise. Seu crédito será devolvido automaticamente.",
                detalhe,
                retryable=erro_fallback_operacional.retryable,
            ) from erro_fallback


# ============================================================
# EXECUTAR ANÁLISE COM RESERVA ATÔMICA
# ============================================================

def executar_analise_com_credito(
    idioma,
    imagem_pil=None,
    nome_carta_info=None,
    tipo_acao="analise",
):

    # Cada análise recebe um identificador único, compartilhado entre
    # consumo de crédito e histórico técnico.
    request_id = uuid.uuid4()
    run_id = None

    st.session_state.aviso_credito = None
    st.session_state.aviso_auditoria = None

    # ========================================================
    # 1. RESERVAR O CRÉDITO ANTES DO GEMINI
    # ========================================================

    reservar_credito(
        tipo_acao,
        request_id,
    )

    # ========================================================
    # 2. ABRIR O REGISTRO DE AUDITORIA
    # ========================================================

    try:
        run_id = iniciar_registro_analise(
            request_id,
            tipo_acao,
        )

    except Exception as erro_auditoria:
        # O Gemini ainda não foi chamado. Portanto podemos devolver
        # o crédito e impedir uma análise que ficaria sem rastreabilidade.
        try:
            devolver_credito(
                request_id
            )
        except Exception as erro_estorno:
            raise RuntimeError(
                "Não foi possível iniciar o histórico técnico e também "
                "houve falha ao devolver o crédito reservado.\n\n"
                f"Erro da auditoria: {erro_auditoria}\n\n"
                f"Erro do estorno: {erro_estorno}"
            )

        raise RuntimeError(
            "A análise não foi iniciada porque o histórico técnico "
            "não pôde ser aberto.\n\n"
            "✅ O crédito reservado foi devolvido automaticamente.\n\n"
            f"Detalhes: {erro_auditoria}"
        )

    # ========================================================
    # 3. CHAMAR O GEMINI E MEDIR LATÊNCIA
    # ========================================================

    inicio_ia = time.perf_counter()

    try:
        resultado, modelo_ia_usado = analisar_carta(
            idioma=idioma,
            imagem_pil=imagem_pil,
            nome_carta_info=nome_carta_info,
        )

        ai_latency_ms = int(
            (time.perf_counter() - inicio_ia)
            * 1000
        )

    except Exception as erro_gemini:
        ai_latency_ms = int(
            (time.perf_counter() - inicio_ia)
            * 1000
        )

        erro_operacional = _classificar_erro_gemini(
            erro_gemini
        )

        falhar_registro_analise(
            run_id,
            erro_operacional.code,
            _sanitizar_detalhe_tecnico(
                erro_operacional.technical_message
                or erro_gemini
            ),
        )

        # ====================================================
        # 4. GEMINI FALHOU -> DEVOLVER CRÉDITO
        # ====================================================

        try:
            devolver_credito(
                request_id
            )

        except Exception as erro_estorno:
            # Não mostramos detalhes internos ou chaves ao usuário.
            st.session_state.aviso_credito = (
                "A análise falhou e o estorno automático do crédito "
                "não pôde ser confirmado. Não repita a análise agora; "
                "o evento ficou registrado para conferência técnica."
            )
            raise RuntimeError(
                st.session_state.aviso_credito
            ) from erro_estorno

        raise RuntimeError(
            f"{erro_operacional.public_message}\n\n"
            "✅ O crédito reservado foi devolvido automaticamente."
        ) from erro_gemini

    # ========================================================
    # 5. PERSISTIR A LEITURA DA IA
    # ========================================================

    try:
        # O run é aberto com o modelo principal. Se houve fallback,
        # registramos o modelo que efetivamente produziu a resposta.
        if modelo_ia_usado != AI_MODEL:
            atualizar_modelo_registro_analise(
                run_id,
                modelo_ia_usado,
            )

        concluir_registro_analise(
            run_id,
            resultado,
            ai_latency_ms=ai_latency_ms,
        )
    except Exception as erro_auditoria:
        # O Gemini já executou. A análise continua sendo entregue e
        # o crédito não é estornado; apenas registramos o incidente.
        st.session_state.aviso_auditoria = (
            "A análise foi concluída, mas o histórico técnico não pôde "
            "ser finalizado nesta execução. "
            f"Detalhe técnico: {_sanitizar_detalhe_tecnico(erro_auditoria, 600)}"
        )

    # ========================================================
    # 6. GEMINI FUNCIONOU -> CONFIRMAR CONSUMO
    # ========================================================

    try:
        confirmado = concluir_uso_credito(
            request_id
        )

        if confirmado is False:
            st.session_state.aviso_credito = (
                "A análise foi concluída, mas o registro "
                "de consumo ficou pendente. "
                "Não repita esta análise."
            )

    except Exception as erro_confirmacao:
        # NÃO fazemos estorno aqui:
        # o Gemini já executou e a análise foi entregue.
        # O detalhe técnico não é exibido para evitar vazamento acidental.
        st.session_state.aviso_credito = (
            _mensagem_falha_credito_pos_analise()
        )

    return resultado


# ============================================================
# DOCUMENTOS LEGAIS - BETA 2.6.15
# ============================================================

LEGAL_VERSION = "2026-09-13"
TERMS_VERSION = LEGAL_VERSION
PRIVACY_VERSION = LEGAL_VERSION


def renderizar_termos_uso(idioma_atual="English"):
    """Exibe os Termos de Uso em linguagem simples e compatível com a fase beta."""

    if idioma_atual == "English":
        titulo = "📜 Terms of Use"
        texto = f"""
**Legal version:** {LEGAL_VERSION}  
**Product:** CardCraftAI — beta

### 1. Service
CardCraftAI is an AI-assisted tool for identifying, organizing and analyzing Trading Card Game (TCG) cards. Features may include visual identification, catalog comparison, descriptive analysis, account credits and purchase history.

### 2. AI limitations
AI and catalog results can be incomplete, outdated or incorrect. CardCraftAI does **not** guarantee exact identification, authenticity, professional grading, market value, investment return or sale price. Any condition or authenticity indication is only a preliminary visual aid and does not replace evaluation by PSA, CGC, Beckett, a qualified dealer or another specialist.

### 3. Market information
When current market search is unavailable, CardCraftAI will not represent estimated values as live market prices. Users should verify prices, recent sales and listing conditions through independent sources before buying, selling or insuring a card.

### 4. User responsibilities
You are responsible for the images, text and information you submit and must have the right to use them. The service must not be used for fraud, counterfeit listings, impersonation, unlawful activity, harassment, security abuse or attempts to bypass credits or access controls.

### 5. Accounts and security
You are responsible for protecting your password and access to your email account. Notify CardCraftAI through the official support channel when available if you suspect unauthorized access.

### 6. Credits and paid services
Credits represent permission to use eligible CardCraftAI features and are not currency, an investment or a stored-value account. Prices, packages, payment methods and refund rules will be displayed before purchase. Mandatory consumer rights applicable in your jurisdiction are not waived by these Terms.

### 7. Availability
The service may be modified, suspended or temporarily unavailable for maintenance, provider outages, rate limits, security incidents or technical failures. CardCraftAI may automatically refund a consumed credit when an eligible analysis fails before completion.

### 8. Intellectual property
The CardCraftAI software, interface, brand and original content are protected by applicable intellectual-property rules. TCG names, card images, trademarks and third-party catalog data belong to their respective owners. CardCraftAI is not affiliated with or endorsed by those rights holders unless expressly stated.

### 9. Limitation of use
Decisions involving purchases, sales, insurance, taxes, legal matters or significant financial value should not rely exclusively on an AI result. Use the service as an informational aid and independently verify important decisions.

### 10. Changes
These Terms may be updated as the product, providers or legal requirements evolve. The current version date is displayed above. A commercial launch will include a published official support/privacy contact.

By continuing to use CardCraftAI, you acknowledge these limitations and agree to use the service responsibly.
"""

    elif idioma_atual == "Español":
        titulo = "📜 Términos de Uso"
        texto = f"""
**Versión legal:** {LEGAL_VERSION}  
**Producto:** CardCraftAI — beta

### 1. Servicio
CardCraftAI es una herramienta asistida por inteligencia artificial para identificar, organizar y analizar cartas de Trading Card Games (TCG). Puede incluir identificación visual, comparación con catálogos, análisis descriptivo, créditos de cuenta e historial de compras.

### 2. Límites de la IA
Los resultados de IA y catálogo pueden ser incompletos, desactualizados o incorrectos. CardCraftAI **no** garantiza identificación exacta, autenticidad, grading profesional, valor de mercado, retorno de inversión ni precio de venta. Cualquier indicación de estado o autenticidad es solo una ayuda visual preliminar.

### 3. Información de mercado
Cuando la búsqueda de mercado actual no esté disponible, CardCraftAI no presentará estimaciones como precios en tiempo real. Verifica precios, ventas recientes y condiciones de anuncios en fuentes independientes antes de comprar, vender o asegurar una carta.

### 4. Responsabilidad del usuario
Eres responsable de las imágenes, textos e información que envías y debes tener derecho a utilizarlos. El servicio no puede usarse para fraude, falsificaciones, suplantación, actividades ilegales, acoso, abuso de seguridad ni intentos de eludir créditos o controles de acceso.

### 5. Cuenta y seguridad
Debes proteger tu contraseña y el acceso a tu correo electrónico. Si sospechas acceso no autorizado, utiliza el canal oficial de soporte cuando esté disponible.

### 6. Créditos y servicios de pago
Los créditos permiten utilizar funciones elegibles de CardCraftAI y no son moneda, inversión ni saldo financiero. Precios, paquetes, métodos de pago y reglas de reembolso se mostrarán antes de la compra. Los derechos obligatorios del consumidor de tu jurisdicción permanecen vigentes.

### 7. Disponibilidad
El servicio puede cambiar, suspenderse o quedar temporalmente indisponible por mantenimiento, fallos de proveedores, límites de uso, incidentes de seguridad o errores técnicos. Cuando corresponda, un crédito puede devolverse automáticamente si un análisis falla antes de completarse.

### 8. Propiedad intelectual
El software, la interfaz, la marca y el contenido original de CardCraftAI están protegidos. Nombres de TCG, imágenes de cartas, marcas y datos de catálogos externos pertenecen a sus respectivos titulares. CardCraftAI no está afiliado ni respaldado por ellos salvo indicación expresa.

### 9. Uso responsable
No tomes decisiones relevantes de compra, venta, seguros, impuestos o finanzas basándote únicamente en una respuesta de IA. Utiliza el servicio como apoyo informativo y verifica de forma independiente las decisiones importantes.

### 10. Cambios
Estos términos pueden actualizarse cuando cambien el producto, los proveedores o los requisitos legales. La fecha de la versión vigente aparece arriba. Antes del lanzamiento comercial se publicará un canal oficial de soporte y privacidad.
"""

    elif idioma_atual == "日本語":
        titulo = "📜 利用規約"
        texto = f"""
**法的文書の版:** {LEGAL_VERSION}  
**製品:** CardCraftAI — ベータ

### 1. サービス
CardCraftAI は、Trading Card Game（TCG）カードの識別、整理、分析を支援するAIツールです。画像による識別、カタログ比較、説明的分析、アカウントクレジット、購入履歴などの機能を提供する場合があります。

### 2. AIの制限
AIおよびカタログの結果は、不完全、古い、または誤っている場合があります。CardCraftAI は、正確な識別、真贋、専門的なグレーディング、市場価格、投資収益、販売価格を保証しません。状態や真贋に関する表示は予備的な視覚支援であり、PSA、CGC、Beckett、専門店などによる評価の代替ではありません。

### 3. 市場情報
現在の市場検索が利用できない場合、推定値をリアルタイム価格として表示しません。購入、販売、保険などの重要な判断を行う前に、価格、最近の取引、出品条件を独立した情報源で確認してください。

### 4. ユーザーの責任
送信する画像、文章、情報について、ユーザーは適切な利用権を持つ必要があります。詐欺、偽造品の出品、なりすまし、違法行為、嫌がらせ、セキュリティの悪用、クレジットやアクセス制御の回避にサービスを利用してはいけません。

### 5. アカウントとセキュリティ
パスワードおよび登録メールへのアクセスを安全に管理してください。不正アクセスが疑われる場合は、公式サポート窓口が公開された後、その窓口を利用してください。

### 6. クレジットと有料サービス
クレジットは対象機能を利用するための権利であり、通貨、投資、預金残高ではありません。価格、パッケージ、決済方法、返金条件は購入前に表示されます。適用法上の消費者保護権は本規約によって放棄されません。

### 7. 可用性
保守、外部サービス障害、API制限、セキュリティ事象、技術障害などにより、サービスが変更、停止、一時利用不可になる場合があります。対象となる分析が完了前に失敗した場合、クレジットが自動返却されることがあります。

### 8. 知的財産
CardCraftAI のソフトウェア、インターフェース、ブランド、独自コンテンツは適用される知的財産法により保護されます。TCG名、カード画像、商標、外部カタログデータは各権利者に帰属します。明示されない限り、CardCraftAI はこれらの権利者と提携または承認関係にありません。

### 9. 責任ある利用
購入、販売、保険、税務、法務、重要な金銭判断をAI結果だけに依存して行わないでください。CardCraftAI は情報支援として利用し、重要な判断は独立して確認してください。

### 10. 変更
製品、外部提供者、法的要件の変化に応じて本規約を更新することがあります。現行版の日付は上部に表示されます。商用公開前に公式サポート／プライバシー窓口を公開します。

CardCraftAI を継続して利用することで、これらの制限を理解し、責任を持ってサービスを利用することに同意したものとみなされます。
"""

    else:
        titulo = "📜 Termos de Uso"
        texto = f"""
**Versão legal:** {LEGAL_VERSION}  
**Produto:** CardCraftAI — beta

### 1. Sobre o serviço
O CardCraftAI é uma ferramenta assistida por inteligência artificial para identificação, organização e análise de cartas de Trading Card Games (TCG). Os recursos podem incluir identificação visual, comparação com catálogo, análise descritiva, créditos de uso e histórico de compras.

### 2. Limitações da inteligência artificial
Resultados de IA e de catálogo podem ser incompletos, desatualizados ou incorretos. O CardCraftAI **não garante** identificação exata, autenticidade, grading profissional, valor de mercado, retorno de investimento ou preço de venda. Indicações de conservação ou autenticidade são apenas apoio visual preliminar e não substituem avaliação de PSA, CGC, Beckett, loja especializada ou outro profissional qualificado.

### 3. Informações de mercado
Quando a consulta de mercado atual estiver indisponível, o CardCraftAI não apresentará estimativas como se fossem preços em tempo real. Antes de comprar, vender ou segurar uma carta, o usuário deve verificar preços, vendas recentes e condições do anúncio em fontes independentes.

### 4. Responsabilidades do usuário
Você é responsável pelas imagens, textos e informações enviados ao serviço e deve possuir autorização para utilizá-los. É proibido usar o CardCraftAI para fraude, anúncios de falsificações, falsidade ideológica, atividade ilegal, assédio, abuso de segurança ou tentativa de burlar créditos e controles de acesso.

### 5. Conta e segurança
Você é responsável por proteger sua senha e o acesso ao e-mail vinculado à conta. Em caso de suspeita de acesso não autorizado, utilize o canal oficial de suporte assim que ele estiver disponível.

### 6. Créditos e serviços pagos
Créditos representam autorização de uso de funcionalidades elegíveis do CardCraftAI. Não são moeda, investimento nem conta de valor armazenado. Preços, pacotes, meios de pagamento e regras de reembolso serão apresentados antes da compra. Direitos obrigatórios do consumidor previstos na legislação aplicável não são afastados por estes Termos.

### 7. Disponibilidade e falhas
O serviço pode ser alterado, suspenso ou ficar temporariamente indisponível por manutenção, indisponibilidade de fornecedores, limites de API, incidentes de segurança ou falhas técnicas. Quando aplicável, o sistema poderá devolver automaticamente o crédito de uma análise que falhou antes da conclusão.

### 8. Propriedade intelectual
O software, a interface, a marca e o conteúdo original do CardCraftAI são protegidos pela legislação aplicável. Nomes de TCG, imagens de cartas, marcas e dados de catálogos externos pertencem aos respectivos titulares. O CardCraftAI não é afiliado ou endossado por esses titulares, salvo quando houver indicação expressa.

### 9. Uso responsável
Decisões relevantes de compra, venda, seguro, tributação, questões jurídicas ou valores financeiros significativos não devem se basear exclusivamente em uma resposta de IA. Utilize o CardCraftAI como apoio informativo e verifique decisões importantes por meios independentes.

### 10. Alterações
Estes Termos poderão ser atualizados conforme o produto, os fornecedores ou os requisitos legais evoluírem. A data da versão vigente aparece no topo. Antes do lançamento comercial, o CardCraftAI publicará um canal oficial de suporte e privacidade.

Ao continuar utilizando o CardCraftAI, você reconhece essas limitações e concorda em utilizar o serviço de forma responsável.
"""

    st.header(titulo)
    st.markdown(texto)


def renderizar_politica_privacidade(idioma_atual="English"):
    """Exibe uma política de privacidade transparente para a fase beta."""

    if idioma_atual == "English":
        titulo = "🔒 Privacy Policy"
        texto = f"""
**Privacy version:** {LEGAL_VERSION}  
**Product:** CardCraftAI — beta

### 1. Data we process
Depending on how you use the service, CardCraftAI may process account information (such as email, user ID, plan and credits), authentication/session data, usage and technical logs, analysis status, catalog selections, purchase records when available, and the card image or text that you intentionally submit for analysis.

### 2. Why we use the data
We use this information to authenticate accounts, provide analyses, control credits, prevent duplicate charges, recover interrupted operations, display account and purchase history, send transactional emails, investigate failures, protect the service and improve reliability.

### 3. Card images and AI processing
When you submit a card image for AI analysis, the application converts it for processing and sends the analysis request to the configured AI provider. In the current architecture, CardCraftAI does not intentionally store the uploaded card image in its own Supabase database. Hosting and AI providers may nevertheless process technical data according to their own terms and privacy policies.

### 4. Service providers
The current technical stack may involve Supabase for authentication/database, Streamlit for application hosting, Google Gemini for AI processing, Brevo for transactional email and an external TCG catalog provider for card search/validation. Payment providers may be added when checkout is enabled. Each provider processes data under its own terms and security controls.

### 5. International processing
Because some technology providers operate globally, data may be processed outside your country. CardCraftAI intends to use providers and safeguards appropriate to the applicable legal requirements before international commercial expansion.

### 6. Retention
Account, credit, purchase and technical records may be retained while needed to provide the service, maintain security, resolve disputes, prevent duplicate charges and comply with applicable legal obligations. Data that is no longer necessary should be deleted or anonymized according to the applicable retention process.

### 7. Your privacy rights
Depending on your jurisdiction, you may have rights to obtain information about processing, access, correct, delete, restrict or object to certain processing, request portability, or exercise other rights provided by applicable law. These rights can have legal exceptions.

### 8. Sale of personal data
The current CardCraftAI design does not sell users' personal data.

### 9. Security
CardCraftAI uses authentication, email confirmation, access controls, database policies and server-side secrets to reduce unauthorized access. No online system can guarantee absolute security.

### 10. Children and minors
The beta service is not designed to intentionally collect sensitive information from children. Users who are not legally able to accept these terms should use the service only with authorization from a parent or legal guardian and subject to local law.

### 11. Updates and contact
This Policy may change as the product and legal obligations evolve. The current version date appears above. An official privacy/support contact will be published before commercial launch.
"""

    elif idioma_atual == "Español":
        titulo = "🔒 Política de Privacidad"
        texto = f"""
**Versión de privacidad:** {LEGAL_VERSION}  
**Producto:** CardCraftAI — beta

### 1. Datos tratados
Según el uso del servicio, CardCraftAI puede tratar datos de cuenta (como correo electrónico, ID de usuario, plan y créditos), autenticación y sesión, registros técnicos y de uso, estado de análisis, selecciones de catálogo, compras cuando existan y la imagen o texto de la carta que envíes voluntariamente para análisis.

### 2. Finalidades
Utilizamos estos datos para autenticar cuentas, entregar análisis, controlar créditos, evitar cobros duplicados, recuperar operaciones interrumpidas, mostrar historial de cuenta y compras, enviar correos transaccionales, investigar fallos, proteger el servicio y mejorar su fiabilidad.

### 3. Imágenes e inteligencia artificial
Cuando envías una imagen para análisis, la aplicación la prepara y envía la solicitud al proveedor de IA configurado. En la arquitectura actual, CardCraftAI no guarda intencionalmente la imagen cargada en su propia base de datos Supabase. Los proveedores de hosting e IA pueden tratar datos técnicos conforme a sus propias políticas.

### 4. Proveedores
La infraestructura actual puede utilizar Supabase, Streamlit, Google Gemini, Brevo y un proveedor externo de catálogo TCG. Se podrán añadir proveedores de pago cuando el checkout esté activo. Cada proveedor trata datos según sus propios términos y controles de seguridad.

### 5. Tratamiento internacional
Algunos proveedores tecnológicos operan globalmente, por lo que los datos pueden tratarse fuera de tu país. Antes de la expansión comercial internacional, CardCraftAI pretende aplicar proveedores y salvaguardas adecuadas a las obligaciones legales aplicables.

### 6. Conservación
Los datos de cuenta, créditos, compras y registros técnicos pueden conservarse mientras sean necesarios para prestar el servicio, proteger la seguridad, resolver disputas, evitar cobros duplicados y cumplir obligaciones legales. Los datos que dejen de ser necesarios deberán eliminarse o anonimizarse según el proceso aplicable.

### 7. Tus derechos
Según tu jurisdicción, puedes tener derechos de información, acceso, corrección, eliminación, limitación, oposición, portabilidad u otros previstos por la ley, sujetos a excepciones legales.

### 8. Venta de datos
El diseño actual de CardCraftAI no vende datos personales de los usuarios.

### 9. Seguridad
CardCraftAI utiliza autenticación, confirmación de correo, controles de acceso, políticas de base de datos y secretos del servidor para reducir accesos no autorizados. Ningún sistema en línea puede garantizar seguridad absoluta.

### 10. Menores
La versión beta no está diseñada para recopilar intencionalmente información sensible de menores. Quien no pueda aceptar legalmente estos términos debe utilizar el servicio solo con autorización de padre, madre o tutor y de acuerdo con la legislación local.

### 11. Actualizaciones y contacto
Esta Política puede cambiar con el producto y las obligaciones legales. La fecha de la versión vigente aparece arriba. Antes del lanzamiento comercial se publicará un canal oficial de privacidad y soporte.
"""

    elif idioma_atual == "日本語":
        titulo = "🔒 プライバシーポリシー"
        texto = f"""
**プライバシー版:** {LEGAL_VERSION}  
**製品:** CardCraftAI — ベータ

### 1. 処理するデータ
利用状況に応じて、CardCraftAI はメールアドレス、ユーザーID、プラン、クレジットなどのアカウント情報、認証・セッション情報、利用・技術ログ、分析状態、カタログ選択、購入記録、および分析のためにユーザーが意図的に送信したカード画像や文章を処理する場合があります。

### 2. 利用目的
これらの情報は、認証、分析提供、クレジット管理、重複請求防止、中断した処理の復旧、アカウント・購入履歴の表示、取引メール送信、障害調査、サービス保護、信頼性向上のために利用します。

### 3. カード画像とAI処理
カード画像をAI分析に送信すると、アプリは画像を処理用に準備し、設定されたAI提供者へ分析リクエストを送ります。現在の構成では、CardCraftAI はアップロード画像を自社のSupabaseデータベースへ意図的に保存しません。ただし、ホスティングやAI提供者は各社の規約・プライバシーポリシーに基づき技術データを処理する場合があります。

### 4. サービス提供者
現在の技術構成では、認証・DBにSupabase、ホスティングにStreamlit、AIにGoogle Gemini、取引メールにBrevo、カード検索・検証に外部TCGカタログを利用する場合があります。チェックアウト導入時には決済提供者が追加される場合があります。

### 5. 国際的な処理
一部の技術提供者は世界各地で運用されているため、データがユーザーの国以外で処理される場合があります。国際的な商用展開前に、適用法に応じた提供者と保護措置を採用する方針です。

### 6. 保持期間
アカウント、クレジット、購入、技術記録は、サービス提供、セキュリティ維持、紛争対応、重複請求防止、法的義務への対応に必要な期間保持される場合があります。不要となったデータは適用される保持方針に従って削除または匿名化されるべきです。

### 7. プライバシー権
法域により、処理内容の確認、アクセス、訂正、削除、制限、異議申立て、データポータビリティなどの権利が認められる場合があります。これらには法的例外が適用される場合があります。

### 8. 個人データの販売
現在のCardCraftAIの設計では、ユーザーの個人データを販売しません。

### 9. セキュリティ
CardCraftAI は、認証、メール確認、アクセス制御、データベースポリシー、サーバー側シークレットなどを使用して不正アクセスの低減に努めます。ただし、オンラインシステムで絶対的な安全性を保証することはできません。

### 10. 子ども・未成年者
ベータ版は、子どもの機微情報を意図的に収集することを目的としていません。法的に本規約へ同意できないユーザーは、現地法に従い、親または法定代理人の許可・監督のもとで利用してください。

### 11. 更新と連絡先
製品および法的義務の変化に応じて本ポリシーを更新する場合があります。現行版の日付は上部に表示されます。商用公開前に公式のプライバシー／サポート窓口を公開します。
"""

    else:
        titulo = "🔒 Política de Privacidade"
        texto = f"""
**Versão de privacidade:** {LEGAL_VERSION}  
**Produto:** CardCraftAI — beta

### 1. Dados tratados
Conforme o uso do serviço, o CardCraftAI pode tratar dados de conta (como e-mail, ID do usuário, plano e créditos), dados de autenticação e sessão, registros técnicos e de uso, status de análises, seleções de catálogo, registros de compras quando existirem e a imagem ou o texto da carta que você enviar voluntariamente para análise.

### 2. Finalidades
Esses dados são utilizados para autenticar contas, entregar análises, controlar créditos, evitar cobranças duplicadas, recuperar operações interrompidas, exibir histórico da conta e de compras, enviar e-mails transacionais, investigar falhas, proteger o serviço e melhorar a confiabilidade.

### 3. Imagens e processamento por IA
Quando você envia a foto de uma carta para análise por IA, o aplicativo prepara a imagem e envia a solicitação ao provedor de inteligência artificial configurado. Na arquitetura atual, o CardCraftAI não salva intencionalmente a imagem enviada em seu próprio banco de dados Supabase. Provedores de hospedagem e IA podem, contudo, processar dados técnicos conforme seus próprios termos e políticas de privacidade.

### 4. Prestadores de serviço
A infraestrutura atual pode utilizar Supabase para autenticação e banco de dados, Streamlit para hospedagem do aplicativo, Google Gemini para processamento por IA, Brevo para e-mails transacionais e um provedor externo de catálogo TCG para busca e validação de cartas. Provedores de pagamento poderão ser adicionados quando o checkout estiver ativo. Cada fornecedor trata dados conforme seus próprios termos e controles de segurança.

### 5. Tratamento internacional
Alguns fornecedores de tecnologia operam globalmente, de modo que dados podem ser processados fora do seu país. Antes da expansão comercial internacional, o CardCraftAI pretende adotar fornecedores e salvaguardas adequadas às exigências legais aplicáveis.

### 6. Retenção
Dados de conta, créditos, compras e registros técnicos podem ser mantidos enquanto forem necessários para prestar o serviço, manter a segurança, resolver disputas, evitar cobranças duplicadas e cumprir obrigações legais aplicáveis. Dados que deixarem de ser necessários deverão ser eliminados ou anonimizados conforme o processo de retenção aplicável.

### 7. Seus direitos de privacidade
Dependendo da sua jurisdição, você pode ter direitos de confirmação do tratamento, acesso, correção, exclusão, limitação, oposição, portabilidade e outros previstos pela legislação aplicável, sujeitos às exceções legais. No Brasil, esses direitos decorrem, entre outras normas, da LGPD.

### 8. Venda de dados pessoais
O desenho atual do CardCraftAI não vende dados pessoais dos usuários.

### 9. Segurança
O CardCraftAI utiliza autenticação, confirmação de e-mail, controles de acesso, políticas de banco de dados e segredos mantidos no servidor para reduzir acessos não autorizados. Nenhum sistema conectado à internet pode garantir segurança absoluta.

### 10. Crianças e adolescentes
A versão beta não é projetada para coletar intencionalmente informações sensíveis de crianças. Usuários que não tenham capacidade legal para aceitar estes termos devem utilizar o serviço apenas com autorização e acompanhamento de responsável legal, observando a legislação local.

### 11. Atualizações e contato
Esta Política poderá ser atualizada conforme o produto e as obrigações legais evoluírem. A data da versão vigente aparece no topo. Antes do lançamento comercial, o CardCraftAI publicará um canal oficial de privacidade e suporte.
"""

    st.header(titulo)
    st.markdown(texto)


# ============================================================
# RELIABILITY 2.6.15 - ACEITE LEGAL PARA CONTAS EXISTENTES
# ============================================================

def buscar_aceite_legal_vigente():
    """Retorna o aceite da versão legal vigente para o usuário autenticado."""
    user_id = st.session_state.get("user_id")

    if not user_id:
        return None

    try:
        resposta = (
            supabase
            .table("legal_acceptances")
            .select(
                "id,user_id,terms_version,privacy_version,accepted_at,"
                "app_version,locale,acceptance_source,created_at"
            )
            .eq("user_id", str(user_id))
            .eq("terms_version", TERMS_VERSION)
            .eq("privacy_version", PRIVACY_VERSION)
            .limit(1)
            .execute()
        )

        dados = resposta.data or []
        return dados[0] if dados else None

    except Exception as erro:
        raise RuntimeError(
            "Não foi possível verificar o aceite dos documentos legais. "
            f"Detalhes: {erro}"
        )


def registrar_aceite_legal_vigente(idioma_atual="English"):
    """Registra, via RPC protegida, o aceite da versão legal vigente."""
    locale = LANGUAGE_LOCALES.get(idioma_atual, "en")

    try:
        resposta = (
            supabase
            .rpc(
                "record_legal_acceptance",
                {
                    "p_terms_version": TERMS_VERSION,
                    "p_privacy_version": PRIVACY_VERSION,
                    "p_app_version": APP_VERSION,
                    "p_locale": locale,
                },
            )
            .execute()
        )

        return resposta.data

    except Exception as erro:
        raise RuntimeError(
            "Não foi possível registrar o aceite dos documentos legais. "
            f"Detalhes: {erro}"
        )


def tela_aceite_legal_pendente():
    """Bloqueia o uso do app até a conta aceitar a versão legal vigente."""
    st.title("🃏 CardCraftAI")
    st.header("📜 Atualização dos documentos legais")

    idioma_legal = renderizar_seletor_idioma(
        st,
        "idioma_legal_widget",
    )

    if idioma_legal == "English":
        st.info(
            "Before continuing, please review and accept the current "
            "Terms of Use and Privacy Policy."
        )
        texto_checkbox = (
            "I have read and accept the Terms of Use and Privacy Policy."
        )
        texto_botao = "✅ Accept and continue"
        texto_alerta = (
            "You must accept the Terms of Use and Privacy Policy to continue."
        )
        texto_sucesso = "Acceptance recorded. You can now continue. ✅"
        texto_sair = "🚪 Sign out"
    elif idioma_legal == "Español":
        st.info(
            "Antes de continuar, revisa y acepta los Términos de Uso "
            "y la Política de Privacidad vigentes."
        )
        texto_checkbox = (
            "He leído y acepto los Términos de Uso y la Política de Privacidad."
        )
        texto_botao = "✅ Aceptar y continuar"
        texto_alerta = (
            "Debes aceptar los Términos de Uso y la Política de Privacidad "
            "para continuar."
        )
        texto_sucesso = "Aceptación registrada. Ya puedes continuar. ✅"
        texto_sair = "🚪 Cerrar sesión"
    elif idioma_legal == "日本語":
        st.info("続行する前に、現行の利用規約とプライバシーポリシーを確認し、同意してください。")
        texto_checkbox = "利用規約とプライバシーポリシーを読み、同意します。"
        texto_botao = "✅ 同意して続行"
        texto_alerta = "続行するには利用規約とプライバシーポリシーへの同意が必要です。"
        texto_sucesso = "同意を記録しました。続行できます。✅"
        texto_sair = "🚪 ログアウト"
    else:
        st.info(
            "Antes de continuar, revise e aceite os Termos de Uso e a "
            "Política de Privacidade vigentes."
        )
        texto_checkbox = (
            "Li e aceito os Termos de Uso e a Política de Privacidade."
        )
        texto_botao = "✅ Aceitar e continuar"
        texto_alerta = (
            "Você precisa aceitar os Termos de Uso e a Política de "
            "Privacidade para continuar."
        )
        texto_sucesso = "Aceite registrado. Você já pode continuar. ✅"
        texto_sair = "🚪 Sair da conta"

    st.caption(
        f"Versão vigente: {LEGAL_VERSION} | CardCraftAI {APP_VERSION}"
    )

    with st.expander("📜 Termos de Uso / Terms of Use", expanded=False):
        renderizar_termos_uso(idioma_legal)

    with st.expander(
        "🔒 Política de Privacidade / Privacy Policy",
        expanded=False,
    ):
        renderizar_politica_privacidade(idioma_legal)

    aceitou = st.checkbox(
        texto_checkbox,
        key="aceite_legal_conta_existente",
    )

    if st.button(
        texto_botao,
        use_container_width=True,
        key="btn_aceite_legal_conta_existente",
    ):
        if not aceitou:
            st.warning(texto_alerta)
        else:
            try:
                registrar_aceite_legal_vigente(idioma_legal)
                st.success(texto_sucesso)
                st.rerun()
            except Exception as erro:
                st.error(
                    "Não foi possível registrar o aceite agora."
                )
                st.caption(
                    f"Detalhe técnico: {erro}"
                )

    st.divider()

    if st.button(
        texto_sair,
        use_container_width=True,
        key="btn_sair_aceite_legal",
    ):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        limpar_sessao()
        st.rerun()


# ============================================================
# TELA DE LOGIN / CADASTRO
# ============================================================

def tela_login():
    idioma = renderizar_seletor_idioma(
        st,
        "idioma_login_widget",
    )

    st.title("🃏 CardCraftAI")
    st.subheader(t("tagline_login", idioma))
    st.divider()
    st.header(t("access_account", idioma))

    if st.session_state.senha_redefinida_sucesso:
        st.success(t("password_reset_success", idioma))
        st.session_state.senha_redefinida_sucesso = False

    if st.session_state.erro_recuperacao_senha:
        st.error(st.session_state.erro_recuperacao_senha)
        st.session_state.erro_recuperacao_senha = None

    aba_login, aba_cadastro = st.tabs([
        t("tab_login", idioma),
        t("tab_signup", idioma),
    ])

    with aba_login:
        st.write(t("login_intro", idioma))
        st.caption(t("email_confirm_hint", idioma))

        email_login = st.text_input(
            t("email", idioma), key="email_login", placeholder=t("email_placeholder", idioma)
        )
        senha_login = st.text_input(
            t("password", idioma), type="password", key="senha_login"
        )

        if st.button(t("sign_in", idioma), use_container_width=True, key="btn_login"):
            if not email_login.strip() or not senha_login:
                st.warning(t("fill_email_password", idioma))
            else:
                try:
                    resposta = supabase.auth.sign_in_with_password({
                        "email": email_login.strip().lower(),
                        "password": senha_login,
                    })
                    if salvar_sessao(resposta):
                        # Garante que a primeira renderização autenticada use
                        # exatamente o idioma escolhido antes do login. A chave
                        # do seletor da sidebar ainda não foi instanciada nesta
                        # execução, portanto pode ser preparada com segurança.
                        st.session_state.idioma_interface = idioma
                        st.session_state.idioma_sidebar_widget = idioma
                        st.session_state.pagina_interface = "photo"
                        st.success(t("login_success", idioma))
                        st.rerun()
                    else:
                        st.error(t("session_failed", idioma))
                except Exception:
                    st.error(t("login_failed", idioma))
                    st.info(t("check_credentials", idioma))

        if st.button(t("forgot_password", idioma), use_container_width=True, key="btn_mostrar_recuperacao_senha"):
            st.session_state.mostrar_recuperacao_senha = not st.session_state.mostrar_recuperacao_senha

        if st.session_state.mostrar_recuperacao_senha:
            st.divider()
            st.subheader(t("recover_access", idioma))
            st.caption(t("recover_caption", idioma))
            email_recuperacao = st.text_input(
                t("recovery_email", idioma), key="email_recuperacao_senha", placeholder=t("email_placeholder", idioma)
            )
            if st.button(t("send_recovery", idioma), use_container_width=True, key="btn_enviar_recuperacao_senha"):
                email_recuperacao = email_recuperacao.strip().lower()
                if not email_recuperacao:
                    st.warning(t("enter_email", idioma))
                else:
                    try:
                        supabase.auth.reset_password_for_email(email_recuperacao)
                        st.success(t("recovery_sent", idioma))
                        st.caption(t("check_spam", idioma))
                    except Exception:
                        st.error(t("recovery_request_failed", idioma))
                        st.info(t("try_again_later", idioma))

    with aba_cadastro:
        st.write(t("signup_intro", idioma))
        st.success(t("free_credits", idioma))
        email_cadastro = st.text_input(
            t("your_email", idioma), key="email_cadastro", placeholder=t("email_placeholder", idioma)
        )
        senha_cadastro = st.text_input(
            t("create_password", idioma), type="password", key="senha_cadastro"
        )
        senha_confirmar = st.text_input(
            t("confirm_password", idioma), type="password", key="senha_confirmar"
        )
        st.caption(t("password_policy", idioma))
        aceitou_documentos = st.checkbox(t("accept_legal", idioma), key="aceite_legal_cadastro")
        st.caption(t("legal_available", idioma, version=LEGAL_VERSION))

        if st.button(t("create_account", idioma), use_container_width=True, key="btn_cadastro"):
            email_cadastro = email_cadastro.strip().lower()
            senha_valida, erro_senha = validar_senha_forte(senha_cadastro, idioma)

            if not email_cadastro:
                st.warning(t("enter_email", idioma))
            elif not senha_valida:
                st.warning(erro_senha)
            elif senha_cadastro != senha_confirmar:
                st.warning(t("password_mismatch", idioma))
            elif not aceitou_documentos:
                st.warning(t("must_accept_legal", idioma))
            else:
                try:
                    resposta = supabase.auth.sign_up({
                        "email": email_cadastro,
                        "password": senha_cadastro,
                        "options": {
                            "data": {
                                "legal_accepted": True,
                                "terms_version": TERMS_VERSION,
                                "privacy_version": PRIVACY_VERSION,
                                "app_version": APP_VERSION,
                                "legal_locale": LANGUAGE_LOCALES.get(idioma, "en"),
                                "preferred_language": LANGUAGE_LOCALES.get(idioma, "en"),
                            }
                        },
                    })
                    if resposta.session:
                        try:
                            supabase.auth.sign_out()
                        except Exception:
                            pass
                    limpar_sessao()
                    st.success(t("signup_success", idioma))
                    st.info(t("confirmation_sent", idioma, email=email_cadastro))
                    st.warning(t("confirmation_required", idioma))
                    st.caption(t("check_spam", idioma))
                except Exception:
                    st.error(t("signup_failed", idioma))

    st.divider()
    st.caption(t("legal_beta", idioma))
    with st.expander(t("terms", idioma)):
        renderizar_termos_uso(idioma)
    with st.expander(t("privacy", idioma)):
        renderizar_politica_privacidade(idioma)


# ============================================================
# RECUPERAÇÃO DE SENHA
# ============================================================

idioma_interface_atual()
processar_link_recuperacao_senha()

if st.session_state.modo_recuperacao_senha:

    tela_redefinir_senha()

    st.stop()


# ============================================================
# BLOQUEAR APP PARA NÃO LOGADOS
# ============================================================

if not usuario_logado():

    tela_login()

    st.stop()


# ============================================================
# RELIABILITY 2.6.15 - ACEITE LEGAL VIGENTE
# ============================================================

try:
    aceite_legal_vigente = buscar_aceite_legal_vigente()
except Exception as erro:
    st.error(
        "Não foi possível verificar os documentos legais da sua conta."
    )
    st.info(
        "Por segurança, o acesso às funções do CardCraftAI permanece "
        "bloqueado até essa verificação funcionar novamente."
    )
    st.caption(
        f"Detalhe técnico: {erro}"
    )

    if st.button(
        "🚪 Sair da conta",
        use_container_width=True,
        key="btn_sair_falha_aceite_legal",
    ):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        limpar_sessao()
        st.rerun()

    st.stop()

if not aceite_legal_vigente:
    tela_aceite_legal_pendente()
    st.stop()


# ============================================================
# PERFIL DO USUÁRIO
# ============================================================

# Reliability 2.6: antes de ler o saldo, recupera execuções antigas
# interrompidas para que qualquer estorno apareça imediatamente.
talvez_recuperar_analises_interrompidas()

perfil = buscar_perfil()

if not perfil:

    st.error(
        "Seu login funcionou, mas o perfil de créditos "
        "não foi encontrado no Supabase."
    )

    st.info(
        "Saia da conta e entre novamente. "
        "Se continuar acontecendo, "
        "precisaremos verificar o trigger."
    )

    if st.button(
        "🚪 Sair e tentar novamente"
    ):

        try:

            supabase.auth.sign_out()

        except Exception:

            pass

        limpar_sessao()

        st.rerun()

    st.stop()


creditos = int(
    perfil.get(
        "credits",
        0
    )
)

plano = perfil.get(
    "plan",
    "free"
)

# Se o usuário voltou do Checkout Pro, direciona a interface para Planos e
# registra somente o status visual. A confirmação financeira continua sendo
# responsabilidade exclusiva do webhook autenticado.
processar_retorno_mercadopago()


def traduzir_pacote_ui(pacote, idioma):
    codigo = str(pacote.get("code") or "")
    traducoes = {
        "English": {
            "STARTER_10": ("Starter Pack", "10 credits for card analyses"),
            "COLLECTOR_50": ("Collector Pack", "50 credits for card analyses"),
            "PRO_150": ("Pro Pack", "150 credits for intensive use"),
            "STORE_MONTHLY": ("Store Plan", "Monthly plan for stores and professional sellers"),
        },
        "Español": {
            "STARTER_10": ("Paquete Inicial", "10 créditos para análisis de cartas"),
            "COLLECTOR_50": ("Paquete Coleccionista", "50 créditos para análisis de cartas"),
            "PRO_150": ("Paquete Pro", "150 créditos para uso intensivo"),
            "STORE_MONTHLY": ("Plan Tienda", "Plan mensual para tiendas y vendedores profesionales"),
        },
        "日本語": {
            "STARTER_10": ("スターターパック", "カード分析用10クレジット"),
            "COLLECTOR_50": ("コレクターパック", "カード分析用50クレジット"),
            "PRO_150": ("プロパック", "集中利用向け150クレジット"),
            "STORE_MONTHLY": ("ショッププラン", "店舗・プロ販売者向け月額プラン"),
        },
    }
    if idioma in traducoes and codigo in traducoes[idioma]:
        return traducoes[idioma][codigo]
    return (pacote.get("name", "Package"), pacote.get("description", ""))


# ============================================================
# SIDEBAR
# ============================================================

idioma = idioma_interface_atual()

st.sidebar.title(t("panel", idioma))

st.sidebar.write(t("account", idioma))

st.sidebar.success(
    st.session_state.user_email
)

st.sidebar.metric(t("credits", idioma), creditos)

plano_exibicao = traduzir_plano_ui(plano, idioma)
st.sidebar.caption(t("current_plan", idioma, plan=plano_exibicao))

if creditos == 0:

    st.sidebar.warning(t("no_credits", idioma))


st.sidebar.divider()


idioma = renderizar_seletor_idioma(
    st.sidebar,
    "idioma_sidebar_widget",
)

st.sidebar.divider()

pagina_atual = pagina_interface_atual()
if st.session_state.get("pagina_navegacao_widget") != pagina_atual:
    st.session_state.pagina_navegacao_widget = pagina_atual

st.sidebar.radio(
    t("navigation", idioma),
    NAVIGATION_OPTIONS,
    format_func=lambda pagina_id: t({
        "photo": "nav_photo",
        "search": "nav_search",
        "plans": "nav_plans",
        "account": "nav_account",
        "terms": "nav_terms",
        "privacy": "nav_privacy",
    }[pagina_id], idioma),
    key="pagina_navegacao_widget",
    on_change=_sincronizar_pagina_widget,
)
pagina = pagina_interface_atual()


st.sidebar.divider()


if st.sidebar.button(
    t("sign_out", idioma),
    use_container_width=True,
):

    try:

        supabase.auth.sign_out()

    except Exception:

        pass

    limpar_sessao()

    st.rerun()


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "🃏 CardCraftAI"
)

st.caption(t("tagline_app", idioma))

st.divider()

if st.session_state.aviso_recuperacao:
    st.info(
        st.session_state.aviso_recuperacao
    )
    st.session_state.aviso_recuperacao = None


# ============================================================
# EXIBIR RESULTADO
# ============================================================

def mostrar_resultado(
    resultado
):

    st.divider()

    st.header(t("result", idioma))

    if isinstance(resultado, dict):
        conteudo = formatar_resultado_estruturado(
            resultado,
            tipo_resultado=st.session_state.get("resultado_tipo"),
        )
    else:
        # Compatibilidade defensiva com resultados de sessoes antigas.
        conteudo = str(resultado)

    st.markdown(
        conteudo
    )

    if st.session_state.aviso_credito:
        st.warning(
            st.session_state.aviso_credito
        )

    if st.session_state.aviso_auditoria:
        st.warning(
            st.session_state.aviso_auditoria
        )

    st.divider()

    st.info(t("web_disabled", idioma))

    st.caption(t("analysis_used_credit", idioma))


# ============================================================
# PÁGINA 1 - ANÁLISE POR FOTO
# ============================================================

if pagina == "photo":

    st.header(t("photo_title", idioma))

    st.write(t("photo_intro", idioma))

    st.info(t("analysis_cost", idioma))

    col1, col2 = st.columns(
        [1, 1],
        gap="large",
    )

    with col1:

        aba_upload, aba_camera = st.tabs(
            [
                t("upload_file", idioma),
                t("use_camera", idioma),
            ]
        )

        with aba_upload:

            arquivo_upload = (
                st.file_uploader(
                    t("choose_image", idioma),
                    type=[
                        "jpg",
                        "jpeg",
                        "png",
                        "webp",
                    ],
                )
            )

        with aba_camera:

            arquivo_camera = (
                st.camera_input(
                    t("take_photo", idioma)
                )
            )

        uploaded_file = (
            arquivo_camera
            if arquivo_camera is not None
            else arquivo_upload
        )

    with col2:

        if uploaded_file is not None:

            try:

                imagem = Image.open(
                    uploaded_file
                )

                imagem.load()

                st.image(
                    imagem,
                    caption=t("selected_card", idioma),
                    use_container_width=True,
                )

                if creditos <= 0:

                    st.error(
                        "💎 Você não possui "
                        "créditos disponíveis."
                    )

                else:

                    if st.button(
                        t("analyze_card", idioma),
                        use_container_width=True,
                        key="btn_analise_foto",
                    ):

                        st.session_state.catalogo_selecionada_foto = None
                        st.session_state.analysis_run_id_atual = None
                        st.session_state.analysis_request_id_atual = None
                        st.session_state.analysis_tipo_atual = None

                        with st.spinner(
                            t("analyzing_card", idioma)
                        ):

                            try:

                                resultado = (
                                    executar_analise_com_credito(
                                        idioma=idioma,
                                        imagem_pil=imagem,
                                        tipo_acao="analise_foto",
                                    )
                                )

                                st.session_state.resultado_analise = (
                                    resultado
                                )

                                st.session_state.resultado_tipo = (
                                    "foto"
                                )

                                st.session_state.resultado_novo = (
                                    True
                                )

                                st.rerun()

                            except Exception as erro:

                                st.error(
                                    f"Erro: {erro}"
                                )

            except Exception as erro:

                st.error(
                    "Não foi possível abrir "
                    f"a imagem: {erro}"
                )

        else:

            st.info(
                t("send_photo_start", idioma)
            )


    # --------------------------------------------------------
    # MOSTRAR RESULTADO APÓS RERUN
    # --------------------------------------------------------

    if (
        st.session_state.resultado_analise
        and
        st.session_state.resultado_tipo == "foto"
    ):

        if st.session_state.resultado_novo:

            st.success(
                t("analysis_complete", idioma)
            )

            st.session_state.resultado_novo = False

        mostrar_resultado(
            st.session_state.resultado_analise
        )

        mostrar_catalogo_para_analise_foto(
            st.session_state.resultado_analise
        )


# ============================================================
# PÁGINA 2 - BUSCAR POR NOME
# ============================================================

elif pagina == "search":

    st.header(t("search_title", idioma))

    st.info(t("catalog_free", idioma))

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:
        termo_busca = st.text_input(
            t("card_name", idioma),
            placeholder="Ex.: Charizard GX",
            key="termo_busca",
        )

    with col2:
        colecao_busca = st.text_input(
            t("set_name", idioma),
            placeholder="Ex.: SM Black Star Promos",
            key="colecao_busca",
        )

    if st.button(
        t("search_catalog", idioma),
        use_container_width=True,
        key="btn_buscar_catalogo_nome",
    ):
        termo = termo_busca.strip()
        colecao = colecao_busca.strip()

        if not termo:
            st.warning(
                t("enter_card_name", idioma)
            )
        else:
            with st.spinner(
                t("searching_catalog", idioma)
            ):
                try:
                    resultados_catalogo = (
                        buscar_cartas_catalogo_pokemon(
                            nome=termo,
                            colecao=colecao,
                            limite=12,
                        )
                    )

                    st.session_state.catalogo_resultados_nome = (
                        resultados_catalogo
                    )
                    st.session_state.catalogo_consulta_nome = {
                        "nome": termo,
                        "colecao": colecao,
                    }
                    st.session_state.catalogo_selecionada_nome = None

                except Exception as erro:
                    st.session_state.catalogo_resultados_nome = []
                    st.session_state.catalogo_consulta_nome = None
                    st.session_state.catalogo_selecionada_nome = None

                    st.error(
                        t("catalog_error", idioma)
                    )
                    st.caption(
                        str(erro)
                    )

    resultados_catalogo = (
        st.session_state.catalogo_resultados_nome
        or []
    )

    consulta_catalogo = (
        st.session_state.catalogo_consulta_nome
    )

    carta_selecionada = st.session_state.get(
        "catalogo_selecionada_nome"
    )

    if carta_selecionada:
        st.divider()

        mostrar_carta_catalogo_selecionada(
            carta_selecionada,
            titulo=t("selected_for_analysis_title"),
        )

        st.info(t("selection_registered"))

    if consulta_catalogo:
        st.divider()

        st.subheader(
            t("catalog_results", idioma)
        )

        consulta_texto = (
            f"{consulta_catalogo.get('nome', '')}"
            + (
                " • " + consulta_catalogo.get("colecao", "")
                if consulta_catalogo.get("colecao")
                else ""
            )
        )
        st.caption(t("search_performed_by", query=consulta_texto))

        if resultados_catalogo:
            mostrar_galeria_catalogo(
                resultados_catalogo,
                contexto="nome",
            )
        else:
            st.warning(
                t("no_catalog_results", idioma)
            )

    st.divider()

    st.subheader(
        t("specialized_analysis", idioma)
    )

    if carta_selecionada:
        st.caption(t("analysis_uses_selected"))
    else:
        st.caption(t("analysis_uses_typed"))

    if creditos <= 0:
        st.warning(
            "💎 Você não possui créditos disponíveis "
            "para gerar uma nova análise."
        )
        st.info(
            "A busca visual acima continua gratuita."
        )

    if st.button(
        t("analyze_one_credit", idioma),
        use_container_width=True,
        key="btn_analise_nome",
        disabled=(creditos <= 0),
    ):
        st.session_state.analysis_run_id_atual = None
        st.session_state.analysis_request_id_atual = None
        st.session_state.analysis_tipo_atual = None

        termo = termo_busca.strip()
        colecao = colecao_busca.strip()

        if carta_selecionada:
            info_texto = info_catalogo_para_analise(
                carta_selecionada
            )
        else:
            if not termo:
                st.warning(
                    "Digite o nome da carta."
                )
                st.stop()

            if colecao:
                info_texto = (
                    f"Nome: {termo}\n"
                    f"Coleção/Set: {colecao}"
                )
            else:
                info_texto = (
                    f"Nome: {termo}\n"
                    "Coleção/Set: não informada"
                )

        with st.spinner(
            "🤖 Analisando..."
        ):
            try:
                resultado = (
                    executar_analise_com_credito(
                        idioma=idioma,
                        nome_carta_info=info_texto,
                        tipo_acao="analise_nome",
                    )
                )

                # Reliability 2.6.3:
                # se a analise partiu de uma carta selecionada no catalogo,
                # persistimos essa evidencia externa no mesmo analysis_run
                # antes do rerun. Nenhuma nova chamada ao catalogo e feita.
                if carta_selecionada:
                    validacao_nome = validar_carta_selecionada_catalogo(
                        resultado,
                        carta_selecionada,
                    )
                    atualizar_registro_catalogo(
                        resultado,
                        validacao=validacao_nome,
                        cartas=[carta_selecionada],
                        catalogo_latency_ms=0,
                    )

                st.session_state.resultado_analise = (
                    resultado
                )
                st.session_state.resultado_tipo = (
                    "nome"
                )
                st.session_state.resultado_novo = (
                    True
                )

                st.rerun()

            except Exception as erro:
                st.error(
                    f"Erro: {erro}"
                )

    # --------------------------------------------------------
    # MOSTRAR RESULTADO APÓS RERUN
    # --------------------------------------------------------

    if (
        st.session_state.resultado_analise
        and
        st.session_state.resultado_tipo == "nome"
    ):
        if st.session_state.resultado_novo:
            st.success(
                "✅ Análise concluída."
            )
            st.session_state.resultado_novo = False

        mostrar_resultado(
            st.session_state.resultado_analise
        )


# ============================================================
# PÁGINA 3 - PLANOS
# ============================================================

elif pagina == "account":

    st.header(t("my_account", idioma))

    st.caption(t("account_caption", idioma))

    col_email, col_creditos, col_plano = st.columns(3)

    with col_email:
        st.metric(
            t("confirmed_email", idioma),
            t("yes", idioma) if st.session_state.email_confirmado else t("no", idioma),
        )

    with col_creditos:
        st.metric(
            t("available_credits", idioma),
            creditos,
        )

    with col_plano:
        st.metric(
            t("plan_label", idioma),
            traduzir_plano_ui(plano, idioma),
        )

    st.subheader(
        t("account_data", idioma)
    )

    st.write(
        f"**{t('email_label', idioma)}:** {st.session_state.user_email}"
    )

    if st.session_state.email_confirmado:
        st.success(
            t("email_confirmed_ok", idioma)
        )
    else:
        st.warning(
            t("email_not_confirmed", idioma)
        )

    st.divider()

    st.subheader(
        t("security", idioma)
    )

    st.write(
        t("security_reset_text", idioma)
    )

    if st.button(
        t("send_password_reset", idioma),
        use_container_width=True,
        key="btn_conta_redefinir_senha",
    ):

        try:
            supabase.auth.reset_password_for_email(
                st.session_state.user_email
            )

            st.success(t("recovery_sent", idioma))
            st.caption(t("check_spam", idioma))

        except Exception:
            st.error(t("recovery_request_failed", idioma))
            st.info(t("try_again_later", idioma))

    st.divider()

    st.subheader(
        t("purchase_history", idioma)
    )

    compras = buscar_compras_usuario()

    if not compras:
        st.info(
            t("no_purchases", idioma)
        )
    else:
        linhas_compras = []

        for compra in compras:
            linhas_compras.append(
                {
                    "Data": formatar_data_conta(
                        compra.get("created_at")
                    ),
                    "Status": rotulo_status_compra(
                        compra.get("status")
                    ),
                    "Créditos": int(
                        compra.get("credits_purchased") or 0
                    ),
                    "Valor": formatar_preco(
                        compra.get("amount_cents") or 0,
                        compra.get("currency") or "BRL",
                    ),
                    "Moeda": compra.get("currency") or "BRL",
                    "Provedor": compra.get("provider") or "—",
                }
            )

        st.dataframe(
            linhas_compras,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader(
        t("session", idioma)
    )

    if st.button(
        t("sign_out_account", idioma),
        use_container_width=True,
        key="btn_conta_sair",
    ):

        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        limpar_sessao()
        st.rerun()


elif pagina == "terms":

    renderizar_termos_uso(
        idioma
    )

    st.info(t("beta_legal_note", idioma))


elif pagina == "privacy":

    renderizar_politica_privacidade(
        idioma
    )

    st.info(t("beta_legal_note", idioma))


elif pagina == "plans":

    st.header(t("plans_title", idioma))

    retorno_pagamento = st.session_state.get(
        "payment_return_status"
    )

    if retorno_pagamento == "success":
        st.success(
            t("payment_success_return", idioma)
        )

    elif retorno_pagamento == "pending":
        st.info(
            t("payment_pending_return", idioma)
        )

    elif retorno_pagamento == "failure":
        st.error(
            t("payment_failure_return", idioma)
        )

    if retorno_pagamento in {
        "success",
        "pending",
    }:
        if st.button(
            t("refresh_balance", idioma),
            use_container_width=True,
            key="btn_atualizar_saldo_pagamento",
        ):
            st.session_state.payment_return_status = None
            st.rerun()

    st.metric(
        t("balance", idioma),
        f"{creditos} {t('credits_word', idioma)}",
    )

    st.success(
        t("free_credits", idioma)
    )

    st.caption(
        t("packages_from_db", idioma)
    )

    moeda_exibicao = st.selectbox(
        t("currency_label", idioma),
        options=PRICING_CURRENCIES,
        key="pricing_currency",
        format_func=lambda codigo: CURRENCY_LABELS.get(codigo, codigo),
    )

    st.caption(
        t("currency_caption", idioma)
    )

    if moeda_exibicao == "BRL":
        st.info(
            t("secure_checkout_note", idioma)
        )
    else:
        st.info(
            t(
                "international_checkout_pending",
                idioma,
                currency=moeda_exibicao,
            )
        )

    st.divider()

    try:

        pacotes = buscar_pacotes_ativos(
            moeda_exibicao
        )

    except Exception as erro:

        st.error(
            str(erro)
        )

        pacotes = []


    if not pacotes:

        st.warning(
            t("no_packages", idioma)
        )

    else:

        pacotes_avulsos = [
            pacote
            for pacote in pacotes
            if pacote.get("package_type") == "one_time"
        ]

        assinaturas = [
            pacote
            for pacote in pacotes
            if pacote.get("package_type") == "subscription"
        ]


        if pacotes_avulsos:

            st.subheader(
                t("credit_packages", idioma)
            )

            colunas = st.columns(
                len(pacotes_avulsos),
                gap="large",
            )

            for coluna, pacote in zip(
                colunas,
                pacotes_avulsos,
            ):

                with coluna:

                    nome, descricao = traduzir_pacote_ui(pacote, idioma)

                    qtd_creditos = int(
                        pacote.get(
                            "credits",
                            0
                        )
                    )

                    preco_disponivel = bool(
                        pacote.get("display_price_available")
                    )

                    preco = formatar_preco(
                        pacote.get("display_price_cents"),
                        moeda_exibicao,
                    )

                    codigo = str(
                        pacote.get(
                            "code",
                            str(
                                pacote.get(
                                    "id",
                                    "pacote"
                                )
                            )
                        )
                    ).strip().upper()

                    st.subheader(
                        f"💎 {nome}"
                    )

                    st.metric(
                        t("credits_label", idioma),
                        qtd_creditos,
                    )

                    st.metric(
                        t("price", idioma),
                        preco,
                    )

                    if descricao:

                        st.write(
                            descricao
                        )

                    checkout_habilitado = (
                        moeda_exibicao == "BRL"
                        and preco_disponivel
                    )

                    if not preco_disponivel:
                        st.caption(
                            t(
                                "currency_price_missing",
                                idioma,
                                currency=moeda_exibicao,
                            )
                        )

                    if st.button(
                        t("buy", idioma, name=nome),
                        use_container_width=True,
                        key=f"comprar_{codigo}_{moeda_exibicao}",
                        disabled=not checkout_habilitado,
                    ):

                        st.session_state.checkout_preference = None

                        with st.spinner(
                            t("checkout_creating", idioma)
                        ):
                            try:
                                preferencia = criar_preferencia_mercadopago(
                                    codigo
                                )
                                st.session_state.checkout_preference = preferencia

                            except Exception as erro:
                                st.error(
                                    t("checkout_error", idioma)
                                )
                                st.caption(
                                    str(erro)
                                )

                    checkout_atual = st.session_state.get(
                        "checkout_preference"
                    )

                    if (
                        isinstance(checkout_atual, dict)
                        and
                        moeda_exibicao == "BRL"
                        and
                        checkout_atual.get("package_code") == codigo
                        and
                        checkout_atual.get("checkout_url")
                    ):
                        st.success(
                            t("checkout_ready", idioma)
                        )

                        st.link_button(
                            t("checkout_open", idioma),
                            checkout_atual.get("checkout_url"),
                            use_container_width=True,
                        )


        if assinaturas:

            st.divider()

            st.subheader(
                t("subscriptions", idioma)
            )

            for pacote in assinaturas:

                nome, descricao = traduzir_pacote_ui(pacote, idioma)

                qtd_creditos = int(
                    pacote.get(
                        "credits",
                        0
                    )
                )

                assinatura_tem_preco_selecionado = bool(
                    pacote.get("display_price_available")
                )

                if assinatura_tem_preco_selecionado:
                    preco = formatar_preco(
                        pacote.get("display_price_cents"),
                        moeda_exibicao,
                    )
                else:
                    preco = formatar_preco(
                        pacote.get("price_cents", 0),
                        pacote.get("currency") or "BRL",
                    )

                codigo = pacote.get(
                    "code",
                    str(
                        pacote.get(
                            "id",
                            "assinatura"
                        )
                    )
                )

                col1, col2 = st.columns(
                    [2, 1],
                    gap="large",
                )

                with col1:

                    st.subheader(
                        f"🏪 {nome}"
                    )

                    if descricao:

                        st.write(
                            descricao
                        )

                    st.write(
                        f"**{t('per_cycle', idioma, n=qtd_creditos)}**"
                    )

                with col2:

                    st.metric(
                        t("monthly_fee", idioma),
                        preco,
                    )

                    st.button(
                        t("subscribe", idioma, name=nome),
                        use_container_width=True,
                        key=f"assinar_{codigo}",
                        disabled=True,
                    )

                    if not assinatura_tem_preco_selecionado:
                        st.caption(
                            t("subscription_brl_only", idioma)
                        )

                    st.caption(
                        t("subscription_pending", idioma)
                    )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "CardCraftAI © 2026"
)
