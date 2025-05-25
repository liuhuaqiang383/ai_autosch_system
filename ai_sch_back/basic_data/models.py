from django.db import models

# Create your models here.

class DepartmentInfo(models.Model):
    department_code = models.CharField(max_length=20, unique=True, verbose_name='部门代码')
    department_name = models.CharField(max_length=100, verbose_name='部门名称')
    department_order = models.CharField(max_length=20, null=True, blank=True, verbose_name='部门序号')
    english_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='部门英文名称')
    short_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='部门简称')
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name='部门地址')
    is_entity = models.BooleanField(default=False, verbose_name='是否实体')
    admin_head = models.CharField(max_length=50, null=True, blank=True, verbose_name='行政负责人')
    party_head = models.CharField(max_length=50, null=True, blank=True, verbose_name='党委负责人')
    establish_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='建立年月')
    expiry_date = models.CharField(max_length=20, null=True, blank=True, verbose_name='失效日期')
    unit_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='所属单位类别')
    unit_affiliation = models.CharField(max_length=50, null=True, blank=True, verbose_name='所属单位办别')
    superior_department = models.CharField(max_length=100, null=True, blank=True, verbose_name='上级部门')
    fixed_building = models.CharField(max_length=100, null=True, blank=True, verbose_name='固定教学楼')
    is_teaching_department = models.BooleanField(default=False, verbose_name='是否开课院系')
    is_course_department = models.BooleanField(default=False, verbose_name='是否上课院系')
    fixed_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='固定电话')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注说明')
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')
    is_teaching_research_office = models.BooleanField(default=False, verbose_name='是否开课教研室')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'department_info'
        verbose_name = '部门信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.department_name


class MajorInfo(models.Model):
    major_code = models.CharField(max_length=20, unique=True, verbose_name='专业编号')
    major_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='专业名称')
    short_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='专业简称')
    school_system = models.CharField(max_length=20, null=True, blank=True, verbose_name='学制')
    english_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='英文名称')
    is_active = models.BooleanField(default=True, verbose_name='开办状态')
    department = models.ForeignKey(DepartmentInfo, to_field='department_code', on_delete=models.CASCADE, db_column='department', verbose_name='所属院系')
    education_level = models.CharField(max_length=20, null=True, blank=True, verbose_name='培养层次')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'major_info'
        verbose_name = '专业信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.major_name or self.major_code


class ClassInfo(models.Model):
    class_code = models.CharField(max_length=20, unique=True, verbose_name='班级编号')
    class_name = models.CharField(max_length=100, verbose_name='班级名称')
    class_short_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='班级简称')
    school_system = models.CharField(max_length=20, null=True, blank=True, verbose_name='学制')
    education_level = models.CharField(max_length=20, null=True, blank=True, verbose_name='培养层次')
    class_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='班级类别')
    counselor = models.CharField(max_length=50, null=True, blank=True, verbose_name='辅导员')
    head_teacher = models.CharField(max_length=50, null=True, blank=True, verbose_name='班主任')
    monitor = models.CharField(max_length=50, null=True, blank=True, verbose_name='班长')
    assistant = models.CharField(max_length=50, null=True, blank=True, verbose_name='班助')
    expected_graduation_year = models.CharField(max_length=20, null=True, blank=True, verbose_name='预计毕业年度')
    is_graduated = models.BooleanField(default=False, verbose_name='是否毕业')
    class_size = models.IntegerField(null=True, blank=True, verbose_name='班级人数')
    gender_distribution = models.CharField(max_length=50, null=True, blank=True, verbose_name='性别分布')
    max_class_size = models.IntegerField(null=True, blank=True, verbose_name='班级最大人数')
    enrollment_year = models.CharField(max_length=10, null=True, blank=True, verbose_name='入学年份')
    department = models.ForeignKey(DepartmentInfo, to_field='department_code', on_delete=models.CASCADE, db_column='department', verbose_name='所属院系')
    major_code = models.ForeignKey(MajorInfo, to_field='major_code', on_delete=models.CASCADE, db_column='major_code', verbose_name='专业编号')
    major_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='专业')
    major_direction = models.CharField(max_length=100, null=True, blank=True, verbose_name='专业方向')
    campus = models.CharField(max_length=50, null=True, blank=True, verbose_name='校区')
    fixed_classroom = models.CharField(max_length=50, null=True, blank=True, verbose_name='固定教室')
    is_fixed_classroom = models.BooleanField(default=False, verbose_name='是否固定教室')
    remarks = models.TextField(null=True, blank=True, verbose_name='备注')
    head_teacher_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='班主任联系电话')
    head_teacher_code = models.CharField(max_length=20, null=True, blank=True, verbose_name='班主任工号')
    graduation_semester = models.CharField(max_length=20, null=True, blank=True, verbose_name='毕业学年学期')
    is_expanded = models.BooleanField(default=False, verbose_name='是否扩招')
    academic_advisor = models.CharField(max_length=50, null=True, blank=True, verbose_name='学业导师')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'class_info'
        verbose_name = '班级信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.class_name


class BuildingInfo(models.Model):
    building_code = models.CharField(max_length=20, unique=True, verbose_name='教学楼编号')
    building_name = models.CharField(max_length=100, verbose_name='教学楼名称')
    campus_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='校区名称')
    status = models.BooleanField(default=True, verbose_name='可用状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'building_info'
        verbose_name = '教学楼信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.building_name


class ClassroomInfo(models.Model):
    classroom_code = models.CharField(max_length=20, unique=True, verbose_name='教室编号')
    classroom_name = models.CharField(max_length=100, verbose_name='教室名称')
    campus = models.CharField(max_length=50, null=True, blank=True, verbose_name='校区')
    building = models.ForeignKey(BuildingInfo, to_field='building_code', on_delete=models.CASCADE, db_column='building', verbose_name='教学楼')
    floor = models.CharField(max_length=10, null=True, blank=True, verbose_name='所在楼层')
    label = models.CharField(max_length=50, null=True, blank=True, verbose_name='教室标签')
    classroom_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='教室类型')
    exam_capacity = models.IntegerField(null=True, blank=True, verbose_name='考场容纳')
    max_capacity = models.IntegerField(null=True, blank=True, verbose_name='最大上课容纳人数')
    has_ac = models.BooleanField(default=False, verbose_name='是否有空调')
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')
    description = models.TextField(null=True, blank=True, verbose_name='教室描述')
    management_department = models.ForeignKey(DepartmentInfo, to_field='department_code', on_delete=models.SET_NULL, null=True, blank=True, db_column='management_department', verbose_name='管理部门')
    weekly_hours = models.CharField(max_length=20, null=True, blank=True, verbose_name='周安排学时')
    area = models.CharField(max_length=20, null=True, blank=True, verbose_name='教室面积')
    furniture_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='桌椅类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'classroom_info'
        verbose_name = '教室信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.classroom_name


class TeacherInfo(models.Model):
    teacher_code = models.CharField(max_length=20, unique=True, verbose_name='工号')
    teacher_name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.CharField(max_length=10, null=True, blank=True, verbose_name='性别')
    english_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='英文姓名')
    ethnicity = models.CharField(max_length=20, null=True, blank=True, verbose_name='民族')
    title = models.CharField(max_length=50, null=True, blank=True, verbose_name='职称')
    department = models.ForeignKey(DepartmentInfo, to_field='department_code', on_delete=models.CASCADE, db_column='department', verbose_name='单位')
    is_external = models.BooleanField(default=False, verbose_name='是否外聘')
    teacher_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='教职工类别')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'teacher_info'
        verbose_name = '教师信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.teacher_name


class CourseInfo(models.Model):
    course_code = models.CharField(max_length=20, unique=True, verbose_name='课程编号')
    course_name = models.CharField(max_length=100, verbose_name='课程名称')
    course_category = models.CharField(max_length=50, null=True, blank=True, verbose_name='课程类别')
    course_attribute = models.CharField(max_length=50, null=True, blank=True, verbose_name='课程属性')
    course_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='课程类型')
    course_nature = models.CharField(max_length=50, null=True, blank=True, verbose_name='课程性质')
    english_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='课程英文名')
    department = models.ForeignKey(DepartmentInfo, to_field='department_code', on_delete=models.CASCADE, db_column='department', verbose_name='开课院系')
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')
    total_hours = models.IntegerField(null=True, blank=True, verbose_name='总学时')
    theory_hours = models.IntegerField(null=True, blank=True, verbose_name='理论学时')
    experiment_hours = models.IntegerField(null=True, blank=True, verbose_name='实验学时')
    computer_hours = models.IntegerField(null=True, blank=True, verbose_name='上机学时')
    practice_hours = models.IntegerField(null=True, blank=True, verbose_name='实践学时')
    other_hours = models.IntegerField(null=True, blank=True, verbose_name='其他学时')
    credits = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='学分')
    weekly_hours = models.IntegerField(null=True, blank=True, verbose_name='周学时')
    is_pure_practice = models.BooleanField(default=False, verbose_name='是否纯实践环节')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'course_info'
        verbose_name = '课程信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.course_name
