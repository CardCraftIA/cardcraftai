"""Run with streamlit run prototypes/collection_preview.py. No Supabase access."""
import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
from collection import render_collection

st.set_page_config(page_title='CardCraftAI · Prévia da coleção', layout='wide')
st.info('PRÉVIA LOCAL · Dados fictícios · Alterações somente nesta sessão · Sem conexão com sua conta')
if 'preview_items' not in st.session_state:
    st.session_state.preview_items = [dict(
        id=str(index), user_id='demo', catalog_id=f'demo-{index}', card_name=name,
        set_name='Promos' if index % 2 else 'Favoritos', card_number=f'{index:03}',
        image_url='', quantity=index % 3 + 1, condition='Not assessed',
        language='Português', variant='', notes='', wishlist=index == 2,
    ) for index, name in enumerate(['Charizard', 'Pikachu', 'Eevee', 'Mewtwo', 'Gengar'], 1)]


class DemoQuery:
    def __init__(self):
        self.filters = []
        self.bounds = (0, 499)
        self.values = None
    def select(self, fields): return self
    def order(self, field): return self
    def eq(self, field, value):
        self.filters.append((field, value))
        return self
    def range(self, start, end):
        self.bounds = (start, end)
        return self
    def update(self, values):
        self.values = values
        return self
    def execute(self):
        rows = [x for x in st.session_state.preview_items if all(x[k] == v for k, v in self.filters)]
        if self.values is not None:
            for row in rows:
                row.update(self.values)
        return SimpleNamespace(data=rows[self.bounds[0]:self.bounds[1] + 1])


class DemoClient:
    def table(self, name): return DemoQuery()


render_collection(st, DemoClient(), 'demo', True)
