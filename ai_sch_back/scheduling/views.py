import sys
from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import SchedulingTask, SchedulingResult, SchedulingStrategy, SchedulingLog, TeachingClassComposition
from .serializers import (
    SchedulingTaskSerializer, SchedulingResultSerializer, SchedulingStrategySerializer,
    SchedulingLogSerializer, TeachingClassCompositionSerializer
)
from .scheduling import SchedulingAlgorithm # 导入排课算法类


class SchedulingTaskViewSet(viewsets.ModelViewSet):
    """
    排课任务管理视图集
    """
    queryset = SchedulingTask.objects.all()
    serializer_class = SchedulingTaskSerializer
    permission_classes = [AllowAny] 
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['semester', 'course_code', 'teacher_code', 'teaching_class_code', 'department', 'campus']
    search_fields = ['teaching_class_code', 'teaching_class_name', 'course_name', 'teacher_name']
    ordering_fields = ['teaching_class_code', 'scheduling_priority', 'created_at']

    @action(detail=False, methods=['get'], url_path='run-scheduling')
    def run_scheduling(self, request):
        """
        一键启动自动排课，记录并跳过因教室数据限制无法安排的任务。
        """
        scheduler = SchedulingAlgorithm()
        try:
            # 你可以根据需要调整 population_size 和 ngen
            best_schedule = scheduler.run(population_size=50, ngen=10)
            scheduler.save_to_database(best_schedule)

            # 准备返回给前端的失败任务信息
            failed_tasks_info = [
                {
                    'course_code': task['course'].get('course_code'),
                    'course_name': task['course'].get('course_name'),
                    'teaching_class_code': task['course'].get('teaching_class_code'),
                    'reason': task['reason']
                }
                for task in scheduler.failed_tasks
            ]

            response_data = {
                "message": f"排课完成。成功安排 {len(best_schedule)} 个任务。",
                "failed_count": len(failed_tasks_info),
                "failed_tasks": failed_tasks_info
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # 建议在生产环境中记录更详细的日志
            error_message = f"排课过程中出错: {str(e)}"
            print(error_message, file=sys.stderr) # 打印到 stderr

            # 即使出错，也尝试返回已记录的失败任务信息
            failed_tasks_info = [
                 {
                    'course_code': task['course'].get('course_code'),
                    'course_name': task['course'].get('course_name'),
                    'teaching_class_code': task['course'].get('teaching_class_code'),
                    'reason': task['reason']
                 }
                 for task in getattr(scheduler, 'failed_tasks', []) # 安全访问
            ]

            return Response({
                "error": error_message,
                "failed_count": len(failed_tasks_info),
                "failed_tasks": failed_tasks_info
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SchedulingResultViewSet(viewsets.ModelViewSet):
    """
    排课结果管理视图集
    """
    queryset = SchedulingResult.objects.all()
    serializer_class = SchedulingResultSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['semester', 'course_code', 'teacher_code', 'teaching_class_code', 'classroom_code', 'day_of_week']
    search_fields = ['teaching_class_code', 'teaching_class_name', 'course_name', 'teacher_name', 'classroom_name']
    ordering_fields = ['day_of_week', 'start_section', 'created_at']


class SchedulingStrategyViewSet(viewsets.ModelViewSet):
    """
    排课策略管理视图集
    """
    queryset = SchedulingStrategy.objects.all()
    serializer_class = SchedulingStrategySerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['strategy_name', 'is_default']
    search_fields = ['strategy_name', 'description']
    ordering_fields = ['strategy_name', 'created_at']

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        设置为默认策略
        """
        strategy = self.get_object()
        # 先将所有策略设置为非默认
        SchedulingStrategy.objects.all().update(is_default=False)
        # 将当前策略设置为默认
        strategy.is_default = True
        strategy.save()
        return Response({"message": f"策略 {strategy.strategy_name} 已设置为默认"}, status=status.HTTP_200_OK)


class SchedulingLogViewSet(viewsets.ModelViewSet):
    """
    排课日志管理视图集
    """
    queryset = SchedulingLog.objects.all()
    serializer_class = SchedulingLogSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['task_id', 'task_type', 'status']
    search_fields = ['task_id', 'message']
    ordering_fields = ['created_at']


class TeachingClassCompositionViewSet(viewsets.ModelViewSet):
    """
    教学班组成管理视图集
    """
    queryset = TeachingClassComposition.objects.all()
    serializer_class = TeachingClassCompositionSerializer
    permission_classes = [AllowAny]  # 开发阶段临时允许未认证访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['teaching_class_code', 'class_code']
