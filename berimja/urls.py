from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('api/', include('apps.places.urls', namespace='places')),
    path('api/', include('apps.questions.urls', namespace='questions')),
    path('api/', include('apps.reviews.urls', namespace='reviews')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)