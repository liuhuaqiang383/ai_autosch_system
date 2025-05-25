import request from '@/utils/request'
import { getClassrooms } from '@/api/classroom'
import { getSchedulingResults } from '@/api/scheduling'
import { getBuildings } from '@/api/building'

/**
 * 获取教室利用率统计数据 - 基于现有API的数据处理
 * @param {Object} params - 查询参数 { time_period, classroom_type, building_id }
 * @returns {Promise}
 */
export function getClassroomUtilization(params) {
  // 使用现有的API获取教室和排课结果数据，在前端进行统计处理
  return new Promise((resolve, reject) => {
    Promise.all([
      getClassrooms({ _fetchAll: true, building: params.building_id }),
      getSchedulingResults({ _fetchAll: true })
    ]).then(([classroomsResponse, schedulingResponse]) => {
      const classrooms = classroomsResponse.results || [];
      const schedulingResults = schedulingResponse.results || [];
      
      // 根据时间范围筛选排课结果
      let filteredResults = schedulingResults;
      
      if (params.time_period === 'week') {
        // 本周筛选逻辑
        const now = new Date();
        const currentWeek = Math.ceil((now - new Date(now.getFullYear(), 0, 1)) / (7 * 24 * 60 * 60 * 1000));
        
        filteredResults = schedulingResults.filter(result => {
          if (!result.week_list) return true;
          if (typeof result.week_list === 'string') {
            const weeks = result.week_list.split(',').map(w => parseInt(w.trim()));
            return weeks.includes(currentWeek);
          }
          return true;
        });
      }
      
      // 按教室类型分组
      const typeGroups = {};
      classrooms.forEach(classroom => {
        const type = classroom.classroom_type || '未分类';
        if (!typeGroups[type]) {
          typeGroups[type] = {
            classroom_type: type,
            count: 0,
            used_classroom_codes: new Set() // 使用Set来存储已使用的教室编号，避免重复计算
          };
        }
        typeGroups[type].count++;
      });
      
      // 统计使用中的教室
      filteredResults.forEach(result => {
        if (result.classroom_code) {
          const classroom = classrooms.find(c => c.classroom_code === result.classroom_code);
          if (classroom) {
            const type = classroom.classroom_type || '未分类';
            if (typeGroups[type]) {
              // 将教室编号添加到Set中，自动去重
              typeGroups[type].used_classroom_codes.add(result.classroom_code);
            }
          }
        }
      });
      
      // 计算利用率
      const results = Object.values(typeGroups).map(group => {
        const usedCount = group.used_classroom_codes.size; // 获取唯一教室数量
        return {
          classroom_type: group.classroom_type,
          count: group.count,
          utilization_rate: group.count > 0 ? Math.round((usedCount / group.count) * 100) : 0
        };
      });
      
      console.log('教室类型利用率统计 - 总排课结果:', schedulingResults.length, '筛选后结果:', filteredResults.length);
      
      resolve({ results });
    }).catch(error => {
      console.error('获取教室类型利用率数据出错:', error);
      reject(error);
    });
  });
}

/**
 * 获取总体教室使用情况概览 - 基于现有API的数据处理
 * @param {Object} params - 查询参数 { timeRange }
 * @returns {Promise}
 */
export function getClassroomOverview(params = {}) {
  // 使用现有的API获取教室和排课结果数据，在前端进行统计处理
  return new Promise((resolve, reject) => {
    Promise.all([
      getClassrooms({ _fetchAll: true }),
      getSchedulingResults({ _fetchAll: true }) // 添加_fetchAll标志以获取所有数据
    ]).then(([classroomsResponse, schedulingResponse]) => {
      const classrooms = classroomsResponse.results || [];
      const schedulingResults = schedulingResponse.results || [];
      
      // 计算已使用教室数量
      const usedClassroomCodes = new Set();
      
      // 根据时间范围筛选排课结果
      let filteredResults = schedulingResults;
      
      if (params.timeRange === 'week') {
        // 本周筛选逻辑
        const now = new Date();
        const currentWeek = Math.ceil((now - new Date(now.getFullYear(), 0, 1)) / (7 * 24 * 60 * 60 * 1000));
        
        filteredResults = schedulingResults.filter(result => {
          if (!result.week_list) return true;
          if (typeof result.week_list === 'string') {
            const weeks = result.week_list.split(',').map(w => parseInt(w.trim()));
            return weeks.includes(currentWeek);
          }
          return true;
        });
      }
      
      // 收集已使用的教室编号
      filteredResults.forEach(result => {
        if (result.classroom_code) {
          usedClassroomCodes.add(result.classroom_code);
        }
      });
      
      console.log('统计已使用教室数量:', usedClassroomCodes.size, '总共获取到排课结果:', schedulingResults.length);
      
      const totalClassrooms = classrooms.length;
      const usedClassrooms = usedClassroomCodes.size;
      const idleClassrooms = totalClassrooms - usedClassrooms;
      const averageUtilization = totalClassrooms > 0 ? Math.round((usedClassrooms / totalClassrooms) * 100) + '%' : '0%';
      
      resolve({
        totalClassrooms,
        usedClassrooms,
        idleClassrooms,
        averageUtilization
      });
    }).catch(error => {
      console.error('获取教室概览数据出错:', error);
      reject(error);
    });
  });
}

/**
 * 获取各时间段教室使用情况 - 基于现有API的数据处理
 * @param {Object} params - 查询参数 { date, building_id, time_period }
 * @returns {Promise}
 */
export function getClassroomTimeDistribution(params) {
  // 使用现有的API获取教室和排课结果数据，在前端进行统计处理
  return new Promise((resolve, reject) => {
    Promise.all([
      getClassrooms({ _fetchAll: true, building: params.building_id }),
      getSchedulingResults({ _fetchAll: true })
    ]).then(([classroomsResponse, schedulingResponse]) => {
      const classrooms = classroomsResponse.results || [];
      const schedulingResults = schedulingResponse.results || [];
      
      // 根据时间范围筛选排课结果
      let filteredResults = schedulingResults;
      
      if (params.time_period === 'week') {
        // 本周筛选逻辑
        const now = new Date();
        const currentWeek = Math.ceil((now - new Date(now.getFullYear(), 0, 1)) / (7 * 24 * 60 * 60 * 1000));
        
        filteredResults = schedulingResults.filter(result => {
          if (!result.week_list) return true;
          if (typeof result.week_list === 'string') {
            const weeks = result.week_list.split(',').map(w => parseInt(w.trim()));
            return weeks.includes(currentWeek);
          }
          return true;
        });
      }
      
      console.log('各时间段教室使用情况 - 总排课结果:', schedulingResults.length, '筛选后结果:', filteredResults.length);
      
      // 按时间段分组
      const timeSlots = [
        { id: 1, label: '第1节', time_slot: '8:00-8:45' },
        { id: 2, label: '第2节', time_slot: '8:55-9:40' },
        { id: 3, label: '第3节', time_slot: '10:00-10:45' },
        { id: 4, label: '第4节', time_slot: '10:55-11:40' },
        { id: 5, label: '第5节', time_slot: '14:00-14:45' },
        { id: 6, label: '第6节', time_slot: '14:55-15:40' },
        { id: 7, label: '第7节', time_slot: '16:00-16:45' },
        { id: 8, label: '第8节', time_slot: '16:55-17:40' },
        { id: 9, label: '第9节', time_slot: '19:00-19:45' },
        { id: 10, label: '第10节', time_slot: '19:55-20:40' },
        { id: 11, label: '第11节', time_slot: '20:50-21:35' },
        { id: 12, label: '第12节', time_slot: '21:45-22:30' }
      ];
      
      const totalClassrooms = classrooms.length;
      
      // 统计各时间段的教室使用情况
      const results = timeSlots.map(slot => {
        // 使用Set存储每个时间段中使用的唯一教室编号
        const weekdayUsedClassrooms = new Set();
        const weekendUsedClassrooms = new Set();
        
        // 周一至周五的使用情况
        filteredResults.forEach(result => {
          if (result.day_of_week >= 1 && result.day_of_week <= 5 && 
              result.start_section <= slot.id && result.end_section >= slot.id && 
              result.classroom_code) {
            weekdayUsedClassrooms.add(result.classroom_code);
          }
        });
        
        // 周末的使用情况
        filteredResults.forEach(result => {
          if ((result.day_of_week === 6 || result.day_of_week === 7) && 
              result.start_section <= slot.id && result.end_section >= slot.id && 
              result.classroom_code) {
            weekendUsedClassrooms.add(result.classroom_code);
          }
        });
        
        // 计算使用率 - 使用唯一教室数量
        const weekdayUtilization = totalClassrooms > 0 ? Math.min(100, Math.round((weekdayUsedClassrooms.size / totalClassrooms) * 100)) : 0;
        const weekendUtilization = totalClassrooms > 0 ? Math.min(100, Math.round((weekendUsedClassrooms.size / totalClassrooms) * 100)) : 0;
        
        return {
          time_slot: slot.label,
          weekday_utilization: weekdayUtilization,
          weekend_utilization: weekendUtilization,
          weekday_count: weekdayUsedClassrooms.size,  // 添加使用数量便于调试
          weekend_count: weekendUsedClassrooms.size   // 添加使用数量便于调试
        };
      });
      
      resolve({ results });
    }).catch(error => {
      console.error('获取各时间段教室使用情况出错:', error);
      reject(error);
    });
  });
}

/**
 * 获取教室闲置推荐 - 基于现有API的数据处理
 * @param {Object} params - 查询参数 { capacity, type, date, time_period }
 * @returns {Promise}
 */
export function getIdleClassroomRecommendation(params) {
  // 使用现有的API获取教室和排课结果数据，在前端进行处理
  return new Promise((resolve, reject) => {
    Promise.all([
      getClassrooms({ _fetchAll: true, building: params.building_id }),
      getSchedulingResults({ _fetchAll: true })
    ]).then(([classroomsResponse, schedulingResponse]) => {
      const classrooms = classroomsResponse.results || [];
      const schedulingResults = schedulingResponse.results || [];
      
      // 获取使用中的教室编号和时段
      const usedClassrooms = {};
      schedulingResults.forEach(result => {
        if (!usedClassrooms[result.classroom_code]) {
          usedClassrooms[result.classroom_code] = [];
        }
        
        // 添加使用时段
        usedClassrooms[result.classroom_code].push({
          day_of_week: result.day_of_week,
          start_section: result.start_section,
          end_section: result.end_section,
          week_list: result.week_list
        });
      });
      
      // 找出空闲教室
      const idleClassrooms = classrooms.map(classroom => {
        const usedPeriods = usedClassrooms[classroom.classroom_code] || [];
        const allDays = [1, 2, 3, 4, 5, 6, 7];
        const allSections = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
        
        // 构建空闲时段
        const availablePeriods = [];
        allDays.forEach(day => {
          const dayName = ['一', '二', '三', '四', '五', '六', '日'][day - 1];
          
          // 检查当天的空闲时段
          let availableSections = [...allSections];
          usedPeriods.forEach(period => {
            if (period.day_of_week === day) {
              // 移除已使用的时段
              for (let i = period.start_section; i <= period.end_section; i++) {
                availableSections = availableSections.filter(s => s !== i);
              }
            }
          });
          
          // 将连续的空闲时段合并
          if (availableSections.length > 0) {
            let start = availableSections[0];
            let last = start;
            
            for (let i = 1; i < availableSections.length; i++) {
              if (availableSections[i] === last + 1) {
                last = availableSections[i];
              } else {
                availablePeriods.push(`周${dayName}第${start}-${last}节`);
                start = availableSections[i];
                last = start;
              }
            }
            
            availablePeriods.push(`周${dayName}第${start}-${last}节`);
          }
        });
        
        return {
          classroom_code: classroom.classroom_code,
          classroom_name: classroom.classroom_name,
          building_name: classroom.building_name || '未知',
          capacity: classroom.max_capacity || 0,
          classroom_type: classroom.classroom_type || '未分类',
          available_periods: availablePeriods.join(', ')
        };
      });
      
      // 按照可用时段数量排序（空闲时段越多的排在前面）
      idleClassrooms.sort((a, b) => {
        const aCount = a.available_periods ? a.available_periods.split(',').length : 0;
        const bCount = b.available_periods ? b.available_periods.split(',').length : 0;
        return bCount - aCount;
      });
      
      resolve({ results: idleClassrooms });
    }).catch(error => {
      reject(error);
    });
  });
}

/**
 * 获取教学楼使用情况统计 - 基于现有API的数据处理
 * @param {Object} params - 查询参数 { time_period }
 * @returns {Promise}
 */
export function getBuildingUtilization(params = {}) {
  // 使用现有的API获取教学楼、教室和排课结果数据，在前端进行统计处理
  return new Promise((resolve, reject) => {
    Promise.all([
      getBuildings(),
      getClassrooms({ _fetchAll: true }),
      getSchedulingResults({ _fetchAll: true })
    ]).then(([buildingsResponse, classroomsResponse, schedulingResponse]) => {
      const buildings = buildingsResponse.results || [];
      const classrooms = classroomsResponse.results || [];
      const schedulingResults = schedulingResponse.results || [];
      
      // 根据时间范围筛选排课结果
      let filteredResults = schedulingResults;
      
      if (params.time_period === 'week') {
        // 本周筛选逻辑
        const now = new Date();
        const currentWeek = Math.ceil((now - new Date(now.getFullYear(), 0, 1)) / (7 * 24 * 60 * 60 * 1000));
        
        filteredResults = schedulingResults.filter(result => {
          if (!result.week_list) return true;
          if (typeof result.week_list === 'string') {
            const weeks = result.week_list.split(',').map(w => parseInt(w.trim()));
            return weeks.includes(currentWeek);
          }
          return true;
        });
      }
      
      // 创建教学楼映射
      const buildingMap = {};
      buildings.forEach(building => {
        buildingMap[building.building_code] = {
          building_code: building.building_code,
          building_name: building.building_name,
          classroom_count: 0,
          used_classrooms: new Set()
        };
      });
      
      // 统计每个教学楼的教室数量
      classrooms.forEach(classroom => {
        if (buildingMap[classroom.building]) {
          buildingMap[classroom.building].classroom_count++;
        }
      });
      
      // 统计使用中的教室
      filteredResults.forEach(result => {
        const classroom = classrooms.find(c => c.classroom_code === result.classroom_code);
        if (classroom && buildingMap[classroom.building]) {
          buildingMap[classroom.building].used_classrooms.add(result.classroom_code);
        }
      });
      
      console.log('教学楼利用率统计 - 总排课结果:', schedulingResults.length, '筛选后结果:', filteredResults.length);
      
      // 计算利用率
      const results = Object.values(buildingMap).map(building => {
        return {
          building_code: building.building_code,
          building_name: building.building_name,
          classroom_count: building.classroom_count,
          utilization_rate: building.classroom_count > 0 ? 
            Math.min(100, Math.round((building.used_classrooms.size / building.classroom_count) * 100)) : 0
        };
      });
      
      // 按利用率降序排序
      results.sort((a, b) => b.utilization_rate - a.utilization_rate);
      
      resolve({ results });
    }).catch(error => {
      console.error('获取教学楼利用率数据出错:', error);
      reject(error);
    });
  });
}

/**
 * 获取教师工作量统计数据 - 基于现有API的数据处理
 * @param {Object} params - 查询参数 { department_id, title, time_period }
 * @returns {Promise}
 */
export function getTeacherWorkload(params = {}) {
  // 使用现有的API获取教师和排课任务数据，在前端进行统计处理
  return new Promise((resolve, reject) => {
    Promise.all([
      import('@/api/teacher').then(module => module.getTeachers({ _fetchAll: true })),
      import('@/api/scheduling').then(module => module.getSchedulingTasks({ _fetchAll: true }))
    ]).then(([teachersResponse, tasksResponse]) => {
      const teachers = teachersResponse.results || [];
      const tasks = tasksResponse.results || [];
      
      // 按教师筛选排课任务
      const filteredTasks = tasks.filter(task => {
        // 如果指定了部门，过滤相关教师的任务
        if (params.department_id) {
          const teacher = teachers.find(t => t.teacher_code === task.teacher_code);
          if (!teacher || teacher.department !== params.department_id) {
            return false;
          }
        }
        return true;
      });
      
      // 按教师分组并计算工作量
      const teacherWorkloads = {};
      filteredTasks.forEach(task => {
        const teacherCode = task.teacher_code;
        if (!teacherWorkloads[teacherCode]) {
          const teacher = teachers.find(t => t.teacher_code === teacherCode);
          if (!teacher) return;
          
          teacherWorkloads[teacherCode] = {
            teacher_code: teacherCode,
            teacher_name: task.teacher_name,
            department: teacher.department,
            department_name: teacher.department_name || '',
            title: teacher.title || '未知职称',
            course_count: 0,
            total_hours: 0,
            class_count: 0,
            student_count: 0
          };
        }
        
        // 累加课程数量、学时数和学生数
        teacherWorkloads[teacherCode].course_count++;
        teacherWorkloads[teacherCode].total_hours += task.total_hours || 0;
        teacherWorkloads[teacherCode].class_count += task.class_composition ? task.class_composition.split(',').length : 0;
        teacherWorkloads[teacherCode].student_count += task.class_size || 0;
      });
      
      // 转换为数组并排序
      const results = Object.values(teacherWorkloads).sort((a, b) => b.total_hours - a.total_hours);
      
      resolve({ results });
    }).catch(error => {
      reject(error);
    });
  });
}

/**
 * 获取院系工作量统计数据 - 基于现有API的数据处理
 * @param {Object} params - 查询参数 { time_period }
 * @returns {Promise}
 */
export function getDepartmentWorkload(params = {}) {
  // 使用现有的API获取教师、部门和排课任务数据，在前端进行统计处理
  return new Promise((resolve, reject) => {
    Promise.all([
      import('@/api/teacher').then(module => module.getTeachers({ _fetchAll: true })),
      import('@/api/scheduling').then(module => module.getSchedulingTasks({ _fetchAll: true })),
      import('@/api/department').then(module => module.getDepartments({ _fetchAll: true }))
    ]).then(([teachersResponse, tasksResponse, departmentsResponse]) => {
      const teachers = teachersResponse.results || [];
      const tasks = tasksResponse.results || [];
      const departments = departmentsResponse.results || [];
      
      // 创建部门映射
      const departmentMap = {};
      departments.forEach(dept => {
        departmentMap[dept.department_code] = {
          department_code: dept.department_code,
          department_name: dept.department_name,
          teacher_count: 0,
          course_count: 0,
          total_hours: 0,
          student_count: 0
        };
      });
      
      // 统计每个部门的教师数量
      teachers.forEach(teacher => {
        if (departmentMap[teacher.department]) {
          departmentMap[teacher.department].teacher_count++;
        }
      });
      
      // 统计每个部门的排课任务
      tasks.forEach(task => {
        const teacher = teachers.find(t => t.teacher_code === task.teacher_code);
        if (!teacher || !departmentMap[teacher.department]) return;
        
        const deptCode = teacher.department;
        departmentMap[deptCode].course_count++;
        departmentMap[deptCode].total_hours += task.total_hours || 0;
        departmentMap[deptCode].student_count += task.class_size || 0;
      });
      
      // 计算平均工作量和转换为数组
      const results = Object.values(departmentMap).map(dept => {
        return {
          ...dept,
          avg_hours_per_teacher: dept.teacher_count > 0 ? +(dept.total_hours / dept.teacher_count).toFixed(1) : 0
        };
      });
      
      // 按总学时降序排序
      results.sort((a, b) => b.total_hours - a.total_hours);
      
      resolve({ results });
    }).catch(error => {
      reject(error);
    });
  });
}

/**
 * 获取职称工作量统计数据 - 基于现有API的数据处理
 * @param {Object} params - 查询参数 { department_id, time_period }
 * @returns {Promise}
 */
export function getTitleWorkload(params = {}) {
  // 使用现有的API获取教师和排课任务数据，在前端进行统计处理
  return new Promise((resolve, reject) => {
    Promise.all([
      import('@/api/teacher').then(module => module.getTeachers({ _fetchAll: true })),
      import('@/api/scheduling').then(module => module.getSchedulingTasks({ _fetchAll: true }))
    ]).then(([teachersResponse, tasksResponse]) => {
      const teachers = teachersResponse.results || [];
      const tasks = tasksResponse.results || [];
      
      // 定义职称层级
      const titleRanks = {
        '教授': 1,
        '副教授': 2,
        '讲师': 3,
        '助教': 4,
        '未知职称': 5
      };
      
      // 筛选教师
      let filteredTeachers = [...teachers];
      if (params.department_id) {
        filteredTeachers = filteredTeachers.filter(teacher => teacher.department === params.department_id);
      }
      
      // 按职称分组统计
      const titleGroups = {};
      filteredTeachers.forEach(teacher => {
        const title = teacher.title || '未知职称';
        if (!titleGroups[title]) {
          titleGroups[title] = {
            title: title,
            rank: titleRanks[title] || 99,
            teacher_count: 0,
            course_count: 0,
            total_hours: 0,
            student_count: 0
          };
        }
        titleGroups[title].teacher_count++;
      });
      
      // 统计每个职称的排课任务
      tasks.forEach(task => {
        const teacher = teachers.find(t => t.teacher_code === task.teacher_code);
        if (!teacher) return;
        
        // 如果指定了部门，跳过其他部门的教师
        if (params.department_id && teacher.department !== params.department_id) {
          return;
        }
        
        const title = teacher.title || '未知职称';
        if (!titleGroups[title]) return;
        
        titleGroups[title].course_count++;
        titleGroups[title].total_hours += task.total_hours || 0;
        titleGroups[title].student_count += task.class_size || 0;
      });
      
      // 计算平均工作量和转换为数组
      const results = Object.values(titleGroups).map(group => {
        return {
          ...group,
          avg_hours_per_teacher: group.teacher_count > 0 ? +(group.total_hours / group.teacher_count).toFixed(1) : 0
        };
      });
      
      // 按职称等级排序
      results.sort((a, b) => a.rank - b.rank);
      
      resolve({ results });
    }).catch(error => {
      reject(error);
    });
  });
}

/**
 * 获取课程分布合理性分析数据
 * @param {Object} params - 查询参数 { semester, department_id }
 * @returns {Promise}
 */
export function getCourseDistributionAnalysis(params = {}) {
  // 使用现有的API获取排课结果数据，在前端进行分析处理
  return new Promise((resolve, reject) => {
    getSchedulingResults({ _fetchAll: true, semester: params.semester }).then(response => {
      const schedulingResults = response.results || [];
      
      // 1. 按星期分布统计
      const dayDistribution = [0, 0, 0, 0, 0, 0, 0]; // 周一到周日
      schedulingResults.forEach(result => {
        if (result.day_of_week >= 1 && result.day_of_week <= 7) {
          dayDistribution[result.day_of_week - 1]++;
        }
      });
      
      // 2. 按节次分布统计
      const sectionDistribution = Array(12).fill(0); // 第1-12节
      schedulingResults.forEach(result => {
        for (let i = result.start_section; i <= result.end_section; i++) {
          if (i >= 1 && i <= 12) {
            sectionDistribution[i - 1]++;
          }
        }
      });
      
      // 3. 教学班规模分布
      let classSizeDistribution = {
        'small': 0,  // 小班 (<30)
        'medium': 0, // 中班 (30-60)
        'large': 0,  // 大班 (61-100)
        'huge': 0    // 特大班 (>100)
      };
      
      // 4. 课程密度热力图数据
      const heatmapData = [];
      for (let day = 1; day <= 7; day++) {
        for (let section = 1; section <= 12; section++) {
          const count = schedulingResults.filter(result => 
            result.day_of_week === day && 
            section >= result.start_section && 
            section <= result.end_section
          ).length;
          
          heatmapData.push([day - 1, section - 1, count]);
        }
      }
      
      // 5. 计算统计指标
      const totalCourses = schedulingResults.length;
      const workdayCourses = schedulingResults.filter(r => r.day_of_week >= 1 && r.day_of_week <= 5).length;
      const weekendCourses = totalCourses - workdayCourses;
      const morningCourses = schedulingResults.filter(r => r.start_section <= 4).length;
      const afternoonCourses = schedulingResults.filter(r => r.start_section > 4 && r.start_section <= 8).length;
      const eveningCourses = schedulingResults.filter(r => r.start_section > 8).length;
      
      // 计算合理性得分
      const dayBalance = calculateBalanceScore(dayDistribution.slice(0, 5)); // 工作日平衡度
      const timeBalance = calculateBalanceScore([morningCourses, afternoonCourses, eveningCourses]); // 时段平衡度
      
      resolve({
        dayDistribution,
        sectionDistribution,
        classSizeDistribution,
        heatmapData,
        statistics: {
          totalCourses,
          workdayCourses,
          weekendCourses,
          morningCourses,
          afternoonCourses,
          eveningCourses,
          dayBalance: Math.round(dayBalance),
          timeBalance: Math.round(timeBalance)
        }
      });
    }).catch(error => {
      reject(error);
    });
  });
}

/**
 * 获取教学资源配置优化建议
 * @param {Object} params - 查询参数 { semester, department_id }
 * @returns {Promise}
 */
export function getResourceOptimizationSuggestions(params = {}) {
  // 使用现有的API获取数据，在前端进行分析处理
  return new Promise((resolve, reject) => {
    Promise.all([
      getSchedulingResults({ _fetchAll: true, semester: params.semester }),
      getClassrooms({ _fetchAll: true })
    ]).then(([schedulingResponse, classroomsResponse]) => {
      const schedulingResults = schedulingResponse.results || [];
      const classrooms = classroomsResponse.results || [];
      
      // 教室容量与实际使用情况匹配度分析
      const roomUtilization = [];
      const mismatchedRooms = [];
      
      schedulingResults.forEach(result => {
        const classroom = classrooms.find(c => c.classroom_code === result.classroom_code);
        if (classroom && result.student_count) {
          const capacity = classroom.max_capacity || 0;
          const usage = result.student_count;
          const utilizationRate = capacity > 0 ? (usage / capacity) * 100 : 0;
          
          // 记录教室使用情况
          roomUtilization.push({
            classroom_code: classroom.classroom_code,
            classroom_name: classroom.classroom_name,
            capacity,
            student_count: usage,
            utilization_rate: Math.round(utilizationRate)
          });
          
          // 识别不匹配的教室
          if (utilizationRate < 40 && capacity > 60) {
            // 大教室使用率低
            mismatchedRooms.push({
              type: 'underutilized',
              classroom_code: classroom.classroom_code,
              classroom_name: classroom.classroom_name,
              capacity,
              student_count: usage,
              course_name: result.course_name,
              suggestion: '建议将课程安排到较小的教室，以提高资源利用率'
            });
          } else if (utilizationRate > 90) {
            // 教室几乎满座，可能不够宽松
            mismatchedRooms.push({
              type: 'crowded',
              classroom_code: classroom.classroom_code,
              classroom_name: classroom.classroom_name,
              capacity,
              student_count: usage,
              course_name: result.course_name,
              suggestion: '教室接近满座，建议考虑安排更大的教室以提高教学体验'
            });
          }
        }
      });
      
      // 计算统计指标
      const totalAnalyzed = roomUtilization.length;
      const goodMatches = roomUtilization.filter(r => r.utilization_rate >= 40 && r.utilization_rate <= 90).length;
      const mismatchCount = mismatchedRooms.length;
      const matchRate = totalAnalyzed > 0 ? Math.round((goodMatches / totalAnalyzed) * 100) : 0;
      
      resolve({
        roomUtilization: roomUtilization.sort((a, b) => a.utilization_rate - b.utilization_rate).slice(0, 20),
        mismatchedRooms,
        statistics: {
          totalAnalyzed,
          goodMatches,
          mismatchCount,
          matchRate
        }
      });
    }).catch(error => {
      reject(error);
    });
  });
}

/**
 * 获取教学资源使用效率分析
 * @param {Object} params - 查询参数 { semester, department_id }
 * @returns {Promise}
 */
export function getResourceEfficiencyAnalysis(params = {}) {
  // 使用现有的API获取数据，在前端进行分析处理
  return new Promise((resolve, reject) => {
    Promise.all([
      getSchedulingResults({ _fetchAll: true, semester: params.semester }),
      getClassrooms({ _fetchAll: true })
    ]).then(([schedulingResponse, classroomsResponse]) => {
      const schedulingResults = schedulingResponse.results || [];
      const classrooms = classroomsResponse.results || [];
      
      // 按教室类型统计使用情况
      const roomTypeStats = {};
      classrooms.forEach(classroom => {
        const type = classroom.classroom_type || '普通教室';
        if (!roomTypeStats[type]) {
          roomTypeStats[type] = {
            classroom_type: type,
            total_count: 0,
            // 使用Set存储已使用的教室编号，避免重复计算
            used_classrooms: new Set(),
            usage_hours: 0
          };
        }
        roomTypeStats[type].total_count++;
      });
      
      // 统计使用时长和已使用教室
      schedulingResults.forEach(result => {
        const classroom = classrooms.find(c => c.classroom_code === result.classroom_code);
        if (classroom) {
          const type = classroom.classroom_type || '普通教室';
          if (roomTypeStats[type]) {
            // 将使用的教室编号添加到Set中（会自动去重）
            roomTypeStats[type].used_classrooms.add(classroom.classroom_code);
            
            // 计算课程时长
            const hours = (result.end_section - result.start_section + 1) * 0.75; // 假设每节课45分钟
            roomTypeStats[type].usage_hours += hours;
          }
        }
      });
      
      // 计算使用率
      const typeEfficiency = Object.values(roomTypeStats).map(stats => {
        // 使用Set的size属性获取唯一的已使用教室数量
        const usedCount = stats.used_classrooms.size;
        return {
          classroom_type: stats.classroom_type,
          total_count: stats.total_count,
          used_count: usedCount,
          usage_hours: Math.round(stats.usage_hours),
          utilization_rate: stats.total_count > 0 ? Math.min(100, Math.round((usedCount / stats.total_count) * 100)) : 0
        };
      });
      
      // 计算总体指标
      const totalRooms = classrooms.length;
      // 使用Set去重，确保每个教室只计算一次
      const totalUsedRooms = new Set(schedulingResults.map(r => r.classroom_code).filter(Boolean)).size;
      // 限制最大利用率为100%
      const totalUtilizationRate = totalRooms > 0 ? Math.min(100, Math.round((totalUsedRooms / totalRooms) * 100)) : 0;
      
      resolve({
        typeEfficiency,
        statistics: {
          totalRooms,
          totalUsedRooms,
          totalUtilizationRate
        }
      });
    }).catch(error => {
      reject(error);
    });
  });
}

// 工具函数：计算数据平衡度得分 (0-100)
function calculateBalanceScore(values) {
  if (!values || values.length === 0 || values.every(v => v === 0)) {
    return 0;
  }
  
  const sum = values.reduce((a, b) => a + b, 0);
  const mean = sum / values.length;
  
  // 计算变异系数 CV (标准差/均值)
  const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);
  const cv = mean > 0 ? stdDev / mean : 0;
  
  // 将CV转换为0-100的平衡度得分 (CV越小，平衡度越高)
  return Math.max(0, 100 - (cv * 100));
} 