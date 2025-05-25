<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.class_name"
        placeholder="班级名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
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

        <el-table-column width="150px" align="center" label="班级编号">
          <template slot-scope="scope">
            <span>{{ scope.row.class_code }}</span>
          </template>
        </el-table-column>

        <el-table-column width="200px" align="center" label="班级名称">
          <template slot-scope="scope">
            <span>{{ scope.row.class_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="150px" align="center" label="所属专业">
          <template slot-scope="scope">
            <span>{{ scope.row.major_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="150px" align="center" label="所属院系">
          <template slot-scope="scope">
            <span>{{ scope.row.department_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="100px" align="center" label="年级">
          <template slot-scope="scope">
            <span>{{ scope.row.enrollment_year }}</span>
          </template>
        </el-table-column>

        <el-table-column class-name="status-col" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="!scope.row.is_graduated ? 'success' : 'danger'">
              {{ !scope.row.is_graduated ? '正常' : '毕业' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column align="center" label="创建时间" width="180">
          <template slot-scope="scope">
            <span>{{ scope.row.created_at | formatDate }}</span>
          </template>
        </el-table-column>

        <el-table-column align="center" label="操作" width="180">
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

    <!-- 添加或修改班级对话框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="100px"
        style="width: 400px; margin-left:50px;"
      >
        <el-form-item label="班级编号" prop="class_code">
          <el-input v-model="temp.class_code" />
        </el-form-item>
        <el-form-item label="班级名称" prop="class_name">
          <el-input v-model="temp.class_name" />
        </el-form-item>
        <el-form-item label="所属专业" prop="major_code">
          <el-select v-model="temp.major_code" class="filter-item" placeholder="请选择专业" @change="handleMajorChange">
            <el-option 
              v-for="major in majorOptions" 
              :key="major.major_code" 
              :label="major.major_name" 
              :value="major.major_code" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属院系" prop="department">
          <el-input v-model="temp.department" disabled />
        </el-form-item>
        <el-form-item label="入学年份" prop="enrollment_year">
          <el-select v-model="temp.enrollment_year" class="filter-item" placeholder="请选择年级">
            <el-option v-for="item in gradeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="班主任">
          <el-input v-model="temp.head_teacher" />
        </el-form-item>
        <el-form-item label="班级类型">
          <el-input v-model="temp.class_type" placeholder="如：普通班级" />
        </el-form-item>
        <el-form-item label="学制">
          <el-input v-model="temp.school_system" placeholder="如：3年" />
        </el-form-item>
        <el-form-item label="培养层次">
          <el-input v-model="temp.education_level" placeholder="如：专科" />
        </el-form-item>
        <el-form-item label="最大人数">
          <el-input-number v-model="temp.max_class_size" :min="0" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="temp.is_graduated" class="filter-item" placeholder="请选择">
            <el-option v-for="item in statusOptions" :key="item.key" :label="item.display_name" :value="item.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="校区">
          <el-input v-model="temp.campus" placeholder="如：铁门关校区" />
        </el-form-item>
        <el-form-item label="固定教室">
          <el-checkbox v-model="temp.is_fixed_classroom">设置固定教室</el-checkbox>
          <el-input v-if="temp.is_fixed_classroom" v-model="temp.fixed_classroom" style="margin-top: 5px;" placeholder="教室名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="temp.remarks" type="textarea" :rows="2" />
        </el-form-item>
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
      <span>确定要删除该班级吗？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeleteVisible = false">取消</el-button>
        <el-button type="primary" @click="deleteData">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getClasses, createClass, updateClass, deleteClass } from '@/api/class'
import { getMajors } from '@/api/major'
import Pagination from '@/components/Pagination' // 分页组件

export default {
  name: 'Classes',
  components: { Pagination },
  computed: {
    totalPages() {
      return this.total > 0 ? Math.ceil(this.total / this.listQuery.limit) : 0
    }
  },
  filters: {
    statusFilter(status) {
      const statusMap = {
        true: 'success',
        false: 'danger'
      }
      return statusMap[status]
    },
    formatDate(timestamp) {
      const date = new Date(timestamp)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }
  },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      majorOptions: [], // 专业选项列表
      listQuery: {
        page: 1,
        limit: 10,
        class_name: undefined
      },
      statusOptions: [
        { key: false, display_name: '正常' },
        { key: true, display_name: '毕业' }
      ],
      gradeOptions: ['2020', '2021', '2022', '2023', '2024'],
      temp: {
        id: undefined,
        class_code: '',
        class_name: '',
        major_code: '',
        department: '',
        enrollment_year: '',
        head_teacher: '',
        class_type: '普通班级',
        school_system: '3年',
        education_level: '专科',
        max_class_size: 60,
        is_graduated: false,
        campus: '铁门关校区',
        is_fixed_classroom: false,
        fixed_classroom: '',
        remarks: '',
        major_name: '' // 用于显示专业名称，提交时会移除
      },
      dialogFormVisible: false,
      dialogDeleteVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑',
        create: '添加'
      },
      rules: {
        class_code: [{ required: true, message: '班级编号不能为空', trigger: 'blur' }],
        class_name: [{ required: true, message: '班级名称不能为空', trigger: 'blur' }],
        major_code: [{ required: true, message: '所属专业不能为空', trigger: 'change' }],
        enrollment_year: [{ required: true, message: '入学年份不能为空', trigger: 'change' }],
        department: [{ required: true, message: '所属院系不能为空', trigger: 'blur' }]
      },
      deleteId: null
    }
  },
  created() {
    this.getList()
    this.getMajorOptions()
  },
  methods: {
    getList() {
      this.listLoading = true
      getClasses(this.listQuery).then(response => {
        this.list = response.results
        this.total = response.count
        this.listLoading = false
      })
    },
    getMajorOptions() {
      getMajors({ limit: 100 }).then(response => {
        this.majorOptions = response.results || []
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
        class_code: '',
        class_name: '',
        major_code: '',
        department: '',
        enrollment_year: '',
        head_teacher: '',
        class_type: '普通班级',
        school_system: '3年',
        education_level: '专科',
        max_class_size: 60,
        is_graduated: false,
        campus: '铁门关校区',
        is_fixed_classroom: false,
        fixed_classroom: '',
        remarks: '',
        major_name: ''
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
          const submitData = Object.assign({}, this.temp)
          
          // 移除前端显示用的字段
          delete submitData.major_name
          
          console.log('提交数据:', submitData) // 调试用
          
          createClass(submitData).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('创建班级错误:', error)
            this.$notify({
              title: '错误',
              message: '创建失败: ' + (error.message || '未知错误'),
              type: 'error',
              duration: 5000
            })
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
          const tempData = Object.assign({}, this.temp)
          
          // 移除前端显示用的字段
          delete tempData.major_name
          
          console.log('更新数据:', tempData) // 调试用
          
          updateClass(tempData).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('更新班级错误:', error)
            this.$notify({
              title: '错误',
              message: '更新失败: ' + (error.message || '未知错误'),
              type: 'error',
              duration: 5000
            })
          })
        }
      })
    },
    handleDelete(row) {
      this.deleteId = row.id
      this.dialogDeleteVisible = true
    },
    deleteData() {
      deleteClass(this.deleteId).then(() => {
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
        this.dialogDeleteVisible = false
        this.getList()
      }).catch(error => {
        console.error('删除班级错误:', error)
        this.$notify({
          title: '错误',
          message: '删除失败: ' + (error.message || '未知错误'),
          type: 'error',
          duration: 5000
        })
      })
    },
    handleMajorChange(majorCode) {
      // 当专业选择变化时，获取对应的专业信息和院系信息
      const selectedMajor = this.majorOptions.find(item => item.major_code === majorCode)
      if (selectedMajor) {
        // 设置院系信息
        this.temp.department = selectedMajor.department
        this.temp.major_name = selectedMajor.major_name
        
        // 如果有入学年份，生成班级编号
        if (this.temp.enrollment_year) {
          // 生成班级编号示例：入学年份后两位+专业代码+序号(如默认为01)
          const yearCode = this.temp.enrollment_year.slice(-2)
          // 获取专业代码中的字母部分作为前缀
          const codePrefix = majorCode.replace(/[0-9]/g, '').toLowerCase()
          this.temp.class_code = `${yearCode}${codePrefix}${majorCode.slice(-2)}01`
          
          // 生成班级名称示例：入学年份+专业名称+1班
          this.temp.class_name = `${this.temp.enrollment_year}${selectedMajor.major_name}1班`
        }
      }
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
}
.record-info {
  margin-left: 10px;
  color: #606266;
}
.table-container {
  height: calc(100vh - 220px);
  min-height: 450px;
  margin-bottom: 10px;
  overflow: hidden;
}
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 10px 0;
}
</style> 