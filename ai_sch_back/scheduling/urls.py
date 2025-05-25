from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tasks', views.SchedulingTaskViewSet)
router.register(r'results', views.SchedulingResultViewSet)
router.register(r'strategies', views.SchedulingStrategyViewSet)
router.register(r'logs', views.SchedulingLogViewSet)
router.register(r'compositions', views.TeachingClassCompositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 