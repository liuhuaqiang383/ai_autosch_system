import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sch_back.settings')
django.setup()

from basic_data.models import ClassInfo, DepartmentInfo

def update_class_departments():
    """
    更新所有班级的部门信息
    """
    # 获取所有班级
    classes = ClassInfo.objects.all()
    
    # 记录更新的数量
    updated_count = 0
    
    for class_obj in classes:
        # 如果department_id是部门名称而不是部门代码
        if class_obj.department_id and not DepartmentInfo.objects.filter(department_code=class_obj.department_id).exists():
            # 尝试通过部门名称查找部门
            dept = DepartmentInfo.objects.filter(department_name=class_obj.department_id).first()
            if dept:
                # 更新为正确的部门代码
                old_department_id = class_obj.department_id
                class_obj.department_id = dept.department_code
                class_obj.save()
                updated_count += 1
                print(f"已更新班级 {class_obj.class_name}(ID: {class_obj.id}) 的部门信息：{old_department_id} -> {dept.department_code}")
    
    print(f"共更新了 {updated_count} 个班级的部门信息")

if __name__ == "__main__":
    update_class_departments() 