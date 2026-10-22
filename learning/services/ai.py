import httpx
from django.conf import settings
from .core import InputError,parse_json
from .analysis import validate_schema,SYSTEM

def enabled():
    return settings.AI_PROVIDER=='openai' and bool(settings.OPENAI_API_KEY)

def request_json(prompt,schema,name,max_tokens=12000):
    """No keys in browser; no automatic retries that could duplicate charges."""
    if not enabled(): raise InputError('Chưa bật API. Dùng Copy prompt + Dán JSON, hoặc cấu hình .env theo README.')
    payload={'model':settings.OPENAI_MODEL,'store':False,
             'input':[{'role':'developer','content':SYSTEM},{'role':'user','content':prompt}],
             'max_output_tokens':max_tokens,
             'text':{'format':{'type':'json_schema','name':name,'strict':True,'schema':schema}}}
    try:
        with httpx.Client(timeout=httpx.Timeout(150,connect=15),follow_redirects=False) as client:
            response=client.post('https://api.openai.com/v1/responses',
                headers={'Authorization':'Bearer '+settings.OPENAI_API_KEY,'Content-Type':'application/json'},json=payload)
    except httpx.RequestError as exc:
        raise InputError('Không kết nối được API hoặc đã hết thời gian chờ. Kiểm tra mạng; không gửi lại liên tục.') from exc
    if response.status_code in (401,403): raise InputError('API từ chối key hoặc quyền truy cập model. Kiểm tra OPENAI_API_KEY và OPENAI_MODEL trong .env.')
    if response.status_code==429: raise InputError('API báo vượt hạn mức/tốc độ hoặc hết ngân sách. Kiểm tra tài khoản API.')
    if response.status_code>=400: raise InputError(f'API trả mã {response.status_code}. Kiểm tra model hỗ trợ Responses + Structured Outputs.')
    try: body=response.json()
    except ValueError as exc: raise InputError('API trả nội dung không hợp lệ.') from exc
    if body.get('status')!='completed': raise InputError('AI chưa trả kết quả hoàn chỉnh. Hãy chia bài thành phần ngắn hơn; kết quả chưa được lưu.')
    chunks=[]
    for item in body.get('output',[]):
        if item.get('type')=='message':
            for c in item.get('content',[]):
                if c.get('type')=='refusal': raise InputError('AI từ chối xử lý nội dung này.')
                if c.get('type')=='output_text': chunks.append(c.get('text',''))
    if not chunks: raise InputError('AI không trả kết quả văn bản.')
    data=parse_json(''.join(chunks))
    validate_schema(data,schema)
    return data
