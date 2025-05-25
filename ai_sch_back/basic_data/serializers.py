from rest_framework import serializers
from .models import DepartmentInfo, MajorInfo, ClassInfo, BuildingInfo, ClassroomInfo, TeacherInfo, CourseInfo

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentInfo
        fields = '__all__'


class MajorSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_name', read_only=True)

    class Meta:
        model = MajorInfo
        fields = '__all__'


class ClassInfoSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    major_code_name = serializers.CharField(source='major_code.major_name', read_only=True)

    class Meta:
        model = ClassInfo
        fields = '__all__'


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingInfo
        fields = '__all__'


class ClassroomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.building_name', read_only=True)
    management_department_name = serializers.CharField(source='management_department.department_name', read_only=True, allow_null=True)
    campus_name = serializers.CharField(source='campus', read_only=True)
    classroom_type_name = serializers.CharField(source='classroom_type', read_only=True)
    manage_department = serializers.CharField(source='management_department.department_code', allow_null=True, required=False)
    manage_department_name = serializers.CharField(source='management_department.department_name', read_only=True, allow_null=True)

    class Meta:
        model = ClassroomInfo
        fields = '__all__'


class TeacherSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherInfo
        fields = '__all__'
        
    def get_department_name(self, obj):
        try:
            if obj.department and hasattr(obj.department, 'department_name'):
                return obj.department.department_name
            
            if hasattr(obj, 'department_id') and obj.department_id:
                from basic_data.models import DepartmentInfo
                dept = DepartmentInfo.objects.filter(department_name=obj.department_id).first()
                if dept:
                    return dept.department_name
        except Exception:
            pass
            
        return None


class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.department_name', read_only=True)

    class Meta:
        model = CourseInfo
        fields = '__all__' 