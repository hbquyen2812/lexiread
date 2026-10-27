from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from learning.models import CuratedLesson, ToeicPractice, VocabularyCollection
from learning.services.content_release import load_release, converted_release


class Command(BaseCommand):
    help = 'Validate and add the bundled v3 readings and vocabulary. Never replaces existing content or progress.'

    def add_arguments(self, parser):
        parser.add_argument('--check', action='store_true', help='Validate without connecting to the database.')

    def handle(self, *args, **options):
        try:
            pack, manifest = load_release()
            rows = list(converted_release(pack, manifest))
        except (ValueError, KeyError, TypeError, OSError) as exc:
            raise CommandError(str(exc)) from exc
        if options['check']:
            self.stdout.write(self.style.SUCCESS(f'Validated {len(rows)} lessons and vocabulary collections.'))
            return
        made = {'lesson': 0, 'toeic': 0, 'vocabulary': 0}
        with transaction.atomic():
            for index, (kind, row, collection) in enumerate(rows):
                model = CuratedLesson if kind == 'lesson' else ToeicPractice
                fields = ('title', 'revision', 'level', 'track', 'topic', 'order') if kind == 'lesson' else ('title', 'revision')
                defaults = {key: row[key] for key in fields}
                defaults.update(content=row, published=True)
                _, created = model.objects.get_or_create(slug=row['slug'], defaults=defaults)
                made[kind] += created
                _, created = VocabularyCollection.objects.get_or_create(slug=collection['id'], defaults={
                    'title': collection['title'], 'topic': collection['topic'], 'level': collection['level'],
                    'order': 1000 + index, 'content': collection})
                made['vocabulary'] += created
        self.stdout.write(self.style.SUCCESS(f'V3 added: {made}. Existing content, accounts and progress preserved.'))
