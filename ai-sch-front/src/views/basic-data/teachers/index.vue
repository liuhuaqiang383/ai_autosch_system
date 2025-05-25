<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.teacher_name"
        placeholder="教师姓名"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-select v-model="listQuery.department" placeholder="所属部门" clearable style="width: 200px" class="filter-item">
        <el-option v-for="item in departmentOptions" :key="item.department_code" :label="item.department_name" :value="item.department_code" />
      </el-select>
      <el-select v-model="listQuery.title" placeholder="职称" clearable style="width: 200px" class="filter-item">
        <el-option
          v-for="item in titleOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select v-model="listQuery.is_external" placeholder="是否外聘" clearable style="width: 120px" class="filter-item">
        <el-option v-for="item in externalOptions" :key="item.key" :label="item.label" :value="item.key" />
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
      <el-upload
        class="filter-item"
        style="margin-left: 10px; display: inline-flex;"
        action=""
        :http-request="handleBatchImport"
        :show-file-list="false"
        :before-upload="beforeUpload"
      >
        <el-button type="success" icon="el-icon-upload">批量导入</el-button>
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
        <el-table-column align="center" label="ID" width="80">
          <template slot-scope="scope">
            <span>{{ scope.row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="工号">
          <template slot-scope="scope">
            <span>{{ scope.row.teacher_code }}</span>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="姓名">
          <template slot-scope="scope">
            <span>{{ scope.row.teacher_name }}</span>
          </template>
        </el-table-column>

        <el-table-column width="80px" align="center" label="性别">
          <template slot-scope="scope">
            <span>{{ scope.row.gender }}</span>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="职称">
          <template slot-scope="scope">
            <span>{{ scope.row.title || '未设置' }}</span>
          </template>
        </el-table-column>

        <el-table-column width="180px" align="center" label="所属部门">
          <template slot-scope="scope">
            <span>{{ scope.row.department_name }}</span>
          </template>
        </el-table-column>

        <el-table-column class-name="status-col" label="是否外聘" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_external ? 'warning' : ''">
              {{ scope.row.is_external ? '外聘' : '专职' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column width="150px" align="center" label="联系电话">
          <template slot-scope="scope">
            <span>{{ scope.row.phone || '未设置' }}</span>
          </template>
        </el-table-column>

        <el-table-column width="180px" align="center" label="邮箱">
          <template slot-scope="scope">
            <span>{{ scope.row.email || '未设置' }}</span>
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

    <!-- 添加或修改教师对话框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="100px"
        style="width: 400px; margin-left:50px;"
      >
        <el-form-item label="工号" prop="teacher_code">
          <el-input v-model="temp.teacher_code" />
        </el-form-item>
        <el-form-item label="姓名" prop="teacher_name">
          <el-input v-model="temp.teacher_name" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="temp.gender" class="filter-item" placeholder="请选择">
            <el-option label="男性" value="男性" />
            <el-option label="女性" value="女性" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属部门" prop="department">
          <el-select v-model="temp.department" class="filter-item" placeholder="请选择部门">
            <el-option 
              v-for="dept in departmentOptions" 
              :key="dept.department_code" 
              :label="dept.department_name" 
              :value="dept.department_code" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职称">
          <el-select v-model="temp.title" class="filter-item" placeholder="请选择">
            <el-option label="未设置" value="" />
            <el-option label="教授" value="教授" />
            <el-option label="副教授" value="副教授" />
            <el-option label="讲师" value="讲师" />
            <el-option label="助教" value="助教" />
            <el-option label="研究员" value="研究员" />
            <el-option label="副研究员" value="副研究员" />
            <el-option label="高级工程师" value="高级工程师" />
            <el-option label="工程师" value="工程师" />
            <el-option label="助理工程师" value="助理工程师" />
            <el-option label="高级实验师" value="高级实验师" />
            <el-option label="实验师" value="实验师" />
            <el-option label="助理实验师" value="助理实验师" />
            <el-option v-for="item in customTitleOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否外聘">
          <el-switch
            v-model="temp.is_external"
            active-color="#ff4949"
            inactive-color="#13ce66"
            :active-text="'是'"
            :inactive-text="'否'"
          />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="temp.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="temp.email" />
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
      <span>确定要删除该教师信息吗？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeleteVisible = false">取消</el-button>
        <el-button type="primary" @click="deleteData">确定</el-button>
      </span>
    </el-dialog>

    <!-- 批量导入结果对话框 -->
    <el-dialog title="导入结果" :visible.sync="importResultVisible" width="50%">
      <div v-if="importResult.success">
        <el-alert
          title="导入成功"
          type="success"
          :description="`成功导入 ${importResult.total} 条数据`"
          show-icon
        />
      </div>
      <div v-else>
        <el-alert
          title="导入失败"
          type="error"
          :description="importResult.message"
          show-icon
        />
        <div v-if="importResult.errors && importResult.errors.length" class="import-errors">
          <h4>错误详情：</h4>
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
import { getTeachers, createTeacher, updateTeacher, deleteTeacher, batchImportTeachers } from '@/api/teacher'
import { getDepartments } from '@/api/department'
import Pagination from '@/components/Pagination' // 分页组件

export default {
  name: 'Teachers',
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
      departmentOptions: [], // 部门选项列表
      titleOptions: [], // 搜索筛选使用的职称选项
      customTitleOptions: [], // 自定义职称选项（从数据库中获取但不在预设列表中的）
      externalOptions: [
        { key: true, label: '外聘' },
        { key: false, label: '专职' }
      ],
      listQuery: {
        page: 1,
        limit: 20,
        teacher_name: undefined,
        department: undefined,
        title: undefined,
        is_external: undefined
      },
      temp: {
        id: undefined,
        teacher_code: '',
        teacher_name: '',
        gender: '男性',
        department: '',
        title: '',
        is_external: false,
        phone: '',
        email: '',
        remarks: ''
      },
      dialogFormVisible: false,
      dialogDeleteVisible: false,
      importResultVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑教师',
        create: '添加教师'
      },
      rules: {
        teacher_code: [{ required: true, message: '工号不能为空', trigger: 'blur' }],
        teacher_name: [{ required: true, message: '姓名不能为空', trigger: 'blur' }],
        gender: [{ required: true, message: '性别不能为空', trigger: 'change' }],
        department: [{ required: true, message: '所属部门不能为空', trigger: 'change' }]
      },
      deleteId: null,
      importResult: {
        success: false,
        total: 0,
        message: '',
        errors: []
      }
    }
  },
  created() {
    this.getList()
    this.getDepartmentOptions()
    this.getAllTeacherTitles()
  },
  methods: {
    getList() {
      this.listLoading = true
      getTeachers(this.listQuery).then(response => {
        this.list = response.results
        this.total = response.count
        this.listLoading = false
      })
    },
    getDepartmentOptions() {
      getDepartments({ _fetchAll: true }).then(response => {
        this.departmentOptions = response.results || []
        console.log(`加载了${this.departmentOptions.length}个部门选项`)
      })
    },
    getAllTeacherTitles() {
      // 预设的职称列表
      const predefinedTitles = [
        '教授', '副教授', '讲师', '助教', '研究员', '副研究员', 
        '高级工程师', '工程师', '助理工程师', '高级实验师', '实验师', '助理实验师'
      ];
      
      getTeachers({ _fetchAll: true }).then(response => {
        const titles = response.results
          .map(teacher => teacher.title)
          .filter(title => title && title.trim() !== '')
        
        const titleCount = titles.reduce((acc, title) => {
          acc[title] = (acc[title] || 0) + 1
          return acc
        }, {})
        
        // 筛选出不在预设列表中的自定义职称
        this.customTitleOptions = Object.entries(titleCount)
          .filter(([title]) => !predefinedTitles.includes(title))
          .map(([title, count]) => ({
            label: `${title} (${count}人)`,
            value: title
          }))
        
        // 生成用于搜索筛选的职称列表
        this.titleOptions = Object.entries(titleCount)
          .map(([title, count]) => ({
            label: `${title} (${count}人)`,
            value: title
          }))
          .sort((a, b) => {
            const rankOrder = {
              '教授': 1,
              '副教授': 2,
              '讲师': 3,
              '助教': 4,
              '研究员': 5,
              '副研究员': 6,
              '高级工程师': 7,
              '工程师': 8,
              '助理工程师': 9,
              '高级实验师': 10,
              '实验师': 11,
              '助理实验师': 12
            }
            const rankA = rankOrder[a.value] || 999
            const rankB = rankOrder[b.value] || 999
            if (rankA !== rankB) {
              return rankA - rankB
            }
            return b.count - a.count
          })
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
        teacher_code: '',
        teacher_name: '',
        gender: '男性',
        department: '',
        title: '',
        is_external: false,
        phone: '',
        email: '',
        remarks: ''
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
          // 创建一个新对象，避免直接修改temp
          const submitData = Object.assign({}, this.temp)
          
          // 处理性别字段，确保与后端兼容
          if (submitData.gender === '男性') {
            submitData.gender = '男'
          } else if (submitData.gender === '女性') {
            submitData.gender = '女'
          }
          
          // 确保phone和email字段存在
          if (!submitData.phone) submitData.phone = ''
          if (!submitData.email) submitData.email = ''
          
          // 调试输出
          console.log('提交的教师数据:', JSON.stringify(submitData, null, 2))
          
          createTeacher(submitData).then(response => {
            console.log('创建教师成功:', response)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('创建教师失败:', error)
            console.error('错误详情:', error.response ? JSON.stringify(error.response.data, null, 2) : error.message)
            
            this.$notify({
              title: '错误',
              message: '创建失败: ' + (error.response?.data?.detail || error.message || '服务器错误'),
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
          const submitData = Object.assign({}, this.temp)
          
          // 处理性别字段，确保与后端兼容
          if (submitData.gender === '男性') {
            submitData.gender = '男'
          } else if (submitData.gender === '女性') {
            submitData.gender = '女'
          }
          
          // 确保phone和email字段存在
          if (!submitData.phone) submitData.phone = ''
          if (!submitData.email) submitData.email = ''
          
          // 调试输出
          console.log('更新的教师数据:', JSON.stringify(submitData, null, 2))
          
          updateTeacher(submitData).then(response => {
            console.log('更新教师成功:', response)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(error => {
            console.error('更新教师失败:', error)
            console.error('错误详情:', error.response ? JSON.stringify(error.response.data, null, 2) : error.message)
            
            this.$notify({
              title: '错误',
              message: '更新失败: ' + (error.response?.data?.detail || error.message || '服务器错误'),
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
      deleteTeacher(this.deleteId).then(() => {
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
      batchImportTeachers(formData).then(response => {
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
.import-errors {
  margin-top: 15px;
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
}
.import-errors h4 {
  color: #f56c6c;
  margin-top: 0;
}
.import-errors ul {
  padding-left: 20px;
  margin: 5px 0;
}
</style> 