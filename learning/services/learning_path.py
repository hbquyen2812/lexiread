"""Explainable recommendations from owned progress, never an AI request."""
from datetime import timedelta
from django.utils import timezone
from ..models import LearningProfile, FoundationAttempt, Vocabulary, Reading, CuratedLesson, ToeicPractice, ToeicAttempt, LessonAttempt
from .core import InputError
from .foundation_content import LEVELS, GOALS, units, unit_summaries

START = {
 'A1': {'title':'Làm quen với tiếng Anh hằng ngày', 'intro':'Bắt đầu với câu ngắn và từ vựng quen thuộc. Mỗi buổi học một ít rồi ôn lại.',
        'steps':[['Học ngữ pháp cơ bản','Làm quen với động từ be, đại từ và câu đơn. Đọc ví dụ, thử đặt câu về bản thân rồi làm bài tập.','#learn/grammar'],['Học từ thông dụng','Chọn một bộ từ về sinh hoạt hằng ngày. Học 5 từ cùng câu ví dụ và lưu những từ cần ôn.','#learn/vocabulary'],['Đọc bài ngắn','Chọn bài pre-A1 hoặc A1. Tự đọc trước, xem bản dịch khi cần và ôn lại từ mới vào buổi sau.','#catalog']],
        'tip':'Ưu tiên câu ngắn và từ thông dụng. Khi đã quen, bạn có thể thử bài đọc dài hơn.'},
 'A2': {'title':'Kể về những việc quen thuộc', 'intro':'Dùng từ vựng và ngữ pháp đã học để kể về một ngày, một chuyến đi hoặc dự định của bạn.',
        'steps':[['Ôn ngữ pháp thường dùng','Ôn thì quá khứ, cách nói về tương lai và câu so sánh. Sau mỗi bài, viết hai câu về bản thân.','#learn/grammar'],['Đọc để hiểu ý chính','Chọn bài A2. Đọc để nắm ý chính trước, rồi tra những từ khiến bạn chưa hiểu câu.','#catalog'],['Ôn từ cùng câu ví dụ','Lưu cả cụm từ và câu ví dụ. Ôn từ theo lịch trước khi học thêm từ mới.','#study']],
        'tip':'Nếu học TOEIC, bạn có thể bắt đầu với Part 5 và email ngắn ở Part 7. Hãy hiểu cách làm trước khi luyện có bấm giờ.'},
 'B1': {'title':'Hiểu bài đọc và giải thích được đáp án', 'intro':'Thử bài đọc dài hơn và luyện các dạng bài phù hợp với mục tiêu của bạn.',
        'steps':[['Ôn phần còn hay nhầm','Xem lại câu điều kiện, câu bị động và mệnh đề quan hệ. Với mỗi lỗi, viết một câu đúng để ghi nhớ cách dùng.','#learn/grammar'],['Học cách làm từng dạng bài','IELTS: bắt đầu với True / False / Not Given. TOEIC: luyện Part 5–6, sau đó thử đọc email ở Part 7.','#guides'],['Tóm tắt sau khi đọc','Chọn bài B1. Sau khi kiểm tra đáp án, tóm tắt nội dung bằng 2–3 câu và lưu các cụm từ hữu ích.','#catalog']],
        'tip':'Sau mỗi bài, xem lại câu chưa đúng và tìm chi tiết trong bài giúp bạn chọn đáp án.'},
 'B2': {'title':'Đọc kỹ và làm bài chính xác hơn', 'intro':'Chú ý cách tác giả liên kết các ý, diễn đạt cùng một ý bằng từ khác và thể hiện quan điểm.',
        'steps':[['Củng cố ngữ pháp','Ôn câu điều kiện, động từ khuyết thiếu và cách nối ý. Làm lại những dạng bài bạn còn hay nhầm.','#learn/grammar'],['Luyện theo mục tiêu','IELTS: nhận ra cách diễn đạt tương đương và ý chính từng đoạn. TOEIC: kết hợp thông tin từ hai hoặc ba văn bản.','#guides'],['Học cách kết hợp từ','Học từ theo chủ đề và các từ thường đi cùng nhau (collocations). Thử dùng chúng khi tóm tắt bài hoặc viết email.','#learn/vocabulary']],
        'tip':'Khi đã nắm cách làm, hãy thử luyện có bấm giờ. Sau đó kiểm tra vì sao từng đáp án đúng hoặc sai.'},
 'C1': {'title':'Hiểu sắc thái, dùng từ chính xác', 'intro':'Tập nhận ra quan điểm, hàm ý và mức độ chắc chắn trong lời tác giả.',
        'steps':[['Luyện cấu trúc nâng cao','Học đảo ngữ, câu nhấn mạnh và cách diễn đạt mức độ chắc chắn. Viết lại câu rồi so sánh sự khác biệt.','#learn/grammar'],['Chọn từ phù hợp','Tra nghĩa trong ngữ cảnh, các từ thường đi cùng nhau và cách dùng trong văn nói hoặc văn viết.','#learn/dictionary'],['Làm quen với đề chính thức','Luyện bài đọc học thuật và xem đề mẫu chính thức để hiểu yêu cầu của kỳ thi.','#resources']],
        'tip':'Dùng kết quả từng bài để chọn nội dung cần ôn. Điểm luyện tập trên website không quy đổi trực tiếp thành band IELTS.'},
 'C2': {'title':'Diễn đạt linh hoạt trong từng ngữ cảnh', 'intro':'Chú ý độ chính xác, hàm ý và văn phong khi đọc cũng như khi viết.',
        'steps':[['So sánh cách viết câu','Xem cách nhấn mạnh, lược bỏ từ và sắp xếp thông tin làm thay đổi ý nghĩa của câu.','#learn/grammar'],['Phân tích lập luận','Đọc bài nâng cao, tìm những giả định của tác giả và trình bày lại lập luận bằng lời của bạn.','#catalog'],['Tra kỹ cách dùng từ','Đối chiếu định nghĩa, ví dụ và các từ thường đi cùng nhau. Lưu cách dùng mới cùng câu ví dụ.','#learn/dictionary']],
        'tip':'Bạn có thể quay lại bài ở trình độ thấp hơn để ôn những cấu trúc ít dùng hoặc còn hay nhầm.'},
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
    if due:add('review',f'Ôn từ vựng ({due} từ)','#study',5,'Dành 5 phút ôn từ cũ trước khi học thêm từ mới.')
    grammar=units('grammar'); vocab=unit_summaries('vocabulary'); candidates=[]
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
        reason=('Đã đến lúc ôn lại bài này. Làm lại bài tập để kiểm tra những gì bạn còn nhớ.' if p['due'] else 'Luyện lại bài này và xem lời giải ở những câu chưa đúng.') if p else f'Bài ngữ pháp phù hợp với trình độ {level} bạn đã chọn.'
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
        reason='Bài trước còn câu chưa đúng. Đọc lại và tìm chi tiết giúp bạn chọn đáp án.' if weak_reading(row) else 'Đọc bài, trả lời câu hỏi và xem lời giải. Bạn có thể học tiếp vào buổi sau nếu chưa xong.'
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
            reason=(f'Lần trước bạn trả lời đúng {result["score"]}/{result["total"]} câu. Làm lại và xem kỹ lời giải.' if result else
                    'Dành 15 phút luyện TOEIC. Nếu chưa làm xong, bạn có thể tiếp tục vào buổi sau.')
            add('toeic',row.title,'#toeic-set/'+row.slug,15,reason)
    available=[r for r in vocab if r['level']==level]
    available.sort(key=lambda r:(progress.get('vocabulary/'+r['id'],{}).get('mastery',-1),goal not in r.get('tags',[])))
    if available:
        row=available[0];add('vocabulary',row['title'],'#collection/'+row['id'],5,'Học 5 từ cùng câu ví dụ, rồi lưu những từ bạn cần ôn.')
    if not tasks:add('guide','Chọn bài học tiếp theo','#learn/grammar',8,'Khám phá chủ đề mới hoặc chọn một bài đã học để ôn lại.')
    done=[p for k,p in progress.items() if any(k=='grammar/'+r['id'] and r['level']==level for r in grammar)]
    advance=len(done)>=3 and all(p['mastery']>=80 for p in done) and index<5
    return {'profile':profile,'guidance':START[level],'tasks':tasks,'planned_minutes':used or 8,'progress':progress,
        'next_level':LEVELS[index+1] if advance else None,
        'method':'Lộ trình dựa trên trình độ, mục tiêu, thời gian học và kết quả gần đây của bạn. LexiRead ưu tiên từ cần ôn và bài cần luyện lại, sau đó gợi ý bài mới. Bạn có thể đổi trình độ và thời gian học bất cứ lúc nào.'}
