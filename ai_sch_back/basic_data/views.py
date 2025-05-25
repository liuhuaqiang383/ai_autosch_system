from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import DepartmentInfo, MajorInfo, ClassInfo, BuildingInfo, ClassroomInfo, TeacherInfo, CourseInfo
from .serializers import (
    DepartmentSerializer, MajorSerializer, ClassInfoSerializer, 
    BuildingSerializer, ClassroomSerializer, TeacherSerializer, CourseSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    部门信息管理视图集
    """
    queryset = DepartmentInfo.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department_code', 'department_name', 'is_enabled', 'is_teaching_department']
    search_fields = ['department_code', 'department_name', 'short_name']
    ordering_fields = ['department_code', 'department_name', 'created_at']


class MajorViewSet(viewsets.ModelViewSet):
    """
    专业信息管理视图集
    """
    queryset = MajorInfo.objects.all()
    serializer_class = MajorSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['major_code', 'major_name', 'department', 'is_active']
    search_fields = ['major_code', 'major_name', 'short_name']
    ordering_fields = ['major_code', 'major_name', 'created_at']


class ClassViewSet(viewsets.ModelViewSet):
    """
    班级信息管理视图集
    """
    queryset = ClassInfo.objects.all()
    serializer_class = ClassInfoSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_code', 'class_name', 'department', 'major_code', 'enrollment_year', 'is_graduated']
    search_fields = ['class_code', 'class_name', 'class_short_name']
    ordering_fields = ['class_code', 'class_name', 'created_at']


class BuildingViewSet(viewsets.ModelViewSet):
    """
    教学楼信息管理视图集
    """
    queryset = BuildingInfo.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['building_code', 'building_name', 'campus_name', 'status']
    search_fields = ['building_code', 'building_name', 'campus_name']
    ordering_fields = ['building_code', 'building_name', 'created_at']


class ClassroomViewSet(viewsets.ModelViewSet):
    """
    教室信息管理视图集
    """
    queryset = ClassroomInfo.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['classroom_code', 'classroom_name', 'campus', 'building', 'classroom_type', 'is_enabled']
    search_fields = ['classroom_code', 'classroom_name', 'label']
    ordering_fields = ['classroom_code', 'classroom_name', 'created_at']


class TeacherViewSet(viewsets.ModelViewSet):
    """
    教师信息管理视图集
    """
    queryset = TeacherInfo.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['teacher_code', 'teacher_name', 'department', 'title', 'is_external']
    search_fields = ['teacher_code', 'teacher_name', 'english_name']
    ordering_fields = ['teacher_code', 'teacher_name', 'created_at']


class CourseViewSet(viewsets.ModelViewSet):
    """
    课程信息管理视图集
    """
    queryset = CourseInfo.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course_code', 'course_name', 'department', 'course_nature', 'course_type', 'is_enabled']
    search_fields = ['course_code', 'course_name', 'english_name']
    ordering_fields = ['course_code', 'course_name', 'created_at']


@api_view(['GET'])
def campus_list(request):
    """
    获取所有校区列表
    """
    # 从教学楼和教室表中提取所有校区信息
    building_campuses = BuildingInfo.objects.values_list('campus_name', flat=True).distinct()
    classroom_campuses = ClassroomInfo.objects.values_list('campus', flat=True).distinct()
    
    # 合并两个查询结果并去重
    all_campuses = set(filter(None, building_campuses)) | set(filter(None, classroom_campuses))
    
    # 格式化为前端需要的格式
    results = [{'id': campus, 'name': campus} for campus in all_campuses]
    
    return Response(results)


@api_view(['GET'])
def classroom_type_list(request):
    """
    获取所有教室类型列表
    """
    # 从教室表中提取所有教室类型
    classroom_types = ClassroomInfo.objects.values_list('classroom_type', flat=True).distinct()
    
    # 格式化为前端需要的格式
    results = [{'id': ctype, 'name': ctype} for ctype in filter(None, classroom_types)]
    
    return Response(results)
