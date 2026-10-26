"""HTTPS delivery for hosts that block SMTP. Never logs credentials or message bodies."""
import httpx
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages or []:
            try:
                if not settings.RESEND_API_KEY:
                    raise RuntimeError('Email delivery is not configured.')
                with httpx.Client(timeout=10, follow_redirects=False) as client:
                    response = client.post('https://api.resend.com/emails',
                        headers={'Authorization': 'Bearer ' + settings.RESEND_API_KEY},
                        json={'from': message.from_email, 'to': message.to,
                              'subject': message.subject, 'text': message.body})
                    response.raise_for_status()
                sent += 1
            except (httpx.HTTPError, RuntimeError):
                if not self.fail_silently:
                    raise RuntimeError('Email delivery failed. Check sender configuration.') from None
        return sent
