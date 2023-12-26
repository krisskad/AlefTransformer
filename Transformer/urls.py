from django.urls import path, include
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register(r'home', HomeView, basename='home')
router.register(r'upload', UploadViewSet, basename='upload')
router.register(r'delete', DeleteFolderViewSet, basename='delete')

urlpatterns = [
    path('', include(router.urls)),
]