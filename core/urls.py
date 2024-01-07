from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from Transformer.views import index

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('api/', include('Transformer.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#
# urlpatterns += [
#     path('', lambda request: JsonResponse({'status': 'ok'}), name='health_check')
# ]