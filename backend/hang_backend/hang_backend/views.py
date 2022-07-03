# todolist/views.py

from django.http import JsonResponse
from django.middleware.csrf import get_token

# https://typeofnan.dev/using-cookie-based-csrf-tokens-for-your-single-page-application/
def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})
