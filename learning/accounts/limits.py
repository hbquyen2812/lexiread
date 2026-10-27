"""Database-backed limits shared by workers. Caller must hold a transaction."""
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import salted_hmac
from learning.models import AuthRateLimit


def lock_identities():
    """Serialize public account creation and identity edits, including case-insensitive checks."""
    key=salted_hmac('lexiread.auth.identity','public-accounts',algorithm='sha256').hexdigest()
    AuthRateLimit.objects.get_or_create(key=key)
    row=AuthRateLimit.objects.select_for_update().get(pk=key)
    row.last_at=timezone.now()
    row.save(update_fields=['last_at'])
    return row


def consume(action, ip_key, email=''):
    now = timezone.now()
    rules = [(f'{action}:global', timedelta(days=1), settings.AUTH_DAILY_LIMIT, 0),
             (f'{action}:ip:{ip_key}', timedelta(hours=1), 10, 0)]
    if email:
        rules.append((f'{action}:email:{email.strip().lower()}', timedelta(hours=1), 3, 60))
    rows = []
    # Always take the global lock first; signup keeps it until user creation commits.
    for raw, window, maximum, cooldown in rules:
        key = salted_hmac('lexiread.auth.limit', raw, algorithm='sha256').hexdigest()
        AuthRateLimit.objects.get_or_create(key=key)
        row = AuthRateLimit.objects.select_for_update().get(pk=key)
        if now - row.started_at >= window:
            row.started_at, row.count = now, 0
        if row.count >= maximum or (cooldown > 0 and row.count and (now - row.last_at).total_seconds() < cooldown):
            return False
        rows.append(row)
    for row in rows:
        row.count += 1
        row.last_at = now
        row.save(update_fields=['started_at', 'last_at', 'count'])
    return True
