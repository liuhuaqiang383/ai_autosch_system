import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_sch_back.settings')
django.setup()

from basic_data.models import ClassroomInfo, BuildingInfo, DepartmentInfo

def update_classroom_relations():
    """
    更新所有教室的建筑和管理部门信息
    """
    # 获取所有教室
    classrooms = ClassroomInfo.objects.all()
    
    # 记录更新的数量
    building_updated_count = 0
    department_updated_count = 0
    
    for classroom in classrooms:
        # 处理建筑信息
        if classroom.building_id and not BuildingInfo.objects.filter(building_code=classroom.building_id).exists():
            # 尝试通过建筑名称查找建筑
            building = BuildingInfo.objects.filter(building_name=classroom.building_id).first()
            if building:
                # 更新为正确的建筑代码
                old_building_id = classroom.building_id
                classroom.building_id = building.building_code
                building_updated_count += 1
                print(f"已更新教室 {classroom.classroom_name}(ID: {classroom.id}) 的建筑信息：{old_building_id} -> {building.building_code}")
        
        # 处理管理部门信息
        if classroom.management_department_id and not DepartmentInfo.objects.filter(department_code=classroom.management_department_id).exists():
            # 尝试通过部门名称查找部门
            department = DepartmentInfo.objects.filter(department_name=classroom.management_department_id).first()
            if department:
                # 更新为正确的部门代码
                old_department_id = classroom.management_department_id
                classroom.management_department_id = department.department_code
                department_updated_count += 1
                print(f"已更新教室 {classroom.classroom_name}(ID: {classroom.id}) 的管理部门信息：{old_department_id} -> {department.department_code}")
        
        # 保存更改
        if building_updated_count > 0 or department_updated_count > 0:
            classroom.save()
    
    print(f"共更新了 {building_updated_count} 个教室的建筑信息")
    print(f"共更新了 {department_updated_count} 个教室的管理部门信息")

if __name__ == "__main__":
    update_classroom_relations() 