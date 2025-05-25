import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sch_back.settings')
django.setup()

from basic_data.models import MajorInfo, DepartmentInfo

def update_major_departments():
    """
    更新所有专业的部门信息
    """
    # 获取所有专业
    majors = MajorInfo.objects.all()
    
    # 记录更新的数量
    updated_count = 0
    
    for major in majors:
        # 如果department_id是部门名称而不是部门代码
        if major.department_id and not DepartmentInfo.objects.filter(department_code=major.department_id).exists():
            # 尝试通过部门名称查找部门
            dept = DepartmentInfo.objects.filter(department_name=major.department_id).first()
            if dept:
                # 更新为正确的部门代码
                old_department_id = major.department_id
                major.department_id = dept.department_code
                major.save()
                updated_count += 1
                print(f"已更新专业 {major.major_name}(ID: {major.id}) 的部门信息：{old_department_id} -> {dept.department_code}")
    
    print(f"共更新了 {updated_count} 个专业的部门信息")

if __name__ == "__main__":
    update_major_departments() 