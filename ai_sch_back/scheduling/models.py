from django.db import models
from basic_data.models import DepartmentInfo, CourseInfo, TeacherInfo, ClassroomInfo, BuildingInfo, ClassInfo

class SchedulingTask(models.Model):
    semester = models.CharField(max_length=20, null=True, blank=True, verbose_name='学年学期')
    course_code = models.ForeignKey(CourseInfo, to_field='course_code', on_delete=models.CASCADE, db_column='course_code', verbose_name='课程编号')
    course_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='课程名称')
    teacher_code = models.ForeignKey(TeacherInfo, to_field='teacher_code', on_delete=models.CASCADE, db_column='teacher_code', verbose_name='教师工号')
    teacher_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='任课教师')
    class_composition = models.TextField(null=True, blank=True, verbose_name='教学班组成')
    teaching_class_code = models.CharField(max_length=50, unique=True, verbose_name='教学班编号')
    course_affiliation = models.CharField(max_length=100, null=True, blank=True, verbose_name='课程归属')
    course_credits = models.CharField(max_length=10, null=True, blank=True, verbose_name='课程学分')
    teaching_class_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='教学班名称')
    hour_type = models.CharField(max_length=20, null=True, blank=True, verbose_name='学时类型')
    course_hours = models.IntegerField(null=True, blank=True, verbose_name='开课学时')
    scheduling_hours = models.IntegerField(null=True, blank=True, verbose_name='排课学时')
    total_hours = models.IntegerField(null=True, blank=True, verbose_name='总学时')
    scheduling_priority = models.IntegerField(null=True, blank=True, verbose_name='排课优先级')
    class_size = models.IntegerField(null=True, blank=True, verbose_name='教学班人数')
    course_nature = models.CharField(max_length=50, null=True, blank=True, verbose_name='课程性质')
    campus = models.CharField(max_length=50, null=True, blank=True, verbose_name='开课校区')
    is_external = models.BooleanField(default=False, verbose_name='是否外聘')
    department = models.ForeignKey(DepartmentInfo, to_field='department_code', on_delete=models.CASCADE, db_column='department', verbose_name='开课院系')
    weekly_hours = models.CharField(max_length=50, null=True, blank=True, verbose_name='开课周次学时')
    consecutive_periods = models.IntegerField(null=True, blank=True, verbose_name='连排节次')
    classroom_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='指定教室类型')
    specified_classroom = models.ForeignKey(ClassroomInfo, to_field='classroom_code', null=True, blank=True, on_delete=models.SET_NULL, db_column='specified_classroom', verbose_name='指定教室')
    specified_building = models.ForeignKey(BuildingInfo, to_field='building_code', null=True, blank=True, on_delete=models.SET_NULL, db_column='specified_building', verbose_name='指定教学楼')
    specified_time = models.CharField(max_length=100, null=True, blank=True, verbose_name='指定时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'scheduling_task'
        verbose_name = '排课任务'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.teaching_class_code}-{self.course_name or ''}"


class SchedulingResult(models.Model):
    task = models.ForeignKey(SchedulingTask, on_delete=models.SET_NULL, null=True, verbose_name='排课任务ID')
    semester = models.CharField(max_length=20, null=True, blank=True, verbose_name='学年学期')
    course_code = models.ForeignKey(CourseInfo, to_field='course_code', on_delete=models.CASCADE, db_column='course_code', verbose_name='课程编号')
    course_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='课程名称')
    teacher_code = models.ForeignKey(TeacherInfo, to_field='teacher_code', on_delete=models.CASCADE, db_column='teacher_code', verbose_name='教师工号')
    teacher_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='任课教师')
    teaching_class_code = models.ForeignKey(SchedulingTask, to_field='teaching_class_code', on_delete=models.CASCADE, db_column='teaching_class_code', related_name='results', verbose_name='教学班编号')
    teaching_class_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='教学班名称')
    classroom_code = models.ForeignKey(ClassroomInfo, to_field='classroom_code', on_delete=models.CASCADE, db_column='classroom_code', verbose_name='教室编号')
    classroom_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='教室名称')
    day_of_week = models.IntegerField(null=True, blank=True, verbose_name='星期几')
    start_section = models.IntegerField(null=True, blank=True, verbose_name='开始节次')
    end_section = models.IntegerField(null=True, blank=True, verbose_name='结束节次')
    week_list = models.CharField(max_length=100, null=True, blank=True, verbose_name='周次列表')
    is_fixed = models.BooleanField(default=False, verbose_name='是否固定')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'scheduling_result'
        verbose_name = '排课结果'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.course_name}-{self.teacher_name}-星期{self.day_of_week or ''}-第{self.start_section or ''}节"


class SchedulingStrategy(models.Model):
    strategy_name = models.CharField(max_length=100, verbose_name='策略名称')
    description = models.TextField(null=True, blank=True, verbose_name='策略描述')
    is_default = models.BooleanField(default=False, verbose_name='是否默认策略')
    teacher_weight = models.IntegerField(default=5, verbose_name='教师权重')
    classroom_weight = models.IntegerField(default=5, verbose_name='教室权重')
    class_weight = models.IntegerField(default=5, verbose_name='班级权重')
    avoid_teacher_conflict = models.BooleanField(default=True, verbose_name='避免教师冲突')
    avoid_classroom_conflict = models.BooleanField(default=True, verbose_name='避免教室冲突')
    avoid_class_conflict = models.BooleanField(default=True, verbose_name='避免班级冲突')
    prefer_teacher_continuous = models.BooleanField(default=False, verbose_name='教师连续上课偏好')
    prefer_class_continuous = models.BooleanField(default=False, verbose_name='班级连续上课偏好')
    max_daily_hours_teacher = models.IntegerField(default=8, verbose_name='教师每日最大课时')
    max_daily_hours_class = models.IntegerField(default=10, verbose_name='班级每日最大课时')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'scheduling_strategy'
        verbose_name = '排课策略'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.strategy_name


class SchedulingLog(models.Model):
    task_id = models.CharField(max_length=36, verbose_name='任务ID')
    task_type = models.CharField(max_length=20, verbose_name='任务类型')
    status = models.CharField(max_length=20, verbose_name='状态')
    progress = models.IntegerField(default=0, verbose_name='进度')
    message = models.TextField(null=True, blank=True, verbose_name='消息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'scheduling_log'
        verbose_name = '排课任务日志'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.task_id}-{self.task_type}"


class TeachingClassComposition(models.Model):
    teaching_class_code = models.ForeignKey(SchedulingTask, to_field='teaching_class_code', on_delete=models.CASCADE, db_column='teaching_class_code', verbose_name='教学班编号')
    class_code = models.ForeignKey(ClassInfo, to_field='class_code', on_delete=models.CASCADE, db_column='class_code', verbose_name='班级编号')

    class Meta:
        db_table = 'teaching_class_composition'
        verbose_name = '教学班组成'
        verbose_name_plural = verbose_name
        unique_together = ('teaching_class_code', 'class_code')

    def __str__(self):
        return f"{self.teaching_class_code}-{self.class_code}"
