from zoneinfo import available_timezones
from django.utils import timezone

def timezone_context(request):
    return {
        'timezones': sorted(available_timezones()),
        'current_timezone': request.session.get('django_timezone', timezone.get_current_timezone_name())
    }


