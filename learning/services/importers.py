import io
import zipfile
from pathlib import Path
from .core import InputError,clean_text,MAX_READING_CHARS
MAX_FILE_BYTES=8*1024*1024

def extract_reading(upload):
    if upload.size>MAX_FILE_BYTES: raise InputError('File tối đa 8 MB. Chỉ nhập riêng phần bài đọc.')
    suffix=Path(upload.name).suffix.lower()
    raw=upload.read(MAX_FILE_BYTES+1)
    if len(raw)>MAX_FILE_BYTES: raise InputError('File quá lớn.')
    try:
        if suffix in ('.txt','.md'):
            text=raw.decode('utf-8-sig')
        elif suffix=='.docx':
            from docx import Document
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                total=sum(i.file_size for i in z.infolist())
                if total>40*1024*1024 or len(z.infolist())>2000: raise InputError('DOCX quá lớn sau giải nén.')
                if 'word/document.xml' not in z.namelist(): raise InputError('File không phải DOCX hợp lệ.')
            doc=Document(io.BytesIO(raw))
            # iter_inner_content preserves paragraph/table order (python-docx >= 1.2).
            lines=[]
            for item in doc.iter_inner_content():
                if hasattr(item,'rows'):
                    lines.extend(' | '.join(c.text for c in row.cells) for row in item.rows)
                else: lines.append(item.text)
            text='\n\n'.join(lines)
        elif suffix=='.pdf':
            from pypdf import PdfReader
            reader=PdfReader(io.BytesIO(raw),strict=False)
            if reader.is_encrypted: raise InputError('PDF có mật khẩu; hãy mở khóa rồi nhập lại.')
            if len(reader.pages)>30: raise InputError('Chỉ nhập tối đa 30 trang một lần.')
            text='\n\n'.join(p.extract_text() or '' for p in reader.pages)
            if len(text.strip())<30: raise InputError('Không đọc được lớp chữ: PDF có thể là ảnh scan. Bản này chưa có OCR; hãy dán văn bản đã nhận dạng.')
        else: raise InputError('Chỉ hỗ trợ TXT, MD, DOCX và PDF có lớp chữ.')
    except InputError: raise
    except UnicodeDecodeError as exc: raise InputError('TXT/MD cần lưu ở mã hóa UTF-8.') from exc
    except Exception as exc: raise InputError('Không đọc được file. File có thể hỏng hoặc không đúng định dạng.') from exc
    return clean_text(text,MAX_READING_CHARS,True)
