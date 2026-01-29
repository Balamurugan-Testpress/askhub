from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import zoneinfo
from django.utils import timezone
import pytz
from account.models import UserProfile

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        user = getattr(request, 'user', None)

        if not tzname and user and user.is_authenticated:
            try:
                tzname = user.userprofile.timezone
                request.session['django_timezone'] = tzname
            except UserProfile.DoesNotExist:
                tzname = None

        if tzname:
            try:
                timezone.activate(ZoneInfo(tzname))
            except ZoneInfoNotFoundError:
                timezone.deactivate()
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response

