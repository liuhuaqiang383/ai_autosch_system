from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'departments', views.DepartmentViewSet)
router.register(r'majors', views.MajorViewSet)
router.register(r'classes', views.ClassViewSet)
router.register(r'buildings', views.BuildingViewSet)
router.register(r'classrooms', views.ClassroomViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'courses', views.CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('campuses/', views.campus_list, name='campus-list'),
    path('classroom-types/', views.classroom_type_list, name='classroom-type-list'),
] 