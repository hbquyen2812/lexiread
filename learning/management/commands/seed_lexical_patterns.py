from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.db import transaction
from learning.models import LexicalReference, VocabularyCollection
from learning.services.lexical_patterns import lessons, manifest, reference_rows


class Command(BaseCommand):
    help = 'Validate and add collocations, word-family lessons and licensed lexical references.'

    def add_arguments(self, parser):
        parser.add_argument('--check', action='store_true')

    def handle(self, *args, **options):
        try:
            units = lessons()
            rows = list(reference_rows())
            if len({r['key'] for r in rows}) != len(rows):
                raise ValueError('Duplicate lexical reference key')
            if len(rows) != sum(manifest()['counts'].values()):
                raise ValueError('Lexical reference count mismatch')
        except (ValueError, KeyError, OSError) as exc:
            raise CommandError(str(exc)) from exc
        if options['check']:
            self.stdout.write(f'Validated {len(units)} lessons and {len(rows)} reference pairs.')
            return
        # Additive: do not replace edited lessons, personal vocabulary or review schedules.
        with transaction.atomic():
            added = 0
            for i, row in enumerate(units):
                _, made = VocabularyCollection.objects.get_or_create(slug=row['id'], defaults=dict(
                    title=row['title'], topic=row['topic'], level=row['level'], order=2000+i, content=row))
                added += made
            existing = set(LexicalReference.objects.filter(key__in=[r['key'] for r in rows]).values_list('key', flat=True))
            pending = [LexicalReference(**row) for row in rows if row['key'] not in existing]
            LexicalReference.objects.bulk_create(pending, ignore_conflicts=True, batch_size=500)
        cache.delete('lexiread:public-vocabulary-summaries:v1')
        self.stdout.write(f'Added {added} lessons; {len(pending)} new reference pairs submitted. Accounts and progress preserved.')
