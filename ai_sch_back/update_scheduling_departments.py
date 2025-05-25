import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sch_back.settings')
django.setup()

from scheduling.models import SchedulingTask
from basic_data.models import DepartmentInfo, CourseInfo

def update_scheduling_departments():
    """
    更新所有排课任务的部门信息
    """
    # 获取所有排课任务
    tasks = SchedulingTask.objects.all()
    
    # 记录更新的数量
    updated_count = 0
    
    for task in tasks:
        # 如果department_id是部门名称而不是部门代码
        if task.department_id and not DepartmentInfo.objects.filter(department_code=task.department_id).exists():
            # 尝试通过部门名称查找部门
            dept = DepartmentInfo.objects.filter(department_name=task.department_id).first()
            if dept:
                # 更新为正确的部门代码
                old_department_id = task.department_id
                task.department_id = dept.department_code
                task.save()
                updated_count += 1
                print(f"已更新排课任务 {task.teaching_class_code}(ID: {task.id}) 的部门信息：{old_department_id} -> {dept.department_code}")
                continue
        
        # 如果department_id为空，尝试从课程获取部门信息
        if not task.department_id and task.course_code_id:
            try:
                course = CourseInfo.objects.get(course_code=task.course_code_id)
                if course.department_id:
                    task.department_id = course.department_id
                    task.save()
                    updated_count += 1
                    print(f"已更新排课任务 {task.teaching_class_code}(ID: {task.id}) 的部门信息：None -> {course.department_id}")
            except CourseInfo.DoesNotExist:
                pass
    
    print(f"共更新了 {updated_count} 个排课任务的部门信息")

if __name__ == "__main__":
    update_scheduling_departments() 