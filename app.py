import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import requests

# Configuração da página com tema moderno
st.set_page_config(
    page_title="CardCraftAI - TCG Intelligence",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para um visual atraente, profissional e colorido
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(168, 85, 247, 0.4);
    }
    .hero-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
        border: 1px solid #4c1d95;
        padding: 2.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .card-metric {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Recuperar chaves de segurança dos Segredos do Streamlit
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error("⚠️ Chave da API do Gemini não configurada nos Segredos do Streamlit (Settings > Secrets).")
    st.stop()

# Cabeçalho / Hero Section Atrativo
st.markdown("""
    <div class="hero-box">
        <h1 style="font-size: 2.8rem; font-weight: 800; background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
            🃏 CardCraftAI
        </h1>
        <p style="font-size: 1.25rem; color: #cbd5e1; max-width: 700px; margin: 0 auto; font-weight: 400;">
            A inteligência artificial definitiva para colecionadores e lojistas de TCG. Precifique, catalogue e avalie suas cartas em segundos.
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar de Navegação e Idioma
st.sidebar.markdown("### ⚙️ Painel de Controle")
idioma = st.sidebar.selectbox("🌐 Idioma / Language", ["Português (BR)", "English", "Español"])

st.sidebar.markdown("---")
pagina = st.sidebar.radio("Navegação", ["📸 Análise por Foto", "🔍 Buscar Carta por Nome", "💳 Planos e Créditos"])

# Função de Análise com Gemini
def analisar_carta(imagem_pil, nome_carta_info=None):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    if nome_carta_info:
        prompt = f"""
        Analise a carta de TCG com base nestas informações fornecidas pelo usuário: {nome_carta_info}.
        Por favor, forneça em {idioma}:
        1. Nome exato da carta, Jogo (Pokémon, Magic, Yu-Gi-Oh, etc.) e Número/Set.
        2. Estimativa detalhada de preço de mercado atual em Reais (BRL) e Dólares (USD).
        3. Condição estimada provável e dicas de conservação.
        4. Sugestão de texto pronto para venda (copywriting) para marketplaces (Mercado Livre, eBay, TCGPlayer, LigaPokémon).
        5. Links simulados úteis de pesquisa em plataformas globais.
        """
        response = model.generate_content([prompt, imagem_pil])
    else:
        prompt = f"""
        Analise esta carta de TCG enviada por imagem.
        Por favor, forneça em {idioma}:
        1. Nome exato da carta, Jogo (Pokémon, Magic, Yu-Gi-Oh, Esportes) e Número/Set.
        2. Avaliação rigorosa da condição visual (Ex: Near Mint, Lightly Played, Moderately Played, Heavily Played, Damaged) com justificativa de bordas, centro e superfície.
        3. Estimativa precisa de preço médio de mercado atual em BRL e USD.
        4. Texto otimizado e atrativo para anúncio de vendas pronto para copiar e colar.
        """
        response = model.generate_content([prompt, imagem_pil])
        
    return response.text

# PÁGINA 1: ANÁLISE POR FOTO
if pagina == "📸 Análise por Foto":
    st.markdown("### 📸 Envie ou Tire a Foto da sua Carta")
    st.write("Faça o upload de uma imagem clara da frente da sua carta para análise instantânea por IA.")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        uploaded_file = st.file_uploader("Escolha a imagem (PNG, JPG, JPEG)", type=["jpg", "jpeg", "png"])
        usar_camera = st.checkbox("Usar a câmera do dispositivo")
        
        if usar_camera:
            camera_file = st.camera_input("Tire uma foto da carta")
            if camera_file:
                uploaded_file = camera_file

    with col2:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Carta Selecionada", use_container_width=True)
            
            if st.button("🚀 Analisar Carta Agora", use_container_width=True):
                with st.spinner("✨ Inteligência Artificial analisando raridade, condição e mercado..."):
                    try:
                        resultado = analisar_carta(image)
                        st.markdown("---")
                        st.markdown("### 📊 Resultado da Análise")
                        st.markdown(resultado)
                    except Exception as e:
                        st.error(f"Erro ao processar a imagem: {e}")
        else:
            st.info("👈 Envie uma foto ao lado para habilitar o botão de análise.")

# PÁGINA 2: BUSCAR CARTA POR NOME
elif pagina == "🔍 Buscar Carta por Nome":
    st.markdown("### 🔍 Busca Rápida de Cartas")
    st.write("Não tem a foto no momento? Digite o nome da carta e a coleção para buscar referências e gerar dados de precificação.")
    
    col_busca1, col_busca2 = st.columns([2, 1])
    with col_busca1:
        termo_busca = st.text_input("Nome da Carta (Ex: Charizard VMAX, Black Lotus, Blue-Eyes White Dragon)")
    with col_busca2:
        colecao_busca = st.text_input("Coleção / Set (Opcional)", placeholder="Ex: Base Set, Fusion Strike")
        
    if st.button("🔍 Buscar e Analisar"):
        if termo_busca:
            with st.spinner(f"Buscando dados de mercado para '{termo_busca}'..."):
                # Criando uma imagem em branco temporária apenas para estruturar o prompt combinando texto
                blank_img = Image.new('RGB', (300, 400), color=(30, 41, 59))
                info_texto = f"Carta pesquisada por texto: {termo_busca} da coleção {colecao_busca}"
                
                try:
                    resultado_busca = analisar_carta(blank_img, nome_carta_info=info_texto)
                    st.markdown("---")
                    st.markdown(f"### 📋 Ficha Técnica e Preços: {termo_busca}")
                    st.markdown(resultado_busca)
                except Exception as e:
                    st.error(f"Erro na busca: {e}")
        else:
            st.warning("Por favor, digite o nome de uma carta para iniciar a busca.")

# PÁGINA 3: PLANOS E CRÉDITOS
elif pagina == "💳 Planos e Créditos":
    st.markdown("### 💳 Escolha seu Pacote de Créditos")
    st.write("Adquira créditos para realizar análises ilimitadas ou escolha o plano ideal para a sua loja.")
    
    col_p1, col_p2 = st.columns(2, gap="large")
    
    with col_p1:
        st.markdown("""
            <div class="card-metric">
                <h3>🎒 Pacote Colecionador</h3>
                <h2 style="color: #818cf8;">R$ 29,90</h2>
                <p>Ideal para colecionadores que querem catalogar e precificar cartas pontualmente.</p>
                <ul style="text-align: left; color: #cbd5e1;">
                    <li>50 Análises completas por IA</li>
                    <li>Identificação de condição rigorosa</li>
                    <li>Links de comparação global</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Comprar Pacote Colecionador", use_container_width=True):
            st.info("🔗 Redirecionando para o ambiente seguro do Stripe...")
            
    with col_p2:
        st.markdown("""
            <div class="card-metric" style="border: 2px solid #818cf8;">
                <h3>🏢 Plano Lojista B2B</h3>
                <h2 style="color: #c084fc;">R$ 149,90/mês</h2>
                <p>Para comércios e lojas de TCG que precisam de alto volume diário de triagem.</p>
                <ul style="text-align: left; color: #cbd5e1;">
                    <li>Análises ilimitadas</li>
                    <li>Geração de textos automáticos para e-commerce</li>
                    <li>Suporte prioritário</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Assinar Plano Lojista", use_container_width=True):
            st.info("🔗 Redirecionando para o ambiente seguro do Stripe...")

# Rodapé profissional
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>CardCraftAI © 2026 — Todos os direitos reservados. Powered by Google Gemini & Streamlit.</p>", unsafe_allow_html=True)
