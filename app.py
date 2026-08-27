import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
from supabase import create_client, Client

# Configuração da página DEVE ser a primeira linha do Streamlit
st.set_page_config(page_title='CardCraftAI', page_icon='🃏', layout='wide')

load_dotenv()

# Inicialização do Gemini
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Inicialização do Supabase (Buscando as chaves dos Secrets)
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
except:
    st.error("Chaves do Supabase não encontradas. Verifique o painel do Streamlit.")

supabase: Client = create_client(supabase_url, supabase_key)

# Gerenciamento de sessão (lembrar se o usuário está logado)
if 'user' not in st.session_state:
    st.session_state.user = None

# ---- TELA DE LOGIN / CADASTRO ----
if st.session_state.user is None:
    st.title('🔒 Acesso ao CardCraftAI')
    st.markdown('Faça login ou crie sua conta para utilizar nossa inteligência artificial.')

    tab1, tab2 = st.tabs(["Entrar", "Criar Conta"])

    with tab1:
        st.subheader("Faça seu Login")
        login_email = st.text_input("E-mail", key="login_email")
        login_password = st.text_input("Senha", type="password", key="login_password")
        if st.button("Entrar", type="primary"):
            try:
                response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                st.session_state.user = response.user
                st.rerun()
            except Exception as e:
                st.error("E-mail ou senha incorretos. Tente novamente.")

    with tab2:
        st.subheader("Nova Conta")
        signup_email = st.text_input("E-mail", key="signup_email")
        signup_password = st.text_input("Senha", type="password", key="signup_password")
        if st.button("Cadastrar", type="primary"):
            try:
                response = supabase.auth.sign_up({"email": signup_email, "password": signup_password})
                st.success("Conta criada com sucesso! Você já pode fazer login na aba ao lado.")
            except Exception as e:
                st.error(f"Erro ao criar conta: {e}")

# ---- APLICATIVO PRINCIPAL (SÓ APARECE SE LOGADO) ----
else:
    # Menu lateral com botão de sair
    st.sidebar.title("Configurações da Conta")
    st.sidebar.write(f"Logado como:\n**{st.session_state.user.email}**")
    if st.sidebar.button("Sair da Conta"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # O SEU CÓDIGO ORIGINAL COMEÇA AQUI
    st.title('🃏 CardCraftAI - Precificação e Anúncios')
    st.subheader('Envie a foto do seu Card de Coleção (Pokémon, Magic, Sports)')

    uploaded_file = st.file_uploader('Escolha a imagem da carta...', type=['jpg', 'png', 'jpeg'])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption='Imagem Enviada', use_container_width=True)
        with col2:
            st.success('Imagem carregada com sucesso!')
            if st.button('🔍 Investigar Modelos Disponíveis'):
                with st.spinner('Consultando os servidores do Google...'):
                    try:
                        # Pede ao Google a lista exata de modelos que a sua chave tem direito
                        modelos = []
                        for m in client.models.list_models():
                            modelos.append(m.name)
                        
                        st.warning('⚠️ MODO INVESTIGAÇÃO: O Google exige um destes nomes exatos abaixo:')
                        st.write(modelos)
                    except Exception as e:
                        st.error(f'Erro na investigação: {e}')
                with st.spinner('Analisando mercado e gerando links de busca...'):
                    try:
                        prompt = 'Analise a carta e retorne formatado em tópicos: 1. Nome da Carta e Numeração, 2. Jogo/Coleção, 3. Raridade, 4. Condição visual, 5. Título chamativo para venda, 6. Preço médio estimado. Por fim, adicione links clicáveis em Markdown de pesquisa para esta exata carta nas seguintes plataformas: Mercado Livre, eBay, TCGPlayer, Shopee, Amazon e LigaPokemon/LigaMagic.'
                        response = client.models.generate_content(model='gemini-1.5-flash', contents=[image, prompt])
                        st.subheader('📋 Resultado da Análise e Mercado Multiplataforma')
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f'Erro na análise: {e}')
