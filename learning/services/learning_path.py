"""Explainable recommendations from owned progress, never an AI request."""
from datetime import timedelta
from django.utils import timezone
from ..models import LearningProfile, FoundationAttempt, Vocabulary, Reading, CuratedLesson, ToeicPractice, ToeicAttempt, LessonAttempt
from .core import InputError
from .foundation_content import LEVELS, GOALS, units

START = {
 'A1': {'title':'Bắt đầu bằng những câu quen thuộc', 'intro':'Mỗi buổi học một ít. Hiểu được một câu ngắn đã là một bước tiến.',
        'steps':[['Ngữ pháp','Học be, đại từ và câu đơn. Đọc ví dụ, tự thay tên hoặc đồ vật rồi làm bài tập.','#learn/grammar'],['Từ vựng','Chọn một bộ về sinh hoạt. Học 5 từ, đọc cả câu ví dụ rồi lưu những từ bạn muốn nhớ.','#learn/vocabulary'],['Đọc & ôn','Chọn bài pre-A1 hoặc A1. Thử đọc trước, mở bản dịch khi cần; hôm sau quay lại ôn từ.','#catalog']],
        'tip':'Chưa cần làm đề IELTS/TOEIC dài. Video VOA hoặc Easy English là điểm bắt đầu nhẹ nhàng.'},
 'A2': {'title':'Nối câu thành câu chuyện của bạn', 'intro':'Dùng điều đã học để kể một ngày, một chuyến đi hoặc một dự định.',
        'steps':[['Ngữ pháp','Ôn quá khứ, tương lai và so sánh. Sau mỗi bài, viết hai câu về chính mình.','#learn/grammar'],['Đọc có mục tiêu','Chọn bài A2. Tìm ý chính trước; chỉ tra những từ làm bạn mất mạch câu chuyện.','#catalog'],['Giữ từ trong ngữ cảnh','Lưu cả cụm từ và câu ví dụ. Ôn các thẻ đến hạn trước khi thêm từ mới.','#study']],
        'tip':'Nếu muốn TOEIC, bắt đầu với ngữ pháp Part 5 và email ngắn; chưa cần bấm giờ cả đề.'},
 'B1': {'title':'Hiểu ý chính rồi tìm bằng chứng', 'intro':'Tăng dần độ dài bài đọc và bắt đầu luyện kỹ năng phục vụ mục tiêu của bạn.',
        'steps':[['Lấp chỗ còn hổng','Xem lại điều kiện, bị động và mệnh đề quan hệ. Ghi một ví dụ cho mỗi lỗi vừa sửa.','#learn/grammar'],['Luyện đúng dạng','IELTS: thử True / False / Not Given. TOEIC: luyện Part 5–6 rồi đọc email Part 7.','#guides'],['Đọc và diễn đạt lại','Chọn bài B1; sau khi kiểm tra đáp án, tóm tắt bằng 2–3 câu và lưu vài cụm hữu ích.','#catalog']],
        'tip':'Đừng tăng số lượng chỉ để hoàn thành. Một lời giải bạn hiểu rõ có ích hơn nhiều đáp án đoán đúng.'},
 'B2': {'title':'Đọc sâu hơn, làm bài có chiến lược', 'intro':'Chú ý cách tác giả liên kết ý, dùng từ gần nghĩa và thể hiện quan điểm.',
        'steps':[['Tăng độ chính xác','Ôn câu điều kiện, động từ khuyết thiếu và cách nối ý; làm lại những dạng còn sai.','#learn/grammar'],['Luyện theo mục tiêu','IELTS: tìm paraphrase và ý chính từng đoạn. TOEIC: nối thông tin giữa hai hoặc ba văn bản.','#guides'],['Mở rộng cách diễn đạt','Học từ theo chủ đề, giữ cả collocation. Thử dùng lại khi tóm tắt bài hoặc viết email.','#learn/vocabulary']],
        'tip':'Bắt đầu bấm giờ sau khi đã hiểu cách làm. Dành thời gian xem bằng chứng cho cả câu đúng và sai.'},
 'C1': {'title':'Đọc tinh ý, diễn đạt có chủ đích', 'intro':'Tập nhận ra sắc thái, giới hạn của một nhận định và cách diễn đạt phù hợp từng hoàn cảnh.',
        'steps':[['Ngữ pháp trong ngữ cảnh','Học đảo ngữ, nhấn mạnh và cách diễn đạt thận trọng; so sánh câu trước và sau khi viết lại.','#learn/grammar'],['Từ chính xác hơn','Tra nghĩa phù hợp ngữ cảnh, collocation và văn phong. Không thay từ chỉ vì từ đó có vẻ khó hơn.','#learn/dictionary'],['Đối chiếu với bài mẫu','Luyện bài học thuật rồi mở tài liệu chính thức để quen yêu cầu của kỳ thi.','#resources']],
        'tip':'Điểm trong bài luyện nhỏ chỉ phản ánh bộ câu đó. Hãy dùng kết quả để chọn chỗ cần ôn, không tự quy đổi band.'},
 'C2': {'title':'Tinh chỉnh sắc thái và sự linh hoạt', 'intro':'Thử thách nằm ở độ chính xác, ngụ ý và văn phong, không chỉ ở từ hiếm.',
        'steps':[['Phân tích lựa chọn câu','So sánh cấu trúc nhấn mạnh, lược bỏ và cách tổ chức thông tin trong từng ngữ cảnh.','#learn/grammar'],['Đọc nhiều góc nhìn','Đọc bài nâng cao, chỉ ra giả định của tác giả và tự diễn đạt lại lập luận.','#catalog'],['Kiểm chứng cách dùng','Đối chiếu từ điển học thuật, ví dụ và collocation; lưu những cách dùng mới thay vì gom từ đơn.','#learn/dictionary']],
        'tip':'Bạn vẫn có thể ôn bài mức thấp hơn nếu gặp lỗi. Các mức ở đây giúp chọn nội dung, không xác nhận chứng chỉ CEFR.'},
}


def clean_profile(data):
    if not isinstance(data,dict) or data.get('level') not in LEVELS or data.get('goal') not in GOALS:
        raise InputError('Chọn trình độ A1–C2 và mục tiêu học.')
    if type(data.get('daily_minutes')) is not int or data['daily_minutes'] not in (15,30,45,60):
        raise InputError('Chọn thời gian học 15, 30, 45 hoặc 60 phút.')
    return {k:data[k] for k in ('level','goal','daily_minutes')}


def profile_for(user):
    p=LearningProfile.objects.filter(owner=user).first()
    return ({'level':p.level,'goal':p.goal,'daily_minutes':p.daily_minutes} if p else
            {'level':'A1','goal':'general','daily_minutes':15}) | {'configured':p is not None}


def progress_for(user):
    groups={}
    for a in FoundationAttempt.objects.filter(owner=user).only('kind','unit_id','result','created_at').order_by('-created_at','-id').iterator(chunk_size=500):
        key=f'{a.kind}/{a.unit_id}'
        if len(groups.setdefault(key,[]))<3:groups[key].append(a)
    result={}
    for key,rows in groups.items():
        weights=(.5,.3,.2)[:len(rows)]
        mastery=round(sum(a.result['percent']*w for a,w in zip(rows,weights))/sum(weights))
        delay=1 if mastery<60 else 3 if mastery<80 else 7
        due=rows[0].created_at+timedelta(days=delay)
        result[key]={'score':rows[0].result['score'],'total':rows[0].result['total'],
            'percent':rows[0].result['percent'],'mastery':mastery,'attempts_used':len(rows),
            'review_at':due.isoformat(),'due':due<=timezone.now(),'last_at':rows[0].created_at.isoformat()}
    return result


def plan_for(user):
    profile=profile_for(user); progress=progress_for(user); now=timezone.now()
    level=profile['level']; index=LEVELS.index(level); goal=profile['goal']; budget=profile['daily_minutes']
    tasks=[]; used=0
    def add(kind,title,href,minutes,reason):
        nonlocal used
        if used+minutes<=budget and not any(t['href']==href for t in tasks):
            tasks.append(dict(kind=kind,title=title,href=href,minutes=minutes,reason=reason));used+=minutes
    due=Vocabulary.objects.filter(owner=user,due_at__lte=now).count()
    if due:add('review',f'Ôn từ đến hạn ({due} thẻ)','#study',5,'Gặp lại từ cũ trước khi thêm từ mới; bạn có thể dừng sau 5 phút.')
    grammar=units('grammar'); vocab=units('vocabulary'); candidates=[]
    for order,row in enumerate(grammar):
        p=progress.get('grammar/'+row['id']); distance=index-LEVELS.index(row['level'])
        if distance<0 or (distance>0 and not p):continue
        # Only prerequisites at the selected level gate new lessons. A C1 learner need not redo A1.
        deps=[d for d in row.get('prerequisites',[]) if any(x['id']==d and x['level']==level for x in grammar)]
        blocked=any(progress.get('grammar/'+d,{}).get('mastery',0)<60 for d in deps)
        if not p and blocked:continue
        if p and p['mastery']>=80 and not p['due']:continue
        priority=(100-p['mastery']+ (40 if p['due'] else 0)) if p else 35
        priority += 12 if goal in row.get('tags',[]) else 0
        reason=(f'Kết quả gần đây {p["mastery"]}%; '+('đã đến lúc ôn lại.' if p['due'] else 'ôn lại để nắm chắc hơn.')) if p else 'Bài mới vừa trình độ, sau những phần nền tảng bạn đã học.'
        candidates.append((-priority,order,row,reason))
    candidates.sort(key=lambda item:(item[0],item[1]))
    if candidates:
        _,_,row,reason=candidates[0];add('grammar',row['title'],'#grammar/'+row['id'],min(10,row.get('minutes',8)),reason)
    completed=set(Reading.objects.filter(owner=user,progress__completed=True).values_list('catalog_slug',flat=True))
    reading_results={}
    for attempt in LessonAttempt.objects.filter(reading__owner=user).order_by('-created_at','-id').values('reading__catalog_slug','result').iterator(chunk_size=500):
        reading_results.setdefault(attempt['reading__catalog_slug'],attempt['result'])
    levels=['pre-A1','A1'] if level=='A1' else [level]
    readings=CuratedLesson.objects.filter(published=True,level__in=levels).order_by('order','title')
    if goal=='ielts' and index>=2:readings=readings.filter(track='ielts')
    else:readings=readings.filter(track='general')
    def weak_reading(row):
        result=reading_results.get(row.slug)
        return bool(result and result.get('total') and result['score']/result['total']<.8)
    readings=sorted(readings,key=lambda r:(not weak_reading(r),r.slug in completed,r.order))
    row=next((r for r in readings if r.slug not in completed or weak_reading(r)),None)
    if row and not (goal=='toeic' and index>=1):
        minutes=max(8,min(15,round(len(row.content.get('text','').split())/100+len(row.content.get('questions',[]))*.7)))
        reason='Lần làm gần nhất còn chỗ chưa chắc; đọc lại và tìm bằng chứng cho các câu sai.' if weak_reading(row) else 'Đọc theo mức bạn chọn; dành thời gian này để đọc và kiểm tra bằng chứng, có thể tiếp tục ở buổi sau.'
        add('reading',row.title,'#lesson/'+row.slug,minutes,reason)
    if goal=='toeic' and index>=1:
        results={}
        for attempt in ToeicAttempt.objects.filter(owner=user).order_by('-created_at','-id').values('set_slug','result').iterator(chunk_size=500):results.setdefault(attempt['set_slug'],attempt['result'])
        def priority(row):
            result=results.get(row.slug)
            ratio=result.get('score',0)/max(1,result.get('total',1)) if result else None
            return (0 if ratio is not None and ratio<.8 else 1 if ratio is None else 2,
                    5 not in row.content.get('parts',[]),row.title)
        choices=list(ToeicPractice.objects.filter(published=True).order_by('title'))
        choices.sort(key=priority)
        if choices:
            row=choices[0];result=results.get(row.slug)
            reason=(f'Lần gần nhất: {result["score"]}/{result["total"]}. Luyện lại và xem kỹ lời giải.' if result else
                    'Dành 15 phút luyện TOEIC theo mục tiêu. Có thể tiếp tục phần còn lại ở buổi sau.')
            add('toeic',row.title,'#toeic-set/'+row.slug,15,reason)
    available=[r for r in vocab if r['level']==level]
    available.sort(key=lambda r:(progress.get('vocabulary/'+r['id'],{}).get('mastery',-1),goal not in r.get('tags',[])))
    if available:
        row=available[0];add('vocabulary',row['title'],'#collection/'+row['id'],5,'Học 5 từ trong câu ví dụ, rồi lưu từ bạn muốn ôn tiếp.')
    if not tasks:add('guide','Chọn một bài muốn tìm hiểu','#learn/grammar',8,'Bạn đã làm tốt các phần được gợi ý. Có thể thử chủ đề mới hoặc quay lại ôn.')
    done=[p for k,p in progress.items() if any(k=='grammar/'+r['id'] and r['level']==level for r in grammar)]
    advance=len(done)>=3 and all(p['mastery']>=80 for p in done) and index<5
    return {'profile':profile,'guidance':START[level],'tasks':tasks,'planned_minutes':used or 8,'progress':progress,
        'next_level':LEVELS[index+1] if advance else None,
        'method':'Ưu tiên từ đến hạn, bài ngữ pháp còn yếu, rồi bài mới vừa trình độ và mục tiêu. Kết quả ba lượt gần nhất có trọng số 50%, 30%, 20% (chuẩn hóa khi chưa đủ ba lượt). Ôn lại sau 1, 3 hoặc 7 ngày theo kết quả. Thời lượng là gợi ý; không tự nâng trình độ hay quy đổi điểm thành CEFR/band.'}
