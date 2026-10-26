"""Local mail only; no external credentials, messages or production database."""
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from unittest.mock import patch
import httpx
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.db import transaction, connection, connections
from django.test import TestCase, TransactionTestCase, Client, override_settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from learning.models import AuthRateLimit, Vocabulary, Reading
from learning.accounts.limits import consume
from learning.services.storage import save_entry, export_library, import_library


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',EMAIL_RECOVERY_ENABLED=True)
class AccountTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user('alice','alice@example.test','Old-strong-pass-2026!')

    def signup_data(self,**changes):
        return {'username':'new-reader','email':'new@example.test','password1':'Strong-reader-2026!',
                'password2':'Strong-reader-2026!',**changes}

    def profile_data(self,**changes):
        return {'username':self.user.username,'email':self.user.email,'first_name':'Lan','last_name':'Nguyễn',**changes}

    def reset_link(self):
        return f'/reset/{urlsafe_base64_encode(force_bytes(self.user.pk))}/{default_token_generator.make_token(self.user)}/'

    def test_signup_logs_in_without_granting_staff_and_hides_password(self):
        response=self.client.post('/signup/',self.signup_data(is_staff=True,is_superuser=True))
        self.assertRedirects(response,'/')
        user=get_user_model().objects.get(username='new-reader')
        self.assertFalse(user.is_staff or user.is_superuser)
        self.assertTrue(user.check_password('Strong-reader-2026!'))
        self.assertNotEqual(user.password,'Strong-reader-2026!')
        self.assertEqual(int(self.client.session['_auth_user_id']),user.pk)

    def test_signup_rejects_duplicate_email_username_and_weak_password(self):
        for changes,field in [({'email':'ALICE@example.test'},'email'),({'username':'ALICE'},'username'),
                              ({'username':'mail@example.com'},'username'),({'password1':'abc','password2':'abc'},'password2')]:
            response=self.client.post('/signup/',self.signup_data(**changes))
            self.assertEqual(response.status_code,200)
            self.assertIn(field,response.context['form'].errors)
        self.assertEqual(get_user_model().objects.count(),1)
        self.assertNotContains(response,'value="abc"')

    def test_signup_limit_is_persistent(self):
        for _ in range(10): self.client.post('/signup/',{})
        self.assertEqual(self.client.post('/signup/',self.signup_data()).status_code,429)
        self.assertEqual(get_user_model().objects.count(),1)

    def test_csrf_and_authentication_required(self):
        strict=Client(enforce_csrf_checks=True)
        for url in ['/signup/','/password-reset/']:
            self.assertEqual(strict.post(url,{}).status_code,403)
        self.assertEqual(self.client.get('/account/').status_code,302)
        self.assertEqual(self.client.get('/account/password/').status_code,302)
        strict.force_login(self.user)
        for url in ['/account/','/account/password/']:
            self.assertEqual(strict.post(url,{}).status_code,403)

    def test_profile_only_updates_allowed_fields_and_keeps_learning_data(self):
        self.client.force_login(self.user)
        reading=Reading.objects.create(owner=self.user,title='My lesson',text='A short passage.')
        response=self.client.post('/account/',self.profile_data(is_staff=True,password='evil',id='999'))
        self.assertRedirects(response,'/account/')
        self.user.refresh_from_db();reading.refresh_from_db()
        self.assertEqual(self.user.first_name,'Lan')
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.check_password('Old-strong-pass-2026!'))
        self.assertEqual(reading.owner_id,self.user.pk)

    def test_identity_change_requires_current_password_and_rejects_duplicates(self):
        self.client.force_login(self.user)
        response=self.client.post('/account/',self.profile_data(email='new@example.test'))
        self.assertIn('current_password',response.context['form'].errors)
        self.user.refresh_from_db();self.assertEqual(self.user.email,'alice@example.test')
        get_user_model().objects.create_user('other','other@example.test','irrelevant')
        response=self.client.post('/account/',self.profile_data(email='OTHER@example.test',current_password='Old-strong-pass-2026!'))
        self.assertIn('email',response.context['form'].errors)
        response=self.client.post('/account/',self.profile_data(username='alice-new',email='new@example.test',current_password='Old-strong-pass-2026!'))
        self.assertEqual(response.status_code,302)
        self.user.refresh_from_db();self.assertEqual(self.user.username,'alice-new')
        self.client.logout()
        self.assertEqual(self.client.post('/login/',{'username':'alice-new','password':'Old-strong-pass-2026!'}).status_code,302)

    def test_password_change_requires_old_password_and_invalidates_other_sessions(self):
        second=Client();second.force_login(self.user);self.client.force_login(self.user)
        data={'old_password':'wrong','new_password1':'New-strong-pass-2026!','new_password2':'New-strong-pass-2026!'}
        response=self.client.post('/account/password/',data)
        self.assertIn('old_password',response.context['form'].errors)
        data['old_password']='Old-strong-pass-2026!'
        response=self.client.post('/account/password/',data)
        self.assertRedirects(response,'/account/password/done/')
        self.assertEqual(self.client.get('/api/bootstrap/').status_code,200)
        self.assertEqual(second.get('/api/bootstrap/').status_code,401)
        self.user.refresh_from_db();self.assertTrue(self.user.check_password(data['new_password1']))

    def test_recovery_sends_single_link_no_password_and_reset_is_one_time(self):
        response=self.client.post('/password-reset/',{'email':'ALICE@example.test'})
        self.assertRedirects(response,'/password-reset/sent/')
        self.assertEqual(len(mail.outbox),1)
        self.assertNotIn('Old-strong-pass',mail.outbox[0].body)
        path=re.search(r'http://testserver(/reset/\S+)',mail.outbox[0].body).group(1)
        confirm=self.client.get(path)
        self.assertEqual(confirm.status_code,302)
        self.assertIn('/set-password/',confirm.url)
        response=self.client.post(confirm.url,{'new_password1':'Reset-strong-2026!','new_password2':'Reset-strong-2026!'})
        self.assertRedirects(response,'/reset/complete/')
        self.user.refresh_from_db();self.assertTrue(self.user.check_password('Reset-strong-2026!'))
        self.assertFalse(Client().get(path).context['validlink'])

    @override_settings(PUBLIC_SITE_URL='https://lexiread-a3h8.onrender.com')
    def test_recovery_uses_canonical_site_not_request_host(self):
        self.client.post('/password-reset/',{'email':self.user.email})
        self.assertIn('https://lexiread-a3h8.onrender.com/reset/',mail.outbox[0].body)
        self.assertNotIn('testserver',mail.outbox[0].body)

    def test_unknown_inactive_duplicate_and_unusable_email_have_same_outcome(self):
        inactive=get_user_model().objects.create_user('inactive','inactive@example.test','password',is_active=False)
        get_user_model().objects.create_user('duplicate','ALICE@example.test','password')
        get_user_model().objects.create_user('unusable','unusable@example.test',None)
        for email in ['missing@example.test',inactive.email,'alice@example.test','unusable@example.test']:
            response=self.client.post('/password-reset/',{'email':email})
            self.assertEqual(response.url,'/password-reset/sent/')
        self.assertEqual(len(mail.outbox),0)

    def test_recovery_cooldown_and_provider_failure_do_not_leak(self):
        self.client.post('/password-reset/',{'email':self.user.email})
        self.client.post('/password-reset/',{'email':self.user.email.upper()})
        self.assertEqual(len(mail.outbox),1)
        AuthRateLimit.objects.all().update(last_at=timezone.now()-timedelta(minutes=2))
        with patch('learning.accounts.forms.RecoveryForm.save',side_effect=RuntimeError('secret-provider-info')):
            with self.assertLogs('learning.accounts.views',level='WARNING') as logs:
                response=self.client.post('/password-reset/',{'email':self.user.email})
        self.assertEqual(response.url,'/password-reset/sent/')
        self.assertNotIn('secret-provider-info',str(logs.output))

    @override_settings(EMAIL_RECOVERY_ENABLED=False)
    def test_missing_mail_configuration_is_explained_without_sending(self):
        response=self.client.get('/password-reset/')
        self.assertContains(response,'chưa được mở')
        self.assertEqual(self.client.post('/password-reset/',{'email':self.user.email}).status_code,200)
        self.assertEqual(len(mail.outbox),0)

    def test_reset_expiry_tampering_and_email_change_invalidate_links(self):
        path=self.reset_link()
        self.assertFalse(self.client.get(path+'invalid').status_code==302)
        self.user.email='changed@example.test';self.user.save(update_fields=['email'])
        self.assertFalse(self.client.get(path).context['validlink'])
        path=self.reset_link()
        with patch('django.contrib.auth.tokens.PasswordResetTokenGenerator._now',return_value=default_token_generator._now()+timedelta(hours=2)):
            self.assertFalse(self.client.get(path).context['validlink'])

    @override_settings(AUTH_DAILY_LIMIT=2)
    def test_global_budget_and_window_reset(self):
        with transaction.atomic():
            self.assertTrue(consume('test','first','a@example.test'))
            self.assertTrue(consume('test','second','b@example.test'))
            self.assertFalse(consume('test','third','c@example.test'))
        AuthRateLimit.objects.update(started_at=timezone.now()-timedelta(days=2),last_at=timezone.now()-timedelta(days=2))
        with transaction.atomic(): self.assertTrue(consume('test','third','c@example.test'))

    @override_settings(EMAIL_BACKEND='learning.accounts.mail.ResendEmailBackend',RESEND_API_KEY='test-key-not-real')
    def test_https_email_adapter_payload_and_failure_redaction(self):
        with patch('learning.accounts.mail.httpx.Client') as client:
            message=mail.EmailMessage('Reset','short body',to=['reader@example.test'])
            self.assertEqual(message.send(),1)
            args=client.return_value.__enter__.return_value.post.call_args
            self.assertEqual(args.args[0],'https://api.resend.com/emails')
            self.assertEqual(args.kwargs['json']['text'],'short body')
            self.assertEqual(args.kwargs['headers']['Authorization'],'Bearer test-key-not-real')
            client.return_value.__enter__.return_value.post.side_effect=httpx.ConnectError('secret-key')
            with self.assertRaisesRegex(RuntimeError,'Email delivery failed') as error: message.send()
            self.assertNotIn('secret-key',str(error.exception))

    def test_word_usage_pattern_survives_api_backup_csv_and_legacy_import(self):
        entry={'word':'depend','meaning_vi':'phụ thuộc','usage_pattern':'depend on + noun',
               'example':'We depend on clean water.','paraphrases':['need someone or something']}
        word,_=save_entry(self.user,entry)
        other=get_user_model().objects.create_user('backup-reader')
        import_library(other,export_library(self.user))
        self.assertEqual(Vocabulary.objects.get(owner=other).usage_pattern,entry['usage_pattern'])
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/api/vocabulary/').json()['items'][0]['usage_pattern'],entry['usage_pattern'])
        self.assertContains(self.client.get('/api/export.csv'),'depend on + noun')
        legacy,_=save_entry(self.user,{'word':'water','meaning_vi':'nước'})
        self.assertEqual(legacy.usage_pattern,'')


@override_settings(AUTH_DAILY_LIMIT=2)
class AuthConcurrencyTests(TransactionTestCase):
    def test_parallel_requests_cannot_overspend_global_budget(self):
        if connection.vendor!='postgresql':
            self.skipTest('Requires real PostgreSQL row locks.')
        def attempt(index):
            try:
                with transaction.atomic(): return consume('parallel',f'ip-{index}',f'{index}@example.test')
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=4) as workers:
            results=list(workers.map(attempt,range(4)))
        self.assertEqual(sum(results),2)
