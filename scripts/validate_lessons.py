"""Check authored lesson structure and exact evidence without a database or AI."""
import json,sys
from collections import Counter
from pathlib import Path
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from learning.services.catalog import validate_lesson

def main():
    folder=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'data/lessons'
    files=sorted(folder.glob('*.json'))
    if not files:raise SystemExit(f'Không có bài JSON trong {folder}')
    lessons=[];slugs=set()
    for path in files:
        try:
            value=validate_lesson(json.loads(path.read_text(encoding='utf-8')))
            if value['slug'] in slugs:raise ValueError('Slug bị trùng trong bộ dữ liệu')
            slugs.add(value['slug']);lessons.append(value)
            print(f'OK {value["level"]:2} | {len(value["text"].split()):3} words | {value["title"]}')
        except (ValueError,TypeError,KeyError,AttributeError) as exc:
            raise SystemExit(f'ERROR {path.name}: {exc}') from exc
    print(f'{len(lessons)} lessons; {dict(Counter(x["level"] for x in lessons))}; '
          f'{sum(len(x["questions"]) for x in lessons)} questions; '
          f'{sum(len(x["analysis"]["vocabulary"]) for x in lessons)} vocabulary suggestions.')
    print('Cấu trúc/trích dẫn hợp lệ không chứng minh nghĩa, bản dịch hoặc mức CEFR đã được chuyên gia kiểm định.')
if __name__=='__main__':main()
