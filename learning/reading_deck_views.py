from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import JsonResponse

from .models import Reading
from .services.reading_decks import create_deck, deck_payload
from .views import api


@api('GET', 'POST')
def reading_deck(request, pk):
    if request.method == 'POST':
        # Same lock order as review/import: retries preserve saved senses and their schedules.
        with transaction.atomic():
            get_user_model().objects.select_for_update().get(pk=request.user.pk)
            reading = Reading.objects.select_for_update().get(owner=request.user, pk=pk)
            data = create_deck(request.user, reading)
    else:
        reading = Reading.objects.get(owner=request.user, pk=pk)
        data = deck_payload(request.user, reading)
    response = JsonResponse(data)
    response['Cache-Control'] = 'private, no-store'
    return response
