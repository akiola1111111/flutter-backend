from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def get_csrf_token(request):
    return JsonResponse({'csrfToken': 'csrf-exempt-for-development'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/products/', include('products.urls')),
    path('api/', include('disease_reports.urls')),
    path('api/csrf-token/', get_csrf_token, name='csrf-token'),
    path('api/weather/', include('weather.urls')),
    path('api/expert-news/', include('expert_news.urls')),  # New expert news
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)