import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sch_back.settings')
django.setup()

from basic_data.models import TeacherInfo, DepartmentInfo

def update_teacher_departments():
    """
    更新所有教师的部门信息
    """
    # 获取所有教师
    teachers = TeacherInfo.objects.all()
    
    # 记录更新的数量
    updated_count = 0
    
    for teacher in teachers:
        # 如果department_id是部门名称而不是部门代码
        if teacher.department_id and not DepartmentInfo.objects.filter(department_code=teacher.department_id).exists():
            # 尝试通过部门名称查找部门
            dept = DepartmentInfo.objects.filter(department_name=teacher.department_id).first()
            if dept:
                # 更新为正确的部门代码
                teacher.department_id = dept.department_code
                teacher.save()
                updated_count += 1
                print(f"已更新教师 {teacher.teacher_name}(ID: {teacher.id}) 的部门信息：{teacher.department_id} -> {dept.department_code}")
    
    print(f"共更新了 {updated_count} 名教师的部门信息")

if __name__ == "__main__":
    update_teacher_departments() 