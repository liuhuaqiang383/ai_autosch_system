from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import SysUser, SysRole
from .serializers import SysUserSerializer, SysRoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    """
    queryset = SysUser.objects.all()
    serializer_class = SysUserSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['username', 'status', 'is_active', 'is_staff']
    search_fields = ['username', 'name', 'email', 'phone']
    ordering_fields = ['id', 'username', 'create_time']


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理视图集
    """
    queryset = SysRole.objects.all()
    serializer_class = SysRoleSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'name']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['id', 'code', 'name', 'create_time']


class LoginView(APIView):
    """
    用户登录视图
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': '请提供用户名和密码'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                serializer = SysUserSerializer(user)
                return Response(serializer.data)
            else:
                return Response({'error': '用户已被禁用'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    用户登出视图
    """
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问

    def post(self, request):
        logout(request)
        return Response({'message': '成功登出'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    用户个人信息视图
    """
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问

    def get(self, request):
        serializer = SysUserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = SysUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
