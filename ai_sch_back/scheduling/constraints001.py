import pandas as pd

# 定义一个名为 HardConstraints 的类，用于处理所有的硬约束检查
class HardConstraints:
    # 定义一个静态方法，用于检查所有的硬约束条件
    @staticmethod
    def check_all(individual, algorithm):
        """检查所有硬约束"""
        # 依次调用各个硬约束检查方法，并使用逻辑与操作符连接结果
        # 只有当所有硬约束条件都满足时，才返回 True
        return (
            # 检查教室分配是否合理
            HardConstraints.check_room_assignment(individual, algorithm) and
            # 检查教师的可用性，确保教师在同一时间没有多门课程的安排
            HardConstraints.check_teacher_availability(individual) and
            # 检查时间冲突，确保同一教室在同一时间没有多门课程的安排
            HardConstraints.check_time_conflicts(individual) and
            # 检查连续课程的安排是否合理，避免连续课程之间的冲突
            HardConstraints.check_consecutive_sessions(individual, algorithm) and
            # 检查课程和教室的校区是否匹配
            HardConstraints.check_campus_constraints(individual, algorithm) and
            # 检查固定教室的安排是否符合要求
            HardConstraints.check_fixed_classrooms(individual, algorithm) and
            # 检查教师上午/下午的课时限制，避免教师在一个半天内授课过多
            HardConstraints.check_teacher_am_pm_limit(individual, algorithm) and
            # 检查教师的周课时限制，避免教师一周内授课过多
            HardConstraints.check_teacher_hours(individual, algorithm) and
            # 检查课程是否安排在指定的教学楼内
            HardConstraints.check_specific_building(individual, algorithm)
        )
    
    # 定义一个静态方法，用于检查教室分配是否合理
    @staticmethod
    def check_room_assignment(individual, algorithm):
        """检查教室分配是否合理，强化对 None 和无效数据的处理。"""
        for assignment in individual:
            course_code = assignment.get('course_code', 'Unknown')
            classroom_code = assignment.get('classroom_code') # 可能为 None (无效基因)

            # 如果基因无效，直接跳过检查 (evaluate 应该已处理，但加一层保险)
            if classroom_code is None:
                continue

            course = algorithm.course_lookup.get(course_code)
            if not course:
                # 理论上不应发生，因为 course_data 是基于 task 表的
                print(f"[严重警告] check_room_assignment: 找不到课程 {course_code} 的信息！")
                return False

            classroom = algorithm.classroom_lookup.get(classroom_code)
            if not classroom:
                # 这可能发生，如果随机生成的 classroom_code 无效
                print(f"硬约束失败: 教室分配 - 找不到教室 {classroom_code} (课程: {course_code}) 的信息。")
                return False

            # 1. 检查教室类型匹配
            course_room_type = course.get('classroom_type') or '普通教室' # 课程要求的类型
            actual_room_type = classroom.get('classroom_type')
            if not actual_room_type: # None 或空字符串
                actual_room_type = '未知类型'

            # 类型不匹配: 实际类型 != 需要类型 且 实际类型不是 '未知类型'
            if actual_room_type != course_room_type and actual_room_type != '未知类型':
                 print(f"硬约束失败: 教室类型不匹配 - 课程 {course_code} 要求 '{course_room_type}', 但分配到教室 {classroom_code} (类型: '{actual_room_type}')。")
                 return False

            # 2. 检查教室容量
            course_size_raw = course.get('class_size')
            max_capacity_raw = classroom.get('max_capacity')
            course_size = None
            max_capacity = None

            # 安全地转换课程人数
            try:
                if course_size_raw is not None and not pd.isna(course_size_raw):
                    course_size = int(course_size_raw)
                    if course_size <= 0: course_size = None # 无效人数视为未知
            except (ValueError, TypeError):
                pass # 转换失败视为未知

            # 安全地转换教室容量
            try:
                if max_capacity_raw is not None and not pd.isna(max_capacity_raw):
                    max_capacity = int(max_capacity_raw)
            except (ValueError, TypeError):
                pass # 转换失败视为未知

            # 仅当课程人数和教室容量都有效时进行比较
            if course_size is not None and max_capacity is not None:
                if course_size > max_capacity:
                    print(f"硬约束失败: 教室容量不足 - 课程 {course_code} ({course_size}人) 分配到教室 {classroom_code} (容量: {max_capacity})。")
                    return False
            elif course_size is not None and max_capacity is None:
                 # 如果课程有人数要求但教室容量未知，认为约束失败
                 print(f"硬约束失败: 教室容量未知 - 课程 {course_code} ({course_size}人) 无法分配到容量未知的教室 {classroom_code}。")
                 return False
            # elif course_size is None: # 如果课程人数未知，暂时允许分配
            #     print(f"警告: 课程 {course_code} 人数未知，无法严格验证教室 {classroom_code} 容量。")

        return True
    
    # 定义一个静态方法，用于检查教师的可用性
    @staticmethod
    def check_teacher_availability(individual):
        """检查教师可用性（基于节次）"""
        teacher_schedule = {}  # {(teacher_code, day_of_week, section): True}
        for assignment in individual:
            teacher_code = assignment['teacher_code']
            day = assignment['day_of_week']
            start_section = assignment['start_section']
            end_section = assignment['end_section']

            # 检查该教师是否为空或无效
            if not teacher_code:
                print(f"警告：跳过教师可用性检查，无效的 teacher_code: {assignment}")
                continue # 或者 return False，取决于业务逻辑严格性

            for section in range(start_section, end_section + 1):
                key = (teacher_code, day, section)
                if key in teacher_schedule:
                    print(f"硬约束失败: 教师冲突 - {key} (Assignment: {assignment['course_code']}/{assignment['teaching_class_code']})")
                    return False
                teacher_schedule[key] = True
        return True
    
    # 定义一个静态方法，用于检查时间冲突
    @staticmethod
    def check_time_conflicts(individual):
        """检查时间冲突（基于教室和节次）"""
        classroom_schedule = {}  # {(classroom_code, day_of_week, section): True}
        for assignment in individual:
            classroom_code = assignment['classroom_code']
            day = assignment['day_of_week']
            start_section = assignment['start_section']
            end_section = assignment['end_section']

            # 检查教室代码是否有效
            if not classroom_code:
                print(f"警告：跳过教室时间冲突检查，无效的 classroom_code: {assignment}")
                continue # 或者 return False

            for section in range(start_section, end_section + 1):
                key = (classroom_code, day, section)
                if key in classroom_schedule:
                    print(f"硬约束失败: 教室冲突 - {key} (Assignment: {assignment['course_code']}/{assignment['teaching_class_code']})")
                    return False
                classroom_schedule[key] = True
        return True
    
    # 定义一个静态方法，用于检查连续课程的安排是否合理
    @staticmethod
    def check_consecutive_sessions(individual, algorithm):
        # 遍历个体中的每个课程安排
        for assignment in individual:
            # 如果课程的连续课时数大于 2
            if assignment['consecutive_periods'] > 2:  # 使用数据库字段名 consecutive_periods
                # 遍历连续课时数
                for i in range(1, assignment['consecutive_periods']):
                    # 获取下一个时间槽
                    next_slot = algorithm.get_next_time_slot(assignment['time_slot'], i)
                    # 如果未找到下一个时间槽，返回 False
                    if not next_slot:
                        return False
                    # 检查是否存在冲突，即同一教室在同一星期的下一个时间槽有其他课程安排
                    conflict = any(
                        a['classroom_code'] == assignment['classroom_code'] and 
                        a['day_of_week'] == assignment['day_of_week'] and 
                        a['time_slot'] == next_slot
                        for a in individual
                    )
                    # 如果存在冲突，返回 False
                    if conflict:
                        return False
        # 如果所有连续课程的安排都合理，返回 True
        return True
    
    # 定义一个静态方法，用于检查课程和教室的校区是否匹配
    @staticmethod
    def check_campus_constraints(individual, algorithm):
        for assignment in individual:
            course = algorithm.course_lookup.get(assignment['course_code'])
            classroom = algorithm.classroom_lookup.get(assignment['classroom_code'])

            if course and classroom:
                course_campus = course.get('campus')
                classroom_campus = classroom.get('campus')

                # 允许 None == None, 但不允许 None != 'SomeCampus'
                if course_campus != classroom_campus and (course_campus is not None or classroom_campus is not None):
                    print(f"硬约束失败: 校区不匹配 - Course {course['course_code']} ({course_campus}) vs Classroom {classroom['classroom_code']} ({classroom_campus})")
                    return False
            # else: 课程或教室查找失败已在 check_room_assignment 处理

        return True
    
    # 定义一个静态方法，用于检查固定教室的安排是否符合要求
    @staticmethod
    def check_fixed_classrooms(individual, algorithm):
        # 遍历个体中的每个课程安排
        for assignment in individual:
            # 通过教学班级代码从算法的班级查找表中获取班级信息
            class_info = algorithm.class_lookup.get(assignment['teaching_class_code'], {})
            # 如果班级信息中指定了固定教室
            if class_info.get('is_fixed_classroom'):
                # 检查分配的教室代码是否与固定教室代码一致
                if assignment['classroom_code'] != class_info['fixed_classroom']:
                    return False
        # 如果所有固定教室的安排都符合要求，返回 True
        return True

    # 定义一个静态方法，用于检查教师上午/下午的课时限制
    @staticmethod
    def check_teacher_am_pm_limit(individual, algorithm):
        """检查教师上午/下午课时限制（基于节次）"""
        teacher_hours = {} # {teacher_code: {'am': sections, 'pm': sections}}
        for assignment in individual:
            teacher_code = assignment['teacher_code']
            if not teacher_code:
                 print(f"警告: 发现无效 teacher_code in check_teacher_am_pm_limit for {assignment['course_code']}")
                 continue

            if teacher_code not in teacher_hours:
                teacher_hours[teacher_code] = {'am': 0, 'pm': 0}

            try:
                start_section = int(assignment['start_section'])
                end_section = int(assignment['end_section'])
                if start_section > end_section:
                     print(f"警告: 无效节次范围 in check_teacher_am_pm_limit for {assignment['course_code']}: {start_section}-{end_section}")
                     continue
                sections_in_assignment = end_section - start_section + 1
            except (ValueError, TypeError):
                 print(f"警告: 无效节次数据 in check_teacher_am_pm_limit for {assignment['course_code']}: start={assignment['start_section']}, end={assignment['end_section']}")
                 continue

            # 假设 1-4 节为上午，5-8 节为下午 (根据 time_slots 定义)
            # 简化处理：主要看开始时间在哪 (需要更精确逻辑处理跨午休)
            if start_section <= 4: # 主要在上午
                teacher_hours[teacher_code]['am'] += sections_in_assignment
            elif start_section >= 5: # 主要在下午
                 teacher_hours[teacher_code]['pm'] += sections_in_assignment
            # else: # 处理跨越中午的课程，例如 3-6 节
                 # am_hours = max(0, 4 - start_section + 1)
                 # pm_hours = max(0, end_section - 5 + 1)
                 # teacher_hours[teacher_code]['am'] += am_hours
                 # teacher_hours[teacher_code]['pm'] += pm_hours

        for teacher_code, hours in teacher_hours.items():
            teacher = algorithm.teacher_lookup.get(teacher_code)
            if teacher:
                # 注意：'max_am_hours', 'max_pm_hours' 不在 teacher_info 表 schema 中
                max_am = teacher.get('max_am_hours', 4)  # 默认上午最多 4 节
                max_pm = teacher.get('max_pm_hours', 4)  # 默认下午最多 4 节
                if hours['am'] > max_am or hours['pm'] > max_pm:
                    print(f"硬约束失败: 教师半天课时超限 - {teacher_code}: AM={hours['am']}/{max_am}, PM={hours['pm']}/{max_pm}")
                    return False
            else:
                 print(f"警告: 在 check_teacher_am_pm_limit 中未找到教师信息: {teacher_code}")
                 # return False
        return True

    # 定义一个静态方法，用于检查教师的周课时限制
    @staticmethod
    def check_teacher_hours(individual, algorithm):
        """检查教师周课时限制（基于节次）"""
        teacher_section_counts = {}
        for assignment in individual:
            teacher_code = assignment['teacher_code']
            # 确保节次有效
            try:
                start_section = int(assignment['start_section'])
                end_section = int(assignment['end_section'])
                if start_section > end_section:
                     print(f"警告: 无效节次范围 in check_teacher_hours for {assignment['course_code']}: {start_section}-{end_section}")
                     continue
                sections_count = end_section - start_section + 1
            except (ValueError, TypeError):
                 print(f"警告: 无效节次数据 in check_teacher_hours for {assignment['course_code']}: start={assignment['start_section']}, end={assignment['end_section']}")
                 continue

            if teacher_code: # 确保 teacher_code 有效
                 teacher_section_counts[teacher_code] = teacher_section_counts.get(teacher_code, 0) + sections_count
            else:
                 print(f"警告: 发现无效 teacher_code in check_teacher_hours for {assignment['course_code']}")

        for teacher_code, count in teacher_section_counts.items():
            teacher = algorithm.teacher_lookup.get(teacher_code)
            if teacher:
                # 注意：'max_weekly_hours' 不在 teacher_info 表 schema 中，这里使用默认值
                # 如果需要严格执行，需在数据库或配置文件中定义此限制
                max_hours = teacher.get('max_weekly_hours', 30) # 假设默认每周最多 30 节
                if count > max_hours:
                    print(f"硬约束失败: 教师周课时超限 - {teacher_code}: {count} > {max_hours}")
                    return False
            else:
                 # 如果在 teacher_lookup 中找不到教师，可能表示数据问题
                 print(f"警告: 在 check_teacher_hours 中未找到教师信息: {teacher_code}")
                 # 根据业务需求决定是跳过还是失败
                 # return False # 如果严格要求教师必须存在
        return True

    # 定义一个静态方法，用于检查课程是否安排在指定的教学楼内
    @staticmethod
    def check_specific_building(individual, algorithm):
        """检查特定教学楼要求"""
        for assignment in individual:
            course = algorithm.course_lookup.get(assignment['course_code'])
            classroom = algorithm.classroom_lookup.get(assignment['classroom_code'])

            if course and classroom:
                specified_building = course.get('specified_building')
                classroom_building = classroom.get('building')

                # 如果课程指定了教学楼，但分配的教室不在该楼 (且教室楼信息存在)
                if specified_building and classroom_building is not None and classroom_building != specified_building:
                     print(f"硬约束失败: 指定教学楼不匹配 - Course {course['course_code']} 要求 {specified_building}, 分配在 {classroom['classroom_code']} ({classroom_building})")
                     return False
                # 如果课程指定了楼，但教室楼信息未知
                elif specified_building and classroom_building is None:
                     print(f"警告: 教室 {classroom['classroom_code']} 楼宇信息未知 (None)，无法验证课程 {course['course_code']} 的指定教学楼 {specified_building}")
                     # return False # 根据业务决定
            # else: 课程或教室查找失败已在 check_room_assignment 处理

        return True

# 定义一个名为 SoftConstraints 的类，用于处理所有的软约束优化
class SoftConstraints:
    # 定义一个静态方法，用于计算所有软约束的总分
    @staticmethod
    def optimize_all(individual, algorithm):
        """计算所有软约束的总分"""
        # 初始化总分为 0
        score = 0
        # 累加同一课程尽量使用同一教室的优化得分
        score += SoftConstraints.optimize_same_room_for_course(individual)
        # 累加教师偏好时间安排的优化得分
        score += SoftConstraints.optimize_teacher_preferences(individual, algorithm)
        # 累加优先课程安排的优化得分
        score += SoftConstraints.optimize_priority_scheduling(individual, algorithm)
        # 累加体育课后尽量不排课的优化得分
        score += SoftConstraints.optimize_post_pe_class(individual, algorithm)
        # 累加体育课尽量安排在下午的优化得分
        score += SoftConstraints.optimize_pe_class_time(individual)
        # 累加院系教室优先的优化得分
        score += SoftConstraints.optimize_department_room_priority(individual, algorithm)
        # 累加周学时拆分优化的得分
        score += SoftConstraints.optimize_weekly_hours_split(individual, algorithm)
        # 返回总得分
        return score
    
    # 定义一个静态方法，用于优化同一课程尽量使用同一教室
    @staticmethod
    def optimize_same_room_for_course(individual):
        # 初始化惩罚分为 0
        penalty = 0
        # 初始化一个空字典，用于存储每个课程使用的教室集合
        course_rooms = {}
        # 遍历个体中的每个课程安排
        for assignment in individual:
            # 如果课程代码不在字典中，初始化该课程的教室集合
            if assignment['course_code'] not in course_rooms:
                course_rooms[assignment['course_code']] = set()
            # 将该课程使用的教室代码添加到教室集合中
            course_rooms[assignment['course_code']].add(assignment['classroom_code'])
        
        # 遍历每个课程使用的教室集合
        for rooms in course_rooms.values():
            # 计算惩罚分，即教室数量减 1
            penalty += len(rooms) - 1
        # 返回负的惩罚分乘以 5，作为该软约束的得分
        return -penalty * 5
    
    # 定义一个静态方法，用于优化教师偏好时间安排
    @staticmethod
    def optimize_teacher_preferences(individual, algorithm):
        # 初始化得分为 0
        score = 0
        # 遍历个体中的每个课程安排
        for assignment in individual:
            # 通过教师代码从算法的教师查找表中获取教师信息
            teacher = algorithm.teacher_lookup.get(assignment['teacher_code'], {})
            # 获取教师的偏好时间列表
            preferred = teacher.get('preferred_times', [])
            # 如果教师有偏好时间
            if preferred:
                # 构建一个包含星期几和时间槽的时间键
                time_key = (assignment['day_of_week'], assignment['time_slot'])
                # 如果时间键在教师的偏好时间列表中，增加得分 2
                if time_key in preferred:
                    score += 2
        # 返回得分
        return score
    
    # 定义一个静态方法，用于优化优先课程安排
    @staticmethod
    def optimize_priority_scheduling(individual, algorithm):
        # 初始化得分为 0
        score = 0
        # 遍历个体中的每个课程安排
        for assignment in individual:
            # 通过课程代码从算法的课程查找表中获取课程信息
            course = algorithm.course_lookup.get(assignment['course_code'], {})
            # 累加课程的调度优先级得分
            score += course.get('scheduling_priority', 1)
        # 返回得分乘以 3
        return score * 3

    # 定义一个静态方法，用于优化体育课后尽量不排课
    @staticmethod
    def optimize_post_pe_class(individual):
        """体育课后尽量不排课"""
        # 初始化惩罚分为 0
        penalty = 0
        # 筛选出所有体育课程的安排
        pe_assignments = [a for a in individual if "体育" in a.get('course_name', '')]
        
        # 遍历每个体育课程的安排
        for pe in pe_assignments:
            # 获取体育课程的下一个时间槽
            next_slot = pe['time_slot'] + 1
            # 检查是否有课程安排在体育课程的下一个时间槽，且星期几和教学班级相同
            if any(a['time_slot'] == next_slot and 
                   a['day_of_week'] == pe['day_of_week'] and
                   a['teaching_class_code'] == pe['teaching_class_code']
                   for a in individual):
                # 如果有，增加惩罚分 8
                penalty += 8
        # 返回负的惩罚分，表示惩罚
        return -penalty  # 返回负分表示惩罚

    # 定义一个静态方法，用于优化体育课尽量安排在下午
    @staticmethod
    def optimize_pe_class_time(individual):
        """体育课尽量安排在下午(假设 5 - 8 节为下午)"""
        # 初始化惩罚分为 0
        penalty = 0
        # 筛选出所有体育课程的安排
        pe_assignments = [a for a in individual if "体育" in a.get('course_name', '')]
        
        # 遍历每个体育课程的安排
        for assignment in pe_assignments:
            # 如果体育课程安排在上午
            if assignment['time_slot'] < 5:  # 上午
                # 增加惩罚分 10
                penalty += 10
        # 返回负的惩罚分，表示惩罚
        return -penalty  # 返回负分表示惩罚

    # 定义一个静态方法，用于优化院系教室优先
    @staticmethod
    def optimize_department_room_priority(individual, algorithm):
        """院系教室优先"""
        # 初始化惩罚分为 0
        penalty = 0
        # 遍历个体中的每个课程安排
        for assignment in individual:
            # 通过课程代码从算法的课程查找表中获取课程信息
            course = algorithm.course_lookup.get(assignment['course_code'], {})
            # 通过教室代码从算法的教室查找表中获取教室信息
            classroom = algorithm.classroom_lookup.get(assignment['classroom_code'], {})
            #