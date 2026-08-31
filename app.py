import base64
import uuid
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
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
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

except Exception:
    st.error(
        "⚠️ Faltam configurações nos Secrets do Streamlit.\n\n"
        "Verifique:\n"
        "- GEMINI_API_KEY\n"
        "- SUPABASE_URL\n"
        "- SUPABASE_KEY"
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

if "resultado_tipo" not in st.session_state:
    st.session_state.resultado_tipo = None

if "resultado_novo" not in st.session_state:
    st.session_state.resultado_novo = False

if "aviso_credito" not in st.session_state:
    st.session_state.aviso_credito = None


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
# AUTENTICAÇÃO
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
    st.session_state.resultado_tipo = None
    st.session_state.resultado_novo = False
    st.session_state.aviso_credito = None


def usuario_logado():

    return (
        st.session_state.user_id is not None
        and
        st.session_state.access_token is not None
    )


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


def buscar_pacotes_ativos():

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

        return resposta.data or []

    except Exception as erro:

        raise RuntimeError(
            "Não foi possível carregar os planos e pacotes.\n\n"
            f"Detalhes: {erro}"
        )


def formatar_preco_brl(
    price_cents
):

    valor = (
        int(price_cents or 0)
        / 100
    )

    texto = (
        f"{valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {texto}"


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

def analisar_carta(
    idioma,
    imagem_pil=None,
    nome_carta_info=None,
):

    modelo = "gemini-3.6-flash"

    prompt_base = f"""
Você é um especialista profissional em Trading Card Games (TCG),
colecionismo, identificação e avaliação de cartas.

Responda obrigatoriamente em {idioma}.

IMPORTANTE:

A pesquisa web está temporariamente desativada.

Não invente preços atuais.
Não diga que consultou sites.
Não invente vendas recentes.
Não invente anúncios existentes.

Se algum dado não puder ser confirmado,
informe claramente que precisa ser verificado.

Organize a resposta da seguinte maneira:

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

Explique:

- importância da carta;
- características conhecidas;
- versões possíveis;
- fatores que podem influenciar o valor.

# 💰 Mercado

A pesquisa web está desativada nesta versão.

Não invente preços.

Informe que os valores atuais deverão ser
consultados posteriormente em plataformas como:

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

Utilize somente como estimativa:

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
para servir como base de anúncio.

Não invente características que
não tenham sido confirmadas.
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
# EXECUTAR ANÁLISE COM RESERVA ATÔMICA
# ============================================================

def executar_analise_com_credito(
    idioma,
    imagem_pil=None,
    nome_carta_info=None,
    tipo_acao="analise",
):

    # Cada análise recebe um identificador único.

    request_id = uuid.uuid4()

    st.session_state.aviso_credito = None

    # ========================================================
    # 1. RESERVAR O CRÉDITO ANTES DO GEMINI
    # ========================================================

    reservar_credito(
        tipo_acao,
        request_id,
    )

    # ========================================================
    # 2. CHAMAR O GEMINI
    # ========================================================

    try:

        resultado = analisar_carta(
            idioma=idioma,
            imagem_pil=imagem_pil,
            nome_carta_info=nome_carta_info,
        )

    except Exception as erro_gemini:

        # ====================================================
        # 3. GEMINI FALHOU -> DEVOLVER CRÉDITO
        # ====================================================

        try:

            devolver_credito(
                request_id
            )

        except Exception as erro_estorno:

            raise RuntimeError(
                "A análise falhou e houve um problema "
                "ao devolver automaticamente o crédito.\n\n"
                "Não faça outra análise agora.\n\n"
                f"Erro da análise: {erro_gemini}\n\n"
                f"Erro do estorno: {erro_estorno}"
            )

        raise RuntimeError(
            "A análise não pôde ser concluída.\n\n"
            "✅ O crédito reservado foi devolvido "
            "automaticamente.\n\n"
            f"Detalhes: {erro_gemini}"
        )

    # ========================================================
    # 4. GEMINI FUNCIONOU -> CONFIRMAR CONSUMO
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

        st.session_state.aviso_credito = (
            "A análise foi concluída, porém houve "
            "uma falha ao marcar o consumo como concluído. "
            "O crédito permanece reservado. "
            f"Detalhe técnico: {erro_confirmacao}"
        )

    return resultado


# ============================================================
# TELA DE LOGIN / CADASTRO
# ============================================================

def tela_login():

    st.title(
        "🃏 CardCraftAI"
    )

    st.subheader(
        "Inteligência artificial para "
        "identificação e avaliação de cartas TCG"
    )

    st.divider()

    st.header(
        "🔐 Acesse sua conta"
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

        st.write(
            "Entre com seu e-mail e senha."
        )

        email_login = st.text_input(
            "E-mail",
            key="email_login",
            placeholder="seuemail@exemplo.com",
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
                    "Preencha o e-mail e a senha."
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
                            "Não foi possível iniciar a sessão."
                        )

                except Exception as erro:

                    st.error(
                        "Não foi possível entrar."
                    )

                    st.info(
                        "Verifique o e-mail, a senha "
                        "e se a conta já foi confirmada."
                    )

                    st.caption(
                        f"Detalhe técnico: {erro}"
                    )

    # --------------------------------------------------------
    # CADASTRO
    # --------------------------------------------------------

    with aba_cadastro:

        st.write(
            "Crie sua conta CardCraftAI."
        )

        st.success(
            "🎁 Novas contas recebem 5 créditos gratuitos."
        )

        email_cadastro = st.text_input(
            "Seu e-mail",
            key="email_cadastro",
            placeholder="seuemail@exemplo.com",
        )

        senha_cadastro = st.text_input(
            "Crie uma senha",
            type="password",
            key="senha_cadastro",
        )

        senha_confirmar = st.text_input(
            "Confirme sua senha",
            type="password",
            key="senha_confirmar",
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
                    "As duas senhas não são iguais."
                )

            else:

                try:

                    resposta = (
                        supabase
                        .auth
                        .sign_up(
                            {
                                "email": email_cadastro,
                                "password": senha_cadastro,
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
                            "Conta criada com sucesso! ✅"
                        )

                        st.info(
                            "📧 Verifique sua caixa de e-mail. "
                            "O Supabase pode exigir a confirmação "
                            "antes do primeiro login."
                        )

                except Exception as erro:

                    st.error(
                        "Não foi possível criar a conta."
                    )

                    st.caption(
                        f"Detalhe técnico: {erro}"
                    )


# ============================================================
# BLOQUEAR APP PARA NÃO LOGADOS
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


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚙️ Painel de Controle"
)

st.sidebar.write(
    "👤 Conta"
)

st.sidebar.success(
    st.session_state.user_email
)

st.sidebar.metric(
    "💎 Créditos",
    creditos,
)

st.sidebar.caption(
    f"Plano atual: {plano}"
)

if creditos == 0:

    st.sidebar.warning(
        "Você não possui créditos disponíveis."
    )


st.sidebar.divider()


idioma = st.sidebar.selectbox(
    "🌐 Idioma / Language",
    [
        "Português (BR)",
        "English",
        "Español",
    ],
)


st.sidebar.divider()


pagina = st.sidebar.radio(
    "Navegação",
    [
        "📸 Análise por Foto",
        "🔍 Buscar Carta por Nome",
        "💳 Planos e Créditos",
    ],
)


st.sidebar.divider()


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


# ============================================================
# CABEÇALHO
# ============================================================

st.title(
    "🃏 CardCraftAI"
)

st.caption(
    "Inteligência artificial para identificação, "
    "avaliação e pesquisa de cartas TCG."
)

st.divider()


# ============================================================
# EXIBIR RESULTADO
# ============================================================

def mostrar_resultado(
    resultado
):

    st.divider()

    st.header(
        "📊 Resultado da Análise"
    )

    st.markdown(
        resultado
    )

    if st.session_state.aviso_credito:

        st.warning(
            st.session_state.aviso_credito
        )

    st.divider()

    st.info(
        "🧪 A pesquisa web está "
        "temporariamente desativada nesta versão."
    )

    st.caption(
        "💎 A análise concluída consumiu 1 crédito."
    )


# ============================================================
# PÁGINA 1 - ANÁLISE POR FOTO
# ============================================================

if pagina == "📸 Análise por Foto":

    st.header(
        "📸 Análise por Foto"
    )

    st.write(
        "Envie ou tire uma foto da sua carta."
    )

    st.info(
        "💎 Cada análise concluída consome 1 crédito."
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
                        key="btn_analise_foto",
                    ):

                        with st.spinner(
                            "🤖 Analisando a carta..."
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
                "👈 Envie ou tire uma foto "
                "para começar."
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
                "✅ Análise concluída."
            )

            st.session_state.resultado_novo = False

        mostrar_resultado(
            st.session_state.resultado_analise
        )


# ============================================================
# PÁGINA 2 - BUSCAR POR NOME
# ============================================================

elif pagina == "🔍 Buscar Carta por Nome":

    st.header(
        "🔍 Buscar Carta por Nome"
    )

    st.info(
        "💎 Cada análise concluída consome 1 crédito."
    )

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:

        termo_busca = st.text_input(
            "Nome da carta",
            placeholder="Ex.: Charizard ex",
            key="termo_busca",
        )

    with col2:

        colecao_busca = st.text_input(
            "Coleção / Set",
            placeholder="Ex.: 151",
            key="colecao_busca",
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
            key="btn_analise_nome",
        ):

            termo = (
                termo_busca.strip()
            )

            colecao = (
                colecao_busca.strip()
            )

            if not termo:

                st.warning(
                    "Digite o nome da carta."
                )

            else:

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

elif pagina == "💳 Planos e Créditos":

    st.header(
        "💳 Planos e Créditos"
    )

    st.metric(
        "💎 Seu saldo atual",
        f"{creditos} créditos",
    )

    st.success(
        "🎁 Novas contas recebem "
        "5 créditos gratuitos."
    )

    st.caption(
        "Os pacotes abaixo são carregados diretamente "
        "do Supabase."
    )

    st.divider()

    try:

        pacotes = buscar_pacotes_ativos()

    except Exception as erro:

        st.error(
            str(erro)
        )

        pacotes = []


    if not pacotes:

        st.warning(
            "Nenhum pacote ativo está disponível no momento."
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
                "🎒 Pacotes de Créditos"
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

                    nome = pacote.get(
                        "name",
                        "Pacote"
                    )

                    descricao = pacote.get(
                        "description",
                        ""
                    )

                    qtd_creditos = int(
                        pacote.get(
                            "credits",
                            0
                        )
                    )

                    preco = formatar_preco_brl(
                        pacote.get(
                            "price_cents",
                            0
                        )
                    )

                    codigo = pacote.get(
                        "code",
                        str(
                            pacote.get(
                                "id",
                                "pacote"
                            )
                        )
                    )

                    st.subheader(
                        f"💎 {nome}"
                    )

                    st.metric(
                        "Créditos",
                        qtd_creditos,
                    )

                    st.metric(
                        "Preço",
                        preco,
                    )

                    if descricao:

                        st.write(
                            descricao
                        )

                    if st.button(
                        f"Comprar {nome}",
                        use_container_width=True,
                        key=f"comprar_{codigo}",
                    ):

                        st.info(
                            "💳 O checkout ainda não está conectado. "
                            "Na próxima etapa vamos vincular este botão "
                            "a um provedor de pagamento."
                        )


        if assinaturas:

            st.divider()

            st.subheader(
                "🏢 Assinaturas"
            )

            for pacote in assinaturas:

                nome = pacote.get(
                    "name",
                    "Plano"
                )

                descricao = pacote.get(
                    "description",
                    ""
                )

                qtd_creditos = int(
                    pacote.get(
                        "credits",
                        0
                    )
                )

                preco = formatar_preco_brl(
                    pacote.get(
                        "price_cents",
                        0
                    )
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
                        f"**{qtd_creditos} créditos por ciclo**"
                    )

                with col2:

                    st.metric(
                        "Mensalidade",
                        preco,
                    )

                    if st.button(
                        f"Assinar {nome}",
                        use_container_width=True,
                        key=f"assinar_{codigo}",
                    ):

                        st.info(
                            "💳 A assinatura ainda não está conectada "
                            "ao checkout. Faremos essa integração "
                            "na próxima etapa."
                        )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    "CardCraftAI © 2026"
)
