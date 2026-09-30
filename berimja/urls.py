from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # اندپوینت‌های اصلی پروژه
    path('api/accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('api/', include('apps.places.urls', namespace='places')),
    path('api/', include('apps.questions.urls', namespace='questions')),
    path('api/', include('apps.reviews.urls', namespace='reviews')),

    # مستندات تعاملی API (OpenAPI 3.0 & Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)