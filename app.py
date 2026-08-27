import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

st.set_page_config(page_title='CardCraftAI', page_icon='🃏', layout='wide')

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
        if st.button('🔍 Analisar Carta com IA'):
            with st.spinner('Analisando mercado e gerando links de busca...'):
                try:
                    prompt = 'Analise a carta e retorne formatado em tópicos: 1. Nome da Carta e Numeração, 2. Jogo/Coleção, 3. Raridade, 4. Condição visual, 5. Título chamativo para venda, 6. Preço médio estimado. Por fim, adicione links clicáveis em Markdown de pesquisa para esta exata carta nas seguintes plataformas: Mercado Livre, eBay, TCGPlayer, Shopee, Amazon e LigaPokemon/LigaMagic.'
                    response = client.models.generate_content(model='gemini-3.6-flash', contents=[image, prompt])
                    st.subheader('📋 Resultado da Análise e Mercado Multiplataforma')
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f'Erro na análise: {e}')
