"""Small first-party analytics layer without raw IP addresses or third-party scripts."""
import hashlib
import uuid
from datetime import timedelta
from django.conf import settings
from django.db import transaction,IntegrityError
from django.db.models import Count,Sum
from django.utils import timezone
from ..models import DailyVisit
from .core import InputError

PAGES={'home','catalog','lesson','toeic','toeic-set','readings','reading','vocabulary','study','settings','analytics','login'}

def record_visit(request,page):
    if page not in PAGES:raise InputError('Trang thống kê không hợp lệ.')
    visitor_id=request.session.get('analytics_visitor_id')
    if not visitor_id:
        visitor_id=str(uuid.uuid4());request.session['analytics_visitor_id']=visitor_id
    visitor_key=hashlib.sha256((settings.SECRET_KEY+'\x1f'+visitor_id).encode()).hexdigest()
    today=timezone.localdate();owner=request.user if request.user.is_authenticated else None
    try:
        with transaction.atomic():
            row=_write_visit(today,visitor_key,owner,page)
    except IntegrityError:
        # Two tabs can create the same daily row concurrently; retry after the winner commits.
        with transaction.atomic():
            row=_write_visit(today,visitor_key,owner,page,create=False)
    return row

def _write_visit(today,visitor_key,owner,page,create=True):
    row=DailyVisit.objects.select_for_update().filter(date=today,visitor_key=visitor_key).first()
    if row:
        pages=dict(row.page_counts or {});pages[page]=int(pages.get(page,0))+1
        row.views+=1;row.page_counts=pages
        if owner and row.owner_id!=owner.pk:row.owner=owner
        row.save(update_fields=['views','page_counts','owner','last_seen'])
    elif create:
        row=DailyVisit.objects.create(date=today,visitor_key=visitor_key,owner=owner,views=1,page_counts={page:1})
    else:
        raise IntegrityError('Không thể hợp nhất lượt truy cập đồng thời.')
    return row

def personal_activity(user):
    today=timezone.localdate();start=today-timedelta(days=29)
    rows=DailyVisit.objects.filter(owner=user,date__gte=start)
    return {'active_days_30':rows.values('date').distinct().count(),
        'page_views_today':rows.filter(date=today).aggregate(total=Sum('views'))['total'] or 0}

def traffic_summary(days):
    if days not in {7,30,90}:raise InputError('Chỉ hỗ trợ thống kê 7, 30 hoặc 90 ngày.')
    today=timezone.localdate();start=today-timedelta(days=days-1);rows=DailyVisit.objects.filter(date__gte=start)
    raw={item['date']:{'date':item['date'].isoformat(),'visitors':item['visitors'],'views':item['views'] or 0,
        'active_users':item['active_users']} for item in rows.values('date').annotate(visitors=Count('id'),
        views=Sum('views'),active_users=Count('owner',distinct=True)).order_by('date')}
    series=[]
    for offset in range(days):
        date=start+timedelta(days=offset)
        series.append(raw.get(date,{'date':date.isoformat(),'visitors':0,'views':0,'active_users':0}))
    page_counts={}
    for value in rows.values_list('page_counts',flat=True):
        for page,count in (value or {}).items():page_counts[page]=page_counts.get(page,0)+int(count)
    totals=rows.aggregate(views=Sum('views'),active_users=Count('owner',distinct=True))
    return {'days':days,'series':series,'totals':{'views':totals['views'] or 0,
        'visitors':rows.values('visitor_key').distinct().count(),'active_users':totals['active_users'] or 0},
        'top_pages':[{'page':page,'views':count} for page,count in sorted(page_counts.items(),key=lambda item:(-item[1],item[0]))[:10]],
        'privacy_note':'Không lưu địa chỉ IP. Khách duy nhất được ước lượng bằng mã phiên ngẫu nhiên đã băm theo từng ngày.'}
