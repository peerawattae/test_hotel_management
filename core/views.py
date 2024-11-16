from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Room

def check_room_availability(request, room_id):
    check_in_date = request.GET.get('check_in_date')
    check_out_date = request.GET.get('check_out_date')

    # Validate input
    if not check_in_date or not check_out_date:
        return JsonResponse({'error': 'Please provide both check_in_date and check_out_date'}, status=400)

    room = get_object_or_404(Room, id=room_id)

    # Check availability
    if room.is_available(check_in_date, check_out_date):
        return JsonResponse({'available': True})
    else:
        return JsonResponse({'available': False})
