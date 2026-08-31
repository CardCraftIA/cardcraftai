import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuração da página com tema moderno
st.set_page_config(
    page_title="CardCraftAI - TCG Intelligence",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white; border-radius: 8px; padding: 0.6rem 1.2rem;
        font-weight: 600; border: none; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(168, 85, 247, 0.4); }
    .hero-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
        border: 1px solid #4c1d95; padding: 2.5rem; border-radius: 16px;
        text-align: center; margin-bottom: 2rem; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .card-metric {
        background-color: #1e293b; border: 1px solid #334155;
        padding: 1.2rem; border-radius: 12px; text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Recuperar chaves de segurança
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error("⚠️ Chave da API do Gemini não configurada nos Segredos do Streamlit (Settings > Secrets).")
    st.stop()

# Cabeçalho
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

# Sidebar
st.sidebar.markdown("### ⚙️ Painel de Controle")
idioma = st.sidebar.selectbox("🌐 Idioma / Language", ["Português (BR)", "English", "Español"])
st.sidebar.markdown("---")
pagina = st.sidebar.radio("Navegação", ["📸 Análise por Foto", "🔍 Buscar Carta por Nome", "💳 Planos e Créditos"])

# Função de Análise com Sistema de Fallback blindado contra o erro 404
def analisar_carta(imagem_pil=None, nome_carta_info=None):
    # Lista atualizada com identificadores exatos e sufixos 'latest'
    ultimo_erro = None
   modelos_disponiveis = [
        'gemini-1.5-flash',
        'gemini-1.5-pro'
    ]
  
    prompt_base = f"""
    Por favor, forneça em {idioma}:
    1. Nome exato da carta, Jogo (Pokémon, Magic, etc.) e Número/Set.
    2. Estimativa detalhada de preço atual em Reais (BRL) e Dólares (USD).
    3. Condição estimada provável e dicas de conservação.
    4. Sugestão de texto pronto para venda (copywriting).
    5. **Links úteis de pesquisa:** Crie links de busca formatados em Markdown usando o nome exato da carta:
       - LigaPokémon (Busca: https://www.ligapokemon.com.br/?view=cards%2Fsearch&card=NOME_DA_CARTA)
       - Mercado Livre (Busca: https://lista.mercadolivre.com.br/NOME_DA_CARTA)
       - eBay (Busca: https://www.ebay.com/sch/i.html?_nkw=NOME_DA_CARTA&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=SEU_CAMPAIGN_ID_AQUI&customid=cardcraftai&toolid=10001&mkevt=1)
    """
    
    if nome_carta_info:
        prompt_final = f"Analise a carta de TCG com base nestas informações: {nome_carta_info}. " + prompt_base
    else:
        prompt_final = "Analise esta carta de TCG enviada por imagem. " + prompt_base

    # Prepara o conteúdo a ser enviado (Apenas texto ou Texto + Imagem)
    conteudo_payload = [prompt_final]
    if imagem_pil is not None:
        conteudo_payload.append(imagem_pil)

    # Tenta rodar os modelos na ordem estipulada
    for nome_modelo in modelos_disponiveis:
        try:
            model = genai.GenerativeModel(nome_modelo)
            response = model.generate_content(conteudo_payload)
            return response.text
        except Exception as e:
            ultimo_erro = str(e)
            continue
            
    raise Exception(f"Falha de comunicação com a API do Google após tentar todos os modelos disponíveis. Detalhe final: {ultimo_erro}")

# PÁGINA 1: ANÁLISE POR FOTO
if pagina == "📸 Análise por Foto":
    st.markdown("### 📸 Envie ou Tire a Foto da sua Carta")
    
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        aba_upload, aba_camera = st.tabs(["📁 Enviar Arquivo", "📷 Usar Câmera"])
        with aba_upload:
            arquivo_upload = st.file_uploader("Escolha a imagem da galeria", type=["jpg", "jpeg", "png"])
        with aba_camera:
            arquivo_camera = st.camera_input("Tire uma foto da carta")
            
        uploaded_file = arquivo_camera if arquivo_camera is not None else arquivo_upload

    with col2:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Carta Selecionada", use_container_width=True)
            
            if st.button("🚀 Analisar Carta Agora", use_container_width=True):
                with st.spinner("✨ Inteligência Artificial analisando..."):
                    try:
                        resultado = analisar_carta(imagem_pil=image)
                        st.markdown("---")
                        st.markdown("### 📊 Resultado da Análise")
                        st.markdown(resultado)
                        st.caption("⚠️ Os preços exibidos são estimativas baseadas em dados de mercado.")
                    except Exception as e:
                        st.error(f"Erro ao processar: {e}")
        else:
            st.info("👈 Envie ou tire uma foto na aba ao lado para habilitar a análise.")

# PÁGINA 2: BUSCAR CARTA POR NOME
elif pagina == "🔍 Buscar Carta por Nome":
    st.markdown("### 🔍 Busca Rápida de Cartas")
    
    col_busca1, col_busca2 = st.columns([2, 1])
    with col_busca1:
        termo_busca = st.text_input("Nome da Carta")
    with col_busca2:
        colecao_busca = st.text_input("Coleção / Set (Opcional)")
        
    if st.button("🔍 Buscar e Analisar"):
        if termo_busca:
            with st.spinner(f"Buscando dados para '{termo_busca}'..."):
                info_texto = f"Nome: {termo_busca} | Coleção/Set: {colecao_busca if colecao_busca else 'Não informada'}"
                try:
                    resultado_busca = analisar_carta(imagem_pil=None, nome_carta_info=info_texto)
                    st.markdown("---")
                    st.markdown("### 📊 Resultado da Busca")
                    st.markdown(resultado_busca)
                    st.caption("⚠️ Os preços exibidos são estimativas baseadas em dados de mercado.")
                except Exception as e:
                    st.error(f"Erro na busca: {e}")
        else:
            st.warning("Por favor, digite o nome de uma carta para pesquisar.")

# PÁGINA 3: PLANOS E CRÉDITOS
elif pagina == "💳 Planos e Créditos":
    st.markdown("### 💳 Escolha seu Pacote")
    col_p1, col_p2 = st.columns(2, gap="large")
    
    with col_p1:
        st.markdown('<div class="card-metric"><h3>🎒 Pacote Colecionador</h3><h2 style="color: #818cf8;">R$ 29,90</h2></div>', unsafe_allow_html=True)
        if st.button("Comprar Pacote Colecionador", use_container_width=True):
            st.markdown('<meta http-equiv="refresh" content="0;url=SEU_LINK_STRIPE_PACOTE_AQUI">', unsafe_allow_html=True)
            
    with col_p2:
        st.markdown('<div class="card-metric" style="border: 2px solid #818cf8;"><h3>🏢 Plano Lojista B2B</h3><h2 style="color: #c084fc;">R$ 149,90/mês</h2></div>', unsafe_allow_html=True)
        if st.button("Assinar Plano Lojista", use_container_width=True):
            st.markdown('<meta http-equiv="refresh" content="0;url=SEU_LINK_STRIPE_ASSINATURA_AQUI">', unsafe_allow_html=True)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 0.9rem;'>CardCraftAI © 2026</p>", unsafe_allow_html=True)
