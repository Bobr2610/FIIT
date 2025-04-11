"""
Конфигурация URL для проекта FIIT.

Список `urlpatterns` маршрутизирует URL-адреса к представлениям (views).
Подробная документация доступна по адресу:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/

Примеры конфигурации URL:

Функциональные представления:
    1. Импорт:  from my_app import views
    2. Добавление в urlpatterns:  path('', views.home, name='home')

Классовые представления:
    1. Импорт:  from other_app.views import Home
    2. Добавление в urlpatterns:  path('', Home.as_view(), name='home')

Включение другого URLconf:
    1. Импорт функции include:  from django.urls import include, path
    2. Добавление в urlpatterns:  path('blog/', include('blog.urls'))

Основные URL-маршруты проекта:
- /admin/ - административная панель Django
- / - основное приложение (app.urls)
- /api-auth/ - аутентификация REST framework
- /swagger/, /redoc/ - API документация
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="FIIT API",
        default_version='v1',
        description="API documentation for FIIT project",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('app.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
    # URL-адреса для документации Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
