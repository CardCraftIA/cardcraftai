import base64
from io import BytesIO

import streamlit as st
from google import genai
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
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
    }

    .card-box {
        border: 1px solid #334155;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }

    .credit-box {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #6366f1;
        margin-bottom: 1rem;
    }

    .footer-cardcraft {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
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

except Exception:
    st.error(
        "⚠️ Faltam configurações nos Secrets do Streamlit.\n\n"
        "Verifique GEMINI_API_KEY, SUPABASE_URL e SUPABASE_KEY."
    )
    st.stop()


# ============================================================
# GEMINI
# ============================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
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

if "resultado_analise" not in st.session_state:
    st.session_state.resultado_analise = None


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

                    st.session_state.user_id = (
                        resposta.user.id
                    )

                    st.session_state.user_email = (
                        resposta.user.email
                    )

        except Exception:

            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user_id = None
            st.session_state.user_email = None

    return cliente


supabase = criar_cliente_supabase()


# ============================================================
# FUNÇÕES DE AUTENTICAÇÃO
# ============================================================

def salvar_sessao(resposta):

    if not resposta:
        return False

    if not resposta.session:
        return False

    st.session_state.access_token = (
        resposta.session.access_token
    )

    st.session_state.refresh_token = (
        resposta.session.refresh_token
    )

    if resposta.user:

        st.session_state.user_id = (
            resposta.user.id
        )

        st.session_state.user_email = (
            resposta.user.email
        )

    return True


def limpar_sessao():

    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user_id = None
    st.session_state.user_email = None
    st.session_state.resultado_analise = None


def usuario_logado():

    return (
        st.session_state.user_id is not None
        and
        st.session_state.access_token is not None
    )


# ============================================================
# CRÉDITOS
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


def consumir_credito(
    acao="analise"
):

    try:

        resposta = (
            supabase
            .rpc(
                "consume_credit",
                {
                    "p_action": acao
                }
            )
            .execute()
        )

        return resposta.data

    except Exception as erro:

        raise RuntimeError(
            f"Não foi possível descontar o crédito: {erro}"
        )


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
# GEMINI - ANÁLISE
# ============================================================

def analisar_carta(
    idioma,
    imagem_pil=None,
    nome_carta_info=None,
):

    modelo = "gemini-3.6-flash"

    prompt_base = f"""
Você é um especialista profissional em Trading Card Games,
colecionismo e avaliação de cartas.

Responda obrigatoriamente em {idioma}.

IMPORTANTE:

Neste momento a pesquisa web está desativada.

Não invente preços atuais.

Não diga que consultou sites ou marketplaces.

Se um preço atual depender de pesquisa de mercado,
informe claramente que será necessário realizar
uma pesquisa web posteriormente.

Organize sua resposta exatamente com as seguintes seções:

# 🃏 Identificação

Informe, quando possível:

- Nome exato
- Jogo
- Coleção / Set
- Número da carta
- Raridade
- Variante
- Ano

Caso não seja possível determinar algo,
informe que precisa ser confirmado.

# 📊 Informações Gerais

Explique:

- importância da carta;
- características;
- versões possíveis;
- fatores que influenciam seu valor.

# 💰 Mercado

Como a pesquisa web está desativada:

- não invente preços;
- não invente vendas recentes;
- não invente anúncios.

Informe que os preços atuais poderão ser
consultados posteriormente em:

- Liga Pokémon
- Mercado Livre
- eBay
- TCGplayer
- Cardmarket
- PriceCharting

# 🔎 Condição Aparente

Caso exista fotografia, avalie:

- cantos;
- bordas;
- superfície;
- centralização;
- riscos;
- amassados;
- desgaste.

Utilize somente como estimativa visual:

- Near Mint
- Lightly Played
- Moderately Played
- Heavily Played

Não atribua nota definitiva PSA, BGS ou CGC.

# ⚠️ Autenticidade

Informe sinais visuais relevantes.

Nunca confirme definitivamente a autenticidade
apenas com base em uma fotografia.

# 🛡️ Conservação

Dê recomendações sobre:

- sleeve;
- top loader;
- armazenamento;
- umidade;
- luz solar.

# 📝 Anúncio para Venda

Crie um texto curto e profissional
para servir como base de anúncio.

Não invente características que não tenham sido confirmadas.
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

        interaction = (
            gemini_client
            .interactions
            .create(
                model=modelo,
                input=entrada,
            )
        )

        resultado = interaction.output_text

        if not resultado:

            raise RuntimeError(
                "O Gemini respondeu sem conteúdo."
            )

        return resultado

    except Exception as erro:

        raise RuntimeError(
            "Falha na análise com Gemini 3.6 Flash.\n\n"
            f"Detalhes: {erro}"
        )


# ============================================================
# TELA DE LOGIN
# ============================================================

def tela_login():

    st.markdown(
        """
        <div class="hero-box">

            <h1 style="
                font-size: 3rem;
                margin-bottom: 0.5rem;
                color: #c084fc;
            ">
                🃏 CardCraftAI
            </h1>

            <p style="
                font-size: 1.2rem;
                color: #cbd5e1;
            ">
                Inteligência artificial para
                identificação e avaliação de cartas TCG.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "## 🔐 Acesse sua conta"
    )

    aba_login, aba_cadastro = st.tabs(
        [
            "🔑 Entrar",
            "✨ Criar Conta",
        ]
    )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    with aba_login:

        email_login = st.text_input(
            "E-mail",
            key="email_login",
        )

        senha_login = st.text_input(
            "Senha",
            type="password",
            key="senha_login",
        )

        if st.button(
            "🔑 Entrar",
            use_container_width=True,
            key="btn_login",
        ):

            if (
                not email_login.strip()
                or
                not senha_login
            ):

                st.warning(
                    "Preencha e-mail e senha."
                )

            else:

                try:

                    resposta = (
                        supabase
                        .auth
                        .sign_in_with_password(
                            {
                                "email": (
                                    email_login
                                    .strip()
                                    .lower()
                                ),
                                "password": senha_login,
                            }
                        )
                    )

                    if salvar_sessao(
                        resposta
                    ):

                        st.success(
                            "Login realizado com sucesso."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Não foi possível iniciar "
                            "a sessão."
                        )

                except Exception as erro:

                    st.error(
                        "Não foi possível entrar.\n\n"
                        "Verifique o e-mail, a senha "
                        "e se o e-mail já foi confirmado."
                    )

                    st.caption(
                        f"Detalhe técnico: {erro}"
                    )

    # --------------------------------------------------------
    # CADASTRO
    # --------------------------------------------------------

    with aba_cadastro:

        email_cadastro = st.text_input(
            "Seu e-mail",
            key="email_cadastro",
        )

        senha_cadastro = st.text_input(
            "Crie uma senha",
            type="password",
            key="senha_cadastro",
        )

        senha_confirmar = st.text_input(
            "Confirme a senha",
            type="password",
            key="senha_confirmar",
        )

        st.caption(
            "🎁 Novas contas começam "
            "com 5 créditos gratuitos."
        )

        if st.button(
            "✨ Criar minha conta",
            use_container_width=True,
            key="btn_cadastro",
        ):

            email_cadastro = (
                email_cadastro
                .strip()
                .lower()
            )

            if not email_cadastro:

                st.warning(
                    "Informe seu e-mail."
                )

            elif len(
                senha_cadastro
            ) < 6:

                st.warning(
                    "A senha precisa ter "
                    "pelo menos 6 caracteres."
                )

            elif (
                senha_cadastro
                !=
                senha_confirmar
            ):

                st.warning(
                    "As senhas não são iguais."
                )

            else:

                try:

                    resposta = (
                        supabase
                        .auth
                        .sign_up(
                            {
                                "email": (
                                    email_cadastro
                                ),
                                "password": (
                                    senha_cadastro
                                ),
                            }
                        )
                    )

                    if resposta.session:

                        salvar_sessao(
                            resposta
                        )

                        st.success(
                            "Conta criada com sucesso!"
                        )

                        st.rerun()

                    else:

                        st.success(
                            "Conta criada! ✅"
                        )

                        st.info(
                            "📧 Verifique sua caixa "
                            "de e-mail e confirme "
                            "o cadastro antes de entrar."
                        )

                except Exception as erro:

                    st.error(
                        "Não foi possível criar "
                        "a conta."
                    )

                    st.caption(
                        f"Detalhe técnico: {erro}"
                    )


# ============================================================
# BLOQUEIO PARA NÃO LOGADOS
# ============================================================

if not usuario_logado():

    tela_login()

    st.stop()


# ============================================================
# PERFIL DO USUÁRIO
# ============================================================

perfil = buscar_perfil()

if not perfil:

    st.error(
        "Seu usuário está autenticado, "
        "mas o perfil de créditos não foi encontrado."
    )

    st.info(
        "Saia da conta e entre novamente. "
        "Se continuar acontecendo, "
        "precisaremos verificar o trigger "
        "do Supabase."
    )

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


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## ⚙️ Painel de Controle"
)

st.sidebar.success(
    f"👤 {st.session_state.user_email}"
)

st.sidebar.markdown(
    f"""
    <div class="credit-box">

        <strong>💎 Seus créditos</strong>

        <h2 style="margin-bottom:0;">
            {creditos}
        </h2>

        <small>
            Plano: {plano}
        </small>

    </div>
    """,
    unsafe_allow_html=True,
)

if creditos == 0:

    st.sidebar.warning(
        "Você não possui créditos disponíveis."
    )

if st.sidebar.button(
    "🚪 Sair da conta",
    use_container_width=True,
):

    try:
        supabase.auth.sign_out()

    except Exception:
        pass

    limpar_sessao()

    st.rerun()


st.sidebar.markdown("---")


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
# CABEÇALHO
# ============================================================

st.markdown(
    """
    <div class="hero-box">

        <h1 style="
            font-size: 2.8rem;
            font-weight: 800;
            color: #c084fc;
            margin-bottom: 0.5rem;
        ">
            🃏 CardCraftAI
        </h1>

        <p style="
            font-size: 1.2rem;
            color: #cbd5e1;
            margin: 0;
        ">
            Inteligência artificial para identificação,
            avaliação e pesquisa de cartas TCG.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FUNÇÃO PARA PROCESSAR ANÁLISE + CRÉDITO
# ============================================================

def executar_analise_com_credito(
    idioma,
    imagem_pil=None,
    nome_carta_info=None,
    tipo_acao="analise",
):

    saldo_atual = buscar_creditos()

    if saldo_atual <= 0:

        raise RuntimeError(
            "Você não possui créditos disponíveis."
        )

    # Primeiro executamos o Gemini.
    #
    # Se o Gemini falhar, nenhum crédito é descontado.

    resultado = analisar_carta(
        idioma=idioma,
        imagem_pil=imagem_pil,
        nome_carta_info=nome_carta_info,
    )

    # Somente após resposta bem-sucedida
    # descontamos 1 crédito no Supabase.

    consumir_credito(
        tipo_acao
    )

    return resultado


# ============================================================
# EXIBIR RESULTADO
# ============================================================

def mostrar_resultado(
    resultado
):

    st.markdown("---")

    st.markdown(
        "## 📊 Resultado da Análise"
    )

    st.markdown(
        resultado
    )

    st.markdown("---")

    st.info(
        "🧪 Nesta versão, a pesquisa web "
        "ainda está temporariamente desativada."
    )

    st.caption(
        "💎 Esta análise consumiu "
        "1 crédito."
    )


# ============================================================
# PÁGINA 1
# ANÁLISE POR FOTO
# ============================================================

if pagina == "📸 Análise por Foto":

    st.markdown(
        "## 📸 Envie ou Tire uma Foto"
    )

    st.caption(
        "Cada análise concluída "
        "consome 1 crédito."
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

            arquivo_upload = (
                st.file_uploader(
                    "Escolha uma imagem",
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
                    "Tire uma foto da carta"
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
                    caption="Carta selecionada",
                    use_container_width=True,
                )

                if creditos <= 0:

                    st.error(
                        "💎 Você não possui "
                        "créditos disponíveis."
                    )

                else:

                    if st.button(
                        "🚀 Analisar Carta — 1 crédito",
                        use_container_width=True,
                    ):

                        with st.spinner(
                            "🤖 Analisando a carta..."
                        ):

                            try:

                                resultado = (
                                    executar_analise_com_credito(
                                        idioma=idioma,
                                        imagem_pil=imagem,
                                        tipo_acao=(
                                            "analise_foto"
                                        ),
                                    )
                                )

                                st.session_state[
                                    "resultado_analise"
                                ] = resultado

                                st.success(
                                    "✅ Análise concluída."
                                )

                                mostrar_resultado(
                                    resultado
                                )

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
                "👈 Envie ou tire uma foto "
                "para começar."
            )


# ============================================================
# PÁGINA 2
# BUSCAR CARTA POR NOME
# ============================================================

elif pagina == "🔍 Buscar Carta por Nome":

    st.markdown(
        "## 🔍 Buscar Carta por Nome"
    )

    st.caption(
        "Cada análise concluída "
        "consome 1 crédito."
    )

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:

        termo_busca = st.text_input(
            "Nome da carta",
            placeholder=(
                "Ex.: Charizard ex"
            ),
        )

    with col2:

        colecao_busca = st.text_input(
            "Coleção / Set",
            placeholder="Ex.: 151",
        )

    if creditos <= 0:

        st.error(
            "💎 Você não possui créditos disponíveis."
        )

        st.info(
            "Vá até Planos e Créditos "
            "para adquirir mais créditos."
        )

    else:

        if st.button(
            "🔍 Analisar — 1 crédito",
            use_container_width=True,
        ):

            termo_busca = (
                termo_busca.strip()
            )

            colecao_busca = (
                colecao_busca.strip()
            )

            if not termo_busca:

                st.warning(
                    "Digite o nome da carta."
                )

            else:

                if colecao_busca:

                    info_texto = (
                        f"Nome: {termo_busca}\n"
                        f"Coleção/Set: "
                        f"{colecao_busca}"
                    )

                else:

                    info_texto = (
                        f"Nome: {termo_busca}\n"
                        "Coleção/Set: "
                        "não informada"
                    )

                with st.spinner(
                    "🤖 Analisando..."
                ):

                    try:

                        resultado = (
                            executar_analise_com_credito(
                                idioma=idioma,
                                nome_carta_info=(
                                    info_texto
                                ),
                                tipo_acao=(
                                    "analise_nome"
                                ),
                            )
                        )

                        st.session_state[
                            "resultado_analise"
                        ] = resultado

                        st.success(
                            "✅ Análise concluída."
                        )

                        mostrar_resultado(
                            resultado
                        )

                    except Exception as erro:

                        st.error(
                            f"Erro: {erro}"
                        )


# ============================================================
# PÁGINA 3
# PLANOS
# ============================================================

elif pagina == "💳 Planos e Créditos":

    st.markdown(
        "## 💳 Planos e Créditos"
    )

    st.metric(
        "💎 Seu saldo atual",
        f"{creditos} créditos",
    )

    st.info(
        "🎁 Novas contas recebem "
        "5 créditos gratuitos."
    )

    st.markdown("---")

    col1, col2 = st.columns(
        2,
        gap="large",
    )

    with col1:

        st.markdown(
            """
            <div class="card-box">

                <h3>
                    🎒 Pacote Colecionador
                </h3>

                <h2>
                    R$ 29,90
                </h2>

                <p>
                    Pacote de créditos para
                    colecionadores.
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
                "💳 O checkout será "
                "configurado em uma próxima etapa."
            )

    with col2:

        st.markdown(
            """
            <div class="card-box">

                <h3>
                    🏢 Plano Lojista B2B
                </h3>

                <h2>
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
                "💳 O checkout será "
                "configurado em uma próxima etapa."
            )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown("---")

st.markdown(
    """
    <p class="footer-cardcraft">
        CardCraftAI © 2026
    </p>
    """,
    unsafe_allow_html=True,
)
