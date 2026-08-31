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
