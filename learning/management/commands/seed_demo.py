import json
from django.core.management.base import BaseCommand,CommandError
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from learning.models import Reading
from learning.services.storage import save_entry
class Command(BaseCommand):
    help='Load the supplied private Set in Metal reading and 116 study cards; never resets progress.'
    def add_arguments(self,parser):
        target=parser.add_mutually_exclusive_group(required=True)
        target.add_argument('--email')
        target.add_argument('--username')
    @transaction.atomic
    def handle(self,*args,**options):
        users=get_user_model().objects
        if options.get('email'):
            matches=list(users.filter(email__iexact=options['email'])[:2])
            if len(matches)>1:raise CommandError('Email belongs to multiple accounts. Make account emails unique first.')
            user=matches[0] if matches else None
        else:user=users.filter(username=options['username']).first()
        if not user:raise CommandError('Account not found. Run createsuperuser first.')
        root=settings.BASE_DIR/'data'
        text=(root/'set_in_metal.txt').read_text(encoding='utf-8')
        analysis=json.loads((root/'demo_analysis.json').read_text(encoding='utf-8'))
        r,new=Reading.objects.get_or_create(owner=user,title='Set in Metal',text=text,
           defaults={'source_name':'Bài đọc do người học cung cấp','analysis':analysis})
        words=json.loads((root/'seed_vocab.json').read_text(encoding='utf-8'))
        count=0
        for word in words:
            _,created=save_entry(user,word,r if word.get('context') and word.get('source_label')=='Set in Metal' else None)
            count+=int(created)
        self.stdout.write(self.style.SUCCESS(f'Added {count} cards. Existing cards and schedules preserved. Reading created: {new}.'))
