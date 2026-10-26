"""Read-only readiness check. Does not contact the mail provider or the database."""
from email.utils import parseaddr
from urllib.parse import urlparse
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help='Check mail configuration without printing secrets or sending email.'
    requires_system_checks=[]

    def handle(self,*args,**options):
        backend=settings.EMAIL_BACKEND
        if backend!='learning.accounts.mail.ResendEmailBackend':
            self.stdout.write('LOCAL/TEST mail backend: no real email delivery verified.')
            return
        missing=[]
        if not getattr(settings,'RESEND_API_KEY','').strip(): missing.append('RESEND_API_KEY')
        sender=parseaddr(settings.DEFAULT_FROM_EMAIL)[1]
        try:
            validate_email(sender)
            if sender.lower().endswith(('@example.com','@example.test','@resend.dev')):
                missing.append('DEFAULT_FROM_EMAIL (use your verified sender domain)')
        except ValidationError:
            missing.append('DEFAULT_FROM_EMAIL')
        origin=getattr(settings,'PUBLIC_SITE_URL','')
        if not origin or urlparse(origin).scheme!='https': missing.append('PUBLIC_SITE_URL (HTTPS)')
        if missing: raise CommandError('Missing/invalid configuration: '+', '.join(missing)+'. No email was sent.')
        self.stdout.write(self.style.SUCCESS('Required values are present. No secrets printed and no email sent.'))
        self.stdout.write('Sender-domain verification, provider key validity and inbox delivery still require a real test using your own email.')
