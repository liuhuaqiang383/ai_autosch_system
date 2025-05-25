from rest_framework import serializers
from .models import SchedulingTask, SchedulingResult, SchedulingStrategy, SchedulingLog, TeachingClassComposition

class SchedulingTaskSerializer(serializers.ModelSerializer):
    course_name_display = serializers.CharField(source='course_code.course_name', read_only=True)
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    teacher_name_display = serializers.CharField(source='teacher_code.teacher_name', read_only=True)

    class Meta:
        model = SchedulingTask
        fields = '__all__'


class SchedulingResultSerializer(serializers.ModelSerializer):
    course_name_display = serializers.CharField(source='course_code.course_name', read_only=True)
    teacher_name_display = serializers.CharField(source='teacher_code.teacher_name', read_only=True)
    classroom_name_display = serializers.CharField(source='classroom_code.classroom_name', read_only=True)
    class_names = serializers.SerializerMethodField(read_only=True)
    
    def get_class_names(self, obj):
        # 获取与该教学班关联的所有班级信息
        compositions = TeachingClassComposition.objects.filter(teaching_class_code=obj.teaching_class_code)
        return [comp.class_code.class_name for comp in compositions]

    class Meta:
        model = SchedulingResult
        fields = '__all__'


class SchedulingStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulingStrategy
        fields = '__all__'


class SchedulingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchedulingLog
        fields = '__all__'


class TeachingClassCompositionSerializer(serializers.ModelSerializer):
    teaching_class_name = serializers.CharField(source='teaching_class_code.teaching_class_name', read_only=True)
    class_name = serializers.CharField(source='class_code.class_name', read_only=True)

    class Meta:
        model = TeachingClassComposition
        fields = '__all__'