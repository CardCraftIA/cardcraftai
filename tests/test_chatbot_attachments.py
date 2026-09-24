from io import BytesIO
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from PIL import Image
from pypdf import PdfWriter
from reportlab.pdfgen import canvas

from chatbot_attachments import prepare_attachment, ask_attachment_ai, is_text_request, extract_text_answer


class Upload(BytesIO):
    def __init__(self, data, name, mime):
        super().__init__(data)
        self.name, self.type, self.size = name, mime, len(data)


class AttachmentTests(TestCase):
    def test_photo_is_validated_downscaled_and_sent_as_image_only_when_requested(self):
        raw = BytesIO()
        Image.new('RGB', (2000, 1000), 'red').save(raw, format='PNG')
        prepared = prepare_attachment(Upload(raw.getvalue(), 'card.png', 'image/png'))
        self.assertEqual(prepared['kind'], 'image')
        self.assertEqual(prepared['mime_type'], 'image/jpeg')
        self.assertEqual(prepared['text'], '')
        ai = Mock()
        ai.interactions.create.return_value = SimpleNamespace(output_text='Visible: Pikachu')
        self.assertEqual(ask_attachment_ai(ai, 'gemini', 'Identify', 'English', prepared), 'Visible: Pikachu')
        payload = ai.interactions.create.call_args.kwargs['input']
        self.assertEqual(payload[0]['type'], 'image')
        self.assertNotIn('price of this card', payload[1]['text'])

    def test_pdf_is_validated_and_text_request_needs_no_ai(self):
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        raw = BytesIO()
        writer.write(raw)
        prepared = prepare_attachment(Upload(raw.getvalue(), 'sample.pdf', 'application/pdf'))
        self.assertEqual(prepared['kind'], 'pdf')
        self.assertEqual(prepared['text'], '')
        self.assertTrue(is_text_request('Extract text from this PDF'))
        self.assertIsNone(extract_text_answer(prepared))
        ai = Mock()
        ai.interactions.create.return_value = SimpleNamespace(output_text='This page has no readable card text')
        ask_attachment_ai(ai, 'gemini', 'What is here?', 'English', prepared)
        self.assertEqual(ai.interactions.create.call_args.kwargs['input'][0]['type'], 'document')

    def test_invalid_signature_and_oversize_rejected(self):
        for data, name, mime in ((b'not a pdf', 'bad.pdf', 'application/pdf'),
                                 (b'%PDF-' + b'x' * (8 * 1024 * 1024), 'huge.pdf', 'application/pdf')):
            with self.subTest(name=name), self.assertRaises(ValueError):
                prepare_attachment(Upload(data, name, mime))
        self.assertRaises(ValueError, prepare_attachment, Upload(b'not an image', 'x.png', 'image/png'))
        writer = PdfWriter()
        for _ in range(6):
            writer.add_blank_page(width=200, height=200)
        raw = BytesIO()
        writer.write(raw)
        with self.assertRaisesRegex(ValueError, 'oversized PDF'):
            prepare_attachment(Upload(raw.getvalue(), 'six-pages.pdf', 'application/pdf'))

    def test_extracted_pdf_text_does_not_call_ai(self):
        raw = BytesIO()
        doc = canvas.Canvas(raw)
        doc.drawString(50, 700, 'Pikachu 58/102 Base Set')
        doc.save()
        attachment = prepare_attachment(Upload(raw.getvalue(), 'card.pdf', 'application/pdf'))
        self.assertIn('Pikachu 58/102 Base Set', extract_text_answer(attachment))
        self.assertTrue(is_text_request('Transcreva o texto deste PDF'))
