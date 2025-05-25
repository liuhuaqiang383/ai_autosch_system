<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.course_name"
        placeholder="课程名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-input
        v-model="listQuery.course_code"
        placeholder="课程编号"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.department" placeholder="开课院系" clearable style="width: 200px" class="filter-item">
        <el-option v-for="item in departmentOptions" :key="item.department_code" :label="item.department_name" :value="item.department_code" />
      </el-select>
      <el-select v-model="listQuery.course_type" placeholder="课程类型" clearable style="width: 180px" class="filter-item">
        <el-option v-for="item in courseTypeOptions" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.course_nature" placeholder="课程性质" clearable style="width: 180px" class="filter-item">
        <el-option v-for="item in courseNatureOptions" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>
      <el-select v-model="listQuery.is_enabled" placeholder="状态" clearable style="width: 100px" class="filter-item">
        <el-option v-for="item in statusOptions" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        添加
      </el-button>
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
        <el-table-column align="center" label="ID" width="80">
          <template slot-scope="scope">
            <span>{{ scope.row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column width="150px" align="center" label="课程编号">
          <template slot-scope="scope">
            <span>{{ scope.row.course_code }}</span>
          </template>
        </el-table-column>

        <el-table-column min-width="180px" align="center" label="课程名称">
          <template slot-scope="scope">
            <span>{{ scope.row.course_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="180px" align="center" label="英文名称">
          <template slot-scope="scope">
            <span>{{ scope.row.english_name || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="课程类型">
          <template slot-scope="scope">
            <span>{{ scope.row.course_type || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="课程性质">
          <template slot-scope="scope">
            <span>{{ scope.row.course_nature || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column width="150px" align="center" label="开课院系">
          <template slot-scope="scope">
            <span>{{ scope.row.department_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="80px" align="center" label="学分">
          <template slot-scope="scope">
            <span>{{ scope.row.credits || '0' }}</span>
          </template>
        </el-table-column>

        <el-table-column width="80px" align="center" label="总学时">
          <template slot-scope="scope">
            <span>{{ scope.row.total_hours || '0' }}</span>
          </template>
        </el-table-column>

        <el-table-column class-name="status-col" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_enabled ? 'success' : 'danger'">
              {{ scope.row.is_enabled ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column align="center" label="操作" width="180" fixed="right">
          <template slot-scope="scope">
            <el-button type="primary" size="mini" @click="handleUpdate(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" size="mini" @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-wrapper">
      <pagination
        v-show="total > 0"
        :total="total"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.limit"
        :layout="'total, prev, pager, next, jumper'"
        @pagination="handlePagination"
      />
    </div>

    <!-- 添加或修改课程对话框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" width="800px">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="right"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程编号" prop="course_code">
              <el-input v-model="temp.course_code" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程名称" prop="course_name">
              <el-input v-model="temp.course_name" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="英文名称">
              <el-input v-model="temp.english_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开课院系" prop="department">
              <el-select v-model="temp.department" class="filter-item" placeholder="请选择开课院系" style="width: 100%">
                <el-option 
                  v-for="item in departmentOptions" 
                  :key="item.department_code" 
                  :label="item.department_name" 
                  :value="item.department_code" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程类型">
              <el-select v-model="temp.course_type" class="filter-item" placeholder="请选择课程类型" style="width: 100%" clearable>
                <el-option 
                  v-for="item in courseTypeOptions" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程性质">
              <el-select v-model="temp.course_nature" class="filter-item" placeholder="请选择课程性质" style="width: 100%" clearable>
                <el-option 
                  v-for="item in courseNatureOptions" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程类别">
              <el-select v-model="temp.course_category" class="filter-item" placeholder="请选择课程类别" style="width: 100%" clearable>
                <el-option 
                  v-for="item in courseCategoryOptions" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程属性">
              <el-select v-model="temp.course_attribute" class="filter-item" placeholder="请选择课程属性" style="width: 100%" clearable>
                <el-option 
                  v-for="item in courseAttributeOptions" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 学分和学时部分 -->
        <el-divider content-position="left">学分与学时设置</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="学分" prop="credits" label-width="70px">
              <el-input-number 
                v-model="temp.credits" 
                :min="0" 
                :max="20" 
                :precision="1" 
                :step="0.5" 
                controls-position="right"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="总学时" prop="total_hours" label-width="70px">
              <el-input-number 
                v-model="temp.total_hours" 
                :min="0" 
                :max="200" 
                :step="1" 
                controls-position="right"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="周学时" label-width="70px">
              <el-input-number 
                v-model="temp.weekly_hours" 
                :min="0" 
                :max="40" 
                :step="1" 
                controls-position="right"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="理论学时" label-width="70px">
              <el-input-number 
                v-model="temp.theory_hours" 
                :min="0" 
                :max="200" 
                :step="1" 
                @change="calculateTotalHours" 
                controls-position="right"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="实验学时" label-width="70px">
              <el-input-number 
                v-model="temp.experiment_hours" 
                :min="0" 
                :max="200" 
                :step="1" 
                @change="calculateTotalHours" 
                controls-position="right"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="上机学时" label-width="70px">
              <el-input-number 
                v-model="temp.computer_hours" 
                :min="0" 
                :max="200" 
                :step="1" 
                @change="calculateTotalHours" 
                controls-position="right"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="实践学时" label-width="70px">
              <el-input-number 
                v-model="temp.practice_hours" 
                :min="0" 
                :max="200" 
                :step="1" 
                @change="calculateTotalHours" 
                controls-position="right"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="其他学时" label-width="70px">
              <el-input-number 
                v-model="temp.other_hours" 
                :min="0" 
                :max="200" 
                :step="1" 
                @change="calculateTotalHours" 
                controls-position="right"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="是否纯实践">
              <el-switch
                v-model="temp.is_pure_practice"
                active-color="#13ce66"
                inactive-color="#ff4949"
                :active-text="'是'"
                :inactive-text="'否'"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否启用">
              <el-switch
                v-model="temp.is_enabled"
                active-color="#13ce66"
                inactive-color="#ff4949"
                :active-text="'启用'"
                :inactive-text="'停用'"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog title="提示" :visible.sync="dialogDeleteVisible" width="30%">
      <span>确定要删除该课程信息吗？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeleteVisible = false">取消</el-button>
        <el-button type="primary" @click="deleteData">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getCourses, createCourse, updateCourse, deleteCourse, getCourseTypes, getCourseNatures, getCourseAttributes, getCourseCategories } from '@/api/course'
import { getDepartments } from '@/api/department'
import Pagination from '@/components/Pagination'

export default {
  name: 'Courses',
  components: { Pagination },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      departmentOptions: [], // 部门选项列表
      courseTypeOptions: [], // 课程类型选项列表
      courseNatureOptions: [], // 课程性质选项列表
      courseAttributeOptions: [], // 课程属性选项列表
      courseCategoryOptions: [], // 课程类别选项列表
      statusOptions: [
        { key: true, label: '启用' },
        { key: false, label: '停用' }
      ],
      listQuery: {
        page: 1,
        limit: 20,
        course_name: undefined,
        course_code: undefined,
        department: undefined,
        course_type: undefined,
        course_nature: undefined,
        is_enabled: undefined
      },
      temp: {
        id: undefined,
        course_code: '',
        course_name: '',
        english_name: '',
        department: undefined,
        course_type: undefined,
        course_nature: undefined,
        course_category: undefined,
        course_attribute: undefined,
        credits: 0,
        total_hours: 0,
        theory_hours: 0,
        experiment_hours: 0,
        computer_hours: 0,
        practice_hours: 0,
        other_hours: 0,
        weekly_hours: 0,
        is_pure_practice: false,
        is_enabled: true
      },
      dialogFormVisible: false,
      dialogDeleteVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑课程',
        create: '添加课程'
      },
      rules: {
        course_code: [{ required: true, message: '课程编号不能为空', trigger: 'blur' }],
        course_name: [{ required: true, message: '课程名称不能为空', trigger: 'blur' }],
        department: [{ required: true, message: '开课院系不能为空', trigger: 'change' }],
        credits: [{ required: true, message: '学分不能为空', trigger: 'blur' }],
        total_hours: [{ required: true, message: '总学时不能为空', trigger: 'blur' }]
      },
      deleteId: null
    }
  },
  created() {
    this.getList()
    this.getDepartmentOptions()
    this.getCourseTypeOptions()
    this.getCourseNatureOptions()
    this.getCourseAttributeOptions()
    this.getCourseCategoryOptions()
  },
  methods: {
    getList() {
      this.listLoading = true
      getCourses(this.listQuery).then(response => {
        this.list = response.results
        this.total = response.count
        this.listLoading = false
      })
    },
    getDepartmentOptions() {
      getDepartments({ 
        _fetchAll: true
      }).then(response => {
        // 在前端过滤单位类型为"院系"的部门
        this.departmentOptions = (response.results || []).filter(item => item.unit_type === '院系');
        console.log(`加载了${this.departmentOptions.length}个院系选项`)
      })
    },
    getCourseTypeOptions() {
      getCourseTypes().then(response => {
        this.courseTypeOptions = response || []
        console.log(`加载了${this.courseTypeOptions.length}种课程类型选项`)
      })
    },
    getCourseNatureOptions() {
      getCourseNatures().then(response => {
        this.courseNatureOptions = response || []
        console.log(`加载了${this.courseNatureOptions.length}种课程性质选项`)
      })
    },
    getCourseAttributeOptions() {
      getCourseAttributes().then(response => {
        this.courseAttributeOptions = response || []
        console.log(`加载了${this.courseAttributeOptions.length}种课程属性选项`)
      })
    },
    getCourseCategoryOptions() {
      getCourseCategories().then(response => {
        this.courseCategoryOptions = response || []
        console.log(`加载了${this.courseCategoryOptions.length}种课程类别选项`)
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handlePagination(data) {
      this.listQuery.page = data.page
      this.listQuery.limit = data.limit
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        course_code: '',
        course_name: '',
        english_name: '',
        department: undefined,
        course_type: undefined,
        course_nature: undefined,
        course_category: undefined,
        course_attribute: undefined,
        credits: 0,
        total_hours: 0,
        theory_hours: 0,
        experiment_hours: 0,
        computer_hours: 0,
        practice_hours: 0,
        other_hours: 0,
        weekly_hours: 0,
        is_pure_practice: false,
        is_enabled: true
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
          // 先计算总学时
          this.calculateTotalHours()
          
          const tempData = Object.assign({}, this.temp)
          
          console.log('创建课程提交数据:', tempData)
          
          createCourse(tempData).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('创建课程错误:', error)
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // 复制当前行数据
      this.dialogStatus = 'update'
      this.dialogFormVisible = true
      
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          // 先计算总学时
          this.calculateTotalHours()
          
          const tempData = Object.assign({}, this.temp)
          
          console.log('更新课程提交数据:', tempData)
          
          updateCourse(tempData).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('更新课程错误:', error)
          })
        }
      })
    },
    handleDelete(row) {
      this.deleteId = row.id
      this.dialogDeleteVisible = true
    },
    deleteData() {
      deleteCourse(this.deleteId).then(() => {
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
        this.dialogDeleteVisible = false
        this.getList()
      })
    },
    // 监听学时变化，自动计算总学时
    calculateTotalHours() {
      const { theory_hours, experiment_hours, computer_hours, practice_hours, other_hours } = this.temp
      this.temp.total_hours = (theory_hours || 0) + (experiment_hours || 0) + (computer_hours || 0) + (practice_hours || 0) + (other_hours || 0)
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.filter-item {
  display: inline-block;
  vertical-align: middle;
  margin-bottom: 10px;
  margin-right: 10px;
}
.record-info {
  margin-left: 10px;
  color: #606266;
}
.table-container {
  height: calc(100vh - 260px); /* 调整高度，留出更多空间给分页组件 */
  min-height: 400px;
  margin-bottom: 20px;
  overflow: hidden;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 15px 0;
  margin-bottom: 20px;
  position: relative;
  z-index: 10; /* 提高分页组件的层级 */
}

/* 自定义输入数字框样式 */
::v-deep .el-input-number {
  width: 100%;
}
::v-deep .el-input-number .el-input__inner {
  text-align: center;
  padding-left: 35px;
  padding-right: 35px;
  min-width: 90px;
}
::v-deep .el-input-number .el-input-number__decrease, 
::v-deep .el-input-number .el-input-number__increase {
  z-index: 10;
  width: 32px;
}
::v-deep .el-form-item--small .el-form-item__label {
  font-size: 13px;
}
::v-deep .el-input-number--small {
  width: 100%;
  line-height: 30px;
}
::v-deep .el-input-number--small .el-input__inner {
  height: 30px;
  line-height: 30px;
}
</style> 