from django.core.management.base import BaseCommand, CommandError
from learning.services.offline_dictionary import import_release, seed_collections, import_recordings


class Command(BaseCommand):
    help = 'Import the bundled OEWN dictionary and topic vocabulary into the database; no network or AI.'

    def handle(self, *args, **options):
        try:
            release, changed = import_release()
            created = seed_collections()
            audio = import_recordings()
        except (OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(
            f'{"Imported" if changed else "Already loaded"}: {release.entry_count} dictionary entries, '
            f'{release.ipa_count} with IPA; {created} new vocabulary collections; {audio} recordings imported.'))
