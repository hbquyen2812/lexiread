import io,unittest
from learning.services.core import InputError
from learning.services.importers import extract_reading
class Upload(io.BytesIO):
    def __init__(self,name,raw):super().__init__(raw);self.name=name;self.size=len(raw)
class ImporterTests(unittest.TestCase):
    def test_utf8_txt(self):self.assertEqual(extract_reading(Upload('test.txt','Hello.\n\nXin chào.'.encode())), 'Hello.\n\nXin chào.')
    def test_invalid_encoding(self):
        with self.assertRaises(InputError):extract_reading(Upload('x.txt',b'\xff\xff'))
    def test_unknown_type(self):
        with self.assertRaises(InputError):extract_reading(Upload('x.exe',b'test'))
    def test_oversize(self):
        u=Upload('x.txt',b'a');u.size=9*1024*1024
        with self.assertRaises(InputError):extract_reading(u)
    def test_docx(self):
        try:from docx import Document
        except ImportError:self.skipTest('python-docx not installed')
        doc=Document();doc.add_paragraph('First paragraph.');doc.add_paragraph('Second paragraph.')
        data=io.BytesIO();doc.save(data)
        self.assertEqual(extract_reading(Upload('test.docx',data.getvalue())),'First paragraph.\n\nSecond paragraph.')
    def test_corrupt_docx(self):
        with self.assertRaises(InputError):extract_reading(Upload('x.docx',b'not a zip'))
    def test_pdf_text(self):
        try:from reportlab.pdfgen.canvas import Canvas
        except ImportError:self.skipTest('reportlab optional fixture generator missing')
        data=io.BytesIO();c=Canvas(data);c.drawString(72,720,'A useful reading passage with more than thirty characters.');c.save()
        self.assertIn('useful reading passage',extract_reading(Upload('x.pdf',data.getvalue())))
    def test_image_only_pdf_rejected(self):
        try:from pypdf import PdfWriter
        except ImportError:self.skipTest('pypdf missing')
        data=io.BytesIO();writer=PdfWriter();writer.add_blank_page(width=100,height=100);writer.write(data)
        with self.assertRaises(InputError):extract_reading(Upload('x.pdf',data.getvalue()))
