from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title='OPPA PRO',
        default_version='v1',
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    authentication_classes=[TokenAuthentication,],
    permission_classes=[permissions.AllowAny,],
)


urlpatterns = [
    # path('jet/', include('jet.urls', 'jet')),
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('', include('product.urls')),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('users/', include('user.urls')),
    path('car/', include('car.urls')),
    path('business/', include('business.urls')),
    path('info/', include('info.urls')),

    path('service/', include('business.service_urls')),
    path('purchase_request/', include('purchase_request.urls')),
    path('chat/', include('chat.urls')),


]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
