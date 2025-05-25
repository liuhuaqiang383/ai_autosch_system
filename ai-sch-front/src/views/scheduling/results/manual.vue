<template>
  <div class="app-container">
    <div class="filter-container">
      <el-alert
        title="手动排课功能支持为课程手动分配教室和时间"
        type="info"
        description="拖放教学班到课表中指定时间段完成排课，系统会自动检查冲突"
        show-icon
        :closable="false"
        class="compact-alert"
      />
      <div class="operation-tips">
        <el-tag type="success">操作提示：</el-tag>
        <ol>
          <li>左侧选择课程后，点击右侧课表空白格子进行排课</li>
          <li>也可以直接拖拽左侧课程到右侧课表进行排课</li>
          <li>已排课程显示在课表中，支持删除操作</li>
        </ol>
      </div>
    </div>

    <div class="manual-scheduling-container">
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="task-selection-container">
            <div class="box-card-header">
              <span>待排课任务列表</span>
              <div class="filter-box">
                <el-input
                  v-model="searchTaskKeyword"
                  placeholder="搜索课程/教师"
                  style="width: 120px;"
                  class="filter-item"
                  @keyup.enter.native="filterTasks"
                />
                <el-button
                  v-waves
                  class="filter-item"
                  type="primary"
                  icon="el-icon-search"
                  size="small"
                  @click="filterTasks"
                >
                  搜索
                </el-button>
              </div>
            </div>
            <el-card class="box-card" shadow="never">
              <div class="task-list-wrapper">
                <div v-if="tasksLoading" class="loading-container">
                  <i class="el-icon-loading"></i>
                  <p>加载任务中...</p>
                </div>
                <div v-else-if="unscheduledTasks.length === 0" class="no-data">
                  <i class="el-icon-s-opportunity" />
                  <p>暂无待排课任务</p>
                </div>
                <el-collapse accordion>
                  <el-collapse-item 
                    v-for="(task, index) in filteredUnscheduledTasks" 
                    :key="task.id"
                    :title="task.course_name"
                    :name="index"
                  >
                    <div 
                      class="task-item"
                      draggable="true"
                      @dragstart="handleDragStart($event, task)"
                    >
                      <div class="task-info">
                        <p><b>教学班编号:</b> {{ task.teaching_class_code }}</p>
                        <p><b>教学班名称:</b> {{ task.teaching_class_name }}</p>
                        <p><b>教师:</b> {{ task.teacher_name }}</p>
                        <p><b>开课学时:</b> {{ task.course_hours }}</p>
                        <p><b>人数:</b> {{ task.class_size }}</p>
                        <p><b>连排节次:</b> {{ task.consecutive_periods || 2 }}</p>
                      </div>
                      <div class="task-actions">
                        <el-button 
                          type="primary" 
                          size="mini"
                          @click="handleTaskSelect(task)"
                        >
                          选择
                        </el-button>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </el-card>
          </div>
        </el-col>

        <el-col :span="18">
          <div class="scheduling-board-container">
            <div class="box-card-header">
              <span>课表</span>
              <div class="filter-box">
                <el-select
                  v-model="selectedBuilding"
                  placeholder="选择教学楼"
                  class="filter-item"
                  clearable
                  :loading="buildingsLoading"
                  @change="handleBuildingChange"
                >
                  <el-option
                    v-for="item in buildingOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
                <el-select
                  v-model="selectedClassroom"
                  placeholder="选择教室"
                  class="filter-item"
                  clearable
                  :loading="classroomsLoading"
                  @change="handleClassroomChange"
                >
                  <el-option
                    v-for="item in classroomOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
                <el-select
                  v-model="selectedWeek"
                  placeholder="周次"
                  class="filter-item"
                  clearable
                >
                  <el-option
                    v-for="week in weekOptions"
                    :key="week.value"
                    :label="week.label"
                    :value="week.value"
                  />
                </el-select>
                <el-button
                  class="filter-item"
                  type="primary"
                  icon="el-icon-refresh"
                  :loading="resultsLoading"
                  size="small"
                  @click="refreshData"
                >
                  刷新
                </el-button>
                <el-button
                  v-if="selectedClassroom && scheduledResults.length > 0"
                  class="filter-item"
                  type="success"
                  icon="el-icon-download"
                  size="small"
                  @click="exportToExcel"
                >
                  导出Excel
                </el-button>
              </div>
            </div>
            <div v-if="selectedClassroom && getCurrentClassroomInfo()" class="selected-classroom-info">
              当前教室: {{ getCurrentClassroomInfo() }}
            </div>
            <el-card class="box-card" shadow="never">
              <div v-if="resultsLoading" class="loading-container">
                <i class="el-icon-loading"></i>
                <p>加载课表中...</p>
              </div>
              <div v-else-if="scheduledResults.length === 0 && !selectedTask && !isDragging" class="no-task-selected">
                <i class="el-icon-s-operation" />
                <p>{{ selectedClassroom ? '当前教室暂无排课记录' : '请选择教室查看排课记录或从左侧选择排课任务' }}</p>
              </div>
              
              <div v-else class="timetable-container">
                <div class="timetable-header">
                  <div class="time-slot"></div>
                  <div class="day-header" v-for="day in daysOfWeek" :key="day.value">
                    {{ day.label }}
                  </div>
                </div>
                <div class="timetable-body">
                  <div v-for="slot in timeSlots" :key="slot.id" class="time-row">
                    <div class="time-slot">
                      <div>{{ slot.label }}</div>
                      <div class="time-info">{{ slot.time }}</div>
                    </div>
                    <div 
                      v-for="day in daysOfWeek" 
                      :key="`${day.value}-${slot.id}`"
                      class="day-slot"
                      :class="{ 'slot-available': isSlotAvailable(day.value, slot.id) }"
                      @dragover="handleDragOver($event, day.value, slot.id)"
                      @drop="handleDrop($event, day.value, slot.id)"
                      @click="handleSlotClick(day.value, slot.id)"
                    >
                      <el-popover
                        v-if="hasScheduledClass(day.value, slot.id)"
                        placement="right"
                        width="300"
                        trigger="hover"
                        popper-class="course-detail-popover"
                      >
                        <div class="course-detail-content">
                          <h4>课程详情</h4>
                          <div class="detail-item">
                            <span class="label">课程名称：</span>
                            <span class="value">{{ getScheduledClass(day.value, slot.id).course_name }}</span>
                          </div>
                          <div class="detail-item">
                            <span class="label">教学班：</span>
                            <span class="value">{{ getScheduledClass(day.value, slot.id).teaching_class_name }}</span>
                          </div>
                          <div class="detail-item" v-if="getScheduledClass(day.value, slot.id).class_names && getScheduledClass(day.value, slot.id).class_names.length > 0">
                            <span class="label">班级：</span>
                            <span class="value">{{ getScheduledClass(day.value, slot.id).class_names.join(', ') }}</span>
                          </div>
                          <div class="detail-item">
                            <span class="label">教师：</span>
                            <span class="value">{{ getScheduledClass(day.value, slot.id).teacher_name }}</span>
                          </div>
                          <div class="detail-item">
                            <span class="label">教室：</span>
                            <span class="value">{{ getScheduledClass(day.value, slot.id).classroom_name }}</span>
                          </div>
                          <div class="detail-item">
                            <span class="label">周次：</span>
                            <span class="value">{{ formatWeekList(getScheduledClass(day.value, slot.id).week_list) }}</span>
                          </div>
                          <div class="detail-item">
                            <span class="label">节次：</span>
                            <span class="value">第{{ getScheduledClass(day.value, slot.id).start_section }}-{{ getScheduledClass(day.value, slot.id).end_section }}节</span>
                          </div>
                        </div>
                        <div slot="reference" class="scheduled-class">
                          <div class="scheduled-content">
                            <p class="course-name">{{ getScheduledClass(day.value, slot.id).course_name }}</p>
                            <p class="classroom-info">{{ getScheduledClass(day.value, slot.id).classroom_name }}</p>
                            <p class="week-info">{{ formatWeekList(getScheduledClass(day.value, slot.id).week_list) }}</p>
                          </div>
                          <div class="scheduled-actions">
                            <el-button 
                              type="danger" 
                              size="mini" 
                              icon="el-icon-delete"
                              @click.stop="handleDeleteScheduling(getScheduledClass(day.value, slot.id))"
                            ></el-button>
                          </div>
                        </div>
                      </el-popover>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 手动排课表单 -->
    <el-dialog
      title="手动排课"
      :visible.sync="dialogFormVisible"
      width="600px"
    >
      <el-form ref="scheduleForm" :model="scheduleForm" :rules="scheduleFormRules" label-width="120px">
        <el-form-item label="教学班编号" prop="teaching_class_code">
          <el-input id="teaching_class_code" v-model="scheduleForm.teaching_class_code" disabled />
        </el-form-item>
        <el-form-item label="课程名称" prop="course_name">
          <el-input id="course_name" v-model="scheduleForm.course_name" disabled />
        </el-form-item>
        <el-form-item label="教师姓名" prop="teacher_name">
          <el-input id="teacher_name" v-model="scheduleForm.teacher_name" disabled />
        </el-form-item>
        <el-form-item label="教室" prop="classroom_code">
          <el-select
            id="classroom_code"
            v-model="scheduleForm.classroom_code"
            filterable
            placeholder="请选择教室"
          >
            <el-option
              v-for="item in availableClassrooms"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
              <span>{{ item.label }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                容量: {{ item.capacity }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="星期" prop="day_of_week">
          <el-select id="day_of_week" v-model="scheduleForm.day_of_week" placeholder="请选择星期">
            <el-option
              v-for="day in daysOfWeek"
              :key="day.value"
              :label="day.label"
              :value="day.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始节次" prop="start_section">
          <el-select id="start_section" v-model="scheduleForm.start_section" placeholder="请选择开始节次">
            <el-option
              v-for="slot in timeSlots"
              :key="slot.id"
              :label="slot.label"
              :value="slot.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="结束节次" prop="end_section">
          <el-select id="end_section" v-model="scheduleForm.end_section" placeholder="请选择结束节次">
            <el-option
              v-for="slot in timeSlots"
              :key="slot.id"
              :label="slot.label"
              :value="slot.id"
              :disabled="slot.id < scheduleForm.start_section"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="周次列表" prop="week_list">
          <el-input id="week_list" v-model="scheduleForm.week_list" placeholder="例如: 1-16" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取消</el-button>
        <el-button type="primary" @click="submitScheduling">确认排课</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getSchedulingTasks, getSchedulingResults, createSchedulingResult, deleteSchedulingResult } from '@/api/scheduling'
import { getClassrooms } from '@/api/classroom'
import { getBuildings } from '@/api/building'
import waves from '@/directive/waves'
import * as XLSX from 'xlsx'
import FileSaver from 'file-saver'

// 缓存管理
let schedulingTasksCache = null
let schedulingTasksCacheTime = null
let classroomsCache = null
let classroomsCacheTime = null
const CACHE_EXPIRY = 5 * 60 * 1000 // 缓存5分钟

// 清除缓存的函数
function clearSchedulingTasksCache() {
  schedulingTasksCache = null
  schedulingTasksCacheTime = null
  console.log('排课任务缓存已清除')
}

function clearClassroomsCache() {
  classroomsCache = null
  classroomsCacheTime = null
  console.log('教室缓存已清除')
}

export default {
  name: 'ManualScheduling',
  directives: { waves },
  data() {
    return {
      // 排课任务相关
      unscheduledTasks: [],
      searchTaskKeyword: '',
      selectedTask: null,
      isDragging: false,
      
      // 加载状态
      tasksLoading: false,
      resultsLoading: false,
      buildingsLoading: false,
      classroomsLoading: false,
      
      // 教室和教学楼
      buildingOptions: [],
      selectedBuilding: '',
      classroomOptions: [],
      selectedClassroom: '',
      availableClassrooms: [],
      
      // 周次
      selectedWeek: '',
      weekOptions: Array.from({ length: 20 }, (_, i) => ({
        value: i + 1,
        label: `第${i + 1}周`
      })),
      
      // 课表布局
      daysOfWeek: [
        { label: '周一', value: 1 },
        { label: '周二', value: 2 },
        { label: '周三', value: 3 },
        { label: '周四', value: 4 },
        { label: '周五', value: 5 },
        { label: '周六', value: 6 },
        { label: '周日', value: 7 }
      ],
      timeSlots: [
        { id: 1, label: '第1节', time: '8:00-8:45' },
        { id: 2, label: '第2节', time: '8:55-9:40' },
        { id: 3, label: '第3节', time: '10:00-10:45' },
        { id: 4, label: '第4节', time: '10:55-11:40' },
        { id: 5, label: '第5节', time: '14:00-14:45' },
        { id: 6, label: '第6节', time: '14:55-15:40' },
        { id: 7, label: '第7节', time: '16:00-16:45' },
        { id: 8, label: '第8节', time: '16:55-17:40' },
        { id: 9, label: '第9节', time: '19:00-19:45' },
        { id: 10, label: '第10节', time: '19:55-20:40' },
        { id: 11, label: '第11节', time: '20:50-21:35' }
      ],
      
      // 已排课结果
      scheduledResults: [],
      
      // 手动排课表单
      dialogFormVisible: false,
      scheduleForm: {
        task: null,
        semester: '',
        course_code: '',
        course_name: '',
        teacher_code: '',
        teacher_name: '',
        teaching_class_code: '',
        teaching_class_name: '',
        classroom_code: '',
        classroom_name: '',
        day_of_week: null,
        start_section: null,
        end_section: null,
        week_list: '1-16',
        is_fixed: true
      },
      scheduleFormRules: {
        classroom_code: [{ required: true, message: '请选择教室', trigger: 'change' }],
        day_of_week: [{ required: true, message: '请选择星期', trigger: 'change' }],
        start_section: [{ required: true, message: '请选择开始节次', trigger: 'change' }],
        end_section: [{ required: true, message: '请选择结束节次', trigger: 'change' }],
        week_list: [{ required: true, message: '请输入周次列表', trigger: 'blur' }]
      }
    }
  },
  computed: {
    filteredUnscheduledTasks() {
      if (!this.searchTaskKeyword) {
        return this.unscheduledTasks
      }
      const keyword = this.searchTaskKeyword.toLowerCase()
      return this.unscheduledTasks.filter(task => {
        return task.teaching_class_code.toLowerCase().includes(keyword) ||
               task.teaching_class_name.toLowerCase().includes(keyword) ||
               task.course_name.toLowerCase().includes(keyword) ||
               task.teacher_name.toLowerCase().includes(keyword)
      })
    }
  },
  created() {
    // 按顺序加载数据
    this.fetchUnscheduledTasks()
    this.fetchBuildings().then(() => {
      // 只有在获取到教学楼列表后，才加载教室
      if (this.selectedBuilding) {
        this.fetchClassrooms(this.selectedBuilding)
      }
    })
    // 初始加载时不筛选教室，显示所有排课结果
    this.fetchScheduledResults()
  },
  methods: {
    // 数据获取
    fetchUnscheduledTasks() {
      this.tasksLoading = true
      getSchedulingTasks({ 
        is_scheduled: false,
        _fetchAll: true // 获取所有未排课任务，而不是只获取第一页
      }).then(response => {
        this.unscheduledTasks = response.results || []
        console.log(`获取到${this.unscheduledTasks.length}个未排课任务`)
        this.tasksLoading = false
      }).catch(error => {
        console.error('获取未排课任务失败:', error)
        this.$notify({
          title: '错误',
          message: '获取待排课任务失败',
          type: 'error',
          duration: 2000
        })
        this.tasksLoading = false
      })
    },
    fetchScheduledResults() {
      this.resultsLoading = true
      // 根据选择的教室筛选排课结果
      const params = {}
      if (this.selectedClassroom) {
        params.classroom_code = this.selectedClassroom
      }
      
      getSchedulingResults(params).then(response => {
        this.scheduledResults = response.results || []
        console.log(`获取到${this.scheduledResults.length}个排课结果`)
        this.resultsLoading = false
      }).catch(error => {
        console.error('获取排课结果失败:', error)
        this.$notify({
          title: '错误',
          message: '获取排课结果失败',
          type: 'error',
          duration: 2000
        })
        this.resultsLoading = false
      })
    },
    fetchBuildings() {
      this.buildingsLoading = true
      return getBuildings({ _fetchAll: true }).then(response => {
        this.buildingOptions = (response.results || []).map(item => {
          return {
            value: item.building_code,
            label: item.building_name
          }
        })
        this.buildingsLoading = false
        return this.buildingOptions
      })
    },
    fetchClassrooms(buildingCode) {
      this.classroomsLoading = true
      const params = { _fetchAll: true }
      if (buildingCode) {
        params.building = buildingCode
      }
      getClassrooms(params).then(response => {
        this.classroomOptions = (response.results || []).map(item => {
          return {
            value: item.classroom_code,
            label: `${item.building_name} ${item.classroom_name}`,
            capacity: item.capacity
          }
        })
        this.availableClassrooms = [...this.classroomOptions]
        this.classroomsLoading = false
      })
    },
    
    // 筛选方法
    filterTasks() {
      // 已通过computed实现筛选
    },
    handleBuildingChange() {
      // 清除已选择的教室
      this.selectedClassroom = ''
      
      // 清空当前教室选项列表，确保在新数据加载前不显示旧数据
      this.classroomOptions = []
      this.availableClassrooms = []
      
      // 清除教室数据缓存
      clearClassroomsCache()
      
      // 由于教室已经清空，需要刷新课表（显示所有排课结果或清空课表）
      this.fetchScheduledResults()
      
      // 根据选择的教学楼加载对应的教室
      if (this.selectedBuilding) {
        this.fetchClassrooms(this.selectedBuilding)
      } else {
        this.fetchClassrooms()
      }
    },
    handleClassroomChange() {
      // 根据选择的教室重新加载排课结果
      this.fetchScheduledResults()
      
      // 如果选择了教室，显示该教室的课表
      if (this.selectedClassroom) {
        console.log('已选择教室:', this.selectedClassroom)
        // 这里可以添加额外的逻辑处理
      } else {
        // 清空教室时也要刷新排课结果
        console.log('已清除教室选择')
      }
    },
    
    // 任务选择和拖拽
    handleTaskSelect(task) {
      this.selectedTask = task
      this.openScheduleDialog(task)
    },
    handleDragStart(event, task) {
      this.isDragging = true
      this.selectedTask = task
      event.dataTransfer.setData('text/plain', JSON.stringify(task))
      event.dataTransfer.effectAllowed = 'move'
    },
    handleDragOver(event, day, slot) {
      // 只有可用的时间槽才允许放置
      if (this.isSlotAvailable(day, slot)) {
        event.preventDefault()
      }
    },
    handleDrop(event, day, slot) {
      event.preventDefault()
      this.isDragging = false
      
      // 获取拖拽的任务数据
      const taskJson = event.dataTransfer.getData('text/plain')
      if (!taskJson) return
      
      const task = JSON.parse(taskJson)
      this.scheduleForm.day_of_week = day
      this.scheduleForm.start_section = slot
      this.scheduleForm.end_section = slot + (task.consecutive_periods || 2) - 1
      
      this.openScheduleDialog(task)
    },
    handleSlotClick(day, slot) {
      if (this.selectedTask && this.isSlotAvailable(day, slot)) {
        this.scheduleForm.day_of_week = day
        this.scheduleForm.start_section = slot
        this.scheduleForm.end_section = slot + (this.selectedTask.consecutive_periods || 2) - 1
        
        this.openScheduleDialog(this.selectedTask)
      }
    },
    
    // 检查时间槽可用性
    isSlotAvailable(day, slot) {
      // 如果有时间冲突，则不可用
      return !this.hasScheduledClass(day, slot)
    },
    hasScheduledClass(day, slot) {
      return this.scheduledResults.some(result => {
        return result.day_of_week === day && 
               slot >= result.start_section && 
               slot <= result.end_section
      })
    },
    getScheduledClass(day, slot) {
      return this.scheduledResults.find(result => {
        return result.day_of_week === day && 
               slot >= result.start_section && 
               slot <= result.end_section
      })
    },
    
    // 排课操作
    openScheduleDialog(task) {
      this.resetScheduleForm()
      
      // 填充表单基本信息
      this.scheduleForm.task = task.id
      this.scheduleForm.semester = task.semester
      this.scheduleForm.course_code = task.course_code
      this.scheduleForm.course_name = task.course_name
      this.scheduleForm.teacher_code = task.teacher_code
      this.scheduleForm.teacher_name = task.teacher_name
      this.scheduleForm.teaching_class_code = task.teaching_class_code
      this.scheduleForm.teaching_class_name = task.teaching_class_name
      
      // 如果还没有选择教室，先加载所有教室
      if (this.availableClassrooms.length === 0) {
        this.fetchClassrooms()
      }
      
      this.dialogFormVisible = true
    },
    resetScheduleForm() {
      this.scheduleForm = {
        task: null,
        semester: '',
        course_code: '',
        course_name: '',
        teacher_code: '',
        teacher_name: '',
        teaching_class_code: '',
        teaching_class_name: '',
        classroom_code: '',
        classroom_name: '',
        day_of_week: null,
        start_section: null,
        end_section: null,
        week_list: '1-16',
        is_fixed: true
      }
    },
    submitScheduling() {
      this.$refs.scheduleForm.validate(valid => {
        if (valid) {
          // 设置教室名称
          const selectedClassroom = this.availableClassrooms.find(
            item => item.value === this.scheduleForm.classroom_code
          )
          if (selectedClassroom) {
            this.scheduleForm.classroom_name = selectedClassroom.label
          }
          
          // 确保数据格式正确
          const postData = {
            task: this.scheduleForm.task,
            semester: this.scheduleForm.semester,
            course_code: this.scheduleForm.course_code,
            course_name: this.scheduleForm.course_name,
            teacher_code: this.scheduleForm.teacher_code,
            teacher_name: this.scheduleForm.teacher_name,
            teaching_class_code: this.scheduleForm.teaching_class_code,
            teaching_class_name: this.scheduleForm.teaching_class_name,
            classroom_code: this.scheduleForm.classroom_code,
            classroom_name: this.scheduleForm.classroom_name,
            day_of_week: parseInt(this.scheduleForm.day_of_week),
            start_section: parseInt(this.scheduleForm.start_section),
            end_section: parseInt(this.scheduleForm.end_section),
            week_list: this.scheduleForm.week_list,
            is_fixed: true
          }
          
          // 检查排课冲突
          const conflicts = this.checkSchedulingConflicts(postData)
          
          if (conflicts.hasConflicts) {
            this.$notify({
              title: '警告',
              message: conflicts.messages.join('\n'),
              type: 'warning',
              duration: 2000
            })
          } else {
            createSchedulingResult(postData).then(response => {
              this.$notify({
                title: '成功',
                message: '手动排课成功',
                type: 'success',
                duration: 2000
              })
              
              this.dialogFormVisible = false
              // 清除缓存以获取最新数据
              clearSchedulingTasksCache()
              
              // 如果排课的教室与当前选中的教室相同，则更新当前课表
              // 否则保持当前选择的教室课表视图
              if (this.selectedClassroom === postData.classroom_code) {
                this.fetchScheduledResults()
              } else if (!this.selectedClassroom) {
                // 如果当前没有选择教室，则刷新所有排课结果
                this.fetchScheduledResults()
              }
              
              this.fetchUnscheduledTasks() // 刷新未排课任务
            }).catch(error => {
              this.$notify({
                title: '失败',
                message: error.message || '手动排课失败',
                type: 'error',
                duration: 2000
              })
            })
          }
        }
      })
    },
    handleDeleteScheduling(scheduledClass) {
      this.$confirm('确认取消该排课?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteSchedulingResult(scheduledClass.id).then(() => {
          this.$notify({
            title: '成功',
            message: '取消排课成功',
            type: 'success',
            duration: 2000
          })
          // 清除缓存以获取最新数据
          clearSchedulingTasksCache()
          
          // 不管当前选择什么教室，都需要更新课表显示
          // 因为我们是从当前显示的课表中删除了一个排课
          this.fetchScheduledResults() 
          
          this.fetchUnscheduledTasks() // 刷新未排课任务
        })
      }).catch(() => {
        // 用户取消操作
      })
    },
    getCurrentClassroomInfo() {
      const selectedClassroom = this.classroomOptions.find(item => item.value === this.selectedClassroom)
      if (selectedClassroom) {
        return selectedClassroom.label
      }
      return null
    },
    // 检查排课冲突
    checkSchedulingConflicts(scheduleData) {
      const conflicts = {
        hasConflicts: false,
        messages: []
      }
      
      // 检查教室时间冲突
      const classroomConflicts = this.scheduledResults.filter(result => {
        return result.classroom_code === scheduleData.classroom_code && 
               result.day_of_week === scheduleData.day_of_week &&
               ((scheduleData.start_section >= result.start_section && scheduleData.start_section <= result.end_section) ||
                (scheduleData.end_section >= result.start_section && scheduleData.end_section <= result.end_section) ||
                (scheduleData.start_section <= result.start_section && scheduleData.end_section >= result.end_section))
      })
      
      if (classroomConflicts.length > 0) {
        conflicts.hasConflicts = true
        conflicts.messages.push(`教室 ${scheduleData.classroom_name} 在周${scheduleData.day_of_week}第${scheduleData.start_section}-${scheduleData.end_section}节已被安排课程`)
      }
      
      // 这里可以添加其他冲突检查，如教师时间冲突等
      
      return conflicts
    },
    formatWeekList(weekList) {
      if (!weekList) return '未设置周次'
      
      // 如果是类似"1-16"这样的格式，直接返回
      if (/^\d+-\d+$/.test(weekList)) {
        return `第${weekList}周`
      }
      
      // 如果是逗号分隔的数字，格式化为"第x,y,z周"
      if (/^(\d+,)*\d+$/.test(weekList)) {
        return `第${weekList}周`
      }
      
      return weekList
    },
    refreshData() {
      // 清除缓存
      clearSchedulingTasksCache()
      
      // 刷新未排课任务
      this.fetchUnscheduledTasks()
      
      // 刷新课表
      this.fetchScheduledResults()
      
      this.$notify({
        title: '成功',
        message: '数据已刷新',
        type: 'success',
        duration: 1500
      })
    },
    // 导出课表到Excel
    exportToExcel() {
      if (!this.selectedClassroom || this.scheduledResults.length === 0) {
        this.$message.warning('没有可导出的课表数据')
        return
      }

      try {
        // 创建工作簿
        const workbook = XLSX.utils.book_new()
        
        // 构建表头
        const headers = ['节次']
        this.daysOfWeek.forEach(day => {
          headers.push(day.label)
        })
        
        // 创建工作表数据
        const data = []
        data.push(headers)
        
        // 填充数据
        this.timeSlots.forEach(slot => {
          const row = [`${slot.label}\n${slot.time}`]
          
          this.daysOfWeek.forEach(day => {
            const hasClass = this.hasScheduledClass(day.value, slot.id)
            if (hasClass) {
              const classInfo = this.getScheduledClass(day.value, slot.id)
              const cellContent = `${classInfo.course_name}\n${classInfo.teacher_name}\n${this.formatWeekList(classInfo.week_list)}`
              row.push(cellContent)
            } else {
              row.push('')
            }
          })
          
          data.push(row)
        })
        
        // 创建工作表
        const worksheet = XLSX.utils.aoa_to_sheet(data)
        
        // 调整列宽
        const colWidths = [{ wch: 10 }]
        for (let i = 0; i < this.daysOfWeek.length; i++) {
          colWidths.push({ wch: 20 })
        }
        worksheet['!cols'] = colWidths
        
        // 调整行高
        const rowHeights = []
        for (let i = 0; i < data.length; i++) {
          rowHeights.push({ hpt: 40 }) // 设置每行高度为40
        }
        worksheet['!rows'] = rowHeights
        
        // 获取当前选中的教室信息
        const classroomName = this.classroomOptions.find(item => item.value === this.selectedClassroom)?.label || this.selectedClassroom
        
        // 添加工作表到工作簿
        XLSX.utils.book_append_sheet(workbook, worksheet, classroomName)
        
        // 导出为Excel文件
        const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
        const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        
        // 准备文件名
        const fileName = `教室课表_${classroomName}_${new Date().toISOString().slice(0, 10)}`
        
        FileSaver.saveAs(blob, `${fileName}.xlsx`)
        
        this.$message({
          message: '课表已成功导出',
          type: 'success'
        })
      } catch (error) {
        console.error('导出Excel错误:', error)
        this.$message.error('导出Excel失败，请稍后重试')
      }
    }
  }
}
</script>

<style scoped>
.filter-container {
  margin-bottom: 10px;
}
.app-container {
  padding: 10px 20px 70px 20px;
}
.compact-alert {
  padding: 4px 8px !important;
}
.compact-alert >>> .el-alert__description {
  margin: 2px 0 0 !important;
  font-size: 12px !important;
}
.operation-tips {
  margin-top: 5px;
  font-size: 14px;
  display: flex;
  align-items: flex-start;
}
.operation-tips ol {
  margin: 0 0 0 10px;
  padding-left: 20px;
}
.operation-tips li {
  line-height: 1.6;
}
.manual-scheduling-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 140px);
  padding-bottom: 50px;
}
.box-card-header {
  height: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}
.box-card-header span {
  font-size: 16px;
  font-weight: bold;
}
.filter-box {
  display: flex;
  align-items: center;
}
.filter-item {
  margin-left: 10px;
}
.task-list-wrapper {
  height: calc(100vh - 270px);
  overflow-y: auto;
}
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
}
.loading-container i {
  font-size: 48px;
  margin-bottom: 10px;
}
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
}
.no-data i {
  font-size: 48px;
  margin-bottom: 10px;
}
.task-item {
  padding: 10px;
  border-radius: 4px;
  background-color: #f5f7fa;
  margin-bottom: 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
}
.task-item:hover {
  background-color: #ebeef5;
}
.task-info p {
  margin: 5px 0;
}
.task-actions {
  display: flex;
  align-items: center;
}
.no-task-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 270px);
  color: #909399;
}
.no-task-selected i {
  font-size: 48px;
  margin-bottom: 10px;
}
.timetable-container {
  width: 100%;
  overflow-x: auto;
  overflow-y: auto;
  max-height: calc(100vh - 270px);
  min-width: 900px;
  margin-bottom: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #dcdfe6;
}
.timetable-header {
  display: flex;
  border-bottom: 2px solid #dcdfe6;
  position: sticky;
  top: 0;
  z-index: 2;
  background-color: #f5f7fa;
  width: 100%;
  table-layout: fixed;
}
.timetable-header .time-slot {
  width: 80px;
  padding: 12px 8px;
  font-weight: bold;
  text-align: center;
  background-color: #f5f7fa;
  border-right: 1px solid #dcdfe6;
  flex: none;
}
.timetable-header .day-header {
  flex: 1;
  width: 0;
  padding: 12px 8px;
  font-weight: bold;
  text-align: center;
  background-color: #f5f7fa;
  border-right: 1px solid #dcdfe6;
}
.timetable-body {
  width: 100%;
  table-layout: fixed;
}
.time-row {
  display: flex;
  border-bottom: 1px solid #ebeef5;
  min-height: 100px;
  width: 100%;
}
.time-row .time-slot {
  width: 80px;
  padding: 8px;
  text-align: center;
  background-color: #f5f7fa;
  position: sticky;
  left: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-right: 1px solid #dcdfe6;
  flex: none;
}
.time-slot .time-info {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}
.time-row .day-slot {
  flex: 1;
  width: 0;
  height: 100px;
  border-right: 1px solid #dcdfe6;
  padding: 2px;
  position: relative;
  transition: all 0.3s;
  background-color: #ffffff;
}
.scheduled-class {
  width: 100%;
  height: 100%;
  background-color: #f0f9eb;
  color: #303133;
  border-radius: 4px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 13px;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e1f3d8;
}
.scheduled-class:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  background-color: rgba(236, 245, 255, 0.98);
}
.scheduled-content {
  text-align: center;
  overflow: hidden;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 2px;
}
.scheduled-content p {
  margin: 2px 0;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.course-name {
  font-weight: bold;
  font-size: 14px;
  color: #67c23a;
  margin-bottom: 4px !important;
}
.classroom-info {
  font-size: 12px;
  color: #606266;
}
.week-info {
  font-size: 12px;
  color: #909399;
  margin-top: 4px !important;
}
.scheduled-actions {
  display: none;
  justify-content: flex-end;
  margin-top: 4px;
}
.scheduled-class:hover .scheduled-actions {
  display: flex;
}
.scheduled-actions .el-button--mini {
  padding: 3px 6px;
  font-size: 12px;
  border-radius: 3px;
  background-color: transparent;
  border: none;
  color: #f56c6c;
}
.scheduled-actions .el-button--mini:hover {
  background-color: #fef0f0;
  color: #f56c6c;
}
.slot-available {
  background-color: rgba(144, 238, 144, 0.1);
  transition: all 0.3s;
}
.slot-available:hover {
  background-color: rgba(144, 238, 144, 0.2);
  cursor: pointer;
}
.selected-classroom-info {
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: bold;
}
.course-detail-content {
  padding: 8px;
}

.course-detail-content h4 {
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
  color: #303133;
  font-size: 16px;
}

.detail-item {
  margin-bottom: 8px;
  line-height: 1.4;
  display: flex;
}

.detail-item .label {
  color: #606266;
  width: 70px;
  flex-shrink: 0;
}

.detail-item .value {
  color: #303133;
  flex: 1;
}

/* 自定义popover样式 */
:deep(.course-detail-popover) {
  padding: 12px;
  border-radius: 4px;
}
</style>