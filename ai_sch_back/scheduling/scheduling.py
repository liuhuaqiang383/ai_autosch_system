import sys
import random
import pandas as pd
import mysql.connector
from deap import base, creator, tools, algorithms
import numpy as np

from .constraints001 import HardConstraints, SoftConstraints


class SchedulingAlgorithm:
    def __init__(self):
        # 初始化课程数据列表
        self.course_data = []
        # 初始化教室数据列表
        self.classroom_data = []
        # 初始化教师数据列表
        self.teacher_data = []
        # 新增: 存储班级信息
        self.class_data = []
        # 新增：存储教学班组成信息
        self.composition_data = []
        # 新增：记录无法安排的任务
        self.failed_tasks = []
        # 定义数据库连接配置
        self.db_config = {
            'user': 'root',
            'password': '123456',
            'host': 'localhost',
            'database': '111'
        }
        # 定义基因结构字段顺序
        self.GENE_FIELDS = [
            'task_id', 'semester', 'course_code', 'course_name', 'teacher_code',
            'teacher_name', 'teaching_class_code', 'teaching_class_name',
            'classroom_code', 'classroom_name', 'day_of_week', 'start_section',
            'end_section', 'week_list', 'is_fixed', 'time_slot', 'consecutive_periods'
        ]
        # 更新后的时间槽定义，包含节次信息
        self.time_slots = [
            {
                'day_of_week': day,
                'period': slot['period'],
                'time_range': slot['time_range'],
                'slot_id': slot['slot_id'],
                'start_section': slot['start_section'],
                'end_section': slot['end_section']
            }
            for day in range(1, 6)  # 周一到周五
            for slot in [
                {'period': '上午', 'time_range': '08:00-09:35', 'slot_id': 1, 'start_section': 1, 'end_section': 2},
                {'period': '上午', 'time_range': '09:50-11:25', 'slot_id': 2, 'start_section': 3, 'end_section': 4},
                {'period': '下午', 'time_range': '13:30-15:05', 'slot_id': 3, 'start_section': 5, 'end_section': 6},
                {'period': '下午', 'time_range': '15:20-16:55', 'slot_id': 4, 'start_section': 7, 'end_section': 8}
            ]
        ]
        
        # 添加任务ID（可根据实际情况设置）
        self.current_task_id = 1  # 或从数据库获取最新任务ID
    
    def get_db_connection(self):
        # 建立数据库连接并返回连接对象
        return mysql.connector.connect(**self.db_config)

    def load_data(self):
        # 获取数据库连接
        conn = self.get_db_connection()
        try:
            # 先处理教学班与班级的对应关系
            cursor = conn.cursor()
            # 解析scheduling_task表中的class_composition字段，获取班级代码
            cursor.execute("""
                INSERT INTO teaching_class_composition (teaching_class_code, class_code)
                SELECT DISTINCT st.teaching_class_code, ci.class_code
                FROM scheduling_task st
                JOIN class_info ci ON FIND_IN_SET(ci.class_name, st.class_composition)
                WHERE NOT EXISTS (
                    SELECT 1 FROM teaching_class_composition 
                    WHERE teaching_class_code = st.teaching_class_code
                    AND class_code = ci.class_code
                )
                AND ci.class_code IS NOT NULL
            """)
            conn.commit()
            
            # 从scheduling_task表中读取有效teacher_code的数据到DataFrame
            task_df = pd.read_sql("""
                SELECT st.* 
                FROM scheduling_task st
                JOIN teacher_info ti ON st.teacher_code = ti.teacher_code
                WHERE st.teacher_code IS NOT NULL AND st.teacher_code != ''
            """, conn)
            
            if task_df.empty:
                raise ValueError("scheduling_task表中没有有效的teacher_code记录")
            # 从classroom_info表中读取is_enabled为1的数据到DataFrame
            classroom_df = pd.read_sql("SELECT * FROM classroom_info WHERE is_enabled=1", conn)
            # 从teacher_info表中读取所有数据到DataFrame
            teacher_df = pd.read_sql("SELECT * FROM teacher_info", conn)
            # 新增: 读取班级信息
            class_df = pd.read_sql("SELECT * FROM class_info", conn)
            # 新增: 读取教学班组成信息
            composition_df = pd.read_sql("SELECT * FROM teaching_class_composition", conn)

            # 将课程数据中classroom_type列的缺失值填充为'普通教室'
            task_df['classroom_type'] = task_df['classroom_type'].fillna('普通教室')

            # 将课程数据转换为字典列表
            self.course_data = task_df.to_dict('records')
            # 将教室数据转换为字典列表
            self.classroom_data = classroom_df.to_dict('records')
            # 将教师数据转换为字典列表
            self.teacher_data = teacher_df.to_dict('records')
            # 新增: 将班级数据转换为字典列表
            self.class_data = class_df.to_dict('records')
            # 新增: 将教学班组成数据转换为字典列表
            self.composition_data = composition_df.to_dict('records')

            # 构建查找表
            self._build_lookup_tables()
            # 数据验证
            if not self.course_data:
                raise ValueError("未加载到课程数据")
            if not self.classroom_data:
                raise ValueError("未加载到教室数据")
            if not self.teacher_data:
                raise ValueError("未加载到教师数据")
            if not self.class_data: # 新增验证
                print("警告: 未加载到班级数据，固定教室约束可能无法正常工作") # 改为警告，因为可能没有固定教室需求
                
            print("数据验证通过")

            
            # 打印数据加载完成信息
            print(f"数据加载完成：{len(self.course_data)}门课程，{len(self.classroom_data)}间教室")
        except Exception as e:
            # 打印数据加载失败信息
            print(f"数据加载失败: {str(e)}")
            # 抛出异常
            raise
        finally:
            # 关闭数据库连接
            conn.close()

    def _build_lookup_tables(self):
        # 构建课程代码到课程数据的查找表
        self.course_lookup = {c['course_code']: c for c in self.course_data}
        # 构建教室代码到教室数据的查找表
        self.classroom_lookup = {r['classroom_code']: r for r in self.classroom_data}
        # 构建教师代码到教师数据的查找表
        self.teacher_lookup = {t['teacher_code']: t for t in self.teacher_data}
        # 新增: 构建班级代码到班级数据的查找表
        self.class_lookup = {c['class_code']: c for c in self.class_data}
        # 新增: 构建教学班代码到班级代码列表的映射
        self.tcc_to_classes = {}
        for comp in self.composition_data:
            tcc = comp['teaching_class_code']
            cc = comp['class_code']
            if tcc not in self.tcc_to_classes:
                self.tcc_to_classes[tcc] = []
            # 只有当班级代码实际存在于 class_lookup 中时才添加，防止悬空引用
            if cc in self.class_lookup:
                 self.tcc_to_classes[tcc].append(cc)
            else:
                 print(f"警告: _build_lookup_tables - 教学班组成中的班级代码 '{cc}' 在 class_info 中未找到 (教学班: {tcc})。")

        # 初始化按教室类型分类的教室字典
        self.classrooms_by_type = {}
        for room in self.classroom_data:
            # 优先使用 'classroom_type'，如果为 None 或空字符串，则视为 '未知类型' 或其他默认值
            room_type_val = room.get('classroom_type')
            if not room_type_val:
                room_type_val = '未知类型' # 或者 '普通教室'，根据业务逻辑

            if room_type_val not in self.classrooms_by_type:
                # 如果教室类型不在字典中，初始化一个空列表
                self.classrooms_by_type[room_type_val] = []
            # 将教室添加到对应类型的列表中
            self.classrooms_by_type[room_type_val].append(room)

    def _select_classroom(self, course):
        """根据课程需求选择合适的教室，严格检查容量。找不到则返回 None。"""
        classroom = None
        course_code = course.get('course_code', 'Unknown') # 用于日志
        course_size = course.get('class_size')

        # 检查 course_size 是否有效数字
        try:
            if course_size is None or pd.isna(course_size):
                print(f"警告: 课程 {course_code} 人数未知 (None或NaN)，无法精确选择教室。")
                course_size = 1 # 假设至少需要1个容量，避免因人数未知而完全失败
            else:
                course_size = int(course_size)
                if course_size <= 0:
                     print(f"警告: 课程 {course_code} 人数无效 ({course_size})，假设需要容量 1。")
                     course_size = 1
        except (ValueError, TypeError):
            print(f"警告: 课程 {course_code} 人数数据类型错误 ({course_size})，无法精确选择教室。")
            course_size = 1 # 出错时假设需要1个容量

        # Helper function to check capacity
        def is_capacity_sufficient(room):
            cap = room.get('max_capacity')
            try:
                # 只有当容量是有效数字且 >= course_size 时才认为足够
                return cap is not None and not pd.isna(cap) and int(cap) >= course_size
            except (ValueError, TypeError):
                return False # 类型错误视为容量不足

        # Helper function to check type compatibility
        def is_type_compatible(room, type_needed):
            actual_type = room.get('classroom_type')
            if not actual_type: # None 或空字符串
                 actual_type = '未知类型'
            # 类型匹配: 实际类型 == 需要类型，或者实际类型未知
            return actual_type == type_needed or actual_type == '未知类型'

        # --- 查找逻辑开始 ---

        # 1. 检查是否有指定的固定教室 (最高优先级)
        specified_classroom_code = course.get('specified_classroom')
        if specified_classroom_code:
            classroom = self.classroom_lookup.get(specified_classroom_code)
            if classroom and is_capacity_sufficient(classroom):
                specified_room_type_needed = course.get('classroom_type') or '普通教室'
                if is_type_compatible(classroom, specified_room_type_needed):
                     return classroom # 指定教室满足所有要求
                else:
                     # 指定教室类型不符，继续寻找其他教室
                     print(f"信息: 课程 {course_code} 指定教室 {specified_classroom_code} 类型不符 (需要 {specified_room_type_needed}, 实际 {classroom.get('classroom_type')})，继续寻找。")
            elif classroom:
                 # 指定教室容量不足
                 print(f"信息: 课程 {course_code} 指定教室 {specified_classroom_code} 容量不足或未知 (需要 {course_size}，实际 {classroom.get('max_capacity')})，继续寻找。")
            else:
                 # 指定教室代码无效
                 print(f"信息: 课程 {course_code} 指定教室 {specified_classroom_code} 在教室列表中不存在，继续寻找。")
            # 如果指定教室检查失败，不立即返回，而是继续按类型查找

        # 2. 按课程指定的类型查找 (或普通教室)
        room_type_needed = course.get('classroom_type') or '普通教室'
        candidates = []

        # 2a. 严格查找所需类型 T 或 未知类型
        if room_type_needed in self.classrooms_by_type:
             candidates.extend([r for r in self.classrooms_by_type[room_type_needed] if is_capacity_sufficient(r)])
        if '未知类型' in self.classrooms_by_type and room_type_needed != '未知类型': # 避免重复添加未知类型
             candidates.extend([r for r in self.classrooms_by_type['未知类型'] if is_capacity_sufficient(r) and is_type_compatible(r, room_type_needed)]) # 未知类型也要能兼容所需类型

        # 如果找到了符合类型(或未知类型)且容量足够的教室
        if candidates:
             selected_room = random.choice(candidates)
             # print(f"信息: 课程 {course_code} 找到类型匹配 ({room_type_needed} 或 未知) 且容量足够的教室: {selected_room.get('classroom_code')}")
             return selected_room

        # 3. 如果严格按类型找不到，并且需要的不是普通教室，则尝试普通教室
        if room_type_needed != '普通教室':
             print(f"信息: 课程 {course_code} 未找到类型 '{room_type_needed}' 或 '未知类型' 且容量足够的教室，尝试普通教室。")
             if '普通教室' in self.classrooms_by_type:
                  candidates = [r for r in self.classrooms_by_type['普通教室'] if is_capacity_sufficient(r)]
                  if candidates:
                       selected_room = random.choice(candidates)
                       # print(f"信息: 课程 {course_code} 降级选择普通教室: {selected_room.get('classroom_code')}")
                       return selected_room

        # 4. 如果连普通教室都找不到 (或者一开始就需要普通教室但找不到)，作为最后手段，查找任何容量足够的教室
        print(f"警告: 课程 {course_code} 未找到类型匹配或普通教室，将选择任何容量足够的教室 (类型要求被忽略)。")
        final_candidates = [r for r in self.classroom_data if is_capacity_sufficient(r)]

        if final_candidates:
            selected_room = random.choice(final_candidates)
            print(f"警告: 课程 {course_code} 最终忽略类型选择了教室 {selected_room.get('classroom_code')} (类型: {selected_room.get('classroom_type', '未知')})。")
            return selected_room
        else:
            # 找不到任何满足容量要求的教室
            print(f"错误: 无法为课程 {course_code} (需要容量={course_size}) 找到任何容量足够的教室。")
            return None # 返回 None 表示无法选择

        
    def generate_gene(self):
        """生成符合数据库结构的基因，如果找不到教室则返回无效基因并记录。"""
        MAX_RETRIES = 10 # 避免无限重试
        for _ in range(MAX_RETRIES):
            try:
                if not self.course_data:
                    return ( # 返回无效基因结构
                        self.current_task_id, '', '', '', '', '', '', '',
                        None, None, 1, 1, 1, '1', 0, '', 1
                    )

                course = random.choice(self.course_data)
                classroom = self._select_classroom(course)

                # 如果找不到合适的教室
                if classroom is None:
                    fail_reason = f"No suitable classroom found (type: {course.get('classroom_type') or '普通教室'}, capacity needed: {course.get('class_size')})"
                    # 避免重复记录相同的失败任务 (基于 teaching_class_code 可能更唯一)
                    tcc = course.get('teaching_class_code')
                    if tcc and not any(ft['course'].get('teaching_class_code') == tcc for ft in self.failed_tasks):
                         self.failed_tasks.append({'course': course, 'reason': fail_reason})
                         print(f"记录失败任务: {tcc} - {fail_reason}")
                    elif not tcc:
                         print(f"警告: 尝试记录失败任务，但 course 缺少 teaching_class_code: {course.get('course_code')}")

                    # 生成一个标记无效的基因 (classroom_code=None)
                    # print(f"警告: 无法为课程 {course.get('course_code')} 选择教室，生成无效基因。") # 减少冗余输出
                    time_slot = random.choice(self.time_slots)
                    consecutive_periods = course.get('consecutive_periods', 1)
                    if not isinstance(consecutive_periods, int) or consecutive_periods < 1: consecutive_periods = 1
                    end_section = time_slot['start_section'] + consecutive_periods - 1
                    return (
                        self.current_task_id, course.get('semester',''), course.get('course_code',''),
                        course.get('course_name',''), course.get('teacher_code',''), course.get('teacher_name',''),
                        course.get('teaching_class_code',''), course.get('teaching_class_name',''),
                        None, None, # 标记教室无效
                        time_slot['day_of_week'], time_slot['start_section'],
                        end_section, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16',
                        0, time_slot['time_range'], consecutive_periods
                    )

                # 成功选择教室，生成正常基因
                # -- 修改时间选择：不再完全随机 --
                # 创建一个包含所有时间槽的列表副本并打乱
                available_slots = list(self.time_slots)
                random.shuffle(available_slots)

                # 尝试找到第一个（目前仅随机选择第一个，未检查冲突）
                time_slot = available_slots[0] # TODO: 在这里或单独函数中实现冲突检查逻辑
                # -------------------------------

                consecutive_periods = course.get('consecutive_periods', 1)
                if not isinstance(consecutive_periods, int) or consecutive_periods < 1:
                    consecutive_periods = 1
                end_section = time_slot['start_section'] + consecutive_periods - 1

                return (
                    self.current_task_id, course.get('semester',''), course.get('course_code',''),
                    course.get('course_name',''), course.get('teacher_code',''), course.get('teacher_name',''),
                    course.get('teaching_class_code',''), course.get('teaching_class_name',''),
                    classroom['classroom_code'], classroom.get('classroom_name',''), # 使用 .get 以防 classroom_name 也可能缺失
                    time_slot['day_of_week'], time_slot['start_section'],
                    end_section, '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16',
                    0, time_slot['time_range'], consecutive_periods
                )

            except IndexError:
                 print("错误: generate_gene - random.choice on empty list.")
                 # 返回无效基因
                 return (
                      self.current_task_id, '', '', '', '', '', '', '',
                      None, None, 1, 1, 1, '1', 0, '', 1
                 )
            except Exception as e:
                print(f"生成基因时发生意外错误: {str(e)}")
                # 返回无效基因
                return (
                    self.current_task_id, '', '', '', '', '', '', '',
                    None, None, 1, 1, 1, '1', 0, '', 1
                )

        print(f"错误: generate_gene 达到最大重试次数 {MAX_RETRIES}，无法选择课程并生成有效基因。")
        # 返回无效基因
        return (
            self.current_task_id, '', '', '', '', '', '', '',
            None, None, 1, 1, 1, '1', 0, '', 1
        )
            
    def evaluate(self, individual):
        """评估函数，忽略无效基因（教室代码为None）"""
        valid_schedule = []
        original_indices = [] # 跟踪有效基因在原始 individual 中的位置
        try: # 包裹基因处理，防止索引错误
            classroom_code_index = self.GENE_FIELDS.index('classroom_code')
            course_code_index = self.GENE_FIELDS.index('course_code') # 用于日志

            for i, gene in enumerate(individual):
                # 增加对 gene 结构和长度的检查
                if not isinstance(gene, (tuple, list)) or len(gene) != len(self.GENE_FIELDS):
                    print(f"警告: 评估时发现无效基因结构或长度: {gene}")
                    continue # 跳过格式错误的基因

                # 检查基因是否标记为无效 (教室代码为 None)
                if gene[classroom_code_index] is None:
                    # course_code = gene[course_code_index] if course_code_index < len(gene) else 'Unknown'
                    # print(f"信息: 评估时跳过无效基因 (课程: {course_code})") # 减少冗余输出
                    continue # 跳过这个无效基因

                # 转换为字典格式
                gene_dict = dict(zip(self.GENE_FIELDS, gene))
                valid_schedule.append(gene_dict)
                original_indices.append(i) # 记录原始索引

        except IndexError:
             print(f"错误: evaluate 处理基因时发生索引错误。Individual 示例: {individual[0] if individual else 'Empty'}")
             return (0,)
        except Exception as e:
             print(f"错误: evaluate 预处理基因时出错: {str(e)}")
             return (0,)


        # 如果所有基因都无效或处理出错，则适应度为0
        if not valid_schedule:
             # print("警告: 个体中所有基因都无效。") # 减少冗余输出
             return (0,)

        try:
            # 硬约束检查 (只对有效的部分进行)
            if not HardConstraints.check_all(valid_schedule, self):
                # print("硬约束检查失败 (基于有效基因)") # 已在 constraints 中打印详细信息
                return (0,)

            # 软约束评分 (只对有效的部分进行)
            soft_score = SoftConstraints.optimize_all(valid_schedule, self)
            # print(f"软约束评分 (基于有效基因): {soft_score}") # 减少冗余输出
            return (soft_score,)

        except Exception as e:
            print(f"评估有效基因时出错: {str(e)}")
            return (0,)

    def _check_slot_availability(self, gene_to_check, new_slot_info, individual, index_to_ignore):
        """检查将 gene_to_check 安排在新时间 new_slot_info 是否与 individual 中其他基因冲突"""
        teacher_code = gene_to_check['teacher_code']
        classroom_code = gene_to_check['classroom_code']
        teaching_class_code = gene_to_check['teaching_class_code']
        consecutive_periods = gene_to_check['consecutive_periods']

        new_day = new_slot_info['day_of_week']
        new_start_section = new_slot_info['start_section']
        # 确保结束节次计算正确
        try:
             periods = int(consecutive_periods)
             if periods < 1: periods = 1
        except (ValueError, TypeError):
             periods = 1
        new_end_section = new_start_section + periods - 1

        # 获取此教学班对应的行政班级代码列表
        admin_class_codes = self.tcc_to_classes.get(teaching_class_code, [])
        if not admin_class_codes:
             # 如果教学班没有对应的行政班，无法检查班级冲突，可能需要警告或跳过检查
             # print(f"警告: 教学班 {teaching_class_code} 没有找到对应的行政班级，无法检查班级冲突。")
             pass # 暂时允许

        for i, other_gene_tuple in enumerate(individual):
            # 跳过自身
            if i == index_to_ignore:
                continue

            # 跳过无效基因
            classroom_code_index = self.GENE_FIELDS.index('classroom_code')
            if other_gene_tuple[classroom_code_index] is None:
                continue

            # 将 tuple 转换为 dict
            try:
                 other_gene = dict(zip(self.GENE_FIELDS, other_gene_tuple))
            except IndexError:
                 print(f"警告: _check_slot_availability 遇到结构错误的 other_gene tuple: {other_gene_tuple}")
                 continue

            other_day = other_gene['day_of_week']
            other_start = other_gene['start_section']
            other_end = other_gene['end_section']

            # 检查星期是否相同
            if new_day != other_day:
                continue

            # 检查时间段是否有重叠 (区间重叠检查)
            # 如果 [new_start, new_end] 和 [other_start, other_end] 重叠
            if max(new_start_section, other_start) <= min(new_end_section, other_end):
                # 检查教师冲突
                if teacher_code and teacher_code == other_gene['teacher_code']:
                    # print(f"Debug Mutate Conflict: Teacher {teacher_code} at Day {new_day}, Sections {new_start_section}-{new_end_section}")
                    return False # 教师冲突

                # 检查教室冲突
                if classroom_code and classroom_code == other_gene['classroom_code']:
                    # print(f"Debug Mutate Conflict: Classroom {classroom_code} at Day {new_day}, Sections {new_start_section}-{new_end_section}")
                    return False # 教室冲突

                # 检查班级冲突
                other_tcc = other_gene['teaching_class_code']
                other_admin_classes = self.tcc_to_classes.get(other_tcc, [])
                # 如果两个教学班有共同的行政班级，则它们不能在同一时间上课
                if admin_class_codes and other_admin_classes and any(cc in other_admin_classes for cc in admin_class_codes):
                    # print(f"Debug Mutate Conflict: Class overlap for TCC {teaching_class_code} and {other_tcc} at Day {new_day}, Sections {new_start_section}-{new_end_section}")
                    return False # 班级冲突

        return True # 没有发现冲突

    def get_next_time_slot(self, current_slot, offset=1):
        """获取下一个时间槽"""
        try:
            # 根据时间范围查找当前时间槽的索引
            current_slots = [slot for slot in self.time_slots if slot['time_range'] == current_slot]
            if not current_slots:
                return None
                
            current_slot_obj = current_slots[0]
            current_day = current_slot_obj['day_of_week']
            current_slot_id = current_slot_obj['slot_id']
            
            # 计算下一个时间槽的索引
            next_slot_id = current_slot_id + offset
            
            # 如果下一个时间槽超出了当天的范围，返回None
            if next_slot_id > 4:  # 假设每天有4个时间槽
                return None
                
            # 查找下一个时间槽
            next_slots = [slot for slot in self.time_slots 
                         if slot['day_of_week'] == current_day and slot['slot_id'] == next_slot_id]
            
            if next_slots:
                return next_slots[0]['time_range']
            return None
        except Exception as e:
            print(f"获取下一个时间槽失败: {str(e)}")
            return None
            
    def custom_mutate(self, individual):
        """自定义变异函数，尝试为随机选择的基因寻找一个无冲突的时间。"""
        try:
            if len(individual) == 0:
                return individual,

            # 1. 随机选择一个个体中的基因进行变异
            index = random.randint(0, len(individual) - 1)
            gene_tuple_to_mutate = individual[index]

            # 检查所选基因是否有效
            classroom_code_index = self.GENE_FIELDS.index('classroom_code')
            if gene_tuple_to_mutate[classroom_code_index] is None:
                 # print(f"Debug Mutate: 跳过对无效基因 {index} 的变异尝试。") # 调试日志
                 # 对无效基因可以尝试重新生成，或者直接跳过
                 # 方案A: 尝试重新生成
                 # new_gene = self.generate_gene()
                 # if isinstance(new_gene, tuple) and len(new_gene) == len(self.GENE_FIELDS):
                 #     individual[index] = new_gene
                 # 方案B: 跳过本次变异
                 return individual,

            # 将 tuple 转换为 dict 以便传递给检查函数
            try:
                 gene_to_check = dict(zip(self.GENE_FIELDS, gene_tuple_to_mutate))
            except IndexError:
                 print(f"警告: custom_mutate 遇到结构错误的 gene tuple: {gene_tuple_to_mutate}")
                 return individual, # 保持不变

            # 2. 准备尝试新时间
            potential_slots = list(self.time_slots)
            random.shuffle(potential_slots)

            # 3. 遍历潜在的新时间槽，寻找第一个无冲突的
            for new_slot_info in potential_slots:
                # 检查这个新时间是否与当前基因的时间不同 (避免无效变异)
                if new_slot_info['day_of_week'] == gene_to_check['day_of_week'] and \
                   new_slot_info['start_section'] == gene_to_check['start_section']:
                    continue # 时间相同，尝试下一个

                # 调用辅助函数检查新时间槽的可用性
                if self._check_slot_availability(gene_to_check, new_slot_info, individual, index):
                    # 找到了一个无冲突的时间槽！
                    # 更新基因元组中的时间相关字段
                    new_gene_list = list(gene_tuple_to_mutate) # 转换为列表以便修改
                    day_index = self.GENE_FIELDS.index('day_of_week')
                    start_index = self.GENE_FIELDS.index('start_section')
                    end_index = self.GENE_FIELDS.index('end_section')
                    timeslot_str_index = self.GENE_FIELDS.index('time_slot')

                    new_day = new_slot_info['day_of_week']
                    new_start = new_slot_info['start_section']
                    # 重新计算结束节次
                    try:
                         periods = int(gene_to_check['consecutive_periods'])
                         if periods < 1: periods = 1
                    except (ValueError, TypeError): periods = 1
                    new_end = new_start + periods - 1

                    new_gene_list[day_index] = new_day
                    new_gene_list[start_index] = new_start
                    new_gene_list[end_index] = new_end
                    new_gene_list[timeslot_str_index] = new_slot_info['time_range']

                    # 将修改后的列表转回元组并更新个体
                    individual[index] = tuple(new_gene_list)
                    # print(f"Debug Mutate: 成功将基因 {index} ({gene_to_check['course_code']}) 时间变异到 Day {new_day}, Start {new_start}") # 调试日志
                    return individual, # 完成一次成功的变异

            # 4. 如果遍历完所有时间槽都找不到无冲突的
            # print(f"Debug Mutate: 未能为基因 {index} ({gene_to_check['course_code']}) 找到无冲突的新时间。") # 调试日志
            # 在这种情况下，可以选择：
            # a) 保持原样 (当前实现)
            # b) 尝试只改变教室 (更复杂)
            # c) 使用原始的完全随机替换 (可能再次引入冲突)
            # return self._fallback_mutate(individual, index) # 例如调用一个回退的随机变异
            return individual, # 保持原样

        except IndexError as ie:
             # 处理 GENE_FIELDS.index 可能引发的错误
             print(f"变异操作失败 (IndexError): {str(ie)}")
             return individual,
        except Exception as e:
            print(f"变异操作失败: {str(e)}")
            return individual,

    def run(self, population_size=50, ngen=10):
        self.failed_tasks = [] # 清空上次运行的失败记录
        try:
            self.load_data()

            # 清除之前可能创建的类
            if hasattr(creator, 'FitnessMax'):
                del creator.FitnessMax
            if hasattr(creator, 'Individual'):
                del creator.Individual

            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMax)

            toolbox = base.Toolbox()
            toolbox.register("attr_gene", self.generate_gene)
            # initRepeat 会调用 generate_gene n 次，n = len(self.course_data)
            # 如果 generate_gene 返回无效基因，它们会包含在初始个体中
            toolbox.register("individual", tools.initRepeat,
                             creator.Individual, toolbox.attr_gene,
                             n=len(self.course_data))
            toolbox.register("population", tools.initRepeat, list, toolbox.individual)
            toolbox.register("evaluate", self.evaluate) # 使用新的评估函数
            toolbox.register("mate", tools.cxTwoPoint)
            toolbox.register("mutate", self.custom_mutate) # 使用新的变异函数
            toolbox.register("select", tools.selTournament, tournsize=3)

            pop = toolbox.population(n=population_size)
            hof = tools.HallOfFame(1)
            stats = tools.Statistics(lambda ind: ind.fitness.values)
            stats.register("avg", np.mean)
            stats.register("max", np.max)

            # 检查初始种群 (第一个个体的第一个基因)
            if pop and pop[0]:
                 print("\n检查初始种群中的第一个个体:")
                 print(pop[0][0])
            else:
                 print("\n警告: 初始种群为空或第一个个体为空。")

            # 评估初始种群
            print("\n评估初始种群...")
            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            if invalid_ind:
                 fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
                 for ind, fit in zip(invalid_ind, fitnesses):
                     ind.fitness.values = fit
            else:
                 print("所有初始个体已有有效适应度。")


            pop, log = algorithms.eaSimple(
                pop, toolbox, cxpb=0.7, mutpb=0.2,
                ngen=ngen, stats=stats, halloffame=hof,
                verbose=True
            )

            # 处理最优个体，过滤掉无效基因
            if hof and hof[0]:
                best_individual_raw = hof[0]
                best_schedule = []
                try:
                     classroom_code_index = self.GENE_FIELDS.index('classroom_code')
                     for gene in best_individual_raw:
                         # 再次检查基因结构和有效性
                         if isinstance(gene, (tuple, list)) and len(gene) == len(self.GENE_FIELDS) and gene[classroom_code_index] is not None:
                              best_schedule.append(dict(zip(self.GENE_FIELDS, gene)))
                         # else: 忽略无效基因
                except IndexError:
                     print("错误: 处理名人堂个体时发生索引错误。")
                     best_schedule = [] # 返回空表示失败

                # --- 新增：最终验证步骤 ---
                if best_schedule:
                    print("\n进行最终课表硬约束验证...")
                    is_final_schedule_valid = HardConstraints.check_all(best_schedule, self)
                    if is_final_schedule_valid:
                        print("\n[成功] 最终生成的课表已通过所有硬约束验证。")
                        # 可以选择在这里打印最优个体的适应度作为参考
                        best_fitness = hof[0].fitness.values[0] if hof[0].fitness.valid else 'N/A'
                        print(f"最终课表适应度 (软约束分数): {best_fitness}")
                        print("最优个体有效安排示例:", best_schedule[0])
                        # 验证成功，返回有效课表
                        # return best_schedule # 不再在这里返回
                    else:
                        # 这通常不应该发生，如果发生，说明 GA 流程或约束检查可能有深层问题
                        print("\n[严重警告] 最终生成的课表未能通过硬约束验证！但仍将尝试保存。")
                        # 不再返回空列表，继续执行
                        # return [] # 注释掉或删除
                else:
                     print("\n警告: 最优个体中没有找到有效的基因安排，无法进行最终验证。")
                     # 即使没有有效安排，也继续返回空列表，由 save_to_database 处理
                     # return []
                # --- 结束最终验证步骤 ---

                return best_schedule # 返回处理过的有效安排列表 (无论验证是否通过)
            else:
                 print("\n错误: 算法未能产生任何名人堂个体。")
                 return []


        except Exception as e:
            print(f"算法运行失败: {str(e)}")
            # 可以在这里记录更详细的错误日志
            raise # 重新抛出异常，让上层 (view) 知道失败了

    def save_to_database(self, schedule):
        # 如果 schedule 为空，则不执行任何数据库操作
        if not schedule:
             print("信息: 没有有效的排课结果需要保存到数据库。")
             return

        conn = self.get_db_connection()
        cursor = conn.cursor()
        try:
            # 清空表之前确认 schedule 不为空
            cursor.execute("TRUNCATE TABLE scheduling_result")

            sql = """
            INSERT INTO scheduling_result (
                task_id, semester, course_code, course_name, teacher_code,
                teacher_name, teaching_class_code, teaching_class_name,
                classroom_code, classroom_name, day_of_week, start_section,
                end_section, week_list, is_fixed
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            saved_count = 0
            for assignment in schedule:
                 # 对每个字段使用 .get 提供默认值，防止 KeyError
                 teacher_code = assignment.get('teacher_code')
                 course_code = assignment.get('course_code')
                 classroom_code = assignment.get('classroom_code') # 这个理论上不应为 None，因为 run 已过滤

                 # 基本验证 (可以根据需要添加更多)
                 if not teacher_code or not course_code or not classroom_code:
                      print(f"警告: save_to_database 跳过无效记录 (缺少关键代码): {assignment}")
                      continue

                 # 确保外键列的值有效 (可选，增加数据库查询开销)
                 # if not self.teacher_lookup.get(teacher_code):
                 #     print(f"警告: save_to_database 发现无效 teacher_code: {teacher_code}")
                 #     continue
                 # if not self.course_lookup.get(course_code): # course_lookup 是基于 task 表的，不代表 course_info
                 #     # 需要查询 course_info
                 #     pass
                 # if not self.classroom_lookup.get(classroom_code):
                 #     print(f"警告: save_to_database 发现无效 classroom_code: {classroom_code}")
                 #     continue

                 # 准备数据，确保类型正确
                 try:
                     task_id = int(assignment.get('task_id', self.current_task_id))
                     day_of_week = int(assignment.get('day_of_week', 1))
                     start_section = int(assignment.get('start_section', 1))
                     end_section = int(assignment.get('end_section', 2))
                     is_fixed = int(assignment.get('is_fixed', 0))
                 except (ValueError, TypeError) as e:
                      print(f"警告: save_to_database 跳过类型转换错误的记录: {assignment} - {e}")
                      continue

                 # 获取其他字段值，提供默认空字符串
                 semester = assignment.get('semester', '')
                 course_name = assignment.get('course_name', '')
                 teacher_name = assignment.get('teacher_name', '')
                 teaching_class_code = assignment.get('teaching_class_code', '')
                 teaching_class_name = assignment.get('teaching_class_name', '')
                 classroom_name = assignment.get('classroom_name', '')
                 week_list = assignment.get('week_list', '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16')

                 try:
                      cursor.execute(sql, (
                          task_id,
                          semester,
                          course_code,
                          course_name,
                          teacher_code,
                          teacher_name,
                          teaching_class_code,
                          teaching_class_name,
                          classroom_code,
                          classroom_name,
                          day_of_week,
                          start_section,
                          end_section,
                          week_list,
                          is_fixed
                      ))
                      saved_count += 1
                 except mysql.connector.Error as db_err:
                      print(f"数据库插入错误: {db_err} - 跳过记录: {assignment}")
                      conn.rollback() # 回滚当前失败的事务
                      # 可以选择继续尝试下一条记录

            conn.commit() # 提交所有成功的插入
            print(f"成功保存 {saved_count} / {len(schedule)} 条有效排课结果")

        except mysql.connector.Error as e:
             # 处理 TRUNCATE 或连接错误
             print(f"数据库操作失败 (非插入错误): {str(e)}")
             conn.rollback()
             # raise # 可以重新抛出，让上层知道保存失败
        except Exception as e:
             # 处理其他意外错误
             print(f"保存到数据库时发生未知错误: {str(e)}")
             conn.rollback()
             # raise
        finally:
             if conn.is_connected():
                  conn.close()

    def export_to_excel(self, schedule, filename="排课结果.xlsx"):
        """将排课结果导出到Excel文件"""
        if not schedule:
            print("信息: 没有有效的排课结果可导出到 Excel。")
            return None

        try:
            # 将排课数据转换为DataFrame
            df = pd.DataFrame(schedule)

            # 添加时间范围列 (基于 start_section 重新查找 time_range)
            # 创建节次到时间范围的映射
            section_to_range = {slot['start_section']: slot['time_range'] for slot in self.time_slots}
            df['time_range'] = df['start_section'].apply(lambda x: section_to_range.get(x, ''))

            # 重新排列列顺序
            columns = [
                'semester', 'course_code', 'course_name', 'teacher_code', 'teacher_name',
                'teaching_class_code', 'teaching_class_name', 'classroom_code', 'classroom_name',
                'day_of_week', 'start_section', 'end_section', 'time_range', 'consecutive_periods', 'week_list', 'is_fixed'
            ]
            # 仅保留 DataFrame 中存在的列
            columns_to_export = [col for col in columns if col in df.columns]
            df = df[columns_to_export]

            # 保存到Excel
            # 检查 HOME 环境变量是否存在
            home_dir = os.path.expanduser("~")
            if not os.path.exists(home_dir):
                print(f"警告: 无法找到用户主目录 '{home_dir}'，将尝试保存到当前工作目录。")
                desktop_path = os.getcwd() # 保存到当前目录
            else:
                 desktop_path = os.path.join(home_dir, "Desktop")
                 # 检查桌面路径是否存在，如果不存在，也保存到主目录
                 if not os.path.exists(desktop_path):
                      print(f"警告: 桌面路径 '{desktop_path}' 不存在，将尝试保存到用户主目录 '{home_dir}'")
                      desktop_path = home_dir

            filepath = os.path.join(desktop_path, filename)
            df.to_excel(filepath, index=False)
            print(f"排课结果已保存到: {filepath}")
            return filepath
        except ImportError:
             print("错误: 导出 Excel 需要 `openpyxl` 库。请运行 `pip install openpyxl` 安装。")
             return None
        except Exception as e:
            print(f"导出Excel失败: {str(e)}")
            # raise # 不向上抛出，避免中断流程
            return None

if __name__ == "__main__":
    import os
    scheduler = SchedulingAlgorithm()
    try:
        best_schedule = scheduler.run(population_size=50, ngen=10)
        if best_schedule:
             scheduler.save_to_database(best_schedule)
             # excel_path = scheduler.export_to_excel(best_schedule)
             # if excel_path:
             #     print(f"排课完成，结果已保存到数据库和Excel文件: {excel_path}")
             # else:
             #     print("排课完成，结果已保存到数据库，但导出 Excel 失败。")
        else:
             print("算法运行完成，但未能生成有效的排课结果。")

        # 打印失败的任务
        if scheduler.failed_tasks:
             print("\n以下任务因无法找到合适的教室而未能安排：")
             for failed in scheduler.failed_tasks:
                  course = failed.get('course', {})
                  print(f"  - 课程代码: {course.get('course_code')}, 教学班: {course.get('teaching_class_code')}, 原因: {failed.get('reason')}")

    except Exception as e:
        print(f"排课主流程出错: {str(e)}")
