<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="输入教学班编号/名称/课程名称"
        style="width: 300px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select
        v-model="listQuery.semester"
        placeholder="学期"
        clearable
        class="filter-item"
        style="width: 130px"
      >
        <el-option
          v-for="item in semesterOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select
        v-model="listQuery.department"
        placeholder="开课院系"
        clearable
        class="filter-item"
        style="width: 180px"
      >
        <el-option
          v-for="item in departmentOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-button
        v-waves
        class="filter-item"
        type="primary"
        icon="el-icon-search"
        @click="handleFilter"
      >
        搜索
      </el-button>
      <el-button
        v-waves
        class="filter-item"
        type="danger"
        icon="el-icon-setting"
        @click="handleGlobalScheduling"
      >
        一键排课
      </el-button>
      <el-button
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        新增
      </el-button>
      <el-upload
        class="filter-item"
        style="margin-left: 10px;"
        action="#"
        accept=".xls,.xlsx"
        :show-file-list="false"
        :http-request="handleBatchImport"
        :before-upload="beforeUpload"
      >
        <el-button
          type="success"
          icon="el-icon-upload2"
        >
          批量导入
        </el-button>
      </el-upload>
      <div v-if="total > 0" class="filter-item record-info">
        <span>共 <strong>{{ total }}</strong> 条记录</span>
      </div>
    </div>

    <div class="table-container">
      <el-table
        v-loading="listLoading"
        :data="list"
        element-loading-text="加载中..."
        border
        fit
        highlight-current-row
        style="width: 100%;"
        height="100%"
      >
        <el-table-column label="教学班编号" prop="teaching_class_code" align="center" width="120px">
          <template slot-scope="{row}">
            <span>{{ row.teaching_class_code }}</span>
          </template>
        </el-table-column>
        <el-table-column label="教学班名称" min-width="150px">
          <template slot-scope="{row}">
            <span>{{ row.teaching_class_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="课程编号" width="120px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.course_code }}</span>
          </template>
        </el-table-column>
        <el-table-column label="课程名称" min-width="150px">
          <template slot-scope="{row}">
            <span>{{ row.course_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="开课学时" width="100px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.course_hours }}</span>
          </template>
        </el-table-column>
        <el-table-column label="教学班人数" width="100px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.class_size }}</span>
          </template>
        </el-table-column>
        <el-table-column label="班级构成" min-width="150px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.class_composition || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="任课教师" width="120px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.teacher_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="开课院系" width="150px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.department_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="80px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.scheduling_priority }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="250px" class-name="small-padding fixed-width">
          <template slot-scope="{row}">
            <el-button type="primary" size="mini" @click="handleUpdate(row)">
              编辑
            </el-button>
            <el-button type="success" size="mini" @click="handleRunScheduling(row)">
              执行排课
            </el-button>
            <el-button type="danger" size="mini" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-wrapper">
      <pagination
        v-show="total>0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.limit"
        :layout="'total, prev, pager, next, jumper'"
        @pagination="getList"
      />
    </div>

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="120px"
        style="width: 80%; margin-left:50px;"
      >
        <el-form-item label="学年学期" prop="semester">
          <el-select v-model="temp.semester" class="filter-item" placeholder="请选择学期">
            <el-option
              v-for="item in semesterOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="课程" prop="course_code">
          <el-select
            v-model="temp.course_code"
            class="filter-item"
            placeholder="请选择课程"
            filterable
            remote
            :remote-method="searchCourses"
            :loading="coursesLoading"
            clearable
            @change="handleCourseChange"
          >
            <el-option
              v-for="item in courseOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
              <span>{{ item.label }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ item.department }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="教师" prop="teacher_code">
          <el-select
            v-model="temp.teacher_code"
            class="filter-item"
            placeholder="请选择教师"
            filterable
            remote
            :remote-method="searchTeachers"
            :loading="teachersLoading"
            clearable
            @change="handleTeacherChange"
          >
            <el-option
              v-for="item in teacherOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
              <span>{{ item.label }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ item.department }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="教学班编号" prop="teaching_class_code">
          <el-input v-model="temp.teaching_class_code" placeholder="请输入教学班编号" />
        </el-form-item>
        <el-form-item label="教学班名称" prop="teaching_class_name">
          <el-input v-model="temp.teaching_class_name" placeholder="请输入教学班名称" />
        </el-form-item>
        <el-form-item label="班级构成" prop="class_composition_array" required>
          <el-select 
            v-model="temp.class_composition_array" 
            multiple 
            filterable 
            :loading="classesLoading"
            placeholder="请选择班级构成(必选，可多选)" 
            style="width: 100%"
            @change="handleClassCompositionChange"
            remote
            :remote-method="searchClasses"
            reserve-keyword
          >
            <el-option 
              v-for="item in classOptions" 
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开课学时" prop="course_hours">
          <el-input-number v-model="temp.course_hours" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="教学班人数" prop="class_size">
          <el-input-number v-model="temp.class_size" :min="1" :max="300" />
        </el-form-item>
        <el-form-item label="排课优先级" prop="scheduling_priority">
          <el-input-number v-model="temp.scheduling_priority" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="开课校区" prop="campus">
          <el-select v-model="temp.campus" class="filter-item" placeholder="请选择校区">
            <el-option 
              v-for="item in campusOptions" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="连排节次" prop="consecutive_periods">
          <el-input-number v-model="temp.consecutive_periods" :min="1" :max="4" />
        </el-form-item>
        <el-form-item label="指定教室类型" prop="classroom_type">
          <el-select v-model="temp.classroom_type" class="filter-item" placeholder="请选择教室类型">
            <el-option 
              v-for="item in classroomTypeOptions" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus==='create'?createData():updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>

    <!-- 导入结果对话框 -->
    <el-dialog title="导入结果" :visible.sync="importResultVisible" width="50%">
      <div v-if="importResult.success">
        <el-result
          icon="success"
          title="导入成功"
          :description="`成功导入 ${importResult.total} 条排课任务数据`"
        />
      </div>
      <div v-else>
        <el-result
          icon="error"
          title="导入失败"
          :description="importResult.message"
        />
        <div v-if="importResult.errors && importResult.errors.length" class="import-errors">
          <h4>详细错误信息：</h4>
          <ul>
            <li v-for="(error, index) in importResult.errors" :key="index">{{ error }}</li>
          </ul>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="importResultVisible = false">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getSchedulingTasks, getSchedulingTask, createSchedulingTask, updateSchedulingTask, deleteSchedulingTask, getTaskSchedulingResults, getSchedulingLogs, batchImportSchedulingTasks, runGlobalAutoScheduling } from '@/api/scheduling'
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'
import { getDepartments } from '@/api/department'
import { getTeachers } from '@/api/teacher'
import { getCourses } from '@/api/course'
import { getClassroomTypes, getCampusList } from '@/api/classroom'
import { getClasses } from '@/api/class'

export default {
  name: 'SchedulingTasks',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        search: undefined,
        semester: undefined,
        department: undefined
      },
      semesterOptions: [
        { value: '2023-2024-1', label: '2023-2024学年第一学期' },
        { value: '2023-2024-2', label: '2023-2024学年第二学期' },
        { value: '2024-2025-1', label: '2024-2025学年第一学期' },
        { value: '2024-2025-2', label: '2024-2025学年第二学期' }
      ],
      departmentOptions: [],
      courseOptions: [],
      teacherOptions: [],
      campusOptions: [],
      classroomTypeOptions: [],
      classOptions: [],
      coursesLoading: false,
      teachersLoading: false,
      classesLoading: false,
      temp: {
        id: undefined,
        teaching_class_code: '',
        teaching_class_name: '',
        semester: '',
        course_code: '',
        course_name: '',
        teacher_code: '',
        teacher_name: '',
        department: '',
        class_size: 0,
        course_hours: 0,
        scheduling_priority: 5,
        campus: '',
        consecutive_periods: 2,
        classroom_type: '',
        class_composition: '',
        class_composition_array: []
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑排课任务',
        create: '创建排课任务'
      },
      rules: {
        teaching_class_code: [
          { required: true, message: '教学班编号不能为空', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_-]+$/, message: '教学班编号只能包含字母、数字、下划线和连字符', trigger: 'blur' }
        ],
        teaching_class_name: [
          { required: true, message: '教学班名称不能为空', trigger: 'blur' }
        ],
        semester: [
          { required: true, message: '学期不能为空', trigger: 'change' }
        ],
        course_code: [
          { required: true, message: '课程不能为空', trigger: 'change' }
        ],
        teacher_code: [
          { required: true, message: '教师不能为空', trigger: 'change' }
        ],
        class_composition: [
          { required: true, message: '班级构成不能为空', trigger: 'change' }
        ],
        class_composition_array: [
          { required: true, type: 'array', message: '请至少选择一个班级', trigger: 'change' }
        ],
        course_hours: [
          { required: true, type: 'number', min: 1, message: '课时必须大于0', trigger: 'blur' }
        ],
        class_size: [
          { required: true, type: 'number', min: 1, message: '班级人数必须大于0', trigger: 'blur' }
        ],
        campus: [
          { required: true, message: '开课校区不能为空', trigger: 'change' }
        ],
        consecutive_periods: [
          { required: true, type: 'number', min: 1, max: 4, message: '连排节次必须在1-4之间', trigger: 'blur' }
        ]
      },
      importResultVisible: false,
      importResult: {
        success: false,
        total: 0,
        message: '',
        errors: []
      },
      courseSearchTimer: null,
      teacherSearchTimer: null,
      classSearchTimer: null
    }
  },
  created() {
    this.getList()
    this.getDepartmentOptions()
    this.getCampusOptions()
    this.getClassroomTypeOptions()
    this.getClassOptions()
  },
  methods: {
    getList() {
      this.listLoading = true
      getSchedulingTasks({
        page: this.listQuery.page,
        page_size: this.listQuery.limit,
        search: this.listQuery.search,
        semester: this.listQuery.semester,
        department: this.listQuery.department
      }).then(response => {
        this.list = response.results
        this.total = response.count
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    getDepartmentOptions() {
      getDepartments({ is_enabled: true, _fetchAll: true }).then(response => {
        this.departmentOptions = response.results
          .filter(item => item.unit_type === '院系')
          .map(item => {
            return {
              value: item.department_code,
              label: item.department_name
            }
          })
      })
    },
    getCampusOptions() {
      getCampusList().then(response => {
        if (Array.isArray(response)) {
          this.campusOptions = response.map(item => {
            return {
              value: item.id || item.name,
              label: item.name
            }
          })
        } else if (response && Array.isArray(response.results)) {
          this.campusOptions = response.results.map(item => {
            return {
              value: item.id || item.name,
              label: item.name
            }
          })
        } else {
          // 如果API返回格式异常，提供默认选项
          this.campusOptions = [
            { value: '本部', label: '本部' },
            { value: '新校区', label: '新校区' }
          ]
        }
      }).catch(() => {
        // 出错时提供默认选项
        this.campusOptions = [
          { value: '本部', label: '本部' },
          { value: '新校区', label: '新校区' }
        ]
      })
    },
    getClassroomTypeOptions() {
      getClassroomTypes().then(response => {
        if (Array.isArray(response)) {
          this.classroomTypeOptions = response.map(item => {
            return {
              value: item.id || item.name,
              label: item.name
            }
          })
        } else if (response && Array.isArray(response.results)) {
          this.classroomTypeOptions = response.results.map(item => {
            return {
              value: item.id || item.name,
              label: item.name
            }
          })
        } else {
          // 如果API返回格式异常，提供默认选项
          this.classroomTypeOptions = [
            { value: '多媒体教室', label: '多媒体教室' },
            { value: '普通教室', label: '普通教室' },
            { value: '实验室', label: '实验室' },
            { value: '语音室', label: '语音室' }
          ]
        }
      }).catch(() => {
        // 出错时提供默认选项
        this.classroomTypeOptions = [
          { value: '多媒体教室', label: '多媒体教室' },
          { value: '普通教室', label: '普通教室' },
          { value: '实验室', label: '实验室' },
          { value: '语音室', label: '语音室' }
        ]
      })
    },
    getClassOptions() {
      this.classesLoading = true
      getClasses({ 
        is_enabled: true,
        _fetchAll: true
      }).then(response => {
        if (response && response.results) {
          this.classOptions = response.results.map(item => {
            return {
              value: item.class_name,
              label: `${item.class_name}(${item.grade || ''})`,
              raw: item
            }
          })
          console.log('获取到班级数据:', this.classOptions.length, '条')
        }
        this.classesLoading = false
      }).catch(() => {
        this.classesLoading = false
      })
    },
    // 搜索班级
    searchClasses(query) {
      this.classesLoading = true
      
      if (query !== '') {
        // 使用防抖，避免频繁请求
        if (this.classSearchTimer) {
          clearTimeout(this.classSearchTimer)
        }
        
        this.classSearchTimer = setTimeout(() => {
          getClasses({ 
            search: query,
            is_enabled: true,
            limit: 20 // 限制返回结果数量
          }).then(response => {
            if (response && response.results) {
              this.classOptions = response.results.map(item => {
                return {
                  value: item.class_name,
                  label: `${item.class_name}(${item.grade || ''})`,
                  raw: item
                }
              })
              console.log('搜索到班级数据:', this.classOptions.length, '条')
            }
            this.classesLoading = false
          }).catch(() => {
            this.classesLoading = false
          })
        }, 300)
      } else {
        // 当输入为空时，加载全部班级
        this.getClassOptions()
      }
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        teaching_class_code: '',
        teaching_class_name: '',
        semester: '',
        course_code: '',
        course_name: '',
        teacher_code: '',
        teacher_name: '',
        department: '',
        class_size: 0,
        course_hours: 0,
        scheduling_priority: 5,
        campus: '',
        consecutive_periods: 2,
        classroom_type: '',
        class_composition: '',
        class_composition_array: []
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          // 深拷贝数据，避免直接修改temp
          const tempData = JSON.parse(JSON.stringify(this.temp))
          
          // 预处理和额外校验
          if (!this.preprocessFormData(tempData)) {
            return false
          }
          
          // 打印调试信息
          console.log('创建排课任务提交数据:', tempData)
          
          createSchedulingTask(tempData).then(response => {
            console.log('创建排课任务成功响应:', response)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建排课任务成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('创建排课任务错误:', error)
            let errorMsg = '创建失败'
            if (error.response && error.response.data) {
              if (typeof error.response.data === 'string') {
                errorMsg = error.response.data
              } else if (error.response.data.detail) {
                errorMsg = error.response.data.detail
              } else if (error.response.data.message) {
                errorMsg = error.response.data.message
              } else {
                errorMsg = JSON.stringify(error.response.data)
              }
            }
            this.$notify({
              title: '错误',
              message: errorMsg,
              type: 'error',
              duration: 4000
            })
          })
        } else {
          console.log('表单校验失败')
          return false
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      
      // 初始化班级构成数组
      if (this.temp.class_composition && !this.temp.class_composition_array) {
        this.temp.class_composition_array = this.temp.class_composition.split(',').filter(Boolean)
      }
      
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          // 深拷贝数据，避免直接修改temp
          const tempData = JSON.parse(JSON.stringify(this.temp))
          
          // 预处理和额外校验
          if (!this.preprocessFormData(tempData)) {
            return false
          }
          
          // 打印调试信息
          console.log('更新排课任务提交数据:', tempData)
          
          updateSchedulingTask(tempData.id, tempData).then(response => {
            console.log('更新排课任务成功响应:', response)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新排课任务成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('更新排课任务错误:', error)
            let errorMsg = '更新失败'
            if (error.response && error.response.data) {
              if (typeof error.response.data === 'string') {
                errorMsg = error.response.data
              } else if (error.response.data.detail) {
                errorMsg = error.response.data.detail
              } else if (error.response.data.message) {
                errorMsg = error.response.data.message
              } else {
                errorMsg = JSON.stringify(error.response.data)
              }
            }
            this.$notify({
              title: '错误',
              message: errorMsg,
              type: 'error',
              duration: 4000
            })
          })
        } else {
          console.log('表单校验失败')
          return false
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该排课任务?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteSchedulingTask(row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '删除排课任务成功',
            type: 'success',
            duration: 2000
          })
          this.getList()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    },
    handleRunScheduling(row) {
      this.$confirm('确认执行该排课任务?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.listLoading = true
        // 使用全局排课API
        runGlobalAutoScheduling().then(response => {
          this.listLoading = false
          this.$notify({
            title: '成功',
            message: response.message || '排课任务已启动',
            type: 'success',
            duration: 2000
          })
          // 刷新任务列表
          this.getList()
        }).catch(error => {
          this.listLoading = false
          this.$notify({
            title: '排课失败',
            message: error.message || '排课过程中出现错误',
            type: 'error',
            duration: 5000
          })
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消排课'
        })
      })
    },
    handleGlobalScheduling() {
      this.$confirm('一键排课会先清空所有已有排课结果，然后重新排课。确认继续?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.listLoading = true
        
        // 执行全局排课（后端会自动清空排课结果表）
        runGlobalAutoScheduling().then(response => {
          this.listLoading = false
          this.$notify({
            title: '排课成功',
            message: response.message || `排课完成，成功安排${response.success_count || 0}个任务`,
            type: 'success',
            duration: 5000
          })
          
          // 刷新任务列表
          this.getList()
          
          if (response.failed_count && response.failed_count > 0) {
            this.$alert(`有${response.failed_count}个任务无法安排，请查看失败任务列表`, '排课未完全成功', {
              confirmButtonText: '确定',
              callback: () => {
                // 可以在这里添加跳转到失败任务列表的逻辑
              }
            })
          }
        }).catch(error => {
          this.listLoading = false
          this.$notify({
            title: '排课失败',
            message: error.message || '排课过程中出现错误',
            type: 'error',
            duration: 5000
          })
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消排课'
        })
      })
    },
    searchCourses(query) {
      this.coursesLoading = true
      
      if (query !== '') {
        // 使用防抖，避免频繁请求
        if (this.courseSearchTimer) {
          clearTimeout(this.courseSearchTimer)
        }
        
        this.courseSearchTimer = setTimeout(() => {
          getCourses({ 
            search: query,
            is_enabled: true,
            limit: 20 // 限制返回结果数量
          }).then(response => {
            this.courseOptions = response.results.map(item => {
              // 打印原始数据，便于调试
              console.log('课程数据:', item)
              
              return {
                value: item.course_code,
                label: `${item.course_code} - ${item.course_name}`,
                department: item.department_name,
                // 保存完整数据，用于后续选择时使用
                raw: item
              }
            })
            this.coursesLoading = false
          }).catch(() => {
            this.coursesLoading = false
          })
        }, 300)
      } else {
        // 当输入为空时，加载默认的课程列表
        getCourses({ 
          is_enabled: true,
          limit: 20 
        }).then(response => {
          this.courseOptions = response.results.map(item => {
            // 打印原始数据，便于调试
            console.log('课程数据:', item)
            
            return {
              value: item.course_code,
              label: `${item.course_code} - ${item.course_name}`,
              department: item.department_name,
              raw: item
            }
          })
          this.coursesLoading = false
        }).catch(() => {
          this.coursesLoading = false
          this.courseOptions = []
        })
      }
    },
    searchTeachers(query) {
      this.teachersLoading = true
      
      if (query !== '') {
        // 使用防抖，避免频繁请求
        if (this.teacherSearchTimer) {
          clearTimeout(this.teacherSearchTimer)
        }
        
        this.teacherSearchTimer = setTimeout(() => {
          getTeachers({ 
            search: query,
            limit: 20 // 限制返回结果数量
          }).then(response => {
            this.teacherOptions = response.results.map(item => {
              return {
                value: item.teacher_code,
                label: `${item.teacher_code} - ${item.teacher_name}`,
                department: item.department_name,
                // 保存完整数据，用于后续选择时使用
                raw: item
              }
            })
            this.teachersLoading = false
          }).catch(() => {
            this.teachersLoading = false
          })
        }, 300)
      } else {
        // 当输入为空时，加载默认的教师列表
        getTeachers({ 
          limit: 20 
        }).then(response => {
          this.teacherOptions = response.results.map(item => {
            return {
              value: item.teacher_code,
              label: `${item.teacher_code} - ${item.teacher_name}`,
              department: item.department_name,
              raw: item
            }
          })
          this.teachersLoading = false
        }).catch(() => {
          this.teachersLoading = false
          this.teacherOptions = []
        })
      }
    },
    beforeUpload(file) {
      // 检查文件类型，只允许上传Excel文件
      const isExcel = file.type === 'application/vnd.ms-excel' || 
                      file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      if (!isExcel) {
        this.$message.error('只能上传Excel文件!')
        return false
      }
      return true
    },
    handleBatchImport(options) {
      const { file } = options
      const formData = new FormData()
      formData.append('file', file)
      
      this.listLoading = true
      batchImportSchedulingTasks(formData).then(response => {
        this.importResult = {
          success: true,
          total: response.total || 0,
          message: '导入成功',
          errors: []
        }
        this.importResultVisible = true
        this.getList() // 刷新列表
      }).catch(error => {
        this.importResult = {
          success: false,
          total: 0,
          message: error.message || '导入失败',
          errors: error.response && error.response.data ? (error.response.data.errors || []) : []
        }
        this.importResultVisible = true
      }).finally(() => {
        this.listLoading = false
      })
    },
    handleCourseChange(value) {
      // 处理课程选择变化后的逻辑
      if (value) {
        const selectedCourse = this.courseOptions.find(item => item.value === value)
        if (selectedCourse && selectedCourse.raw) {
          console.log('选中课程数据:', selectedCourse.raw)
          
          // 更新课程相关信息
          this.temp.course_name = selectedCourse.raw.course_name
          
          // 设置开课院系 - 检查所有可能的属性名
          if (selectedCourse.raw.department) {
            // 直接使用department字段
            this.temp.department = selectedCourse.raw.department
            console.log('设置开课院系(department):', this.temp.department)
          } else if (selectedCourse.raw.department_code) {
            // 使用department_code字段
            this.temp.department = selectedCourse.raw.department_code
            console.log('设置开课院系(department_code):', this.temp.department)
          } else if (selectedCourse.raw.department_name) {
            // 尝试从departmentOptions查找对应的department_code
            const dept = this.departmentOptions.find(d => d.label === selectedCourse.raw.department_name)
            if (dept) {
              this.temp.department = dept.value
              console.log('根据department_name设置开课院系:', this.temp.department)
            } else {
              console.warn('无法根据department_name找到对应的department_code:', selectedCourse.raw.department_name)
            }
          } else {
            console.warn('课程数据中没有找到开课院系信息')
          }
          
          // 如果需要更新学时等信息，可以在这里添加
          if (selectedCourse.raw.hours) {
            this.temp.course_hours = selectedCourse.raw.hours
          } else if (selectedCourse.raw.total_hours) {
            this.temp.course_hours = selectedCourse.raw.total_hours
          }
        }
      } else {
        // 清空选择时重置相关字段
        this.temp.course_name = ''
        this.temp.department = ''
      }
    },
    handleTeacherChange(value) {
      // 处理教师选择变化后的逻辑
      if (value) {
        const selectedTeacher = this.teacherOptions.find(item => item.value === value)
        if (selectedTeacher && selectedTeacher.raw) {
          // 更新教师相关信息
          this.temp.teacher_name = selectedTeacher.raw.teacher_name
          // 如果需要更新其他信息，可以在这里添加
        }
      } else {
        // 清空选择时重置相关字段
        this.temp.teacher_name = ''
      }
    },
    // 处理班级构成变更
    handleClassCompositionChange(value) {
      // 将选中的班级数组转换为字符串，以逗号分隔
      if (Array.isArray(value) && value.length > 0) {
        this.temp.class_composition = value.join(',')
        console.log('设置班级构成:', this.temp.class_composition)
        
        // 自动计算班级人数总和
        const selectedClasses = value.map(className => 
          this.classOptions.find(item => item.value === className)
        ).filter(Boolean);
        
        // 如果所有选中的班级都有学生数量信息，则累加
        const studentCountExists = selectedClasses.every(cls => cls.raw && typeof cls.raw.student_count === 'number');
        if (studentCountExists) {
          const totalStudents = selectedClasses.reduce((sum, cls) => sum + (cls.raw.student_count || 0), 0);
          if (totalStudents > 0) {
            this.temp.class_size = totalStudents;
            console.log('自动计算班级人数总和:', totalStudents);
          }
        }
      } else {
        this.temp.class_composition = ''
      }
    },
    // 表单数据预处理和额外校验
    preprocessFormData(tempData) {
      // 转换类型：确保数值字段是数值类型
      tempData.course_hours = Number(tempData.course_hours || 0)
      tempData.class_size = Number(tempData.class_size || 0)
      tempData.scheduling_priority = Number(tempData.scheduling_priority || 5)
      tempData.consecutive_periods = Number(tempData.consecutive_periods || 2)
      
      console.log('预处理前数据:', JSON.stringify(tempData))
      
      // 确保必填字段存在
      if (!tempData.semester) {
        this.$message.error('请选择学年学期')
        return false
      }
      
      if (!tempData.course_code) {
        this.$message.error('请选择课程')
        return false
      }
      
      if (!tempData.teacher_code) {
        this.$message.error('请选择教师')
        return false
      }
      
      if (!tempData.teaching_class_code) {
        this.$message.error('请输入教学班编号')
        return false
      }
      
      if (!tempData.teaching_class_name) {
        this.$message.error('请输入教学班名称')
        return false
      }
      
      // 检查班级构成是否已选择
      if (!tempData.class_composition) {
        this.$message.error('请选择班级构成')
        return false
      }
      
      if (!tempData.campus) {
        this.$message.error('请选择开课校区')
        return false
      }
      
      // 检查开课院系是否存在
      if (!tempData.department) {
        // 尝试从选择的课程中获取开课院系
        if (tempData.course_code) {
          const selectedCourse = this.courseOptions.find(item => item.value === tempData.course_code)
          if (selectedCourse) {
            if (selectedCourse.raw) {
              // 检查各种可能的属性名
              if (selectedCourse.raw.department) {
                tempData.department = selectedCourse.raw.department
              } else if (selectedCourse.raw.department_code) {
                tempData.department = selectedCourse.raw.department_code
              } else if (selectedCourse.raw.department_name) {
                // 根据名称查找代码
                const dept = this.departmentOptions.find(d => d.label === selectedCourse.raw.department_name)
                if (dept) {
                  tempData.department = dept.value
                }
              }
            }
            
            // 如果仍未设置department，使用选项中的department信息
            if (!tempData.department && selectedCourse.department) {
              // 查找对应的department代码
              const dept = this.departmentOptions.find(d => d.label === selectedCourse.department)
              if (dept) {
                tempData.department = dept.value
              }
            }
          }
          
          // 如果仍然无法获取department，显示错误
          if (!tempData.department) {
            this.$message.error('无法获取开课院系信息，请重新选择课程')
            console.error('无法从课程中获取开课院系，可用的课程数据:', 
              selectedCourse ? JSON.stringify(selectedCourse) : '未找到选中的课程')
            return false
          }
          
          console.log('自动设置开课院系:', tempData.department)
        } else {
          this.$message.error('开课院系不能为空')
          return false
        }
      }
      
      console.log('预处理后数据:', JSON.stringify(tempData))
      
      // 验证通过
      return true
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
}
.filter-item {
  display: inline-block;
  vertical-align: middle;
  margin-bottom: 10px;
  margin-right: 10px;
}
.record-info {
  float: right;
  line-height: 40px;
  color: #606266;
}
.table-container {
  height: calc(100vh - 220px);
  overflow: hidden;
}
.pagination-wrapper {
  margin-top: 15px;
}
.import-errors {
  margin-top: 15px;
  border: 1px solid #f56c6c;
  border-radius: 4px;
  padding: 10px 15px;
  background-color: #fef0f0;
}
.import-errors h4 {
  margin-top: 0;
  color: #f56c6c;
}
.import-errors ul {
  margin-bottom: 0;
}
</style> 