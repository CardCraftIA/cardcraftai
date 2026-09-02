# CARDCRAFTAI RELIABILITY 2.1.3
# Catalogo visual Pokemon + links de mercado resilientes + Reliability 1.0

import base64
import json
import time
import unicodedata
import uuid
from difflib import SequenceMatcher
from html import escape
from io import BytesIO
from urllib.parse import quote_plus

import requests
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


def texto_ou_nao_confirmado(valor):
    if valor is None:
        return "Nao confirmado"
    texto = str(valor).strip()
    return texto if texto else "Nao confirmado"


def formatar_resultado_estruturado(dados):
    status = dados.get("status_identificacao", "incerta")
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

    linhas = [
        "## 🃏 Identificacao",
        f"**Status:** {rotulos_status.get(status, '🔴 Identificacao incerta')}",
        "",
        f"- **Jogo:** {texto_ou_nao_confirmado(dados.get('jogo'))}",
        f"- **Nome:** {texto_ou_nao_confirmado(dados.get('nome_carta'))}",
        f"- **Colecao / Set:** {texto_ou_nao_confirmado(dados.get('colecao_set'))}",
        f"- **Numero:** {texto_ou_nao_confirmado(dados.get('numero_carta'))}",
        f"- **Raridade:** {texto_ou_nao_confirmado(dados.get('raridade'))}",
        f"- **Variante:** {texto_ou_nao_confirmado(dados.get('variante'))}",
        f"- **Idioma:** {texto_ou_nao_confirmado(dados.get('idioma_carta'))}",
        f"- **Ano:** {texto_ou_nao_confirmado(dados.get('ano'))}",
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
    linhas.extend([
        "",
        "## 🔎 Condicao aparente",
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
    linhas.extend([
        "",
        "## ⚠️ Autenticidade visual",
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
        "Dados de preco atualizados ainda nao estao conectados nesta versao. "
        "O CardCraftAI nao inventa valores de mercado.",
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
        "*Reliability 1.0: a identificacao acima ainda nao foi validada contra um catalogo TCG externo. "
        "Essa validacao sera adicionada na proxima fase.*",
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
                _similaridade_catalogo(
                    colecao,
                    set_nome,
                )
                * 30
            )

        if numero:
            numero_norm = _normalizar_texto_catalogo(numero)
            numero_carta_norm = _normalizar_texto_catalogo(
                numero_carta
            )

            if (
                numero_norm
                and
                numero_norm == numero_carta_norm
            ):
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
                score,
                carta,
            )
        )

    pontuadas.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        carta
        for _, carta in pontuadas[:limite]
    ]


def buscar_cartas_catalogo_pokemon(
    nome,
    colecao="",
    numero="",
    limite=12,
):
    cartas = consultar_catalogo_pokemon(
        nome
    )

    return ranquear_cartas_catalogo(
        cartas,
        nome=nome,
        colecao=colecao,
        numero=numero,
        limite=limite,
    )


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

    return {
        "id": carta.get("id"),
        "nome": carta.get("name"),
        "set": set_dados.get("name"),
        "numero": carta.get("number"),
        "raridade": carta.get("rarity"),
        "artista": carta.get("artist"),
        "ano": (
            str(
                set_dados.get(
                    "releaseDate",
                    "",
                )
            )[:4]
            or None
        ),
    }



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

    return f"{simbolo} {texto}"


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
    Mostra apenas preços que já vieram no objeto da API.

    Não chama o redirecionador de preços e não afirma que
    os valores são tempo real. A data exibida é a data de
    atualização informada pelo próprio catálogo.
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
        "💰 Referências de mercado do catálogo",
        expanded=False,
    ):
        st.caption(
            "Valores fornecidos pelo catálogo Pokémon TCG. "
            "Eles podem estar desatualizados e não garantem "
            "estoque, condição, idioma ou preço final."
        )

        if tcg_prices:
            st.markdown(
                "#### TCGplayer — USD"
            )

            atualizado = tcgplayer.get(
                "updatedAt"
            )

            if atualizado:
                st.caption(
                    "Última atualização informada pelo catálogo: "
                    + str(atualizado)
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
                        f"mercado {mercado}"
                    )

                if minimo:
                    partes.append(
                        f"mínimo {minimo}"
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
            st.markdown(
                "#### Cardmarket — EUR"
            )

            atualizado = cardmarket.get(
                "updatedAt"
            )

            if atualizado:
                st.caption(
                    "Última atualização informada pelo catálogo: "
                    + str(atualizado)
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
    titulo=(
        "✅ Carta selecionada no catálogo"
    ),
):
    if not carta:
        return

    resumo = _resumo_carta_catalogo(
        carta
    )

    st.success(
        titulo
    )

    col_img, col_info = st.columns(
        [1, 2],
        gap="large",
    )

    with col_img:
        _renderizar_imagem_clicavel(
            carta
        )
        st.caption(
            "Clique na imagem para abrir "
            "a versão maior."
        )

    with col_info:
        st.markdown(
            f"### {texto_ou_nao_confirmado(resumo.get('nome'))}"
        )
        st.write(
            "**Coleção / Set:** "
            + texto_ou_nao_confirmado(
                resumo.get("set")
            )
        )
        st.write(
            "**Número:** "
            + texto_ou_nao_confirmado(
                resumo.get("numero")
            )
        )
        st.write(
            "**Raridade:** "
            + texto_ou_nao_confirmado(
                resumo.get("raridade")
            )
        )
        st.write(
            "**Artista:** "
            + texto_ou_nao_confirmado(
                resumo.get("artista")
            )
        )
        st.write(
            "**ID do catálogo:** "
            + texto_ou_nao_confirmado(
                resumo.get("id")
            )
        )

        url_tcgplayer = (
            _url_busca_tcgplayer(
                carta
            )
        )

        if url_tcgplayer:
            st.caption(
                "Busca externa direta no TCGplayer. "
                "O CardCraftAI não depende do redirecionador "
                "de preços do catálogo para abrir este link."
            )

            st.link_button(
                "🛒 Buscar esta carta no TCGplayer",
                url_tcgplayer,
                use_container_width=True,
            )

        _mostrar_precos_referencia_catalogo(
            carta
        )


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
        st.warning(
            "Nenhuma correspondência visual foi encontrada "
            "no catálogo Pokémon."
        )
        return

    st.caption(
        "Clique em uma imagem para ampliá-la. "
        "Use “Selecionar esta carta” para indicar "
        "a correspondência correta."
    )

    colunas_por_linha = 4

    for inicio in range(
        0,
        len(cartas),
        colunas_por_linha,
    ):
        bloco = cartas[
            inicio:
            inicio + colunas_por_linha
        ]
        colunas = st.columns(
            colunas_por_linha,
            gap="medium",
        )

        for coluna, carta in zip(
            colunas,
            bloco,
        ):
            with coluna:
                _renderizar_imagem_clicavel(
                    carta
                )

                set_nome = (
                    (carta.get("set") or {})
                    .get("name")
                )
                numero = carta.get(
                    "number"
                )
                raridade = carta.get(
                    "rarity"
                )

                st.markdown(
                    "**"
                    + escape(
                        str(
                            carta.get(
                                "name",
                                "Carta Pokémon",
                            )
                        )
                    )
                    + "**"
                )

                st.caption(
                    (
                        texto_ou_nao_confirmado(
                            set_nome
                        )
                        + " • #"
                        + texto_ou_nao_confirmado(
                            numero
                        )
                    )
                )

                if raridade:
                    st.caption(
                        str(raridade)
                    )

                carta_id = str(
                    carta.get(
                        "id",
                        inicio,
                    )
                )

                st.button(
                    "✅ Selecionar esta carta",
                    key=(
                        f"catalogo_selecionar_"
                        f"{contexto}_{carta_id}"
                    ),
                    use_container_width=True,
                    on_click=selecionar_carta_catalogo,
                    args=(
                        contexto,
                        carta,
                    ),
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
        f"Ano do set: {resumo.get('ano')}"
    )


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
        return

    nome = resultado.get(
        "nome_carta"
    )

    if not nome:
        return

    st.divider()
    st.subheader(
        "🖼️ Correspondências no catálogo Pokémon"
    )
    st.caption(
        "Esta consulta ao catálogo não consome "
        "um novo crédito."
    )

    try:
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
        )
    except Exception as erro:
        st.warning(
            "A análise foi concluída, mas o catálogo "
            "visual não pôde ser consultado."
        )
        st.caption(
            str(erro)
        )
        return

    selecionada = st.session_state.get(
        "catalogo_selecionada_foto"
    )

    if selecionada:
        mostrar_carta_catalogo_selecionada(
            selecionada,
            titulo=(
                "✅ Correspondência escolhida "
                "para esta análise"
            ),
        )

    mostrar_galeria_catalogo(
        cartas,
        contexto="foto",
    )


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

if "catalogo_resultados_nome" not in st.session_state:
    st.session_state.catalogo_resultados_nome = []

if "catalogo_consulta_nome" not in st.session_state:
    st.session_state.catalogo_consulta_nome = None

if "catalogo_selecionada_nome" not in st.session_state:
    st.session_state.catalogo_selecionada_nome = None

if "catalogo_selecionada_foto" not in st.session_state:
    st.session_state.catalogo_selecionada_foto = None


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

    st.session_state.catalogo_resultados_nome = []
    st.session_state.catalogo_consulta_nome = None
    st.session_state.catalogo_selecionada_nome = None
    st.session_state.catalogo_selecionada_foto = None


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
Voce atua como especialista em Trading Card Games (TCG), mas deve priorizar
precisao e incerteza explicita acima de completar campos.

Responda em {idioma} nos campos descritivos.

REGRAS OBRIGATORIAS:
- Retorne somente dados compativeis com o schema solicitado.
- Quando um dado nao puder ser confirmado, use null e inclua o nome do campo
  em campos_incertos.
- Nao invente colecao, numero, raridade, variante, idioma ou ano.
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
            raise RuntimeError("O Gemini respondeu sem conteudo.")

        try:
            dados = json.loads(texto_json)
        except json.JSONDecodeError as erro_json:
            raise RuntimeError(
                "O Gemini nao retornou JSON valido. "
                f"Detalhes: {erro_json}"
            )

        return validar_analise_estruturada(dados)

    except Exception as erro:
        raise RuntimeError(
            "Falha na analise estruturada com Gemini 3.6 Flash.\n\n"
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
    "análise e catálogo visual de cartas TCG."
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
        "📊 Resultado da Analise"
    )

    if isinstance(resultado, dict):
        conteudo = formatar_resultado_estruturado(resultado)
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

    st.divider()

    st.info(
        "🧪 A pesquisa web esta temporariamente desativada nesta versao."
    )

    st.caption(
        "💎 A analise concluida consumiu 1 credito."
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

                        st.session_state.catalogo_selecionada_foto = None

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

        mostrar_catalogo_para_analise_foto(
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
        "🖼️ Buscar e comparar imagens no catálogo Pokémon "
        "é grátis. A análise especializada consome 1 crédito."
    )

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:
        termo_busca = st.text_input(
            "Nome da carta",
            placeholder="Ex.: Charizard GX",
            key="termo_busca",
        )

    with col2:
        colecao_busca = st.text_input(
            "Coleção / Set",
            placeholder="Ex.: SM Black Star Promos",
            key="colecao_busca",
        )

    if st.button(
        "🖼️ Buscar no catálogo — grátis",
        use_container_width=True,
        key="btn_buscar_catalogo_nome",
    ):
        termo = termo_busca.strip()
        colecao = colecao_busca.strip()

        if not termo:
            st.warning(
                "Digite o nome da carta para pesquisar "
                "no catálogo."
            )
        else:
            with st.spinner(
                "📚 Procurando cartas no catálogo Pokémon..."
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
                        "Não foi possível consultar "
                        "o catálogo Pokémon agora."
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
            titulo=(
                "✅ Carta escolhida para esta análise"
            ),
        )

        st.info(
            "A seleção foi registrada. "
            "Você pode continuar comparando outras versões "
            "ou usar esta carta na análise especializada."
        )

    if consulta_catalogo:
        st.divider()

        st.subheader(
            "🖼️ Resultados visuais do catálogo"
        )

        st.caption(
            "Busca realizada por: "
            f"{consulta_catalogo.get('nome', '')}"
            + (
                " • "
                + consulta_catalogo.get(
                    "colecao",
                    ""
                )
                if consulta_catalogo.get(
                    "colecao"
                )
                else ""
            )
        )

        if resultados_catalogo:
            mostrar_galeria_catalogo(
                resultados_catalogo,
                contexto="nome",
            )
        else:
            st.warning(
                "Nenhuma carta correspondente foi encontrada."
            )

    st.divider()

    st.subheader(
        "🤖 Análise especializada"
    )

    if carta_selecionada:
        st.caption(
            "A análise usará a entrada que você "
            "selecionou no catálogo."
        )
    else:
        st.caption(
            "Sem uma carta selecionada, a análise usará "
            "somente o nome e a coleção digitados."
        )

    if creditos <= 0:
        st.warning(
            "💎 Você não possui créditos disponíveis "
            "para gerar uma nova análise."
        )
        st.info(
            "A busca visual acima continua gratuita."
        )

    if st.button(
        "🤖 Analisar — 1 crédito",
        use_container_width=True,
        key="btn_analise_nome",
        disabled=(creditos <= 0),
    ):
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
