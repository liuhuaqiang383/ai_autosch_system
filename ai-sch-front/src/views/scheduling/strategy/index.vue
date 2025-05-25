<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input
        v-model="listQuery.search"
        placeholder="输入策略名称"
        style="width: 200px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
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
        class="filter-item"
        style="margin-left: 10px;"
        type="primary"
        icon="el-icon-plus"
        @click="handleCreate"
      >
        新增
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
        <el-table-column label="ID" align="center" width="80px">
          <template slot-scope="{row}">
            <span>{{ row.id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="策略名称" min-width="150px">
          <template slot-scope="{row}">
            <span>{{ row.strategy_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="策略描述" min-width="200px">
          <template slot-scope="{row}">
            <span>{{ row.description }}</span>
          </template>
        </el-table-column>
        <el-table-column label="教师权重" width="100px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.teacher_weight }}</span>
          </template>
        </el-table-column>
        <el-table-column label="教室权重" width="100px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.classroom_weight }}</span>
          </template>
        </el-table-column>
        <el-table-column label="班级权重" width="100px" align="center">
          <template slot-scope="{row}">
            <span>{{ row.class_weight }}</span>
          </template>
        </el-table-column>
        <el-table-column label="默认策略" width="100px" align="center">
          <template slot-scope="{row}">
            <el-tag :type="row.is_default ? 'success' : 'info'">
              {{ row.is_default ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center" width="250px" class-name="small-padding fixed-width">
          <template slot-scope="{row}">
            <el-button type="primary" size="mini" @click="handleUpdate(row)">
              编辑
            </el-button>
            <el-button 
              v-if="!row.is_default" 
              type="success" 
              size="mini" 
              @click="handleSetDefault(row)"
            >
              设为默认
            </el-button>
            <el-button 
              v-if="!row.is_default" 
              type="danger" 
              size="mini" 
              @click="handleDelete(row)"
            >
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
        <el-form-item label="策略名称" prop="strategy_name">
          <el-input v-model="temp.strategy_name" placeholder="请输入策略名称" />
        </el-form-item>
        <el-form-item label="策略描述" prop="description">
          <el-input v-model="temp.description" type="textarea" :rows="3" placeholder="请输入策略描述" />
        </el-form-item>
        <el-form-item label="教师权重" prop="teacher_weight">
          <el-slider v-model="temp.teacher_weight" :min="1" :max="10" show-input></el-slider>
        </el-form-item>
        <el-form-item label="教室权重" prop="classroom_weight">
          <el-slider v-model="temp.classroom_weight" :min="1" :max="10" show-input></el-slider>
        </el-form-item>
        <el-form-item label="班级权重" prop="class_weight">
          <el-slider v-model="temp.class_weight" :min="1" :max="10" show-input></el-slider>
        </el-form-item>
        <el-form-item label="避免教师冲突" prop="avoid_teacher_conflict">
          <el-switch v-model="temp.avoid_teacher_conflict"></el-switch>
        </el-form-item>
        <el-form-item label="避免教室冲突" prop="avoid_classroom_conflict">
          <el-switch v-model="temp.avoid_classroom_conflict"></el-switch>
        </el-form-item>
        <el-form-item label="避免班级冲突" prop="avoid_class_conflict">
          <el-switch v-model="temp.avoid_class_conflict"></el-switch>
        </el-form-item>
        <el-form-item label="教师连续上课偏好" prop="prefer_teacher_continuous">
          <el-switch v-model="temp.prefer_teacher_continuous"></el-switch>
        </el-form-item>
        <el-form-item label="班级连续上课偏好" prop="prefer_class_continuous">
          <el-switch v-model="temp.prefer_class_continuous"></el-switch>
        </el-form-item>
        <el-form-item label="教师每日最大课时" prop="max_daily_hours_teacher">
          <el-input-number v-model="temp.max_daily_hours_teacher" :min="1" :max="12"></el-input-number>
        </el-form-item>
        <el-form-item label="班级每日最大课时" prop="max_daily_hours_class">
          <el-input-number v-model="temp.max_daily_hours_class" :min="1" :max="12"></el-input-number>
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
  </div>
</template>

<script>
import { getSchedulingStrategies, createSchedulingStrategy, updateSchedulingStrategy } from '@/api/scheduling'
import waves from '@/directive/waves'
import Pagination from '@/components/Pagination'
import request from '@/utils/request'

export default {
  name: 'SchedulingStrategy',
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
        search: undefined
      },
      temp: {
        id: undefined,
        strategy_name: '',
        description: '',
        is_default: false,
        teacher_weight: 5,
        classroom_weight: 5,
        class_weight: 5,
        avoid_teacher_conflict: true,
        avoid_classroom_conflict: true,
        avoid_class_conflict: true,
        prefer_teacher_continuous: false,
        prefer_class_continuous: false,
        max_daily_hours_teacher: 8,
        max_daily_hours_class: 10
      },
      dialogFormVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑排课策略',
        create: '创建排课策略'
      },
      rules: {
        strategy_name: [{ required: true, message: '策略名称不能为空', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getSchedulingStrategies({
        page: this.listQuery.page,
        page_size: this.listQuery.limit,
        search: this.listQuery.search
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
    resetTemp() {
      this.temp = {
        id: undefined,
        strategy_name: '',
        description: '',
        is_default: false,
        teacher_weight: 5,
        classroom_weight: 5,
        class_weight: 5,
        avoid_teacher_conflict: true,
        avoid_classroom_conflict: true,
        avoid_class_conflict: true,
        prefer_teacher_continuous: false,
        prefer_class_continuous: false,
        max_daily_hours_teacher: 8,
        max_daily_hours_class: 10
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
          createSchedulingStrategy(this.temp).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '创建排课策略成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
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
          updateSchedulingStrategy(tempData.id, tempData).then(() => {
            this.dialogFormVisible = false
            this.$notify({
              title: '成功',
              message: '更新排课策略成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          })
        }
      })
    },
    handleSetDefault(row) {
      this.$confirm('确认将该策略设为默认?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 调用设置默认策略的API
        request({
          url: `/scheduling/strategies/${row.id}/set_default/`,
          method: 'post'
        }).then(() => {
          this.$notify({
            title: '成功',
            message: '设置默认策略成功',
            type: 'success',
            duration: 2000
          })
          this.getList()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消设置'
        })
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除该排课策略?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 调用删除策略的API
        request({
          url: `/scheduling/strategies/${row.id}/`,
          method: 'delete'
        }).then(() => {
          this.$notify({
            title: '成功',
            message: '删除排课策略成功',
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
</style> 