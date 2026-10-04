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

    # ۱. صفحات وبسایت (HTML Views برای فرانت و سئو)
    path('', include(('apps.places.urls_web', 'places_web'), namespace='places_web')),

    # ۲. اندپوینت‌های REST API (خروجی JSON با پیشوند api/)
    path('api/accounts/', include('apps.accounts.urls', namespace='accounts_api')),
    path('api/places/', include('apps.places.urls', namespace='places_api')),
    path('api/questions/', include('apps.questions.urls', namespace='questions_api')),
    path('api/reviews/', include('apps.reviews.urls', namespace='reviews_api')),

    # ۳. مستندات خودکار OpenAPI / Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)