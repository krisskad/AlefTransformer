from django.urls import path, include
from rest_framework import routers
from .views import *
from django.conf.urls.static import static


router = routers.DefaultRouter()
router.register(r'home', HomeView, basename='home')
router.register(r'upload', UploadViewSet, basename='upload')
router.register(r'delete', DeleteFolderViewSet, basename='delete')

router.register(r'v1/process', LocalFileProcessViewSet, basename='process')

urlpatterns = [
    path('', include(router.urls)),
    path('', index),
]

# Add this to serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)