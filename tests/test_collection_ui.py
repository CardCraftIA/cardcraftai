"""Exercises the real Streamlit module against an in-memory demo client."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from collection import save_edit
from pathlib import Path
try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None


@unittest.skipIf(AppTest is None, 'Streamlit not installed in this test environment')
class CollectionUITests(unittest.TestCase):
    def editor(self, language='English', variant='Holo'):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'prototypes' / 'collection_preview.py')).run()
        app.session_state['preview_items'][0].update(language=language, variant=variant)
        # Remount the entry to load the fixture as a fresh saved record.
        app.session_state['preview_items'][0]['id'] = 'saved-entry'
        app.run()
        self.assertFalse(app.exception)
        return app

    def select(self, app, label):
        return next(s for s in app.selectbox if s.label == label)

    def save(self, app):
        next(b for b in app.button if b.label == 'Salvar').click().run()
        self.assertFalse(app.exception)

    def test_save_success_feedback_and_busy_state(self):
        app = self.editor()
        app.text_area[0].set_value('Saved note')
        def confirmed_save(*args):
            import streamlit as st
            self.assertTrue(st.session_state['collection_save_demo_saved-entry'])
            return save_edit(*args)
        with patch('collection.save_edit', side_effect=confirmed_save) as update:
            self.save(app)
            self.assertEqual(update.call_count, 1)
        self.assertFalse(app.success)
        self.assertEqual(len(app.get('toast')), 1)
        self.assertEqual(app.get('toast')[0].proto.body, 'Alterações salvas com sucesso.')
        self.assertEqual(app.get('toast')[0].proto.icon, '✅')
        self.assertTrue(next(e for e in app.expander if e.label == 'Editar exemplar').proto.expanded)
        self.assertFalse(app.error)
        self.assertEqual(app.text_area[0].value, 'Saved note')
        self.assertFalse(app.session_state['collection_save_demo_saved-entry'])
        self.assertFalse(next(b for b in app.button if b.label == 'Salvar').disabled)
        app.run()
        self.assertFalse(app.success)
        self.assertFalse(app.get('toast'))

    def test_save_failure_preserves_entries_and_allows_retry(self):
        for response in ('exception', 'empty'):
            with self.subTest(response=response):
                app = self.editor()
                original = dict(app.session_state['preview_items'][0])
                app.number_input[0].set_value(9)
                app.text_area[0].set_value('Unsaved private note')
                self.select(app, 'Idioma da carta').select('Japanese')
                kwargs = ({'side_effect': RuntimeError('TECHNICAL_SECRET_SENTINEL')} if response == 'exception'
                          else {'return_value': SimpleNamespace(data=[])})
                with patch('collection.save_edit', **kwargs):
                    self.save(app)
                self.assertEqual(app.session_state['preview_items'][0], original)
                self.assertFalse(app.success)
                self.assertFalse(app.get('toast'))
                self.assertIn('Seus dados foram mantidos', app.error[0].value)
                self.assertNotIn('TECHNICAL_SECRET_SENTINEL', app.error[0].value)
                self.assertEqual(app.text_area[0].value, 'Unsaved private note')
                self.assertEqual(app.number_input[0].value, 9)
                self.assertEqual(self.select(app, 'Idioma da carta').value, 'Japanese')
                self.assertFalse(next(b for b in app.button if b.label == 'Salvar').disabled)
                self.save(app)
                self.assertFalse(app.error)
                self.assertTrue(app.get('toast'))
                self.assertFalse(app.success)
                self.assertEqual(app.session_state['preview_items'][0]['notes'], 'Unsaved private note')

    def test_feedback_uses_provided_app_translator(self):
        source = (Path(__file__).resolve().parents[1] / 'prototypes' / 'collection_preview.py').read_text(encoding='utf-8')
        source = source.replace("render_collection(st, DemoClient(), 'demo', True)",
                                "render_collection(st, DemoClient(), 'demo', True, translate=lambda key: {'collection_saved': 'Changes saved successfully.', 'collection_saving': 'Saving…'}[key])")
        app = AppTest.from_string(source).run()
        self.save(app)
        self.assertEqual(app.get('toast')[0].proto.body, 'Changes saved successfully.')
        self.assertEqual(app.get('toast')[0].proto.icon, '✅')

    def test_saved_language_and_variant(self):
        app = self.editor()
        self.assertEqual(self.select(app, 'Idioma da carta').value, 'English')
        self.assertEqual(self.select(app, 'Variante').value, 'Holo')
        self.save(app)
        self.assertEqual(app.session_state['preview_items'][0]['language'], 'English')
        self.assertEqual(app.session_state['preview_items'][0]['variant'], 'Holo')

    def test_change_language_and_variant(self):
        app = self.editor()
        original = dict(app.session_state['preview_items'][0])
        self.select(app, 'Variante').select('Reverse Holo').run()
        self.assertEqual(app.session_state['preview_items'][0], original)
        self.select(app, 'Idioma da carta').select('Japanese')
        self.save(app)
        expected = dict(original, language='Japanese', variant='Reverse Holo')
        self.assertEqual(app.session_state['preview_items'][0], expected)
        self.assertEqual(self.select(app, 'Idioma da carta').value, 'Japanese')
        self.assertEqual(self.select(app, 'Variante').value, 'Reverse Holo')

    def test_custom_variant(self):
        app = self.editor()
        self.select(app, 'Variante').select(0).run()
        custom = next(t for t in app.text_input if t.label == 'Variante personalizada')
        self.assertEqual(custom.max_chars, 120)
        custom.set_value('Stamped tournament edition')
        self.save(app)
        self.assertEqual(app.session_state['preview_items'][0]['variant'], 'Stamped tournament edition')
        self.assertEqual(next(t for t in app.text_input if t.label == 'Variante personalizada').value, 'Stamped tournament edition')

    def test_unknown_saved_values_are_preserved(self):
        app = self.editor(language='Português (Brasil)', variant='Edição antiga especial')
        self.assertEqual(self.select(app, 'Idioma da carta').value, 'Português (Brasil)')
        self.assertEqual(self.select(app, 'Variante').value, 'Edição antiga especial')
        self.save(app)
        self.assertEqual(app.session_state['preview_items'][0]['language'], 'Português (Brasil)')
        self.assertEqual(app.session_state['preview_items'][0]['variant'], 'Edição antiga especial')
        self.select(app, 'Variante').select(0).run()
        self.assertEqual(next(t for t in app.text_input if t.label == 'Variante personalizada').value, 'Edição antiga especial')

    def test_not_specified_uses_empty_saved_values(self):
        app = self.editor(language='', variant='')
        self.assertEqual(self.select(app, 'Idioma da carta').value, '')
        self.assertEqual(self.select(app, 'Variante').value, '')
        self.save(app)
        self.assertEqual(app.session_state['preview_items'][0]['language'], '')
        self.assertEqual(app.session_state['preview_items'][0]['variant'], '')

    def test_notes_load_edit_save_and_clear(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'prototypes' / 'collection_preview.py')).run()
        app.session_state['preview_items'][0]['notes'] = 'Nota existente'
        app.session_state['preview_items'][1]['notes'] = 'Nota de outra carta'
        app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_area[0].value, 'Nota existente')
        self.assertEqual(app.text_area[0].max_chars, 2000)
        for notes in ('Nota editada\nSegunda linha', 'a' * 2000, ''):
            app.text_area[0].set_value(notes)
            next(b for b in app.button if b.label == 'Salvar').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['preview_items'][0]['notes'], notes)
            self.assertEqual(app.text_area[0].value, notes)
            self.assertEqual(app.session_state['preview_items'][1]['notes'], 'Nota de outra carta')

    def test_filter_edit_and_export(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'prototypes' / 'collection_preview.py')).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '11')
        app.number_input[0].set_value(4)
        next(b for b in app.button if b.label == 'Salvar').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value, '13')
        app.text_input[0].set_value('Pikachu').run()
        self.assertEqual(len(app.number_input), 1)
        for fmt in ['xlsx', 'pdf', 'docx']:
            next(s for s in app.selectbox if s.label == 'Formato').set_value(fmt).run()
            next(b for b in app.button if b.label == 'Preparar arquivo').click().run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.get('download_button')), 1)
