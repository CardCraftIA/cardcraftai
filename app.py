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
# ESTILIZAÇÃO CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
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
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONFIGURAÇÃO DA API GEMINI
# ============================================================

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

except Exception:
    st.error(
        "⚠️ Chave da API do Gemini não configurada. "
        "Adicione GEMINI_API_KEY nos Secrets do Streamlit."
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
            font-weight: 400;
        ">
            A inteligência artificial definitiva para
            colecionadores e lojistas de TCG.
            Precifique, catalogue e avalie suas cartas em segundos.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("### ⚙️ Painel de Controle")

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
# FUNÇÃO DE ANÁLISE GEMINI
# ============================================================

def analisar_carta(imagem_pil=None, nome_carta_info=None):
    """
    Analisa uma carta TCG usando Gemini.

    Pode receber:
    - uma imagem PIL;
    - informações textuais sobre uma carta;
    - ou ambos.

    Utiliza modelos Gemini estáveis com fallback.
    """

    ultimo_erro = None

    modelos_disponiveis = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
    ]

    prompt_base = f"""
Você é um especialista profissional em Trading Card Games (TCG),
colecionismo e avaliação de cartas.

Responda obrigatoriamente em: {idioma}.

Analise cuidadosamente as informações fornecidas.

Forneça a resposta organizada nos seguintes tópicos:

## 🃏 Identificação da Carta

1. Nome exato da carta.
2. Jogo:
   - Pokémon
   - Magic: The Gathering
   - Yu-Gi-Oh!
   - One Piece
   - Lorcana
   - ou outro TCG.
3. Coleção / Set.
4. Número da carta.
5. Variante, raridade ou edição, quando identificável.

## 💰 Estimativa de Valor

Forneça uma estimativa aproximada de preço:

- Reais (BRL)
- Dólares (USD)

Quando possível, diferencie:

- Near Mint (NM)
- Lightly Played (LP)
- Moderately Played (MP)
- Heavily Played (HP)

Deixe claro quando o preço for apenas uma estimativa
e quando não houver informação suficiente para uma avaliação confiável.

## 🔎 Condição Aparente

Se uma imagem tiver sido fornecida:

- Analise cantos.
- Bordas.
- Superfície.
- Centralização.
- Riscos ou marcas aparentes.
- Possíveis danos.

Não afirme que a carta é autêntica apenas pela fotografia.
Não atribua nota PSA/BGS/CGC definitiva apenas pela imagem.

## 🛡️ Conservação

Forneça recomendações de conservação e armazenamento.

## 📝 Texto para Venda

Crie um anúncio curto, profissional e atraente
que possa ser utilizado em marketplace.

## 🔗 Onde Pesquisar

Informe que o usuário pode pesquisar a carta em:

- Liga Pokémon
- Mercado Livre
- eBay

Use o nome exato identificado da carta
como termo sugerido de pesquisa.

Não invente vendas realizadas, preços históricos específicos
ou dados de mercado que você não consiga verificar.
"""

    if nome_carta_info:
        prompt_final = (
            "Analise a seguinte carta de TCG com base "
            f"nas informações fornecidas:\n\n{nome_carta_info}\n\n"
            f"{prompt_base}"
        )
    else:
        prompt_final = (
            "Analise cuidadosamente a carta de TCG "
            "presente na imagem fornecida.\n\n"
            f"{prompt_base}"
        )

    conteudo_payload = [prompt_final]

    if imagem_pil is not None:
        conteudo_payload.append(imagem_pil)

    for nome_modelo in modelos_disponiveis:
        try:
            response = client.models.generate_content(
                model=nome_modelo,
                contents=conteudo_payload,
            )

            if response.text:
                return response.text

        except Exception as erro:
            ultimo_erro = str(erro)

    raise RuntimeError(
        "Falha de comunicação com a API do Gemini após "
        "tentar todos os modelos disponíveis.\n\n"
        f"Último erro: {ultimo_erro}"
    )


# ============================================================
# PÁGINA 1: ANÁLISE POR FOTO
# ============================================================

if pagina == "📸 Análise por Foto":
    st.markdown("### 📸 Envie ou Tire a Foto da sua Carta")

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
                "Escolha a imagem da galeria",
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

        if arquivo_camera is not None:
            uploaded_file = arquivo_camera
        else:
            uploaded_file = arquivo_upload

    with col2:
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                image.load()

                st.image(
                    image,
                    caption="Carta Selecionada",
                    use_container_width=True,
                )

                if st.button(
                    "🚀 Analisar Carta Agora",
                    use_container_width=True,
                ):
                    with st.spinner(
                        "✨ Inteligência Artificial analisando..."
                    ):
                        try:
                            resultado = analisar_carta(
                                imagem_pil=image
                            )

                            st.markdown("---")
                            st.markdown(
                                "### 📊 Resultado da Análise"
                            )
                            st.markdown(resultado)

                            st.caption(
                                "⚠️ Os preços exibidos são "
                                "estimativas e podem variar conforme "
                                "condição, edição e mercado."
                            )

                        except Exception as erro:
                            st.error(
                                f"Erro ao processar a carta: {erro}"
                            )

            except Exception as erro:
                st.error(
                    "Não foi possível abrir a imagem enviada. "
                    f"Detalhes: {erro}"
                )

        else:
            st.info(
                "👈 Envie ou tire uma foto na aba ao lado "
                "para habilitar a análise."
            )


# ============================================================
# PÁGINA 2: BUSCAR CARTA POR NOME
# ============================================================

elif pagina == "🔍 Buscar Carta por Nome":
    st.markdown("### 🔍 Busca Rápida de Cartas")

    col_busca1, col_busca2 = st.columns(
        [2, 1]
    )

    with col_busca1:
        termo_busca = st.text_input(
            "Nome da Carta",
            placeholder="Ex.: Charizard ex",
        )

    with col_busca2:
        colecao_busca = st.text_input(
            "Coleção / Set (Opcional)",
            placeholder="Ex.: 151",
        )

    if st.button(
        "🔍 Buscar e Analisar",
        use_container_width=True,
    ):
        termo_busca = termo_busca.strip()
        colecao_busca = colecao_busca.strip()

        if termo_busca:
            with st.spinner(
                f"Analisando dados para '{termo_busca}'..."
            ):
                if colecao_busca:
                    info_texto = (
                        f"Nome: {termo_busca}\n"
                        f"Coleção/Set: {colecao_busca}"
                    )
                else:
                    info_texto = (
                        f"Nome: {termo_busca}\n"
                        "Coleção/Set: Não informada"
                    )

                try:
                    resultado_busca = analisar_carta(
                        nome_carta_info=info_texto
                    )

                    st.markdown("---")
                    st.markdown(
                        "### 📊 Resultado da Busca"
                    )
                    st.markdown(resultado_busca)

                    st.caption(
                        "⚠️ Os preços exibidos são "
                        "estimativas e podem variar conforme "
                        "condição, edição e mercado."
                    )

                except Exception as erro:
                    st.error(
                        f"Erro na análise: {erro}"
                    )

        else:
            st.warning(
                "Por favor, digite o nome de uma carta "
                "para pesquisar."
            )


# ============================================================
# PÁGINA 3: PLANOS E CRÉDITOS
# ============================================================

elif pagina == "💳 Planos e Créditos":
    st.markdown("### 💳 Escolha seu Pacote")

    col_p1, col_p2 = st.columns(
        2,
        gap="large",
    )

    with col_p1:
        st.markdown(
            """
            <div class="card-metric">
                <h3>🎒 Pacote Colecionador</h3>
                <h2 style="color: #818cf8;">
                    R$ 29,90
                </h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Comprar Pacote Colecionador",
            use_container_width=True,
        ):
            st.info(
                "Configure aqui o link de pagamento "
                "do Pacote Colecionador."
            )

    with col_p2:
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
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Assinar Plano Lojista",
            use_container_width=True,
        ):
            st.info(
                "Configure aqui o link de pagamento "
                "do Plano Lojista B2B."
            )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown("---")

st.markdown(
    """
    <p style="
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
    ">
        CardCraftAI © 2026
    </p>
    """,
    unsafe_allow_html=True,
)
