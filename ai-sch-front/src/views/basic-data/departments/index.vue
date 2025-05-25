<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.department_name"
        placeholder="部门名称"
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

        <el-table-column width="180px" align="center" label="部门编码">
          <template slot-scope="scope">
            <span>{{ scope.row.department_code }}</span>
          </template>
        </el-table-column>

        <el-table-column width="200px" align="center" label="部门名称">
          <template slot-scope="scope">
            <span>{{ scope.row.department_name }}</span>
          </template>
        </el-table-column>

        <el-table-column class-name="status-col" label="状态" width="110">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_enabled ? 'success' : 'danger'">
              {{ scope.row.is_enabled ? '正常' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="单位类型">
          <template slot-scope="scope">
            <span>{{ scope.row.unit_type || '未设置' }}</span>
          </template>
        </el-table-column>

        <el-table-column width="150px" align="center" label="单位归属">
          <template slot-scope="scope">
            <span>{{ scope.row.unit_affiliation || '未设置' }}</span>
          </template>
        </el-table-column>

        <el-table-column min-width="200px" label="备注">
          <template slot-scope="scope">
            <span>{{ scope.row.remarks }}</span>
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

    <!-- 添加或修改部门对话框 -->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible">
      <el-form
        ref="dataForm"
        :rules="rules"
        :model="temp"
        label-position="left"
        label-width="100px"
        style="width: 400px; margin-left:50px;"
      >
        <el-form-item label="部门编码" prop="department_code">
          <el-input v-model="temp.department_code" />
        </el-form-item>
        <el-form-item label="部门名称" prop="department_name">
          <el-input v-model="temp.department_name" />
        </el-form-item>
        <el-form-item label="单位类型">
          <el-select v-model="temp.unit_type" class="filter-item" placeholder="请选择">
            <el-option v-for="item in unitTypeOptions.filter(i => i !== '全部')" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="单位归属">
          <el-select v-model="temp.unit_affiliation" class="filter-item" placeholder="请选择">
            <el-option v-for="item in unitAffiliationOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="temp.is_enabled" class="filter-item" placeholder="请选择">
            <el-option v-for="item in statusOptions" :key="item.key" :label="item.display_name" :value="item.key" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="temp.remarks" :autosize="{ minRows: 2, maxRows: 4 }" type="textarea" />
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
      <span>确定要删除该部门吗？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeleteVisible = false">取消</el-button>
        <el-button type="primary" @click="deleteData">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getDepartments, createDepartment, updateDepartment, deleteDepartment } from '@/api/department'
import Pagination from '@/components/Pagination' // 分页组件

export default {
  name: 'Departments',
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
      listQuery: {
        page: 1,
        limit: 10,
        department_name: undefined
      },
      statusOptions: [
        { key: true, display_name: '正常' },
        { key: false, display_name: '停用' }
      ],
      unitTypeOptions: ['全部', '院系', '行政类', '科研机构', '其它'],
      unitAffiliationOptions: ['直属（校办）', '校企合办', '其它'],
      temp: {
        id: undefined,
        department_code: '',
        department_name: '',
        unit_type: '院系',
        unit_affiliation: '直属（校办）',
        is_enabled: true,
        remarks: ''
      },
      dialogFormVisible: false,
      dialogDeleteVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑',
        create: '添加'
      },
      rules: {
        department_code: [{ required: true, message: '部门编码不能为空', trigger: 'blur' }],
        department_name: [{ required: true, message: '部门名称不能为空', trigger: 'blur' }]
      },
      deleteId: null
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      
      // 确保页码和页大小参数正确
      const params = {
        ...this.listQuery,
        page: this.listQuery.page || 1,
        limit: this.listQuery.limit || 10
      }
      
      getDepartments(params).then(response => {
        console.log('API响应数据:', response) // 调试用，可以观察实际返回数据
        
        // Django REST Framework标准分页响应处理
        if (response.results && Array.isArray(response.results)) {
          this.list = response.results
          this.total = response.count || 0
          console.log('数据总数:', this.total, '当前页数据:', this.list.length)
        } else if (response.data && Array.isArray(response.data)) {
          // 其他可能的响应格式
          this.list = response.data
          this.total = response.total || 0
        } else if (Array.isArray(response)) {
          // 直接返回数组的情况
          this.list = response
          this.total = response.length
        } else {
          console.error('未知的API响应格式', response)
          this.list = []
          this.total = 0
        }
        
        this.listLoading = false
      }).catch(error => {
        console.error('获取院系列表失败:', error)
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handlePagination(pagination) {
      console.log('分页事件触发:', pagination)
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        department_code: '',
        department_name: '',
        unit_type: '院系',
        unit_affiliation: '直属（校办）',
        is_enabled: true,
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
          createDepartment(this.temp).then(() => {
            this.list.unshift(this.temp)
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) // copy obj
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
          updateDepartment(tempData.id, tempData).then(() => {
            for (const v of this.list) {
              if (v.id === this.temp.id) {
                const index = this.list.indexOf(v)
                this.list.splice(index, 1, this.temp)
                break
              }
            }
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          })
        }
      })
    },
    handleDelete(row) {
      this.deleteId = row.id
      this.dialogDeleteVisible = true
    },
    deleteData() {
      deleteDepartment(this.deleteId).then(() => {
        this.$notify({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2000
        })
        this.dialogDeleteVisible = false
        this.getList()
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