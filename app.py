import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
from supabase import create_client, Client

# Configuração da página DEVE ser a primeira linha do Streamlit
st.set_page_config(page_title='CardCraftAI', page_icon='🃏', layout='wide')

load_dotenv()

# Inicialização do Gemini e Supabase
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
except:
    st.error("Chaves do Supabase não encontradas.")
supabase: Client = create_client(supabase_url, supabase_key)

# ---- DICIONÁRIO DE IDIOMAS ----
TRANSLATIONS = {
    "🇧🇷 Português (BR)": {
        "ai_lang": "Português do Brasil",
        "login_title": "🔒 Acesso ao CardCraftAI", "login_sub": "Faça login ou crie sua conta.",
        "tab_in": "Entrar", "tab_up": "Criar Conta", "email": "E-mail", "pass": "Senha",
        "btn_in": "Entrar", "btn_up": "Cadastrar", "err_login": "E-mail ou senha incorretos.",
        "succ_up": "Conta criada com sucesso! Faça login na aba ao lado.", "err_up": "Erro ao criar conta: ",
        "cfg": "⚙️ Configurações", "log_as": "Logado como:", "btn_out": "Sair da Conta",
        "app_title": "🃏 CardCraftAI - Precificação e Anúncios", "app_sub": "Envie a foto do seu Card de Coleção",
        "upload": "Escolha a imagem da carta...", "img_cap": "Imagem Enviada", "img_succ": "Imagem carregada com sucesso!",
        "spin": "Analisando mercado e gerando links...", "res_title": "📋 Resultado da Análise", "err_ana": "Erro na análise: "
    },
    "🇺🇸 English": {
        "ai_lang": "English",
        "login_title": "🔒 Access CardCraftAI", "login_sub": "Login or create an account.",
        "tab_in": "Login", "tab_up": "Sign Up", "email": "Email", "pass": "Password",
        "btn_in": "Sign In", "btn_up": "Create Account", "err_login": "Incorrect email or password.",
        "succ_up": "Account created successfully! Please log in.", "err_up": "Error creating account: ",
        "cfg": "⚙️ Settings", "log_as": "Logged in as:", "btn_out": "Log Out",
        "app_title": "🃏 CardCraftAI - Pricing & Listings", "app_sub": "Upload your Trading Card photo",
        "upload": "Choose card image...", "img_cap": "Uploaded Image", "img_succ": "Image successfully loaded!",
        "spin": "Analyzing market and generating links...", "res_title": "📋 Analysis Result", "err_ana": "Analysis error: "
    },
    "🇪🇸 Español": {
        "ai_lang": "Español",
        "login_title": "🔒 Acceso a CardCraftAI", "login_sub": "Inicia sesión o crea tu cuenta.",
        "tab_in": "Entrar", "tab_up": "Registrarse", "email": "Correo", "pass": "Contraseña",
        "btn_in": "Entrar", "btn_up": "Crear Cuenta", "err_login": "Correo o contraseña incorrectos.",
        "succ_up": "¡Cuenta creada con éxito! Inicia sesión.", "err_up": "Error al crear cuenta: ",
        "cfg": "⚙️ Ajustes", "log_as": "Sesión iniciada como:", "btn_out": "Cerrar Sesión",
        "app_title": "🃏 CardCraftAI - Precios y Anuncios", "app_sub": "Sube la foto de tu Carta Coleccionable",
        "upload": "Elige la imagen de la carta...", "img_cap": "Imagen Enviada", "img_succ": "¡Imagen cargada con éxito!",
        "spin": "Analizando el mercado...", "res_title": "📋 Resultado del Análisis", "err_ana": "Error en el análisis: "
    },
    "🇵🇹 Português (PT)": {
        "ai_lang": "Português de Portugal",
        "login_title": "🔒 Acesso ao CardCraftAI", "login_sub": "Inicie sessão ou crie a sua conta.",
        "tab_in": "Iniciar Sessão", "tab_up": "Criar Conta", "email": "E-mail", "pass": "Palavra-passe",
        "btn_in": "Entrar", "btn_up": "Registar", "err_login": "E-mail ou palavra-passe incorretos.",
        "succ_up": "Conta criada com sucesso! Inicie sessão.", "err_up": "Erro ao criar conta: ",
        "cfg": "⚙️ Definições", "log_as": "Sessão iniciada como:", "btn_out": "Terminar Sessão",
        "app_title": "🃏 CardCraftAI - Preços e Anúncios", "app_sub": "Envie a fotografia da sua Carta de Coleção",
        "upload": "Escolha a imagem da carta...", "img_cap": "Imagem Enviada", "img_succ": "Imagem carregada com sucesso!",
        "spin": "A analisar o mercado...", "res_title": "📋 Resultado da Análise", "err_ana": "Erro na análise: "
    },
    "🇫🇷 Français": {
        "ai_lang": "Français",
        "login_title": "🔒 Accès CardCraftAI", "login_sub": "Connectez-vous ou créez un compte.",
        "tab_in": "Connexion", "tab_up": "S'inscrire", "email": "E-mail", "pass": "Mot de passe",
        "btn_in": "Se connecter", "btn_up": "Créer un compte", "err_login": "E-mail ou mot de passe incorrect.",
        "succ_up": "Compte créé avec succès ! Connectez-vous.", "err_up": "Erreur : ",
        "cfg": "⚙️ Paramètres", "log_as": "Connecté en tant que :", "btn_out": "Se déconnecter",
        "app_title": "🃏 CardCraftAI - Prix et Annonces", "app_sub": "Téléchargez la photo de votre carte",
        "upload": "Choisissez l'image...", "img_cap": "Image envoyée", "img_succ": "Image chargée avec succès !",
        "spin": "Analyse du marché en cours...", "res_title": "📋 Résultat de l'analyse", "err_ana": "Erreur : "
    },
    "🇷🇺 Русский": {
        "ai_lang": "Русский",
        "login_title": "🔒 Доступ к CardCraftAI", "login_sub": "Войдите или создайте учетную запись.",
        "tab_in": "Вход", "tab_up": "Регистрация", "email": "Email", "pass": "Пароль",
        "btn_in": "Войти", "btn_up": "Создать аккаунт", "err_login": "Неверный email или пароль.",
        "succ_up": "Аккаунт успешно создан! Войдите.", "err_up": "Ошибка: ",
        "cfg": "⚙️ Настройки", "log_as": "Вы вошли как:", "btn_out": "Выйти",
        "app_title": "🃏 CardCraftAI - Цены и объявления", "app_sub": "Загрузите фото вашей коллекционной карты",
        "upload": "Выберите изображение карты...", "img_cap": "Загруженное изображение", "img_succ": "Изображение успешно загружено!",
        "spin": "Анализ рынка...", "res_title": "📋 Результат анализа", "err_ana": "Ошибка анализа: "
    },
    "🇨🇳 中文 (Mandarin)": {
        "ai_lang": "Simplified Chinese (Mandarin)",
        "login_title": "🔒 访问 CardCraftAI", "login_sub": "登录或创建您的帐户。",
        "tab_in": "登录", "tab_up": "注册", "email": "电子邮件", "pass": "密码",
        "btn_in": "登录", "btn_up": "创建帐户", "err_login": "电子邮件或密码错误。",
        "succ_up": "帐户创建成功！请登录。", "err_up": "创建帐户时出错：",
        "cfg": "⚙️ 设置", "log_as": "当前登录：", "btn_out": "登出",
        "app_title": "🃏 CardCraftAI - 定价和列表", "app_sub": "上传您的集换式卡牌照片",
        "upload": "选择卡片图像...", "img_cap": "上传的图像", "img_succ": "图像加载成功！",
        "spin": "正在分析市场...", "res_title": "📋 分析结果", "err_ana": "分析错误："
    },
    "🇯🇵 日本語": {
        "ai_lang": "Japanese",
        "login_title": "🔒 CardCraftAIへアクセス", "login_sub": "ログインまたはアカウントを作成してください。",
        "tab_in": "ログイン", "tab_up": "サインアップ", "email": "メールアドレス", "pass": "パスワード",
        "btn_in": "ログイン", "btn_up": "アカウント作成", "err_login": "メールアドレスまたはパスワードが間違っています。",
        "succ_up": "アカウントが正常に作成されました！ログインしてください。", "err_up": "エラー：",
        "cfg": "⚙️ 設定", "log_as": "ログイン中：", "btn_out": "ログアウト",
        "app_title": "🃏 CardCraftAI - 価格設定と出品", "app_sub": "トレーディングカードの写真をアップロード",
        "upload": "カードの画像を選択...", "img_cap": "アップロードされた画像", "img_succ": "画像の読み込みに成功しました！",
        "spin": "市場を分析中...", "res_title": "📋 分析結果", "err_ana": "分析エラー："
    },
    "🇩🇪 Deutsch": {
        "ai_lang": "Deutsch",
        "login_title": "🔒 Zugang zu CardCraftAI", "login_sub": "Anmelden oder Konto erstellen.",
        "tab_in": "Anmelden", "tab_up": "Registrieren", "email": "E-Mail", "pass": "Passwort",
        "btn_in": "Einloggen", "btn_up": "Konto erstellen", "err_login": "E-Mail oder Passwort falsch.",
        "succ_up": "Konto erfolgreich erstellt! Bitte einloggen.", "err_up": "Fehler: ",
        "cfg": "⚙️ Einstellungen", "log_as": "Angemeldet als:", "btn_out": "Abmelden",
        "app_title": "🃏 CardCraftAI - Preise & Anzeigen", "app_sub": "Laden Sie ein Foto Ihrer Sammelkarte hoch",
        "upload": "Kartenbild auswählen...", "img_cap": "Hochgeladenes Bild", "img_succ": "Bild erfolgreich geladen!",
        "spin": "Markt wird analysiert...", "res_title": "📋 Analyseergebnis", "err_ana": "Analysefehler: "
    },
    "🇰🇷 한국어": {
        "ai_lang": "Korean",
        "login_title": "🔒 CardCraftAI 접속", "login_sub": "로그인하거나 계정을 만드세요.",
        "tab_in": "로그인", "tab_up": "가입하기", "email": "이메일", "pass": "비밀번호",
        "btn_in": "로그인", "btn_up": "계정 만들기", "err_login": "이메일 또는 비밀번호가 올바르지 않습니다.",
        "succ_up": "계정이 성공적으로 생성되었습니다! 로그인해주세요.", "err_up": "오류: ",
        "cfg": "⚙️ 설정", "log_as": "로그인 됨:", "btn_out": "로그아웃",
        "app_title": "🃏 CardCraftAI - 가격 및 목록", "app_sub": "트레이딩 카드 사진 업로드",
        "upload": "카드 이미지 선택...", "img_cap": "업로드된 이미지", "img_succ": "이미지를 성공적으로 불러왔습니다!",
        "spin": "시장 분석 중...", "res_title": "📋 분석 결과", "err_ana": "분석 오류: "
    }
}

# SELETOR DE IDIOMA NA BARRA LATERAL (Aparece em todas as telas)
st.sidebar.title("🌐 Language / Idioma")
selected_lang = st.sidebar.selectbox("Choose your language:", list(TRANSLATIONS.keys()))
t = TRANSLATIONS[selected_lang] # 't' agora carrega o dicionário do idioma escolhido

# Gerenciamento de sessão
if 'user' not in st.session_state:
    st.session_state.user = None

# ---- TELA DE LOGIN / CADASTRO ----
if st.session_state.user is None:
    st.title(t["login_title"])
    st.markdown(t["login_sub"])

    tab1, tab2 = st.tabs([t["tab_in"], t["tab_up"]])

    with tab1:
        login_email = st.text_input(t["email"], key="login_email")
        login_password = st.text_input(t["pass"], type="password", key="login_password")
        if st.button(t["btn_in"], type="primary"):
            try:
                response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                st.session_state.user = response.user
                st.rerun()
            except Exception as e:
                st.error(t["err_login"])

    with tab2:
        signup_email = st.text_input(t["email"], key="signup_email")
        signup_password = st.text_input(t["pass"], type="password", key="signup_password")
        if st.button(t["btn_up"], type="primary"):
            try:
                response = supabase.auth.sign_up({"email": signup_email, "password": signup_password})
                st.success(t["succ_up"])
            except Exception as e:
                st.error(f'{t["err_up"]}{e}')

# ---- APLICATIVO PRINCIPAL ----
else:
    st.sidebar.divider()
    st.sidebar.title(t["cfg"])
    st.sidebar.write(f'{t["log_as"]}\n**{st.session_state.user.email}**')
    if st.sidebar.button(t["btn_out"]):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    st.title(t["app_title"])
    st.subheader(t["app_sub"])

    uploaded_file = st.file_uploader(t["upload"], type=['jpg', 'png', 'jpeg'])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)

        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption=t["img_cap"], use_container_width=True)

        with col2:
            st.success(t["img_succ"])

        with st.spinner(t["spin"]):
            try:
                # O comando da IA agora instrui dinamicamente em qual idioma ela deve responder
                prompt = f"""Analise a carta e retorne formatado em tópicos: 
                1. Nome da Carta e Numeração 
                2. Jogo/Coleção 
                3. Raridade 
                4. Condição visual 
                5. Título chamativo para venda 
                6. Preço médio estimado. 
                Por fim, adicione links clicáveis em Markdown de pesquisa para esta exata carta nas plataformas globais e locais: eBay, TCGPlayer, Amazon, e Mercado Livre.
                
                IMPORTANTE: Todo o seu texto de resposta DEVE ser traduzido e escrito EXCLUSIVAMENTE no idioma: {t['ai_lang']}.
                """
                
                response = client.models.generate_content(model='gemini-3.6-flash', contents=[image, prompt])
                
                st.subheader(t["res_title"])
                st.markdown(response.text)
            except Exception as e:
                st.error(f'{t["err_ana"]}{e}')
