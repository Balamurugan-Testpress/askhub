from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.
#


@login_required
def home(request):
    return HttpResponse(f"Welcome home {request.user}")
