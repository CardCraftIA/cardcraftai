import base64
from io import BytesIO

import streamlit as st
from google import genai
from PIL import Image


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
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }

    .stButton > button {
        background: linear-gradient(
            135deg,
            #6366f1 0%,
            #a855f7 100%
        );
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(168, 85, 247, 0.4);
    }

    .hero-box {
        background: linear-gradient(
            135deg,
            #1e1b4b 0%,
            #311042 100%
        );
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

    .footer-cardcraft {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONFIGURAÇÃO DO GEMINI
# ============================================================

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

except Exception:
    st.error(
        "⚠️ GEMINI_API_KEY não configurada "
        "nos Secrets do Streamlit."
    )
    st.stop()


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="hero-box">
        <h1 style="
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(
                90deg,
                #818cf8,
                #c084fc,
                #f472b6
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        ">
            🃏 CardCraftAI
        </h1>

        <p style="
            font-size: 1.25rem;
            color: #cbd5e1;
            max-width: 700px;
            margin: 0 auto;
        ">
            Inteligência artificial para identificação,
            avaliação e pesquisa de mercado de cartas TCG.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "### ⚙️ Painel de Controle"
)

idioma = st.sidebar.selectbox(
    "🌐 Idioma / Language",
    [
        "Português (BR)",
        "English",
        "Español",
    ],
)

st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegação",
    [
        "📸 Análise por Foto",
        "🔍 Buscar Carta por Nome",
        "💳 Planos e Créditos",
    ],
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def imagem_para_base64(imagem_pil):
    imagem_convertida = imagem_pil.convert("RGB")

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
# FUNÇÃO PRINCIPAL DE ANÁLISE
# ============================================================

def analisar_carta(
    imagem_pil=None,
    nome_carta_info=None,
):
    modelo = "gemini-3.6-flash"

    prompt_base = f"""
Você é um especialista profissional em Trading Card Games (TCG)
e colecionismo de cartas.

Responda obrigatoriamente em {idioma}.

ESTE É UM TESTE TÉCNICO DO CARDFCRAFTAI.

Neste momento você NÃO possui acesso a pesquisa web.

Portanto:

- Não invente preços atuais.
- Não afirme que consultou sites.
- Não invente vendas concluídas.
- Não invente anúncios.
- Não apresente valores como atuais se não puder confirmá-los.
- Caso não tenha informação atual de mercado,
  diga claramente que uma pesquisa web será necessária.

Organize a análise desta forma:

# 🃏 Identificação

Informe, quando possível:

- Nome exato
- Jogo
- Coleção / Set
- Número da carta
- Raridade
- Variante
- Ano

# 📊 Informações Gerais

Explique brevemente:

- importância da carta;
- características conhecidas;
- possíveis versões;
- fatores que podem influenciar o valor.

# 💰 Mercado

Como a pesquisa web está desativada neste teste,
não invente preços.

Informe que os preços atuais deverão ser
consultados posteriormente em mercados como:

- Liga Pokémon
- Mercado Livre
- eBay
- TCGplayer
- Cardmarket
- PriceCharting

# 🔎 Condição Aparente

Se houver fotografia, avalie visualmente:

- cantos;
- bordas;
- superfície;
- centralização;
- riscos;
- amassados;
- marcas;
- desgaste.

Use apenas como estimativa visual:

- Near Mint
- Lightly Played
- Moderately Played
- Heavily Played

Não atribua nota definitiva de:

- PSA
- BGS
- CGC

# ⚠️ Autenticidade

Informe sinais visuais relevantes.

Nunca declare uma carta como definitivamente
autêntica apenas com base em uma fotografia.

# 🛡️ Conservação

Dê recomendações sobre:

- sleeve;
- top loader;
- armazenamento;
- umidade;
- luz solar.

# 📝 Anúncio para Venda

Crie um texto curto e profissional
que possa servir como base para marketplace.
"""

    if nome_carta_info:
        prompt_final = f"""
Analise esta carta com base nestas informações:

{nome_carta_info}

{prompt_base}
"""

    else:
        prompt_final = f"""
Identifique cuidadosamente a carta
presente na imagem.

{prompt_base}
"""

    if imagem_pil is not None:
        imagem_base64 = imagem_para_base64(
            imagem_pil
        )

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

    try:
        interaction = client.interactions.create(
            model=modelo,
            input=entrada,
        )

        resultado = interaction.output_text

        if not resultado:
            raise RuntimeError(
                "O Gemini respondeu sem conteúdo."
            )

        return resultado

    except Exception as erro:
        raise RuntimeError(
            "Falha no teste do Gemini 3.6 Flash.\n\n"
            f"Detalhes: {erro}"
        )


# ============================================================
# EXIBIÇÃO DO RESULTADO
# ============================================================

def mostrar_resultado(resultado):
    st.markdown("---")

    st.markdown(
        "### 📊 Resultado da Análise"
    )

    st.markdown(resultado)

    st.markdown("---")

    st.info(
        "🧪 Modo de teste ativo: "
        "a pesquisa Google está temporariamente desativada."
    )

    st.caption(
        "⚠️ Não utilize valores mencionados pela IA "
        "como cotação atual enquanto o módulo de pesquisa "
        "web estiver desativado."
    )


# ============================================================
# PÁGINA 1: ANÁLISE POR FOTO
# ============================================================

if pagina == "📸 Análise por Foto":
    st.markdown(
        "### 📸 Envie ou Tire a Foto da sua Carta"
    )

    col1, col2 = st.columns(
        [1, 1],
        gap="large",
    )

    with col1:
        aba_upload, aba_camera = st.tabs(
            [
                "📁 Enviar Arquivo",
                "📷 Usar Câmera",
            ]
        )

        with aba_upload:
            arquivo_upload = st.file_uploader(
                "Escolha uma imagem",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ],
            )

        with aba_camera:
            arquivo_camera = st.camera_input(
                "Tire uma foto da carta"
            )

        uploaded_file = (
            arquivo_camera
            if arquivo_camera is not None
            else arquivo_upload
        )

    with col2:
        if uploaded_file is not None:
            try:
                image = Image.open(
                    uploaded_file
                )

                image.load()

                st.image(
                    image,
                    caption="Carta selecionada",
                    use_container_width=True,
                )

                if st.button(
                    "🚀 Analisar Carta Agora",
                    use_container_width=True,
                ):
                    with st.spinner(
                        "🧪 Testando Gemini 3.6 Flash..."
                    ):
                        try:
                            resultado = analisar_carta(
                                imagem_pil=image
                            )

                            mostrar_resultado(
                                resultado
                            )

                        except Exception as erro:
                            st.error(
                                f"Erro ao processar: {erro}"
                            )

            except Exception as erro:
                st.error(
                    "A imagem enviada não pôde "
                    f"ser aberta: {erro}"
                )

        else:
            st.info(
                "👈 Envie ou tire uma foto "
                "para iniciar a análise."
            )


# ============================================================
# PÁGINA 2: BUSCAR CARTA POR NOME
# ============================================================

elif pagina == "🔍 Buscar Carta por Nome":
    st.markdown(
        "### 🔍 Busca de Carta"
    )

    st.info(
        "🧪 Modo de teste: "
        "pesquisa de preços na web temporariamente desativada."
    )

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:
        termo_busca = st.text_input(
            "Nome da Carta",
            placeholder="Ex.: Charizard ex",
        )

    with col2:
        colecao_busca = st.text_input(
            "Coleção / Set",
            placeholder="Ex.: 151",
        )

    if st.button(
        "🔍 Testar Análise",
        use_container_width=True,
    ):
        termo_busca = termo_busca.strip()
        colecao_busca = colecao_busca.strip()

        if not termo_busca:
            st.warning(
                "Digite o nome da carta."
            )

        else:
            if colecao_busca:
                info_texto = (
                    f"Nome: {termo_busca}\n"
                    f"Coleção/Set: {colecao_busca}"
                )

            else:
                info_texto = (
                    f"Nome: {termo_busca}\n"
                    "Coleção/Set: não informada"
                )

            with st.spinner(
                "🧪 Testando Gemini 3.6 Flash..."
            ):
                try:
                    resultado = analisar_carta(
                        nome_carta_info=info_texto
                    )

                    mostrar_resultado(
                        resultado
                    )

                except Exception as erro:
                    st.error(
                        f"Erro no teste: {erro}"
                    )


# ============================================================
# PÁGINA 3: PLANOS E CRÉDITOS
# ============================================================

elif pagina == "💳 Planos e Créditos":
    st.markdown(
        "### 💳 Escolha seu Pacote"
    )

    col1, col2 = st.columns(
        2,
        gap="large",
    )

    with col1:
        st.markdown(
            """
            <div class="card-metric">
                <h3>🎒 Pacote Colecionador</h3>
                <h2 style="color: #818cf8;">
                    R$ 29,90
                </h2>
                <p>
                    Para colecionadores que desejam
                    analisar suas cartas.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Comprar Pacote Colecionador",
            use_container_width=True,
        ):
            st.info(
                "Checkout ainda não configurado."
            )

    with col2:
        st.markdown(
            """
            <div
                class="card-metric"
                style="border: 2px solid #818cf8;"
            >
                <h3>🏢 Plano Lojista B2B</h3>
                <h2 style="color: #c084fc;">
                    R$ 149,90/mês
                </h2>
                <p>
                    Para lojas e vendedores
                    profissionais de TCG.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Assinar Plano Lojista",
            use_container_width=True,
        ):
            st.info(
                "Checkout ainda não configurado."
            )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown("---")

st.markdown(
    '<p class="footer-cardcraft">CardCraftAI © 2026</p>',
    unsafe_allow_html=True,
)
