from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, QAViewSet, ChatSessionViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'qa', QAViewSet, basename='qa')
router.register(r'chat', ChatSessionViewSet, basename='chat')

urlpatterns = [path('', include(router.urls))]